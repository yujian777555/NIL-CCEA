> **Superseded planning draft (2026-11-20):** The smoke row below originally used 2 tasks × 1 seed = 32 episodes. The current Phase 0B candidate uses 2 tasks × 2 seeds × 16 configurations = 64 episodes. Use [PHASE0B_PROTOCOL_FREEZE.md](PHASE0B_PROTOCOL_FREEZE.md) as the current candidate protocol. This document is retained for historical design context.

# Pilot Experiment Protocol: 2^4 Module Factorial

**State:** Phase 0B corrected protocol candidate; no real runs have been executed.

## 1. Purpose

Test whether the chosen modular Agent environment exposes reproducible pairwise module interactions that can be measured with a paired factorial design. This pilot does not establish that NIL-CCEA outperforms an evolutionary baseline.

## 2. Environment selection gate

Candidate environments may include tau-bench or a suitable multi-turn/function-calling benchmark. Before selection, the executor must verify:

- the benchmark license and access conditions;
- stable task identifiers and versioning;
- whether Planner, Selector, Caller, and Synthesizer can be independently replaced;
- whether all module variants can share identical tool permissions and interfaces;
- whether task state and environment seeds can be reset;
- whether the runner exposes enough raw trajectory data for auditing.

If a benchmark does not support controlled module replacement, do not force it. Select or construct a suitable controlled environment and document the trade-off.

## 3. Factorial design

Four module slots, two frozen variants per slot:

- Planner: P0 / P1
- Selector: S0 / S1
- Caller: C0 / C1
- Synthesizer: Y0 / Y1

Full factorial size:

\[
2^4=16\text{ configurations}.
\]

The same task instances and environment seeds must be used across all 16 configurations. Candidate versions, prompts, code, interfaces, model version, decoding settings, and tool permissions are frozen before the pilot.

## 4. Planned sample sizes

| Stage | Tasks | Environment seeds per task | Configurations | Planned episodes |
|---|---:|---:|---:|---:|
| Smoke test | 2 | 1 | 16 | 32 |
| Pilot | 12 | 2 | 16 | 384 |
| Independent confirmation (only after pilot review) | 40 | 3 | 16 | 1,920 |

These are planning targets, not observed results. A power/sensitivity analysis and runner-cost check may revise them before the pilot is frozen. Do not silently change sample sizes after observing confirmatory outcomes.

## 5. Pairing and randomness

- Pair by exact task instance and environment initial-state seed.
- Use the same model/provider version and decoding parameters for all configurations.
- Use deterministic decoding where available, while recording that it does not guarantee full determinism.
- If a run fails, preserve the failure record and apply only the pre-registered retry policy.
- Count retries and failed API calls in the cost ledger.
- Do not treat repeated runs on the same task as independent task samples.

## 6. Outcomes

The frozen candidate primary endpoint is tau2 `EvaluationType.ENV` environment reward, covering DB and environment assertions. Full task reward, communication, and NL assertion results are secondary diagnostics. Secondary outcomes may include tool-call validity, constraint violations, token/API cost, latency, and execution steps.

Do not create a post-hoc weighted score to favor a method. If optimization requires a scalar utility, define it and its constraints before confirmatory runs.

## 7. Statistical analysis

For each module pair, estimate the difference-in-differences contrast averaged over the other two module slots. Report:

- mean interaction effect;
- task-clustered confidence interval;
- per-task-family estimates where supportable;
- practical threshold \(\delta\), fixed before confirmatory analysis;
- multiplicity correction across module-pair tests;
- sensitivity to missing runs, retries, and task composition.

The preferred uncertainty method is a bootstrap that resamples the 12 task instances as clusters. The two seeds remain repeated measurements within each task. A hierarchical model may be added as a sensitivity analysis, not substituted after seeing which method gives a preferred result.

## 8. Fair-budget rule for the later search comparison

All methods receive the same total Agent-execution budget. NIL-CCEA must charge interaction probes, diagnostic evaluations, failed calls, and retries to its budget. Baselines must use the same task set, model, environment, and endpoint definitions.

Report both final quality and quality-versus-total-evaluations curves. Do not compare NIL-CCEA's best-of-many probes against a baseline's single evaluation without accounting for the difference.

## 9. Data and manifest requirements

Each episode record must include at least:

- `run_id`, `task_id`, `task_version`, `task_family`;
- `configuration_id` and hashes for all four module variants;
- environment seed and replicate index;
- model/provider/version and decoding parameters;
- runner commit SHA and config hash;
- start/end timestamps and status;
- primary and secondary outcomes;
- tool-call trace reference;
- token/API cost and retry/failure accounting.

Store raw trajectories separately from derived summaries. Never commit credentials or sensitive records.

## 10. Acceptance criteria

The pilot is acceptable only if:

1. all 16 configurations pass interface and smoke tests;
2. configuration hashes and run manifests are complete;
3. task/seed pairing is verified by automated checks;
4. missing and failed episodes are visible and accounted for;
5. all interaction estimates can be recomputed from raw episode records;
6. the analysis reports uncertainty and multiplicity handling;
7. the report clearly distinguishes observed results from hypotheses.

## 11. Interpretation

- Reproducible non-additive effects support continued linkage-algorithm development.
- Weak or unstable effects trigger diagnosis of task choice, module variants, execution noise, and measurement power.
- No positive interaction in this pilot does not prove that all Agent modules are separable.
- A detected interaction does not by itself prove that linkage-aware evolution improves search; that requires the later fair-budget comparison.
