# Executor Handoff — NIL-CCEA

**Repository:** https://github.com/yujian777555/NIL-CCEA  
**Branch:** `phase0b-adapter-statistical-corrections`  
**HEAD:** `0031055c14ac50dec9d6436e3d35659897d02016`  
**PR #2:** https://github.com/yujian777555/NIL-CCEA/pull/2 (open; base = `phase0a-literature-environment-audit`)  
**PR #1:** https://github.com/yujian777555/NIL-CCEA/pull/1 (open)  
**Authoritative prompt:** [docs/EXECUTOR_PROMPT_PHASE0C.md](EXECUTOR_PROMPT_PHASE0C.md)  
**Review:** [docs/PHASE0B1_PRICING_AND_SMOKE_READINESS_REVIEW.md](PHASE0B1_PRICING_AND_SMOKE_READINESS_REVIEW.md)

## Research state

Phase 0A literature/environment audit and Phase 0B estimator/tau2 no-API corrections are reported complete. No real tau2 benchmark episode, paid API call, statistical significance, performance gain, or novelty claim exists.

## Pricing and lifecycle

As checked on 2026-11-20, GPT-4.1 standard API rates are $2/M input, $0.50/M cached input, and $8/M output. Existing budget arithmetic is correct and uses the conservative uncached rate.

The configured snapshot `gpt-4.1-2025-04-14` is deprecated with shutdown date 2027-01-14. OpenAI recommends `gpt-6-luna`, whose standard rate is $0.10/M input and $0.50/M output. GPT-6 Luna Chat Completions function calling requires `reasoning_effort=none`.

No model migration has been approved. Do not change the model or make a paid request until the user chooses.

## Remaining pre-smoke blockers

1. `tau2_adapter.py` invokes Caller before checking the selected action; Caller must run only for `tool_call`.
2. Provider-backed module implementations do not exist; current modules are deterministic mocks.
3. A real tau2 factorial runner does not exist; current runner emits mock episodes only.
4. The intended `practical_delta=0.05` is not supported by the existing sensitivity table, which is for `delta=0.10`.
5. Older protocol and README files contain stale descriptions.
6. PR #2 has no GitHub status/check runs at the reviewed SHA.

## Immediate actions

Follow [Phase 0C prompt](EXECUTOR_PROMPT_PHASE0C.md):
- fix Caller control flow and tests;
- implement provider-backed module wrappers and tau2 factorial runner;
- use fake clients for all no-key tests;
- reconcile model lifecycle and practical delta;
- update docs and CI;
- request explicit approval before the 64-episode exploratory smoke.

## Current gates

- G0 Literature: PASS
- G1 Environment: PASS for pinned tau2 source and reported no-key class integration
- G2 Contracts/protocol: NEEDS_REVISION
- G3 No-API integration: PASS for tested scope
- G3 Real-runner readiness: BLOCKED
- G4 Paid smoke: NOT STARTED
- G5 Search: NOT STARTED

Keep the project isolated from other repositories. Do not implement the full optimizer until real interaction measurement is trustworthy.
