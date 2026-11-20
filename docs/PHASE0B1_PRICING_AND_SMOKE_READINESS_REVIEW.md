# Phase 0B.1 — Pricing Verification and Smoke-Readiness Review

**Review date:** 2026-11-20  
**Repository:** `yujian777555/NIL-CCEA`  
**Branch reviewed:** `phase0b-adapter-statistical-corrections`  
**Reviewed HEAD:** `0031055c14ac50dec9d6436e3d35659897d02016`  
**PR #2:** https://github.com/yujian777555/NIL-CCEA/pull/2  
**Review type:** read-only source/configuration review plus official provider documentation check. No model API calls were made.

## Executive decision

The Phase 0B statistical and tau2 no-API corrections are a substantial step forward. The declared GPT-4.1 standard input/output rates are correct as of this review date, and the current arithmetic is reproducible.

**Do not start the paid exploratory smoke yet.** The price check uncovered a model-lifecycle issue, and source inspection found remaining gaps between the Phase 0B completion report and the executable repository:

1. GPT-4.1 is deprecated and has a published shutdown date of 2027-01-14.
2. The adapter still invokes Caller before checking whether Selector chose `tool_call`.
3. The repository currently contains deterministic mock modules and a MockRunner, but no provider-backed module implementations or real tau2 factorial runner.
4. The practical interaction threshold is inconsistent between the code default and the protocol sensitivity table.
5. An older protocol document still describes a 32-episode smoke, while the current candidate protocol specifies 64 episodes.
6. The package README still says the tau2 adapter is unvalidated, contradicting the Phase 0B no-API integration tests.

These are finite pre-smoke tasks, not reasons to abandon NIL-CCEA.

## 1. Provider pricing — VERIFIED

The active cost profile specifies:

- Provider: OpenAI
- Agent model: `gpt-4.1-2025-04-14`
- User simulator model: `gpt-4.1-2025-04-14`
- Input: USD 2.00 / 1M tokens
- Cached input: USD 0.50 / 1M tokens
- Output: USD 8.00 / 1M tokens

The official GPT-4.1 model page lists standard input at $2.00, cached input at $0.50, and output at $8.00 per million tokens:
https://developers.openai.com/api/docs/models/gpt-4.1

The active upper-bound calculation correctly uses the uncached input rate, so it does not rely on prompt-cache savings.

Given 2,000 input and 512 output tokens per provider request:

`2000 × 2 / 1,000,000 + 512 × 8 / 1,000,000 = $0.008096`

At 30 agent requests plus 30 user-simulator requests per episode:

- Per episode: $0.48576
- 64-episode exploratory smoke: $31.08864
- Exploratory smoke with every request retried once: $62.17728
- 384-episode pilot: $186.53184
- Pilot with every request retried once: $373.06368

The existing $80 smoke cap and $400 pilot cap cover those declared worst-case token/request assumptions. They are budget ceilings, not expected spend.

## 2. Model lifecycle — BLOCKER FOR LONG-RUN FREEZE

OpenAI marks `gpt-4.1-2025-04-14` as Deprecated and publishes 2027-01-14 as its shutdown date:
https://developers.openai.com/api/docs/deprecations

The deprecation page lists `gpt-6-luna` as the recommended replacement. Its official model page lists standard rates of $0.10 input and $0.50 output per million tokens, and states that Chat Completions function calling is supported with `reasoning_effort=none`:
https://developers.openai.com/api/docs/models/gpt-6-luna

Using the same token/request caps, the reference-only GPT-6 Luna estimate would be:

- Per request: $0.000456
- Per episode: $0.02736
- 64-episode smoke: $1.75104; with one retry on every request: $3.50208
- 384-episode pilot: $10.50624; with one retry on every request: $21.01248

**This is not an approved model change.** Model migration changes the experimental backbone and must be versioned before any real run. Do not mix GPT-4.1 and GPT-6 Luna within one factorial dataset. The user must decide whether to retain GPT-4.1 for a time-bounded experiment or migrate both Agent and User Simulator to GPT-6 Luna before smoke.

## 3. Adapter control-flow residual

In `src/nil_ccea/tau2_adapter.py`, line 185 currently invokes:

`proposal = self.caller.propose(context, plan, selection)`

before the branch at line 200 checks whether `selection.kind == "tool_call"`.

This contradicts the intended contract that Caller runs only when Selector selects a tool call. For `respond` and `stop`, Caller should not be invoked. This matters for module isolation: the Caller slot must not consume model calls or influence a non-tool action.

**Required correction:** move Caller invocation inside the `tool_call` branch. For `respond/stop`, record an explicit skipped/not-applicable event if needed, then invoke Synthesizer. Add tests with a Caller that raises if invoked for respond or stop.

## 4. Real API execution path is not yet implemented

The current repository has:

- `src/nil_ccea/mock_modules.py`: deterministic local module variants;
- `src/nil_ccea/runner.py`: `MockRunner`, which explicitly emits `mode="mock"`;
- `src/nil_ccea/tau2_adapter.py`: an adapter that accepts injected module objects.

The repository does not yet contain provider-backed Planner/Selector/Caller/Synthesizer implementations or a real tau2 factorial runner that constructs each of the 16 configurations, resets the pinned task/environment, executes the Orchestrator, and writes raw trajectories and cost events. `pyproject.toml` also declares no runtime provider dependencies.

The 21 tau2 tests establish no-key compatibility with tau2 classes and Orchestrator. They do not establish that a paid real-model smoke is executable.

**Required correction:** implement a provider-client abstraction and four real module wrappers plus a tau2 runner. Tests must inject a deterministic fake client and prove zero outbound completions. The runner must produce all 16 configuration manifests, task/seed pairing, raw messages, module events, usage records, retries, failures, and cost ledger entries.

## 5. Practical delta mismatch

- `src/nil_ccea/interaction.py` defaults `practical_delta=0.05`.
- The Phase 0B report also states practical delta 0.05.
- `docs/PHASE0B_PROTOCOL_FREEZE.md` currently has a sensitivity table explicitly framed as identifying `delta=0.10`.

The code default and intended candidate are consistent with 0.05, but the table does not establish power/precision for 0.05.

**Required correction:** keep 0.05 as the candidate unless the user changes it; recompute the sensitivity/power table for 0.05 using task-level clusters and the declared six-test multiplicity method. Do not reuse the 0.10 table as evidence for 0.05. The two-task exploratory smoke is descriptive and must not be used to claim confirmatory power.

## 6. Conflicting and stale documentation

- `docs/EXPERIMENT_PROTOCOL_PILOT.md` still lists smoke as 2 tasks × 1 seed × 16 = 32 episodes.
- `docs/PHASE0B_PROTOCOL_FREEZE.md` and the latest handoff specify 2 tasks × 2 seeds × 16 = 64 episodes.
- `src/nil_ccea/README.md` says the tau2 adapter remains unvalidated, while Phase 0B reports 21 real-class no-API integration tests.

**Required correction:** mark the older protocol as superseded by the Phase 0B freeze, and update the package README to distinguish no-API adapter validation from the not-yet-implemented real provider runner.

## 7. GitHub review state

PR #2 is open, not merged, and targets `phase0a-literature-environment-audit`. Its head is `0031055c14ac50dec9d6436e3d35659897d02016`. GitHub reports it mergeable, but the reviewed SHA has zero commit statuses and zero check runs. The 21-pass result remains executor-reported local evidence until CI or an independently reproduced run is attached.

PR #1 remains open and unmerged.

## Gate decision

| Gate | Decision | Reason |
|---|---|---|
| G0 Literature | PASS | Phase 0A audit remains the accepted literature baseline |
| G1 Environment | PASS | Pinned tau2 classes and no-key Orchestrator path reported tested |
| G2 Contracts/protocol | NEEDS_REVISION | Model lifecycle decision, delta/power alignment, and real execution contract remain open |
| G3 No-API smoke | PASS for tested scope only | Real tau2 classes tested without completions; Caller control-flow test still required |
| G3 Real-runner readiness | BLOCKED | Provider-backed modules and real tau2 factorial runner absent |
| G4 Paid exploratory smoke | NOT STARTED | Requires code readiness and explicit user approval |
| G5 Search | NOT STARTED | No reliable real interaction data yet |

## Next action

Execute `docs/EXECUTOR_PROMPT_PHASE0C.md` using the user's now-selected DeepSeek Flash configuration. Do not make any paid API call. The model choice is resolved; implementation, no-API validation, independent review, and explicit paid-smoke approval remain required.

## 8. Superseding user model decision — DeepSeek Flash (2026-11-20)

After this review, the user explicitly selected **DeepSeek Flash**. This supersedes the earlier recommendation to choose between GPT-4.1 and GPT-6 Luna. The active model for Agent, User Simulator, Planner, Selector, Caller, and Synthesizer is now the DeepSeek API alias `deepseek-flash`.

The official DeepSeek page identifies the current served model as DeepSeek-V4.1-Flash-1017, supports JSON Output and Tool Calls, and publishes peak rates of $0.30/M input cache miss, $0.006/M input cache hit, and $1.20/M output; off-peak rates are half. The alias is mutable, so every request must record response `model` and `system_fingerprint`.
Sources:
- https://api-docs.deepseek.com/quick_start/pricing/
- https://api-docs.deepseek.com/api/create-chat-completion/

Execution contract:
- Thinking/CoT disabled: `thinking={"type":"disabled"}`, `reasoning_effort="none"`.
- JSON mode enabled for structured JSON content responses; Caller uses native Tool Calls and local schema validation.
- Temperature 0.0; max output 512; input cap 2,000.
- Direct DeepSeek network connection using dedicated HTTPX client `trust_env=false`; bypass system proxy.
- Use `DEEPSEEK_API_KEY` from environment only.
- Conservative peak/cache-miss budget: $0.0012144/request; $0.072864/episode; $4.663296/64-episode smoke; $9.326592 with one retry on every request; $27.979776/384-episode pilot; $55.959552 with one retry on every request.
- No paid API call has been approved. The user selected the model, not the paid run.

This decision supersedes only the model/provider selection in this review. Adapter control flow, provider-backed modules, real tau2 runner, practical-delta sensitivity, CI, and independent review remain pre-smoke requirements.

