# Next Steps

**Current task:** execute [Phase 0D independent audit, provider preflight, and paid-smoke readiness](docs/EXECUTOR_PROMPT_PHASE0D.md).

## Frozen model decision

User-selected model: `deepseek-flash` for Planner, Selector, Caller, Synthesizer, Agent, and User Simulator.

- Base URL: `https://api.deepseek.com`
- Current served model as of 2026-11-20: DeepSeek-V4.1-Flash-1017; capture returned model and system fingerprint because the alias is mutable.
- Thinking/CoT disabled: `thinking={"type":"disabled"}`, `reasoning_effort="none"`.
- JSON mode for structured content; native Tool Calls for Caller; validate locally.
- Temperature 0.0; max output 512; input cap 2,000.
- Direct network only; dedicated HTTPX client `trust_env=false`; no system proxy.
- Key from `DEEPSEEK_API_KEY`; never store in Git.
- Do not use GPT-4.1, GPT-6 Luna, deepseek-v4-pro, or retired DeepSeek model aliases.

## Conservative DeepSeek cost ceilings

Peak cache-miss rates: $0.30/M input, $1.20/M output; cache-hit peak $0.006/M; off-peak half. Budget on peak cache-miss:
- $0.0012144/request
- $0.072864/episode
- $4.663296/64-episode smoke; $9.326592 if every request retries once
- $27.979776/384-episode pilot; $55.959552 if every request retries once

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
