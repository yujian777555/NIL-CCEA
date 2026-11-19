"""四模块的纯数据契约和可替换接口。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class AgentContext:
    task_id: str
    task_version: str
    task_family: str
    visible_messages: tuple[dict[str, Any], ...]
    domain_policy: str
    tool_schemas: tuple[dict[str, Any], ...]
    step_index: int
    max_steps: int
    plan_state: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Plan:
    goals: tuple[dict[str, Any], ...]
    termination_condition: str
    unknowns: tuple[str, ...]
    module_version: str


@dataclass(frozen=True)
class Selection:
    kind: str
    tool_name: str | None
    goal_id: str | None
    reason_code: str
    module_version: str


@dataclass(frozen=True)
class ToolCallProposal:
    tool_name: str
    arguments: dict[str, Any]
    schema_valid: bool
    missing_fields: tuple[str, ...]
    module_version: str


@dataclass(frozen=True)
class AssistantDecision:
    kind: str
    content: str | None
    tool_call: ToolCallProposal | None
    module_events: tuple[dict[str, Any], ...]
    module_versions: dict[str, str]


class Planner(Protocol):
    module_version: str

    def plan(self, context: AgentContext) -> Plan:
        ...


class Selector(Protocol):
    module_version: str

    def select(self, context: AgentContext, plan: Plan) -> Selection:
        ...


class Caller(Protocol):
    module_version: str

    def propose(
        self,
        context: AgentContext,
        plan: Plan,
        selection: Selection,
    ) -> ToolCallProposal:
        ...


class Synthesizer(Protocol):
    module_version: str

    def synthesize(
        self,
        context: AgentContext,
        plan: Plan,
        selection: Selection,
        tool_result: dict[str, Any] | None,
    ) -> str:
        ...
