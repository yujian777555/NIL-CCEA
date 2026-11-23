# Next Steps

**Current task:** execute [Phase 0E.1 smoke factory, shared-budget enforcement, and protocol freeze](docs/EXECUTOR_PROMPT_PHASE0E.md).

## Frozen model decision

User-selected model: `deepseek-flash` for Planner, Selector, Caller, Synthesizer, Agent, and User Simulator.

- Base URL: `https://api.deepseek.com`
- Current served model publicly listed as of 2026-11-23: DeepSeek-V4.1-Flash-1017; capture returned model and system fingerprint because the alias is mutable.
- Thinking/CoT disabled: `thinking={"type":"disabled"}`, `reasoning_effort="none"`.
- JSON mode for structured content; native Tool Calls for Caller; validate locally.
- Temperature 0.0; max output 512; input cap 2,000.
- Direct network only; dedicated HTTPX client `trust_env=false`; no system proxy.
- Key from `DEEPSEEK_API_KEY`; never store in Git.
- Do not use GPT-4.1, GPT-6 Luna, deepseek-v4-pro, or retired DeepSeek model aliases.

## Conservative DeepSeek cost ceilings

Peak cache-miss rates: $0.30/M input, $1.20/M output; cache-hit peak $0.006/M; off-peak half. Budget on peak cache-miss:
- $0.0012144/request
- $0.145728/episode (120 logical requests); $0.291456 if every request retries once
- $9.326592/64-episode smoke (7,680 normal requests); $18.653184 if every request retries once (15,360 physical attempts)
- $55.959552/384-episode pilot (46,080 normal requests); $111.919104 if every request retries once (92,160 physical attempts)
- Proposed 64-episode spend ceiling: $20.00, not authorized; separate $80 hard stop is not spending authorization

Keep $80 smoke and $400 pilot hard caps. Recheck pricing before any paid call.

## Phase 0C progress

- DeepSeek client, four provider-backed modules, and the real tau2 factorial runner are implemented.
- Fake Client and real tau2 no-API tests pass. No DeepSeek request has been sent.
- GitHub Actions run `44914883210` passed on Phase 0C implementation head `f97467b8dcfb60a3d36cfd6638cd4e507509bc4a`.

## Required order

1. Recheck DeepSeek endpoint, model availability, and pricing.
2. Obtain independent review of the client and runner.
3. Ask for explicit paid-smoke approval only after all preflight gates pass.

## Hard guardrails

- No paid API call without explicit user approval.
- Model choice is already made; do not ask the user to choose GPT-4.1 or GPT-6 Luna again.
- No model mixing within a factorial dataset.
- No CoT/thinking mode.
- JSON outputs must be validated; never trust raw model tool arguments.
- DeepSeek requests must bypass the system proxy.
- Do not implement the full evolutionary optimizer before trustworthy interaction measurements.
- Preserve all failures, retries, raw trajectories, manifests and costs.
- Two exploratory task clusters are descriptive only.
- Null/weak interaction triggers diagnosis and further experiments, not automatic termination or fabricated positive results.

## Gate status

| Gate | State |
|---|---|
| G0 Literature | PASS |
| G1 Environment | PASS for tested scope |
| G2 Contracts/protocol | NEEDS_REVISION |
| G3 No-API integration | PASS |
| G3 Real-runner readiness | PASS for no-API scope |
| G4 Paid exploratory smoke | NOT STARTED |
| G5 Search | NOT STARTED |


## Phase 0D — immediate execution order

1. Recheck the current branch/PR head and reproduce the 29-test no-API suite plus the pinned tau2 32-cell no-API integration.
2. Obtain a genuinely independent review; PR #2 currently has no submitted review or review threads.
3. Fix retry mismatch and remove whole-episode replay; persist request-level audit/cost events and partial trajectories.
4. Enforce response model/fingerprint identity, input/request limits, and per-request/episode/smoke budget guards.
5. Re-run no-API tests and CI. No provider endpoint request is allowed during Phase 0D.
6. Freeze exploratory tasks retail 5 and airline 2 using the first-listed-per-family rule, after verifying both exist in the pinned test split.
7. Produce an exact cost/request ceiling and ask the user for explicit approval. Wait; do not execute the 64-episode smoke without approval.

Official docs rechecked 2026-11-23:
- `deepseek-flash` is listed and served as DeepSeek-V4.1-Flash-1017.
- Chat Completions: `https://api.deepseek.com`.
- Peak cache-miss input $0.30/M, cache-hit input $0.006/M, output $1.20/M.
- Public documentation does not substitute for checking the actual response model and fingerprint on the first approved completion.

## Preliminary source-review items (must be independently confirmed and fixed)

- Client retry default is 2 while the protocol allows one retry per request.
- Runner retries whole episodes, risking duplicate paid requests.
- Request audit events are not yet durably linked to episode artifacts.
- Fingerprint tracking is not enforced in the request path and does not validate response.model.
- Request/cost hard-stop enforcement and 2,000-token input enforcement need verification.
- Runner exception paths can lose partial trajectories.

Smoke task candidate: retail task 5 + airline task 2, selected deterministically as the first listed test task in each locked family. The 64-episode smoke is exploratory only (two task clusters); do not claim significance or use it as a reliable task-cluster power estimate.
# Phase 0D closeout state

- Local Phase 0D code corrections and independent read-only review are complete. See `docs/PHASE0D_INDEPENDENT_REVIEW.md`.
- Host and pinned tau2 Python 3.12.16 no-API suites each pass 39 tests. The pinned suite exercises real tau2 v1.0.1 classes and a 32-cell factorial runner.
- DeepSeek API calls remain 0. No API key was read. The 64-episode smoke remains blocked until the user grants explicit paid-run approval.
- Before approval, verify provider pricing again, construct a provider-backed User Simulator exposing `deepseek-flash`, generate the retail-5 and airline-2 pre-run manifest, and set a `RequestBudget` sized for the chosen retry profile.
- After approval, run only the frozen exploratory smoke, stop on the first model or fingerprint mismatch, preserve all raw artifacts, and report descriptive interaction estimates without significance or performance claims.
- Next-stage handoff prompt: `docs/EXECUTOR_PROMPT_PHASE0E.md`.


## Phase 0E — current blockers and exact next actions

1. Wire `DeepSeekTau2UserSimulator` into the actual smoke factory through `Tau2FactorialRunner.user_factory_with_environment` and pass the same `RequestBudget` object to all four module clients and the user client.
2. Keep the user adapter's episode context and request events in the same raw ledger as module calls.
3. Review retail task 5's open tau2 issue `issue_770466c1` about missing authentication enforcement. Both retail 5 and airline 2 are in the pinned test split. Do not silently replace retail 5. Record impact and request a protocol amendment if it should be changed.
4. Re-run host tests, pinned Python 3.12.16/tau2 tests, 32-cell no-API Orchestrator integration, and CI after the wiring change.
5. Build a new pre-run manifest with the actual final code SHA, protocol hash, task IDs, seeds, all 16 configurations, model alias, UserSimulator adapter, and RequestBudget profile.
6. Only after these checks pass, ask the user for explicit approval. No API key read or provider request before approval.

## Phase 0E current gate snapshot (2026-11-23)

- Phase 0D code and independent read-only review: PASS per reported evidence.
- Phase 0D CI: PASS, run `45046796585` on SHA `b1c197eb5973575ae2ffa7c5c4cfe0d0fc9bf3a9`.
- Phase 0E User Simulator adapter commit: `d7273064ad20f4452347ec0680c3ec1e14278f18`; CI run `45100451548` passed.
- DeepSeek public docs/pricing: PASS; last checked 2026-11-23; no price change.
- Task split membership: PASS for retail 5 and airline 2.
- Retail task 5 known issue impact: NEEDS REVIEW.
- Controlled provider-backed UserSimulator: IMPLEMENTED and fake-client tested; smoke-factory wiring pending.
- Actual response model/fingerprint: unverified until first approved completion.
- Paid 64-episode smoke: NOT AUTHORIZED / NOT STARTED.
- Linkage-aware evolutionary search: not started.


## Phase 0E.1 — exact remaining execution order

1. Build a paid-smoke factory with five distinct DeepSeekClient objects: Planner, Selector, Caller, Synthesizer, User Simulator.
2. Share the exact same RequestBudget object and ModelFingerprintTracker object across all five clients. Do not share the client object itself; module context and request-event attribution must remain separate.
3. Add task-aware environment selection. The frozen task list mixes Retail 5 and Airline 2; choose a fresh environment from `task.user_scenario.instructions.domain` for every episode.
4. Strengthen Tau2FactorialRunner so evaluate=True fails closed unless all five clients have identical model/endpoint/decoding, share the exact same budget/tracker objects, and expose event draining. Reject stock tau2 UserSimulator and shared module clients.
5. Freeze an immutable smoke manifest containing code SHA, tau2 SHA, protocol hash, task IDs, seeds, all 16 configurations, request bounds, budget, model configuration, and Retail task 5 quality flag.
6. Retain Retail task 5 unchanged with the explicit limitation in `docs/PHASE0E_PROTOCOL_DECISION.md`. Its tools do not enforce authenticated-user state; task reward_basis DB + NL_ASSERTION does not guarantee authentication compliance. No authentication/privacy/safety claim is allowed.
7. Run the host no-API suite (current reported baseline: 39 pass, 12 tau2-dependent skips), pinned Python 3.12.16 + tau2 v1.0.1 suite (39 pass), 32-cell Orchestrator integration, new mixed-domain/factory tests, and final CI.
8. Only after all checks pass, ask the user to approve the 64-episode paid smoke. Do not read `DEEPSEEK_API_KEY` or send a provider request before explicit approval.

### Corrected smoke bounds

- Each Agent response invokes Planner + Selector + one of Caller/Synthesizer: up to 3 model calls.
- Conservative per-episode bound: 90 Agent module calls + 30 User Simulator calls = 120 logical requests.
- One retry reserved per request: 240 physical attempts per episode.
- 64 episodes: 7,680 normal logical requests / 15,360 maximum physical attempts.
- Cost: $9.326592 without retries / $18.653184 with one retry for every request.
- Proposed spend ceiling: $20.00 (NOT AUTHORIZED); separate hard stop: $80.
- 384-episode pilot: $55.959552 without retries / $111.919104 with one retry for every request.

### Current decisions

- Model remains `deepseek-flash`, no thinking, direct `https://api.deepseek.com`.
- Retail task 5 remains in the exploratory candidate, unchanged, with issue `issue_770466c1` disclosed.
- No API key read, no DeepSeek API request, no paid Episode.
- Linkage-aware evolutionary search remains NOT STARTED until reliable interaction measurements exist.
