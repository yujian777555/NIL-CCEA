# Literature Ledger

**状态说明**：本表已从初始候选队列升级为 Phase 0A 审计索引。`VERIFIED` 表示论文主来源和官方代码或官方 benchmark 文档已核验。`UNVERIFIED` 表示仍缺少发表状态、补充材料或可复算实现证据。详细机制比较见 [LITERATURE_AUDIT_PHASE0A.md](LITERATURE_AUDIT_PHASE0A.md)。

| ID | 工作 | 对象 | 主来源 | 官方代码 | 状态 | NIL-CCEA 相关性 |
|---|---|---|---|---|---|---|
| L1 | AgentSquare | 模块化 LLM Agent 设计搜索 | [ICLR 2025 正式稿](https://proceedings.iclr.cc/paper_files/paper/2025/file/0ae94013da7cd459402fd77874e09ee3-Paper-Conference.pdf)；arXiv:2410.06153 | [tsinghua-fib-lab/AgentSquare](https://github.com/tsinghua-fib-lab/AgentSquare) | VERIFIED | 最近邻，模块演化、重组和 predictor |
| L2 | EVOTOOL | 工具策略模块演化 | [ACL 2026](https://aclanthology.org/2026.acl-long.2016/)；DOI:10.18653/v1/2026.acl-long.2016 | [SYang2000/ACL_2026_EvoTool](https://github.com/SYang2000/ACL_2026_EvoTool) | VERIFIED | 最近邻，四模块和单模块定向突变 |
| L3 | AgentSpec | embodied Agent typed composition | [arXiv:2606.14674](https://arxiv.org/abs/2606.14674) | [chenjix/AgentSpec](https://github.com/chenjix/AgentSpec) | VERIFIED，发表状态 UNVERIFIED | 最近邻，接口、组合和交互分析 |
| L4 | DG | 连续黑盒变量交互和 CC 分组 | [TEVC 2014 预印本](https://titan.csit.rmit.edu.au/~e46507/publications/differntialGrouping-tevc.pdf)；DOI:10.1109/TEVC.2013.2281543 | [bitbucket differential-grouping](https://bitbucket.org/mno/differential-grouping) | VERIFIED | 交互检测基线 |
| L5 | DG2 | 逐对交互、round-off threshold 和连接分组 | [IEEE 2017 公开稿](https://titan.csit.rmit.edu.au/~e46507/publications/dg2-omidvar-tevc-17.pdf)；DOI:10.1109/TEVC.2017.2694221 | 未定位到作者维护的独立仓库 | VERIFIED | 变量 linkage 和阈值先例 |
| L6 | RDG | 集合级递归交互检测 | [IEEE 2018 公开稿](https://openresearch-repository.anu.edu.au/server/api/core/bitstreams/6aa1cbb3-1ad1-41ec-aee2-8f1ec1f47b98/content)；DOI:10.1109/TEVC.2017.2778089 | 未定位到作者维护的独立仓库 | VERIFIED | 低评估次数分组先例 |
| L7 | RDG2 | RDG 自适应 round-off threshold | [GECCO 2018](https://www.cmap.polytechnique.fr/~nikolaus.hansen/proceedings/2018/GECCO/proceedings/proceedings_files/pap197s3-file1.pdf)；DOI:10.1145/3205455.3205483 | 未定位到作者维护的独立仓库 | VERIFIED | 噪声/阈值处理先例 |
| L8 | LMM | 噪声黑盒中的 linkage measurement minimization | [Springer 2022](https://link.springer.com/article/10.1007/s40747-022-00957-6)；DOI:10.1007/s40747-022-00957-6 | 未定位到作者维护的独立仓库 | VERIFIED | 噪声交互检测和预算控制先例 |
| L9 | Cooperative coevolution | 合作子种群和上下文协作 | [Potter & De Jong 1994](https://cs.gmu.edu/~mpotter/pubs/ppsn94.pdf)；DOI:10.1007/3-540-58484-6_269 | 不适用 | VERIFIED | 演化主线基础 |
| L10 | Linkage Tree Genetic Algorithm | 层次 linkage 与重组 | [DBLP](https://dblp.org/rec/conf/ppsn/Thierens10.html)；DOI:10.1007/978-3-642-15844-5_27 | 未作为本项目依赖 | VERIFIED | group-wise crossover 先例 |
| L11 | EvoAgentX | Agentic workflow 平台和演化优化 | [EMNLP 2025 Demo](https://aclanthology.org/2025.emnlp-demos.47/)；DOI:10.18653/v1/2025.emnlp-demos.47 | [EvoAgentX/EvoAgentX](https://github.com/EvoAgentX/EvoAgentX) | VERIFIED | workflow 演化邻域 |
| L12 | AgentEvo | workflow 的性能—token cost Pareto 演化 | [Springer 2026](https://doi.org/10.1007/s40747-026-02325-0)；DOI:10.1007/s40747-026-02325-0 | 未定位到与论文绑定的官方仓库 | VERIFIED | 成本多目标邻域，非本项目主线 |
| L13 | CoPES | Agent 模型参数子空间 CC | [arXiv:2608.02391](https://arxiv.org/abs/2608.02391) | [MetaronWang/CoPES](https://github.com/MetaronWang/CoPES) | VERIFIED | 参数 post-training 邻域，排除出模块搜索主线 |
| L14 | AgenticEvolve | 持久 Agent 岛模型程序搜索 | [arXiv:2610.31326](https://arxiv.org/abs/2610.31326) | [pengzy-cosmo/AgenticEvolve](https://github.com/pengzy-cosmo/AgenticEvolve) | VERIFIED | 演化程序搜索邻域 |
| L15 | τ-bench | 旧版工具—用户交互 benchmark | [旧仓库](https://github.com/sierra-research/tau-bench)；arXiv:2406.12045 | [sierra-research/tau-bench](https://github.com/sierra-research/tau-bench) | VERIFIED，但任务过时 | 只用于定位历史来源，禁止用于正式实验 |
| L16 | τ²-bench / τ³-bench | 当前文本和语音 benchmark | [当前仓库](https://github.com/sierra-research/tau2-bench)；arXiv:2506.07982 | 同上 | VERIFIED | Phase 0A 主环境候选，锁定 v1.0.1 |
| L17 | ToolSandbox | 本地状态化工具和里程碑评估 | [论文](https://arxiv.org/abs/2408.04682) | [apple-aiml-research/ToolSandbox](https://github.com/apple-aiml-research/ToolSandbox) | VERIFIED | 本地受控诊断备选 |

## 机制审计状态

- AgentSquare、EvoTool、AgentSpec 已完成主来源和官方代码核验。
- DG、DG2、RDG、RDG2、LMM 已完成论文机制和噪声/阈值证据核验。
- 合作协同演化和 linkage tree 已完成基础来源核验。
- 2025—2026 邻域已补充 EvoAgentX、AgentEvo、CoPES、AgenticEvolve。它们的机制与 NIL-CCEA 的模块交互图主线不同，仍需在最终算法比较前做针对性复现差异记录。
- AgentSpec 的同行评审发表状态仍是 `UNVERIFIED`，当前只能以 2026 arXiv 预印本和官方代码引用。

## 仍需核验

1. EvoTool 代码中每类调用的精确 token/美元成本和失败重试口径。
2. tau2-bench v1.0.1 选定 task IDs 的 task family 标签和 binding revision。
3. AgentSpec 是否在 2026 年后续版本或会议版本中改变模块集合和评估协议。
4. 2024—2026 是否出现直接使用 signed、uncertainty-aware、task-conditioned Agent module linkage graph 的工作。

## 下一步检索词

`"signed interaction graph" LLM agent`, `"uncertainty-aware linkage" agent module`, `"task-conditioned" module interaction evolutionary agent`, `agent scaffold interaction effect evolutionary search`, `trajectory factorial intervention LLM agent`, `cooperative coevolution modular agent`。
