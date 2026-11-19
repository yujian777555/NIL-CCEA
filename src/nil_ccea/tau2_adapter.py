"""τ²-bench v1.0.1 的四模块 HalfDuplexAgent 适配器。"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from .contracts import AgentContext, Caller, Planner, Selector, Synthesizer


class Tau2UnavailableError(RuntimeError):
    """当前解释器没有安装固定版本 tau2-bench。"""


class InvalidToolCallError(RuntimeError):
    """模块生成了无效或越权的工具调用。"""


@dataclass
class Tau2AgentState:
    messages: list[Any] = field(default_factory=list)
    plan_state: dict[str, Any] = field(default_factory=dict)
    module_events: list[dict[str, Any]] = field(default_factory=list)


def _get_tool_name(tool: Any) -> str | None:
    if hasattr(tool, "name"):
        return str(tool.name)
    if hasattr(tool, "get_name"):
        return str(tool.get_name())
    return None


def _get_openai_schema(tool: Any) -> dict[str, Any]:
    """读取 tau2 Tool 的真实 openai_schema，不依赖猜测属性。"""

    schema = getattr(tool, "openai_schema", None)
    if isinstance(schema, dict):
        return schema
    raise InvalidToolCallError(f"工具缺少 openai_schema: {tool!r}")


def _tool_schema(tool: Any) -> dict[str, Any]:
    schema = _get_openai_schema(tool)
    function = schema.get("function")
    if not isinstance(function, dict) or not function.get("name"):
        raise InvalidToolCallError(f"openai_schema 缺少 function.name: {schema!r}")
    parameters = function.get("parameters")
    if not isinstance(parameters, dict):
        raise InvalidToolCallError(f"openai_schema 缺少 function.parameters: {schema!r}")
    return {
        "name": function["name"],
        "description": function.get("description", ""),
        "parameters": parameters,
    }


def _validate_arguments(tool: Any, arguments: dict[str, Any]) -> dict[str, Any]:
    """使用 tau2 Tool.params 的 Pydantic 模型验证并规范化参数。"""

    params_model = getattr(tool, "params", None)
    if params_model is None:
        raise InvalidToolCallError(f"工具缺少 params 模型: {_get_tool_name(tool)}")
    try:
        if hasattr(params_model, "model_validate"):
            validated = params_model.model_validate(arguments)
            return validated.model_dump()
        if hasattr(params_model, "parse_obj"):
            validated = params_model.parse_obj(arguments)
            return validated.dict()
    except Exception as exc:
        raise InvalidToolCallError(
            f"工具参数 schema 校验失败: tool={_get_tool_name(tool)}, arguments={arguments!r}"
        ) from exc
    raise InvalidToolCallError(f"不支持的 params 模型: {_get_tool_name(tool)}")


def build_tau2_agent_class():
    """延迟导入 tau2，避免无 tau2 环境误报通过。"""

    try:
        from tau2.agent.base_agent import HalfDuplexAgent
        from tau2.data_model.message import (
            AssistantMessage,
            MultiToolMessage,
            ToolCall,
            ToolMessage,
        )
    except ImportError as exc:  # pragma: no cover - 取决于独立 tau2 环境
        raise Tau2UnavailableError(
            "请在 tau2-bench v1.0.1 的 Python 3.12 或 3.13 环境中加载此适配器"
        ) from exc

    class Tau2FourModuleAgent(HalfDuplexAgent[Tau2AgentState]):
        """四模块实现，共享 tau2 传入的 tools 和 domain_policy。"""

        def __init__(
            self,
            tools: list[Any],
            domain_policy: str,
            *,
            planner: Planner,
            selector: Selector,
            caller: Caller,
            synthesizer: Synthesizer,
            task_id: str,
            task_version: str,
            task_family: str,
        ) -> None:
            if not all((task_id, task_version, task_family)):
                raise ValueError("task_id、task_version、task_family 必须显式注入")
            super().__init__(tools=tools, domain_policy=domain_policy)
            self.planner = planner
            self.selector = selector
            self.caller = caller
            self.synthesizer = synthesizer
            self.task_id = task_id
            self.task_version = task_version
            self.task_family = task_family
            self.seed: int | None = None
            self._tools_by_name: dict[str, Any] = {}
            self._tool_schemas: list[dict[str, Any]] = []
            for tool in tools:
                schema = _tool_schema(tool)
                name = schema["name"]
                if name in self._tools_by_name:
                    raise ValueError(f"重复工具名: {name}")
                self._tools_by_name[name] = tool
                self._tool_schemas.append(schema)

        def set_seed(self, seed: int) -> None:
            """保存 orchestrator 注入的 seed，供模块上下文和 manifest 追踪。"""

            self.seed = int(seed)

        def get_init_state(self, message_history=None) -> Tau2AgentState:
            return Tau2AgentState(messages=list(message_history or []))

        @staticmethod
        def _tool_results(message: Any) -> list[dict[str, Any]]:
            if isinstance(message, ToolMessage):
                return [{"id": message.id, "content": message.content, "error": message.error}]
            if isinstance(message, MultiToolMessage):
                return [
                    {"id": item.id, "content": item.content, "error": item.error}
                    for item in message.tool_messages
                ]
            return []

        @staticmethod
        def _message_dump(message: Any) -> dict[str, Any]:
            if hasattr(message, "model_dump"):
                return message.model_dump()
            return {"value": str(message)}

        def generate_next_message(self, message, state: Tau2AgentState):
            tool_results = self._tool_results(message)
            if isinstance(message, MultiToolMessage):
                state.messages.extend(message.tool_messages)
            else:
                state.messages.append(message)
            state.plan_state["last_tool_results"] = tool_results
            state.plan_state["public_state_ready"] = bool(tool_results)
            state.plan_state["environment_seed"] = self.seed
            context = AgentContext(
                task_id=self.task_id,
                task_version=self.task_version,
                task_family=self.task_family,
                visible_messages=tuple(self._message_dump(item) for item in state.messages),
                domain_policy=self.domain_policy,
                tool_schemas=tuple(self._tool_schemas),
                step_index=len(state.messages),
                max_steps=30,
                plan_state=dict(state.plan_state),
            )
            plan = self.planner.plan(context)
            state.plan_state["last_plan"] = {
                "goals": plan.goals,
                "termination_condition": plan.termination_condition,
                "unknowns": plan.unknowns,
                "module_version": plan.module_version,
            }
            selection = self.selector.select(context, plan)
            proposal = self.caller.propose(context, plan, selection)
            state.module_events.extend(
                [
                    {"module": "planner", "version": plan.module_version},
                    {"module": "selector", "version": selection.module_version},
                    {"module": "caller", "version": proposal.module_version},
                ]
            )
            state.plan_state["last_selection"] = {
                "kind": selection.kind,
                "tool_name": selection.tool_name,
                "goal_id": selection.goal_id,
                "reason_code": selection.reason_code,
                "module_version": selection.module_version,
            }
            if selection.kind == "tool_call":
                if selection.tool_name is None:
                    raise InvalidToolCallError("Selector 返回 tool_call 但没有 tool_name")
                if proposal.tool_name != selection.tool_name:
                    raise InvalidToolCallError(
                        f"Selector/Caller 工具不一致: selected={selection.tool_name}, proposed={proposal.tool_name}"
                    )
                tool = self._tools_by_name.get(selection.tool_name)
                if tool is None:
                    raise InvalidToolCallError(f"Selector 选择了未授权工具: {selection.tool_name}")
                arguments = _validate_arguments(tool, proposal.arguments)
                tool_call = ToolCall(
                    id=str(uuid.uuid4()),
                    name=selection.tool_name,
                    arguments=arguments,
                    requestor="assistant",
                )
                response = AssistantMessage(role="assistant", tool_calls=[tool_call])
            elif selection.kind in {"respond", "stop"}:
                content = self.synthesizer.synthesize(
                    context, plan, selection, tool_results[-1] if tool_results else None
                )
                if not isinstance(content, str) or not content.strip():
                    raise InvalidToolCallError("Synthesizer 返回空文本")
                response = AssistantMessage.text(content)
            else:
                raise InvalidToolCallError(f"Selector 返回未知动作类型: {selection.kind}")
            state.messages.append(response)
            return response, state

    return Tau2FourModuleAgent


__all__ = [
    "InvalidToolCallError",
    "Tau2AgentState",
    "Tau2UnavailableError",
    "build_tau2_agent_class",
    "_get_openai_schema",
    "_tool_schema",
    "_validate_arguments",
]
