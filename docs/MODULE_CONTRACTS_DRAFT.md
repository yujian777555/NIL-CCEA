# NIL-CCEA 模块契约草案

**适用环境**：τ²-bench `v1.0.1` text-v1 的自定义 `HalfDuplexAgent` adapter。
**状态**：DRAFT，已依据环境 API 定义，尚未通过付费环境运行。mock runner 使用这些契约的纯本地实现。
**固定条件**：所有候选共享同一 Agent backbone、provider、模型版本、工具列表、domain policy、上下文上限、解码设置和 retry 上限。变体只改变模块机制。

## 1. 全局边界

- 模块只能读取用户可见消息、tool result、当前 Agent state 和公开 domain policy。
- 模块禁止读取 `evaluation_criteria`、reference trajectory、gold DB hash、隐藏 evaluator metadata、task split 文件中的答案字段或任何结果缓存。
- 所有工具权限来自 tau2 环境传入的同一 `tools` 列表。Selector 不能扩展工具列表，Caller 不能绕过 orchestrator 直接修改数据库。
- 每个模块以不可变 manifest 注册，包含 `module_id`、`module_version`、源码或提示内容 SHA-256、接口版本和配置 hash。
- 任何无效输出都必须产生显式 `failure` 事件。重试只能使用运行协议规定的上限并计入成本账本。

## 2. 公共数据结构

### `AgentContext`

```json
{
  "task_id": "canonical task id",
  "task_version": "binding revision",
  "task_family": "retail|airline|...",
  "visible_messages": [],
  "domain_policy": "public policy text",
  "tool_schemas": [],
  "step_index": 0,
  "max_steps": 30,
  "plan_state": {}
}
```

### `Plan`

```json
{
  "goals": [
    {"goal_id": "g0", "description": "...", "prerequisites": []}
  ],
  "termination_condition": "public condition",
  "unknowns": ["..."],
  "module_version": "planner variant id"
}
```

### `Selection`

```json
{
  "kind": "tool_call|respond|stop",
  "tool_name": "public tool name or null",
  "goal_id": "g0 or null",
  "reason_code": "schema_match|prerequisite|response_needed|...",
  "module_version": "selector variant id"
}
```

### `ToolCallProposal`

```json
{
  "tool_name": "selected public tool",
  "arguments": {"schema validated arguments": "..."},
  "validation": {"schema_valid": true, "missing_fields": []},
  "module_version": "caller variant id"
}
```

### `AssistantDecision`

```json
{
  "kind": "tool_call|respond|stop",
  "tool_call": {"name": "...", "arguments": {}},
  "content": "assistant-visible text or null",
  "module_events": [],
  "module_versions": {},
  "config_hash": "sha256"
}
```

## 3. Planner 契约

**输入**：`AgentContext`，当前用户消息和已有公开 tool result。
**输出**：`Plan`。
**状态**：只允许在 Agent state 中保存计划和公开中间状态。
**异常**：解析失败或计划为空时产生 `planner_invalid_output`，按协议最多重试一次，之后输出 `respond` 请求用户澄清。

### P0 `linear_constraint_plan`

- 机制：按用户目标生成线性有序子目标，显式列出每一步所需公开信息。
- 不做分支搜索，不重复调用同一工具，不把 tool result 写入不可见外部存储。
- 适合作为低复杂度、低额外调用参考。

### P1 `state_dependency_plan`

- 机制：将目标表示为带前置条件和未知字段的依赖图，每一步标记需要的状态证据。
- 只有在前置条件满足或已显式确认缺失时推进下一目标。
- 适合作为状态依赖和长链任务参考。

## 4. Selector 契约

**输入**：`AgentContext`、`Plan`、所有当前可见工具 schema。
**输出**：`Selection`。
**权限**：只能返回 `tool_schemas` 中的工具名或 `respond/stop`。
**异常**：工具名不在 schema 时产生 `selector_unknown_tool`，不得交给 Caller 猜测。

### S0 `schema_match_selector`

- 机制：按当前 goal 与工具名、描述、参数字段的直接匹配选择一个动作。
- 不维护跨步骤的候选队列，只读取当前 plan goal 和公开历史。

### S1 `prerequisite_gate_selector`

- 机制：先检查 goal prerequisites 和已观测状态，再从满足前置条件的候选工具中选择动作。
- 如果没有满足前置条件的工具，输出 `respond` 请求公开信息或澄清。

## 5. Caller 契约

**输入**：`Selection`、目标工具 schema、当前 goal、公开历史。
**输出**：`ToolCallProposal`，实际调用由 tau2 orchestrator 执行。
**权限**：不能直接写数据库，不能调用未在 schema 中的工具。
**异常**：参数缺失、类型错误、schema 校验失败时产生 `caller_invalid_arguments`，按协议最多重试一次，之后返回 `respond` 请求缺失信息。

### C0 `direct_schema_caller`

- 机制：从当前用户消息和公开历史中提取参数，执行最小 schema 校验后输出调用。
- 不主动增加确认步骤，适合作为低延迟参考。

### C1 `validated_repair_caller`

- 机制：先构造参数草稿，再执行字段完整性、类型和公开前置条件校验。
- 缺失字段只通过用户消息或工具返回的公开信息补齐，不猜测隐藏答案。无效参数在同一调用预算内做一次结构化修复。

## 6. Synthesizer 契约

**输入**：当前用户消息、公开 tool result、`Plan`、最近一次模块事件。
**输出**：`AssistantDecision` 中的 `respond` 或 `stop` 文本。
**边界**：不得声称未发生的工具结果，不得泄露 evaluator 或 reference trajectory，不得修改 tool call。

### Y0 `evidence_first_synthesizer`

- 机制：只总结已经由公开 tool result 支持的事实，缺失证据时明确说明尚未完成。
- 输出简短、可核验的用户答复。

### Y1 `state_reconcile_synthesizer`

- 机制：将计划目标、已完成动作、未完成目标和下一步公开行动整理成状态清单，再生成答复。
- 只有所有公开终止条件满足时才输出完成陈述，否则保留未完成状态。

## 7. 版本和 hash 规则

- `module_id` 采用 `planner.p0`、`planner.p1`、`selector.s0`、`selector.s1`、`caller.c0`、`caller.c1`、`synthesizer.y0`、`synthesizer.y1`。
- `content_sha256` 对规范化源码或提示内容计算，换行统一为 LF，UTF-8 编码，不包含运行时时间戳。
- `configuration_id` 是四个 module ID 按固定槽位排序后的短标识。完整 `config_hash` 对所有模块 hash、模型/provider/version、解码设置、环境版本、协议版本和 runner 版本做 JSON canonicalization 后计算。
- 运行中不允许修改 manifest。变体改动必须生成新 module version 和新 protocol version。

## 8. 静态泄漏检查

正式 adapter 需要自动检查以下字符串和导入路径未出现在模块实现中：

- `evaluation_criteria`
- `reference_trajectory`
- `gold_data_hash`
- `reward_basis`
- `ground_truth`
- `task_answer`
- tau2 `data/tau2/domains/*/tasks*` 的 evaluator-only 字段访问

这组检查只能证明没有明显字符串或路径泄漏，不能替代代码审查和最小权限运行。

## 9. 冻结条件

本草案只有在以下条件全部满足后才转为 `FROZEN`：

1. mock adapter 能在 16 个配置上完成接口、权限、hash 和轨迹测试。
2. tau2 adapter 的一条无 API 真实构建检查确认工具列表和 policy 在所有配置中相同。
3. 付费 API smoke 通过且记录 user simulator、agent、judge 的实际调用数和失败语义。
4. 预先登记 primary endpoint、实用效应阈值、task-clustered bootstrap 和 Holm 校正规则。
