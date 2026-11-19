# Research Charter

## 1. Working title

**Noise-aware Interaction Linkage Cooperative Co-evolution for Modular LLM Agents (NIL-CCEA)**

This is a working title. It is not a novelty claim and may change after the literature audit.

## 2. Problem statement

A modular LLM Agent can be represented as a composition of replaceable components:

\[
A(\mathbf{x}) = \operatorname{Compose}(x_1,x_2,\ldots,x_m),
\]

where each decision variable \(x_i\) selects an implementation or configuration for one module slot (for example Planner, Selector, Caller, or Synthesizer).

Optimizing each module independently assumes that the effect of changing one module is approximately separable from the effects of other modules. That assumption may fail: the value of a Planner variant may depend on which Selector or Caller is paired with it.

The research question is:

> Can an evolutionary optimizer estimate these non-additive module interactions reliably under noisy Agent execution, learn a useful linkage structure, and use it to improve search under a fixed total evaluation budget?

## 3. Scope

### Included in the first study

- Four replaceable module slots, subject to environment compatibility.
- Two frozen variants per slot for an initial \(2^4\) factorial pilot.
- Pairwise interaction estimation, with task and execution noise explicitly represented.
- Signed interaction relationships: synergistic and antagonistic/non-additive.
- A dynamic linkage model that can later guide group-wise variation.
- Fair-budget comparisons with independent and non-linkage search baselines.

### Excluded from the first study

- Base-model fine-tuning or parameter-space evolution.
- Unconstrained automatic rewriting of the entire Agent.
- Claims about universal Agent self-improvement.
- Simultaneous optimization of every possible Agent component.
- A large-scale benchmark sweep before the measurement protocol is validated.

## 4. Formal interaction definition

For module slots \(i\) and \(j\), consider two alternatives per slot in the pilot. Let \(z\) denote a fixed configuration of all other module slots, and let \(\mu(a,b,z)\) be the expected primary task score under the corresponding configuration.

The difference-in-differences interaction contrast is:

\[
I_{ij}(z)=\mu(1,1,z)-\mu(1,0,z)-\mu(0,1,z)+\mu(0,0,z).
\]

For a four-slot full-factorial pilot, average this contrast over the configurations of the other slots:

\[
I_{ij}=\frac{1}{2^{m-2}}\sum_{z\in\{0,1\}^{m-2}} I_{ij}(z), \qquad m=4.
\]

This is a pairwise factorial interaction contrast, not a proof that all higher-order interactions are absent. Three-way or higher-order effects may be explored if the pilot indicates that pairwise structure is inadequate.

## 5. Noise-aware estimation

For each task instance and matched environment seed, evaluate the relevant configurations under the same frozen environment and model settings. Define the per-task contrast:

\[
d_{ij,t,s}(z)=r_{11,t,s}(z)-r_{10,t,s}(z)-r_{01,t,s}(z)+r_{00,t,s}(z).
\]

The primary estimate aggregates paired contrasts across task instances and seeds. Uncertainty should be estimated by resampling at the task-instance level (not by pretending every repeated episode is independent). The confirmatory analysis should report:

- effect estimate and confidence interval;
- practical effect threshold \(\delta\), specified before confirmatory analysis;
- task-family-specific estimates where sample size permits;
- multiplicity handling for the set of module-pair tests;
- sensitivity to execution stochasticity and missing/failed calls.

A same-seed label does not guarantee identical LLM randomness. Record provider/model version, decoding parameters, environment seed, request identifiers where safe, and all retries. Use deterministic decoding where available, but do not assume full determinism.

## 6. Linkage representation

Represent module slots as vertices in a signed weighted graph:

\[
G=(V,E,W,S),
\]

where vertices are module slots, edge weights encode estimated interaction magnitude, and edge signs distinguish positive from negative interaction.

An edge is considered actionable only when its uncertainty and practical magnitude meet pre-registered criteria. Uncertain edges should remain uncertain and may trigger additional measurement; they must not automatically be interpreted as independence.

The graph may be conditioned on task family if there is enough data. Avoid assuming that one global graph describes every task distribution.

## 7. Evolutionary use of linkage

The proposed search policy is:

- weak or unsupported interaction: allow independent module-level variation;
- positive interaction: test joint variation/crossover that preserves or explores useful combinations;
- negative interaction: use compatibility-aware joint search rather than assuming independent optimization;
- uncertain interaction: allocate a limited, explicit measurement budget before committing to a grouping decision.

A naive connected-components grouping can create one giant group. The implementation should compare at least one bounded or hierarchical grouping strategy (for example linkage-tree/overlapping groups) against a simple graph baseline.

## 8. Primary and secondary outcomes

- **Primary:** task success rate or another benchmark-native primary score, selected before experiments.
- **Secondary:** tool-call validity, constraint violations, token/API cost, latency, and execution length.

Do not combine these into an arbitrary scalar after seeing results. If a scalar utility is needed for selection, define and justify it before confirmatory runs; otherwise use constrained or multi-objective selection and report each metric.

## 9. Falsifiable hypotheses

- **H1:** some module pairs have non-negligible, reproducible interaction effects in the selected environment.
- **H2:** interaction structures vary across task families or operating contexts.
- **H3:** linkage-aware cooperative evolution improves final quality or sample efficiency under an equal total evaluation budget.

H1 can be false in a chosen environment. That would motivate inspecting module choice, task dependency, measurement power, and task diversity—not fabricating a positive effect. H3 must be tested against strong, fair baselines.

## 10. Novelty standard

A contribution is not established by renaming differential grouping, cooperative coevolution, factorial testing, or Agent module search. The final novelty claim must identify the exact difference from the closest prior mechanisms, explain why the difference matters, and show through ablations and fair-budget experiments that it contributes measurable value.
