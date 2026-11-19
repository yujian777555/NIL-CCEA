"""从原始 episode 记录复算差分交互和 task-cluster bootstrap。"""

from __future__ import annotations

import math
import random
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class InteractionEstimate:
    slot_i: str
    slot_j: str
    estimate: float
    ci_low: float
    ci_high: float
    cluster_count: int
    complete_cluster_count: int
    status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "slot_i": self.slot_i,
            "slot_j": self.slot_j,
            "estimate": self.estimate,
            "ci_low": self.ci_low,
            "ci_high": self.ci_high,
            "cluster_count": self.cluster_count,
            "complete_cluster_count": self.complete_cluster_count,
            "status": self.status,
        }


def _cluster_key(record: dict[str, Any]) -> tuple[str, int]:
    return (str(record["task_id"]), int(record["seed"]))


def _contrast_by_cluster(
    records: Iterable[dict[str, Any]], slot_i: str, slot_j: str
) -> dict[tuple[str, int], float]:
    records = list(records)
    remaining_slots = sorted(
        set(records[0]["configuration"]) - {slot_i, slot_j}
    ) if records else []
    cells: dict[
        tuple[str, int], dict[tuple[int, ...], dict[tuple[int, int], float]]
    ] = defaultdict(lambda: defaultdict(dict))
    for record in records:
        if record.get("status") != "success":
            continue
        configuration = record["configuration"]
        key = _cluster_key(record)
        context = tuple(int(configuration[slot]) for slot in remaining_slots)
        cells[key][context][
            (int(configuration[slot_i]), int(configuration[slot_j]))
        ] = float(record["primary_score"])
    required = {(0, 0), (0, 1), (1, 0), (1, 1)}
    contrasts: dict[tuple[str, int], float] = {}
    for key, contexts in cells.items():
        context_contrasts = []
        for values in contexts.values():
            if required <= values.keys():
                context_contrasts.append(
                    values[(1, 1)]
                    - values[(1, 0)]
                    - values[(0, 1)]
                    + values[(0, 0)]
                )
        if context_contrasts:
            contrasts[key] = sum(context_contrasts) / len(context_contrasts)
    return contrasts


def _percentile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("不能对空样本计算分位数")
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def estimate_pairwise_interaction(
    records: Iterable[dict[str, Any]],
    slot_i: str,
    slot_j: str,
    *,
    practical_delta: float = 0.05,
    bootstrap_samples: int = 2000,
    random_seed: int = 0,
) -> InteractionEstimate:
    if slot_i == slot_j:
        raise ValueError("交互必须涉及两个不同槽位")
    record_list = list(records)
    all_clusters = {_cluster_key(record) for record in record_list}
    contrasts = _contrast_by_cluster(record_list, slot_i, slot_j)
    values = list(contrasts.values())
    if not values:
        return InteractionEstimate(
            slot_i,
            slot_j,
            float("nan"),
            float("nan"),
            float("nan"),
            0,
            0,
            "UNCERTAIN",
        )
    estimate = sum(values) / len(values)
    rng = random.Random(random_seed)
    bootstrap_means = [
        sum(rng.choice(values) for _ in values) / len(values)
        for _ in range(max(bootstrap_samples, 1))
    ]
    ci_low = _percentile(bootstrap_means, 0.025)
    ci_high = _percentile(bootstrap_means, 0.975)
    if ci_low > practical_delta:
        status = "POSITIVE"
    elif ci_high < -practical_delta:
        status = "NEGATIVE"
    elif ci_low >= -practical_delta and ci_high <= practical_delta:
        status = "WEAK"
    else:
        status = "UNCERTAIN"
    return InteractionEstimate(
        slot_i,
        slot_j,
        estimate,
        ci_low,
        ci_high,
        len(all_clusters),
        len(values),
        status,
    )

