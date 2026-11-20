import json
import unittest

import httpx

from nil_ccea.deepseek_client import (
    DeepSeekClient,
    DeepSeekResponseError,
    DeepSeekTimeoutError,
    ModelFingerprintTracker,
    estimate_cost,
    parse_json_content,
)


class FakeResponse:
    def __init__(self, payload, status_code=200, headers=None):
        self._payload = payload
        self.status_code = status_code
        self.headers = headers or {"x-request-id": "req-1"}

    def json(self):
        return self._payload


class FakeHttpClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def post(self, url, *, headers, json):
        self.calls.append({"url": url, "headers": headers, "json": json})
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def response_payload(content='{"ok":true}', *, tool_calls=None, fingerprint="fp-1"):
    message = {"role": "assistant", "content": content}
    if tool_calls is not None:
        message["tool_calls"] = tool_calls
    return {
        "id": "chatcmpl-1",
        "model": "deepseek-flash",
        "system_fingerprint": fingerprint,
        "choices": [{"message": message}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 4, "total_tokens": 14},
    }


class DeepSeekClientTests(unittest.TestCase):
    def test_json_request_parameters_and_usage(self):
        fake = FakeHttpClient([FakeResponse(response_payload())])
        client = DeepSeekClient(api_key="secret", http_client=fake, max_retries=0)
        result = client.complete_json([{"role": "user", "content": "x"}])
        request = fake.calls[0]
        self.assertEqual(request["url"], "/chat/completions")
        self.assertEqual(request["json"]["response_format"], {"type": "json_object"})
        self.assertEqual(request["json"]["temperature"], 0.0)
        self.assertEqual(request["json"]["max_tokens"], 512)
        self.assertEqual(request["json"]["thinking"], {"type": "disabled"})
        self.assertEqual(result.usage["total_tokens"], 14)
        self.assertEqual(fake.calls[0]["headers"]["Authorization"], "Bearer secret")
        self.assertEqual(client.audit_events[0]["status"], "success")
        self.assertEqual(len(client.audit_events[0]["prompt_hash"]), 64)

        direct = DeepSeekClient(api_key="secret", max_retries=0)
        try:
            self.assertFalse(direct.http_client._trust_env)
        finally:
            direct.close()

    def test_native_tool_call_and_invalid_json(self):
        tool_call = {"id": "tc-1", "type": "function", "function": {"name": "get_users", "arguments": "{}"}}
        fake = FakeHttpClient([FakeResponse(response_payload(content=None, tool_calls=[tool_call]))])
        client = DeepSeekClient(api_key="secret", http_client=fake, max_retries=0)
        result = client.complete_tools(
            [{"role": "user", "content": "x"}],
            tools=[{"type": "function", "function": {"name": "get_users", "parameters": {}}}],
            tool_choice={"type": "function", "function": {"name": "get_users"}},
        )
        self.assertEqual(result.tool_calls[0]["function"]["name"], "get_users")
        bad = DeepSeekClient(
            api_key="secret",
            http_client=FakeHttpClient([FakeResponse(response_payload(content="not-json"))]),
            max_retries=0,
        )
        with self.assertRaises(DeepSeekResponseError):
            parse_json_content(bad.complete_json([]))

    def test_timeout_is_not_retried_and_network_error_is_bounded(self):
        timeout_client = FakeHttpClient([httpx.TimeoutException("timeout")])
        client = DeepSeekClient(api_key="secret", http_client=timeout_client, max_retries=2)
        with self.assertRaises(DeepSeekTimeoutError):
            client.complete([])
        self.assertEqual(len(timeout_client.calls), 1)

        network_client = FakeHttpClient(
            [httpx.ConnectError("down"), FakeResponse(response_payload())]
        )
        client = DeepSeekClient(
            api_key="secret",
            http_client=network_client,
            max_retries=1,
            retry_backoff_seconds=0,
        )
        client.complete([])
        self.assertEqual(len(network_client.calls), 2)

    def test_fingerprint_tracker_and_cost(self):
        fake = FakeHttpClient([FakeResponse(response_payload())])
        client = DeepSeekClient(api_key="secret", http_client=fake, max_retries=0)
        response = client.complete([])
        tracker = ModelFingerprintTracker()
        tracker.observe(response)
        changed = response.__class__(**{**response.__dict__, "system_fingerprint": "changed"})
        with self.assertRaises(DeepSeekResponseError):
            tracker.observe(changed)
        self.assertAlmostEqual(
            estimate_cost(response.usage, input_usd_per_million=0.30, output_usd_per_million=1.20),
            0.0000078,
        )


if __name__ == "__main__":
    unittest.main()
