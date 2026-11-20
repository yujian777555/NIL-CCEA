# Next Steps

**Current task:** execute [Phase 0C DeepSeek Flash integration and real-runner readiness](docs/EXECUTOR_PROMPT_PHASE0C.md).

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

## Required order

1. Recheck DeepSeek endpoint, model availability, and pricing.
2. Establish GitHub Actions CI result.
3. Obtain independent review of the client and runner.
4. Ask for explicit paid-smoke approval only after all preflight gates pass.

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
| G3 No-API integration | Existing tau2 tests PASS; DeepSeek request-contract tests pending |
| G3 Real-runner readiness | BLOCKED |
| G4 Paid exploratory smoke | NOT STARTED |
| G5 Search | NOT STARTED |
