# Project Status

**Last updated:** 2026-11-20
**Overall state:** PRE-EXPERIMENT
**Current workstream:** Phase 0B — statistical correction, tau2 adapter validation, and protocol freeze
**Executor prompt:** [docs/EXECUTOR_PROMPT_PHASE0A.md](docs/EXECUTOR_PROMPT_PHASE0A.md)

## Confirmed

- A focused research question has been defined: learn module interactions and use them to guide cooperative evolutionary search over modular LLM Agents.
- The working algorithm label is NIL-CCEA; the v0.1 mechanism remains a hypothesis, not a validated contribution.
- A measurement-first factorial interaction protocol has been drafted.
- The public GitHub repository has been initialized and the initial research workspace synchronized.
- A detailed Phase 0A executor prompt is now recorded in the repository, including source-audit requirements, environment compatibility checks, experimental guardrails, acceptance gates, and handoff rules.
- The Phase 0A literature audit now verifies AgentSquare, EvoTool, AgentSpec, DG/DG2/RDG/RDG2, LMM, cooperative coevolution, linkage-tree methods, and 2025–2026 adjacent Agent evolution work with primary-source links and overlap risks.
- The environment audit rejects the outdated tau-bench checkout for formal runs and pins tau2-bench v1.0.1 text-v1 as the primary candidate. ToolSandbox is retained as a local diagnostic fallback.
- A draft four-slot module contract and pre-freeze pilot design are recorded. The contract keeps Planner, Selector, Caller, and Synthesizer behind separate interfaces and identical tool permissions.
- A pure-local mock runner now generates all 16 configurations, immutable manifests, config hashes, task/seed pairing, retry/failure records, raw trajectories, cost ledger entries, and pairwise interaction estimates.
- Pure-local Planner, Selector, Caller, and Synthesizer variants now share typed contracts and pass static evaluator-token leakage checks.
- The tau2 `HalfDuplexAgent` adapter now reads real `Tool.openai_schema` and `Tool.params`, validates Selector/Caller consistency, handles ToolMessage/MultiToolMessage, persists plan_state, and requires task metadata.
- Real tau2 v1.0.1 Tool, Environment, HalfDuplexAgent, and Orchestrator classes pass all 21 no-API tests in Python 3.12.16 with a local LiteLLM stub that raises on any completion call.
- The corrected estimator uses task-level clusters, two repeated seeds, complete 16 configurations, four contexts, explicit failure semantics, and six-pair Holm correction.

## Not yet completed

- Provider price verification and user approval before any real benchmark call.
- Controlled 2-task × 2-seed × 16-configuration exploratory smoke.
- Confirmation-level variance and power review after exploratory smoke.
- Formal factorial pilot and interaction analysis.
- Any evidence that NIL-CCEA improves an evolutionary baseline.

## Current decision

G0, G1, and no-API G3 evidence are complete. G2 remains under review until provider pricing is verified. Do not start paid smoke or the formal factorial pilot without explicit approval.

If one benchmark or module pair is unsuitable, diagnose and move to the next candidate or a controlled fallback. A single null interaction or benchmark incompatibility is not a project stop condition.

## Next acceptance gates

| Gate | Required evidence | State |
|---|---|---|
| G0 Literature | Verified primary-source bibliography and mechanism comparison | PASS |
| G1 Environment | Source-backed benchmark compatibility and module replacement | PASS |
| G2 Contracts/protocol | Frozen module interfaces, variants, endpoint, statistics, and cost rules | NEEDS_REVISION pending price verification |
| G3 Smoke | Configuration, pairing/reset, failure, and cost tests pass | PASS for mock and tau2 no-API scope |
| G4 Pilot | Frozen factorial pilot and reproducible interaction estimates | NOT STARTED |
| G5 Search | Fair-budget comparison of linkage-aware cooperative evolution | NOT STARTED |

## Evidence discipline

No pilot data, benchmark result, statistical significance, performance gain, or novelty claim is asserted in this file. Update this status only when supported by committed artifacts and reproducible commands.
