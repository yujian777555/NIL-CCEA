# Next Steps

**Current task:** execute [Phase 0B adapter and estimator corrections](docs/EXECUTOR_PROMPT_PHASE0B.md).

## Review baseline

- Phase 0A branch: `phase0a-literature-environment-audit`
- Phase 0A HEAD: `6bed028a4675a75928734b633bbfae49d6b98b14`
- PR #1: open, not merged
- Phase 0B branch: `phase0b-adapter-statistical-corrections`
- Review: [docs/PHASE0A_INDEPENDENT_REVIEW.md](docs/PHASE0A_INDEPENDENT_REVIEW.md)

## Required execution order

1. Fix tau2 Tool schema extraction using the pinned v1.0.1 `Tool.params` / `Tool.openai_schema` API.
2. Enforce Selector → Caller consistency, schema validation, explicit failure events, and correct UserMessage/ToolMessage/MultiToolMessage handling.
3. Persist public plan state and require real task/version/family metadata in experiment mode.
4. Correct the interaction estimator to resample task IDs, with seeds nested inside tasks.
5. Require complete factorial cells/contexts; reject duplicates and explicitly handle task failures versus infrastructure failures.
6. Add tests for all corrections and pinned tau2 v1.0.1 no-key adapter integration in Python 3.12/3.13.
7. Freeze exact task IDs, endpoint, delta, inference/Holm method, retry/missingness policy, and task-level sensitivity/power analysis.
8. Produce provider/model-specific cost estimate and hard stop limits.
9. Ask for explicit approval before any paid exploratory tau2 smoke.

## Research guardrails

- Do not repeat the Phase 0A literature audit or the already-passing pure mock smoke unless a targeted regression requires it.
- Do not merge PR #1 until blockers are corrected and independently reviewed.
- Do not make paid API calls before explicit user approval.
- Treat the task instance, not task × seed, as the independent statistical cluster.
- Never silently drop incomplete factorial contexts or failed episodes.
- Keep exploratory smoke data separate from confirmatory pilot data.
- Do not change endpoint, delta, task IDs, or sample size after observing confirmatory results.
- A null pairwise interaction is a diagnosis trigger, not a project stop condition.
- Keep NIL-CCEA isolated from other repositories.
- Do not implement the full optimizer or base-model training in this phase.

## Acceptance gates

| Gate | State |
|---|---|
| G0 Literature | PASS |
| G1 Environment | PASS at source level |
| G2 Contracts/protocol | BLOCKED pending Phase 0B corrections |
| G3 Mock smoke | PASS for mock scope; tau2 no-key integration pending |
| G4 Pilot | NOT STARTED |
| G5 Search | NOT STARTED |

Do not mark G2 or G3 fully passed without committed tests and reproducible evidence.
