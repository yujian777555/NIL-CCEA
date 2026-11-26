"""真实 tau2 Orchestrator factorial runner。"""

from __future__ import annotations

import json
import inspect
import traceback
import uuid
from pathlib import Path
from typing import Any, Callable

from .manifest import SLOTS, build_run_manifest, canonical_json, configuration_id, sha256_text
from .factorial import generate_binary_configurations, validate_complete_binary_configurations
from .tau2_adapter import InvalidToolCallError, build_tau2_agent_class
from .deepseek_client import DeepSeekIdentityError, ModelFingerprintTracker, RequestBudget


class Tau2RunnerError(RuntimeError):
    pass


class Tau2FactorialRunner:
    """以新环境实例和新 Agent state 执行每个 task-seed-config。"""

    def __init__(
        self,
        *,
        tau2_source_commit: str,
        task_version: str,
        environment_factory: Callable[[], Any],
        environment_factory_with_task: Callable[[Any], Any] | None = None,
        user_factory: Callable[[Any], Any],
        module_factory: Callable[[dict[str, int]], dict[str, Any]],
        user_factory_with_environment: Callable[[Any, Any], Any] | None = None,
        output_dir: str | Path | None = None,
        max_steps: int = 30,
        max_errors: int = 10,
        evaluate: bool = True,
        request_budget: RequestBudget | None = None,
        identity_tracker: ModelFingerprintTracker | None = None,
    ) -> None:
        self.tau2_source_commit = tau2_source_commit
        self.task_version = task_version
        self.environment_factory = environment_factory
        self.environment_factory_with_task = environment_factory_with_task
        self.user_factory = user_factory
        self.module_factory = module_factory
        self.user_factory_with_environment = user_factory_with_environment
        self.output_dir = Path(output_dir) if output_dir is not None else None
        self.max_steps = max_steps
        self.max_errors = max_errors
        self.evaluate = evaluate
        self.request_budget = request_budget
        self.identity_tracker = identity_tracker
        if self.evaluate and self.request_budget is None:
            raise ValueError("真实 ENV 运行必须显式提供 RequestBudget")
        if self.evaluate and self.identity_tracker is None:
            raise ValueError("真实 ENV 运行必须显式提供 ModelFingerprintTracker")
        self.agent_class = build_tau2_agent_class()

    def run(
        self,
        tasks: list[Any],
        seeds: tuple[int, ...] = (0, 1),
    ) -> list[dict[str, Any]]:
        configurations = generate_binary_configurations(SLOTS)
        validate_complete_binary_configurations(configurations, SLOTS)
        if len(seeds) < 2 or len(set(seeds)) != len(seeds):
            raise ValueError("tau2 factorial runner 要求至少两个不重复 seed")
        records: list[dict[str, Any]] = []
        self._prepare_output()
        for task in tasks:
            for seed in seeds:
                for configuration in configurations:
                    record = self.run_episode(task, seed, configuration)
                    records.append(record)
                    self._append_record(record)
                    if record.get("quarantine"):
                        self._write_run_summary(records)
                        raise Tau2RunnerError("模型身份或 fingerprint 漂移，批次已 quarantine")
        self._validate_run_completeness(records, tasks, seeds)
        self._write_run_summary(records)
        return records

    def run_episode(
        self, task: Any, seed: int, configuration: dict[str, int]
    ) -> dict[str, Any]:
        return self._run_episode_once(task, seed, configuration)

    def _run_episode_once(
        self, task: Any, seed: int, configuration: dict[str, int]
    ) -> dict[str, Any]:
        environment = self._make_environment(task)
        modules = self.module_factory(configuration)
        self._bind_runtime_controls(modules)
        agent = self.agent_class(
            tools=environment.get_tools(),
            domain_policy=environment.get_policy(),
            planner=modules["planner"],
            selector=modules["selector"],
            caller=modules["caller"],
            synthesizer=modules["synthesizer"],
            task_id=str(task.id),
            task_version=self.task_version,
            task_family=environment.get_domain_name(),
        )
        if self.user_factory_with_environment is not None:
            user = self.user_factory_with_environment(task, environment)
        else:
            user = self.user_factory(task)
        self._bind_user_runtime_controls(user)
        run_id = str(uuid.uuid4())
        for slot, module in modules.items():
            client = getattr(module, "client", None)
            if client is not None and hasattr(client, "set_episode_context"):
                client.set_episode_context(
                    run_id=run_id,
                    episode_id=run_id,
                    task_id=str(task.id),
                    seed=seed,
                    configuration_id=configuration_id(configuration),
                    module=slot,
                )
        for attribute in ("client", "llm_client", "deepseek_client"):
            client = getattr(user, attribute, None)
            if client is not None and hasattr(client, "set_episode_context"):
                client.set_episode_context(
                    run_id=run_id,
                    episode_id=run_id,
                    task_id=str(task.id),
                    seed=seed,
                    configuration_id=configuration_id(configuration),
                    module="user_simulator",
                )
        manifest = build_run_manifest(
            configuration,
            environment={
                "name": "tau2-bench",
                "version": self.task_version,
                "domain": environment.get_domain_name(),
                "primary_endpoint": "environment_reward",
                "evaluation_type": "ENV",
            },
            model={
                "provider": "deepseek",
                "requested_model": "deepseek-flash",
                "served_model": None,
                "system_fingerprint": None,
            },
            decoding={
                "temperature": 0.0,
                "max_output_tokens": 512,
                "thinking": False,
            },
            mode="tau2-text-v1",
            source_commit=self.tau2_source_commit,
            module_overrides={slot: self._module_provenance(slot, module) for slot, module in modules.items()},
        )
        orchestrator = None
        try:
            from tau2.orchestrator.orchestrator import Orchestrator

            orchestrator = Orchestrator(
                domain=environment.get_domain_name(),
                agent=agent,
                user=user,
                environment=environment,
                task=task,
                max_steps=self.max_steps,
                max_errors=self.max_errors,
                seed=seed,
            )
            self._validate_model_consistency(modules, user)
            if self.evaluate:
                from tau2.evaluator.evaluator import EvaluationType
                from tau2.runner.simulation import run_simulation

                simulation = run_simulation(
                    orchestrator,
                    evaluation_type=EvaluationType.ENV,
                )
            else:
                simulation = orchestrator.run()
            messages = simulation.get_messages()
            request_events = self._drain_request_events(modules, user)
            reward_info = getattr(simulation, "reward_info", None)
            primary_score = None
            if reward_info is not None:
                primary_score = getattr(reward_info, "reward", None)
            termination_reason = getattr(simulation, "termination_reason", None)
            termination_value = getattr(termination_reason, "value", str(termination_reason))
            if self.evaluate and reward_info is None:
                raise Tau2RunnerError("ENV reward missing; episode is not a valid success")
            if not self.evaluate:
                status = "success"
                failure_kind = None
            elif termination_value in {"agent_error", "too_many_errors"} or primary_score == 0:
                status = "agent_failed"
                failure_kind = "agent"
            else:
                status = "success"
                failure_kind = None
            return {
                "run_id": run_id,
                "mode": "tau2-text-v1",
                "task_id": str(task.id),
                "task_version": self.task_version,
                "task_family": environment.get_domain_name(),
                "seed": seed,
                "configuration_id": configuration_id(configuration),
                "configuration": configuration,
                "config_hash": manifest.config_hash,
                "source_commit": self.tau2_source_commit,
                "status": status,
                "failure_kind": failure_kind,
                "primary_score": primary_score,
                "trajectory": [message.model_dump() for message in messages],
                "retry_count": 0,
                "failures": [],
                "request_events": request_events,
                "quarantine": False,
                "termination_reason": termination_value,
                "manifest": manifest.to_dict(),
            }
        except Exception as exc:
            failure_kind = "agent" if isinstance(exc, InvalidToolCallError) else "infrastructure"
            status = "agent_failed" if failure_kind == "agent" else "infra_failed"
            partial_messages = []
            if orchestrator is not None and hasattr(orchestrator, "trajectory"):
                partial_messages = [message.model_dump() for message in orchestrator.trajectory]
            request_events = self._drain_request_events(modules, user)
            return {
                "run_id": run_id,
                "mode": "tau2-text-v1",
                "task_id": str(task.id),
                "task_version": self.task_version,
                "task_family": environment.get_domain_name(),
                "seed": seed,
                "configuration_id": configuration_id(configuration),
                "configuration": configuration,
                "config_hash": manifest.config_hash,
                "source_commit": self.tau2_source_commit,
                "status": status,
                "failure_kind": failure_kind,
                "primary_score": None,
                "trajectory": partial_messages,
                "retry_count": 0,
                "failures": [
                    {
                        "type": type(exc).__name__,
                        "message": str(exc),
                        "traceback": traceback.format_exc(),
                    }
                ],
                "request_events": request_events,
                "quarantine": isinstance(exc, DeepSeekIdentityError),
                "manifest": manifest.to_dict(),
            }

    @staticmethod
    def _module_provenance(slot: str, module: Any) -> dict[str, Any]:
        variant_id = getattr(module, "module_version", type(module).__name__)
        try:
            source = inspect.getsource(type(module))
        except (OSError, TypeError):
            source = f"{type(module).__module__}:{type(module).__qualname__}"
        return {
            "slot": slot,
            "variant_id": variant_id,
            "mechanism": type(module).__name__,
            "interface_version": "module-contracts-draft-r1",
            "content_sha256": sha256_text(
                canonical_json({"variant_id": variant_id, "source": source})
            ),
        }

    def _bind_runtime_controls(self, modules: dict[str, Any]) -> None:
        for module in modules.values():
            client = getattr(module, "client", None)
            if client is None or self.request_budget is None or not hasattr(client, "budget"):
                continue
            if client.budget is not None and client.budget is not self.request_budget:
                raise Tau2RunnerError("模块客户端携带了不同的 RequestBudget")
            client.budget = self.request_budget
            if self.identity_tracker is not None:
                if (
                    hasattr(client, "identity_tracker")
                    and client.identity_tracker is not self.identity_tracker
                ):
                    raise Tau2RunnerError("模块客户端携带了不同的 ModelFingerprintTracker")
                if hasattr(client, "identity_tracker"):
                    client.identity_tracker = self.identity_tracker

    def _make_environment(self, task: Any) -> Any:
        if self.environment_factory_with_task is not None:
            return self.environment_factory_with_task(task)
        try:
            signature = inspect.signature(self.environment_factory)
            positional = [
                parameter
                for parameter in signature.parameters.values()
                if parameter.kind
                in (parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD)
            ]
            if positional:
                return self.environment_factory(task)  # type: ignore[misc]
        except (TypeError, ValueError):
            pass
        return self.environment_factory()

    def _bind_user_runtime_controls(self, user: Any) -> None:
        if self.request_budget is None:
            return
        for attribute in ("client", "llm_client", "deepseek_client"):
            client = getattr(user, attribute, None)
            if client is not None and hasattr(client, "budget"):
                if client.budget is not None and client.budget is not self.request_budget:
                    raise Tau2RunnerError("User Simulator 携带了不同的 RequestBudget")
                client.budget = self.request_budget
                if self.identity_tracker is not None and hasattr(client, "identity_tracker"):
                    if client.identity_tracker is not self.identity_tracker:
                        raise Tau2RunnerError("User Simulator 携带了不同的 ModelFingerprintTracker")
                    client.identity_tracker = self.identity_tracker

    def _validate_model_consistency(self, modules: dict[str, Any], user: Any) -> None:
        if set(modules) != set(SLOTS):
            raise Tau2RunnerError(f"真实 ENV 运行要求四个模块槽位: {SLOTS}")
        clients = [getattr(module, "client", None) for module in modules.values()]
        clients = [client for client in clients if client is not None]
        if self.evaluate and len(clients) != len(modules):
            raise Tau2RunnerError("真实 ENV 运行要求四个模块均暴露 DeepSeek 客户端")
        if self.evaluate and len({id(client) for client in clients}) != len(clients):
            raise Tau2RunnerError("真实 ENV 运行要求四个模块使用不同的 DeepSeek 客户端")
        for client in clients:
            if getattr(client, "model", None) != "deepseek-flash":
                raise Tau2RunnerError("模块客户端必须使用 deepseek-flash")
            if (
                getattr(client, "temperature", 0.0) != 0.0
                or getattr(client, "max_output_tokens", 512) != 512
                or getattr(client, "max_input_tokens", 2000) != 2000
                or getattr(client, "max_retries", 1) != 1
            ):
                raise Tau2RunnerError("模块客户端 decoding 配置不一致")
            self._validate_client_runtime_controls(client)
        module_bases = {getattr(client, "base_url", "https://api.deepseek.com") for client in clients}
        if len(module_bases) > 1:
            raise Tau2RunnerError("模块客户端 base URL 不一致")
        user_client = next(
            (getattr(user, attribute, None) for attribute in ("client", "llm_client", "deepseek_client") if getattr(user, attribute, None) is not None),
            None,
        )
        user_model = getattr(user, "llm", None)
        if user_model is None and user_client is not None:
            user_model = getattr(user_client, "model", None)
        if user_model is None:
            if self.evaluate:
                raise Tau2RunnerError("User Simulator 未暴露可验证的 DeepSeek Flash 客户端")
            return
        if not isinstance(user_model, str):
            user_model = getattr(user_model, "model", None)
        if user_model != "deepseek-flash":
            raise Tau2RunnerError(
                f"User Simulator model mismatch: expected deepseek-flash, observed {user_model}"
            )
        if self.evaluate and user_client is None:
            raise Tau2RunnerError("真实 ENV User Simulator 必须暴露受控 DeepSeek 客户端")
        if user_client is not None and (
            getattr(user_client, "temperature", 0.0) != 0.0
            or getattr(user_client, "max_output_tokens", 512) != 512
            or getattr(user_client, "max_input_tokens", 2000) != 2000
            or getattr(user_client, "max_retries", 1) != 1
        ):
            raise Tau2RunnerError("User Simulator decoding 配置不一致")
        if self.evaluate and user_client is not None:
            if id(user_client) in {id(client) for client in clients}:
                raise Tau2RunnerError("User Simulator 必须使用独立的 DeepSeek 客户端")
            self._validate_client_runtime_controls(user_client)
            if user_client.budget is not self.request_budget:
                raise Tau2RunnerError("五个客户端必须共享同一个 RequestBudget")
            if user_client.identity_tracker is not self.identity_tracker:
                raise Tau2RunnerError("五个客户端必须共享同一个 ModelFingerprintTracker")
            if not hasattr(user_client, "drain_audit_events"):
                raise Tau2RunnerError("User Simulator 客户端必须支持请求事件 drain")
            try:
                from .tau2_user_simulator import DeepSeekTau2UserSimulator
            except ImportError as exc:
                raise Tau2RunnerError("tau2 User Simulator 适配器不可用") from exc
            if not isinstance(user, DeepSeekTau2UserSimulator):
                raise Tau2RunnerError("禁止使用 stock tau2 UserSimulator")
        if self.evaluate:
            for client in clients:
                if client.budget is not self.request_budget:
                    raise Tau2RunnerError("五个客户端必须共享同一个 RequestBudget")
                if client.identity_tracker is not self.identity_tracker:
                    raise Tau2RunnerError("五个客户端必须共享同一个 ModelFingerprintTracker")
                if not hasattr(client, "drain_audit_events"):
                    raise Tau2RunnerError("模块客户端必须支持请求事件 drain")
        if module_bases and user_client is not None and getattr(user_client, "base_url", "https://api.deepseek.com") not in module_bases:
            raise Tau2RunnerError("User Simulator base URL 与模块不一致")

    def _validate_client_runtime_controls(self, client: Any) -> None:
        if self.evaluate and getattr(client, "budget", None) is None:
            raise Tau2RunnerError("客户端缺少 RequestBudget")
        http_client = getattr(client, "http_client", None)
        if http_client is not None and getattr(http_client, "_trust_env", False):
            raise Tau2RunnerError("客户端必须使用 trust_env=False 的直连 HTTPX")

    @staticmethod
    def _drain_request_events(modules: dict[str, Any], user: Any) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        clients: list[Any] = [getattr(module, "client", None) for module in modules.values()]
        clients.extend(
            getattr(user, attribute, None)
            for attribute in ("client", "llm_client", "deepseek_client")
        )
        seen: set[int] = set()
        for client in clients:
            if client is None or id(client) in seen or not hasattr(client, "drain_audit_events"):
                continue
            seen.add(id(client))
            events.extend(client.drain_audit_events())
        return events

    def _validate_run_completeness(
        self, records: list[dict[str, Any]], tasks: list[Any], seeds: tuple[int, ...]
    ) -> None:
        expected = {
            (str(task.id), seed, configuration_id(configuration))
            for task in tasks
            for seed in seeds
            for configuration in generate_binary_configurations(SLOTS)
        }
        actual = {
            (record["task_id"], record["seed"], record["configuration_id"])
            for record in records
        }
        if expected != actual:
            raise Tau2RunnerError("tau2 runner 输出缺少或重复 task-seed-configuration")

    def _prepare_output(self) -> None:
        if self.output_dir is None:
            return
        self.output_dir.mkdir(parents=True, exist_ok=True)
        for filename in ("episodes.jsonl", "request_events.jsonl", "cost_ledger.json", "run_summary.json"):
            path = self.output_dir / filename
            if path.exists() and path.stat().st_size > 0:
                raise Tau2RunnerError(f"拒绝覆盖已有 raw artifact: {path}")
            path.touch()

    def _append_record(self, record: dict[str, Any]) -> None:
        if self.output_dir is None:
            return
        with (self.output_dir / "episodes.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        with (self.output_dir / "request_events.jsonl").open("a", encoding="utf-8") as handle:
            for event in record.get("request_events", []):
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        self._write_cost_ledger()

    def _write_cost_ledger(self) -> None:
        if self.output_dir is None:
            return
        events_path = self.output_dir / "request_events.jsonl"
        events = [
            json.loads(line)
            for line in events_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        totals = {
            "events": len(events),
            "input_tokens": sum(event.get("usage", {}).get("prompt_tokens", 0) for event in events),
            "output_tokens": sum(event.get("usage", {}).get("completion_tokens", 0) for event in events),
            "api_cost": sum(event.get("cost_usd", 0.0) for event in events),
            "failed_events": sum(event.get("status") in {"infra_failed", "agent_failed"} for event in events),
            "agent_failed_events": sum(event.get("status") == "agent_failed" for event in events),
            "infra_failed_events": sum(event.get("status") == "infra_failed" for event in events),
            "retry_events": sum(event.get("status") == "retry" for event in events),
        }
        with (self.output_dir / "cost_ledger.json").open("w", encoding="utf-8") as handle:
            json.dump({"events": events, "totals": totals}, handle, ensure_ascii=False, indent=2)

    def _write_run_summary(self, records: list[dict[str, Any]]) -> None:
        if self.output_dir is None:
            return
        with (self.output_dir / "run_summary.json").open("w", encoding="utf-8") as handle:
            json.dump(
                {
                    "episodes": len(records),
                    "status_counts": {
                        status: sum(record["status"] == status for record in records)
                        for status in sorted({record["status"] for record in records})
                    },
                    "api_calls": sum(len(record.get("request_events", [])) for record in records),
                },
                handle,
                ensure_ascii=False,
                indent=2,
            )
