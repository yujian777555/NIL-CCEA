# Next Steps

**Current task:** execute [Phase 0C real-runner readiness and provider lifecycle](docs/EXECUTOR_PROMPT_PHASE0C.md).

## Verified baseline

- Repository: `yujian777555/NIL-CCEA`
- Branch: `phase0b-adapter-statistical-corrections`
- HEAD: `0031055c14ac50dec9d6436e3d35659897d02016`
- PR #2: open, not merged; base is `phase0a-literature-environment-audit`
- PR #1: open, not merged
- tau2: v1.0.1, commit `fc0055dc4e0a316c3f83133267fbd6faaa770992`
- Phase 0B reported no-API tests: 21 passed, 0 real API calls

## Current verified pricing

- GPT-4.1: $2/M input, $0.50/M cached input, $8/M output.
- Existing upper-bound calculations use uncached input pricing and are correct.
- GPT-4.1 is deprecated; announced shutdown is 2027-01-14.
- Official recommended replacement: GPT-6 Luna; standard price $0.10/M input and $0.50/M output.
- Model replacement is reference-only until the user approves a protocol change.

## Required order

1. Fix `tau2_adapter.py`: invoke Caller only for `tool_call`; test respond and stop branches with a Caller that must not be invoked.
2. Implement real provider-backed Planner, Selector, Caller, Synthesizer wrappers; preserve mock variants as test doubles.
3. Implement a real tau2 factorial runner that builds all 16 configurations, resets each task/seed, executes Orchestrator, and writes trajectories/manifests/usage/retry/cost records.
4. Use fake provider clients for all no-key tests; prove 0 completion calls.
5. Resolve the GPT-4.1 deprecation decision before any paid call. Do not mix models inside a factorial dataset.
6. Recompute task-level sensitivity/power for the intended `delta=0.05`; the existing table is for `delta=0.10`.
7. Mark the old 32-episode smoke plan superseded by the 64-episode 2-task × 2-seed plan.
8. Update package README, add/repair CI, and obtain independent review.
9. Only then ask for explicit user approval for the 64-episode exploratory smoke.

## Hard guardrails

- No paid API call without explicit user approval.
- No model switch without a versioned protocol update and explicit user approval.
- No model mixing within one factorial dataset.
- No full evolutionary optimizer yet.
- No changes to confirmatory task IDs, endpoint, delta, or sample size after observing confirmatory outcomes.
- Two exploratory task clusters are descriptive only, not inferential evidence.
- Preserve all failures, retries, raw trajectories, manifests, and costs.
- A null or weak interaction triggers diagnosis, not automatic project termination.

## Gate status

| Gate | State |
|---|---|
| G0 Literature | PASS |
| G1 Environment | PASS |
| G2 Contracts/protocol | NEEDS_REVISION |
| G3 No-API integration | PASS for tested scope |
| G3 Real-runner readiness | BLOCKED |
| G4 Paid exploratory smoke | NOT STARTED |
| G5 Search | NOT STARTED |

Do not mark G2 or real-runner readiness as passed until committed tests and reproducible evidence exist.
