"""真实 tau2 Orchestrator factorial runner。"""

from __future__ import annotations

import json
import traceback
import uuid
from pathlib import Path
from typing import Any, Callable

from .manifest import SLOTS, build_run_manifest, configuration_id
from .factorial import generate_binary_configurations, validate_complete_binary_configurations
from .tau2_adapter import build_tau2_agent_class


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
        user_factory: Callable[[Any], Any],
        module_factory: Callable[[dict[str, int]], dict[str, Any]],
        output_dir: str | Path | None = None,
        max_steps: int = 30,
        max_errors: int = 10,
        evaluate: bool = True,
    ) -> None:
        self.tau2_source_commit = tau2_source_commit
        self.task_version = task_version
        self.environment_factory = environment_factory
        self.user_factory = user_factory
        self.module_factory = module_factory
        self.output_dir = Path(output_dir) if output_dir is not None else None
        self.max_steps = max_steps
        self.max_errors = max_errors
        self.evaluate = evaluate
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
        for task in tasks:
            for seed in seeds:
                for configuration in configurations:
                    records.append(self.run_episode(task, seed, configuration))
        self._write_records(records)
        self._validate_run_completeness(records, tasks, seeds)
        return records

    def run_episode(
        self, task: Any, seed: int, configuration: dict[str, int]
    ) -> dict[str, Any]:
        environment = self.environment_factory()
        modules = self.module_factory(configuration)
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
        user = self.user_factory(task)
        run_id = str(uuid.uuid4())
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
                "model": "deepseek-flash",
                "version": "DeepSeek-V4.1-Flash-1017",
            },
            decoding={
                "temperature": 0.0,
                "max_output_tokens": 512,
                "thinking": False,
            },
            mode="tau2-text-v1",
            source_commit=self.tau2_source_commit,
        )
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
            reward_info = getattr(simulation, "reward_info", None)
            primary_score = None
            if reward_info is not None:
                primary_score = getattr(reward_info, "reward", None)
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
                "status": "agent_failed" if self.evaluate and primary_score == 0 else "success",
                "failure_kind": None,
                "primary_score": primary_score,
                "trajectory": [message.model_dump() for message in messages],
                "retry_count": 0,
                "failures": [],
                "manifest": manifest.to_dict(),
            }
        except Exception as exc:
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
                "status": "infra_failed",
                "failure_kind": "infrastructure",
                "primary_score": None,
                "trajectory": [],
                "retry_count": 0,
                "failures": [
                    {
                        "type": type(exc).__name__,
                        "message": str(exc),
                        "traceback": traceback.format_exc(),
                    }
                ],
                "manifest": manifest.to_dict(),
            }

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

    def _write_records(self, records: list[dict[str, Any]]) -> None:
        if self.output_dir is None:
            return
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with (self.output_dir / "episodes.jsonl").open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
