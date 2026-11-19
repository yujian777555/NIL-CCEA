"""调用、失败、重试和成本事件账本。"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class CostEvent:
    event_id: str
    run_id: str
    event_type: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    api_cost: float = 0.0
    retry_index: int = 0
    status: str = "success"
    timestamp_utc: str = ""
    detail: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if not data["timestamp_utc"]:
            data["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
        return data


class CostLedger:
    def __init__(self) -> None:
        self.events: list[CostEvent] = []

    def add(self, event: CostEvent) -> None:
        if event.status not in {"success", "failed", "retry", "timeout"}:
            raise ValueError(f"未知账本状态: {event.status}")
        self.events.append(event)

    def totals(self) -> dict[str, float | int]:
        return {
            "events": len(self.events),
            "input_tokens": sum(event.input_tokens for event in self.events),
            "output_tokens": sum(event.output_tokens for event in self.events),
            "api_cost": sum(event.api_cost for event in self.events),
            "failed_events": sum(event.status in {"failed", "timeout"} for event in self.events),
            "retry_events": sum(event.status == "retry" for event in self.events),
        }
