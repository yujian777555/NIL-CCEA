# Executor Handoff — NIL-CCEA

**Repository:** https://github.com/yujian777555/NIL-CCEA  
**Branch:** `phase0b-adapter-statistical-corrections`  
**Base SHA for this handoff:** `8d6aeae3af39487c7d0fa390ec3d88b0f030b03d`  
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

Phase 0A and Phase 0B are reported complete. No real tau2 benchmark episode, paid API call, statistical significance, performance gain, or novelty claim exists.

## Remaining work

1. Fix Caller control flow; only invoke for `tool_call`.
2. Implement DeepSeek Flash-backed Planner/Selector/Caller/Synthesizer.
3. Implement real tau2 factorial runner for all 16 configurations.
4. Add fake-client no-key tests for direct transport, non-thinking JSON mode, tool calls, validation, token usage, and model fingerprint logging.
5. Recompute `delta=0.05` task-level power/sensitivity.
6. Update docs and CI; independent review.
7. Obtain explicit paid-smoke approval only after preflight is complete.

## Gates

- G0 Literature: PASS
- G1 Environment: PASS for tested scope
- G2 Contracts/protocol: NEEDS_REVISION
- G3 No-API integration: existing tau2 tests reported PASS; DeepSeek request-contract tests pending
- G3 Real-runner readiness: BLOCKED
- G4 Paid smoke: NOT STARTED
- G5 Search: NOT STARTED

The user has selected the model but has **not** authorized paid API calls. Keep this repository isolated from all other projects.
