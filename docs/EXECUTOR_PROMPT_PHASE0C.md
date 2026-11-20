# NIL-CCEA Phase 0C — DeepSeek Flash 接入与真实实验执行链路打通

你现在接管我的科研项目，请直接开始执行，不要只给研究建议或实施计划。

## 一、项目身份与仓库边界

唯一允许操作的仓库：

`https://github.com/yujian777555/NIL-CCEA`

当前分支：

`phase0b-adapter-statistical-corrections`

接管时记录的最新提交：

`4b9e21f7aed42b76a18b6ff0df2be876fec3850c`

首先检查远端 HEAD、当前分支、工作区状态和 PR 状态。

注意：

1. 只允许修改 NIL-CCEA。
2. 不允许混用其他科研仓库的代码、实验数据或研究结论。
3. 不允许擅自修改 main。
4. 不允许擅自合并 PR #1 或 PR #2。
5. 保留现有 Phase 0A、Phase 0B 的研究成果和历史证据。
6. 所有修改必须有测试、提交和远端同步记录。

## 二、研究目标

项目名称：

Noise-aware Interaction Linkage Cooperative Co-evolution for LLM Agents（NIL-CCEA）。

核心研究问题：

能否通过统计可靠的模块交互效应识别 LLM Agent 内部具有协同作用的模块，再利用学习到的 Linkage Structure 改进协同演化搜索？

研究主线：

1. 将 LLM Agent 拆分为 Planner、Selector、Caller、Synthesizer 四个可替换模块。
2. 使用配对因子实验测量模块主效应和交互效应。
3. 识别具有统计可靠性的模块交互关系。
4. 构建动态 Linkage Graph。
5. 根据 Linkage Graph 设计分组变异、交叉和协同搜索机制。
6. 与普通独立演化、固定分组演化和其他公平基线比较。
7. 最终证明 NIL-CCEA 是否能够提高 Agent 的任务成功率、搜索效率或其他预注册的核心评价指标。

不要把本项目改造成普通 Prompt Optimization，也不要把核心研究问题转移到预算分配或一般性的 Agent 工程优化。

**演化计算必须是核心算法贡献，LLM Agent 是研究对象。**

## 三、统一模型配置

用户已经明确选择 DeepSeek Flash，不再讨论 GPT-4.1、GPT-6 Luna 或其他模型替代方案。

统一配置：

- Provider：DeepSeek
- Model：`deepseek-flash`
- 当前配置记录的服务版本：DeepSeek-V4.1-Flash-1017
- Base URL：`https://api.deepseek.com`
- API：OpenAI-compatible Chat Completions
- API Key：`DEEPSEEK_API_KEY`
- Temperature：0.0
- Max output tokens：512
- 输入 token 预算上限：2000
- Thinking / CoT：关闭
- 结构化输出：JSON
- DeepSeek 请求必须直连，不使用系统代理。

四个模块必须使用同一个模型：

- Planner
- Selector
- Caller
- Synthesizer

Agent 和 User Simulator 也使用同一模型。

特别注意：

1. DeepSeek 的模型别名可能发生变化，必须记录 API 返回的实际 model 和 system_fingerprint。
2. 每次请求记录 request_id、prompt hash、token usage、请求状态和成本。
3. 如果模型实际版本在同一实验过程中发生变化，必须停止并隔离该批次，不能混合不同版本的数据。
4. 必须根据 DeepSeek 官方 API 文档核实参数兼容性。不要为了兼容其他供应商而盲目发送不受支持的参数。
5. JSON 模式与 Native Tool Calls 应根据具体模块使用正确的请求模式，不能假设两者可以无条件组合。
6. 禁止将 API Key 写入代码、配置文件、日志或 Git。

## 四、Phase 0C 必须完成的工作

### Task 1：修复 tau2 Adapter

检查：

`src/nil_ccea/tau2_adapter.py`

当前已知问题：

Caller 在判断 Selector 的输出类型之前就被调用。

必须修复为：

- Selector 选择 tool_call：调用 Caller。
- Selector 选择 respond：不调用 Caller。
- Selector 选择 stop：不调用 Caller。

增加对应回归测试。

必须验证 Caller 不会在不需要工具调用的情况下被执行。

### Task 2：实现 DeepSeek API Client

实现真正可用的 DeepSeek API 客户端。

要求：

- 使用官方兼容的 Chat Completions 接口。
- 使用独立 HTTPX Client，并设置 `trust_env=False`，确保不读取系统代理环境变量。
- 不修改系统全局代理。
- 关闭 Thinking。
- 支持 JSON 输出。
- 支持 Native Tool Calls。
- 正确解析响应和 token usage。
- 对网络错误、超时、限流和格式错误进行分类。
- 实现有界重试，防止重复扣费。
- 保留原始请求和响应的必要审计信息，但不得记录密钥。

必须采用依赖注入，方便使用 Fake Client 进行无 API 测试。

### Task 3：实现四个真实 LLM 模块

实现：

1. DeepSeek Planner
2. DeepSeek Selector
3. DeepSeek Caller
4. DeepSeek Synthesizer

要求：

- 遵守现有模块接口。
- 保留原有 Mock 模块。
- Mock 和真实 LLM 模块能够通过统一接口切换。
- 不能使用硬编码答案代替模型输出。
- 每个模块都有独立输入、输出契约。
- 输出必须经过 JSON 或工具参数验证。
- Caller 必须遵守 tau2 工具权限和参数 Schema。
- 模块调用过程必须保留可复算轨迹。

不要为了赶进度而删除原来的 Mock 测试。

### Task 4：实现真实 tau2 Factorial Runner

目前 Mock Runner 不能作为真实实验运行器。

必须实现真实 tau2 Runner。

实验设计为四个二元模块，共 16 个配置：

2^4 = 16。

要求：

- 使用冻结的任务集和随机种子。
- 每个任务和 seed 必须执行全部 16 个配置。
- 保证配对实验设计。
- 正确 reset 环境。
- 使用真实 tau2 Orchestrator。
- 记录每个 episode 的完整轨迹。
- 记录任务成功、失败和超时。
- 记录所有 API 调用、token、成本和重试。
- 保留配置 manifest、代码 SHA 和任务版本。
- 不允许将 Mock 数据混入真实实验数据。

当前 Smoke 候选规模：

2 tasks × 2 seeds × 16 configurations = 64 episodes。

先实现完整 Runner 和无 API 测试，不要在本阶段执行付费 Smoke。

### Task 5：统计功效与实验协议复核

重新审计：

- 当前 task-level estimator。
- Nested seeds。
- 配对因子设计。
- Task-clustered bootstrap。
- Permutation test。
- Holm multiple-testing correction。
- Failure handling。
- Practical delta = 0.05。

检查此前功效分析与实际实验设计是否一致。

不能使用针对 delta=0.10 的分析冒充 delta=0.05 的功效分析。

如果样本量不足，提出可执行的修正方案，并保留原始协议版本。

### Task 6：完整无 API 测试

必须使用 Fake Client。

测试至少包括：

1. DeepSeek 请求参数正确。
2. Thinking 关闭。
3. JSON 解析成功。
4. JSON 格式错误。
5. Tool Calls 解析成功。
6. Tool Calls 参数不符合 Schema。
7. Caller 的 respond 分支。
8. Caller 的 stop 分支。
9. Caller 的 tool_call 分支。
10. API 超时。
11. 有界重试。
12. Token usage 统计。
13. 成本账本。
14. Model fingerprint 变化检测。
15. Runner 的 16 配置完整性。
16. Task/seed 配对一致性。
17. 轨迹和 manifest 完整性。
18. Mock 与真实运行数据隔离。
19. 代理绕过配置。
20. 无真实 API 请求的测试保证。

所有测试必须可以在没有 API Key、没有真实 API 调用的情况下运行。

## 五、实验推进原则

这项研究不能一直停留在工程修复和文档整理阶段。

必须遵循以下原则：

1. 一个小问题不能成为停止整个研究的理由。
2. 测试失败后，首先定位具体根因，然后修复并回归。
3. 如果某个机制没有提升，分析原因并设计下一轮改进实验。
4. 如果一种搜索策略效果不好，可以调整机制、搜索算子、Linkage 更新规则或候选生成方式。
5. 不允许编造提升数据。
6. 不允许因为一次 NO-GO 就终止整个研究。
7. 保留失败实验，利用失败结果寻找有效机制。
8. 优先寻找能够产生真实算法性能提升的方案。
9. 不要在没有可靠交互数据之前就急于实现复杂的完整演化算法。

我们的目标是找到有效的算法改进，而不是尽快宣布实验完成。

## 六、成本与安全限制

当前 DeepSeek 价格配置以高峰 cache-miss 价格作为保守预算：

- Input：$0.30 / 1M tokens。
- Output：$1.20 / 1M tokens。
- 每次请求预算上界：2000 input + 512 output。
- 64 Episode Smoke 预算上界：约 $4.66。
- 全部请求重试一次的极端预算上界：约 $9.33。

当前硬限制：

- Smoke cap：$80。
- Pilot cap：$400。

必须按照实际 API usage 计算成本，不能只使用理论 token 上限。

**重要：本阶段不允许产生任何真实付费 API 请求。**

只有 Phase 0C 实现、测试、Runner 验证和独立审查全部完成后，才能向用户申请 Smoke 执行批准。

## 七、仓库维护要求

每完成一个有意义的阶段，必须更新：

- `STATUS.md`
- `NEXT_STEPS.md`
- `docs/HANDOFF.md`
- `docs/RESEARCH_LOG.md`
- `docs/EXECUTOR_PROMPT_PHASE0C.md`

必须确保：

1. 下一位执行 Agent 能够准确知道当前仓库、分支和 HEAD。
2. 知道哪些任务已经完成。
3. 知道哪些测试真实通过。
4. 知道哪些实验尚未执行。
5. 知道下一步具体执行什么。
6. 知道哪些操作禁止执行。
7. 记录所有重要实验结果和提交 SHA。

每次提交后核实远端分支与本地 HEAD 一致。

不能只更新文档而不推进代码。

## 八、最终验收标准

Phase 0C 完成时，必须提供：

1. 仓库和分支状态。
2. 起始 SHA 和最终 SHA。
3. 修改文件列表。
4. DeepSeek Client 实现说明。
5. 四个模块实现说明。
6. Caller 修复结果。
7. 真实 tau2 Runner 实现结果。
8. 无 API 测试结果。
9. 完整回归测试结果。
10. 统计功效分析结果。
11. GitHub Actions CI 结果。
12. 独立审查结果。
13. 当前成本与安全状态。
14. 下一阶段具体实验方案。
15. 更新后的接手提示词。

不要把代码实现成功等同于算法创新成功。

## 九、Phase 0C 完成后的下一阶段

不要重新回到文献整理和泛泛的方案讨论。

Phase 0C 通过后，按以下顺序推进：

**Phase 1：真实模块交互实验**

使用 DeepSeek Flash 和 tau2 环境，运行完整 16 配置因子实验，分析四个模块之间的交互效应。

**Phase 2：Linkage Learning**

利用真实实验数据构建模块交互图，研究：

- 交互效应估计。
- 交互强度和方向。
- 任务条件化 Linkage。
- 动态 Linkage 更新。
- 不确定性交互关系处理。

**Phase 3：Cooperative Co-evolution**

设计由 Linkage Graph 引导的协同演化机制：

- 独立模块变异。
- 联合模块变异。
- Linkage-aware crossover。
- 自适应分组。
- 动态协同搜索。

**Phase 4：算法提升实验**

与公平基线比较：

- Independent Evolution。
- Fixed-group Cooperative Co-evolution。
- Conventional Cooperative Co-evolution。
- NIL-CCEA。

重点检验是否真正提高 Agent 的任务成功率、交互结构学习质量和搜索效率。

---

## 十、现在立即执行

不要再向我汇报一份新的长篇计划。

现在：

1. 拉取并核实最新仓库。
2. 阅读 `docs/EXECUTOR_PROMPT_PHASE0C.md`。
3. 对照真实代码检查任务。
4. 从 Task 1 开始直接修改代码。
5. 完成一个模块就运行对应测试。
6. 继续推进，不要遇到小问题就停止。
7. 完成后提交、推送并更新全部接手文档。

如果发现现有协议与真实代码不一致，以实际代码、测试和可复现证据为准，先查明差异，再修正协议。

**最终目标：尽快打通 DeepSeek Flash + tau2 真实实验执行链路，让 NIL-CCEA 从工程准备正式进入算法实验。**
