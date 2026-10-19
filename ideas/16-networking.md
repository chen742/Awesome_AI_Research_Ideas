<a id="top"></a>
# 📡 Computer Networking

> 从 SIGCOMM / NSDI 正式论文（以欧美团队为主）中提炼的网络方向 idea，覆盖 AI 训练集群的光互连与集合通信、数据中心故障缓解与网络感知调度、遥测传输、可编程数据平面 ML 与在网计算安全、实时视频码率控制与 SFU、UWB 无线定位，目标投稿 SIGCOMM / NSDI（备选 OSDI / MLSys / USENIX Security）。
> 符号说明：🎯 源论文 · 📌 线索来源 · 📮 投稿建议 · ⭐ Novelty · 🚀 Impact · 🧗 Difficulty · 🧪 验证方案 · 🔑 关键词 · 📄 会议正式论文

[⬅️ 返回主页](../README.md)

---

## 💡 Idea 16.1 — *Phase-Aligned Optical Time-Sharing: Co-Scheduling Transceiver-Level Circuit Reconfiguration with TP and EP Collectives for Fault-Resilient MoE High-Bandwidth Domains*

| | |
|:--|:--|
| 🎯 **源论文** | **InfiniteHBD: Building Datacenter-Scale High-Bandwidth Domain for LLM with Optical Circuit Switching Transceivers** · Chenchen Shou et al. (PKU) · 📄 SIGCOMM 2025 · [arXiv:2502.03885](https://arxiv.org/abs/2502.03885) ＋ **MixNet: A Runtime Reconfigurable Optical-Electrical Fabric for Distributed Mixture-of-Experts Training** · Xudong Liao et al. (HKUST) · 📄 SIGCOMM 2025 · [arXiv:2501.03905](https://arxiv.org/abs/2501.03905) |
| 📌 **线索来源** | InfiniteHBD 7. Discussion §"Ring topology in InfiniteHBD struggles with AllToAll communication (e.g., EP)" + MixNet 9. Discussion §"Therefore, the radius of the EP all-to-all communications does not grow linearly with the number of experts, as multiple small experts will be packed into one GPU for training efficiency." |
| 📮 **投稿建议** | 📡 **Networking** · SIGCOMM / NSDI ＋ 🧪 ML · MLSys / NeurIPS |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★★★ |

**🔍 深入分析**
InfiniteHBD 把硅光 OCS 做进每个 GPU 的光模块（OCSTrx，60–80 μs 切换），用 K-Hop Ring 获得数据中心级 HBD 与近乎理想的故障爆炸半径，但作者承认环拓扑对 EP 的 AllToAll 是 O(p²)，且整套设计"针对单一并行维度优化"；他们提出的"时分多维度"只停留在讨论层面。MixNet 则用区域级 OCS 为 MoE 的 all-to-all 动态重构拓扑，并指出细粒度专家使 EP 半径不随专家数线性增长。两者合起来揭示一个空隙：**收发器级快速光切换 + EP 半径有界** 意味着可以在一次迭代内按层相位在 TP 环与 EP 拓扑之间时分复用同一组光端口，而目前没有工作把电路重构、并行维度和故障旁路放进同一个调度问题。关键 insight：MoE 训练的通信相位（TP allreduce → EP dispatch → EP combine）在层内周期性、可预测，且 μs 级切换远小于每层计算时间，重构可被完全藏进计算阴影。

**💡 一句话 Idea**
把每个 GPU 的 OCSTrx 端口视为可时分复用的资源，联合求解"层相位 → 电路配置"时间表，使 TP 环、EP 低直径拓扑（n±2^i 连接）与故障旁路线在同一组光端口上按计算阴影轮换，以接近交换机式 HBD 的 MoE 吞吐换取 GPU 中心式 HBD 的成本与故障隔离。

**🛠️ 可能的解决方法**
1. **问题建模**：输入为每层的流量矩阵序列（TP 环 allreduce 体量、EP 由上一迭代门控统计预测的 token 分布）、OCSTrx 切换延迟 δ、端口数 K 与故障节点集 F；决策为每个时隙每个端口的电路配置；目标为最小化迭代时间 Σ_layer max(compute, comm(config)) ＋ 未被计算掩盖的重构开销，约束为每端口每时隙至多一条电路、δ 必须落在计算窗口内、故障节点必须被旁路。
2. **离线模板 + 在线选择**：离线用 ILP 为 {TP 组大小, EP 度, 故障模式} 预计算少量配置模板（环 / 超立方 / Bruck 风格对数直径拓扑）；在线根据上一迭代的专家负载直方图选择模板，并以 Binary-Exchange / Bruck 算法实现 O(p log p) all-to-all，热点专家对应的 GPU 对在额外时隙获得直连电路。
3. **故障语义**：沿用 InfiniteHBD 的主 / 备线路，把"备线"同时用作 EP 的 2^i 跳连接；节点故障时求解最小改动的模板修补（局部重编号），保证爆炸半径仍为单节点。
4. **转发与编排**：避免 InfiniteHBD 讨论中提到的"需要 GPU 路由能力"，只在单跳直连电路上传输，多跳由集合通信算法分阶段完成；与 Megatron / NCCL 集成，通过自定义 collective 插件在层边界触发切换。
5. **成本控制**：大规模用包级 / 流级模拟器评估，小规模用商用光交换机 + 16–32 GPU 原型验证切换时序与 NCCL 集成。

**🧭 与最接近工作的区别**
- InfiniteHBD (SIGCOMM 2025)：环拓扑针对单维度并行，多维度与 AllToAll 仅在讨论中提出；本 idea 将时分多维度作为一等调度问题求解。
- MixNet (SIGCOMM 2025)：区域级 OCS 为 EP 重构，粒度在区域交换机层面；本 idea 在收发器层面按层相位切换并与故障旁路共享端口。
- TopoOpt (Wang et al., NSDI 2023)：按训练作业一次性优化光拓扑，不在迭代内随通信相位切换。

**🧪 验证方案**
- 工作负载：Mixtral 8×22B、DeepSeek-V3 规模的细粒度 MoE（EP=64）及稠密 Llama-3 70B 作为对照；指标：MFU、迭代时间、EP all-to-all 完成时间、每 GPU 互连成本与功耗、故障下 GPU 利用率与爆炸半径。
- 平台：ns-3 / htsim 包级模拟 2k–8k GPU，结合公开的大规模训练故障统计（如 Llama 3 报告的中断分布）注入故障；小规模光交换原型测重构时序。
- 对比：NVL-72 式交换机 HBD、TPUv4 式 3D-torus + OCS、InfiniteHBD 原设计、MixNet。
- 消融：去掉在线模板选择（固定拓扑）/ 去掉热点专家直连 / δ 从 10 μs 扫到 1 ms，找出时分复用失效的切换延迟拐点。

🔑 `optical circuit switching` `high-bandwidth domain` `mixture-of-experts` `all-to-all` `topology reconfiguration` `fault tolerance`

[🔝 top](#top)

---

## 💡 Idea 16.2 — *BoundedRDMA: NIC-Offloaded Unreliable Bounded Transport with Loss-Spreading Transforms for Tail-Optimal Collectives in Shared Clouds*

| | |
|:--|:--|
| 🎯 **源论文** | **OptiReduce: Resilient and Tail-Optimal AllReduce for Distributed Deep Learning in the Cloud** · Ertza Warraich et al. (Purdue) · 📄 NSDI 2025 · [arXiv:2310.06993](https://arxiv.org/abs/2310.06993) |
| 📌 **线索来源** | 6 Limitations & Future Work §"However, these implementations are still susceptible to tail effects in the network (e.g., packet drops and retransmissions)." + §"As a next step, we could explore offloading OptiReduce ’s transport onto hardware using RDMA’s Unreliable Connected (UC) or Unreliable Datagram (UD) queue pairs" |
| 📮 **投稿建议** | 📡 **Networking** · SIGCOMM / NSDI ＋ 🧪 ML · MLSys / NeurIPS |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
OptiReduce 利用分布式训练对少量梯度丢失的容忍，用"有界不可靠传输（UBT）+ 自适应超时 + Hadamard 变换"把 AllReduce 的尾延迟砍掉，在公有云共享环境中比 Gloo / NCCL 快 30–70%。但它的传输跑在 CPU 上（DPDK），在 400G 链路下 CPU 本身就是瓶颈；而 RDMA 虽然卸载了数据搬运，其 RC 语义仍会因丢包重传而放大尾部。作者明确把"在 RDMA UC/UD 上实现 UBT"列为下一步。空隙在于：RDMA UC 没有可靠性也没有"截止时间"概念，现有 NIC 无法表达"到点就收、缺的置零"的语义，而丢失的分布又直接决定收敛性。关键 insight：只要发送前对梯度做随机正交变换，任意数据块丢失都等价于对全向量施加无偏、方差有界的噪声，因此接收端只需一个按块的到达位图和一个截止时间，就能在 NIC / DPA 侧完成"有界收集"，完全不需要重传。

**💡 一句话 Idea**
在 RDMA UC 上实现带截止时间的分块写入与到达位图，由 NIC 侧（BlueField-3 DPA）执行超时判定和缺块置零，GPU 侧做随机 Hadamard 变换把丢块转为无偏噪声，从而在不触碰 CPU 的情况下获得 OptiReduce 的尾部收益。

**🛠️ 可能的解决方法**
1. **传输语义**：每个 collective 阶段的数据切成固定大小块，使用 UC `RDMA_WRITE_WITH_IMM`，立即数携带 (round, chunk_id)；接收端 DPA 线程维护每 round 的位图，到达比例 ≥ 1−ε 或截止时间 T_r 到期即发布完成事件，缺失块按 0 处理并记录丢失率。
2. **截止时间自适应**：T_r 取前 W 轮块到达时间分布的分位数 q（如 P99）乘以安全系数，q 按"迭代时间 vs 有效丢失率"的在线拉格朗日乘子调整；丢失率持续超过 ε 时自动退回 RC 路径。
3. **损失扩散变换**：在 GPU 上对每个 bucket 做随机符号 + 快速 Walsh-Hadamard 变换（O(d log d)，与 NCCL kernel 融合），接收端逆变换后缺块误差在全坐标上均匀分布；理论上给出 SGD 收敛界：额外方差 ∝ ε·‖g‖²，与无偏压缩分析同形。
4. **集合算法**：沿用 OptiReduce 的 Transpose AllReduce，但把 reduce 放到 GPU（而非 CPU），NIC 只负责有界收集；同一框架支持 reduce-scatter / all-gather，以便接入 FSDP。
5. **工程成本**：基于 libibverbs + DOCA DPA 实现，8–64 节点、100/400G RoCE 即可；需要的仅是商用 ConnectX-7 / BlueField-3。

**🧭 与最接近工作的区别**
- OptiReduce (NSDI 2025)：UBT 在 CPU 上实现；本 idea 把截止时间语义下沉到 RDMA UC + NIC 处理器，并把 reduce 移到 GPU。
- MLT (Wang et al., NSDI 2024)：利用梯度重要性做选择性丢包与优先级，依赖交换机支持；本 idea 不改交换机，靠变换使任意丢失均无偏。
- SwitchML (Sapio et al., NSDI 2021)：交换机内聚合追求精确结果；本 idea 面向无法部署在网聚合的公有云租户。

**🧪 验证方案**
- 环境：公有云 / 自建 RoCE 集群，用背景流（iperf、存储流量）与 tc 注入丢包及时延抖动制造共享环境尾部；指标：AllReduce P50/P99 时间、训练吞吐、Time-to-Accuracy、CPU 周期 / 迭代、实际丢失率。
- 模型：BERT-large、GPT-2 / Llama-7B 微调、ResNet-50，覆盖 DDP 与 FSDP。
- 对比：NCCL (RC)、Gloo、OptiReduce (DPDK)、仅 UC 不做变换（验证变换的必要性）。
- 假设检验：(a) 同等丢失率下有变换的最终精度与无损基线差 <0.1%；(b) 400G 下 CPU 实现成为瓶颈而 NIC 实现不随带宽退化；(c) 截止时间自适应在背景负载阶跃变化时 3 轮内收敛。

🔑 `AllReduce` `RDMA UC` `bounded transport` `tail latency` `Hadamard transform` `SmartNIC`

[🔝 top](#top)

---

## 💡 Idea 16.3 — *Swarm-L: Ranking Failure Mitigations by Collective Completion Time in Lossless RDMA Training Fabrics*

| | |
|:--|:--|
| 🎯 **源论文** | **Enhancing Network Failure Mitigation with Performance-Aware Ranking** · Pooria Namyar et al. (USC) · 📄 NSDI 2025 · [arXiv:2305.13792](https://arxiv.org/abs/2305.13792) |
| 📌 **线索来源** | 5 Discussion and Limitations §"Cloud providers increasingly use RDMA [ 22 , 58 ] for internal traffic. We can modify swarm ’s CLPEstimator to (a) detect and account for pauses and (b) model loss-recovery approaches when losses happen." |
| 📮 **投稿建议** | 📡 **Networking** · SIGCOMM / NSDI ＋ 🖥️ Systems · OSDI |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
swarm 把"故障发生后该做哪个缓解动作（关链路、隔离交换机、改 WCMP 权重……）"变成按连接级性能（CLP：短流 FCT、长流吞吐）排序的问题，用可扩展的近似估计器在 Clos 网络上选出性能惩罚低几个数量级的动作。但它假设有损 TCP + ECMP，作者明确把 RDMA 的 PFC 暂停与丢包恢复列为未来工作，也没有考虑直连拓扑和瞬态影响。这在 AI 训练集群里恰恰是最痛的地方：RoCE 网络中一条降级链路会通过 PFC 反压扩散成 HoL 阻塞，而同步式集合通信的完成时间由最慢的一条流决定，"平均 FCT"完全不能反映作业代价。关键 insight：训练流量周期性强、可从集合通信日志中精确复原，因此可以把 CLP 换成"每个作业的迭代时间膨胀"，并在估计器里显式建模 PFC 暂停传播与 go-back-N 重传，使缓解排序直接以 JCT 为目标。

**💡 一句话 Idea**
扩展 swarm 的估计器，使其在 RoCE 网络中建模 PFC 暂停传播与 go-back-N 恢复，并以集合通信为单位（coflow 的最大完成时间）评估每个候选缓解动作对各训练作业迭代时间的影响，输出 JCT 感知的缓解排序。

**🛠️ 可能的解决方法**
1. **流量输入**：从 NCCL / 集合通信库日志与作业调度器中重建每个作业的通信图（ring / tree 阶段、每阶段字节数、rank→NIC 映射），把训练流量表示为周期性 coflow，存储 / 推理流量仍用 swarm 的流分布。
2. **估计器**：在 swarm 的近似 max-min 吞吐模型上增加两项：(a) PFC 暂停传播：对每条拥塞或降级链路，按缓冲阈值与入口速率计算上游暂停占空比，迭代到不动点；(b) 丢失恢复：对随机丢包链路，用 go-back-N 的有效吞吐公式 (1−p)/(1+p·W) 折算。作业代价 = Σ_phase max_{flow∈phase} 完成时间。
3. **候选动作空间**：除 swarm 原有动作外，加入训练特有动作：重映射 rank 绕开故障 NIC、降低 DCQCN 速率上限、作业级 checkpoint-restart 与迁移（代价 = 重启开销 + 预计修复时间内的损失）、不处理。
4. **排序目标**：多作业场景下最小化 Σ_job w_job · 迭代时间膨胀，可选 CVaR 形式以兼顾风险；对瞬态动作（交换机重启）用短时窗内的峰值代价计入。
5. **规模与成本**：估计器需在分钟内完成万卡规模评估；对估计不确定的前 k 个动作再用流级模拟（m3 / Parsimon 风格）精排。

**🧭 与最接近工作的区别**
- swarm (NSDI 2025)：面向有损 TCP 与 CLP 指标，RDMA 列为未来工作；本 idea 建模 PFC / 重传并以集合通信 JCT 为目标。
- CorrOpt (Zhuo et al., SIGCOMM 2017)：针对链路丢包损坏决定是否关闭链路，以容量约束为准则，不估计应用性能。
- NetPilot (Wu et al., SIGCOMM 2012)：自动化缓解但以网络利用率启发式为准，不涉及训练作业语义。

**🧪 验证方案**
- 平台：HPCC 开源 ns-3 RDMA 模拟器上搭建 k=16 fat-tree 与 rail-optimized 拓扑，注入链路降速、随机丢包（10⁻⁵–10⁻²）、交换机故障等典型故障；工作负载为多租户 Llama / MoE 训练 + 存储背景流。
- 指标：所选动作的迭代时间膨胀与"真值最优动作"之比、排序 Kendall τ、估计器运行时间、小流 P99 FCT。
- 对比：swarm 原版（视作有损 TCP）、CorrOpt 规则、"一律隔离"运维默认策略、Oracle（全量包级模拟）。
- 关键假设检验：(a) 忽略 PFC 时排序错误率显著上升；(b) 以 JCT 为目标与以平均 FCT 为目标会选出不同动作，且前者使训练作业损失更小。

🔑 `failure mitigation` `RDMA` `PFC` `collective communication` `job completion time` `datacenter operations`

[🔝 top](#top)

---

## 💡 Idea 16.4 — *Deadline-Bounded Scavenger Telemetry: Slack-Constrained Backpressure Routing with Collector Aggregation for Timely Network-Wide Telemetry*

| | |
|:--|:--|
| 🎯 **源论文** | **Enabling Silent Telemetry Data Transmission with InvisiFlow** · Yinda Zhang et al. (UPenn) · 📄 NSDI 2025 · [USENIX](https://www.usenix.org/conference/nsdi25/presentation/zhang-yinda) |
| 📌 **线索来源** | Discussion §"Heretofore, InvisiFlow was presented as a framework that minimizes loss but does not bound the latency of reports." + §"InvisiFlow may also struggle with networks that need a large number of distinct collector types, as it requires the use of a separate buffer allocation for every type." |
| 📮 **投稿建议** | 📡 **Networking** · SIGCOMM / NSDI ＋ 🖥️ Systems · OSDI |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
InvisiFlow 把遥测数据当作最低优先级流量，借"拥塞梯度"在全网未用带宽中机会式转发，从而既不影响用户流量又维持高持续吞吐。但它只最小化丢失，不限定报告时延；且每种收集器需要单独的缓冲分配，收集器类型一多就不可扩展。这两点恰好卡住了最需要遥测的场景：故障定位、拥塞诊断、安全检测都要求报告在秒级甚至亚秒级送达，而现代网络往往同时运行路径追踪、INT、丢包定位等多类收集器。现有降采样 / sketch 方法以精度换带宽，不解决传输时效。关键 insight：拥塞梯度转发本质上是 backpressure 路由，而带截止时间的 backpressure 可以用"剩余松弛 ≥ 到收集器的最小跳数 × 每跳最小时延"作为可行性约束，在松弛耗尽前把极少量报告升级到一个预留的小速率保底通道——这样延迟有界且对用户流量的影响有上界。

**💡 一句话 Idea**
给每个遥测报告附带截止时间，交换机只在"剩余松弛允许"的邻居集合内做拥塞梯度转发，松弛将尽时升级到占链路 ε 容量的保底类；同时把多类收集器按目的地聚合为共享缓冲中的虚拟队列，使延迟有界、收集器数量可扩展。

**🛠️ 可能的解决方法**
1. **报告头与松弛计算**：报告头携带 (deadline, collector_group, type)；每台交换机维护到各收集器组的最小跳数表 h(c)，转发候选集为 {邻居 n : h_n(c) < h(c) 或 slack − d_hop ≥ h_n(c)·d_min}，在候选中按拥塞梯度选择。
2. **升级保底通道**：slack < h(c)·d_min + margin 时报告进入高一级优先级、由 token bucket 限速在 ε·C；给出用户流量最坏影响 ≤ ε 的上界与报告延迟上界。
3. **收集器聚合**：把收集器按位置聚合成少量 anycast 组，交换机只维护"组"粒度的缓冲计数，组内按 type 标签在收集端分发；用共享缓冲 + 动态阈值代替每类固定分区，缓冲状态复杂度从 O(#types) 降到 O(#groups)。
4. **理论动机**：用 Lyapunov drift-plus-penalty 分析，证明在 ε 保底下截止期内送达率的下界，并量化 ε 与送达率的权衡曲线。
5. **工程可行性**：在 Tofino2 上实现（松弛递减用寄存器 + 时间戳），候选集查表在一个 stage 内完成。

**🧭 与最接近工作的区别**
- InvisiFlow (NSDI 2025)：最小化丢失但不限定时延，每类收集器独立缓冲；本 idea 加入截止时间可行性约束与收集器组聚合。
- PINT (Ben Basat et al., SIGCOMM 2020)：在源端压缩遥测数据量，属于减少数据而非改善传输通道，可与本 idea 叠加。
- NetSeer (Zhou et al., SIGCOMM 2020)：在数据平面检测与压缩事件，传输仍走常规通道，不处理与用户流量的竞争。

**🧪 验证方案**
- 平台：Tofino2 测试床（4–8 台交换机的 leaf-spine）+ ns-3 k=8 fat-tree 大规模模拟；工作负载：Hadoop、WebSearch 流分布，负载 30–90%。
- 指标：截止期内送达率、报告时延 P99、Age-of-Information、用户流 FCT 膨胀、交换机缓冲 / SRAM 占用随收集器类型数（2→32）的变化。
- 对比：InvisiFlow 原版、低优先级 UDP、pull-based 收集、全部走高优先级。
- 消融：去掉松弛约束 / 去掉保底通道 / 去掉收集器聚合；ε 扫描。

🔑 `network telemetry` `backpressure routing` `deadline` `scavenger transport` `programmable switches` `Age of Information`

[🔝 top](#top)

---

## 💡 Idea 16.5 — *Evasion-Robust Partitioned Trees: Switch-Anchored Adaptive Windowing and Certified Robustness for Line-Rate Traffic Classification*

| | |
|:--|:--|
| 🎯 **源论文** | **SpliDT: Partitioned Decision Trees for Scalable Stateful Inference at Line Rate** · Murayyiam Parvez et al. (Purdue) · 📄 SIGCOMM 2025 · [arXiv:2509.00397](https://arxiv.org/abs/2509.00397) |
| 📌 **线索来源** | 6 Limitations & Future Work §"Currently, SpliDT uses fixed per-flow window sizes, which may not always reflect real-world traffic dynamics." + §"SpliDT ’s reliance on flow size information stored in packet headers makes it vulnerable to scenarios where this information is hacked or spoofed." |
| 📮 **投稿建议** | 📡 **Networking** · SIGCOMM / NSDI ＋ 🔐 Security · USENIX Security |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
SpliDT 把决策树切成按窗口执行的子树，在每个窗口只提取当前子树需要的特征，使可编程交换机上的有状态推理扩展到百万级流。作者坦承两点：窗口大小固定，不随流的动态变化；窗口边界依赖包头中的流大小信息，可被伪造，进而导致误分类、资源错配甚至 DoS。对于入侵检测这类首要应用，这不是边角问题：攻击者完全控制自己流的包长、时序与填充，固定窗口给了他精确的"在哪一步改变行为"的地图。现有数据平面 ML 工作（NetBeacon、Leo、Pegasus）几乎都以良性分布评估精度，没有威胁模型。关键 insight：窗口边界应由交换机自身观测的状态（已见包数、字节数、时间）锚定，而非信任包头；同时，树模型的鲁棒性可以精确验证（MILP），因此可以在 BO 训练管线里把"可证明的最小规避代价"作为与精度、资源并列的优化目标。

**💡 一句话 Idea**
用交换机本地计数器锚定窗口边界并学习按置信度提前终止的自适应窗口策略，在训练中加入受攻击者可控特征约束的对抗扰动，并用 MILP 验证给出每个子树的最小规避代价，使分区树在线速下兼具精度与可证明的抗规避性。

**🛠️ 可能的解决方法**
1. **威胁模型**：攻击者控制自己流的包长、包间隔、填充与插入哑包（受带宽 / 时延预算约束），不能修改他人流与交换机状态；目标为规避检测或耗尽每流状态。
2. **switch-anchored 窗口**：窗口边界只由寄存器中的包计数 / 时间戳决定；自适应窗口建模为 early-exit：每个子树输出类别与置信度，置信度 ≥ τ_k 时终止，τ_k 与窗口长度由 BO 在"精度 / 决策时延 / 寄存器占用"多目标下搜索。
3. **鲁棒训练**：对攻击者可控特征（包长统计、IAT 统计）在预算 B 内做对抗扰动，用鲁棒分裂准则（最坏情况信息增益）训练每个子树；对不可控特征（如服务端响应）不扰动。
4. **可证明性**：对编译后的每个子树用 MILP 求最小规避扰动（L∞ / 代价加权），把"最小规避代价"作为 BO 的约束；附带 DoS 分析：流状态分配延迟到首窗口置信度不足时才发生。
5. **硬件可行性**：沿用 SpliDT 的 Tofino 资源模型，增加的只是每流一个置信度寄存器与少量 stage。

**🧭 与最接近工作的区别**
- SpliDT (SIGCOMM 2025)：固定窗口、信任包头流大小字段、无威胁模型；本 idea 以交换机状态锚定窗口并加入可证明的抗规避。
- NetBeacon (Zhou et al., USENIX Security 2023)：多阶段树推理与流状态管理，阶段划分固定，未分析自适应攻击者。
- Chen et al. (NeurIPS 2019) 树模型鲁棒性验证：离线、无硬件约束；本 idea 将其嵌入数据平面资源约束下的训练管线。

**🧪 验证方案**
- 数据：CIC-IDS2017/2018、UNSW-NB15、ISCX VPN-nonVPN；硬件：Tofino / Tofino2 线速回放。
- 指标：Macro-F1、决策时延（包数）、支持流数、自适应攻击下的规避成功率与所需扰动代价、伪造流大小字段时的误分类率与资源耗尽程度。
- 对比：SpliDT、NetBeacon、Leo；攻击者包括随机填充、基于代理模型的梯度/搜索攻击、针对固定窗口的定时切换攻击。
- 消融：仅自适应窗口 / 仅鲁棒训练 / 仅 switch-anchored 边界。

🔑 `in-network ML` `decision trees` `programmable switches` `adversarial robustness` `intrusion detection` `adaptive windowing`

[🔝 top](#top)

---

## 💡 Idea 16.6 — *Least-Privilege In-Network Computing: Field-Scoped Encryption and Verifiable Modification for Message Transports with Offload Pathlets*

| | |
|:--|:--|
| 🎯 **源论文** | **MTP: Transport for In-Network Computing** · Tao Ji et al. (UT Austin) · 📄 NSDI 2025 · [USENIX](https://www.usenix.org/conference/nsdi25/presentation/ji) |
| 📌 **线索来源** | Discussion §"Though out of our scope, security remains an open problem for, not just MTP, but INC in general, because INC involves examining and tampering with packet payload by the network, which is exactly what today’s transport-layer security (TLS) strives to prevent." |
| 📮 **投稿建议** | 📡 **Networking** · SIGCOMM / NSDI ＋ 🔐 Security · USENIX Security |
| ⭐ Novelty | ★★★★★ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
MTP 把在网计算（INC）卸载点抽象为"pathlet"，为其提供按消息的可靠交付与拥塞控制，使 L7 INC 应用可以在真实传输层上运行。但作者直接承认：INC 需要网络查看并修改载荷，恰恰与 TLS 的目标冲突，因此安全仍是开放问题。当前现实是二选一：要么端到端加密而放弃 INC，要么明文暴露全部载荷给所有中间设备。这对数据中心尤其尴尬——零信任与机密计算正在把加密推向每条内部 RPC（同批 SMT 工作把 TLS 记录层接入消息传输即是一例）。关键 insight：INC 的典型操作只触及消息中少数几个字段（键、计数器、聚合值），而 MTP 已经以消息为单位，可以自然地把消息划分为若干"字段上下文"，为每个 pathlet 分发只覆盖其所需字段的密钥，并要求 pathlet 对其修改附加可验证的证明，从而实现最小权限的 INC。

**💡 一句话 Idea**
在消息传输层引入字段级加密上下文：端点为每个 pathlet 分发仅覆盖其所需字段的读 / 写密钥，pathlet 对修改附加逐跳 MAC，接收端据此验证"只有被授权的 pathlet、只以被授权的方式修改了被授权的字段"。

**🛠️ 可能的解决方法**
1. **威胁模型**：链路上的被动 / 主动攻击者；被攻陷或好奇的 pathlet（可读写其所持密钥覆盖范围内的内容，可能篡改或重放）；端点与控制面可信。
2. **消息格式**：MTP 消息 = 头部 + 若干字段段，每段有独立 AEAD 上下文（无访问 / 只读 / 读写）；仿 mcTLS 思想，但上下文与 MTP 的 pathlet 发现过程绑定，端点在建立会话时按应用策略声明"pathlet P 可读 key、可写 value"。
3. **可验证修改**：写权限 pathlet 在修改字段后重新加密该段，并在消息尾部追加 (pathlet_id, 字段, 新段的 MAC) 链；接收端检查 MAC 链与策略一致。对 Tofino 类交换机无法做 AES 的情形，采用"明文但带 SipHash 认证"的弱化模式，并在安全分析中明确其保密性损失。
4. **硬件映射**：SmartNIC / FPGA pathlet 使用板载加密引擎；主机端复用 NIC 的 TLS 发送侧卸载，接收端在软件中验证 MAC 链。
5. **形式化验证**：用 Tamarin / ProVerif 对密钥分发、字段访问与 MAC 链协议建模，证明保密性与修改授权属性。

**🧭 与最接近工作的区别**
- mcTLS (Naylor et al., SIGCOMM 2015)：为 HTTP 中间盒提供多上下文 TLS，基于字节流、面向软件中间盒；本 idea 面向消息传输与硬件 pathlet，并提供修改链验证。
- BlindBox (Sherry et al., SIGCOMM 2015)：在加密流量上做模式匹配，仅支持检测，不支持修改载荷。
- SMT (Gao et al., 2025)：把 TLS 记录层与数据中心消息传输结合并利用 NIC 卸载，但仍是端到端加密，不允许 INC 读写。

**🧪 验证方案**
- 应用：MTP 论文的 INC 应用（如在网 KV 缓存、L7 负载均衡）+ 在网聚合；测试床：MTP 原型 + BlueField / FPGA pathlet + Tofino。
- 指标：消息吞吐与 P99 时延相对明文 MTP 与端到端 TLS（禁用 INC）的开销、pathlet 加解密吞吐、MAC 链长度带来的字节开销、CPU 周期 / 消息。
- 安全评估：Tamarin 证明；红队实验（被攻陷 pathlet 越权读写、重放、删除 MAC 链）检测率 100%。
- 消融：字段粒度 vs 整消息粒度加密；SipHash 弱化模式 vs AES 模式。

🔑 `in-network computing` `transport security` `least privilege` `message transport` `SmartNIC offload` `formal verification`

[🔝 top](#top)

---

## 💡 Idea 16.7 — *Confounder-Aware Offline RL for Real-Time Video Rate Control: Inferring Latent Path Capacity from Telemetry Logs with Safe Fallback*

| | |
|:--|:--|
| 🎯 **源论文** | **Mowgli: Passively Learned Rate Control for Real-Time Video** · Neil Agarwal et al. (Princeton) · 📄 NSDI 2025 · [arXiv:2410.03339](https://arxiv.org/abs/2410.03339) |
| 📌 **线索来源** | 7 Discussion §"Incorporating insights from these works into Mowgli and other video conferencing systems is a promising avenue for future exploration, such as improving the critic by explicitly inferring latent confounders." + §"In the case of Mowgli, encountering previously unseen network conditions (e.g., new bandwidth ranges) would necessitate a model update" |
| 📮 **投稿建议** | 📡 **Networking** · SIGCOMM / NSDI ＋ 🧪 ML · MLSys / NeurIPS |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
Mowgli 只用 GCC 在生产中已产生的遥测日志做离线强化学习，避免在线探索造成的 QoE 损失，并通过保守策略在数据不足时模仿 GCC。作者指出两个未解决问题：日志里存在未记录的潜在混杂因素（如瓶颈容量、交叉流量），使 critic 的反事实估计有偏；遇到训练分布外的网络条件需重新训练。这两点本质上是同一问题：策略的"状态"缺少真正决定动力学的隐变量，导致既估不准也无法判断何时越界。Veritas 已证明可以从 ABR 日志中推断潜在带宽，但它用于改进模拟而非直接学习控制策略。关键 insight：在实时视频中，发送速率、排队时延与丢包之间的关系由瓶颈容量强约束，可以用状态空间模型从 GCC 日志推断容量的后验分布，把后验均值与不确定度同时送进 critic——前者去混杂，后者天然成为 OOD 检测信号，用于触发安全回退。

**💡 一句话 Idea**
从 GCC 遥测日志中用隐马尔可夫 / 状态空间模型推断瓶颈容量的后验，将其作为离线 RL critic 的输入来去混杂，并以后验不确定度和数据覆盖度驱动 SPIBB 式安全策略改进，在分布外条件下自动退回 GCC。

**🛠️ 可能的解决方法**
1. **隐变量推断**：对每个会话构建状态空间模型：隐状态 = (瓶颈容量 C_t, 交叉流量 X_t)；观测 = 发送速率、接收速率、单向时延梯度、丢包；发射模型基于排队动力学（时延增长 ∝ (send − C + X)/C），用粒子滤波或摊销变分推断得到 p(C_t | 日志)。
2. **critic 去混杂**：critic 输入 = 原始特征 + 后验均值 / 方差，训练采用 CQL 或 IQL 等保守离线 RL 目标；奖励沿用 Mowgli 的 QoE 组合（码率、帧时延、卡顿）。
3. **安全策略改进**：采用 SPIBB 思想：仅在 (状态, 动作) 的数据计数 ≥ N 且容量后验方差低于阈值时允许偏离 GCC，其余情形回退 GCC 动作；给出相对 GCC 不劣的高概率保证。
4. **持续更新**：OOD 检测命中率作为触发信号，自动把新条件下的 GCC 日志加入训练集，周期性再训练，无需在线探索。
5. **工程成本**：推断与训练在离线完成；部署模型为小型 MLP，推理开销与 Mowgli 相同。

**🧭 与最接近工作的区别**
- Mowgli (NSDI 2025)：离线 RL 但 critic 不建模潜在混杂，OOD 需人工重训。
- Veritas (Alomar et al., SIGCOMM 2023)：从 ABR 日志推断潜在带宽用于反事实模拟，不直接学习控制策略。
- CausalSim (Alomar et al., NSDI 2023)：用因果推断去偏的 trace 驱动模拟器，同样用于评估而非策略学习。

**🧪 验证方案**
- 数据：Mahimahi 仿真 + 公开带宽轨迹（FCC 宽带、Norway 3G/HSDPA、Puffer 测量轨迹）生成 GCC 日志；真实 WebRTC 端到端测试（含蜂窝与 Wi-Fi）。
- 指标：平均视频码率、帧时延 P95、卡顿率、QoE；容量推断误差（在仿真中可得真值）。
- 对比：GCC、Mowgli、在线 RL（如 Pensieve 风格的 RTC 变体）、无隐变量的离线 RL。
- 关键假设检验：(a) 去混杂后 critic 的反事实价值误差下降；(b) 在训练时未出现的带宽区间，安全回退使 QoE 不劣于 GCC。

🔑 `real-time video` `rate control` `offline reinforcement learning` `latent confounders` `WebRTC` `safe policy improvement`

[🔝 top](#top)

---

## 💡 Idea 16.8 — *E2EE at Line Rate: Dual-Layer Authentication for Programmable-Switch SFUs and Their Cascades*

| | |
|:--|:--|
| 🎯 **源论文** | **Scalable Video Conferencing Using SDN Principles** · Oliver Michel et al. (Princeton) · 📄 SIGCOMM 2025 · [arXiv:2503.11649](https://arxiv.org/abs/2503.11649) |
| 📌 **线索来源** | 8. Discussion §"In Scallop, neither mechanism is currently implemented. The main challenge is key distribution: WebRTC’s split-proxy design uses a separate key for each P2P connection, exchanged between SFU and client." |
| 📮 **投稿建议** | 📡 **Networking** · SIGCOMM / NSDI ＋ 🔐 Security · USENIX Security |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
Scallop 观察到 SFU 的主要工作是复制与丢弃媒体包，于是把这部分下沉到 Tofino2 数据平面、控制面只处理信令与码率适配，可扩展性比 32 核 SFU 服务器高 7–210 倍。但它尚未实现 SRTP 加密与认证：WebRTC 的逐连接密钥与"一个发送者复制给多个接收者"的数据平面不兼容；SFU 改写 RTP 头字段（SSRC、序号）后，发送者的头部 HMAC 就失效。论文给出方向（集中分发密钥、硬件算头部 HMAC），但没有设计与安全论证。空隙在于：需要一个同时满足"SFU 不可读媒体（E2EE）""SFU 可以改写头部""接收者能区分发送者篡改与 SFU 合法改写"的协议，并能在交换机流水线约束下实现。关键 insight：把认证拆为两层——发送者对载荷与不可变字段做端到端认证（SFrame 式，密钥由 MLS 群组管理），SFU 只对它改写的少数可变字段做逐跳 MAC，交换机只需在短头部上计算 SipHash 级别的 MAC。

**💡 一句话 Idea**
为数据平面 SFU 设计双层认证：端到端层用 MLS 群组密钥对载荷与不可变头字段做 SFrame 式 AEAD，逐跳层由交换机对其改写的 RTP 可变字段计算 SipHash MAC，使 Scallop 及其级联拓扑在线速下获得与 WebRTC 同等甚至更强的安全性。

**🛠️ 可能的解决方法**
1. **威胁模型**：网络攻击者可窃听、篡改、重放；SFU（交换机及其控制面）诚实但好奇——可转发、丢弃、改写可变头部，但不应读媒体或伪造媒体；会议参与者集合由 MLS 管理，成员变动时需前向 / 后向保密。
2. **端到端层**：发送者对 (payload, 不可变字段：原始 SSRC、帧计数器、层 ID) 做 AEAD，密钥由 MLS epoch 派生；接收者据此验证来源与完整性，SFU 无需密钥。
3. **逐跳层**：控制面为每个 (SFU 出端口, 接收者) 派生 MAC 密钥，经 DTLS 下发给接收者；交换机改写 SSRC / 序号后，对 12 字节可变字段 + 计数器计算 HalfSipHash 并写入扩展头；接收者验证以检测外部篡改与重放。
4. **级联支持**：多台交换机级联时，每跳覆盖上一跳 MAC（只验最后一跳），端到端层不变；控制器统一管理多台交换机的密钥轮换。
5. **硬件与安全证明**：在 Tofino2 上评估 HalfSipHash 所需 stage 与对每包复制扇出数的影响；用 Tamarin 证明端到端认证与逐跳认证属性。

**🧭 与最接近工作的区别**
- Scallop (SIGCOMM 2025)：未实现加密与认证，仅讨论可行方向；本 idea 给出完整协议、威胁模型与线速实现。
- SFrame (IETF RFC 9605) 与 MLS (RFC 9420)：定义媒体帧端到端加密与群组密钥，未考虑 SFU 在硬件中改写头部的认证问题。
- 软件 SFU（如 Zoom 的 E2EE 方案）：在服务器 CPU 上处理加密媒体转发，扩展性受限于 CPU。

**🧪 验证方案**
- 测试床：Tofino2 + 商用服务器，Chrome / WebRTC 客户端（使用 Insertable Streams 实现端到端层）；会议规模 2–500 人、多码率 simulcast / SVC。
- 指标：每台交换机支持的会议 / 参与者数、媒体端到端时延、MAC 计算引入的流水线资源（stage、哈希单元）、密钥轮换时延、成员变动时的中断时长。
- 安全评估：Tamarin 形式化证明；注入攻击（头部篡改、重放、伪造发送者）检测率。
- 对比：Scallop 无安全版本、软件 SFU（mediasoup / Janus）+ SRTP、软件 SFU + SFrame。

🔑 `video conferencing` `SFU` `end-to-end encryption` `programmable switches` `MLS` `SipHash`

[🔝 top](#top)

---

## 💡 Idea 16.9 — *SLO-Guaranteed Hotspot-Aware Placement: Chance-Constrained Scheduling with ToR Utilization Quantile Forecasts*

| | |
|:--|:--|
| 🎯 **源论文** | **Preventing Network Bottlenecks: Accelerating Datacenter Services with Hotspot-Aware Placement for Compute and Storage** · Hamid Hajabdolali Bazzaz et al. (Google) · 📄 NSDI 2025 · [USENIX](https://www.usenix.org/conference/nsdi25/presentation/bazzaz) |
| 📌 **线索来源** | Future Directions §"Our current placement strategy, which is hotspot-aware but best-effort, cannot guarantee performance under every network and workload condition. To ensure consistent performance, we must define SLOs and implement mechanisms to guarantee them." |
| 📮 **投稿建议** | 📡 **Networking** · SIGCOMM / NSDI ＋ 🖥️ Systems · OSDI |
| ⭐ Novelty | ★★★☆☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
这篇 Google 论文发现，即使磁盘或计算密集的操作，在 ToR 热点下尾延迟也会翻倍；只需给现有计算 / 存储调度器加上简单的热点感知（避开高利用 ToR），就能消除大部分热点。但策略是尽力而为的，作者明确指出无法在所有网络与负载条件下提供保证，需要定义 SLO 并实现保证机制，同时指出 ML 工作负载需要新的网络容错策略。空隙在于：经典带宽保证（Oktopus、Silo）要求租户声明带宽需求并做硬预留，在大规模共享集群中利用率代价太高；而热点感知放置只看当前利用率，不评估未来风险。关键 insight：ToR 利用率具有强日周期与可预测性，可以对每个 ToR 的未来利用率做分位数预测，把放置变成机会约束问题——"任务落在 ToR r 上时，在其生命周期内 r 利用率超过阈值的概率 ≤ δ"，并用应用侧的"利用率→尾延迟"敏感度曲线把网络约束翻译成 SLO。

**💡 一句话 Idea**
用 ToR 利用率的分位数预测和应用的"利用率→尾延迟"敏感度曲线，把热点感知放置升级为机会约束调度：每次放置都保证在任务生命周期内 SLO 违约概率 ≤ δ，并在预测风险上升时触发迁移或限流。

**🛠️ 可能的解决方法**
1. **预测器**：对每个 ToR 上行 / 下行利用率做多步分位数预测（周期分解 + 梯度提升或 TFT），输出 P90 / P99 曲线；新任务的流量增量由同类任务历史画像估计。
2. **敏感度曲线**：对每类服务离线拟合 tail_latency = f(ToR 利用率)（论文已观测到存储操作在高利用率下延迟翻倍），SLO 阈值反推为利用率上限 u*。
3. **机会约束放置**：放置目标为最小化碎片化与资源成本，约束为 Pr[u_r(t) + Δ_task > u*] ≤ δ, ∀t∈生命周期；用分位数预测把概率约束转成确定性约束，嵌入现有调度器的打分函数，复杂度与原调度器同级。
4. **反应式补救**：预测风险越界时，按代价排序选择任务迁移、副本读重定向或 QoS 降级；对 ML 训练作业，把"单点慢节点"风险作为额外约束（避免把同一作业的关键 rank 放在高风险 ToR）。
5. **成本控制**：仅需 ToR 计数器与应用延迟日志，不需要交换机改动。

**🧭 与最接近工作的区别**
- 源论文 (NSDI 2025)：尽力而为的热点感知放置，无 SLO 保证。
- Oktopus (Ballani et al., SIGCOMM 2011) / Silo (Jang et al., SIGCOMM 2015)：基于租户声明的带宽 / 时延硬保证与预留；本 idea 无需声明，用预测做概率保证，以换取更高利用率。
- Firmament (Gog et al., OSDI 2016)：基于最小费用流的网络感知调度，追求放置延迟与质量，不提供概率 SLO。

**🧪 验证方案**
- 数据：公开集群轨迹（Google Borg 2019、Alibaba cluster trace）驱动的放置模拟器 + ns-3 叶脊网络中的存储 RPC 流量；小规模真实集群（32–64 节点）验证。
- 指标：SLO 违约率、P99 / P99.9 尾延迟、ToR 热点频率、集群利用率与碎片化、迁移次数。
- 对比：无网络感知调度、源论文的热点感知放置、带宽预留（Oktopus 风格）。
- 关键假设检验：δ 从 1% 扫到 10% 时违约率与利用率的权衡曲线；预测器误差对保证的影响（用真值利用率作 oracle 上界）。

🔑 `workload placement` `network hotspots` `SLO` `chance-constrained scheduling` `tail latency` `datacenter`

[🔝 top](#top)

---

## 💡 Idea 16.10 — *Partitioned Cooperative UWB Localization: Subgraph Leaders, Rigid Alignment and Uncertainty-Driven Ranging Schedules for Mobile Infrastructure-Free Networks*

| | |
|:--|:--|
| 🎯 **源论文** | **Large Network UWB Localization: Algorithms and Implementation** · Nakul Garg et al. (UMD) · 📄 NSDI 2025 · [USENIX](https://www.usenix.org/conference/nsdi25/presentation/garg) |
| 📌 **线索来源** | Discussion §"An extension of the proposed system with a semi-distributed approach can further improve its worst-case latency and robustness." + §"This distributed architecture can offer better handling of high mobility scenarios subjected to future research." |
| 📮 **投稿建议** | 📡 **Networking** · SIGCOMM / NSDI ＋ 🧪 ML · MLSys / NeurIPS |
| ⭐ Novelty | ★★★☆☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
Locate3D 在无基础设施的 UWB 网络中联合使用测距与到达角（AoA），通过边选择算法减少所需测距，使大规模网络的定位时延降低 75% 而不损失精度。但系统是集中式的：所有测量汇总后统一求解，最坏时延随网络规模增长，单点故障影响全网；作者提出半分布式架构（子图 leader 并行计算再聚合）并把高移动性留作未来工作。这在急救、仓储等目标场景中是关键障碍：UWB 测距占用信道时间，节点越多，每轮测距周期越长，而高速移动的节点需要更高刷新率。关键 insight：定位误差的结构是局部的——移动节点只影响其邻域子图；如果把网络划分为有重叠的子图，各子图独立解算后只需通过共享节点做刚体对齐，并把有限的测距时隙按各边对位置不确定度（Fisher 信息）的边际贡献分配给最需要的边，就能同时降低时延和提升移动场景下的精度。

**💡 一句话 Idea**
把 UWB 网络划分为重叠子图，由 leader 并行求解局部 3D 位姿并通过共享节点做刚体对齐，同时以位置后验不确定度的边际下降为准则调度每轮测距时隙，使移动场景下的刷新率与精度随网络规模平稳扩展。

**🛠️ 可能的解决方法**
1. **划分**：用基于测距图的谱聚类划分为重叠子图（每个子图 20–40 节点，重叠 ≥ 4 个非共面节点以保证 3D 刚体对齐可解），leader 选择取度中心性最高且电量充足的节点；拓扑变化时增量调整。
2. **局部求解与对齐**：子图内沿用 Locate3D 的测距 + AoA 联合优化；子图间用共享节点做加权 Procrustes 对齐，再做一次全局稀疏位姿图优化（只含少量子图间约束），保证全局一致。
3. **不确定度驱动的测距调度**：每轮可用测距时隙有限，对每条候选边计算其对相关节点位置协方差的 Fisher 信息增益，结合节点速度估计（移动节点协方差随时间膨胀），用贪心子模选择分配时隙；可学习的部分仅为运动模型（如 IMU 融合的速度先验）。
4. **容错**：leader 失效时由子图内次高分节点接管；子图间对齐对离群测距使用鲁棒核（Huber）。
5. **工程可行性**：基于 Qorvo DW3000 系列 UWB 模块（支持 PDoA 测角）与嵌入式主机实现，城市尺度用仿真。

**🧭 与最接近工作的区别**
- Locate3D (NSDI 2025)：集中式求解，半分布式与高移动性列为未来工作。
- SPAWN (Wymeersch et al., Proc. IEEE 2009)：分布式合作定位的消息传递框架，多为 2D 测距、未考虑测距时隙调度与 AoA。
- MDS-MAP(P) (Shang & Ruml, INFOCOM 2004)：局部子图 MDS 再拼接，静态网络、无移动性与不确定度驱动调度。

**🧪 验证方案**
- 测试床：多层建筑中 30–60 个 UWB 节点（部分由人员 / 机器人携带移动），动作捕捉或全站仪提供真值；仿真扩展到 1k–10k 节点的城市场景。
- 指标：3D 位置误差 P50 / P90、朝向误差、每轮更新时延、刷新率、信道占用、leader 失效后的恢复时间。
- 对比：Locate3D 集中式、仅测距的分布式基线、随机 / 轮询测距调度。
- 消融：去掉重叠对齐（独立子图）/ 去掉不确定度调度 / 不同子图大小与移动速度（0–3 m/s）。

🔑 `UWB` `cooperative localization` `distributed estimation` `mobility` `ranging scheduling` `wireless sensing`

[🔝 top](#top)
