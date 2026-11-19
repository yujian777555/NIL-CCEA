# Next Steps

## Immediate priority: prepare the measurement pilot

1. **Audit literature.** Verify primary sources for AgentSquare, EvoTool, AgentSpec, differential grouping/linkage-learning methods, and cooperative coevolution. Add exact bibliographic metadata and a mechanism-level comparison to `docs/LITERATURE_LEDGER.md`.
2. **Select environment.** Inspect candidate benchmarks (initial candidates: tau-bench and a suitable multi-turn/function-calling benchmark). Confirm that the selected environment supports replaceable Planner, Selector, Caller, and Synthesizer components. Do not assume compatibility from a benchmark name.
3. **Freeze module contracts.** Define input/output schemas, error behavior, tool permissions, and two candidate implementations per module slot. Keep interfaces identical across variants.
4. **Build the runner.** Support task/seed pairing, immutable configuration manifests, raw trajectory capture, retry accounting, and cost accounting.
5. **Validate the 16-cell factorial.** Run a tiny smoke test first, then the planned pilot only after the harness passes.
6. **Analyze interactions.** Estimate pairwise non-additivity, uncertainty, effect-size relevance, multiplicity, and stability by task family.
7. **Decide the algorithm design from evidence.** Only then implement linkage grouping and cooperative variation.

## Do not do yet

- Do not claim NIL-CCEA is novel or superior.
- Do not launch a large API experiment before confirming the runner and cost ledger.
- Do not train or fine-tune a base model in this first milestone.
- Do not select a benchmark solely because it appears in a related paper; verify its suitability for controlled module replacement.
- Do not silently drop failed episodes or retry them without recording the event and cost.
