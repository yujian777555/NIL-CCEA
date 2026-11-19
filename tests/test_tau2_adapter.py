import unittest

from nil_ccea.tau2_adapter import Tau2UnavailableError, build_tau2_agent_class


class Tau2AdapterTests(unittest.TestCase):
    def test_adapter_has_explicit_external_dependency_gate(self):
        try:
            adapter = build_tau2_agent_class()
        except Tau2UnavailableError:
            adapter = None
        self.assertTrue(adapter is None or adapter.__name__ == "Tau2FourModuleAgent")


if __name__ == "__main__":
    unittest.main()
