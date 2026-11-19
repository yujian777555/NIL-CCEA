# Project Status

**Last updated:** 2026-11-19  
**Overall state:** PRE-EXPERIMENT  
**Current workstream:** Phase 0B — adapter and estimator correctness corrections  
**Current execution branch:** `phase0b-adapter-statistical-corrections`  
**Phase 0A PR:** [#1](https://github.com/yujian777555/NIL-CCEA/pull/1), open and not merged  
**Authoritative prompt:** [docs/EXECUTOR_PROMPT_PHASE0B.md](docs/EXECUTOR_PROMPT_PHASE0B.md)

## Phase 0A completed

- Primary-source literature audit completed for the closest Agent module-evolution and linkage/cooperative co-evolution neighbors.
- tau2-bench v1.0.1 text-v1 selected as the primary environment candidate at source-audit level; ToolSandbox retained as a diagnostic fallback.
- Four provisional module contracts, pilot design R1, local mock runner, manifest/cost schemas, and tau2 adapter entry point added.
- Executor-reported local test suite: 11 passed; mock run: 32 episodes; real API calls: 0.
- No real tau2 execution, performance result, or novelty claim exists.

## Independent review findings

The read-only review is recorded in [docs/PHASE0A_INDEPENDENT_REVIEW.md](docs/PHASE0A_INDEPENDENT_REVIEW.md). It found repairable blockers:

1. tau2 Tool schema extraction reads attributes that do not exist in the pinned tau2 Tool class; it must use `params` or `openai_schema`.
2. The interaction estimator treats task-seed pairs as independent clusters, contrary to the task-level clustering protocol.
3. Incomplete factorial contexts and failed episodes can be silently omitted, changing the estimand.
4. Adapter tool proposals are not checked against the selected tool or validated against the real parameter schema; invalid calls can silently fall through to Synthesizer.
5. Persistent plan state is declared but not updated.
6. No test currently instantiates the adapter against the pinned tau2 package.
7. Required task metadata can silently remain `unknown`.

These findings do not invalidate NIL-CCEA. They block G2/G3 until corrected.

## Current decisions

- Keep PR #1 open; do not merge until the blockers are fixed and reviewed.
- Do not run paid API calls or formal pilot yet.
- Continue using the exact tau2 commit pinned in `experiments/pilot_factorial/environment.lock.json`.
- Prepare a separate Python 3.12/3.13 environment for tau2; retain the host Python 3.10 mock environment.
- Keep evolutionary computation and interaction-linkage as the research core.
- Do not implement the full evolutionary optimizer until interaction measurement is reliable.

## Gate status

| Gate | State | Evidence |
|---|---|---|
| G0 Literature | PASS | Phase 0A primary-source audit |
| G1 Environment | PASS at source level | tau2 API inspected; adapter not yet executed |
| G2 Contracts/protocol | BLOCKED pending corrections | See independent review F0-1 through F0-7 |
| G3 Smoke | PASS for local mock only | 11 tests reported; tau2 adapter integration not tested |
| G4 Pilot | NOT STARTED | Zero real benchmark episodes |
| G5 Search | NOT STARTED | No empirical linkage validation |

## Immediate next steps

1. Correct tool schema extraction, adapter control flow, state persistence, and task metadata.
2. Correct task-level clustering and fail-closed missing/duplicate-cell handling in the interaction estimator.
3. Add pinned tau2 v1.0.1 no-key integration tests in Python 3.12/3.13.
4. Freeze endpoint, task IDs, delta, Holm inference, failure/retry policy, and task-cluster sensitivity analysis.
5. Produce a provider/model-specific cost estimate and request explicit approval before any paid smoke.

No real benchmark result, statistical significance, algorithmic improvement, or novelty claim is asserted.
