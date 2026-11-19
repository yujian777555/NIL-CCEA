# Executor Handoff — NIL-CCEA

**Repository:** https://github.com/yujian777555/NIL-CCEA (public, default branch main).
**Current workstream:** Phase 0B — statistical correction, tau2 adapter validation, and protocol freeze.
**Authoritative execution prompt:** [docs/EXECUTOR_PROMPT_PHASE0A.md](EXECUTOR_PROMPT_PHASE0A.md).
**Current research state:** PRE-EXPERIMENT. No real benchmark episode, performance result, or novelty claim has been established.

## Mission

Establish whether measurable, reproducible non-additive interactions exist among independently replaceable LLM-Agent modules, then use reliable signed and uncertainty-aware linkage to guide cooperative evolutionary search. Evolutionary computation and module-interaction linkage are the method core. A fixed total evaluation budget is a fairness constraint, not the research contribution.

## Immediate actions

1. Run the tau2 v1.0.1 `HalfDuplexAgent` adapter tests in the independent Python 3.12 environment.
2. Review the task-level estimator and six-pair Holm output.
3. Review `docs/PHASE0B_PROTOCOL_FREEZE.md` and update only if a source-backed correction is required.
4. Estimate and verify provider pricing before any real call.
5. Obtain approval, then run the controlled 2-task exploratory smoke.

## Planned measurement design

The corrected candidate uses four binary module slots (2^4 = 16 configurations), 12 fixed tasks, and two repeated seeds per task. The target is 12 tasks × 2 seeds × 16 configurations = 384 episodes. The independent statistical cluster is task, not task-seed.

For each module pair, estimate a paired difference-in-differences interaction contrast across four contexts, average the two seeds within task, then use task-level bootstrap and Holm correction. Do not interpret uncertain edges as independence.

## Required controls

- Preserve task/version, seed, model/provider/version, decoding settings, module hashes, runner commit, and config hash.
- Keep raw trajectories immutable and summaries reproducible.
- Count all probes, failures, retries, and diagnostic evaluations in total cost.
- Never silently drop failed episodes or retry without accounting.
- Do not change tasks, module variants, prompts, endpoints, or decoding parameters mid-run without a new protocol version.
- No base-model training or fine-tuning in this milestone.
- Do not claim novelty, significance, or improvement without primary-source and experimental evidence.
- Do not stop the project because one module pair is null or one benchmark is incompatible; diagnose measurement validity, task dependence, noise, power, and alternatives without manufacturing positive results.
- Keep NIL-CCEA isolated from all other repositories.

## Acceptance gates

- G0: primary-source literature audit complete and closest prior art compared. PASS.
- G1: benchmark/task/reset/scoring/trajectory and module-replacement compatibility documented. PASS at source level.
- G2: module contracts, variants, primary endpoint, statistical protocol, and cost rules frozen. NEEDS_REVISION pending price verification and review.
- G3: mock and tau2-class no-API smoke tests pass. PASS for no-API scope.
- G4: formal factorial pilot run after independent review.
- G5: fair-budget evolutionary comparison against independent and non-linkage baselines.

## Required handoff report

Report exact repository, branch, start/end SHA, changed files, primary-source URLs, environment evidence, test commands/results, API usage/cost, gate status, unresolved risks, and the next concrete experiment. Clearly label completed, implemented-but-unvalidated, planned, and hypothesized work.
