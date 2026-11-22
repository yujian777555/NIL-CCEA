# NIL-CCEA Phase 0D — Independent Audit, Provider Preflight, and Paid-Smoke Readiness

Repository: https://github.com/yujian777555/NIL-CCEA
Active branch: phase0b-adapter-statistical-corrections
Phase 0C implementation SHA: f97467b8dcfb60a3d36cfd6638cd4e507509bc4a
PR #2: https://github.com/yujian777555/NIL-CCEA/pull/2
Pinned benchmark: tau2-bench v1.0.1, commit fc0055dc4e0a316c3f83133267fbd6faaa770992

## Mission

Phase 0C implementation is complete for the reported no-API scope. Your job is to independently audit the actual code, close the remaining preflight gaps, verify the current public DeepSeek contract and price, and prepare the 64-episode exploratory smoke for an explicit user approval decision.

Do not merely write another plan. Inspect the repository, reproduce the tests, fix concrete defects, and produce a reviewable handoff.

**Hard stop: no DeepSeek endpoint request, no completion request, no API key read, and no paid call during Phase 0D.** Public documentation checks are allowed. The 64-episode smoke is not authorized by this prompt. After all gates pass, present a precise approval request and wait.

## 1. Repository safety and branch discipline

1. Verify repository, branch, local/remote HEAD, PR #2 head/base, clean working tree, and CI before editing.
2. Work only in NIL-CCEA.
3. Keep the active branch phase0b-adapter-statistical-corrections unless a separate branch is necessary and documented.
4. Do not modify main.
5. Do not merge PR #1 or PR #2.
6. Do not force-push, reset hard, rewrite history, or discard artifacts.
7. Preserve all Phase 0A/0B/0C evidence and historical records.
8. After each meaningful change, run targeted tests; after the final change, run the full no-API suite and CI.
9. Keep the repository's status, next steps, research log, handoff, and executor prompt synchronized.

## 2. Current verified state

Phase 0C implementation SHA: f97467b8dcfb60a3d36cfd6638cd4e507509bc4a.
Reported no-API tests: 29 passed in host and independent Python 3.12.16/tau2 v1.0.1 environments.
Reported real tau2 Orchestrator no-API integration: 32 task-seed-configuration cells.
DeepSeek API calls: 0.
Paid smoke: NOT STARTED.
GitHub Actions run 44914883210: success on the reported final implementation head.
PR #2 is open and unmerged. At handoff, GitHub showed no submitted reviews, no inline review threads, and no PR comments. Do not describe the self-review as an external independent review.

Reproduce these claims from GitHub and the actual checkout. If the current head or CI run differs, report the actual values.

## 3. DeepSeek Flash public contract verification

The user-selected provider/model is fixed. Do not ask the user to choose another model and do not substitute another provider.

Current official public documentation checked on 2026-11-23:

- Model alias: deepseek-flash.
- Publicly documented served version: DeepSeek-V4.1-Flash-1017.
- OpenAI-compatible base URL: https://api.deepseek.com
- Chat Completions endpoint: /chat/completions
- JSON Output and function Tool Calls are supported.
- Thinking can be disabled with thinking={type: disabled}; this explicit setting takes precedence over reasoning_effort.
- Peak cache-miss input: $0.30 / 1M tokens.
- Peak cache-hit input: $0.006 / 1M tokens.
- Peak output: $1.20 / 1M tokens.
- Off-peak prices are half of peak prices.

Official sources:
- https://api-docs.deepseek.com/quick_start/pricing/
- https://api-docs.deepseek.com/api/create-chat-completion/
- https://api-docs.deepseek.com/guides/thinking_mode/
- https://api-docs.deepseek.com/en/

Recheck these pages at execution time and record access date, exact values, and source URLs. Public docs verify the alias and published service version; they do NOT verify the model/fingerprint returned to this account. The returned model and system_fingerprint can only be verified by a real completion response. Do not claim live response verification in Phase 0D.

The first live completion, if later approved, must verify:
- returned model equals the expected documented service version;
- system_fingerprint is present and stable;
- request ID and token usage are present;
- the actual decoding contract matches the frozen configuration.

If any of these checks fail, stop after the first affected request, quarantine the run, and do not mix it with later data.

## 4. Required independent review

Obtain an actual independent review from a different reviewer/agent who did not implement Phase 0C. If no independent reviewer is available, record the limitation and keep the external-review gate open. Do not relabel self-review as independent review.

Review at least these concrete areas against the current source:

1. Retry mismatch: DeepSeekClient currently defaults to max_retries=2 while cost_profile.json declares one infrastructure retry per request.
2. Episode replay: Tau2FactorialRunner retries the entire episode after infra_failed. This can repeat already completed and billed requests. Remove whole-episode replay; retries must be scoped to an individual request and only used when delivery is known to be safe.
3. Ambiguous transport errors: do not automatically retry errors that may occur after the request was delivered. Timeouts and uncertain post-send failures must be recorded as delivery-unknown and must not be replayed automatically.
4. Request audit persistence: DeepSeekClient.audit_events currently accumulates in memory. Verify that every request event is attached to the correct episode and durably written to raw artifacts.
5. Token and cost accounting: parse prompt_cache_hit_tokens and prompt_cache_miss_tokens when returned. Preserve actual usage and calculate provider-billed cost from the correct cache-hit/miss rates. Also retain a conservative peak cache-miss upper-bound cost.
6. Fingerprint enforcement: ModelFingerprintTracker must be used by the execution path. Check both response.model and system_fingerprint. Missing identity fields must not silently pass. Stop and quarantine on drift.
7. Manifest accuracy: do not hardcode the served model version as if it were observed. Record requested alias separately from the actual response model and fingerprint.
8. Budget enforcement: enforce request counts, token limits, per-episode caps, smoke cap, and pre-request budget reservation before every outbound completion.
9. Partial trajectory preservation: exceptions must not discard messages/tool calls already produced. Persist incremental events or a durable partial trajectory before continuing/retrying.
10. Input token cap: the declared 2,000-token input limit must be enforced by a tokenizer-compatible counter or a conservative fail-closed input bound. If exact enforcement is unavailable, revise the claim and recalculate the cost upper bound before approval.
11. Runner outcome semantics: missing ENV reward must not be marked as success. Distinguish agent task failure from infrastructure failure and retain the actual primary endpoint.
12. Model consistency: verify that Planner, Selector, Caller, Synthesizer, Agent and User Simulator all use the same DeepSeek Flash alias and identical provider-level decoding settings.
13. Caller native Tool Calls must still be locally validated against the selected tau2 schema; provider-side strict mode is not a substitute for local validation.
14. Check that raw responses, logs and exception messages cannot expose API keys or other credentials.

The review must identify severity, exact file/line, reproduction, required correction, and test coverage. Record the independent review in a new review artifact.

## 5. Required implementation corrections

Fix all confirmed preflight blockers before asking for paid approval.

Minimum acceptance:

- Align client retry configuration with the frozen one-retry-per-request policy.
- Remove whole-episode automatic retries.
- Only retry failures that are demonstrably safe to retry; never replay timeouts or delivery-unknown requests.
- Add an append-only per-request ledger and link every request to run_id, episode_id, task_id, seed, configuration_id, module, attempt, request_id, prompt_hash, requested model, returned model, fingerprint, status, token usage and cost.
- Persist partial trajectories and failure records incrementally.
- Wire model identity validation into every completion response.
- Enforce request and cost budgets before sending the next request.
- Enforce or correctly revise the 2,000 input-token assumption.
- Parse cache-hit/cache-miss usage details and preserve both billed-cost estimate and conservative upper-bound cost.
- Fail closed on missing ENV reward or invalid response identity.
- Ensure a model/fingerprint change quarantines the entire batch.
- Ensure the User Simulator is also provider-backed by the same selected model, not a hidden mock or alternate model.

Do not make unrelated architectural changes. Preserve the four module contracts and the 2^4 factorial design.

## 6. Freeze the exploratory smoke design

The exploratory smoke is exactly:

2 tasks × 2 seeds × 16 configurations = 64 episodes.

Seeds: 0 and 1.
Configurations: all 16 combinations of the four binary module variants.
Task split: tau2 test.
Primary endpoint: EvaluationType.ENV environment_reward.
Maximum steps: 30.
All four module variants, Agent and User Simulator use the same DeepSeek Flash model alias and frozen decoding configuration.

The current locked test-task lists are:
- retail: [5, 9, 12, 17, 18, 26]
- airline: [2, 6, 8, 13, 16, 18]

For the exploratory smoke, use a deterministic family-balanced selection rule: the first listed task from each family, namely retail task 5 and airline task 2. Verify both IDs exist in the pinned test split and record the selection rule and IDs in the pre-run manifest before any paid request. Do not select tasks based on observed model performance.

The smoke is exploratory and has only two independent task clusters. It must not be used to claim confirmatory significance, estimate a reliable task-cluster variance, or establish algorithmic improvement.

## 7. Cost and stop rules

The existing conservative price calculation assumes 2,000 input tokens and 512 output tokens per request:

- Maximum normal requests: 64 episodes × 60 requests = 3,840.
- Maximum with one retry per request: 7,680.
- Per-request upper bound at peak cache-miss pricing: $0.0012144.
- 64-episode upper bound without retries: $4.663296.
- Upper bound if every request is retried once: $9.326592.
- Existing smoke hard cap: $80.
- Existing formal pilot hard cap: $400.

Important:
- The $80 hard cap is a stop limit, NOT permission to spend $80.
- The $9.326592 estimate is valid only if the 2,000/512 token caps and one-retry-per-request rule are actually enforced.
- If the enforced token cap or retry semantics change, recompute all upper bounds before asking for approval.
- Count failed requests and retries.
- Reserve the worst-case next-request cost before sending it.
- Never start an episode if the remaining hard-cap allowance cannot cover its reserved maximum.
- Stop before the next request when the user-approved spend ceiling or the repository hard cap would be exceeded.
- Do not top up, increase caps, or continue beyond the approved amount.

No live request is allowed in Phase 0D. After all fixes and independent review pass, present a separate approval request stating:
- exact task IDs, seeds, configurations and episode count;
- maximum request count;
- expected upper-bound cost and retry upper bound;
- hard cap and the fact it is not spending authorization;
- model/provider and endpoint;
- stop/quarantine rules;
- confirmation that no model training or fine-tuning is included.

Then wait for the user's explicit approval. Silence, model selection, or prior discussion of budget is not approval.

## 8. Statistics and interpretation

- Keep the independent statistical unit as task; seeds are nested repeated measurements.
- The 2-task smoke is for API, runner, schema, trajectory, cost and basic interaction-feasibility diagnostics only.
- Do not estimate formal power from two task clusters.
- After the smoke, review descriptive pairwise interaction estimates and data quality; do not claim statistical significance.
- The next 12-task stage is 12 task clusters × 2 seeds × 16 configurations = 384 episodes, subject to a separate protocol/cost/approval gate.
- Use the 12 task-level contrasts from that stage to estimate task-cluster variance and recalculate power for any subsequent confirmatory study. Do not count 24 task-seed observations as 24 independent clusters.
- Keep practical delta at 0.05 unless a separately documented pre-run review justifies a change. Correct six pairwise module-interaction tests using the frozen Holm procedure.
- Do not change endpoint, task IDs, delta, model or analysis after observing outcomes.

## 9. Research direction after smoke

Do not implement the full optimizer before the interaction measurements are trustworthy.

The algorithmic main line remains evolutionary computation:
1. Estimate signed module interactions and their uncertainty from paired factorial contrasts.
2. Build an uncertainty-aware Linkage Graph.
3. Study task-conditional and dynamic linkage updates only when supported by data.
4. Design linkage-guided cooperative co-evolution operators: independent mutation, joint mutation, linkage-aware crossover and adaptive grouping.
5. Compare against independent evolution and fixed-group/conventional cooperative co-evolution under equal total evaluation budgets.
6. Charge all interaction probes, failed calls, diagnostics and retries to each method's budget.

A null interaction is a diagnosis trigger, not an automatic project stop. Investigate manipulation validity, task-family dependence, noise, task coverage, higher-order interactions and statistical power. Do not manufacture positive effects.

No base-model training or fine-tuning in this milestone.

## 10. Tests and final handoff

Add no-API tests for every corrected behavior. The suite must run without API key or network access. Include:
- retry attempt accounting and delivery-unknown handling;
- no whole-episode replay;
- request ledger persistence and episode linkage;
- cache-hit/miss cost accounting;
- missing/changed model and fingerprint rejection;
- input/request/episode/smoke budget guard;
- partial trajectory persistence;
- missing ENV reward handling;
- User Simulator model consistency;
- all 16 configurations and task/seed pairing.

Run host tests and pinned Python 3.12/tau2 tests, then verify GitHub Actions on the final head. Record exact commands, counts, CI run ID and SHA.

Update:
- STATUS.md
- NEXT_STEPS.md
- docs/HANDOFF.md
- docs/RESEARCH_LOG.md
- docs/EXECUTOR_PROMPT_PHASE0D.md
- a separate Phase 0D independent-review artifact
- cost profile and protocol only if values or enforcement assumptions change

Final report must separate:
- verified public provider documentation;
- actual provider identity (still unverified until an approved live response);
- no-API test evidence;
- independent review evidence;
- paid API status and cost;
- Gate decisions;
- exact next action.

Do not merge PRs. Do not claim algorithmic improvement. Do not send a paid API request.
