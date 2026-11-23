# NIL-CCEA Phase 0E.1 — Smoke Factory, Request-Budget Closure, and Protocol Freeze

## Repository baseline

- Repository: https://github.com/yujian777555/NIL-CCEA
- Branch: phase0b-adapter-statistical-corrections
- Baseline before this prompt update: 833fb4f1c19b4dce74b7783dd6ac1d10bbc92875
- PR #2: https://github.com/yujian777555/NIL-CCEA/pull/2 (open, unmerged)
- Pinned tau2-bench: v1.0.1, commit fc0055dc4e0a316c3f83133267fbd6faaa770992
- Provider-backed User Simulator: src/nil_ccea/tau2_user_simulator.py (implemented, no-API tested)
- Retail task decision: docs/PHASE0E_PROTOCOL_DECISION.md
- Cost profile: experiments/pilot_factorial/cost_profile.json

## Mission

Finish the no-API smoke factory wiring, enforce one shared global RequestBudget and one shared model-identity tracker across five distinct provider clients, make the runner support both Retail and Airline tasks in one 64-episode run, and freeze an immutable pre-run manifest. Retain Retail task 5 unchanged with the explicit issue disclosure recorded in the protocol decision.

**HARD STOP:** Until the user explicitly approves the paid run, do not read DEEPSEEK_API_KEY, do not send any DeepSeek request, and do not execute a paid benchmark episode. Do not treat this prompt, a model selection, a cost estimate, or a prior conversation as paid-run authorization.

## Read first

1. docs/PHASE0E_PROTOCOL_DECISION.md
2. docs/PHASE0E_PREFLIGHT_REVIEW.md
3. docs/PHASE0D_INDEPENDENT_REVIEW.md
4. STATUS.md
5. NEXT_STEPS.md
6. docs/HANDOFF.md
7. experiments/pilot_factorial/cost_profile.json
8. src/nil_ccea/tau2_runner.py
9. src/nil_ccea/tau2_user_simulator.py
10. src/nil_ccea/deepseek_client.py
11. src/nil_ccea/deepseek_modules.py
12. pinned tau2 Orchestrator, Retail, and Airline environment source at the commit above.

## 1. Preserve repository and artifacts

- Verify branch, local HEAD, PR #2 head, remote sync, worktree cleanliness, latest CI and PR reviews.
- Keep NIL-CCEA isolated from all other repositories.
- Do not modify main, merge PR #1/#2, force-push, rewrite history, or overwrite any existing artifact.
- Preserve every existing episodes.jsonl, request_events.jsonl, cost_ledger.json, run_summary.json, and manifest.
- Correct stale SHA/run references in all handoff documents.
- A read-only independent code review is not the same as a formal GitHub PR review. Report both states separately.

## 2. P0 — Build the actual five-client smoke factory

The current User Simulator adapter exists, but the paid smoke factory is not yet wired. Implement a narrow factory, preferably src/nil_ccea/smoke_factory.py plus a guarded scripts/run_tau2_smoke.py entry point.

The factory must construct:

- four distinct DeepSeekClient objects: Planner, Selector, Caller, Synthesizer;
- one additional distinct DeepSeekClient for DeepSeekTau2UserSimulator;
- one shared RequestBudget object assigned by identity to all five clients;
- one shared ModelFingerprintTracker object assigned by identity to all five clients.

Do not use a single DeepSeekClient instance for all four modules. Tau2FactorialRunner sets episode context with a module name on each client. If the same client instance is reused, the last context assignment overwrites the earlier module name and request attribution becomes incorrect.

The current build_deepseek_modules(client, configuration) shares one client across all four module wrappers. Add a mapping-based builder or instantiate the four module classes with their corresponding clients. Preserve the old builder only for compatibility if needed.

All five clients must have identical:
- model alias deepseek-flash;
- base URL https://api.deepseek.com;
- temperature 0.0;
- max_output_tokens 512;
- max_input_tokens 2000;
- max_retries 1;
- thinking disabled;
- direct HTTPX transport with trust_env=False;
- provider pricing values from the refreshed cost profile.

All five clients must have the same RequestBudget object and the same ModelFingerprintTracker object. Each client must remain a distinct object so its audit events and module context remain correctly attributable.

The module factory must construct the four configured variants from the four per-slot clients. The environment-aware user factory must construct DeepSeekTau2UserSimulator using the fifth client and the current task/environment.

## 3. P0 — Support mixed Retail + Airline tasks in one runner

The 64-episode candidate contains one Retail task and one Airline task. The current Tau2FactorialRunner calls environment_factory() without the task, which cannot safely choose the correct domain environment for a mixed-domain task list.

Implement task-aware environment selection without breaking existing zero-argument test factories. Prefer an explicit environment_factory_with_task(task) callback or a backwards-compatible signature adapter.

Determine domain from the pinned task schema, specifically task.user_scenario.instructions.domain. Support only the frozen smoke domains:
- retail -> tau2.domains.retail.environment.get_environment()
- airline -> tau2.domains.airline.environment.get_environment()

Fail closed on unknown or mismatched domains. Add a no-API test that runs both task types and proves each receives the correct environment, policy, and tools. Do not share one mutable environment or database state between episodes.

The User Simulator factory must receive the task and the exact environment instance used by the Orchestrator. Preserve task instructions using the tau2 UserScenario string representation, and preserve any intended user-tool behavior.

## 4. P0 — Enforce shared budget and model identity, fail closed

Strengthen Tau2FactorialRunner validation for evaluate=True:

- exactly four module slots are present;
- each module exposes its own DeepSeekClient;
- all four module client objects are distinct;
- the User Simulator exposes the provider-backed DeepSeekTau2UserSimulator and its controlled client;
- the User Simulator client is distinct from all four module clients;
- every one of the five clients has client.budget is runner.request_budget;
- every one of the five clients has client.identity_tracker is the same shared tracker;
- every client uses the same model alias, base URL, temperature, output cap, input cap and retry limit;
- the five clients expose request-event draining;
- each client receives the correct per-episode context and module attribution;
- no stock tau2 LiteLLM generation path can be used in paid execution.

A model-name string alone is not evidence of a controlled provider path. Reject a User Simulator that only exposes llm='deepseek-flash' but does not carry the adapter's controlled client.

Add tests proving:
1. five distinct clients, one shared budget object, one shared identity tracker;
2. module attribution is separately planner, selector, caller, synthesizer, user_simulator;
3. all five event streams are drained into the same episode record;
4. a separate budget or shared module client is rejected;
5. stock tau2 UserSimulator is rejected;
6. missing or mismatched identity tracker is rejected;
7. model/fingerprint drift quarantines the batch;
8. direct transport settings are validated without a live request.

The first live request must establish response.model and system_fingerprint and bind the shared tracker. Never hardcode the public documentation's model version as an observed response.

## 5. Correct request-count and cost bounds — do not reuse the old 60-request arithmetic

Source-level call graph:
- Every Agent response invokes Planner and Selector, then exactly one of Caller or Synthesizer: up to 3 module requests per Agent response.
- max_steps is 30.
- Conservatively allow up to 30 Agent responses and 30 User Simulator responses per episode.
- Therefore the conservative bound is 90 Agent module requests + 30 User Simulator requests = 120 logical requests per episode.
- One safe retry per logical request reserves up to 240 physical attempts per episode.

Using peak cache-miss prices and 2,000 input + 512 output tokens:
- per-request upper bound: $0.0012144;
- per-episode, 120 logical requests, no retry: $0.145728;
- per-episode, all requests retried once: $0.291456;
- 64 episodes: 7,680 normal logical requests;
- 64 episodes: 15,360 maximum physical attempts with one retry each;
- 64-episode cost upper bound, no retries: $9.326592;
- 64-episode cost upper bound, one retry for every request: $18.653184;
- 384-episode pilot: 46,080 normal logical requests / 92,160 maximum physical attempts;
- 384-episode cost upper bound: $55.959552 without retries / $111.919104 with one retry for every request.

The prior 3,840 / 7,680 request and $4.663296 / $9.326592 smoke estimates undercounted module calls and are superseded. Do not use them in any approval request.

For the 64-episode smoke, construct the shared RequestBudget with conservative reservation semantics:
- max_requests = 15,360 physical-attempt reservations;
- max_input_tokens = 30,720,000;
- max_output_tokens = 7,864,320;
- max_cost_usd = $20.00 proposed spend ceiling (not authorized yet);
- episode_max_requests = 240;
- episode_max_input_tokens = 480,000;
- episode_max_output_tokens = 122,880;
- episode_max_cost_usd = $0.291456.

RequestBudget.reserve currently reserves max_retries + 1 attempts before sending; size these limits to physical reservations, not logical requests. Confirm the exact semantics in code and tests. The $80 exploratory hard stop remains a separate outer safety limit, not spending authorization. The proposed $20 authorization ceiling is not yet granted. If any changed provider pricing or code assumptions increase the upper bound above $20, stop and present the revised amount before asking for approval.

The cost profile and all protocol documents must be updated to these corrected figures. Explain that 120 per episode is a conservative bound derived from the three module calls per Agent response plus User Simulator calls.

## 6. Retail task 5 protocol decision — retain unchanged, disclose the limitation

Follow docs/PHASE0E_PROTOCOL_DECISION.md:

- Keep Retail task 5 and Airline task 2 in this exploratory smoke.
- Do not patch the pinned tau2 environment or silently substitute a task.
- Record open issue issue_770466c1 in the pre-run manifest.
- Retail policy requires authentication, but pinned RetailTools does not maintain authenticated-user state or guard get_user_details/get_order_details.
- Retail task 5 reward_basis is DB + NL_ASSERTION, not ACTION. The ENV reward therefore does not guarantee authentication-sequence compliance.
- This task may be used for integration, module-interaction and transaction-state diagnostics only. Do not claim authentication, privacy, or policy-enforcement robustness.
- Record whether find_user_id_by_name_zip occurred before get_user_details/get_order_details as a descriptive diagnostic only. Do not alter the primary ENV endpoint or score.
- Final paid-run approval must explicitly disclose this known limitation and ask the user to accept it.

## 7. Immutable pre-run manifest

Create a new immutable smoke pre-run manifest and schema. Do not overwrite any existing manifest.

It must include:
- NIL-CCEA code SHA;
- protocol version and protocol hash;
- pinned tau2 version and commit SHA;
- exact task IDs, domains, test split and task-quality flags;
- seeds 0 and 1;
- all 16 binary configurations and deterministic execution order/seed;
- model alias, endpoint, temperature, thinking-disabled setting, output/input caps;
- five distinct client roles and shared budget/identity-tracker policy (no credentials or secret values);
- normal and maximum physical request counts;
- per-request, per-episode and total cost bounds;
- proposed $20 spend ceiling and separate $80 hard stop;
- Retail task 5 issue disclosure;
- primary endpoint EvaluationType.ENV;
- statement that the smoke is exploratory only and has two task clusters.

The manifest must distinguish NIL-CCEA code SHA from tau2 source SHA. Do not label the tau2 SHA as the NIL-CCEA source commit. Hash the canonical manifest and make the artifact immutable.

No served model or fingerprint can be recorded as observed before the first approved request. The first response identity check is part of the approved 64-episode run, not an unbudgeted extra request.

## 8. Guarded CLI and zero-API preflight

- The smoke factory must be importable and testable without reading DEEPSEEK_API_KEY.
- The script must not read the API key at import time or during preflight/dry-run.
- Require an explicit paid-execution flag for the CLI path that reads the key and starts the runner. This flag is an additional guard, not a substitute for explicit user approval in this conversation.
- Use fake clients and fake keys only in tests; never send requests in tests.
- No endpoint probe, test completion, or provider health check before user approval.
- Preserve direct transport trust_env=False; do not modify global proxy settings.

## 9. Tests and CI

Run and report:
- host no-API suite (expected current baseline: 39 pass, 12 tau2-dependent skips);
- pinned Python 3.12.16 + tau2-bench v1.0.1 suite (expected current baseline: 39 pass);
- real tau2 Orchestrator no-API integration across the 32 cells;
- new smoke-factory tests;
- mixed Retail/Airline task environment selection test;
- request-count arithmetic tests;
- final GitHub Actions on the final pushed SHA.

Do not claim the prior CI proves the new smoke factory. It only covers the code that existed at its head.

## 10. Maintenance and final approval package

Update:
- STATUS.md
- NEXT_STEPS.md
- docs/HANDOFF.md
- docs/RESEARCH_LOG.md
- docs/PHASE0E_PREFLIGHT_REVIEW.md
- docs/PHASE0E_PROTOCOL_DECISION.md
- docs/EXECUTOR_PROMPT_PHASE0E.md
- experiments/pilot_factorial/cost_profile.json
- protocol and manifest schemas as needed.

After all no-API tests and CI pass, present the user with an exact approval request:
- 64 episodes: Retail 5 + Airline 2 × seeds 0/1 × 16 configurations;
- 7,680 normal logical requests; 15,360 maximum physical attempts;
- $9.326592 no-retry upper bound; $18.653184 worst-case retry upper bound;
- proposed maximum spend authorization: $20;
- separate hard stop: $80;
- model: deepseek-flash; endpoint https://api.deepseek.com; thinking disabled;
- first response model/fingerprint verification and quarantine rule;
- Retail task 5 issue_770466c1 disclosure and scope limitation;
- no significance, confirmatory algorithmic improvement, security, or novelty claim from this two-cluster smoke.

Wait for explicit user approval. Do not start the paid smoke in this phase.

## Research interpretation and continuation

The smoke measures integration reliability, trace/cost accounting, task execution and descriptive 2^4 interaction behavior. It cannot establish statistical significance or reliable task-cluster variance with only two tasks.

After a valid smoke, the next separately approved study remains 12 tasks × 2 seeds × 16 configurations = 384 episodes, with corrected cost bounds above. Only after trustworthy interaction estimates should Linkage Learning and Linkage-aware Cooperative Co-evolution be implemented and compared under equal evaluation budgets.

Do not stop the research because a task or wiring issue needs revision. Diagnose, version the protocol, and continue without fabricating evidence.

## 2026-11-23 Phase 0E.1 implementation update

Smoke Factory, task-aware mixed-domain environments, five-client shared-budget/shared-tracker validation, guarded dry-run CLI, and immutable pre-run manifest are implemented. Current code SHA is `bcc762e711815316dae17e4eef8bdbd4f2a815ee`. Manifest hash is `66132bb3e7f83661b5acecfd95340da37162734287be72a2baca3384324ff0de`. Host and pinned no-API suites each pass 47 tests. No API key was read and no provider request was sent.
