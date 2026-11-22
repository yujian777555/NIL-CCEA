# NIL-CCEA Phase 0E 接手提示词

## 当前仓库状态

- 仓库：`https://github.com/yujian777555/NIL-CCEA`
- 分支：`phase0b-adapter-statistical-corrections`
- Phase 0D 修复提交：`7f07bbfd75927bb35a6cabd466799aded8c5fb57`
- 当前文档头：`55e36241f77d81ba413a27a011fb886b5ca68ff0`
- pinned tau2-bench：v1.0.1，commit `fc0055dc4e0a316c3f83133267fbd6faaa770992`
- 当前 DeepSeek API 请求：0
- 当前付费批准：未获得

## 开始前必须阅读

1. `docs/EXECUTOR_PROMPT_PHASE0D.md`
2. `docs/PHASE0D_INDEPENDENT_REVIEW.md`
3. `STATUS.md`
4. `NEXT_STEPS.md`
5. `experiments/pilot_factorial/cost_profile.json`

## 硬性边界

- 未获得用户明确批准前，不得读取 API key，不得向 DeepSeek 发送请求，不得启动付费 smoke。
- 不得修改主线研究问题，不得提前实现完整演化优化器，不得声称性能提升、统计显著性或创新性成立。
- 保留所有原始 artifact，禁止覆盖已有 `episodes.jsonl`、`request_events.jsonl`、`cost_ledger.json` 和 `run_summary.json`。

## 获得批准后的唯一实验

- Provider：DeepSeek
- 请求模型别名：`deepseek-flash`
- 公开文档 served version：`DeepSeek-V4.1-Flash-1017`
- Base URL：`https://api.deepseek.com`
- thinking disabled，temperature 0，max output 512，输入保守上限 2,000
- Planner、Selector、Caller、Synthesizer、Agent 和 User Simulator 使用同一模型别名和 decoding
- task：retail 5、airline 2
- seed：0、1
- 配置：四模块全部 16 个二进制配置
- 规模：64 episodes
- primary endpoint：`EvaluationType.ENV` 的 environment reward
- 最大正常请求：3,840。按照每请求一次重试的上界：7,680
- 成本上界：无重试 `$4.663296`，所有请求一次重试 `$9.326592`
- `$80` 只是硬停止线，不是消费授权

## 执行前检查

1. 重新核对官方 endpoint、模型文档、价格和 tau2 任务 ID。
2. 明确用户批准的消费上限，并据此构造 `RequestBudget`，预留最大重试 profile。
3. 生成包含 task、seed、16 配置、模型请求别名、协议 hash 和代码 SHA 的 pre-run manifest。
4. 验证 User Simulator 暴露可检查的 `deepseek-flash` client 或模型元数据。
5. 运行最小单 episode 请求前检查，确认 ledger 字段、response model、system fingerprint、请求 ID 和 usage 存在。

## 停止条件

- 任何 model 或 system fingerprint 缺失或漂移，立即 quarantine 整批并停止。
- 任何预算预留、输入上限、请求数或硬停止线即将超限，停止下一请求。
- timeout、5xx 或交付状态未知的网络错误不得自动重放。
- 缺少 ENV reward、工具 schema 或模块模型不一致时，将 episode 标记为失败并保留部分轨迹。

## 结果解释

该 smoke 只有两个 task cluster，只用于验证真实调用链、轨迹、成本和交互可行性。完成后只报告原始记录、描述性四格对比和数据质量，不进行显著性结论。后续 12-task 阶段仍需独立协议、功效和批准 gate，演化主线保持为交互测量、Linkage Learning 和 Linkage-aware Cooperative Co-evolution。
