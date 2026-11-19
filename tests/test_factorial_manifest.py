import unittest

from nil_ccea.factorial import (
    generate_binary_configurations,
    validate_complete_binary_configurations,
)
from nil_ccea.manifest import (
    SLOTS,
    build_run_manifest,
    configuration_hash,
    default_module_specs,
)


class FactorialManifestTests(unittest.TestCase):
    def test_complete_four_slot_factorial(self):
        configurations = generate_binary_configurations(SLOTS)
        self.assertEqual(len(configurations), 16)
        self.assertEqual(len({tuple(item.values()) for item in configurations}), 16)
        validate_complete_binary_configurations(configurations, SLOTS)

    def test_configuration_hash_changes_with_variant(self):
        specs = default_module_specs()
        common = {
            "environment": {"name": "mock", "version": "1"},
            "model": {"provider": "mock", "model": "m"},
            "decoding": {"temperature": 0.0},
            "protocol_version": "r1",
            "runner_version": "0.1.0",
        }
        first = configuration_hash({slot: 0 for slot in SLOTS}, specs, **common)
        second = configuration_hash(
            {**{slot: 0 for slot in SLOTS}, "planner": 1}, specs, **common
        )
        self.assertNotEqual(first, second)

    def test_manifest_contains_hashes_and_mode(self):
        manifest = build_run_manifest(
            {slot: 0 for slot in SLOTS},
            environment={"name": "mock"},
            model={"provider": "mock", "model": "m"},
            decoding={"temperature": 0.0},
        )
        self.assertEqual(manifest.mode, "mock")
        self.assertEqual(len(manifest.config_hash), 64)
        self.assertTrue(all("content_sha256" in value for value in manifest.modules.values()))


if __name__ == "__main__":
    unittest.main()
