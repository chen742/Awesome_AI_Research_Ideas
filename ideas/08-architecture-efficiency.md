<a id="top"></a>
# ⚙️ Architecture, Efficiency & Scaling

> 从门控注意力、稀疏注意力、Transformer 表达力理论 等获奖论文中提炼的 idea。
> 符号说明：🎯 源论文 · 📌 线索来源 · ⭐ Novelty · 🚀 Impact · 🧗 Difficulty · 🧪 验证方案 · 🔑 关键词

[⬅️ 返回主页](../README.md)

---

## 💡 Idea 8.1 — *Gate-Guided KV Eviction: Using Attention Gates as a Free Importance Oracle for Long-Context Inference*

| | |
|:--|:--|
| 🎯 **源论文** | **Gated Attention for Large Language Models: Non-linearity, Sparsity, and Attention-Sink-Free** · Qiu et al. (Qwen) · 🏆 NeurIPS 2025 Best Paper · [arXiv:2505.06708](https://arxiv.org/abs/2505.06708) |
| 📌 **线索来源** | Discussion §"gates are sparse and query-dependent; attention sinks disappear" + Future Work §"interplay with KV-cache compression and sparse attention" |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★☆☆☆ |

**🔍 深入分析**
论文在 30 组变体、15B MoE 与 1.7B dense 模型上系统比较了门控位置，发现在 SDPA 输出后加一个**头级、query 依赖的 sigmoid 门**效果最好：引入非线性、使门输出稀疏、并**消除了 attention sink**（首 token 不再吸收大量注意力），同时显著改善长上下文外推与训练稳定性。Future Work 提到与 KV 压缩/稀疏注意力的结合，但未做。深入看：当前所有 KV 驱逐方法（H2O、SnapKV、PyramidKV 等）都用**累计注意力分数**作为"重要性"代理，而这个代理恰恰被 attention sink 污染（首 token 永远"重要"），而且注意力分数只衡量"被看了多少"，不衡量"看到的内容被用了多少"。门控注意力的门值 g_{h,t} 恰好是后者：它表示该头在该步的输出被**使用**的程度。一个被频繁看但门始终关闭的 KV 项，对输出没有贡献。更进一步，门消除 sink 之后，注意力分数本身也更可信。

**💡 一句话 Idea**
把门控注意力中的头级门值作为免费的"使用度"信号，与去 sink 后的注意力分数联合定义 KV 重要性，实现无需额外计算的 KV 驱逐与头级动态稀疏，在同等缓存预算下显著提升长上下文精度。

**🛠️ 可能的解决方法**
1. **重要性定义**：对 KV 项 j 在头 h 的重要性 s_{h,j} = Σ_t g_{h,t}·A_{h,t,j}（门加权的累计注意力），g 低的时间步不计入，避免"看了但没用"的高估；用指数衰减窗口做在线估计。
2. **头级预算分配**：门的平均激活率衡量一个头的整体活跃度，活跃度低的头分配更小的 KV 预算（甚至整头跳过计算——即推理期的头级动态稀疏），活跃头保留更多。
3. **门感知的驱逐策略**：在 prefill 结束与解码过程中按 s 驱逐，sink token 不再被特殊保留（因为已无 sink）；对比 H2O 的"sink + recent + heavy hitters"规则。
4. **零训练成本**：对已用门控注意力训练的模型（如 Qwen3-Next 系列）直接适用；对无门模型，可用少量数据微调加门后再用。

**🧪 验证方案**
- LongBench、RULER、Needle-in-a-Haystack、∞-Bench，缓存预算 10%–50%；
- 指标：精度—预算曲线、解码吞吐、头级稀疏带来的 FLOPs 节省；
- 对比：H2O、SnapKV、PyramidKV、Quest、DuoAttention。

🔑 `gated attention` `KV cache` `long context` `attention sink` `sparse attention` `inference efficiency`

[🔝 top](#top)

---

## 💡 Idea 8.2 — *Sparse Diffusion Attention: Natively Trainable Block-Sparse Attention for Bidirectional Diffusion Language Models*

| | |
|:--|:--|
| 🎯 **源论文** | **Native Sparse Attention: Hardware-Aligned and Natively Trainable Sparse Attention** · Yuan et al. (DeepSeek) · 🏆 ACL 2025 Best Paper · [arXiv:2502.11089](https://arxiv.org/abs/2502.11089) |
| 📌 **线索来源** | Limitation §"designed for causal autoregressive decoding; block selection relies on causal compressed keys" + dLLM 领域的共识痛点 §"bidirectional attention prevents KV caching; every denoising step recomputes full attention" |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
NSA 的贡献是把稀疏注意力做成**可从头训练、硬件对齐**的三分支结构（压缩 token、块选择、滑动窗口），在 27B 模型上以稀疏方式预训练并在长上下文下获得数倍加速且不掉点。它的设计完全是因果/自回归的：压缩键按时间顺序构造，块选择使用因果可见的压缩注意力分数。另一方面，扩散语言模型（LLaDA、Dream、以及 ICML 2026 最佳论文关注的 dLLM 系列）最大的实际瓶颈是：**双向注意力下没有 KV cache**，每个去噪步都对整段序列做全注意力，推理成本随步数线性放大；现有加速（dKV-Cache、Fast-dLLM 的近似缓存）都是"事后近似"，没有在训练时让模型适应稀疏结构。两者的交叉是空白：**为双向、迭代去噪的生成过程设计 natively trainable 的稀疏注意力**。关键差异在于 dLLM 的 query 可以看未来、而且序列内容随去噪步演化，块选择必须是双向且随步更新的。

**💡 一句话 Idea**
把 NSA 的"压缩—选择—局部"三分支改造为双向、去噪步感知的块稀疏注意力，并在扩散语言模型预训练中原生使用，使每个去噪步只对少量被选块与压缩块计算注意力，在保持质量的同时把 dLLM 推理成本降低数倍。

**🛠️ 可能的解决方法**
1. **双向压缩分支**：序列按固定块压缩（可学习的块内池化），不受因果约束，所有 query 可见全部压缩键；由于掩码 token 的嵌入在去噪早期大量重复，压缩分支天然廉价。
2. **去噪步感知的块选择**：用压缩分支的注意力分数选 top-k 块，但增加两个信号：(a) 块内"已解码比例"（已解码块携带信息更多），(b) 上一去噪步的选择结果作为先验（跨步平滑，避免抖动并允许复用上一步的块级 KV）。
3. **局部分支**：改为以 query 为中心的双向窗口。
4. **跨步缓存**：对连续两步中未被重新解码的块，其 K/V 可直接复用（已解码 token 的表示在相邻步几乎不变，这是 dKV-Cache 的经验观察），与块稀疏结合后每步只需重算被改动块与被选块。
5. **训练**：从头预训练 1B dLLM（LLaDA 配方）对比全注意力；三分支的可学习门按 NSA 方式初始化。

**🧪 验证方案**
- 语言建模困惑度、GSM8K/HumanEval/MMLU（dLLM 标准评测）、长上下文（RULER 改造为填空式）；
- 指标：每步 FLOPs、端到端延迟、与 Fast-dLLM/dKV-Cache 的叠加增益；
- 消融：步感知选择、跨步缓存、各分支贡献。

🔑 `diffusion LLM` `sparse attention` `block selection` `inference acceleration` `bidirectional attention`

[🔝 top](#top)

---

## 💡 Idea 8.3 — *From Succinct to Learnable: Closing the Expressivity–Learnability Gap with Algorithmic Pretraining Curricula*

| | |
|:--|:--|
| 🎯 **源论文** | **Transformers are Inherently Succinct** · Bergsträßer, Cotterell & Lin · 🏆 ICLR 2026 Outstanding Paper · [arXiv:2510.19315](https://arxiv.org/abs/2510.19315) |
| 📌 **线索来源** | Discussion §"succinctness is an expressivity statement; whether gradient descent finds these succinct solutions is open" + Future Work §"learnability of succinct constructions" |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★☆☆ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
论文从形式语言的角度给出了一个新视角：衡量 Transformer 的不应只是"能表示什么"，而是"**用多小的规模**表示"。结果表明 Transformer 能以比自动机/经典模型指数级更小的描述长度表示一大类语言（succinctness），这为"为何 Transformer 规模扩展如此有效"给出了理论解释。但作者谨慎地指出：succinct 的构造是存在性的，**梯度下降能否找到它们**完全是另一个问题——这也是整个表达力理论与实践之间长期的鸿沟。已有的经验证据（如 Transformer 难学奇偶性、计数、组合泛化）恰恰说明许多"可简洁表示"的函数并不"可学"。空隙：没有系统的方法把"可简洁表示但难学"的构造找出来，更没有人利用它们去设计预训练数据。而最近的实践表明，在预训练中混入少量算法/合成数据（代码、数学、合成推理）能不成比例地提升推理能力——这暗示"可学性缺口"是可以用数据填补的。

**💡 一句话 Idea**
系统地构造"存在简洁 Transformer 表示但标准训练学不到"的形式语言族，刻画可学性缺口的规律，并把这些语言作为算法化预训练课程注入，使模型学会它本可以简洁表示的算法原语，从而提升组合与长度泛化。

**🛠️ 可能的解决方法**
1. **缺口探测**：取论文中给出 succinct 构造的语言族（计数、嵌套、模运算、布尔组合等），对每个语言训练与构造同规模的 Transformer，测量 (a) 达到构造精度所需的样本/步数，(b) 长度泛化；定义可学性缺口 = 实际所需规模 / 简洁构造规模。
2. **机理分析**：对缺口大的语言，检查损失地形（是否存在简洁解但被更大的、非泛化的"查表解"吸引），用论文的构造作为参考解计算与训练解的参数距离/功能相似度。
3. **算法课程**：把缺口大但"可被课程引导"的语言（先短长度、带中间监督的变体）编成合成语料，以 1–5% 比例混入 LLM 预训练；用 scaffolded 格式（显式中间状态）降低学习难度，训练后期去掉 scaffold。
4. **验证迁移**：课程是否提升真实任务上的算法泛化（长算术、代码执行追踪、多步推理）。

**🧪 验证方案**
- 合成：各语言族的缺口表、长度泛化曲线；
- 真实：1B 模型 ± 课程，评测 GSM8K、CRUXEval、长度外推任务；
- 对比：随机合成数据、代码数据、无课程。

🔑 `expressivity` `learnability` `formal languages` `synthetic pretraining` `length generalization`

[🔝 top](#top)

---

## 💡 Idea 8.4 — *Function-Composition Probing: Measuring Control-Variable Structure in Real Long-Context Workloads to Decide Where Hybrids Need Attention*

| | |
|:--|:--|
| 🎯 **源论文** | **Expressivity-Efficiency Tradeoffs for Hybrid Sequence Models** · Cooper et al. · 🎤 ICML 2026 Oral · [arXiv:2603.08859](https://arxiv.org/abs/2603.08859) |
| 📌 **线索来源** | Conclusion §"Limitations include our focus on synthetic tasks and restricted Transformer attention mechanisms; extending the theory to broader attention patterns, external memory, identification of real function-composition datasets, and naturalistic long-context workloads is an important direction for future work." |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
论文把一大类长上下文任务形式化为"函数复合"F(u(x), v(x))：u 是需要从长序列里**内容寻址检索**的宽度为 m 的关键子序列，v 是依赖于远处位置的**控制变量**（R-局部敏感）。他们证明纯 SSM 的状态规模必须随 m 线性增长、纯滑窗 Transformer 的窗口总和必须 ≥ R，而小型混合模型能同时规避两者，并在 selective copying / associative recall 上验证了分离。Limitation 坦承：分析只覆盖合成任务和滑窗注意力，**现实数据里是否存在、以何种比例存在函数复合结构**完全未知。这正是当前混合模型设计（Jamba、Samba、Hymba、MiniMax-01 的 1:7 或 1:3 混合比例）的盲点——比例和放置位置都是靠网格搜索和困惑度得来的，没有任何可测量的任务结构量来指导。关键 insight：理论给出了两个可操作的量——m（关键上下文宽度）和 R（控制变量的敏感半径）——它们在真实数据上可以通过**反事实消融**来估计：遮蔽/置换某段上下文看预测是否改变，就能给每个样本标出 (m, R)。有了样本级的 (m, R) 分布，混合比例就从超参数变成了可以由数据推导的设计决策。

**💡 一句话 Idea**
构建一个自动化的"函数复合探针"，用反事实遮蔽在真实长上下文语料上估计每个样本的关键宽度 m 与控制敏感半径 R，用这一分布预测并验证混合模型应有的注意力层比例与放置深度，把混合架构设计从网格搜索变成可测量的结构匹配。

**🛠️ 可能的解决方法**
1. **探针定义**：对样本 x 的目标 token y，用一个强参考模型计算 (a) R̂ = 最小的后缀长度，使得仅保留最后 R̂ 个 token 时 log p(y) 的损失 < ε（控制变量半径）；(b) m̂ = 用贪心/二分搜索找到的、保留后仍能恢复 log p(y) 的最小非连续 token 集合大小（关键宽度）。用注意力/梯度归因做初筛以把搜索代价压到 O(log L) 次前向。
2. **语料画像**：在 RULER、LongBench、代码仓库、多文档 QA、法律/医学长文上统计 (m̂, R̂) 的联合分布；按论文定理，R̂ 大而 m̂ 小的样本是 SSM 友好、m̂ 大的样本需要注意力，两者都大的样本是"真正的函数复合"。
3. **架构预测**：以 (m̂, R̂) 分布为输入，推导所需注意力层的最小数目（按定理 3.7 的窗口和约束）与 SSM 状态维度（按定理 3.3 的 m log|V| 下界），生成候选混合配置；对比与困惑度网格搜索得到的最优配置是否一致。
4. **控制变量条件化检索层**：若真实数据中"先算 v 再检索 u"的模式普遍，设计一个显式两阶段层：SSM 分支输出的控制向量作为 query 的调制项进入稀疏注意力分支（query = W_q x ⊙ g(v)），复现论文构造的小型混合解。
5. **成本控制**：探针只在 ~50k 样本上离线运行一次；架构验证用 350M–1.3B 规模、同 FLOPs 的混合变体各训练 20B token。

**🧭 与最接近工作的区别**
- Jamba (Lieber et al., 2024) / Samba (Ren et al., 2024) / Hymba (Dong et al., 2024)：混合比例靠经验扫描；本 idea 提供可测量的数据结构量来**推导**比例并验证定理预测。
- Zoology / Based (Arora et al., 2024)：用合成 MQAR 刻画 recall–吞吐权衡；本 idea 把"关键宽度 + 控制半径"的双变量结构搬到真实语料上并与可证明的下界对齐。
- Jelassi et al. (2024) "Repeat After Me"：只比较复制任务上 Transformer 与 SSM；本 idea 关注控制变量与检索的复合及其在自然数据中的分布。

**🧪 验证方案**
- 关键假设检验：探针估计的 (m̂, R̂) 分布能否预测各任务上纯 SSM / 纯滑窗 / 混合模型的相对排名（Spearman 相关）；
- 基准：RULER、LongBench、∞-Bench、代码补全（RepoBench）、合成函数复合任务作为校准；
- 消融：探针给出的配置 vs 网格搜索最优配置 vs 固定 1:7 比例；控制变量条件化检索层 ± 对比。

🔑 `hybrid architecture` `state space models` `long context` `expressivity` `architecture search` `associative recall`

[🔝 top](#top)

---

## 💡 Idea 8.5 — *Designed, Not Emergent: Wavelet-Banded RoPE with Per-Head Frequency Allocation for Scale-Invariant Long-Context Attention*

| | |
|:--|:--|
| 🎯 **源论文** | **Beyond Position: the Emergence of Wavelet-like Properties in Transformers** · Ruscio et al. · 🏆 ACL 2025 SAC Highlights· [arXiv:2410.18067](https://arxiv.org/abs/2410.18067) |
| 📌 **线索来源** | Limitations §"Our primary analysis, like much of the field, examines model properties at inference time after training is complete." + Conclusion §"understanding that these optimal structures are emergent rather than designed could inspire new architectural innovations, potentially leading to models that are either explicitly guided towards these solutions or are built with more efficient, innate multi-scale processing capabilities from the start." |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
论文跨模型规模与训练检查点分析 RoPE 模型，发现注意力头**自发地**组织成类似小波变换的多分辨率结构：不同头占据不同的频率带与位置分辨率，整体遵守 Heisenberg–Gabor 不确定性原理；这种结构只在 RoPE 模型上出现，并经历"高谱熵探索期 → 专门化期"两个阶段，且在约 410M 参数处出现尺度不变性的相变。作者进一步指出 RoPE 的根本缺陷：固定频率使位置精度与长程分辨率互相牺牲、周期性导致长序列混叠、无法随输入长度自适应尺度。Limitation 明确说分析停留在训练后的观察，而"既然最优结构是涌现而非设计的，就可以把它直接设计进去"是未做的方向。真正的空隙在于：现有长上下文方法（YaRN、NTK-aware、LongRoPE）都是在**所有头共享同一频率表**的前提下做整体缩放，而论文的证据表明模型想要的是**头级的、覆盖不同尺度的频带分工**，并且小模型（<410M）学不到这种分工。关键 insight：把小波式的二进频带分配与"探索—专门化"课程显式地写入位置编码，既可能让小模型提前获得大模型才有的尺度不变性，也可能在长度外推时避免混叠。

**💡 一句话 Idea**
把 RoPE 的频率表改造成按头分配的二进（dyadic）小波频带，并用可学习的带限旋转加上"先宽带探索、后窄带专门化"的训练课程，使多分辨率处理成为内置属性而非涌现现象，从而在小模型上提前获得尺度不变性并提升长度外推。

**🛠️ 可能的解决方法**
1. **频带分配**：把 d/2 个旋转频率划分为 J 个二进尺度 [2^{-j}, 2^{-j+1})·θ_max；每个头 h 分配一个主尺度 j(h) 与可学习的带宽 σ_h，该头的旋转频率只在其频带内取值（头间覆盖所有尺度，形成小波框架）；用论文测得的头—尺度分布作为初始化先验。
2. **尺度自适应**：按论文指出的"10 token 差异在 50 token 序列里显著、在 5000 token 里可忽略"，让每个头的频带中心随序列长度 L 做对数缩放 θ_h(L) = θ_h · (L_0/L)^{α_h}，α_h 可学，长度外推时自动平移频带而非整体插值。
3. **探索—专门化课程**：训练早期对带宽 σ_h 加熵奖励（宽带、高谱熵），中后期按余弦日程收紧到窄带；监测论文定义的谱熵与位置—频谱相关系数作为课程触发信号。
4. **不确定性约束正则**：对每个头计算位置方差 × 频率方差，惩罚远离 Gabor 下界的头（避免既不精确定位也不分频的"死头"）。
5. **成本**：只改旋转频率表与两个标量/头，无额外 FLOPs；在 125M / 410M / 1B 模型上各训 20–50B token。

**🧭 与最接近工作的区别**
- YaRN (Peng et al., 2023) / LongRoPE (Ding et al., 2024)：对共享频率表做分段插值；本 idea 做头级频带分工与长度自适应，而非整体缩放。
- "Round and Round We Go" (Barbero et al., ICLR 2025)：发现高频用于位置、低频用于语义，建议截断低频；本 idea 把"哪个头用哪个频带"显式化并引入课程与不确定性约束。
- Wavelet-based Positional Representation (Oka et al., ICLR 2025)：用小波基替代 RoPE；本 idea 保留 RoPE 的相对编码（论文证明尺度不变性依赖 RoPE），只重组其频率分配。

**🧪 验证方案**
- 困惑度（训练长度内）与长度外推（2×–8× 训练长度）：PG-19、Proof-pile、RULER、Needle-in-a-Haystack；
- 关键假设检验：125M/410M 模型是否在更早的步数/更小规模出现论文定义的尺度不变性指标；带限头是否在外推时减少混叠（位置—频谱相关系数）；
- 对比：标准 RoPE、YaRN、NTK-aware、FoPE、ALiBi；消融：固定 vs 可学频带、有无课程、有无不确定性正则。

🔑 `RoPE` `positional encoding` `wavelet` `multi-resolution` `length extrapolation` `attention heads`

[🔝 top](#top)

---

## 💡 Idea 8.6 — *Tokenizer-Anchored Byte-ification: A Patch-Boundary Curriculum for Retrofitting Token LLMs into Byte Latent Transformers That Surpass Their Teachers*

| | |
|:--|:--|
| 🎯 **源论文** | **Byte Latent Transformer: Patches Scale Better Than Tokens** · Pagnoni et al. (Meta) · 🏆 ACL 2025 Outstanding Paper · [arXiv:2412.09871](https://arxiv.org/abs/2412.09871) |
| 📌 **线索来源** | Limitations and Future Work §"While BLT uses a separately trained entropy model for patching, learning the patching model in an end-to-end fashion can be an interesting direction for future work." + §"Further work in this direction may uncover methods that not only retain the benefits of bytefying, but also push performance beyond that of these tokenizer-based models without training them from scratch." |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
BLT 用一个小型字节熵模型把字节流切成动态 patch，局部编码器把字节聚合成 patch 表示送入全局 Transformer，在 8B/4T 字节的 FLOPs 受控对比中首次让字节级模型追平 Llama 3，并换来最多 50% 的推理 FLOPs 节省与对噪声的鲁棒性。Limitation 指出两个空隙：patch 切分器是独立训练、不可端到端学习；以及"byte-ify"现有的 token 模型（冻结全局 Transformer 以 Llama 3 权重初始化）只做了初步尝试，离"超越 token 教师且无需从头训练"还有距离。端到端的切分后来被 H-Net（Hwang et al., 2025）的动态分块填补，但 **retrofit 方向仍然空白**：直接用熵 patch 喂给一个在 BPE token 上训练了 15T token 的全局 Transformer，其输入分布与它见过的 token 嵌入完全不匹配，这是 BLT §6.2 结果不如从头训练的根本原因。关键 insight：tokenizer 的边界本身是一个"合法的 patch 方案"——如果 retrofit 从 patch 边界 = BPE 边界、patch 表示蒸馏到对应 token 嵌入开始，全局 Transformer 一开始就处于分布内，然后**逐步把边界退火到熵切分**，就能把"从头训练 vs 冻结迁移"的二选一变成一条平滑的路径，并在退火后期解冻全局模型以利用 patch 更长、更均匀的信息密度去超越教师。

**💡 一句话 Idea**
用"tokenizer 锚定 → 熵切分退火"的 patch 边界课程把预训练 token LLM 改造成 BLT：先让局部编码器在 BPE 边界上蒸馏出与原 token 嵌入一致的 patch 表示，再按混合比例逐步切换到熵驱动的动态 patch 并解冻全局模型，以远低于从头训练的成本获得字节级鲁棒性与推理 FLOPs 节省，且不低于教师性能。

**🛠️ 可能的解决方法**
1. **阶段 0（对齐）**：patch 边界取 BPE 边界；局部编码器输出 e_patch，损失 = ‖e_patch − E_tok‖² + 原 LM 损失（全局模型冻结）；局部解码器同样蒸馏到教师的输出分布。此时模型功能上等价于教师，但已能接收字节输入。
2. **阶段 1（边界退火）**：每个序列以概率 ρ(t) 使用熵切分边界、1−ρ(t) 使用 BPE 边界，ρ 从 0 线性升到 1；对熵切分的 patch 不再有对应 token 嵌入，改用**序列级蒸馏**（教师在 token 边界的 logits 对齐到学生字节边界的 logits，按 BLT 的字节级 next-byte 目标）。
3. **阶段 2（超越）**：解冻全局 Transformer（LoRA 或全参），用熵阈值较高的长 patch 在相同推理 FLOPs 下扩大全局模型层数或宽度（BLT 发现 patch 变长允许模型变大）；加入字节级噪声增强（拼写、Unicode 混淆）作为教师没有的训练信号。
4. **可学习切分**：把熵模型替换为可微的边界预测器（H-Net 式的相似度路由），但用阶段 0 的 BPE 边界做监督热启动，避免从头学习分块。
5. **成本**：以 Llama-3-8B 为教师，总训练量 ≤ 200B 字节（约为教师预训练的 1%），8×H100 数周。

**🧭 与最接近工作的区别**
- BLT §6.2 的 byte-ify 实验：直接冻结全局模型并用熵 patch，分布不匹配；本 idea 用 tokenizer 锚定课程消除这一失配。
- H-Net (Hwang et al., 2025)：端到端动态分块但从头预训练；本 idea 是 retrofit 路径，复用 10T+ token 的已有预训练。
- MrT5 (Kallini et al., 2024) / SpaceByte (Slagle, 2024)：字节模型内的 token 删除/空格切分；不涉及从 token 模型迁移。

**🧪 验证方案**
- 基准：MMLU、HellaSwag、ARC、HumanEval、GSM8K（与教师对比）；鲁棒性：CUTE、噪声 HellaSwag、拼写扰动；多语言 FLORES；
- 指标：相同推理 FLOPs 下的准确率、bits-per-byte、训练成本（字节数 / GPU 时）；
- 关键假设检验：阶段 0 后是否与教师功能等价（KL < 0.01）；退火中性能曲线是否平滑无塌陷；阶段 2 是否在 ≥3 个基准上超过教师；
- 消融：无锚定直接熵切分（复现 BLT §6.2）、无退火硬切换、冻结 vs 解冻全局模型。

🔑 `byte-level LLM` `dynamic patching` `retrofitting` `distillation` `tokenization-free` `inference efficiency`

[🔝 top](#top)

---

## 💡 Idea 8.7 — *Coherence-Breaking Rounding: Online Detection and Decorrelation of Low-Rank Error Accumulation for Stable FP8 Flash Attention Training*

| | |
|:--|:--|
| 🎯 **源论文** | **Why Low-Precision Transformer Training Fails: An Analysis on Flash Attention** · Qiu & Yao · 🎤 ICLR 2026 Oral · [arXiv:2510.04212](https://arxiv.org/abs/2510.04212) |
| 📌 **线索来源** | Limitations §"The generalizability of our findings to other architectures, larger scales, or different low-precision formats like FP8 requires further investigation." + Future Work §"developing automated tools to detect and mitigate such numerical instabilities during training would be valuable for the community." |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
论文首次为"BF16 flash attention 训练 GPT-2 在数千步后损失爆炸"这一悬置两年的问题给出机理：(1) 注意力内部出现**相似的低秩表示**，使误差矩阵 (PK)[T]ᵀX[T] 在不同 token 上结构相似；(2) BF16 的**有偏舍入**（尤其是 attention sink 令 P 中出现恰好为 1 的概率值，触发 P̄V 计算中的系统性舍入偏差）；两者耦合使舍入误差在梯度中**相干地累积**成低秩误差矩阵，推高权重谱范数，形成恶性循环。他们还解释了 QK-norm 与门控注意力为何有效——它们打破误差的结构相似性。Limitation 清楚：分析只针对 GPT-2/BF16，FP8 与更大规模未验证；修复是针对该特定舍入误差的定点补丁；并呼吁自动化的检测与缓解工具。空隙在于：当前 FP8 训练实践（DeepSeek-V3 的细粒度分块缩放、Scalify 的尺度传播）处理的是**动态范围**问题，而论文揭示的是**误差相干性**问题——即便每个元素的舍入误差很小，只要方向一致就会累积。没有任何现有方法在训练中度量"误差方向的相干度"。关键 insight：相干累积是可以在线、廉价地检测的（误差矩阵的主奇异方向跨步余弦相似度），而一旦检测到，只需对触发源（P≈1 的 sink 列、低秩区块）做**去相关**的舍入（随机/抖动舍入），而不必全局提升精度。

**💡 一句话 Idea**
在 flash attention 内核中内置一个低开销的"误差相干度监视器"（跨步追踪梯度误差主方向的一致性），当相干度超阈值时仅对触发源（接近 1 的注意力概率与低秩区块）切换为随机/抖动舍入以打破误差方向一致性，使 FP8/BF16 flash attention 在不牺牲吞吐的情况下保持稳定。

**🛠️ 可能的解决方法**
1. **相干度统计量**：每 k 步对一个采样层计算 E_t = (PK)[T]ᵀX[T] 的 top-1 奇异向量（用 2–3 步幂迭代，在 tile 级别聚合，开销 <1%），定义 c_t = |⟨u_t, u_{t−k}⟩|；同时记录 P 中等于 1 的元素比例 s_t（sink 触发率）与 Q/K 的有效秩。c_t 持续上升 + s_t 上升即为爆炸前兆（论文的损失爆炸前数百步应可观测）。
2. **靶向去相关舍入**：当 c_t > τ 时，对 P̄V 乘积中 P̄ ≥ 1−δ 的元素采用**随机舍入**（无偏），对其余元素保留 RN 舍入（保持吞吐）；对 dQ/dK 的低秩累积项加入每 tile 独立的微小随机抖动（dither），幅度为该 tile 尺度的 ½ ulp。
3. **FP8 扩展**：在 E4M3/E5M2 下复现论文的失败案例，检验相干累积是否更早出现（动态范围更小、偏差更大）；与细粒度分块缩放（DeepSeek-V3 风格）组合，验证两者正交。
4. **自动化工具**：把监视器做成训练钩子，输出"相干度—步数"曲线并在阈值触发时自动切换舍入模式或临时启用 QK-norm 等价的在线缩放；与论文的"定位误差源 → 找相似更新方向 → 回溯根因"流程一致。
5. **成本**：GPT-2 124M/350M 复现 + 1B 规模 FP8 训练各 50B token，8×H100。

**🧭 与最接近工作的区别**
- QK-norm (Henry et al., 2020; Qwen3) / QK-clip (Kimi K2) / Gated Attention (Qiu et al., 2025)：架构级预防，改变模型函数；本 idea 不改模型，只在触发时改变舍入统计。
- Stochastic rounding for training (Ali et al., 2024) / Scalify (Balança et al., 2024)：全局随机舍入或尺度传播，针对范围与均值偏差；本 idea 只在检测到相干累积时对触发源靶向应用，开销与吞吐几乎不变。
- DeepSeek-V3 FP8 训练 (2024)：分块缩放解决动态范围；不度量也不处理误差方向相干性。

**🧪 验证方案**
- 复现：GPT-2 + BF16 flash attention 的损失爆炸（nanoGPT issue 303/524/554）；记录相干度 c_t 是否在爆炸前显著上升（前兆检验）；
- 干预：靶向随机舍入 vs 全局随机舍入 vs FP32 attention vs QK-norm，比较稳定性、最终困惑度与吞吐；
- FP8：E4M3 训练 350M/1B 模型，有/无监视器，比较崩溃率与权重谱范数增长；
- 消融：阈值 τ、只处理 sink 列 vs 只处理低秩块、监视频率 k。

🔑 `low-precision training` `flash attention` `FP8` `numerical stability` `attention sink` `rounding error`

[🔝 top](#top)

---

## 💡 Idea 8.8 — *Signed Log-Space Scans: Making Negative Eigenvalues Compatible with Chunked Linear RNN Kernels and Charting the State-Tracking vs. Recall Trade-off*

| | |
|:--|:--|
| 🎯 **源论文** | **Unlocking State-Tracking in Linear RNNs Through Negative Eigenvalues** · Grazzi et al. · 🎤 ICLR 2025 Oral · [arXiv:2411.12537](https://arxiv.org/abs/2411.12537) |
| 📌 **线索来源** | Conclusion (Limitations and Future work) §"Our modification is not directly compatible with a numerical technique used by some diagonal LRNNs such as Mamba2, GLA and mLSTM. In particular, these models rely on positive state-transition matrices to compute cumulative products in log space" + §"we hypothesize a fundamental trade-off between state-tracking and associative recall, which is also of theoretical interest and could guide hybrid model design." |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
论文证明有限精度、状态转移矩阵特征值仅为正的线性 RNN（Mamba、GLA、DeltaNet 等）无法解奇偶性等最简单的状态追踪任务，而把特征值范围从 [0,1] 扩展到 [−1,1]（Mamba 把对角转移标量从 (0,1] 重新参数化到 [−1,1]、DeltaNet 把 β 的范围扩到 [0,2]）即可解奇偶性、模加法与更多群词问题，且零额外开销。Limitation 指出一个具体的工程障碍：Mamba2、GLA、mLSTM 的高效 chunked 内核依赖**对数空间累乘**（log a 累加后 exp），这只对正数成立，所以负特征值无法进入这些最主流的内核；同时作者提出但未验证"状态追踪与关联检索之间存在根本权衡"的假设。后续 DeltaProduct（Siems et al., 2025）用 Householder 乘积扩展了表达力，但依然绕开了对数空间内核的问题，GLA/Mamba2 系列至今仍限制在正特征值。关键 insight：负数的累乘可以精确分解为"幅度的对数累加 + 符号的异或累加"——符号是一个比特，其前缀积是 XOR 前缀扫描，与对数累加一样可并行、可分块，代价仅为每个标量一位；这意味着负特征值与数值稳定的 log-space 内核本质上是兼容的，只是从未被实现。有了这样的内核，就能在真实语言模型规模上检验"追踪—检索权衡"并据此分配头级特征值范围。

**💡 一句话 Idea**
把状态转移标量参数化为 (符号比特, 对数幅度) 并在 chunked 扫描中用 XOR 前缀积携带符号、用对数累加携带幅度，使负特征值零成本地进入 Mamba2/GLA/mLSTM 内核；再用该内核在语言模型规模上实证"状态追踪 vs 关联检索"权衡，并设计按头分配特征值范围的混合配置。

**🛠️ 可能的解决方法**
1. **参数化**：a_t = s_t · exp(−Δ_t)，s_t ∈ {−1,+1} 由 s_t = sign(tanh(w·x_t)) 给出，前向用硬符号、反向用 tanh 的直通估计；幅度分支与原模型完全相同。
2. **内核**：chunk 内与 chunk 间的累乘拆为 (Σ log|a|, ⊕ sign-bit)；在 Triton 实现中把符号打包进 int8/位掩码，与 log 幅度的前缀和一起扫描；输出时 exp(Σlog|a|)·(−1)^{⊕bits}。对 Mamba2 的 SSD 分解与 GLA 的 chunked 形式分别给出实现，验证数值精度与原内核一致。
3. **可学习符号的软化**：训练早期用 s_t = tanh(w·x_t/τ) 的软符号并退火 τ→0，避免符号翻转导致的梯度噪声；对比直接硬符号。
4. **权衡实证**：在 340M/1.3B 模型上同 FLOPs 训练三组：全部头 [0,1]、全部头 [−1,1]、混合（一半头 [−1,1]）；在状态追踪（奇偶性、S_5 群词、代码执行追踪）与关联检索（MQAR、Needle、SWDE）上测量，检验论文的权衡假设并量化最优混合比例。
5. **成本**：内核开发 + 1.3B×30B token 训练，8×H100 两周。

**🧭 与最接近工作的区别**
- Sarrof et al. (2024) / 本源论文：证明并实现了负特征值，但只在无 log-space 的实现上；本 idea 解决与主流 chunked 内核的兼容性。
- DeltaProduct (Siems et al., 2025) / PaTH Attention (Yang et al., 2025)：通过 Householder 乘积提高表达力，仍不触及 Mamba2/GLA 的正数约束。
- Gated DeltaNet (Yang et al., 2025)：门控 + delta 规则；本 idea 可直接叠加到其内核上，并额外提供权衡实证与头级分配。

**🧪 验证方案**
- 内核：与 FP32 顺序实现的数值误差、吞吐与原 Mamba2/GLA 内核对比；
- 合成：奇偶性、模加法、S_3/S_5 群词问题、MQAR 的长度泛化曲线；
- 语言建模：困惑度、LAMBADA、代码执行（CRUXEval）、长上下文检索（RULER）；
- 关键假设检验：[−1,1] 头的比例与 MQAR 精度是否负相关、与状态追踪精度是否正相关（权衡曲线）。

🔑 `linear RNN` `state tracking` `Mamba2` `log-space scan` `negative eigenvalues` `associative recall`

[🔝 top](#top)

---

## 💡 Idea 8.9 — *Compression-in-the-Loop Reasoning: Eliminating Generation-Length Inflation under KV Cache Compression via Cache-Perturbed RL Fine-Tuning*

| | |
|:--|:--|
| 🎯 **源论文** | **ThinKV: Thought-Adaptive KV Cache Compression for Efficient Reasoning Models** · Ramachandran et al. (NVIDIA / Georgia Tech) · 🎤 ICLR 2026 Oral · [arXiv:2510.01290](https://arxiv.org/abs/2510.01290) |
| 📌 **线索来源** | Discussions and Ablations §"TBQ, operating at an average precision of 3.5 bits, maintains accuracy comparable to FullKV. However, as shown in Figure 10 (d), its substantial generation-length inflation negates most of the compression gains" + Appendix F Limitations §"While ThinKV demonstrates strong performance for long-output reasoning tasks, it is not directly applicable to settings dominated by long input contexts." |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
ThinKV 发现推理模型的 CoT 可按注意力稀疏模式分为推理、执行、过渡三类"思维段"，并据此做段级量化 + 渐进驱逐，以 <5% 的 KV 缓存取得近无损精度与最高 5.8× 吞吐。论文一个被低估的发现是：**KV 压缩会让生成变长**——纯量化（TBQ）虽然精度无损，但"生成长度膨胀"把大部分压缩收益吃掉了；这说明被压缩的缓存让模型"记不清自己想过什么"，于是重复推导、反复验证。现有所有 KV 压缩方法（H2O、SnapKV、R-KV、LazyEviction、ThinKV）都是**训练后、推理时**的近似，模型从未在"缓存会被压缩"的条件下训练过，所以压缩的代价表现为隐性的长度膨胀而非显性的精度下降——而当前评测几乎只看精度，不看长度。另一个 Limitation 是只处理长输出、不处理长输入。关键 insight：对推理模型而言，压缩策略是推理环境的一部分；若把压缩算子放进 RL 训练的 rollout 中（策略在被压缩的缓存下生成），并把生成长度纳入奖励，模型就能学会在有损记忆下**不重复、不迷路**地推理——这把压缩从"近似"变成"模型可适应的训练条件"，并自然地统一长输入与长输出场景。

**💡 一句话 Idea**
把 KV 压缩算子（段级量化 + 驱逐，随机采样压缩预算）嵌入推理模型的 RL rollout 与 SFT 前向中，用"正确率 − λ·相对生成长度"作为奖励进行微调，使模型在被压缩的缓存下不再出现生成长度膨胀，从而把 ThinKV 类方法的理论压缩收益完整兑现，并扩展到长输入 + 长输出的混合场景。

**🛠️ 可能的解决方法**
1. **可微/可采样的压缩环境**：训练时对每条 rollout 采样压缩配置 c ~ U{预算 ∈ [2%, 20%], 位宽 ∈ {2,3,4,16}}，在生成过程中按 ThinKV 规则（或简化的段级规则）实时量化/驱逐缓存；教师强制的 SFT 前向同样在压缩缓存上计算（用 straight-through 的量化与 mask 的驱逐）。
2. **奖励**：r = 1[答案正确] − λ·max(0, L_c/L_full − 1) − μ·重复 n-gram 比例，其中 L_full 是同题无压缩时的生成长度（用参考策略离线估计）；GRPO 组内样本共享题目但各自采样不同压缩配置，使优势估计包含"在更紧预算下保持短而对"的信号。
3. **压缩感知的思维标记**：允许模型输出轻量的"摘要 token"（如 `<keep>` 段）来主动指定哪些段必须高精度保留——驱逐策略以此为优先级；该行为由奖励自然激励。
4. **长输入扩展**：prefill 阶段用同样的段级规则（对输入按注意力稀疏模式分段）压缩，训练时混入长输入 + 长推理的任务（如长文档数学/代码题），使模型同时适应两种压缩。
5. **成本**：R1-Distill-Llama-8B / Qwen3-8B，RL 微调 ~2k 步，8×H100 数天；压缩内核沿用 ThinKV 的 PagedAttention 扩展。

**🧭 与最接近工作的区别**
- ThinKV / R-KV (Cai et al., 2025) / LazyEviction (Zhang et al., 2025)：纯推理时压缩，模型未适应，长度膨胀未被优化。
- Dynamic Memory Compression (Nawrot et al., 2024)：通过继续预训练让模型学会 KV 合并，但面向通用 LLM、不含推理 RL，也不处理长度膨胀。
- 长度惩罚 RL（如 L1 / ThinkPrune, 2025）：压缩推理长度但在全精度缓存下训练；本 idea 的目标是**在有损缓存下**保持长度与精度，两者可叠加。

**🧪 验证方案**
- 基准：AIME24/25、MATH-500、LiveCodeBench、GPQA；长输入：LongBench-Reasoning / 长文档数学题；
- 指标：精度、生成长度比 L_c/L_full、端到端吞吐与内存（iso-batch 与 iso-memory 两种设定）；
- 关键假设检验：微调后在 5% 缓存预算下 L_c/L_full 是否从 >1.3 降到 ≈1.0 且精度不降；对未见过的压缩预算/位宽是否泛化；
- 消融：无长度惩罚、固定 vs 采样压缩配置、有无 `<keep>` 标记、SFT-only vs RL。

🔑 `KV cache compression` `reasoning models` `RL fine-tuning` `generation length` `inference efficiency` `long CoT`

[🔝 top](#top)

---

## 💡 Idea 8.10 — *Newton-Friendly Recurrences: Training Nonlinear RNNs to Converge in Two Parallel Iterations with Learned Structured Jacobians*

| | |
|:--|:--|
| 🎯 **源论文** | **ParaRNN: Unlocking Parallel Training of Nonlinear RNNs for Large Language Models** · Danieli et al. (Apple) · 🎤 ICLR 2026 Oral · [arXiv:2510.21450](https://arxiv.org/abs/2510.21450) |
| 📌 **线索来源** | §2.1 Limitations §"In practice, we need convergence in a small O(1) number of iterations. Fortunately, for the RNN considered in this work, three iterations proved to be sufficient in all cases, but this must be verified for newly defined RNN wanting to leverage ParaRNN." + §"In practice, then, one should inject some additional structure in the Jacobians definition, so to make these operations more tractable." |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
ParaRNN 把整段非线性递推 h_t = f(h_{t−1}, x_t) 写成一个大方程组，用牛顿迭代 + 并行归约求解，使经典非线性 RNN（LSTM/GRU 变体）在 7B 规模上可并行训练，并与 Transformer/SSM 打平。但论文自己列出两个制约：(1) 并行化收益完全取决于牛顿迭代能否在 O(1) 步内收敛——理论保证是 L 步（退化为顺序），实践中"三步够用"只是对他们所选的单元成立，**任何新 RNN 都要重新验证**；(2) 雅可比矩阵必须有结构（他们用对角结构），否则内存 O(L·d²)、计算 O(d³) 不可行。这意味着 ParaRNN 实际上只把"可并行"的门槛从线性递推放宽到了"雅可比简单、收缩性强的非线性递推"，而**哪些非线性是便宜的**从未被系统刻画，也没有机制让训练本身朝着"便宜的非线性"走。关键 insight：牛顿收敛速度由递推映射的局部 Lipschitz 常数（雅可比谱半径）与残差的非线性程度控制，这两者都可以在训练中测量并正则化——把"迭代次数"当作一个可优化的代价而不是事后验证的常数，就能让模型自己学到既有表达力又快速可并行求解的非线性；同时雅可比结构可以从"对角"放宽到"对角 + 低秩"，在保持 O(d·r²) 代价下恢复通道混合（论文指出通道混合是 DeltaNet 类模型表达力的关键）。

**💡 一句话 Idea**
把牛顿迭代次数内生为训练目标：对非线性 RNN 施加雅可比谱半径正则与"K 步残差"惩罚，并用对角 + 低秩的可学习雅可比结构，使任何新设计的非线性递推都能在训练中自发收敛到 ≤2 步牛顿迭代可解的区域，从而把 ParaRNN 的并行收益从特定单元推广为通用的架构设计原则。

**🛠️ 可能的解决方法**
1. **收敛性正则**：对采样的时间步估计 ρ_t = ‖∂f/∂h‖_2（幂迭代 2 步，Hutchinson 采样），加损失 λ·Σ max(0, ρ_t − ρ_max)²；理论上 ρ_max < 1 保证压缩映射、牛顿在 O(log(1/ε)) 步内收敛。
2. **K 步残差惩罚**：训练时固定牛顿步数 K=2，把第 K 步后的残差范数 ‖h^{(K)} − f(h^{(K)}_{prev}, x)‖ 作为辅助损失（直通梯度），直接惩罚"需要更多迭代"的参数区域；推理时用自适应停止。
3. **结构化雅可比**：递推写成 h_t = D(x_t)⊙h_{t−1} + U(x_t)V(x_t)ᵀh_{t−1} + φ(·)，雅可比为对角 + 秩 r 的形式；并行归约中两个 (对角+低秩) 的乘积仍是对角 + 秩 ≤2r，用截断 SVD 投回秩 r（误差进入残差，由牛顿修正）。
4. **非线性菜单搜索**：以上述正则为代价，在 {tanh, GELU 门、乘性交互、softmax 归一化} 等非线性族上做小规模 NAS，输出"表达力（状态追踪/MQAR 分数）vs 牛顿步数"的 Pareto 前沿。
5. **成本**：沿用 ParaRNN 代码；340M/1B 规模各训 20B token，8×H100。

**🧭 与最接近工作的区别**
- DEER (Lim et al., 2024) / ELK & quasi-DEER (Gonzalez et al., 2024)：提出并行牛顿/拟牛顿求解非线性序列模型，但把收敛性当作给定属性；本 idea 把收敛性变成训练目标与架构约束。
- ParaRNN 本身：对角雅可比 + 固定 3 步；本 idea 给出对角 + 低秩结构与自适应步数，并提供通用的"可并行非线性"设计原则。
- Mamba / Gated DeltaNet 等线性 RNN：靠线性化保证并行；本 idea 保留真正的非线性递推（可解奇偶性等）同时保持并行。

**🧪 验证方案**
- 指标：平均牛顿步数、训练吞吐（token/s）vs 顺序实现与 ParaRNN 基线、困惑度；
- 表达力：奇偶性、S_5 群词、MQAR、代码执行追踪；
- 关键假设检验：加入收敛正则后新非线性单元的迭代次数是否从 >5 降到 ≤2 而困惑度不降；对角+低秩雅可比是否在 MQAR 上优于纯对角；
- 消融：各正则项、秩 r、K 的取值。

🔑 `nonlinear RNN` `parallel training` `Newton iteration` `Jacobian structure` `sequence modeling` `expressivity`

[🔝 top](#top)

---

## 💡 Idea 8.11 — *Elastic-k MoE: Matryoshka Routing to Decouple Train-Time Sparsity from Test-Time Active FLOPs in Overtrained Mixture-of-Experts*

| | |
|:--|:--|
| 🎯 **源论文** | **Optimal Sparsity of Mixture-of-Experts Language Models for Reasoning Tasks** · Nakamura et al. · 🎤 ICLR 2026 Oral · [arXiv:2508.18672](https://arxiv.org/abs/2508.18672) ＋ **OLMoE: Open Mixture-of-Experts Language Models** · Muennighoff et al. · 🎤 ICLR 2025 Oral · [arXiv:2409.02060](https://arxiv.org/abs/2409.02060) |
| 📌 **线索来源** | Nakamura · Discussion and Limitations §"with larger training corpora, one could train larger models at higher tokens-per-parameter, potentially shifting the optimal sparsity toward sparser configurations, even for reasoning skills. We leave this as a direction for future work." + OLMoE · Limitations and Future Work §"to what degree overtraining is effective for MoEs and how it differs from dense models still requires more research" |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
Nakamura 等在固定 125B token 预算下系统扫描 MoE 的总参数、激活参数与 top-k，发现两条规律：**训练损失相同时激活 FLOPs 更多的模型推理更强**（top-k 越大越好），以及**每参数 token 数（TPP）决定任务类型的最优点**（记忆任务偏好高稀疏、推理任务在 TPP≈20 处达峰，稀疏度与推理表现呈倒 U）。他们明确把"更大语料下最优稀疏度是否右移"留给未来；OLMoE 则以 5T token 训练 1B 激活参数（token 乘数 ≈5000）并承认"MoE 过训练的有效性与稠密模型有何不同仍需研究"。两篇论文合起来暴露了一个结构性问题：所有结论都来自**训练时 k 固定、测试时 k 相同**的模型族，于是"激活 FLOPs 有益"到底来自训练时每个 token 看到更多专家（更高训练强度），还是来自测试时更多计算，无法分离；而回答"过训练是否应该更稀疏"又需要为每个 (稀疏度, 数据量) 组合各训一个模型，代价极高。关键 insight：如果路由被训练成**嵌套的**（top-1 的输出是有效模型、top-2 在其上增量改进、…），那么一个模型就能在推理时任意选择 k，从而 (a) 直接分离训练 FLOPs 与测试 FLOPs 的贡献，(b) 把稀疏度扫描从"多次训练"变成"一次训练 + 多次评测"，使过训练区间的最优稀疏度曲线可负担地测出来。

**💡 一句话 Idea**
用 Matryoshka 式嵌套路由训练 MoE（每步随机采样 k，并使 top-k' 前缀对任意 k'≤k 都是合法输出），得到一个可在推理时弹性调节激活 FLOPs 的模型，以此分离训练/测试 FLOPs 对推理能力的贡献，并在过训练（TPP 数千）区间一次性测出最优稀疏度随数据量的迁移规律。

**🛠️ 可能的解决方法**
1. **嵌套路由**：路由权重 g = softmax(logits)，输出 y_k = Σ_{i≤k} g_i e_i / Σ_{i≤k} g_i（前缀归一化），训练时每个 micro-batch 采样 k ~ {1,2,4,8}（按 FLOPs 预算加权），损失为 Σ_k w_k·L(y_k)；加入"前缀一致性"蒸馏项 KL(y_8 ‖ y_k) 使小 k 输出逼近大 k。
2. **负载均衡**：对每个 k 分别计算负载均衡损失，避免 top-1 坍缩到少数专家；路由 z-loss 沿用 OLMoE 配方。
3. **FLOPs 分离实验**：固定总参数 7B、训练 k 分布相同的 Elastic-k 模型，在 k_test ∈ {1,2,4,8} 下评测推理（GSM8K、MATH、ARC-C）与记忆（TriviaQA、NQ）任务；与"训练 k=测试 k"的固定模型族对比，判断增益来自训练还是测试。
4. **过训练扫描**：在 1B 激活参数上把训练 token 从 125B 推到 2T（TPP 从 20 到 300+ 以总参数计），每个检查点测出各 k 下的推理/记忆曲线，拟合"最优稀疏度 vs 数据量"的函数形式，检验 Nakamura 等的右移假设。
5. **测试时计算的新维度**：对比"提高 k"与"更长 CoT / 多数投票"在等 FLOPs 下的推理收益，给出 k 作为测试时计算旋钮的性价比。

**🧭 与最接近工作的区别**
- Ada-K Routing (Yue et al., 2024) / "Harder Tasks Need More Experts" (Huang et al., 2024)：按 token 难度动态选 k，目标是省算；本 idea 的嵌套结构面向**事后弹性评测与科学分离**，并给出过训练稀疏度规律。
- MatFormer (Devvrit et al., 2023)：在 FFN 宽度上做嵌套；本 idea 把嵌套放在 MoE 路由前缀上，保持专家粒度与负载均衡。
- Nakamura et al. / OLMoE：固定 k 的模型族；本 idea 用一个模型覆盖整条稀疏度曲线。

**🧪 验证方案**
- 指标：各 k_test 下的推理/记忆基准、困惑度、激活 FLOPs；与固定 k 模型族的差距（嵌套代价）应 <1%；
- 关键假设检验：训练 k 分布固定、仅改 k_test 时推理分数是否单调上升（测试 FLOPs 假设）；过训练后最优 k 是否下降（右移假设）；
- 对比：固定 top-k MoE、Ada-K、稠密同 FLOPs 模型；消融：前缀一致性蒸馏、k 的采样分布。

🔑 `mixture of experts` `sparsity` `scaling laws` `test-time compute` `overtraining` `reasoning`

[🔝 top](#top)

---

## 💡 Idea 8.12 — *Tokenization Consistency as a Trainable Objective: A Controlled Test of Whether Surface-Form Invariance Causes Tokenizer Robustness*

| | |
|:--|:--|
| 🎯 **源论文** | **TokSuite: Measuring the Impact of Tokenizer Choice on Language Model Behavior** · Altıntaş et al. · 🎤 ICML 2026 Oral · [arXiv:2512.20757](https://arxiv.org/abs/2512.20757) |
| 📌 **线索来源** | Discussion §"We speculate this is driven by TokenMonster's tokenization consistency, the degree to which the same surface form maps to the same token sequence" + §"A fully controlled factorial study, training tokenizers from scratch while varying one design factor at a time, is beyond the scope of our work." |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
TokSuite 训练了 14 个除分词器外完全相同的模型，并用母语者标注的五语言扰动基准测量鲁棒性，发现：分词器的影响不能由压缩率/词表大小等常规指标解释；最鲁棒的是一个词表仅 32k、只在英文上训练的 TokenMonster；而 LaTeX/STEM 内容中微小的格式差异会导致灾难性退化。作者把 TokenMonster 的优势**归因于"分词一致性"**（同一表面形式总映射到同一 token 序列，例如统一 `hello` 与 `␣hello`），但明确说这是推测，且受限于现成分词器多个设计维度同时变化，无法做因果归因。空隙有二：(1) 没有人把"一致性"量化为可独立操纵的变量去做受控实验；(2) 即便一致性是原因，现有的解决思路只能是换分词器——而绝大多数已部署模型的分词器不可更换。关键 insight：一致性可以在**模型侧**而不是分词器侧施加——同一文本的多种合法切分（BPE-dropout 采样、带/不带前导空格、Unicode 规范化变体）应产生相同的预测分布，这是一个可直接优化的不变性目标；它既是对"一致性假设"的干预式检验，也是不换分词器就能提升鲁棒性的方法。

**💡 一句话 Idea**
把"分词一致性"从分词器属性变成模型训练目标——对同一文本采样多种合法切分并最小化其预测分布的 KL 散度，同时做一个只改变一致性、其余因素固定的分词器因子实验，以因果地检验 TokSuite 的假设并给出不更换分词器即可提升鲁棒性的方法。

**🛠️ 可能的解决方法**
1. **受控因子实验**：从同一语料、同一词表大小（32k）训练 BPE 分词器的四个变体：{贪心, ungreedy} × {区分前导空格, 统一前导空格}，计算每个变体的一致性分数 C =（同一词型的最常见切分占比）；其余（算法、规范化、语料）固定。各训一个 TokSuite 配置的模型，测量鲁棒性与 C 的相关性。
2. **切分不变性目标**：训练时以概率 p 对输入做切分扰动 τ'(x)（BPE-dropout、前导空格翻转、NFC/NFKC 变体、LaTeX 空白变体），损失 = L_LM(τ(x)) + β·KL(p(·|τ(x)) ‖ p(·|τ'(x)))，其中 KL 在字节边界对齐的位置上计算（把 token 级分布边缘化到字节级）。
3. **Retrofit 版本**：对已有模型（Llama-3、Qwen3）做 1–5B token 的继续训练仅加入不变性项，检验是否能在不改分词器的情况下缩小 STEM/LaTeX 扰动下的退化。
4. **STEM 专项**：在数学/代码数据上构造"语义不变但切分不同"的扰动对（空格、换行、`\left(` vs `(`），作为不变性目标的硬样本。
5. **成本**：TokSuite 规模（~1B 参数）模型各训 1 次，共 ~6 次训练；retrofit 实验 8×H100 数天。

**🧭 与最接近工作的区别**
- BPE-dropout (Provilkov et al., 2020)：训练时随机切分作为正则，目标仍是 LM 损失，不显式要求切分间一致；本 idea 显式最小化切分间的预测差异，并把一致性量化为因子变量。
- "Tokenization Consistency Matters" (Sun et al., 2023)：发现抽取式 QA 中输入/输出切分不一致有害，提出一致性解码；本 idea 面向预训练鲁棒性与 STEM 格式扰动，且提供因果实验。
- TokenMonster / SuperBPE (Liu et al., 2025)：分词器侧的改进；本 idea 在模型侧实现一致性，可用于不可更换分词器的已部署模型。

**🧪 验证方案**
- 基准：TokSuite 五语言扰动基准、CUTE、LaTeX/STEM 扰动集、代码格式扰动（HumanEval 变体）；
- 关键假设检验：因子实验中一致性分数 C 与鲁棒性的相关是否显著且独立于词表大小/压缩率；不变性训练是否使"低一致性分词器"的模型追平"高一致性分词器"的模型；
- 对比：BPE-dropout、无扰动基线、字节级模型；消融：β、扰动类型、字节对齐 KL vs token 级 KL。

🔑 `tokenization` `robustness` `invariance training` `controlled study` `BPE` `STEM text`

[🔝 top](#top)

---

## 💡 Idea 8.13 — *Symmetry-Aligned Adapter Transport: Carrying PEFT Modules Across Independently Pretrained Base Models via Generalized Mode Connectivity*

| | |
|:--|:--|
| 🎯 **源论文** | **Adapt Once, Thrive with Updates: Transferable Parameter-Efficient Fine-Tuning on Evolving Base Models** · Gu et al. · 🏆 ACL 2025 SAC Highlights· [arXiv:2506.06844](https://arxiv.org/abs/2506.06844) ＋ **Generalized Linear Mode Connectivity for Transformers** · Theus et al. · 🎤 NeurIPS 2025 Oral · [arXiv:2506.22712](https://arxiv.org/abs/2506.22712) |
| 📌 **线索来源** | Trans-PEFT · Limitations §"Since PEFT operates within a specific parameter space Aghajanyan et al. (2021), transferring parameters across completely distinct spaces remains infeasible. Exploring ways to adapt our method to these conditions represents a direction for future research." + GLMC · Limitations §"The current scope is focused on aligning pairs of models that have been pretrained on the same task" |
| ⭐ Novelty | ★★★★★ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
Trans-PEFT 发现基座模型的**继续训练**主要改变 FFN 中的任务知识、而注意力中的任务模式相对稳定，于是让 PEFT 模块少依赖 FFN、多依赖注意力，从而在基座更新后无需重调；但 Limitation 直言：当基座是**重新预训练**（不同随机初始化、如 LLaMA2→LLaMA3）时，参数空间完全不同，迁移"不可行"。另一方面，GLMC 证明只要考虑足够丰富的对称群（置换、半置换、正交变换、一般可逆映射），独立训练的 ViT 与 GPT-2 之间也存在零势垒的线性连接路径——即"不同初始化的参数空间"在对称变换下是可对齐的；其 Limitation 是只处理同任务预训练的模型对，且未在大模型上验证。两篇合起来指向一个未被尝试的推论：Trans-PEFT 认为不可行的跨初始化迁移，恰好是 GLMC 所证明的对称对齐能解决的问题——LoRA 的更新 ΔW = BA 存在于基座 A 的坐标系中，若能估计把基座 A 映射到基座 B 坐标系的层级变换 (T_in, T_out)，则 ΔW_B ≈ T_out·ΔW_A·T_in⁻¹ 就是在 B 坐标系中的同一功能更新。关键 insight：对齐不需要在整个参数空间上做，只需在 LoRA 触及的子空间上做，而正交/可逆变换对低秩结构封闭（BA 变换后仍是秩 r），所以传输后的适配器仍是合法的 LoRA，可以继续以极低成本微调。

**💡 一句话 Idea**
用 GLMC 的广义对称对齐在少量校准数据上估计旧基座到新基座的逐层可逆/正交变换，把 LoRA 等 PEFT 模块按 ΔW_B = T_out ΔW_A T_in⁻¹ 传输到独立预训练的新基座上，再做数百步校准微调，使"重新预训练"场景下的大量 PEFT 模块免于全量重调。

**🛠️ 可能的解决方法**
1. **变换估计**：对每层残差流与各线性层输入/输出，在 ~10k 校准样本上收集 A、B 两基座的激活，求解 T = argmin ‖T·H_A − H_B‖_F（正交 Procrustes 或带岭正则的最小二乘得到一般可逆映射），注意力头内按 GLMC 的方法先消除头内依赖再做半置换匹配。
2. **适配器传输**：LoRA 的 B_A ∈ ℝ^{d_out×r}、A_A ∈ ℝ^{r×d_in} 传输为 B_B = T_out B_A、A_B = A_A T_in⁻¹；对 DoRA/IA³ 等做相应的坐标变换；传输后仍为秩 r。
3. **残差校准**：由于两基座功能并非完全等价，用传输后的适配器作初始化，在原任务数据上做 100–500 步微调（相当于 Trans-PEFT 成本的 1–5%），并把 Trans-PEFT 的"少依赖 FFN"策略叠加以提高可迁移性。
4. **几何验证**：按 GLMC 检查对齐后两基座 + 适配器之间的线性插值势垒是否接近零，作为传输是否成功的无标签预测指标。
5. **成本**：7B 级（LLaMA2-7B → LLaMA3-8B，需处理 d 相同、词表不同的情况：词表层用共享 token 子集做对齐）；单机 8 卡数小时即可完成全部对齐。

**🧭 与最接近工作的区别**
- Trans-LoRA (Wang et al., 2024)：用合成数据把 LoRA 的行为蒸馏到新基座上，需要生成数据并重新训练；本 idea 直接在参数空间传输，训练量低一至两个数量级。
- LoRA-X (Farhadzadeh et al., 2025)：把适配器限制在基座权重的子空间内以便跨模型迁移，要求目标模型子空间相似；本 idea 不限制适配器形式，而是显式估计跨模型坐标变换。
- Git Re-Basin (Ainsworth et al., 2023) / ZipIt (Stoica et al., 2024)：置换对齐用于模型合并；本 idea 用更广的对称群（GLMC）并把对象从"合并模型"换成"传输适配器"。

**🧪 验证方案**
- 场景：LLaMA2-7B→LLaMA3-8B、Qwen2-7B→Qwen2.5-7B、Pythia 不同种子；任务：GLUE/SuperGLUE 子集、GSM8K、代码（HumanEval）LoRA；
- 指标：传输后零步精度、校准 k 步后精度 vs 从头重训 LoRA；对齐后插值势垒；
- 关键假设检验：传输增益是否随对称群丰富度（置换 < 正交 < 一般可逆）单调上升；势垒是否能预测传输成功；
- 消融：只对齐注意力 vs 只对齐 FFN、校准样本量、是否叠加 Trans-PEFT。

🔑 `PEFT` `LoRA transfer` `mode connectivity` `model alignment` `symmetry` `base model updates`

[🔝 top](#top)

---

## 💡 Idea 8.14 — *Merge-and-Verify Decoding: Bringing True Dynamic Tokenization to Autoregressive Generation via Speculative Subword Merging*

| | |
|:--|:--|
| 🎯 **源论文** | **Retrofitting Large Language Models with Dynamic Tokenization** · Feher et al. · 🏆 ACL 2025 SAC Highlights· [arXiv:2411.18553](https://arxiv.org/abs/2411.18553) |
| 📌 **线索来源** | Limitations §"our current dynamic tokenization approach is primarily designed for settings where the full sequence is known in advance (e.g., scoring and prefilling in decoder models)." + §"Closing this gap by integrating 'true' dynamic tokenization into autoregressive generation remains an open challenge for future research." |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
论文让已训练好的 LM 使用**动态分词**：在一个 batch 内按 BPE 风格合并高频子词序列得到新 token，并用预训练的嵌入预测超网络（hypernetwork）即时生成这些新 token 的嵌入；编码器上 14 种语言平均缩短 >20% 序列、精度损失 <2%，解码器的 prefill/评分同样有效。Limitation 明确：方法要求**整段序列已知**，自回归生成只给了一个"大而静态的有界词表"的折中方案，"真正的动态分词进入自回归生成"仍是开放问题。难点在于生成时要在一个随输入变化的输出词表上做 softmax：合并 token 的输出嵌入需要即时生成、候选集合不固定、而且生成分布不能偏离原模型。空隙没有被填补——SuperBPE 等工作通过**重训**更长的 token 来加速生成，而不是在现有模型上动态合并。关键 insight：一个合并 token w = s₁s₂…s_j 在原静态模型下的概率是 ∏ p(s_i | ·) 这一链式乘积，因此"提出合并 token、再用静态模型验证"恰好是**推测解码的结构**：小的边界/合并预测器扮演 drafter（提出把接下来的几个子词合并成一个动态 token），静态 LM 在并行验证中一次性对这些子词打分；接受后，前缀用动态 token 重新压缩进 KV 缓存。这样既保证输出分布与原模型一致（推测解码的无损性），又获得动态分词的序列压缩（更短的 KV、更少的解码步）。

**💡 一句话 Idea**
把动态分词做成推测解码：用轻量的合并预测器 + 超网络即时生成候选动态 token 的嵌入作为草稿，由静态 LM 并行验证其子词链式概率，接受后把该跨度压缩为单个动态 token 写入 KV 缓存，从而在不改变原模型输出分布的前提下，让自回归生成同时获得更少解码步与更短上下文。

**🛠️ 可能的解决方法**
1. **合并预测器（drafter）**：一个 ~50M 的字节/子词级模型，在当前前缀下预测"接下来 j 个子词构成一个高频合并跨度"的候选集合（top-m 个跨度，j ≤ 6），训练目标是最大化静态 LM 对这些跨度的接受率（与 EAGLE 式的 drafter 蒸馏相同）。
2. **验证**：静态 LM 对候选跨度的子词序列做一次并行前向，按推测解码的拒绝采样接受最长前缀；接受的跨度 w 被超网络映射为输入嵌入 e(w) 并替换 KV 缓存中对应 j 个子词的条目（用 e(w) 重新计算该位置的 K/V，一次前向，摊销于后续步）。
3. **输出侧一致性**：验证只用静态词表的 softmax，无需动态输出头，因此分布无损；超网络只负责输入嵌入——这规避了论文中"输出词表无界"的核心障碍。
4. **压缩与质量权衡**：KV 替换引入与 prefill 场景相同的微小失配（论文测得 <2%），可通过"只对被接受 ≥2 次的高频跨度做 KV 压缩"控制；提供无压缩（纯加速）与压缩（加速 + 省内存）两档。
5. **成本**：drafter 训练 ~2B token；在 Mistral-7B/Llama-3-8B 上实现，单卡即可评测。

**🧭 与最接近工作的区别**
- 推测解码 (Leviathan et al., 2023) / EAGLE (Li et al., 2024)：加速但不改变序列表示，KV 缓存仍按静态 token 增长；本 idea 的草稿单位是**动态合并 token**，接受后真正缩短上下文。
- SuperBPE (Liu et al., 2025) / 多 token 预测 (Gloeckle et al., 2024)：需要重新训练模型以使用更长 token 或多头；本 idea 是对已有模型的 retrofit。
- 本源论文的"大而静态词表"方案：词表固定、无法覆盖输入特异的合并；本 idea 的合并是输入自适应的。

**🧪 验证方案**
- 指标：每秒生成字节数、解码步数减少比例、KV 缓存长度减少比例、与原模型的输出分布 KL（应≈0 在无压缩档）、下游任务（MT-Bench、GSM8K、多语言 FLORES 生成）；
- 关键假设检验：合并跨度的接受率是否 >60%（否则无加速）；KV 压缩档的精度损失是否 <2%；
- 对比：标准推测解码（同 drafter 规模）、SuperBPE 重训模型、原模型；消融：j 上限、超网络 vs 平均嵌入、压缩阈值。

🔑 `dynamic tokenization` `speculative decoding` `hypernetwork` `KV cache` `inference efficiency` `multilingual`

[🔝 top](#top)

---

## 💡 Idea 8.15 — *Pruning Hypernetworks: Predicting Class-Specific Weight Compensation for Instant, Retraining-Free Derivation of Edge ViTs at Extreme Pruning Rates*

| | |
|:--|:--|
| 🎯 **源论文** | **NuWa: Deriving Lightweight Class-Specific Vision Transformers for Edge Devices** · Wei et al. · 🏆 CVPR 2026 Best Paper Candidate · [arXiv:2504.03118](https://arxiv.org/abs/2504.03118) |
| 📌 **线索来源** | Limitations and Future Works §"However, when the pruning rate exceeds 70%, noticeable accuracy degradation still occurs." + §"an offline-trained hypernetwork could be developed to predict weight updates, enabling the online derivation process to efficiently map task specifications, such as model architecture, sub-task, and pruning rate, to corresponding pruned weights." |
| ⭐ Novelty | ★★★☆☆ |
| 🚀 Impact | ★★★☆☆ |
| 🧗 Difficulty | ★★☆☆☆ |

**🔍 深入分析**
NuWa 针对"边缘设备只需要部分类别"的现实，发现基座 ViT 中存在**类别有害权重**（删除后目标类精度反而上升），先用自知识净化（SKP）剪掉它们得到锚模型，再用闭式解求出结构化剪枝后的补偿权重，无需重训就能在 60% 剪枝率下超过基座，并把大规模定制化部署的成本降到极低。Limitation 清楚：剪枝率 >70% 或子任务类别数 >50 时精度仍明显下降；作者提出两条路——轻量重训，或训练一个离线超网络把任务规格（架构、类别子集、剪枝率）直接映射为剪枝后的权重。空隙在于：现有超网络式剪枝（DHP、Once-for-All）要么预测的是整套权重（规模随基座增长、难以泛化到未见任务），要么需要一次昂贵的"超网训练"且不按类别子集条件化；而 NuWa 的闭式解提供了一个关键的新前提——对任意任务规格都能便宜地生成"近似正确"的目标权重，这使得超网络只需学习**残差补偿**（从闭式解到轻量重训结果的差），而残差是低秩、小幅度的，远比整套权重好学。关键 insight：把"剪枝 + 补偿"看作一个以类别子集为条件的元学习问题，训练数据可以由 NuWa 自身无限生成。

**💡 一句话 Idea**
训练一个以类别子集嵌入、剪枝率与层索引为条件的低秩补偿超网络，用 NuWa 闭式解作为基线、轻量重训结果作为监督，学习预测"闭式解到重训解"的残差更新，使 70%+ 剪枝率或大子任务下的类别专用 ViT 也能在秒级、零重训地在线派生。

**🛠️ 可能的解决方法**
1. **训练数据自生成**：从 ImageNet-1k 等随机采样子任务 S（|S| ∈ [5, 100]）与剪枝率 ρ ∈ [0.5, 0.85]，对每个 (S, ρ) 跑 NuWa 得到 W_closed，再做 500 步轻量重训得到 W_ft；目标残差 Δ = W_ft − W_closed（经验上低秩，用秩 16 的 SVD 截断存储）。
2. **超网络**：输入 = 类别子集的集合编码（对类别原型做 DeepSets/attention pooling）⊕ ρ ⊕ 层/模块 ID，输出每个线性层的低秩因子 (U, V)（秩 16）；与 NuWa 的锚模型共享骨干特征以感知"类别有害权重"的位置。
3. **目标函数**：‖UVᵀ − Δ‖_F + λ·KL(f_{W_closed+UVᵀ}(x) ‖ f_{W_ft}(x))（在少量校准图上做功能蒸馏），后者比纯权重回归更稳定。
4. **泛化与在线派生**：对未见过的子任务与剪枝率，派生只需一次 NuWa 闭式解 + 一次超网络前向（毫秒级）；可选地加 50 步在线校准作为上界对照。
5. **成本**：训练数据生成约 2k 个 (S, ρ) 组合，单 8 卡机两天；推理时无额外开销。

**🧭 与最接近工作的区别**
- Once-for-All (Cai et al., 2020)：一次训练超网再抽取子网，需要昂贵的渐进收缩训练，且不按类别子集条件化。
- DHP (Li et al., 2020)：超网络生成剪枝后权重以实现可微剪枝，面向单任务；本 idea 以任务规格为条件、只学残差，并以 NuWa 闭式解为锚。
- NuWa 本身：无重训的闭式补偿；本 idea 在其上加一层学习到的补偿以突破 70% 剪枝率。

**🧪 验证方案**
- 基准：NuWa 的四个数据集（ImageNet 子集、CIFAR-100、Food-101 等）与六个 ViT（DeiT/ViT 各规模）；剪枝率 70%–85%、|S| 5–100；
- 指标：目标类精度、派生时间、Jetson Orin NX 上的吞吐；
- 关键假设检验：残差 Δ 的有效秩是否 ≤ 16；超网络对未见 (S, ρ) 的精度是否接近轻量重训的 90% 以上；
- 对比：NuWa、NuWa + 轻量重训（上界）、Numerical Pruning、Wanda-sp；消融：集合编码方式、功能蒸馏项、秩。

🔑 `structured pruning` `hypernetwork` `vision transformer` `edge deployment` `class-specific models` `low-rank`

[🔝 top](#top)

---

## 💡 Idea 8.16 — *Lookahead Deferral: Learning Sequence-Level Deferral Policies for Speculative Cascades Beyond Local, Calibration-Dependent Rules*

| | |
|:--|:--|
| 🎯 **源论文** | **Faster Cascades via Speculative Decoding** · Narasimhan et al. (Google) · 🎤 ICLR 2025 Oral · [arXiv:2405.19261](https://arxiv.org/abs/2405.19261) |
| 📌 **线索来源** | Appendix F Limitations §"the optimization objectives we seek to minimize are local objectives that seek to make the best deferral decision at the current position t. In doing so, they ignore the downstream effects of choosing a particular model in the current step." + Conclusions §"we wish to replace our plug-in estimators with a router model ... and to extend our proposal to more than two models." |
| ⭐ Novelty | ★★★☆☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★☆☆☆ |

**🔍 深入分析**
论文把级联（只在"难"输入上调用大模型、常常能超过大模型）与推测解码（并行验证、质量中性）结合：用推测执行实现级联的延迟规则，并推导出在 token 级的最优延迟规则，得到比两者都好的成本—质量曲线。Limitation 指出两处根本局限：(1) 延迟规则依赖插件估计（小模型与大模型的概率），要求模型**校准良好**；(2) 目标是**局部的**——只在当前位置 t 做最优决策，忽略了"现在选哪个模型"对后续 token 的影响（例如小模型的一个错误会把后续生成带偏，而局部规则不会为此提前延迟）；此外只支持两个模型。空隙：虽然 RouteLLM 等做查询级路由、Gupta et al. (2024) 用 token 级不确定性做级联，但没有人把 token 级延迟建模为**序列决策问题**并用后续质量作为回报来训练——而推测级联恰好提供了便宜的 rollout（草稿已经并行生成，大模型的验证分数是免费的信号）。关键 insight：延迟决策的下游效应可以用"小模型草稿在未来 k 个 token 上被大模型拒绝的比例"来廉价估计——这正是推测执行已经计算出来的量，因此可以用它构造带前瞻的回报，训练一个不依赖校准的轻量路由器，并自然推广到多模型（每个候选模型一个动作）。

**💡 一句话 Idea**
把推测级联的延迟规则改为一个用强化学习训练的序列级路由策略：以小模型隐状态与草稿为输入、以"质量 − λ·成本"的序列回报（利用推测验证的拒绝信号作为免费的前瞻估计）为目标，学会为下游错误提前延迟，并推广到两个以上模型的级联。

**🛠️ 可能的解决方法**
1. **状态与动作**：状态 = 小模型在位置 t 的最后一层隐状态 ⊕ 草稿窗口的 token 熵与 top-2 边际 ⊕ 最近 k 步的拒绝历史；动作 ∈ {接受草稿, 延迟到模型 2, …, 延迟到模型 M}；路由器为 2 层 MLP（<1M 参数）。
2. **回报**：r_t = −λ·cost(a_t) + 前瞻项：对接受动作，用推测验证在未来 w 个 token 上的拒绝比例的负值（免费获得）；序列末尾加任务奖励（正确性 / 参考答案相似度 / 奖励模型分）。用 GRPO 或 off-policy 的优势加权回归训练，样本来自离线记录的推测级联轨迹。
3. **校准无关性**：路由器输入不含大模型概率，只在训练时用大模型验证作为信号，推理时对未校准模型仍适用。
4. **多模型扩展**：动作空间含 M 个模型，草稿由最小模型生成，验证按动作选定的模型做；回报中的成本按各模型 FLOPs 计。
5. **成本**：Gemma/T5 系列（论文设定）或 Qwen 0.5B/1.5B/7B；离线轨迹 ~100k 条，单卡训练路由器数小时。

**🧭 与最接近工作的区别**
- 本源论文：局部最优延迟规则 + 插件估计；本 idea 用序列回报 + 学习路由器，并支持多模型。
- Gupta et al. (2024) "Language Model Cascades: Token-level Uncertainty and Beyond"：token 级不确定性特征训练延迟器，仍是逐位置、不考虑下游影响。
- RouteLLM (Ong et al., 2024) / Hybrid LLM (Ding et al., 2024)：查询级一次性路由；本 idea 在 token 级逐步决策且利用推测执行的信号。

**🧪 验证方案**
- 基准：WMT 翻译、XSum 摘要、GSM8K、MMLU 生成式设定；
- 指标：质量—成本曲线（曲线下面积）、延迟率、相对大模型的吞吐；
- 关键假设检验：带前瞻回报的路由器在同成本下质量是否高于局部最优规则；在故意去校准（温度扰动）的模型上局部规则退化而学习路由器稳定；
- 消融：前瞻窗口 w、是否使用拒绝历史、模型数 M=2 vs 3。

🔑 `model cascades` `speculative decoding` `routing` `reinforcement learning` `inference cost` `deferral`

[🔝 top](#top)

---

## 💡 Idea 8.17 — *Decay-Audited Hybridization: Using Token-Interaction Decomposition to Diagnose and Repair Mamba's Recall Decay, Layer by Layer*

| | |
|:--|:--|
| 🎯 **源论文** | **LaTIM: Measuring Latent Token-to-Token Interactions in Mamba Models** · Pitorro & Treviso · 🏆 ACL 2025 Outstanding Paper· [arXiv:2502.15612](https://arxiv.org/abs/2502.15612) ＋ **Mamba Knockout for Unraveling Factual Information Flow** · Endy et al. · 🏆 ACL 2025 SAC Highlights· [arXiv:2505.24244](https://arxiv.org/abs/2505.24244) |
| 📌 **线索来源** | LaTIM · Conclusion §"our findings suggest that Mamba's recall limitations in long-context tasks may stem from its sparse and decaying focus on relevant tokens." + Limitations §"while LaTIM helps visualize token interactions, its impact on improving model robustness and trustworthiness remains an open question." ；Mamba Knockout · Limitations §"Future works should attempt to explain the inductive-biases of the different architectures that drive these differences in information flow." |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★☆☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
LaTIM 为 Mamba-1/2 给出 token 级的交互分解（类似注意力图），在复制、翻译与检索式生成上揭示 Mamba 的选择性处理模式，并得出一个机制性结论：Mamba 的长上下文召回缺陷来自它对相关 token 的**稀疏且随距离衰减的关注**。Mamba Knockout 用注意力敲除的思路追踪事实信息流，发现 SSM 与 Transformer 在"主语→末 token"的信息传递上既有共性也有架构特异的差异，并呼吁解释驱动这些差异的归纳偏置。两篇的 Limitation 共同指出：解释工具已经有了，但**把解释变成改进**仍是空白——LaTIM 直言其对鲁棒性的影响"仍是开放问题"。与此同时，混合模型（Jamba、MambaInLlama、Hymba）在决定"哪些层用注意力"时完全不看 SSM 层内部的信息流，只凭总体困惑度；而 LaTIM 恰好能逐层量化"相关 token 的贡献随距离衰减了多少"。关键 insight：召回衰减是一个**可逐层测量、可逐层归因**的量——衰减最严重的层就是最值得替换为注意力（或增加状态维度 / 修改衰减参数化）的层；更进一步，分解出的交互可以直接作为训练信号，在不改架构的前提下惩罚对相关 token 的过度衰减。

**💡 一句话 Idea**
把 LaTIM 的 token 交互分解变成一个逐层"召回衰减审计"，用它 (a) 决定混合模型中哪些 Mamba 层应替换为注意力或扩大状态，(b) 作为训练时的正则项惩罚对已知相关 token 的贡献衰减，从而以可解释的方式修复 SSM 的长上下文召回，并解释不同架构信息流差异的来源。

**🛠️ 可能的解决方法**
1. **衰减审计指标**：在带标注相关 token 的任务（MQAR、Needle、事实召回的主语 token）上，对每层 ℓ 计算 LaTIM 分解的相关 token 贡献 c_ℓ(d) 随距离 d 的衰减曲线，拟合衰减率 κ_ℓ；同时用 Mamba Knockout 的敲除验证 κ_ℓ 高的层确实是召回失败的因果位置。
2. **审计驱动的混合化**：对预训练 Mamba（如 Mamba-2 1.3B/2.7B），按 κ_ℓ 排序，把 top-k 层替换为注意力层并蒸馏（MambaInLlama 式），与"均匀间隔替换"和"随机替换"对比；同样可选择性扩大这些层的状态维度或把衰减参数 A 的范围放宽。
3. **交互正则**：训练/微调时加入 L_recall = Σ_ℓ max(0, κ_ℓ − κ_max)（需要 LaTIM 的可微版本——论文的"exact"变体通过去掉 SiLU 非线性实现），或更简单地在合成检索数据上最大化相关 token 的分解贡献占比。
4. **归纳偏置解释**：比较 Transformer 与 Mamba 在相同事实任务上的逐层信息流（LaTIM 图 vs 注意力图），把差异归因到衰减参数化（指数衰减 vs 无衰减）这一具体机制，回应 Mamba Knockout 的开放问题。
5. **成本**：审计只需前向；混合化蒸馏 ~10B token，8 卡数天。

**🧭 与最接近工作的区别**
- MambaInLlama (Wang et al., 2024) / Jamba (2024) / Hymba (2024)：注意力层位置按固定间隔或经验选择；本 idea 用逐层可解释的召回衰减指标来选。
- Zoology / Based (Arora et al., 2024)：从合成任务与理论刻画 recall–效率权衡并提出新层；本 idea 诊断**现有**模型的具体层并做靶向修复。
- LaTIM / Mamba Knockout 本身：只做解释；本 idea 把解释闭环到架构决策与训练目标。

**🧪 验证方案**
- 基准：MQAR、Needle-in-a-Haystack、RULER、SWDE/FDA 检索、CounterFact 事实召回；困惑度（The Pile）；
- 关键假设检验：κ_ℓ 与敲除造成的召回损失是否显著相关；按 κ_ℓ 选层的混合模型是否在同样注意力层数下优于均匀/随机选层；交互正则是否降低 κ_ℓ 并提升召回而不伤困惑度；
- 消融：替换层数 k、扩状态 vs 换注意力、正则强度。

🔑 `Mamba` `interpretability` `hybrid models` `associative recall` `information flow` `state space models`

[🔝 top](#top)

---

## 💡 Idea 8.18 — *Complexity-Matched Pre-pretraining: Choosing Formal Languages by Architecture Circuit Class and Mixing Schedule for Transformers, SSMs and Hybrids*

| | |
|:--|:--|
| 🎯 **源论文** | **Between Circuits and Chomsky: Pre-pretraining on Formal Languages Imparts Linguistic Biases** · Hu et al. · 🏆 ACL 2025 Outstanding Paper· [arXiv:2502.19249](https://arxiv.org/abs/2502.19249) |
| 📌 **线索来源** | Limitations §"it is possible that the optimal training regimen involves mixing formal and natural language during training" + §"our work only considers transformers. Circuit complexity has also quantified the expressive power of neural networks like RNNs and state-space models ... and it would be interesting to extend our results to these architectures." |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
论文提出并部分验证了一个假设：形式语言"预预训练"有效的条件是 (1) 语言具有自然语言式的层级依赖，(2) 语言落在架构的计算能力内（对 Transformer 即 C-RASP 可表达）。k-Shuffle Dyck 效果最好，复制语言 ww（有交叉依赖但非层级、也不在 C-RASP 内）反而有害，而且好的形式语言比等量的额外自然语言数据更有用。Limitation 列出三点：只做了先形式后自然的"块状"训练，混合可能更优；只研究 Transformer，而 RNN/SSM 的电路复杂度刻画已经存在；缺少 scaling law。这打开了一个精确的问题：**如果有效语言必须落在架构能力边界内，那么不同架构应该用不同的形式语言**——线性 RNN/SSM 能表达的是（带负特征值时的）正则/状态追踪类语言而非 Dyck 式的层级计数，Transformer 相反；混合模型两者兼有。现有的合成预训练工作（Papadimitriou & Jurafsky 的结构提示、算法数据混入）都把数据当作架构无关的，从未检验"架构—语言匹配"。关键 insight：这一假设可以被证伪——若 SSM 从 Dyck 获益与 Transformer 一样多，则"落在能力内"的条件就不成立；若匹配假设成立，则预预训练成为一种廉价地**补足架构归纳偏置**（而非替代架构）的手段，混合模型还能用它来引导各层分工。

**💡 一句话 Idea**
系统检验"有效的形式语言必须落在架构计算能力内"这一假设：为 Transformer、线性 RNN/SSM 与混合模型分别用层级（Dyck 类）、状态追踪（正则/群词类）与两者组合的形式语言做预预训练，并比较块状 vs 混合衰减日程，以得到架构匹配的预预训练配方与其 scaling law。

**🛠️ 可能的解决方法**
1. **语言族设计**：三类——层级类（k-Dyck、k-Shuffle Dyck，C-RASP 内）、状态追踪类（奇偶性、模 m 计数、S_3/S_5 群词问题的字符串形式，正则但非 TC⁰ 友好）、交叉类（ww 复制、交错依赖）；每类控制词表、长度与熵，使 token 数可比。
2. **架构族**：Transformer 160M/1B（复现论文）、Mamba-2 与带负特征值的 DeltaNet（同参数量）、1:7 混合模型；每种架构 × 每种语言做预预训练后转自然语言训练。
3. **日程**：块状（先形式后自然）、恒定混合（形式占 5%）、衰减混合（从 30% 线性降到 0）；比较自然语言损失、BLiMP 语言学泛化、以及与语言族对应的能力测试（长程括号匹配、代码执行追踪、长度泛化）。
4. **Scaling law**：固定架构，扫描预预训练 token 数（10M–2B）与模型规模，拟合"预预训练收益 vs 规模"的函数形式，检验收益是否随规模消失（论文"1B 以上未知"）。
5. **成本**：160M 级全因子（3 架构 × 4 语言 × 3 日程），1B 级只跑最优配置；8×H100 数周。

**🧭 与最接近工作的区别**
- 本源论文：只有 Transformer + 块状日程；本 idea 加入架构维度与日程维度，并把"落在能力内"假设变成可证伪的交叉实验。
- Papadimitriou & Jurafsky (2020, 2023) "structural hints"：用音乐/代码/合成结构做预训练迁移，不区分架构；本 idea 以电路复杂度为依据配对语言与架构。
- Idea 8.3（本仓库）：面向 Transformer 的简洁性—可学习性缺口课程；本 idea 关注架构间差异与混合日程，两者互补。

**🧪 验证方案**
- 指标：自然语言困惑度、BLiMP、长度泛化、状态追踪与括号匹配的下游任务；
- 关键假设检验：Dyck 对 Transformer 的增益 > 对 SSM 的增益，状态追踪语言对（负特征值）SSM 的增益 > 对 Transformer 的增益；混合模型在组合语言上最优；衰减混合是否优于块状；
- 对比：等量额外自然语言数据、随机字符串、无预预训练；消融：语言熵、长度分布、形式语言比例。

🔑 `formal languages` `pre-pretraining` `inductive bias` `state space models` `circuit complexity` `curriculum`

[🔝 top](#top)
