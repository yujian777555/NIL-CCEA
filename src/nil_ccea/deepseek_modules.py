"""四个 DeepSeek Flash 模块。"""

from __future__ import annotations

import json
from typing import Any

from .contracts import AgentContext, Plan, Selection, ToolCallProposal
from .deepseek_client import DeepSeekClient, DeepSeekResponseError, parse_json_content


def _compact_text(value: Any, limit: int = 3500) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return text if len(text) <= limit else text[:limit] + "…"


def _compact_messages(messages: tuple[dict[str, Any], ...], limit: int = 3) -> list[dict[str, Any]]:
    selected = list(messages[-limit:])
    return [
        {
            **message,
            "content": _compact_text(message.get("content", ""), 300),
        }
        for message in selected
    ]


def _compact_tool_schemas(
    schemas: tuple[dict[str, Any], ...], *, selected_name: str | None = None
) -> list[dict[str, Any]]:
    selected = [schema for schema in schemas if selected_name is None or schema.get("name") == selected_name]
    if selected_name is None:
        return [
            {"name": schema.get("name"), "description": _compact_text(schema.get("description", ""), 120)}
            for schema in selected
        ]

    def strip_descriptions(value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: strip_descriptions(item)
                for key, item in value.items()
                if key != "description"
            }
        if isinstance(value, list):
            return [strip_descriptions(item) for item in value]
        return value

    return [strip_descriptions(selected[0])] if selected else []


def _context_payload(
    context: AgentContext, *, selected_tool_name: str | None = None, compact: bool = False
) -> dict[str, Any]:
    return {
        "task_id": context.task_id,
        "task_version": context.task_version,
        "task_family": context.task_family,
        "visible_messages": _compact_messages(
            context.visible_messages, limit=1 if compact else 3
        ),
        "domain_policy": _compact_text(context.domain_policy, 300 if compact else 1200),
        "tool_schemas": _compact_tool_schemas(
            context.tool_schemas, selected_name=selected_tool_name
        ),
        "step_index": context.step_index,
        "max_steps": context.max_steps,
        "plan_state": _compact_text(context.plan_state, 300 if compact else 600),
    }


class DeepSeekPlanner:
    def __init__(self, client: DeepSeekClient, variant: int = 0) -> None:
        self.client = client
        self.variant = variant
        self.module_version = f"planner.deepseek-flash.p{variant}.v1"

    def plan(self, context: AgentContext) -> Plan:
        response = self.client.complete_json(
            [
                {
                    "role": "system",
                    "content": (
                        f"你是 Planner 变体 P{self.variant}。只输出 JSON 对象，字段为 goals、"
                        "termination_condition、unknowns。不得读取隐藏评测信息。"
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        _context_payload(context, compact=True), ensure_ascii=False
                    ),
                },
            ]
        )
        value = parse_json_content(response)
        goals = value.get("goals")
        unknowns = value.get("unknowns", [])
        termination = value.get("termination_condition", "")
        if not isinstance(goals, list) or not isinstance(unknowns, list) or not isinstance(termination, str):
            raise DeepSeekResponseError("Planner JSON 契约无效")
        return Plan(tuple(goals), termination, tuple(str(item) for item in unknowns), self.module_version)


class DeepSeekSelector:
    def __init__(self, client: DeepSeekClient, variant: int = 0) -> None:
        self.client = client
        self.variant = variant
        self.module_version = f"selector.deepseek-flash.p{variant}.v1"

    def select(self, context: AgentContext, plan: Plan) -> Selection:
        payload = {"context": _context_payload(context, compact=True), "plan": plan.__dict__}
        response = self.client.complete_json(
            [
                {
                    "role": "system",
                    "content": (
                        f"你是 Selector 变体 S{self.variant}。只输出 JSON。kind 只能是 tool_call、respond 或 stop。"
                        "tool_call 时必须选择 tool_schemas 中的工具名。"
                    ),
                },
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ]
        )
        value = parse_json_content(response)
        if isinstance(value.get("content"), dict):
            value = {**value, **value["content"]}
        kind = value.get("kind")
        if kind is None and value.get("action") in {"tool_call", "respond", "stop"}:
            kind = value["action"]
        if kind is None and value.get("type") in {"tool_call", "respond", "stop"}:
            kind = value["type"]
        if kind is None and isinstance(value.get("content"), str):
            kind = "respond"
        if kind not in {"tool_call", "respond", "stop"}:
            raise DeepSeekResponseError("Selector kind 无效")
        tool_name = value.get("tool_name", value.get("name", value.get("tool")))
        if tool_name is not None and not isinstance(tool_name, str):
            raise DeepSeekResponseError("Selector tool_name 无效")
        return Selection(
            kind=kind,
            tool_name=tool_name,
            goal_id=value.get("goal_id"),
            reason_code=str(value.get("reason_code", "model")),
            module_version=self.module_version,
        )


class DeepSeekCaller:
    def __init__(self, client: DeepSeekClient, variant: int = 0) -> None:
        self.client = client
        self.variant = variant
        self.module_version = f"caller.deepseek-flash.p{variant}.v1"

    def propose(self, context: AgentContext, plan: Plan, selection: Selection) -> ToolCallProposal:
        if selection.kind != "tool_call":
            return ToolCallProposal("", {}, True, (), self.module_version)
        schema = next(
            (item for item in context.tool_schemas if item.get("name") == selection.tool_name),
            None,
        )
        if schema is None:
            raise DeepSeekResponseError("Caller 收到未授权工具")
        native_tool = {"type": "function", "function": schema}
        response = self.client.complete_tools(
            [
                {
                    "role": "system",
                    "content": f"你是 Caller 变体 C{self.variant}。只能生成所选工具的一次合法调用。",
                },
                {
                    "role": "user",
                    "content": json.dumps(
                            {
                                "context": _context_payload(
                                    context,
                                    selected_tool_name=selection.tool_name,
                                    compact=True,
                                ),
                                "plan": plan.__dict__,
                                "selection": selection.__dict__,
                            },
                        ensure_ascii=False,
                    ),
                },
            ],
            tools=[native_tool],
            tool_choice={"type": "function", "function": {"name": selection.tool_name}},
        )
        if len(response.tool_calls) != 1:
            raise DeepSeekResponseError("Caller 必须返回恰好一个 tool call")
        call = response.tool_calls[0]
        function = call.get("function", call)
        name = function.get("name")
        arguments = function.get("arguments", {})
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError as exc:
                raise DeepSeekResponseError("Caller arguments 不是合法 JSON") from exc
        if name != selection.tool_name or not isinstance(arguments, dict):
            raise DeepSeekResponseError("Caller 工具名或参数结构不一致")
        return ToolCallProposal(name, arguments, True, (), self.module_version)


class DeepSeekSynthesizer:
    def __init__(self, client: DeepSeekClient, variant: int = 0) -> None:
        self.client = client
        self.variant = variant
        self.module_version = f"synthesizer.deepseek-flash.p{variant}.v1"

    def synthesize(
        self,
        context: AgentContext,
        plan: Plan,
        selection: Selection,
        tool_result: dict[str, Any] | None,
    ) -> str:
        response = self.client.complete_json(
            [
                {
                    "role": "system",
                    "content": f"你是 Synthesizer 变体 Y{self.variant}。只输出 JSON 对象，字段为 content。不得编造工具结果。",
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "context": _context_payload(context, compact=True),
                            "plan": plan.__dict__,
                            "selection": selection.__dict__,
                            "tool_result": _compact_text(tool_result, 500),
                        },
                        ensure_ascii=False,
                    ),
                },
            ]
        )
        value = parse_json_content(response)
        content = value.get("content")
        if not isinstance(content, str) or not content.strip():
            raise DeepSeekResponseError("Synthesizer content 无效")
        return content


def build_deepseek_modules(client: DeepSeekClient, configuration: dict[str, int]) -> dict[str, object]:
    """按照四个二元位构造真实 DeepSeek 模块。"""

    return {
        "planner": DeepSeekPlanner(client, configuration["planner"]),
        "selector": DeepSeekSelector(client, configuration["selector"]),
        "caller": DeepSeekCaller(client, configuration["caller"]),
        "synthesizer": DeepSeekSynthesizer(client, configuration["synthesizer"]),
    }


def build_deepseek_modules_by_client(
    clients: dict[str, DeepSeekClient], configuration: dict[str, int]
) -> dict[str, object]:
    """使用四个独立客户端构造四个模块。"""

    expected = {"planner", "selector", "caller", "synthesizer"}
    if set(clients) != expected:
        raise ValueError(f"模块客户端槽位必须恰好为 {sorted(expected)}")
    if len({id(client) for client in clients.values()}) != len(expected):
        raise ValueError("四个模块必须使用四个不同的 DeepSeekClient")
    return {
        "planner": DeepSeekPlanner(clients["planner"], configuration["planner"]),
        "selector": DeepSeekSelector(clients["selector"], configuration["selector"]),
        "caller": DeepSeekCaller(clients["caller"], configuration["caller"]),
        "synthesizer": DeepSeekSynthesizer(
            clients["synthesizer"], configuration["synthesizer"]
        ),
    }
