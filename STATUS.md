# Project Status

**Last updated:** 2026-11-23
**Overall state:** PRE-EXPERIMENT
**Current workstream:** Phase 0E.1 — smoke factory wiring, shared-budget enforcement, and protocol freeze
**Last verified handoff base before this status sync:** `81f89f38ef1adcb9dec5d081516572b3250bc5b1`
**Latest verified CI:** `45102805659` — success on that handoff base
**Phase 0E.1 current implementation SHA:** `bcc762e711815316dae17e4eef8bdbd4f2a815ee`
**Active branch:** `phase0b-adapter-statistical-corrections`
**Phase 0C implementation baseline SHA:** `f97467b8dcfb60a3d36cfd6638cd4e507509bc4a`
**Phase 0D final implementation SHA:** `b1c197eb5973575ae2ffa7c5c4cfe0d0fc9bf3a9`
**Latest Phase 0D GitHub Actions run:** `45046796585` — success
**Phase 0E User Simulator adapter code SHA:** `d7273064ad20f4452347ec0680c3ec1e14278f18`
**Phase 0E adapter code CI:** `45100451548` — success on adapter code SHA; user-reported final handoff CI: `45100563417` — success; latest docs-maintenance CI on current HEAD: `45102591927` — success
**PR #2:** https://github.com/yujian777555/NIL-CCEA/pull/2 (open, not merged)
**PR #1:** https://github.com/yujian777555/NIL-CCEA/pull/1 (open, not merged)
**Authoritative next prompt:** [docs/EXECUTOR_PROMPT_PHASE0E.md](docs/EXECUTOR_PROMPT_PHASE0E.md)

## User model decision

The user explicitly selected **DeepSeek Flash**:
- All four module slots and User Simulator use `deepseek-flash`.
- Current served version per official docs rechecked 2026-11-23: DeepSeek-V4.1-Flash-1017; alias is mutable, record response model and system fingerprint on every request.
- OpenAI-compatible Chat Completions at `https://api.deepseek.com`.
- Thinking/CoT disabled (`thinking.type=disabled`, `reasoning_effort=none`).
- JSON mode for structured content; native Tool Calls for Caller.
- Temperature 0.0; max output 512; declared input cap 2,000.
- Direct DeepSeek connection; dedicated HTTPX client `trust_env=false`; do not use system proxy.
- Credentials from `DEEPSEEK_API_KEY` only.
- GPT-4.1 and GPT-6 Luna are historical alternatives, not selected.

## Provider pricing (last rechecked 2026-11-23)

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
- Episode (120 logical requests): $0.145728; one retry for every request: $0.291456
- 64-episode smoke (7,680 normal / 15,360 maximum physical attempts): $9.326592 no-retry; $18.653184 with one retry for every request
- 384-episode pilot (46,080 normal / 92,160 maximum physical attempts): $55.959552 no-retry; $111.919104 with one retry for every request

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

1. Implement the five-client smoke factory: four distinct module clients plus one distinct User Simulator client.
2. Enforce one shared RequestBudget and one shared ModelFingerprintTracker by object identity across all five clients.
3. Add task-aware environment selection for Retail and Airline tasks in the same run.
4. Freeze an immutable pre-run manifest with Retail task 5's disclosed authentication limitation.
5. Re-run all no-API tests and CI, then obtain explicit user approval.

## Gate status

| Gate | State |
|---|---|
| G0 Literature | PASS |
| G1 Environment | PASS for pinned tau2 and reported no-key integration |
| G2 Public provider docs | PASS, rechecked 2026-11-23 |
| G2 User Simulator adapter | IMPLEMENTED, 39-test report includes coverage |
| G2 five distinct clients/shared budget/tracker | NOT YET WIRED / NOT ENFORCED |
| G2 mixed Retail/Airline environment factory | NOT YET WIRED |
| G2 Retail task 5 issue impact | DECIDED: RETAIN UNMODIFIED WITH DISCLOSURE |
| G3 No-API integration | PASS, 39 tests in host and pinned tau2 environments |
| G3 Real-runner readiness | PASS for no-API scope, 32 real tau2 Orchestrator cells |
| G4 Paid exploratory smoke | NOT AUTHORIZED / NOT STARTED |
| G5 Linkage-aware evolutionary search | NOT STARTED |

No real benchmark performance, statistical significance, algorithmic improvement, or novelty claim is asserted. Model selection is not paid-run approval.

## 2026-11-23 — Phase 0D code corrections completed locally

- Independent read-only review is recorded in [docs/PHASE0D_INDEPENDENT_REVIEW.md](docs/PHASE0D_INDEPENDENT_REVIEW.md). The review is separate from the implementation work and is not a GitHub PR review.
- DeepSeek client retries are bounded to one safe retry. Timeout, 5xx, and delivery-unknown network errors are recorded without automatic replay. Episode-level retries were removed.
- Every physical request attempt now records episode linkage, task and seed, configuration, module, attempt number, client request ID, prompt hash, requested model, returned model, system fingerprint, usage, actual cost, conservative cost upper bound, and delivery status. The tau2 runner writes `request_events.jsonl` and `cost_ledger.json` incrementally.
- Model identity is enforced on every parsed completion. Missing or changed identity quarantines the batch. Real ENV execution requires an explicit `RequestBudget`, four provider-backed module clients, and an inspectable DeepSeek Flash User Simulator.
- The client enforces the declared input cap with a conservative UTF-8 serialized-request bound and reserves the maximum physical attempts before each request. Cache hit and miss usage is retained separately.
- Host no-API suite passes 39 tests. Pinned Python 3.12.16 with tau2-bench v1.0.1 passes the same 39 tests, including the real tau2 Orchestrator 32-cell factorial check. DeepSeek API calls remain 0.
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
| G3 No-API integration | PASS, 47 host and 47 pinned tau2 tests |
| G3 Real-runner readiness | PASS for no-API scope only |
| External independent review | PENDING |
| G4 Paid exploratory smoke | NOT STARTED; no approval granted |
| G5 Linkage-aware evolutionary search | NOT STARTED |

Historical 60-request cost estimates ($4.663296 without retries; $9.326592 with one retry on every request) are superseded by the Phase 0E.1 source-level correction: 120 logical requests per episode, $9.326592 without retries and $18.653184 with one retry for every request. The $80 smoke hard cap is a stop limit, not spending authorization. No algorithmic improvement, statistical significance, or novelty claim is made.


## 2026-11-23 — Phase 0E preflight findings

- The reported Phase 0D final SHA is `b1c197eb5973575ae2ffa7c5c4cfe0d0fc9bf3a9`; GitHub PR #2 head matches. PR #2 remains open and unmerged.
- Final Phase 0D GitHub Actions run `45046796585` succeeded on that SHA.
- Official DeepSeek public documentation and pricing were rechecked 2026-11-23. Alias, published served version, endpoint, feature support, and prices are unchanged. Live account response model/fingerprint remain unverified.
- Retail task 5 and airline task 2 are both in the pinned tau2 v1.0.1 test split. Retail task 5 metadata also contains open issue `issue_770466c1`: retail user-level actions may be possible without authentication even though the domain policy requires authentication. Impact on this smoke must be assessed before freezing the manifest; do not silently substitute a task.
- Critical User Simulator integration finding: pinned tau2's stock `UserSimulator` calls tau2 `llm_utils.generate`, which calls LiteLLM `completion`. A model string `user.llm == deepseek-flash` does not prove use of NIL-CCEA's DeepSeekClient, shared RequestBudget, request ledger, fingerprint checks, or direct transport.
- Phase 0E therefore requires a provider-backed tau2 half-duplex UserSimulator adapter/subclass that routes all user-simulator requests through the controlled DeepSeekClient, shares the same RequestBudget, and persists user request events.
- Preflight review: [docs/PHASE0E_PREFLIGHT_REVIEW.md](docs/PHASE0E_PREFLIGHT_REVIEW.md).
- Authoritative next prompt: [docs/EXECUTOR_PROMPT_PHASE0E.md](docs/EXECUTOR_PROMPT_PHASE0E.md).
- No DeepSeek API request has been sent and no API key has been read. Paid smoke remains NOT AUTHORIZED / NOT STARTED.

## Phase 0E implementation update

- Added `src/nil_ccea/tau2_user_simulator.py`, a tau2-compatible half-duplex adapter backed by NIL-CCEA `DeepSeekClient`.
- Added four no-API tests covering LiteLLM bypass, plain-text generation, native user-tool validation, shared budget attachment, and episode-linked user request events.
- Host suite now passes 39 tests with tau2-dependent tests skipped. Pinned Python 3.12.16 + tau2-bench v1.0.1 passes all 39 tests.
- The adapter is ready for explicit smoke-factory wiring. Retail task 5 remains selected unchanged under the decision in docs/PHASE0E_PROTOCOL_DECISION.md; its authentication limitation must be disclosed in the pre-run manifest.


## 2026-11-23 — Phase 0E.1 takeover and protocol correction

- Verified PR #2 head and reported final code SHA: `d63bf1bd0062bb99b86ba61240caa4658835b5e7`. PR #2 remains open and unmerged. Code CI `45100451548` and final-documentation CI `45100563417` both succeeded on the reported code/final heads.
- User-reported no-API tests: host 39 passed with 12 tau2-dependent skips; pinned Python 3.12.16 + tau2-bench v1.0.1: 39 passed. DeepSeek requests and API-key reads remain 0.
- Provider-backed `DeepSeekTau2UserSimulator` is implemented. Remaining work is the actual paid-smoke factory, not the adapter itself.
- New source audit found that `build_deepseek_modules(client, configuration)` attaches one client object to all four module wrappers. Because the runner sets module context per slot, a single shared client can overwrite module attribution. The paid factory must use four distinct module clients plus a fifth distinct User Simulator client.
- New source audit found that `Tau2FactorialRunner` calls `environment_factory()` without a task. The 64-episode run mixes Retail and Airline; the runner/factory must select a fresh environment by `task.user_scenario.instructions.domain`.
- Strengthen fail-closed validation: all five clients must reference the exact same RequestBudget and ModelFingerprintTracker objects, while remaining distinct client objects.
- Corrected the provider request upper bound from 60 to 120 logical requests per episode: each Agent response invokes Planner + Selector + Caller/Synthesizer (3 calls), conservatively allowing 30 Agent responses plus 30 User Simulator responses. The 64-episode smoke is 7,680 normal logical requests / 15,360 maximum physical attempts, costing $9.326592 without retries / $18.653184 with one retry on every request.
- Proposed exploratory spend ceiling is $20.00, NOT AUTHORIZED. The separate $80 hard stop remains a stop limit, not spending authorization. Formal 384-episode pilot upper bound is $55.959552 without retries / $111.919104 with one retry per request.
- Retail task 5 decision: retain the user-selected task unmodified for this exploratory smoke, explicitly disclose open issue `issue_770466c1`, and make no authentication/privacy/policy-enforcement claim. Its ENV reward basis is DB + NL_ASSERTION, not ACTION; tool-level authentication is not enforced. See `docs/PHASE0E_PROTOCOL_DECISION.md`.
- Updated cost profile, Phase 0E preflight review, Phase 0B protocol freeze, and Pilot Design R1. Authoritative execution prompt: `docs/EXECUTOR_PROMPT_PHASE0E.md`.
- No smoke factory has been executed, no API key has been read, and no provider request has been sent. Paid smoke remains NOT AUTHORIZED / NOT STARTED.

## Phase 0E.1 implementation update

- Added five-client Smoke Factory with distinct Planner, Selector, Caller, Synthesizer, and User Simulator clients.
- All five clients share one `RequestBudget` and one `ModelFingerprintTracker`, while retaining separate request-event streams.
- Added mixed Retail/Airline environment selection, strict evaluated-run validation, guarded dry-run CLI, and immutable pre-run manifest generation.
- Host suite passes 47 tests with tau2-dependent tests skipped. Pinned Python 3.12.16 + tau2-bench v1.0.1 passes all 47 tests.
- Immutable manifest: `experiments/pilot_factorial/manifests/phase0e1_smoke_prerun_bcc762e7118153.json`.
- Manifest SHA-256: `66132bb3e7f83661b5acecfd95340da37162734287be72a2baca3384324ff0de`.
