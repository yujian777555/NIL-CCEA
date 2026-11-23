# Executor Handoff — NIL-CCEA

**Repository:** https://github.com/yujian777555/NIL-CCEA
**Branch:** `phase0b-adapter-statistical-corrections`
**Phase 0C implementation baseline SHA:** `f97467b8dcfb60a3d36cfd6638cd4e507509bc4a`
**Phase 0D final implementation SHA:** `b1c197eb5973575ae2ffa7c5c4cfe0d0fc9bf3a9`
**Latest Phase 0D GitHub Actions run:** `45046796585` — success
**Phase 0E current implementation SHA:** `d7273064ad20f4452347ec0680c3ec1e14278f18`
**Latest verified Phase 0E code CI:** `45100451548` — success; final documentation CI on reported d63bf1b: `45100563417` — success
**Phase 0E.1 implementation SHA:** `bcc762e711815316dae17e4eef8bdbd4f2a815ee`
**Phase 0E.1 final documentation head:** `bbf46d9688bd716c5bbdebc43fd5b8fb198e9193`
**Latest Phase 0E.1 CI:** `45105192442` — success
**PR #2:** https://github.com/yujian777555/NIL-CCEA/pull/2 (open)
**PR #1:** https://github.com/yujian777555/NIL-CCEA/pull/1 (open)
**Authoritative prompt:** [docs/EXECUTOR_PROMPT_PHASE0E.md](EXECUTOR_PROMPT_PHASE0E.md)

## User-selected model

**Use DeepSeek Flash exclusively** for all module slots, Agent, and User Simulator:
- API model alias: `deepseek-flash`
- Current served model publicly listed as of 2026-11-23: DeepSeek-V4.1-Flash-1017; alias is mutable.
- OpenAI-compatible Chat Completions, base URL `https://api.deepseek.com`.
- Disable thinking/CoT: `thinking={"type":"disabled"}`, `reasoning_effort="none"`.
- JSON mode for structured content; Caller uses native Tool Calls and local schema validation.
- Temperature 0.0; max output 512; input cap 2,000.
- Direct connection: dedicated HTTPX client with `trust_env=false`, bypass system proxy.
- Read `DEEPSEEK_API_KEY` from environment; never commit secrets.
- Record requested model, response model, system fingerprint, request ID, prompt hash and usage.

Official docs:
- https://api-docs.deepseek.com/quick_start/pricing/
- https://api-docs.deepseek.com/api/create-chat-completion/

## Conservative cost profile

Peak cache-miss prices: $0.30/M input and $1.20/M output; peak cache-hit input $0.006/M; off-peak prices half. Budget uses peak cache-miss rates:
- Request $0.0012144
- Episode 120 logical requests: $0.145728; one retry each: $0.291456
- Smoke 64 episodes: 7,680 normal / 15,360 max physical attempts; $9.326592 no-retry / $18.653184 one-retry upper bound
- Pilot 384 episodes: 46,080 normal / 92,160 max physical attempts; $55.959552 no-retry / $111.919104 one-retry upper bound

Hard caps: $80 smoke, $400 pilot. Recheck price before paid run.

## Research state

Phase 0A and Phase 0B are reported complete. Phase 0C client, modules, and no-API real tau2 runner are implemented. No real DeepSeek request, paid benchmark episode, statistical significance, performance gain, or novelty claim exists.

## Phase 0C completed implementation

- Direct DeepSeek client with no system proxy, JSON/native tool calls, audit events, usage/fingerprint checks, and safe bounded retries.
- Four DeepSeek module wrappers and binary manifest variants.
- Real tau2 factorial runner and 32-cell no-API Orchestrator test.
- 29 total tests pass in host and independent tau2 environments.
- GitHub Actions run `44914883210` passed on implementation head `f97467b8dcfb60a3d36cfd6638cd4e507509bc4a`.
- Self-review is recorded in `docs/PHASE0C_INDEPENDENT_REVIEW.md`; external independent review is still required.

## Remaining work

1. Establish GitHub Actions result and independent review.
2. Verify DeepSeek endpoint and pricing immediately before any paid request.
3. Obtain explicit paid-smoke approval only after preflight is complete.

## Gates

- G0 Literature: PASS
- G1 Environment: PASS for tested scope
- G2 Contracts/protocol: NEEDS_REVISION
- G3 No-API integration: PASS, 29 tests
- G3 Real-runner readiness: PASS for no-API scope, 32 cells
- G4 Paid smoke: NOT STARTED
- G5 Search: NOT STARTED

The user has selected the model but has **not** authorized paid API calls. Keep this repository isolated from all other projects.


## Phase 0D handoff — 2026-11-23

- Phase 0C no-API implementation is complete as reported; no DeepSeek API request or paid benchmark episode has been executed.
- PR #2 remains open/unmerged. At handoff, there are no submitted reviews or review threads; external independent review is pending.
- Official public DeepSeek docs currently list `deepseek-flash` served by DeepSeek-V4.1-Flash-1017. This does not verify a live response model or fingerprint.
- Phase 0D prompt: [docs/EXECUTOR_PROMPT_PHASE0D.md](EXECUTOR_PROMPT_PHASE0D.md).
- Phase 0D is strictly no-API. Resolve retry accounting, remove episode replay, persist request-level audit and partial trajectories, enforce model/fingerprint and budgets, obtain independent review, and rerun tests/CI.
- Proposed exploratory smoke tasks: retail 5 and airline 2 (first listed task per locked family); verify against the pinned test split and freeze before any paid call.
- The user has not authorized paid API requests. Ask for explicit approval after all preflight gates pass.
- The 64-episode smoke is exploratory with two task clusters only. Do not claim significance or estimate formal power from n=2 tasks.
- Keep NIL-CCEA isolated from all other repositories; do not merge PR #1 or #2.
# Phase 0D handoff update

- Branch remains `phase0b-adapter-statistical-corrections`.
- Phase 0D code corrections are implemented locally. The independent read-only review is recorded in `docs/PHASE0D_INDEPENDENT_REVIEW.md`.
- The DeepSeek client now enforces one safe retry maximum, delivery-unknown no-replay, input/request/cost reservation, model/fingerprint validation, cache-aware accounting, and per-attempt audit events.
- The real tau2 runner now has no episode-level retry, preserves partial trajectories, fails closed on missing ENV reward, requires explicit budgets for evaluated runs, checks module/User Simulator model consistency, and writes `episodes.jsonl`, `request_events.jsonl`, `cost_ledger.json`, and `run_summary.json` incrementally.
- Host and pinned tau2 Python 3.12.16 suites each pass 39 tests. DeepSeek API calls and key reads remain 0.
- Paid smoke gate remains closed. The frozen candidate is retail task 5 plus airline task 2, seeds 0 and 1, all 16 configurations, 64 exploratory episodes. No statistical significance or algorithmic improvement claim is allowed.
- Next executor must verify the final GitHub Actions run on the pushed SHA, recheck public pricing, and wait for explicit user approval before any provider request.
- Next-stage executor prompt: [docs/EXECUTOR_PROMPT_PHASE0E.md](EXECUTOR_PROMPT_PHASE0E.md).


## Phase 0E handoff update — 2026-11-23

- Reported Phase 0D final SHA: `b1c197eb5973575ae2ffa7c5c4cfe0d0fc9bf3a9`; GitHub PR #2 head matches; CI run `45046796585` passed.
- Official DeepSeek documentation and pricing rechecked 2026-11-23; public values unchanged. The actual response model and fingerprint remain unverified until an explicitly approved first completion.
- Pinned tau2 test split confirms retail task 5 and airline task 2 are both test tasks.
- Retail task 5 has an open task metadata issue `issue_770466c1` about the retail domain allowing user-level actions without authentication. Assess its impact before final task freeze; do not silently change task IDs.
- P0 preflight finding: tau2's stock UserSimulator uses `tau2.utils.llm_utils.generate` -> LiteLLM `completion()`. A string-level `llm="deepseek-flash"` check does not prove the user simulator uses the NIL-CCEA DeepSeekClient, RequestBudget, ledger, identity checks, or direct transport.
- Implemented `src/nil_ccea/tau2_user_simulator.py`, a provider-backed tau2 half-duplex UserSimulator adapter using the NIL-CCEA DeepSeekClient. Four pinned fake-client tests prove LiteLLM is not invoked, native user tools are validated, the shared budget can be attached, and user request events carry episode/module attribution.
- The remaining integration step is to wire this adapter into the paid smoke factory and pass one shared RequestBudget to all module and user clients.
- Preflight review: [docs/PHASE0E_PREFLIGHT_REVIEW.md](PHASE0E_PREFLIGHT_REVIEW.md).
- Authoritative prompt: [docs/EXECUTOR_PROMPT_PHASE0E.md](EXECUTOR_PROMPT_PHASE0E.md).
- No API key read, no DeepSeek request, and no paid episode. The 64-episode smoke is not authorized.


## Phase 0E.1 handoff — 2026-11-23

- Verified current reported code/final SHA: `d63bf1bd0062bb99b86ba61240caa4658835b5e7`; PR #2 remains open/unmerged. Code CI `45100451548` and final CI `45100563417` passed.
- User-reported no-API suite: host 39 passed / 12 tau2-dependent skipped; pinned Python 3.12.16 + tau2 v1.0.1: 39 passed. 32-cell real tau2 Orchestrator no-API integration remains reported PASS.
- Provider-backed User Simulator adapter is implemented. The paid smoke factory is still pending.
- Factory must use five distinct DeepSeekClient objects (four module roles + user simulator), sharing one exact RequestBudget and one exact ModelFingerprintTracker. Do not reuse a single client across module slots because per-slot episode context would overwrite request attribution.
- Runner must select a fresh environment per task domain. The frozen smoke includes both Retail 5 and Airline 2; current `environment_factory()` no-arg API cannot safely choose the correct domain for a mixed task list.
- Fail closed unless all five clients share budget/tracker by object identity, have identical model/endpoint/decoding/retry settings, and have separate request-event streams.
- Corrected cost model: 3 module calls per Agent response (Planner + Selector + Caller/Synthesizer), plus up to 30 User Simulator calls. Conservative bound is 120 logical requests per episode; 240 physical attempts with one retry. 64 episodes = 7,680 normal / 15,360 max physical requests; $9.326592 no-retry / $18.653184 retry-every-request upper bound.
- Proposed $20 spend ceiling is not authorized. Separate $80 hard stop is not spending authorization.
- Retail task 5 is retained unchanged by protocol decision, with open issue `issue_770466c1` disclosed. Its tools do not enforce authentication state; ENV reward basis DB + NL_ASSERTION does not guarantee authentication-sequence compliance. No auth/privacy/safety claim.
- Preflight protocol decision: [docs/PHASE0E_PROTOCOL_DECISION.md](PHASE0E_PROTOCOL_DECISION.md).
- Corrected cost profile: [experiments/pilot_factorial/cost_profile.json](../experiments/pilot_factorial/cost_profile.json).
- Authoritative next prompt: [docs/EXECUTOR_PROMPT_PHASE0E.md](EXECUTOR_PROMPT_PHASE0E.md).
- No API key read, no provider request, no paid Episode. Wait for explicit approval after smoke factory, mixed-domain tests, manifest, and CI pass.

## Phase 0E.1 implementation update

- Current code SHA: `bcc762e711815316dae17e4eef8bdbd4f2a815ee`.
- Smoke Factory creates five distinct clients with one shared RequestBudget and one shared ModelFingerprintTracker.
- Runner supports task-aware Retail/Airline environment selection and strict evaluated-run validation.
- Immutable manifest: `experiments/pilot_factorial/manifests/phase0e1_smoke_prerun_bcc762e7118153.json`.
- Manifest hash: `66132bb3e7f83661b5acecfd95340da37162734287be72a2baca3384324ff0de`.
- Bounds: 7,680 logical requests, 15,360 physical reservations, `$9.326592` no retry, `$18.653184` retry-every-request, proposed `$20` ceiling, separate `$80` hard stop.
