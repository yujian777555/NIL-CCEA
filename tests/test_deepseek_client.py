import json
import unittest

import httpx

from nil_ccea.deepseek_client import (
    DeepSeekClient,
    DeepSeekAPIError,
    DeepSeekBudgetExceeded,
    DeepSeekResponseError,
    DeepSeekTimeoutError,
    ModelFingerprintTracker,
    RequestBudget,
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
        self.assertEqual(client.audit_events[0]["status"], "retry")
        self.assertEqual(client.audit_events[1]["attempt"], 2)

        uncertain_client = FakeHttpClient([httpx.ReadError("write may have completed"), FakeResponse(response_payload())])
        client = DeepSeekClient(api_key="secret", http_client=uncertain_client, max_retries=1)
        with self.assertRaises(Exception):
            client.complete([])
        self.assertEqual(len(uncertain_client.calls), 1)
        self.assertEqual(client.audit_events[0]["delivery_status"], "unknown")

    def test_server_error_is_delivery_unknown_and_not_retried(self):
        fake = FakeHttpClient([FakeResponse({}, status_code=500), FakeResponse(response_payload())])
        client = DeepSeekClient(api_key="secret", http_client=fake)
        with self.assertRaises(DeepSeekAPIError):
            client.complete([])
        self.assertEqual(len(fake.calls), 1)

    def test_budget_and_cache_hit_miss_cost(self):
        budget = RequestBudget(
            max_requests=1,
            max_input_tokens=100,
            max_output_tokens=20,
            max_cost_usd=0.01,
        )
        payload = response_payload()
        payload["usage"] = {
            "prompt_tokens": 10,
            "prompt_cache_hit_tokens": 8,
            "prompt_cache_miss_tokens": 2,
            "completion_tokens": 4,
            "total_tokens": 14,
        }
        fake = FakeHttpClient([FakeResponse(payload), FakeResponse(payload)])
        client = DeepSeekClient(
            api_key="secret",
            http_client=fake,
            budget=budget,
            max_retries=0,
            max_output_tokens=20,
        )
        client.complete([])
        with self.assertRaises(DeepSeekBudgetExceeded):
            client.complete([])

        episode_budget = RequestBudget(
            max_requests=3,
            max_input_tokens=1000,
            max_output_tokens=1000,
            max_cost_usd=1.0,
            episode_max_requests=1,
        )
        client = DeepSeekClient(
            api_key="secret",
            http_client=FakeHttpClient([FakeResponse(response_payload()), FakeResponse(response_payload())]),
            budget=episode_budget,
            max_retries=0,
        )
        client.set_episode_context(episode_id="ep-1")
        client.complete([])
        with self.assertRaises(DeepSeekBudgetExceeded):
            client.complete([])

    def test_input_cap_and_audit_identity_are_fail_closed(self):
        client = DeepSeekClient(
            api_key="secret",
            http_client=FakeHttpClient([FakeResponse(response_payload())]),
            max_input_tokens=2,
        )
        client.set_episode_context(run_id="run-1", episode_id="ep-1", task_id="5", seed=0, configuration_id="cfg-0000", module="planner")
        with self.assertRaises(DeepSeekBudgetExceeded):
            client.complete([{"role": "user", "content": "too long"}])
        event = client.audit_events[0]
        self.assertEqual(event["status"], "infra_failed")
        self.assertEqual(event["delivery_status"], "not_sent")
        self.assertEqual(event["requested_model"], "deepseek-flash")
        self.assertEqual(event["episode_id"], "ep-1")

    def test_missing_model_identity_fails_closed(self):
        payload = response_payload()
        payload["model"] = None
        payload["system_fingerprint"] = None
        client = DeepSeekClient(
            api_key="secret",
            http_client=FakeHttpClient([FakeResponse(payload)]),
            max_retries=0,
        )
        with self.assertRaises(Exception):
            client.complete([])

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
