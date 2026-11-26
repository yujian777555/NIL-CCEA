import unittest
from unittest.mock import patch

try:
    from tau2.data_model.message import AssistantMessage
    from tau2.environment.tool import as_tool
    from nil_ccea.deepseek_client import DeepSeekClient, DeepSeekResponse, RequestBudget
    from nil_ccea.tau2_user_simulator import DeepSeekTau2UserSimulator

    TAU2_AVAILABLE = True
except ImportError:
    TAU2_AVAILABLE = False


@unittest.skipUnless(TAU2_AVAILABLE, "需要独立 tau2 v1.0.1 环境")
class Tau2UserSimulatorTests(unittest.TestCase):
    class FakeClient:
        model = "deepseek-flash"
        temperature = 0.0
        max_output_tokens = 512
        base_url = "https://api.deepseek.com"
        input_usd_per_million = 0.30
        cached_input_usd_per_million = 0.006
        output_usd_per_million = 1.20

        def __init__(self, response):
            self.response = response
            self.calls = []
            self.budget = None

        def complete(self, messages, **kwargs):
            self.calls.append((messages, kwargs))
            return self.response

        def complete_tools(self, messages, *, tools, **kwargs):
            self.calls.append((messages, {"tools": tools, **kwargs}))
            return self.response

    @staticmethod
    def response(content="hello", tool_calls=None):
        return DeepSeekResponse(
            request_id="req-user-1",
            model="deepseek-flash",
            system_fingerprint="fp-user-1",
            content=content,
            tool_calls=tool_calls or [],
            usage={
                "prompt_tokens": 5,
                "completion_tokens": 2,
                "total_tokens": 7,
                "prompt_cache_hit_tokens": 0,
                "prompt_cache_miss_tokens": 5,
            },
            raw_response={"id": "chat-user-1"},
        )

    def test_plain_text_uses_injected_client_and_skips_litellm(self):
        fake = self.FakeClient(self.response())
        with patch("tau2.user.user_simulator.get_global_user_sim_guidelines", return_value="guidelines"):
            user = DeepSeekTau2UserSimulator(client=fake, instructions="user instructions")
            state = user.get_init_state()
            with patch("tau2.user.user_simulator.generate", side_effect=AssertionError("LiteLLM path used")):
                message, state = user.generate_next_message(
                    AssistantMessage(role="assistant", content="hello"), state
                )
        self.assertEqual(message.content, "hello")
        self.assertEqual(len(fake.calls), 1)
        self.assertEqual(message.usage["completion_tokens"], 2)
        self.assertEqual(state.messages[-1].content, "hello")

    def test_native_user_tool_call_is_locally_validated(self):
        def lookup_user(user_id: str) -> str:
            return user_id

        tool = as_tool(lookup_user)
        fake = self.FakeClient(
            self.response(
                content=None,
                tool_calls=[
                    {
                        "id": "user-call-1",
                        "type": "function",
                        "function": {"name": "lookup_user", "arguments": '{"user_id":"u1"}'},
                    }
                ],
            )
        )
        with patch("tau2.user.user_simulator.get_global_user_sim_guidelines", return_value="guidelines"):
            user = DeepSeekTau2UserSimulator(
                client=fake,
                instructions="user instructions",
                tools=[tool],
            )
            state = user.get_init_state()
            message, _ = user.generate_next_message(
                AssistantMessage(role="assistant", content="use the tool"), state
            )
        self.assertEqual(message.tool_calls[0].requestor, "user")
        self.assertEqual(message.tool_calls[0].arguments, {"user_id": "u1"})
        self.assertEqual(fake.calls[0][1]["tools"][0]["function"]["name"], "lookup_user")

    def test_user_client_can_share_request_budget(self):
        budget = RequestBudget(
            max_requests=10,
            max_input_tokens=1000,
            max_output_tokens=1000,
            max_cost_usd=1.0,
        )
        fake = self.FakeClient(self.response())
        fake.budget = budget
        user = DeepSeekTau2UserSimulator(client=fake, instructions="user instructions")
        self.assertIs(user.client.budget, budget)
        self.assertEqual(user.llm, "deepseek-flash")

    def test_real_client_audit_event_is_attributed_to_user_simulator(self):
        class FakeResponse:
            status_code = 200
            headers = {"x-request-id": "req-user-real"}

            @staticmethod
            def json():
                return {
                    "id": "chat-user-real",
                    "model": "deepseek-flash",
                    "system_fingerprint": "fp-user-real",
                    "choices": [{"message": {"role": "assistant", "content": "hello"}}],
                    "usage": {
                        "prompt_tokens": 5,
                        "completion_tokens": 2,
                        "total_tokens": 7,
                    },
                }

        class FakeHttp:
            def __init__(self):
                self.calls = 0

            def post(self, url, *, headers, json):
                self.calls += 1
                return FakeResponse()

        http = FakeHttp()
        client = DeepSeekClient(api_key="secret", http_client=http, max_retries=0)
        client.set_episode_context(
            run_id="run-1",
            episode_id="episode-1",
            task_id="5",
            seed=0,
            configuration_id="cfg-0000",
            module="user_simulator",
        )
        with patch("tau2.user.user_simulator.get_global_user_sim_guidelines", return_value="guidelines"):
            user = DeepSeekTau2UserSimulator(client=client, instructions="user instructions")
            state = user.get_init_state()
            user.generate_next_message(AssistantMessage(role="assistant", content="hello"), state)
        events = client.drain_audit_events()
        self.assertEqual(http.calls, 1)
        self.assertEqual(events[0]["module"], "user_simulator")
        self.assertEqual(events[0]["episode_id"], "episode-1")
        self.assertEqual(events[0]["returned_model"], "deepseek-flash")


if __name__ == "__main__":
    unittest.main()

