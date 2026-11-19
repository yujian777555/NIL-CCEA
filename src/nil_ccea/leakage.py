"""模块源码的保守静态泄漏检查。"""

from __future__ import annotations

from pathlib import Path


FORBIDDEN_TOKENS = (
    "evaluation_criteria",
    "reference_trajectory",
    "gold_data_hash",
    "reward_basis",
    "ground_truth",
    "task_answer",
)


def find_forbidden_tokens(source: str) -> list[str]:
    return [token for token in FORBIDDEN_TOKENS if token in source]


def check_source_file(path: str | Path) -> list[str]:
    return find_forbidden_tokens(Path(path).read_text(encoding="utf-8"))
