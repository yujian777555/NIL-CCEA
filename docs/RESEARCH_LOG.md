# Research Decision Log

## 2026-11-18 — Project initialization

- Created a dedicated research workspace for module-interaction-aware cooperative evolution of modular LLM Agents.
- Working algorithm name: NIL-CCEA.
- Chosen first step: measurement-first 2^4 factorial pilot, not immediate full optimizer implementation.
- Provisional four module slots: Planner, Selector, Caller, Synthesizer. These are subject to benchmark compatibility and interface audit.
- Core estimator: paired difference-in-differences interaction contrast, averaged over other module-slot contexts.
- Core algorithm hypothesis: use a signed, uncertainty-aware linkage graph to select independent, cooperative, or compatibility-aware variation.
- No implementation, benchmark result, performance gain, or novelty claim is asserted at initialization.

## Decision rules

- Every material change to the algorithm must be recorded with rationale and evidence.
- Every experimental change after protocol freeze must be versioned and explained.
- Do not delete failed experiments; mark them and preserve raw records.
- Keep a separate record of negative, null, and positive results.

## 2026-11-19 — GitHub remote initialized

- Created the public remote repository: https://github.com/yujian777555/NIL-CCEA.
- Published the project README and synchronized the initial research workspace.
- Research stage remains PRE-EXPERIMENT; no benchmark execution, statistical result, performance gain, or novelty claim is recorded.

## 2026-11-19 — Phase 0A executor prompt prepared

- Added docs/EXECUTOR_PROMPT_PHASE0A.md as the authoritative execution contract for the next agent handoff.
- Converted the broad next-step list into a time-boxed sequence: parallel primary-source literature and environment audits, evidence-backed module compatibility decision, module contracts/variants, mock runner validation, independent review, then the formal pilot.
- Explicitly retained NIL-CCEA's evolutionary-computation and module-interaction-linkage focus. Fixed total evaluation budget remains a fairness constraint, not a budget-allocation contribution.
- Added a diagnostic continuation rule: null or weak interactions trigger checks of manipulation validity, task-family dependence, noise, statistical power, and higher-order effects; they do not automatically terminate the project or justify manufacturing positive results.
- Updated STATUS.md, NEXT_STEPS.md, and this handoff file to point to the prompt.
- This is a planning/handoff update only. No benchmark was selected, no experiment was run, and no algorithmic improvement or novelty is claimed.

## 2026-11-19 — Phase 0A literature and environment audit

- Created branch `phase0a-literature-environment-audit` from remote main SHA `98e202f21bb82f6df4835f48e4d1c922113719ad`.
- Completed primary-source checks for AgentSquare, EvoTool, AgentSpec, DG, DG2, RDG, RDG2, LMM, cooperative coevolution, linkage-tree methods, EvoAgentX, AgentEvo, CoPES, and AgenticEvolve.
- Confirmed that EvoTool and AgentSquare are direct module-evolution neighbors, while AgentSpec is a controlled-composition and interaction-analysis neighbor. A novelty claim based only on four module slots or module search is therefore rejected.
- Rejected the outdated `tau-bench` checkout for formal runs because its own README points to updated tau2-bench tasks. Selected tau2-bench v1.0.1 text-v1 as the primary environment candidate and recorded the exact release commit in `experiments/pilot_factorial/environment.lock.json`.
- Retained ToolSandbox as a local diagnostic fallback because it exposes state snapshots and milestone evaluation, while recording its seed, license, host-execution, and RapidAPI limitations.
- Added `docs/LITERATURE_AUDIT_PHASE0A.md`, `docs/ENVIRONMENT_COMPATIBILITY_PHASE0A.md`, `docs/MODULE_CONTRACTS_DRAFT.md`, and `docs/PILOT_DESIGN_R1.md`.
- The four-slot boundary is supported by the tau2 custom `HalfDuplexAgent` API at source level. It is not yet validated by a real adapter run.

## 2026-11-19 — Mock runner implemented

- Added a stdlib-only local runner that generates all 16 binary configurations, immutable module manifests, configuration hashes, task/seed pairing, reset state, raw trajectory records, failure/retry events, and cost ledger entries.
- Added a pure difference-in-differences estimator with context averaging, task-cluster bootstrap, and `UNCERTAIN` state handling.
- Added configuration, episode, cost ledger, and environment lock schemas under `experiments/pilot_factorial/`.
- Added typed module contracts, eight pure-local mechanism variants, and static evaluator-token leakage checks.
- Added a tau2 `HalfDuplexAgent` adapter entry point with an explicit external-dependency gate. It is implemented but unvalidated against tau2.
- Ran the local suite with eleven passing tests on host Python 3.10.1. The mock run generated 32 episodes and made zero real API calls. The synthetic positive interaction is a runner validation signal only and is not a research result.
- G0 is PASS, source-level G1 is PASS, G2 is NEEDS_REVISION until the tau2 adapter and endpoint freeze are reviewed, and G3 is PASS for the mock scope.


## 2026-11-19 — Independent review of Phase 0A implementation

- Read-only review of PR #1 and the pinned tau2-bench v1.0.1 source completed.
- Confirmed that tau2 v1.0.1 requires Python `>=3.12,<3.14`, its `Tool` exposes `params` and `openai_schema`, and its half-duplex agent receives user/tool/multi-tool messages.
- Identified adapter schema extraction mismatch: current code reads `parameters` / `schema`, so real tool parameter schemas can be empty.
- Identified statistical unit mismatch: current estimator bootstraps `(task_id, seed)` although the protocol requires task-level clusters and nested seeds.
- Identified incomplete-cell handling that can average only available contexts after filtering failures, potentially changing the estimand.
- Identified missing Selector-to-Caller consistency checks, missing real schema validation, unpersisted plan state, unknown task metadata defaults, and absence of pinned tau2 integration tests.
- PR #1 remains open and unmerged. GitHub reports no status checks and no reviews on the reviewed SHA; the 11-test result remains executor-reported local evidence.
- Created Phase 0B review and executor prompt. This is a code-review/handoff milestone only; no code correction, tau2 execution, paid API call, or benchmark experiment is claimed.

## 2026-11-20 — Phase 0B corrections completed

- Merged the remote Phase 0B review baseline without overwriting its independent review or executor prompt.
- Corrected the estimator to task-level clusters with two nested seeds, complete 16 configurations, four contexts, duplicate rejection, explicit failure semantics, task-level bootstrap, permutation p-values, and Holm step-down for six pairs.
- Corrected the tau2 adapter against real v1.0.1 classes. Tool schemas now come from `openai_schema`, arguments are validated through `params`, Selector/Caller mismatches fail closed, tool and multi-tool messages update public state, metadata and seed are injected, and invalid calls raise typed errors.
- Added real tau2 no-API tests for 16 permission-invariant configurations, schema validation, multi-turn tool execution, state recovery, manifest metadata, and Orchestrator trajectories.
- No paid API calls were made. Exploratory and formal cost caps are recorded in `docs/PHASE0B_PROTOCOL_FREEZE.md` and `experiments/pilot_factorial/cost_profile.json`.

## 2026-11-20 — Phase 0B.1 pricing and smoke-readiness review

- Verified OpenAI GPT-4.1 standard rates from the official model page: $2/M input, $0.50/M cached input, $8/M output. The active cost profile uses uncached input pricing and its upper-bound arithmetic is correct.
- Confirmed `gpt-4.1-2025-04-14` is deprecated with announced shutdown date 2027-01-14; OpenAI lists `gpt-6-luna` as the recommended replacement. No model switch was made.
- Recorded a reference-only GPT-6 Luna standard rate of $0.10/M input and $0.50/M output; Chat Completions function calling requires `reasoning_effort=none`.
- Identified residual adapter control-flow issue: Caller is invoked before the action-kind branch, including respond/stop decisions.
- Confirmed provider-backed module implementations and a real tau2 factorial runner are absent; the current runner/modules remain mock-only.
- Identified practical-delta mismatch: code default/candidate is 0.05, while the protocol sensitivity table is for 0.10.
- Marked the old 32-episode smoke planning row as superseded by the current 64-episode candidate.
- PR #2 remains open and unmerged. GitHub reports zero status checks/check runs for its current head. No paid API calls were made.
- Added Phase 0C handoff requirements. G2 remains NEEDS_REVISION; real-runner readiness is BLOCKED; G4 remains NOT STARTED.

## 2026-11-20 — User selects DeepSeek Flash for NIL-CCEA

- User explicitly selected `deepseek-flash` instead of the previously discussed OpenAI models.
- Decision applies uniformly to Planner, Selector, Caller, Synthesizer, Agent, and User Simulator. No mixed-model factorial datasets.
- Official DeepSeek docs identify the alias as serving DeepSeek-V4.1-Flash-1017 as of this date; because the alias is mutable, capture response model and system fingerprint on every request.
- Fixed API configuration: OpenAI-compatible Chat Completions at `https://api.deepseek.com`; thinking/CoT disabled; JSON mode for structured outputs; temperature 0.0; output cap 512.
- DeepSeek requests must bypass the system proxy via a dedicated HTTP client with `trust_env=false`; do not change global proxy settings.
- Verified official peak rates: $0.30/M input cache miss, $0.006/M input cache hit, $1.20/M output; off-peak rates are half. Budget upper bounds use peak cache-miss rates.
- New conservative estimates: $0.0012144/request; $0.072864/episode; $4.663296 for 64-episode smoke; $9.326592 with one retry on every request; $27.979776 for 384-episode pilot; $55.959552 with one retry on every request.
- Model selection is not paid-run approval. No API call was made; paid smoke remains NOT STARTED.
- Phase 0C now targets DeepSeek client/request-contract integration, four provider-backed modules, real tau2 runner, Caller control-flow correction, and no-key tests.

