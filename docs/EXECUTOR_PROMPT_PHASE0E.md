# NIL-CCEA Phase 0E — Final preflight and exploratory-smoke authorization

## Repository baseline

- Repository: https://github.com/yujian777555/NIL-CCEA
- Branch: `phase0b-adapter-statistical-corrections`
- Current reported remote/PR #2 head: `b1c197eb5973575ae2ffa7c5c4cfe0d0fc9bf3a9`
- PR #2: https://github.com/yujian777555/NIL-CCEA/pull/2 (open, unmerged)
- Phase 0D CI: run `45046796585`, success
- Pinned tau2-bench: v1.0.1, commit `fc0055dc4e0a316c3f83133267fbd6faaa770992`
- Phase 0D review: `docs/PHASE0D_INDEPENDENT_REVIEW.md`
- Phase 0E preflight findings: `docs/PHASE0E_PREFLIGHT_REVIEW.md`

## Mission

Complete the final preflight for the 64-episode DeepSeek Flash exploratory factorial smoke. Resolve the provider-backed User Simulator bypass and assess the known retail task 5 issue. Reproduce all no-API tests and CI, freeze the manifest and cost controls, then ask the user for explicit paid-run approval.

**HARD STOP: Until explicit approval is received, do not read `DEEPSEEK_API_KEY`, do not send any request to DeepSeek, and do not execute a paid benchmark episode.**

## Read first

1. `docs/PHASE0E_PREFLIGHT_REVIEW.md`
2. `docs/PHASE0D_INDEPENDENT_REVIEW.md`
3. `docs/EXECUTOR_PROMPT_PHASE0D.md`
4. `STATUS.md`
5. `NEXT_STEPS.md`
6. `experiments/pilot_factorial/cost_profile.json`
7. Pinned tau2 UserSimulator and LiteLLM source at the commit above.

## 1. Verify repository and preserve artifacts

- Verify branch, current HEAD, PR #2 head, remote sync, working tree, and latest CI.
- Keep NIL-CCEA isolated from all other repositories.
- Do not modify main, merge PR #1/#2, force-push, rewrite history, or overwrite any existing artifact.
- Preserve all existing `episodes.jsonl`, `request_events.jsonl`, `cost_ledger.json`, and `run_summary.json`.
- Correct stale SHA/run references in handoff docs and keep all docs synchronized.

## 2. P0 — Replace stock tau2 UserSimulator's LiteLLM path

Pinned tau2 `UserSimulator._generate_next_message` calls tau2's imported `llm_utils.generate`, which calls LiteLLM `completion()`. A stock UserSimulator with only `llm="deepseek-flash"` may pass the current string-level model check while bypassing NIL-CCEA's controlled DeepSeekClient, RequestBudget, request ledger, fingerprint checks, and direct no-proxy transport.

Implement a narrow provider-backed tau2 User Simulator adapter/subclass in NIL-CCEA:

- Preserve tau2's half-duplex UserSimulator interface and UserState semantics.
- Override the generation path so every user-simulator completion uses the NIL-CCEA DeepSeekClient.
- Expose `llm="deepseek-flash"` and an inspectable `client` attribute.
- Share the exact same RequestBudget object with the four module clients.
- Set per-episode request context: run_id, episode_id, task_id, seed, configuration_id, module=`user_simulator`.
- Drain and persist every physical user-simulator request event to the same episode-linked ledger.
- Preserve message history role flipping, optional user tool calls, tau2 Tool schemas, usage/cost, and raw response metadata.
- Use the same base URL, temperature 0, output cap 512, thinking disabled, retry policy, identity enforcement, and budget reservation.
- Do not call tau2's LiteLLM `generate` in the paid execution path.
- Do not modify pinned tau2 source or monkeypatch global LiteLLM state.
- Fail closed if the user simulator does not expose the controlled client or if its model/decoding/budget is inconsistent.

Add fake-client no-API tests:
1. stock tau2 LiteLLM generate is not invoked;
2. UserSimulator uses the injected DeepSeekClient;
3. user and agent requests share one RequestBudget;
4. user requests carry module attribution `user_simulator`;
5. tool-call and plain-text user responses preserve tau2 semantics;
6. model/fingerprint failure quarantines the run;
7. audit events and costs persist incrementally.

## 3. Assess retail task 5's known environment issue

Both proposed tasks are confirmed members of the pinned test split:
- retail task 5;
- airline task 2.

However, retail task 5 metadata contains open issue `issue_770466c1`: the retail environment may permit user-level actions without authentication, while the retail policy requires identity verification by email or name + zip before profile/order access.

Before freezing the pre-run manifest:
- inspect the exact task 5 action path and whether the issue can change ENV reward or permit a shortcut;
- document the issue and impact;
- do not silently change task IDs;
- if the issue invalidates the task, propose an explicit protocol amendment and ask the user before substituting a task or patching the environment.

Do not modify the pinned tau2 release in place. Any environment patch must be separately versioned, hashed, and reviewed.

## 4. Recheck public provider docs and pricing

Recheck on execution date:
- https://api-docs.deepseek.com/quick_start/pricing/
- https://api-docs.deepseek.com/api/create-chat-completion/
- https://api-docs.deepseek.com/guides/thinking_mode/
- https://api-docs.deepseek.com/guides/tool_calls/

At the 2026-11-23 check, the public docs list:
- alias `deepseek-flash`;
- served version `DeepSeek-V4.1-Flash-1017`;
- base URL `https://api.deepseek.com`;
- peak cache-miss input $0.30/M, peak cache-hit input $0.006/M, peak output $1.20/M;
- JSON Output, Tool Calls, and explicit disabled-thinking control.

Public documentation does not verify the model/fingerprint returned to this account. That check must occur on the first approved request, which must be counted inside the 64-episode budget, not as an unbudgeted extra request.

## 5. Frozen smoke candidate and costs

Unless a task-quality issue requires a user-approved protocol amendment, the candidate is:

- retail task 5 + airline task 2;
- test split;
- seeds 0 and 1;
- all 16 binary configurations of Planner, Selector, Caller, Synthesizer;
- 64 episodes;
- max 30 steps;
- primary endpoint: tau2 `EvaluationType.ENV` environment reward;
- all agent modules and User Simulator use `deepseek-flash`, temperature 0, thinking disabled, output cap 512, declared input cap 2,000.

Cost upper bounds at peak cache-miss prices:
- $0.0012144/request;
- 3,840 normal physical requests;
- 7,680 physical requests if every request is safely retried once;
- $4.663296 no-retry upper bound;
- $9.326592 all-requests-retried-once upper bound;
- $80 hard stop, not spending authorization.

These bounds are valid only if both agent and user requests share the same request/token/cost budgets and retry controls. Reserve the worst-case next physical attempt before sending. No episode-level replay. Never retry delivery-unknown requests, timeouts, or 5xx.

## 6. Pre-run manifest and approval package

After the UserSimulator fix, task issue assessment, tests and CI pass:

- Generate a new immutable pre-run manifest with current code SHA, protocol hash, task IDs, test split, seeds, all 16 configurations, tau2 commit, requested model alias, decoding, endpoint, budget profile, and task issue disclosure.
- Verify user simulator and four module clients expose the same model alias, endpoint, decoding and shared RequestBudget.
- Verify the first request's response identity will be checked before continuing; no model/fingerprint value may be hardcoded as observed.
- Ensure first identity check is the first request within the approved 64-episode run.
- Do not read the API key before approval.
- Present the user with exact task IDs, 64 episodes, 3,840 normal / 7,680 maximum physical requests, cost bounds, user-approved spend ceiling, $80 hard stop, model/endpoint, and stop/quarantine rules.
- Wait for explicit approval. Silence, prior model choice, or budget discussion is not approval.

## 7. Tests, CI and maintenance

Run:
- host no-API suite;
- pinned Python 3.12.16 + tau2 v1.0.1 suite;
- 32-cell real tau2 Orchestrator no-API factorial integration;
- all new UserSimulator fake-client tests;
- final GitHub Actions on the final pushed SHA.

Update:
- `STATUS.md`
- `NEXT_STEPS.md`
- `docs/HANDOFF.md`
- `docs/RESEARCH_LOG.md`
- `docs/PHASE0E_PREFLIGHT_REVIEW.md`
- `docs/EXECUTOR_PROMPT_PHASE0E.md`
- `experiments/pilot_factorial/cost_profile.json` (only if public price or assumptions change)

Report exact SHA, CI run, tests, task issue decision, UserSimulator implementation, API calls (must remain zero until approval), key reads (must remain zero until approval), and gates.

## Research interpretation

The 64-episode smoke has only two task clusters. It is strictly exploratory: verify provider/runner wiring, traces, cost, task execution, and descriptive 2^4 interaction feasibility. Do not claim statistical significance, reliable task-cluster variance, algorithmic improvement, or novelty.

After a valid smoke, the next research stage is a separately approved 12-task × 2-seed × 16-configuration study (384 episodes) to estimate task-level interaction variance. Only then proceed to Linkage Learning and Linkage-aware Cooperative Co-evolution under equal evaluation budgets.

Do not implement the full evolutionary optimizer before trustworthy interaction measurements exist. Do not stop the research because one task or integration needs revision; diagnose and continue without fabricating evidence.

## 2026-11-23 implementation update

The provider-backed tau2 User Simulator adapter is implemented at `src/nil_ccea/tau2_user_simulator.py`. Four pinned fake-client tests plus one runner integration test pass and demonstrate that stock tau2 LiteLLM generation is bypassed, native user-tool calls are locally validated, shared budgets can be attached, user request events carry episode/module attribution, and the environment-aware factory receives the shared budget and context. The remaining gate is explicit smoke-factory wiring with one shared `RequestBudget` for all module and user clients. Retail task 5 remains in the frozen candidate with `issue_770466c1` disclosed as a material authentication-enforcement risk requiring a protocol decision before manifest freeze.
