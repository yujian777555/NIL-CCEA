# NIL-CCEA Algorithm Specification v0.1

**State:** candidate specification; not yet implemented or validated.

## 1. Inputs

- A modular Agent with \(m\) replaceable module slots.
- A candidate set \(\mathcal{X}_i\) for each slot \(i\).
- A training task set \(T_{train}\), with task-family labels where available.
- A fixed total evaluation budget \(B\), counting all probes, optimization episodes, failed calls, and retries.
- A primary score and secondary metrics fixed before runs.

## 2. Population representation

An individual is a module configuration:

\[
\mathbf{x}=(x_1,x_2,\ldots,x_m), \quad x_i\in\mathcal{X}_i.
\]

Each module candidate must satisfy the same declared interface contract for its slot. Candidate provenance and version hashes are part of the individual genotype metadata.

## 3. Interaction estimation

For a selected parent/context configuration, create controlled alternatives for a pair of module slots. In the binary pilot, evaluate the four cells \((0,0),(1,0),(0,1),(1,1)\), holding all other slots fixed. For the full-factorial pilot, average pairwise contrasts across all contexts of the remaining slots.

Use matched task instances and environment seeds. Cache results by a key containing task version, environment seed, module hashes, model/provider version, decoding settings, and runner version.

Estimate uncertainty with task-clustered bootstrap or a pre-specified hierarchical model. Correct for testing multiple module pairs. Use a pre-registered practical threshold \(\delta\), not a threshold selected after inspecting results.

## 4. Linkage graph update

Create a signed weighted graph over module slots. Edge state should distinguish:

- `POSITIVE`: reliably positive interaction above the practical threshold;
- `NEGATIVE`: reliably negative interaction below the negative threshold;
- `WEAK`: evidence supports a practically negligible interaction;
- `UNCERTAIN`: interval overlaps the practical-equivalence region or evidence is insufficient.

Do not collapse `UNCERTAIN` into `WEAK`.

For task-conditioned learning, maintain separate estimates by task family only when sample size and task labels justify it. Otherwise use a global graph and report that limitation.

## 5. Group formation

The graph is converted into linkage groups. Candidate approaches to compare:

1. thresholded connected components (simple reference);
2. bounded-size graph clustering;
3. hierarchical/overlapping linkage groups.

The selected approach must prevent a single noisy edge from merging every module into one group. Grouping must be deterministic given the frozen graph and configuration.

## 6. Variation policy

- `WEAK`: single-slot mutation/crossover is allowed.
- `POSITIVE`: group-wise variation explores combinations while preserving useful co-adapted blocks.
- `NEGATIVE`: use compatibility-aware joint variation and explicitly test alternative combinations; do not interpret negative interaction as “no linkage.”
- `UNCERTAIN`: either preserve the current configuration or run a bounded diagnostic probe, with its cost charged to \(B\).

The first implementation should use simple, auditable operators. LLM-generated operators are out of scope until the linkage mechanism itself is tested.

## 7. Selection

Use the same selection objective and constraints across NIL-CCEA and comparison methods. Preserve genotype/behavioral diversity if needed, but do not add a diversity mechanism only to NIL-CCEA unless the corresponding baseline is budget- and design-matched.

## 8. Dynamic refresh

Refresh the linkage graph at a pre-specified interval or after a pre-defined task-distribution drift signal. Do not recompute it after every episode by default. The refresh schedule and diagnostic budget are experimental factors.

## 9. Pseudocode

```text
Input: module candidate sets X, task set T, total budget B
Initialize population P and evaluation cache C
Evaluate initial population; charge every call to B

while budget remains:
    choose parent/context configurations from P
    select module-pair/context probes using the current probe policy
    evaluate paired factorial cells on matched tasks/seeds
    estimate signed interaction effects and uncertainty
    update the linkage graph G without converting uncertainty to independence
    derive bounded/hierarchical linkage groups from G
    generate offsprings using independent or group-aware operators
    evaluate offsprings on the shared evaluation protocol
    update P using the common selection rule
    refresh G only when the frozen refresh condition is met

Return: best validated configurations,  population/archive, linkage history,
        complete cost ledger, raw trajectories, and run manifests
```

## 10. Required algorithmic comparisons

At minimum:

- static Agent;
- random module mutation;
- independent cooperative coevolution;
- module recombination/search baseline;
- trajectory-attribution/directed-mutation baseline where reproducible;
- NIL-CCEA.

If a published method cannot be reproduced exactly, label the implementation as a paper-inspired reimplementation and document all deviations. Never label it an exact reproduction without evidence.

## 11. Open design decisions

- How to handle multi-allelic module candidates beyond the binary pilot.
- Whether the final grouping should use linkage trees, bounded clustering, or overlapping groups.
- Whether pairwise interactions suffice or higher-order interactions are necessary.
- How to select probe pairs without introducing selection bias.
- How to handle non-stationary task distributions and module drift.
- Whether primary optimization should be single-objective, constrained, or multi-objective.
