# NIL-CCEA

**Noise-aware Interaction Linkage Cooperative Co-evolution for LLM Agents**

> Research workspace for studying whether statistically reliable interactions among modular LLM-Agent components can guide linkage learning and cooperative evolutionary search.

## Status

- **Project stage:** PRE-EXPERIMENT
- **Algorithm label:** NIL-CCEA v0.1 (working name; not a validated contribution)
- **Current objective:** establish a reproducible module-interaction pilot before implementing the full evolutionary algorithm
- **Evidence status:** no experimental performance claim has been established
- **Remote repository:** https://github.com/yujian777555/NIL-CCEA (public)

## Research question

Can an evolutionary optimizer improve its search over modular LLM Agents by estimating module interactions under execution noise, learning a dynamic linkage structure, and using that structure to choose independent or cooperative variation operators?

The proposed research is not simply “apply a genetic algorithm to Agent modules.” The intended algorithmic contribution is the closed loop:

1. estimate module interaction effects with paired factorial interventions;
2. represent reliable interactions in a signed, potentially task-conditioned linkage graph;
3. derive groups or linkage structures from that graph;
4. use linkage-aware mutation/crossover and compatibility search;
5. refresh the linkage model as the population or task distribution changes.

All five steps remain research hypotheses until independently tested.

## Initial research hypotheses

- **H1 — measurable interaction:** at least some Agent module pairs exhibit reproducible non-additive effects on task performance.
- **H2 — task dependence:** interaction strengths or signs can differ across task families or operating conditions.
- **H3 — search utility:** using a reliable linkage model improves search quality or sample efficiency over fair-budget independent and non-linkage baselines.

A null result for one module pair is not a project stop condition. It is evidence to inspect task choice, module variants, effect size, measurement power, and the search mechanism. Claims must remain bounded by the evidence.

## Repository map

```text
.
├── README.md
├── STATUS.md
├── NEXT_STEPS.md
├── docs/
│   ├── RESEARCH_CHARTER.md
│   ├── ALGORITHM_SPEC_v0.1.md
│   ├── EXPERIMENT_PROTOCOL_PILOT.md
│   ├── LITERATURE_LEDGER.md
│   ├── RESEARCH_LOG.md
│   └── HANDOFF.md
├── experiments/
│   └── README.md
├── src/nil_ccea/
│   └── README.md
├── tests/
│   └── README.md
└── scripts/
    └── PUBLISH_TO_GITHUB.md
```

## Working rules

1. Do not claim novelty based on a name or a superficial difference. Compare mechanisms against the closest prior work.
2. Do not claim algorithmic improvement until fair-budget experiments and independent checks support it.
3. Count interaction probes, failed calls, retries, and optimization evaluations in the total experimental cost.
4. Freeze task sets, module variants, model versions, seeds, and evaluation rules before confirmatory runs.
5. Preserve raw results; derived summaries must be reproducible from raw logs.
6. Every result must record the source commit, config hash, task/version identifiers, model/provider version, decoding settings, seeds, and run manifest.
7. Never commit API keys, credentials, personal data, or unredacted provider logs.
8. Keep literature claims, hypotheses, implementation status, and empirical findings explicitly separate.
9. Update `STATUS.md`, `RESEARCH_LOG.md`, and `HANDOFF.md` after each material milestone.

## First milestone

Complete the literature audit and a small, reproducible factorial pilot with four frozen module slots and two variants per slot. The pilot is designed to test interaction measurement, not to claim that NIL-CCEA already outperforms existing methods.

See:

- [Research charter](docs/RESEARCH_CHARTER.md)
- [Algorithm specification v0.1](docs/ALGORITHM_SPEC_v0.1.md)
- [Pilot protocol](docs/EXPERIMENT_PROTOCOL_PILOT.md)
- [Literature ledger](docs/LITERATURE_LEDGER.md)
- [Execution handoff](docs/HANDOFF.md)

## Citation and provenance policy

The literature ledger currently contains candidate leads, not a completed bibliography. Verify each title, authors, venue/version, DOI or arXiv identifier, and exact mechanism from the primary source before using it in a paper or treating it as a definitive baseline.
