# NIL-CCEA source package

The current package contains:
- a deterministic local mock runner and mock module variants;
- pure factorial, manifest, cost-ledger, leakage, and task-level interaction components;
- typed Planner/Selector/Caller/Synthesizer contracts;
- a tau2 v1.0.1 `HalfDuplexAgent` adapter.

The Phase 0B executor reports 21 no-API integration tests passing against real tau2 v1.0.1 classes and Orchestrator in Python 3.12.16. This validates the tested class/adapter integration path without model completions.

**Not yet implemented:** provider-backed Planner/Selector/Caller/Synthesizer classes and a real tau2 factorial experiment runner. The existing `MockRunner` only emits `mode="mock"`; it is not a real benchmark runner.

Keep statistical estimation pure and unit-testable. Keep the benchmark adapter, provider client, real runner, and algorithm logic as separate layers. No paid API request is permitted until the user explicitly approves it.
