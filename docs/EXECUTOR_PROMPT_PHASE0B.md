# NIL-CCEA Phase 0B 执行提示词：修复真实 Adapter 与交互估计器，冻结 Pilot 前置协议

你现在接管独立仓库 **yujian777555/NIL-CCEA**。

- 仓库：https://github.com/yujian777555/NIL-CCEA
- Phase 0A 分支：`phase0a-literature-environment-audit`
- Phase 0A HEAD：`6bed028a4675a75928734b633bbfae49d6b98b14`
- 本阶段分支：`phase0b-adapter-statistical-corrections`
- PR #1：https://github.com/yujian777555/NIL-CCEA/pull/1
- 独立审查报告：`docs/PHASE0A_INDEPENDENT_REVIEW.md`

**本阶段目标：修复真实 tau2 Adapter 和统计估计器的正确性问题，完成 tau2 v1.0.1 无 API key 集成验证，冻结正式实验前置协议并形成可信成本估算。不要重做 Phase 0A 文献审计，也不要重跑已经通过的纯 Mock smoke。**

## 0. 接管与保护

1. 先检查远端 HEAD、PR #1 head、当前工作区、分支和未提交修改。
2. 不得覆盖本地未提交内容；如有修改，先备份并汇报。
3. 从本提示词所在分支继续工作，不要直接改写 main。
4. 保持 PR #1 开放；在本阶段所有 blocker 修复和独立审查通过前，不要合并。
5. 禁止 force-push、reset --hard、删除历史或覆盖原始实验记录。
6. 只维护 NIL-CCEA，不得混入其他仓库的代码、实验编号和数据。

## 1. 必须先修复的统计问题

审查报告发现当前 `interaction.py` 有两个核心问题：

### 1.1 独立 cluster 定义错误

当前代码把 `(task_id, seed)` 当成独立 cluster。正式计划中一个 task 的两个 seeds 是同一 task 内的重复测量，不能被当作两个独立 task。

修复为：

- cluster = canonical task instance（至少使用稳定 task ID；若 ID 可跨版本复用，加入 task/binding version）。
- seed 是 task cluster 内的重复测量维度。
- 每个 task-seed 先计算完整 factorial pairwise contrast。
- 对同一个 task 的预注册 seeds 按预先定义的规则平均，得到一个 task-level contrast。
- bootstrap 时只重采样 task IDs，并保留被抽中 task 的全部 seeds 和 16 个配置。
- 输出 unique task count、complete task count、incomplete task count、seed count，不能把 task-seed 数报成 cluster 数。

### 1.2 不完整 factorial 数据不能静默参与估计

当前代码只对存在的 context 求平均，并过滤非 success 记录。这会使缺失配置改变 estimand。

修复为 fail-closed：

- 每个 task × seed 必须恰好有 16 个配置，每个配置恰好一条 episode 记录。
- 对任一模块对，其他两个模块的四种 context 必须全部存在；每个 context 的四个 pair cells `00/01/10/11` 必须完整。
- 重复配置、缺失配置、未知配置、配置 hash 冲突必须显式报错或标记为 incomplete，禁止覆盖字典中的旧记录。
- 区分真正的 Agent task failure 与 provider/环境基础设施失败。前者按冻结的 benchmark primary endpoint 计分；后者不能擅自记为 0，也不能静默删除。
- 基础设施失败按冻结 retry policy 重试；超过上限后，保留失败记录并按预先冻结的 cluster missingness policy 处理。必须报告 attrition，并给出敏感性分析。
- 如果某个 task 的任一 seed 仍缺失关键配置，主分析中整个 task cluster 是否纳入必须由预先冻结规则决定，不能按观察结果临时选择。

增加测试：
1. 同一 task 两个 seeds 只形成一个 bootstrap cluster；
2. 一个 task 有 2 seeds、另一个 task 有 1 seed 时，cluster 数仍为 2；
3. 缺少任一配置时不能静默估计；
4. 任一 pair context 不完整时返回明确 incomplete 状态；
5. 同一 task-seed-config 重复时必须拒绝；
6. task-level task failure 与 infra failure 处理不同；
7. 完整数据仍能正确复算合成已知交互。

### 1.3 六组交互的统计推断

四个模块共有六个 pairwise contrasts。正式冻结前：

- 明确主估计量、置信区间方法、检验方法和 Holm step-down 的具体实现；
- 不得把普通 bootstrap percentile interval 直接称为 Holm-adjusted significance；
- 以 task-level contrast 为统计单位；
- 任务族异质性作为预先声明的分析；
- 记录所有六个 pair 的原始效应、区间、未校正 p 值（如采用）、校正后结果和不确定性；
- 对小样本做敏感性/功效分析，不得把 12 tasks × 2 seeds 当成 24 个独立 clusters。

若 12 个 task clusters 无法对预设 practical delta 提供足够精度，优先增加 canonical task 数，而不是简单增加同一 task 的 seeds。调整必须发生在正式协议冻结前。

## 2. 必须修复 tau2 Adapter

官方 tau2 v1.0.1 源码已核实：

- `Tool` 使用 `tool.params` 和 `tool.openai_schema`，而不是当前 adapter 检查的 `tool.parameters` / `tool.schema`。
- `HalfDuplexAgent` 输入为 `UserMessage | ToolMessage | MultiToolMessage`，输出为 `AssistantMessage`。
- tau2 v1.0.1 要求 Python `>=3.12,<3.14`。

官方源码：
- https://github.com/sierra-research/tau2-bench/blob/fc0055dc4e0a316c3f83133267fbd6faaa770992/src/tau2/environment/tool.py
- https://github.com/sierra-research/tau2-bench/blob/fc0055dc4e0a316c3f83133267fbd6faaa770992/src/tau2/agent/base_agent.py
- https://github.com/sierra-research/tau2-bench/blob/fc0055dc4e0a316c3f83133267fbd6faaa770992/src/tau2/agent/README.md
- https://github.com/sierra-research/tau2-bench/blob/fc0055dc4e0a316c3f83133267fbd6faaa770992/pyproject.toml

修复要求：

1. `_tool_schema()` 从真实 tau2 Tool 提取 name、description 和完整 JSON 参数 schema。优先用 `tool.params.model_json_schema()` 或官方 `tool.openai_schema["function"]["parameters"]`。
2. Selector 选择 `respond/stop` 时，不得调用 Caller。
3. Selector 选择 `tool_call` 时，Caller 的 `proposal.tool_name` 必须等于 `selection.tool_name`。
4. 使用真实 tau2 Tool 的 `params` 模型校验参数。不能只验证工具名。
5. 未知工具、工具名不匹配、缺失参数、类型错误、schema 校验失败必须产生明确的 typed failure event，并执行冻结的修复/重试策略；禁止静默落入 Synthesizer 并伪装成正常回答。
6. Synthesizer 必须正确处理 UserMessage、ToolMessage 和 MultiToolMessage；工具结果只来自实际公开 tool result。
7. 明确并实现 `plan_state` 的持久化转移。Planner/Selector 声明使用 state 时，下一轮必须拿到真实更新后的公开状态。
8. 实验模式下 task_id、task_version/binding revision、task_family 不允许默认为 `unknown`；实现真实 tau2 factory/runner 注入路径，缺少必需 metadata 时 fail closed。
9. 所有配置必须使用相同的工具集合、policy、backbone/provider/model、decoding、上下文上限和 retry 上限；只允许模块变体发生变化。
10. 保留模块版本、content hash、config hash 和逐步 module event。

## 3. Python 3.12/3.13 环境与无 API Key 集成测试

准备独立 Python 3.12 或 3.13 环境，并从精确 commit 安装 tau2：

`fc0055dc4e0a316c3f83133267fbd6faaa770992`

此阶段只允许 no-key 测试，不允许发出模型/API 请求。

必须新增真实 tau2 集成测试：

- 导入并实例化 pinned `HalfDuplexAgent` adapter；
- 用 tau2 自己的 Tool 类型构造至少一个含必需参数的工具；
- 验证 schema 非空且字段完整；
- 测试 UserMessage → AssistantMessage；
- 测试 tool-call 输出的 ToolCall name/arguments；
- 测试 ToolMessage 输入后的下一轮决策；
- 测试 MultiToolMessage；
- 测试 respond/stop 分支；
- 测试错误工具名、参数缺失和 schema invalid 的 fail-closed 行为；
- 测试 plan_state 跨轮持久化；
- 验证 16 个配置的权限、policy、模型和解码设置完全一致；
- 验证 task metadata、module hashes 和 config hash 写入 manifest；
- 确认所有测试不需要 API key，真实 API 调用数为 0。

不要因为当前主机 Python 3.10 不兼容 tau2 就停止；用独立 Python 3.12/3.13 环境解决，不要破坏现有 Mock 环境。

## 4. 冻结 Pilot 协议

更新 `docs/PILOT_DESIGN_R1.md`，必要时升为 R2。必须冻结：

1. 精确 12 个或经功效分析调整后的 canonical task IDs；
2. task domain/family、发布版本、binding revision、language、trial、resolved seeds；
3. 唯一 primary endpoint 及 tau2 reward 具体组成；
4. 是否排除依赖 NL judge 的任务；若排除，说明选择规则并在看结果前冻结；
5. practical interaction threshold `delta` 及实际意义；
6. 六组 pairwise 检验和 Holm correction；
7. task-level cluster bootstrap / 其他推断方法；
8. agent task failure、provider failure、timeout、invalid tool call、缺失 episode 的处理；
9. 每个 episode 的最大步数、调用数、retry policy；
10. per-episode、exploratory smoke、正式 pilot 的预算上限；
11. 终止条件、超预算行为、数据保留规则；
12. sample size / sensitivity analysis，统计单位是 task ID。

不要直接把函数默认的 delta=0.05 当成已冻结标准。需要解释其在 endpoint 尺度上的实际含义，并用敏感性分析展示不同 delta 和任务数下的精度。

## 5. 成本估算与付费门禁

在任何真实 API 调用前，提交一份成本估算：

- Agent 模型；
- user simulator 模型；
- judge 模型（若任务使用）；
- 每个 episode 预计和最大调用次数；
- 每次调用 token 估算；
- provider 当前价格来源和核验日期；
- retry、timeout、失败调用的成本；
- 2-task exploratory smoke 及完整 pilot 的预计成本；
- 单次调用、单 episode、smoke 总额和 pilot 总额上限；
- 触发停止的明确条件。

不得读取、打印、提交或写入日志的 API key。不得用真实调用来“测一下价格”。先用价格表和本地最大调用上限估算。

**未经用户明确批准，不得运行任何付费 API smoke 或正式 pilot。** 用户批准前，完成所有无 API key 的代码与协议工作。

## 6. 不因局部失败停止研究

某个接口、模块或测试失败时：

1. 定位失败发生在哪一层；
2. 区分 benchmark API 不兼容、模块契约错误、统计实现错误和环境依赖问题；
3. 修复并添加回归测试；
4. 如原四模块划分不适用，基于源码调整模块边界并更新协议；
5. 如 tau2 adapter 仍不合适，先验证 ToolSandbox 等受控备选，不得直接终止项目；
6. 零交互、弱交互或某个 task family 结果不理想，只触发诊断，不允许伪造正结果。

不得通过删掉困难任务、改变主终点、降低 `delta` 或事后改变样本量来追求正结果。

## 7. Gate 与交付

- **G2 PASS**：模块接口、tool schema、state transition、task metadata、primary endpoint、统计推断、缺失处理、retry 和成本门禁全部冻结。
- **G3 PASS**：mock 回归通过，真实 tau2 v1.0.1 no-key adapter integration tests 全部通过。
- **G4 NOT STARTED**：只有在用户批准成本后，才运行一条探索性真实 tau2 smoke。探索性 smoke 不作为确认性 factorial 结果。
- **Formal pilot**：只有 smoke 审查通过、任务和预算冻结后才启动。
- **G5 NOT STARTED**：交互测量可靠后再实现 linkage-aware CCEA。

每个 Gate 给出 PASS / BLOCKED / NEEDS_REVISION 和可复现证据。BLOCKED 必须附带可执行修复路径，不得只写“不能继续”。

## 8. 仓库维护与交付报告

每个阶段必须更新：
- `STATUS.md`
- `NEXT_STEPS.md`
- `docs/RESEARCH_LOG.md`
- `docs/HANDOFF.md`
- 相关代码、测试和协议文件

报告必须给出：
- 起始/最终 SHA；
- 分支与 PR 状态；
- 变更文件；
- 精确 tau2 commit；
- Python 版本；
- 测试命令及结果；
- no-key 与真实 API 调用数；
- 六个 pair 的统计实现和 cluster 定义；
- 任务数、seed 数、缺失处理；
- 成本估算来源；
- Gate 状态；
- 下一步唯一具体行动。

**本阶段先修正 F0-1 至 F0-4，再完成 F0-5 至 F0-7 和协议冻结。不要写完整论文，不要实现完整演化优化器，不要启动付费调用。目标是尽快把真实 tau2 Adapter 和交互估计器做到可信、可复现，然后进入受控 smoke。**
