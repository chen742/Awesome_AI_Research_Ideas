<a id="top"></a>
# 🖥️ Computer Systems & ML Systems

> 从 OSDI / FAST 的获奖论文与正式论文（以欧美团队为主）中提炼的系统方向 idea，覆盖 LLM 推理与训练系统、文件系统与存储、BFT 与分布式容错、形式化验证、内存分层与操作系统、内核调试、资源分配与调度、隐私与安全分析、数据平面 ML，目标投稿 OSDI / SOSP（备选 EuroSys / ATC / FAST）。
> 符号说明：🎯 源论文 · 📌 线索来源 · 📮 投稿建议 · ⭐ Novelty · 🚀 Impact · 🧗 Difficulty · 🧪 验证方案 · 🔑 关键词 · 📄 会议正式论文

[⬅️ 返回主页](../README.md)

---

## 💡 Idea 15.1 — *SpecFS-Crash: Generating Crash-Consistent Kernel File Systems from Persistence-Ordered Specifications with Push-Button Verification*

| | |
|:--|:--|
| 🎯 **源论文** | **Sharpen the Spec, Cut the Code: A Case for Generative File System with SYSSPEC** · Qingyuan Liu et al. (SJTU) · 🏆 FAST 2026 Best Paper · [arXiv:2512.13047](https://arxiv.org/abs/2512.13047) |
| 📌 **线索来源** | 6.6 Limitations and Discussion §"Consequently, it does not operate in kernel mode and lacks a storage stack, such as direct disk access, nor does it consider crash consistency." + §"a greater potential of SpecFS lies in the fact that each module is equipped with a ready specification." |
| 📮 **投稿建议** | 🖥️ **Systems** · OSDI / SOSP / FAST ＋ 🧪 ML · MLSys / NeurIPS |
| ⭐ Novelty | ★★★★★ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
SysSpec 把文件系统开发从"写代码"转为"写规约"：每个模块配有功能、模块化与并发规约，由 LLM 生成并演化 SpecFS，再经 SpecValidator 测试与审查。论文坦承 SpecFS 只是 FUSE 原型，没有块设备栈，也**完全没考虑崩溃一致性**；同时指出"每个模块自带规约"天然适合接入 push-button 验证。这正是生成式文件系统落地的核心难点：崩溃一致性 bug 源于**持久化顺序**，而顺序约束在自然语言规约中最易丢失、LLM 最易写错、测试也难以覆盖。SquirrelFS 用 Rust typestate 静态检查顺序但需手写，PoWER 能证明崩溃一致性但证明负担重。关键 insight：把持久化顺序作为规约的**第四个维度**显式写出，就能从中**自动编译出 typestate 骨架和 PoWER 风格的证明义务**；LLM 只填写函数体，顺序正确性交给编译器与验证器保证。

**💡 一句话 Idea**
在 SysSpec 规约中加入持久化顺序维度，从中自动生成 Rust typestate 骨架与 Verus 证明义务，让 LLM 只生成"填空式"实现，从而得到一个运行在内核、带块设备栈、崩溃一致性可机器检查的生成式文件系统。

**🛠️ 可能的解决方法**
1. **规约扩展**：为每个模块增加 `persist-order` 段，用小型 DSL 描述"更新 → flush/fence → 可见"的偏序（如 inode 分配 ≺ 目录项链接 ≺ 父目录 mtime），以及崩溃后的恢复语义（原子 / 前缀一致）。规约编译器把它转成（a）Rust typestate 类型（借鉴 SquirrelFS 的 synchronous soft updates），（b）Verus 中的崩溃不变式与 PoWER 风格的写权限（permission）谓词。
2. **生成—验证闭环**：LLM 在固定的 typestate 签名内生成函数体；`rustc` 类型检查失败或 Verus 证明失败时，把最小反例（违反的偏序边、未满足的不变式）回传给 LLM 修复，最多迭代 k 轮。证明不通过的模块退回 CrashMonkey / Chipmunk 式崩溃状态枚举做测试兜底，并在报告中标出"已证明 / 仅测试"两类模块。
3. **增量演化**：遵循论文自己提出的路线，从 Ext2 子集起步，以 DAG 形式的特性补丁逐步加入 extent、日志、延迟分配；每个补丁只需修改受影响模块的规约，证明按模块增量重跑，从而度量"演化成本"。
4. **内核落地**：生成代码通过 Rust-for-Linux 绑定接入 VFS，下层用 bio 直接访问 NVMe；PM 版本复用 SquirrelFS 的 PM 原语，用来与其做同介质对比。
5. **成本控制**：只对元数据路径做证明，数据路径用 checksum + 测试覆盖；LLM 调用按模块缓存，规约不变的模块不重新生成。

**🧭 与最接近工作的区别**
- SysSpec / SpecFS（FAST 2026）：用户态，无崩溃一致性；本 idea 把持久化顺序纳入规约，并由此自动派生证明义务。
- SquirrelFS（OSDI 2024）与 CapybaraKV / PoWER（OSDI 2025）：typestate 与证明都由人手写；本 idea 从规约自动生成证明骨架，并用 LLM 填充实现。
- Yggdrasil（OSDI 2016）：push-button 验证文件系统，但实现须手写在受限风格内；本 idea 的实现由 LLM 从规约生成，并支持增量演化。

**🧪 验证方案**
- 正确性：xfstests 通用用例通过率；CrashMonkey / Chipmunk 的崩溃状态枚举中发现的 bug 数，与 SpecFS-FUSE 及无顺序规约的 LLM 生成版本对比；统计已证明模块所占比例。
- 性能：Filebench（varmail / fileserver / webserver）、fio、RocksDB db_bench、LevelDB on NVMe 与 PM；基线为 ext4（data=ordered）、ext2、SquirrelFS、NOVA；指标为吞吐、p99 延迟、fsync 延迟。
- 演化成本：为 5–8 个真实 ext4 特性（extent、inline data、延迟分配、日志校验和等）分别统计规约修改行数、LLM 迭代轮数与证明时间，并与对应 Linux 补丁的代码行数对比。
- 消融：去掉 persist-order 规约、去掉证明反馈（只做测试）、更换生成模型，分别观察崩溃 bug 数的变化。

🔑 `generative file system` `crash consistency` `typestate` `push-button verification` `LLM code generation` `specification`

[🔝 top](#top)

---

## 💡 Idea 15.2 — *Handicapped Races: Topology-Aware, Byzantine-Robust Adaptation of Protocol-Rigged Racing for Heterogeneous BFT Deployments*

| | |
|:--|:--|
| 🎯 **源论文** | **Ambulance: Saving BFT through Racing** · Neil Giridharan et al. (UC Berkeley) · 🏆 OSDI 2026 Best Paper · [arXiv:2606.25099](https://arxiv.org/abs/2606.25099) |
| 📌 **线索来源** | Appendix C Additional Technical Discussion §"In some deployments, such as LAN environments, this advantage may be insufficient because communication delays between replicas are extremely small. As a result, a non-slow leader may be mistakenly classified as slow, causing replicas to trigger recovery more often than necessary." |
| 📮 **投稿建议** | 🖥️ **Systems** · OSDI / SOSP ＋ 📡 Networking · NSDI |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
Ambulance 用 protocol-rigged race 取代超时：leader 两个消息延迟即可提交，其他副本需要三个，副本之间比的是协议步数而不是时钟；leader 输掉比赛就进入随机选 lane 的恢复路径，因此正常情况下与 PBFT 一样快，遇到慢 leader 时又能像异步协议一样快速恢复。附录承认，固定一个消息延迟的领先量在 LAN 中太小，正常 leader 也会被误判为慢；motorization 后 leader 更晚凑齐 coverage，同样会被误判。作者的补救是**静态配置** dummy phase。真实部署（跨地域、副本异构）中，leader 应得的领先量取决于它到法定人数的延迟分布并随时间漂移，而且**不能由副本自报**：Byzantine 副本谎报延迟，就能让 leader 永远赢（掩护慢 leader）或永远输（引发恢复风暴）。关键 insight：每轮比赛结果本身就是带签名的观测样本，对其做 Byzantine 鲁棒统计，即可在不引入时钟假设的前提下自适应调整 dummy phase 数。

**💡 一句话 Idea**
把 Ambulance 的 leader 领先量从静态常数变成按 (leader, 拓扑) 自适应的"让步数"，依据是带法定人数签名的比赛结果统计与可证明 Byzantine 鲁棒的延迟估计，在 LAN、WAN 与异构部署中同时压低误判恢复率和慢 leader 检测延迟。

**🛠️ 可能的解决方法**
1. **可审计的比赛记录**：每个 slot 结束后，把"谁赢、各 lane 进入 race cutoff 时已完成的阶段数"附进下一个提案的证书；只统计有 2f+1 签名支持的观测，Byzantine 副本无法单方面伪造结果。
2. **鲁棒估计**：对每个候选 leader 维护最近 W 个 slot 的"领先余量"（leader 提交时，最快非 leader lane 落后的阶段数）。用 f 截尾中位数估计其分布，取下分位数 q 作为目标余量；dummy phase 数取 k = max(0, ⌈目标余量 − 实测余量⌉)。只允许 k 在每个 epoch 改变 ±1，防止被操纵后剧烈振荡。
3. **安全性与活性论证**：dummy phase 只推迟非 leader 进入比赛的时机，不改变证书规则，因此安全性沿用原证明。活性方面需证明：即使 f 个 Byzantine 副本合谋操纵统计，k 也有上界 k_max；超过 k_max 的慢 leader 仍能在 O(k_max) 个消息延迟内被检测到。
4. **拓扑感知 leader 轮换**：把余量估计反馈给 leader 选择，优先轮换到余量大的副本（类似 AWARE 的权重与 leader 位置优化），但保留随机性，以维持论文要求的不可预测性。
5. **工程实现**：在 Ambulance 开源实现上改动，dummy phase 与 non-equivocation 证书生成复用同一条消息，保持"等待期间仍在做有用的协议工作"这一性质。

**🧭 与最接近工作的区别**
- Ambulance（OSDI 2026）：领先量固定为 1 个消息延迟加静态 dummy phase；本 idea 让它按 leader 与拓扑自适应，并给出抗 Byzantine 操纵的界。
- AWARE（Berger et al., 2020）：基于延迟测量调整 BFT 投票权重与 leader 位置，但仍依赖超时检测慢 leader，延迟测量也可被自报污染；本 idea 只用带签名的比赛结果做统计。
- BFTBrain（NSDI 2025）：用强化学习在多个 BFT 协议之间切换；本 idea 在单一协议内调整连续参数，并带形式化活性界。

**🧪 验证方案**
- 部署：(a) 单数据中心 LAN（n=4/16/64）；(b) 5 地域 WAN（AWS us-east / eu-west / ap-southeast 等）；(c) 混合部署（部分副本 CPU 受限、一个副本带周期性网络抖动）。
- 指标：正常情况下的吞吐与 p50/p99 提交延迟；误判恢复率（非慢 leader 触发恢复的比例）；慢 leader（注入 50–500 ms 延迟、渐进变慢、间歇卡顿）下的检测延迟与延迟膨胀。
- 对抗实验：f 个 Byzantine 副本分别尝试"压低余量引发恢复风暴"与"抬高余量掩护慢 leader"，测量 k 的偏移与吞吐损失，验证理论上界。
- 基线：Ambulance（k=0 / 1 / 2 静态）、HotStuff-2 / Jolteon 类超时协议（多组超时设置）、带 hedging 的协议，以及 Autobahn。

🔑 `BFT` `state machine replication` `slowdown detection` `adaptive protocols` `Byzantine-robust statistics` `geo-replication`

[🔝 top](#top)

---

## 💡 Idea 15.3 — *Certificate Provenance: Automating Inductive Invariants for Byzantine Fault-Tolerant Protocols via Honest-Witness Quorum Reasoning*

| | |
|:--|:--|
| 🎯 **源论文** | **Basilisk: Using Provenance Invariants to Automate Proofs of Undecidable Protocols** · Tony Nuda Zhang et al. (UMich) · 🏆 OSDI 2025 Best Paper · [USENIX](https://www.usenix.org/conference/osdi25/presentation/zhang-tony) ＋ **Inductive Invariants That Spark Joy: Using Invariant Taxonomies to Streamline Distributed Protocol Proofs** · Tony Nuda Zhang et al. (UMich) · 📄 OSDI 2024 · [USENIX](https://www.usenix.org/conference/osdi24/presentation/zhang-nuda) |
| 📌 **线索来源** | Basilisk Limitations §"In particular, it cannot derive relationships between variables when their relationships are only implicitly established across multiple steps." + Kondo Limitations §"Moreover, Kondo is not applicable in a Byzantine fault model, as it is not safe to relate a message to the state of a Byzantine-faulty sender or receiver." |
| 📮 **投稿建议** | 🖥️ **Systems** · OSDI / SOSP ＋ 🔐 Security · USENIX Security |
| ⭐ Novelty | ★★★★★ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
Kondo 提出不变式分类法：大量 Regular Invariant 只是把"网络中的消息"与"发送者 / 接收者的本地状态"联系起来，可以机械生成。Basilisk 在此基础上用 Provenance Invariant 与 atomic sharding 把这部分全自动化，在不可判定逻辑下证明了多个崩溃容错协议，获得 OSDI 2025 最佳论文。两篇论文各自承认一个短板：Kondo 不适用于 Byzantine 模型，因为不能把消息与拜占庭发送者的状态挂钩；Basilisk 推不出跨多步隐式建立的变量关系。而这恰恰是工业界最需要证明的协议类别——PBFT、HotStuff、Tendermint 以及新一代 racing / DAG 协议——它们目前的证明几乎全靠手写。关键 insight：BFT 协议的正确性论证从来不依赖"某个发送者的状态"，而依赖**法定人数交集**：任何 2f+1 签名的证书中至少有 f+1 个诚实签名者，这些诚实副本的历史里**确实**执行过投票步骤。这是一种"证书级的 provenance"，可以像 Basilisk 一样自动生成，只需把来源从单个发送者换成"诚实见证者集合"，再加上单调的 ghost 历史变量，把跨步关系显式化。

**💡 一句话 Idea**
把 provenance invariant 从"消息 → 发送者状态"推广到"法定人数证书 → 诚实见证者集合的单调历史"，并自动引入 ghost 历史变量来捕获跨多步的隐式关系，使 PBFT / HotStuff 类协议的归纳不变式在不可判定逻辑下也能大部分自动推出。

**🛠️ 可能的解决方法**
1. **模型**：在 Basilisk 的 Dafny 框架中加入 Byzantine 主机，其转移关系为"可以发送任何不伪造签名的消息"。诚实主机照常建模，签名用不可伪造的抽象谓词表示。
2. **Honest-Witness Provenance**：对每类证书 QC（k 个签名），自动生成不变式 ∀QC ∈ Network. ∃H ⊆ signers(QC). |H| ≥ k − f ∧ H ⊆ Honest ∧ ∀h ∈ H. VoteStep(h, QC.payload) ∈ history(h)。再由 quorum-intersection 引理（两个 2f+1 集合至少交于 f+1 个、其中至少 1 个诚实）自动派生 Kondo 式的 Regular Invariant。
3. **Ghost 历史化**：针对 Basilisk 的局限，静态分析找出"被某步清空或重置"的变量（论文中 `events` 与 `currentYear` 的例子），自动插入单调的 ghost 日志 `hist: seq<(step, snapshot)>`，把"events 中的元素都属于当前年份"改写成对 ghost 日志的单步可验证关系，再交给 atomic sharding 处理。
4. **证明搜索**：生成的候选不变式先用有界模型检查（TLC / Apalache 的小实例）过滤反例，再送 Dafny 做归纳性检查；对失败的子句只请求开发者补写 Protocol Invariant，并记录人工行数。

**🧭 与最接近工作的区别**
- Basilisk（OSDI 2025）与 Kondo（OSDI 2024）：仅限崩溃容错，且无法处理跨多步的隐式关系；本 idea 两者都覆盖。
- Berkovits et al.（CAV 2019）：把阈值类拜占庭协议分解到可判定逻辑后在 Ivy 中验证，需要手工抽象与分解；本 idea 保持不可判定逻辑，自动生成证书级不变式。
- DuoAI（OSDI 2022）/ IC3PO（2021）：基于枚举或 IC3 推断不变式，适用于可判定片段的崩溃容错协议，并非为 Byzantine 量词交替设计。

**🧪 验证方案**
- 协议集：Basilisk 原有的 CFT 基准（回归测试）＋ PBFT（normal case + view change）、HotStuff / HotStuff-2、Tendermint、Byzantine reliable broadcast（Bracha）、一个带随机 lane 选举的 racing 协议简化模型。
- 指标：自动生成的不变式子句占比、需要人工补写的 Protocol Invariant 行数（对比文献中已有手写证明的行数）、Dafny 验证时间、证明搜索总时间。
- 关键假设检验：(a) 仅加入 Honest-Witness Provenance 时可自动化的比例；(b) 再加 ghost 历史化后的提升；(c) 注入错误（把法定人数改成 f+1、删去 view-change 证书检查），检验工具能否给出反例而不是"证明通过"。
- 基线：手写证明（IronFleet 风格）、Kondo 工作流在 Byzantine 协议上的人工改写成本、Ivy 分解方法。

🔑 `formal verification` `inductive invariants` `Byzantine fault tolerance` `provenance` `quorum certificates` `Dafny`

[🔝 top](#top)

---

## 💡 Idea 15.4 — *BubbleSpec: Turning Wafer-Scale Pipeline Bubbles into Speculative Tokens for Single-Request LLM Decoding*

| | |
|:--|:--|
| 🎯 **源论文** | **WaferLLM: Large Language Model Inference at Wafer Scale** · Congjie He et al. (Edinburgh) · 📄 OSDI 2025 · [arXiv:2502.04563](https://arxiv.org/abs/2502.04563) |
| 📌 **线索来源** | 8 Implementation Detail and Future Direction §"The performance of WaferLLM is currently constrained by execution bubbles caused by the need for pipeline parallelism." + §"LLM decoding demands a near 1:1 memory-to-compute ratio." |
| 📮 **投稿建议** | 🖥️ **Systems** · OSDI / SOSP ＋ 🧪 ML · MLSys / NeurIPS |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★★★ |

**🔍 深入分析**
WaferLLM 提出 PLMR 设备模型，设计了 MeshGEMM / MeshGEMV 与移位式 KV cache 管理，在 Cerebras WSE-2 上的解码速度比 GPU 集群快几个数量级。但单核内存只有几十 KB，模型放不进一个张量并行组，只能把晶圆切成多个流水段；单请求解码时同一时刻只有一个段在工作，利用率约为 1/S。作者给出的出路是等硬件把单核内存再扩大 5–6 倍。软件上常用的填气泡办法（增大 batch、micro-batch 交错）在晶圆上并不适用：KV cache 同样占用片上 SRAM，batch 一大就违反 M 约束，而晶圆芯片的卖点本来就是**单请求极低延迟**。关键 insight：解码气泡是"有算力、缺依赖"的空闲，而推测解码恰好能制造不依赖上一 token 的工作。让第 s 段在空闲时处理推测位置 t+s 的 token（草稿由晶圆角落的小模型提供），S 段流水线就变成了推测式流水线；验证失败时的 KV 回滚，正好可以由移位式 KV 管理低成本完成。

**💡 一句话 Idea**
在晶圆上划出一小块区域运行草稿模型，让各流水段在气泡期并行处理不同推测位置的 token，并用支持回滚的移位式 KV 管理丢弃错误分支，在不增加片上内存的前提下把单请求解码的流水线利用率从约 1/S 提高到接近接受长度 / S。

**🛠️ 可能的解决方法**
1. **空间布局**：按 PLMR 约束为草稿模型（如 EAGLE 式单层草稿头或 0.5B 级小模型）分配一个靠近第 1 段的矩形核区，草稿 logits 经 NoC 短路径送入第 1 段，满足 L 与 R 约束；目标模型各段布局沿用 WaferLLM。
2. **推测式流水调度**：第 s 段在步 τ 处理位置 t+s 的候选 token；每个位置可以是 top-k 树分支，分支数由该段剩余 SRAM 决定，满足 M 约束。最后一段输出验证结果后，向前广播"接受长度 a"，各段丢弃位置 > t+a 的工作并从新前沿继续。
3. **KV 回滚**：扩展 shift-based KV 管理，为每个推测位置维护一个"暂存列"，接受后整体移位合并、拒绝时只需把指针复位，避免 GPU 上常见的 KV 拷贝；分析回滚开销与 NoC 跳数的关系。
4. **成本模型与自适应**：建立期望吞吐 E[tokens/step] = f(接受率 α, 段数 S, 树宽 w) 的解析模型，根据在线估计的 α 动态选择 w 和推测深度；α 过低时自动退回 WaferLLM 原始调度。
5. **可行性**：先在 Cerebras SDK 的模拟器和 PLMR 参数化模拟器上验证，再上 WSE-2/3 实机；草稿模型训练沿用 EAGLE / Medusa 的公开流程。

**🧭 与最接近工作的区别**
- WaferLLM（OSDI 2025）：单请求解码时流水气泡未被利用；本 idea 用推测工作填充气泡。
- PipeInfer（SC 2024）：在多节点 CPU / GPU 流水线上做异步推测，假设节点间带宽充足、内存不紧；本 idea 面向 SRAM 受限的 2D mesh，联合设计推测宽度、KV 回滚与 NoC 布局。
- SpecInfer（ASPLOS 2024）、EAGLE / Medusa（ICML 2024）：在 GPU 上做树形推测验证；本 idea 关注的是推测工作在空间上的放置与流水线利用率，而不是草稿质量本身。

**🧪 验证方案**
- 硬件与模型：Cerebras WSE-2 / WSE-3；LLaMA-3-8B、Qwen2.5-14B 等 WaferLLM 已支持的稠密模型；对照 A100 / H100 × 8 上的 vLLM 与 SGLang（开启 EAGLE-2 推测）。
- 指标：单请求 TPOT、每 token 能耗、流水段利用率、平均接受长度；负载取 MT-Bench、HumanEval、GSM8K 以及长输出推理链（体现 test-time scaling 场景）。
- 关键假设检验：(a) 段数 S 与加速比的关系，验证解析模型；(b) 接受率很低（如随机任务）时不劣于 WaferLLM；(c) KV 回滚开销占比 < 5%。
- 消融：去掉树分支（w=1）、草稿放在晶圆远端、关闭自适应深度。

🔑 `wafer-scale computing` `LLM inference` `speculative decoding` `pipeline bubbles` `on-chip memory` `mesh NoC`

[🔝 top](#top)

---

## 💡 Idea 15.5 — *Preempt to Be Fair: Bounded-Unfairness LLM Serving across Disaggregated and Replicated Engines with Cost-Charged Virtual Token Counters*

| | |
|:--|:--|
| 🎯 **源论文** | **Fairness in Serving Large Language Models** · Ying Sheng et al. (UC Berkeley & Stanford) · 📄 OSDI 2024 · [arXiv:2401.00588](https://arxiv.org/abs/2401.00588) |
| 📌 **线索来源** | C.3 Future Work §"Having a preemption mechanism could be a good solution to address the problem of underestimating and tightening the bound." + §"Integrating VTC in a distributed LLM serving system is an interesting direction for future work." |
| 📮 **投稿建议** | 🖥️ **Systems** · OSDI / SOSP ＋ 🧪 ML · MLSys / NeurIPS |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
VTC 把公平排队搬到 LLM 服务中：按客户端累计的加权输入 / 输出 token 数（虚拟计数器）优先服务计数最小者，并证明不公平度上界 U = 2·max(w_p·L_input, w_q·M)，其中 M 为 KV cache 容量。附录承认这个界源于不可抢占：长请求一旦进入 batch 就会占满内存直到结束；作者设想用抢占收紧界，并把多副本部署留作未来工作。两年来服务形态已经变化：prefill / decode 解耦成为主流，前缀缓存让请求对副本有了亲和性，抢占也有了真实代价（KV 换出或重算）。因此公平不再是单一资源上的 token 计数，而是**跨 prefill 池、decode 池与 KV 内存的多资源公平**。关键 insight：把抢占代价**记到触发抢占的一方**的计数器上，就能同时得到与 M 无关的公平界和抢占频率上界，避免为公平而反复抢占、导致吞吐崩溃。

**💡 一句话 Idea**
设计一种按阈值触发、代价记账的抢占式 VTC：在 prefill / decode 解耦且多副本的部署中，以 DRF 式主导资源计数衡量服务量，并证明不公平度上界与 KV 容量 M 无关、抢占开销有界。

**🛠️ 可能的解决方法**
1. **多资源计数器**：每个客户端维护向量 c = (prefill FLOPs, decode token-steps, KV 字节·秒)，以各资源池容量归一化后取主导份额（DRF 思想）作为调度键；prefill 池与 decode 池各自调度，但共享同一组计数器。
2. **代价记账的抢占**：当 max_i c_i − min_j c_j > Δ（j 为有积压的客户端）时，抢占计数最高的客户端在 decode 池中的请求，抢占代价（KV 换出到 CPU 的字节数 / PCIe 带宽，或重算 FLOPs）计入触发方 j 的计数器。证明不公平度 ≤ Δ + O(w·单步 token)，抢占次数 ≤ 总服务量 / (Δ − 代价)。
3. **分布式分发器**：中心分发器持有全局计数器，副本周期性上报增量；在前缀亲和与公平之间用"公平赤字预算"折中——只要客户端赤字小于 δ，就允许按前缀命中路由到偏好副本，否则强制路由到负载最低的副本。证明全局不公平度 ≤ Δ + δ + 上报延迟 × 峰值速率。
4. **工程实现**：基于 SGLang / vLLM 的 PD 解耦模式（如 Mooncake 风格 KV 传输）实现，抢占使用分层 KV 换出（GPU → CPU → SSD）。

**🧭 与最接近工作的区别**
- VTC（OSDI 2024）：单引擎、不可抢占，界依赖 M；本 idea 引入代价记账的抢占，并推广到多副本与 PD 解耦部署。
- Locality-aware fair scheduling（DLPM，Cao et al., 2025）：在多副本中兼顾前缀局部性与公平，但不涉及 PD 解耦的多资源计数与抢占代价；本 idea 给出这两方面的联合界。
- DistServe（OSDI 2024）：优化 goodput / SLO，没有客户端间的公平目标。

**🧪 验证方案**
- 负载：LMSYS-Chat-1M、ShareGPT、BurstGPT 真实到达过程；构造"长文档客户端 vs 短对话客户端""突发型客户端"三类混合；模型为 Llama-3.1-8B / 70B，部署在 8–32 张 H100 上（2P2D、4P4D 及 4 个副本）。
- 指标：积压客户端之间的最大服务差（随时间变化）、Jain 公平指数、总吞吐（tokens/s）、各客户端的 p99 TTFT / TPOT、抢占次数与抢占开销占比。
- 基线：FCFS、按 RPM 限流、VTC、VTC + 长度预测、DLPM、PD 解耦下的 FCFS。
- 关键假设检验：(a) 实测不公平度不随 M 增大而增大；(b) 代价记账能防止"抢占风暴"——去掉记账后，吞吐在高负载下明显下降；(c) 赤字预算 δ 在前缀命中率与公平度之间形成平滑权衡曲线。

🔑 `LLM serving` `fair scheduling` `preemption` `prefill-decode disaggregation` `dominant resource fairness` `KV cache`

[🔝 top](#top)

---

## 💡 Idea 15.6 — *Invariants Below Python: Compiler-IR-Level Invariant Inference for Silent Errors in Compiled and Fused LLM Training*

| | |
|:--|:--|
| 🎯 **源论文** | **Training with Confidence: Catching Silent Errors in Deep Learning Training with Automated Proactive Checks** · Yuxuan Jiang et al. (UMich) · 📄 OSDI 2025 · [arXiv:2506.14813](https://arxiv.org/abs/2506.14813) |
| 📌 **线索来源** | 6 Limitations §"First, its instrumentation interferes with JIT compilation tools like torch.compile , preventing the analysis of optimized code paths." + §"Finally, representing tensors in hash form prevents fine-grained numerical analysis, limiting its applicability to detecting instabilities caused by inappropriate hyperparameters." |
| 📮 **投稿建议** | 🖥️ **Systems** · OSDI / SOSP ＋ 🧪 ML · MLSys / NeurIPS |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
TrainCheck 从正常的训练运行中自动推断"训练不变式"（例如各 DP rank 的参数在 step 之后保持一致、optimizer.step 之前必须 zero_grad），并在新的训练运行中主动检查，复现的 20 个真实静默错误中大部分能被及早发现。但它在 Python API 层插桩：torch.compile 一开，被融合的路径就看不到；FlashAttention、TransformerEngine 等 C++ / Triton 内核的逻辑也看不到；张量又只以哈希表示，无法做数值层面的检查。这几项局限恰好覆盖了当今大模型训练的主路径——生产训练几乎都在编译图与融合内核上运行，而 FP8 缩放因子错误、注意力 mask 错位、融合内核在特定形状下的错误结果，正是最典型的静默错误。关键 insight：编译器 IR（FX graph、Inductor IR、Triton IR）是插桩的天然位置，KPerfIR 已经证明在编译器 pass 中插入探针是可行的、开销可控。如果把探针输出从"哈希"换成**低成本数值草图**（范数、最值、NaN / Inf 计数、分位数），就能在编译后的代码上推断并检查**数值关系型不变式**，同时保留 TrainCheck 的跨 rank 一致性检查能力。

**💡 一句话 Idea**
把训练不变式的推断与检查下沉为 TorchInductor / Triton 的编译 pass，用数值草图代替张量哈希，在 torch.compile 与融合内核路径上发现结构型和数值型静默错误，开销控制在 5% 以内。

**🛠️ 可能的解决方法**
1. **IR 插桩**：在 FX graph 降级到 Inductor 之前注册自定义 pass，为每个节点（包括被融合节点的逻辑边界）插入草图探针；对 Triton 内核，在 epilogue 中加入块内归约，写出 (‖x‖₂, max|x|, nan_cnt, 抽样分位数)。探针按采样周期激活，未激活时只多一个分支。
2. **不变式模板扩展**：在 TrainCheck 的关系模板之外，加入数值模板，例如：缩放一致性（FP8 amax 与 scale 的关系，scale·max|x| ≤ dtype_max）、融合等价性（融合内核与参考实现的输出草图在容差内一致，抽样执行参考实现做差分）、单调性 / 有界性（grad norm 比值、LayerNorm 输出方差在 [a,b] 内）、跨 rank 一致性（DP 副本草图相等，TP 分片草图之和等于全量）。
3. **推断**：从 2–3 个已知健康的小规模运行（不同 seed、不同并行配置）中收集草图，用 Daikon 式候选生成加统计置信区间筛选，只保留在所有健康运行中都成立、且对注入扰动敏感的不变式。
4. **跨 rank 低成本检查**：草图只有几十字节，搭载在已有的 all-reduce 上做异步聚合，不新增同步点。
5. **开销控制**：按层与步数分级采样；在内核内做归约，避免额外的 HBM 往返。

**🧭 与最接近工作的区别**
- TrainCheck（OSDI 2025）：只在 Python API 层插桩且使用哈希；本 idea 在编译 IR 与内核层插桩，并支持数值不变式。
- KPerfIR（OSDI 2025）：在 Triton 编译器中插入性能探针；本 idea 复用这种思路做正确性检查与不变式推断，而不是性能剖析。
- 损失尖峰 / grad-norm 监控与 Meta 的静默数据损坏检测（Dixit et al., 2022）：前者只是事后信号，后者针对硬件故障；本 idea 面向软件栈与配置引起的静默错误，并能把问题定位到具体算子。

**🧪 验证方案**
- 错误集：TrainCheck 的 20 个错误（检验回归）＋ 从 PyTorch、Megatron-LM、DeepSpeed、TransformerEngine、FlashAttention 的 issue 中新收集 15–25 个"只在编译 / 融合路径出现"的静默错误，在相应版本上复现。
- 训练配置：Llama-3-8B / Qwen2.5-7B 在 8–64 张 H100 上训练，组合 FSDP / TP / PP、BF16 / FP8、torch.compile 开与关。
- 指标：检出率、检出所需迭代数、定位精度（是否定位到出错算子）、在 N 次健康运行上的误报率、吞吐开销（MFU 下降百分比）。
- 基线：TrainCheck（关闭 compile 后运行）、损失 / grad-norm 阈值告警、PyTorch anomaly mode、NaN 检测钩子。
- 消融：只用结构不变式 / 只用数值不变式；草图维度；采样周期。

🔑 `silent errors` `training reliability` `invariant inference` `torch.compile` `compiler instrumentation` `numerical checks`

[🔝 top](#top)

---

## 💡 Idea 15.7 — *Beyond Separability: Coupled-Constraint Decomposition for Hyperscale Resource Allocation with Quota-Aware Proximal ADMM*

| | |
|:--|:--|
| 🎯 **源论文** | **Decouple and Decompose: Scaling Resource Allocation with DeDe** · Zhiying Xu et al. (Harvard) · 📄 OSDI 2025 · [arXiv:2412.11447](https://arxiv.org/abs/2412.11447) |
| 📌 **线索来源** | 4.2 Limitations §"For example, this occurs when the jobs submitted by each user are collectively limited by a user-specific GPU hour quota." + §"However, this aggregation reduces the granularity of parallelism, from the job level to the user level." |
| 📮 **投稿建议** | 🖥️ **Systems** · OSDI / SOSP ＋ 📡 Networking · NSDI |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
DeDe 发现多数真实资源分配问题是可分的：目标是各资源 / 各需求效用之和，约束只涉及单个资源或单个需求，于是用 ADMM 交替求解大量独立子问题，比商用求解器快一到两个数量级。论文坦承两类结构会让它退化：一是**跨资源、跨需求的耦合约束**（如用户级 GPU 小时配额，只能把同一用户的作业聚合，并行粒度从作业级退到用户级）；二是**交互型目标**（独占与共享 GPU 时吞吐不同）。生产中这两类结构越来越多：团队配额、电力上限、故障域分散、WAN 路径共享链路容量。关键 insight：耦合约束数通常远小于变量数（用户数 ≪ 作业数），可以为每条耦合约束引入**份额变量**，拆成"每个作业持有一份配额份额"与"份额之和 ≤ 配额"的 sharing 问题，并行度仍保持在作业级。由于三块 ADMM 的直接推广可能发散，需要采用有收敛保证的 proximal Jacobian 变体。

**💡 一句话 Idea**
为 DeDe 增加第三类变量块——耦合约束的份额变量，用带近端项的 Jacobian ADMM 在保持作业级并行的同时处理用户配额、电力上限、路径链路等耦合约束，并对交互型目标做逐次凸近似，给出可证明收敛的分配器。

**🛠️ 可能的解决方法**
1. **重构**：对耦合约束 Σ_{j∈U} a_j·x_j ≤ Q_U，引入份额 s_j，改写为 a_j·x_j ≤ s_j（并入需求子问题，可分）与 Σ_j s_j ≤ Q_U（每个用户一个低维投影问题，O(|U| log |U|) 闭式求解）。资源块、需求块、份额块三块交替更新。
2. **收敛保证**：采用 proximal Jacobian ADMM，各块加上近端项 τ‖x − x^k‖²；在凸情形下按已有理论选取 τ 以保证收敛，并实现自适应罚参数（残差平衡）。
3. **交互型目标**：把"独占 vs 共享"的吞吐差异建模为双线性项，每轮外层迭代在当前解处线性化，内层仍是 DeDe 可分形式（凸凹过程 / 逐次凸近似），并给出单调下降性质。
4. **整数性**：子问题内做随机化舍入，加上一轮只针对违反约束的资源 / 用户的局部修复，修复本身也按用户并行。
5. **系统实现**：在 DeDe 的 Python 包上扩展建模 API（`couple(sum over group ≤ Q)`），子问题用 Ray 分发；热启动沿用上一调度周期的对偶变量。

**🧭 与最接近工作的区别**
- DeDe（OSDI 2025）：遇到耦合约束只能按用户聚合，牺牲并行度；本 idea 保持作业级并行，并有收敛性保证。
- POP（SOSP 2021）：把问题随机划分成子问题各自求解，耦合约束需要按比例切分，可能无解或质量下降；本 idea 通过份额变量动态再分配配额。
- Rebalancer（OSDI 2024）与 NCFlow（NSDI 2021）：前者用局部搜索换可扩展性，后者针对 WAN TE 做特定分解；本 idea 是面向耦合约束的通用分解方法。

**🧪 验证方案**
- 问题集：(a) 带用户 / 团队配额的 GPU 集群调度（Gavel 策略，Philly 与 Alibaba PAI 公开 trace，扩展到 10⁵ 作业 × 10⁴ GPU）；(b) 带机架电力上限的服务放置；(c) 路径级 WAN 流量工程（Topology Zoo 中的大拓扑，加入链路共享约束）。
- 指标：求解时间、最优性差距（相对 Gurobi，或给定时间上限内的 Gurobi 最佳解）、约束违反量、可扩展性曲线（CPU 核数 1–256）。
- 基线：Gurobi、DeDe（用户级聚合）、POP、贪心启发式；TE 场景另加 NCFlow 与 Teal。
- 关键假设检验：耦合约束数 / 变量数比值从 10⁻⁴ 到 10⁻¹ 变化时的加速比；三块 ADMM 不加近端项时出现发散或振荡的实例数。

🔑 `resource allocation` `ADMM` `decomposition` `coupled constraints` `cluster scheduling` `traffic engineering`

[🔝 top](#top)

---

## 💡 Idea 15.8 — *Know When to Stop Migrating: Sampled Cross-Tier Miss-Ratio Curves for Migration Admission Control in CXL Memory Tiering*

| | |
|:--|:--|
| 🎯 **源论文** | **Nomad: Non-Exclusive Memory Tiering via Transactional Page Migration** · Lingfeng Xiang et al. (UT Arlington) · 📄 OSDI 2024 · [arXiv:2401.13154](https://arxiv.org/abs/2401.13154) |
| 📌 **线索来源** | 5 Discussions and Future Work §"However, estimating the working set size to resume page migration becomes challenging, as the working set now spans multiple tiers. It requires global memory tracking, which could be prohibitively expensive, to identify the hot data set that can potentially be migrated to the fast tier." |
| 📮 **投稿建议** | 🖥️ **Systems** · OSDI / SOSP ＋ 🗄️ DB · VLDB |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
Nomad 用事务式页迁移与页影子把迁移移出关键路径，在内存压力下比 TPP 快最多 6 倍。但它的评估揭示了一个更根本的事实：当工作集超过快层容量时，最优策略是**完全停止迁移**，直接从初始位置访问。检测抖动（升降级次数相当）很容易，难的是判断**何时恢复迁移**：这需要知道跨两层的工作集大小，而全局追踪的代价高得难以接受。现有分层系统各取一端：TPP 与 Nomad 基于缺页（反映新近性、开销在关键路径上），Memtis 基于 PEBS 采样（反映频率、对负载变化反应慢）。它们都在回答"哪些页热"，没有回答"把快层装满能带来多少收益"。关键 insight：存储缓存领域早已用空间采样（SHARDS）以常数内存在线构造**缺失率曲线（MRC）**；把快层视为跨层工作集的一个缓存，用约 0.1% 的页做空间哈希采样、追踪其重用距离，就能低成本得到"快层容量 → 命中率"曲线，从而对每次迁移做收益 / 成本的准入判断。

**💡 一句话 Idea**
用基于空间哈希采样的跨层重用距离追踪，在线构造快层 MRC，并据此对页迁移做准入控制：预计边际命中收益低于迁移成本时自动停止迁移，工作集回落时自动恢复，从而把 Nomad 的"优雅降级"推进到接近"不迁移"与"理想迁移"两者中较优的那一个。

**🛠️ 可能的解决方法**
1. **采样追踪**：对页帧号做哈希，保留 hash(pfn) mod P < T 的页（采样率 R = T/P）。对这些页，快层侧用 accessed-bit 周期扫描，慢层侧用 PEBS / IBS 采样，合并为统一的访问流；按 SHARDS 的方法计算重用距离并按 1/R 缩放，得到 MRC。
2. **迁移准入**：对候选升级页 p，估计收益 = ΔHitRate(C) × 访问率 × (t_slow − t_fast)，成本 = 拷贝开销 + TLB shootdown + 被挤出页的预期回迁成本；只有收益 > 成本时才升级。当 MRC 在快层容量 C 处已经平坦（工作集远大于 C）时进入"冻结"状态，MRC 的拐点回到 C 以内时解冻，并加入滞回避免振荡。
3. **与 Nomad 机制叠加**：准入控制只决定"是否迁移、迁移哪些"，执行仍使用事务式迁移与页影子；影子页的命中也作为 MRC 的输入。
4. **开销控制**：采样率 0.1%–1%，追踪结构限定为固定大小的哈希表；MRC 每 100 ms 增量更新；所有计算放在 kthread 中，不进入缺页路径。

**🧭 与最接近工作的区别**
- Nomad（OSDI 2024）与 TPP（ASPLOS 2023）：只判断页的冷热，不估计跨层工作集，内存压力下只能被动降级；本 idea 显式估计 MRC 并据此做准入。
- Memtis（SOSP 2023）：基于 PEBS 的频率直方图动态设定热度阈值，但不建模"快层容量—收益"关系，也不会主动停止迁移。
- Colloid（SOSP 2024）：通过平衡各层访问延迟来决定放置，关注带宽与排队延迟；本 idea 关注容量不足时迁移本身的净收益，二者可以组合。
- SHARDS（FAST 2015）：用于存储缓存的 MRC 采样；本 idea 首次将其用于双层内存，并联合使用缺页与硬件采样两种信号。

**🧪 验证方案**
- 平台：Intel Sapphire Rapids 搭配 CXL Type-3 内存扩展卡（或用远端 NUMA 节点模拟 CXL 延迟），Linux 6.x 内核。
- 负载：GAPBS（PageRank、BFS）、XSBench、Redis / Memcached + YCSB（Zipf 0.9–1.2）、Silo TPC-C、Liblinear；并构造"工作集周期性越过快层容量"的相变负载。
- 指标：吞吐、p99 延迟、迁移次数与迁移带宽、MRC 估计误差（与全量追踪对比）、追踪 CPU 开销。
- 基线：不迁移、TPP、Memtis、Nomad、Colloid，以及最优静态放置（oracle）。
- 关键假设检验：工作集 < 快层容量、≈ 快层容量、> 快层容量三种区间下，本方法都不劣于各区间内的最佳基线；相变后恢复迁移所需的时间。

🔑 `tiered memory` `CXL` `page migration` `miss-ratio curve` `working set estimation` `Linux kernel`

[🔝 top](#top)

---

## 💡 Idea 15.9 — *Lock-Order Kernel Replay: Parallel Kernel Record-Replay via Synchronization Logging and KCSAN-Guided Race Capture*

| | |
|:--|:--|
| 🎯 **源论文** | **KRR: Efficient and Scalable Kernel Record Replay** · Tianren Zhang et al. (SmartX) · 📄 OSDI 2025 · [USENIX](https://www.usenix.org/conference/osdi25/presentation/zhang-tianren) |
| 📌 **线索来源** | Discussion §"A promising direction is to integrate techniques from chunk-based serialization algorithms, such as Samsara’s algorithm [54, 60]. Adopting such an approach in KRR could enable true parallel kernel execution and potentially broaden the class of bugs that KRR can reproduce." |
| 📮 **投稿建议** | 🖥️ **Systems** · OSDI / SOSP ＋ 🔐 Security · USENIX Security |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
KRR 把录制边界从整个虚拟机缩小到客户机内核，在 kernel-bypass 负载上接近原生性能；但为了保证确定性，它把内核执行串行化，超过 8 个 vCPU 后扩展性明显下降，并发 bug（数据竞争、竞争导致的 UAF）也因此难以复现，而这恰恰是最难诊断、syzbot 上数量最多的一类内核 bug。作者建议借鉴 Samsara 的基于 chunk 的串行化，但 chunk 方法依赖硬件虚拟化特性追踪内存访问，在多核上的冲突检测与回滚开销都不小。关键 insight：内核不是任意的多线程程序，它有高度结构化的同步纪律（spinlock、mutex、RCU、原子操作、seqlock），而且社区已经用 KCSAN 与 `data_race()` / `READ_ONCE` 标注了大部分有意的竞争访问。因此可以采用"记录同步顺序 + 只记录竞争读的值"的方式（RecPlay / Kendo 一类思想在内核中的实现）：对遵守锁纪律的代码，并行重放是确定的；对标注过的竞争访问，记录读到的值；剩余未标注的竞争，则在重放发散时局部退回 chunk 串行化。

**💡 一句话 Idea**
在 KRR 的客户机内录制器中，按锁对象记录获取顺序，用值日志记录 KCSAN / 标注的竞争读，并且只在检测到重放发散的代码区域退回 chunk 串行化，从而实现内核的真正并行录制与重放，并能复现并发 bug。

**🛠️ 可能的解决方法**
1. **同步顺序日志**：在 spinlock / mutex / rwsem / seqlock 的获取路径与原子 RMW 上插桩（复用 lockdep 钩子与 instrumented atomics），为每个同步对象记录 (vCPU, 序号) 序列；RCU 记录 grace period 边界及 `rcu_dereference` 读到的指针值。
2. **竞争值日志**：编译期复用 KCSAN 的插桩点（关闭 watchpoint 检测，只保留钩子），对 `READ_ONCE` / `data_race()` 及 KCSAN 报告过的位置记录读值；用基于页的布隆过滤器跳过只读热点，控制日志体积。
3. **发散检测与局部回退**：重放时对每个 vCPU 定期比较寄存器与关键状态的哈希；一旦发散，标记对应函数，在后续录制中对其进入 chunk 串行模式（Samsara 式）。形成"自学习"白名单，使串行化只覆盖少数未标注的竞争区域。
4. **设备与 DMA**：沿用 KRR 的 hypervisor 侧设备录制；直通设备的支持另行处理，不在本工作范围内。
5. **工程实现**：基于 KRR 开源实现与 KVM；以 Linux 6.x 为客户机，配置为 KCSAN 插桩但关闭报告。

**🧭 与最接近工作的区别**
- KRR（OSDI 2025）：内核执行被串行化，扩展到约 8 vCPU；本 idea 使内核真正并行执行，目标扩展到 32–64 vCPU，并能复现并发 bug。
- Samsara（Ren et al., 2016）：基于硬件虚拟化的整机 chunk 串行化，不利用内核的同步语义；本 idea 只在发散区域使用 chunk。
- Kendo（ASPLOS 2009）/ RecPlay（1999）：面向用户态、要求无数据竞争的程序；本 idea 借助 KCSAN 的标注体系处理内核中有意存在的竞争。

**🧪 验证方案**
- bug 复现：从 syzbot 选取 30–50 个已修复的并发 bug（数据竞争、竞争导致的 UAF / 死锁），在原始触发程序下录制，统计重放复现率与首次复现所需的录制次数；对比 KRR 串行模式（因执行被串行化，许多交错无法出现）。
- 性能：RocksDB db_bench、Nginx + wrk、Redis、内核编译、PostgreSQL pgbench，vCPU 数取 4 / 8 / 16 / 32 / 64；指标为录制开销（相对原生的吞吐比）、日志速率（MB/s）、重放速度。
- 基线：KRR、整机 RR（QEMU record / replay）、rr（只覆盖用户态，用于对照）。
- 消融：只记录锁顺序（无竞争值日志）时的发散率；关闭局部回退；不同的布隆过滤器大小。

🔑 `record and replay` `kernel debugging` `concurrency bugs` `KCSAN` `deterministic replay` `virtualization`

[🔝 top](#top)

---

## 💡 Idea 15.10 — *Beyond the Process Boundary: Resource-Aliasing Dependence Graphs for Privacy Policies Spanning Files, Databases, and Services*

| | |
|:--|:--|
| 🎯 **源论文** | **Paralegal: Practical Static Analysis for Privacy Bugs** · Justus Adam et al. (Brown) · 📄 OSDI 2025 · [USENIX](https://www.usenix.org/conference/osdi25/presentation/adam) |
| 📌 **线索来源** | Limitations §"Paralegal may omit true dependencies induced by effects on external systems like a file system, OS, or database." + §"But Paralegal does not understand that f2 = File::open("foo.txt") is effectively an alias on f, and that f2.read() should depend on f.write(bytes)." |
| 📮 **投稿建议** | 🖥️ **Systems** · OSDI / SOSP ＋ 🔐 Security · USENIX Security |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
Paralegal 让隐私工程师用基于标记的 DSL 写策略（如"用户数据必须流向删除函数"），开发者在代码中打标记，再从 Rust 程序抽取程序依赖图（PDG）检查，几十秒即可完成，适合放进 CI。论文坦承：经由文件系统、操作系统或数据库产生的依赖会被遗漏，例如写入 `foo.txt` 后再次打开读取，二者之间的依赖它看不到。这对隐私策略后果严重：真实 Web 后端的删除、保留期、目的限制策略几乎都要经过数据库表、缓存键、对象存储路径或下游 HTTP 服务；"写进 A 表、却只从 B 表删除"这类违规，恰恰发生在进程之外。关键 insight：外部资源的身份在代码中通常由**可静态近似的标识符**决定（路径字符串、ORM 实体与表名、缓存键模板、路由 URL）。把它们抽象为资源位置，就能在 PDG 中加入"写 ℓ → 读 ℓ′（可能别名）"的边，把跨进程的数据流纳入同一张图。

**💡 一句话 Idea**
为 Paralegal 的 PDG 加入外部资源位置抽象：用字符串前缀与模板抽象域近似文件路径、SQL 表列、缓存键与 HTTP 路由，并以 ORM 模式和查询解析为依据，补上"写 → 读""写 → 删除"之间的跨资源依赖边；再按策略极性选择可能别名或必然别名，分别控制漏报与误报。

**🛠️ 可能的解决方法**
1. **资源位置抽象**：为 std::fs、tokio::fs、Diesel / SeaORM / sqlx、redis-rs、reqwest 等常用 crate 编写资源模型（摘要）：每个 API 映射到 (资源类型, 标识符表达式, 读 / 写 / 删除)。标识符用字符串模板抽象域表示，例如 `format!("users/{}/avatar", id)` 对应 `users/*/avatar`。
2. **SQL 解析**：sqlx 的字面 SQL 与 ORM 生成的查询解析到（表, 列, 谓词形状）；删除策略额外检查谓词覆盖性，例如 `DELETE ... WHERE user_id = ?` 是否覆盖所有以 user_id 为键写入的行。
3. **按策略极性选择别名语义**：针对论文指出的不对称性，"禁止流向"类策略使用可能别名（宁可误报），"必须流向 / 必须删除"类策略使用必然别名（宁可漏报），并在报告中标注每条依据所用的语义。
4. **动态补全**：在应用测试套件运行时用 eBPF 追踪 openat / sendto 及数据库协议报文，记录实际出现的资源标识符；如果静态模型没有覆盖这些标识符，就提示补充摘要，不让未建模的资源悄悄漏过检查。
5. **开发者负担**：资源模型按 crate 编写、跨项目复用；应用层只需在 schema 上标记个人数据列。

**🧭 与最接近工作的区别**
- Paralegal（OSDI 2025）：PDG 止于进程边界；本 idea 通过资源位置抽象把文件、数据库、缓存与服务纳入同一张依赖图。
- Sesame（SOSP 2024）：用策略容器在运行时强制执行隐私策略，需要改造应用代码；本 idea 是不改代码的静态检查，可在 CI 中运行。
- FlowDroid（PLDI 2014）：Android 污点分析，用源 / 汇模型而不是外部资源别名，不支持"必须删除"这类活性型策略。

**🧪 验证方案**
- 应用：Paralegal 的 8 个案例应用（包括 HyperSwitch，约 198k LOC）＋ 5–8 个新的开源 Rust Web 后端（如 Lemmy、Plume、Atuin server 等使用 Diesel / sqlx 的项目）。
- 策略：数据删除、保留期、凭据隔离、目的限制，每个应用 2–4 条。
- 指标：真实 bug 数（向上游报告并统计确认数）、误报率（人工核验）、在人为注入的跨资源违规上的漏报率、分析时间（是否仍能用于 CI）、每个应用新增的标记与资源模型行数。
- 对比：原版 Paralegal、只用可能别名 / 只用必然别名的变体、CodeQL 数据流查询（同一组策略手写）。

🔑 `privacy compliance` `static analysis` `program dependence graph` `Rust` `data deletion` `resource aliasing`

[🔝 top](#top)

---

## 💡 Idea 15.11 — *Oblivious Collectives: Differentially Private Traffic Shaping for Routing-Leakage-Free Mixture-of-Experts Training and Inference*

| | |
|:--|:--|
| 🎯 **源论文** | **Weave: Efficient and Expressive Oblivious Analytics at Scale** · Mahdi Soleimani et al. (Yale) · 📄 OSDI 2025 · [USENIX](https://www.usenix.org/conference/osdi25/presentation/soleimani) |
| 📌 **线索来源** | Discussion and Future Work §"Other analytics frameworks, such as distributed ML training or deep learning, employ different communication patterns, especially in collective operations such as broadcast, all-reduce, gather, all-gather, etc. These communications also suffer from similar access pattern leakages [66,67] and can benefit from noise-injection-based obliviousness for efficiency and privacy." |
| 📮 **投稿建议** | 🖥️ **Systems** · OSDI / SOSP ＋ 🔐 Security · USENIX Security |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
Weave 在可信执行环境中运行 MapReduce 分析，用"随机洗牌 + 注入噪声记录"取代排序网络，把隐藏访问模式的开销降到常数级，比此前最好的方法快 4–10 倍；作者明确指出分布式训练与推理的集合通信也存在访问模式泄露。这一空隙如今尤为紧迫：H100 机密计算模式能加密通信内容，却**隐藏不了通信量**。all-reduce 的数据量与输入无关，不受影响；但 MoE all-to-all 发给每个专家的 token 数直接取决于输入内容，DLRM 稀疏嵌入交换和变长 gather 同样如此。观察链路流量的云服务商可以据此推断输入的主题或语言。完全不经意的做法是把每个专家填充到容量上限，代价相当于放弃 MoE 的稀疏收益。关键 insight：沿用 Weave 的思路，不追求完全不经意，而是把路由直方图当作要保护的统计量，按差分隐私校准每个目的地的虚拟 token 数，用可调的少量填充换取形式化的泄露上界。

**💡 一句话 Idea**
在机密计算 GPU 集群中，对 MoE all-to-all 及其他依赖数据的集合通信，按 (ε,δ)-差分隐私向每个目的地注入可校准数量的虚拟 token，使链路观测者无法从路由直方图区分相邻输入；同时与专家容量和负载均衡联合优化，把填充开销降到全量填充的一小部分。

**🛠️ 可能的解决方法**
1. **威胁模型**：GPU 运行在 CC 模式（显存与链路内容加密、完整性受保护），攻击者为能观测 NVLink / InfiniBand 上流量大小与时序的诚实但好奇的云服务商或同网租户；保护对象是每个 micro-batch 中各 (源 rank, 目的专家) 的 token 计数向量 h。
2. **机制**：发送量 h̃ = h + max(0, ⌈Lap(Δ/ε)⌉ + b)，其中 b 为偏置，保证以 1−δ 的概率非负且只需截断很少。虚拟 token 在接收端由加密标志位识别并丢弃，不参与专家计算（只占带宽，可选择是否占用算力）。按 micro-batch 组合，使用 Rényi DP 累计整个推理会话或训练 epoch 的预算。
3. **与容量联合优化**：路由器本身有 capacity factor，噪声可以"借用"本来就会被丢弃或填充的容量槽位；把专家放置与噪声分布联合求解，使每条链路的最大期望流量最小。
4. **其他集合通信**：变长 gather / all-gather 按长度分桶并注入噪声；DLRM 的嵌入 all-to-all 对 ID 频次直方图使用同样的机制。
5. **工程实现**：在 DeepEP / NCCL all-to-all 外包一层，噪声采样与标志位在 GPU 内生成；支持 Megatron-LM MoE 训练与 SGLang / vLLM 的专家并行推理。

**🧭 与最接近工作的区别**
- Weave（OSDI 2025）：只覆盖 MapReduce 的 shuffle 与 CPU 可信执行环境；本 idea 面向 GPU 集合通信，以 MoE 路由直方图为保护对象。
- Opaque（NSDI 2017）与 Snoopy（SOSP 2021）：依赖排序网络或完全不经意的存储，开销为对数级或需全量填充；本 idea 采用差分隐私式的部分填充。
- 差分不经意算法（Chan et al., SODA 2019）：提供理论框架，本 idea 将其落地到真实的 GPU 通信栈，并与专家容量机制联合设计。

**🧪 验证方案**
- 负载：Mixtral-8x7B、DeepSeek-MoE-16B、Qwen1.5-MoE-A2.7B 的推理（ShareGPT、多语言混合请求）与训练（16–64 张 H100，EP=8/16）；DLRM 在 Criteo 1TB 上训练。
- 开销指标：推理吞吐与 TPOT、训练 step 时间、额外链路字节数；对照无保护、全量填充到容量、Weave 风格的整批洗牌移植版本。
- 泄露指标：训练攻击分类器，根据观测到的 all-to-all 字节直方图预测请求的语言、主题或是否属于某一敏感类别；报告不同 ε 下的攻击 AUC，并与理论上界对照。
- 消融：是否借用容量槽位、是否与专家放置联合优化、不同的 RDP 预算分配策略。

🔑 `oblivious computation` `access pattern leakage` `confidential computing` `mixture of experts` `differential privacy` `collective communication`

[🔝 top](#top)

---

## 💡 Idea 15.12 — *Rollback-Ready In-Network Learning: Poisoning-Resilient Online Updates with Provenance-Tracked Model Versions for Data-Plane ML*

| | |
|:--|:--|
| 🎯 **源论文** | **Caravan: Practical Online Learning of In-Network ML Models with Labeling Agents** · Qizheng Zhang et al. (Stanford) · 📄 OSDI 2024 · [USENIX](https://www.usenix.org/conference/osdi24/presentation/zhang-qizheng) |
| 📌 **线索来源** | Limitations & Future Work §"If online data (such as network traffic) is being used to retrain and update models, bad actors can poison training data by intentionally feeding bad traffic in the network. Future research may detect and protect against these attacks and restore models to a clean state." |
| 📮 **投稿建议** | 🖥️ **Systems** · OSDI / SOSP ＋ 📡 Networking · NSDI |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
Caravan 让交换机或 SmartNIC 上的 ML 模型（入侵检测、流量分类等）能在线更新：标注代理为随机采样的流量自动打标签，系统监控精度下降并触发重训。论文点明了这一闭环的根本风险：训练数据来自网络本身，攻击者只需**发送流量**就能毒化数据平面模型；检测攻击并恢复到干净状态被列为未来工作。被毒化的 IDS 会直接放行攻击流量。现有投毒防御（RONI、鲁棒训练）假设离线训练、数据可反复审查，而在线网络数据按窗口滚动、只出现一次。关键 insight：Caravan 本来就按时间窗口切分数据并产生模型版本。只要为每个版本记录**训练数据来源**（源前缀、窗口、标注置信度），检测到异常时就能精确回滚到最后的干净版本并排除可疑窗口重训；再配合按来源配额采样，即可从源头限制单个攻击者的影响份额。

**💡 一句话 Idea**
为在线网络 ML 构建带数据来源记录的模型版本 DAG：用按来源前缀配额的采样限制单个攻击者的影响份额，用版本间行为漂移与影响度估计检测投毒，检测到后在数据平面原子回滚到干净版本，并排除可疑数据重训。

**🛠️ 可能的解决方法**
1. **威胁模型**：攻击者控制一部分源地址（可伪造少量前缀），能注入任意流量，但无法攻破控制平面与标注代理；目标包括让特定攻击流量被判为良性（后门 / 定向投毒）或整体降低精度。
2. **来源受限采样**：替代 Caravan 的随机采样，对 /24 前缀（或 AS）做分层蓄水池采样，每个来源在每个窗口内的样本份额不超过 q；理论上单个攻击者对梯度的影响 ≤ q·L（L 为单样本梯度界），借此把投毒影响转化为可计算的上界。
3. **版本 DAG 与检测**：每个模型版本 v 记录 (父版本, 训练窗口, 各来源样本摘要)。新版本上线前在固定的金丝雀集（历史已确认样本与合成攻击模板）上做差分测试，并用近似影响函数（如 TracIn 式梯度相似度）找出对金丝雀预测变化贡献最大的来源。
4. **回滚与重训**：数据平面使用双缓冲表（Tofino 的表项版本位或 SmartNIC 的双模型槽），通过一次寄存器翻转原子切换；控制平面回滚到最后一个干净祖先版本，剔除被标记的来源后重放后续窗口进行重训。
5. **成本控制**：样本摘要只存特征哈希与标签，按窗口滚动删除；影响度只针对金丝雀出现异常的版本计算。

**🧭 与最接近工作的区别**
- Caravan（OSDI 2024）：采用随机采样，没有投毒检测与回滚；本 idea 加入来源受限采样、版本来源记录与原子回滚。
- RONI（Nelson et al., 2008）：逐样本测试其对模型性能的负面影响，适合离线小规模场景；本 idea 按来源 × 时间窗口聚合，满足线速流量与在线更新的要求。
- Kitsune（NDSS 2018）：在线无监督 IDS，本身容易被逐步毒化；本 idea 是与具体模型无关的防护层，也可以套在 Kitsune 一类模型之上。

**🧪 验证方案**
- 数据与平台：CIC-IDS2017 / 2018、UNSW-NB15，以及 CAIDA 背景流量混合回放；模型部署在 Tofino（或 bmv2 + Taurus 风格的 SmartNIC 仿真）上，沿用 Caravan 的任务与标注代理。
- 攻击：(a) 标签翻转式投毒（构造能骗过标注代理的流量）；(b) 后门触发特征（特定包长或 TTL 模式）；(c) 慢速渐进投毒；攻击者控制的前缀比例为 0.1%–5%。
- 指标：攻击下的 F1 与攻击成功率、检测时延（窗口数）、回滚时延（数据平面切换耗时）、无攻击时的精度损失（来源配额的代价）、交换机资源占用（SRAM / stage）。
- 基线：Caravan 原版、Caravan + 截尾损失鲁棒训练、Caravan + RONI、固定离线模型（不更新）。

🔑 `in-network ML` `online learning` `data poisoning` `model rollback` `programmable switches` `provenance`

[🔝 top](#top)
