<a id="top"></a>
# 🔐 Security & Privacy

> 从安全四大（USENIX Security / IEEE S&P / ACM CCS）的获奖论文的 Limitation / Future Work / Discussion 段落中提炼的 idea，覆盖软件与解释器模糊测试、协议与形式化验证、网络与互联网测量、Web/供应链安全、隐私审计、可验证机器学习与可用安全学术方法学等方向，目标投稿 USENIX Security / IEEE S&P / CCS / NDSS。每条都带清晰的威胁模型、真实目标与负责任披露考量。
> 符号说明：🎯 源论文 · 📌 线索来源 · 📮 投稿建议 · ⭐ Novelty · 🚀 Impact · 🧗 Difficulty · 🧪 验证方案 · 🔑 关键词

[⬅️ 返回主页](../README.md)

---

## 💡 Idea 17.1 — *Semantics-Carrying Coverage: Unifying Data, Automata, and Grammar Signals for Throughput-Aware Guided Fuzzing*

| | |
|:--|:--|
| 🎯 **源论文** | **Data Coverage for Guided Fuzzing** · Mingzhe Wang et al. (Tsinghua) · 🏆 USENIX Security 2024 Distinguished Paper · [USENIX](https://www.usenix.org/conference/usenixsecurity24/presentation/wang-mingzhe) |
| 📌 **线索来源** | Discussion §"While our enhancements to libFuzzer have yielded significant performance gains, the integration with other fuzzers and mechanisms is an area ripe for exploration." + Conclusion §"The major improvement comes from the static data, a sophisticated form of constant data with rich semantics." |
| 📮 **投稿建议** | 🔐 **Security** · USENIX Security / IEEE S&P ＋ 🖥️ Systems · OSDI |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
论文指出代码覆盖率只反映程序结构的一小部分：magic number、转移表、lookup table 等"富语义常量数据"无法被代码覆盖率或约束求解有效引导，于是提出 data coverage——检测对常量数据的新颖引用并最大化其覆盖，在 FuzzBench 上拿到最佳覆盖。但它把 data coverage 作为一个独立信号加到 libFuzzer 上，Discussion 明确坦言"与其它 fuzzer 和机制的整合尚待探索"。这是真正的空隙：现代 fuzzer 同时拥有边覆盖、cmplog/比较进度、data coverage、语法/自动机状态等多路异构信号，但调度器往往把它们简单拼成一个单调增长的 bitmap，无法回答"此刻哪一路信号的边际收益最高、吞吐代价最低"。关键 insight：不同信号的"单位吞吐收益"随 target 与阶段动态变化（解析磁头阶段 data coverage 价值高、进入业务逻辑后边覆盖价值高），应把信号选择建模为预算（执行吞吐）约束下的在线资源分配问题。

**💡 一句话 Idea**
把多路覆盖信号（边、比较进度、data coverage、语法状态）统一成带吞吐代价的"收益向量"，用在线 bandit 调度在每个 target/阶段动态决定插桩哪一路、以多大采样率收集，使每秒发现的新语义行为最大化而非盲目叠加 bitmap。

**🛠️ 可能的解决方法**
1. **统一信号层**：在 LLVM pass 中为每路信号打统一标签（edge/cmp/data/grammar-state），记录其插桩开销与命中率；data coverage 沿用论文的语义分类以控制吞吐。
2. **核心方法**：把"选择启用哪些信号子集"建模为带约束的 contextual bandit——context 为近期各信号的新覆盖增量与 exec/s，reward 为"新语义覆盖/秒"，用 Thompson sampling 周期性切换插桩配置；对高开销信号自适应降采样。
3. **机理动机**：覆盖增长呈阶段性饱和，固定权重会在饱和后浪费吞吐；在线分配把吞吐显式作为稀缺资源。
4. **工程可行性**：以 libFuzzer/AFL++ 为底座，信号可热插拔；在 FuzzBench 以 CPU-hour 为预算统一对比。

**🧭 与最接近工作的区别**
- 本源论文（Wang et al., 2024）贡献 data coverage 单一信号与静态调度；本 idea 做跨信号的在线预算调度。
- Entropy/AFL++ 的 schedule（如 Entropic, 2020）在种子层做能量分配，不在"覆盖信号种类"层做选择。
- CMPLOG/RedQueen（2019）只利用比较反馈；本 idea 把它作为可被调度的一路信号纳入统一框架。

**🧪 验证方案**
- 基准：FuzzBench 全套 + Magma（带 ground-truth bug）；指标：edge coverage、data coverage、唯一 bug 发现时间（TTB）、exec/s。
- 关键假设检验：(a) 在线调度在固定 CPU-hour 下不劣于任一单信号基线且在多数 target 更优；(b) 解析密集 target（LCMS、libpcap、图像/压缩格式）增益最大。
- 对比与消融：固定等权 / 仅 data coverage / 仅边覆盖 / 去掉吞吐代价项；统计用 Mann-Whitney + 多次重复（遵循 SoK 评测规范）。

🔑 `fuzzing` `coverage feedback` `data coverage` `online scheduling` `bandit` `FuzzBench`

[🔝 top](#top)

---

## 💡 Idea 17.2 — *Coverage-Guided Differential Parsing: Closing Semantic Gaps Between File-Format Implementations at the Source*

| | |
|:--|:--|
| 🎯 **源论文** | **My ZIP isn't your ZIP: Identifying and Exploiting Semantic Gaps Between ZIP Parsers** · Yufan You et al. (Tsinghua) · 🏆 USENIX Security 2025 Distinguished Paper · [USENIX](https://www.usenix.org/conference/usenixsecurity25/presentation/you) |
| 📌 **线索来源** | Limitation §"As a blackbox fuzzer, ZipDiff only receives the parsing outputs as feedback and does not utilize greybox feedback like code coverage. It might generate more sophisticated test samples with cross-language coverage-guided fuzzing." + Conclusion §"our work highlights the critical need for rigorously defined file formats and consistent parser implementations." |
| 📮 **投稿建议** | 🔐 **Security** · USENIX Security / CCS ＋ 🌐 WWW · WWW |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
论文用黑盒差分模糊测试 ZipDiff 对 19 种语言的 50 个 ZIP parser 做比较，几乎所有 parser 对都存在解析歧义，归纳出 3 类 14 种歧义，并对 Gmail/Outlook 等真实邮件服务负责任披露。但它只用解析输出做反馈，坦言缺少跨语言覆盖引导，因而难以主动驱动 parser 走向"分歧最大"的输入区域；同时它只发现歧义、不回答"歧义根因在哪条代码路径、如何修复"。威胁模型清晰：攻击者构造一个在 AV/网关解析器看来良性、但在终端解析器看来含恶意载荷的多义归档（content smuggling）。空隙在于：差分测试要高效定位分歧需要覆盖信号，而 50 个异构实现分散在 19 种语言，没有统一的覆盖度量。关键 insight：可以用跨语言的"结构化解析事件轨迹"（读取哪个 header 字段、走哪条分支）作为语言无关的覆盖代理，用分歧最大化作为目标函数做灰盒差分测试，并把分歧归约到最小可复现字段差异，直接产出面向标准化的修复建议。

**💡 一句话 Idea**
用语言无关的"解析事件覆盖"作为灰盒差分测试的反馈，以 parser 间输出分歧最大化为目标驱动变异，并对每个分歧做 delta 化字段归约，自动生成可用于格式标准化与实现对齐的根因报告。

**🛠️ 可能的解决方法**
1. **统一覆盖代理**：对每个 parser 轻量插桩（源可得者用 coverage，否则用结构化日志/解析器回调）记录"字段读取序列"，映射到统一的格式语法节点上作为覆盖向量。
2. **核心方法**：目标函数 = 加权（新覆盖 + parser 对输出分歧熵）；变异算子围绕格式关键字段（EOCD/central directory/local header 的偏移、长度、重复项），用覆盖引导走向冲突区域。
3. **根因归约**：对每个分歧样本做字段级 delta-debugging，输出"最小改动字段 → 各 parser 行为表"，供 RFC/实现维护者对齐。
4. **工程可行性**：复用源论文的 50 parser harness；覆盖代理对黑盒实现退化为解析事件序列，不破坏跨语言可比性。
5. **扩展**：同框架迁移到 PDF、TAR、PNG、Matroska 等"容器格式"。

**🧭 与最接近工作的区别**
- 本源论文 ZipDiff（2025）为黑盒、输出级反馈；本 idea 引入跨语言覆盖代理 + 分歧目标 + 根因归约。
- 协议/parser 差分测试如 Frankencerts（2014）、NEZHA（2017）用覆盖引导，但面向单语言二进制、无跨语言统一覆盖度量。
- 格式歧义 SoK 类工作多做人工归纳；本 idea 把"面向标准化的修复"做成自动产物。

**🧪 验证方案**
- 基准：源论文 50 个 ZIP parser + 新增 PDF/TAR parser 集；指标：单位时间发现的唯一歧义类型数、真实服务可利用 content-smuggling 场景覆盖、归约后字段差异的最小性。
- 关键假设检验：覆盖引导相比纯黑盒在相同预算下发现更多且更深的歧义；根因报告能被维护者接受为可操作 issue。
- 对比与消融：ZipDiff 黑盒基线 / 去覆盖项 / 去分歧目标；全程负责任披露，仅对自有账户与自建服务实测。

🔑 `differential fuzzing` `parser inconsistency` `file format` `content smuggling` `coverage-guided` `responsible disclosure`

[🔝 top](#top)

---

## 💡 Idea 17.3 — *Composable Channel Models: Joint Handshake-and-Record Formal Analysis of Secure Transport Protocols with Stateful Sequence Tracking*

| | |
|:--|:--|
| 🎯 **源论文** | **Terrapin Attack: Breaking SSH Channel Integrity By Sequence Number Manipulation** · Fabian Bäumer et al. (Ruhr University Bochum) · 🏆 USENIX Security 2024 Distinguished Paper · [arXiv:2312.12422](https://arxiv.org/abs/2312.12422) |
| 📌 **线索来源** | Future Work §"models of SSH for computer-aided proofs could (1) model the handshake as well as the BPP together, (2) keep track of sequence numbers in the BPP, including the handshake, which requires modeling integer numbers that can overflow as the internal state, (3) model seemingly unimportant messages like Ignore ... (4) consider each encryption mode separately." + §"Applying state learning to implementations also has the potential to find our attacks automatically." |
| 📮 **投稿建议** | 🔐 **Security** · IEEE S&P / USENIX Security ＋ 📡 Networking · NSDI |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
Terrapin 表明 SSH 二进制包协议不再是安全信道：通过在握手期间操纵序列号可做前缀截断，根因是握手记录从未被完整认证、序列号从不归零。作者在 Future Work 精确诊断了形式化方法的失败原因：既有证明把握手与记录层分开建模、把序列号抽象掉、忽略 Ignore/ExtInfo 等"看似无关"的消息，于是整类跨层攻击落在模型盲区之外。这不是单个 bug，而是形式化工具链的系统性空隙——计算机辅助证明（Tamarin/ProVerif）擅长密钥协商，却难以承载"可溢出整数状态、消息注入/删除、逐密码模式差异"的记录层细节。关键 insight：把握手与记录层合并为一个带显式序列号状态和 `ModifyState` 对手查询的组合信道模型，并用从实现中学到的状态机为符号模型提供"消息字母表 + 真实可达转移"，就能把这类跨层截断/重排攻击变成可自动发现、可证明可抵御的目标。

**💡 一句话 Idea**
构建一个把握手与记录层联合建模、显式跟踪可溢出序列号并引入 `ModifyState`（注入/删除/重排）对手查询的组合信道形式化框架，用实现侧状态学习提供真实消息字母表，自动发现并证明抵御 Terrapin 式跨层完整性攻击。

**🛠️ 可能的解决方法**
1. **模型表示**：在 Tamarin 中以多重集重写规则表达握手+BPP，序列号用有界整数项（含溢出语义）作为内部状态，逐密码模式（CBC-EtM/CTR/GCM/ChaCha20-Poly1305）分开实例化。
2. **对手能力**：新增 `ModifyState`/`Delete`/`Inject` 规则建模主动 MitM，覆盖 Ignore、ExtInfo 等消息。
3. **实现对齐**：对 OpenSSH/libssh/Dropbear 做主动状态学习（L*-风格）提取状态机，作为字母表与可达性约束喂给符号模型，缩减组合爆炸。
4. **安全目标**：验证 INT-aPTXT 等强完整性性质，证明官方 countermeasure（strict kex）确实消除攻击、并探测其它密码模式是否残留。
5. **工程可行性**：以本案例为种子，推广到 TLS 1.3 record/handshake 组合与 QUIC。

**🧭 与最接近工作的区别**
- 既有 SSH/TLS 形式化（如 Cremers 等 Tamarin TLS 1.3, 2017）分层建模、抽象序列号；本 idea 的贡献正是把被抽象掉的状态显式化并引入状态修改对手。
- 状态学习找实现 bug（如 Fiterau-Brostean 等 SSH state machine, 2017）不带密码学安全证明；本 idea 用学到的状态机约束符号证明。

**🧪 验证方案**
- 基准：SSH（多密码模式）+ TLS 1.3 record 层作为可迁移验证；指标：能否自动重现 Terrapin、证明 strict-kex 下性质成立、发现新的模式相关残留。
- 关键假设检验：实现状态学习提供的字母表显著缩小符号搜索、使合并模型可终止。
- 对比：分层旧模型（应漏报 Terrapin）vs 组合新模型（应命中）；消融去掉序列号溢出/去掉 Ignore 消息。

🔑 `formal verification` `SSH` `Tamarin` `channel integrity` `state learning` `protocol security`

[🔝 top](#top)

---

## 💡 Idea 17.4 — *Spec-Anchored Automata Learning: Reducing Expert Effort in Differential Testing of Cellular Baseband Control Planes*

| | |
|:--|:--|
| 🎯 **源论文** | **Logic Gone Astray: A Security Analysis Framework for the Control Plane Protocols of 5G Basebands** · Kai Tu et al. (Penn State) · 🏆 USENIX Security 2024 Distinguished Paper · [USENIX](https://www.usenix.org/conference/usenixsecurity24/presentation/tu) |
| 📌 **线索来源** | Discussion and Limitations §"5GBaseChecker requires domain expertise to define alphabet selection criteria and manual inspection of message formats to create an alphabet for testing. Additionally, the expert also needs to implement a 5G-specific adapter for converting symbols to concrete packets and vice versa." + Future Work §"we will extend 5GBaseChecker to analyze 5G session management procedures." |
| 📮 **投稿建议** | 🔐 **Security** · USENIX Security / IEEE S&P ＋ 📡 Networking · NSDI |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
5GBaseChecker 用黑盒自动机学习把 17 款商用基带与 2 个开源 UE 的控制面行为提取成 FSM，再差分比对发现偏离并与规范对齐，挖出 22 个实现级问题。但它的两处人力瓶颈限制了可扩展与可复现：输入字母表需专家手工选择、消息格式需手工检查，且需要为每个目标写 5G 特定 adapter；加上当前只覆盖注册/移动性而未覆盖会话管理。威胁模型清晰：实现级 FSM 偏离可被恶意基站/中间人用于降级、DoS 或绕过认证。空隙在于：字母表与适配器的"规范到符号"映射本可从 3GPP 规范文本与现成消息解码器（如 Open5GS/free5GC 的 ASN.1/NAS 定义）半自动导出，却仍靠专家。关键 insight：把 TS 24.501 等规范中的消息/信元定义作为结构化先验，结合主动学习的反例驱动，用"规范引导的字母表精化"替代手工字母表，并自动生成符号↔具体包的 adapter。

**💡 一句话 Idea**
用 3GPP 规范中结构化的 NAS/RRC 消息定义作为先验，驱动反例引导的字母表自动精化与 adapter 自动生成，把基带控制面差分测试从"专家密集"变为"规范密集"，并覆盖会话管理过程。

**🛠️ 可能的解决方法**
1. **规范先验**：解析 TS 24.501/38.331 的消息与信元定义，建立符号 ↔ 具体 NAS/RRC 包的映射骨架，自动生成 adapter 代码，专家仅复核。
2. **核心方法**：在 L*/TTT 自动机学习外层加"字母表精化循环"——当差分比对发现两实现对某抽象符号行为不同，自动按规范把该符号细化为更具体子符号重学，用反例指导细化粒度。
3. **会话管理扩展**：把 PDU session establishment/modification 纳入字母表，建模与注册态的耦合。
4. **工程可行性**：以 srsRAN + 开源核心网为可复现测试床，商用基带通过软件无线电接入；与源论文同口径统计偏离。
5. **安全三角**：偏离 → 规范属性 → 可利用性，输出负责任披露报告。

**🧭 与最接近工作的区别**
- 本源论文 5GBaseChecker（2024）手工字母表/adapter；本 idea 做规范引导的自动字母表精化与 adapter 合成。
- DIKEUE/DoLTEst 等（2022）聚焦 LTE 且仍需手工属性/字母表；本 idea 以规范结构化先验降低人力并扩到 5G 会话管理。

**🧪 验证方案**
- 基准：复现源论文的 17 基带/2 开源 UE 集合 + 新增会话管理用例；指标：达到同等偏离发现所需人工小时、字母表自动细化命中率、新发现属性违规数。
- 关键假设检验：规范引导的字母表在相同学习预算下不劣于专家字母表。
- 对比与消融：手工字母表 vs 自动精化；去掉规范先验仅靠随机细化。

🔑 `5G security` `automata learning` `differential testing` `baseband` `protocol conformance` `3GPP`

[🔝 top](#top)

---

## 💡 Idea 17.5 — *Behavioral-Fingerprint Corroboration: Reducing False Positives in Non-Intrusive Internet-Scale Compromised-Host Detection*

| | |
|:--|:--|
| 🎯 **源论文** | **Catch-22: Uncovering Compromised Hosts using SSH Public Keys** · Cristian Munteanu et al. (MPI-INF) · 🏆 USENIX Security 2025 Best Paper · [USENIX](https://www.usenix.org/conference/usenixsecurity25/presentation/munteanu) |
| 📌 **线索来源** | Discussion §"around 1% of compromised hosts is located within this hoster ... this single hoster not being included could have significantly changed our findings." + §"an operator opting out may, unintentionally, occlude malicious activity. This may not only impact research results, but also ... led to potential harm for third parties." |
| 📮 **投稿建议** | 🔐 **Security** · USENIX Security / CCS ＋ 📡 Networking · NSDI |
| ⭐ Novelty | ★★★☆☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
论文利用 SSH 仅对"已安装公钥"发送 challenge 的行为，设计出无需登录、无需访问即可在互联网规模识别被攻陷主机的方法，凭 52 个已验证恶意密钥在 144 国发现 2.1 万余台受控系统，且不触及被攻陷系统，伦理代价极低。但 Discussion 揭示两个关键局限：(1) 检测依赖单一信号（恶意公钥命中），覆盖度受威胁情报密钥列表完备性与测量 opt-out 的严重影响——单个 hoster 的 opt-out 就能左右 1% 结论；(2) 单信号易被攻击者轮换密钥规避。空隙在于：把"受控主机识别"从单一密钥命中升级为多信号、带不确定性的推断，既提升召回又给出每台主机的置信度，便于 CSIRT 优先清理。关键 insight：被同一威胁行为体控制的主机在非侵入可观测特征（证书/JA4+ 指纹、开放端口组合、自治系统、时序上线模式）上高度同构，可用这些侧写对密钥命中做"互证"，把缺失密钥的主机也纳入概率推断，同时显式建模 opt-out 导致的覆盖缺失。

**💡 一句话 Idea**
在非侵入密钥探测之上叠加被动可观测的行为指纹互证层，用概率图模型把"密钥命中 + 同构侧写"融合为每台主机的受控置信度，提升召回与稳健性，并显式刻画测量 opt-out 带来的覆盖偏差。

**🛠️ 可能的解决方法**
1. **数据与威胁模型**：对 IPv4/IPv6 做合乎伦理的被动+轻量主动测量（遵循 Menlo、IRB、opt-out），仅观测握手级特征，绝不登录系统。
2. **核心方法**：以已验证恶意密钥命中为锚点，用行为指纹（TLS/SSH 指纹、端口画像、AS、上线时序）构建相似度图，跑标签传播/概率图模型把受控置信度扩散到未命中但同构的主机。
3. **稳健性**：显式建模密钥轮换与 opt-out 为缺失机制，报告"覆盖校正后"的流行率区间而非点估计。
4. **工程可行性**：复用 ZMap 风格扫描 + 被动数据（如 passive DNS、证书透明日志），与国家 CSIRT 协作做通报与验证。

**🧭 与最接近工作的区别**
- 本源论文（2025）单密钥信号；本 idea 做多信号概率互证与覆盖偏差建模。
- Mirai/IoT 僵尸网络测量（如 Antonakakis et al., 2017）靠流量/蜜罐；本 idea 保持非侵入握手观测并输出每主机置信度。

**🧪 验证方案**
- 基准：以源论文已验证受控主机为正例、CSIRT 回执为验证；指标：召回提升、每主机置信度校准（ECE）、密钥轮换下稳健性。
- 关键假设检验：行为指纹互证能在密钥缺失下仍保持高精度；opt-out 校正后的流行率区间覆盖真实值。
- 对比与消融：单密钥基线 vs 多信号；去互证 / 去覆盖校正；全程负责任通报，不公开可定位个体主机的原始数据。

🔑 `internet measurement` `compromised hosts` `SSH` `threat intelligence` `probabilistic inference` `responsible disclosure`

[🔝 top](#top)

---

## 💡 Idea 17.6 — *Per-Prefix Risk Budgets: Adaptive-Threshold, Low-Alarm BGP Anomaly Detection with Semantic Routing Roles*

| | |
|:--|:--|
| 🎯 **源论文** | **Learning with Semantics: Towards a Semantics-Aware Routing Anomaly Detection System** · Yihao Chen et al. (Tsinghua) · 🏆 USENIX Security 2024 Distinguished Paper · [arXiv:2402.16025](https://arxiv.org/abs/2402.16025) |
| 📌 **线索来源** | Discussion §"Our system uses the same detection threshold values ... for all prefixes. Assigning an individual threshold for each prefix may gain better results. But it will incur significant computational overheads ..." + §"We can apply two heuristics to further reduce our system's false alarms ... We leave the application of both heuristics in our system to future work." |
| 📮 **投稿建议** | 🔐 **Security** · USENIX Security / IEEE S&P ＋ 📡 Networking · NSDI |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
BEAM 通过学习每个 AS 的"routing role"把 BGP 异常检测规约为观测到路由角色突变，在大型 ISP 一个月实测发现 497 个真实异常、日均仅 1.65 个误报。但 Discussion 坦言两处未填补：(1) 全网用统一阈值，逐前缀阈值虽更准却因 >94 万 IPv4 前缀的在线计算开销而未做；(2) 两条可大幅降误报的启发式（长寿命路由标记为正常、合法 MOAS 的同组织 AS 路由角色相似）留给未来工作。威胁模型清晰：前缀劫持/路由泄漏会被运营商在海量告警中淹没，误报是部署的首要障碍。空隙在于：逐前缀阈值的开销与收益从未被量化权衡，而这正是一个"告警预算"分配问题——运营商每天只能人工核查有限告警。关键 insight：不同前缀的风险价值与基线稳定性差异巨大（如关键基础设施前缀 vs 短寿命实验前缀），应把有限的"低阈值敏感度预算"集中分配给高价值、低噪声前缀，并用源论文提到的两条语义启发式做在线去噪，从而在同样告警预算下捕获更多真实异常。

**💡 一句话 Idea**
把 BGP 异常检测重构为告警预算下的逐前缀风险分配：用前缀价值与基线稳定性驱动自适应阈值，并以"路由角色相似的同组织 MOAS"和"长寿命路由"两条语义启发式在线抑噪，在同等人工核查预算下提升真实异常捕获率。

**🛠️ 可能的解决方法**
1. **数据**：RouteViews/RIPE RIS 大规模 announcement + 已确认劫持/泄漏事件（如 MANRS、历史 incident 库）。
2. **核心方法**：为每前缀估计基线波动与价值权重（critical infra、流量、层级），用带约束优化把全局告警预算分配为逐前缀阈值；在线用 BEAM 的角色嵌入计算 MOAS 组内相似度、路由寿命做去噪过滤。
3. **成本控制**：阈值按前缀簇共享参数（聚类 >94 万前缀到 O(10^3) 簇）避免逐前缀在线开销。
4. **工程可行性**：以 BEAM 嵌入为特征，增量更新；输出"告警预算–召回"曲线供运营商选点。

**🧭 与最接近工作的区别**
- 本源论文 BEAM（2024）统一阈值、未用两条启发式；本 idea 做预算驱动自适应阈值 + 语义去噪。
- ARTEMIS（2018）等前缀劫持检测靠自配置与数据平面验证，不做角色语义与告警预算优化。

**🧪 验证方案**
- 基准：源论文 18 个 RouteViews 数据集 + 大型 ISP 回放；指标：固定日均告警预算下的真实异常召回、误报率、检测延迟。
- 关键假设检验：预算集中到高价值低噪声前缀显著提升召回；聚类阈值共享不显著损失精度。
- 对比与消融：统一阈值 BEAM / 去 MOAS 启发式 / 去寿命启发式 / 逐前缀 vs 簇级阈值。

🔑 `BGP` `routing anomaly` `adaptive threshold` `alarm budget` `representation learning` `false positives`

[🔝 top](#top)

---

## 💡 Idea 17.7 — *Deployment-Incremental Relay Protection: Incentive-Aware Rollout and TEE-Reduced Trust for UWB-Secured Contactless Payments*

| | |
|:--|:--|
| 🎯 **源论文** | **PURE: Payments with UWB RElay-protection** · Daniele Coppola et al. (ETH Zürich) · 🏆 USENIX Security 2024 Distinguished Paper · [USENIX](https://www.usenix.org/conference/usenixsecurity24/presentation/coppola) |
| 📌 **线索来源** | Limitations and Future Work §"one limitation of PURE and other relay protections is that they are useful to cardholders only if they are largely deployed in all terminals. Otherwise, cardholders either have to use only a small subset of protected terminals ... or cards must support backward compatibility, remaining vulnerable to a relay to an unprotected terminal." + §"the use of Trusted Execution Environments (TEEs) could help reduce the trust assumptions on user and device." |
| 📮 **投稿建议** | 🔐 **Security** · IEEE S&P / USENIX Security ＋ 📡 Networking · NSDI |
| ⭐ Novelty | ★★★☆☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
PURE 首次把 UWB 测距安全集成进 EMV，在 Tamarin 中形式化验证、在真实手机上以可忽略开销部署、抵御已知距离缩减攻击。但它坦言两个现实障碍：(1) 部署的"全有或全无"困境——只要存在未保护终端，向后兼容的卡仍可被中继到该终端，保护形同虚设；(2) 对恶意持卡方的距离绑定仍是开放难题，需要当前商用硬件不具备的物理层能力。威胁模型清晰：攻击者把卡的交易中继到远处未保护终端完成欺诈。空隙在于：既有工作证明了单次交易的协议安全，却没有建模"渐进部署期"的系统安全——在只有部分终端支持 UWB 的真实过渡期，应如何通过发卡行/网络侧策略把向后兼容的攻击面降到最低。关键 insight：把过渡期的安全建模为"策略层风险控制"问题——在卡/发卡行侧用交易上下文（金额、商户类别、地理、UWB 可用性信号）做风险自适应的回退决策，并用手机 TEE 承载测距密钥与回退策略以降低对终端/用户的信任假设，从而在部署率 <100% 时也能提供可证明的风险上界。

**💡 一句话 Idea**
为 UWB 支付中继保护补上"渐进部署期"的系统安全层：用金额/商户/地理与 UWB 可用性驱动风险自适应的回退策略，并把测距密钥与策略置于手机 TEE，在部分部署下给出可证明的欺诈风险上界而非全有或全无。

**🛠️ 可能的解决方法**
1. **系统设计与威胁模型**：外部中继攻击者 + 部分终端支持 UWB；卡/手机侧可观测交易上下文与终端 UWB 能力标志。
2. **核心方法**：发卡行侧风险引擎——当终端不支持 UWB 时按上下文（高金额/异常地理/高风险 MCC）阶梯式要求额外认证或拒绝；用 Tamarin 把"协议 + 回退策略"联合建模，证明过渡期风险上界。
3. **TEE 集成**：测距密钥、回退策略与计数器放入手机 TEE（如 TrustZone），减少对用户/设备 OS 的信任；形式化其接口。
4. **工程可行性**：复用 PURE 的 UWB-HRP 原型 + EMV kernel；以真实手机测交易时延与回退触发率。

**🧭 与最接近工作的区别**
- 本源论文 PURE（2024）证明单次交易安全、把部署与恶意持卡方列为开放；本 idea 建模渐进部署期系统安全并引入 TEE 降信任。
- 距离绑定协议（如 Brands-Chaum 系列）关注单协议安全边界，不处理混合部署期的策略层风险控制。

**🧪 验证方案**
- 基准：EMV 交易轨迹（合成 + 公开商户类别分布）回放 + PURE 原型；指标：过渡期不同 UWB 部署率下的可证明风险上界、回退误拒率、交易时延。
- 关键假设检验：风险自适应回退在部署率 20–80% 时显著压低可利用中继面而对正常交易影响有限。
- 对比与消融：无策略向后兼容 vs 风险自适应；有/无 TEE 的信任假设对比；Tamarin 证明过渡期性质。

🔑 `contactless payment` `relay attack` `UWB` `distance bounding` `TEE` `incremental deployment`

[🔝 top](#top)

---

## 💡 Idea 17.8 — *Grounded-by-Construction Code Generation: Registry-Verified Decoding and Tokenizer Audits Against Package Hallucination in the Software Supply Chain*

| | |
|:--|:--|
| 🎯 **源论文** | **We Have a Package for You! A Comprehensive Analysis of Package Hallucinations by Code Generating LLMs** · Joseph Spracklen et al. (UT San Antonio) · 🏆 USENIX Security 2025 Best Paper · [arXiv:2406.10279](https://arxiv.org/abs/2406.10279) |
| 📌 **线索来源** | Discussion and Conclusion §"understanding the precise underlying causes of package hallucinations is still an open question. This includes exploring the architecture and components of LLMs that can contribute to these errors, examining the adequacy of tokenizers, and assessing how the composition of the training data ... impact hallucination tendencies." + §"Understanding how package hallucinations are systemic and persistent at the token level remains crucial." |
| 📮 **投稿建议** | 🔐 **Security** · USENIX Security / CCS ＋ 🧪 ML · ICLR / NeurIPS |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
论文系统评测了 16 个代码 LLM，发现 19.7% 生成的包是虚构的，构成"package confusion / slopsquatting"供应链攻击面（攻击者抢注高频幻觉名）。它负责任地没有把幻觉名真的注册到 PyPI。但 Future Work 把根因列为开放：tokenizer 是否把包名切成可被"拼接"的碎片、训练数据分布如何影响、幻觉为何在 token 级系统性持续。威胁模型清晰：开发者或 agent 直接 pip install 模型建议的包，落入攻击者抢注的恶意包。空隙在于：现有缓解多是生成后黑盒过滤（查注册表），既有延迟又无法解释"为什么模型偏偏爱编这些名"，更没有把注册表这一权威约束放进解码过程。关键 insight：包名空间是一个可枚举、带权威真值（PyPI/npm 索引）的受限词表，完全可以把"包名必须来自真实索引"作为解码期约束（受限/FSA-guided decoding），并把 tokenizer 对包名的切分充分性作为可量化、可审计的根因指标。

**💡 一句话 Idea**
把真实包索引作为解码期的硬约束（trie/FSA 引导的受限解码），让模型在 import/install 语句处只能生成注册表中存在的包名，并用"包名 token 切分充分性"指标系统归因 tokenizer 与训练分布对幻觉的贡献。

**🛠️ 可能的解决方法**
1. **数据与真值**：以 PyPI/npm 完整索引构建包名 trie；复用源论文的提示集与幻觉标注做评测。
2. **核心方法**：在生成到 import/require/install 上下文时切换到受限解码——用包名 trie 约束候选 token，仅允许能延伸为真实包名的前缀；对真正新包用显式"需人工确认"标记而非静默编造。
3. **根因归因**：定义 token 切分充分性（包名被切成多少跨语义碎片、碎片重组概率），在不同 tokenizer/模型上回归幻觉率，检验 Future Work 的 tokenizer 假设。
4. **工程可行性**：受限解码只在包名上下文触发，开销可控；索引可定期快照并带版本/时间戳防"未来包"泄漏。
5. **防御评估**：模拟 slopsquatting——统计攻击者能抢注的高频幻觉名在受限解码下归零。

**🧭 与最接近工作的区别**
- 本源论文（2025）测量幻觉并做黑盒后过滤建议；本 idea 把注册表约束放进解码并做 token 级根因归因。
- 受限/语法引导解码（如 outlines/GCD, 2023）用于 JSON/语法；本 idea 把它用于权威真值词表的供应链安全。

**🧪 验证方案**
- 基准：源论文提示集 + 真实 PyPI/npm 索引；指标：幻觉率（虚构包占比）、合法新包的漏过率、受限解码延迟、slopsquatting 可抢注名数量。
- 关键假设检验：token 切分充分性与幻觉率显著相关（支撑/否证 tokenizer 假设）；受限解码把幻觉率降到接近 0 而不显著伤害代码功能正确性（pass@k）。
- 对比与消融：无约束 / 后过滤 / 受限解码；不同 tokenizer 的归因实验。

🔑 `code LLM` `package hallucination` `supply chain security` `constrained decoding` `tokenizer` `slopsquatting`

[🔝 top](#top)

---

## 💡 Idea 17.9 — *One Detector, Many Modalities: Game-Theoretic Prompt-Injection Detection for Multimodal and Tool-Calling LLM Agents*

| | |
|:--|:--|
| 🎯 **源论文** | **DataSentinel: A Game-Theoretic Detection of Prompt Injection Attacks** · Yupei Liu et al. (Penn State) · 🏆 IEEE S&P 2025 Best Paper · [arXiv:2504.11358](https://arxiv.org/abs/2504.11358) |
| 📌 **线索来源** | Conclusion and Future Work §"Interesting future work includes 1) exploring stronger adaptive attacks ... and 2) extending our DataSentinel to detect prompt injection attacks to multi-modal models." + Discussion §"some contaminated target data samples that evade detection still cause the backend LLM to complete the injected task successfully." |
| 📮 **投稿建议** | 🔐 **Security** · IEEE S&P / USENIX Security ＋ 🧪 ML · ICLR / NeurIPS |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★★ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
DataSentinel 把提示注入检测建模为 minimax 博弈：微调一个检测 LLM 去识别为逃避检测而自适应优化的注入输入，用交替梯度法求解内层强攻击与外层检测，对现存与自适应文本注入都很有效。但它明确把两件事列为未来工作：(1) 更强自适应攻击；(2) 扩展到多模态模型。Discussion 还揭示一个微妙现象：有些逃过检测的样本仍使后端完成注入任务——即"检测通过"不等于"后端安全"，检测目标与后端行为存在错配。威胁模型清晰：攻击者把指令藏进数据（文本、图像像素/EXIF、文档、工具返回），诱导 agent 执行攻击者意图。空隙在于：纯文本博弈无法覆盖多模态/工具调用这一 agent 的真实攻击面，且 minimax 的检测目标没有与"后端是否真的被操纵"对齐。关键 insight：把博弈的内层攻击者扩展到跨模态注入通道、把检测目标从"输入被污染"改为"后端行为是否偏离良性意图"，用后端行为差异作为检测监督信号，能同时堵上模态缺口与目标错配。

**💡 一句话 Idea**
把 DataSentinel 的 minimax 检测扩展到多模态与工具调用通道，并用"后端行为相对良性输入的偏离"作为检测监督信号，训练一个跨模态、与后端对齐的注入检测器。

**🛠️ 可能的解决方法**
1. **威胁模型与数据**：注入通道含文本、图像（像素扰动/排版文字/元数据）、PDF、工具/检索返回；构造良性-污染配对。
2. **核心方法**：内层自适应攻击在多模态连续空间（图像像素）与离散空间（文本/工具输出）联合优化逃避；外层检测器以多模态编码器为骨干，minimax 交替训练。
3. **目标对齐**：新增"后端行为偏离"监督——对同一任务，良性输入与污染输入下后端输出/工具调用序列的差异作为正标签，解决"检测通过但后端被操纵"的错配。
4. **工程可行性**：检测器作为 agent 前置轻量 gate；对图像通道用 certified/随机平滑辅助评估稳健性。

**🧭 与最接近工作的区别**
- 本源论文 DataSentinel（2025）纯文本、检测输入污染；本 idea 跨模态 + 以后端行为对齐检测目标。
- StruQ/SecAlign（2024）加固后端而非检测；本 idea 走检测侧且显式处理"检测-后端错配"。
- 多模态注入研究（如图像越狱）多做攻击；本 idea 做博弈式检测防御。

**🧪 验证方案**
- 基准：文本注入基准（如 InjecAgent、源论文设置）+ 新建多模态/工具注入基准；指标：检测 AUC/FNR@低FPR、后端注入任务成功率、自适应攻击下的鲁棒性。
- 关键假设检验：行为对齐监督显著降低"检测通过但后端被操纵"的样本比例。
- 对比与消融：DataSentinel 文本基线 / 去行为对齐 / 单模态 vs 多模态；自适应 vs 非自适应攻击。

🔑 `prompt injection` `LLM agents` `multimodal security` `minimax` `detection` `tool calling`

[🔝 top](#top)

---

## 💡 Idea 17.10 — *Compression-Aware Privacy Auditing: Certifying Membership Leakage Across Pruning, Quantization, and Weight-Clustering Release Trees*

| | |
|:--|:--|
| 🎯 **源论文** | **CompLeak: Deep Learning Model Compression Exacerbates Privacy Leakage** · Na Li et al. · 🏆 USENIX Security 2026 Best Paper · [arXiv:2507.16872](https://arxiv.org/abs/2507.16872) |
| 📌 **线索来源** | V-D Discussion §"we further identify which samples amplify this leakage post-compression ... most of these samples are members ... these vulnerable members are relatively more important within the overall member set." + §"the results of CompLeak NR and CompLeak SR against MIA defenses using DP-SGD." |
| 📮 **投稿建议** | 🔐 **Security** · IEEE S&P / USENIX Security ＋ 🧪 ML · ICLR / NeurIPS |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★☆☆ |

**🔍 深入分析**
CompLeak 首次系统评估 pruning/quantization/weight clustering 三种商用压缩操作的隐私风险，发现它们都加剧成员推断泄漏，且当攻击者能访问"同一模型的多个压缩版本"时泄漏被进一步放大（stacking 多压缩模型的 loss）。Discussion 还发现放大的样本多为成员、且是 Shapley 价值高的重要成员。威胁模型清晰：厂商按资源/预算发布多个压缩版本（移动端、边缘端），攻击者聚合这些版本做成员推断。空隙在于：论文量化了"多压缩版本"这一新攻击面，却没有把它转成发布前的隐私审计工具——厂商无法在发布一棵"压缩发布树"（原模型 + 若干压缩变体）之前，预估这组发布联合起来会泄漏多少。关键 insight：压缩发布树应被当作一个整体来审计，其联合成员泄漏近似可由各变体输出差异的"结构化"程度（而非随机 seed 差异）刻画，据此可在发布前做组合级隐私风险估计，并指导"发布哪些变体 / 对哪些变体加 DP"的最小代价防御。

**💡 一句话 Idea**
把"同一模型的多个压缩版本"当作一棵发布树做组合级隐私审计：用变体间输出差异的结构化度量预估联合成员泄漏，在发布前给出风险上界并规划最小代价的 DP/变体裁剪防御。

**🛠️ 可能的解决方法**
1. **数据与威胁模型**：攻击者可查询发布树中任意子集的压缩变体；复用 CompLeak 的三类压缩与基准数据/架构。
2. **核心方法**：定义"联合泄漏审计分数"——以各变体 per-sample loss 向量的协方差/一致性度量结构化差异（区分压缩诱导 vs seed 诱导，呼应论文的 duplication 基线），回归到联合 MIA 的 TPR@低FPR。
3. **防御规划**：以"发布哪些变体 + 对哪些变体用 DP-SGD"为决策变量，在效用约束下最小化审计分数（整数规划/贪心）。
4. **理论动机**：高 Shapley 重要成员最易被放大，审计分数对其加权。
5. **工程可行性**：审计只需各变体的输出，不需重训；可作为发布 pipeline 插件。

**🧭 与最接近工作的区别**
- 本源论文 CompLeak（2026）量化多压缩版本放大、做攻击；本 idea 把它转为发布前组合级审计 + 最小代价防御规划。
- 单模型 MIA 审计（如 LiRA, 2022）与 Li et al. 的单剪枝模型分析不处理"发布树组合泄漏"。

**🧪 验证方案**
- 基准：CIFAR/ImageNet + 文本基础模型微调，按论文发布多压缩变体；指标：审计分数与实际联合 MIA（TPR@0.1%FPR）的相关性、DP 规划的隐私-效用 Pareto。
- 关键假设检验：结构化差异度量能区分压缩放大与 seed 变化；按审计分数加 DP 比均匀加 DP 代价更低。
- 对比与消融：单变体审计 vs 组合审计；去结构化度量仅用方差。

🔑 `membership inference` `model compression` `privacy auditing` `DP-SGD` `release tree` `MIA`

[🔝 top](#top)

---

## 💡 Idea 17.11 — *Verifiable by Design, Beyond Large-Spread: Training Boosted Ensembles for Polynomial-Time Robustness Certification Under General Norms*

| | |
|:--|:--|
| 🎯 **源论文** | **Verifiable Boosted Tree Ensembles** · Stefano Calzavara et al. (Ca' Foscari Venice) · 🏆 IEEE S&P 2025 Best Paper · [arXiv:2402.14988](https://arxiv.org/abs/2402.14988) |
| 📌 **线索来源** | Conclusion §"we would like to investigate different approaches to verifiable learning for tree ensembles, besides the large-spread condition advocated in existing work. Moreover, we plan to study how verifiable learning can be applied to fundamentally different classes of machine learning models, such as DNNs." + §"robustness verification ... remains NP-hard for other norm-based attackers." |
| 📮 **投稿建议** | 🔐 **Security** · IEEE S&P / USENIX Security ＋ 🧪 ML · ICLR / NeurIPS |
| ⭐ Novelty | ★★★★☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★★★☆ |

**🔍 深入分析**
论文把"可验证学习"从硬多数投票推广到 XGBoost/LightGBM 式 boosted 集成：在 L∞ 下可多项式时间验证鲁棒性，对其它范数 NP-hard，但给出伪多项式算法，实证在公开数据集上兼顾精度与高效验证。其核心机制是训练时施加 large-spread 条件使验证可处理。Conclusion 明确把两条未来方向留空：(1) 除 large-spread 外是否有别的"训练时可验证性约束"；(2) 推广到 DNN。空隙在于：large-spread 是一个较强且可能损害精度的充分条件，它把"可验证性"约束加在特征分裂阈值的间隔上，但并非唯一能换来多项式验证的结构；安全关键场景（恶意软件、欺诈、入侵检测的树模型）需要在精度损失更小的前提下获得对更一般范数（L1/L2，对应真实扰动预算）的高效认证。关键 insight：可把"可验证性"视为可微的训练正则——不是硬性 large-spread，而是惩罚那些使验证组合爆炸的分裂交互（跨树共享特征的阈值重叠），从而在精度-可验证性间连续权衡，并对 L1/L2 给出更紧的伪多项式/近似认证。

**💡 一句话 Idea**
用"可验证性正则"替代硬性 large-spread 条件训练 boosted 树集成：在训练目标里惩罚导致验证组合爆炸的跨树阈值交互，在精度-认证效率间连续权衡，并对 L1/L2 攻击者给出更紧的高效鲁棒性认证。

**🛠️ 可能的解决方法**
1. **数据与任务**：安全关键表格数据（恶意软件 EMBER、网络入侵 NSL-KDD/CIC-IDS、欺诈检测）+ 论文用的公开集。
2. **核心方法**：在 boosting 每轮分裂选择里加"可验证性代价"——度量候选分裂与已有树在同特征上的阈值重叠（重叠越多验证时交互越爆炸），作为软惩罚融入增益；得到连续 spread 而非硬条件。
3. **认证算法**：针对 L1/L2 设计基于该结构的伪多项式动态规划/松弛上界，给出 certified accuracy。
4. **理论动机**：验证复杂度由跨树特征交互图的树宽主导，正则即在降低该交互图复杂度。
5. **工程可行性**：改 LightGBM 分裂准则即可；认证器独立实现。

**🧭 与最接近工作的区别**
- 本源论文（2025）用硬 large-spread；本 idea 用可微可验证性正则做连续权衡，并聚焦 L1/L2 认证。
- 树集成鲁棒性验证（Chen et al., 2019; Ranum/Törnblom）做验证但不在训练时塑造可验证结构。

**🧪 验证方案**
- 基准：论文公开数据集 + 安全关键表格集；指标：clean accuracy、L∞/L1/L2 certified accuracy、平均验证时延、精度-认证效率 Pareto。
- 关键假设检验：可验证性正则在相同 certified accuracy 下比 large-spread 保留更多 clean accuracy；交互图树宽与验证时间正相关。
- 对比与消融：large-spread / 本正则 / 无约束 + 事后验证；不同正则强度。

🔑 `verifiable learning` `robustness certification` `gradient boosting` `tree ensembles` `adversarial robustness` `tabular security`

[🔝 top](#top)

---

## 💡 Idea 17.12 — *Transparency-as-Checklist: Automated Auditing of Open-Science Reporting in Usable Security and Privacy Research*

| | |
|:--|:--|
| 🎯 **源论文** | **How Transparent is Usable Privacy and Security Research? A Meta-Study on Current Research Transparency Practices** · Jan H. Klemmer et al. (CISPA) · 🏆 USENIX Security 2025 Best Paper · [USENIX](https://www.usenix.org/conference/usenixsecurity25/presentation/klemmer) |
| 📌 **线索来源** | Future Work & Outlook §"there were considerable changes recently, e.g., USENIX Security's new mandatory open science policy in 2025. It would be valuable to repeat our analysis in a few years to monitor the overall transparency development and how these policies impacted transparency." + Conclusion §"authors hosting artifacts on personal websites long-term often fails." |
| 📮 **投稿建议** | 🔐 **Security** · USENIX Security / IEEE S&P ＋ 🌐 WWW · WWW |
| ⭐ Novelty | ★★★☆☆ |
| 🚀 Impact | ★★★★☆ |
| 🧗 Difficulty | ★★☆☆☆ |

**🔍 深入分析**
论文人工分析 200 篇 UPS 论文对 52 条透明度标准的符合情况，发现社区整体重视透明度（均值 0.677）但无一篇全满足，并给出 10 条建议；同时发现把 artifact 托管在个人网站上长期常常失效。Future Work 明确希望"几年后重复分析，监测 2025 年 USENIX 强制开放科学政策的影响"。空隙在于：这项宝贵的测量是一次性人工标注，52 条标准的符合判定与 artifact 链接可用性检查都靠人力，无法随政策变化持续、规模化、跨会议地做；而政策（强制开放科学、CfA）的因果效果恰恰需要前后、跨会议的持续面板数据。关键 insight：52 条标准中大部分（是否声明 RQ、是否报告 limitations、是否有 IRB、是否公布 artifact 链接、链接是否存活、是否预注册）可用检索增强的 LLM 抽取 + 自动链接存活探测来可扩展判定，把一次性 meta-study 升级为持续运行的"透明度观测站"，用政策生效的自然实验做因果分解。

**💡 一句话 Idea**
把 UPS 透明度 meta-study 做成可持续运行的自动观测站：用检索增强 LLM 对 52 条透明度标准做可扩展、可校准的抽取，加上 artifact 链接长期存活探测，并以 2025 开放科学政策为自然实验做前后-跨会议的因果效果评估。

**🛠️ 可能的解决方法**
1. **数据与真值**：以源论文 200 篇人工标注为金标准校准集，扩到 USENIX/S&P/CCS/SOUPS/CHI 多年全量论文。
2. **核心方法**：对每条标准训练/提示一个抽取器（RAG + 结构化输出），报告每条的置信度与人工复核采样；artifact 链接做周期性存活探测（HTTP + 内容指纹，区分 DOI/机构仓库 vs 个人网站）。
3. **因果分解**：以强制开放科学政策/CfA 生效时间为断点，用 difference-in-differences（政策会议 vs 未变会议）估计透明度提升，控制领域与年份。
4. **校准与可信**：报告抽取器与人工的一致性（κ）、对少数难判标准（positionality、预注册）保留人工环节。
5. **工程可行性**：纯公开文献数据、无人类受试，伦理门槛低；产出公开 dashboard 与可复现 pipeline。

**🧭 与最接近工作的区别**
- 本源论文（2025）为一次性人工 meta-study；本 idea 做可扩展自动化 + 链接存活面板 + 政策因果分析。
- 可复现性 checklist 自动检查（如 ML 领域的部分工作）多针对代码/数据存在性；本 idea 覆盖 UPS 特有的 52 条（含 IRB、consent、披露流程）并做跨会议纵向因果。

**🧪 验证方案**
- 基准：源论文 200 篇金标准；指标：每条标准抽取的 precision/recall 与 κ、链接存活探测准确率、DiD 估计的政策效应及置信区间。
- 关键假设检验：自动抽取在高置信标准上达到接近人工一致性；强制开放科学政策显著提升 artifact 可得性与存活率。
- 对比与消融：LLM 抽取 vs 关键词规则 vs 人工；有/无 RAG；个人网站 vs 机构仓库的长期存活对比。

🔑 `usable security` `research transparency` `open science` `meta-science` `reproducibility` `causal evaluation`

[🔝 top](#top)
