# NIL-CCEA source package

The current package contains a local mock runner, pure statistical components, typed module contracts, and an explicit tau2 adapter entry point. The tau2 adapter remains unvalidated and is intentionally kept separate from the mock path.

Planned modules:

- `factorial.py`: generation and validation of factorial configurations;
- `manifest.py`: module manifests, SHA-256 hashes, and provenance;
- `contracts.py`: typed Planner/Selector/Caller/Synthesizer interfaces;
- `mock_modules.py`: mechanism-distinct local variants for smoke tests;
- `interaction.py`: task-level paired difference-in-differences, repeated-seed aggregation, bootstrap, and Holm correction;
- `runner.py`: local reset, trajectory, retry, failure, and cost accounting;
- `ledger.py`: shared evaluation-cost ledger;
- `leakage.py`: conservative static evaluator-token checks.
- `tau2_adapter.py`: delayed-import `HalfDuplexAgent` adapter for tau2 v1.0.1.

Keep statistical estimation pure and unit-testable. Keep benchmark adapters separate from algorithm logic.
