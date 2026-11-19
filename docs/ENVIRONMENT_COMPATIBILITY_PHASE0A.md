# Phase 0A 环境兼容性审计

**审计日期**：2026-11-19
**决策目标**：选择一个能支持多轮工具调用、状态 reset、任务/seed 配对、完整轨迹审计和 Agent 模块替换的环境。
**重要版本结论**：旧 `sierra-research/tau-bench` README 明确标注任务过时。正式实验不使用该旧仓库，而使用 `sierra-research/tau2-bench` 的 `v1.0.1` 发布版本，解析提交为 `fc0055dc4e0a316c3f83133267fbd6faaa770992`。当前 `main` 继续变化时，不自动跟随。

## 1. 候选环境比较

| 候选 | 任务与状态 | reset/seed | 轨迹与评分 | 模块替换 | 外部依赖和成本 | Phase 0A 判断 |
|---|---|---|---|---|---|---|
| **τ²-bench v1.0.1 text-v1** | airline、retail、telecom，每个发布子集 50 个冻结任务；task ID、task split、binding revision 和 benchmark manifest 有版本约束 | 官方文档提供 `--seed`、固定 trials、任务选择和 resumable output。seed 控制运行计划和用户模拟器输入配置，但不能假定第三方 LLM 采样完全确定 | text 运行保存 benchmark frame、plan、execution 和 results。每个任务有 DB、通信、环境断言或 NL assertion 评分组件，基础 reward 是二值任务成功 | 官方 `HalfDuplexAgent` 要求实现 `get_init_state` 和 `generate_next_message`，构造器接收 `tools` 与 `domain_policy`。可以在相同工具和 policy 下注入自定义 Agent，四模块需由自定义 Agent 内部显式分层 | 需要 user simulator、agent LLM，正式运行需要 API key。文本 benchmark 也会调用 semantic communication judge。官方文档没有完整成本估计 | **主环境，PASS**。先选英文 text-v1 的 retail/airline 子集，使用自定义四模块 Agent adapter |
| 旧 τ-bench 仓库 | airline/retail 旧任务 | `run.py` 有 seed 和 task index，但旧版 `Env.reset()` 只按 task index 重载数据，不能把完整初始状态 seed 作为统一发布契约 | 有 messages 和 reward，但 README 明确任务未更新，最新修订指向 tau2-bench | 旧版 `Agent.solve` 可替换，但环境代码和任务版本已过时 | LiteLLM、多家 API，历史轨迹可供参考 | **排除正式实验**。只保留为历史来源 |
| **ToolSandbox** | 1032 个状态化场景，34 个工具，场景包含多工具、多轮、状态依赖、信息不足和里程碑 DAG | `Scenario.play()` 对 starting context 做深拷贝，每轮保存 world state snapshot。官方材料没有确认统一 CLI seed 契约 | 保存 execution context、conversation、tool trace、token usage 和 milestone mapping，动态评估允许多条成功路径 | 场景定义包含 tool allow list，可控制暴露给 Agent 的工具。角色实现可替换，适合本地模块注入 | 需要模型 API，搜索场景需要 RapidAPI。工具代码在主机直接执行。仓库 LICENSE 为 Apple 保留权利文本，许可边界比 MIT 严格 | **本地诊断备选，NEEDS_REVISION**。适合验证 reset、状态快照和模块干预，不作为主结果 benchmark |
| **Toolathlon** | 600+ 工具、长链任务，提供 containerized 和 decoupled agent loop | 容器重启可隔离任务，但公开文档没有形成与 tau2 同等清晰的 task/seed 配对契约 | decoupled 模式保存任务 bundle、trajectory logs 和 eval 输出，环境由容器持有 | decoupled loop 允许替换 host agent framework，理论上可注入模块，但需要适配 MCP gateway | Docker/Podman、应用账号和 MCP 服务。公开服务每 IP 每 24 小时有 180 分钟累计时长和请求数限制 | **不作为 Phase 0A 主环境**。环境复杂、外部服务和账号依赖较多 |
| **AgentSpec** | DeliveryBench、ALFRED、MiniGrid、RoboTHOR，embodied scaffold 任务 | 文档示例明确调用 `env.reset()` 和 `agent.reset()`，但不同 benchmark 的环境随机性和外部 simulator 依赖不同 | 每步保存 reasoning、memory、reflection、action 和 metrics 到 `artifacts/runs/` | typed module interfaces 和 registry 直接支持替换 Perception、Memory、Reasoning、Reflection、Action | AI2-THOR、ALFRED、DeliveryBench 等依赖较重，主问题不是外部工具 API | **模块契约备选**。适合做组合接口和交互热图，不作为工具调用主结果环境 |

## 2. τ²-bench 源码与文档证据

### 2.1 版本与任务稳定性

- 当前仓库 README 将 `tau2-bench` 描述为 τ-Bench 的持续版本，提供 `text-v1` 和其他发布 manifest。
- `docs/running-the-benchmark.md` 说明 `text-v1` 使用 airline、retail、telecom 三个域，每域 50 个冻结任务，发布版本包含 benchmark frame、task subset digest 和 binding revision。
- 同一文档说明正式发布运行会保存 `benchmark-frame.json`、`benchmark-plan.json`、`execution.json` 和每个 cell 的 `results.json`。
- `v1.0.1` 修复了 banking_knowledge 评分，旧版本和新版本的该域分数不可混比。Phase 0A 不使用 banking_knowledge，仍把 v1.0.1 作为完整代码/数据版本 pin。

来源：[tau2-bench README](https://github.com/sierra-research/tau2-bench)、[运行文档](https://github.com/sierra-research/tau2-bench/blob/main/docs/running-the-benchmark.md)、[版本标签](https://github.com/sierra-research/tau2-bench/releases/tag/v1.0.1)。

### 2.2 reset、配对和失败语义

- 运行文档提供 `--task-ids`、`--num-tasks`、`--num-trials`、`--seed`、`--workers` 和 `--max-concurrency`。
- 发布运行默认启用 resume。已完成 calls 保留，基础设施错误可重试，缺失和未评分 calls 与 task reward 0 分开记录。
- 官方评分文档说明 task reward 是若干组件 reward 的乘积，DB 评分把 reference action 在 fresh environment 中重放得到目标状态，Agent 不必须复现唯一动作序列，除非任务把 `ACTION` 放进 `reward_basis`。
- 对 NIL-CCEA 而言，配对单位应是固定的 canonical task ID、task binding revision、language、domain、trial 和 resolved seed。重复 episode 不能当成独立 task cluster。

来源：[评分文档](https://github.com/sierra-research/tau2-bench/blob/main/docs/evaluation.md)、[运行文档的 resume 和 scoring 小节](https://github.com/sierra-research/tau2-bench/blob/main/docs/running-the-benchmark.md)。

### 2.3 轨迹访问和模块注入

- `src/tau2/agent/README.md` 定义 `HalfDuplexAgent` 的两个必要方法。`generate_next_message` 接收 `UserMessage`、`ToolMessage` 或 `MultiToolMessage`，返回 `AssistantMessage`，Agent state 由实现自己维护。
- 同一开发者文档把 `tools` 和 `domain_policy` 作为统一构造器输入。自定义 Agent 可以共享 benchmark 的工具集合和 policy，而不需要修改环境评分器。
- `LLMAgent` 的默认实现把系统 prompt 和 message history 送入一个生成调用，因此标准实现是单体的。四槽位不能通过修改一个大 prompt 声称完成独立干预，必须提供一个真实的自定义 Agent 类，将 Planner、Selector、Caller、Synthesizer 放在可独立 hash 和替换的组件中。
- orchestrator 保存消息和 tool result。NIL-CCEA runner 还需把模块局部事件、配置 hash、请求成本和失败重试写入自己的 episode record，不能只依赖 benchmark 的最终 `results.json`。

来源：[Agent Developer Guide](https://github.com/sierra-research/tau2-bench/blob/main/src/tau2/agent/README.md)、[HalfDuplexAgent 源码](https://raw.githubusercontent.com/sierra-research/tau2-bench/v1.0.1/src/tau2/agent/base_agent.py)、[LLMAgent 源码](https://raw.githubusercontent.com/sierra-research/tau2-bench/v1.0.1/src/tau2/agent/llm_agent.py)。

## 3. 四模块边界审计

### Planner

可替换性成立。自定义 Agent 可以在收到用户消息后生成中间计划，计划只进入 Agent state 和后续 Selector 输入，不改变 environment tools 或 scoring。计划内容不会读取任务的 `evaluation_criteria`、gold action 或 evaluator metadata。

### Selector

可替换性成立，但要防止与 Caller 混淆。Selector 只输出从 `env.get_tools()` 得到的工具名、是否需要发消息或结束动作，以及一个结构化选择理由。它不构造具体参数，也不执行工具。

### Caller

可替换性成立。Caller 接收 Selector 选中的工具名、工具 schema、当前可见历史和计划步骤，输出符合同一工具 schema 的 `ToolCall`。实际工具执行仍由 tau2 orchestrator/environment 完成，保证不同 Caller 不获得额外权限。

### Synthesizer

可替换性成立。Synthesizer 只接收用户可见消息、tool result、计划状态和任务上下文，输出普通 assistant message。它不能读取 evaluator、reference trajectory、数据库 gold hash 或 hidden task metadata。

### 结论

四个模块在 τ²-bench 的 Agent API 层面具有可替换插入点，但当前仓库没有现成四槽位实现。G1 的 PASS 依赖下一步 `Tau2HalfDuplexAdapter` 的 mock 和静态泄漏测试。若真实 adapter 无法保持以上边界，正式协议必须改为可证实的三槽或两槽设计，并重新计算 (2^m) 配置数。

## 4. 推荐实验入口

### 主入口

- 版本：`tau2-bench v1.0.1`，commit `fc0055dc4e0a316c3f83133267fbd6faaa770992`。
- 模式：`text-v1`，只使用英文，先选 retail 与 airline 两个 task family。
- 任务：正式冻结前从发布子集中选择 12 个 canonical task ID，建议两个域各 6 个，不能用任务内容或 reward 结果事后筛选。
- 模型：同一 agent backbone、同一 user simulator、同一 semantic judge、同一 decoding 参数。模型版本和 provider 必须进入 manifest。
- Agent：自定义 `HalfDuplexAgent` 四模块 adapter，共享 tau2 的工具列表和 domain policy。

### 本地受控入口

ToolSandbox 可作为没有 API 成本的接口和状态诊断平台，但它的官方工具代码在主机执行，搜索工具还依赖 RapidAPI，且 seed 契约和许可证边界不如 tau2-bench 清晰。它只能产生探索性诊断记录，不能替代 tau2 的确认性结果。

## 5. 未解决风险与处置

| 风险 | 影响 | 处置 |
|---|---|---|
| 用户模拟器与 semantic judge 也是 LLM | 同一 seed 不保证完整轨迹确定，执行噪声可能淹没交互 | 记录 provider/model/decoding/request ID，使用 task-clustered bootstrap，先在 mock 验证统计管线 |
| tau2 官方 reward 中有 LLM judge 组件 | reward 可能带评价器噪声 | 将 DB/ENV_ASSERTION 组件和通信 judge 组件分别记录，预先指定主终点，做 judge sensitivity |
| 自定义四模块 Agent 还没有真实运行 | G1 只有源码证据，没有 adapter 运行证据 | 先实现 mock half-duplex adapter 和接口静态测试，再申请一条付费 API smoke |
| τ²-bench 版本继续演进 | 结果跨版本不可比 | 所有运行绑定 tag commit、manifest、binding revision 和源代码 hash |
| ToolSandbox 许可、主机执行和 RapidAPI | 不适合直接作为可发布主基准 | 仅作为本地诊断，不进入正式主结果 |

## 6. Gate 状态

| Gate | 状态 | 证据 |
|---|---|---|
| G1 Environment | **PASS** | τ²-bench v1.0.1 版本、任务 manifest、reset/resume、评分和自定义 HalfDuplexAgent API 已有官方源码/文档证据。四模块独立运行仍需 adapter smoke 作为 G2/G3 前置检查。 |
| ToolSandbox fallback | **NEEDS_REVISION** | 有状态快照和完整轨迹，但 seed、许可证和外部 RapidAPI 约束尚未达到主环境标准。 |
