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
- Ran the local suite with nineteen passing tests on host Python 3.10.1. The mock run generated 32 episodes and made zero real API calls. The synthetic positive interaction is a runner validation signal only and is not a research result.
- G0 is PASS, source-level G1 is PASS, G2 is NEEDS_REVISION until the tau2 adapter and endpoint freeze are reviewed, and G3 is PASS for the mock scope.

## 2026-11-20 — Phase 0B statistical and adapter corrections

- Created branch `phase0b-adapter-statistical-corrections` from the Phase 0A branch.
- Corrected interaction estimation so the independent cluster is `task`. Seed `0` and seed `1` are repeated measurements within task. Full task-level validation now requires two seeds, unique complete 16 configurations per seed, four contexts per pair, and no infrastructure failures.
- Added explicit `success`, `agent_failed`, and `infra_failed` semantics. Agent failures contribute a valid primary score of zero. Infrastructure failures are retained and reject confirmation-level interaction estimation after retry exhaustion.
- Added task-level bootstrap, permutation p-values, six-pair Holm correction, duplicate configuration rejection, and regression tests.
- Reworked the tau2 adapter to use `Tool.openai_schema` and `Tool.params`, validate Selector/Caller consistency and arguments, process `ToolMessage` and `MultiToolMessage`, persist `plan_state`, and require task metadata injection.
- Created an independent Python 3.12.16 environment and checked out tau2-bench v1.0.1 at `fc0055dc4e0a316c3f83133267fbd6faaa770992`. Real tau2 Tool, message, HalfDuplexAgent, Environment, and Orchestrator classes passed 21 no-API tests using a local LiteLLM stub that raises on any completion call.
- Added `docs/PHASE0B_PROTOCOL_FREEZE.md`. The frozen candidate uses 12 task clusters, `ENV` as primary endpoint, seeds `0` and `1`, `delta=0.05`, Holm alpha `0.05`, max_steps `30`, one infrastructure retry, and explicit exploratory/formal cost caps.
