<a id="top"></a>
# 🔐 Security & Privacy

> 从 USENIX Security / IEEE S&P 获奖论文的 Limitation / Future Work / Discussion 中提炼的 idea，覆盖 Web 资产测量、网络与路由安全、协议与文件格式一致性、微架构隔离验证、软件测试、隐私与高风险用户、ML 系统的隐私与可验证性，目标投稿 USENIX Security / IEEE S&P / CCS / NDSS。
> 符号说明：🎯 源论文 · 📌 线索来源 · 📮 投稿建议 · ⭐ Novelty · 🚀 Impact · 🧗 Difficulty · 🧪 验证方案 · 🔑 关键词

[⬅️ 返回主页](../README.md)

---

## 💡 Idea 17.1 — *Functional Fingerprints: Normalized Semantic Hashing and Minimal Distinguishing Probes for Robust Web Application Version Inventory*

| | |
|:--|:--|
| 🎯 **源论文** | **Smudged Fingerprints: Characterizing and Improving the Performance of Web Application Fingerprinting** · Brian Kondracki et al. (Stony Brook) · 🏆 USENIX Security 2024 Distinguished Paper · [USENIX](https://www.usenix.org/conference/usenixsecurity24/presentation/kondracki) |
| 📌 **线索来源** | Discussion and Future Work §"we emphasize the need of creating improved web application fingerprinting techniques which utilize the functional aspects of application content to conduct fingerprinting, rather than all content in general." + Conclusion §"we find 82 instances in which a web application release which contains a severe vulnerability is labeled as a non-vulnerable version." |
| 📮 **投稿建议** | 🔐 **Security** · USENIX Security / IEEE S&P ＋ 🌐 WWW · WWW |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
论文用 Docker 化的 WASABO 框架在 1,360 个版本上评测 6 款指纹工具，发现工具过度依赖"部署时内容与训练时完全一致"：一旦管理员压缩 JS、改主题或 CDN 改写，版本判定就会给出跨越数年的多个候选，甚至把含严重漏洞的版本标成安全版本。对防守方（大型组织的资产清点、CERT 的补丁通知）而言，这意味着漏报高危资产。作者明确指出方向：基于"功能性内容"而非全部内容做指纹。空隙在于：现有工具把指纹当作静态特征匹配，没有利用"版本之间到底改了什么"这一可从源码仓库自动获得的信息。关键 insight：版本差异是稀疏的，只要从相邻 release 的 diff 中提取对部署变换不变的功能性差异（AST 级 JS 语义、路由与 API 行为、静态资源结构），就能构造少量、无害的 GET 探测，把版本区间收缩到一个"补丁等价类"，直接回答防守方真正关心的问题：该实例是否已修复某个 CVE。

**💡 一句话 Idea**
从开源 Web 应用相邻版本的源码 diff 中自动提取对压缩、主题、CDN 改写不变的功能性差异，构造信息增益最大的最小探测序列，把版本识别问题改写为"是否包含某修复"的补丁等价类判定。

**🛠️ 可能的解决方法**
1. **不变特征**：对 JS/CSS 做规范化（去空白注释、标识符 α-重命名、常量折叠）后取 AST 子树哈希；对 HTML 取 DOM 结构骨架；对后端取路由存在性与默认错误响应模式；每个特征标注其在部署变换（minify、bundle、主题替换、反代改写）下的稳定性，稳定性用 WASABO 上自动施加的变换集估计。
2. **版本格与补丁等价类**：把版本组织成格，每个 CVE 对应"已修复/未修复"划分；目标不是精确版本，而是给定 CVE 集合时的等价类，减少不必要的探测。
3. **主动探测选择**：把探测选择建模为自适应信息增益最大化（贪心近似，子模性下有 (1−1/e) 保证），每步选择能最大化切分剩余候选等价类的请求；预算控制在 ≤10 个只读 GET。
4. **鲁棒判定**：对不匹配特征采用加权投票并输出置信区间；探测失败（WAF、404）作为缺失值处理而非否定证据。
5. **工程**：复用 WASABO 自动部署全部版本，自动从 Git tag 抽取 diff，新增应用的人工成本主要是安装脚本。

**🧭 与最接近工作的区别**
- Wappalyzer / WhatWeb：基于固定正则与文件哈希的被动匹配，论文已证明对部署变换脆弱；本 idea 用变换不变特征和主动最小探测。
- 源论文本身：提供评测框架与问题刻画，未给出新的指纹方法；本 idea 直接回应其"功能性内容"方向，并把目标从版本号改为补丁状态。

**🧪 验证方案**
- 数据：WASABO 中 5 个应用的 1,360 个版本，施加 minify、bundle、主题、反代改写及其组合；再在授权的校园/合作单位网络资产上做真实环境验证。
- 指标：版本 top-1 准确率、候选集大小、CVE 补丁状态判定的漏报率（对应论文中 82 例误判）、每目标请求数。
- 对比：论文评测的 6 款工具；消融：去掉规范化、去掉主动选择、去掉稳定性加权。
- 伦理：仅发送只读请求，真实网络验证需资产所有者授权；发现未修复实例按 CERT 流程通知。

🔑 `web fingerprinting` `asset inventory` `patch status` `semantic hashing` `active probing` `measurement`

[🔝 top](#top)

---

## 💡 Idea 17.2 — *Release-Set Privacy Accounting: Auditing and Bounding Membership Leakage Across Families of Compressed Model Variants*

| | |
|:--|:--|
| 🎯 **源论文** | **CompLeak: Deep Learning Model Compression Exacerbates Privacy Leakage** · Na Li et al. · 🏆 USENIX Security 2026 Best Paper · [arXiv:2507.16872](https://arxiv.org/abs/2507.16872) |
| 📌 **线索来源** | VII Conclusion §"Notably, this leakage is further exacerbated when leveraging information from multiple compressed models." + V-D Discussion §"These critical findings highlight that model compression not only increases the number of member samples effectively inferred, but also amplifies the exposure of high-value members." |
| 📮 **投稿建议** | 🔐 **Security** · USENIX Security / IEEE S&P ＋ 🧪 ML · ICLR / NeurIPS |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
CompLeak 证明剪枝、量化、权重聚类都会放大成员推断风险，且同时可访问多个压缩版本时泄露更严重；其对照实验说明这种增益来自压缩引起的结构化输出差异，而非简单的"多模型集成"。更值得注意的是，因压缩而新暴露的样本多为成员且 Shapley 价值更高。这对模型发布方提出了一个现有隐私框架没有覆盖的问题：同一份训练数据衍生出的"版本族"（FP16、INT8、INT4、剪枝 50% 等）是一次性发布的，隐私风险应按**发布集合**而非单个模型核算。DP-SGD 只保证原模型，压缩是后处理，理论上不增加 DP 损失，但大多数商用模型并非 DP 训练。关键 insight：版本族之间的差异信号可以被当作一个可度量、可约束的量——如果压缩过程只依赖与成员身份无关的信息，或对差异做校准，发布集合的经验泄露就能被压回单模型水平。

**💡 一句话 Idea**
把多压缩版本发布视为一个联合发布机制，提出发布集合级的经验隐私审计（以最强多版本攻击为下界）和成员无关的压缩流程（用公开校准数据决定剪枝/量化参数并约束版本间输出差异），使整个版本族的泄露不超过单一原模型。

**🛠️ 可能的解决方法**
1. **审计协议**：给定版本族 {f₀, f₁…f_k}，以 CompLeak 的多版本攻击和 LiRA 式影子模型攻击作为最强已知攻击，报告低 FPR（0.1%）下的 TPR，以及按样本的"压缩后新暴露"集合；输出发布前的风险报告。
2. **成员无关压缩**：量化尺度、剪枝掩码、聚类中心只由公开校准集计算，不接触训练集；理论上若原模型为 (ε,δ)-DP，整个版本族仍为 (ε,δ)-DP（后处理），实验上检验非 DP 模型下这一做法能否降低差异信号。
3. **差异约束蒸馏**：压缩后用公开数据做一致性微调，损失 = 任务损失 + λ·E[KL(f_i(x)‖f₀(x))]，直接压缩版本间可被攻击利用的结构化差异。
4. **按价值保护**：针对论文发现的高 Shapley 价值成员，对影响最大的层采用更保守的量化位宽，形成可调的"隐私–体积"前沿。
5. **成本**：审计只需在少量影子模型上重复压缩流程，CIFAR / Purchase / BERT 微调规模单卡即可完成。

**🧭 与最接近工作的区别**
- 源论文引用的 Li et al.：只评估单一剪枝模型的成员推断；本 idea 处理多版本联合发布并给出缓解。
- LiRA（Carlini et al., IEEE S&P 2022）：单模型审计标准；本 idea 把审计单元扩展到版本族。
- DP-SGD（Abadi et al., CCS 2016）：给出原模型保证，但大多数部署模型并非 DP 训练；本 idea 面向非 DP 模型的实用发布规范。

**🧪 验证方案**
- 数据与模型：CompLeak 使用的图像/表格数据集与 BERT、GPT-2 微调；压缩工具为 TF-Lite 与 PyTorch 量化/剪枝。
- 指标：TPR@0.1%FPR、AUC、按样本新暴露率、模型精度与体积。
- 假设检验：(a) 成员无关压缩 + 差异约束后，多版本攻击优势降至单模型基线附近；(b) 精度损失 <1%。
- 对比：普通压缩、DP-SGD 原模型压缩；消融：仅成员无关校准 / 仅差异约束。

🔑 `membership inference` `model compression` `privacy auditing` `quantization` `release policy` `model families`

[🔝 top](#top)

---

## 💡 Idea 17.3 — *Phase-Aware Devices: Event-Temporal Access Control and Remote Protective Lockdown for High-Risk Activist Groups*

| | |
|:--|:--|
| 🎯 **源论文** | **Information Security in Small-Scale Protests: Surveillance of Ugandan Anti-EACOP Protesters** · Ntezi Mbabazi et al. · 🏆 USENIX Security 2026 Best Paper · [arXiv:2605.29621](https://arxiv.org/abs/2605.29621) |
| 📌 **线索来源** | 7 Conclusion: Future Work §"Future work might consider specific forms of access control that allow for information protection during a compromise, i.e. as it happens." + §"Future work might consider modelling temporality in the design of security technology, recognising that security needs are dynamic and change over time and place, such as before, during and after an event (e.g. protest, arrest)." |
| 📮 **投稿建议** | 🔐 **Security** · USENIX Security / IEEE S&P ＋ 📡 Networking · NSDI |
| ⭐ Novelty | ★★★★★ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
这项乌干达田野研究揭示：小规模学生抗议者面对的是会逮捕、审讯并没收设备的强大对手；他们依赖分层传递信息和"恢复出厂设置"来保护同伴，宁可丢数据也不愿泄露；同时流量资费限制使安全通信无法始终可用。作者提出两个设计方向：在"被攻破的当下"保护信息的访问控制，以及把时间性（事件前、中、后）纳入安全设计。现有工具基本是静态的：消息要么一直在设备上，要么由固定计时器删除；锁屏防护无法应对"设备在解锁状态下被夺走"或"被迫解锁"。关键 insight：抗议活动具有可预期的阶段结构，群体可以事先约定每个阶段的信息可见范围；把这些约定编码成随时间和群体信号变化的访问策略，就能在不依赖个人当场操作的情况下缩小被没收设备上的暴露面。

**💡 一句话 Idea**
设计一个面向小型活动团体的"阶段感知"访问控制层：消息与联系人按事件阶段（筹备、进行、事后）自动缩放可见范围，组内成员可在低带宽条件下（SMS 回退）为失联成员的设备触发保护性锁定，使信息在设备被夺取时仍受保护。

**🛠️ 可能的解决方法**
1. **策略模型**：每条消息带阶段标签和最小必要知情人集合；阶段转换由时间表、组长签名信号或"签到超时"触发；策略用简单的时序逻辑描述，便于形式化检查（如"事件开始后，非核心成员设备不可见具体地点"）。
2. **保护性锁定**：密钥分层——消息密钥由设备密钥与组内阈值份额共同派生；当 t-of-n 组员确认某成员失联，组内撤销其份额，被没收设备上的历史消息即无法再解密，无需设备在线配合（设备上线时同步销毁本地密钥）。
3. **低带宽回退**：控制信号（阶段切换、撤销）压缩到单条短信可承载的签名令牌，适应论文描述的数据资费限制。
4. **可用性设计**：与当地组织者共同设计（参与式设计），默认配置为最少操作；明确告知锁定会造成数据丢失，与参与者"保护优先于保存"的偏好一致。
5. **实现**：基于开源 Signal 协议库或 Matrix 客户端做原型，Android 优先；威胁模型排除对手掌握设备内核级取证工具的情况，并在论文中如实说明边界。

**🧭 与最接近工作的区别**
- Albrecht et al.（USENIX Security 2021）对香港抗议的集体信息安全研究：刻画大规模抗议实践；本 idea 针对小规模、高可见度群体并给出系统设计。
- Signal 消失消息：固定计时、与事件阶段无关，且设备被没收时无法远程追溯保护。
- MobiFlage（Skillen & Mannan, NDSS 2013）等可否认加密：面向个人被迫解密场景，不处理群体层面的阶段性知情范围。

**🧪 验证方案**
- 形式化：用 Tamarin 验证在设备被没收后，被撤销份额的密文对对手保持保密。
- 系统：测量短信信令延迟、锁定生效时间、电量和流量开销（目标：每日额外流量 <1MB）。
- 用户研究：与人权组织合作，在低风险环境中做情景模拟（桌面推演）与可用性评估（SUS、任务成功率）；不在真实抗议中部署实验。
- 伦理：IRB 高风险审查，参与者匿名、数据最小化，遵循源论文的风险评估做法。

🔑 `at-risk users` `temporal access control` `threshold cryptography` `device seizure` `participatory design` `usable security`

[🔝 top](#top)

---

## 💡 Idea 17.4 — *Opt-Out Without Blind Spots: Private Set Intersection for Operator-Side Compromise Self-Checks Against Threat-Intelligence Key Lists*

| | |
|:--|:--|
| 🎯 **源论文** | **Catch-22: Uncovering Compromised Hosts using SSH Public Keys** · Cristian Munteanu et al. (MPI-INF) · 🏆 USENIX Security 2025 Best Paper · [USENIX](https://www.usenix.org/conference/usenixsecurity25/presentation/munteanu) |
| 📌 **线索来源** | Discussion §"Depending on a measurement’s purpose, an operator opting out may, unintentionally, occlude malicious activity." + Internet Measurement Opt-Out and Ethics §"In our results, around 1% of compromised hosts is located within this hoster." |
| 📮 **投稿建议** | 🔐 **Security** · USENIX Security / CCS ＋ 📡 Networking · NSDI |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
Catch-22 利用 SSH 公钥认证只在密钥存在时才发出挑战这一行为，在不登录任何系统的前提下发现了 2 万多个被植入恶意密钥的账户。作者在讨论中指出一个伦理张力：某托管商曾退出测量，而该托管商恰好承载约 1% 的受害主机；退出测量会在无意中遮蔽恶意活动，伤害第三方。现有伦理讨论把"尊重退出"视为无代价。空隙在于：没有一种机制让退出方既不被外部扫描，又能获得同等的检测结果；同时威胁情报方往往也不愿公开恶意密钥全集。关键 insight：判定本质上是两个集合的交集——运营方主机上的 authorized_keys 指纹与威胁情报方的恶意密钥列表；用隐私集合求交（PSI）可以让运营方在本地完成检查，双方都不暴露各自的集合，从而把"外部扫描"替换为"自愿的私有自检"。

**💡 一句话 Idea**
为退出外部扫描的网络提供一个基于非平衡 PSI 的本地自检代理：运营方在主机上计算 authorized_keys 指纹并与威胁情报方的私有恶意密钥集求交，只得到命中结果，从而在尊重退出的同时消除测量盲区。

**🛠️ 可能的解决方法**
1. **协议**：采用非平衡 PSI（服务端集合大、客户端集合小），基于 OPRF + 布谷鸟过滤器，服务端定期发布加密过滤器，客户端每台主机只需一次 OPRF 交互；可选 PSI-cardinality 模式，只向研究者汇报命中数用于聚合统计。
2. **代理**：轻量 agent（或 Ansible 任务）枚举所有用户的 authorized_keys、发行版默认路径及 AuthorizedKeysCommand 配置，计算 SHA-256 指纹；不上传任何密钥原文。
3. **安全性**：半诚实模型下双方集合保密；对恶意服务端（塞入大量密钥探测运营方集合）用速率限制和集合大小承诺缓解，并在论文中分析剩余风险。
4. **部署激励**：与 CERT/Shadowserver 式通报渠道结合，命中结果直接生成处置建议；为退出扫描的托管商提供替代方案。
5. **成本**：OPRF 每主机毫秒级，过滤器百 KB 级，适合十万台主机规模。

**🧭 与最接近工作的区别**
- 源论文：外部主动扫描，需要目标未退出；本 idea 把检测移到运营方本地并保护双方数据。
- Kales et al.（USENIX Security 2019）移动端私有联系人发现：非平衡 PSI 用于社交场景；本 idea 将其用于威胁情报与运营方之间的入侵指标匹配。
- Have I Been Pwned 的 k-匿名范围查询：泄露哈希前缀，不保护查询方集合的全部信息；PSI 给出更强保证。

**🧪 验证方案**
- 正确性：在实验网络中植入测试密钥（非真实恶意密钥），检查召回率 100%、零误报。
- 等价性：在源论文同意参与的网络上，比较外部扫描结果与本地自检结果的一致性。
- 性能：10³–10⁵ 台主机、10³–10⁶ 条恶意密钥下的延迟、带宽与 CPU 开销。
- 用户研究：访谈托管商与 CSIRT 运营人员，评估部署意愿与退出动机是否被消除；伦理审批与 Menlo 原则。

🔑 `private set intersection` `SSH` `compromise detection` `threat intelligence` `measurement ethics` `opt-out`

[🔝 top](#top)

---

## 💡 Idea 17.5 — *Campaign Fingerprints Without Raw Audio: Privacy-Preserving Cross-Vantage Robocall Campaign Linkage for Enforcement*

| | |
|:--|:--|
| 🎯 **源论文** | **Characterizing Robocalls with Multiple Vantage Points** · Sathvik Prasad et al. (NC State) · 🏆 IEEE S&P 2025 Best Paper · [arXiv:2410.17361](https://arxiv.org/abs/2410.17361) |
| 📌 **线索来源** | VI Discussion and Recommendations §"Data sharing and collaboration is virtually impossible without a common model of robocalling." + §"Leveraging automated audio analysis techniques similar to the ones presented in this work can minimize manual analysis time and enable swift action against bad actors." |
| 📮 **投稿建议** | 🔐 **Security** · IEEE S&P / USENIX Security ＋ 📡 Networking · NSDI |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
论文汇集行业与学术语音蜜罐、执法数据与消费者投诉多个观测点，比较约 300 万通电话的音频与转写，发现执法行动几乎终结了相关活动，但各方缺乏统一的"活动"定义：有人把主题相似但音频不同的通话混为一谈，投诉类别长期停留在"其他"，仅凭主叫号码追踪又不可靠。作者呼吁统一建模与自动音频分析。现实障碍是：蜜罐数据受保密协议约束，录音可能含个人语音，运营商和执法机构无法直接共享原始音频。关键 insight：活动识别只需要"近重复音频"的判定，这可以通过对时间平移和编码鲁棒的感知指纹完成；若在本地把录音变换为不可逆的指纹并只交换指纹，就能在不共享原始音频的条件下跨观测点关联同一活动，为执法提供证据链。

**💡 一句话 Idea**
定义可跨数据源复用的形式化"活动"概念，各观测点在本地把语音变换为对编码、截断、噪声鲁棒的感知指纹，只共享指纹并用局部敏感哈希做跨源近重复匹配，从而在不交换原始录音的前提下实现跨观测点的活动关联与执法优先级排序。

**🛠️ 可能的解决方法**
1. **活动定义**：活动 = 音频近重复的通话簇（沿用论文 HDBSCAN 设定），并在其上分层加入"主题族"（基于转写的话题聚类），明确区分两种构造，解决论文指出的混用问题。
2. **鲁棒指纹**：基于频谱峰值星座图（Shazam 式）或自监督语音嵌入二值化，针对电话信道（G.711/AMR 编码、丢包、截断到 60 秒）做数据增强训练；指纹不可还原为可懂语音，在论文中用重建攻击测试其不可逆性。
3. **跨源匹配**：LSH 分桶 + 精确汉明距离验证；可选用安全计算（如基于 PSI 的阈值匹配）在指纹层面也不完全公开。
4. **执法排序**：为每个活动合并跨源计数、主叫号码分布、STIR/SHAKEN 认证级别，输出供执法与运营商回溯（traceback）使用的优先级列表。
5. **成本**：指纹提取 CPU 实时，百万级通话的索引可单机完成。

**🧭 与最接近工作的区别**
- Prasad et al.（USENIX Security 2020）：单一蜜罐上的音频聚类；本 idea 解决多方无法共享原始数据时的跨源关联。
- STIR/SHAKEN：验证主叫号码真实性，但不识别内容层面的活动；本 idea 与其互补。
- 源论文：在获得数据后集中分析；本 idea 将其方法转化为可在保密约束下运行的共享协议。

**🧪 验证方案**
- 数据：源论文类型的蜜罐录音与 FTC 投诉（在数据协议允许范围内），以集中式聚类结果作为真值。
- 指标：跨源活动关联的精确率/召回率、电话信道扰动下的鲁棒性、从指纹重建语音的可懂度（STOI/ASR 词错误率，越差越好）。
- 假设检验：仅共享指纹的关联结果与集中分析结果的一致度 >95%。
- 伦理：IRB 与法律审查；不共享原始录音；与执法机构的合作遵守数据协议。

🔑 `robocalls` `telephony abuse` `audio fingerprinting` `privacy-preserving data sharing` `measurement` `enforcement`

[🔝 top](#top)

---

## 💡 Idea 17.6 — *Soft Blocks in the Wild: Differential Rendering Detection of Silent Sanctions Geoblocking Across Sanctioned Regions*

| | |
|:--|:--|
| 🎯 **源论文** | **Digital Discrimination of Users in Sanctioned States: The Case of the Cuba Embargo** · Anna Ablove et al. (UMich) · 🏆 USENIX Security 2024 Distinguished Paper · [USENIX](https://www.usenix.org/conference/usenixsecurity24/presentation/ablove) |
| 📌 **线索来源** | Discussion and Recommendations §"We encourage service providers to serve meaningful blockpages that contain explicit language indicative of geoblocking." + Conclusion §"We identify 546 geoblocking with 17 diverse implementations, ranging from DNS failures to HTTP(S) response pages with a variety of status codes." |
| 📮 **投稿建议** | 🔐 **Security** · USENIX Security / IEEE S&P ＋ 🌐 WWW · WWW |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
论文首次系统测量古巴用户受制裁地理封锁的情况：在 Tranco Top 10K 中发现 546 个被封锁域名、17 种实现方式，88% 不给出原因，且有响应以 200 OK 返回封锁页。这意味着基于状态码或关键词的测量会系统性低估"静默封锁"。该研究只覆盖古巴一个国家、一次测量。空隙有两点：(1) 制裁封锁涉及多个国家和地区，缺少横向比较与纵向追踪；(2) 识别"返回 200 但内容不同"的软封锁需要内容层面的判定。关键 insight：同一 URL 从制裁地区与对照地区同时获取，比较的应是渲染后的页面语义而非原始字节；动态内容造成的差异可以用对照地区的多次重复获取估计基线，从而把软封锁判定转化为一个有统计控制的差分检测问题。

**💡 一句话 Idea**
从多个受制裁地区与对照地区同步抓取并渲染页面，以对照地区重复获取的自然变化作为零假设基线，用视觉与 DOM 语义差分检测"静默封锁"，建立跨地区、可持续运行的制裁封锁透明度测量。

**🛠️ 可能的解决方法**
1. **观测点**：在受制裁地区使用经伦理审查的合规观测方式（如自愿志愿者设备、已有研究平台中合法可用的节点），对照地区使用云节点；严格评估参与者风险，避免在法律风险高的地区招募个人。
2. **差分检测**：对每个 URL，在对照地区获取 k 次估计 DOM 结构、文本嵌入、截图感知哈希的自然变化分布；制裁地区响应若超出基线 99% 分位，判为候选封锁；再用轻量分类器区分封锁页、登录墙、本地化页面。
3. **层次归因**：结合 DNS、TCP、TLS、HTTP 各层失败模式，归因到 CDN、云平台或站点本身，复用论文 17 种实现分类并扩展。
4. **纵向追踪**：每月运行，关联制裁政策变化（如许可证颁布）与封锁变化，量化服务商的过度合规。
5. **公开数据**：发布聚合后的数据集与开放检测器，供公民社会组织使用。

**🧭 与最接近工作的区别**
- 源论文：单国家、单次测量，以状态码与人工检查为主；本 idea 做多地区、纵向、以内容差分识别软封锁。
- McDonald et al.（IMC 2018）"403 Forbidden"：基于 CDN 封锁页特征的全球地理封锁测量，难以发现 200 OK 静默封锁。
- Censored Planet（Sundara Raman et al., CCS 2020）：面向政府审查的远程测量；本 idea 关注服务商侧的制裁封锁。

**🧪 验证方案**
- 数据：Tranco Top 10K + 各地区本地常用服务列表；人工标注 1,000 对页面作为真值。
- 指标：软封锁检测精确率/召回率、各地区封锁率、透明度（是否说明原因）、随时间变化。
- 对比：状态码规则、关键词规则、源论文方法；消融：去掉对照基线、仅用 DOM 或仅用视觉。
- 伦理：IRB，Menlo 原则，参与者风险评估优先于覆盖率；向服务商反馈透明度建议。

🔑 `geoblocking` `sanctions` `internet measurement` `soft blockpages` `transparency` `censorship measurement`

[🔝 top](#top)

---

## 💡 Idea 17.7 — *Isolation Regression Testing: Continuous Contract-Based Verification of Kernel and Hypervisor Mitigations Across CPU Generations*

| | |
|:--|:--|
| 🎯 **源论文** | **Enter, Exit, Page Fault, Leak: Testing Isolation Boundaries for Microarchitectural Leaks** · Oleksii Oleksenko et al. (Microsoft) · 🏆 IEEE S&P 2026 Best Paper · [arXiv:2507.06039](https://arxiv.org/abs/2507.06039) |
| 📌 **线索来源** | IX Discussion §"Limitations. The search space for fuzzing the microarchitectural isolation is vast." + §"First, architectural information flows between actors, e.g., shared memory, are not supported. Second, self-modifying code is not supported." |
| 📮 **投稿建议** | 🔐 **Security** · IEEE S&P / USENIX Security ＋ 🖥️ Systems · OSDI |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
论文把基于模型的关系测试扩展到安全域之间（VM、内核、进程），用"actor"抽象描述各安全域，并用统计测量绕过不透明的微码。作者坦承搜索空间巨大，且尚不支持 actor 之间的显式共享内存与自修改代码。从防守方角度看，更迫切的问题是：操作系统与虚拟机监控器的缓解补丁频繁变更（新 CPU、新内核版本、新配置），每次变更都可能悄悄削弱隔离，而目前缺少能在 CI 中持续运行的回归测试。关键 insight：防守方不需要在全空间中寻找新漏洞，而需要验证"某个缓解配置在新平台上是否仍满足其声称的契约"；这使搜索可以以已有缓解的规格为中心进行定向，大幅缩小空间，同时补上共享内存这一真实系统中普遍存在的信息流。

**💡 一句话 Idea**
把隔离测试从"漏洞发现"改造为"缓解回归验证"：以每项内核/虚拟化缓解声称的隔离契约为中心定向生成测试，支持 actor 间声明式共享内存，在 CI 中针对新 CPU 与新内核版本持续检查缓解是否仍然成立。

**🛠️ 可能的解决方法**
1. **缓解契约库**：为常见缓解（如上下文切换时的预测器屏障、内核页表隔离、虚拟机进出时的缓冲区清理）写出可执行规格：在什么边界、哪些微架构状态应当不可观测。
2. **共享内存支持**：在模型中把共享页作为显式声明的架构信息流，契约追踪中区分"预期可见"与"不应可