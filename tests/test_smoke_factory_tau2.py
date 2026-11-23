import unittest

try:
    from nil_ccea.smoke_factory import (
        build_smoke_factory,
        get_environment_for_task,
        load_frozen_smoke_tasks,
    )
    from nil_ccea.tau2_runner import Tau2FactorialRunner, Tau2RunnerError
    from tau2.user.user_simulator import UserSimulator

    from tau2.domains.airline.environment import get_environment as get_airline_environment
    from tau2.domains.retail.environment import get_environment as get_retail_environment

    TAU2_AVAILABLE = True
except ImportError:
    TAU2_AVAILABLE = False


@unittest.skipUnless(TAU2_AVAILABLE, "需要独立 tau2 v1.0.1 环境")
class SmokeFactoryTau2Tests(unittest.TestCase):
    def test_frozen_tasks_and_task_aware_environments(self):
        tasks = load_frozen_smoke_tasks()
        self.assertEqual([(task.id, task.user_scenario.instructions.domain) for task in tasks], [("5", "retail"), ("2", "airline")])
        environments = [get_environment_for_task(task) for task in tasks]
        self.assertEqual([environment.get_domain_name() for environment in environments], ["retail", "airline"])
        self.assertNotEqual(id(environments[0]), id(environments[1]))
        self.assertGreater(len(environments[0].get_tools()), 0)
        self.assertGreater(len(environments[1].get_tools()), 0)
        self.assertNotEqual(environments[0].get_policy(), environments[1].get_policy())

    def test_user_factory_uses_exact_environment_instance(self):
        tasks = load_frozen_smoke_tasks()
        factory = build_smoke_factory("fake-key")
        environment = get_environment_for_task(tasks[0])
        user = factory.user_factory_with_environment(tasks[0], environment)
        self.assertEqual(user.llm, "deepseek-flash")
        self.assertIs(user.client, factory.clients["user_simulator"])
        self.assertIsNotNone(user.client.budget)

    def test_evaluated_runner_requires_five_controlled_clients(self):
        tasks = load_frozen_smoke_tasks()
        factory = build_smoke_factory("fake-key")
        runner = Tau2FactorialRunner(
            tau2_source_commit="fc0055dc4e0a316c3f83133267fbd6faaa770992",
            task_version="v1.0.1",
            environment_factory=lambda: get_environment_for_task(tasks[0]),
            user_factory=lambda task: None,
            user_factory_with_environment=factory.user_factory_with_environment,
            module_factory=factory.module_factory,
            evaluate=True,
            request_budget=factory.budget,
            identity_tracker=factory.identity_tracker,
        )
        modules = factory.module_factory({"planner": 0, "selector": 0, "caller": 0, "synthesizer": 0})
        user = factory.user_factory_with_environment(tasks[0], get_environment_for_task(tasks[0]))
        runner._validate_model_consistency(modules, user)

        factory.clients["selector"].identity_tracker = type(factory.identity_tracker)()
        with self.assertRaises(Tau2RunnerError):
            runner._validate_model_consistency(modules, user)

        with self.assertRaises(Tau2RunnerError):
            runner._validate_model_consistency(modules, UserSimulator(llm="deepseek-flash"))

    def test_runner_rejects_user_client_with_separate_budget(self):
        tasks = load_frozen_smoke_tasks()
        factory = build_smoke_factory("fake-key")
        separate_budget = type(factory.budget)(**{
            "max_requests": 1,
            "max_input_tokens": 100,
            "max_output_tokens": 100,
            "max_cost_usd": 1.0,
        })
        factory.clients["user_simulator"].budget = separate_budget
        runner = Tau2FactorialRunner(
            tau2_source_commit="fc0055dc4e0a316c3f83133267fbd6faaa770992",
            task_version="v1.0.1",
            environment_factory=lambda: get_environment_for_task(tasks[0]),
            user_factory=lambda task: None,
            user_factory_with_environment=factory.user_factory_with_environment,
            module_factory=factory.module_factory,
            evaluate=False,
            request_budget=factory.budget,
        )
        with self.assertRaises(Tau2RunnerError):
            runner.run_episode(tasks[0], 0, {"planner": 0, "selector": 0, "caller": 0, "synthesizer": 0})


if __name__ == "__main__":
    unittest.main()

