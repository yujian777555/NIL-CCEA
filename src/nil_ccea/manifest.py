"""不可变 manifest、配置 hash 和来源记录。"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from .factorial import generate_binary_configurations


SLOTS = ("planner", "selector", "caller", "synthesizer")


def canonical_json(value: Any) -> str:
    """生成稳定的 JSON 表示，用于 hash 和缓存键。"""

    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ModuleSpec:
    slot: str
    variant_id: str
    mechanism: str
    interface_version: str = "module-contracts-draft-r1"
    content_sha256: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class RunManifest:
    protocol_version: str
    runner_version: str
    source_commit: str
    environment: dict[str, Any]
    model: dict[str, Any]
    decoding: dict[str, Any]
    modules: dict[str, dict[str, Any]]
    configuration_id: str
    config_hash: str
    created_at_utc: str
    mode: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def get_source_commit() -> str:
    """读取当前仓库 commit，无法读取时返回明确的 unknown。"""

    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return completed.stdout.strip()


def default_module_specs() -> dict[str, ModuleSpec]:
    """返回与契约草案一致的两个候选变体。"""

    mechanisms = {
        ("planner", 0): "linear_constraint_plan",
        ("planner", 1): "state_dependency_plan",
        ("selector", 0): "schema_match_selector",
        ("selector", 1): "prerequisite_gate_selector",
        ("caller", 0): "direct_schema_caller",
        ("caller", 1): "validated_repair_caller",
        ("synthesizer", 0): "evidence_first_synthesizer",
        ("synthesizer", 1): "state_reconcile_synthesizer",
    }
    specs: dict[str, ModuleSpec] = {}
    for slot in SLOTS:
        for bit in (0, 1):
            variant_id = f"{slot}.{bit}"
            content = canonical_json(
                {"slot": slot, "variant_id": variant_id, "mechanism": mechanisms[(slot, bit)]}
            )
            specs[variant_id] = ModuleSpec(
                slot=slot,
                variant_id=variant_id,
                mechanism=mechanisms[(slot, bit)],
                content_sha256=sha256_text(content),
            )
    return specs


def configuration_id(configuration: dict[str, int]) -> str:
    bits = "".join(str(configuration[slot]) for slot in SLOTS)
    return f"cfg-{bits}"


def configuration_hash(
    configuration: dict[str, int],
    module_specs: dict[str, ModuleSpec],
    environment: dict[str, Any],
    model: dict[str, Any],
    decoding: dict[str, Any],
    protocol_version: str,
    runner_version: str,
) -> str:
    modules = {
        slot: module_specs[f"{slot}.{configuration[slot]}"].to_dict()
        for slot in SLOTS
    }
    payload = {
        "configuration": configuration,
        "modules": modules,
        "environment": environment,
        "model": model,
        "decoding": decoding,
        "protocol_version": protocol_version,
        "runner_version": runner_version,
    }
    return sha256_text(canonical_json(payload))


def build_run_manifest(
    configuration: dict[str, int],
    *,
    environment: dict[str, Any],
    model: dict[str, Any],
    decoding: dict[str, Any],
    protocol_version: str = "pilot-design-r1",
    runner_version: str = "0.1.0",
    mode: str = "mock",
    source_commit: str | None = None,
) -> RunManifest:
    module_specs = default_module_specs()
    config_id = configuration_id(configuration)
    config_hash = configuration_hash(
        configuration,
        module_specs,
        environment,
        model,
        decoding,
        protocol_version,
        runner_version,
    )
    modules = {
        slot: module_specs[f"{slot}.{configuration[slot]}"].to_dict()
        for slot in SLOTS
    }
    return RunManifest(
        protocol_version=protocol_version,
        runner_version=runner_version,
        source_commit=source_commit or get_source_commit(),
        environment=environment,
        model=model,
        decoding=decoding,
        modules=modules,
        configuration_id=config_id,
        config_hash=config_hash,
        created_at_utc=datetime.now(timezone.utc).isoformat(),
        mode=mode,
    )


def all_configuration_manifests(
    *,
    environment: dict[str, Any],
    model: dict[str, Any],
    decoding: dict[str, Any],
    mode: str = "mock",
) -> list[RunManifest]:
    return [
        build_run_manifest(
            config,
            environment=environment,
            model=model,
            decoding=decoding,
            mode=mode,
        )
        for config in generate_binary_configurations(SLOTS)
    ]
