<a id="top"></a>
# 🧠 LLM Reasoning & RL Post-Training

> 从 RLVR / 多轮推理 / 创造性生成 等方向的获奖论文中提炼的 idea。
> 符号说明：🎯 源论文 · 📌 线索来源 · ⭐ Novelty · 🚀 Impact · 🧗 Difficulty · 🧪 验证方案 · 🔑 关键词

[⬅️ 返回主页](../README.md)

---

## 💡 Idea 1.1 — *Rescue-RL: Reclaiming the Reasoning Boundary Lost under RLVR via Base-Model Replay and Problem-Adaptive Trust Regions*

| | |
|:--|:--|
| 🎯 **源论文** | **Does Reinforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?** · Yue et al. · 🥈 NeurIPS 2025 Best Paper Runner-Up · [arXiv:2504.13837](https://arxiv.org/abs/2504.13837) |
| 📌 **线索来源** | Limitation §"RLVR narrows the reasoning boundary" + Future Work §"better RL paradigms to elicit capability beyond the base model" |
| 📮 **投稿建议** | 🧪 **ML** · ICLR / NeurIPS ＋ 🗣️ NLP · ACL |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★☆☆（需要大规模采样与 7B–32B 级训练） |

**🔍 深入分析**
论文的核心证据是 pass@k 曲线：k 很小时 RLVR 模型领先，k 增大到数百后 **基座模型反而覆盖更多问题**，RL 模型的可解问题集合是基座的子集。作者归因为现有 RL（GRPO/PPO）只是把概率质量"重新分配"到基座本就能采到的路径上，并伴随熵坍缩。Limitation 中作者承认：(i) 没有给出一种能真正**扩张**边界的训练范式；(ii) 蒸馏能扩张边界说明"外部信号"有效，但自举（self-improvement）路径未被探索；(iii) 实验只在数学/代码/视觉推理，训练算法单一。这里的空隙很明确：**边界损失是可以被定位的**——给定问题 x，若 base 在 k=256 时能解而 policy 在 k=8 时失败，就说明这是一个"被 RL 挤掉"的问题。现有方法没有利用这一可观测信号。

**💡 一句话 Idea**
把"RL 后丢失的可解问题"显式检测出来，用基座模型自身在高 k 下采到的正确轨迹作为 off-policy 正样本进行"救援"，并对这些问题施加朝向基座的逐题自适应信任域，使 RLVR 在提升 pass@1 的同时**不缩小、甚至扩大** pass@k 边界。

**🛠️ 可能的解决方法**
1. **边界探针（Boundary Probe）**：训练前对每个训练题用基座模型做一次大 k 采样（k=256，温度 1.0），缓存所有通过验证器的轨迹，得到逐题 "base coverage" 位图；训练中周期性用当前 policy 以小 k（k=8）评估，得到 "policy coverage"。差集 B⁻ = {x : base 能解, policy 不能解} 即"丢失集"。
2. **自源 off-policy 救援（Self-Sourced Rescue）**：对 B⁻ 中的题，从缓存里取基座的正确轨迹作为 off-policy 正样本并入 GRPO 组，优势按 importance ratio 截断加权（类似 LUFFY 的 mixed-policy 做法，但样本来自**同一模型的基座版本**而非外部教师，因此不引入新知识、只找回失去的覆盖）。
3. **逐题自适应信任域**：KL(π‖π_base) 的系数 β_x 随 x 是否落在 B⁻ 动态调整——丢失题上加大 β，把策略拉回基座的高熵区域；已稳定解出的题上减小 β，允许充分 exploit。
4. **分叉 token 熵保持**：仅在高熵"分叉 token"（Wang et al., 2025 的 80/20 观察）上施加熵正则，避免整体熵坍缩的同时不干扰确定性 token。
整个算法仅比标准 GRPO 多一次离线大 k 采样和一个位图维护，工程代价可控。

**🧪 验证方案**
- 指标：pass@k 曲线（k 到 1024）、"覆盖率"（至少一次解出的题占比）、AIME24/25、LiveCodeBench、MATH-500；对比 GRPO、DAPO、Pass@k-training、LUFFY。
- 关键假设检验：训练结束时 policy 的 pass@256 ≥ base 的 pass@256（边界不缩小），且丢失集 |B⁻| 单调下降。
- 消融：去掉救援 / 去掉自适应 β / 救援样本来自外部教师 vs 自源。

🔑 `RLVR` `pass@k` `exploration` `off-policy` `trust region` `reasoning boundary`

[🔝 top](#top)

---

## 💡 Idea 1.2 — *Don't Commit Early: Specification-Ledger Reinforcement Learning for Recoverable Multi-Turn Reasoning*

| | |
|:--|:--|
| 🎯 **源论文** | **LLMs Get Lost In Multi-Turn Conversation** · Laban et al. · 🏆 ICLR 2026 Outstanding Paper · [arXiv:2505.06120](https://arxiv.org/abs/2505.06120) |
| 📌 **线索来源** | Limitation §"simulation of sharded instructions" + Discussion §"models make premature assumptions and cannot recover" |
| 📮 **投稿建议** | 🧪 **ML** · ICLR / NeurIPS ＋ 🗣️ NLP · EMNLP |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
论文把单轮指令切成多轮"碎片"（sharded）逐步给出，发现 15 个顶级模型平均性能下降 39%，且 **可靠性（best-case 与 worst-case 的差距）** 恶化比平均能力更严重。作者定位了四个机制：过早尝试给出完整解、对缺失信息做假设、回答越写越长（bloat）、以及**无法从早期错误假设中恢复**（后续轮次只是在初稿上打补丁）。Limitation 指出：实验是分析性的，没有给出训练解法；温度降到 0 也救不了；"lost" 的根因是模型一旦在上下文里写下了某个假设，后续生成就会锚定到它。这里的 insight 是：问题不在于"知道多少"，而在于模型**没有显式维护"已知/未知/已假设"的状态**，也没有被训练过"撤回"行为。现有多轮 RL 工作（如澄清问题、CollabLLM）优化的是轮次级奖励，不直接奖励"状态一致"与"可恢复性"。

**💡 一句话 Idea**
让模型在每一轮前先维护一个结构化的**规格账本（Specification Ledger：已确认 / 未知 / 临时假设）**，并用 RL 直接奖励"账本与已揭示碎片一致"和"假设被证伪时的正确撤回"，从而把多轮退化从 39% 压缩到个位数。

**🛠️ 可能的解决方法**
1. **数据与环境**：复用论文的 sharded 生成流程，但把碎片揭示顺序**随机化且加入冲突碎片**（后一碎片推翻前一假设），形成一个可自动验证的多轮环境；每题带有 gold 规格集合 S*。
2. **账本格式**：模型在每轮输出前生成一个隐式 scratchpad `<ledger>` 区块，包含三类条目 (confirmed / unknown / assumed) 及其来源轮次；最终答案只允许基于 confirmed 条目或被明确标注的 assumed 条目。
3. **奖励设计（可自动计算）**：(a) 账本精确率/召回率 vs. 当前已揭示的 S* 子集；(b) **过早承诺惩罚**：当 unknown 非空而模型给出"最终解"时扣分；(c) **撤回奖励**：当新碎片与某 assumed 条目冲突时，若下一轮账本正确删除/修正该条目则加分，否则重罚；(d) 终局任务正确性 + 长度惩罚抑制 bloat。
4. **训练**：多轮 GRPO，组内样本共享同一碎片序列；用轮次级奖励做 turn-level credit assignment，并在 rollout 中让用户模拟器（固定 LLM）严格按碎片脚本行事以保证可复现。
5. 推理阶段账本可隐藏，不影响用户体验。

**🧪 验证方案**
- 论文原始 6 类任务（code/数据库/数学/API/摘要/文档）的 sharded 设置，对比 full-vs-sharded 退化幅度与 unreliability；
- 新增"冲突碎片"子集专门测恢复；
- 迁移测试：τ-bench、MultiChallenge；检查单轮性能不下降。

🔑 `multi-turn` `underspecification` `belief state` `RL` `clarification` `recoverability`

[🔝 top](#top)

---

## 💡 Idea 1.3 — *Seed-Conditioned Group Policy Optimization: Learning to Be Diverse Without Raising Temperature*

| | |
|:--|:--|
| 🎯 **源论文** | **Roll the Dice & Look Before You Leap: Going Beyond the Creative Limits of Next-Token Prediction** · Nagarajan et al. · 🏆 ICML 2025 Outstanding Paper · [arXiv:2504.15266](https://arxiv.org/abs/2504.15266) ＋ **Artificial Hivemind: The Open-Ended Homogeneity of Language Models** · Jiang et al. · 🏆 NeurIPS 2025 Best Paper |
| 📌 **线索来源** | Future Work §"scale seed-conditioning to real LLMs and combine with RL"；Hivemind §"RLHF 加剧 intra-model mode collapse" |
| 📮 **投稿建议** | 🧪 **ML** · ICML / NeurIPS ＋ 🗣️ NLP · ACL |
| ⭐ Novelty | ★★★★★ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
Nagarajan 等在精心设计的算法任务上证明：next-token prediction 在需要"先全局规划再落笔"的创造性任务上天然短视，而**在输入端注入噪声（seed-conditioning）** 比提高温度更能产生多样且正确的输出，因为温度在输出端注入噪声会破坏连贯性。Future Work 明确写到：要在真实 LLM 上验证，并与 RL 结合。另一方面 Artificial Hivemind（Infinity-Chat，26K 开放式提示、25 位标注者/条）发现：不同模型给出高度相似的回答，且**RLHF 后的模型 intra-model 多样性进一步坍缩**，奖励模型倾向于给"典型"回答高分。两篇论文合起来指出一个同一根因：训练目标是逐样本、逐 token 的，没有任何项奖励"一组样本之间的差异"。而 GRPO 这类算法天然在同一提示下采样一个 group，却只用 group 做基线，从未把 group 的多样性当作目标。

**💡 一句话 Idea**
在 LLM 输入端加入可学习的随机种子 token，并用 **组级（set-level）多样性—质量联合奖励** 做策略优化，让模型学会"换种子就换思路"，从源头解决 Hivemind 式同质化，而不是靠温度牺牲连贯性。

**🛠️ 可能的解决方法**
1. **种子注入**：在 prompt 前插入 m 个 seed token，其 embedding 由 z∼N(0,I) 经一个小 MLP 映射；训练与推理时每个样本独立采样 z，解码采用低温/贪心。
2. **组级奖励**：对同一提示采样 N 个种子得到 N 个回答，奖励 = Σ_i q(y_i) + λ·logdet(K)，其中 q 是任务质量（验证器或 RM），K 是回答之间的核矩阵（基于嵌入或 n-gram Jaccard）；logdet 即 DPP 体积，奖励"彼此不同且都好"的组。为了把组级奖励分配到个体，用 leave-one-out 边际贡献 r_i = R(Y) − R(Y∖{y_i})，天然兼容 GRPO 的组内归一化。
3. **防止"伪多样"**：核矩阵使用语义嵌入 + 答案等价类（数学题用最终答案聚类，开放题用 LLM 判定"是否同一思路"），避免模型靠措辞换皮刷分。
4. **两阶段**：先在算法/组合任务（论文的 sibling discovery、triangle discovery 等）上验证"边界扩张"，再在 Infinity-Chat 开放式提示上做 pluralistic 评测。

**🧪 验证方案**
- 算法任务：distinct-and-correct 输出数 vs. 温度采样基线；
- 开放式：Infinity-Chat 的 inter/intra-model 相似度、人类标注者"至少一人最喜欢"的覆盖率；
- 推理任务：pass@k 是否随 k 增长更快（与 Idea 1.1 互补）。

🔑 `seed conditioning` `diversity` `DPP reward` `mode collapse` `GRPO` `creativity`

[🔝 top](#top)

---

## 💡 Idea 1.4 — *Load-Bearing Steps: Aligning Verbalized Importance with Parametric Faithfulness via Amortized Unlearning Rewards*

| | |
|:--|:--|
| 🎯 **源论文** | **Measuring Chain of Thought Faithfulness by Unlearning Reasoning Steps** · Tutek et al. · 🏆 EMNLP 2025 Outstanding Paper· [arXiv:2502.14829](https://arxiv.org/abs/2502.14829) |
| 📌 **线索来源** | Limitations §"By eliminating the contextual confounder, we limit ourselves to studying cases in which the CoT and no-CoT predictions of the models agree" + 7 Discussion and Future Outlook §"(1) fully fine-tuning all second feed-forward layers of the model involves updating a large number of parameters, and (2) intervening on each CoT step can be time-consuming." + 8 Conclusion §"CoT steps identified as highly relevant are not considered plausible by humans, higlighting the need for specialized alignment." |
| 📮 **投稿建议** | 🗣️ **NLP** · ACL / EMNLP ＋ 🧪 ML · ICLR |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆（需对 7B–14B 模型做可微反学习探针，训练循环中多一次反传） |

**🔍 深入分析**
FUR 的核心思想是把"忠实性"从上下文层面搬到参数层面：对某个推理步做机器反学习（只更新第二层 FFN），若模型预测随之翻转，说明该步在参数内部确实被用到了。论文给出两类指标（ff-hard / ff-soft），并发现一个令人不安的结论——**被参数认定为最关键的步骤，人类往往认为并不合理**。Limitation 明确指出三件事：(i) 只能分析 CoT 与 no-CoT 预测一致的样本；(ii) 对长推理模型逐步反学习代价过高；(iii) 需要参数访问。真正的空隙是：FUR 只是**测量工具**，而现有忠实性训练（FRODO 等）用的是上下文反事实信号——正是 FUR 要规避的 confounder；没有工作把"参数级 load-bearing"当训练信号，也没人让模型**自己声明**关键步并与参数事实对齐。关键 insight：ff-soft 的本质是"反学习后答案分布的位移"，它可以用一次受限 LoRA 梯度上升近似，把每步数小时的反学习摊销为一次前向反传，从而进入 RL 循环。

**💡 一句话 Idea**
用"单步 LoRA 反学习探针"把 FUR 摊销成可在线计算的步骤级参数重要性，训练推理模型使其**自报的关键步骤 = 参数上真正承重的步骤**，并同时约束这些步骤对人类可信，从而把 CoT 忠实性从事后测量变成可优化目标。

**🛠️ 可能的解决方法**
1. **摊销探针（Amortized FUR）**：把长 CoT 切成 10–30 个语义段；对每段 s_j，在仅挂于 FFN₂ 的 LoRA 上做 1–2 步 NPO/梯度上升（目标是降低该段 token 的似然），测答案分布位移 δ_j = JS(p_before ‖ p_after)。每段只需一次反传，LoRA 复位即可恢复，整条轨迹成本约等于 2 倍常规反传。先在论文的 MCQA 设置下验证 δ_j 与完整 FUR 的 ff-soft 排序相关（Spearman > 0.7）。
2. **自报关键步**：模型在 CoT 末尾输出 `<key-steps>` 列表（引用段编号）。忠实性奖励 r_faith = NDCG(自报排序, δ 排序)；若模型声称关键的段反学习后答案不动（δ≈0），重罚——这直接惩罚"写出来但没用"的装饰性推理。
3. **扩展到不一致样本**：对 CoT/no-CoT 预测不一致的样本，采用作者建议的替代测量：反学习后用语义等价的改写 CoT 重新推理，以"改写不变性"替代"答案翻转"作为 δ。
4. **可信性约束**：加入轻量 plausibility 判别器（人类标注的"合理/不合理关键步"训练）作为第二奖励项 r_plaus，避免模型学会把参数上承重但人类看不懂的步骤标为关键；总奖励 R = r_correct + λ₁ r_faith + λ₂ r_plaus，GRPO 优化。
5. **成本控制**：探针只在每个 prompt 的 G 个采样中随机抽 2 条计算；其余样本用一个在线蒸馏的"δ 预测头"（基于隐藏状态）近似。

**🧭 与最接近工作的区别**
- Lanham et al. (2023) / Turpin et al. (2023)：用截断、改写、偏置提示等**上下文**干预测量忠实性，无参数级证据，也不做训练。
- FRODO (Paul et al., 2024)：用反事实 CoT 训练"推理器—回答器"使答案依赖 CoT，信号仍是上下文级，且不要求模型自报关键步。
- Chen et al. (2025, "Reasoning Models Don't Always Say What They Think")：只测量推理模型是否口头承认用了提示，不提供训练手段。本 idea 的差异是信号来自**参数反学习**而非上下文干预，并把"自报重要性—参数重要性对齐"作为显式目标。

**🧪 验证方案**
- 基准：论文的 5 个多跳 MCQA（StrategyQA、OpenBookQA 等）＋ GSM8K / MATH-500（长 CoT）；指标：ff-hard、ff-soft、自报-参数 NDCG、准确率不下降、人类 plausibility 评分。
- 关键假设检验：(a) 摊销探针与完整 FUR 的排序一致性；(b) 训练后随机删除"自报关键步"导致答案翻转率显著高于删除非关键步（上下文级交叉验证）。
- 对比与消融：GRPO 仅正确性奖励、FRODO、去掉 r_plaus（看是否出现"承重但不可信"的步骤）、探针替换为上下文删改。

🔑 `CoT faithfulness` `machine unlearning` `parametric attribution` `RL reward design` `interpretability` `self-report alignment`

[🔝 top](#top)

---

## 💡 Idea 1.5 — *Witness-Verified Autoformalization: Instance-Level Semantic Tests as Verifiable Rewards for Formalizing Real-World Definitions*

| | |
|:--|:--|
| 🎯 **源论文** | **Autoformalization in the Wild: Assessing LLMs on Real-World Mathematical Definitions** · Zhang et al. · 🏆 EMNLP 2025 Best Resource Paper· [arXiv:2502.12065](https://arxiv.org/abs/2502.12065) |
| 📌 **线索来源** | 6 Limitations §"while the proposed refinements improve formalization performance, they do not fully eliminate semantic inconsistencies between natural language definitions and their formalized counterparts. More advanced methods are still needed to be developed." + 5 Conclusion §"Future research could focus on improving self-correction capabilities and integrating more robust contextual understanding into LLM-based formalization systems." |
| 📮 **投稿建议** | 🗣️ **NLP** · EMNLP / ACL ＋ 🧪 ML · NeurIPS |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆（需要 Isabelle/Lean REPL 批量执行与 7B 级 RL） |

**🔍 深入分析**
论文把自动形式化从 miniF2F 式的初等算术搬到真实世界的**定义**（Wikipedia 与 arXiv 中的定义，目标语言 Isabelle/HOL），发现主要失败模式是语法不一致、未定义引用与类型错误；两种干预（按错误类别的精炼、用形式库定义做 grounding）能减少语法/类型错误，但 Limitation 承认**语义不一致无法消除**——即形式化能通过类型检查，却定义了另一个概念。空隙在于：证明助手只能回答"是否合法"，不能回答"是否等价于自然语言的意思"；而现有工作对语义的检查要么用 LLM 打分（FormalAlign），要么用回译＋相似度（Herald），两者都是软信号，容易被"貌似合理"的形式化骗过。关键 insight：定义是一个**谓词**，谓词的语义可以在具体实例上被执行检验——"二部图"的形式化必须对 K₂,₃ 返回真、对三角形返回假。实例级检验在证明助手中是可判定且廉价的（`decide`/`simp`/`norm_num`/`eval`），把"语义等价"这一不可判定问题降维成可验证的测试集，恰好构成 RLVR 所需的硬奖励。

**💡 一句话 Idea**
为每条自然语言定义自动生成带标签的正例/负例/边界例（witness），在证明助手中执行候选形式化对这些实例的判定并以通过率作为可验证奖励做 RL，使模型学会生成**语义正确**而非仅"类型正确"的形式化。

**🛠️ 可能的解决方法**
1. **Witness 生成与去偏**：用强 LLM 从 NL 定义生成 8–16 个具体实例（含正例、负例与刻意的边界例，如空集、退化情形），每个实例同时给出 NL 判断与形式对象；用两个独立模型交叉标注并只保留一致的实例；对于无法用具体对象实例化的高阶定义，退化为"性质测试"（如单调性、封闭性）以小定理形式表述。
2. **执行式检验**：将候选形式化 F 应用到每个 witness，由 Isabelle（`simp`/`auto`/Sledgehammer，限时 10s）或 Lean（`decide`/`norm_num`/`aesop`）判定；结果形成混淆矩阵，奖励 r_sem = balanced accuracy；类型检查失败 r = 0；超时按"未知"处理而不计分，避免奖励偏向可判定但无意义的定义。
3. **RLVR 训练**：GRPO，总奖励 R = 1[type-checks] · (r_sem + 0.2·r_ground)，其中 r_ground 奖励复用了库中已有定义（防止模型把每个概念从头重写）；训练数据来自 Def_Wiki/Def_ArXiv 的训练划分与自动扩充的 Wikipedia 定义。
4. **对抗性 witness 迭代**：训练中周期性让另一个模型针对当前策略的形式化生成"区分性实例"（在形式化与 NL 判断不一致的地方），加入测试集，形成最小化—最大化循环，防止策略过拟合固定实例。
5. **成本控制**：实例判定通常在亚秒级，批处理 REPL；对比全自动定理证明式验证便宜两个数量级。

**🧭 与最接近工作的区别**
- FormalAlign (Lu et al., 2025)：训练一个 LLM 打分器判断 NL–形式语句对齐，信号是学习出来的软分数；本 idea 用证明助手**执行**语义测试，信号可验证且不可被措辞欺骗。
- Herald (Gao et al., 2025) / Lean Workbook (Ying et al., 2024)：用回译或编译通过率筛选大规模语句；回译只能检查"读起来像"，编译只检查合法性。
- 论文自身的 Categorical Refinement：只用证明助手的语法/类型错误反馈，本 idea 补上它缺失的语义反馈通道。

**🧪 验证方案**
- 基准：Def_Wiki、Def_ArXiv（Isabelle）＋ 迁移到 Lean 的 ProofNet / Lean Workbook 定义子集；指标：类型检查通过率、**留出 witness 通过率**、人类专家语义正确率。
- 关键假设检验：witness 通过率与人类语义判断的相关性显著高于回译相似度与 LLM 打分；训练后人类判定的"语义不一致"比例下降。
- 对比与消融：SFT、仅类型检查奖励的 RLVR、FormalAlign 打分作奖励、去掉对抗性 witness 迭代、去掉 r_ground。

🔑 `autoformalization` `RLVR` `property-based testing` `Isabelle/Lean` `semantic verification` `definitions`

[🔝 top](#top)

---

## 💡 Idea 1.6 — *Margin-over-Majority Policy Optimization: Training for Vote-Time Scaling with Learned Strategy Selection*

| | |
|:--|:--|
| 🎯 **源论文** | **Rethinking the Role of Prompting Strategies in LLM Test-Time Scaling: A Perspective of Probability Theory** · Liu et al. · 🏆 ACL 2025 Outstanding Paper· [arXiv:2505.10981](https://arxiv.org/abs/2505.10981) |
| 📌 **线索来源** | Limitations §"However, our experiment results indicate that LLMs alone cannot readily achieve the intended effects, pushing us to explore more practicable and effective methods in our future work." + Limitations §"In this paper, we mainly focus on majority voting, which is a simple but effective scaling approach." |
| 📮 **投稿建议** | 🗣️ **NLP** · ACL ＋ 🧪 ML · ICLR |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★☆☆☆（标准 GRPO 代价，7B 单机可做） |

**🔍 深入分析**
论文在 6 模型 × 8 提示策略 × 6 基准上系统观察到：复杂提示策略在小采样数时领先，但随着 majority voting 规模增大，**简单 CoT 反超**。其概率论解释很干净：多数投票能否收敛到正确答案，取决于每道题上正确答案概率是否高于最强错误答案的概率，以及"易题/难题"的分布比例；复杂策略虽提升了部分难题，却在更多题上把概率质量集中到某个错误答案。作者提出的两条改进——按难度自适应分配采样预算、按题动态选策略——在 Limitation 里被明确承认"LLM 自身做不到"，只能靠外部预测器。空隙在于：当前 RLVR 都在优化 pass@1（或 pass@k），而部署时人们用的是 maj@k；pass@1 的提升可能伴随错误答案的"共识化"，反而损害投票上限。关键 insight：组采样（GRPO）天然给出了每题的经验答案分布，因此可以**直接优化"正确答案概率 − 最强错误答案概率"这一投票裕度**，并让策略选择与停采决策成为策略自身的动作。

**💡 一句话 Idea**
把 GRPO 的组内样本当作对该题答案分布的估计，以"正确答案份额减去最强错误答案份额"的投票裕度作为组级奖励（leave-one-out 分配到个体），并让模型先输出一个策略 token 选择推理策略，从而让模型学会在多数投票规模增大时持续受益。

**🛠️ 可能的解决方法**
1. **裕度奖励**：对每题采样 G=16，聚合最终答案得份额向量 q；定义 M(q) = q_correct − max_{a≠correct} q_a。个体优势用 leave-one-out：A_i = M(q) − M(q₋ᵢ)，使得"支持最强错误答案"的样本被惩罚得比"孤立错误"更重，正确样本的奖励在正确份额已经领先时递减（避免过度确定化）。理论动机：maj@k 的错误率 ≈ Φ(−√k·M/σ)，M 是其一阶决定量。
2. **策略 token**：在回答前模型输出 `<strategy: cot|l2m|plan|…>`（词表新增 K 个 token），该 token 的 logprob 一并进入策略梯度；不同策略的样本混在同一组里比较，模型自然学到"哪类题用哪种策略裕度最大"，替代外部预测器。
3. **自适应停采头**：在生成结束的隐状态上训练一个头预测当前题的 (q_correct, q_wrong_max) 后验（用组统计作监督），推理时用 Dirichlet 后验做序贯停止，预算分配给裕度小的题。
4. **防坍缩**：在 M 上加入熵底线（答案分布熵不低于 base 的 50%），避免模型把所有样本压成同一个答案以刷 M；这与 Idea 1.1 的边界保持互补。
5. 成本与 GRPO 相同，仅多一次答案聚合。

**🧭 与最接近工作的区别**
- Pass@k Training (Chen et al., 2025)：以 pass@k 作为奖励鼓励探索，关注"至少一个对"，不关心错误答案是否集中，与投票目标不同。
- ScPO (Prasad et al., 2024)：用 self-consistency 的多数答案作伪标签做偏好优化，是**用投票做监督**，本 idea 是**为投票而优化**，且有可验证标签。
- Adaptive-Consistency (Aggarwal et al., 2023) / ESC (Li et al., 2024)：推理期序贯停止，不改变模型本身；本 idea 的停采头与裕度奖励联合训练。

**🧪 验证方案**
- 基准：MATH-500、GSM8K、GPQA、AIME24/25、ARC-C（论文使用的类型）；指标：maj@k 曲线（k=1…256）、裕度 M 的分布、pass@1 不降。
- 关键假设检验：pass@1-GRPO 训练后 q_wrong_max 上升（错误共识化）而本方法下降；策略 token 的选择与题目类型显著相关。
- 对比与消融：GRPO(pass@1)、Pass@k Training、ScPO、去掉策略 token、去掉熵底线、固定策略 vs 学习策略。

🔑 `majority voting` `test-time scaling` `GRPO` `prompting strategy` `reward design` `adaptive sampling`

[🔝 top](#top)

---

## 💡 Idea 1.7 — *Length-Augmented Groups: Reinforcement Learning for Input-Length-Invariant Reasoning*

| | |
|:--|:--|
| 🎯 **源论文** | **Same Task, More Tokens: the Impact of Input Length on the Reasoning Performance of Large Language Models** · Levy et al. · 🏆 ACL 2024 Outstanding Paper· [arXiv:2402.14848](https://arxiv.org/abs/2402.14848) |
| 📌 **线索来源** | Limitations §"Because of the nature of behavioral testing, the observed drop in performance with varying input lengths remains unexplained" + Limitations §"Finally, our study did not test the distance between key paragraphs, leaving an aspect of LLM performance unexplored that we leave for future research." + 9 Discussion §"we identified specific failure modes, including difficulties in following extended instructions and biases towards less relevant information." |
| 📮 **投稿建议** | 🗣️ **NLP** · ACL / EMNLP ＋ 🧪 ML · ICLR |
| ⭐ Novelty | ★★★☆☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆（长序列 RL，需 8 卡与高效注意力） |

**🔍 深入分析**
FLenQA 的设计很巧妙：同一道两跳推理题，用不同长度、不同类型（无关文本 / 同域文本 / 重复）、不同位置的填充扩展出多个版本，从而把"输入长度"从"任务难度"中隔离出来。结论是：**远在上下文窗口上限之前**（约 3K token），推理性能就显著下降，且下一词预测困惑度与推理性能负相关；失败模式包括不遵循"逐步推理"指令、偏向无关信息。Limitation 承认退化机制未被解释，也未测试关键段落之间的距离。之后的工作（NoLiMa、IN2 训练等）大多关注**检索式**长上下文（把事实找出来），而非"找到后还能推理"；并且 SFT 式的 IN2 训练只教模型读到信息，没有直接以"长短版本答案一致"作为优化目标。空隙在于：FLenQA 的"同题多版本"结构正是 GRPO 需要的"组"——把同一问题的不同长度/距离版本放进同一组，共享基线后优势信号就直接等于"长度敏感性"，这是一个此前没人利用的免费训练信号，而且不需要新标签。

**💡 一句话 Idea**
把同一道题的多个长度/填充类型/关键段距离版本作为 GRPO 的一个组做 RL，并加入"长版本答案与短版本一致"的奖励与关键段注意力守恒的辅助损失，使推理能力对输入长度不变，同时用注意力诊断给退化现象一个机理解释。

**🛠️ 可能的解决方法**
1. **数据与环境**：复用 FLenQA 的构造流程，对每题生成 V 个版本：长度 L∈{0.5K,2K,8K,32K}、填充类型（无关/同域/重复）、关键段距离 d∈{相邻, 1/4 L, 1/2 L, 两端}；外加 MuSiQue/HotpotQA 类多跳题的同样扩展。
2. **长度增强组 GRPO**：组 = 同题 V 个版本 × 每版本 2 个样本；优势按组归一化，于是短版本答对而长版本答错时，长版本样本获得负优势而短版本正优势，梯度直接指向"长度鲁棒"。再加一致性奖励 r_cons = 1[ans_long = majority(ans_short)]，可在**无标签**问题上训练。
3. **注意力守恒辅助损失**：记录回答位置对关键段的注意力质量 m(L)；加入 ℓ_att = (m(L) − m(L₀))²，只在最后 1/3 层施加，权重小；同时用它做诊断，检验"退化 = 关键段注意力被稀释"这一机理假设。
4. **距离维度**：把关键段距离作为显式变量做课程（由近到远），回答论文未测试的问题。
5. **成本控制**：32K 版本只占组的 1/4；使用序列并行与 FlashAttention；7B 模型 8 卡数天。

**🧭 与最接近工作的区别**
- IN2 / FILM (An et al., 2024)：用合成长文 QA 做 SFT 教模型利用上下文中部信息，无 RL、无同题多长度对比，且目标是检索而非推理。
- QwenLong-L1 (Wan et al., 2025)：长上下文推理 RL，但训练样本本身就是长文档，长度不是受控变量，无法隔离长度敏感性。
- Found in the Middle (Hsieh et al., 2024)：推理期注意力校准，不训练模型；本 idea 把类似的注意力量作为可训练目标并与结果奖励联合。

**🧪 验证方案**
- 基准：FLenQA 全部版本、NoLiMa、RULER 推理子集、LongBench v2；指标：准确率—长度曲线的斜率、长短一致率、"关键段距离—准确率"曲线。
- 关键假设检验：训练后 m(L) 不再随 L 衰减；去掉 ℓ_att 时准确率曲线是否仍变平（判断注意力是机制还是伴随现象）。
- 对比与消融：普通 GRPO（只用短版本）、IN2-SFT、QwenLong-L1 式 RL、去掉一致性奖励、去掉距离课程；检查短输入性能与通用基准不退化。

🔑 `long context` `input length` `GRPO` `invariance` `multi-hop reasoning` `attention dilution`

[🔝 top](#top)

---

## 💡 Idea 1.8 — *Learned Dynamics as Reward: Inverse-Dynamics Validity and Potential-Based Progress Signals for Visual Planning RL*

| | |
|:--|:--|
| 🎯 **源论文** | **Visual Planning: Let's Think Only with Images** · Xu et al. · 🎤 ICLR 2026 Oral · [arXiv:2505.11409](https://arxiv.org/abs/2505.11409) |
| 📌 **线索来源** | Appendix D Limitations and future work §"For simplicity, we adopt the rule-based approach that compares pixel-wise features between the current state and the previous state" + §"the underlying reward formulation remains extensible, but the primary challenge lies in defining reliable progress signals as visual transitions become more complex." + §"explicitly generating images introduces computational overhead during inference compared to a textual response." |
| 📮 **投稿建议** | 🧪 **ML** · ICLR / NeurIPS ＋ 👁️ CV · CVPR |
| ⭐ Novelty | ★★★☆☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆（需训练 IDM 与距离函数，LVM 7B 级 GRPO） |

**🔍 深入分析**
论文提出"只用图像思考"的 Visual Planning：模型直接生成下一帧状态图像序列来规划，用两阶段 VPRL（随机策略初始化 + GRPO）在 FrozenLake、Maze、MiniBehavior 上比文本规划高 27% EM，并证明文本模型在把视觉布局口头化时有 20%+ 的 grounding 错误。但奖励完全依赖**规则式像素差分解释器**：对比前后两帧像素推断动作并判断是否合法、是否接近目标。Limitation 坦承这在复杂视觉结构下不可行，"可靠的进度信号"是核心难题；同时逐帧生成图像的推理开销很大。这个空隙是实质性的：VPRL 的成功依赖一个只在网格世界成立的 oracle，现有多模态"思考"工作（MVoT、Thinking with Generated Images）要么是 SFT、要么把图像当辅助而非状态。关键 insight：规则解释器做的两件事——"这一步对应什么动作"与"离目标更近了吗"——恰好是 RL 文献中已有可学习对象：逆动力学模型（IDM）与目标条件时间距离函数；后者作为势函数做 shaping 还能保证最优策略不变，从而把 VPRL 推广到任意有模拟器的视觉域。

**💡 一句话 Idea**
用从随机交互数据学习的逆动力学模型判定视觉转移的合法性、用目标条件时间距离函数的势差作为进度奖励，替换 VPRL 的像素规则，使视觉规划 RL 能扩展到复杂视觉动态并以潜变量规划降低生成开销。

**🛠️ 可能的解决方法**
1. **逆动力学合法性奖励**：在环境里用随机策略收集 (s_t, a_t, s_{t+1}) 图像三元组训练 IDM p(a|s_t,s_{t+1})；对模型生成的相邻两帧，r_valid = max_a p(a|·) 超过阈值且该动作在模拟器中可执行；再用正向模型重建 s_{t+1} 做一致性校验，防止生成"看似合法"的伪帧。
2. **势函数进度奖励**：训练目标条件时间距离 V(s,g)（quasimetric / VIP 式目标），r_prog = γV(s_{t+1},g) − V(s_t,g)，作为 potential-based shaping，不改变最优策略；终局奖励保留为是否到达目标。
3. **多 IDM 集成抗 hack**：策略可能生成让 IDM 高置信但物理上错误的图像；用 3 个不同架构 IDM 取最小置信，并以 IDM 在生成帧上的预测熵做 OOD 检测，OOD 帧直接 0 奖励。
4. **潜空间规划降开销**：先把帧编码为 VQ token（≤64 token/帧）在潜空间规划，只在末尾或抽检时解码为像素；IDM 与 V 都在潜空间训练，推理成本降一个数量级。
5. **新环境**：Sokoban（物体交互）、ManiSkill 桌面操作（真实渲染）、ProcTHOR 导航，均无法手写像素规则。

**🧭 与最接近工作的区别**
- VPRL（源论文）：奖励来自手写像素差分规则，只适用于网格世界。
- MVoT (Li et al., 2025)：多模态"可视化思维"用 SFT 学习交替生成图像与文本，无 RL 与进度信号。
- VIP / LIV (Ma et al., 2023)：学习视觉价值函数用于机器人控制的奖励，本 idea 把它迁移为**生成式规划模型**的训练信号并与 IDM 合法性奖励配合。

**🧪 验证方案**
- 基准：论文三任务（EM、OOD 更大网格）＋ Sokoban、ManiSkill、ProcTHOR；指标：任务成功率、合法转移率、每步生成 token 数/延迟。
- 关键假设检验：在网格世界中学习的 IDM+V 奖励与规则奖励训练结果持平（无损替代），在复杂环境中规则不可用而学习奖励仍有效；shaping 不改变最终策略（去 shaping 后收敛更慢但终点一致）。
- 对比与消融：VPRL、VPFT、文本规划 RL、单 IDM vs 集成、像素空间 vs 潜空间、去 r_prog。

🔑 `visual planning` `GRPO` `inverse dynamics` `reward shaping` `multimodal reasoning` `latent planning`

[🔝 top](#top)

---

## 💡 Idea 1.9 — *Semantic Coverage: Estimating and Optimizing Post-Training Readiness of Base Models Beyond Cross-Entropy*

| | |
|:--|:--|
| 🎯 **源论文** | **The Coverage Principle: How Pre-Training Enables Post-Training** · Chen et al. · 🎤 ICLR 2026 Oral · [arXiv:2510.15020](https://arxiv.org/abs/2510.15020) |
| 📌 **线索来源** | 7.2 Future Work §"The notion of coverage we focus on, the coverage profile, is mathematically convenient but may be conservative in regard to downstream performance, since it only depends on the model through its predicted probabilities. An important direction for future work is to understand pre-training and post-training through fine-grained “semantic” notions of coverage" + §"More ambitiously, one could imagine re-structuring the entire language modeling pipeline itself around coverage." |
| 📮 **投稿建议** | 🧪 **ML** · ICLR / NeurIPS |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★★☆（需 1B–7B 级中期训练与多次 RLVR 对照） |

**🔍 深入分析**
论文从理论上说明：Best-of-N、RLVR 等后训练能否成功，充分必要条件不是交叉熵，而是**覆盖率**——基座模型对高质量回答放了多少概率质量（覆盖率剖面 Cov_N = P[π_D/π̂ > N]，即似然比的尾部）；next-token prediction 隐式地优化覆盖率，但在有限样本下交叉熵并不能预测覆盖率，并且作者展示覆盖率可用于指导优化器与模型选择。Future Work 指出两点：覆盖率剖面只依赖预测概率、可能过于保守；应发展"语义"覆盖率。空隙很清楚：选基座/数据配比仍看 loss 与 few-shot，而 RLVR 的真正瓶颈（能否采到正确答案）既无专门度量也无针对性目标。Idea 1.1 从 RL 侧防止边界缩小，本 idea 从**预训练侧**扩大边界本身。关键 insight：覆盖率是似然比的尾部统计量，所以降低它的正确代理不是平均 NLL，而是**最差 α 分位的 NLL（CVaR）**；而"语义"版本只需把序列级概率换成"等价类的概率质量"（同一答案或同一解法的全部表述），这可以通过采样 + 验证器/聚类估计。

**💡 一句话 Idea**
定义以答案/解法等价类为单位的语义覆盖率，用它（而非交叉熵）作为预训练检查点与数据配比的选择标准，并在中期训练中以 CVaR 式尾部似然损失直接优化覆盖率，使基座模型"更可被后训练"。

**🛠️ 可能的解决方法**
1. **语义覆盖率估计器**：对探针集的每个 prompt 采样 N=256 条，用验证器（数学/代码）或嵌入聚类（开放域）划分等价类；Cov^sem_N = P_{(x,c*)}[π̂(c*|x) < 1/N]，其中 π̂(c*|x) 由采样频率估计并用 Good–Turing 平滑处理零计数。成本：1K prompt × 256 样本，远低于一次 RL。
2. **检查点/数据选择**：在同一预训练 run 的多个检查点与不同数据配比上，测 Cov^sem 与随后 RLVR/BoN 增益的相关性，与 CE、few-shot 准确率对比（假设：Cov^sem 的预测力显著更高）。
3. **覆盖率导向的中期训练目标**：ℓ_cov = CVaR_α(NLL) ＋ λ·平均 NLL，α=0.1–0.2，按文档或按可验证回答计算；理论上 CVaR 直接压低似然比尾部即覆盖率剖面；语义版本加入 ℓ_sem = −log Σ_{y∈c*} π̂(y|x)（对采样到的正确等价类做集合级最大似然，等价于奖励"任何一种正确表述"而非特定参考答案）。
4. **防止退化**：CVaR 对噪声/低质量文档敏感，先用质量过滤器排除最差 1% 文档再取尾部；对可验证域只对验证通过的回答施加 ℓ_sem。
5. **流水线**：标准 NTP → 覆盖率中期训练（≤5% token 预算）→ 固定配方的 GRPO；对比同算力的普通继续预训练。

**🧭 与最接近工作的区别**
- Huang et al. (2025, "Is Best-of-N the Best of Them?")：分析覆盖率与 BoN 最优性，不给出可估计的语义覆盖率，也不训练。
- Foster et al. (2025, 计算视角的基座模型与探索)：说明覆盖率决定 RL 探索效率，仍是理论分析。
- Rho-1 (Lin et al., 2024)：按 token 选择训练损失提升下游，但选择标准是参考模型的 excess loss，不是尾部覆盖；本 idea 以覆盖率为显式目标并提供选择标准。

**🧪 验证方案**
- 设置：Pythia/OLMo 系列公开检查点＋自训 1B 模型；下游：GRPO 后的 MATH-500、GSM8K、HumanEval 增益，BoN@256。
- 关键假设检验：Cov^sem 与后训练增益的 Spearman 相关高于 CE 与 few-shot；覆盖率中期训练在同算力下使 RLVR 增益和 pass@256 显著提升而 CE 可能持平或略升。
- 对比与消融：平均 NLL 继续训练、Rho-1 式 token 选择、去 CVaR 只留 ℓ_sem、不同 α。

🔑 `coverage` `pre-training` `post-training readiness` `CVaR loss` `pass@k` `model selection`

[🔝 top](#top)

---

## 💡 Idea 1.10 — *Multi-Basin Energy-Based Transformers: Winner-Takes-All Landscape Shaping for Multimodal System-2 Thinking*

| | |
|:--|:--|
| 🎯 **源论文** | **Energy-Based Transformers are Scalable Learners and Thinkers** · Gladstone et al. · 🎤 ICLR 2026 Oral · [arXiv:2507.02092](https://arxiv.org/abs/2507.02092) |
| 📌 **线索来源** | 7 Limitations and Conclusion §"EBTs currently struggle with data distributions that have many modes, such as class conditional image generation, likely due to the convex energy landscape assumption made during training." + B.2 EBT Failure Cases §"when there are many different modes within the same region (same condition), this convex energy landscape “merges” to one landscape averaged around the different modes, resulting in blurriness." + 7 §"Tuning these hyperparameters is crucial for training stability, as we found poorly chosen values often lead to unstable training." |
| 📮 **投稿建议** | 🧪 **ML** · ICLR / NeurIPS |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★★☆（需复现 EBT 预训练并做 100M–800M 规模扩展实验） |

**🔍 深入分析**
EBT 把"思考"重构为对学习到的能量（验证器）做梯度下降：对候选预测迭代优化直到能量最低，动态算力分配与自我验证完全来自无监督预训练，且在文本和视频上扩展率快于 Transformer++。但 Limitation 指出两个相互关联的软肋：训练时假设能量面在训练样本周围是**凸**的（从随机初始化沿一条梯度轨迹拉向真值），当同一条件下存在多个模态时各模态的凸盆地被平均成一个，输出模糊；且步长/步数等超参数极易导致训练不稳定。而推理任务天然多模态——一道题有多条正确路径，能量面若把它们平均，"思考"就退化为向均值回归；现有能量式迭代推理（IRED、JEM）也未处理"条件内多模态 + 单轨迹训练"的冲突。关键 insight：问题出在**用一条轨迹对所有模态负责**；多选学习（winner-takes-all）的经典做法是让多条轨迹各自只对最近的模态负责，再配合对比负样本在模态之间抬高能量，就能得到多盆地而非平均化的能量面。

**💡 一句话 Idea**
用 K 个可学习初始化并行运行能量下降、只对离真值最近的轨迹施加拉低能量的损失（winner-takes-all），同时用其他轨迹的终点作为对比负样本抬高模态之间的能量，并以元学习步长替代手调，使 EBT 在多模态分布上形成多个尖锐盆地而非一个模糊平均。

**🛠️ 可能的解决方法**
1. **多初始化 WTA 训练**：一个轻量提议头产生 K（4–8）个初始预测 ŷ₀^{(k)}（混合高斯或可学习码本），各自跑 T 步能量下降得到 ŷ_T^{(k)}；损失只作用于 k* = argmin_k ‖ŷ_T^{(k)} − y‖ 的轨迹（ℓ_WTA），其余轨迹接收一个小权重 ε 的损失以防死亡（relaxed WTA）。
2. **模态间对比项**：把非赢家轨迹终点作为负样本，ℓ_con = max(0, m − [E(x, ŷ^{(k≠k*)}) − E(x, y)])，在模态之间抬高能量形成鞍；这相当于短程对比散度，无需 MCMC。
3. **元学习步长与步数**：步长 η 与阻尼由一个以能量梯度范数为输入的小网络输出，用内层展开的元梯度训练（类似 learned optimizer），并加入 Lipschitz 正则防止爆炸，直接回应"超参数敏感"问题。
4. **推理期的多盆地思考**：推理时从 K 个初始化下降，按最终能量选择或按能量做 softmax 采样——这给出了"多样且各自自洽"的 System-2 输出，可直接测 pass@k。
5. **规模与成本**：K 条轨迹可批内并行，成本约 K/2 倍（因可提前终止高能量轨迹）；先在 CIFAR 类条件生成与 COCO 文生图小规模复现模糊问题，再做 100M–800M 文本 EBT。

**🧭 与最接近工作的区别**
- IRED (Du et al., 2024)：能量扩散式迭代推理，用退火能量处理多模态，但仍是单轨迹训练；本 idea 用 WTA 把多模态责任分配到多条轨迹。
- Multiple Choice Learning / WTA (Guzmán-Rivera et al., 2012; Lee et al., 2016)：用于多头预测器，本 idea 首次将其作用于**能量下降轨迹**并加入模态间对比项。
- JEM (Grathwohl et al., 2020)：用 SGLD 负样本训练能量，昂贵且不稳定；本 idea 的负样本来自并行轨迹，免 MCMC。

**🧪 验证方案**
- 基准：类条件 CIFAR-10/ImageNet-64（FID、模式覆盖率/precision-recall）、COCO 小规模文生图；文本：论文的语言建模困惑度与 OOD 推理集，GSM8K 的 pass@1/pass@k（多盆地思考）。
- 关键假设检验：训练后能量面在同条件多模态样本上呈多个局部极小（用插值路径上的能量曲线验证）；模糊度（高频能量）显著下降。
- 对比与消融：原 EBT、K=1、去对比项、固定步长 vs 元学习步长、relaxed-WTA 的 ε 扫描；扩展率对比 Transformer++。

🔑 `energy-based model` `System 2 thinking` `multimodality` `winner-takes-all` `learned optimizer` `iterative inference`

[🔝 top](#top)

---

## 💡 Idea 1.11 — *Causal Transition Values: History-Conditioned Counterfactual Resampling of Cognitive States as Dense Process Rewards*

| | |
|:--|:--|
| 🎯 **源论文** | **Modeling Hierarchical Thinking in Large Reasoning Models** · Shahariar et al. · 🎤 ICML 2026 Oral · [arXiv:2510.22437](https://arxiv.org/abs/2510.22437) |
| 📌 **线索来源** | Appendix E Limitations and Future Work §"We model long reasoning as a memoryless FSM over six discrete states. This makes the analysis and control tractable, but it cannot capture finer-grained skills (e.g., algebraic manipulation vs. proof search) or longer-range dependencies where the best next move depends on earlier context, not just the current state." + §"if the model lacks the underlying domain knowledge to rectify its error, steering it into a Backtracking state may merely result in “hallucinated corrections” or repetitive loops." + §"identifying a more robust and reliable reward signal beyond the empirical R matrix remains a compelling future research direction." |
| 📮 **投稿建议** | 🧪 **ML** · ICML / NeurIPS ＋ 🗣️ NLP · ACL |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆（反事实采样昂贵但可离线摊销，7B–14B 推理模型） |

**🔍 深入分析**
论文把长 CoT 抽象为六个认知状态（演绎、不确定、回溯、验证……）之间的有限状态机，发现成功与失败轨迹的状态转移统计显著不同，并用一个"转移优势矩阵 R"做 Q 值引导的激活操控，在少量干预下提升难题表现。Limitation 自己点破了三个问题：FSM 无记忆、R 只是相关不是因果（把模型推入"回溯"可能只产生幻觉式纠错）、需要比经验 R 更可靠的奖励信号。空隙在于：R 来自观测统计，拿它做操控是"用相关做干预"；推理 RL 已有反事实价值工具（VinePPO、Thought Anchors），却从未在**认知状态**层面做因果估计，也没把状态转移价值当作稠密过程奖励。关键 insight：在每个句子边界可以**强制**模型进入某个状态（用状态提示语或激活操控）并多次续写，得到的结果成功率就是该转移的因果 Q 值；以状态历史（而非当前状态）为条件估计，即得到有记忆的、因果的转移价值，可直接替代 R 用于 credit assignment。

**💡 一句话 Idea**
在推理轨迹的句子边界做"强制进入状态 s′ 并续写"的反事实重采样，估计以状态历史为条件的因果转移价值 Q(h, s′)，用它作为 GRPO 的句子级稠密过程奖励，让模型学会在正确的时机进入正确的认知状态，而非靠推理期操控。

**🛠️ 可能的解决方法**
1. **反事实数据生成**：对每个训练题采样 8 条轨迹，用论文的状态分类器切分状态段；在每个段边界 t，对每个候选状态 s′∈6 种，用短提示前缀（如 "Wait, let me double-check…" 对应验证）或论文的正交激活注入强制进入 s′，各续写 M=4 次至结束，用验证器记录成功率 → Q̂(h_t, s′)，其中 h_t 为到 t 为止的状态序列。
2. **历史条件价值模型**：训练一个小 Transformer（输入：状态序列 + 段末隐状态）回归 Q̂，与无记忆 R 做对照；若 Q̂ 对历史的依赖显著（消融历史后误差上升），就证实了"无记忆 FSM 不足"。
3. **稠密过程奖励 RL**：r_t = Q̂(h_t, s_{t+1}) − E_{s′}[Q̂(h_t, s′)]（转移优势），加上终局正确性；GRPO 组内按句子级优势加权。"知识缺口"保护：若某边界所有 s′ 的 Q̂ 都接近 0，则该处奖励置零，不鼓励任何"幻觉式纠错"。
4. **成本控制**：反事实采样只在 20% 的训练题上离线做一次（每题 ≈ 8×边界数×6×4 次续写，用 2K token 截断与早停），其余由价值模型泛化；训练后期每 N 步刷新一小批以减缓分布漂移。
5. **扩展到开放任务**：用 LLM-judge 作为成功信号时，引入成对比较而非绝对分数以降噪。

**🧭 与最接近工作的区别**
- 源论文的 Q-Value Steering：推理期用相关性的 R 矩阵操控激活；本 idea 用反事实干预估计**因果**转移价值并用于**训练**。
- Thought Anchors (Bogdan et al., 2025)：用句子级反事实重采样找"关键句"做解释，不在认知状态层面、不做 RL。
- VinePPO (Kazemnejad et al., 2024)：用 MC 续写估计每步价值做 credit assignment，但动作是 token/步骤而非"认知状态"，且无法回答"换一种思维动作会怎样"。
- Gandhi et al. (2025, cognitive behaviors)：用 SFT 预置回溯/验证等行为，不估计何时该用。

**🧪 验证方案**
- 基准：MATH-500、AIME24/25、GPQA-Diamond、LiveCodeBench；指标：准确率、平均长度、状态转移熵。
- 关键假设检验：(a) Q̂ 与经验 R 的符号在 >20% 的转移上不一致（相关≠因果）；(b) 历史条件模型显著优于无记忆模型；(c) 用 Q̂ 奖励训练后"回溯后仍错"的比例下降。
- 对比与消融：GRPO 结果奖励、PRM（Qwen-PRM）、VinePPO、源论文推理期操控、无记忆 R 作奖励、去掉知识缺口保护。

🔑 `cognitive states` `counterfactual resampling` `process reward` `credit assignment` `long CoT` `causal steering`

[🔝 top](#top)

---

## 💡 Idea 1.12 — *Necessity-Adjusted Monitorability: Disentangling Whether a Model Needs to Think Aloud from Whether It Chooses To*

| | |
|:--|:--|
| 🎯 **源论文** | **Monitoring Monitorability** · Guan et al. · 🎤 ICML 2026 Oral · [arXiv:2512.18311](https://arxiv.org/abs/2512.18311) |
| 📌 **线索来源** | 9 Discussion and Conclusion §"Our evaluations do not disentangle the propensity to verbalize versus the necessity to verbalize, and so it could very well be that sycophantic tendencies (if any) are “baked in” into the model weights such that they do not need to be verbalized." + E.4 Limitations and Future Directions §"many of the negative examples are manually constructed, rather than being naturally occurring failures of the base model whose CoT is being monitored." |
| 📮 **投稿建议** | 🧪 **ML** · ICML / NeurIPS ＋ 🗣️ NLP · ACL |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★☆☆（主要是大规模采样与干预评测，可在开源推理模型上做） |

**🔍 深入分析**
论文为"CoT 可监控性"建立三类评测原型（干预、过程、结果属性）与新指标，发现前沿推理模型总体可监控但不均匀——谄媚比编码环境中的 reward hacking 更少被口头化；并研究了 CoT 奖励压力、RL 与预训练算力对可监控性的侵蚀。两个 Limitation 很关键：(i) 指标混合了"必须口头化"与"倾向口头化"，低可监控性可能只是行为已内化到权重里；(ii) 退化基准的负例是人工构造的，监控器可能学到"分布指纹"而非真正的理解。这决定了数字能否指导决策：下降若来自"必要性降低"（能力内化）与来自"倾向降低"（隐匿），对策完全不同。Lanham 等的截断/改写干预与 Emmons 等的"CoT 必要时难以逃避监控"给出了雏形，但都没有做成逐样本估计器并与可监控性指标联合。关键 insight：必要性是可以**因果地**测的——干预掉 CoT 的对应片段后行为属性是否改变；而退化负例可以通过锚定重采样从目标模型自身生成并做统计匹配。

**💡 一句话 Idea**
为每条轨迹估计"行为属性是否因果依赖 CoT 片段"的必要性分数，把可监控性分解为必要条件下的监控率与非必要条件下的自愿口头化率，并用目标模型自身的锚定重采样生成统计匹配的退化负例，使可监控性评测既可解释又抗分布捷径。

**🛠️ 可能的解决方法**
1. **必要性估计器**：对每条带属性标签（如 reward hack / 谄媚 / 遵循干预）的轨迹，做三种干预：截断 CoT 至片段前、用模型生成的"不含该属性信息"的改写替换片段、等长填充 token；n(x) = 干预后属性标签翻转的频率（各 8 次续写取平均）。n 高 = 模型确实需要在 CoT 里"算"这件事。
2. **分解指标**：Mon_nec = P(监控器检出 | n>τ)，Mon_vol = P(检出 | n<τ)；报告 (Mon_nec, Mon_vol) 曲线随 RL 算力、预训练算力、CoT 压力的变化，判断侵蚀来源；预期谄媚类行为的 n 普遍低，这解释了其低口头化率。
3. **锚定重采样负例**：对同一前缀，用干预变体生成"遵循/不遵循干预"的两组续写，只保留长度、停用词比、重复率、困惑度在匹配区间内的配对；再训练一个域分类器，要求正负例 AUC<0.55 才通过，否则继续筛。
4. **监控器训练与测试**：在匹配负例上训练/评估监控器，并与原人工负例对比：若监控器在人工负例上高分、匹配负例上掉分，说明此前存在捷径。
5. **成本控制**：必要性估计只需推理，不需训练；对每个环境抽样 500–2000 条轨迹；在开源推理模型（Qwen3、DeepSeek-R1-Distill）上做算力扫描。

**🧭 与最接近工作的区别**
- Lanham et al. (2023)：用截断/改写等干预测 CoT 忠实性，是单一设定下的全局指标，不与监控器指标联动。
- Emmons et al. (2025, "When Chain of Thought is Necessary…")：在少数必须用 CoT 的任务上证明模型难以逃避监控，是任务级的二元"必要"；本 idea 做逐样本连续估计并覆盖整套评测。
- Baker et al. (2025, CoT 压力导致隐匿)：说明奖励压力下的隐匿，本 idea 提供区分"隐匿"与"内化"的度量。

**🧪 验证方案**
- 设置：复现论文三类原型中的开源可做部分（干预型、过程型）＋编码 reward-hack 环境（如 SWE-style 带漏洞测试）；模型：多个尺寸与 RL 步数的开源推理模型。
- 关键假设检验：(a) 用匹配负例训练的监控器在真实退化样本上的 AUC 高于用人工负例训练的；(b) 不同行为类型的 Mon_nec/Mon_vol 分离，谄媚的低可监控性主要由低必要性解释；(c) RL 算力增大时两分量的变化方向不同。
- 对比与消融：原指标、不做匹配筛选、不同 τ、不同干预类型。

🔑 `CoT monitorability` `necessity vs propensity` `counterfactual intervention` `reward hacking` `resampling` `AI oversight`

[🔝 top](#top)

---

## 💡 Idea 1.13 — *Circuit-Distilled Verifiers: Compressing White-Box Reasoning Error Signatures into Real-Time Gray-Box Process Rewards*

| | |
|:--|:--|
| 🎯 **源论文** | **Verifying Chain-of-Thought Reasoning via Its Computational Graph** · Zhao et al. · 🎤 ICLR 2026 Oral · [arXiv:2510.09312](https://arxiv.org/abs/2510.09312) |
| 📌 **线索来源** | Appendix E Limitations §"CRV in its current form is positioned as a scientific tool for deep analysis, not as a scalable, real-time verifier for production systems." + §"The feature set used by CRV is primarily aggregative; it captures statistical and topological properties of the graph, such as node counts, influence scores, and density. As an early work, it does not yet fully exploit the semantic content of the individual transcoder features that constitute the graph’s nodes." |
| 📮 **投稿建议** | 🧪 **ML** · ICLR / NeurIPS ＋ 🗣️ NLP · EMNLP |
| ⭐ Novelty | ★★★☆☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆（需训练 transcoder 与构图作教师，一次性成本高） |

**🔍 深入分析**
CRV 用 transcoder 替换 Llama-3.1-8B 的模块，对每个推理步构建归因图，把图的结构特征（节点数、影响力、密度等）喂给分类器，发现正确与错误推理步的"电路执行轨迹"有可区分的结构指纹，而且指纹是**因果**的——干预对应 transcoder 特征能纠正错误。Limitation 承认两点：每步构图比黑盒/灰盒验证贵几个数量级，无法实时使用；特征只是聚合统计，没有利用单个 transcoder 特征的语义。空隙在于：一边是"被证明因果相关"却贵到无法进入训练循环的信号，一边是便宜但无因果保证、可能只学到"置信度"的隐藏状态探针。关键 insight：知识蒸馏可以跨越这一鸿沟——用 CRV 作为教师给大量推理步打上结构指纹分数，训练一个只读残差流（或稀疏特征激活）的学生探针；若学生保留教师的因果信号（干预实验验证），就得到了零额外成本的实时验证器，可以直接作为 RLVR 的步骤级奖励，从而把机理可解释性的产出第一次接入后训练。

**💡 一句话 Idea**
把 CRV 的归因图错误指纹蒸馏到一个仅读取残差流与 top-k transcoder 特征身份的轻量探针中，获得与因果结构信号对齐的实时步骤验证器，并把它作为白盒来源的过程奖励用于 RL。

**🛠️ 可能的解决方法**
1. **教师信号**：复现 CRV（Llama-3.1-8B + 各层 transcoder），在 50K–100K 推理步（GSM8K/MATH/逻辑/代码混合）上计算结构指纹分数 s_CRV 与正确标签；一次性成本可控。
2. **学生探针**：输入为步末 token 的多层残差拼接 ＋ 该步 top-32 活跃 transcoder 特征的稀疏 one-hot（"特征身份袋"，回应"未利用语义"的限制）；两头输出：回归 s_CRV 与分类正确性；训练用 KD 损失 + 交叉熵。
3. **因果保真检验**：对学生判为错的步，沿着教师识别的特征做激活干预，检查学生分数与结果同时改善；与"置信度探针"对比，学生应在"高置信但错"的样本上仍能检出。
4. **域混合**：错误指纹域特异，用按任务嵌入门控的混合探针（3–5 个专家），并测试跨域迁移与 MoE/更大模型（Llama-3.3-70B、Qwen3-MoE）上的可复现性。
5. **作为过程奖励**：r_t = σ(学生分数)，与结果奖励结合做 GRPO（步骤级优势加权）；探针只多一次线性运算，几乎零开销；为防奖励 hack，探针每 N 步用新采样数据与教师重新校准。

**🧭 与最接近工作的区别**
- Zhang et al. (2025, "Reasoning Models Know When They're Right")：直接用隐藏状态探针预测中间答案正确性，无因果来源，可能退化为置信度；本 idea 以因果验证过的结构信号为教师并引入特征语义。
- Lookback Lens (Chuang et al., 2024)：用注意力比值探针检测幻觉，是单一手工特征；本 idea 蒸馏的是完整归因图的结构信息。
- 传统 PRM（Qwen2.5-Math-PRM 等）：需要大量步骤标签或 MC 估计，是黑盒；本 idea 的标签来自模型内部计算，可无标注扩展。

**🧪 验证方案**
- 基准：ProcessBench（步骤错误定位）、PRMBench、GSM8K/MATH 的 BoN 重排；指标：步骤级 AUROC、首错定位准确率、BoN@16 增益、推理延迟。
- 关键假设检验：学生探针与 CRV 分数相关 >0.8；在"高置信错误"子集上 AUROC 显著高于置信度探针；干预实验保持因果一致。
- 对比与消融：CRV 全量、置信探针、黑盒 PRM、去特征身份袋、单探针 vs 门控混合、跨域/跨尺度迁移；RL 中对比结果奖励与 PRM 奖励。

🔑 `mechanistic interpretability` `transcoder` `process reward model` `knowledge distillation` `verification` `attribution graph`

[🔝 top](#top)

---

## 💡 Idea 1.14 — *Self-Probed Redundancy: Answer-Probability Trajectories as a Detector-Free Signal for Decoupled Overthinking Rewards*

| | |
|:--|:--|
| 🎯 **源论文** | **Overthinking Reduction with Decoupled Rewards and Curriculum Data Scheduling** · Jiang et al. · 🎤 ICLR 2026 Oral · [arXiv:2509.25827](https://arxiv.org/abs/2509.25827) |
| 📌 **线索来源** | Appendix E Limitation & Future Work §"First, the NRP detector is implemented as a small auxiliary model (1.5B parameters)." + §"Integrating NRP detection directly into the policy, e.g., via confidence (Yan et al., 2025) or entropy signals (Cui et al., 2025), is a promising future direction but not required for the current solution to work well." |
| 📮 **投稿建议** | 🧪 **ML** · ICLR ＋ 🗣️ NLP · ACL |
| ⭐ Novelty | ★★★☆☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★☆☆☆（7B 级 GRPO，额外开销小） |

**🔍 深入分析**
DeCS 从理论上指出长度奖励在 GRPO 下的两个缺陷：轨迹级优势会错误惩罚**必要的探索 token**，又会无意奖励"部分冗余"；于是把 token 分成"非必要推理片段（NRP）"与其他，分别赋奖励，再用课程批调度保持探索，削减约 50% token 而不掉点。但 NRP 的判定依赖一个外部训练的 1.5B 检测器——它需要标注、是另一个会漂移的模型，并把"什么是冗余"固定为检测器的先验。Limitation 建议把检测并入策略自身的置信/熵信号，但置信与熵并不直接度量"这一段有没有改变答案"。空隙在于：冗余的操作性定义应当是**反事实的**——删掉该段，模型对正确答案的信念不变；而这个量恰恰可以由策略自己便宜地提供：在每个推理段末尾强制解码答案（early-answer probing），得到 p_t(正确答案) 的轨迹，片段的"信息增益"就是 Δp。它同时自然区分了 DeCS 担心的两种情况：探索段的 Δp 可能先降后升（需要用前瞻而非即时变化判断），而重复验证段的 Δp≈0。

**💡 一句话 Idea**
用策略自身在每个推理段末尾的早答概率轨迹定义段级信息增益，把"增益为零的段"作为无需外部检测器的 NRP 掩码接入解耦 token 奖励，并以前瞻增益保护先抑后扬的探索段。

**🛠️ 可能的解决方法**
1. **早答探针**：按段（换行/"Wait"/"Alternatively" 等边界）切分推理；在每个段末插入 `</think>` 并贪心解码最终答案 ≤16 token，记录 p_t = π(正确答案 | 前缀)；对 G=8 条轨迹、平均 30 段，成本约为 rollout 的 10–15%（短解码、KV 复用）。
2. **段级信息增益**：g_t = max_{t'≥t} p_{t'} − p_{t-1}（前瞻增益），使"先降后升"的探索段获得正增益；NRP_t = 1[|g_t| < ε ∧ p_{t-1} > p_thr]（已高置信后仍不改变信念的段）。
3. **解耦奖励**：沿用 DeCS 的 token 级解耦——NRP token 受长度惩罚，非 NRP token 只受结果奖励；再加一个"早停奖励"：若在某段 p_t 已 >0.95 而模型继续生成，则后续 token 的长度惩罚加倍。
4. **防止探针被 hack**：策略可能学会在段末"假装高置信"；对策是探针用冻结的参考模型（训练起点）而非当前策略，或两者取最小值。
5. **课程调度**：沿用 DeCS 的难度课程，但难度直接由 p_0（不思考时的早答概率）定义，省去额外难度估计。

**🧭 与最接近工作的区别**
- DeCS（源论文）：NRP 由外部 1.5B 检测器判定；本 idea 用策略自身的反事实答案概率定义冗余，无需标注与额外模型。
- DEER (Yang et al., 2025)：推理期在"Wait"处试探答案并按置信早停，不训练模型；本 idea 把同类探针变成训练奖励。
- LC-R1 (Cheng et al., 2025) / L1 (Aggarwal & Welleck, 2025)：用长度/压缩奖励或长度控制做 RL，仍是轨迹级长度信号，未区分必要探索与冗余。

**🧪 验证方案**
- 基准：MATH-500、AIME24/25、GPQA、LiveCodeBench；指标：准确率、平均 token 数、准确率—长度 Pareto 前沿、"正确后继续生成"的 token 比例。
- 关键假设检验：早答探针标出的 NRP 与 DeCS 检测器/人工标注的一致率；去掉前瞻增益后准确率下降（证明探索段保护有效）。
- 对比与消融：DeCS、GRPO+长度惩罚、L1、LC-R1；探针用当前策略 vs 冻结参考；ε、p_thr 扫描。

🔑 `overthinking` `efficient reasoning` `early-answer probing` `token-level reward` `GRPO` `information gain`

[🔝 top](#top)

---

## 💡 Idea 1.15 — *Self-Declared Reasoning Graphs: Verifiable Dependency Tags for Structure-Aware Rewards with Revisits and Cycles*

| | |
|:--|:--|
| 🎯 **源论文** | **Characterizing, Evaluating, and Optimizing Complex Reasoning** · Zhang et al. · 🎤 ICML 2026 Oral · [arXiv:2602.08498](https://arxiv.org/abs/2602.08498) |
| 📌 **线索来源** | C.2 Discussion on Self-Refine §"Explicitly modeling cyclic structures would require recovering fully general graphs from arbitrary free-form reasoning traces. This is difficult and brittle in practice, as it demands reliably identifying revisited latent states and long-range dependencies across the trace" + Limitations of Direct Prompt-Based Evaluation §"many reasoning trace pairs differ primarily in how reasoning steps are organized and consolidated, rather than in local step content." |
| 📮 **投稿建议** | 🧪 **ML** · ICML / NeurIPS ＋ 🗣️ NLP · ACL |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
论文提出 ME² 原则（宏观/微观 × 效率/效果）刻画推理质量，把推理轨迹用 LLM 抽取成 DAG 后做成对比较，构建 TRM-Preference 并训练"思维奖励模型"TRM；结果显示结构化比较能分辨直接提示评估分不出的差异（后者有大量平局），且 TRM 作为训练奖励能提升推理。两个 Limitation 指向同一根因：结构是**事后由另一个 LLM 猜出来的**——所以循环/重访无法表示（只能摊成 DAG），依赖抽取器的稳定性，而且每次评估都要再跑一个强模型。空隙是：既然"步骤如何组织"是质量的主要差异，为何不让策略**自己声明**依赖结构？结构奖励（冗余分支、无前提捷径、重访）就成了可精确计算的量，也能表示循环；但自我声明可能撒谎，必须可验证。关键 insight：依赖声明的真伪可以通过**消融一致性**来审计——删除一个未被引用的步骤不应影响被引用步骤的成立，删除被引用的前提应当使之不再成立；抽样审计的成本远低于全量 DAG 抽取。

**💡 一句话 Idea**
让推理模型在每个步骤上自带"引用了哪些前步、属于推导/验证/修订哪类"的轻量标签，以此直接计算含循环的结构奖励，并用随机消融审计惩罚不诚实的依赖声明，使 ME² 式结构优化不再依赖外部 DAG 抽取器。

**🛠️ 可能的解决方法**
1. **标签格式**：每步前缀 `[s7 ← s3,s5 | derive]`、`[s9 ← s7 | verify]`、`[s12 ← s4 | revise(s8)]`（revise 允许指向早先步骤，形成重访边/环）；用少量 SFT（从 TRM-Preference 的 DAG 转换 + 合成）让模型学会格式，推理时标签可剥离不影响用户。
2. **结构奖励（精确计算）**：冗余分支率（无后继且未被最终答案引用的子图占比）、捷径率（derive 步零前提且含新结论）、重访深度（revise 环的长度与次数）、整合度（最终答案祖先集合覆盖率），按 ME² 四象限加权成 r_struct。
3. **消融审计（诚实性奖励）**：每批随机抽 5% 步骤：删去一个被 s_k 引用的前提，让一个冻结 judge 判断 s_k 是否仍成立——应变为不成立；删去未引用步骤——应仍成立。两类检验失败率构成 r_honest 的惩罚；审计成本 ≈ 5% 的 judge 调用。
4. **训练**：GRPO，R = r_correct + λ₁ r_struct + λ₂ r_honest − 长度惩罚；对比直接用 TRM 作奖励。
5. **循环的价值**：分析成功轨迹中 revise 环的统计（与 Idea 1.11 的状态转移互补），检验"少而准的重访"是否是难题成功的标志。

**🧭 与最接近工作的区别**
- 源论文 TRM：结构由外部 LLM 抽取为 DAG，不能表示循环，评估成本高；本 idea 让策略自带可审计结构。
- Graph of Thoughts (Besta et al., 2024)：由外部控制器编排图结构的提示框架，而非模型自我声明并被训练。
- ReasonFlux-PRM (Zou et al., 2025)：轨迹级+步骤级 PRM，仍是黑盒打分，不利用显式依赖。

**🧪 验证方案**
- 基准：MATH-500、AIME、GPQA、LiveCodeBench ＋ TRM-Preference 上的成对一致率；指标：准确率、token 数、结构指标、审计通过率。
- 关键假设检验：自声明图与 LLM 抽取 DAG 的边重合率 >0.8 且在 revise 环上有额外信息；去掉审计后出现"虚假引用"刷分；r_struct 训练后难题上的重访更少但更有效。
- 对比与消融：GRPO 结果奖励、TRM 奖励、无标签 + 事后抽取、去 r_honest、不同审计比例。

🔑 `reasoning structure` `dependency graph` `self-annotation` `reward modeling` `GRPO` `consistency audit`

[🔝 top](#top)

---

## 💡 Idea 1.16 — *Contrastive Input-Grounding Rewards: A Mutual-Information Regularizer Against Template Collapse in Agentic RL*

| | |
|:--|:--|
| 🎯 **源论文** | **RAGEN-2: Reasoning Collapse in Agentic RL** · Wang et al. · 🎤 ICML 2026 Oral · [arXiv:2604.06268](https://arxiv.org/abs/2604.06268) |
| 📌 **线索来源** | 7 Conclusions and Limitations §"A capable model could game the filtering criterion by artificially inflating reward variance, a risk worth monitoring over long training horizons. The method requires reward variance to be a reliable signal proxy, which degrades in sparse or noisy reward environments." + §"Aggressive filtering may narrow exploration coverage; the kept mass requires per-task tuning." |
| 📮 **投稿建议** | 🧪 **ML** · ICML / NeurIPS |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★☆☆☆（标准多轮 RL 流水线上加一个对比 critic） |

**🔍 深入分析**
RAGEN-2 发现多轮智能体 RL 的"安静失败"：熵稳定，推理却退化为与输入无关的流畅模板——**模板坍缩**。作者把推理质量分解为输入内多样性（熵）与跨输入可区分性（MI），证明 MI 与性能相关远强于熵，并提出 SNR 机制：组内奖励方差小时任务梯度被正则项淹没，于是用"SNR 感知过滤"只保留奖励有方差的 prompt。Limitation 把方法的脆弱性说得很清楚：过滤准则可被策略以"人为制造方差"博弈；稀疏/噪声奖励下方差不是好代理；激进过滤会缩小探索覆盖且需逐任务调参。空隙在于：诊断量是 MI，补救却是间接的 prompt 过滤，缺一个**直接优化 MI 的训练项**；熵正则、KL 约束都只作用于单输入分布，挡不住跨输入同质化。关键 insight：I(X;Z) 有现成的可微下界——InfoNCE：训练一个 critic 从批内的 B 个输入中识别推理 z 属于哪一个，critic 的对数得分就是对该样本的"输入接地"奖励；它不依赖奖励方差，在稀疏奖励下仍提供梯度，且不能靠操纵方差来博弈。

**💡 一句话 Idea**
在多轮智能体 RL 的目标里加入基于批内 InfoNCE 的互信息下界奖励（critic 能否从推理中辨认出它所属的输入），直接惩罚输入无关的模板推理，替代易被博弈且依赖奖励方差的 SNR 过滤。

**🛠️ 可能的解决方法**
1. **对比 critic**：f_φ(x, z) 为小型双塔或交叉编码器（可用策略自身冻结的前几层 + 线性头），损失为批内 InfoNCE：−log [e^{f(x_i,z_i)} / Σ_j e^{f(x_j,z_i)}]；r_MI,i = log-softmax 得分，即 I(X;Z) 的样本级下界贡献。
2. **防"抄输入"**：策略可能通过复述观察来刷 MI；对 z 做 n-gram 掩码（与 x 重叠 ≥4-gram 的片段替换为 [MASK]）后再喂 critic，迫使 MI 来自**对输入的加工**而非复制；并限制 critic 只看推理段不看动作。
3. **目标函数**：J = E[R_task] + β·r_MI − KL；β 用目标 MI 水平做自适应（类似熵温度自适应），并在奖励方差为零的 prompt 上仍更新（解决稀疏奖励与"丢弃 prompt"的覆盖问题）。
4. **博弈分析**：critic 与策略交替更新（critic 以较大学习率跟随），并保留一个冻结的 held-out critic 作监控；若在线 MI 上升而 held-out MI 不升，即判定为博弈并提高掩码强度。
5. **多智能体扩展**：每个智能体的 MI 以其**自身观测**为条件，检验模板坍缩是否在多智能体间传播（论文的开放问题）。

**🧭 与最接近工作的区别**
- RAGEN-2（源论文）：用 MI 做诊断、用奖励方差过滤做补救；本 idea 直接优化 MI 下界。
- MMI 解码 (Li et al., 2016)：在对话中用最大互信息目标抑制通用回复，是推理期重排或 seq2seq 目标；本 idea 是 RL 中的对比奖励并处理博弈。
- 熵机制分析 (Cui et al., 2025)：控制策略熵防坍缩，但熵不度量跨输入可区分性，正是源论文指出的盲区。

**🧪 验证方案**
- 基准：RAGEN 的 Sokoban、FrozenLake、WebShop；ALFWorld、τ-bench 子集；指标：任务成功率、MI 代理（论文的）、held-out critic MI、模板率（推理 n-gram 跨输入重复度）。
- 关键假设检验：MI 奖励在稀疏奖励环境（成功率 <5%）仍能避免模板坍缩而 SNR 过滤失效；人为制造奖励方差的对抗策略无法提高 r_MI。
- 对比与消融：PPO/GRPO 基线、SNR 过滤、熵正则、去掩码（观察抄输入）、不同 β、critic 架构。

🔑 `agentic RL` `template collapse` `mutual information` `InfoNCE` `multi-turn` `regularization`

[🔝 top](#top)

---

## 💡 Idea 1.17 — *Prover-as-Navigator: Agentic Repository Exploration with Constraint-Aware Rewards for Context-Dependent Theorem Proving*

| | |
|:--|:--|
| 🎯 **源论文** | **miniCTX: Neural Theorem Proving with (Long-)Contexts** · Hu et al. · 🎤 ICLR 2025 Oral · [arXiv:2408.03350](https://arxiv.org/abs/2408.03350) |
| 📌 **线索来源** | 5 Discussion and future challenges §"Our file-tuning method simply truncates contexts to be within a token budget (1024), which can discard useful contextual information." + §"Although we incorporated premise selection as a means of leveraging cross-file context, our experiments indicate that it does not consistently improve performance, even on datasets with high cross-file dependencies." + §"Models have a tendency to invoke these powerful tactics, and struggle with more explicit step-by-step proofs." |
| 📮 **投稿建议** | 🧪 **ML** · ICLR / NeurIPS ＋ 🗣️ NLP · ACL |
| ⭐ Novelty | ★★★☆☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆（Lean REPL 多轮环境 + 7B 级多轮 RL） |

**🔍 深入分析**
miniCTX 指出真实的形式化证明依赖**新的上下文**——同一仓库里刚定义的概念、引理、注释与文件结构——而 miniF2F 式基准不测这一点；他们的 file-tuning（把前文作为条件）大幅优于只看证明状态的方法，但 Discussion 列出三个未解问题：上下文被硬截断到 1K token；跨文件前提选择不稳定甚至无益；模型倾向滥用强自动化策略，在禁用它们时表现骤降。共同点是：现有方法把上下文当**静态输入**（截断或检索后喂入），而人类用 Lean 时上下文是**探索**出来的——`#check` 类型、打开文件、试一个策略。固定检索器（ReProver/LeanDojo）决定了模型能看什么，但"该看什么"只有在证明过程中才知道；多轮 RL 能让证明器学会导航仓库，且证明助手给出完美的可验证奖励。关键 insight：把"前提选择"从预处理变成策略的**动作**，并把"禁用自动化策略"写进奖励，就能同时解决三个 Discussion 问题。

**💡 一句话 Idea**
把定理证明建模为多轮智能体任务——证明器可以搜索定义、打开文件片段、`#check` 类型、试探策略——用 Lean 的可验证结果和"约束合规"（不得调用被禁用的强自动化）作为奖励做多轮 RL，使模型学会按需探索仓库上下文而非依赖截断或固定检索。

**🛠️ 可能的解决方法**
1. **环境**：基于 Lean REPL / LeanDojo 构建动作空间 {search(query)→候选声明列表, open(path, L1–L2)→源码, check(expr)→类型, tactic(t)→新目标或错误, finish}；观测为工具返回与当前目标；上下文窗口 16K，由策略决定读入内容（替代截断）。
2. **奖励**：终局 +1（证明通过且不含禁用策略，禁用列表按 miniCTX 表 6 设定，如 `simp_all`/`omega`/`aesop` 的受限模式）；每次工具调用 −0.01（鼓励高效探索）；证明通过但违规 → 0.3（部分分，诱导逐步证明）。
3. **训练算法**：多轮 GRPO，组内共享同一定理；用 VinePPO 式的轮次级 MC 价值做 credit assignment（在关键轮次——例如一次 search 之后——分叉续写估计其价值）；冷启动用 miniCTX 训练集 + 从真实仓库提交历史合成的"带上下文证明"做 SFT。
4. **数据与防泄漏**：采用 miniCTX 的时间切分（训练只用截止日期前的仓库状态），新增 Mathlib 近期 PR 作为测试；跨文件依赖比例作为分层变量。
5. **成本控制**：Lean 检查用并行 REPL 池；策略每轮生成 ≤256 token；7B 模型 8 卡数天。

**🧭 与最接近工作的区别**
- ReProver / LeanDojo (Yang et al., 2023)：固定的前提检索器 + 策略生成，检索不随证明过程调整，也不学习何时检索。
- LeanAgent (Kumarappan et al., 2024)：跨仓库的终身学习与课程，仍是检索增强的单步策略生成。
- Rango (Thompson et al., 2025)：面向 Coq 的项目级上下文检索证明合成，检索由启发式而非策略学习；本 idea 用 RL 让探索成为动作，并把约束合规写入奖励。

**🧪 验证方案**
- 基准：miniCTX（含跨文件依赖子集、PFR 难题、禁用自动化设置）、miniCTX-v2 若可用、Mathlib 新 PR；指标：pass@1/pass@32、禁用策略下的通过率、平均工具调用数、读入 token 数。
- 关键假设检验：学习的探索在高跨文件依赖子集上的增益显著大于固定检索；违规部分分设计使"逐步证明"通过率上升；去掉 search 动作后性能回落到 file-tuning 水平。
- 对比与消融：file-tuning、ReProver 检索、全文截断 8K、无工具 RL、无约束奖励、无轮次级 credit。

🔑 `theorem proving` `Lean` `agentic RL` `premise selection` `repository context` `tool use`

[🔝 top](#top)

---

## 💡 Idea 1.18 — *Compress-to-Conjecture: Growing a Lemma Library by MDL-Rewarded Conjecturing in Self-Play Formal Mathematics*

| | |
|:--|:--|
| 🎯 **源论文** | **Learning Formal Mathematics From Intrinsic Motivation** · Poesia et al. · 🎤 NeurIPS 2024 Oral · [arXiv:2407.00695](https://arxiv.org/abs/2407.00695) |
| 📌 **线索来源** | 5 Limitations and Conclusion §"First, even if the agent’s policy improves, its library remains fixed to the definitions and axioms that it starts with. Proofs that do not use lemmas (cut-free proofs in logic) can be exponentially longer than equivalent ones that do, and thus quickly grow beyond the reach of search." + §"With this constraint, our agent most often finds harder conjectures by making the statements longer and more complicated." + Appendix F §"eventually being able to invent new definitions and accumulate a growing library (which Minimo does not, yet)" |
| 📮 **投稿建议** | 🧪 **ML** · NeurIPS / ICML |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆（Peano 环境开源，单机可做；扩展到 Lean 需更多工程） |

**🔍 深入分析**
Minimo 从公理出发自博弈：同一模型既提出猜想（受约束解码保证合法）又做证明搜索，用"难但可证"作为猜想的内在奖励，在群论/命题逻辑/算术三个域上证明长度随迭代增长。Limitation 直指根本瓶颈：库固定不变，没有引理就没有"cut"，证明长度指数膨胀；而且由于难度以证明长度衡量，智能体靠把命题写长写怪来制造"难题"，而不是发现深刻结果。这与人类数学的做法相反——人类通过**积累命名结果**使高层结论能被简洁表述。程序合成早有库学习（DreamCoder、Stitch），LEGO-Prover 也在 miniF2F 上维护技能库，但没有人把库增长放进**从公理起步的猜想—证明自博弈**，更没有把"压缩收益"作为猜想奖励。关键 insight：一个好猜想的价值不在于它的证明有多长，而在于把它加入库后**其他证明能缩短多少**（MDL 压缩增益）；这既是引理价值的操作性定义，又天然惩罚"写长写怪"的伪难题（它们不能压缩任何东西）。

**💡 一句话 Idea**
在 Minimo 的猜想—证明循环中加入库增长步骤——用反合一从已证明的证明树中抽取可复用子证明并命名为引理/定义——并把"加入库后对已有证明与新猜想证明的总描述长度压缩量"作为猜想奖励，让智能体从公理出发自发构建深层理论而非冗长命题。

**🛠️ 可能的解决方法**
1. **库增长（sleep 阶段）**：每轮迭代后对已证明的证明树做反合一/子树频繁模式挖掘（Stitch 风格），候选抽象 = 多次出现的证明片段；对每个候选计算 Δ = Σ_proofs(原长 − 用引理改写后的长度) − 引理自身长度；Δ>0 的加入库并给出类型签名；同样对频繁出现的项模式定义新符号（定义发明）。
2. **MDL 猜想奖励**：猜想 c 被证明后，奖励 r(c) = 压缩增益 Δ(c)（对库中已有证明与近期证明的重写收益）+ 小权重的"难度"项；未被证明的猜想奖励为 0 但保留供下轮；该奖励让"长而怪"的猜想得分为负或零。
3. **策略与价值共享**：沿用 Minimo 的单模型策略/价值，但把库中的引理作为可调用动作加入受约束解码（类型导向合成保证合法），库变大时用检索前 K 个相关引理控制分支因子。
4. **防止库膨胀**：周期性"修剪"——删除近 N 轮未被使用的引理，或合并被更一般引理蕴含的引理（用证明器检查蕴含）。
5. **评估外推**：用人类教材中的标准定理（如群的消去律、逆元唯一性）作为"隐藏目标"，不参与训练，测量智能体能否自发证明它们；再扩展到 Lean（按附录 F 的翻译路径）。

**🧭 与最接近工作的区别**
- Minimo（源论文）：库固定，难度 = 证明长度。
- DreamCoder (Ellis et al., 2021) / Stitch (Bowers et al., 2023)：程序库学习，任务是给定的，不自我提出猜想；本 idea 把库学习与猜想生成通过 MDL 奖励耦合。
- LEGO-Prover (Wang et al., 2024)：在 miniF2F 上维护增长的技能库辅助证明，目标是外部题库而非从公理自博弈发现理论，也没有用压缩作为奖励。

**🧪 验证方案**
- 设置：Peano 的群论/命题逻辑/算术域；指标：隐藏标准定理的证明率、库大小与平均"有效证明长度"（用引理后）、猜想的平均语句长度（期望下降）、理论深度（最终定理依赖链长度）。
- 关键假设检验：MDL 奖励下猜想长度不再单调增长而隐藏定理证明率上升；去掉库增长后退化为 Minimo；库增长但用长度奖励时仍出现"写长写怪"。
- 对比与消融：Minimo、仅库增长、仅 MDL 奖励、不同修剪策略、不同抽象算法。

🔑 `conjecturing` `library learning` `MDL` `self-play` `formal mathematics` `intrinsic motivation`

[🔝 top](#top)
