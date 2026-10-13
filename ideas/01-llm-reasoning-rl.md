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
