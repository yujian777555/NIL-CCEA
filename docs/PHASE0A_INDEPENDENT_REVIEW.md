# Phase 0A Independent Code Review

**Review date:** 2026-11-19  
**Reviewed PR:** [#1](https://github.com/yujian777555/NIL-CCEA/pull/1)  
**Reviewed branch:** `phase0a-literature-environment-audit`  
**Reviewed HEAD:** `6bed028a4675a75928734b633bbfae49d6b98b14`  
**Review type:** read-only source review of the PR and the pinned tau2-bench v1.0.1 source. No repository code was changed during the review.

## Executive decision

Phase 0A has delivered useful research infrastructure: the primary-source literature audit, a source-backed tau2 environment choice, module-contract drafts, a local mock runner, and an interaction estimator. The reported 11 local tests are useful for the mock scope.

**Do not merge PR #1 or start a paid tau2 run yet.** The review found correctness gaps in the real tau2 adapter and the statistical estimator. These are repairable and do not invalidate the research direction. They must be fixed before G2/G3 can be accepted.

The PR is open and GitHub reports it mergeable, but the reviewed commit has no status checks recorded (status state `pending`, zero statuses) and no PR reviews. The reported local test result is therefore recorded as executor-reported, not independently reproduced by this review.

## Findings

### F0-1 — tau2 tool schemas are currently read from the wrong attributes

**Severity:** BLOCKER

In `src/nil_ccea/tau2_adapter.py`, `_tool_schema()` checks `tool.parameters` and `tool.schema`. The pinned tau2 v1.0.1 `Tool` implementation exposes the parameter model as `tool.params` and its provider-facing schema through `tool.openai_schema`; it does not expose the attributes the adapter currently reads.

Consequently, the adapter can pass an empty parameter schema to Planner/Selector/Caller even while the tool name is present. This invalidates the claimed real module-contract interface.

Primary-source evidence:
- [tau2 v1.0.1 Tool implementation](https://github.com/sierra-research/tau2-bench/blob/fc0055dc4e0a316c3f83133267fbd6faaa770992/src/tau2/environment/tool.py)
- [tau2 v1.0.1 agent developer guide](https://github.com/sierra-research/tau2-bench/blob/fc0055dc4e0a316c3f83133267fbd6faaa770992/src/tau2/agent/README.md)

**Required correction:** derive the schema from `tool.params.model_json_schema()` or `tool.openai_schema["function"]["parameters"]`; include the correct tool name and description; add tests using actual tau2 `Tool` objects. Assert required parameters are non-empty for a representative tool.

### F0-2 — the interaction estimator treats task-seed pairs as independent clusters

**Severity:** BLOCKER

In `src/nil_ccea/interaction.py`, `_cluster_key()` returns `(task_id, seed)`. The current bootstrap therefore resamples 24 task-seed units for the planned 12 tasks × 2 seeds.

The protocol states that the task instance is the cluster and that seeds/configurations within one task must not be treated as independent task instances. Two seeds from one canonical task are repeated measurements nested inside that task, not two independent task clusters.

**Required correction:**
1. Make the resampling cluster the canonical task instance (`task_id`, with version/binding revision included if IDs can be reused).
2. Preserve seed as a within-task repeated-measure dimension.
3. Compute a seed-level interaction contrast for each task, average the pre-specified seeds within that task, then bootstrap task IDs.
4. Report the number of unique tasks, complete tasks, incomplete tasks, and seeds per task separately.
5. Add a regression test proving that two seeds for one task produce one bootstrap cluster, not two.

### F0-3 — incomplete factorial contexts and failed episodes can be silently omitted

**Severity:** BLOCKER

The estimator currently filters to records with `status == "success"`, then averages whichever remaining-slot contexts happen to contain the four pairwise cells. It does not require all four contexts for a module pair, nor does it fail closed on duplicate or missing configuration cells.

This can silently change the estimand and create selection bias if failed or missing episodes are not evenly distributed. A task-seed cluster with one complete context can contribute as though it represented the full factorial average.

**Required correction:**
- Validate exactly one record for each task × seed × 16-configuration cell; reject duplicates.
- For each pair, require all four remaining-module contexts and all four `(0,0),(0,1),(1,0),(1,1)` cells in every seed used for the task-level contrast.
- Distinguish a genuine agent task failure (a valid benchmark outcome, scored according to the frozen benchmark endpoint, usually zero success) from an infrastructure/provider failure (missing observation after the frozen retry policy).
- Never silently convert an infrastructure failure to a task failure or drop only the failed cell.
- Freeze a complete-cluster policy before confirmatory runs. If a task cluster remains incomplete after infrastructure retries, report it explicitly and provide a pre-specified sensitivity/attrition analysis.
- Add tests for missing cells, duplicate cells, failed task outcomes, infrastructure failures, and incomplete task clusters.

### F0-4 — adapter does not enforce the selected tool or validate the proposal against tau2's schema

**Severity:** BLOCKER

The adapter calls `caller.propose()` on every turn, including turns where Selector has selected `respond` or `stop`. When Selector selects a tool, the adapter checks only that the proposal's tool name appears in the available tool-name set. It does not verify that the proposal tool equals `selection.tool_name`, and it does not validate arguments against the actual tau2 `Tool.params` model.

If a selected tool is unknown or the proposal is invalid, the current branch can fall through to Synthesizer and return a normal text response. That hides an invalid module decision instead of recording an explicit failure.

**Required correction:**
- Invoke Caller only when `selection.kind == "tool_call"`.
- Require `proposal.tool_name == selection.tool_name`.
- Validate arguments against the selected tau2 tool's `params` model before emitting a `ToolCall`.
- On invalid selection/proposal, emit a typed failure event and apply the frozen repair/retry policy; do not silently synthesize a success-like answer.
- Add tests for mismatched tool names, unknown tools, invalid/missing arguments, respond/stop branches, and valid calls.

### F0-5 — state-conditioned planning state is not persisted

**Severity:** MAJOR

`Tau2AgentState` contains `plan_state`, and the context passes a copy of it to Planner/Selector, but the adapter never updates `state.plan_state` after generating a plan or processing a tool result. The declared state-conditioned module mechanism therefore has no explicit persistent plan state.

**Required correction:** define the state transition contract and persist only public, agent-observable plan/progress state. Add a multi-turn test showing that the next module invocation receives the expected updated state. Do not store evaluator-only fields.

### F0-6 — no tests currently exercise the actual tau2 adapter

**Severity:** MAJOR

The 11 reported tests exercise the local mock contracts, runner, manifests, and mock interaction estimator. They do not import and instantiate the adapter against the pinned tau2 v1.0.1 package. The adapter remains explicitly unvalidated.

The pinned tau2 package requires Python `>=3.12,<3.14`, which is correctly identified in its official [pyproject.toml](https://github.com/sierra-research/tau2-bench/blob/fc0055dc4e0a316c3f83133267fbd6faaa770992/pyproject.toml).

**Required correction:** create a dedicated Python 3.12 or 3.13 environment, install tau2 from the exact pinned commit, and add no-API-key integration tests using fake deterministic modules and actual tau2 message/tool classes. Cover UserMessage, ToolMessage and MultiToolMessage input paths, state transitions, output types, tool schema extraction, and tool-call validation.

### F0-7 — task metadata defaults can silently remain unknown

**Severity:** MAJOR

The adapter constructor defaults `task_id`, `task_version`, and `task_family` to `"unknown"`. No factory/integration path currently demonstrates that the tau2 runner supplies these values for every episode.

**Required correction:** implement or document the actual agent factory/runner injection path. For experiment mode, fail closed if required task/version/family metadata is absent; do not write apparently valid manifests with unknown task metadata.

## Protocol items still open

The following items remain pre-freeze decisions in `docs/PILOT_DESIGN_R1.md`:

- exact canonical task IDs and task/binding versions;
- exact primary endpoint and reward component(s);
- practical interaction threshold `delta` and its substantive justification;
- inference method and Holm correction across six pairwise tests;
- infrastructure retry and missing-cluster policy;
- per-episode, per-smoke, and total pilot cost caps;
- sensitivity/power analysis using **task count as the number of independent clusters**.

The current 12 tasks × 2 seeds × 16 configurations is a planning target, not a frozen or demonstrated adequate sample. Two seeds do not turn 12 tasks into 24 independent clusters. If sensitivity analysis indicates inadequate precision, consider more canonical tasks before increasing repeated seeds.

## Gate decision after review

| Gate | Review decision | Reason |
|---|---|---|
| G0 Literature | PASS (as Phase 0A audit) | Primary-source audit and overlap caveats are recorded; this is not a proof of novelty |
| G1 Environment | PASS at source level only | tau2 API supports a custom HalfDuplexAgent; adapter not yet exercised |
| G2 Contracts/protocol | BLOCKED pending corrections | Tool schemas, state handling, task metadata, endpoint and missingness remain unresolved |
| G3 Smoke | PASS for local mock only; tau2 adapter NOT PASSED | Current tests do not exercise the real tau2 package |
| G4 Pilot | NOT STARTED | No real benchmark episode |
| G5 Search | NOT STARTED | No reliable empirical linkage evidence yet |

## Next action

Execute [Phase 0B adapter and estimator corrections](EXECUTOR_PROMPT_PHASE0B.md). Keep PR #1 open until the blockers are fixed and tested. Do not make a paid API call until the no-key integration suite passes, the protocol and cost cap are frozen, and the user explicitly approves the paid smoke.
