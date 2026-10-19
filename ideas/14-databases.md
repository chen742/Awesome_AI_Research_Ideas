<a id="top"></a>
# 🗄️ Databases & Data Systems

> 从 SIGMOD / VLDB 的获奖论文与正式论文（以欧美团队为主）中提炼的数据库方向 idea，覆盖基数估计与连接排序、LLM 驱动的查询重写、自解码存储格式、CXL 解耦内存事务、LLM 智能体事务、向量检索（流式更新与过滤检索）、图查询语言、Text-to-SQL 与查询理解、LLM 管道数据质量，目标投稿 SIGMOD / VLDB / ICDE。
> 符号说明：🎯 源论文 · 📌 线索来源 · 📮 投稿建议 · ⭐ Novelty · 🚀 Impact · 🧗 Difficulty · 🧪 验证方案 · 🔑 关键词 · 📄 会议正式论文

[⬅️ 返回主页](../README.md)

---

## 💡 Idea 14.1 — *Dyadic Degree Norms: Extending Pessimistic Cardinality Bounds to Range Joins, LIKE Predicates and Nested Queries*

| | |
|:--|:--|
| 🎯 **源论文** | **LpBound: Pessimistic Cardinality Estimation Using ℓp-Norms of Degree Sequences** · Haozhe Zhang et al. (UZH) · 🏆 SIGMOD 2025 Best Paper · [arXiv:2502.05912](https://arxiv.org/abs/2502.05912) |
| 📌 **线索来源** | 7 Conclusion and Future Work §"Second, it does not yet support range (and theta) joins, complex and negated predicates, and nested queries. LpBound's flexible framework can in principle accommodate such query constructs, yet this is not immediate and deserves an in-depth treatment in future work." |
| 📮 **投稿建议** | 🗄️ **DB** · SIGMOD / VLDB ＋ 🖥️ Systems · OSDI |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
LpBound 用连接列度序列的 ℓp 范数加信息不等式给出单侧上界，在 JOB / STATS 上误差低、无需训练，且能换来最多 3000 秒的查询加速。但它只覆盖等值连接与简单谓词，作者明确列出范围 / theta 连接、复杂与否定谓词、嵌套查询为未解决问题。这恰恰是分析型负载的常见形态：时间窗口关联、价格区间匹配、`NOT EXISTS` 反连接。SafeBound 用 3-gram 处理 LIKE，但仍限于等值连接；据我们所知，度序列类上界尚未覆盖不等值连接。关键 insight：不等值条件 `R.a < S.b` 可以用二进制前缀（dyadic）分解精确改写为 O(log U) 个**互不相交**的等值连接之和——两值第一次分叉的那一位唯一确定一个层级。每层都是等值连接，可直接套用 LpBound 的线性规划，求和后仍是合法上界。谓词同理：把 ℓp 范数存储在 dyadic / q-gram 桶上，查询时组合桶范数即可得到谓词条件下的范数上界。

**💡 一句话 Idea**
用 dyadic 分解把范围 / theta 连接改写为 O(log U) 个不相交的等值连接，并在 dyadic 区间与 q-gram 桶上预存度序列 ℓp 范数，使 LpBound 的单侧保证在不等值连接、LIKE / 否定谓词和去相关后的嵌套查询上依然成立。

**🛠️ 可能的解决方法**
1. **不等值连接归约**：对域 [0, U) 构造 dyadic 树。`R.a < S.b` ⇔ ∃ 层 ℓ：a、b 在 ℓ 之前的前缀相同，且第 ℓ 位 a=0、b=1。为每层引入派生键 (prefix_ℓ, bit_ℓ)，对它求 ℓp 范数，得到界 |R ⋈_< S| ≤ Σ_ℓ LpBound(R ⋈_{key_ℓ} S)。带宽连接 |a−b| ≤ δ 改写为两个不等式的交，取两侧界中较小者。
2. **谓词条件范数**：离线为每个 dyadic 节点 / 3-gram 存储 (‖deg‖_1, ‖deg‖_2, …, ‖deg‖_∞)。范围谓词按 O(log U) 个覆盖节点组合（ℓp^p 可加）；LIKE 取所含 3-gram 范数的最小值；合取取各谓词界的 min；否定谓词借助"全量范数 − 下界"，因此需要同时存储范数的下界（如分桶最小度）。
3. **嵌套查询**：先去相关为半连接 / 反连接。半连接的结果度序列逐点不超过原度序列，可直接复用原范数；反连接用"原表 − 半连接下界"。由此证明整体输出仍是上界（单侧保证）。
4. **统计开销控制**：只为出现在工作负载中的列建 dyadic 统计；每层只保留 p∈{1,2,3,∞} 四个数，存储为 O(log U) 倍。估计时把各层 LP 合并成一个共享约束的大 LP，避免逐层求解。

**🧭 与最接近工作的区别**
- LpBound (2025)：仅等值连接与简单谓词；本 idea 用可证明的归约把不等值与嵌套结构纳入同一框架。
- SafeBound (Deeds et al., SIGMOD 2023)：度序列上界 + 3-gram 处理 LIKE，同样只支持等值连接，且只用 ℓ1 / ℓ∞ 类信息。
- 学习型估计器（NeuroCard、FactorJoin 等）：没有单侧保证，对不等值连接通常缺乏支持。

**🧪 验证方案**
- 基准：JOB、STATS-CEB、DSB（含非等值连接与复杂谓词），以及在 JOB 上追加时间窗口 / 价格带宽连接构造的 JOB-range；端到端在 PostgreSQL 与 DuckDB 中注入估计值。
- 指标：q-error 分布（P50/P95/max）、低估率（理论上应为 0）、端到端查询时延、估计时间（ms）、统计存储大小。
- 对比：LpBound（不等值连接回退到 PostgreSQL 默认估计）、SafeBound、PostgreSQL / DuckDB 原生估计器、FactorJoin。
- 消融：去掉 dyadic 层合并 LP / 只用 ℓ1 / 去掉下界范数（否定谓词退化）。

🔑 `cardinality estimation` `pessimistic bounds` `degree sequences` `theta joins` `dyadic decomposition` `query optimization`

[🔝 top](#top)

---

## 💡 Idea 14.2 — *Memory-Elastic Join Ordering: Load-Adaptive Selection from the C_out/C_max Pareto Frontier in Multi-Tenant Cloud Warehouses*

| | |
|:--|:--|
| 🎯 **源论文** | **DPconv: Super-Polynomially Faster Join Ordering** · Mihail Stoian et al. (UTN) · 🏆 SIGMOD 2025 Honorable Mention · [arXiv:2409.08013](https://arxiv.org/abs/2409.08013) |
| 📌 **线索来源** | 11. Discussion §"Instead, one could follow a proactive approach in which a query's runtime and memory consumption is co-optimized with query scheduling. For example, when there is a high (concurrent) memory load on the system, one would want to minimize the peak memory consumption of newly arriving queries, while when there is low memory load, one can afford a higher memory consumption." |
| 📮 **投稿建议** | 🗄️ **DB** · SIGMOD / VLDB ＋ 🖥️ Systems · OSDI |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
DPconv 借助子集卷积，首次在超多项式意义上打破 O(3^n) 的连接排序下界：C_max（最大中间结果，可视为峰值内存的代理）可在 O(2^n n^3) 内最优求解，C_cap 先求最优 C_max 再在其约束下最小化 C_out。作者在 Discussion 中指出，C_cap 只取"最优 C_max"这一个点过于僵硬，更有价值的做法是让查询的运行时间与内存消耗**和调度联合优化**，按系统当前内存压力选择计划。Redshift 一类云数仓目前只是"预测内存后排队"（被动），并不改变计划本身。空隙在于：没有人把 (C_out, C_max) 的完整 Pareto 前沿作为可调度对象。关键 insight：DPconv 的阈值化结构天然支持"给定 C_max ≤ t，最小化 C_out"。在几何阈值网格上复用 DP 表，就能低成本得到 ε-近似前沿，于是调度器可以在查询到达时按内存余量从前沿上选点。

**💡 一句话 Idea**
用 DPconv 的阈值化子集卷积一次性求出 (C_out, C_max) 的 ε-近似 Pareto 前沿，再由内存感知的准入控制器按实时内存负载与并发查询的剩余寿命，从前沿上为每个新查询挑选计划，主动削峰而非被动排队。

**🛠️ 可能的解决方法**
1. **前沿计算**：取阈值集合 T = {t_0(1+ε)^k}（t_0 为最优 C_max），对每个 t 运行带上限的 DP：只保留中间结果 ≤ t 的子集，在其上最小化 C_out。各阈值的子集是单调嵌套的，因此可以增量复用 DP 表，总开销约为 O(log_{1+ε}(W/t_0)) 倍的 C_max 求解。
2. **鲁棒峰值**：用悲观基数上界（如度序列类上界）而非点估计来计算 C_max，使"内存不超过 t"成为高概率保证，避免 OOM 与溢写。
3. **调度器**：建模为在线背包问题。状态包括当前已用内存 M(t)、各运行查询的预计剩余时间与内存释放曲线；新查询到达时选前沿点 argmin_i [ĉ_out,i + λ(M)·ĉ_max,i]，其中 λ(M) 为随内存压力上升的影子价格（对偶变量在线更新）。
4. **系统集成**：在 DuckDB 中实现（单节点多租户：多个连接共享 buffer pool），并在 Spark SQL 中实现（executor 内存配额）。计划切换只发生在查询开始前，无需运行时重优化。

**🧭 与最接近工作的区别**
- DPconv (2025)：给出 C_cap 单点与快速 C_max 算法，未做前沿与调度耦合。
- Auto-WLM (Saxena et al., SIGMOD 2023)：Redshift 基于预测内存做排队与资源分配，计划固定不变；本 idea 改变计划本身以适应负载。
- 资源感知查询优化 (Viswanathan et al., 2018)：提出理念，没有可扩展的精确多目标连接排序算法。

**🧪 验证方案**
- 基准：JOB（113 条）、TPC-DS SF100、DSB；并发负载按 Redset（Amazon Redshift 公开的集群负载 trace）回放到达过程与查询混合。
- 指标：吞吐（queries/h）、P50/P99 时延、峰值内存、溢写字节数、OOM / 被杀查询数、10–30 表连接的优化耗时。
- 对比：仅 C_out 最优（DPhyp）、仅 C_max 最优、C_cap、固定计划 + Auto-WLM 式准入控制。
- 关键假设检验：(a) 高内存压力时选前沿上低 C_max 的点，能以 <10% 的单查询时延代价把 OOM 降到 0；(b) 低压力时自动退回 C_out 最优，不损失吞吐。

🔑 `join ordering` `subset convolution` `multi-objective optimization` `memory-aware scheduling` `cloud data warehouse`

[🔝 top](#top)

---

## 💡 Idea 14.3 — *From Verified Pairs to Guarded Rules: Synthesizing Provably Safe Rewrite Rules from LLM Query Rewrites*

| | |
|:--|:--|
| 🎯 **源论文** | **GenRewrite: Query Rewriting via Large Language Models** · Jie Liu & Barzan Mozafari (UMich) · 📄 SIGMOD 2024 · [arXiv:2403.09060](https://arxiv.org/abs/2403.09060) |
| 📌 **线索来源** | 6. Discussion §"Even the most powerful SQL verifier to date, SQLSolver (Ding et al., 2023), can verify only 18.9% of the generated TPC-DS rewrites." + §"A rule distilled from only one such pair is brittle and often fails to generalize—it overfits incidental syntax choices and misses necessary preconditions." |
| 📮 **投稿建议** | 🗄️ **DB** · SIGMOD / VLDB ＋ 🧪 ML · NeurIPS |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
GenRewrite 用 LLM 和自然语言重写规则（NLR2）发现传统规则库覆盖不到的重写，在 TPC-DS / JOB 上取得显著加速，但留下两个硬伤：(1) 逐查询验证等价性几乎不可行，SQLSolver 只能验证 18.9% 的 TPC-DS 重写，论文最终依赖人工检查；(2) 作者设想把重写对蒸馏成可装入优化器的规则，但单个重写对得出的规则会过拟合语法细节、漏掉必要前置条件。这暴露了 LLM 重写落地的根本矛盾：要么每条查询都调用 LLM（成本高且无保证），要么手写规则（覆盖窄）。关键 insight：验证的单位应当从"查询对"上移到"规则模式"。对同一 NLR2 下的多个已验证重写对做反统一（anti-unification），得到参数化 AST 模式；再用反例引导的方式合成最小前置条件集合（键、NOT NULL、外键、聚合单调性等）。规则只需**一次性、schema 参数化地**证明，之后对任意查询零成本、零 LLM 地应用。

**💡 一句话 Idea**
把 LLM 产生的已验证重写对按 NLR2 聚类、反统一成参数化规则模板，用 CEGIS 合成最小约束前置条件并做一次性符号证明，产出可直接装入 Calcite / DuckDB 的"带守卫规则"，让 LLM 的发现能力以零推理成本、可证明安全的方式进入优化器。

**🛠️ 可能的解决方法**
1. **模板抽取**：对同一 NLR2 簇中的 k 个 (Q, Q′) 对，在关系代数树上做反统一，求最小一般化：常量、列名、表名替换为模式变量，不一致的子树替换为"任意子计划"变量，得到规则 P(X⃗) → P′(X⃗)。
2. **前置条件合成（CEGIS）**：候选守卫来自有限语法 G = {key(X.c), notnull(X.c), fk(X.c, Y.d), distinct(X), monotone(agg)…}。循环执行：用有界模型检查器（VeriEQL 式小实例搜索）为当前规则找反例数据库 → 从反例中提取被违反的约束加入守卫 → 直到在 schema 参数化的符号表上通过 SQLSolver / U-semiring 证明，或达到守卫预算后放弃该模板。
3. **成本门控**：每条规则附带一个轻量适用性模型（规则触发前后的估计代价比），仅在代价下降超过阈值时由 Cascades 搜索采用，避免"正确但变慢"。
4. **闭环**：线上把重复出现、没有规则命中的慢查询送入 GenRewrite 产生新对 → 聚类 → 合成规则。LLM 调用只发生在规则发现阶段，按慢查询总 CPU 时间做预算。

**🧭 与最接近工作的区别**
- WeTune (Wang et al., SIGMOD 2022)：枚举小规模规则模板并用 SMT 证明，搜索空间受模板大小限制；本 idea 用 LLM 提出语义驱动的候选，并从多对样本泛化。
- QueryBooster (Bai et al., VLDB 2023)：由人以 DSL 编写或举例给出规则，没有自动前置条件合成与证明。
- LLM-R2 (2024)：用 LLM 选择已有规则的应用顺序，不产生新规则。

**🧪 验证方案**
- 基准：TPC-DS（SF10/100）、JOB、DSB，以及 GenRewrite 使用的 SQLStorm 变体；按 NLR2 簇划分训练 / 留出查询，检验规则在**未见过的查询**上的命中率。
- 指标：留出集总运行时间加速比、规则数量与平均守卫数、可证明规则比例（对比逐查询 18.9% 的验证率）、差分测试发现的错误重写数（应为 0）、优化器开销。
- 对比：原生 PostgreSQL / Calcite 规则集、WeTune 规则、逐查询 GenRewrite（LLM 在线调用）、LLM-R2。
- 消融：单对蒸馏（无反统一）/ 无 CEGIS 守卫（观察错误率）/ 无成本门控。

🔑 `query rewriting` `rule synthesis` `SQL equivalence` `CEGIS` `LLM for databases`

[🔝 top](#top)

---

## 💡 Idea 14.4 — *Decoders that Explain Themselves: A Statically Verified Decoder DSL Exposing Encoded-Domain Pushdown and Sound Statistics for Self-Decoding Datasets*

| | |
|:--|:--|
| 🎯 **源论文** | **AnyBlox: A Framework for Self-Decoding Datasets** · Mateusz Gienieczko et al. (TUM) · 🏆 VLDB 2025 Best Research Paper · [PDF](https://www.vldb.org/pvldb/vol18/p4017-gienieczko.pdf) |
| 📌 **线索来源** | Discussion §"For example, if a statically-verified DSL for Decoders was designed (as discussed in Section 2.4), a Decoder in the DSL could be distributed with an automatic equivalent Wasm version being generated alongside." + §"An example of this is sizeInBytes, describing the estimated size of a fully decoded dataset in memory, which can aid Spark in its network traffic estimations." |
| 📮 **投稿建议** | 🗄️ **DB** · VLDB / SIGMOD ＋ 🖥️ Systems · OSDI |
| ⭐ Novelty | ★★★★★ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
AnyBlox 让数据集随身携带 Wasm 解码器，把编码格式与读取系统解耦，从而支持格式演进和实例最优编码，并已接入 DuckDB、Spark、Umbra。代价是 Wasm 解码器对宿主系统是**黑盒**：优化器看不到解码后大小、min/max、排序性，也无法把谓词下推到编码域（字典码比较、FOR 偏移比较），只能"全部解码再过滤"。同时，安全依赖 Wasm 沙箱与运行时限制，而不是静态保证。作者把"静态可验证的解码器 DSL"和"可选元数据（如 sizeInBytes）"列为未来方向，但没有回答 DSL 应该长什么样、元数据怎样才可信。关键 insight：只要 DSL 由有界的编码组合子构成（bit-unpack、FOR、delta、RLE、dictionary、有界循环），**同一份程序**就能被抽象解释出三样东西：终止性与内存上界（安全）、输出大小与值域上界（统计）、编码域谓词变换（下推）。这样元数据从"作者自报"变为"读取方可复算验证"。

**💡 一句话 Idea**
设计一个由有界编码组合子构成的解码器 DSL，并为每个组合子定义抽象语义和谓词变换器，使读取系统能对随数据分发的解码器静态验证安全性、复算可信统计量，并自动生成编码域过滤内核，同时保留 Wasm 版本以向后兼容。

**🛠️ 可能的解决方法**
1. **DSL 设计**：组合子代数 D ::= bitunpack(w) | for(base, D) | delta(D) | rle(D, D) | dict(Dict, D) | concat(D, D) | bounded_loop(n, D)，类型系统携带位宽与长度。终止性和内存上界由类型规则直接得出，无需 Wasm fuel 计量。
2. **抽象解释出统计**：在区间域 × 单调性域上解释解码器，得到每个块的 [min, max]、解码后字节数和是否有序，作为可选元数据随数据发布。读取系统用同一解释器在 O(块元数据) 时间内复算校验，不一致即拒绝该提示。
3. **编码域下推**：为每个组合子定义谓词变换 τ。例如 for：x < c ⇒ packed < c − base；dict：先在字典上求值得到码位图；rle：按 run 粒度求值。把 τ 组合起来自动生成 SIMD 过滤内核，在解码前跳过整块或整段。
4. **兼容与回退**：DSL 编译到 Wasm 与原生代码两份。旧版 AnyBlox 读取 Wasm，新版选择原生 + 下推；不可表达的编码保留纯 Wasm 解码器，作为黑盒回退。

**🧭 与最接近工作的区别**
- AnyBlox (2025)：Wasm 黑盒解码器，元数据为可选提示、不可验证，不支持编码域下推。
- F3 (Zeng et al., 2025)：同样在文件中嵌入 Wasm 解码器以支持格式演进，解码器对引擎同样不透明。
- BtrBlocks (Kuschewski et al., SIGMOD 2023)、FastLanes (Afroozeh & Boncz, VLDB 2023)：高效级联编码，但编码集合固定在格式规范内，不随数据分发。

**🧪 验证方案**
- 基准：TPC-H SF100、ClickBench、Public BI Benchmark（真实 BI 数据）；集成到 DuckDB 与 Spark（复用 AnyBlox 接口）。
- 指标：扫描吞吐（GB/s）、端到端查询时延、跳过的块 / 字节比例、压缩率、元数据复算与验证耗时、Spark shuffle 估计误差（使用可信 sizeInBytes 前后对比）。
- 对比：Parquet、AnyBlox-Wasm、BtrBlocks、F3。
- 安全性：对恶意解码器（死循环、越界、超大输出声明）做模糊测试，检验类型检查能否静态拒绝，以及元数据造假能否被复算发现。

🔑 `storage formats` `self-decoding data` `WebAssembly` `abstract interpretation` `predicate pushdown` `compression`

[🔝 top](#top)

---

## 💡 Idea 14.5 — *Coherence by Immutability: Multi-Host MVCC over Non-Coherent CXL Memory Pools with a Tiny Hardware-Coherent Metadata Region*

| | |
|:--|:--|
| 🎯 **源论文** | **Beluga: A CXL-Based Memory Architecture for Scalable and Efficient LLM KVCache Management** · Xinjun Yang et al. (Alibaba Cloud) · 📄 SIGMOD 2025 · [arXiv:2511.20172](https://arxiv.org/abs/2511.20172) |
| 📌 **线索来源** | 8. Future Work on CXL Switches §"Second, a critical research area is the design of more efficient coherence protocols for CXL memory pools. Potential directions include: (1) leveraging application-level semantics to relax coherency, (2) implementing scalable, directory-based coherence using in-switch resources, and (3) developing hybrid models where a small, hardware-coherent region manages coherence metadata for a significantly larger address space." |
| 📮 **投稿建议** | 🗄️ **DB** · VLDB / ICDE ＋ 🖥️ Systems · OSDI |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★★★ |

**🔍 深入分析**
Beluga 基于首批商用 CXL 2.0 交换机搭建 GPU 集群共享内存池，用来卸载 KVCache，性能明显优于 MoonCake 的 RDMA 方案。它之所以成功，很大程度上是因为 KVCache **一次写入、多次读取、不可变**，完全回避了跨主机缓存一致性：CXL 2.0 的池化并不提供跨主机硬件一致性。作者把"利用应用语义放松一致性"和"用小块硬件一致区管理大地址空间的元数据"列为关键方向。数据库是最需要、也最难用好这种共享内存池的场景：多主 OLTP 若能以 load/store 共享同一份数据，就不再需要分区和 2PC。关键 insight：MVCC 的版本记录在提交后同样不可变，与 KVCache 同构。真正需要一致性的只有极少量可变字（版本链头、锁 / 时间戳字、提交时间戳）。因此可以把数据库状态拆成"不可变版本区（可被各主机 CPU 自由缓存）"和"KB 级可变元数据区（走非缓存原子访问或交换机内目录）"，用 MVCC 语义替代通用一致性协议。

**💡 一句话 Idea**
在不提供跨主机一致性的 CXL 2.0 内存池上构建 shared-everything 的多主 MVCC 引擎：版本记录写一次、发布后不可变，可在各主机自由缓存；只有版本链头与时间戳等元数据放在小型一致区，用非缓存原子操作维护，从而在无分区、无 2PC 的前提下扩展到多台主机。

**🛠️ 可能的解决方法**
1. **内存布局**：池内划分 (a) 版本堆：每主机独占追加的 log-structured 区域，记录写入后用 `clflushopt + sfence` 刷回再发布；(b) 元数据区：每个元组一个 8B 头字（最新版本指针 + 写锁位），所有访问走 uncached / 非临时原子（或 CXL 3.x back-invalidation 区）；(c) 全局时间戳计数器，批量分配以摊薄争用。
2. **并发控制**：快照隔离 / 可串行化 SI。读事务按快照时间戳沿版本链读取，不可变版本可命中本地 CPU cache；写事务对头字 CAS 加锁，提交时发布新版本并原子更新头字。可串行化用 SSI 的 rw-antidependency 标记，标记位同样放在元数据区。
3. **垃圾回收与失效**：版本只在全局最小活跃快照之后回收，回收前发出主机间 epoch 屏障，保证没有主机缓存残留旧行。这是唯一需要显式失效的路径，频率低、可批量。
4. **故障模型**：主机崩溃时，其未提交版本因头字未更新而不可见；锁位由带租约的时间戳回收；内存池掉电由持久化日志（远端 SSD）负责恢复。

**🧭 与最接近工作的区别**
- PolarDB-MP (SIGMOD 2024)：基于 RDMA 的解耦共享内存实现多主，需要显式的缓存失效与页级融合协议；本 idea 利用 load/store 与版本不可变性，去掉通用失效协议。
- Tigon (OSDI 2025)：面向 CXL pod 的分布式数据库，仍以分区为主，只把跨分区共享数据放进 CXL；本 idea 是非分区的 shared-everything 设计。
- Leis & Dietrich《CXL and the Return of Scale-Up Database Engines》(VLDB 2024)：愿景性论述，没有给出无一致性条件下的并发控制设计。

**🧪 验证方案**
- 硬件：商用 CXL 2.0 交换机 + 2–8 台主机（与 Beluga 同类平台）；对照组为同规模 RDMA 集群。
- 基准：TPC-C（仓库数 = 主机数 × k，含 10% 跨仓事务）、YCSB A/B/F（Zipf 0.99）、CH-benCHmark（HTAP 读多写少）。
- 指标：吞吐、P99 时延、abort 率、扩展效率（1→8 主机）、CXL 带宽占用、元数据区访问占比。
- 对比：分区 + 2PC、PolarDB-MP 式 RDMA 共享内存、Tigon 式部分共享；用 Elle 检查器对执行历史做隔离级别异常检测（SI / SSI 下应无违例）。
- 消融：版本区禁止缓存（全部走 uncached）以量化"不可变性"的收益。

🔑 `CXL` `disaggregated memory` `MVCC` `cache coherence` `multi-primary OLTP` `cloud-native databases`

[🔝 top](#top)

---

## 💡 Idea 14.6 — *Verified Compensation for Agentic Transactions: Synthesizing, Checking and Isolating Saga Rollbacks for LLM Agents over Databases*

| | |
|:--|:--|
| 🎯 **源论文** | **SagaLLM: Context Management, Validation, and Transaction Guarantees for Multi-Agent LLM Planning** · Edward Y. Chang & Longling Geng (Stanford) · 📄 VLDB 2025 · [arXiv:2503.11951](https://arxiv.org/abs/2503.11951) |
| 📌 **线索来源** | 6. Conclusion §"Future work will address several critical challenges: developing formal verification methods for LLM-generated compensation code to ensure logging and rollback correctness, addressing intrinsic autoregressive context limitations, creating comprehensive verification frameworks for transactional multi-agent systems, ..." + 2.3 §"LangGraph and AutoGen enable structured workflows and agent interactions, but lack built-in atomicity guarantees, compensation logic, or robust failure recovery." |
| 📮 **投稿建议** | 🗄️ **DB** · VLDB / ICDE ＋ 🧪 ML · NeurIPS |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
SagaLLM 把经典 Saga 事务引入多智能体规划：用不可变日志、补偿动作和独立校验代理来应对 LLM 的状态遗忘与自我校验失效。但它的补偿逻辑仍由 LLM 生成，正确性没有保证；作者把"LLM 生成补偿代码的形式化验证"和"事务型多智能体的验证框架"列为首要未来工作。随着智能体直接对生产数据库执行 SQL / API 写操作，这一问题从规划演示变成了数据正确性问题。Saga 天然缺乏隔离性：并发运行的智能体会读到彼此的中间状态，或在补偿时覆盖他人的更新（经典的 Saga 隔离异常），而 LangGraph 等框架只提供检查点，没有原子性。关键 insight：数据库层的每个工具调用都有**可符号化的效果**（写集 + 谓词 + 增量）。在此基础上可以静态检查"补偿 ∘ 正向 ≡ 恒等（模语义不变式）"，并用效果的可交换性决定哪些智能体动作可以并发、哪些需要语义锁，把 LLM 从正确性关键路径中移除。

**💡 一句话 Idea**
为数据库上的 LLM 智能体建立"效果规约 → 补偿合成与验证 → 基于可交换性的语义隔离"三层运行时：LLM 只负责提出动作与候选补偿，正确性由符号验证与 escrow / 语义锁保证，使智能体 saga 在故障与并发下都满足用户声明的不变式。

**🛠️ 可能的解决方法**
1. **效果规约**：每个工具（SQL 模板或 REST API）标注效果 E = (读集谓词, 写集谓词, 增量形式)，如 `book(seat)`: seats.avail −= 1 where id=?。对 SQL 工具可由静态分析自动推导，对外部 API 由开发者用小型 DSL 声明。
2. **补偿合成与验证**：LLM 为每个正向动作生成候选补偿 c。验证器把 E_fwd 与 E_c 编码为 SMT 公式，检查 ∀s. Inv(s) ⇒ Inv(c(f(s))) ∧ π(c(f(s))) = π(s)，其中 π 为用户声明的语义投影（如余额、库存，允许日志表不同）。失败时把反例状态回传给 LLM 修复；验证通过的补偿缓存为模板，供同类动作复用。
3. **语义隔离**：对动作对的效果做可交换性分析。可交换则并发执行；计数器类增量用 escrow 事务（预留额度）；不可交换的使用"语义锁"（仅锁谓词覆盖的行），锁跨越 saga 的整个生命周期但粒度最小化。
4. **运行时**：意图日志先写（WAL 风格）后执行；LLM 进程崩溃后由日志驱动的恢复器继续前滚或补偿，不依赖 LLM 记忆。

**🧭 与最接近工作的区别**
- SagaLLM (2025)：补偿由 LLM 生成，无验证，也不处理多个 saga 并发时的隔离异常。
- Sagas (Garcia-Molina & Salem, SIGMOD 1987) 与 escrow 事务 (O'Neil, 1986)：提供补偿与增量并发的经典机制，但假设补偿由人编写、正确性由程序员保证。
- 《Supporting Our AI Overlords: Redesigning Data Systems to be Agent-First》(Liu et al., 2025)：愿景性讨论智能体负载对数据系统的影响，没有给出可验证的补偿与隔离机制。

**🧪 验证方案**
- 基准：τ-bench（retail / airline，带数据库状态和业务规则）；"Agentic TPC-C"：由智能体按自然语言指令执行 New-Order / Payment / Delivery，并用 TPC-C 一致性条件作为不变式。
- 故障注入：工具调用失败、LLM 进程中途崩溃、并发冲突；并发度 1–64 个智能体。
- 指标：不变式违例率、补偿成功率、补偿被形式化验证的比例、吞吐（任务/分钟）、LLM token 成本、锁等待时间。
- 对比：SagaLLM、LangGraph 检查点、把整个智能体回合包进一个可串行化长事务（2PL）、无隔离的朴素 saga。

🔑 `LLM agents` `sagas` `compensating transactions` `semantic concurrency control` `SMT verification` `transaction processing`

[🔝 top](#top)

---

## 💡 Idea 14.7 — *Fresh-by-Design Disaggregated Vector Search: Streaming Index Updates with Bounded Staleness for Accelerator-Based RAG Serving*

| | |
|:--|:--|
| 🎯 **源论文** | **Chameleon: a Heterogeneous and Disaggregated Accelerator System for Retrieval-Augmented Language Models** · Wenqi Jiang et al. (ETH Zurich) · 🏆 VLDB 2025 Best Scalable Data Science Paper · [arXiv:2310.09949](https://arxiv.org/abs/2310.09949) |
| 📌 **线索来源** | 8. Conclusion and Outlook §"ChamVS could also be extended to support index updates (Xu et al., 2023b) and relational features (Zhang et al., 2023)." |
| 📮 **投稿建议** | 🗄️ **DB** · VLDB / ICDE ＋ 🖥️ Systems · OSDI |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
Chameleon 把检索增强语言模型拆成 GPU 上的 LLM 推理（ChamLM）和 FPGA 解耦内存节点上的 IVF-PQ 向量检索（ChamVS），两者独立扩缩容，在延迟和能效上优于 CPU-GPU 方案。但 ChamVS 的索引是**静态**的：FPGA 流水线按固定 IVF 列表布局扫描，作者把索引更新列为首要扩展。真实 RAG 语料（新闻、工单、代码库）持续增删，静态索引只能周期性全量重建，带来分钟到小时级的陈旧窗口。CPU 侧的 FreshDiskANN、SPFresh 已经解决了图 / 聚类索引的就地更新，但它们假设 CPU 能随机读写索引。在解耦加速器上，更新需要和流水线扫描并存，PQ 码本会随分布漂移失效，而且内存节点之间存在负载倾斜，这些都是新问题。关键 insight：IVF 列表天然适合 log-structured 追加。只要把"追加段 + 删除位图 + epoch 快照"做成 FPGA 流水线原生可扫描的格式，就能把更新变成纯追加的内存写，并以 epoch 为单位给出有界陈旧保证。

**💡 一句话 Idea**
为解耦 FPGA 向量检索节点设计 log-structured 的 IVF 增量段与 epoch 快照格式，使扫描流水线在不停机的情况下读到有界陈旧的最新数据；同时用 PQ 重建误差与列表倾斜监控触发局部重聚类和跨节点迁移，在持续更新下保持召回率与吞吐。

**🛠️ 可能的解决方法**
1. **数据格式**：每个 IVF 列表 = 不可变主段 + 若干追加段（固定大小，按 FPGA burst 对齐）+ 删除位图。插入先在 CPU 协调器编码为 PQ 码，再以 RDMA / 网络写追加到对应节点；FPGA 扫描单元逐段扫描，并按位图屏蔽已删除向量。
2. **一致性**：全局 epoch 计数器。查询携带 epoch e，只扫描 seal_epoch ≤ e 的段，删除位图按 epoch 版本化。陈旧上界 = epoch 周期 Δ（如 100 ms），可按 SLA 配置。
3. **漂移维护**：每个列表在线监控 PQ 重建误差 ê 与列表长度。当 ê 超阈值或长度超过均值的 κ 倍时，后台在 CPU 上对该列表局部 split / 重新编码（类似 SPFresh 的 LIRE 局部重平衡），完成后在新 epoch 原子切换。
4. **跨节点均衡**：把列表视为可迁移分片，以"扫描字节数 × 访问频率"为负载，用贪心迁移把节点间最大负载比控制在 1+ε 内；迁移期间双写，保证查询不受影响。

**🧭 与最接近工作的区别**
- Chameleon (2025)：静态 IVF-PQ，只能离线重建。
- SPFresh (SOSP 2023)、FreshDiskANN (2021)：CPU / SSD 上的就地更新，不涉及加速器流水线格式与解耦节点间的均衡。
- 周期性全量重建（Faiss 常见做法）：重建期间陈旧窗口大、资源翻倍。

**🧪 验证方案**
- 基准：SIFT1B / Deep1B；NeurIPS'23 Big-ANN streaming track 的插入 / 删除 runbook；RAG 端到端使用按时间切分的 Wikipedia 增量快照与问答集。
- 指标：随时间变化的 recall@10、QPS、P99 检索时延、插入吞吐、实测陈旧度、RAG 回答准确率（对新近事实的问题）。
- 对比：Chameleon + 周期重建、CPU Faiss IVF-PQ（`add` + 定期 retrain）、SPFresh、FreshDiskANN。
- 关键假设检验：持续 10% / 小时的数据替换下，recall@10 衰减 <1%，P99 时延上升 <20%。

🔑 `vector search` `disaggregated accelerators` `FPGA` `streaming index updates` `RAG serving`

[🔝 top](#top)

---

## 💡 Idea 14.8 — *Drift-Robust Index Collections for Filtered Vector Search: Subsumption-Lattice Planning under Unseen Templates and Cardinality Uncertainty*

| | |
|:--|:--|
| 🎯 **源论文** | **SIEVE: Effective Filtered Vector Search with Collection of Indexes** · Zhaoheng Li et al. (UIUC) · 📄 VLDB 2025 · [arXiv:2507.11907](https://arxiv.org/abs/2507.11907) |
| 📌 **线索来源** | 6. Discussion §"One potential problem for SIEVE is an exploding optimization space when the historical workload contains many distinct filter templates." + §"SIEVE assumes availability of accurate filter cardinality info (card(h))." |
| 📮 **投稿建议** | 🗄️ **DB** · VLDB / ICDE ＋ 🌐 WWW · KDD |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
SIEVE 用三维代价模型（内存、速度、召回）从历史负载中挑选一组按过滤条件划分的 HNSW 索引，并在查询时于"带参数的索引搜索"和"暴力 KNN"之间选择，最高取得 8× QPS 提升。它的优化建立在两个假设上：历史过滤模板分布能代表未来，且精确基数可得。作者承认，模板数量多时优化空间爆炸，负载漂移会影响效果。在推荐、电商搜索等场景中，过滤模板是长尾且快速变化的（新类目、新活动），按历史频率选出的索引集合会迅速过时。而当过滤涉及关联表或湖仓外部属性时，精确位图也不再廉价。关键 insight：过滤条件之间存在**包含关系格**。为 h 建的索引可以服务任意 h′ ⊆ h 的查询（加后过滤），代价取决于选择率比 card(h′)/card(h)。因此选择问题可以从"为见过的模板挑索引"改写为"在格上覆盖整个模板分布邻域"，用分布鲁棒优化抵御漂移，并以区间基数代替精确基数。

**💡 一句话 Idea**
把过滤向量检索的索引集合选择建模为过滤条件包含格上的分布鲁棒覆盖问题：对历史模板分布周围的不确定集合最小化最坏情况服务代价，用区间基数替代精确基数，再配合 ski-rental 式在线建索引策略，使索引集合在新模板与负载漂移下保持接近最优。

**🛠️ 可能的解决方法**
1. **包含格建模**：节点为合取过滤条件（属性 = 值的集合），边为包含关系。服务代价 cost(q | idx_h) = f_HNSW(card(h), recall) · ρ(q, h)^{-1}，其中 ρ = card(q)/card(h) 为后过滤损耗。未见过的模板可以由其在格上的祖先索引服务，或回退暴力搜索。
2. **分布鲁棒选择**：取历史模板分布 P̂ 周围的 φ-散度球 𝒰。目标为 min_{S, mem(S) ≤ M} max_{P ∈ 𝒰} E_{q∼P}[cost(q | S)]。内层 max 有闭式对偶，整体化为带对偶变量的次模覆盖问题，用贪心求解，并给出近似比。
3. **区间基数**：当 card(h) 无法精确获得时，用采样或悲观上界给出区间 [ℓ_h, u_h]，代价模型取区间内的最坏值，保证召回目标不被违反（召回对选择率单调）。
4. **在线自适应**：对新出现的高频模板，累计"若有专用索引可节省的代价"，超过构建代价时触发构建（ski-rental，2-competitive）；内存满时按格上的边际效用淘汰。

**🧭 与最接近工作的区别**
- SIEVE (2025)：基于历史频率的离线选择，假设精确基数，模板爆炸时只能截断到 top-k 常见过滤。
- ACORN (Patel et al., SIGMOD 2024)：单一谓词无关图索引，不做多索引选择，在低选择率下性能下降。
- Filtered-DiskANN (Gollapudi et al., WWW 2023)：针对标签过滤构建专用图，模板集合固定。

**🧪 验证方案**
- 基准：YFCC-10M（NeurIPS'23 Big-ANN filtered track）、SIEVE 使用的 UQV 等数据集；按时间切分查询日志构造漂移，并人为注入新模板（10%–50% 未见过）。
- 指标：recall 0.9 / 0.95 下的 QPS、内存占用、建索引时间、相对离线 oracle 的 regret、漂移后的恢复时间。
- 对比：SIEVE（静态 / 定期重优化）、ACORN、Filtered-DiskANN、HNSW + 前过滤 / 后过滤。
- 消融：去掉 DRO（用经验分布）/ 去掉包含格（只匹配完全相同的模板）/ 精确 vs 区间基数。

🔑 `filtered vector search` `index selection` `distributionally robust optimization` `workload drift` `ANN`

[🔝 top](#top)

---

## 💡 Idea 14.9 — *Value-Monotone Path Patterns: Polynomial Evaluation of Edge-Property Constraints in GQL and SQL/PGQ via Dominance-Pruned Product Search*

| | |
|:--|:--|
| 🎯 **源论文** | **GQL and SQL/PGQ: Theoretical Models and Expressive Power** · Amélie Gheerbrant et al. (Université Paris Cité) · 📄 VLDB 2024 · [arXiv:2409.01102](https://arxiv.org/abs/2409.01102) |
| 📌 **线索来源** | 6. Limitations of Patterns: a theoretical investigation §"Specifically, it seems to be impossible to express queries that impose conditions on how values of edges properties change along the paths, even if the same conditions can be expressed for properties of nodes." + 7. Limitations of Patterns: an experimental investigation §"We now show experimentally that this way of expressing simple graph queries has no realistic chance to work, as it generates enormous (exponential size) intermediate results, and the query would not terminate even on tiny graphs." |
| 📮 **投稿建议** | 🗄️ **DB** · SIGMOD / VLDB ＋ 🌐 WWW · KDD |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
该论文为 GQL 和 SQL/PGQ 建立了理论模型，证明 Core GQL / PGQ 无法表达"沿路径边属性单调变化"一类查询（如转账时间戳递增的路径）。这类查询正是 ISO 标准委员会讨论的焦点。实际语言虽能借助路径变量和补集写出它，但会枚举所有路径，在极小的图上也不终止。这类查询是金融反洗钱、供应链追溯中的典型需求，标准与引擎却都没有原生支持。关键 insight：时间戳递增的路径就是时序图中的"时间相容路径"，而时序图可达性有多项式算法。更一般地，只要相邻边比较 θ 是传递的偏序（<、≤、前缀包含等），在"图节点 × 自动机状态"的乘积上，每个状态只需保留**支配意义下最优**的最后一条边取值（递增约束取最小值），就能把指数级的路径枚举压缩成类 Dijkstra 的多项式搜索。非传递的 θ 则需要另行刻画复杂度。

**💡 一句话 Idea**
为 GQL / SQL/PGQ 增加"相邻边值约束"模式构造，证明当 θ 为传递偏序时，在 WALK / TRAIL 语义下可用支配剪枝的乘积搜索在多项式时间内求值，刻画非传递 θ 的复杂度边界，并在图引擎中实现原生物理算子。

**🛠️ 可能的解决方法**
1. **语言扩展**：在路径模式中引入 `-[e]->{θ(prev.ts, e.ts)}*` 形式的相邻边约束，语义定义为：路径上任意相邻两条边 (e_i, e_{i+1}) 满足 θ。给出与 Core GQL 的组合语义，并证明它严格增加了表达能力（复用论文中的不可表达性结果）。
2. **求值算法**：构造乘积图 G × A（A 为模式自动机）。对传递且全序兼容的 θ，每个乘积状态 (v, q) 维护 Pareto 最优的最后边值集合（全序下只有一个值），用优先队列按边值扩展，复杂度 O((|E||A|) log(|E||A|))。偏序情形下维护反链，复杂度与最大反链宽度成正比。
3. **复杂度刻画**：WALK 语义 + 传递 θ ∈ PTIME；SIMPLE / ACYCLIC 语义下即使 θ 为 `<` 也需要讨论（时序图上的简单路径问题），给出 NP-hardness 或参数化可解的边界；非传递 θ（如 |Δ| ≤ δ）给出硬度归约。
4. **工程实现**：在 DuckPGQ（DuckDB 的 SQL/PGQ 扩展）中实现为新的物理算子，支持多源批量求值；对时间戳类 θ 预先按边值排序，转为一次线性扫描的流式算法。

**🧭 与最接近工作的区别**
- Libkin & Vrgoč 的带数据正则路径查询 / 寄存器自动机 (2012 起)：主要处理数据值相等比较，没有落到 GQL 标准语义和引擎实现上。
- Temporal Regular Path Queries (Arenas et al., ICDE 2022)：针对时序图的专门语言，没有给出 GQL 内的一般 θ 约束与支配剪枝框架。
- 时序图路径算法 (Wu et al., VLDB 2014)：只处理时间相容路径的最短 / 最早到达问题，不与正则模式组合。

**🧪 验证方案**
- 基准：LDBC FinBench（含时间戳有序的转账链查询）、LDBC SNB（按 creationDate 单调的消息链）、SNAP 时序图（如 wiki-talk、sx-stackoverflow）。
- 指标：查询时延、峰值内存、中间结果规模；对比论文中会超时的 Cypher 补集写法（Neo4j）。
- 对比：Neo4j Cypher 路径变量写法、DuckPGQ 现有实现 + 后过滤、专用时序可达性算法（作为下界参照）。
- 关键假设检验：传递 θ 下时延随 |E| 近线性增长；SIMPLE 语义下给出实测的指数爆炸点，用来佐证理论上的硬度。

🔑 `graph query languages` `GQL` `SQL/PGQ` `regular path queries` `temporal graphs` `expressive power`

[🔝 top](#top)

---

## 💡 Idea 14.10 — *Budgeted Context Assembly for Enterprise NL2SQL: Submodular Schema–Example Selection over Thousand-Column Warehouses*

| | |
|:--|:--|
| 🎯 **源论文** | **Is Long Context All You Need? Leveraging LLM's Extended Context for NL2SQL** · Yeounoh Chung et al. (Google) · 📄 VLDB 2025 · [arXiv:2501.12372](https://arxiv.org/abs/2501.12372) |
| 📌 **线索来源** | 6.3 Long context in production and limitations §"One limitation of our study, as we analyze the impact of long context and additional contextual information on NL2SQL, is the absence of benchmark datasets that accurately model enterprise use cases. Such cases typically involve hundreds of very wide tables with thousands of columns, as well as schemas with less descriptive and similar table and column names, making schema linking significantly more challenging." |
| 📮 **投稿建议** | 🗄️ **DB** · VLDB / ICDE ＋ 🗣️ NLP · ACL |
| ⭐ Novelty | ★★★☆☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
该论文表明，长上下文模型（gemini-1.5-pro）在塞入完整 schema、样例值、提示和大量合成示例后，不微调即可在 BIRD 上达到 67.41% EX，而且对无关信息不敏感。但代价惊人：约 68% 的 BIRD dev 请求累计达到约 400k tokens。作者也承认缺少能反映企业场景的基准：数百张宽表、上千列、命名不具描述性。两个结论合在一起形成一个真实空隙：在企业库上"全塞进去"既不可行（超出窗口、成本爆炸），而"严格 schema linking"又会因为命名模糊而漏召回。真正需要回答的问题是：**给定 token 预算，选哪些上下文条目使准确率最高**。关键 insight：上下文条目（表、列描述、样例值、示例、提示）的效用对准确率近似单调次模：覆盖问题实体和连接路径的条目边际收益递减。因此可以把选择写成带背包约束的次模最大化问题，享有 (1−1/e) 近似保证，并用长上下文实验中的反事实删除数据来学习效用。

**💡 一句话 Idea**
把 NL2SQL 的上下文构造形式化为带 token 背包约束的次模覆盖问题：效用由"问题实体覆盖 + schema 图 Steiner 连接覆盖 + 学习到的条目价值"组成，配合置信度驱动的预算升级和 schema 前缀缓存，在企业级宽 schema 上以一个数量级更低的成本逼近全上下文准确率。

**🛠️ 可能的解决方法**
1. **企业级压力基准**：以 Spider 2.0（BigQuery / Snowflake 真实企业库）为主，并对 BIRD 做可控变换：注入同领域干扰表，把表宽扩到 500–3000 列，按企业命名习惯把列名混淆为缩写（`cst_nm_2`）且保留语义映射用于评测。
2. **效用函数**：u(S) = α·Cov_entity(S) + β·Cov_join(S) + γ·Σ_{i∈S} v̂_i。Cov_join 为问题实体在 schema 图上的近似 Steiner 树中被 S 覆盖的边比例；v̂_i 由小模型预测，训练标签来自长上下文运行的反事实删除（去掉条目 i 后 EX 的变化）。
3. **选择算法**：成本 c_i = token 数，用代价加权贪心 + 单元素比较，得到 (1−1/e)/2 近似；样例值与示例按"与问题的值 / 结构相似度"作为候选池，再参与同一背包。
4. **预算升级与缓存**：先用小预算 B_0 生成 SQL；若执行失败、结果为空或多次采样不一致，则把预算翻倍并重选（只追加条目，保持前缀稳定以命中 KV / prompt cache）。schema 部分按库排序固定，作为可缓存前缀。

**🧭 与最接近工作的区别**
- 本源论文 (2025)：证明全上下文有效，但没有给出预算约束下的选择方法和企业级评测。
- CHESS (Talaei et al., 2024)、DIN-SQL (Pourreza & Rafiei, NeurIPS 2023)：启发式 schema linking 加多阶段生成，没有显式的成本–准确率最优化。
- 《The Death of Schema Linking?》(Maamari et al., 2024)：主张强推理模型可以弱化 schema linking，但实验库规模在窗口内；本 idea 针对超出窗口的宽 schema。

**🧪 验证方案**
- 基准：BIRD dev、Spider 2.0-Lite / Snow，以及上述宽表 + 命名混淆变体。
- 指标：执行准确率 EX、每请求 token 数、P50/P95 时延、美元成本；绘制成本–准确率 Pareto 曲线。
- 对比：全上下文（源论文配置）、CHESS、DIN-SQL、只做 schema linking 的 top-k 检索、随机预算填充。
- 关键假设检验：(a) 在 10% token 预算下达到全上下文 EX 的 95% 以上；(b) 列名混淆后，次模选择相对 top-k 检索的优势扩大；(c) 学习到的 v̂ 能跨库迁移（留一库评测）。

🔑 `Text-to-SQL` `NL2SQL` `long context` `schema linking` `submodular optimization` `cost-aware LLM`

[🔝 top](#top)

---

## 💡 Idea 14.11 — *Seeing Aggregates: Pattern-Preserving Relational Diagrams for Grouping and Aggregation as a Verification Interface for LLM-Generated SQL*

| | |
|:--|:--|
| 🎯 **源论文** | **On The Reasonable Effectiveness of Relational Diagrams: Explaining Relational Query Patterns and the Pattern Expressiveness of Relational Languages** · Wolfgang Gatterbauer et al. (Northeastern) · 🏆 SIGMOD 2024 Honorable Mention · [arXiv:2401.04758](https://arxiv.org/abs/2401.04758) |
| 📌 **线索来源** | 8. Conclusions and Future Work §"Finding a pattern-preserving diagrammatic representation for disjunction and even more general features of SQL (such as grouping and aggregates) is an open problem." |
| 📮 **投稿建议** | 🗄️ **DB** · SIGMOD / VLDB ＋ 🗣️ NLP · ACL |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
该论文提出"模式同构"（pattern-isomorphism）来刻画跨 Datalog¬ / RA / TRC / SQL 的查询模式，证明 Relational Diagrams 能在非析取嵌套否定片段上保持模式，用户研究也显示它比 SQL 文本更快、更准地传达查询模式。作者明确指出，分组与聚合以及析取仍是开放问题。然而现实中的分析型 SQL 几乎都带 GROUP BY / HAVING / 聚合，这正是 LLM 生成 SQL 最常出错的地方（分组粒度错、聚合前后过滤混淆、计数重复）。如今 Text-to-SQL 已进入生产，**人如何快速判断生成的 SQL 是否表达了自己的意图**成了瓶颈：执行准确率需要标准答案，读 SQL 文本又太慢。关键 insight：模式同构本身就是介于"结果相等"（太宽松）和"语法相等"（太严格）之间的结构等价概念。把它扩展到聚合，可以同时得到可视化验证界面和一个更可靠的 Text-to-SQL 评测度量。

**💡 一句话 Idea**
把模式同构与 Relational Diagrams 扩展到"每个嵌套块带分组与聚合"的片段，并证明模式保持性；以此构建 LLM 生成 SQL 的可视化核验界面，同时把"聚合模式同构"作为 Text-to-SQL 的结构化评测度量，弥补执行准确率的假阳性。

**🛠️ 可能的解决方法**
1. **形式化**：定义片段 NDAgg：非析取 + 嵌套否定 + 每个作用域块可带 GROUP BY / 聚合 / HAVING。对聚合块扩展"表解联"（dissociation）定义：分组键作为块的界面变量，聚合作为块输出属性上的注解；证明 SQL、RA_γ 与扩展图示之间的模式保持双射。
2. **图示设计**：在原有否定作用域框之外引入"分组框"（框边列出分组键，框内为聚合输入，框外以带聚合函数标签的端口输出）；HAVING 画成分组框端口上的选择边。用最少新符号保证与原图示兼容。
3. **核验界面**：NL 问题、生成 SQL 与图示三栏联动；高亮"结构疑点"，即模式中出现与问题实体无关的自连接、分组键与问题量词不一致等，提示用户重点检查。
4. **结构化度量**：PatternMatch(gold, pred) = 1[两者在 NDAgg 下模式同构]，对超出片段的查询回退到执行准确率；用于检测 EX 的假阳性（结果碰巧相同但模式错误）。

**🧭 与最接近工作的区别**
- 源论文 (2024)：模式保持只覆盖非析取、无聚合的片段。
- QueryVis (Leventidis et al., SIGMOD 2020)：同一谱系的早期图示，不处理聚合，也没有模式保持证明。
- Test-suite accuracy (Zhong et al., EMNLP 2020)：用多数据库实例降低 EX 假阳性，仍基于执行结果而非结构模式，代价是需要生成大量数据库实例。

**🧪 验证方案**
- 用户研究：被试为 60 名众包参与者与 20 名数据分析师；材料取 BIRD / Spider 2.0 中带聚合的查询，混入真实 LLM 错误（来自 GPT 类模型的失败输出）；比较 SQL 文本、LLM 自然语言解释、扩展图示三种条件下的错误检出率、检出时间和信心校准。
- 度量研究：在 BIRD dev 上收集多个模型的预测，对比 EX、test-suite accuracy、PatternMatch 与人工判断的一致性（Cohen's κ）。
- 形式部分：给出定理与证明，并在 BIRD 全部查询上统计 NDAgg 覆盖率（预期大部分聚合查询落在片段内）。

🔑 `query visualization` `relational diagrams` `aggregation` `Text-to-SQL verification` `pattern-isomorphism` `human-in-the-loop`

[🔝 top](#top)

---

## 💡 Idea 14.12 — *Statistically Valid Assertions for Multi-Stage LLM Pipelines: Blame-Aware Placement with Prediction-Powered False-Failure Guarantees*

| | |
|:--|:--|
| 🎯 **源论文** | **SPADE: Synthesizing Data Quality Assertions for Large Language Model Pipelines** · Shreya Shankar et al. (UC Berkeley) · 📄 VLDB 2024 · [arXiv:2401.03038](https://arxiv.org/abs/2401.03038) |
| 📌 **线索来源** | 4.4 Limitations and Future Work §"Additionally, assessing the accuracy of FFR estimates with limited E′ and exploring methods to enhance FFR accuracy in the absence of large labeled datasets (e.g., via prediction-powered inference (Angelopoulos et al., 2023)), presents an interesting area for future work." + §"Our study focuses on single-prompt LLM pipelines, but more complex pipelines, such as those involving multiple prompts, external resources, and human interaction, present opportunities for auto-generating assertions for each pipeline component." |
| 📮 **投稿建议** | 🗄️ **DB** · VLDB / ICDE ＋ 🧪 ML · NeurIPS |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
SPADE 从 prompt 版本差异中合成候选断言，再用 ILP 在覆盖率 ≥ α、误报率 FFR ≤ τ 的约束下挑出最小断言集，已在 LangChain 上部署。但它存在两个明确缺口：(1) FFR 由极少量标注样本估计，ILP 约束的满足只是"点估计意义上"的，作者提出可以用 prediction-powered inference（PPI）改进；(2) 只支持单 prompt 管道，而生产中的 RAG / 智能体管道是多阶段 DAG，失败可能源于检索、生成或格式化中的任意一环。把断言只放在最终输出上，会让定位失败和误报控制都变得粗糙。关键 insight：PPI 可以把大量廉价的 LLM 评审标签和少量人工标签结合，给 FFR 与覆盖率构造**有效置信区间**。ILP 约束改为对置信上界成立后，就得到带统计保证的断言选择。多阶段情形下，用反事实重放（把某阶段输出替换为参考输出）为失败做阶段归因，就能把断言放到真正出错的阶段，尽早拦截。

**💡 一句话 Idea**
把 SPADE 的断言选择推广到多阶段 LLM 管道：用反事实重放做阶段级失败归因，用 PPI 为每个候选断言的误报率与覆盖率构造置信界，在"置信上界满足约束"的 ILP 中联合选择断言及其放置阶段，并用主动标注收紧起约束作用的置信区间。

**🛠️ 可能的解决方法**
1. **阶段归因**：管道表示为 DAG。对一次最终失败的运行，依次把各阶段输出替换为参考输出（更强模型或人工）后重放；若下游转为成功，则把失败归因到该阶段，得到阶段级失败标签 y_{run,stage}。
2. **PPI 估计**：对每个断言 a，FFR_a = P(a 失败 | 输出正确)。用 LLM 评审给全部运行打代理标签 ŷ，人工只标注 n 条，构造 PPI 估计 θ̂ = mean(f(ŷ)) − mean_n(f(ŷ) − f(y)) 及 1−δ 置信区间。多个断言之间做 Bonferroni / e-value 校正。
3. **选择 ILP**：变量 x_{a,s}（断言 a 放在阶段 s）。目标为最小化断言运行成本 Σ c_a x_{a,s}；约束：阶段级覆盖下界 LCB(Cov_s) ≥ α_s，整体误报上界 UCB(FFR) ≤ τ。保留 SPADE 的包含关系（subsumption）剪枝。
4. **主动标注**：每轮选出使"起作用约束"的置信区间宽度下降最多的样本交给人工标注，直到所有约束以统计意义满足或预算耗尽，这对应 SPADE 结论中提出的类似主动学习的开放问题。

**🧭 与最接近工作的区别**
- SPADE (2024)：单 prompt 管道，FFR 为小样本点估计，没有统计保证。
- EvalGen (Shankar et al., UIST 2024)：通过人机交互让评估标准与人类偏好对齐，没有置信保证和多阶段放置。
- Prediction-powered inference (Angelopoulos et al., Science 2023) 与 Active Statistical Inference (Zrnic & Candès, ICML 2024)：提供统计工具，没有用于数据质量断言的组合选择。

**🧪 验证方案**
- 基准：SPADE 公开的 9 条真实管道；多阶段管道：HotpotQA / MuSiQue 上的 RAG（检索 → 生成 → 引用格式化），以及 DocETL 风格的文档抽取管道。
- 指标：失败覆盖率、实际 FFR、置信区间的经验覆盖率（应 ≥ 1−δ）、达到约束所需的人工标注数、断言运行开销、失败被拦截的阶段（越早越好）。
- 对比：SPADE_cov / SPADE_sub、只用 LLM 评审标签（无 PPI 校正）、只用人工标签的经典置信区间、只在最终输出放断言。
- 消融：去掉阶段归因 / 去掉主动标注 / 不同 LLM 评审质量下 PPI 的增益。

🔑 `data quality` `LLM pipelines` `assertions` `prediction-powered inference` `integer linear programming` `RAG`

[🔝 top](#top)
