# Project Status

**Last updated:** 2026-11-23
**Overall state:** PRE-EXPERIMENT
**Current workstream:** Phase 0D — independent audit, provider preflight, and paid-smoke readiness
**Active branch:** `phase0b-adapter-statistical-corrections`
**Phase 0C implementation baseline SHA:** `f97467b8dcfb60a3d36cfd6638cd4e507509bc4a`
**Phase 0D current implementation SHA:** `7f07bbfd75927bb35a6cabd466799aded8c5fb57`
**Latest GitHub Actions run:** `45046604660` — success
**PR #2:** https://github.com/yujian777555/NIL-CCEA/pull/2 (open, not merged)
**PR #1:** https://github.com/yujian777555/NIL-CCEA/pull/1 (open, not merged)
**Authoritative next prompt:** [docs/EXECUTOR_PROMPT_PHASE0D.md](docs/EXECUTOR_PROMPT_PHASE0D.md)

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
- tau2 v1.0.1 no-API integration tests pass. Phase 0C expands the total no-API suite to 29 passing tests; paid API calls remain 0.

## Phase 0C implementation completed so far

- DeepSeek client is implemented with direct HTTPX transport, `trust_env=False`, JSON mode, native tool-call parsing, classified errors, bounded safe retries, request audit events, usage/cost accounting, and fingerprint drift detection.
- DeepSeek Planner, Selector, Caller, and Synthesizer wrappers are implemented with two binary manifest variants each.
- Real tau2 factorial runner is implemented and no-API tested over 32 task-seed-configuration cells with real tau2 Orchestrator classes.
- GitHub Actions workflow is added for the no-API host test suite.
- GitHub Actions Phase 0C tests pass on implementation head `f97467b8dcfb60a3d36cfd6638cd4e507509bc4a`, run `44914883210`.
- Self-review is recorded in `docs/PHASE0C_INDEPENDENT_REVIEW.md`; an external independent review remains pending.

## Remaining pre-smoke blockers

1. Review DeepSeek request contract against the current provider endpoint before any paid call.
2. Obtain independent review of the DeepSeek client and real runner.
3. Ask for explicit paid-smoke approval only after preflight gates pass.

## Gate status

| Gate | State |
|---|---|
| G0 Literature | PASS |
| G1 Environment | PASS for pinned tau2 and reported no-key integration |
| G2 Contracts/protocol | NEEDS_REVISION |
| G3 No-API integration | PASS | 29 tests pass with real tau2 classes and Fake Client |
| G3 Real-runner readiness | PASS for no-API scope | 32 real tau2 Orchestrator cells run with local modules |
| G4 Paid exploratory smoke | NOT STARTED |
| G5 Search | NOT STARTED |

No real benchmark performance, statistical significance, algorithmic improvement, or novelty claim is asserted. Model selection is not paid-run approval.

## 2026-11-23 — Phase 0D code corrections completed locally

- Independent read-only review is recorded in [docs/PHASE0D_INDEPENDENT_REVIEW.md](docs/PHASE0D_INDEPENDENT_REVIEW.md). The review is separate from the implementation work and is not a GitHub PR review.
- DeepSeek client retries are bounded to one safe retry. Timeout, 5xx, and delivery-unknown network errors are recorded without automatic replay. Episode-level retries were removed.
- Every physical request attempt now records episode linkage, task and seed, configuration, module, attempt number, client request ID, prompt hash, requested model, returned model, system fingerprint, usage, actual cost, conservative cost upper bound, and delivery status. The tau2 runner writes `request_events.jsonl` and `cost_ledger.json` incrementally.
- Model identity is enforced on every parsed completion. Missing or changed identity quarantines the batch. Real ENV execution requires an explicit `RequestBudget`, four provider-backed module clients, and an inspectable DeepSeek Flash User Simulator.
- The client enforces the declared input cap with a conservative UTF-8 serialized-request bound and reserves the maximum physical attempts before each request. Cache hit and miss usage is retained separately.
- Host no-API suite passes 34 tests. Pinned Python 3.12.16 with tau2-bench v1.0.1 passes the same 34 tests, including the real tau2 Orchestrator 32-cell factorial check. DeepSeek API calls remain 0.
- These results establish engineering readiness only. The 64-episode smoke remains exploratory and has no significance or performance claim.


## 2026-11-23 — Phase 0C closeout and Phase 0D handoff

- Phase 0C implementation baseline: `f97467b8dcfb60a3d36cfd6638cd4e507509bc4a`.
- GitHub Actions run `44914883210` completed successfully on the reported implementation head.
- PR #2 remains open and unmerged. GitHub currently reports no submitted reviews, no inline review threads, and no PR comments; external independent review is still pending.
- No DeepSeek API request or paid episode has been executed. The 29-test host/tau2 results and 32-cell Orchestrator run are no-API evidence only.
- Official DeepSeek public docs were rechecked on 2026-11-23. They list `deepseek-flash`, served version DeepSeek-V4.1-Flash-1017, the OpenAI-compatible endpoint, JSON/Tool Calls, disabled-thinking controls, and the same published price profile. This is public-document verification, not a live response-model/fingerprint check.
- A preliminary read-only source review identified items for independent confirmation and correction: retry count mismatch (client default 2 vs protocol 1), whole-episode replay after infrastructure failure, request audit events not durably linked to episodes, fingerprint tracker not enforced in the request path, missing request/cost budget enforcement, and loss of partial trajectory on exceptions.
- The 2-task exploratory smoke candidate is family-balanced and deterministic: retail task 5 and airline task 2, selected as the first listed test task in each locked family. Verify both against the pinned test split and record the selection rule before any paid request.
- Authoritative next prompt: [docs/EXECUTOR_PROMPT_PHASE0D.md](docs/EXECUTOR_PROMPT_PHASE0D.md).
- Phase 0D is no-API only. It must fix and independently review preflight gaps, then request explicit user approval before any live DeepSeek request.

### Updated gates

| Gate | State |
|---|---|
| G0 Literature | PASS |
| G1 Environment | PASS for pinned tau2 and reported no-API integration |
| G2 Public provider docs | PASS on 2026-11-23 |
| G2 Live returned model/fingerprint | NOT VERIFIED; requires first approved completion |
| G2 Runner/accounting/retry contract | PASS for no-API code path; live identity unverified |
| G3 No-API integration | PASS, 34 host and 34 pinned tau2 tests |
| G3 Real-runner readiness | PASS for no-API scope only |
| External independent review | PENDING |
| G4 Paid exploratory smoke | NOT STARTED; no approval granted |
| G5 Linkage-aware evolutionary search | NOT STARTED |

The $80 smoke hard cap is a stop limit, not spending authorization. Current conservative 64-episode estimates ($4.663296 without retries; $9.326592 with one retry on every request) are valid only if the 2,000-input/512-output token limits and one-retry-per-request rule are enforced. No algorithmic improvement, statistical significance, or novelty claim is made.
