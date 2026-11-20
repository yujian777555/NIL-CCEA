import unittest

from nil_ccea.contracts import AgentContext, Plan, Selection
from nil_ccea.deepseek_client import DeepSeekResponse
from nil_ccea.deepseek_modules import (
    DeepSeekCaller,
    DeepSeekPlanner,
    DeepSeekSelector,
    DeepSeekSynthesizer,
    build_deepseek_modules,
)


class FakeDeepSeekClient:
    def __init__(self, *, json_values=None, tool_calls=None):
        self.json_values = list(json_values or [])
        self.tool_calls = tool_calls or []

    def complete_json(self, messages):
        value = self.json_values.pop(0)
        import json

        return DeepSeekResponse(None, "deepseek-flash", "fp", json.dumps(value), [], {}, {})

    def complete_tools(self, messages, *, tools, tool_choice=None):
        return DeepSeekResponse(None, "deepseek-flash", "fp", None, self.tool_calls, {}, {})


class DeepSeekModuleTests(unittest.TestCase):
    def setUp(self):
        self.context = AgentContext(
            task_id="t0",
            task_version="v1",
            task_family="mock",
            visible_messages=(),
            domain_policy="policy",
            tool_schemas=(
                {
                    "name": "get_users",
                    "description": "list",
                    "parameters": {"type": "object", "properties": {}},
                },
            ),
            step_index=0,
            max_steps=30,
        )

    def test_four_modules_use_contracts_and_native_caller(self):
        planner = DeepSeekPlanner(FakeDeepSeekClient(json_values=[{"goals": [], "termination_condition": "done", "unknowns": []}]))
        plan = planner.plan(self.context)
        selector = DeepSeekSelector(FakeDeepSeekClient(json_values=[{"kind": "tool_call", "tool_name": "get_users", "goal_id": "g0"}]))
        selection = selector.select(self.context, plan)
        caller = DeepSeekCaller(
            FakeDeepSeekClient(
                tool_calls=[
                    {"function": {"name": "get_users", "arguments": "{}"}}
                ]
            )
        )
        proposal = caller.propose(self.context, plan, selection)
        self.assertEqual(proposal.tool_name, "get_users")
        synthesizer = DeepSeekSynthesizer(FakeDeepSeekClient(json_values=[{"content": "done"}]))
        self.assertEqual(synthesizer.synthesize(self.context, plan, selection, None), "done")

    def test_binary_variants_have_distinct_manifest_versions(self):
        fake = FakeDeepSeekClient(json_values=[])
        modules = build_deepseek_modules(
            fake,
            {"planner": 1, "selector": 0, "caller": 1, "synthesizer": 0},
        )
        self.assertEqual(modules["planner"].module_version, "planner.deepseek-flash.p1.v1")
        self.assertEqual(modules["selector"].module_version, "selector.deepseek-flash.p0.v1")
        self.assertEqual(modules["caller"].module_version, "caller.deepseek-flash.p1.v1")
        self.assertEqual(modules["synthesizer"].module_version, "synthesizer.deepseek-flash.p0.v1")


if __name__ == "__main__":
    unittest.main()
