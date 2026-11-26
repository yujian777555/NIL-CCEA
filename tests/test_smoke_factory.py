import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from nil_ccea.deepseek_modules import build_deepseek_modules_by_client
from nil_ccea.smoke_factory import (
    SMOKE_BUDGET,
    build_smoke_factory,
    build_smoke_prerun_manifest,
    task_domain,
    write_immutable_manifest,
)


class SmokeFactoryTests(unittest.TestCase):
    def test_factory_builds_five_distinct_clients_with_shared_controls(self):
        factory = build_smoke_factory("fake-key")
        self.assertEqual(set(factory.clients), {"planner", "selector", "caller", "synthesizer", "user_simulator"})
        self.assertEqual(len({id(client) for client in factory.clients.values()}), 5)
        self.assertTrue(all(client.budget is factory.budget for client in factory.clients.values()))
        self.assertTrue(
            all(client.identity_tracker is factory.identity_tracker for client in factory.clients.values())
        )
        self.assertTrue(all(client.model == "deepseek-flash" for client in factory.clients.values()))
        self.assertTrue(all(client.max_retries == 1 for client in factory.clients.values()))
        self.assertTrue(all(client.max_input_tokens == 2000 for client in factory.clients.values()))
        self.assertTrue(all(client.http_client._trust_env is False for client in factory.clients.values()))
        self.assertEqual(factory.budget.max_requests, 15360)
        self.assertEqual(factory.budget.episode_max_requests, 240)
        self.assertEqual(factory.budget.max_input_tokens, 30_720_000)
        self.assertEqual(factory.budget.max_output_tokens, 7_864_320)
        self.assertAlmostEqual(factory.budget.max_cost_usd, 20.0)

    def test_mapping_builder_keeps_module_clients_distinct(self):
        factory = build_smoke_factory("fake-key")
        modules = factory.module_factory({"planner": 0, "selector": 1, "caller": 0, "synthesizer": 1})
        self.assertEqual(
            len({id(modules[slot].client) for slot in ("planner", "selector", "caller", "synthesizer")}),
            4,
        )
        self.assertEqual(modules["planner"].variant, 0)
        self.assertEqual(modules["selector"].variant, 1)

    def test_task_domain_fails_closed(self):
        retail = SimpleNamespace(
            user_scenario=SimpleNamespace(instructions=SimpleNamespace(domain="retail"))
        )
        self.assertEqual(task_domain(retail), "retail")
        unknown = SimpleNamespace(
            user_scenario=SimpleNamespace(instructions=SimpleNamespace(domain="telecom"))
        )
        with self.assertRaises(ValueError):
            task_domain(unknown)

    def test_prerun_manifest_is_hashed_and_immutable(self):
        with tempfile.TemporaryDirectory() as directory:
            protocol = Path(directory, "protocol.md")
            protocol.write_text("protocol", encoding="utf-8")
            manifest = build_smoke_prerun_manifest(
                code_sha="code-sha",
                tau2_source_sha="tau2-sha",
                protocol_path=protocol,
            )
            self.assertEqual(manifest["code_sha"], "code-sha")
            self.assertEqual(manifest["tau2_source_sha"], "tau2-sha")
            self.assertEqual(len(manifest["configurations"]), 16)
            self.assertEqual(manifest["budget"]["normal_logical_requests"], 7680)
            self.assertEqual(manifest["budget"]["maximum_physical_attempts"], 15360)
            self.assertAlmostEqual(manifest["budget"]["total_no_retry_upper_bound_usd"], 9.326592)
            self.assertAlmostEqual(manifest["budget"]["total_one_retry_upper_bound_usd"], 18.653184)
            self.assertEqual(manifest["model"]["served_model_observed"], None)
            target = Path(directory, "manifest.json")
            write_immutable_manifest(target, manifest)
            with self.assertRaises(FileExistsError):
                write_immutable_manifest(target, manifest)
            saved = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(saved["manifest_sha256"], manifest["manifest_sha256"])


if __name__ == "__main__":
    unittest.main()

