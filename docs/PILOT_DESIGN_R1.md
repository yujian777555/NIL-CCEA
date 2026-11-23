# NIL-CCEA Pilot Design R1

**状态**：Phase 0B 统计修订后的冻结候选协议。正式 benchmark 仍未运行。
**环境候选**：τ²-bench `v1.0.1` text-v1。
**目标**：先验证四模块交互测量、轨迹审计和成本账本，再决定是否进入 linkage-aware cooperative evolution。

## 1. 研究问题

在固定 Agent backbone、工具权限、task、environment seed 和评分器条件下，Planner、Selector、Caller、Synthesizer 的二元变体是否产生可重复的非加性任务成功效应。若存在，带符号和不确定性的 linkage 是否能在等总 Agent-execution budget 下指导合作协同演化。

## 2. 候选实验因素

| 槽位 | 0 变体 | 1 变体 | 机制差异 |
|---|---|---|---|
| Planner | `planner.p0` | `planner.p1` | 线性子目标序列 vs 前置条件状态依赖图 |
| Selector | `selector.s0` | `selector.s1` | 直接 schema 匹配 vs 前置条件门控 |
| Caller | `caller.c0` | `caller.c1` | 直接参数抽取 vs 校验后一次修复 |
| Synthesizer | `synthesizer.y0` | `synthesizer.y1` | 证据优先总结 vs 状态对账清单 |

四槽位完整组合为 (2^4=16)。若 adapter smoke 证明某槽位不能独立替换，必须先修改模块契约和本协议，再减少到 (2^m)。

## 3. 任务和配对

- 正式候选任务集固定为 retail `[5, 9, 12, 17, 18, 26]` 与 airline `[2, 6, 8, 13, 16, 18]`，均来自 v1.0.1 的 `test` split。
- 每个 task 使用两个固定 seed `0` 和 `1`。独立统计 cluster 是 12 个 task，两个 seed 是 task 内重复测量。
- 16 个配置在完全相同的 task ID、task version、language、domain、binding revision、trial 和 resolved seed 下运行。
- 运行顺序由固定伪随机排列生成，排列种子写入 manifest。配置顺序不能根据中间结果改变。
- 同一 task 内的两个 seed 先分别形成完整 factorial contrast，再在 task 内平均。bootstrap 只重采样 12 个 task，不能把 seed 或配置当成独立 cluster。

## 4. 终点

### 主终点

`environment_reward`，取 tau2 原生 `EvaluationType.ENV` 的 DB 与 environment assertion 评分。完整 task reward、COMMUNICATE 和 NL_ASSERTION 作为次要诊断，主实验不调用额外 LLM judge。

### 次要终点

- tool-call schema validity；
- tool-call count 和 execution steps；
- constraint violation / invalid argument count；
- agent、user simulator、judge 的 input/output token；
- provider request cost、wall time、timeout、retry；
- 轨迹长度和终止原因。

不得在观察结果后把次要终点加权成新的主终点。

## 5. 交互估计

对模块对 (i,j)，在其他两个槽位配置 (z) 固定时计算

\[
I_{ij}(z)=\mu(1,1,z)-\mu(1,0,z)-\mu(0,1,z)+\mu(0,0,z).
\]

在所有其他槽位上下文上平均得到

\[
I_{ij}=\frac{1}{4}\sum_z I_{ij}(z).
\]

每个 task-seed 计算完整四上下文 contrast，再对两个 seed 求 task-level 平均。以 task 为重采样单位估计 95% bootstrap interval。不能把同一 task 的两个 seed 或 16 个配置视为独立 task。

### 交互状态

- `POSITIVE`：区间上界和下界均在预先定义的正向实用区域之外；
- `NEGATIVE`：区间完全落入负向实用区域；
- `WEAK`：区间完全落入实用等价区间；
- `UNCERTAIN`：样本不足或区间跨越实用等价区间。

`UNCERTAIN` 不得折叠成 `WEAK` 或独立关系。

### 多重比较

四个模块共有六个 pairwise tests。正式冻结前登记 practical threshold \(\delta\) 和 Holm step-down correction。任务族估计作为预先声明的异质性分析，样本不足时只报告区间，不做显著性结论。

## 6. 预算和成本

冻结计划为 12 tasks × 2 seeds × 16 configurations = 384 episodes。每个 episode 需要记录 agent、user simulator、失败调用和 retry。主终点使用 ENV evaluator，不产生 judge 调用。

正式 pilot 前必须完成：

1. 使用 mock runner 测量每个配置的最大模块调用次数和失败路径；
2. 固定 agent/user 为 `openai/gpt-4.1-2025-04-14`，temperature 0.0，max_steps 30；主终点评估类型固定为 `ENV`；
3. 每个 provider request 允许最多一次基础设施 retry，agent task failure 不重试，基础设施 retry 全部计入预算；
4. 在价格验证完成并得到用户明确批准后才能启动真实 pilot。

固定总 Agent-execution budget 只用于后续算法比较的公平性。交互探测、诊断、失败和重试均计入所有方法的总预算。

## 7. 运行顺序

1. mock adapter 与 16 配置完整性测试；
2. pairing、reset、cache key、hash、failure/retry、ledger 和复算测试；
3. 2 tasks × 2 seeds × 16 configurations 的本地 smoke，使用纯 mock environment；
4. 代码审查和协议修订；
5. 仅在用户批准后运行一条真实 tau2 adapter smoke；
6. 根据实际调用数、方差和成本冻结 12-task pilot 或调整样本量；
7. 只有 G0—G3 通过后才启动正式 factorial pilot；
8. 只有交互估计可靠后才实现完整 linkage-aware cooperative evolution。

## 8. 失败与诊断规则

某个 pair 没有明显交互时，按以下顺序检查：

1. 两个变体是否产生可观察行为差异；
2. task 是否依赖对应模块组合；
3. reset、配对和评分是否正确；
4. user simulator、judge、tool failure 和模型 sampling 噪声是否过大；
5. 当前 cluster 数是否有能力识别 \(\delta\)；
6. 是否存在 task-conditioned 或三阶交互；
7. tau2 是否给该模块足够的干预空间。

追加诊断必须使用新的 protocol version，并将结果标记为 exploratory，不能回写成确认性结果。

## 9. R1 Gate 状态

| Gate | 状态 | 说明 |
|---|---|---|
| G0 Literature | PASS | 见 `LITERATURE_AUDIT_PHASE0A.md` 和更新后的 ledger |
| G1 Environment | PASS | tau2 v1.0.1 和模块注入 API 有源码证据 |
| G2 Contracts/protocol | NEEDS_REVISION | 统计和 adapter 已修订，provider 价格验证与 review 仍待完成 |
| G3 Smoke | PASS（无 API） | mock 与真实 tau2 类的 no-API smoke 已通过 |
| G4 Pilot | NOT STARTED | 禁止在 G3 和成本批准前运行 |
| G5 Search | NOT STARTED | 禁止在交互测量可靠前实现完整搜索 |


## 10. Phase 0E.1 provider request-bound correction — 2026-11-23

The original pilot request estimate must be superseded by the four-module call graph. Every Agent response invokes Planner + Selector + one of Caller/Synthesizer (three model requests). Conservatively allow up to 30 Agent responses and 30 User Simulator responses per episode:

- 90 Agent module requests + 30 User Simulator requests = 120 logical requests per episode.
- With one retry per logical request: 240 physical request attempts per episode.
- 64-episode exploratory smoke: 7,680 normal logical requests / 15,360 maximum physical attempts; $9.326592 no-retry / $18.653184 with one retry for every request.
- 384-episode pilot: 46,080 normal logical requests / 92,160 maximum physical attempts; $55.959552 no-retry / $111.919104 with one retry for every request.

These are conservative peak cache-miss estimates at 2,000 input + 512 output tokens per physical request. The $20 exploratory authorization ceiling is proposed but not granted; the separate $80 hard stop is not spending authorization. See `docs/PHASE0B_PROTOCOL_FREEZE.md` and `experiments/pilot_factorial/cost_profile.json` for the current machine-readable protocol.
