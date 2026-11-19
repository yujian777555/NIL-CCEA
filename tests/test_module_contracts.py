import inspect
import unittest

from nil_ccea.contracts import AgentContext
from nil_ccea.leakage import find_forbidden_tokens
from nil_ccea.mock_modules import build_mock_modules


class ModuleContractTests(unittest.TestCase):
    def _context(self):
        return AgentContext(
            task_id="mock-task",
            task_version="mock-v1",
            task_family="family",
            visible_messages=(),
            domain_policy="public policy",
            tool_schemas=({"name": "public_tool", "parameters": {}},),
            step_index=0,
            max_steps=4,
        )

    def test_all_variants_keep_common_pipeline_interfaces(self):
        context = self._context()
        for planner_bit in (0, 1):
            for selector_bit in (0, 1):
                for caller_bit in (0, 1):
                    for synthesizer_bit in (0, 1):
                        modules = build_mock_modules(
                            {
                                "planner": planner_bit,
                                "selector": selector_bit,
                                "caller": caller_bit,
                                "synthesizer": synthesizer_bit,
                            }
                        )
                        plan = modules["planner"].plan(context)
                        selection = modules["selector"].select(context, plan)
                        proposal = modules["caller"].propose(context, plan, selection)
                        text = modules["synthesizer"].synthesize(
                            context, plan, selection, {"ok": True}
                        )
                        self.assertIsInstance(text, str)
                        self.assertEqual(len(proposal.module_version.split(".")), 2)

    def test_module_source_has_no_evaluator_tokens(self):
        from nil_ccea import mock_modules

        source = inspect.getsource(mock_modules)
        self.assertEqual(find_forbidden_tokens(source), [])


if __name__ == "__main__":
    unittest.main()
