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
