# Project Status

**Last updated:** 2026-11-20  
**Overall state:** PRE-EXPERIMENT  
**Current workstream:** Phase 0C — DeepSeek Flash provider integration and real-runner readiness  
**Active branch:** `phase0b-adapter-statistical-corrections`  
**Base SHA for this handoff:** `8d6aeae3af39487c7d0fa390ec3d88b0f030b03d`  
**PR #2:** https://github.com/yujian777555/NIL-CCEA/pull/2 (open, not merged)  
**PR #1:** https://github.com/yujian777555/NIL-CCEA/pull/1 (open, not merged)  
**Authoritative next prompt:** [docs/EXECUTOR_PROMPT_PHASE0C.md](docs/EXECUTOR_PROMPT_PHASE0C.md)

## User model decision

The user explicitly selected **DeepSeek Flash**:
- All four module slots and User Simulator use `deepseek-flash`.
- Current served version per official docs on 2026-11-20: DeepSeek-V4.1-Flash-1017; alias is mutable, record response model and system fingerprint on every request.
- OpenAI-compatible Chat Completions at `https://api.deepseek.com`.
- Thinking/CoT disabled (`thinking.type=disabled`, `reasoning_effort=none`).
- JSON mode for structured content; native Tool Calls for Caller.
- Temperature 0.0; max output 512; declared input cap 2,000.
- Direct DeepSeek connection; dedicated HTTPX client `trust_env=false`; do not use system proxy.
- Credentials from `DEEPSEEK_API_KEY` only.
- GPT-4.1 and GPT-6 Luna are historical alternatives, not selected.

## Provider pricing (2026-11-20)

Official DeepSeek price page:
https://api-docs.deepseek.com/quick_start/pricing/

Conservative budget uses peak cache-miss rates:
- Input: $0.30 / 1M tokens.
- Output: $1.20 / 1M tokens.
- Cached input peak rate: $0.006 / 1M; not assumed in budget.
- Off-peak rates are half of peak.
- Peak UTC: weekdays 01:00–04:00 and 06:00–10:00, excluding Chinese public holidays.

At 2,000 input + 512 output tokens/request:
- Request: $0.0012144
- Episode (60 requests): $0.072864
- 64-episode smoke: $4.663296; all requests retried once: $9.326592
- 384-episode pilot: $27.979776; all requests retried once: $55.959552

Existing hard caps remain $80 exploratory and $400 pilot. Recheck prices immediately before paid execution.

## Phase 0A / 0B completed (reported)

- Literature and tau2-bench v1.0.1 source audit completed.
- Task-level estimator, nested seeds, full factorial validation, failure semantics, bootstrap, permutation p-values, and Holm correction implemented.
- tau2 v1.0.1 no-API integration tests reported 21 passed; 0 paid API calls.

## Remaining pre-smoke blockers

1. Fix Caller control flow: invoke only for Selector `tool_call`.
2. Implement provider-backed Planner, Selector, Caller, Synthesizer using DeepSeek Flash.
3. Implement real tau2 factorial runner for all 16 configurations.
4. Add no-key request-contract tests for DeepSeek model, JSON, non-thinking mode, direct connection, tool calls, parsing and validation.
5. Recompute task-level sensitivity/power for `practical_delta=0.05`.
6. Align stale docs and establish actual GitHub CI evidence.
7. Obtain independent review.

## Gate status

| Gate | State |
|---|---|
| G0 Literature | PASS |
| G1 Environment | PASS for pinned tau2 and reported no-key integration |
| G2 Contracts/protocol | NEEDS_REVISION |
| G3 No-API integration | PASS for previously tested scope; DeepSeek adapter tests pending |
| G3 Real-runner readiness | BLOCKED |
| G4 Paid exploratory smoke | NOT STARTED |
| G5 Search | NOT STARTED |

No real benchmark performance, statistical significance, algorithmic improvement, or novelty claim is asserted. Model selection is not paid-run approval.
