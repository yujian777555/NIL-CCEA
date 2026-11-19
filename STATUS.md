# Project Status

**Last updated:** 2026-11-19  
**Overall state:** PRE-EXPERIMENT  
**Current workstream:** Phase 0A — audit complete at source level, mock runner implemented
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
- Ten automated tests pass on the host Python 3.10.1 interpreter. The mock run used zero real API calls.

## Not yet completed

- Live tau2 custom-agent adapter smoke and source-level leakage audit.
- Confirmation of independently replaceable module slots in a real tau2 execution.
- Freezing the primary endpoint, practical threshold, task IDs, and cost stop rules.
- Paid API cost estimate and user approval before any real benchmark call.
- Formal factorial pilot and interaction analysis.
- Any evidence that NIL-CCEA improves an evolutionary baseline.

## Current decision

G0 and source-level G1 are complete. Continue with the custom tau2 `HalfDuplexAgent` adapter and mock-to-raw recomputation checks. Do not start the formal factorial pilot or complete evolutionary optimizer until G2 and G3 are reviewed.

If one benchmark or module pair is unsuitable, diagnose and move to the next candidate or a controlled fallback. A single null interaction or benchmark incompatibility is not a project stop condition.

## Next acceptance gates

| Gate | Required evidence | State |
|---|---|---|
| G0 Literature | Verified primary-source bibliography and mechanism comparison | PASS |
| G1 Environment | Source-backed benchmark compatibility and module replacement | PASS |
| G2 Contracts/protocol | Frozen module interfaces, variants, endpoint, statistics, and cost rules | NEEDS_REVISION |
| G3 Smoke | Configuration, pairing/reset, failure, and cost tests pass | PASS for mock scope |
| G4 Pilot | Frozen factorial pilot and reproducible interaction estimates | NOT STARTED |
| G5 Search | Fair-budget comparison of linkage-aware cooperative evolution | NOT STARTED |

## Evidence discipline

No pilot data, benchmark result, statistical significance, performance gain, or novelty claim is asserted in this file. Update this status only when supported by committed artifacts and reproducible commands.
