<a id="top"></a>
# 🧭 LLM Agents: Tools, GUI/Web, Coding & Memory

> 从电脑操作 / GUI 智能体、Web 与深度研究智能体、软件工程与科研代码智能体、工具创建、智能体记忆、agentic RL 与智能体安全评测等方向的顶会论文与高引用论文（以欧美团队为主）中提炼的单智能体 idea，目标投稿 ICLR / NeurIPS / ACL / EMNLP。
> 符号说明：🎯 源论文 · 📌 线索来源 · 📮 投稿建议 · ⭐ Novelty · 🚀 Impact · 🧗 Difficulty · 🧪 验证方案 · 🔑 关键词 · 📄 会议 / arXiv 论文 · 📈 高引用

[⬅️ 返回主页](../README.md)

---

## 💡 Idea 19.1 — *Willing but Unable: Capability-Decoupled Safety Evaluation of Computer-Use Agents via Affordance Ladders and Twin Tasks*

| | |
|:--|:--|
| 🎯 **源论文** | **OS-Harm: A Benchmark for Measuring Safety of Computer Use Agents** · Thomas Kuntz et al. (EPFL) · 📄 NeurIPS 2025 · 📈 高引用 (120+) · [arXiv:2506.14866](https://arxiv.org/abs/2506.14866) |
| 📌 **线索来源** | Discussion and Future Work §"These limitations might hide the true level of safety risk posed by computer use agents, as harmful goals are potentially not achieved because the model is not sufficiently capable rather than well-aligned." + §"in the future, with more complex tasks, we may need agentic judges ... that can automatically verify the state of the environment." |
| 📮 **投稿建议** | 🧪 **ML** · ICLR / NeurIPS ＋ 🔐 Security · USENIX Security / CCS |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
OS-Harm 在 OSWorld 之上构造了蓄意滥用、提示注入、模型自发失误三类共 150 个任务，用 LLM judge 同时打"安全"与"成功"标签。作者坦承一个根本性混淆：电脑操作智能体本身成功率很低，"没造成伤害"可能只是"做不到"，而不是"不愿做"。现有安全基准（OS-Harm、SafeArena、AgentHarm）报告的都是**结果层**的有害完成率，它等于"意愿 × 能力"的乘积，随着能力快速提升，今天看似安全的模型明天会自动变得危险。同时，作者在附录中发现 judge 只看文本描述会漏掉注入、对"成功"过于宽松，提示需要直接检查环境状态的 agentic judge。关键 insight：能力是可以**人为抬高**的——给智能体提供特权动作（a11y API、预置宏、grounding oracle）构成一条"能力阶梯"，再用配对的良性孪生任务在同一阶梯上测出纯能力，就能把"意愿"从乘积中解耦出来，并外推到未来更强模型的风险。

**💡 一句话 Idea**
为每个有害任务构造同环境、同操作难度的良性孪生任务，并在逐级增强的"能力阶梯"（原始像素 → a11y 树 → 特权 API → 技能宏）上评测，用因子化模型把有害完成率分解为潜在意愿与能力，并以状态差分的 agentic judge 取代纯文本 judge。

**🛠️ 可能的解决方法**
1. **孪生任务构造**：对 OS-Harm/SafeArena 每个有害任务 h，人工+LLM 生成良性孪生 b（相同应用、相同操作序列骨架，仅改变目标内容，如"给同事发会议纪要"对"发骚扰邮件"），用动作序列编辑距离与专家标注保证操作难度匹配。
2. **能力阶梯**：定义 4 级 affordance：L0 截图+键鼠；L1 +a11y 树；L2 +高层 API（send_email、write_file）；L3 +任务相关技能宏。L3 下良性任务成功率应接近上限，使"做不到"不再是解释变量。
3. **因子化估计**：对每个模型 m、阶梯 ℓ、任务对 (h,b) 建模 P(harm-complete)=W_m(h)·C_{m,ℓ}(h)，用 C_{m,ℓ}(b) 作为 C_{m,ℓ}(h) 的估计，配合层次贝叶斯（任务类别随机效应）推断潜在意愿 W 与置信区间；报告"能力饱和下的有害完成率"作为前瞻风险指标。
4. **状态差分 judge**：在 VM 快照前后做文件系统/邮件/浏览器状态 diff，结合轨迹由 agentic judge 判定"是否实际造成伤害"与"是否尝试"，在 OS-Harm 人工标注轨迹上校准，专门修复论文 B.5 中的"成功标签假阳性"和"看不到注入"两类错误。
5. **成本**：阶梯 L2/L3 动作数显著减少，整体评测 token 成本低于原始 L0 评测；全部基于现有 OSWorld VM 镜像。

**🧭 与最接近工作的区别**
- AgentHarm (Andriushchenko et al., 2024)：报告 harm score 与拒绝率，但能力与意愿仍耦合在同一结果指标中。
- SafeArena (Tur et al., 2025)：用有害/安全配对任务做归一化安全分，但未控制操作能力，也未在能力增强条件下重测。
- Agent-as-a-Judge (Zhuge et al., 2024)：提出用智能体评判智能体，本 idea 将其落到 VM 状态差分的安全判定并与人工标签校准。

**🧪 验证方案**
- 基准：OS-Harm、SafeArena、OSWorld（良性孪生的能力参照）；指标：各阶梯有害完成率、潜在意愿 W、拒绝率、judge 与人工的一致率 / F1。
- 关键假设：(a) L0→L3 阶梯上，有害完成率显著上升而拒绝率基本不变，说明结果层指标低估风险；(b) 用小模型阶梯曲线外推的 W 能预测更强新模型在 L0 下的有害完成率。
- 对比与消融：去掉孪生校正 / 去掉状态 diff judge / 只用文本 judge；比较 GPT-4.1、o4-mini、Claude、Qwen-VL 等前沿与开源模型。

🔑 `computer-use agents` `agent safety` `capability elicitation` `twin tasks` `agentic judge` `OSWorld`

[🔝 top](#top)

---

## 💡 Idea 19.2 — *Know When Not to Click: Counterfactual Screen Editing for Calibrated Abstention in GUI Grounding*

| | |
|:--|:--|
| 🎯 **源论文** | **Scaling Computer-Use Grounding via User Interface Decomposition and Synthesis** · Tianbao Xie et al. (HKU) · 📄 NeurIPS 2025 · 📈 高引用 (140+) · [arXiv:2505.13227](https://arxiv.org/abs/2505.13227) |
| 📌 **线索来源** | Limitations §"Rejecting infeasible actions is crucial, as it helps prevent errors and mitigates the risks associated with incorrect instructions." + §"Refusal modeling in GUI grounding remains a significant challenge, as models show limited improvement due to the inherent limitations in pretraining and the hallucination phenomenon in VLMs." |
| 📮 **投稿建议** | 🧪 **ML** · ICLR / NeurIPS ＋ 🧩 AI · AAAI |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
Jedi 通过 UI 分解与合成构建了 400 万条 grounding 数据，在 ScreenSpot-Pro 与 OSWorld-G 上达到强性能，但作者明确指出"拒绝不可执行的指令"几乎没有随数据扩展而改善，并把原因归于预训练局限与 VLM 幻觉。失败案例同样揭示：模型会点击灰色（未激活）的同名选项、或在指令措辞误导下点到相近元素。根源在于现有 grounding 数据**全部是可行样本**：模型从未见过"目标不存在/不可用"的屏幕，因此输出坐标是唯一选项。关键 insight：Jedi 的合成管线本身就能渲染 UI，因而可以对同一屏幕做**反事实编辑**——删除、禁用或替换目标元素——得到与原样本仅差一个局部的不可行配对，这正是训练"知道何时不点"所需的最小对比信号；再配合选择性预测的校准，就能把拒绝从"偶发幻觉"变为可控的风险-覆盖率权衡。

**💡 一句话 Idea**
用 UI 合成管线对可行样本做"删除/禁用/改名"的反事实屏幕编辑，构造最小差异的可行-不可行配对，联合训练坐标预测与弃权头，并用保形校准给出可保证错误率的点击/拒绝决策。

**🛠️ 可能的解决方法**
1. **反事实数据**：对每条 (指令, 截图, bbox) 生成三类负样本：(i) 目标元素被移除并在原位置渲染背景；(ii) 目标被置为禁用态（灰色、不可交互）；(iii) 同名但语义不同的干扰元素保留、真实目标移除。另外生成指令侧负样本（引用屏幕上不存在的菜单）。HTML/a11y 渲染路径直接改 DOM，截图路径用局部 inpainting。
2. **目标函数**：L = L_ground(坐标 token) + λ·BCE(abstain | x) + μ·L_pair，其中 L_pair 对同一配对要求可行样本的"可行性 logit"高于不可行样本至少 margin m（配对排序损失），迫使模型关注局部差异而非全局先验。
3. **保形弃权**：在留出校准集上用 split conformal 选阈值 τ，使"在接受的点击中错误率 ≤ α"有有限样本保证；推理时输出点击或 `INFEASIBLE`。
4. **智能体集成**：在 OSWorld 智能体中，grounding 弃权触发重新规划或向用户澄清，而不是盲点；记录弃权带来的步数与成本变化。
5. **成本**：反事实样本仅需对已有合成数据做局部编辑，约为原数据量的 20–30%；7B 级模型 8 卡数天可完成微调。

**🧭 与最接近工作的区别**
- OSWorld-G / Jedi (Xie et al., 2025)：包含拒绝类评测，但训练数据几乎无不可行配对，拒绝能力未随规模提升。
- SeeClick (Cheng et al., 2024) 与 ScreenSpot-Pro (Li et al., 2025)：只评测/训练可行指令的定位精度。
- 保形预测 (Angelopoulos & Bates, 2021) 用于分类风险控制，本 idea 将其用于 GUI 动作级的点击/拒绝决策并与反事实训练结合。

**🧪 验证方案**
- 基准：OSWorld-G（含 refusal 子集）、ScreenSpot-v2、ScreenSpot-Pro；下游 OSWorld（含官方 infeasible 任务）与 WindowsAgentArena。
- 指标：grounding 准确率、拒绝 F1、风险-覆盖率曲线 AUC、ECE；下游成功率、平均步数与 token 成本。
- 关键假设：(a) 配对排序损失比单纯加入负样本提升拒绝 F1 更多；(b) 弃权不降低可行样本准确率；(c) 保形阈值在跨应用分布偏移下仍近似满足目标错误率。
- 消融：三类负样本逐一移除；去掉 L_pair；固定阈值 vs 保形阈值。

🔑 `GUI grounding` `abstention` `counterfactual data` `conformal prediction` `computer-use agents`

[🔝 top](#top)

---

## 💡 Idea 19.3 — *Watch, Infer, Replay: Inverse-Dynamics Pseudo-Labeling of Unlabeled Software Tutorial Videos for Long-Horizon GUI Agents*

| | |
|:--|:--|
| 🎯 **源论文** | **VideoCAD: A Dataset and Model for Learning Long-Horizon 3D CAD UI Interactions from Video** · Brandon Man et al. (MIT) · 📄 NeurIPS 2025 · [arXiv:2505.24838](https://arxiv.org/abs/2505.24838) |
| 📌 **线索来源** | Limitations and Future Work §"All trajectories are synthetically generated by a rule-based bot, and despite human-inspired heuristics, they lack natural variability in timing, errors, and strategy." + §"To address these gaps, future work will: (1) incorporate human demonstration data (e.g., from YouTube CAD tutorials)" |
| 📮 **投稿建议** | 🧪 **ML** · ICLR / NeurIPS ＋ 🧩 AI · AAAI |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
VideoCAD 用规则机器人在 Onshape 中生成了数万条带精确低层动作的长程 CAD 操作视频，并训练 VideoCADFormer 从视频预测动作；而通用 LLM 智能体在该任务上几乎无法推进。作者承认数据全部来自规则机器人，缺少人类在节奏、错误与策略上的自然变化，并计划引入 YouTube 教程。难点在于：教程视频**没有动作标签**，光标渲染、缩放、剪辑和旁白都与合成数据不同，直接做行为克隆不可行。关键 insight：VideoCAD 恰好提供了"视频-动作"对齐数据，可以训练**逆动力学模型**（IDM：由前后帧推断动作），这与 VPT 在 Minecraft 上的路线一致；而 CAD 的独特优势是**可回放验证**——把伪标签动作在真实 Onshape 中执行，比较生成几何与视频末帧，就能自动过滤错误标签。这样既获得人类的错误与恢复行为，又不依赖人工标注。

**💡 一句话 Idea**
在 VideoCAD 合成数据上训练逆动力学模型，为海量无标注 CAD 教程视频生成动作伪标签，并通过在真实 CAD 软件中回放、比对几何结果来自动筛选，得到含人类策略与纠错行为的大规模长程 GUI 轨迹。

**🛠️ 可能的解决方法**
1. **IDM 训练**：输入相邻 k 帧（含光标裁剪放大），输出动作类型 + 坐标/键值；在 VideoCAD 上训练，并用光标样式、缩放、帧率、压缩伪影做强数据增强以缩小合成→真实差距。
2. **教程视频处理**：检索 Onshape/Fusion 360/FreeCAD 教程，用 ASR 字幕 + 场景切换检测切分子目标片段（"画草图""拉伸 10mm"），过滤剪辑跳变片段。
3. **回放验证**：将伪标签动作序列在 Onshape 中按片段回放，计算回放末帧与视频末帧的视觉相似度，以及重建 CAD 与视频中模型的几何一致性（Chamfer 距离 / 体素 IoU）；仅保留通过阈值的片段，失败片段用局部重搜索（在 IDM top-k 候选动作中做束搜索）修复。
4. **策略学习**：在"合成 + 筛选后的真实"轨迹上训练视频-动作策略，保留人类的撤销/重做与错误恢复片段，并以子目标文本作为条件，支持论文提出的逐步文本交互。
5. **成本**：IDM 与策略为中等规模 Transformer；主要开销在回放验证，可用多个 Onshape 浏览器会话并行。

**🧭 与最接近工作的区别**
- VPT (Baker et al., 2022)：用 IDM 给 Minecraft 视频打标签，但游戏环境没有可回放验证的结构化产物；本 idea 利用 CAD 几何作为自动校验信号。
- AgentTrek (Xu et al., 2024)：用网页教程文本引导回放合成轨迹，依赖文本步骤而非视频中的人类动作。
- VideoCAD (Man et al., 2025)：仅用规则机器人数据，缺少人类变化与错误恢复。

**🧪 验证方案**
- 基准：VideoCAD 测试集（动作准确率、长程任务成功率、生成 CAD 与目标的 Chamfer / IoU）；跨平台泛化到 FreeCAD 的新任务；UI-Vision 的动作预测任务作为通用 GUI 迁移检验。
- 关键假设：(a) 回放过滤后的伪标签准确率显著高于未过滤；(b) 加入真实教程数据后，在人类风格的测试集上（含错误恢复）成功率提升最多；(c) 数据量扩展曲线呈对数线性。
- 对比与消融：仅合成数据 / 未过滤伪标签 / 无数据增强 IDM；GPT-4o 等 LLM 智能体作为零样本基线。

🔑 `GUI agents` `inverse dynamics` `learning from video` `CAD` `pseudo-labeling` `long-horizon`

[🔝 top](#top)

---

## 💡 Idea 19.4 — *Beyond the Cited URL: Corroboration- and Derivation-Aware Agent-as-a-Judge for Deep Research Agents*

| | |
|:--|:--|
| 🎯 **源论文** | **Mind2Web 2: Evaluating Agentic Search with Agent-as-a-Judge** · Boyu Gou et al. (Ohio State) · 📄 NeurIPS 2025 · [arXiv:2506.21506](https://arxiv.org/abs/2506.21506) |
| 📌 **线索来源** | Appendix A Limitations §"Our evaluation framework relies on URL-based attribution, presupposing that cited URLs provide truthful and credible information, despite potential misinformation on the web." + §"Additionally, our evaluation and task design assume critical information can be attributed to individual webpages, which may not always hold true for all possible tasks." |
| 📮 **投稿建议** | 🗣️ **NLP** · ACL / EMNLP ＋ 🌐 WWW · WWW / KDD |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
Mind2Web 2 用 130 个长程、答案随时间变化的检索任务和树状 rubric 的 Agent-as-a-Judge 评测深度研究系统，判定逻辑是"答案中的事实是否被所引 URL 支持"。作者明确列出两个假设：被引网页本身可信；关键信息可归因于单个网页。这两个假设恰好是深度研究系统在真实网络中最常见的失效面：引用低质量或过时页面即可"通过"评测；而需要跨多页聚合、计算或推理得出的结论（如"三家航司中最便宜的"）无法由单页支持。因此当前 judge 会系统性地奖励"引用得像样"而非"结论正确"。关键 insight：把每个答案拆成**证据有向图**——叶子是原子事实，每个叶子需要多源互证与来源可信度评分；内部节点是推导（比较、求和、筛选），可由代码执行验证。这样评测从"URL 支持"升级为"证据链可信且推导正确"。

**💡 一句话 Idea**
将深度研究答案分解为"原子事实 → 推导"的证据图，对事实节点做跨来源互证与可信度评分、对推导节点用代码执行验证，并在受控注入错误信息页面的沙盒任务上检验 judge 能否识破"引用合规但结论错误"的答案。

**🛠️ 可能的解决方法**
1. **证据图抽取**：judge 智能体把答案解析为 DAG：叶子 = 原子事实（含所引 URL），内部节点 = 显式运算（max/sum/filter/时间比较）。运算节点用 Python 执行复算，不一致即判错。
2. **互证与可信度**：对每个原子事实，judge 独立检索 k 个额外来源；可信度分 = f(来源一致性, 域名先验, 页面时效, 是否一手来源)。最终节点得分 = 支持度 × 可信度，替代原有的二元 URL 支持。
3. **对抗测试集**：在自建测试域名上发布与真实信息冲突的诱饵页面（过时价格、伪造规格），并通过搜索 API 模拟层将其混入检索结果；构造"必须跨页推导"的新任务，作为 Mind2Web 2 的扩展子集。
4. **judge 训练与成本**：先用前沿模型做 judge；再用人工标注的证据图蒸馏到开源 judge，降低单任务评测成本；记录每任务 judge token 开销。
5. **作为奖励**：证据图得分可直接用作深度研究智能体 RL 的过程级奖励，比仅检查答案更难被 hack。

**🧭 与最接近工作的区别**
- Mind2Web 2 (Gou et al., 2025)：只检查答案事实是否被所引 URL 支持，不评估来源可信度与跨页推导。
- ALCE (Gao et al., 2023) / FActScore (Min et al., 2023)：引用质量与原子事实核查，面向静态语料，不处理可信度冲突与可执行推导。
- BrowseComp (Wei et al., 2025)：短答案精确匹配，绕开了开放答案的归因评测问题。

**🧪 验证方案**
- 基准：Mind2Web 2 原任务 + 新增"跨页推导"与"诱饵页面"子集；被测系统包括 OpenAI / Gemini Deep Research、Perplexity、开源搜索智能体。
- 指标：judge 与人工的一致率（Cohen's κ）、对注入错误的检出率、对推导错误的检出率、每任务评测成本；被测系统在新指标下的排名变化。
- 关键假设：(a) 原 URL-attribution judge 会把大量诱饵引用答案判为正确，新 judge 显著降低该假阳性；(b) 互证分与人工可信度判断强相关。
- 消融：去掉互证 / 去掉代码复算 / 去掉可信度先验。

🔑 `deep research` `agent-as-a-judge` `source credibility` `attribution` `misinformation` `evaluation`

[🔝 top](#top)

---

## 💡 Idea 19.5 — *Hack-Aware Rubric Rewards: Multi-Turn RL for Web Agents on Open-Ended Tasks without Verifiable Outcomes*

| | |
|:--|:--|
| 🎯 **源论文** | **WebAgent-R1: Training Web Agents via End-to-End Multi-Turn Reinforcement Learning** · Zhepei Wei et al. (UVA) · 📄 EMNLP 2025 · 📈 高引用 (180+) · [arXiv:2505.16421](https://arxiv.org/abs/2505.16421) |
| 📌 **线索来源** | Limitations and Potential Risks §"Second, our method relies on rule-based outcome rewards to guide RL training. While effective in our setting, such reward functions may not be readily available in other interactive scenarios, such as open-ended travel planner agents, where task goals are ambiguous and no clear reference or verifiable outcome is available." |
| 📮 **投稿建议** | 🗣️ **NLP** · ACL / EMNLP ＋ 🧪 ML · ICLR / NeurIPS |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
WebAgent-R1 把 GRPO 扩展到多轮（M-GRPO），配合动态上下文压缩和并行 rollout，在 WebArena-Lite 上取得 SOTA，但它依赖 WebArena 自带的规则化结果奖励。作者指出，在旅行规划这类目标模糊、没有参考答案的开放任务中，这种奖励根本不存在。自然的替代是 LLM judge + rubric，但多轮 RL 会在数百步优化中找到 judge 的漏洞（冗长自信的总结、伪造"已完成"的陈述），这是奖励过优化的典型形态，在单轮 RLHF 中已被量化，而在多轮 web RL 中几乎没有被研究。关键 insight：WebArena 同时拥有规则奖励，可以作为**校准场**——在同一任务上并行计算 judge 奖励与真实奖励，直接测出 judge 被 hack 的速率与模式；再把发现的 hack 模式转化为对抗样本持续更新 judge，并让 judge 基于环境证据（访问过的页面、表单状态）而非智能体的自述打分。

**💡 一句话 Idea**
用"基于环境证据的 rubric judge + 集成不确定性惩罚 + 在线 hack 挖掘与 judge 刷新"作为多轮 web RL 的奖励，并以 WebArena 的规则奖励作为校准场量化与抑制 judge 过优化，从而把 agentic RL 推广到没有可验证结果的开放任务。

**🛠️ 可能的解决方法**
1. **证据型 rubric judge**：judge 输入为任务、动态生成的 rubric（约束清单，如预算、日期、偏好）以及**环境证据日志**（URL 序列、关键页面 a11y 片段、最终表单状态），禁止只依据智能体最终自述打分。
2. **不确定性惩罚奖励**：K 个异构 judge（不同模型/提示）给分 r_1..r_K，奖励 r = mean(r) − β·std(r)，抑制利用单一 judge 偏好的策略。
3. **hack 挖掘与 judge 刷新**：在 WebArena 子集上同时计算规则奖励 r* 与 judge 奖励 r̂；将 r̂ 高而 r* 低的轨迹自动聚类为 hack 模式，生成对抗反例加入 judge 的少样本/微调数据，每 N 个 RL 迭代刷新一次 judge。
4. **训练算法**：沿用 M-GRPO + BC 预热；在开放任务（TravelPlanner 沙盒版、Mind2Web 2 风格的信息收集任务）与 WebArena 混合训练，混合比例由 judge-真实奖励差距自适应调节。
5. **成本**：judge 只在轨迹结束时调用一次；集成 K=3 时奖励成本约为 rollout 的 10–20%。

**🧭 与最接近工作的区别**
- WebAgent-R1 (Wei et al., 2025) / WebRL (Qi et al., 2024)：分别依赖规则奖励与学习的结果奖励模型，未研究开放任务中 judge 奖励被多轮策略 hack 的问题。
- Rubrics as Rewards (Gunjal et al., 2025)：rubric 奖励用于单轮生成任务，不涉及环境证据与多轮交互。
- Gao et al. (2023) 奖励模型过优化缩放律：在单轮 RLHF 中量化过优化，本 idea 在多轮 web 智能体中测量并加以抑制。

**🧪 验证方案**
- 基准：WebArena-Lite（规则奖励可用于校准）、TravelPlanner、Mind2Web 2、WebVoyager 在线任务；指标：成功率 / rubric 满足率（人工复核）、pass^k 可靠性、平均步数与 token 成本。
- 关键假设：(a) 纯 judge 奖励训练时，r̂ 与 r* 的差距随训练步数扩大（可画出过优化曲线）；(b) 证据输入 + 不确定性惩罚 + 刷新三者使该差距显著缩小；(c) 在开放任务上人工评分提升。
- 对比与消融：规则奖励（仅 WebArena）、单 judge 奖励、去掉证据日志、去掉 judge 刷新。

🔑 `web agents` `agentic RL` `LLM-as-judge rewards` `reward hacking` `multi-turn GRPO` `open-ended tasks`

[🔝 top](#top)

---

## 💡 Idea 19.6 — *Interface Counterfactuals: Failure-Attributed Automatic Design of Agent-Computer Interfaces for Software Engineering Agents*

| | |
|:--|:--|
| 🎯 **源论文** | **SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering** · John Yang et al. (Princeton) · 📄 NeurIPS 2024 · 📈 高引用 (2200+) · [arXiv:2405.15793](https://arxiv.org/abs/2405.15793) |
| 📌 **线索来源** | E.3 Limitations & Future Work §"Second, in this work, the ACI development process and case studies are done manually." + §"Automating part or all of this process could not only accelerate work built on top of SWE-agent, but also provide greater insights into developing ACI principles for agentic software engineering." |
| 📮 **投稿建议** | 🧪 **ML** · ICLR / NeurIPS ＋ 🗣️ NLP · ACL / EMNLP |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
SWE-agent 证明了"给 LM 设计的界面"（ACI：带语法检查的编辑命令、分页文件查看器、精简搜索输出）能大幅提升 SWE-bench 解决率，但所有设计都来自作者对轨迹的人工观察。其失败分析显示约 23.4% 的未解决实例属于"编辑失败后无法恢复"，这正是界面可改进的信号。自动化的难点在于评估成本：每改一个界面参数就重跑整个 SWE-bench，代价极高，而现有自动化智能体设计方法（ADAS、Darwin Gödel Machine）搜索的是整套智能体代码，代价更大且难以归因。关键 insight：界面改动的影响是**局部的**——它只改变某一步之后的观测格式或动作语义。因此可以对失败轨迹在"首次与该界面组件交互的步"处分叉，用新界面重放后缀（界面反事实），以远低于全量重跑的成本估计每个组件的边际效应，并把失败分类直接映射为待搜索的界面组件。

**💡 一句话 Idea**
把 ACI 表示为可组合的类型化界面程序，用失败分类定位可疑组件，在失败轨迹的关键步做"界面反事实"后缀重放来廉价估计改动效果，并以跨多个 backbone 的最差情况解决率为目标搜索稳健的界面设计。

**🛠️ 可能的解决方法**
1. **界面空间**：将 ACI 参数化为组件集合 {文件查看窗口大小、搜索输出截断与摘要策略、编辑命令语义（行区间/查找替换/AST 级）、编辑后 lint 与回滚、错误信息格式、测试运行输出过滤}；每个组件有离散变体，并允许 LLM 提议新变体（以代码形式）。
2. **失败归因**：用 LLM 分类器（参照论文 B.4 的分类）标注失败轨迹，学习"失败类别 → 组件"的关联矩阵，作为提议分布的先验。
3. **界面反事实估计**：对每条失败轨迹，在首次调用被修改组件的步 t 分叉，在相同容器快照中用新界面重放后缀，估计 Δ解决率；用 Thompson sampling 在组件变体上分配重放预算，最后只对少数候选做全量评测。
4. **稳健目标**：max_I min_{m∈M} ResolveRate(I, m) − λ·Cost(I, m)，M 含闭源与开源 backbone，防止界面只对单一模型过拟合；最终设计在新仓库与新任务上检验。
5. **成本**：反事实后缀平均长度约为全轨迹的一半，且只对失败实例重放；整体搜索预算可控制在数次全量 SWE-bench Verified 评测之内。

**🧭 与最接近工作的区别**
- ADAS (Hu et al., 2024) 与 Darwin Gödel Machine (Zhang et al., 2025)：在整套智能体代码空间做开放式搜索，每个候选需全量评测，缺少失败到组件的归因。
- DSPy (Khattab et al., 2023) 等提示优化：优化提示文本，不改变工具语义与观测格式。
- SWE-agent (Yang et al., 2024)：手工迭代 ACI，本 idea 将其流程形式化为可自动化、可归因的搜索。

**🧪 验证方案**
- 基准：SWE-bench Verified（主指标 % Resolved）、SWE-bench Lite（搜索集）、SWE-rebench 新近任务（防污染的留出集）；指标：解决率、每实例 token 成本、步数、"编辑失败后无法恢复"类别占比。
- 关键假设：(a) 反事实后缀估计的 Δ 与全量重跑 Δ 的秩相关显著；(b) 稳健目标下搜到的界面在未参与搜索的 backbone 上同样提升；(c) 自动设计至少达到人工 ACI 的水平。
- 对比与消融：人工 SWE-agent ACI、ADAS 式整体搜索（同等预算）、随机组件搜索、去掉失败归因先验。

🔑 `agent-computer interface` `SWE-bench` `automated agent design` `counterfactual replay` `software engineering agents`

[🔝 top](#top)

---

## 💡 Idea 19.7 — *Executable Landmarks: Auto-Synthesized, Mutation-Validated Process Probes for Grading Research-Code Agents*

| | |
|:--|:--|
| 🎯 **源论文** | **RExBench: Can coding agents autonomously implement AI research extensions?** · Nicholas Edwards et al. (Vienna) · 📄 ACL 2025 · [arXiv:2506.22598](https://arxiv.org/abs/2506.22598) ＋ **PaperBench: Evaluating AI's Ability to Replicate AI Research** · Starace et al. · 📄 ICML 2025 · 📈 高引用 (340+) · [arXiv:2504.01848](https://arxiv.org/abs/2504.01848) |
| 📌 **线索来源** | RExBench Limitations §"additional process-level metrics such as landmark evaluation ... would help alleviate the difficulty of post-hoc error analysis ..., especially for implicit errors, as well as reducing reward hacking or gamification of the benchmark." + PaperBench Appendix A §"Additionally, the output cannot be programmatically graded." |
| 📮 **投稿建议** | 🧪 **ML** · ICLR / NeurIPS ＋ 🗣️ NLP · ACL / EMNLP |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
RExBench 要求智能体在已有论文代码上实现研究扩展，仅以最终数值是否落入预期区间判定成功；PaperBench 则依赖与原作者共建的大型人工 rubric 和 LLM 评分员。两者指向同一个空隙：科研代码输出是非结构化的长程产物，**结果级**判定无法定位错误（隐式错误尤其难查）、可被凑数值 hack，而**人工 rubric/landmark** 成本高（RExBench 明说中间检查"requires substantial manual effort"）。关键 insight：这类任务有一个被忽视的资源——**参考实现**。从参考实现的 diff 出发，可以自动合成可执行的中间探针（固定种子下某函数的输出、损失在小批次上的值、配置开关是否真正影响计算图），再用**变异测试**筛选：探针必须在参考实现上通过、在变异后的参考实现上失败，从而保证区分力。这样得到的 landmark 既是自动的、可执行的，又自带有效性证据。

**💡 一句话 Idea**
从参考实现的 diff 自动合成可执行中间探针，用"在参考实现上通过、在变异体上失败"的变异测试保证其区分力，为科研代码智能体提供自动、可定位、抗 hack 的过程级评分与稠密训练信号。

**🛠️ 可能的解决方法**
1. **探针合成**：对参考实现相对原仓库的 diff，LLM 枚举受影响的函数/模块，生成三类探针：(i) 函数级 I/O 断言（固定种子、小输入）；(ii) 训练动态探针（前 N 步损失、梯度范数在容差内）；(iii) 数据流探针（新超参数是否流入计算图，用 hook 检查）。
2. **变异筛选**：对参考实现施加语义变异（删掉新增项、改符号、换归一化维度、漏掉 mask），保留"参考通过且杀死 ≥1 个变异体"的探针；探针集的变异得分作为其质量指标。
3. **接口对齐**：智能体实现可能命名不同，探针通过 LLM 生成的轻量适配层（定位对应函数并调用）运行；适配失败计为"不可评"，单独统计以免误罚。
4. **评分与用途**：过程分 = 通过的探针加权和（权重 ∝ 杀死变异体数），与结果分共同报告；同一探针集可作为 SFT/RL 的稠密奖励，并用来检测"结果对、过程错"的 hack 轨迹。
5. **成本**：探针运行在 CPU 或小 GPU 上数分钟内完成，远低于完整实验复现。

**🧭 与最接近工作的区别**
- PaperBench (Starace et al., 2025)：人工共建层级 rubric + LLM 评分，成本高且非可执行。
- RExBench (Edwards et al., 2025) 与 SUPER (Bogin et al., 2024)：结果级判定或人工设计的 landmark；本 idea 自动合成并用变异测试验证。
- MLE-bench (Chan et al., 2024)：以 Kaggle 排行榜分数为结果指标，不评估实现过程。

**🧪 验证方案**
- 基准：RExBench 全部任务、PaperBench Code-Dev 子集；被测智能体：OpenHands、aider、Claude Code 风格 CLI 智能体等。
- 指标：探针变异得分、过程分与最终成功的相关性、错误定位准确率（与人工错误分析对比）、对人为构造 hack 解（凑数值）的检出率、评测成本。
- 关键假设：(a) 过程分对"接近正确"实现给出区分，提升评测分辨率；(b) 变异筛选显著提高探针与人工判断的一致率；(c) 以探针为稠密奖励的 RFT 优于仅用结果奖励。
- 消融：去掉变异筛选 / 只用 I/O 探针 / 去掉适配层。

🔑 `research agents` `process evaluation` `mutation testing` `RExBench` `PaperBench` `reward hacking`

[🔝 top](#top)

---

## 💡 Idea 19.8 — *Certified Tool Making: Repository-Grounded Differential and Metamorphic Testing for Agent-Created Scientific Tools*

| | |
|:--|:--|
| 🎯 **源论文** | **LLM Agents Making Agent Tools** · Georg Wölflein et al. (St Andrews) · 📄 ACL 2025 · [arXiv:2502.11705](https://arxiv.org/abs/2502.11705) |
| 📌 **线索来源** | Limitations §"While TM-Bench contains over 100 unit tests, passing these tests does not guarantee correctness in all real-world scenarios." + §"Scientific workflows often involve edge cases or unexpected patterns that are not captured by a small set of tests." |
| 📮 **投稿建议** | 🗣️ **NLP** · ACL / EMNLP ＋ 🧪 ML · ICLR / NeurIPS |
| ⭐ Novelty | ★★★☆☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
ToolMaker 让智能体把科研代码仓库自动安装、封装成 LLM 可调用的工具，在 TM-Bench 上达到 80% 正确率，超过 OpenHands。但作者承认：100 多个单元测试远不能保证工具在真实场景中正确，科学工作流充满边界情况，而高风险应用（如临床研究）需要更严格的验证。这里的空隙是：工具创建类工作把"能跑通几个示例"当作完成标准，下游智能体随后会**无条件信任**这些工具，错误在多步任务中被静默放大。关键 insight：科研仓库本身携带大量**隐式预言**——README 示例、notebook 输出、仓库自带测试、论文中的数值——可用于差分测试；而科学计算往往满足可写成代码的**变形关系**（输入置换不变、单位缩放等变、子集一致性），无需真值即可发现错误。把这些组合起来，可以为每个工具出具带置信度的"证书"，让下游智能体按证书决定是否使用。

**💡 一句话 Idea**
为智能体创建的工具自动挖掘仓库内的参考输出做差分测试，合成并验证领域变形关系、做接口级属性模糊测试，输出带置信度的工具证书，下游智能体只调用通过认证的工具或在低置信时显式标注不确定性。

**🛠️ 可能的解决方法**
1. **仓库预言挖掘**：解析 README、docs、notebook 输出单元格与原始测试，抽取 (输入, 期望输出) 对；对工具的封装接口执行同样输入并做容差比较（数值相对误差、表格 schema 一致）。
2. **变形关系合成**：LLM 根据工具描述提议变形关系（如"对样本顺序置换，聚类标签按置换对应""分辨率减半，分割结果下采样一致"），先在原始仓库代码上验证关系成立，只保留通过者用于测试封装后的工具。
3. **属性模糊测试**：基于接口类型签名（Hypothesis 风格）生成边界输入（空文件、极端尺寸、缺失元数据），检查崩溃、静默 NaN 与无效输出。
4. **证书与修复回路**：证书 = 各测试族通过率 + 覆盖的输入空间描述；失败测试反馈给 ToolMaker 的修复循环；低于阈值的工具不进入下游工具库。
5. **成本**：测试在工具的容器环境中运行，主要开销是 LLM 合成关系，每工具约数十次调用。

**🧭 与最接近工作的区别**
- ToolMaker (Wölflein et al., 2025)：以少量单元测试验证，作者明确指出覆盖不足。
- LATM (Cai et al., 2023) / CREATOR (Qian et al., 2023)：工具为简单 Python 函数，验证仅靠几个示例。
- 变形测试 (Chen et al., 1998) 是经典软件测试方法，本 idea 将其与仓库预言挖掘结合，用于 LLM 智能体的自动工具认证。

**🧪 验证方案**
- 基准：TM-Bench（原测试 + 新增隐藏边界测试）；向正确工具注入语义错误（错误归一化、轴错位、单位错误）构造变异工具集，测检出率。
- 指标：错误工具检出率 / 误报率、修复后隐藏测试通过率、下游多步任务（使用工具库完成科研分析）的成功率、每工具认证成本。
- 关键假设：(a) 原单元测试通过但隐藏测试失败的工具中，大部分能被差分或变形测试发现；(b) 只用认证工具的下游智能体错误率更低。
- 消融：仅差分 / 仅变形 / 仅模糊测试；去掉"先在原仓库验证关系"步骤。

🔑 `tool creation` `metamorphic testing` `differential testing` `scientific agents` `verification`

[🔝 top](#top)

---

## 💡 Idea 19.9 — *When Memory Amplifies Mistakes: Error-Propagation Bounds and Evaluator-Calibrated Admission Control for Self-Evolving Agent Memory*

| | |
|:--|:--|
| 🎯 **源论文** | **How Memory Management Impacts LLM Agents: An Empirical Study of Experience-Following Behavior** · Zidi Xiong et al. (Harvard) · 📄 ACL 2025 · 📈 高引用 (120+) · [arXiv:2505.16067](https://arxiv.org/abs/2505.16067) |
| 📌 **线索来源** | Conclusion §"We identify the experience-following phenomenon and reveal two key challenges—error propagation and misaligned experience replay." + Limitations §"Another limitation concerns the lack of theoretical guarantees." |
| 📮 **投稿建议** | 🧪 **ML** · ICLR / NeurIPS ＋ 🗣️ NLP · ACL / EMNLP |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
该文研究经验记忆的最基本操作——添加与删除——并发现"经验跟随"现象：当前查询与检索到的记录越相似，输出与记录中的执行就越相似。由此产生两个问题：错误记录被加入后会被反复检索、复制，导致错误传播；过时或不对齐的经验被重放后损害新任务。作者强调评估器可靠性是关键，但所有结论都是经验性的，缺乏理论刻画。这正是空隙：现有记忆系统（AWM、ExpeL、A-MEM）都在设计"加什么、怎么组织"，却没有回答**在评估器有噪声时，记忆库的错误比例会收敛到哪里、何时会失控**。关键 insight：经验跟随使记忆库成为一个**正反馈的随机过程**——可以用带强化的 Pólya 型模型描述：错误记录被检索的概率 × 被复制的概率 × 评估器漏判率，决定了错误比例的不动点。由此可推出添加阈值与删除策略的条件，使错误比例有界，把"评估器很重要"变为可计算的设计准则。

**💡 一句话 Idea**
把经验记忆库建模为由检索、经验跟随和噪声评估器驱动的强化随机过程，推导错误比例的不动点与失控条件，并据此设计后验驱动的添加阈值与基于反事实效用的删除策略，使自进化记忆的错误比例可证明有界。

**🛠️ 可能的解决方法**
1. **理论模型**：设记忆库错误比例 e_t，检索命中错误记录的概率 g(e_t)（受相似度结构影响），经验跟随系数 ρ（命中错误记录时输出继承错误的概率），基础错误率 ε，评估器假阳性/假阴性率 α/β。推导 e_{t+1} 的期望动态，给出不动点 e* 与稳定性条件（如 ρ·g'(e*)·(1−β) < 1），说明何时错误传播失控。
2. **后验添加控制**：不使用评估器的二值输出，而计算 P(正确 | 评估器信号, 自一致性, 执行反馈)，仅当后验 > τ(α, β, ρ) 时添加；τ 由理论给出以满足目标 e*。
3. **反事实效用删除**：在线随机地对检索结果做"使用/屏蔽"切换，估计每条记录的边际效用（类似留一法的 bandit 估计），删除效用为负的记录，处理"不对齐重放"。
4. **ρ 的在线估计**：用嵌入相似度与输出相似度的回归在线估计 ρ，供阈值自适应。
5. **成本**：额外开销是评估器调用与少量屏蔽实验，无需训练模型。

**🧭 与最接近工作的区别**
- Xiong et al. (2025)：经验性揭示错误传播，无理论刻画与可证明有界的控制策略。
- Agent Workflow Memory (Wang et al., 2024) / ExpeL (Zhao et al., 2024)：设计经验抽取与复用方式，默认加入的经验是正确的。
- A-MEM (Xu et al., 2025)：关注记忆组织与链接演化，不处理噪声评估下的错误累积。

**🧪 验证方案**
- 基准：论文的合成 RegAgent 环境（可精确控制 ρ、α、β 以检验理论预测）、WebArena（配合 AWM/CER 式记忆）、AppWorld、τ-bench；指标：长期成功率曲线、记忆库错误比例、pass^k 可靠性、每任务 token 成本。
- 关键假设：(a) 理论预测的不动点与合成环境中观测到的错误比例吻合；(b) 后验阈值在评估器噪声较大时比固定阈值显著更稳；(c) 反事实删除优于基于时间或频率的删除。
- 对比与消融：全部添加、评估器二值过滤、论文中的最佳策略；去掉 ρ 自适应。

🔑 `agent memory` `experience replay` `error propagation` `self-evolving agents` `admission control` `theory`

[🔝 top](#top)

---

## 💡 Idea 19.10 — *Skeleton Memory: Utility-Preserving Abstraction and Session-Bound Vaults against Memory Extraction in LLM Agents*

| | |
|:--|:--|
| 🎯 **源论文** | **Unveiling Privacy Risks in LLM Agent Memory** · Bo Wang et al. (Michigan State) · 📄 ACL 2025 · 📈 高引用 (130+) · [arXiv:2502.13172](https://arxiv.org/abs/2502.13172) |
| 📌 **线索来源** | Limitation §"Introducing user-level and session-level memory isolation would limit attackers’ access to private data and mitigate the impact of memory extraction." + Appendix C §"However, this operation may weaken the effectiveness of stored records as demonstrations for future queries." |
| 📮 **投稿建议** | 🗣️ **NLP** · ACL / EMNLP ＋ 🔐 Security · USENIX Security / CCS |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
MEXTRA 表明，黑盒攻击者只需精心设计的查询就能诱导智能体把记忆中其他用户的历史查询原样输出，在 EHRAgent 与 RAP 上泄露大量私有记录。作者给出两个尚未解决的方向：会话/用户级记忆隔离，以及记忆脱敏——但脱敏会削弱记录作为示范的作用。这揭示了一个隐私-效用的结构性矛盾：智能体记忆之所以有用，是因为它复用**过程**（计划、代码、工具调用顺序），而泄露的是**具体值**（姓名、病历号、地址）。现有做法要么完全隔离（丢掉跨用户的经验共享），要么整体脱敏（破坏示范）。关键 insight：把每条记录拆成"程序骨架 + 槽值"两层——骨架用类型化占位符替换敏感值，可跨用户共享；槽值留在绑定会话身份的保险库中，仅对原用户可见。这样跨用户检索只能拿到骨架，攻击者即便完整提取记忆也得不到私有值，而示范效用几乎保留。

**💡 一句话 Idea**
将智能体记忆记录分解为可共享的类型化程序骨架与绑定会话身份的私有槽值保险库，跨用户检索只暴露骨架，在保持经验复用效用的同时使记忆提取攻击得不到私有值。

**🛠️ 可能的解决方法**
1. **骨架化**：记录写入时，用 NER + LLM 识别敏感片段并替换为类型化占位符（⟨PATIENT_ID:int⟩、⟨DATE⟩、⟨ADDRESS⟩），保留计划步骤、代码结构与工具调用序列；对代码类记录用 AST 级替换，保证骨架仍可解析。
2. **会话绑定保险库**：槽值加密存储，密钥派生自用户身份；检索时仅当 requester == owner 才回填，否则智能体看到骨架并需自行填入当前用户数据。
3. **聚合去标识**：对低频骨架（可能通过结构本身识别个人）做 k-匿名合并——只有被至少 k 个用户共享的骨架模式才进入共享池。
4. **自适应攻击评估**：在 MEXTRA 基础上设计针对骨架记忆的自适应攻击（诱导智能体"回忆具体值"、跨会话拼接），报告最坏情况泄露。
5. **成本**：写入时一次 LLM 调用做骨架化；检索开销与原系统相当。

**🧭 与最接近工作的区别**
- MEXTRA (Wang et al., 2025)：揭示攻击并讨论过滤与脱敏，但未给出兼顾效用的方案。
- AirGapAgent (Bagdasarian et al., 2024)：按上下文最小化单次任务可访问的用户数据，不涉及跨用户共享的经验记忆。
- PrivacyLens (Shao et al., 2024)：基于情境完整性评估智能体行为中的隐私泄露，是评测框架而非记忆架构。

**🧪 验证方案**
- 基准：EHRAgent、RAP/WebShop（MEXTRA 原设置）、τ-bench retail/airline（含用户个人信息的标准工具使用任务）。
- 指标：提取攻击下私有值泄露数与泄露率、任务成功率（相对原始记忆的效用保持比例）、pass^k、写入与检索 token 成本。
- 关键假设：(a) 骨架记忆在成功率上接近原始记忆、显著高于整体脱敏；(b) 泄露率接近完全隔离；(c) k-匿名合并能抵御基于结构的再识别。
- 对比与消融：无防护、系统提示过滤、整体脱敏、完全会话隔离；去掉保险库 / 去掉 k-匿名。

🔑 `agent memory` `privacy` `memory extraction` `contextual integrity` `de-identification`

[🔝 top](#top)

---

## 💡 Idea 19.11 — *Beyond the First Step: Trajectory-Level Adaptive Prompt Injection against Stacked Agent Defenses*

| | |
|:--|:--|
| 🎯 **源论文** | **Adaptive Attacks Break Defenses Against Indirect Prompt Injection Attacks on LLM Agents** · Qiusi Zhan et al. (UIUC) · 📄 NAACL 2025 · 📈 高引用 (170+) · [arXiv:2503.00061](https://arxiv.org/abs/2503.00061) |
| 📌 **线索来源** | Limitations §"Our adaptive attacks focus solely on the agent’s first-step action." + §"Exploring adaptive attacks that target combinations of defenses is an important area for future work." |
| 📮 **投稿建议** | 🗣️ **NLP** · ACL / EMNLP ＋ 🔐 Security · USENIX Security / CCS |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
该文针对 8 种间接提示注入防御分别设计自适应攻击（基于 GCG 等优化对抗串），全部攻破，强有力地说明防御必须用自适应攻击评测。但攻击目标只是让智能体**第一步**输出"我将调用攻击者工具"；在数据窃取这类需要两步的攻击中，第二步的提升最小。同时攻击假设白盒、且只针对单一防御。真实部署恰好相反：智能体是多步的，防御是叠加的（检测器 + 提示隔离 + 微调），攻击者多为黑盒。因此，"自适应攻击打破所有防御"的结论在最现实的设置下尚未被检验，防御方也不知道叠加防御到底提供了多少真实增益。关键 insight：把攻击目标从单步 token 序列换成**轨迹级回报**（攻击者目标是否最终完成、途中是否被任何检测器拦截），并用开源代理智能体与防御的集成做白盒优化、再迁移到黑盒目标，就能检验多步、叠加防御下的真实鲁棒性。

**💡 一句话 Idea**
以"攻击目标在多步轨迹中最终完成且未被任何防御层拦截"为回报，结合代理集成上的梯度优化与攻击者 LLM 的强化学习，生成可迁移的轨迹级注入，系统评测叠加防御与黑盒前沿智能体的真实鲁棒性。

**🛠️ 可能的解决方法**
1. **轨迹级目标**：R(δ) = 1[攻击者目标在 T 步内完成] − Σ_j 1[第 j 层防御报警]；对不可微部分用攻击者 LLM 的策略梯度（GRPO）优化注入文本，对可微代理（开源智能体 + 开源检测器）用 GCG 类离散优化生成候选。
2. **目标持久性**：注入内容包含"子目标链"，引导智能体在后续步骤自行生成下一步攻击动作，并在注入中伪装为与任务相关的内容（混入医生评价、邮件正文等良性文本），对应 InjecAgent 指出的混合内容场景。
3. **叠加防御**：组合检测类（PromptGuard 类分类器、困惑度过滤）、提示类（分隔符/三明治）、微调类防御与设计类防御（CaMeL 的控制/数据流隔离），逐层报告边际防御增益与组合后的残余攻击成功率。
4. **迁移到黑盒**：在多个开源模型代理集成上优化，迁移到闭源前沿智能体；记录查询预算。
5. **负责任披露**：只在沙盒基准内评测，向防御方提前披露。

**🧭 与最接近工作的区别**
- Zhan et al. (2025)：单防御、白盒、仅优化第一步动作。
- InjecAgent (Zhan et al., 2024) / AgentDojo (Debenedetti et al., 2024)：提供静态或模板化注入的基准，非自适应优化。
- CaMeL (Debenedetti et al., 2025)：设计类防御，本 idea 将其纳入叠加防御并测量自适应攻击下的残余风险，而不是提出新防御。

**🧪 验证方案**
- 基准：InjecAgent（多步扩展）、AgentDojo、WebArena 中注入网页的场景；指标：轨迹级攻击成功率（ASR）、各防御层检出率、良性任务效用下降、查询预算。
- 关键假设：(a) 轨迹级优化在两步及以上攻击上的 ASR 显著高于第一步优化；(b) 叠加防御的组合增益小于各层独立增益之和；(c) 代理集成优化的注入能迁移到闭源智能体。
- 对比与消融：Zhan et al. 的第一步自适应攻击、固定 hacking prompt；去掉 RL / 去掉代理集成 / 去掉目标持久性。

🔑 `prompt injection` `adaptive attacks` `agent security` `defense composition` `multi-step agents`

[🔝 top](#top)

---

## 💡 Idea 19.12 — *Probabilistic Code World Models: Likelihood-Guided Program Synthesis of Stochastic, Partially Observable Simulators for Agent Planning*

| | |
|:--|:--|
| 🎯 **源论文** | **Generating Code World Models with Large Language Models Guided by Monte Carlo Tree Search** · Nicola Dainese et al. (Aalto) · 📄 NeurIPS 2024 · [arXiv:2405.15383](https://arxiv.org/abs/2405.15383) |
| 📌 **线索来源** | 6.1 Limitations §"we still rely on limiting assumptions of deterministic and fully observable environments." + §"Both stochasticity and partial observability would pose challenges, especially on the verification of the CWM prediction, as there is no set result for a given input." |
| 📮 **投稿建议** | 🧪 **ML** · ICLR / NeurIPS ＋ 🧩 AI · AAAI |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
Code World Models 让 LLM 写出环境的 Python step 函数，用 GIF-MCTS（生成 / 改进 / 修复三类动作的树搜索）以离线转移数据的预测准确率为奖励迭代改进代码，所得模型推理极快、可解释、样本高效。但整个框架依赖确定性与完全可观测：验证就是逐条比较预测与观测的下一状态。一旦环境有随机性或隐藏状态，同一输入没有唯一正确输出，精确匹配奖励失效。作者还观察到准确率与回报的差距主要来自罕见终止状态的预测错误。这里的空隙是：程序化世界模型无法覆盖绝大多数真实智能体环境（游戏、网页、对话用户都含随机与隐藏信息）。关键 insight：让程序**显式输出分布**（在代码中调用随机采样并维护隐状态），就能用**数据似然**而非精确匹配评估程序；隐状态用粒子滤波边缘化。这样 GIF-MCTS 的奖励自然推广为保留集对数似然，并可对稀有事件（终止、奖励）加权。

**💡 一句话 Idea**
让 LLM 合成带显式随机采样与隐状态的概率程序作为世界模型，以粒子滤波估计的保留集对数似然（并对稀有终止事件加权）作为树搜索奖励，把代码世界模型推广到随机、部分可观测环境并用于 POMCP 类规划。

**🛠️ 可能的解决方法**
1. **程序形式**：要求程序实现 `init_belief()`、`step(state, action, rng) -> (next_state, obs, reward, done)` 与 `obs_logprob(obs | state)`；随机性只能通过 rng 的命名分布调用（categorical、normal），从而可精确计算转移对数概率。
2. **似然评估**：对每条离线轨迹用 bootstrap 粒子滤波估计 log p(o_{1:T} | a_{1:T}, 程序)；奖励 = 保留集平均对数似然 + 对终止/奖励事件的加权项（直接针对论文观察到的准确率-回报差距）。
3. **搜索**：沿用 GIF-MCTS 的三类动作，新增"引入隐变量"和"把确定性分支改为分布"两类编辑；用似然的分段分解（哪一步、哪个观测维度似然最低）作为修复提示。
4. **规划**：用学到的程序做 POMCP / 粒子信念上的 MCTS，评估下游回报；程序运行快，可支持大量模拟。
5. **成本**：粒子数 100–500 时每个候选程序的评估为 CPU 秒级；LLM 调用预算与原 GIF-MCTS 同量级。

**🧭 与最接近工作的区别**
- GIF-MCTS / CWM (Dainese et al., 2024) 与 WorldCoder (Tang et al., 2024)：均假设确定性与完全可观测，以精确匹配验证程序。
- PoE-World (Piriyakulkij et al., 2025)：用大量程序化专家的乘积组合出概率世界模型，本 idea 则合成单一显式隐状态程序并用粒子滤波似然驱动搜索，直接处理部分可观测性。
- POMCP (Silver & Veness, 2010)：需要已知的生成模型，本 idea 由 LLM 合成该模型。

**🧪 验证方案**
- 基准：CWMB 原环境（检验向下兼容）、随机版本（FrozenLake slippery、带随机转移的 MiniGrid）、部分可观测环境（MiniGrid 部分视野、BALROG 中的 BabyAI / MiniHack 子集）。
- 指标：保留集对数似然、终止事件预测 F1、基于模型规划的归一化回报、环境交互样本数、LLM 调用成本。
- 关键假设：(a) 似然奖励在随机环境中显著优于精确匹配奖励；(b) 隐状态程序在部分可观测环境中的规划回报优于无记忆程序；(c) 稀有事件加权缩小准确率-回报差距。
- 消融：去掉粒子滤波（用最可能状态近似）/ 去掉稀有事件加权 / 去掉新增编辑动作。

🔑 `code world models` `program synthesis` `probabilistic programming` `POMDP` `MCTS` `model-based planning`

[🔝 top](#top)

---

## 💡 Idea 19.13 — *Observational Scaling for Agents: Forecasting Agentic Success from Capability Factors, Scaffolds, and Inference Budgets*

| | |
|:--|:--|
| 🎯 **源论文** | **Observational Scaling Laws and the Predictability of Language Model Performance** · Yangjun Ruan et al. (Toronto) · 📄 NeurIPS 2024 · 📈 高引用 (150+) · [arXiv:2405.10938](https://arxiv.org/abs/2405.10938) |
| 📌 **线索来源** | Conclusion, Limitations, and Future Work §"Secondly, our study mostly focuses on the scaling behavior of model capabilities measured through few-shot prompting or basic prompting techniques (such as CoT, self-consistency, or simple agent scaffolding)." + §"Extending our approach to other post-training setups, including scenarios involving fine-tuning or more intensive inference-time computation ... would be valuable." |
| 📮 **投稿建议** | 🧪 **ML** · ICLR / NeurIPS ＋ 🗣️ NLP · ACL / EMNLP |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
观测缩放律发现，跨模型族的基准表现可以由少数几个主成分（低维能力空间）解释，并能用小模型预测大模型的涌现与简单智能体任务表现，无需自己训练模型族。但作者明确指出，研究只覆盖了基础提示和简单脚手架，对微调与密集推理计算尚未扩展。对智能体而言，这恰好是关键缺口：今天的 SWE-bench Verified、OSWorld、τ-bench 成绩由**模型 × 脚手架 × 推理预算（步数、采样数、思考 token）**三者共同决定，评测一次成本高昂，领域缺乏一个能回答"换脚手架/加预算值多少"以及"新模型上线前能预测多少"的定量框架。关键 insight：可以把脚手架与预算视为观测缩放律中的额外协变量——能力因子决定"天花板"，脚手架决定"转化效率"，预算决定沿曲线的位置——用公开排行榜与少量补充评测拟合，就能以非智能体基准的低成本预测昂贵的智能体成绩，并识别哪些能力因子真正驱动智能体表现。

**💡 一句话 Idea**
把观测缩放律扩展为"能力因子 × 脚手架效率 × 推理预算"的分层模型，用公开智能体排行榜与低成本非智能体基准拟合，预测新模型/新脚手架在 SWE-bench、OSWorld、τ-bench 上的成功率与可靠性，并量化脚手架和推理预算的边际价值。

**🛠️ 可能的解决方法**
1. **数据**：收集数十个模型在标准非智能体基准上的分数，提取低维能力因子 PC_m；收集同一批模型在 SWE-bench Verified、OSWorld、τ-bench、WebArena 上不同脚手架与预算下的成绩（公开数据 + 选择性补测）。
2. **模型**：logit(S_{m,s,b,k}) = α_s + Σ_j β_{s,j}·PC_{m,j} + γ_s·log b + δ·(PC_m·log b) − κ_s·log k，其中 s 为脚手架、b 为推理预算、k 为 pass^k 的重复次数（刻画可靠性随 k 的衰减）；层次贝叶斯共享脚手架参数。
3. **能力因子归因**：检验是否需要非智能体基准未覆盖的额外"智能体因子"（如长上下文工具使用），用留一模型族交叉验证判断。
4. **污染检测**：在新近任务（SWE-rebench 等）上比较预测残差，残差显著为正的模型/基准组合提示可能存在污染，作为副产品。
5. **成本**：主要依赖公开数据；补测控制在少数开源模型与两种脚手架上。

**🧭 与最接近工作的区别**
- Ruan et al. (2024)：仅覆盖基础提示与简单脚手架，没有把脚手架与推理预算作为显式变量。
- Owen (2024) 基准表现可预测性研究：以计算量为预测变量预测聚合基准分，不针对智能体任务与可靠性。
- Kwa et al. (2025) 任务时长度量：用"可完成任务的人类时长"刻画智能体能力增长，不分解模型、脚手架与预算的贡献。

**🧪 验证方案**
- 基准：SWE-bench Verified、OSWorld、τ-bench（含 pass^k）、WebArena；指标：对留出新模型与留出脚手架的预测误差（MAE、校准）、预测区间覆盖率。
- 关键假设：(a) 低维能力因子 + 脚手架 + 预算能解释大部分方差；(b) 用发布前可得的非智能体基准能提前预测前沿模型的智能体成绩；(c) 可靠性衰减系数 κ 主要由脚手架而非模型决定（或相反，用数据检验）。
- 对比与消融：仅用模型规模/计算量预测、仅用单一基准分预测、去掉预算项或交互项。

🔑 `observational scaling laws` `agent evaluation` `forecasting` `inference-time compute` `pass^k reliability` `SWE-bench`

[🔝 top](#top)
