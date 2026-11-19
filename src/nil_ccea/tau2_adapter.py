"""τ²-bench HalfDuplexAgent 适配器草案。

该文件只负责把已定义的四模块契约接入 tau2 Agent API。实际 LLM 模块实现由
调用方注入，当前仓库没有在这里偷偷改变模型、工具权限或评分器。
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from .contracts import AgentContext, Caller, Planner, Selector, Synthesizer


class Tau2UnavailableError(RuntimeError):
    """当前解释器没有安装 tau2-bench。"""


@dataclass
class Tau2AgentState:
    messages: list[Any] = field(default_factory=list)
    plan_state: dict[str, Any] = field(default_factory=dict)
    module_events: list[dict[str, Any]] = field(default_factory=list)


def _tool_schema(tool: Any) -> dict[str, Any]:
    name = getattr(tool, "name", None)
    if name is None and hasattr(tool, "get_name"):
        name = tool.get_name()
    schema = getattr(tool, "parameters", None)
    if schema is None:
        schema = getattr(tool, "schema", None)
    return {"name": name, "parameters": schema or {}}


def build_tau2_agent_class():
    """延迟导入 tau2 并返回适配器类，便于无依赖环境执行静态测试。"""

    try:
        from tau2.agent.base_agent import HalfDuplexAgent
        from tau2.data_model.message import AssistantMessage, ToolCall
    except ImportError as exc:  # pragma: no cover - 取决于外部环境
        raise Tau2UnavailableError(
            "请在 tau2-bench v1.0.1 的 Python 环境中加载此适配器"
        ) from exc

    class Tau2FourModuleAgent(HalfDuplexAgent[Tau2AgentState]):
        """使用同一工具集合和 policy 的四模块 Agent。"""

        def __init__(
            self,
            tools: list[Any],
            domain_policy: str,
            *,
            planner: Planner,
            selector: Selector,
            caller: Caller,
            synthesizer: Synthesizer,
            task_id: str = "unknown",
            task_version: str = "unknown",
            task_family: str = "unknown",
        ) -> None:
            super().__init__(tools=tools, domain_policy=domain_policy)
            self.planner = planner
            self.selector = selector
            self.caller = caller
            self.synthesizer = synthesizer
            self.task_id = task_id
            self.task_version = task_version
            self.task_family = task_family
            self._tool_names = {
                schema["name"] for schema in (_tool_schema(tool) for tool in tools)
            }

        def get_init_state(self, message_history=None) -> Tau2AgentState:
            return Tau2AgentState(messages=list(message_history or []))

        def generate_next_message(self, message, state: Tau2AgentState):
            state.messages.append(message)
            context = AgentContext(
                task_id=self.task_id,
                task_version=self.task_version,
                task_family=self.task_family,
                visible_messages=tuple(
                    message.model_dump() if hasattr(message, "model_dump") else {"value": str(message)}
                    for message in state.messages
                ),
                domain_policy=self.domain_policy,
                tool_schemas=tuple(_tool_schema(tool) for tool in self.tools),
                step_index=len(state.messages),
                max_steps=30,
                plan_state=dict(state.plan_state),
            )
            plan = self.planner.plan(context)
            selection = self.selector.select(context, plan)
            proposal = self.caller.propose(context, plan, selection)
            state.module_events.extend(
                [
                    {"module": "planner", "version": plan.module_version},
                    {"module": "selector", "version": selection.module_version},
                    {"module": "caller", "version": proposal.module_version},
                ]
            )
            if selection.kind == "tool_call" and proposal.tool_name in self._tool_names:
                tool_call = ToolCall(
                    id=str(uuid.uuid4()),
                    name=proposal.tool_name,
                    arguments=proposal.arguments,
                    requestor="assistant",
                )
                response = AssistantMessage(role="assistant", tool_calls=[tool_call])
            else:
                result = None
                if getattr(message, "role", None) == "tool":
                    result = {"content": getattr(message, "content", None)}
                content = self.synthesizer.synthesize(context, plan, selection, result)
                response = AssistantMessage.text(content)
            state.messages.append(response)
            return response, state

    return Tau2FourModuleAgent


__all__ = ["Tau2AgentState", "Tau2UnavailableError", "build_tau2_agent_class"]
