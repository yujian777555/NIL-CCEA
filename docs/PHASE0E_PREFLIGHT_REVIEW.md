# Phase 0E Preflight Review — 2026-11-23

## 1. Repository and CI verification

- Repository: https://github.com/yujian777555/NIL-CCEA
- Branch: `phase0b-adapter-statistical-corrections`
- Phase 0D final code SHA: `b1c197eb5973575ae2ffa7c5c4cfe0d0fc9bf3a9`
- Phase 0E User Simulator code SHA: `d7273064ad20f4452347ec0680c3ec1e14278f18`
- User-reported final Phase 0E handoff SHA: `d63bf1bd0062bb99b86ba61240caa4658835b5e7` (current documentation head is tracked in STATUS.md)
- PR #2 state: open, unmerged
- Final Phase 0D workflow: run `45046796585`, conclusion `success`, on the reported final SHA
- User-reported working tree: clean and pushed
- No DeepSeek API request has been made; no API key has been read.
- Phase 0D no-API evidence: 39 host tests passed (12 tau2-dependent tests skipped on host), 39 passed under Python 3.12.16 + tau2 v1.0.1, and 32 real tau2 Orchestrator factorial cells passed.

## 2. Official DeepSeek documentation rechecked

Checked 2026-11-23:

- Model alias: `deepseek-flash`
- Publicly listed served version: `DeepSeek-V4.1-Flash-1017`
- OpenAI-compatible base URL: `https://api.deepseek.com`
- Endpoint: `/chat/completions`
- JSON Output and function Tool Calls are supported.
- Non-thinking mode is selected with `thinking: {type: disabled}`; the explicit thinking object takes precedence over `reasoning_effort`.
- Peak cache-miss input: $0.30 / 1M tokens.
- Peak cache-hit input: $0.006 / 1M tokens.
- Peak output: $1.20 / 1M tokens.
- Off-peak rates are half the peak rates.

Official sources:
- https://api-docs.deepseek.com/quick_start/pricing/
- https://api-docs.deepseek.com/api/create-chat-completion/
- https://api-docs.deepseek.com/guides/thinking_mode/
- https://api-docs.deepseek.com/guides/tool_calls/

The published prices and model alias are unchanged from the cost profile. This is public-document verification only; the actual account response model and system fingerprint remain unverified until the first explicitly approved completion request.

## 3. Historical P0 finding — stock tau2 UserSimulator bypass (resolved by Phase 0E adapter)

Pinned source: tau2-bench v1.0.1, commit `fc0055dc4e0a316c3f83133267fbd6faaa770992`.

Relevant upstream files:
- https://github.com/sierra-research/tau2-bench/blob/fc0055dc4e0a316c3f83133267fbd6faaa770992/src/tau2/user/user_simulator.py
- https://github.com/sierra-research/tau2-bench/blob/fc0055dc4e0a316c3f83133267fbd6faaa770992/src/tau2/utils/llm_utils.py

Observed source behavior:

1. tau2 `UserSimulator.__init__` accepts an `llm: str` and `llm_args`.
2. `UserSimulator._generate_next_message` calls the module-level tau2 `generate(...)`.
3. tau2 `llm_utils.generate` calls LiteLLM's `completion(...)`, with tau2's own retry default and a separately configured LiteLLM HTTP session.
4. NIL-CCEA's current runner can accept `user.llm == "deepseek-flash"` as model metadata. However, budget binding and request-event draining only attach to an exposed `client`, `llm_client`, or `deepseek_client`.
5. Therefore a stock tau2 `UserSimulator(llm="deepseek-flash")` may pass the string-level model check while its actual calls bypass the NIL-CCEA `DeepSeekClient`, shared `RequestBudget`, per-request ledger, fingerprint enforcement, and `trust_env=False` transport.

This was a paid-run blocker before the Phase 0E adapter. The provider-backed adapter is now implemented and tested; the remaining paid-run blocker is actual smoke-factory wiring and fail-closed validation of all five clients.

### Required correction

Implement a provider-backed tau2 User Simulator adapter/subclass that remains compatible with tau2's half-duplex user interface but routes every generation through the NIL-CCEA `DeepSeekClient`.

Acceptance requirements:

- Expose `llm = "deepseek-flash"` and an inspectable `client` attribute.
- Use the same shared `RequestBudget` object as the four agent module clients.
- Set episode/task/seed/configuration/module context on the user-simulator client.
- Persist its physical request events into the same episode-linked request ledger.
- Preserve tau2 UserState, message-role flipping, optional user tool calls, tool schemas, returned usage/cost, and raw response metadata.
- Use the same base URL, temperature, output cap, thinking-disabled setting, retry semantics, response-model/fingerprint checks, and budget reservation as the agent modules.
- Do not call tau2's imported LiteLLM `generate` function in the paid execution path.
- Fail closed if the user simulator is not backed by the controlled client.
- Add fake-client tests proving that the stock LiteLLM path is never invoked, user requests share the budget, and request events are attributed to `user_simulator`.
- Re-run host tests, pinned tau2 tests, all 32 no-API Orchestrator cells, and GitHub Actions.

Do not modify the pinned tau2 source or silently monkeypatch global LiteLLM state. Prefer a narrow subclass/adapter in NIL-CCEA.

## 4. Task ID verification and task-quality warning

Both candidate IDs are in the pinned v1.0.1 test split:

- Retail task `5`: present in `data/tau2/domains/retail/split_tasks.json` test list.
- Airline task `2`: present in `data/tau2/domains/airline/split_tasks.json` test list.

Pinned split file blob SHAs:
- Retail split: `8b20704a17aa1940b1e58668f89dcef2ddaeeea3`
- Airline split: `c83cce155671e66a6bf07450fd2845fe0eb1f229`

However, retail task 5's task metadata contains an open issue `issue_770466c1` with status `open`:

> Domain level issue. Agent is allowed to do user level actions e.g. look-up their order info, without authenticating the user. The tool should throw an error if user has not been authenticated yet.

The retail domain policy requires identity authentication by email or name + zip before accessing profile/order data, even if the user provides an ID. The task's known issue says the environment tools may not enforce this invariant.

This does not automatically invalidate task 5, but it is a material task-quality risk for a two-cluster exploratory smoke. Before final pre-run freeze:

- inspect whether this issue affects task 5's actual tool path and ENV reward;
- record the issue and its impact in the manifest;
- do not silently substitute another task;
- if task 5 must be replaced or the environment must be patched, propose a protocol amendment and obtain user approval before changing the frozen task set.

The smoke remains diagnostic only and cannot support confirmatory statistical or algorithm-performance claims.

## 5. Current cost profile

Official prices rechecked 2026-11-23 and unchanged:

- Per request upper bound: $0.0012144, assuming 2,000 input and 512 output tokens at peak cache-miss prices.
- Each Agent response invokes Planner + Selector + exactly one of Caller/Synthesizer: up to 3 module requests.
- Conservatively allow up to 30 Agent responses and 30 User Simulator responses per episode: 90 + 30 = 120 logical requests.
- With one retry reserved for every logical request: 240 physical attempts per episode.
- 64 episodes: 7,680 normal logical requests / 15,360 maximum physical attempts.
- No-retry upper bound: $9.326592.
- Every request retried once: $18.653184.
- Proposed spend ceiling: $20.00, NOT AUTHORIZED.
- Exploratory hard stop: $80; this is not authorization to spend $80.

The previous 60-request-per-episode estimates ($4.663296 / $9.326592) undercounted the four-module call graph and are superseded. The corrected figures are conservative source-level bounds and must be enforced through one shared RequestBudget across five distinct clients.

## 6. Gate decision

| Gate | State |
|---|---|
| Phase 0D code fixes | PASS per reported tests |
| Phase 0D independent code review | PASS; separate GitHub PR review remains absent |
| Final Phase 0D GitHub Actions | PASS, run 45046796585 |
| DeepSeek public docs and pricing | PASS, checked 2026-11-23 |
| Retail 5 / Airline 2 test-split membership | PASS |
| Retail task 5 known issue impact | DECIDED: RETAIN UNMODIFIED WITH DISCLOSURE |
| Provider-backed User Simulator | IMPLEMENTED; smoke-factory wiring pending |
| Five distinct clients / shared budget and identity tracker | NEEDS IMPLEMENTATION + FAIL-CLOSED VALIDATION |
| Mixed Retail/Airline environment selection | NEEDS IMPLEMENTATION |
| Actual returned model/fingerprint | NOT VERIFIED; requires first approved live request |
| Paid 64-episode smoke | NOT AUTHORIZED / NOT STARTED |
| Linkage-aware evolutionary search | NOT STARTED |

## 7. Next executable action

Implement the five-client smoke factory, shared RequestBudget and identity tracker, task-aware Retail/Airline environment selection, fail-closed runner checks, and immutable pre-run manifest. Retain Retail task 5 unmodified with the limitation in docs/PHASE0E_PROTOCOL_DECISION.md. Re-run all no-API tests and CI, then present the corrected 64-episode approval request.

No DeepSeek request, API-key read, paid episode, significance test, algorithmic performance claim, or novelty claim is authorized by this review.

## 8. No-API implementation update

The provider-backed adapter is implemented in `src/nil_ccea/tau2_user_simulator.py`.

Current implementation commit: `d7273064ad20f4452347ec0680c3ec1e14278f18`. Final CI run on this commit: `45100451548`, success.

- `DeepSeekTau2UserSimulator` preserves tau2 half-duplex `UserState` and message-role flipping.
- Every completion routes through the injected NIL-CCEA `DeepSeekClient`.
- Native user tool calls use tau2 `Tool.openai_schema` and are validated through `Tool.params` before becoming `UserMessage` tool calls.
- The adapter exposes `llm="deepseek-flash"` and `client`, so the runner can bind the shared `RequestBudget`, episode context, and request ledger.
- The runner's existing user-client binding and event draining attach `module=user_simulator` to the same episode ledger.
- Four pinned tau2 fake-client tests pass. They prove the stock LiteLLM generation function is not invoked, plain text and native tool calls preserve tau2 semantics, a shared budget can be attached, and a real client event is linked to `user_simulator` and an episode. A fifth pinned integration test proves `Tau2FactorialRunner.user_factory_with_environment` receives the episode environment and binds the shared budget and user context.

The adapter is an implementation and no-API verification milestone. The paid smoke factory still needs to construct this adapter explicitly through `Tau2FactorialRunner.user_factory_with_environment`, use a distinct user client and four distinct module clients, and pass the same RequestBudget and ModelFingerprintTracker objects to all five clients.

## 9. Retail task 5 impact assessment

The pinned task 5 evaluation path requires `find_user_id_by_name_zip`, `get_user_details`, `get_order_details`, `get_product_details`, and `return_delivered_order_items`. The pinned retail tool implementations expose the user and order lookups without a stored authentication-state check. This matches the open `issue_770466c1` metadata and makes the issue relevant to the selected task's environment semantics.

The task remains in the frozen candidate because the user explicitly selected retail 5 and the task is present in the pinned test split. Protocol decision: retain the task unmodified for this exploratory smoke, disclose that authentication is not enforced at the tool layer, and make no authentication/privacy/safety claim. The task's reward_basis is DB + NL_ASSERTION, not ACTION, so ENV reward does not guarantee authentication-sequence compliance. See docs/PHASE0E_PROTOCOL_DECISION.md.

## 10. Updated gate decision

| Gate | State |
|---|---|
| Provider-backed User Simulator code | IMPLEMENTED |
| User Simulator no-API tests | PASS, 4 pinned tests |
| Paid smoke factory wiring | NOT YET IMPLEMENTED |
| Retail task 5 authentication issue | DECIDED: RETAIN UNMODIFIED WITH EXPLICIT LIMITATION |
| Paid 64-episode smoke | NOT AUTHORIZED / NOT STARTED |


## 11. Phase 0E.1 source-level runner and budget audit — 2026-11-23

The adapter implementation is complete, but the paid smoke factory is not yet ready. The current runner and module factory reveal three integration requirements:

1. **Mixed-domain environment selection:** `Tau2FactorialRunner._run_episode_once` currently calls `environment_factory()` without the task. The 64-episode candidate mixes Retail task 5 and Airline task 2, so the smoke factory must provide task-aware environment selection using `task.user_scenario.instructions.domain`. Each episode must receive a fresh domain-specific environment.
2. **Distinct module clients:** `build_deepseek_modules(client, configuration)` currently attaches one client object to all four module wrappers. The runner sets the client episode context once per slot, so a shared client would have its module attribution overwritten by the last slot. The paid factory must create four distinct module clients plus a fifth distinct User Simulator client.
3. **Fail-closed budget/identity checks:** the runner currently assigns the shared budget when a client exposes a budget attribute, but it does not require all five clients to reference the exact same RequestBudget object or ModelFingerprintTracker. Strengthen validation so a stock UserSimulator, missing client, separate budget, missing tracker, or shared module client is rejected for `evaluate=True`.

### Corrected call-count derivation

The pinned NIL-CCEA agent adapter calls Planner and Selector on every Agent response, then calls exactly one of Caller or Synthesizer. Thus each Agent response can produce three model requests. With max_steps=30, a conservative upper bound is 30 Agent responses and 30 User Simulator responses per episode:

- 90 Agent-module requests + 30 User Simulator requests = 120 logical requests per episode.
- One retry per logical request reserves 240 physical attempts per episode.
- 64 episodes: 7,680 normal logical requests; 15,360 maximum physical attempts.
- At $0.0012144 per request: $9.326592 no-retry upper bound; $18.653184 if every request is retried once.
- Proposed authorization ceiling: $20.00, NOT GRANTED. Separate $80 hard stop remains a stop limit only.

The earlier 60-request-per-episode figures are superseded. Updated machine-readable values are in `experiments/pilot_factorial/cost_profile.json`.

## 12. Retail task 5 protocol decision

The user-selected Retail task 5 remains in the smoke unchanged. Pinned RetailTools does not enforce authenticated-user state for `get_user_details` or `get_order_details`; the policy nevertheless requires authentication. Since task 5 reward_basis is DB + NL_ASSERTION and not ACTION, ENV reward does not independently guarantee authentication-sequence compliance. This smoke may assess module interaction and transaction-state behavior, but it cannot support authentication, privacy, or policy-enforcement claims. The decision and future confirmatory options are recorded in `docs/PHASE0E_PROTOCOL_DECISION.md`.

## 13. Current gate snapshot

| Gate | State |
|---|---|
| Phase 0D accounting/retry fixes | PASS per no-API tests |
| Provider-backed User Simulator adapter | IMPLEMENTED; 39-test report includes adapter coverage |
| Five distinct provider clients | NOT YET WIRED |
| Shared RequestBudget identity across five clients | NOT YET ENFORCED |
| Shared ModelFingerprintTracker across five clients | NOT YET ENFORCED |
| Mixed Retail/Airline environment factory | NOT YET WIRED |
| Retail task 5 protocol decision | RETAIN UNMODIFIED WITH DISCLOSURE |
| Corrected request/cost upper bounds | RECORDED; factory enforcement pending |
| Immutable 64-episode pre-run manifest | NOT YET FROZEN |
| GitHub Actions on d63bf1b | PASS, run 45100563417 |
| Actual provider model/fingerprint | NOT VERIFIED; first approved request only |
| Paid smoke | NOT AUTHORIZED / NOT STARTED |
