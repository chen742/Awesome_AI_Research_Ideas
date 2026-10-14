<a id="top"></a>
# 🔬 AI for Science & Others

> 从 AI4Science（蛋白/基因/分子/PDE/时间序列）、医疗 LLM 评测、科学推理 Agent 等方向的获奖与 oral 论文中提炼的 idea。
> 符号说明：🎯 源论文 · 📌 线索来源 · ⭐ Novelty · 🚀 Impact · 🧗 Difficulty · 🧪 验证方案 · 🔑 关键词

[⬅️ 返回主页](../README.md)

---

## 💡 Idea 11.1 — *Clinician-Decomposed Rubric Rewards: Replacing Similarity Metrics for Free-Text Medical Answers in Low-Resource Settings*

| | |
|:--|:--|
| 🎯 **源论文** | **AfriMed-QA: A Pan-African, Multi-Specialty, Medical Question-Answering Benchmark Dataset** · Olatunji et al. · 🏆 ACL 2025 Best Paper · [arXiv:2411.15640](https://arxiv.org/abs/2411.15640) |
| 📌 **线索来源** | Limitations of automated metrics §"no single automated metric reliably captures both the correctness and completeness of free-text medical responses ... even when metrics are combined" + §"We therefore defer analysis of open-ended answers to future human evaluations where clinicians can better discriminate between semantically similar and clinically correct answers" |
| 📮 **投稿建议** | 🗣️ **NLP** · ACL ＋ 🔬 Science · ML4H / Nature Medicine |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
AfriMed-QA 收集了 16 个国家、60 余所医学院的 15k 道题（MCQ/SAQ/CQ），评测 30 个 LLM，是第一个泛非洲多专科医疗 QA 基准。但论文自己承认评测链条断在开放式题上：BERTScore 全部模型挤在 0.86–0.89，ROUGE-Lsum 与 QuestEval 的区分度虽宽却与临床正确性无关，作者只能把开放式答案的分析推给"未来的临床医生人工评测"。这是一个真正的空隙：后续工作大多转向 LLM-as-judge，但在非洲语境下 judge 本身就带有地理与人口偏差（论文已测出 demographic bias），而把 judge 的分数当作标量奖励又无法告诉模型"漏了哪一步"。关键 insight 是：临床答案的正确性天然是**可分解的事实集合**（诊断、鉴别诊断、首选检查、剂量、转诊阈值），而相似度指标把它压成了一个标量；只要把每道题的参考答案分解成可判定的原子条目，评测就从"语义相似"变成"条目覆盖 + 禁忌违规"，既能跑自动化又能对齐临床判断。

**💡 一句话 Idea**
把每道开放式医疗题的参考答案由临床医生分解为带权重的原子 rubric 条目（必须项/加分项/危险项），用一个在少量医生标注上校准、并显式做地理-人口不变性正则的轻量 judge 逐条判定，从而得到可解释、可审计、可直接当 RL 奖励的自动指标。

**🛠️ 可能的解决方法**
1. **数据**：在 AfriMed-QA 的 SAQ/CQ 子集上，由各区域临床贡献者把参考答案标注为 5–12 条原子条目，并标出"危险项"（如漏掉疟疾/结核等地域高发鉴别、错误剂量）；每题再采集 3–5 个模型答案的条目级人工判定作为校准集。
2. **判定模型**：训练一个 3–8B 的 entailment 式 judge，输入 (问题, 条目, 候选答案)，输出 {覆盖, 矛盾, 未提及}；损失用条目级交叉熵 + 对 judge logit 做 **人口/地域不变性惩罚**（同一答案在替换患者国籍/性别描述后判定应不变，用 JS 散度惩罚）。
3. **指标**：最终分数 = Σ 必须项权重 × 覆盖率 − λ × 危险项违规；报告条目级 Krippendorff α 与人工评分的相关性，替代 BERTScore。
4. **当奖励用**：rubric 分数稀疏但可分解，适合做 GRPO 的逐条 credit；训练阶段用"条目覆盖增量"作为过程奖励，避免长答案刷分（长度惩罚 + 矛盾项直接置零）。
5. **成本控制**：医生标注只做一次（条目可跨模型复用），judge 可蒸馏到 3B 以在本地/低带宽环境离线运行。

**🧭 与最接近工作的区别**
- HealthBench（OpenAI, 2025）用医生写的 rubric 评分，但 rubric 由医生针对对话整体撰写、judge 未做地域不变性校准，且不面向非洲语境与低资源部署；本 idea 把 rubric 绑定到现有基准的参考答案并显式做偏差正则。
- QuestEval / BERTScore：纯语义相似，论文已证明在该场景失效。
- Med-PaLM 2 的人工评分维度（2023）：定义了"潜在危害"等维度但仅用于人工评测，没有可复现的自动化判定器。

**🧪 验证方案**
- 基准：AfriMed-QA SAQ/CQ；指标：与医生总体排序的 Spearman ρ、条目级 F1、危险项检出率；对比 BERTScore / ROUGE-Lsum / QuestEval / 单标量 LLM-judge。
- 关键假设检验：(a) rubric 分数的动态范围与医生评分相关性显著高于所有相似度指标；(b) 替换患者人口属性后 rubric 分数漂移显著小于标量 judge。
- 消融：去掉不变性正则、去掉危险项、judge 规模 3B vs 8B；跨区域泛化（用西非标注训练，在东/南非题上测）。

🔑 `medical QA` `rubric reward` `LLM-as-judge` `evaluation metric` `demographic bias` `low-resource`

[🔝 top](#top)

---

## 💡 Idea 11.2 — *Glianorex Probes at Scale: Separating Clinical Reasoning from Test-Taking Heuristics with Counterfactual Knowledge Worlds*

| | |
|:--|:--|
| 🎯 **源论文** | **Pattern Recognition or Medical Knowledge? The Problem with Multiple-Choice Questions in Medicine** · Griot et al. · 🏆 ACL 2025 SAC Highlights· [arXiv:2406.02394](https://arxiv.org/abs/2406.02394) |
| 📌 **线索来源** | Conclusion §"models of different architectures, sizes, and specializations outperform physicians on this benchmark, suggesting that pattern recognition and test-taking strategies may play a larger role for LLMs than for humans" + Limitations §"future work should evaluate models on multiple-choice questions covering clinical knowledge published after the training cut-off date" |
| 📮 **投稿建议** | 🗣️ **NLP** · ACL ＋ 🔬 Science · ML4H |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★☆☆☆ |

**🔍 深入分析**
作者虚构了一个器官 Glianorex，用 LLM 生成教材与配套 MCQ，使"记忆"被完全排除：模型平均得 64%，而两位医生只有 27%。这证明现有医疗 MCQ 很大一部分分数来自选项表面线索与应试启发式。论文的 Limitation 同时暴露了方法本身的脆弱：虚构教材由 LLM 独立生成，子章节间可能矛盾；接地信息来自单一临床医生，残余合成偏差难排除；且只有一个虚构器官、两种语言，无法定位"启发式"究竟是哪一种。真正的空隙在于：现在只知道"有捷径"，但没有**可控的捷径归因工具**——不知道是选项长度、绝对化措辞、分布线索，还是真实医学先验的迁移在起作用。而"用训练截止后的新知识测"这条后续路线又受污染与时间漂移限制。关键 insight：虚构世界的真正价值不是一个基准，而是一个**可干预的生成器**——同一条知识可以被系统性地改写成与真实医学一致或相反的版本，于此做因果式消融。

**💡 一句话 Idea**
把 Glianorex 从单个虚构基准升级为"反事实知识世界"生成流水线：对同一命题生成"与真实医学同向/反向/无关"三套一致教材与 MCQ，并对选项表面特征做受控扰动，从而把模型分数因果地分解为真实医学先验迁移、表面启发式与真正的文内推理。

**🛠️ 可能的解决方法**
1. **一致性优先的世界生成**：先生成一个结构化知识图（实体、机制、因果边、数值区间），用约束求解器保证无矛盾，再由 LLM 把图渲染成教材与题目；矛盾检查从"部分人工抽查"升级为对图的自动一致性验证。
2. **三臂反事实设计**：对每条机制生成 (i) aligned（与真实生理同向，如"激素升高→心率升高"）、(ii) inverted（反向）、(iii) orthogonal（与真实医学无关的新机制）三版；若模型在 inverted 上显著掉分，说明分数来自真实先验迁移而非文内推理。
3. **表面特征扰动**：对每题做选项长度均衡、绝对化词（always/never）剥离、"以上都不是"注入、正确答案位置随机化、干扰项同质化五类扰动，得到每种启发式的边际贡献（可做成 5 维"捷径指纹"）。
4. **开放式对照臂**：同一命题同时出成自由作答题并用条目级 rubric 评分（可复用 Idea 11.1 的判定器），检验"MCQ 高分-开放式低分"的落差。
5. **成本控制**：知识图小（百量级节点）即可支撑上万道题；评测只需零样本推理，单模型成本在数十美元级。

**🧭 与最接近工作的区别**
- 原 Glianorex（本论文）：单一虚构世界、无反事实臂、无表面特征受控扰动，只能给出"存在捷径"的总体结论。
- MedMCQA / USMLE 类基准：真实知识，记忆与推理不可分。
- "选项打乱/去题干"鲁棒性测试（如 Balepur et al., 2024 关于选择题可在无题干时被猜中）：只做了表面扰动，没有可控的知识内容干预。

**🧪 验证方案**
- 评测 20+ 开源/闭源/医疗微调模型 + 医生对照组；指标：aligned-inverted 分差（先验迁移量）、扰动前后分差（启发式量）、残差（文内推理量）。
- 关键假设检验：医疗微调模型的先验迁移量显著大于通用模型（解释论文中"微调模型在英语上更强、法语上不强"的异常）。
- 消融：语言（英/法/斯瓦希里）、题型（单选/多选/排序）、教材是否提供在上下文中（闭卷 vs 开卷）。

🔑 `medical benchmark` `shortcut learning` `counterfactual evaluation` `MCQ` `causal ablation` `synthetic knowledge`

[🔝 top](#top)

---

## 💡 Idea 11.3 — *Generate-to-Explain: Training Tabular Generators Against Global Structural Utility Instead of Marginal Density*

| | |
|:--|:--|
| 🎯 **源论文** | **TabStruct: Measuring Structural Fidelity of Tabular Data** · Xiangjian Jiang et al. · 🎤 ICLR 2026 Oral · [arXiv:2509.11950](https://arxiv.org/abs/2509.11950) |
| 📌 **线索来源** | Conclusion §"we find that existing evaluation methods often favour models that capture local causal interactions while neglecting global structure" + Future Work §"acts as an independent benchmark to assess whether a generator is underfitting or overfitting the training data" + §"SMOTE generally overfits to the training data ... rather than learning truly generalisable distributions" |
| 📮 **投稿建议** | 🧪 **ML** · ICLR / NeurIPS ＋ 🌐 WWW · KDD |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
TabStruct 提出在没有 ground-truth SCM 的情况下也能评估合成表格数据是否尊重真实因果结构，办法是 SCM-free 的 **global utility**：用合成数据训练下游预测器、在真实独立集上评估多个目标变量（而非单一标签）的可预测性。13 个生成器、29 个数据集的大规模实验给出一个尖锐结论：主流评测维度（密度、下游单任务效用、隐私 DCR）奖励的是"把局部条件分布拟合好"的模型，全局结构的破坏不会被惩罚；SMOTE 这种近邻插值在 Trend 上甚至能赢过独立真实集，纯属对训练集的过拟合。空隙在于：TabStruct 只是**诊断工具**，没有任何生成器把 global utility 放进训练目标；现有扩散/自回归表格生成器的损失仍是逐列或逐 token 的似然，天然对"变量间的全局依赖图"无约束。关键 insight：global utility 是可微近似的——"用合成数据训出的预测器在真实数据上泛化"等价于一个双层优化，而双层里内层可以用闭式或少步线性探针替代，使其可以当训练信号。

**💡 一句话 Idea**
把 TabStruct 的 SCM-free global utility 从评测指标变成训练目标：以"合成数据训练的多目标线性/树探针在真实留出集上的平均预测性能"作为可微（或 REINFORCE 近似）奖励，微调表格生成器，使其在不牺牲密度的前提下恢复全局结构。

**🛠️ 可能的解决方法**
1. **双层目标**：min_θ Σ_{j∈变量集} L_real( f_j*(θ) )，其中 f_j* 是在合成数据上用岭回归/逻辑回归闭式解得到的"以变量 j 为目标、其余为特征"的探针；闭式解使外层梯度可通过隐函数定理解析回传，避免展开内层优化。
2. **对离散/混合列的处理**：类别列用 one-hot + 带温度的 Gumbel-softmax 让采样可微；或对不可微生成器（如扩散的离散步）用 leave-one-variable-out 奖励 + GRPO 式组内归一化做无梯度优化。
3. **防过拟合约束**：按论文 Future Work 的 3:3:3:1 划分引入独立集 𝒟_indep，把"DCR 不超过 𝒟_indep 的 DCR"作为硬约束（拉格朗日罚项），直接实现作者建议的"以独立集为基准而非最大化 DCR"的平衡准则。
4. **结构正则作为廉价代理**：对生成样本估计偏相关矩阵（或用 NOTEARS 式连续结构分数），惩罚其与真实数据估计值的差异，作为 global utility 的低成本先验项，用于大维度表格。
5. **成本控制**：探针是闭式的，整条流水线相对基线训练只增加 O(d) 次小规模回归，单卡可跑完 29 个数据集。

**🧭 与最接近工作的区别**
- TabStruct（本论文）：提供 global utility 作为评测，明确未进入训练目标。
- TabDiff / TabSyn（2024–2025）：扩散式表格生成，目标是边缘与成对相关的似然，论文实测在新划分下 Trend 退化，说明其对全局结构无约束。
- Causal-TGAN / 需要已知 SCM 的因果生成器：依赖 ground-truth 图，正是 TabStruct 指出不可得的前提。

**🧪 验证方案**
- 基准：TabStruct 的 29 个数据集（含 SCM 合成集与真实集）；指标：global utility、column-wise density、Trend/α-precision、DCR 相对 𝒟_indep 的位置。
- 关键假设检验：在有 ground-truth SCM 的子集上，本方法生成数据恢复的结构汉明距离显著低于似然训练的生成器，且 global utility 提升不是靠牺牲密度得到（Pareto 前沿外移）。
- 消融：闭式探针 vs REINFORCE；去掉 DCR 约束（检查是否退化为记忆训练集，即 SMOTE 式作弊）；探针族（线性/GBDT）敏感性。

🔑 `tabular generation` `structural fidelity` `bilevel optimization` `causal structure` `synthetic data` `evaluation-as-objective`

[🔝 top](#top)

---

## 💡 Idea 11.4 — *Co-Evolving Task and Verifier: Difficulty-Matched Prompt–Rubric Curricula for Long-Form Deep Research*

| | |
|:--|:--|
| 🎯 **源论文** | **DR Tulu: Reinforcement Learning with Evolving Rubrics for Deep Research** · Rulin Shao et al. · 🎤 ICML 2026 Oral · [arXiv:2511.19399](https://arxiv.org/abs/2511.19399) |
| 📌 **线索来源** | Discussion §"we adapt the environment by updating the verifier (rubrics). Future work may consider jointly adapting both prompts and rubric criteria to further improve training efficiency" + §"scaling up this information often increases context length and compute costs" |
| 📮 **投稿建议** | 🧪 **ML** · ICML ＋ 🗣️ NLP · ACL |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
DR Tulu 把长文本深度研究的奖励从"可验证短答案"换成**随训练共同演化的 rubric**：每步用当前 rollout 的对比、检索到的新证据来更新评分细则，使反馈保持 on-policy 的区分度，8B 模型因此在四个长文研究基准上超过同量级开放模型。作者在 Appendix A 明确留了两个口子：(1) 只自适应了 verifier，没有同时自适应**任务分布（prompt）**；(2) "privileged information"（对比回答、外部检索、过程信息）虽然比堆 reward model 的推理 token 更有效，但上下文与算力成本随之上升，需要在固定预算下取舍。空隙在于：现有自适应课程工作（调 prompt 难度）与 DR Tulu（调 rubric）各做一半，而两者耦合时会出现一个此前没人处理的病态——**难度与可判别性可以互相补偿**：rubric 变细会让简单题也出现梯度，prompt 变难会让 rubric 失去区分度，若不联合控制，训练信号的有效方差无法稳定。关键 insight：可以把"组内奖励方差"当作共同的控制量，用它同时调度 prompt 难度与 rubric 粒度，并把 verifier 的算力当作第三个可调预算。

**💡 一句话 Idea**
用"组内奖励方差落在目标带内"这一单一信号联合调度任务难度、rubric 粒度和验证器算力，把深度研究 RL 变成一个显式的三变量预算分配问题，从而在相同 GPU 小时内获得更多有效梯度。

**🛠️ 可能的解决方法**
1. **双侧课程**：维护一个 prompt 池并为每个 prompt 估计近期组内通过率/奖励方差；按带状准则（如方差落在 [σ_lo, σ_hi]）采样 prompt，过易/过难者降权，与 rubric 更新交替进行。
2. **rubric 粒度控制器**：对每个 prompt 维护 rubric 条目数 k_x；当该 prompt 的组内奖励方差过低（rollout 难以区分）时由 rubric 生成器基于对比 rollout 扩展条目，过高时合并条目，形成 prompt 级的自适应判别率。
3. **验证器算力分配**：把 privileged information 的三类来源（对比回答 / 检索证据 / 过程轨迹）作为可选插件，按边际收益（加入该来源后奖励与人工/强判别器一致性的提升 ÷ token 成本）做贪心预算分配；低不确定度样本只用轻量 rubric 判定。
4. **防 rubric 漂移**：保留一个冻结的"锚 rubric"子集与少量人工标注的校验集，每 N 步检验新 rubric 的排序与锚一致（Kendall τ 门限），不通过则回滚，避免策略与 verifier 共同漂移到互相奖励的退化点。
5. **工程**：以 8B 策略 + 8B rubric 生成器复现 RLER 基线，再加入上述控制器；成本以"达到基线最终分数所需 GPU 小时"衡量。

**🧭 与最接近工作的区别**
- DR Tulu / RLER（本论文）：只演化 verifier，prompt 分布固定。
- 自适应 prompt 课程（如按通过率筛题的 DAPO 式动态采样、Zeng et al. 2025 的 prompt 调度）：只调任务难度，奖励函数固定。
- Rubrics-as-Rewards / 长文 rubric 奖励工作（2025）：rubric 静态且人工撰写，不随策略演化，也无算力预算分配。

**🧪 验证方案**
- 基准：DR Tulu 的四个长文深度研究基准（科学/健康/通用）+ 保留的人工偏好校验集；指标：最终分数、达到目标分数的 GPU 小时、有效梯度比例（非零优势样本占比）。
- 关键假设检验：联合调度下组内奖励方差分布显著收紧于目标带，且"锚 rubric 一致性"不随训练下降（无共同漂移）。
- 消融：只调 prompt / 只调 rubric / 两者都调；去掉验证器预算分配；去掉锚 rubric 回滚（预期出现奖励膨胀而人工评分停滞）。

🔑 `deep research` `evolving rubrics` `curriculum` `verifier compute` `reward hacking` `RL for agents`

[🔝 top](#top)

---

## 💡 Idea 11.5 — *Flow-Matched Forecasts Deserve Better Samplers: Horizon-Consistent Test-Time Search for Time-Series Foundation Models*

| | |
|:--|:--|
| 🎯 **源论文** | **Sundial: A Family of Highly Capable Time Series Foundation Models** · Yong Liu et al. · 🎤 ICML 2025 Oral · [arXiv:2502.00816](https://arxiv.org/abs/2502.00816) |
| 📌 **线索来源** | Limitations §"we only adopt a naïve sampling strategy that begins with random Gaussian noise, it leaves much room for future improvement in sampling strategy and post-processing" + §"multiple steps of autoregression may still lead to over-smooth predictions and unreliable results" |
| 📮 **投稿建议** | 🧪 **ML** · ICML / NeurIPS ＋ 🌐 WWW · KDD |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
Sundial 用 TimeFlow Loss（基于 flow matching 的 next-patch 分布预测）绕开离散 tokenization，在万亿点 TimeBench 上预训练，生成多条可能预测而非单点均值，显著缓解 MSE 训练导致的 mode collapse。但 Limitations 自认两件事：推理端只是"从高斯噪声出发的朴素采样"，以及**多步自回归仍会把预测抹平**。这正是生成式预测的结构性矛盾：patch 级分布建模是局部的，自回归把局部样本串起来时没有任何机制保证整条轨迹在全局上自洽（周期相位、累计和、趋势斜率），平均化于是在 horizon 后段重新出现。扩散/流匹配社区已有大量推理期技术（引导、SMC、best-of-n 重排），但几乎都针对图像的"单次全图生成"，没有处理**沿时间自回归拼接的一致性**，也没有时间序列特有的可验证约束。关键 insight：时间序列拥有图像所没有的廉价一致性检验量（谱峰相位、整段均值/方差、历史自相关、已知守恒或非负约束），它们可以作为近似似然把采样从"碰运气"变成"带约束的推理期搜索"，且完全不需要重训基座。

**💡 一句话 Idea**
给时间序列基础模型配一套推理期序贯搜索器：以频谱相位一致性、分段统计量匹配与领域硬约束作为可计算的"伪似然"，用粒子滤波式重采样在自回归 patch 之间筛选轨迹，在不重训的前提下同时提升概率预测质量并消除长 horizon 的过平滑。

**🛠️ 可能的解决方法**
1. **轨迹级伪似然**：定义 log w(y) = −λ₁·谱相位偏差（历史主周期在预测段的相位/幅值延续）−λ₂·分段均值方差与历史的分布距离 −λ₃·约束违规（非负、容量上限、总量守恒），权重用小规模验证集按 CRPS 调优。
2. **序贯重采样**：把自回归按 patch 划为阶段，每阶段对 M 条粒子做 flow-matching 采样，按累积 log w 做 systematic resampling（SMC），配合"回溯一个 patch 重采样"抑制退化；复杂度 O(M) 次前向，M=8–32 即可。
3. **引导式反向流**：在流匹配的 ODE/SDE 积分过程中加入 ∇log w 的引导项（对可微项如谱/统计量），相当于时间序列版 classifier guidance；不可微项（硬约束）只用于重采样阶段。
4. **抗过平滑的输出聚合**：报告中位数轨迹与分位数带，而非粒子平均（平均本身即过平滑的来源）；对点预测基准用"按伪似然加权的中位数"。
5. **成本控制**：全部为推理期方法，可对 Sundial / Chronos / TimesFM 等任意概率基座即插即用；可按预算自适应选 M（简单序列 M=4，高波动序列 M=32）。

**🧭 与最接近工作的区别**
- Sundial（本论文）：训练端解决 mode collapse，推理端明确留空。
- 扩散模型推理期引导 / FK-steering、SMC for diffusion（2024–2025）：面向图像单次生成，没有自回归阶段间的一致性与时间序列专属约束。
- TimeGrad / CSDI 等扩散预测器：训练目标不同，但同样采用朴素采样，本方法可直接作为其推理期插件对照。

**🧪 验证方案**
- 基准：GIFT-Eval、Monash、长时预测标准集；指标：CRPS、分位数损失、MASE，以及"长 horizon 过平滑度"（预测段高频能量 / 历史高频能量比）。
- 关键假设检验：随 horizon 增长，基线的高频能量比单调下降而本方法保持接近 1；CRPS 提升主要来自后 50% horizon。
- 消融：逐项去掉谱/统计/约束项；SMC vs best-of-n 重排 vs 纯引导；粒子数与成本曲线；在高频数据（论文自认弱项）上的专项测试。

🔑 `time series foundation model` `flow matching` `inference-time search` `sequential Monte Carlo` `probabilistic forecasting` `over-smoothing`

[🔝 top](#top)

---

## 💡 Idea 11.6 — *Where to Put the Basis: Residual-Driven Feature Resampling and Domain Decomposition for Gradient-Free PINNs*

| | |
|:--|:--|
| 🎯 **源论文** | **Fast training of accurate physics-informed neural networks without gradient descent** · Chinmay Datar et al. · 🎤 ICLR 2026 Oral · [arXiv:2405.20836](https://arxiv.org/abs/2405.20836) |
| 📌 **线索来源** | Conclusion §"While Frozen-PINNs efficiently deal with extreme temporal complexity ... dealing with spatial complexity encountered while solving PDEs like Navier–Stokes is an exciting next step, where one could leverage domain decomposition" + §"understanding the role of re-sampling network parameters in overcoming the Kolmogorov n-width barrier" |
| 📮 **投稿建议** | 🧪 **ML** · ICLR / NeurIPS ＋ 🔬 Science · J. Comput. Phys. |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
Frozen-PINN 用空间-时间分离 + 随机特征（ELM / SWIM 采样）把 PINN 的训练从梯度下降变成线性最小二乘，并按构造保持时间因果性，在九个 PDE 上比 SOTA PINN 快且准数个数量级，甚至不需要 GPU。作者自己划出的边界很清楚：方法擅长**时间复杂度**（极端对流速度、长时模拟），但**空间复杂度**（Navier–Stokes 那种多尺度结构）尚未解决；附录进一步给出机理——ELM 的基函数位置是数据无关的，解若有局部陡梯度就必须靠 SWIM 把基函数采到梯度大的地方，但 SWIM 用的是"香草"版本，且基函数的放置本身决定了误差的指数衰减能否发生。空隙在于：目前的随机特征放置是**一次性、全局、与残差无关**的；而经典自适应有限元几十年前就证明"按残差自适应加密"是攻克多尺度的关键。关键 insight：在线性最小二乘的框架下，残差是闭式可得的（解完一次 LSQ 立刻有逐点残差），因此可以做"求解—按残差重采样基函数—再求解"的廉价迭代，整个过程仍然没有一次梯度下降。

**💡 一句话 Idea**
把 Frozen-PINN 的随机特征采样改成残差驱动的自适应循环，并以重叠子域分解 + 界面罚项把它扩展到空间多尺度 PDE，使"无梯度下降"的速度优势延伸到 Navier–Stokes 级别的问题。

**🛠️ 可能的解决方法**
1. **残差驱动重采样**：解一次线性系统得到配点残差场 r(x)，以 |r(x)|^p 归一化为采样密度，用它重新采样（或增补）一批 SWIM 基函数的中心与方向；迭代 3–5 轮即停。每轮只增加一次 LSQ（可用增量 QR 复用上一轮分解）。
2. **基函数预算与剪枝**：对系数幅值接近零的基函数剪枝，把预算转移到高残差区域，保持总宽度不变，从而把"n-width 障碍"转化为"基函数位置的优化问题"而非单纯加宽。
3. **重叠域分解**：空间分为重叠子域，每个子域独立随机特征 + 局部 LSQ，界面上以罚项（解与法向通量连续）耦合，整体仍是一个稀疏最小二乘；采用 Schwarz 式交替求解，天然并行、无梯度。
4. **时间方向保持因果**：延续论文的空间-时间分离与时间步进结构，空间自适应在每个时间块内部进行，避免破坏因果性。
5. **诊断**：报告每轮的条件数与残差直方图，验证"基函数位置而非数量"是精度瓶颈。

**🧭 与最接近工作的区别**
- Frozen-PINN（本论文）：一次性 SWIM/ELM 采样，无残差反馈、无域分解。
- RAR / RAD 自适应配点（Wu et al., 2023）：自适应的是**配点**，网络仍用梯度下降训练；本 idea 自适应的是**基函数位置**且全程无梯度下降。
- FBPINN / XPINN（Moseley et al., 2023; Jagtap & Karniadakis, 2020）：域分解 + 梯度训练的 PINN；本 idea 把域分解放进线性最小二乘求解器。

**🧪 验证方案**
- 基准：论文的九个 PDE（含 Burgers 激波、高维扩散）+ 新增 2D Navier–Stokes（Kolmogorov flow）、多尺度 Helmholtz；指标：相对 L² 误差、墙钟时间、达到目标误差所需基函数数。
- 关键假设检验：固定总基函数数时，残差自适应比香草 SWIM 的误差低一个数量级以上（证明是"位置"而非"宽度"受限）；误差随轮次呈几何下降。
- 消融：无自适应 / 无剪枝 / 无域分解；界面罚权敏感性；与经典谱方法和高阶有限元在同等墙钟预算下对比。

🔑 `PINN` `random features` `least squares` `adaptive sampling` `domain decomposition` `multiscale PDE`

[🔝 top](#top)

---

## 💡 Idea 11.7 — *Budgeted Chunking: Content-Adaptive Compression Ratios for Tokenizer-Free Genomic Foundation Models*

| | |
|:--|:--|
| 🎯 **源论文** | **dnaHNet: A Scalable and Hierarchical Foundation Model for Genomic Sequence Learning** · Arnav Shah et al. · 🎤 ICML 2026 Oral · [arXiv:2602.10603](https://arxiv.org/abs/2602.10603) |
| 📌 **线索来源** | Limitations §"The fixed target compression ratios, while biologically motivated, may be suboptimal for non-coding or eukaryotic sequences" + Future Directions §"extending pretraining to eukaryotic genomes to test whether dynamic chunking discovers structures such as splice sites and enhancers" |
| 📮 **投稿建议** | 🧪 **ML** · ICML ＋ 🔬 Science · Bioinformatics / ISMB |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
dnaHNet 用可微动态分块把原始核苷酸端到端压缩成潜 token，摆脱固定词表对密码子/调控元件的切割，在原核基因组上比 StripedHyena2 的 scaling 更优（3× 推理效率），并且第一层自发学出三联密码子、第二层偏好标记启动子与基因间区。问题恰恰藏在它最漂亮的结果里：分块的**目标压缩率是固定超参**（靠辅助损失把平均块长拉到设定值）。原核基因组编码密度极高，固定压缩率勉强合适；而真核基因组的内含子/重复序列信息密度比外显子低一个量级，用同一个压缩率会把低信息区压得过细（浪费算力）、把高信息区压得过粗（丢失变异效应）。空隙在于：现有 H-Net 类工作把压缩率当全局常数，没人把它当成**按局部信息密度分配的预算**；而基因组恰好提供了可用的监督信号（序列熵、保守性评分、预测误差）。关键 insight：压缩率应当由"该片段的预测难度"决定，这可以用一个受总预算约束的边界门控来实现——相当于在序列上做可微的比特分配。

**💡 一句话 Idea**
把动态分块的固定目标压缩率替换为受全局预算约束的局部自适应压缩：由局部预测熵驱动边界概率，用拉格朗日乘子在线调节使整条序列的平均块长达标，从而在真核基因组上把算力自动倾斜给信息密集区。

**🛠️ 可能的解决方法**
1. **熵驱动门控**：边界概率 p(boundary at i) = σ(g(h_i, ĥ_i))，其中输入包含局部 next-nucleotide 预测熵与路由模块的隐状态；高熵（难预测、信息密集）处更倾向切出短块。
2. **预算约束而非固定比率**：把"平均块长 = L̄"从辅助 L2 损失改为不等式约束，用在线更新的拉格朗日乘子 λ 控制（类似 VQ 的 commitment 自适应或 constrained RL 的 dual ascent），使模型可以在序列内部自由分配而只在全局满足预算。
3. **分层预算分配**：两级 chunking 分别设预算，并允许第二级按第一级的压缩结果再分配（嵌套比特分配），对应论文观察到的"一级学密码子、二级学功能组织"。
4. **真核数据与评估**：在人/小鼠基因组上继续预训练，检验边界是否对齐剪接位点（GT-AG 边界）、增强子/启动子注释（用 ENCODE cCRE），用边界-注释互信息与 AUROC 量化，而不仅看困惑度。
5. **成本控制**：自适应压缩在低信息区产出更长块，理论上降低总 token 数；以"等效困惑度下的 FLOPs"与论文的 3.75× 对照，验证效率不退化。

**🧭 与最接近工作的区别**
- dnaHNet（本论文）与 H-Net（2025）：动态分块但目标压缩率是全局固定超参。
- Evo / StripedHyena2、Nucleotide Transformer：固定 k-mer 或单核苷酸词表，压缩率完全固定。
- 语音/文本的自适应下采样（如 CTC 式分段、Byte Latent Transformer 的熵分块，2024）：同样用熵分块但无全局预算约束与分层嵌套分配，也未面向基因组的功能元件对齐评估。

**🧪 验证方案**
- 基准：原核（复现论文设置）+ 真核（人/小鼠）预训练；下游：蛋白变异效应零样本预测、基因必需性分类、剪接位点与 cCRE 边界对齐、长上下文（≥1 Mb）困惑度。
- 关键假设检验：自适应压缩在真核上的"每 FLOP 困惑度"优于固定压缩率，且块长与保守性评分（phyloP）显著负相关。
- 消融：固定比率 vs 预算约束；熵特征去除；单级 vs 两级预算；预算值扫描（看是否存在明显最优而固定比率落在次优点）。

🔑 `genomic foundation model` `dynamic chunking` `tokenizer-free` `bit allocation` `eukaryotic genome` `scaling`

[🔝 top](#top)

---

## 💡 Idea 11.8 — *Specificity-Aware Test-Time Search: Avoiding In-Silico Metric Hacking in Atomistic Binder Design*

| | |
|:--|:--|
| 🎯 **源论文** | **Scaling Atomistic Protein Binder Design with Generative Pretraining and Test-Time Compute** · Kieran Didi et al. · 🎤 ICLR 2026 Oral · [arXiv:2603.27950](https://arxiv.org/abs/2603.27950) |
| 📌 **线索来源** | Limitations and Future Work §"While our evaluations are limited to in-silico success metrics, an important next step will be experimental validation" + §"could also target additional molecular properties—such as specificity or thermostability—by integrating suitable computational predictors into Complexa" (Appendix A) |
| 📮 **投稿建议** | 🧪 **ML** · ICLR ＋ 🔬 Science · ISMB / Nature Methods |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
Proteína-Complexa 用 AFDB 域-域相互作用构造的大规模合成二聚体数据集 Teddymer 做预训练，再用扩散/流模型的**推理期优化**（test-time scaling）直接在全原子空间搜索 binder，统一了"条件生成"与"hallucination"两条路线，无需序列重设计即达 SOTA，并示范了对界面氢键的优化。作者点明两处要害：评估全是 in-silico；以及特异性、热稳定性等性质尚未进入搜索目标。这两点是同一个风险的两面：推理期搜索本质上是在**优化一个代理打分器**，当打分器是 AF2/AF3 式 ipTM/PAE 时，搜索规模越大越容易找到"打分器喜欢但物理上不成立"的解——这正是 reward hacking 在结构生物学里的形态，而且 binder 最常见的湿实验失败模式恰恰是脱靶结合（特异性差）而非亲和力不足。空隙在于：现有 test-time scaling 工作（包括本文）只做单目标标量搜索，没有把"对非目标蛋白不结合"写进目标；而负靶信息是免费的（人类蛋白组、同家族旁系同源物）。关键 insight：特异性是一个**对比式**目标，可以用同一个结构预测器对负靶打分并取差值，把搜索从"最大化亲和代理"变成"最大化亲和-脱靶间隔"，这同时天然抑制了代理打分器的系统性偏差（偏差在正负靶上同向，被差值消掉）。

**💡 一句话 Idea**
把 binder 的推理期搜索目标从单靶亲和代理改为"目标靶与一组负靶之间的对比间隔"，并对多个独立代理打分器做最小值聚合，使 test-time compute 的增加换来可湿实验验证的特异性而不是代理指标过拟合。

**🛠️ 可能的解决方法**
1. **对比式搜索目标**：J(b) = s(b, target) − γ·softmax_β{ s(b, decoy_j) } − δ·不稳定性罚项，其中负靶集包含同家族旁系同源物、随机人类蛋白与"诱饵界面"；softmax_β 近似 max，惩罚最差的脱靶。
2. **打分器集合与最小值聚合**：s 取多个代理（AF 式 ipTM/PAE、物理力场打分如 Rosetta ddG、界面氢键/埋藏面积几何项）的**最小值或加权分位数**，使单一代理的盲点无法被搜索利用；在搜索中记录"代理间分歧度"作为可疑样本标志。
3. **搜索算法**：沿用论文的推理期优化框架（流模型上的引导/重排/粒子搜索），把 J 作为奖励；对可微项用梯度引导，对不可微项（Rosetta）只在重采样阶段使用，控制调用次数。
4. **留出代理防过拟合**：搜索时只用代理子集 A，评估时用完全留出的代理 B（含不同版本的结构预测器）；报告"搜索预算 vs 留出代理通过率"曲线——若曲线随预算先升后降，即直接量化了 metric hacking 的发生点。
5. **成本控制**：负靶打分可共享 target 无关的表示缓存；负靶集先用快速几何筛（界面互补性）粗筛再用贵代理精算。

**🧭 与最接近工作的区别**
- Proteína-Complexa（本论文）：统一生成与 hallucination 的推理期搜索，单目标 in-silico 代理，特异性明确列为未来工作。
- BindCraft / RFdiffusion + ProteinMPNN 流水线（2023–2024）：优化 AF2 置信度等单靶代理，脱靶不进入目标函数。
- 多目标蛋白设计/扩散引导工作：多以可微属性（溶解度、二级结构比例）为目标，没有把"对一组负靶的最差情形"作为对比间隔，也没有留出代理的 hacking 诊断。

**🧪 验证方案**
- 基准：论文的 de novo binder 设计目标集 + 同家族旁系同源物构成的特异性测试；指标：留出代理通过率、目标-脱靶间隔、设计多样性与可设计性 Pareto。
- 关键假设检验：对比式目标在**留出**代理上的通过率随 test-time compute 单调上升，而单目标基线在高预算区出现下降（hacking 曲线分离）。
- 消融：γ=0（退化为单靶）、单代理 vs 最小值聚合、负靶集构成（随机 vs 同家族）、是否含物理力场项；条件允许时对 Top-N 设计做表达与结合的湿实验验证。

🔑 `protein binder design` `test-time compute` `specificity` `reward hacking` `surrogate ensemble` `flow matching`

[🔝 top](#top)

---

## 💡 Idea 11.9 — *Curl-Budgeted Dynamics: Making Direct-Force Models Usable in Molecular Dynamics via Cheap Jacobian Diagnostics and Predictor–Corrector Integration*

| | |
|:--|:--|
| 🎯 **源论文** | **The dark side of the forces: assessing non-conservative force models for atomistic machine learning** · Filippo Bigi et al. · 🎤 ICML 2025 Oral · [arXiv:2412.11569](https://arxiv.org/abs/2412.11569) |
| 📌 **线索来源** | Discussion §"Non-conservative behavior also results in molecular dynamics trajectories exhibiting a spontaneous drift away from the desired thermodynamic conditions. Controlling this effect with thermostats requires careful tuning, and disrupts both time-dependent properties and the sampling efficiency" + §"assessing non-conservative behavior requires the explicit evaluation of the Jacobian both as diagnostics and as additional loss term" |
| 📮 **投稿建议** | 🧪 **ML** · ICML / NeurIPS ＋ 🔬 Science · JCTC / Nature Comm. |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
论文系统论证了"直接预测力"这一效率诱人的做法在真实微观模拟中的危险：力不再是能量的精确梯度，导致 MD 轨迹自发漂移出目标热力学条件，用恒温器压制则需精细调参并破坏时间相关性质与采样效率；而与旋转对称性不同，非保守性无法在推理期便宜地监测或用数据增强学会，必须显式计算 Jacobian。作者把"Jacobian 既作诊断量又作损失项"明确摆在桌面上，但没有给出做法：完整 Jacobian 是 3N×3N，对数千原子体系不可承受。空隙很具体：社区现在只有二选一——要么回到能量导数（慢但安全），要么用直接力（快但不可靠）；没人给出**定量的"可用性判据"**，也没人把非保守性当作可预算控制的量。关键 insight：真正影响长时统计量的不是整个 Jacobian，而是它的**反对称部分**（力场的"旋度"）；而反对称部分的范数可以用 Hutchinson 随机估计以 O(几次 JVP) 的代价无偏估计，这既能做在线诊断，也能做可微的罚项，而且可以在积分器层面做一次廉价的"保守化投影"。

**💡 一句话 Idea**
用随机估计的力场旋度（Jacobian 反对称部分）作为非保守性的可计算预算：训练时作为罚项、模拟时作为在线诊断与触发器，并给出一个预测-校正积分器，在旋度超阈值时才回退到能量梯度，从而在保留直接力速度的同时恢复可信的热力学统计。

**🛠️ 可能的解决方法**
1. **旋度罚项**：对直接力模型 F(x)，用 Hutchinson 估计 E_v‖(J − Jᵀ)v‖²（v 为 Rademacher 随机向量），每步只需 1–2 次 JVP/VJP；加入训练损失，权重按验证集上的能量守恒漂移率调节。该项为零当且仅当力场局部保守，是比"能量-力一致性损失"更直接的约束。
2. **在线诊断与触发**：MD 过程中每 k 步做一次随机旋度估计，维护滑动均值；超过阈值时该步改用保守骨干（能量梯度，或一个小的保守模型）计算力——即**预测-校正**：直接力做预测步，保守力做校正步，使累计能量漂移受控。
3. **混合模型架构**：F(x) = −∇E_θ(x) + G_φ(x)，显式分离保守主干与非保守残差，并对 G_φ 施加旋度罚与幅值预算；推理时可按需丢弃 G_φ 得到严格保守模型（安全模式）。
4. **统计量级验证**：不只看力的 MAE，而看长时统计量——NVE 能量漂移率、NVT 温度/压强稳定性、扩散系数、振动谱（VDOS）与自相关函数，这些正是论文指出被恒温器破坏的量。
5. **成本控制**：旋度估计与一次力计算同量级，诊断可低频执行；预测-校正只在少数步触发，整体仍显著快于全程能量导数。

**🧭 与最接近工作的区别**
- 本论文：诊断并警示非保守模型的问题，提出"需要 Jacobian 作诊断与损失"但未实现可扩展方案。
- 直接力模型（如 Neumann et al., 2024 的 Orb 系列、GemNet-T 的 direct-force 变体）：以效率为由放弃保守性，不提供旋度预算或回退机制。
- 保守力 MLIP（MACE、NequIP）：安全但需反向传播求力；本 idea 把它们用作校正步骤而非全程计算。

**🧪 验证方案**
- 基准：论文使用的体系 + 标准 MD 测试（液态水、Li 离子导体、分子晶体）；指标：NVE 能量漂移率、NVT 温度分布与目标的 KL、扩散系数与实验/保守模型基准的偏差、VDOS 谱误差、墙钟加速比。
- 关键假设检验：估计的旋度范数与长时能量漂移率呈显著单调关系（即它是一个有效的"可用性判据"）；加入旋度罚项后在同等力 MAE 下漂移率下降一个数量级以上。
- 消融：仅罚项 / 仅预测-校正 / 两者结合；触发阈值扫描；Hutchinson 样本数与估计方差；与"恒温器强压制"基线对比时间相关性质的损伤。

🔑 `machine learning interatomic potentials` `energy conservation` `molecular dynamics` `Jacobian estimation` `predictor-corrector` `direct force models`

[🔝 top](#top)

---

## 💡 Idea 11.10 — *Train Where It Is Hard: Similarity-Stratified Risk Minimization for Drug–Target Affinity Generalization*

| | |
|:--|:--|
| 🎯 **源论文** | **Rethinking the generalization of drug target affinity prediction algorithms via similarity aware evaluation** · Chenbin Zhang et al. · 🎤 ICLR 2025 Oral · [arXiv:2504.09481](https://arxiv.org/abs/2504.09481) |
| 📌 **线索来源** | Conclusion §"we show the generality of the imbalanced distribution of samples by randomized split and the consequent overshadowing of low-similarity samples" + §"split to create a “mimic split”, splitting the training set and internal test set by replicating the distribution found in an external test set" |
| 📮 **投稿建议** | 🧪 **ML** · ICLR ＋ 🔬 Science · Bioinformatics / ISMB |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★☆☆☆ |

**🔍 深入分析**
论文指出 DTA（药物-靶点亲和力）评测的系统性缺陷：随机划分的测试集被"与训练集高相似"的样本主导，模型在低相似样本上性能剧烈退化却被平均分掩盖；作者提出相似度感知划分（SAE）以构造任意期望的相似度分布，并用"mimic split"复制外部测试集的分布来选超参，显著改善外部表现。但这项工作全部落在**评测与超参选择**上：模型本身的训练目标没有变，仍是在高相似样本占绝对多数的训练分布上做经验风险最小化。空隙在于：既然相似度分层是可计算的（分子指纹 Tanimoto、蛋白序列同源性），那它就是一个现成的**环境标签**，可以直接驱动分布鲁棒优化或重加权；而现有 DTA 方法（DeepDTA 系列、图神经网络、预训练分子/蛋白编码器）普遍把它当作评测后的事后分析。关键 insight：低相似度样本的退化不只是数据量问题，更是**捷径问题**——模型学到了"与训练集近邻的记忆式匹配"；用相似度分层的组不变/最差组目标能把这条捷径的收益抹平。

**💡 一句话 Idea**
把 SAE 的相似度分层从评测搬进训练：以 (药物相似度, 靶点相似度) 二维分箱作为环境标签做分组分布鲁棒优化与近邻遮蔽式增强，使模型在低相似区间的误差显著下降而不牺牲整体精度。

**🛠️ 可能的解决方法**
1. **环境构造**：对每个训练样本计算其到训练集其余部分的最大药物相似度（ECFP4 Tanimoto）与最大靶点相似度（Smith-Waterman 归一化），按 3×3 分箱得到 9 个环境；注意相似度须在训练集内部按折计算以避免泄漏。
2. **最差组目标**：用 group DRO（指数权重更新最差组）或 CVaR 风险替代平均 MSE；为稳定起见对组损失做 EMA 平滑，并对样本量小的组加置信上界（避免噪声组吃掉全部权重）。
3. **近邻遮蔽增强**：训练时对高相似样本随机"遮蔽"其训练集近邻（在 batch 内禁止其最近邻共同出现，或对检索式模型屏蔽近邻），强制模型不能依赖记忆式匹配；相当于在训练中模拟低相似推理条件。
4. **不变性正则**：对不同相似度组的表示施加梯度惩罚或组间风险方差惩罚（V-REx 式），直接压低"误差随相似度下降而上升"的斜率，并把该斜率作为报告指标。
5. **成本控制**：相似度矩阵用论文给出的稀疏化策略（>95% 的相似度低于 1/3 可置零）即可扩展到 10⁵–10⁶ 规模；方法与具体编码器无关，可叠加在任意 DTA 骨干上。

**🧭 与最接近工作的区别**
- 本论文（SAE / mimic split）：改评测划分与超参选择，训练目标不变。
- 冷启动/scaffold split 评测工作（如 DTA 的 cold-drug/cold-target 设定、MoleculeNet scaffold split）：同样只定义更难的划分，不提供针对性训练目标。
- Group DRO / V-REx（2020–2021）：通用分布鲁棒方法，但依赖人工给定的组标签；本 idea 的贡献是把"与训练集的相似度"这一领域特有、可自动计算的量作为环境，并配合近邻遮蔽针对记忆式捷径。

**🧪 验证方案**
- 基准：Davis、KIBA、BindingDB 及论文使用的外部测试集；指标：按相似度分箱报告 RMSE/Pearson/CI，重点看最低相似箱与"误差-相似度斜率"，以及外部集表现。
- 关键假设检验：最差组误差显著下降且整体误差不退化（或退化 <1%）；误差-相似度斜率显著变平；近邻遮蔽单独即可带来可测提升（证明捷径假设）。
- 消融：ERM / 重加权 / group DRO / CVaR / +近邻遮蔽 / +方差惩罚；骨干模型（CNN 式 DeepDTA、图网络、预训练编码器）跨架构一致性；与 mimic split 超参选择叠加后的增益是否可加。

🔑 `drug-target affinity` `distribution shift` `group DRO` `similarity split` `shortcut learning` `generalization`

[🔝 top](#top)
