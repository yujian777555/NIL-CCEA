import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from tau2.data_model.message import MultiToolMessage, ToolMessage, UserMessage
    from tau2.domains.mock.environment import get_environment, get_tasks
    from tau2.orchestrator.orchestrator import Orchestrator
    from tau2.environment.tool import as_tool
    from nil_ccea.contracts import Plan, Selection, ToolCallProposal
    from nil_ccea.deepseek_client import DeepSeekResponse, RequestBudget
    from nil_ccea.factorial import generate_binary_configurations
    from nil_ccea.manifest import SLOTS
    from nil_ccea.mock_modules import build_mock_modules
    from nil_ccea.tau2_runner import Tau2FactorialRunner
    from nil_ccea.tau2_adapter import InvalidToolCallError, build_tau2_agent_class
    from nil_ccea.tau2_user_simulator import DeepSeekTau2UserSimulator

    TAU2_AVAILABLE = True
except ImportError:
    TAU2_AVAILABLE = False


@unittest.skipUnless(TAU2_AVAILABLE, "需要独立 tau2 v1.0.1 环境")
class Tau2RealNoApiTests(unittest.TestCase):
    def setUp(self):
        self.contexts = []

        def lookup_user(user_id: str) -> str:
            return f"user:{user_id}"

        self.tool = as_tool(lookup_user)

        class Planner:
            module_version = "planner.test"

            def plan(inner, context):
                self.contexts.append(context)
                return Plan(({"goal_id": "g0", "description": "lookup", "prerequisites": ()},), "done", (), inner.module_version)

        class Selector:
            module_version = "selector.test"

            def select(inner, context, plan):
                return Selection("tool_call", context.tool_schemas[0]["name"], "g0", "schema_match", inner.module_version)

        class Caller:
            module_version = "caller.test"

            def propose(inner, context, plan, selection):
                return ToolCallProposal(selection.tool_name, {"user_id": "u1"}, True, (), inner.module_version)

        class Synthesizer:
            module_version = "synth.test"

            def synthesize(inner, context, plan, selection, tool_result):
                return "已处理公开工具结果。"

        agent_class = build_tau2_agent_class()
        self.agent = agent_class(
            tools=[self.tool],
            domain_policy="public policy",
            planner=Planner(),
            selector=Selector(),
            caller=Caller(),
            synthesizer=Synthesizer(),
            task_id="task-001",
            task_version="binding-v1",
            task_family="retail",
        )

    def test_schema_permissions_multitool_and_state_recovery(self):
        schema = self.tool.openai_schema["function"]
        self.assertEqual(self.agent._tool_schemas[0]["name"], schema["name"])
        self.assertEqual(self.agent._tool_schemas[0]["parameters"], schema["parameters"])
        state = self.agent.get_init_state()
        response, state = self.agent.generate_next_message(UserMessage.text("lookup"), state)
        self.assertEqual(response.tool_calls[0].name, "lookup_user")
        self.assertEqual(response.tool_calls[0].arguments, {"user_id": "u1"})
        tool_message = ToolMessage(
            id=response.tool_calls[0].id,
            role="tool",
            content="{\"ok\": true}",
            requestor="assistant",
        )
        response, state = self.agent.generate_next_message(tool_message, state)
        self.assertTrue(state.plan_state["public_state_ready"])
        self.assertEqual(state.plan_state["last_tool_results"][0]["id"], tool_message.id)
        multi = MultiToolMessage(role="tool", tool_messages=[tool_message])
        self.agent.generate_next_message(multi, state)
        self.assertEqual(self.contexts[0].task_id, "task-001")
        self.assertEqual(self.contexts[0].task_version, "binding-v1")
        self.assertEqual(self.contexts[0].task_family, "retail")

    def test_invalid_arguments_fail_closed(self):
        class InvalidCaller:
            module_version = "caller.invalid"

            def propose(self, context, plan, selection):
                return ToolCallProposal(selection.tool_name, {}, True, (), self.module_version)

        self.agent.caller = InvalidCaller()
        with self.assertRaises(InvalidToolCallError):
            self.agent.generate_next_message(UserMessage.text("lookup"), self.agent.get_init_state())

    def test_caller_is_not_called_for_respond_or_stop(self):
        calls = []

        class RespondSelector:
            module_version = "selector.respond"

            def select(self, context, plan):
                return Selection("respond", None, "g0", "response_needed", self.module_version)

        class CountingCaller:
            module_version = "caller.counting"

            def propose(self, context, plan, selection):
                calls.append(selection.kind)
                raise AssertionError("Caller must not run for respond")

        self.agent.selector = RespondSelector()
        self.agent.caller = CountingCaller()
        self.agent.generate_next_message(UserMessage.text("respond"), self.agent.get_init_state())
        self.assertEqual(calls, [])

        class StopSelector(RespondSelector):
            def select(self, context, plan):
                return Selection("stop", None, "g0", "done", self.module_version)

        self.agent.selector = StopSelector()
        self.agent.generate_next_message(UserMessage.text("stop"), self.agent.get_init_state())
        self.assertEqual(calls, [])

    def test_real_orchestrator_multiturn_tool_trajectory_without_api(self):
        class ScriptedUser:
            def get_init_state(self, message_history=None):
                return {"turns": 0}

            def set_seed(self, seed):
                return None

            def stop(self, message=None, state=None):
                return None

            def generate_next_message(self, message, state):
                state["turns"] += 1
                if state["turns"] == 1:
                    return UserMessage.text("list users"), state
                if message is not None and getattr(message, "is_tool_call", lambda: False)():
                    return UserMessage.text("done ###STOP###"), state
                return UserMessage.text("done ###STOP###"), state

        class Planner:
            module_version = "planner.orch"

            def plan(self, context):
                return Plan(({"goal_id": "g0", "description": "list users", "prerequisites": ()},), "done", (), self.module_version)

        class Selector:
            module_version = "selector.orch"

            def select(self, context, plan):
                if context.plan_state.get("public_state_ready"):
                    return Selection("respond", None, "g0", "response_needed", self.module_version)
                return Selection("tool_call", "get_users", "g0", "schema_match", self.module_version)

        class Caller:
            module_version = "caller.orch"

            def propose(self, context, plan, selection):
                return ToolCallProposal(selection.tool_name or "", {}, True, (), self.module_version)

        class Synthesizer:
            module_version = "synth.orch"

            def synthesize(self, context, plan, selection, tool_result):
                return "已读取公开用户列表。"

        env = get_environment()
        task = get_tasks()[0]
        agent_class = build_tau2_agent_class()
        agent = agent_class(
            tools=env.get_tools(),
            domain_policy=env.get_policy(),
            planner=Planner(),
            selector=Selector(),
            caller=Caller(),
            synthesizer=Synthesizer(),
            task_id=task.id,
            task_version="mock-v1.0.1",
            task_family="mock",
        )
        orchestrator = Orchestrator(
            domain="mock",
            agent=agent,
            user=ScriptedUser(),
            environment=env,
            task=task,
            max_steps=5,
            seed=0,
        )
        simulation = orchestrator.run()
        messages = simulation.get_messages()
        self.assertTrue(any(message.is_tool_call() for message in messages if hasattr(message, "is_tool_call")))
        self.assertTrue(any(getattr(message, "role", None) == "tool" for message in messages))
        self.assertTrue(orchestrator.agent_state.plan_state["public_state_ready"])
        self.assertEqual(orchestrator.agent.seed, 0)

    def test_all_16_configs_keep_identical_tool_permissions(self):
        env = get_environment()
        agent_class = build_tau2_agent_class()
        expected_names = tuple(sorted(tool.name for tool in env.get_tools()))
        expected_schemas = None
        for configuration in generate_binary_configurations(SLOTS):
            modules = build_mock_modules(configuration)
            agent = agent_class(
                tools=env.get_tools(),
                domain_policy=env.get_policy(),
                planner=modules["planner"],
                selector=modules["selector"],
                caller=modules["caller"],
                synthesizer=modules["synthesizer"],
                task_id="mock-task",
                task_version="mock-v1.0.1",
                task_family="mock",
            )
            self.assertEqual(tuple(sorted(agent._tools_by_name)), expected_names)
            schemas = tuple(
                (schema["name"], schema["parameters"])
                for schema in agent._tool_schemas
            )
            if expected_schemas is None:
                expected_schemas = schemas
            self.assertEqual(schemas, expected_schemas)

    def test_real_tau2_factorial_runner_writes_all_cells_without_api(self):
        class ScriptedUser:
            def get_init_state(self, message_history=None):
                return {"turns": 0}

            def set_seed(self, seed):
                return None

            def stop(self, message=None, state=None):
                return None

            def generate_next_message(self, message, state):
                state["turns"] += 1
                if state["turns"] == 1:
                    return UserMessage.text("list users"), state
                if message is not None and getattr(message, "is_tool_call", lambda: False)():
                    return UserMessage.text("done ###STOP###"), state
                return UserMessage.text("done ###STOP###"), state

        class RunnerPlanner:
            module_version = "planner.runner"

            def plan(self, context):
                return Plan(
                    ({"goal_id": "g0", "description": "list users", "prerequisites": ()},),
                    "done",
                    (),
                    self.module_version,
                )

        class RunnerSelector:
            module_version = "selector.runner"

            def select(self, context, plan):
                if context.plan_state.get("public_state_ready"):
                    return Selection("respond", None, "g0", "response_needed", self.module_version)
                return Selection("tool_call", "get_users", "g0", "schema_match", self.module_version)

        class RunnerCaller:
            module_version = "caller.runner"

            def propose(self, context, plan, selection):
                return ToolCallProposal(selection.tool_name or "", {}, True, (), self.module_version)

        class RunnerSynthesizer:
            module_version = "synthesizer.runner"

            def synthesize(self, context, plan, selection, tool_result):
                return "已读取公开用户列表。"

        def runner_modules(configuration):
            return {
                "planner": RunnerPlanner(),
                "selector": RunnerSelector(),
                "caller": RunnerCaller(),
                "synthesizer": RunnerSynthesizer(),
            }

        with tempfile.TemporaryDirectory() as output_dir:
            runner = Tau2FactorialRunner(
                tau2_source_commit="fc0055dc4e0a316c3f83133267fbd6faaa770992",
                task_version="v1.0.1",
                environment_factory=get_environment,
                user_factory=lambda task: ScriptedUser(),
                module_factory=runner_modules,
                output_dir=output_dir,
                max_steps=5,
                evaluate=False,
            )
            records = runner.run([get_tasks()[0]], seeds=(0, 1))
            self.assertEqual(len(records), 32)
            self.assertEqual(
                len({(record["seed"], record["configuration_id"]) for record in records}),
                32,
            )
            self.assertTrue(all(record["mode"] == "tau2-text-v1" for record in records))
            self.assertTrue(all(record["status"] == "success" for record in records))
            self.assertEqual(len(Path(output_dir, "episodes.jsonl").read_text().splitlines()), 32)
            self.assertEqual(Path(output_dir, "request_events.jsonl").read_text(), "")
            ledger = json.loads(Path(output_dir, "cost_ledger.json").read_text())
            self.assertEqual(ledger["totals"]["events"], 0)
            self.assertEqual(ledger["totals"]["api_cost"], 0.0)

    def test_runner_does_not_replay_failed_episode(self):
        calls = []

        class FailingPlanner:
            module_version = "planner.failure"

            def plan(self, context):
                raise RuntimeError("synthetic planner failure")

        def failing_modules(configuration):
            calls.append(configuration)
            modules = build_mock_modules(configuration)
            modules["planner"] = FailingPlanner()
            return modules

        runner = Tau2FactorialRunner(
            tau2_source_commit="fc0055dc4e0a316c3f83133267fbd6faaa770992",
            task_version="v1.0.1",
            environment_factory=get_environment,
            user_factory=lambda task: object(),
            module_factory=failing_modules,
            max_steps=2,
            evaluate=False,
        )
        record = runner.run_episode(get_tasks()[0], 0, {slot: 0 for slot in SLOTS})
        self.assertEqual(record["status"], "infra_failed")
        self.assertEqual(record["retry_count"], 0)
        self.assertEqual(len(calls), 1)

    def test_runner_binds_shared_budget_and_environment_aware_user_factory(self):
        class FakeUserClient:
            model = "deepseek-flash"
            temperature = 0.0
            max_output_tokens = 512
            base_url = "https://api.deepseek.com"
            input_usd_per_million = 0.30
            cached_input_usd_per_million = 0.006
            output_usd_per_million = 1.20

            def __init__(self):
                self.budget = None
                self.context = None

            def set_episode_context(self, **context):
                self.context = context

            def complete(self, messages, **kwargs):
                return DeepSeekResponse(
                    request_id="user-run-1",
                    model="deepseek-flash",
                    system_fingerprint="fp-user-run-1",
                    content="done ###STOP###",
                    tool_calls=[],
                    usage={
                        "prompt_tokens": 5,
                        "completion_tokens": 3,
                        "total_tokens": 8,
                        "prompt_cache_hit_tokens": 0,
                        "prompt_cache_miss_tokens": 5,
                    },
                    raw_response={},
                )

            def drain_audit_events(self):
                return []

        fake_client = FakeUserClient()
        budget = RequestBudget(
            max_requests=100,
            max_input_tokens=10000,
            max_output_tokens=10000,
            max_cost_usd=10.0,
        )
        seen_environment = []

        def user_factory_with_environment(task, environment):
            seen_environment.append(environment)
            return DeepSeekTau2UserSimulator(
                client=fake_client,
                instructions="stop after greeting",
            )

        with patch("tau2.user.user_simulator.get_global_user_sim_guidelines", return_value="guidelines"):
            runner = Tau2FactorialRunner(
                tau2_source_commit="fc0055dc4e0a316c3f83133267fbd6faaa770992",
                task_version="v1.0.1",
                environment_factory=get_environment,
                user_factory=lambda task: (_ for _ in ()).throw(AssertionError("fallback user factory used")),
                user_factory_with_environment=user_factory_with_environment,
                module_factory=build_mock_modules,
                max_steps=2,
                evaluate=False,
                request_budget=budget,
            )
            record = runner.run_episode(get_tasks()[0], 0, {slot: 0 for slot in SLOTS})
        self.assertEqual(record["status"], "success")
        self.assertEqual(len(seen_environment), 1)
        self.assertIs(fake_client.budget, budget)
        self.assertEqual(fake_client.context["module"], "user_simulator")


if __name__ == "__main__":
    unittest.main()
