# Executor Handoff — NIL-CCEA

**Repository:** https://github.com/yujian777555/NIL-CCEA  
**Current branch:** `phase0b-adapter-statistical-corrections`  
**Phase 0A branch:** `phase0a-literature-environment-audit`  
**Phase 0A HEAD:** `6bed028a4675a75928734b633bbfae49d6b98b14`  
**PR #1:** https://github.com/yujian777555/NIL-CCEA/pull/1 (open; do not merge yet)  
**Authoritative prompt:** [docs/EXECUTOR_PROMPT_PHASE0B.md](EXECUTOR_PROMPT_PHASE0B.md)  
**Independent review:** [docs/PHASE0A_INDEPENDENT_REVIEW.md](PHASE0A_INDEPENDENT_REVIEW.md)

## Current research state

PRE-EXPERIMENT. Phase 0A literature and source-level environment audits are complete. The local mock runner is implemented and the executor reports 11 passing tests and zero real API calls. The tau2 adapter has not yet been executed against the pinned package. No real benchmark episode, performance gain, statistical significance, or novelty claim exists.

## Key review blockers

1. Adapter reads `tool.parameters` / `tool.schema`, but pinned tau2 Tool exposes `params` and `openai_schema`.
2. Interaction estimator treats `(task_id, seed)` as independent clusters; it must bootstrap task IDs with seeds nested.
3. Missing factorial cells/contexts and failed records can be silently omitted; implement fail-closed completeness and explicit missingness policy.
4. Caller proposal is not required to match Selector's chosen tool and is not validated against the actual tau2 parameter schema.
5. `plan_state` is declared but never persisted.
6. No actual tau2 package integration tests exist.
7. Task metadata defaults to `unknown`; experiment mode must inject and validate canonical task metadata.

## Immediate actions

- Follow [Phase 0B prompt](EXECUTOR_PROMPT_PHASE0B.md) in order.
- Use Python 3.12 or 3.13 and install tau2 from exact commit `fc0055dc4e0a316c3f83133267fbd6faaa770992`.
- Add no-API-key tests using actual tau2 Tool and message classes.
- Correct task-level inference and freeze the protocol before any paid run.
- Prepare a detailed provider/model cost estimate and obtain explicit user approval before a paid exploratory smoke.

## Statistical unit

One canonical task instance is one independent cluster. Multiple seeds and all 16 configurations are repeated measurements within that task. For the planned 12 tasks × 2 seeds, the independent cluster count is 12, not 24.

For every pairwise interaction, all four contexts of the other two binary module slots and all four pair cells must be complete. Missing infrastructure episodes must not be silently dropped or converted to task failures.

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
