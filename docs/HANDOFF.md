# Executor Handoff — NIL-CCEA

**Repository:** https://github.com/yujian777555/NIL-CCEA (public, default branch main).  
**Current workstream:** Phase 0A — primary-source literature audit and benchmark/environment compatibility audit.  
**Authoritative execution prompt:** [docs/EXECUTOR_PROMPT_PHASE0A.md](EXECUTOR_PROMPT_PHASE0A.md).  
**Current research state:** PRE-EXPERIMENT. No benchmark experiment or performance result has been established.

## Mission

Establish whether measurable, reproducible non-additive interactions exist among independently replaceable LLM-Agent modules, then use reliable signed and uncertainty-aware linkage to guide cooperative evolutionary search. Evolutionary computation and module-interaction linkage are the method core. A fixed total evaluation budget is a fairness constraint, not the research contribution.

## Immediate actions

1. Verify the current remote HEAD and worktree; create a dedicated Phase 0A branch.
2. Audit primary sources for the closest Agent-module evolution, interaction detection/linkage learning, noisy black-box optimization, and cooperative co-evolution work.
3. In parallel, inspect tau-bench and other suitable tool-use environments using official source code and documentation.
4. Verify whether the provisional Planner, Selector, Caller, and Synthesizer slots can truly be replaced independently under identical permissions and interfaces.
5. If the four-slot design is incompatible, propose and document an evidence-backed alternative before running experiments.
6. Define module contracts and mechanism-distinct variants only after the environment decision.
7. Build the smallest auditable runner, validate it with mock tests, and obtain independent review before the formal factorial pilot.

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

- G0: primary-source literature audit complete and closest prior art compared.
- G1: benchmark/task/reset/scoring/trajectory and module-replacement compatibility documented.
- G2: module contracts, variants, primary endpoint, statistical protocol, and cost rules frozen.
- G3: mock smoke test and automated pairing/reset/failure/cost tests pass.
- G4: formal factorial pilot run after independent review.
- G5: fair-budget evolutionary comparison against independent and non-linkage baselines.

## Required handoff report

Report exact repository, branch, start/end SHA, changed files, primary-source URLs, environment evidence, test commands/results, API usage/cost, gate status, unresolved risks, and the next concrete experiment. Clearly label completed, implemented-but-unvalidated, planned, and hypothesized work.
