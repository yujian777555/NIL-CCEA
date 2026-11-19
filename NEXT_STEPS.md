# Next Steps

**Current task:** execute the Phase 0A handoff prompt in [docs/EXECUTOR_PROMPT_PHASE0A.md](docs/EXECUTOR_PROMPT_PHASE0A.md).

## Completed in the current Phase 0A turn

1. Created branch `phase0a-literature-environment-audit` from remote main SHA `98e202f21bb82f6df4835f48e4d1c922113719ad`.
2. Added the primary-source literature audit and updated the literature ledger.
3. Audited tau-bench, tau2-bench, ToolSandbox, Toolathlon, and AgentSpec. Locked tau2-bench v1.0.1 as the primary candidate and kept ToolSandbox as a diagnostic fallback.
4. Added draft module contracts and the pre-freeze pilot design.
5. Implemented the local mock runner, manifest/hash generation, retry/failure accounting, cost ledger, raw episode schema, and pairwise interaction estimator.
6. Added typed mock module contracts and static leakage checks.
7. Ran the local test suite with ten passing tests and zero real API calls.

## Immediate execution order

1. Implement the tau2 `HalfDuplexAgent` adapter with Planner, Selector, Caller, and Synthesizer as independently hashed components. Keep the adapter compatible with tau2 v1.0.1 and do not use hidden evaluator fields.
2. Add adapter-side static leakage checks and a no-key construction test that verifies identical tool lists, domain policy, model version, decoding settings, and interface schemas across all 16 manifests.
3. Add raw-file loading and derived-summary recomputation tests so every interaction estimate can be regenerated from `episodes.jsonl`.
4. Resolve G2 by freezing the tau2 task IDs, primary endpoint, practical threshold, Holm correction, missing-run policy, retry limit, and stop budget.
5. Produce a real API cost estimate and stop condition. Ask for approval before any paid calls.
6. Run one real tau2 adapter smoke only after the cost gate. Preserve all raw results and mark the run exploratory.
7. Review the smoke and then decide whether the 12-task factorial pilot is sufficiently powered and affordable.

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
| G2 Contracts/protocol | Frozen interfaces, variants, endpoint, statistics, and cost rules | NEEDS_REVISION |
| G3 Smoke | All configurations, pairing/reset, failure and cost tests pass | PASS for mock scope |
| G4 Pilot | Frozen factorial pilot and reproducible interaction estimates | NOT STARTED |
| G5 Search | Fair-budget linkage-aware evolutionary comparison | NOT STARTED |

Do not report a gate as passed without committed artifacts and reproducible evidence.
