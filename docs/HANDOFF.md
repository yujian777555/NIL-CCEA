# Executor Handoff — NIL-CCEA

**Repository:** https://github.com/yujian777555/NIL-CCEA (public, default branch main).  
**Current workstream:** Phase 0A — source audit complete, tau2 environment selected, mock runner implemented.
**Authoritative execution prompt:** [docs/EXECUTOR_PROMPT_PHASE0A.md](EXECUTOR_PROMPT_PHASE0A.md).  
**Current research state:** PRE-EXPERIMENT. No real benchmark episode, performance result, or novelty claim has been established.

## Mission

Establish whether measurable, reproducible non-additive interactions exist among independently replaceable LLM-Agent modules, then use reliable signed and uncertainty-aware linkage to guide cooperative evolutionary search. Evolutionary computation and module-interaction linkage are the method core. A fixed total evaluation budget is a fairness constraint, not the research contribution.

## Immediate actions

1. Implement the tau2 v1.0.1 `HalfDuplexAgent` adapter and validate four independently hashed modules under identical tools and policy.
2. Add static leakage checks, raw-file replay, and adapter construction tests.
3. Freeze task IDs, primary endpoint, practical threshold, Holm correction, missing-run and retry policy.
4. Estimate paid API cost and obtain approval before any real call.
5. Run one exploratory tau2 smoke, preserve all raw results, and review before the factorial pilot.

## Planned measurement design

The provisional design uses four binary module slots (2^4 = 16 configurations) and paired task/environment-seed evaluations. The existing target of 12 tasks × 2 seeds × 16 configurations = 384 episodes is a planning value, not an observed result or an immutable requirement. Reassess cost and statistical sensitivity before protocol freeze.

For each module pair, estimate a paired difference-in-differences interaction contrast averaged over the contexts of the other module slots. Use task-clustered uncertainty, pre-specified practical effect threshold and multiplicity handling. Do not interpret uncertain edges as independence.

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
- G2: module contracts, variants, primary endpoint, statistical protocol, and cost rules frozen. NEEDS_REVISION pending adapter and endpoint review.
- G3: mock smoke test and automated pairing/reset/failure/cost tests pass. PASS for the local mock scope.
- G4: formal factorial pilot run after independent review.
- G5: fair-budget evolutionary comparison against independent and non-linkage baselines.

## Required handoff report

Report exact repository, branch, start/end SHA, changed files, primary-source URLs, environment evidence, test commands/results, API usage/cost, gate status, unresolved risks, and the next concrete experiment. Clearly label completed, implemented-but-unvalidated, planned, and hypothesized work.
