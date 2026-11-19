# Executor Handoff — NIL-CCEA

**Repository:** https://github.com/yujian777555/NIL-CCEA (public, default branch `main`).  
**Current task:** prepare and execute the measurement-first module-interaction pilot.  
**Do not:** implement the full evolutionary optimizer before the pilot protocol and environment are validated.

## Mission

Build a reproducible harness to test whether four modular Agent slots (Planner, Selector, Caller, Synthesizer), each with two frozen variants, exhibit measurable pairwise non-additive effects under a controlled task environment.

## Phase 0 — literature and environment audit

1. Verify primary-source bibliographic records and mechanisms for every item in `LITERATURE_LEDGER.md`.
2. Inspect candidate benchmarks and confirm independent replacement of the four module slots is possible.
3. Select one environment only after documenting licensing, reset semantics, task IDs, tool permissions, and compatibility.
4. Freeze the model/provider version, decoding parameters, tool environment, and module interface contracts.
5. If no suitable public benchmark supports the required controls, propose a small controlled environment and explain its external-validity limits.

## Phase 1 — runner and test harness

Implement:

- a declarative config for the 16 factorial configurations;
- frozen module variant identifiers and content hashes;
- task/seed pairing and environment reset;
- structured episode logs and raw trajectory references;
- retry/failure accounting;
- token/API cost accounting;
- deterministic cache keys;
- manifest generation with source commit and config hash;
- tests that verify every configuration differs only in intended module slots.

Start with a tiny smoke test (2 tasks × 1 seed × 16 configurations). Do not launch the planned pilot until smoke tests and an independent review pass.

## Phase 2 — factorial pilot

Planned target: 12 tasks × 2 environment seeds × 16 configurations = 384 episodes. This is a planning target and may be changed only before the pilot is frozen, with a documented cost/power rationale.

Compute all six pairwise module interaction contrasts. Average over contexts of the other module slots. Use task-clustered uncertainty estimates and pre-specified multiplicity handling. Keep weak and uncertain edges distinct.

## Phase 3 — report and handoff

Deliver:

- exact repository commit SHA and clean/dirty status;
- environment and model lock files;
- frozen module variant manifests;
- test results;
- run manifest and cost ledger;
- raw data location and checksums;
- analysis script and machine-readable outputs;
- concise report with estimates, confidence intervals, multiplicity handling, task-family stability, and limitations;
- updated `STATUS.md`, `RESEARCH_LOG.md`, and this handoff file.

## Engineering and research constraints

- Never commit API keys or credentials. Read secrets from environment variables or an approved secret manager.
- Do not silently retry, omit, or relabel failed episodes.
- Count every probe and retry in total cost.
- Do not change prompts, module code, task set, model version, or decoding parameters mid-run without creating a new protocol/config version.
- Do not claim exact reproduction of a paper unless its implementation and settings have been matched and documented.
- Keep raw trajectories immutable; summaries must be regenerable.
- No training/fine-tuning in this milestone.
- Do not stop the project merely because one pair has no interaction. Diagnose measurement power and task dependence, then report the evidence accurately.

## Acceptance checklist

- [ ] Primary-source literature audit complete
- [ ] Benchmark compatibility documented
- [ ] Module contracts frozen
- [ ] 16 configurations generated and hash-checked
- [ ] Smoke test passes
- [ ] Pairing/reset tests pass
- [ ] Cost/retry accounting tests pass
- [ ] Pilot run completed or a documented blocker identified
- [ ] All six pairwise interaction contrasts reproducible from raw data
- [ ] Independent review completed
- [ ] Repository status and next handoff updated
