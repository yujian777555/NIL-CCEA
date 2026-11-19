"""因子配置生成与完整性检查。"""

from __future__ import annotations

from itertools import product
from typing import Iterable


def generate_binary_configurations(slots: Iterable[str]) -> list[dict[str, int]]:
    """按固定槽位顺序生成完整的二元因子配置。"""

    slot_names = list(slots)
    if not slot_names or len(set(slot_names)) != len(slot_names):
        raise ValueError("slots 必须是非空且不重复的序列")
    return [
        dict(zip(slot_names, values))
        for values in product((0, 1), repeat=len(slot_names))
    ]


def validate_complete_binary_configurations(
    configurations: Iterable[dict[str, int]], slots: Iterable[str]
) -> None:
    """验证配置集合恰好覆盖一次完整的二元笛卡尔积。"""

    slot_names = list(slots)
    expected = {
        tuple(config[slot] for slot in slot_names)
        for config in generate_binary_configurations(slot_names)
    }
    actual = {
        tuple(config.get(slot) for slot in slot_names)
        for config in configurations
    }
    if actual != expected:
        raise ValueError(
            f"配置不完整或包含重复项，expected={len(expected)}, actual={len(actual)}"
        )
