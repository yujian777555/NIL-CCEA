# Phase 0D 独立审查记录

## 审查范围

审查对象是分支 `phase0b-adapter-statistical-corrections` 上的 Phase 0C 实现，以及本阶段新增的 DeepSeek 客户端、真实 tau2 runner、原始轨迹和成本账本改动。审查由独立只读 reviewer `/root/phase0d_independent_review` 完成，reviewer 没有实现 Phase 0C，也没有修改工作树。审查使用实际 checkout 和 pinned tau2-bench v1.0.1 源码，未读取 API key，也未发送网络请求。

## 初始发现与处理

| 严重度 | 位置 | 可复现问题 | 处理状态 | 覆盖测试 |
|---|---|---|---|---|
| P0 | `src/nil_ccea/deepseek_client.py`，旧默认参数 | 客户端默认允许两次重试，成本协议只允许一次 | 已修复。最大值强制为一次 | `test_timeout_is_not_retried_and_network_error_is_bounded` |
| P0 | `src/nil_ccea/tau2_runner.py`，旧 `run_episode` | 基础设施失败会重放整个 episode，可能重复已完成调用 | 已修复。runner 不再执行 episode 级重试 | `test_real_tau2_factorial_runner_writes_all_cells_without_api` |
| P0 | `src/nil_ccea/deepseek_client.py`，请求异常分支 | timeout、5xx 和不确定网络异常可能在交付状态未知时重试 | 已修复。仅连接建立失败和 429 可按上限重试 | `test_timeout_is_not_retried_and_network_error_is_bounded`、`test_server_error_is_delivery_unknown_and_not_retried` |
| P1 | `src/nil_ccea/deepseek_client.py:314` | audit events 只存在内存，缺少 attempt、episode、模型身份、fingerprint、usage 和成本字段 | 已修复。每个物理尝试形成事件，runner 增量写入 `request_events.jsonl` 和 `cost_ledger.json` | `test_input_cap_and_audit_identity_are_fail_closed`，tau2 runner ledger assertions |
| P1 | `src/nil_ccea/deepseek_client.py:131` | fingerprint tracker 未接入执行路径，缺失身份字段可静默通过 | 已修复。model 与 system_fingerprint 缺失或漂移抛出身份错误，runner quarantine 批次 | `test_missing_model_identity_fails_closed`、`test_fingerprint_tracker_and_cost` |
| P1 | `src/nil_ccea/deepseek_client.py:64` | 请求、token 和成本没有发送前预留 | 已修复。RequestBudget 支持全局与 episode 级预留，并按最大重试次数预留物理请求 | `test_budget_and_cache_hit_miss_cost` |
| P1 | `src/nil_ccea/tau2_runner.py:216` | 异常会丢失已产生的轨迹 | 已修复。捕获异常时保存 orchestrator 当前 trajectory，episode 记录立即追加到 raw artifact | runner failure-path coverage |
| P1 | `src/nil_ccea/deepseek_client.py:391` | cache hit/miss usage 没有解析，成本估计不对应 provider 费率 | 已修复。解析并保留两类 token，同时保存实际成本和保守上界 | `test_budget_and_cache_hit_miss_cost` |
| P1 | `src/nil_ccea/tau2_runner.py:271` | User Simulator 和四个模块的模型一致性不可验证 | 已修复。真实 ENV runner 要求四个模块和 User Simulator 暴露 `deepseek-flash` 客户端或模型元数据，并检查 decoding | 真实 provider smoke 前置 gate，mock runner 使用 `evaluate=False` |
| P1 | `src/nil_ccea/tau2_runner.py:180` | 缺少 ENV reward 可能被标记为成功 | 已修复。`evaluate=True` 下 reward 缺失直接记录 infrastructure failure | runner outcome path |
| P2 | `src/nil_ccea/tau2_runner.py:351` | 原始请求事件没有成本账本汇总 | 已修复。每个 episode 写入后重建 `cost_ledger.json`，保留事件和 totals | tau2 factorial ledger assertion |

## 当前残留 gate

1. 公开文档可以确认 `deepseek-flash` 别名、发布的 served version 和价格。实际账户返回的 model 与 system fingerprint 仍需要首个获批请求才能验证。
2. 真实 User Simulator 的 tau2 构造器需要在付费运行前提供可检查的 `llm` 或 client 属性。匿名 opaque user factory 会在 `evaluate=True` 下 fail closed。
3. 本审查是独立代码审查，不等同于 GitHub PR review。GitHub 外部 review gate 仍需按仓库流程记录。
4. 价格和服务条款应在用户批准前再次核对。Phase 0D 没有付费调用。

## 结论

本阶段的代码级 P0/P1 修复已落地，并由主机和 pinned Python 3.12/tau2 v1.0.1 无 API 测试覆盖。两套套件各通过 34 项测试。No-API 证据不能证明真实 provider 身份、真实 ENV reward 或模块交互效应。64 episode exploratory smoke 仍需用户明确批准后才可执行。
