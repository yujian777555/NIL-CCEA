"""受保护的 Phase 0E.1 Smoke 入口。

默认只执行无 API 的 dry-run manifest 预检。付费执行必须显式传入 --paid-execute，
并且仍需要当前会话中的用户批准。
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from nil_ccea.smoke_factory import (
    build_smoke_factory,
    build_smoke_prerun_manifest,
    get_environment_for_task,
    load_frozen_smoke_tasks,
    write_immutable_manifest,
)
from nil_ccea.tau2_runner import Tau2FactorialRunner


TAU2_SOURCE_SHA = "fc0055dc4e0a316c3f83133267fbd6faaa770992"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--paid-execute", action="store_true")
    parser.add_argument("--manifest", type=Path, default=Path("artifacts/phase0e1_smoke_prerun.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/phase0e1_smoke"))
    parser.add_argument("--tokenizer-path", type=Path, default=None)
    args = parser.parse_args()

    if args.dry_run:
        api_key = "phase0e1-dry-run-fake-key"
    else:
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise SystemExit("--paid-execute 要求显式 DEEPSEEK_API_KEY。当前会话仍需用户批准。")

    factory = build_smoke_factory(
        api_key,
        tokenizer_path=str(args.tokenizer_path) if args.tokenizer_path else None,
    )
    manifest = build_smoke_prerun_manifest(
        tau2_source_sha=TAU2_SOURCE_SHA,
        protocol_path="docs/PHASE0E_PROTOCOL_DECISION.md",
    )
    write_immutable_manifest(args.manifest, manifest)
    print(f"pre-run manifest: {args.manifest}")
    if args.dry_run:
        print("dry-run complete: no API key read and no provider request sent")
        return 0

    tasks = load_frozen_smoke_tasks()
    runner = Tau2FactorialRunner(
        tau2_source_commit=TAU2_SOURCE_SHA,
        task_version="v1.0.1",
        environment_factory=lambda: None,
        environment_factory_with_task=get_environment_for_task,
        user_factory=lambda task: None,
        user_factory_with_environment=factory.user_factory_with_environment,
        module_factory=factory.module_factory,
        output_dir=args.output_dir,
        max_steps=30,
        evaluate=True,
        request_budget=factory.budget,
        identity_tracker=factory.identity_tracker,
    )
    records = runner.run(tasks, seeds=(0, 1))
    print(f"episodes: {len(records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

