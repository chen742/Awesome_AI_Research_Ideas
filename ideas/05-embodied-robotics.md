<a id="top"></a>
# 🤖 Embodied AI & Robotics

> 从 ICRA/IROS 最佳论文、VLA、世界模型 等方向提炼的 idea。
> 符号说明：🎯 源论文 · 📌 线索来源 · ⭐ Novelty · 🚀 Impact · 🧗 Difficulty · 🧪 验证方案 · 🔑 关键词

[⬅️ 返回主页](../README.md)

---

## 💡 Idea 5.1 — *Learned Potentials for Dynamically Composed Control: Bridging Feedback Composition and Foundation Policies*

| | |
|:--|:--|
| 🎯 **源论文** | **No Plan but Everything under Control: Robustly Solving Sequential Tasks with Dynamically Composed Gradient Descent** · Mengers & Brock · 🏆 ICRA 2025 Best Paper (Planning & Control) |
| 📌 **线索来源** | Limitation §"requires hand-specified differentiable task models / sub-objectives" + Future Work §"learning the components" |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
该论文反对"先规划后执行"的范式：把顺序任务表示为一组可微子目标（势函数），运行时根据感知状态**动态组合**这些势的梯度做下降，从而在扰动下无需重规划就能完成多步任务（如开门、取物），显示出极强的鲁棒性。其 Limitation 很诚实：子目标的可微模型是手工设计的，这限制了任务种类；而当前的通用机器人策略（π0、OpenVLA、Diffusion Policy）恰恰相反——能从数据学到广泛技能，但是黑盒、无法在执行中按反馈组合。两条线的交点是空白：**把基础策略蒸馏成一组可组合的、可微的势函数**，让 VLA 的广度与动态组合的鲁棒性结合。扩散/流匹配策略提供了天然入口：其学到的 score 函数本身就是动作空间上的梯度场。

**💡 一句话 Idea**
把流匹配/扩散类机器人策略分解为按子目标条件化的 score 场，使之成为可动态组合的学习型"势"，在执行期按感知反馈加权组合这些场，实现无需重规划的鲁棒长程操作。

**🛠️ 可能的解决方法**
1. **子目标条件化训练**：对示教数据用 VLM 自动切分为语义子目标（"够到把手"、"旋转"、"拉开"），训练一个子目标条件化的流匹配策略 v_θ(a, o, g)，每个 g 对应一个动作空间上的向量场。
2. **组合规则**：运行时维护每个子目标的"激活度" w_g(o)（由一个小的进度估计器从观测预测，类似论文中的"everything under control"的反馈门控），执行动作场 Σ_g w_g·v_θ(·, o, g)；向量场的加权和在 score 组合意义下近似产品分布采样（compositional diffusion 的已有理论可直接套用）。
3. **稳定性约束**：对每个 g 加入 Lyapunov 风格的正则（场在子目标完成区域附近收敛），保证组合后不会在两个子目标之间振荡；可用 contrastive 的成功/失败片段训练。
4. **恢复行为天然出现**：当扰动使进度回退，w_g 自动重新激活早期子目标的场，无需显式重规划。

**🧪 验证方案**
- LIBERO-long、RoboCasa 的长程任务 + 真实机械臂上的扰动实验（抽走物体、推门回去）；
- 指标：成功率、扰动下的恢复率、无需重规划的比例；
- 对比：π0 / Diffusion Policy 直接执行、LLM 重规划、原论文手工势。

🔑 `compositional control` `flow matching policy` `potential fields` `robust manipulation` `VLA`

[🔝 top](#top)

---

## 💡 Idea 5.2 — *Which Demonstrations Matter? In-Run Data Shapley for Curating Cross-Embodiment Robot Pretraining Mixtures*

| | |
|:--|:--|
| 🎯 **源论文** | **Robo-DM: Data Management for Large Robot Datasets** · Chen et al. (Goldberg Lab) · 🏆 ICRA 2025 Best Paper (Robot Learning) ＋ **Data Shapley in One Training Run** · Wang et al. · 🏅 ICLR 2025 Honorable Mention · [arXiv:2406.11011](https://arxiv.org/abs/2406.11011) |
| 📌 **线索来源** | Robo-DM Future Work §"dataset selection and curation beyond storage/compression"；In-Run Shapley Limitation §"only tested on LM pretraining; extension to other modalities" |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
Robo-DM 解决的是"机器人数据太大"（OXE 级别数据的存储、压缩、加载）的工程问题，并指出下一步是**数据选择**：跨本体（cross-embodiment）预训练里混合比例目前靠人工（如 OpenVLA、π0 的数据配比都是手工调出来的），而且有大量低质/冗余示教。另一边，In-Run Data Shapley 证明了可以在**一次训练运行中**以几乎零额外成本估计每个训练样本对目标损失的 Shapley 贡献（通过一阶/二阶梯度点积），解决了 Shapley 需要重训的问题，但只在语言模型上验证。两者的交点是一个具体且有价值的问题：**对一条机器人示教（或一个数据集/本体），它对目标机器人任务的贡献是多少？** 机器人数据天然是异构的（不同本体、相机、控制频率），负迁移严重，正是 Shapley 值最能发挥作用的场景。

**💡 一句话 Idea**
把单次运行的 Data Shapley 推广到序列化、多本体的机器人示教数据，在 VLA 预训练过程中在线估计每条示教/每个数据集对目标任务的贡献，并据此动态重加权混合比例与剔除有害示教。

**🛠️ 可能的解决方法**
1. **粒度定义**：以"示教片段（episode）"为基本单位，目标集为目标机器人的少量验证示教；贡献 = 一次运行中逐步累积的 ⟨∇ℓ_episode, ∇ℓ_val⟩（一阶）与 Hessian-vector 修正（二阶，低频计算）。
2. **动作模态适配**：VLA 的动作头（离散 token 或流匹配）损失不共享尺度，对两类损失的梯度分别归一化后再做点积；对流匹配策略，使用固定的时间步采样以降低梯度噪声。
3. **在线重加权**：每 K 步按数据集级 Shapley 聚合更新采样概率（softmax 带温度 + 下限以防完全丢弃某本体），并对 episode 级贡献持续为负的样本打"有害"标签剔除。
4. **可解释产物**：输出每个数据集对每个目标本体的贡献矩阵，可直接指导未来数据采集。

**🧪 验证方案**
- OXE 子集 → 目标为 Bridge/DROID/自有机械臂；
- 指标：目标任务成功率 vs. 手工配比（OpenVLA/π0 配比）、随机、Re-Mix（分布鲁棒加权）；
- 验证"剔除负贡献示教"后性能是否上升，以及贡献矩阵与人类专家判断的一致性。

🔑 `robot data curation` `data Shapley` `cross-embodiment` `VLA pretraining` `data mixture`

[🔝 top](#top)

---

## 💡 Idea 5.3 — *Geometry-Consistent World Models: Rewarding Generative Simulators for Being 3D-Consistent*

| | |
|:--|:--|
| 🎯 **源论文** | **Learning Interactive Real-World Simulators (UniSim)** · Yang et al. · 🏆 ICLR 2024 Outstanding Paper · [arXiv:2310.06114](https://arxiv.org/abs/2310.06114) ＋ **Genie: Generative Interactive Environments** · Bruce et al. · 🏆 ICML 2024 Best Paper · [arXiv:2402.15391](https://arxiv.org/abs/2402.15391) |
| 📌 **线索来源** | UniSim Limitation §"hallucinated physics; limited memory / long-horizon consistency"；Genie Limitation §"hallucinates unrealistic futures; 16-frame memory" |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
UniSim 与 Genie 展示了视频生成模型可以作为可交互的世界模拟器并用于训练策略，但两篇 Limitation 都指向同一个问题：模拟器**几何与物理不一致**——物体在视角变化后形状漂移、消失或穿模，长时程下场景"遗忘"。这直接限制了"在生成的模拟器里训练策略再迁移到真实世界"的可信度。当前主流做法是靠更多数据与更大模型"隐式"学到一致性。与此同时，前馈式 3D 几何模型（VGGT，CVPR 2025 Best Paper；D4RT，CVPR 2026 Best Paper）已能从若干帧直接回归出相机、深度、点图，几十毫秒内完成——它们提供了一个**可计算的、可微/可打分的几何一致性判据**，却从未被用作世界模型的训练信号。

**💡 一句话 Idea**
用前馈 3D 几何模型作为"几何裁判"，对视频世界模型生成的片段计算多视角几何一致性与物体持久性分数，并以此作为奖励对世界模型做 RL 微调，使生成的模拟器在长时程与视角变化下保持 3D 一致。

**🛠️ 可能的解决方法**
1. **几何裁判**：把生成片段（含动作条件下的相机运动）送入 VGGT/D4RT，得到逐帧相机位姿与点图；定义 (a) 重投影一致性：相邻帧点图经估计位姿变换后的重投影误差；(b) 物体持久性：用跟踪器（SAM 2）在片段内跟踪物体并检查其 3D 轨迹的平滑性与体积守恒；(c) 动作—相机一致性：估计的相机运动与输入动作的匹配度。
2. **奖励与优化**：对同一初始帧与动作序列采样多个片段，以上述分数（归一化、加权）为奖励做 GRPO/DPO 风格的视频扩散微调（已有 VideoDPO、DanceGRPO 等成熟的视频扩散 RL 框架可直接复用），任务保真度用原始重建损失兜底。
3. **长时程记忆**：在世界模型中加入显式的 3D 记忆（由几何裁判在线构建的稀疏点云），作为后续帧生成的条件，使"看过的区域"在回看时保持一致。
4. **策略评估闭环**：在微调后的模拟器里训练策略，测真实迁移是否提升——这是最终的有效性判据。

**🧪 验证方案**
- 数据：BridgeData V2 / DROID 视频 + 动作；
- 指标：几何一致性分数、人类一致性评分、生成片段上的 VLA 评估与真实机器人成功率的相关性（sim-to-real rank correlation）；
- 对比：UniSim/Genie 风格基线、仅更大数据、显式 3D 高斯世界模型。

🔑 `world model` `video generation` `3D consistency` `feed-forward geometry` `RL fine-tuning` `sim-to-real`

[🔝 top](#top)
