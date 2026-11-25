"""DeepSeek Flash 的 OpenAI-compatible Chat Completions 客户端。"""

from __future__ import annotations

import json
import hashlib
import time
import uuid
from dataclasses import dataclass, field
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


class DeepSeekIdentityError(DeepSeekResponseError):
    pass


class DeepSeekBudgetExceeded(DeepSeekError):
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


@dataclass
class RequestBudget:
    max_requests: int
    max_input_tokens: int
    max_output_tokens: int
    max_cost_usd: float
    requests: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    episode_max_requests: int | None = None
    episode_max_input_tokens: int | None = None
    episode_max_output_tokens: int | None = None
    episode_max_cost_usd: float | None = None
    episode_usage: dict[str, dict[str, float]] = field(default_factory=dict)

    def reserve(
        self,
        *,
        input_upper: int,
        output_upper: int,
        cost_upper: float,
        episode_id: str | None = None,
        request_count: int = 1,
    ) -> None:
        if input_upper < 0 or output_upper < 0 or cost_upper < 0 or request_count < 1:
            raise ValueError("预算预留值不能为负数")
        if self.requests + request_count > self.max_requests:
            raise DeepSeekBudgetExceeded("请求次数硬限制已达到")
        if self.input_tokens + input_upper * request_count > self.max_input_tokens:
            raise DeepSeekBudgetExceeded("输入 token 硬限制已达到")
        if self.output_tokens + output_upper * request_count > self.max_output_tokens:
            raise DeepSeekBudgetExceeded("输出 token 硬限制已达到")
        if self.cost_usd + cost_upper * request_count > self.max_cost_usd:
            raise DeepSeekBudgetExceeded("成本硬限制已达到")
        if episode_id is not None:
            usage = self.episode_usage.setdefault(
                episode_id,
                {"requests": 0.0, "input_tokens": 0.0, "output_tokens": 0.0, "cost_usd": 0.0},
            )
            if self.episode_max_requests is not None and usage["requests"] + request_count > self.episode_max_requests:
                raise DeepSeekBudgetExceeded("单 episode 请求次数硬限制已达到")
            if (
                self.episode_max_input_tokens is not None
                and usage["input_tokens"] + input_upper * request_count > self.episode_max_input_tokens
            ):
                raise DeepSeekBudgetExceeded("单 episode 输入 token 硬限制已达到")
            if (
                self.episode_max_output_tokens is not None
                and usage["output_tokens"] + output_upper * request_count > self.episode_max_output_tokens
            ):
                raise DeepSeekBudgetExceeded("单 episode 输出 token 硬限制已达到")
            if (
                self.episode_max_cost_usd is not None
                and usage["cost_usd"] + cost_upper * request_count > self.episode_max_cost_usd
            ):
                raise DeepSeekBudgetExceeded("单 episode 成本硬限制已达到")
        self.requests += request_count
        self.input_tokens += input_upper * request_count
        self.output_tokens += output_upper * request_count
        self.cost_usd += cost_upper * request_count
        if episode_id is not None:
            usage["requests"] += request_count
            usage["input_tokens"] += input_upper * request_count
            usage["output_tokens"] += output_upper * request_count
            usage["cost_usd"] += cost_upper * request_count


class ModelFingerprintTracker:
    """检测同一批次内 system_fingerprint 变化。"""

    def __init__(self) -> None:
        self.expected_model: str | None = None
        self.expected: str | None = None

    def observe(self, response: DeepSeekResponse) -> None:
        if response.model is None or response.system_fingerprint is None:
            raise DeepSeekIdentityError("响应缺少 model 或 system_fingerprint")
        if self.expected_model is None:
            self.expected_model = response.model
        elif response.model != self.expected_model:
            raise DeepSeekIdentityError(
                f"returned model 变化: expected={self.expected_model}, observed={response.model}"
            )
        fingerprint = response.system_fingerprint
        if self.expected is None:
            self.expected = fingerprint
            return
        if fingerprint != self.expected:
            raise DeepSeekIdentityError(
                f"system_fingerprint 变化: expected={self.expected}, observed={fingerprint}"
            )


def estimate_cost(
    usage: dict[str, int],
    *,
    input_usd_per_million: float,
    output_usd_per_million: float,
    cached_input_usd_per_million: float = 0.006,
) -> float:
    cache_hit = usage.get("prompt_cache_hit_tokens", 0)
    cache_miss = usage.get("prompt_cache_miss_tokens", usage.get("prompt_tokens", 0))
    return (
        cache_miss / 1_000_000 * input_usd_per_million
        + cache_hit / 1_000_000 * cached_input_usd_per_million
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
        max_retries: int = 1,
        retry_backoff_seconds: float = 1.0,
        max_input_tokens: int = 2_000,
        input_usd_per_million: float = 0.30,
        cached_input_usd_per_million: float = 0.006,
        output_usd_per_million: float = 1.20,
        budget: RequestBudget | None = None,
        identity_tracker: ModelFingerprintTracker | None = None,
        tokenizer_path: str | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("DeepSeekClient 需要显式 API key")
        if not base_url.startswith("https://api.deepseek.com"):
            raise ValueError("Phase 0C 要求 DeepSeek 直连官方 base URL")
        if max_input_tokens < 1 or max_output_tokens < 1:
            raise ValueError("token 上限必须为正数")
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.timeout_seconds = timeout_seconds
        self.max_retries = min(1, max(0, max_retries))
        self.retry_backoff_seconds = retry_backoff_seconds
        self.max_input_tokens = max_input_tokens
        self.input_usd_per_million = input_usd_per_million
        self.cached_input_usd_per_million = cached_input_usd_per_million
        self.output_usd_per_million = output_usd_per_million
        self.audit_events: list[dict[str, Any]] = []
        self.budget = budget
        self.identity_tracker = identity_tracker or ModelFingerprintTracker()
        self.tokenizer = None
        if tokenizer_path is not None:
            try:
                from tokenizers import Tokenizer

                self.tokenizer = Tokenizer.from_file(tokenizer_path)
            except Exception as exc:
                raise ValueError(f"无法加载 DeepSeek tokenizer: {tokenizer_path}") from exc
        self.episode_context: dict[str, Any] = {}
        self._last_attempts: list[dict[str, Any]] = []
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
            "thinking": {"type": "disabled"},
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
        input_material = {
            "messages": messages,
            "response_format": response_format,
            "tools": tools,
            "tool_choice": tool_choice,
        }
        serialized_input = json.dumps(input_material, ensure_ascii=False, sort_keys=True)
        input_upper = self._count_input_tokens(serialized_input)
        cost_upper = estimate_cost(
            {"prompt_tokens": input_upper, "completion_tokens": self.max_output_tokens},
            input_usd_per_million=self.input_usd_per_million,
            output_usd_per_million=self.output_usd_per_million,
        )
        parsed: DeepSeekResponse | None = None
        try:
            if input_upper > self.max_input_tokens:
                raise DeepSeekBudgetExceeded("请求输入超过保守 token 硬限制")
            if self.budget is not None:
                self.budget.reserve(
                    input_upper=input_upper,
                    output_upper=self.max_output_tokens,
                    cost_upper=cost_upper,
                    episode_id=self.episode_context.get("episode_id"),
                    request_count=self.max_retries + 1,
                )
            response = self._post_with_retries(headers=headers, payload=payload)
            parsed = self._parse_response(response)
            self.identity_tracker.observe(parsed)
        except DeepSeekError as exc:
            if not self._last_attempts:
                self._last_attempts = [{"attempt": 1, "status": "rejected", "delivery_status": "not_sent"}]
            self._record_attempt_events(
                client_request_id=client_request_id,
                prompt_hash=prompt_hash,
                input_upper=input_upper,
                cost_upper=cost_upper,
                response=parsed,
                error=exc,
            )
            raise
        self._record_attempt_events(
            client_request_id=client_request_id,
            prompt_hash=prompt_hash,
            input_upper=input_upper,
            cost_upper=cost_upper,
            response=parsed,
            error=None,
        )
        return parsed

    def _count_input_tokens(self, serialized_input: str) -> int:
        """使用 DeepSeek V4.1 tokenizer 计数，未配置时退回保守字节上界。"""

        if self.tokenizer is None:
            return len(serialized_input.encode("utf-8"))
        # Chat-template control tokens add a small fixed overhead. Reserve a
        # conservative margin while keeping the declared 2,000-token cap.
        return len(self.tokenizer.encode(serialized_input).ids) + 64

    def _record_attempt_events(
        self,
        *,
        client_request_id: str,
        prompt_hash: str,
        input_upper: int,
        cost_upper: float,
        response: DeepSeekResponse | None,
        error: DeepSeekError | None,
    ) -> None:
        attempts = self._last_attempts or [{"attempt": 1, "status": "success", "delivery_status": "delivered"}]
        actual_cost = (
            estimate_cost(
                response.usage,
                input_usd_per_million=self.input_usd_per_million,
                cached_input_usd_per_million=self.cached_input_usd_per_million,
                output_usd_per_million=self.output_usd_per_million,
            )
            if response is not None
            else 0.0
        )
        for index, attempt in enumerate(attempts):
            is_final = index == len(attempts) - 1
            event = {
                **self.episode_context,
                "request_id": (response.request_id if response is not None else None) or client_request_id,
                "client_request_id": client_request_id,
                "prompt_hash": prompt_hash,
                "requested_model": self.model,
                "returned_model": response.model if response is not None else None,
                "system_fingerprint": response.system_fingerprint if response is not None else None,
                "attempt": attempt.get("attempt", index + 1),
                "attempt_count": len(attempts),
                "status": attempt.get("status", "error") if error is None or not is_final else "infra_failed",
                "delivery_status": attempt.get("delivery_status", "unknown"),
                "http_status": attempt.get("http_status"),
                "usage": response.usage if response is not None and is_final else {},
                "response_content": (
                    response.content if response is not None and error is not None and is_final else None
                ),
                "input_token_upper_bound": input_upper if is_final else 0,
                "input_bound_method": (
                    "deepseek_v41_tokenizer_plus_64_margin"
                    if self.tokenizer is not None
                    else "utf8_serialized_request_bytes"
                ),
                "cost_upper_bound_usd": cost_upper if is_final else 0.0,
                "cost_usd": actual_cost if response is not None and is_final else 0.0,
                **({"error_type": type(error).__name__} if error is not None and is_final else {}),
            }
            self.audit_events.append(event)
        self._last_attempts = []

    def set_episode_context(self, **context: Any) -> None:
        self.episode_context = dict(context)

    def drain_audit_events(self) -> list[dict[str, Any]]:
        events = list(self.audit_events)
        self.audit_events.clear()
        return events

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
        attempts: list[dict[str, Any]] = []
        self._last_attempts = attempts
        for attempt in range(self.max_retries + 1):
            attempt_record = {"attempt": attempt + 1}
            try:
                response = self.http_client.post(
                    "/chat/completions",
                    headers=headers,
                    json=payload,
                )
            except httpx.TimeoutException as exc:
                # 超时可能已经扣费，默认不重试，避免重复扣费。
                attempt_record.update({"status": "error", "delivery_status": "unknown"})
                attempts.append(attempt_record)
                raise DeepSeekTimeoutError("DeepSeek 请求超时，未自动重试") from exc
            except httpx.RequestError as exc:
                if not isinstance(exc, httpx.ConnectError) or attempt >= self.max_retries:
                    attempt_record.update({"status": "error", "delivery_status": "unknown"})
                    attempts.append(attempt_record)
                    raise DeepSeekNetworkError("DeepSeek 网络错误，交付状态未知") from exc
                attempt_record.update({"status": "retry", "delivery_status": "not_delivered"})
                attempts.append(attempt_record)
                time.sleep(self.retry_backoff_seconds * (2**attempt))
                continue
            status = int(response.status_code)
            if status == 429:
                if attempt >= self.max_retries:
                    attempt_record.update({"status": "error", "delivery_status": "not_delivered", "http_status": status})
                    attempts.append(attempt_record)
                    raise DeepSeekRateLimitError("DeepSeek rate limit")
                attempt_record.update({"status": "retry", "delivery_status": "not_delivered", "http_status": status})
                attempts.append(attempt_record)
                time.sleep(self.retry_backoff_seconds * (2**attempt))
                continue
            if status >= 500:
                attempt_record.update({"status": "error", "delivery_status": "unknown", "http_status": status})
                attempts.append(attempt_record)
                raise DeepSeekAPIError(f"DeepSeek server error: {status}, delivery status unknown")
            if status >= 400:
                attempt_record.update({"status": "error", "delivery_status": "not_delivered", "http_status": status})
                attempts.append(attempt_record)
                raise DeepSeekAPIError(f"DeepSeek client error: {status}")
            attempt_record.update({"status": "success", "delivery_status": "delivered", "http_status": status})
            attempts.append(attempt_record)
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
            "prompt_cache_hit_tokens": int(usage_raw.get("prompt_cache_hit_tokens", 0)),
            "prompt_cache_miss_tokens": int(
                usage_raw.get("prompt_cache_miss_tokens", usage_raw.get("prompt_tokens", 0))
            ),
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
