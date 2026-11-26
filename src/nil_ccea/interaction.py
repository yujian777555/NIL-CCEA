"""任务级差分交互、两 seed 重复测量、bootstrap 和 Holm 校正。"""

from __future__ import annotations

import itertools
import math
import random
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Iterable

from .factorial import generate_binary_configurations
from .manifest import SLOTS


PAIRWISE_SLOTS = tuple(itertools.combinations(SLOTS, 2))
VALID_STATUSES = {"success", "agent_failed", "infra_failed"}


class InteractionDataError(ValueError):
    """原始 episode 无法支持完整 factorial 复算。"""


@dataclass(frozen=True)
class InteractionEstimate:
    slot_i: str
    slot_j: str
    estimate: float
    ci_low: float
    ci_high: float
    cluster_count: int
    complete_cluster_count: int
    seed_count: int
    context_count: int
    p_value: float
    holm_adjusted_p: float | None
    reject_null: bool | None
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
            "seed_count": self.seed_count,
            "context_count": self.context_count,
            "p_value": self.p_value,
            "holm_adjusted_p": self.holm_adjusted_p,
            "reject_null": self.reject_null,
            "status": self.status,
        }


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


def _configuration_key(configuration: dict[str, Any]) -> tuple[int, ...]:
    try:
        values = tuple(int(configuration[slot]) for slot in SLOTS)
    except (KeyError, TypeError, ValueError) as exc:
        raise InteractionDataError("configuration 缺少四个二元模块槽位") from exc
    if any(value not in (0, 1) for value in values):
        raise InteractionDataError(f"configuration 必须是二元值: {configuration}")
    return values


def _validate_and_group(
    records: Iterable[dict[str, Any]],
    *,
    expected_seeds: tuple[int, ...],
) -> dict[str, dict[int, dict[tuple[int, ...], dict[str, Any]]]]:
    expected_configs = {
        tuple(configuration[slot] for slot in SLOTS)
        for configuration in generate_binary_configurations(SLOTS)
    }
    grouped: dict[str, dict[int, dict[tuple[int, ...], dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    for record in records:
        status = record.get("status")
        if status not in VALID_STATUSES:
            raise InteractionDataError(
                f"status 必须明确区分 success、agent_failed、infra_failed，收到 {status!r}"
            )
        task_id = str(record.get("task_id"))
        try:
            seed = int(record["seed"])
        except (KeyError, TypeError, ValueError) as exc:
            raise InteractionDataError("episode 缺少有效 seed") from exc
        if seed not in expected_seeds:
            raise InteractionDataError(f"出现未登记 seed={seed}")
        configuration_key = _configuration_key(record.get("configuration", {}))
        if configuration_key in grouped[task_id][seed]:
            raise InteractionDataError(
                f"重复配置: task_id={task_id}, seed={seed}, configuration={configuration_key}"
            )
        if status == "infra_failed":
            raise InteractionDataError(
                f"基础设施失败不能静默进入交互估计: task_id={task_id}, seed={seed}, configuration={configuration_key}"
            )
        if record.get("primary_score") is None:
            raise InteractionDataError(
                f"有效 task episode 缺少 primary_score: task_id={task_id}, seed={seed}"
            )
        grouped[task_id][seed][configuration_key] = record

    if not grouped:
        raise InteractionDataError("没有可用于交互估计的 episode")
    for task_id, seed_records in grouped.items():
        observed_seeds = tuple(sorted(seed_records))
        if observed_seeds != tuple(sorted(expected_seeds)):
            raise InteractionDataError(
                f"task={task_id} 的 seed 集合不完整: expected={expected_seeds}, observed={observed_seeds}"
            )
        for seed, config_records in seed_records.items():
            observed_configs = set(config_records)
            if observed_configs != expected_configs:
                missing = sorted(expected_configs - observed_configs)
                extra = sorted(observed_configs - expected_configs)
                raise InteractionDataError(
                    f"task={task_id}, seed={seed} 未覆盖完整 16 配置，missing={missing}, extra={extra}"
                )
    return grouped


def _task_contrasts(
    grouped: dict[str, dict[int, dict[tuple[int, ...], dict[str, Any]]]],
    slot_i: str,
    slot_j: str,
) -> dict[str, float]:
    slot_i_index = SLOTS.index(slot_i)
    slot_j_index = SLOTS.index(slot_j)
    context_indices = [
        index for index in range(len(SLOTS)) if index not in {slot_i_index, slot_j_index}
    ]
    required_cells = {(0, 0), (0, 1), (1, 0), (1, 1)}
    task_values: dict[str, float] = {}
    for task_id, seed_records in grouped.items():
        seed_contrasts: list[float] = []
        for config_records in seed_records.values():
            context_values: dict[tuple[int, ...], dict[tuple[int, int], float]] = defaultdict(dict)
            for configuration_key, record in config_records.items():
                context = tuple(configuration_key[index] for index in context_indices)
                cell = (configuration_key[slot_i_index], configuration_key[slot_j_index])
                context_values[context][cell] = float(record["primary_score"])
            if len(context_values) != 4:
                raise InteractionDataError(
                    f"task={task_id} 交互上下文数量不是 4: {len(context_values)}"
                )
            context_contrasts: list[float] = []
            for context, cells in context_values.items():
                if set(cells) != required_cells:
                    raise InteractionDataError(
                        f"task={task_id} context={context} 未覆盖四个交互 cell"
                    )
                context_contrasts.append(
                    cells[(1, 1)]
                    - cells[(1, 0)]
                    - cells[(0, 1)]
                    + cells[(0, 0)]
                )
            seed_contrasts.append(sum(context_contrasts) / len(context_contrasts))
        task_values[task_id] = sum(seed_contrasts) / len(seed_contrasts)
    return task_values


def _bootstrap(values: list[float], samples: int, seed: int) -> tuple[float, float]:
    rng = random.Random(seed)
    means = [
        sum(rng.choice(values) for _ in values) / len(values)
        for _ in range(max(samples, 1))
    ]
    return _percentile(means, 0.025), _percentile(means, 0.975)


def _permutation_p_value(values: list[float], samples: int, seed: int) -> float:
    observed = abs(sum(values) / len(values))
    rng = random.Random(seed)
    exceed = 0
    for _ in range(max(samples, 1)):
        randomized = [value if rng.getrandbits(1) else -value for value in values]
        if abs(sum(randomized) / len(randomized)) >= observed:
            exceed += 1
    return (exceed + 1) / (max(samples, 1) + 1)


def _estimate_from_values(
    values: list[float],
    *,
    slot_i: str,
    slot_j: str,
    seed_count: int,
    practical_delta: float,
    bootstrap_samples: int,
    random_seed: int,
) -> InteractionEstimate:
    estimate = sum(values) / len(values)
    ci_low, ci_high = _bootstrap(values, bootstrap_samples, random_seed)
    p_value = _permutation_p_value(values, bootstrap_samples, random_seed + 1)
    if ci_low > practical_delta:
        status = "POSITIVE"
    elif ci_high < -practical_delta:
        status = "NEGATIVE"
    elif ci_low >= -practical_delta and ci_high <= practical_delta:
        status = "WEAK"
    else:
        status = "UNCERTAIN"
    return InteractionEstimate(
        slot_i=slot_i,
        slot_j=slot_j,
        estimate=estimate,
        ci_low=ci_low,
        ci_high=ci_high,
        cluster_count=len(values),
        complete_cluster_count=len(values),
        seed_count=seed_count,
        context_count=4,
        p_value=p_value,
        holm_adjusted_p=None,
        reject_null=None,
        status=status,
    )


def holm_bonferroni(
    p_values: dict[tuple[str, str], float], *, alpha: float = 0.05
) -> dict[tuple[str, str], tuple[float, bool]]:
    """返回 Holm step-down 调整后的 p 值和拒绝标记。"""

    ordered = sorted(p_values.items(), key=lambda item: item[1])
    adjusted: dict[tuple[str, str], tuple[float, bool]] = {}
    running_max = 0.0
    rejection_stopped = False
    total = len(ordered)
    for rank, (pair, p_value) in enumerate(ordered):
        multiplier = total - rank
        adjusted_p = min(1.0, p_value * multiplier)
        running_max = max(running_max, adjusted_p)
        threshold = alpha / multiplier
        reject = not rejection_stopped and p_value <= threshold
        if not reject:
            rejection_stopped = True
        adjusted[pair] = (running_max, reject)
    return adjusted


def estimate_pairwise_interaction(
    records: Iterable[dict[str, Any]],
    slot_i: str,
    slot_j: str,
    *,
    expected_seeds: tuple[int, ...] = (0, 1),
    practical_delta: float = 0.05,
    bootstrap_samples: int = 2000,
    random_seed: int = 0,
) -> InteractionEstimate:
    if slot_i == slot_j or slot_i not in SLOTS or slot_j not in SLOTS:
        raise ValueError("交互必须涉及两个不同的已登记槽位")
    if len(expected_seeds) < 2 or len(set(expected_seeds)) != len(expected_seeds):
        raise ValueError("Phase 0B 要求至少两个不重复的 seed 作为 task 内重复测量")
    grouped = _validate_and_group(records, expected_seeds=expected_seeds)
    task_values = _task_contrasts(grouped, slot_i, slot_j)
    return _estimate_from_values(
        list(task_values.values()),
        slot_i=slot_i,
        slot_j=slot_j,
        seed_count=len(expected_seeds),
        practical_delta=practical_delta,
        bootstrap_samples=bootstrap_samples,
        random_seed=random_seed,
    )


def estimate_all_pairwise_interactions(
    records: Iterable[dict[str, Any]],
    *,
    expected_seeds: tuple[int, ...] = (0, 1),
    practical_delta: float = 0.05,
    bootstrap_samples: int = 2000,
    alpha: float = 0.05,
    random_seed: int = 0,
) -> dict[tuple[str, str], InteractionEstimate]:
    """复算六组交互并统一应用 Holm 校正。"""

    record_list = list(records)
    grouped = _validate_and_group(record_list, expected_seeds=expected_seeds)
    estimates: dict[tuple[str, str], InteractionEstimate] = {}
    for offset, (slot_i, slot_j) in enumerate(PAIRWISE_SLOTS):
        task_values = _task_contrasts(grouped, slot_i, slot_j)
        estimates[(slot_i, slot_j)] = _estimate_from_values(
            list(task_values.values()),
            slot_i=slot_i,
            slot_j=slot_j,
            seed_count=len(expected_seeds),
            practical_delta=practical_delta,
            bootstrap_samples=bootstrap_samples,
            random_seed=random_seed + offset * 17,
        )
    correction = holm_bonferroni(
        {pair: estimate.p_value for pair, estimate in estimates.items()},
        alpha=alpha,
    )
    return {
        pair: InteractionEstimate(
            **{
                **estimate.__dict__,
                "holm_adjusted_p": correction[pair][0],
                "reject_null": correction[pair][1],
            }
        )
        for pair, estimate in estimates.items()
    }
