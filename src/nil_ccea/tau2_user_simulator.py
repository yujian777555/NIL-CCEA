"""受控 DeepSeek Flash tau2 半双工 User Simulator 适配器。"""

from __future__ import annotations

import json
from typing import Any

from .deepseek_client import DeepSeekClient, DeepSeekResponseError, estimate_cost

try:
    from tau2.data_model.message import (
        AssistantMessage,
        Message,
        MultiToolMessage,
        SystemMessage,
        ToolCall,
        ToolMessage,
        UserMessage,
    )
    from tau2.data_model.persona import PersonaConfig
    from tau2.environment.tool import Tool
    from tau2.user.user_simulator import UserSimulator
except ImportError as exc:  # pragma: no cover - exercised only without tau2
    TAU2_AVAILABLE = False
    _TAU2_IMPORT_ERROR = exc

    class DeepSeekTau2UserSimulator:
        """外部 tau2 未安装时的显式依赖门。"""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise ImportError("DeepSeekTau2UserSimulator 需要 tau2-bench v1.0.1") from _TAU2_IMPORT_ERROR

else:
    TAU2_AVAILABLE = True

    def _message_to_openai(message: Message) -> dict[str, Any]:
        """将 tau2 消息转换为 DeepSeek Chat Completions 消息。"""

        if isinstance(message, SystemMessage):
            return {"role": "system", "content": message.content or ""}
        if isinstance(message, UserMessage):
            return {"role": "user", "content": message.content}
        if isinstance(message, AssistantMessage):
            payload: dict[str, Any] = {
                "role": "assistant",
                "content": message.content,
            }
            if message.tool_calls:
                payload["tool_calls"] = [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.name,
                            "arguments": json.dumps(call.arguments, ensure_ascii=False),
                        },
                    }
                    for call in message.tool_calls
                ]
            return payload
        if isinstance(message, ToolMessage):
            return {
                "role": "tool",
                "content": message.content or "",
                "tool_call_id": message.id,
            }
        raise DeepSeekResponseError(f"User Simulator 收到不支持的消息类型: {type(message).__name__}")


    def _compact_openai_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """保留系统指令与最近对话，确保 User Simulator 输入受控。"""

        system = next((item for item in messages if item.get("role") == "system"), None)
        history = [item for item in messages if item.get("role") != "system"][-6:]
        compact: list[dict[str, Any]] = []
        if system is not None:
            compact.append({**system, "content": str(system.get("content", ""))[:1400]})
        for item in history:
            value = dict(item)
            if isinstance(value.get("content"), str):
                value["content"] = value["content"][:500]
            compact.append(value)
        return compact


    class DeepSeekTau2UserSimulator(UserSimulator):
        """保持 tau2 UserSimulator 接口并强制使用 NIL-CCEA DeepSeekClient。"""

        def __init__(
            self,
            *,
            client: DeepSeekClient,
            instructions: str,
            tools: list[Tool] | None = None,
            persona_config: PersonaConfig | None = None,
        ) -> None:
            self.client = client
            super().__init__(
                llm="deepseek-flash",
                instructions=instructions,
                tools=tools,
                llm_args={},
                persona_config=persona_config,
            )

        def _validate_user_tool_call(self, name: str, arguments: dict[str, Any]) -> None:
            tool = next((item for item in self.tools or [] if item.name == name), None)
            if tool is None:
                raise DeepSeekResponseError(f"User Simulator 调用了未授权工具: {name}")
            try:
                if hasattr(tool.params, "model_validate"):
                    tool.params.model_validate(arguments)
                else:  # pragma: no cover - tau2 v1.0.1 使用 pydantic v2
                    tool.params.parse_obj(arguments)
            except Exception as exc:
                raise DeepSeekResponseError(f"User Simulator 工具参数无效: {name}") from exc

        def _generate_next_message(self, message: Any, state: Any) -> UserMessage:
            if isinstance(message, AssistantMessage) and message.is_audio:
                raise ValueError("Assistant message cannot be audio. Use VoiceUserSimulator instead.")
            if isinstance(message, MultiToolMessage):
                state.messages.extend(message.tool_messages)
            elif isinstance(message, ToolMessage):
                state.messages.append(message)
            elif message.has_content() or message.is_tool_call():
                state.messages.append(message)

            messages = state.system_messages + state.flip_roles()
            openai_messages = _compact_openai_messages(
                [_message_to_openai(item) for item in messages]
            )
            schemas = [tool.openai_schema for tool in self.tools or []]
            if schemas:
                response = self.client.complete_tools(openai_messages, tools=schemas)
            else:
                response = self.client.complete(openai_messages)

            tool_calls: list[ToolCall] = []
            for raw_call in response.tool_calls:
                function = raw_call.get("function", raw_call)
                name = function.get("name")
                arguments = function.get("arguments", {})
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError as exc:
                        raise DeepSeekResponseError("User Simulator tool arguments 不是合法 JSON") from exc
                if not isinstance(name, str) or not isinstance(arguments, dict):
                    raise DeepSeekResponseError("User Simulator tool call 结构无效")
                self._validate_user_tool_call(name, arguments)
                tool_calls.append(
                    ToolCall(
                        id=str(raw_call.get("id", "")),
                        name=name,
                        arguments=arguments,
                        requestor="user",
                    )
                )

            cost = estimate_cost(
                response.usage,
                input_usd_per_million=self.client.input_usd_per_million,
                cached_input_usd_per_million=self.client.cached_input_usd_per_million,
                output_usd_per_million=self.client.output_usd_per_million,
            )
            return UserMessage(
                role="user",
                content=response.content,
                tool_calls=tool_calls or None,
                cost=cost,
                usage=response.usage,
                raw_data=response.raw_response,
            )


def build_deepseek_tau2_user_simulator(
    *,
    client: DeepSeekClient,
    task: Any,
    tools: list[Any] | None = None,
) -> Any:
    """从 tau2 Task 构造 provider-backed User Simulator。"""

    if not TAU2_AVAILABLE:
        raise ImportError("构造 User Simulator 需要 tau2-bench v1.0.1")
    return DeepSeekTau2UserSimulator(
        client=client,
        instructions=str(task.user_scenario),
        tools=tools,
    )

