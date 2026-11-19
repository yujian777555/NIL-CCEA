# Literature Ledger

**Important:** this is an initial reading queue, not a verified bibliography. The names below are candidate leads carried into the project from the preliminary discussion. Before citing any item, verify the exact title, author list, publication venue/status, version, DOI/arXiv identifier, and the mechanism actually implemented from the primary source.

| Candidate | Topic to audit | Questions for the review | Audit state |
|---|---|---|---|
| AgentSquare | Modular LLM-Agent search and module recombination | What is the exact representation, search operator, predictor, and interaction treatment? | TODO |
| EvoTool | Tool-use policy evolution and trajectory attribution | How are module blame scores estimated? Are multiple modules jointly modified? What are the baselines and costs? | TODO |
| AgentSpec | Controlled composition of Agent modules | Which module combinations are tested? How are interaction effects measured? Is the work peer-reviewed or a preprint? | TODO |
| Differential Grouping / DG2 | Black-box variable interaction detection | Exact interaction test, assumptions, query complexity, noise sensitivity, and thresholding | TODO |
| Recursive Differential Grouping (RDG) | Recursive interaction detection | What is gained over pairwise testing and how are overlapping groups handled? | TODO |
| Linkage Measurement Minimization (LMM) | Linkage learning under black-box optimization | What objective is optimized and how is noise treated? | TODO |
| Cooperative coevolution | Decomposition and subpopulation optimization | How are subcomponents grouped, optimized, and periodically regrouped? | TODO |
| AgenticEvolve | Persistent Agent-driven evolutionary program search | Does it already use quality-diversity archives, experiment design, or linkage information? | TODO |
| CoPES / Agent post-training evolution | Cooperative evolution in model parameter/subspace search | Is the search over model parameters, Agent modules, or both? | TODO |
| Other closest 2025–2026 work | Dynamic Agent architecture and team evolution | Search for direct overlap with signed/task-conditioned module linkage and linkage-aware operators | TODO |

## Required comparison matrix

For every verified paper, record:

1. problem and target object (prompt, module, workflow, team, model weights, or environment);
2. genotype/search-space representation;
3. evolutionary algorithm and operators;
4. how interactions or dependencies are detected (if at all);
5. how noisy evaluation is handled;
6. how evaluation budget is counted;
7. task/benchmark and model details;
8. baselines, ablations, statistical tests;
9. limitations acknowledged by the authors;
10. exact difference from NIL-CCEA.

## Novelty guardrail

Do not state that a method “does not consider module interaction” until its full paper, appendices, code, and relevant follow-up work have been checked. Distinguish “not explicitly represented as a learned linkage graph” from “not considered at all.”
