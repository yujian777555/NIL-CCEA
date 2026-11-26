# Phase 0C Review Record

**状态**：SELF-REVIEW COMPLETE，外部独立审查待进行。
**范围**：DeepSeek client、四个模块 wrapper、tau2 factorial runner、no-API tests、CI workflow。
**真实 API**：0。

## 已核验

- DeepSeek client 使用独立 HTTPX client，`trust_env=False`，不会读取系统代理。
- JSON 模式与 native tool-call 模式分开构造请求。
- 超时不自动重试，网络连接错误和 429 仅进行有界重试，避免对已发出的不确定请求重复扣费。
- 请求审计只保存 request ID、prompt hash、model、system fingerprint、usage、status 和 cost，不保存 API key。
- Caller 只在 Selector 返回 `tool_call` 时调用。
- tau2 `Tool.openai_schema` 和 `Tool.params` 被真实类验证。
- MultiToolMessage、plan_state、task metadata 和 seed 都有真实 tau2 类测试。
- 真实 tau2 Orchestrator 运行了 32 个 task-seed-configuration no-API cells。
- GitHub Actions host workflow 在 head `26d905d8ccafbcad9384f49978ac8d846c3b526c` 通过。

## 保留问题

1. `deepseek-flash` alias 和 `system_fingerprint` 仍需在真实 provider 请求中验证。
2. DeepSeek price profile 来自用户提供的 Phase 0C 配置，付费运行前仍需重新核价。
3. 真实 runner 的 `ENV` reward 在 no-API test 中没有代表性任务成功结果，正式统计仍未运行。
4. 当前 review 由主执行 Agent 完成，尚未获得独立人工或独立 Agent review。
5. GitHub Actions 当前只覆盖 host no-API tests，未在 CI 中安装 tau2 v1.0.1。

## 结论

Phase 0C 的工程前置链路达到 no-API readiness。G4 paid exploratory smoke 仍然关闭，直到 provider 核验、独立审查和用户明确批准完成。
