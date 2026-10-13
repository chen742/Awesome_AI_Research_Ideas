<a id="top"></a>
# 🌊 Diffusion & Generative Models (incl. Diffusion LLMs)

> 从扩散语言模型的生成顺序、扩散模型泛化机理、视觉自回归 等获奖论文中提炼的 idea。
> 符号说明：🎯 源论文 · 📌 线索来源 · ⭐ Novelty · 🚀 Impact · 🧗 Difficulty · 🧪 验证方案 · 🔑 关键词

[⬅️ 返回主页](../README.md)

---

## 💡 Idea 3.1 — *Order as a Policy: Learning Where to Unmask in Diffusion Language Models under Constrained Order Families*

| | |
|:--|:--|
| 🎯 **源论文** | **The Flexibility Trap: Rethinking the Value of Arbitrary Order in Diffusion Language Models** · Ni et al. · 🏆 ICML 2026 Outstanding Paper ＋ **Train for the Worst, Plan for the Best: Understanding Token Ordering in Masked Diffusions** · Kim et al. · 🏆 ICML 2025 Outstanding Paper · [arXiv:2502.06768](https://arxiv.org/abs/2502.06768) |
| 📌 **线索来源** | Flexibility Trap §"任意顺序的训练负担与其收益不匹配"；Train-for-the-Worst §"adaptive inference-time ordering closes the train/test gap" + Future Work §"learned orderings" |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
两篇论文从相反方向指向同一结论。Kim 等证明：掩码扩散模型（MDM）在训练时被迫学习**所有**随机顺序下的条件分布，其中很多（如先填中间再填两边）是极难的子问题，这是 MDM 似然落后于 AR 的根因；但在推理时可以**自适应选择**最容易的位置先解码，从而在 Sudoku 等逻辑任务上从 <7% 提到 ~90%。Ni 等（Flexibility Trap）则系统质疑"任意顺序"的价值：大部分收益来自并行解码而非顺序自由，灵活性反而成为训练效率的陷阱。合起来的 insight：**顺序应当既不是"任意"也不是"固定"，而是一个受约束的、可学习的策略**；训练只在一个小的顺序族上做（减轻 worst-case 负担），推理在该族内学习如何选位置（保留 plan-for-the-best 的收益）。现有 dLLM（LLaDA、Dream、MMaDA）使用的置信度/熵启发式是手工规则，没有被当作可优化对象。

**💡 一句话 Idea**
把"下一步解码哪些位置"建模为一个轻量级策略头，用执行反馈的 RL 在受限顺序族（块级半自回归 + 块内自由）内学习解码顺序，同时让训练的顺序分布与推理策略对齐，消除 train/test 顺序失配。

**🛠️ 可能的解决方法**
1. **受限顺序族**：采用块级半自回归（块间从左到右，块内任意），块长 B 为超参；训练时仅对块内位置随机掩码，使模型只需学习 O(B) 规模的顺序子问题。
2. **顺序策略头**：在主干最后一层加一个小的逐位置打分头 g_θ(h_i)，每步在当前块内按 g 选取 top-m 位置解码（m 可自适应：以 g 的归一化分数阈值决定并行度）；策略头与主干共享特征，几乎不增加成本。
3. **执行反馈 RL**：在可验证任务（数学、代码、Sudoku/逻辑谜题）上用结果奖励 + 步数惩罚训练策略头（REINFORCE / GRPO，主干冻结或低学习率联合训练），奖励鼓励"用更少步数得到正确答案"，从而自动学到"先易后难、先约束强的位置"。
4. **训练分布对齐**：把策略头产生的顺序回灌为训练时的掩码调度（self-play 式的 order distillation），进一步缩小 worst-case 训练负担。

**🧪 验证方案**
- 逻辑任务：Sudoku、Zebra puzzles（复现 Kim 等的设置）；代码/数学：HumanEval、GSM8K、MATH；
- 指标：准确率、解码步数（吞吐）、与置信度/熵启发式、固定从左到右、完全任意顺序的对比；
- 消融：块长 B、策略头是否训练、是否做顺序回灌。

🔑 `diffusion LLM` `masked diffusion` `decoding order` `semi-autoregressive` `RL` `parallel decoding`

[🔝 top](#top)

---

## 💡 Idea 3.2 — *Twin-Denoiser Consistency: Turning the Memorization-to-Generalization Transition into a Training Objective*

| | |
|:--|:--|
| 🎯 **源论文** | **Generalization in Diffusion Models Arises from Geometry-Adaptive Harmonic Representations** · Kadkhodaie et al. · 🏆 ICLR 2024 Outstanding Paper · [arXiv:2310.02557](https://arxiv.org/abs/2310.02557) |
| 📌 **线索来源** | Finding §"two denoisers trained on disjoint subsets converge to the same density when data is sufficient" + Limitation §"analysis limited to small UNets; transition not controllable" |
| ⭐ Novelty | ★★★★★ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★☆☆☆ |

**🔍 深入分析**
论文最惊人的实验：把数据集拆成两个不相交子集分别训练去噪器，当每个子集足够大（~10⁵ 张）时两个模型对同一噪声输入生成**几乎像素级相同**的图像——说明它们收敛到同一个"真实密度"的估计而非记忆训练集；数据少时则各自记忆、输出完全不同。作者把这归因于网络的归纳偏置（几何自适应谐波基）。Limitation 指出：该转变只是被观测、未被控制；也没有讨论如何在数据不足（如医学影像、私有数据）时主动推动模型进入泛化区。这里的 insight 非常直接：**"两个不相交子集上的模型是否一致"本身就是一个可计算的泛化判据**，而且它只依赖模型本身，不需要最近邻检索式的记忆检测。既然它是判据，就可以把它变成正则项。

**💡 一句话 Idea**
同时训练两个在不相交数据分片上学习的去噪器，并以它们对共享噪声输入的去噪输出的一致性为正则项，把扩散模型从"记忆相"主动推向"泛化相"，在小数据与版权敏感场景下显著降低训练样本复现。

**🛠️ 可能的解决方法**
1. **双子训练**：随机把数据集 D 分为 D₁、D₂，训练 ε_θ₁、ε_θ₂（可共享大部分参数，仅分片特定的 LoRA/归一化层不同，以控制成本）。
2. **一致性正则**：在每个 batch 额外采样与数据无关的噪声输入 x_t（来自高斯先验或两分片之外的生成样本），加入损失 λ(t)·‖ε_θ₁(x_t,t) − ε_θ₂(x_t,t)‖²；λ(t) 在中高噪声水平更大（论文指出记忆主要发生在低噪声段，但泛化基在中段形成）。
3. **理论动机**：若两模型分别记忆各自分片，则在对方分片附近的去噪输出必然分歧；一致性损失的最小化等价于把两者拉向 D₁∪D₂ 共同支撑的密度估计——可用论文的谐波基分析给出线性化情形下的证明。
4. **推理**：用两模型平均或任一即可；可额外提供"分歧图"作为逐像素记忆风险的在线指示器。

**🧪 验证方案**
- CelebA/LSUN 子集（10²–10⁵ 张）上的记忆率（最近邻 SSCD 距离）、FID、以及双模型一致性随数据量的相变曲线；
- 文生图微调场景（DreamBooth 规模）复现率；
- 对比 dedup、ambient diffusion、anti-memorization guidance。

🔑 `diffusion` `memorization` `generalization` `consistency regularization` `copyright` `inductive bias`

[🔝 top](#top)

---

## 💡 Idea 3.3 — *Entropy-Gated Next-Scale Prediction: Spatially Adaptive Refinement Budgets for Visual Autoregressive Models*

| | |
|:--|:--|
| 🎯 **源论文** | **Visual Autoregressive Modeling: Scalable Image Generation via Next-Scale Prediction** · Tian et al. · 🏆 NeurIPS 2024 Best Paper · [arXiv:2404.02905](https://arxiv.org/abs/2404.02905) |
| 📌 **线索来源** | Limitation §"fixed coarse-to-fine scale schedule shared by all images" + Future Work §"better tokenizer; video; text-to-image" |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
VAR 把"下一 token"改为"下一尺度"，使自回归图像生成首次在 ImageNet 上超过扩散 Transformer，并展示了清晰的 scaling law。但其尺度调度（1→2→…→16）是**全局固定**的：每张图、每个区域都要走完全部尺度，细尺度的 token 数量占总量的绝大部分（最后两级占 >60% 的 token）。对于大面积平坦区域（天空、墙面），粗尺度已足够，继续细化是算力浪费；而纹理密集区域又可能需要比 16×16 更细的尺度。Limitation 隐含地承认了这一点（"更好的 tokenizer"），但没有触碰调度本身。另一个相关现象：VAR 的训练是 teacher-forced 的，每个尺度的 token 熵分布极不均匀——这个熵恰好可以成为"是否还需要细化"的信号。

**💡 一句话 Idea**
让每个空间区域根据自身的预测熵决定何时停止细化：引入"熵门控"的空间自适应尺度调度，使 VAR 把算力集中在高频区域，实现 2–3× 的推理加速与同等或更高的质量。

**🛠️ 可能的解决方法**
1. **区域级停止准则**：在尺度 k 生成完成后，计算每个区域（对应下一尺度的 2×2 子块）的 logits 熵 H；若 H < τ_k，则该区域在后续尺度上被"冻结"：其细尺度 token 由上采样确定性填充（残差为零），不再进入注意力计算的 query 集合（但仍作为 key/value 存在以保证上下文完整）。
2. **训练对齐**：训练时以 teacher-forced 的残差能量（该区域在尺度 k+1 的量化残差范数）作为"是否值得细化"的标签，联合训练一个二分类门控头；推理用门控头而非纯熵，避免熵与残差不一致。
3. **可变的最大尺度**：对门控持续为"需要细化"的区域，允许超出原始最大尺度一级（局部 32×32），tokenizer 需用多尺度 VQ 支持此扩展。
4. **效率实现**：冻结区域的 query 丢弃可直接用变长注意力（FlashAttention varlen）实现，不需要稀疏注意力内核。

**🧪 验证方案**
- ImageNet 256/512：FID、IS、每张图的平均 token 数、延迟；
- 质量—算力曲线 vs. 原始 VAR、Infinity、HART；
- 可视化门控图与图像高频能量图的相关性。

🔑 `visual autoregressive` `next-scale prediction` `adaptive computation` `entropy gating` `efficient generation`

[🔝 top](#top)
