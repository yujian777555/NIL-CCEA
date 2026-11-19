# Phase 0B 协议冻结记录

**状态**：冻结候选，真实 API 仍未启动。
**环境**：tau2-bench v1.0.1，commit `fc0055dc4e0a316c3f83133267fbd6faaa770992`。
**独立统计 cluster**：task。两个 seed 是同一 task 内的重复测量。

## 1. 固定 task IDs

| task family | split | task IDs |
|---|---|---|
| retail | test | `5, 9, 12, 17, 18, 26` |
| airline | test | `2, 6, 8, 13, 16, 18` |

总 task 数为 12。每个 task 使用 seed `0` 和 `1`，每个 seed 必须完成唯一完整的 16 配置。

## 2. 主要终点

主终点固定为 tau2 `EvaluationType.ENV` 的 `environment_reward`，包括 DB 和 environment assertion 组件。该选择避免把通信或自然语言 judge 噪声混入主交互估计。

次要记录包括完整 task reward、communication reward、NL assertion reward、tool-call schema validity、步骤数、失败类型、token 和实际 provider cost。次要指标不合成为新的主终点。

## 3. 交互估计规则

- 16 配置必须各出现一次，重复配置直接拒绝。
- 每个 task 的两个 seed 必须都存在。
- 每个 module pair 必须有四个剩余模块上下文，每个上下文包含四个 cell。
- 先对每个 task-seed-context 计算 DiD，再对四个 context 平均，随后对两个 seed 平均成一个 task-level contrast。
- bootstrap 只重采样 12 个 task。
- `success` 和 `agent_failed` 是有效观测，后者的主终点为 0。
- `infra_failed` 不得静默丢弃或插值。一次 retry 后仍失败时，该 task/configuration 使 factorial 记录不完整，确认性分析拒绝运行。
- 六组 pairwise interaction 统一使用 Holm step-down correction，alpha 固定为 0.05。

## 4. 变体和运行设置

- Planner、Selector、Caller、Synthesizer 各两个变体，共 16 配置。
- Agent model：`openai/gpt-4.1-2025-04-14`。
- User simulator：`openai/gpt-4.1-2025-04-14`。
- Primary evaluator：`ENV`，不调用额外 judge。
- Temperature：0.0。
- `max_steps`：30。
- Agent、user、tool permissions、policy、task version、binding revision 和 decoding 参数全部固定。
- 单个 provider request 最多一次基础设施 retry。Agent task failure 不重试。

## 5. 样本量与功效敏感性

12 个 task 是当前冻结候选值。未观察真实方差前，不把 24 个 task-seed 当成独立样本。

下表使用保守的 Holm/Bonferroni 首轮 alpha 近似和 80% power，只做敏感性分析。它不代表真实 power 已经确认。

| task-level contrast SD 假设 | 12 tasks 下的近似 MDE | 识别 delta=0.10 所需近似 tasks |
|---:|---:|---:|
| 0.10 | 0.10 | 13 |
| 0.20 | 0.20 | 49 |
| 0.30 | 0.30 | 109 |
| 0.40 | 0.40 | 194 |

如果 pilot 前的探索性方差估计接近 0.20 或更高，优先增加 task 数量。增加 seed 不能替代 task-level cluster 数的增加。

## 6. 成本上限与调用上界

### 调用上界

- 每 episode 最多 30 个 agent request 和 30 个 user-simulator request，共 60 个正常 provider requests。
- 每 request 最多一次基础设施 retry，retry 上界为 120 个 provider requests per episode。
- 两 task exploratory smoke 使用 2 tasks × 2 seeds × 16 configurations = 64 episodes，正常上界 3,840 requests，含 retry 上界 7,680 requests。
- 384-episode pilot 正常上界 23,040 requests，含 retry 上界 46,080 requests。
- 主终点评估使用 ENV，不计额外 LLM judge request。

### Token 和美元估算

为形成可审计上界，先使用以下声明式 token cap。实际 provider usage 必须由 tau2/LiteLLM response usage 覆盖。

- 每 request 上界：2,000 input tokens + 512 output tokens。
- 费率配置：input 2 USD/M tokens，output 8 USD/M tokens。该费率仅是待验证的预算 profile，不能当作当前公开价格事实。
- 单 request 上界：`2000/1e6*2 + 512/1e6*8 = 0.008096 USD`。
- 单 episode 正常上界：约 `0.486 USD`。
- 64-episode exploratory smoke 正常上界：约 `31.09 USD`，含一次 retry 上界约 `62.18 USD`。
- 384-episode pilot 正常上界：约 `186.53 USD`，含一次 retry 上界约 `373.06 USD`。

### 停止条件

- exploratory smoke hard cap：`80 USD`；
- formal pilot hard cap：`400 USD`；
- 任意单 episode 触及 120 provider requests、出现两次连续基础设施失败、或配置 manifest 不一致时，停止该 episode 并保留失败记录；
- 达到 hard cap 前不启动下一 episode。达到 hard cap 后运行状态为 `BUDGET_EXHAUSTED`，不自动追加调用。
- 真实调用前必须验证 provider 费率和模型可用性，并得到用户明确批准。

对应机器可读配置见 `experiments/pilot_factorial/cost_profile.json`。费率字段保持 `requires_provider_verification` 状态，当前不能视为已支付或已验证成本。

## 7. 缺失数据和报告规则

- Agent task failure 计为 primary endpoint 0，并保留完整轨迹。
- Infrastructure failure 保留原始错误、retry、request metadata 和 partial trajectory。retry 后仍失败时，confirmation run 标记 `INCOMPLETE_FACTORIAL`，不计算交互显著性。
- 所有 task-level contrasts、seed-level contrasts、context-level cells 和 Holm 调整结果均可从 `episodes.jsonl` 复算。

## 8. Provider pricing verification and lifecycle (2026-11-20)

The active provider price profile has been checked against the official OpenAI GPT-4.1 model page:
- Standard input: USD 2.00 / 1M tokens
- Cached input: USD 0.50 / 1M tokens
- Standard output: USD 8.00 / 1M tokens

The budget upper bound intentionally uses uncached input pricing. The arithmetic in `experiments/pilot_factorial/cost_profile.json` is unchanged and verified.

**Lifecycle warning:** `gpt-4.1-2025-04-14` is marked Deprecated. OpenAI lists 2027-01-14 as its shutdown date and recommends `gpt-6-luna`. The model decision is unresolved; do not silently switch models and do not make a paid request until the user explicitly chooses. Do not mix model versions within a factorial dataset.

Official sources:
- https://developers.openai.com/api/docs/models/gpt-4.1
- https://developers.openai.com/api/docs/deprecations
- https://developers.openai.com/api/docs/models/gpt-6-luna

## 9. Remaining pre-smoke consistency checks

- The intended practical-delta candidate is `0.05` (matching the estimator default and Phase 0B completion report). The sensitivity table in Section 5 is explicitly calculated for `delta=0.10`; it does not establish precision/power for `delta=0.05`. Recompute the table before the confirmatory pilot.
- The 64-episode exploratory smoke (2 tasks × 2 seeds × 16 configurations) supersedes the earlier 32-episode row in `docs/EXPERIMENT_PROTOCOL_PILOT.md`.
- The current adapter still calls Caller before branching on `selection.kind`; Phase 0C must ensure Caller is invoked only for `tool_call`.
- Current no-API tests establish tau2 class/Orchestrator compatibility, not a paid-run implementation. Provider-backed module classes and a real tau2 factorial runner are still required.

