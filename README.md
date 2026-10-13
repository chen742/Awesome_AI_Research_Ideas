<a id="top"></a>
<div align="center">

# 🧠✨ Awesome AI Research Ideas

**从顶会 Best / Oral / Spotlight 论文与高引用工作的 *Limitation & Future Work* 中，提炼出有 novelty、有 impact 的研究 idea。**

[![Ideas](https://img.shields.io/badge/💡_Ideas-27-blueviolet?style=flat-square)](#-目录)
[![Categories](https://img.shields.io/badge/🗂️_Categories-8-8A2BE2?style=flat-square)](#-目录)
[![Sources](https://img.shields.io/badge/🏆_Award_Papers-30%2B-orange?style=flat-square)](#-来源雷达)
[![Last Commit](https://img.shields.io/github/last-commit/chen742/Awesome_AI_Research_Ideas?style=flat-square&color=teal&label=🕒%20updated)](https://github.com/chen742/Awesome_AI_Research_Ideas/commits/main)
[![Views](https://hits.sh/github.com/chen742/Awesome_AI_Research_Ideas.svg?style=flat-square&label=👀%20views&color=ff69b4)](https://hits.sh/github.com/chen742/Awesome_AI_Research_Ideas/)
[![Private Notebook](https://img.shields.io/badge/🔒_status-private_notebook-lightgrey?style=flat-square)](#)

<sub>🧭 ICLR · ICML · NeurIPS · CVPR · ICCV · ECCV · ACL · EMNLP · ICRA · IROS</sub>

</div>

---

> 💬 **这个仓库是什么？** 一本私人研究笔记。每一条 idea 都来自对一篇顶会获奖论文（或高引用工作）**limitation / future work / discussion** 的深入阅读：先定位论文自己承认的空隙，再判断这个空隙为什么没有被后续工作填上，然后给出 **一句话 idea + 一段 solid 的解决方案 + 一个深思熟虑的标题 + 验证方案**。
>
> 🧩 每条 idea 都标注了 ⭐ Novelty · 🚀 Impact · 🧗 Difficulty，并按方向分类。

## 📈 访问统计

<div align="center">

<img src="stats/views.svg" alt="views">

<!-- VIEWS:START -->
| 👀 累计浏览 | 🧑‍💻 独立访客 | 📥 累计克隆 | 🕒 更新于 |
|:--:|:--:|:--:|:--:|
| **0** | **0** | **0** | — |
<!-- VIEWS:END -->

</div>

<details>
<summary>🔧 统计是怎么工作的？（点击展开）</summary>

两套互补的计数：

1. **👀 hits.sh 徽章**（顶部 `views` 徽章）：每次 README 被渲染时 +1，实时，不需要任何配置。
2. **📈 GitHub 原生流量**（上面的表格 + `stats/views.svg`）：GitHub 只保留 14 天的流量数据，所以 [`.github/workflows/track-views.yml`](.github/workflows/track-views.yml) 每天运行一次 [`scripts/track_views.py`](scripts/track_views.py)，调用 Traffic API 把当天的 views / unique visitors / clones 累加进 [`stats/traffic.json`](stats/traffic.json)，重绘徽章并刷新这张表。这是**终身累计**的真实访问量，私有仓库同样有效。
   - 若 Actions 日志报 403：在 *Settings → Secrets → Actions* 添加一个 fine-grained PAT（权限 `Administration: Read-only`，仅限本仓库），命名为 `TRAFFIC_TOKEN`。
   - 也可以随时在 *Actions → 📈 Track repository views → Run workflow* 手动触发。

</details>

## 🧭 符号说明

| 符号 | 含义 | 符号 | 含义 |
|:--:|:--|:--:|:--|
| 🎯 | 源论文 | 📌 | 线索来源（Limitation / Future Work 的具体段落） |
| 🏆 | Best / Outstanding Paper | 🥈 | Runner-up / 🏅 Honorable Mention |
| 🎤 | Oral / Spotlight | 📈 | 高引用工作 |
| ⭐ | Novelty（新颖性） | 🚀 | Impact（影响力） |
| 🧗 | Difficulty（实现难度） | 🧪 | 验证方案 |
| 💡 | 一句话 idea | 🛠️ | 解决方案 |

<!-- INDEX:START -->
## 🗂️ 目录

| # | 类别 | 💡 数量 | 直达 |
|:--:|:--|:--:|:--|
| 1 | 🧠 LLM Reasoning & RL Post-Training | 3 | [ideas/01-llm-reasoning-rl](ideas/01-llm-reasoning-rl.md) |
| 2 | 🛡️ Alignment, Safety & Interpretability | 4 | [ideas/02-alignment-safety](ideas/02-alignment-safety.md) |
| 3 | 🌊 Diffusion & Generative Models (incl. Diffusion LLMs) | 3 | [ideas/03-diffusion-generative](ideas/03-diffusion-generative.md) |
| 4 | 🤝 Multi-Agent Systems & LLM Agents | 4 | [ideas/04-multi-agent-systems](ideas/04-multi-agent-systems.md) |
| 5 | 🤖 Embodied AI & Robotics | 3 | [ideas/05-embodied-robotics](ideas/05-embodied-robotics.md) |
| 6 | 👁️ Computer Vision & 3D | 4 | [ideas/06-vision-3d](ideas/06-vision-3d.md) |
| 8 | ⚙️ Architecture, Efficiency & Scaling | 3 | [ideas/08-architecture-efficiency](ideas/08-architecture-efficiency.md) |
| 9 | 🗣️ NLP & Language Understanding | 3 | [ideas/09-nlp-language](ideas/09-nlp-language.md) |

---

## 🧠 1 · LLM Reasoning & RL Post-Training

| 💡 Idea（点击查看完整分析） | 🎯 源论文 | ⭐ | 🚀 | 🧗 |
|:--|:--|:--:|:--:|:--:|
| [**Rescue-RL**: Reclaiming the Reasoning Boundary Lost under RLVR via Base-Model Replay and Problem-Adaptive Trust Regions](ideas/01-llm-reasoning-rl.md#-idea-11--rescue-rl-reclaiming-the-reasoning-boundary-lost-under-rlvr-via-base-model-replay-and-problem-adaptive-trust-regions) | Does Reinforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model? · 🥈 NeurIPS 2025 Best Paper Runner-Up | ★★★★☆ | ★★★★★ | ★★★☆☆ |
| [**Don't Commit Early**: Specification-Ledger Reinforcement Learning for Recoverable Multi-Turn Reasoning](ideas/01-llm-reasoning-rl.md#-idea-12--dont-commit-early-specification-ledger-reinforcement-learning-for-recoverable-multi-turn-reasoning) | LLMs Get Lost In Multi-Turn Conversation · 🏆 ICLR 2026 Outstanding Paper | ★★★★☆ | ★★★★★ | ★★★☆☆ |
| [**Seed-Conditioned Group Policy Optimization**: Learning to Be Diverse Without Raising Temperature](ideas/01-llm-reasoning-rl.md#-idea-13--seed-conditioned-group-policy-optimization-learning-to-be-diverse-without-raising-temperature) | Roll the Dice & Look Before You Leap: Going Beyond the Creative Limits of Next-Token Prediction · 🏆 ICML 2025 Outstanding Paper · 🏆 NeurIPS  | ★★★★★ | ★★★★☆ | ★★★☆☆ |

<div align="right"><a href="#top">🔝</a></div>

## 🛡️ 2 · Alignment, Safety & Interpretability

| 💡 Idea（点击查看完整分析） | 🎯 源论文 | ⭐ | 🚀 | 🧗 |
|:--|:--|:--:|:--:|:--:|
| [**Persistent Refusal**: Anchoring Safety Alignment to an Internal Intent State Rather Than Shallow Token Prefixes](ideas/02-alignment-safety.md#-idea-21--persistent-refusal-anchoring-safety-alignment-to-an-internal-intent-state-rather-than-shallow-token-prefixes) | Safety Alignment Should Be Made More Than Just a Few Tokens Deep · 🏆 ICLR 2025 Outstanding Paper | ★★★★☆ | ★★★★★ | ★★★☆☆ |
| [**From Pointwise to Set-Level Rewards**: Pluralistic RLHF Against the Artificial Hivemind](ideas/02-alignment-safety.md#-idea-22--from-pointwise-to-set-level-rewards-pluralistic-rlhf-against-the-artificial-hivemind) | Artificial Hivemind: The Open-Ended Homogeneity of Language Models (and Beyond) · 🏆 NeurIPS 2025 Best Paper | ★★★★★ | ★★★★★ | ★★★☆☆ |
| [**Ripple-Consistent Null-Space Editing**: Propagating Consequences While Preserving the Rest](ideas/02-alignment-safety.md#-idea-23--ripple-consistent-null-space-editing-propagating-consequences-while-preserving-the-rest) | AlphaEdit: Null-Space Constrained Model Editing for Language Models · 🏆 ICLR 2025 Outstanding Paper | ★★★★☆ | ★★★★☆ | ★★☆☆☆ |
| [**Anti-Squeeze Preference Optimization**: Controlling Where Probability Mass Goes During Off-Policy Alignment](ideas/02-alignment-safety.md#-idea-24--anti-squeeze-preference-optimization-controlling-where-probability-mass-goes-during-off-policy-alignment) | Learning Dynamics of LLM Finetuning · 🏆 ICLR 2025 Outstanding Paper | ★★★★☆ | ★★★★☆ | ★★☆☆☆ |

<div align="right"><a href="#top">🔝</a></div>

## 🌊 3 · Diffusion & Generative Models (incl. Diffusion LLMs)

| 💡 Idea（点击查看完整分析） | 🎯 源论文 | ⭐ | 🚀 | 🧗 |
|:--|:--|:--:|:--:|:--:|
| [**Order as a Policy**: Learning Where to Unmask in Diffusion Language Models under Constrained Order Families](ideas/03-diffusion-generative.md#-idea-31--order-as-a-policy-learning-where-to-unmask-in-diffusion-language-models-under-constrained-order-families) | The Flexibility Trap: Rethinking the Value of Arbitrary Order in Diffusion Language Models · 🏆 ICML 2026 Outstanding Paper ＋ **Train for the | ★★★★☆ | ★★★★★ | ★★★☆☆ |
| [**Twin-Denoiser Consistency**: Turning the Memorization-to-Generalization Transition into a Training Objective](ideas/03-diffusion-generative.md#-idea-32--twin-denoiser-consistency-turning-the-memorization-to-generalization-transition-into-a-training-objective) | Generalization in Diffusion Models Arises from Geometry-Adaptive Harmonic Representations · 🏆 ICLR 2024 Outstanding Paper | ★★★★★ | ★★★★☆ | ★★☆☆☆ |
| [**Entropy-Gated Next-Scale Prediction**: Spatially Adaptive Refinement Budgets for Visual Autoregressive Models](ideas/03-diffusion-generative.md#-idea-33--entropy-gated-next-scale-prediction-spatially-adaptive-refinement-budgets-for-visual-autoregressive-models) | Visual Autoregressive Modeling: Scalable Image Generation via Next-Scale Prediction · 🏆 NeurIPS 2024 Best Paper | ★★★★☆ | ★★★★☆ | ★★★☆☆ |

<div align="right"><a href="#top">🔝</a></div>

## 🤝 4 · Multi-Agent Systems & LLM Agents

| 💡 Idea（点击查看完整分析） | 🎯 源论文 | ⭐ | 🚀 | 🧗 |
|:--|:--|:--:|:--:|:--:|
| [**Blame-Aware Multi-Agent Policy Optimization**: Counterfactual Credit Assignment from Failure Taxonomies](ideas/04-multi-agent-systems.md#-idea-41--blame-aware-multi-agent-policy-optimization-counterfactual-credit-assignment-from-failure-taxonomies) | Why Do Multi-Agent LLM Systems Fail? · 📈 高引用 | ★★★★☆ | ★★★★★ | ★★★★☆ |
| [**Teammate-Aware Rewards**: Training LLM Agents to Optimize the Team's Future, Not the Current Turn](ideas/04-multi-agent-systems.md#-idea-42--teammate-aware-rewards-training-llm-agents-to-optimize-the-teams-future-not-the-current-turn) | CollabLLM: From Passive Responders to Active Collaborators · 🏆 ICML 2025 Outstanding Paper | ★★★★☆ | ★★★★☆ | ★★★☆☆ |
| [**Debate Needs Disagreement**: Engineering Epistemic Diversity in Multi-Agent LLM Deliberation](ideas/04-multi-agent-systems.md#-idea-43--debate-needs-disagreement-engineering-epistemic-diversity-in-multi-agent-llm-deliberation) | Improving Factuality and Reasoning in Language Models through Multiagent Debate · 📈 高引用 · 🏆 NeurIPS 2025 Best Paper | ★★★★☆ | ★★★★☆ | ★★☆☆☆ |
| [**Cost-Aware Amortized Workflow Synthesis**: One Generator for Any Task via Execution-Grounded RL](ideas/04-multi-agent-systems.md#-idea-44--cost-aware-amortized-workflow-synthesis-one-generator-for-any-task-via-execution-grounded-rl) | AFlow: Automating Agentic Workflow Generation · 🏆 ICLR 2025 Oral | ★★★☆☆ | ★★★★☆ | ★★★☆☆ |

<div align="right"><a href="#top">🔝</a></div>

## 🤖 5 · Embodied AI & Robotics

| 💡 Idea（点击查看完整分析） | 🎯 源论文 | ⭐ | 🚀 | 🧗 |
|:--|:--|:--:|:--:|:--:|
| [**Learned Potentials for Dynamically Composed Control**: Bridging Feedback Composition and Foundation Policies](ideas/05-embodied-robotics.md#-idea-51--learned-potentials-for-dynamically-composed-control-bridging-feedback-composition-and-foundation-policies) | No Plan but Everything under Control: Robustly Solving Sequential Tasks with Dynamically Composed Gradient Descent · 🏆 ICRA 2025 Best Paper  | ★★★★☆ | ★★★★☆ | ★★★★☆ |
| [**Which Demonstrations Matter? In-Run Data Shapley for Curating Cross-Embodiment Robot Pretraining Mixtures**](ideas/05-embodied-robotics.md#-idea-52--which-demonstrations-matter-in-run-data-shapley-for-curating-cross-embodiment-robot-pretraining-mixtures) | Robo-DM: Data Management for Large Robot Datasets · 🏆 ICRA 2025 Best Paper (Robot Learning) ＋ **Data Shapley in One Training Run** · 🏅 ICLR  | ★★★★☆ | ★★★★★ | ★★★☆☆ |
| [**Geometry-Consistent World Models**: Rewarding Generative Simulators for Being 3D-Consistent](ideas/05-embodied-robotics.md#-idea-53--geometry-consistent-world-models-rewarding-generative-simulators-for-being-3d-consistent) | Learning Interactive Real-World Simulators (UniSim) · 🏆 ICLR 2024 Outstanding Paper · 🏆 ICML 2024 Best Paper | ★★★★☆ | ★★★★☆ | ★★★★☆ |

<div align="right"><a href="#top">🔝</a></div>

## 👁️ 6 · Computer Vision & 3D

| 💡 Idea（点击查看完整分析） | 🎯 源论文 | ⭐ | 🚀 | 🧗 |
|:--|:--|:--:|:--:|:--:|
| [**Calibrated VGGT**: Metrics-Aware Covariance for Feed-Forward 3D Reconstruction and Downstream Bundle Adjustment](ideas/06-vision-3d.md#-idea-61--calibrated-vggt-metrics-aware-covariance-for-feed-forward-3d-reconstruction-and-downstream-bundle-adjustment) | VGGT: Visual Geometry Grounded Transformer · 🏆 CVPR 2025 Best Paper · 🏆 ICRA 2025 Best Conference Paper | ★★★★☆ | ★★★★★ | ★★★☆☆ |
| [**Objects Are Not Alone**: Relational Memory for Joint Multi-Object Promptable Video Segmentation](ideas/06-vision-3d.md#-idea-62--objects-are-not-alone-relational-memory-for-joint-multi-object-promptable-video-segmentation) | SAM 2: Segment Anything in Images and Videos · 🏅 ICLR 2025 Honorable Mention | ★★★★☆ | ★★★★☆ | ★★★☆☆ |
| [**Build Anything Buildable**: Stability-Verified RL for Assembly-Grounded 3D Generation](ideas/06-vision-3d.md#-idea-63--build-anything-buildable-stability-verified-rl-for-assembly-grounded-3d-generation) | Generating Physically Stable and Buildable Brick Structures from Text (BrickGPT) · 🏆 ICCV 2025 Best Paper (Marr Prize) | ★★★★☆ | ★★★★☆ | ★★★☆☆ |
| [**Task-Programmable Freeform Pixels**: Learning a Shared Minimalist Sensor Code for Many Vision Tasks](ideas/06-vision-3d.md#-idea-64--task-programmable-freeform-pixels-learning-a-shared-minimalist-sensor-code-for-many-vision-tasks) | Minimalist Vision with Freeform Pixels · 🏆 ECCV 2024 Best Paper | ★★★★☆ | ★★★☆☆ | ★★★☆☆ |

<div align="right"><a href="#top">🔝</a></div>

## ⚙️ 8 · Architecture, Efficiency & Scaling

| 💡 Idea（点击查看完整分析） | 🎯 源论文 | ⭐ | 🚀 | 🧗 |
|:--|:--|:--:|:--:|:--:|
| [**Gate-Guided KV Eviction**: Using Attention Gates as a Free Importance Oracle for Long-Context Inference](ideas/08-architecture-efficiency.md#-idea-81--gate-guided-kv-eviction-using-attention-gates-as-a-free-importance-oracle-for-long-context-inference) | Gated Attention for Large Language Models: Non-linearity, Sparsity, and Attention-Sink-Free · 🏆 NeurIPS 2025 Best Paper | ★★★★☆ | ★★★★★ | ★★☆☆☆ |
| [**Sparse Diffusion Attention**: Natively Trainable Block-Sparse Attention for Bidirectional Diffusion Language Models](ideas/08-architecture-efficiency.md#-idea-82--sparse-diffusion-attention-natively-trainable-block-sparse-attention-for-bidirectional-diffusion-language-models) | Native Sparse Attention: Hardware-Aligned and Natively Trainable Sparse Attention · 🏆 ACL 2025 Best Paper | ★★★★☆ | ★★★★★ | ★★★★☆ |
| [**From Succinct to Learnable**: Closing the Expressivity–Learnability Gap with Algorithmic Pretraining Curricula](ideas/08-architecture-efficiency.md#-idea-83--from-succinct-to-learnable-closing-the-expressivitylearnability-gap-with-algorithmic-pretraining-curricula) | Transformers are Inherently Succinct · 🏆 ICLR 2026 Outstanding Paper | ★★★★☆ | ★★★☆☆ | ★★★★☆ |

<div align="right"><a href="#top">🔝</a></div>

## 🗣️ 9 · NLP & Language Understanding

| 💡 Idea（点击查看完整分析） | 🎯 源论文 | ⭐ | 🚀 | 🧗 |
|:--|:--|:--:|:--:|:--:|
| [**Frequency-Aware Token Weighting**: Using Internet-Scale n-gram Counts to Curb Memorization in Pretraining](ideas/09-nlp-language.md#-idea-91--frequency-aware-token-weighting-using-internet-scale-n-gram-counts-to-curb-memorization-in-pretraining) | Infini-gram mini: Exact n-gram Search at the Internet Scale with FM-Index · 🏆 EMNLP 2025 Best Paper · 🏆 NeurIPS 2024 Best Paper | ★★★★☆ | ★★★★☆ | ★★★☆☆ |
| [**Learning to Elicit**: Active Field-Linguistics Agents for Low-Resource Language Documentation](ideas/09-nlp-language.md#-idea-92--learning-to-elicit-active-field-linguistics-agents-for-low-resource-language-documentation) | LingGym: How Far Are LLMs from Thinking Like Field Linguists? · 🏆 EMNLP 2025 Outstanding Paper | ★★★★★ | ★★★★☆ | ★★★★☆ |
| [**Context-Conditioned Fairness**: Teaching LLMs When Group Differences Should and Should Not Matter](ideas/09-nlp-language.md#-idea-93--context-conditioned-fairness-teaching-llms-when-group-differences-should-and-should-not-matter) | Fairness through Difference Awareness: Measuring Desired Group Discrimination in LLMs · 🏆 ACL 2025 Best Paper | ★★★★☆ | ★★★★☆ | ★★★☆☆ |

<div align="right"><a href="#top">🔝</a></div>
<!-- INDEX:END -->

---

## 🏆 来源雷达

<details open>
<summary><b>已挖掘的获奖 / 高引用论文（按会议）</b></summary>

| 会议 | 已挖掘的论文 |
|:--|:--|
| 🟣 **ICLR** | 2026 🏆 Transformers are Inherently Succinct · 2026 🏆 LLMs Get Lost in Multi-Turn Conversation · 2025 🏆 Safety Alignment…Few Tokens Deep · 2025 🏆 Learning Dynamics of LLM Finetuning · 2025 🏆 AlphaEdit · 2025 🏅 SAM 2 · 2025 🏅 Data Shapley in One Training Run · 2025 🎤 AFlow · 2024 🏆 Generalization in Diffusion Models (GAHB) · 2024 🏆 UniSim |
| 🔵 **ICML** | 2026 🏆 The Flexibility Trap · 2025 🏆 Roll the Dice & Look Before You Leap · 2025 🏆 CollabLLM · 2025 🏆 Train for the Worst, Plan for the Best · 2025 Which Agent Causes Task Failures and Where? · 2024 🏆 Genie · 2024 📈 Multiagent Debate |
| 🟠 **NeurIPS** | 2025 🏆 Artificial Hivemind · 2025 🏆 Gated Attention · 2025 🥈 Does RL Really Incentivize Reasoning Capacity? · 2024 🏆 VAR · 2024 🏆 Rho-1 (Not All Tokens Are What You Need) |
| 🟢 **CVPR / ICCV / ECCV** | CVPR 2025 🏆 VGGT · ICCV 2025 🏆 BrickGPT (Marr Prize) · ECCV 2024 🏆 Minimalist Vision with Freeform Pixels · CVPR 2026 🏆 D4RT（作为参照） |
| 🟡 **ACL / EMNLP** | ACL 2025 🏆 Native Sparse Attention · ACL 2025 🏆 Fairness through Difference Awareness · EMNLP 2025 🏆 Infini-gram mini · EMNLP 2025 🏆 LingGym (Outstanding) |
| 🔴 **ICRA / IROS** | ICRA 2025 🏆 MAC-VO (Best Conference Paper) · ICRA 2025 🏆 No Plan but Everything under Control · ICRA 2025 🏆 Robo-DM (Robot Learning) |
| 📈 **高引用** | Why Do Multi-Agent LLM Systems Fail? (MAST) · π0 / OpenVLA（作为参照） |

</details>

<details>
<summary><b>🎯 待挖掘队列（下一批）</b></summary>

- NeurIPS 2025 🏆 1000 Layer Networks for Self-Supervised RL · 🥈 Optimal Mistake Bounds for Transductive Online Learning
- ICML 2025 🏆 Conformal Prediction as Bayesian Quadrature · 🏆 Score Matching with Missing Data · 🏆 The Value of Prediction in Identifying the Worst-Off
- ICML 2026 🏆 High-Accuracy Sampling for Diffusion Models · 🏆 Position: The Alignment Community is Building a Censor's Toolkit
- CVPR 2026 🏆 D4RT · 🏆 Native and Compact Structured Latents for 3D Generation · 🏅 SAM 3D · 🏅 NitroGen
- ICCV 2025 🏅 Spatially-Varying Autofocus · 🏅 RayZer
- EMNLP 2025 Outstanding: Mind the Value-Action Gap · Measuring CoT Faithfulness by Unlearning · MiCRo
- ACL 2025 🏆 A Theory of Response Sampling in LLMs · 🏆 Language Models Resist Alignment · Outstanding: All That Glitters is Not Novel
- IROS 2025 🏆 Neural MP (Best Student Paper) · AgiBot World Colosseo (finalist)
- ICLR 2026 🏅 The Polar Express

</details>

## 🔬 方法论：一条 idea 是怎么产生的

```
 📄 获奖论文 ──► 📌 读 Limitation / Future Work / Discussion ──► ❓ 这个空隙为什么还没被填？
                                                                        │
      🏷️ 标题 ◄── 🧪 验证方案 ◄── 🛠️ solid 的方法 ◄── 💡 一句话 idea ◄── 🔍 定位真正的 insight
```

1. **只从论文自己承认的空隙出发**：Limitation / Future Work 是作者最了解、却没时间做的部分。
2. **交叉验证空隙是否仍然存在**：检查后续引用工作，确认没有被填上，或只被"打补丁"。
3. **优先选择两篇获奖论文的交叉点**（如 Hivemind × Roll the Dice、VGGT × MAC-VO）：交叉处 novelty 与 impact 通常同时满足。
4. **方法必须可实现**：写到目标函数、数据来源、训练算法、成本控制的粒度；给出可检验的关键假设。
5. **标题要能直接当论文标题用**：主标题说机制，副标题说问题。

## ✍️ 如何添加新 idea

1. 按 [`TEMPLATE.md`](TEMPLATE.md) 写入对应的 `ideas/0X-*.md`。
2. 在本页对应类别的表格加一行，并更新顶部 `Ideas` 徽章数字。
3. 可选：给标题加状态标签 `🟢 ready` / `🟡 exploring` / `🔵 in-progress` / `🟣 done` / `⚪ parked`。

## 🗺️ Roadmap

- [x] 🧱 建立结构、模板、8 个类别、27 条 idea
- [x] 📈 终身访问量计数（hits 徽章 + GitHub Traffic 累计）
- [ ] 🤖 自动抓取各会议新一届 award / oral 列表并开 issue 提醒挖掘
- [ ] 🔗 为每条 idea 增加"相关后续工作"追踪，标注空隙是否已被填补
- [ ] 🏷️ 状态看板（ready / exploring / in-progress / done）

---

<div align="center">
<sub>🔒 Private research notebook · maintained by <a href="https://github.com/chen742">@chen742</a> · 📅 since 2026-10</sub>
<br>
<a href="#top">🔝 Back to top</a>
</div>
