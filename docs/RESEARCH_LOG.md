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
