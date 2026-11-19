"""契约草案的纯本地模块变体，用于接口和权限 smoke。"""

from __future__ import annotations

from typing import Any

from .contracts import (
    AgentContext,
    Caller,
    Plan,
    Planner,
    Selection,
    Selector,
    Synthesizer,
    ToolCallProposal,
)


class LinearPlanner:
    module_version = "planner.0"

    def plan(self, context: AgentContext) -> Plan:
        return Plan(
            goals=(
                {
                    "goal_id": "g0",
                    "description": "完成当前用户目标",
                    "prerequisites": (),
                },
            ),
            termination_condition="用户目标完成或需要澄清",
            unknowns=(),
            module_version=self.module_version,
        )


class StateDependencyPlanner:
    module_version = "planner.1"

    def plan(self, context: AgentContext) -> Plan:
        return Plan(
            goals=(
                {
                    "goal_id": "g0",
                    "description": "确认公开状态并完成当前用户目标",
                    "prerequisites": ("公开状态可用",),
                },
            ),
            termination_condition="目标完成且没有未满足公开前置条件",
            unknowns=("当前公开状态",),
            module_version=self.module_version,
        )


class SchemaMatchSelector:
    module_version = "selector.0"

    def select(self, context: AgentContext, plan: Plan) -> Selection:
        if not context.tool_schemas:
            return Selection("respond", None, "g0", "response_needed", self.module_version)
        return Selection(
            "tool_call",
            context.tool_schemas[0].get("name"),
            "g0",
            "schema_match",
            self.module_version,
        )


class PrerequisiteGateSelector:
    module_version = "selector.1"

    def select(self, context: AgentContext, plan: Plan) -> Selection:
        if not context.tool_schemas or context.plan_state.get("public_state_ready") is not True:
            return Selection("respond", None, "g0", "response_needed", self.module_version)
        return Selection(
            "tool_call",
            context.tool_schemas[0].get("name"),
            "g0",
            "prerequisite",
            self.module_version,
        )


class DirectSchemaCaller:
    module_version = "caller.0"

    def propose(
        self,
        context: AgentContext,
        plan: Plan,
        selection: Selection,
    ) -> ToolCallProposal:
        if selection.kind != "tool_call" or selection.tool_name is None:
            return ToolCallProposal("", {}, True, (), self.module_version)
        return ToolCallProposal(selection.tool_name, {}, True, (), self.module_version)


class ValidatedRepairCaller:
    module_version = "caller.1"

    def propose(
        self,
        context: AgentContext,
        plan: Plan,
        selection: Selection,
    ) -> ToolCallProposal:
        if selection.kind != "tool_call" or selection.tool_name is None:
            return ToolCallProposal("", {}, True, (), self.module_version)
        return ToolCallProposal(selection.tool_name, {}, True, (), self.module_version)


class EvidenceFirstSynthesizer:
    module_version = "synthesizer.0"

    def synthesize(
        self,
        context: AgentContext,
        plan: Plan,
        selection: Selection,
        tool_result: dict[str, Any] | None,
    ) -> str:
        if tool_result is None:
            return "目前缺少公开工具结果，无法确认任务已完成。"
        return "已根据公开工具结果更新任务状态。"


class StateReconcileSynthesizer:
    module_version = "synthesizer.1"

    def synthesize(
        self,
        context: AgentContext,
        plan: Plan,
        selection: Selection,
        tool_result: dict[str, Any] | None,
    ) -> str:
        if tool_result is None:
            return "公开状态尚未完整，下一步需要补充可见信息。"
        return "公开状态已对账，当前步骤已处理。"


def build_mock_modules(configuration: dict[str, int]) -> dict[str, object]:
    planners = (LinearPlanner, StateDependencyPlanner)
    selectors = (SchemaMatchSelector, PrerequisiteGateSelector)
    callers = (DirectSchemaCaller, ValidatedRepairCaller)
    synthesizers = (EvidenceFirstSynthesizer, StateReconcileSynthesizer)
    return {
        "planner": planners[configuration["planner"]](),
        "selector": selectors[configuration["selector"]](),
        "caller": callers[configuration["caller"]](),
        "synthesizer": synthesizers[configuration["synthesizer"]](),
    }
