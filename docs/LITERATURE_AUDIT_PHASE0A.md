# Phase 0A 文献审计

**审计日期**：2026-11-19
**审计范围**：Agent 模块搜索、工具策略演化、模块化组合、差分分组、linkage learning、合作协同演化、噪声黑盒优化，以及 2024—2026 年相邻的 Agent workflow evolution。
**证据规则**：论文正式版本或作者公开稿、补充材料、官方代码和官方 benchmark 文档优先。搜索摘要只用于定位来源，不能单独支撑机制结论。

## 1. 审计结论摘要

1. **EvoTool 是当前最近邻**。它已经采用 Planner、Selector、Caller、Synthesizer 四模块、轨迹记录、梯度无关演化、单模块定向突变和多样性选择。它的核心信号是轨迹归因，不是通过成对干预估计模块间非加性交互，也没有公开 signed、uncertainty-aware、task-conditioned linkage graph。
2. **AgentSquare 是模块搜索方向的直接先例**。它用 Planning、Reasoning、Tool Use、Memory 四类统一接口模块，执行模块演化和模块重组，并用 in-context predictor 跳过候选评估。论文和官方代码没有把模块交互表示成带不确定性的交互图。
3. **AgentSpec 证明了受控组合和交互分析的可行性**。它把 embodied agent 表示成 Perception、Memory、Reasoning、Reflection、Action 以及可选 Learning 的 typed composition，并提供可替换实现和轨迹记录。它是组合测量平台，不是合作协同演化算法。
4. **DG、DG2、RDG、RDG2 与 LMM 提供了交互检测和噪声处理的机制先例**。DG2 用逐对变量的非线性差异和自适应 round-off threshold，RDG 用递归集合检测降低评估次数，RDG2 为 RDG 引入自适应阈值，LMM 将分组本身作为组合优化问题处理噪声。它们的对象是数值黑盒变量，不能直接等同于 LLM 模块交互。
5. **当前不能声称“首次提出模块交互图驱动的 Agent 演化”**。已有工作已经明确讨论模块组合质量、交互效应或模块定向演化。可检验的差异只能落在交互估计协议、符号和不确定性表示、任务条件化、以及在统一预算下的 linkage-aware cooperative evolution。

## 2. 已核验来源

| 编号 | 准确标题与作者 | 年份、状态、标识 | 主要来源与官方代码 | 核验结果 |
|---|---|---|---|---|
| L1 | **AgentSquare: Automatic LLM Agent Search in Modular Design Space**，Yu Shang、Yu Li、Keyu Zhao、Likai Ma、Jiahe Liu、Fengli Xu、Yong Li | ICLR 2025；arXiv:2410.06153 | [ICLR 正式稿](https://proceedings.iclr.cc/paper_files/paper/2025/file/0ae94013da7cd459402fd77874e09ee3-Paper-Conference.pdf)；[官方代码](https://github.com/tsinghua-fib-lab/AgentSquare) | 已核验论文、代码仓库和模块接口说明 |
| L2 | **EVOTOOL: Self-Evolving Tool-Use Policy Optimization in LLM Agents via Blame-Aware Mutation and Diversity-Aware Selection**，Shuo Yang、Caren Han、Xueqi Ma、Yan Li、Mohammad Reza Ghasemi Madani、Eduard Hovy | ACL 2026；DOI:10.18653/v1/2026.acl-long.2016；arXiv:2603.04900 | [ACL Anthology](https://aclanthology.org/2026.acl-long.2016/)；[官方代码](https://github.com/SYang2000/ACL_2026_EvoTool) | 已核验正式论文、附录、项目页和代码 |
| L3 | **AgentSpec: Understanding Embodied Agent Scaffolds Through Controlled Composition**，Jixuan Chen 等 13 位作者 | 2026；arXiv:2606.14674；截至审计日为预印本 | [arXiv](https://arxiv.org/abs/2606.14674)；[官方代码](https://github.com/chenjix/AgentSpec)；[官方文档](https://agentspec-embodied.github.io/docs.html) | 已核验论文摘要、仓库 README、文档和模块替换示例。同行评审状态未找到独立正式记录，标记为 UNVERIFIED |
| L4 | **Cooperative Co-Evolution With Delta Grouping for Large Scale Non-Separable Function Optimization**，Mohammad Nabi Omidvar、Xiaodong Li、Xin Yao | CEC 2010；DOI:10.1109/CEC.2010.5585979 | [作者/机构记录](https://research.birmingham.ac.uk/en/publications/cooperative-co-evolution-with-delta-grouping-for-large-scale-non-/) | 已核验 delta grouping 前驱 |
| L5 | **Cooperative Co-evolution with Differential Grouping for Large Scale Optimization**，Mohammad Nabi Omidvar、Xiaodong Li、Yi Mei、Xin Yao | IEEE TEVC 2014；DOI:10.1109/TEVC.2013.2281543 | [论文预印本](https://titan.csit.rmit.edu.au/~e46507/publications/differntialGrouping-tevc.pdf)；[代码线索](https://bitbucket.org/mno/differential-grouping) | 已核验 DG 定义、CC 分解与评估逻辑 |
| L6 | **DG2: A Faster and More Accurate Differential Grouping for Large-Scale Black-Box Optimization**，Mohammad Nabi Omidvar、Ming Yang、Yi Mei、Xiaodong Li、Xin Yao | IEEE TEVC 2017；DOI:10.1109/TEVC.2017.2694221 | [作者公开稿](https://titan.csit.rmit.edu.au/~e46507/publications/dg2-omidvar-tevc-17.pdf) | 已核验 raw interaction matrix、round-off threshold、连接分组和成本 |
| L7 | **A Recursive Decomposition Method for Large Scale Continuous Optimization**，Yuan Sun、Michael Kirley、Saman K. Halgamuge | IEEE TEVC 2018 卷期；DOI:10.1109/TEVC.2017.2778089 | [作者公开稿](https://openresearch-repository.anu.edu.au/server/api/core/bitstreams/6aa1cbb3-1ad1-41ec-aee2-8f1ec1f47b98/content) | 已核验 RDG 的递归集合检测与 (O(n\log n)) 评估目标 |
| L8 | **Adaptive Threshold Parameter Estimation with Recursive Differential Grouping for Problem Decomposition**，Yuan Sun、Mohammad Nabi Omidvar、Michael Kirley、Xiaodong Li | GECCO 2018；DOI:10.1145/3205455.3205483 | [GECCO 论文](https://www.cmap.polytechnique.fr/~nikolaus.hansen/proceedings/2018/GECCO/proceedings/proceedings_files/pap197s3-file1.pdf) | 已核验 RDG2 的 round-off upper bound 和自适应阈值 |
| L9 | **Cooperative coevolutionary differential evolution with linkage measurement minimization for large-scale optimization problems in noisy environments**，Rui Zhong、Enzhi Zhang、Masaharu Munetomo | Complex & Intelligent Systems 2022；DOI:10.1007/s40747-022-00957-6 | [Springer 正式页](https://link.springer.com/article/10.1007/s40747-022-00957-6) | 已核验 LMM、噪声失效分析和显式重评估讨论 |
| L10 | **A Cooperative Coevolutionary Approach to Function Optimization**，Mitchell A. Potter、Kenneth A. De Jong | PPSN 1994；DOI:10.1007/3-540-58484-6_269 | [作者公开稿](https://cs.gmu.edu/~mpotter/pubs/ppsn94.pdf) | 已核验合作子种群、上下文协作和基础 CC 架构 |
| L11 | **The Linkage Tree Genetic Algorithm**，Dirk Thierens | PPSN 2010；DOI:10.1007/978-3-642-15844-5_27 | [DBLP](https://dblp.org/rec/conf/ppsn/Thierens10.html) | 已核验层次 linkage tree 和按树节点重组 |
| L12 | **τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains**，Shunyu Yao、Noah Shinn、Pedram Razavi、Karthik Narasimhan | 2024；arXiv:2406.12045 | [旧仓库](https://github.com/sierra-research/tau-bench)；旧仓库 README 明确提示任务已过时 | 作为 benchmark 来源核验，不能使用旧任务做正式实验 |
| L13 | **τ²-Bench: Evaluating Conversational Agents in a Dual-Control Environment**，Victor Barres、Honghua Dong、Soham Ray、Xujie Si、Karthik Narasimhan | 2025；arXiv:2506.07982；当前仓库发布 v1.0.1 | [当前仓库](https://github.com/sierra-research/tau2-bench)；[运行文档](https://github.com/sierra-research/tau2-bench/blob/main/docs/running-the-benchmark.md) | 已核验任务冻结、版本 pin、reset/resume、轨迹保存和评分语义 |
| L14 | **EvoAgentX: An Automated Framework for Evolving Agentic Workflows**，Yingxu Wang、Siwei Liu、Jinyuan Fang、Zaiqiao Meng | EMNLP 2025 Demo；DOI:10.18653/v1/2025.emnlp-demos.47 | [ACL Anthology](https://aclanthology.org/2025.emnlp-demos.47/)；[官方代码](https://github.com/EvoAgentX/EvoAgentX) | 已核验平台层、workflow topology 与 TextGrad/AFlow/MIPRO 集成 |
| L15 | **AgentEvo: cost-aware agentic workflow generation via adaptive multi-stage evolution**，Bo Xiao、Haiyang Liu、Yitong Wang、Yanning Hou、Ke Xu、Xingyi Zhang 等 | 2026；DOI:10.1007/s40747-026-02325-0 | [Springer 正式页](https://doi.org/10.1007/s40747-026-02325-0) | 已核验多阶段演化、Pareto archive 和性能—token 成本目标。它是成本多目标工作，不能作为 NIL-CCEA 的方法主线 |
| L16 | **Cooperative Coevolution for Resource-Constrained Agentic LLM Post-Training**，Zhiyuan Wang、Shengcai Liu、Jiahao Wu、Ning Lu、Hui Ouyang、Shaofeng Zhang、Haoze Lv、Ke Tang | 2026；arXiv:2608.02391 | [arXiv](https://arxiv.org/abs/2608.02391)；[代码](https://github.com/MetaronWang/CoPES) | 已核验其对象是模型参数子空间和 post-training，不是 Agent 模块组合 |
| L17 | **AgenticEvolve: Evolutionary Program Search with Persistent Language Model Agents that Design and Run Experiments**，Ze-Yu Peng、Qing-Yu Lan、Zhan-He Wang、Jun Zhang、Yun-Song Piao | 2026；arXiv:2610.31326 | [arXiv](https://arxiv.org/abs/2610.31326)；[代码](https://github.com/pengzy-cosmo/AgenticEvolve) | 已核验持久 Agent、岛模型、实验设计与程序搜索。与模块 linkage 只存在方法层相邻关系 |
| L18 | **ToolSandbox: A Stateful, Conversational, Interactive Evaluation Benchmark for LLM Tool Use Capabilities**，Jiarui Lu 等 | 2024；arXiv:2408.04682 | [论文](https://arxiv.org/abs/2408.04682)；[官方代码](https://github.com/apple-aiml-research/ToolSandbox) | 已核验状态化工具、里程碑 DAG、完整 execution context 和轨迹保存 |

## 3. 机制级横向比较

| 工作 | 优化对象与搜索空间 | 交互/依赖检测 | 分组或结构 | 演化算子 | 噪声处理 | 预算与评估 |
|---|---|---|---|---|---|---|
| AgentSquare | 四类 Agent 模块的代码/提示规格，模块组合与新模块 | 没有显式成对交互估计；依靠历史候选性能和 predictor | 模块重组，非 learned linkage graph | module evolution、module recombination、LLM meta-prompt | 通过 predictor 跳过候选，未把执行噪声建模为交互不确定性 | ALFWorld、WebShop、M3ToolEval、SciWorld 等，搜索脚本记录 test count，但论文未把所有探测与失败统一成 NIL-CCEA 式账本 |
| EvoTool | 四个工具策略模块的自然语言 prompt specification，基模冻结 | 轨迹诊断由 Blamer LLM 给模块 blame score，不是 factorial interaction contrast | 固定四槽组合，人口池保留互补候选 | 只编辑被 blame 的一个模块，按 batch gate 接受，diversity-aware selection | 依赖轨迹和诊断反馈，未提供统计不确定性或 signed linkage | 训练池、选择集、四个 benchmark；论文附录给出每代 mini-batch 和最大代数，官方代码保存 run log |
| AgentSpec | typed embodied agent slots，Perception/Memory/Reasoning/Reflection/Action/可选 Learning | 通过配置网格和交互热图分析组合效应，未见 linkage graph 学习 | 受控模块组合 | 主要是配置替换和受控消融，不是合作协同演化 | 通过固定环境、模型、seed 和 trajectory logging 控制比较，未形成噪声图模型 | DeliveryBench、ALFRED、MiniGrid、RoboTHOR，文档说明轨迹和指标写入 artifacts |
| DG | 连续黑盒决策变量 | 比较两次差分是否超过固定 \(\epsilon\) | 连接分量 | CC 子问题优化 | 对 round-off 敏感，固定阈值 | 评估次数随变量数增长，主要数值 benchmark |
| DG2 | 连续黑盒决策变量 | raw interaction matrix \(\Lambda\)，逐对检测；按 round-off 自适应 \(\epsilon\) | 由 adjacency matrix 的 connected components 得到分组，可表达重叠结构的检测结果 | CC 中交替优化分组 | 处理浮点 round-off，未处理随机执行噪声 | 通过复用 sample points 降低 FE，论文明确讨论完全可分问题和不平衡组件 |
| RDG | 连续黑盒决策变量 | 一个变量与变量集合之间的非线性差异 | 对剩余集合递归二分 | CC | 使用全局阈值，依赖参数 \(\alpha\)，对不平衡和噪声敏感 | 目标为小于 \(6n\log n\) 的分解 FE |
| RDG2 | 连续黑盒决策变量 | RDG 检测 + 基于 round-off upper bound 的自适应阈值 | RDG 递归结构 | CC | 改善 round-off 和组件尺度不平衡，仍不是随机 LLM noise 模型 | GECCO 2018 报告与 RDG、DG2 的分解准确率和 CC 优化比较 |
| LMM | 连续黑盒决策变量的分组编码 | 把 linkage measure 作为组合优化目标，由 EGA 搜索分组 | 染色体编码的子问题分配 | EGA 优化 LMF，MDE-DS 优化子问题 | 明确针对乘性噪声，讨论显式重复评估可降低标准误 | 评估预算可控，实验使用 25 次重复计算分解准确率 |
| LTGA/GOMEA | 离散或实值变量 | 从群体统计或局部结构学习 linkage tree | 层次 FOS/linkage tree | 按树节点做 optimal mixing 或 gene-pool mixing | 经典工作主要假设可观测 fitness，后续工作单独处理灰盒和噪声 | 以函数评估效率和可分结构为主 |
| EvoAgentX | 多 Agent workflow、提示、工具配置和 topology | 不学习模块交互图，集成 TextGrad、AFlow、MIPRO | workflow graph | prompt、tool、topology 的迭代优化 | 平台记录评估，但论文机制不是噪声统计 | HotPotQA、MBPP、MATH、GAIA |
| AgentEvo | 可执行 workflow operators、nodes 和 workflow code | 不做模块 DiD，维护性能—token cost Pareto archive | workflow structure | exploration、refinement、crossover 三阶段 | 将 token cost 纳入目标，不等同执行噪声 | MATH、GSM8K、HumanEval、MBPP，明确成本目标 |
| CoPES | Qwen3.5 agent 的参数子空间 | 参数空间分解，不是 Agent 模块交互 | cooperative parameter subspaces | ES/CC 搜索子空间 | 研究 GPU/训练成本，不是 rollout noise | post-training 与 GPU-hour 比较 |
| AgenticEvolve | 程序候选和持久 Agent 岛 | Agent 设计实验辅助候选变异，不是模块图 | 岛模型和 archive | persistent agent 选择父代、实验、提交候选 | 以程序评估为主，未提供模块级不确定交互估计 | 以 evaluations 和 dollar cost 报告 |

## 4. 最近邻排序与重叠风险

### 4.1 第一近邻：EvoTool

**相同点**：四模块工具策略、冻结基模、梯度无关演化、轨迹记录、任务成功信号、只变异一个模块的候选更新。
**差异**：EvoTool 用 blame attribution 选择要变异的模块，NIL-CCEA 的核心假设是先用成对 factorial interventions 估计非加性交互，再决定模块分组和 cooperative variation。EvoTool 的 blame score 是模块责任归因，不是 (f(1,1)-f(1,0)-f(0,1)+f(0,0)) 的交互效应。论文和代码中尚未找到 signed、uncertainty-aware、task-conditioned linkage graph。
**风险**：如果 NIL-CCEA 只实现“模块级变异 + 轨迹诊断”，与 EvoTool 的机制重叠很高，不能以不同名称主张创新。

### 4.2 第二近邻：AgentSquare

**相同点**：把 Agent 设计抽象为统一接口模块，搜索模块组合并使用演化式候选生成。
**差异**：AgentSquare 的模块演化主要是 LLM meta-prompt 产生新模块，模块重组由 LLM 根据候选描述建议组合，性能 predictor 过滤候选。NIL-CCEA 需要把交互测量作为独立统计对象，并用带符号和不确定性的 linkage 结构驱动后续算子。
**风险**：只做组合搜索、模块重组或 predictor 将落入 AgentSquare 的已知范围。

### 4.3 第三近邻：AgentSpec

**相同点**：显式 typed module contract、可替换实现、相同环境和模型下的组合比较，并报告模块交互。
**差异**：AgentSpec 重点是 embodied scaffold 的 controlled composition 和分析，不是通过交互图进行演化搜索。NIL-CCEA 可复用其接口和轨迹审计思想，但必须把优化目标和算子实现为演化计算主线。
**风险**：如果实验只做模块组合热图而没有公平预算下的演化比较，就只是 AgentSpec 风格消融。

### 4.4 第四近邻：DG2/RDG/RDG2/LMM 与 linkage learning

**相同点**：都把变量之间的非可分性作为分组依据，并关注检测成本、阈值和分组对 CC 的影响。
**差异**：NIL-CCEA 的变量是带行为和状态的 Agent 模块配置，观测值是带执行随机性的任务结果。交互必须估计正负方向、置信区间和任务族异质性。DG2 的 round-off threshold 不能直接当成 LLM rollout uncertainty，LMM 的组合优化分组也不等同 signed graph。
**风险**：把 DG2 改成“对模块编号做差分”而不处理任务聚类、随机轨迹和高阶交互，只是算法名称替换。

### 4.5 第五近邻：AgentEvo、EvoAgentX、AgenticEvolve、CoPES

这些工作覆盖 workflow 演化、成本 Pareto 搜索、持久 Agent 程序搜索或参数子空间 CC。它们说明 2025—2026 年 Agent 演化和 cooperative evolution 已经很活跃，也意味着 NIL-CCEA 必须明确对象是模块组合交互，而不是成本优化、workflow topology 搜索、模型权重 post-training 或一般程序搜索。

## 5. 可以主张与暂时不能主张的差异

### 当前可以主张为研究假设的差异

- 对 Agent 模块采用成对 factorial intervention，并在固定其他模块的条件下估计非加性交互。
- 把交互效应的符号、区间和任务族条件化结果放入 linkage graph，而不是只输出单一模块 blame 或静态分组。
- 对正向、负向和不确定边使用不同的 group-wise variation、compatibility-aware search 和诊断策略。
- 在相同总 Agent-execution budget 下，把 linkage 探测、失败调用和重试显式计入比较，并与独立变异、随机分组、固定分组和无 linkage CC 对照。

### 目前不能主张

- 不能主张首次进行 Agent 模块组合搜索。
- 不能主张首次使用 Planner、Selector、Caller、Synthesizer 四模块。
- 不能主张已有方法完全忽视模块交互。AgentSpec 明确分析交互，EvoTool 明确处理跨模块错误归因。
- 不能主张噪声下交互检测已经解决。LMM 说明 DG 类方法在乘性噪声下会失效，LLM rollout 噪声还包含用户模拟器、工具失败和模型采样。
- 不能把交互测量可靠写成搜索性能提升。后者必须由公平预算的演化对照实验支持。

## 6. 未解决条目与下一步检索词

| 条目 | 当前状态 | 下一步 |
|---|---|---|
| AgentSpec 正式发表状态 | UNVERIFIED，当前证据为 arXiv 与官方仓库 | 检索 ACL/ICLR/ICML/CoRL 2026 proceedings 和版本历史 |
| EvoTool 的补充材料和完整成本表 | 论文附录已读，需逐项复算每类 LLM 调用的计费口径 | 从代码 run log 和 ACL checklist 提取调用类型、失败与重试 |
| tau2-bench v1.0.1 的 task family 元数据 | 官方 manifest 和 domain 文档已核验，NIL-CCEA 仍需锁定具体 12 个 task IDs | 在 adapter smoke 中保存 task ID、binding revision 和 domain 标签 |
| LLM Agent 的 signed linkage 直接先例 | 未找到与本项目完全重叠的主来源 | 检索 `signed interaction graph LLM agent`, `uncertainty linkage agent module`, `task-conditioned module interaction evolutionary agent` |
| 高阶交互与任务族异质性 | 研究设计中保留，尚未实验验证 | 预注册三阶诊断和 task-clustered bootstrap sensitivity |

## 7. 参考来源索引

- AgentSquare 论文第 1 节和第 2 节定义 MoLAS、四模块和 module evolution/recombination；官方仓库 `modules/README.md` 给出 Planning、Reasoning、ToolUse、Memory 接口。
- EvoTool 论文第 4 节和附录 Algorithm 1 给出 blame、targeted mutation、population selection、训练池/选择集和预算参数；ACL 正式记录确认 2026 年会议状态与 DOI。
- AgentSpec 官方文档给出 typed interfaces、模块交换、`env.reset()`、`agent.reset()`、逐步轨迹和 artifacts 输出。
- DG2 正式稿第 III 节给出 raw interaction structure matrix、round-off threshold 和 connected components。
- RDG 正式稿摘要和算法给出集合级递归检测与评估复杂度目标。
- RDG2 论文第 1 节和第 3 节给出 RDG 全局阈值的局限及自适应 round-off upper bound。
- LMM 正式页第 Introduction、Our proposal 和 Discussion 说明 DG 类方法在乘性噪声下的失效、LMF 组合优化和显式重复评估。

**结论**：Phase 0A 的近邻机制已经足以否定“模块搜索本身”或“四模块划分本身”的新颖性叙述，但没有否定 NIL-CCEA 的可检验假设。后续必须把贡献压缩为可复算的交互估计、带不确定性的 linkage 决策和公平预算下的合作协同演化结果。
