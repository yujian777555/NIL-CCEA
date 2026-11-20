# Project Status

**Last updated:** 2026-11-20
**Overall state:** PRE-EXPERIMENT
**Current workstream:** Phase 0C — DeepSeek Flash client, real modules, and tau2 execution chain
**Current execution branch:** `phase0b-adapter-statistical-corrections`
**Phase 0A PR:** [#1](https://github.com/yujian777555/NIL-CCEA/pull/1), open and not merged
**Authoritative prompt:** [docs/EXECUTOR_PROMPT_PHASE0C.md](docs/EXECUTOR_PROMPT_PHASE0C.md)

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

## Phase 0B corrections completed

- The estimator now treats task as the independent cluster, with seeds `0` and `1` nested within task.
- Full 16-configuration and four-context completeness, duplicate rejection, and explicit task/infrastructure failure handling are enforced.
- Task-level bootstrap, permutation p-values, six-pair Holm correction, and regression tests are implemented.
- The tau2 adapter now uses real `Tool.openai_schema` and `Tool.params`, validates selector/caller consistency and arguments, handles `ToolMessage` and `MultiToolMessage`, persists `plan_state`, injects task metadata, and records the orchestrator seed.
- Real tau2 v1.0.1 classes and Orchestrator pass 29 no-API tests in Python 3.12.16. The LiteLLM test stub raises on any completion call.
- The frozen candidate protocol is recorded in `docs/PHASE0B_PROTOCOL_FREEZE.md`. Provider pricing remains to be verified before any paid call.

## Phase 0C implementation completed so far

- Added a dependency-injected DeepSeek Flash client with direct HTTPX transport, `trust_env=False`, JSON mode, native tool-call parsing, usage/cost accounting, fingerprint tracking, classified errors, and bounded safe retries.
- Added DeepSeek Planner, Selector, Caller, and Synthesizer implementations behind the existing contracts.
- Added a real tau2 factorial runner that creates fresh environments, uses the real Orchestrator, records manifests and trajectories, and supports ENV evaluation when enabled.
- Added Fake Client tests and a no-API tau2 runner test. No DeepSeek request has been sent.

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
| G1 Environment | PASS | tau2 API and real no-API adapter execution |
| G2 Contracts/protocol | NEEDS_REVISION | Frozen candidate exists, provider price verification remains |
| G3 Smoke | PASS for no-API scope | 28 tests pass on host and tau2 Python 3.12 environments |
| G4 Pilot | NOT STARTED | Zero real benchmark episodes |
| G5 Search | NOT STARTED | No empirical linkage validation |

## Immediate next steps

1. Verify DeepSeek provider/model availability and pricing against the declared cost profile.
2. Request explicit approval before any paid DeepSeek request.
3. Run 2 tasks × 2 seeds × 16 configurations and preserve all raw outputs.
4. Reassess task-level variance and the sensitivity table before formal pilot approval.

No real benchmark result, statistical significance, algorithmic improvement, or novelty claim is asserted.
