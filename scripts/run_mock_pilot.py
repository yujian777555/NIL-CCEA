"""运行纯本地 mock pilot，不产生真实 API 调用。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from nil_ccea.interaction import estimate_pairwise_interaction
from nil_ccea.runner import MockEnvironment, MockRunner, MockTask


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    tasks = [
        MockTask("mock-task-0", "mock-v1", "family-a"),
        MockTask("mock-task-1", "mock-v1", "family-b"),
    ]
    runner = MockRunner(environment=MockEnvironment(fail_first_call=True))
    records = runner.run(tasks, [0], output_dir=args.output, max_retries=1)
    estimate = estimate_pairwise_interaction(records, "planner", "selector")
    print(json.dumps({"episodes": len(records), "interaction": estimate.to_dict()}, indent=2))


if __name__ == "__main__":
    main()
