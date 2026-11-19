# Next Steps

**Current task:** execute Phase 0B statistical correction, tau2 adapter validation, and protocol freeze.

## Completed in Phase 0A and the current Phase 0B turn

1. Created branch `phase0a-literature-environment-audit` from remote main SHA `98e202f21bb82f6df4835f48e4d1c922113719ad`.
2. Added the primary-source literature audit and updated the literature ledger.
3. Audited tau-bench, tau2-bench, ToolSandbox, Toolathlon, and AgentSpec. Locked tau2-bench v1.0.1 as the primary candidate and kept ToolSandbox as a diagnostic fallback.
4. Added draft module contracts and the pre-freeze pilot design.
5. Implemented the local mock runner, manifest/hash generation, retry/failure accounting, cost ledger, raw episode schema, and pairwise interaction estimator.
6. Added typed mock module contracts and static leakage checks.
7. Added the tau2 adapter entry point behind an external-dependency gate.
8. Ran the local test suite with twenty-one passing tests and zero real API calls. The Python 3.12 tau2 run also passed all twenty-one.
9. Corrected task-level statistical clustering, six-pair Holm adjustment, failure semantics, and tau2 Tool schema handling.
10. Ran real tau2 v1.0.1 classes and Orchestrator with local modules and zero API calls in the independent Python 3.12.16 environment.

## Immediate execution order

1. Review provider pricing and update the declared cost profile before any paid call.
2. Run the 2-task × 2-seed × 16-configuration exploratory smoke only after explicit user approval.
3. Preserve all raw trajectories and manifests. Mark the smoke exploratory.
4. Reassess task-level variance and the power sensitivity table before formal pilot approval.
5. Do not implement the full evolutionary optimizer until the corrected interaction estimates are reviewable.

## Research guardrails

- Keep evolutionary computation and module-interaction linkage as the method core.
- Fixed total evaluation budget is a fairness constraint, not a new budget-allocation research direction.
- A null result for one module pair is a diagnosis trigger, not a project stop condition. Investigate manipulation validity, task-family dependence, noise, statistical power, and higher-order effects using separately versioned diagnostics.
- Do not manufacture positive interactions or change endpoints after observing results.
- Do not implement the complete optimizer before the interaction-measurement protocol is validated.
- No base-model training or fine-tuning in this milestone.
- Count every probe, failed call, retry, and diagnostic evaluation in total cost.
- Keep NIL-CCEA separate from all other repositories.

## Acceptance gates

| Gate | Required evidence | State |
|---|---|---|
| G0 Literature | Verified primary-source bibliography and mechanism comparison | PASS |
| G1 Environment | Source-backed benchmark and module-replacement compatibility | PASS at source level |
| G2 Contracts/protocol | Frozen interfaces, variants, endpoint, statistics, and cost rules | NEEDS_REVISION pending price verification |
| G3 Smoke | All configurations, pairing/reset, failure and cost tests pass | PASS for mock and tau2 no-API scope |
| G4 Pilot | Frozen factorial pilot and reproducible interaction estimates | NOT STARTED |
| G5 Search | Fair-budget linkage-aware evolutionary comparison | NOT STARTED |

Do not report a gate as passed without committed artifacts and reproducible evidence.
