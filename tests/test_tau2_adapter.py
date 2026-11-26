import unittest

from pydantic import BaseModel

from nil_ccea.tau2_adapter import (
    Tau2UnavailableError,
    _tool_schema,
    _validate_arguments,
    build_tau2_agent_class,
)


class FakeParams(BaseModel):
    user_id: str


class FakeTool:
    name = "lookup_user"
    params = FakeParams
    openai_schema = {
        "type": "function",
        "function": {
            "name": "lookup_user",
            "description": "lookup",
            "parameters": {
                "type": "object",
                "required": ["user_id"],
                "properties": {"user_id": {"type": "string"}},
            },
        },
    }


class Tau2AdapterTests(unittest.TestCase):
    def test_real_tool_schema_and_params_are_used(self):
        schema = _tool_schema(FakeTool())
        self.assertEqual(schema["name"], "lookup_user")
        self.assertIn("user_id", schema["parameters"]["properties"])
        self.assertEqual(_validate_arguments(FakeTool(), {"user_id": "u1"}), {"user_id": "u1"})
        with self.assertRaises(Exception):
            _validate_arguments(FakeTool(), {})

    def test_adapter_has_explicit_external_dependency_gate(self):
        try:
            adapter = build_tau2_agent_class()
        except Tau2UnavailableError:
            adapter = None
        self.assertTrue(adapter is None or adapter.__name__ == "Tau2FourModuleAgent")


if __name__ == "__main__":
    unittest.main()
