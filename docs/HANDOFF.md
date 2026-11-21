# Executor Handoff — NIL-CCEA

**Repository:** https://github.com/yujian777555/NIL-CCEA
**Branch:** `phase0b-adapter-statistical-corrections`
**Base SHA for this handoff:** `33db2fdf2603d6ba37975f82b3b9a9b0a90217b9`
**PR #2:** https://github.com/yujian777555/NIL-CCEA/pull/2 (open)
**PR #1:** https://github.com/yujian777555/NIL-CCEA/pull/1 (open)
**Authoritative prompt:** [docs/EXECUTOR_PROMPT_PHASE0C.md](EXECUTOR_PROMPT_PHASE0C.md)

## User-selected model

**Use DeepSeek Flash exclusively** for all module slots, Agent, and User Simulator:
- API model alias: `deepseek-flash`
- Current served model as of 2026-11-20: DeepSeek-V4.1-Flash-1017; alias is mutable.
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
- Episode $0.072864
- Smoke 64 episodes $4.663296; full retry upper bound $9.326592
- Pilot 384 episodes $27.979776; full retry upper bound $55.959552

Hard caps: $80 smoke, $400 pilot. Recheck price before paid run.

## Research state

Phase 0A and Phase 0B are reported complete. Phase 0C client, modules, and no-API real tau2 runner are implemented. No real DeepSeek request, paid benchmark episode, statistical significance, performance gain, or novelty claim exists.

## Phase 0C completed implementation

- Direct DeepSeek client with no system proxy, JSON/native tool calls, audit events, usage/fingerprint checks, and safe bounded retries.
- Four DeepSeek module wrappers and binary manifest variants.
- Real tau2 factorial runner and 32-cell no-API Orchestrator test.
- 29 total tests pass in host and independent tau2 environments.
- GitHub Actions host workflow passes on final head `33db2fdf2603d6ba37975f82b3b9a9b0a90217b9`.
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
