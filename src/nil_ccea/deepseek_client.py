"""DeepSeek Flash 的 OpenAI-compatible Chat Completions 客户端。"""

from __future__ import annotations

import json
import hashlib
import time
import uuid
from dataclasses import dataclass
from typing import Any, Protocol

import httpx


class DeepSeekError(RuntimeError):
    """DeepSeek 请求基类异常。"""


class DeepSeekNetworkError(DeepSeekError):
    pass


class DeepSeekTimeoutError(DeepSeekError):
    pass


class DeepSeekRateLimitError(DeepSeekError):
    pass


class DeepSeekAPIError(DeepSeekError):
    pass


class DeepSeekResponseError(DeepSeekError):
    pass


class HttpClientProtocol(Protocol):
    def post(self, url: str, *, headers: dict[str, str], json: dict[str, Any]) -> Any:
        ...


@dataclass(frozen=True)
class DeepSeekResponse:
    request_id: str | None
    model: str | None
    system_fingerprint: str | None
    content: str | None
    tool_calls: list[dict[str, Any]]
    usage: dict[str, int]
    raw_response: dict[str, Any]


class ModelFingerprintTracker:
    """检测同一批次内 system_fingerprint 变化。"""

    def __init__(self) -> None:
        self.expected: str | None = None

    def observe(self, response: DeepSeekResponse) -> None:
        fingerprint = response.system_fingerprint
        if fingerprint is None:
            return
        if self.expected is None:
            self.expected = fingerprint
            return
        if fingerprint != self.expected:
            raise DeepSeekResponseError(
                f"system_fingerprint 变化: expected={self.expected}, observed={fingerprint}"
            )


def estimate_cost(
    usage: dict[str, int], *, input_usd_per_million: float, output_usd_per_million: float
) -> float:
    return (
        usage.get("prompt_tokens", 0) / 1_000_000 * input_usd_per_million
        + usage.get("completion_tokens", 0) / 1_000_000 * output_usd_per_million
    )


class DeepSeekClient:
    def __init__(
        self,
        *,
        api_key: str,
        model: str = "deepseek-flash",
        base_url: str = "https://api.deepseek.com",
        temperature: float = 0.0,
        max_output_tokens: int = 512,
        timeout_seconds: float = 60.0,
        http_client: HttpClientProtocol | None = None,
        max_retries: int = 2,
        retry_backoff_seconds: float = 1.0,
        input_usd_per_million: float = 0.30,
        output_usd_per_million: float = 1.20,
    ) -> None:
        if not api_key:
            raise ValueError("DeepSeekClient 需要显式 API key")
        if not base_url.startswith("https://api.deepseek.com"):
            raise ValueError("Phase 0C 要求 DeepSeek 直连官方 base URL")
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.timeout_seconds = timeout_seconds
        self.max_retries = max(0, max_retries)
        self.retry_backoff_seconds = retry_backoff_seconds
        self.input_usd_per_million = input_usd_per_million
        self.output_usd_per_million = output_usd_per_million
        self.audit_events: list[dict[str, Any]] = []
        self._owns_http_client = http_client is None
        self.http_client = http_client or httpx.Client(
            base_url=self.base_url,
            timeout=httpx.Timeout(timeout_seconds),
            trust_env=False,
        )

    def close(self) -> None:
        if self._owns_http_client and hasattr(self.http_client, "close"):
            self.http_client.close()

    def __enter__(self) -> "DeepSeekClient":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    def complete(
        self,
        messages: list[dict[str, Any]],
        *,
        response_format: dict[str, str] | None = None,
        tools: list[dict[str, Any]] | None = None,
        tool_choice: dict[str, Any] | str | None = None,
        request_id: str | None = None,
    ) -> DeepSeekResponse:
        client_request_id = request_id or str(uuid.uuid4())
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_output_tokens,
            "stream": False,
        }
        if response_format is not None:
            payload["response_format"] = response_format
        if tools is not None:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        headers["X-Client-Request-Id"] = client_request_id
        prompt_hash = hashlib.sha256(
            json.dumps(messages, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        try:
            response = self._post_with_retries(headers=headers, payload=payload)
            parsed = self._parse_response(response)
        except DeepSeekError as exc:
            self.audit_events.append(
                {
                    "request_id": client_request_id,
                    "prompt_hash": prompt_hash,
                    "status": "error",
                    "error_type": type(exc).__name__,
                }
            )
            raise
        self.audit_events.append(
            {
                "request_id": parsed.request_id or client_request_id,
                "client_request_id": client_request_id,
                "prompt_hash": prompt_hash,
                "status": "success",
                "model": parsed.model,
                "system_fingerprint": parsed.system_fingerprint,
                "usage": parsed.usage,
                "cost_usd": estimate_cost(
                    parsed.usage,
                    input_usd_per_million=self.input_usd_per_million,
                    output_usd_per_million=self.output_usd_per_million,
                ),
            }
        )
        return parsed

    def complete_json(
        self, messages: list[dict[str, Any]], *, request_id: str | None = None
    ) -> DeepSeekResponse:
        return self.complete(
            messages,
            response_format={"type": "json_object"},
            request_id=request_id,
        )

    def complete_tools(
        self,
        messages: list[dict[str, Any]],
        *,
        tools: list[dict[str, Any]],
        tool_choice: dict[str, Any] | str | None = None,
        request_id: str | None = None,
    ) -> DeepSeekResponse:
        return self.complete(
            messages,
            tools=tools,
            tool_choice=tool_choice,
            request_id=request_id,
        )

    def _post_with_retries(
        self, *, headers: dict[str, str], payload: dict[str, Any]
    ) -> Any:
        for attempt in range(self.max_retries + 1):
            try:
                response = self.http_client.post(
                    "/chat/completions",
                    headers=headers,
                    json=payload,
                )
            except httpx.TimeoutException as exc:
                # 超时可能已经扣费，默认不重试，避免重复扣费。
                raise DeepSeekTimeoutError("DeepSeek 请求超时，未自动重试") from exc
            except httpx.RequestError as exc:
                if attempt >= self.max_retries:
                    raise DeepSeekNetworkError(str(exc)) from exc
                time.sleep(self.retry_backoff_seconds * (2**attempt))
                continue
            status = int(response.status_code)
            if status == 429:
                if attempt >= self.max_retries:
                    raise DeepSeekRateLimitError("DeepSeek rate limit")
                time.sleep(self.retry_backoff_seconds * (2**attempt))
                continue
            if status >= 500:
                if attempt >= self.max_retries:
                    raise DeepSeekAPIError(f"DeepSeek server error: {status}")
                time.sleep(self.retry_backoff_seconds * (2**attempt))
                continue
            if status >= 400:
                raise DeepSeekAPIError(f"DeepSeek client error: {status}")
            return response
        raise DeepSeekNetworkError("DeepSeek 请求未返回")

    @staticmethod
    def _parse_response(response: Any) -> DeepSeekResponse:
        try:
            payload = response.json()
        except Exception as exc:
            raise DeepSeekResponseError("DeepSeek 返回非 JSON") from exc
        if not isinstance(payload, dict):
            raise DeepSeekResponseError("DeepSeek 返回结构不是对象")
        try:
            choice = payload["choices"][0]
            message = choice["message"]
        except (KeyError, IndexError, TypeError) as exc:
            raise DeepSeekResponseError("DeepSeek 返回缺少 choices[0].message") from exc
        usage_raw = payload.get("usage") or {}
        usage = {
            "prompt_tokens": int(usage_raw.get("prompt_tokens", 0)),
            "completion_tokens": int(usage_raw.get("completion_tokens", 0)),
            "total_tokens": int(usage_raw.get("total_tokens", 0)),
        }
        tool_calls = message.get("tool_calls") or []
        if not isinstance(tool_calls, list):
            raise DeepSeekResponseError("tool_calls 不是列表")
        return DeepSeekResponse(
            request_id=response.headers.get("x-request-id") or payload.get("id"),
            model=payload.get("model"),
            system_fingerprint=payload.get("system_fingerprint"),
            content=message.get("content"),
            tool_calls=tool_calls,
            usage=usage,
            raw_response=payload,
        )


def parse_json_content(response: DeepSeekResponse) -> dict[str, Any]:
    if not response.content:
        raise DeepSeekResponseError("JSON 模式返回为空")
    try:
        value = json.loads(response.content)
    except json.JSONDecodeError as exc:
        raise DeepSeekResponseError("JSON 模式返回无法解析") from exc
    if not isinstance(value, dict):
        raise DeepSeekResponseError("JSON 模式返回必须是对象")
    return value
