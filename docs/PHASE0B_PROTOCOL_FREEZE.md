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
- Provider/model for Agent and User Simulator: DeepSeek API `deepseek-flash` (currently served as DeepSeek-V4.1-Flash-1017 as of 2026-11-20). All four module slots use the same model alias.
- API: OpenAI-compatible Chat Completions at `https://api.deepseek.com`.
- Thinking/CoT disabled: `thinking={"type":"disabled"}` and `reasoning_effort="none"`.
- Structured output: JSON mode (`response_format={"type":"json_object"}`) for JSON content responses; Caller uses native function Tool Calls with local JSON/Pydantic validation.
- Network: direct DeepSeek connection; dedicated HTTP client uses `trust_env=false` so system proxy environment variables are ignored.
- Record request model alias, response `model`, `system_fingerprint`, prompt hash, decoding settings, request ID, and token usage for every request. The alias is mutable; detect and stop on backend model drift.
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

- 每次 Agent 响应最多调用 Planner、Selector，以及 Caller/Synthesizer 之一，即最多 3 个模块请求。
- 保守按每 episode 最多 30 次 Agent 响应和 30 次 User Simulator 响应计算：90 个 Agent 模块请求 + 30 个 User 请求 = 120 个正常逻辑请求。
- 每个逻辑请求最多预留一次安全基础设施 retry，因此每 episode 最多预留 240 个物理请求尝试。
- 两 task exploratory smoke 使用 2 tasks × 2 seeds × 16 configurations = 64 episodes，正常上界 7,680 个逻辑请求，含 retry 上界 15,360 个物理请求尝试。
- 384-episode pilot 正常上界 46,080 个逻辑请求，含 retry 上界 92,160 个物理请求尝试。
- 主终点评估使用 ENV，不计额外 LLM judge request。

### Token 和美元估算

Token 上界仍为每 request 2,000 input + 512 output。DeepSeek 官方价格分峰谷时段；为形成不依赖运行时段的保守预算，使用**高峰、输入缓存未命中**费率：

- 高峰 input cache miss：0.30 USD / 1M tokens；cache hit：0.006 USD / 1M tokens。
- 高峰 output：1.20 USD / 1M tokens。
- 峰时段：UTC 周一至周五 01:00–04:00、06:00–10:00（中国法定节假日除外）；其他时段费率减半。
- 单 request 保守上界：`2000/1e6*0.30 + 512/1e6*1.20 = 0.0012144 USD`。
- 单 episode 正常上界：`120 * 0.0012144 = 0.145728 USD`。
- 64-episode exploratory smoke 正常上界：`9.326592 USD`；所有逻辑 request 均重试一次的极端上界：`18.653184 USD`。
- 384-episode pilot 正常上界：`55.959552 USD`；所有逻辑 request 均重试一次的极端上界：`111.919104 USD`。

以上使用高峰 cache-miss 费率，不依赖缓存折扣。实际成本必须由 DeepSeek 返回的 token usage 和实际账单核对。价格可能变化，付费执行前必须再次核验官方价格页面。

### 停止条件

- exploratory smoke hard cap：`80 USD`；
- formal pilot hard cap：`400 USD`；
- 任意单 episode 触及 240 个物理请求预留、出现两次连续基础设施失败、或配置 manifest 不一致时，停止该 episode 并保留失败记录；
- 达到 hard cap 前不启动下一 episode。达到 hard cap 后运行状态为 `BUDGET_EXHAUSTED`，不自动追加调用。
- 真实调用前必须验证 provider 费率和模型可用性，并得到用户明确批准。

对应机器可读配置见 `experiments/pilot_factorial/cost_profile.json`。DeepSeek 费率已按官方价格页核验；付费执行前仍须重新核价。当前没有真实 API 调用或实际扣费。

## 7. 缺失数据和报告规则

- Agent task failure 计为 primary endpoint 0，并保留完整轨迹。
- Infrastructure failure 保留原始错误、retry、request metadata 和 partial trajectory。retry 后仍失败时，confirmation run 标记 `INCOMPLETE_FACTORIAL`，不计算交互显著性。
- 所有 task-level contrasts、seed-level contrasts、context-level cells 和 Holm 调整结果均可从 `episodes.jsonl` 复算。

## 8. Historical OpenAI pricing verification and lifecycle (2026-11-20)

> Historical review only. The active model decision is superseded by Section 10; OpenAI models are not selected for this experiment.

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



## 10. DeepSeek Flash model decision (2026-11-20)

**User-selected active model:** `deepseek-flash` for Agent and User Simulator, and for Planner, Selector, Caller, and Synthesizer. GPT-4.1 and GPT-6 Luna are not selected for this experiment.

As of this protocol revision, DeepSeek's official model page identifies the `deepseek-flash` alias as serving DeepSeek-V4.1-Flash-1017. The API alias is mutable rather than an immutable snapshot. Every request must log the requested alias, response `model`, `system_fingerprint`, prompt hash, decoding settings, request ID, and token usage. If backend identity changes during a run, stop and quarantine the run rather than mixing model backends.

Fixed API/decode settings:
- OpenAI-compatible Chat Completions; base URL `https://api.deepseek.com`.
- Thinking disabled: `thinking={"type":"disabled"}`; `reasoning_effort="none"`.
- JSON mode for structured JSON content responses; Caller uses native Tool Calls and validates arguments locally against the selected tau2 tool schema.
- Temperature 0.0; max output 512 tokens; declared input cap 2,000 tokens.
- Direct network only. Configure the dedicated HTTP client with `trust_env=false`; do not route DeepSeek through the system proxy and do not alter global proxy configuration.
- Use `DEEPSEEK_API_KEY` from the runtime environment; never commit or log credentials.
- Do not use `deepseek-v4-pro`, retired `deepseek-chat`, `deepseek-reasoner`, or legacy Flash aliases.

Official pricing as checked 2026-11-20:
- Peak input cache miss: $0.30 / 1M; peak input cache hit: $0.006 / 1M; peak output: $1.20 / 1M.
- Off-peak rates are half the peak rates.
- Budget caps use peak cache-miss input rates and therefore do not assume caching or off-peak execution.
- See [DeepSeek Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing/) and [Chat Completions API](https://api-docs.deepseek.com/api/create-chat-completion/).

The prior OpenAI/GPT-4.1 and GPT-6 Luna price comparisons are historical only and do not define the active experiment configuration. This model selection does **not** authorize paid API calls. G4 remains NOT STARTED until the user explicitly approves the paid smoke after all preflight gates pass.


## 11. Phase 0E.1 request-bound correction — 2026-11-23

The previous Section 6 arithmetic counted one Agent request per Agent response. Source inspection of NIL-CCEA's four-module adapter shows that each Agent response invokes Planner + Selector + exactly one of Caller/Synthesizer. Therefore the corrected conservative upper bound is 90 Agent-module requests + 30 User Simulator requests = 120 logical requests per episode. With one retry reserved per logical request, the physical-attempt reservation is 240 per episode.

The 64-episode exploratory smoke is therefore 7,680 normal logical requests / 15,360 maximum physical attempts, costing at most $9.326592 without retries / $18.653184 if every logical request is retried once. The 384-episode pilot is 46,080 normal logical requests / 92,160 maximum physical attempts, costing at most $55.959552 without retries / $111.919104 with one retry per logical request.

The machine-readable source of current bounds is `experiments/pilot_factorial/cost_profile.json`. The $20 exploratory spend ceiling is proposed only and has not been authorized; the $80 hard stop remains separate and is not spending authorization.
