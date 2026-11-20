# Executor Handoff — NIL-CCEA

**Repository:** https://github.com/yujian777555/NIL-CCEA
**Current branch:** `phase0b-adapter-statistical-corrections`
**Phase 0A branch:** `phase0a-literature-environment-audit`
**Phase 0A HEAD:** `6bed028a4675a75928734b633bbfae49d6b98b14`
**PR #1:** https://github.com/yujian777555/NIL-CCEA/pull/1 (open; do not merge yet)
**Authoritative prompt:** [docs/EXECUTOR_PROMPT_PHASE0C.md](EXECUTOR_PROMPT_PHASE0C.md)
**Independent review:** [docs/PHASE0A_INDEPENDENT_REVIEW.md](PHASE0A_INDEPENDENT_REVIEW.md)

## Current research state

PRE-EXPERIMENT. Phase 0A literature and source-level environment audits are complete. Phase 0B corrections are implemented. Phase 0C code is implemented through the DeepSeek client, four real modules, and real tau2 factorial runner. The executor reports 29 passing tests in the host environment and 29 passing tests against real tau2 v1.0.1 classes in Python 3.12.16 with zero DeepSeek API calls. No real benchmark episode, performance gain, statistical significance, or novelty claim exists.

## Key review blockers

1. Adapter reads `tool.parameters` / `tool.schema`, but pinned tau2 Tool exposes `params` and `openai_schema`.
2. Interaction estimator treats `(task_id, seed)` as independent clusters; it must bootstrap task IDs with seeds nested.
3. Missing factorial cells/contexts and failed records can be silently omitted; implement fail-closed completeness and explicit missingness policy.
4. Caller proposal is not required to match Selector's chosen tool and is not validated against the actual tau2 parameter schema.
5. `plan_state` is declared but never persisted.
6. No actual tau2 package integration tests exist.
7. Task metadata defaults to `unknown`; experiment mode must inject and validate canonical task metadata.

The seven blockers are implemented and covered by regression tests. Provider price verification and paid smoke approval remain open gates.

## Phase 0C completed implementation

- DeepSeek client is dependency-injected and direct-only with HTTPX `trust_env=False`.
- DeepSeek JSON and native tool-call paths are covered by Fake Client tests.
- Real module classes and a real tau2 factorial runner are implemented.
- No-API tau2 tests run against real Tool, Environment, HalfDuplexAgent, Orchestrator, and task classes.

## Immediate actions

- Follow [Phase 0C prompt](EXECUTOR_PROMPT_PHASE0C.md) in order.
- Use Python 3.12.16 and tau2 exact commit `fc0055dc4e0a316c3f83133267fbd6faaa770992`.
- Reproduce the no-API tests with `scripts/run_tau2_no_api_tests.ps1`.
- Verify DeepSeek `deepseek-flash` availability and pricing and obtain explicit user approval before any paid request.
- Run the frozen 2-task exploratory smoke only after approval.

## Statistical unit

One canonical task instance is one independent cluster. Multiple seeds and all 16 configurations are repeated measurements within that task. For the planned 12 tasks × 2 seeds, the independent cluster count is 12, not 24.

For every pairwise interaction, all four contexts of the other two binary module slots and all four pair cells must be complete. Missing infrastructure episodes must not be silently dropped or converted to task failures. Six pairs receive one Holm step-down correction.

## Boundaries

- Keep NIL-CCEA separate from every other repository.
- Keep evolutionary computation and module-interaction linkage as the method core.
- Fixed total Agent-execution budget is a fairness constraint, not a budget-allocation contribution.
- No full optimizer or model training in Phase 0B.
- No paid API call before explicit approval.
- Do not merge PR #1 until the blockers are corrected and independently reviewed.
- Null or weak interactions trigger diagnosis, not automatic project termination.

## Required handoff report

Report exact start/end SHA, branch, changed files, pinned tau2 commit, Python version, tests, API calls/cost, task-level cluster counts, missingness policy, endpoint/delta/Holm freeze, Gate status, and the next concrete experiment.
