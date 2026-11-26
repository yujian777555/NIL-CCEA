"""Phase 0E.1 的无 API Smoke Factory 与预运行 manifest。"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .deepseek_client import DeepSeekClient, ModelFingerprintTracker, RequestBudget
from .deepseek_modules import build_deepseek_modules_by_client
from .factorial import generate_binary_configurations
from .manifest import SLOTS, canonical_json, sha256_text
from .tau2_user_simulator import build_deepseek_tau2_user_simulator


SMOKE_TASKS = {"retail": "5", "airline": "2"}
SMOKE_SEEDS = (0, 1)
SMOKE_MAX_STEPS = 30
SMOKE_BUDGET = {
    "max_requests": 15_360,
    "max_input_tokens": 30_720_000,
    "max_output_tokens": 7_864_320,
    "max_cost_usd": 20.0,
    "episode_max_requests": 240,
    "episode_max_input_tokens": 480_000,
    "episode_max_output_tokens": 122_880,
    "episode_max_cost_usd": 0.291456,
}


def task_domain(task: Any) -> str:
    instructions = getattr(getattr(task, "user_scenario", None), "instructions", None)
    domain = getattr(instructions, "domain", None)
    if domain is None and isinstance(instructions, dict):
        domain = instructions.get("domain")
    if domain not in SMOKE_TASKS:
        raise ValueError(f"任务 domain 不在冻结 smoke 范围内: {domain!r}")
    return str(domain)


def get_environment_for_task(task: Any) -> Any:
    domain = task_domain(task)
    if domain == "retail":
        from tau2.domains.retail.environment import get_environment
    elif domain == "airline":
        from tau2.domains.airline.environment import get_environment
    else:  # pragma: no cover - task_domain 已经 fail closed
        raise ValueError(f"不支持的 smoke domain: {domain}")
    environment = get_environment()
    if environment.get_domain_name() != domain:
        raise ValueError(
            f"环境 domain 不匹配: task={domain}, environment={environment.get_domain_name()}"
        )
    return environment


def load_frozen_smoke_tasks() -> list[Any]:
    from tau2.domains.airline.environment import get_tasks as get_airline_tasks
    from tau2.domains.retail.environment import get_tasks as get_retail_tasks

    candidates = {
        "retail": {task.id: task for task in get_retail_tasks("test")},
        "airline": {task.id: task for task in get_airline_tasks("test")},
    }
    tasks = []
    for domain, task_id in (("retail", "5"), ("airline", "2")):
        task = candidates[domain].get(task_id)
        if task is None:
            raise ValueError(f"冻结 task 不在 test split: {domain} {task_id}")
        if task_domain(task) != domain:
            raise ValueError(f"任务 domain 校验失败: {domain} {task_id}")
        tasks.append(task)
    return tasks


@dataclass
class SmokeFactory:
    clients: dict[str, DeepSeekClient]
    budget: RequestBudget
    identity_tracker: ModelFingerprintTracker

    def module_factory(self, configuration: dict[str, int]) -> dict[str, object]:
        return build_deepseek_modules_by_client(
            {slot: self.clients[slot] for slot in SLOTS}, configuration
        )

    def user_factory_with_environment(self, task: Any, environment: Any) -> Any:
        tools = None
        try:
            include = getattr(task, "user_tools", None)
            tools = environment.get_user_tools(include=include)
        except (AttributeError, ValueError):
            tools = None
        return build_deepseek_tau2_user_simulator(
            client=self.clients["user_simulator"], task=task, tools=tools
        )


def build_smoke_factory(api_key: str, *, tokenizer_path: str | None = None) -> SmokeFactory:
    if not api_key:
        raise ValueError("Smoke Factory 需要显式 api_key，且不会从环境变量读取")
    budget = RequestBudget(**SMOKE_BUDGET)
    identity_tracker = ModelFingerprintTracker()
    roles = (*SLOTS, "user_simulator")
    clients = {
        role: DeepSeekClient(
            api_key=api_key,
            model="deepseek-flash",
            base_url="https://api.deepseek.com",
            temperature=0.0,
            max_output_tokens=512,
            max_input_tokens=2000,
            max_retries=1,
            input_usd_per_million=0.30,
            cached_input_usd_per_million=0.006,
            output_usd_per_million=1.20,
            budget=budget,
            identity_tracker=identity_tracker,
            tokenizer_path=tokenizer_path,
        )
        for role in roles
    }
    if len({id(client) for client in clients.values()}) != 5:
        raise RuntimeError("Smoke Factory 未构造五个独立客户端")
    return SmokeFactory(clients=clients, budget=budget, identity_tracker=identity_tracker)


def _git_sha() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()


def build_smoke_prerun_manifest(
    *,
    code_sha: str | None = None,
    tau2_source_sha: str,
    protocol_path: str | Path,
) -> dict[str, Any]:
    protocol_text = Path(protocol_path).read_text(encoding="utf-8")
    configurations = [
        {slot: bits[index] for index, slot in enumerate(SLOTS)}
        for bits in (
            tuple(int(bit) for bit in format(value, "04b"))
            for value in range(16)
        )
    ]
    manifest = {
        "manifest_version": "phase0e1-smoke-prerun-r1",
        "code_sha": code_sha or _git_sha(),
        "protocol_version": "phase0e1-smoke-r1",
        "protocol_sha256": hashlib.sha256(protocol_text.encode("utf-8")).hexdigest(),
        "tau2_version": "1.0.1",
        "tau2_source_sha": tau2_source_sha,
        "tasks": [
            {"id": "5", "domain": "retail", "split": "test", "issue_id": "issue_770466c1"},
            {"id": "2", "domain": "airline", "split": "test", "issue_id": None},
        ],
        "task_selection_rule": "first listed task from each frozen family list",
        "seeds": list(SMOKE_SEEDS),
        "configurations": configurations,
        "execution_order": "task order retail-5, airline-2; seed ascending; cfg-0000 through cfg-1111",
        "model": {
            "provider": "deepseek",
            "requested_alias": "deepseek-flash",
            "served_model_observed": None,
            "system_fingerprint_observed": None,
            "base_url": "https://api.deepseek.com",
            "temperature": 0.0,
            "thinking": {"type": "disabled"},
            "max_input_tokens": 2000,
            "max_output_tokens": 512,
        },
        "client_roles": ["planner", "selector", "caller", "synthesizer", "user_simulator"],
        "client_policy": {
            "distinct_clients": 5,
            "shared_request_budget": True,
            "shared_model_identity_tracker": True,
            "direct_transport_trust_env": False,
        },
        "budget": {
            **SMOKE_BUDGET,
            "normal_logical_requests": 7680,
            "maximum_physical_attempts": 15360,
            "per_request_upper_bound_usd": 0.0012144,
            "total_no_retry_upper_bound_usd": 9.326592,
            "total_one_retry_upper_bound_usd": 18.653184,
            "proposed_spend_ceiling_usd": 20.0,
            "hard_stop_usd": 80.0,
        },
        "primary_endpoint": "EvaluationType.ENV.environment_reward",
        "interpretation": "exploratory two-task diagnostic only",
        "retail_task_quality_disclosure": {
            "issue_id": "issue_770466c1",
            "authentication_enforced": False,
            "reward_basis": ["DB", "NL_ASSERTION"],
            "scope": "no authentication, privacy, security, or policy-robustness claim",
        },
    }
    manifest["manifest_sha256"] = sha256_text(canonical_json(manifest))
    return manifest


def write_immutable_manifest(path: str | Path, manifest: dict[str, Any]) -> None:
    destination = Path(path)
    if destination.exists():
        raise FileExistsError(f"拒绝覆盖已有 pre-run manifest: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

