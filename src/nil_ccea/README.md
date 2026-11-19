# NIL-CCEA source package

The current package contains a local mock runner and pure statistical components. The tau2 adapter remains unvalidated and is intentionally kept separate from the mock path.

Planned modules:

- `factorial.py`: generation and validation of factorial configurations;
- `manifest.py`: module manifests, SHA-256 hashes, and provenance;
- `contracts.py`: typed Planner/Selector/Caller/Synthesizer interfaces;
- `mock_modules.py`: mechanism-distinct local variants for smoke tests;
- `interaction.py`: paired difference-in-differences estimates and task-cluster bootstrap;
- `runner.py`: local reset, trajectory, retry, failure, and cost accounting;
- `ledger.py`: shared evaluation-cost ledger;
- `leakage.py`: conservative static evaluator-token checks.

Keep statistical estimation pure and unit-testable. Keep benchmark adapters separate from algorithm logic.
