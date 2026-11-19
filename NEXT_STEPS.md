# Next Steps

**Current task:** execute the Phase 0A handoff prompt in [docs/EXECUTOR_PROMPT_PHASE0A.md](docs/EXECUTOR_PROMPT_PHASE0A.md).

## Immediate execution order

1. **Take over safely.** Verify the latest remote main SHA, local worktree, and branch. Create a dedicated Phase 0A branch; do not overwrite existing work or force-push.
2. **Run literature and environment audits in parallel.** Verify primary sources for the closest Agent-module evolution, interaction/linkage learning, noisy optimization, and cooperative co-evolution work. Inspect tau-bench and other suitable tool-use environments from their official sources.
3. **Make an evidence-backed environment decision.** Confirm task/version stability, reset semantics, scoring, trajectory access, and independent module replacement. Do not force the provisional Planner/Selector/Caller/Synthesizer split if source code does not support it.
4. **Freeze module contracts and variants.** Define identical interfaces and permissions for two mechanism-distinct variants per confirmed slot. Prevent task leakage and confounding changes.
5. **Prepare the pilot runner and protocol.** Implement immutable manifests, task/seed pairing, raw trajectory references, failure/retry accounting, deterministic cache keys, and total cost accounting. Pre-register the primary endpoint, practical effect threshold, uncertainty method, and multiplicity handling.
6. **Run a mock smoke test first.** Validate all configurations, reset/pairing, failure paths, and cost accounting without paid model calls.
7. **Independent review, then pilot.** Only after G0-G3 pass and the runner is independently reviewed, run the frozen factorial pilot. The existing 12 tasks × 2 seeds × 16 configurations is a planning target, subject to pre-freeze cost/power analysis.

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
| G0 Literature | Verified primary-source bibliography and mechanism comparison | TODO |
| G1 Environment | Source-backed benchmark and module-replacement compatibility | TODO |
| G2 Contracts/protocol | Frozen interfaces, variants, endpoint, statistics, and cost rules | TODO |
| G3 Smoke | All configurations, pairing/reset, failure and cost tests pass | TODO |
| G4 Pilot | Frozen factorial pilot and reproducible interaction estimates | NOT STARTED |
| G5 Search | Fair-budget linkage-aware evolutionary comparison | NOT STARTED |

Do not report a gate as passed without committed artifacts and reproducible evidence.
