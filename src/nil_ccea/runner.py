"""最小 mock runner，模拟环境 reset、轨迹、失败和账本。"""

from __future__ import annotations

import hashlib
import json
import random
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ledger import CostEvent, CostLedger
from .manifest import SLOTS, RunManifest, all_configuration_manifests


@dataclass(frozen=True)
class MockTask:
    task_id: str
    task_version: str
    task_family: str


class MockEnvironment:
    """纯本地环境，输出用于验证 runner，不代表 benchmark 结果。"""

    def __init__(self, *, fail_first_call: bool = False) -> None:
        self.fail_first_call = fail_first_call
        self.reset_count = 0

    def reset(self, task: MockTask, seed: int) -> dict[str, Any]:
        self.reset_count += 1
        return {
            "task_id": task.task_id,
            "task_version": task.task_version,
            "seed": seed,
            "state_hash": hashlib.sha256(
                f"{task.task_id}|{task.task_version}|{seed}".encode("utf-8")
            ).hexdigest(),
        }

    def run(
        self,
        task: MockTask,
        seed: int,
        configuration: dict[str, int],
        *,
        attempt: int,
    ) -> tuple[float, list[dict[str, Any]], dict[str, int]]:
        reset_state = self.reset(task, seed)
        if self.fail_first_call and attempt == 0:
            raise TimeoutError("mock timeout injected for retry-path validation")
        # 这是一个可知的合成机制，只用于检验复算和状态流，不是研究数据。
        base = 0.50
        main_effects = {
            "planner": 0.04,
            "selector": 0.03,
            "caller": 0.02,
            "synthesizer": 0.01,
        }
        interaction = 0.10 if configuration["planner"] and configuration["selector"] else 0.0
        deterministic = base + sum(
            main_effects[slot] * configuration[slot] for slot in SLOTS
        ) + interaction
        noise = (
            int.from_bytes(
                hashlib.sha256(f"{task.task_id}|{seed}".encode("utf-8")).digest()[:4],
                "big",
            )
            % 5
            - 2
        ) / 1000
        score = max(0.0, min(1.0, deterministic + noise))
        trajectory = [
            {"module": "planner", "event": "plan_created", "step": 0},
            {"module": "selector", "event": "action_selected", "step": 1},
            {"module": "caller", "event": "tool_call_proposed", "step": 2},
            {"module": "synthesizer", "event": "response_composed", "step": 3},
        ]
        usage = {"input_tokens": 40, "output_tokens": 20}
        trajectory.insert(0, {"environment_reset": reset_state})
        return score, trajectory, usage


class MockRunner:
    """生成完整二元配置并写入原始 episode 与成本账本。"""

    def __init__(
        self,
        *,
        environment: MockEnvironment | None = None,
        model: dict[str, Any] | None = None,
        decoding: dict[str, Any] | None = None,
    ) -> None:
        self.environment = environment or MockEnvironment()
        self.model = model or {"provider": "mock", "model": "mock-agent-0"}
        self.decoding = decoding or {"temperature": 0.0, "max_steps": 4}
        self.ledger = CostLedger()

    def run(
        self,
        tasks: list[MockTask],
        seeds: list[int],
        *,
        output_dir: str | Path | None = None,
        max_retries: int = 1,
    ) -> list[dict[str, Any]]:
        environment_meta = {
            "name": "nil-ccea-mock",
            "version": "0.1",
            "reset_contract": "task_id|task_version|seed",
        }
        manifests = all_configuration_manifests(
            environment=environment_meta,
            model=self.model,
            decoding=self.decoding,
            mode="mock",
        )
        records: list[dict[str, Any]] = []
        for task in tasks:
            for seed in seeds:
                for manifest in manifests:
                    records.append(
                        self._run_episode(
                            task,
                            seed,
                            manifest,
                            max_retries=max_retries,
                        )
                    )
        if output_dir is not None:
            self._write_outputs(Path(output_dir), records)
        return records

    def _run_episode(
        self,
        task: MockTask,
        seed: int,
        manifest: RunManifest,
        *,
        max_retries: int,
    ) -> dict[str, Any]:
        run_id = str(uuid.uuid4())
        configuration = {
            slot: int(manifest.modules[slot]["variant_id"].rsplit(".", 1)[1])
            for slot in SLOTS
        }
        failures: list[dict[str, Any]] = []
        for attempt in range(max_retries + 1):
            try:
                score, trajectory, usage = self.environment.run(
                    task,
                    seed,
                    configuration,
                    attempt=attempt,
                )
                episode_status = "agent_failed" if score <= 0 else "success"
                self.ledger.add(
                    CostEvent(
                        event_id=str(uuid.uuid4()),
                        run_id=run_id,
                        event_type="agent_episode",
                        provider=self.model["provider"],
                        model=self.model["model"],
                        input_tokens=usage["input_tokens"],
                        output_tokens=usage["output_tokens"],
                        retry_index=attempt,
                        status="retry" if attempt else episode_status,
                        detail={"task_id": task.task_id},
                    )
                )
                return {
                    "run_id": run_id,
                    "mode": "mock",
                    "task_id": task.task_id,
                    "task_version": task.task_version,
                    "task_family": task.task_family,
                    "seed": seed,
                    "configuration_id": manifest.configuration_id,
                    "configuration": configuration,
                    "config_hash": manifest.config_hash,
                    "source_commit": manifest.source_commit,
                    "status": episode_status,
                    "failure_kind": "agent" if episode_status == "agent_failed" else None,
                    "primary_score": score,
                    "trajectory": trajectory,
                    "failures": failures,
                    "retry_count": attempt,
                    "usage": usage,
                    "manifest": manifest.to_dict(),
                }
            except Exception as exc:
                failure = {
                    "attempt": attempt,
                    "type": type(exc).__name__,
                    "message": str(exc),
                }
                failures.append(failure)
                self.ledger.add(
                    CostEvent(
                        event_id=str(uuid.uuid4()),
                        run_id=run_id,
                        event_type="agent_episode",
                        provider=self.model["provider"],
                        model=self.model["model"],
                        retry_index=attempt,
                        status="infra_failed",
                        detail=failure,
                    )
                )
        return {
            "run_id": run_id,
            "mode": "mock",
            "task_id": task.task_id,
            "task_version": task.task_version,
            "task_family": task.task_family,
            "seed": seed,
            "configuration_id": manifest.configuration_id,
            "configuration": configuration,
            "config_hash": manifest.config_hash,
            "source_commit": manifest.source_commit,
            "status": "infra_failed",
            "failure_kind": "infrastructure",
            "primary_score": None,
            "trajectory": [],
            "failures": failures,
            "retry_count": max_retries,
            "usage": {"input_tokens": 0, "output_tokens": 0},
            "manifest": manifest.to_dict(),
        }

    def _write_outputs(self, output_dir: Path, records: list[dict[str, Any]]) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        with (output_dir / "episodes.jsonl").open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        with (output_dir / "cost_ledger.json").open("w", encoding="utf-8") as handle:
            json.dump(
                {
                    "events": [event.to_dict() for event in self.ledger.events],
                    "totals": self.ledger.totals(),
                },
                handle,
                ensure_ascii=False,
                indent=2,
            )
