# Tests

Required test classes before the pilot:

1. factorial configuration completeness and uniqueness;
2. module-slot-only intervention invariants;
3. task/seed pairing and reset correctness;
4. cache-key stability and provenance completeness;
5. interaction estimator correctness on hand-computed examples;
6. bootstrap resampling at task-cluster level;
7. edge-state classification, including `UNCERTAIN`;
8. evaluation budget accounting for probes, retries, and failures;
9. raw-data-to-summary reproducibility.

Phase 0B adds `test_tau2_real_no_api.py`. It runs against the pinned tau2 v1.0.1 source in the independent Python 3.12 environment with a LiteLLM stub that raises on any completion call. The test covers real Tool schemas, Tool.params validation, HalfDuplexAgent construction, MultiToolMessage handling, plan_state persistence, task metadata injection, 16 configuration permission invariance, Orchestrator tool execution, and trajectory recovery.

Reproduce the no-API run with:

```powershell
$env:NIL_CCEA_TAU2_SRC = "C:\path\to\tau2-bench-v1.0.1"
.\scripts\run_tau2_no_api_tests.ps1
```
