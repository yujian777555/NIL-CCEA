import unittest

from nil_ccea.interaction import estimate_pairwise_interaction
from nil_ccea.runner import MockEnvironment, MockRunner, MockTask


class RunnerInteractionTests(unittest.TestCase):
    def test_mock_runner_covers_all_configurations_and_retries(self):
        runner = MockRunner(environment=MockEnvironment(fail_first_call=True))
        records = runner.run(
            [MockTask("t0", "v1", "family")],
            [7],
            max_retries=1,
        )
        self.assertEqual(len(records), 16)
        self.assertTrue(all(record["status"] == "success" for record in records))
        self.assertTrue(all(record["retry_count"] == 1 for record in records))
        totals = runner.ledger.totals()
        self.assertEqual(totals["retry_events"], 16)
        self.assertEqual(totals["failed_events"], 16)

    def test_task_seed_configuration_pairing_and_reset(self):
        environment = MockEnvironment()
        runner = MockRunner(environment=environment)
        records = runner.run(
            [MockTask("t0", "v1", "family"), MockTask("t1", "v1", "family")],
            [0, 1],
        )
        keys = {
            (record["task_id"], record["seed"], record["configuration_id"])
            for record in records
        }
        self.assertEqual(len(keys), 64)
        self.assertEqual(environment.reset_count, 64)

    def test_interaction_recomputed_from_raw_records(self):
        runner = MockRunner()
        records = runner.run(
            [MockTask("t0", "v1", "family"), MockTask("t1", "v1", "family")],
            [0, 1],
        )
        estimate = estimate_pairwise_interaction(
            records,
            "planner",
            "selector",
            bootstrap_samples=200,
        )
        self.assertEqual(estimate.complete_cluster_count, 4)
        self.assertEqual(estimate.cluster_count, 4)
        self.assertGreater(estimate.estimate, 0.05)
        self.assertEqual(estimate.status, "POSITIVE")

    def test_interaction_averages_remaining_slot_contexts(self):
        runner = MockRunner()
        records = runner.run([MockTask("t0", "v1", "family")], [0])
        estimate = estimate_pairwise_interaction(
            records,
            "planner",
            "selector",
            bootstrap_samples=100,
        )
        self.assertAlmostEqual(estimate.estimate, 0.1, places=6)

    def test_incomplete_clusters_are_uncertain(self):
        runner = MockRunner()
        records = runner.run([MockTask("t0", "v1", "family")], [0])
        estimate = estimate_pairwise_interaction(
            records[:3],
            "planner",
            "selector",
            bootstrap_samples=50,
        )
        self.assertEqual(estimate.status, "UNCERTAIN")


if __name__ == "__main__":
    unittest.main()
