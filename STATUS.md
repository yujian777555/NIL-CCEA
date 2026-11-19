# Project Status

**Last updated:** 2026-11-20  
**Overall state:** PRE-EXPERIMENT  
**Current workstream:** Phase 0C — real-runner readiness and provider lifecycle  
**Active branch:** `phase0b-adapter-statistical-corrections`  
**Current HEAD:** `0031055c14ac50dec9d6436e3d35659897d02016`  
**PR #2:** [Phase 0B corrections](https://github.com/yujian777555/NIL-CCEA/pull/2), open, not merged  
**PR #1:** [Phase 0A audit](https://github.com/yujian777555/NIL-CCEA/pull/1), open, not merged  
**Authoritative next prompt:** [docs/EXECUTOR_PROMPT_PHASE0C.md](docs/EXECUTOR_PROMPT_PHASE0C.md)

## Phase 0A / 0B completed (reported)

- Primary-source literature audit and tau2-bench v1.0.1 source audit completed.
- Statistical estimator corrected to task-level clusters, nested seeds, complete factorial validation, explicit failure handling, task bootstrap, permutation p-values, and Holm correction.
- tau2 adapter tested against real v1.0.1 classes and Orchestrator in a no-API Python 3.12.16 environment.
- Executor reports 21 tau2 no-API tests passed and 0 real API calls.
- No real benchmark episodes or performance claims exist.

## Provider pricing verification (2026-11-20)

- OpenAI GPT-4.1 standard input/output rates verified at USD 2.00 / USD 8.00 per million tokens; cached input is USD 0.50.
- Existing cost calculations are arithmetically correct and conservatively use uncached input pricing.
- **Lifecycle issue:** `gpt-4.1-2025-04-14` is deprecated with announced shutdown 2027-01-14. OpenAI recommends `gpt-6-luna`.
- GPT-6 Luna is recorded as an alternative reference only; no model change has been approved.
- No paid API calls have been made.

## Additional pre-smoke review findings

1. `tau2_adapter.py` invokes Caller before checking whether Selector chose `tool_call`; move Caller invocation inside that branch and test respond/stop.
2. No provider-backed Planner/Selector/Caller/Synthesizer or real tau2 factorial runner exists yet; current modules and runner are deterministic mock implementations.
3. The intended `practical_delta=0.05` conflicts with a sensitivity table calculated for `delta=0.10`.
4. An older protocol still lists a 32-episode smoke; the current candidate is 64 episodes.
5. `src/nil_ccea/README.md` has stale adapter-validation wording.
6. PR #2 head currently has zero GitHub status checks/check runs; the reported tests are local executor evidence.

Full review: [docs/PHASE0B1_PRICING_AND_SMOKE_READINESS_REVIEW.md](docs/PHASE0B1_PRICING_AND_SMOKE_READINESS_REVIEW.md).

## Gate status

| Gate | State | Evidence |
|---|---|---|
| G0 Literature | PASS | Phase 0A primary-source audit |
| G1 Environment | PASS | Pinned tau2 source and no-API class/Orchestrator tests reported |
| G2 Contracts/protocol | NEEDS_REVISION | Model lifecycle, delta/power consistency, adapter control flow |
| G3 No-API integration | PASS for tested scope | 21 tau2 no-API tests reported; new Caller branch test pending |
| G3 Real-runner readiness | BLOCKED | Provider-backed modules and real tau2 factorial runner absent |
| G4 Paid exploratory smoke | NOT STARTED | Requires code readiness and explicit user approval |
| G5 Search | NOT STARTED | No real interaction data |

## Immediate next steps

1. Fix Caller invocation semantics and add regression tests.
2. Implement provider-backed module wrappers and a real tau2 factorial runner, using fake clients for all no-key tests.
3. Resolve model lifecycle choice before any paid call; never mix models.
4. Reconcile `delta=0.05` with the power/sensitivity analysis.
5. Align superseded protocol/README docs and establish CI evidence.
6. After independent review, ask for explicit approval before the 64-episode paid exploratory smoke.

No benchmark performance, statistical significance, algorithmic improvement, or novelty claim is asserted.
