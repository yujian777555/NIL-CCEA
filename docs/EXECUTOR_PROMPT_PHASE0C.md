# NIL-CCEA Phase 0C — Real-runner readiness and provider lifecycle

Repository: https://github.com/yujian777555/NIL-CCEA  
Branch: `phase0b-adapter-statistical-corrections`  
Starting HEAD: `8d6aeae3af39487c7d0fa390ec3d88b0f030b03d`  
PR #2: https://github.com/yujian777555/NIL-CCEA/pull/2  
Review: `docs/PHASE0B1_PRICING_AND_SMOKE_READINESS_REVIEW.md`

## Mission

Complete the remaining pre-smoke engineering and protocol corrections so that NIL-CCEA can execute a controlled tau2-bench v1.0.1 exploratory factorial smoke. Do not repeat Phase 0A literature work or Phase 0B estimator/adapter tests except targeted regression tests.

**No paid API call is authorized by this prompt.** The user must explicitly approve the model choice and paid smoke before any real completion request is sent.

## 0. Protect the repository

1. Verify branch, HEAD, PR #2 head, working tree, and remote state before editing.
2. Preserve all existing changes and raw artifacts.
3. Do not force-push, reset hard, rewrite history, or merge PR #1 / PR #2.
4. Keep NIL-CCEA isolated from all other repositories.
5. Keep the exact tau2 commit `fc0055dc4e0a316c3f83133267fbd6faaa770992`.

## 1. User-selected provider and model — DeepSeek Flash

The user has explicitly selected **DeepSeek Flash**. This selection supersedes the earlier GPT-4.1 / GPT-6 Luna discussion.

Official references:
- Models & Pricing: https://api-docs.deepseek.com/quick_start/pricing/
- Chat Completions: https://api-docs.deepseek.com/api/create-chat-completion/
- First API Call: https://api-docs.deepseek.com/quick_start/

Fixed model configuration:
- Provider: DeepSeek.
- Requested model alias: `deepseek-flash` for Agent, User Simulator, Planner, Selector, Caller, and Synthesizer.
- Current served model as of 2026-11-20: DeepSeek-V4.1-Flash-1017. The API alias is mutable, so capture response `model` and `system_fingerprint` on every request.
- Base URL: `https://api.deepseek.com`; use OpenAI-compatible Chat Completions.
- Thinking/CoT MUST be disabled using `thinking={"type":"disabled"}` and `reasoning_effort="none"`.
- Structured JSON responses MUST use `response_format={"type":"json_object"}` and an explicit prompt instruction to return JSON. Caller should use native function Tool Calls; parse and validate arguments locally against the selected tau2 tool schema.
- Temperature: 0.0; max output: 512 tokens; declared input cap: 2,000 tokens.
- Direct connection only. Use a dedicated HTTPX client with `trust_env=False` (or equivalent) so DeepSeek bypasses system proxy environment variables. Do not change global proxy settings.
- Read `DEEPSEEK_API_KEY` from environment/secret storage only. Never commit, print, or log the key.
- Do not use `deepseek-v4-pro`, `deepseek-chat`, `deepseek-reasoner`, or legacy Flash aliases.

Pricing checked against the official DeepSeek page on 2026-11-20:
- Peak input cache miss: $0.30 / 1M tokens; peak cache hit: $0.006 / 1M; peak output: $1.20 / 1M.
- Off-peak prices are half the peak rates.
- Peak UTC schedule: weekdays 01:00–04:00 and 06:00–10:00, excluding Chinese public holidays.
- Use peak cache-miss rates for conservative budget ceilings: $0.0012144 per request, $0.072864 per episode, $4.663296 per 64-episode smoke, $9.326592 if every smoke request is retried once, $27.979776 per 384-episode pilot, and $55.959552 if every pilot request is retried once.
- Preserve the existing $80 smoke and $400 pilot hard caps unless a separately reviewed change is required.

Implementation requirements:
1. Update active model/cost config and all protocol/handoff docs to DeepSeek Flash.
2. Add an explicit DeepSeek client adapter using the OpenAI-compatible API. Ensure its HTTP client bypasses system proxies without modifying global proxy state.
3. Add no-key tests that inspect request construction: exact model alias, base URL, thinking disabled, reasoning_effort none, JSON mode, temperature, token cap, and direct-connection client configuration.
4. Add no-key tests for JSON parsing, function Tool Calls, malformed JSON, missing tool calls, invalid schema arguments, and empty JSON-mode content.
5. Log requested model alias, returned model, system fingerprint, request ID, prompt hash, decoding, token usage, retry and cost. If the returned model changes during a run, stop and quarantine the run; do not mix backend versions.
6. Keep the model the same for all four module slots and User Simulator.
7. Do not make any real API request during Phase 0C. Model selection is approved; paid smoke execution is not.

The earlier OpenAI pricing/deprecation comparison is historical only and is no longer an active model-choice question.
 
## 2. Fix adapter control flow

In `src/nil_ccea/tau2_adapter.py`, Caller is currently invoked before checking `selection.kind`.

Required:
- Invoke Caller only when `selection.kind == "tool_call"`.
- For `respond` and `stop`, do not invoke Caller.
- Record a clear not-applicable/skipped event if module event completeness requires it; do not count this as a model request.
- Preserve Selector/Caller tool-name equality and Pydantic parameter validation.
- Add tests where a Caller intentionally raises if invoked for respond or stop.
- Add tests that valid tool_call still invokes Caller exactly once.
- Keep typed fail-closed behavior for invalid actions and invalid tool arguments.

## 3. Implement the real provider-backed modules

The current code contains deterministic `mock_modules.py` only. Do not mistake these for real LLM module implementations.

Implement separate provider-backed module classes for:
- Planner
- Selector
- Caller
- Synthesizer

Requirements:
- Use one shared provider/client abstraction with explicit provider and model identifiers.
- Use the same model, temperature, token cap, and decoding settings for all four modules and all 16 configurations.
- Module-specific prompts and response schemas must be versioned and content-hashed.
- Parse outputs strictly; invalid JSON/schema must create typed module failure events.
- Caller must consume only the selected tool schema and validate arguments before returning.
- Do not allow a module variant to read evaluator-only state.
- Ensure only the selected binary module variant changes between factorial configurations.
- Make retries explicit, bounded, ledgered, and included in the total request cap.
- Keep the mock module implementations intact as deterministic test doubles.

No-key testing:
- Inject a fake client that raises immediately if any completion method is called unexpectedly.
- Verify prompt assembly, response parsing, schema failures, module hashes, and module selection without network access.
- Assert the total provider completion count remains exactly zero in the no-key suite.

## 4. Implement a real tau2 factorial runner

The current `MockRunner` only produces `mode="mock"`; the adapter alone is not a runnable paid experiment.

Add a separate tau2 runner using the pinned tau2 v1.0.1 classes. It must:
- Load only the frozen test split task IDs from `environment.lock.json`.
- Build all 16 module configurations.
- Create a fresh environment/task episode for each task × seed × configuration.
- Set task ID, task version/binding revision, family, language, trial, seed, module versions, model, decoding, and hashes in the manifest.
- Use identical tool permissions, domain policy, model settings, and endpoint across all 16 configurations.
- Execute the real Orchestrator and collect raw messages/tool calls, module events, terminal state, ENV reward, token usage, provider request IDs, failures, retries, and cost events.
- Enforce 30 max steps and the per-request token caps.
- Stop before the next episode if the hard budget cap would be exceeded.
- Preserve partial trajectories and infrastructure failure records.
- Never convert provider/infrastructure failures into task score zero.
- Keep exploratory smoke artifacts separate from any later confirmation dataset.

The planned exploratory smoke remains 2 tasks × 2 seeds × 16 configurations = 64 episodes. Explicitly mark it exploratory; 2 task clusters are not confirmatory evidence.

## 5. Resolve protocol inconsistencies

- The estimator default and Phase 0B report use practical delta 0.05.
- The current sensitivity table is labelled for delta 0.10.
- Keep 0.05 as the candidate unless the user changes it, but recompute the task-level sensitivity/power table for 0.05 using the actual task-cluster method and six-pair multiplicity adjustment.
- Clearly separate task-level cluster count from nested seeds.
- Mark `docs/EXPERIMENT_PROTOCOL_PILOT.md` as superseded or update its 32-episode smoke row to match the current 64-episode candidate. The authoritative scope is `docs/PHASE0B_PROTOCOL_FREEZE.md`.
- Update `src/nil_ccea/README.md`: tau2 adapter no-API integration tests have passed as reported, but provider-backed modules and the real tau2 runner remain pending until implemented.
- Do not change task IDs, primary endpoint, delta, model, or sample size after seeing confirmatory results.

## 6. Tests and CI

- Preserve host Python 3.10 mock tests.
- Preserve Python 3.12.16 / pinned tau2 no-key integration tests.
- Add the new caller-control-flow tests and provider module/runner fake-client tests.
- Add or repair GitHub Actions CI so PR #2 has reproducible test evidence; do not claim CI success until a real check run reports success.
- Record exact test commands and counts.
- Confirm API calls = 0 and cost = $0 for all no-key tests.

## 7. Paid-run gate

Do not call the provider during Phase 0C.

Before a paid smoke, deliver:
1. model choice and matching updated protocol/cost profile;
2. real provider module implementations;
3. real tau2 factorial runner;
4. no-key tests and CI green;
5. corrected practical-delta sensitivity analysis;
6. exact two exploratory task IDs;
7. hard-cap enforcement and cost ledger;
8. independent review.

Only after those are delivered, ask the user for explicit approval to run the 64-episode exploratory smoke. Silence or prior discussion of budget is not approval.

## 8. Repository maintenance and handoff

Update:
- `STATUS.md`
- `NEXT_STEPS.md`
- `docs/RESEARCH_LOG.md`
- `docs/HANDOFF.md`
- `docs/PHASE0B_PROTOCOL_FREEZE.md`
- `experiments/pilot_factorial/cost_profile.json`
- tests, source, and runner docs

Final report must include start/end SHA, branch/PR status, files changed, model and lifecycle decision, prices and sources, exact cost bounds, tau2 commit, Python versions, test results, API calls/cost, task/seed/config counts, endpoint/delta/multiplicity, Gate status, and the next executable action.

## Research rule

Do not stop the research because one model is deprecated or one integration test fails. Diagnose, implement a compatible route, test it offline, and continue. Do not fabricate benchmark evidence or claim improvement before real data exists.
