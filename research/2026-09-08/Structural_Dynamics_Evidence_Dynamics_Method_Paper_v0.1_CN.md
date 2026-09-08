# Structural Dynamics + Evidence Dynamics：一种可审计的结构动力学与公共证据一致性研究框架
## 阶段性方法论文 v0.1

**版本：** v0.1  
**日期：** 2026-09-08  
**研究状态：** METHOD PILOT  
**首个实证对象：** Strategy Inc.（NASDAQ: MSTR）  
**研究框架：** RDL × RTP × ECN × Structural Dynamics × ECL  
**声明：** 本文是一份阶段性方法论文，不构成投资建议、交易授权、法律判断或对任何实体的不当行为指控。

---

## 摘要

现实系统的研究通常面临两个容易被混淆的问题：第一，系统本身正在发生什么；第二，关于该系统的公开证据是否彼此一致。传统市场分析、公司研究和事实核查往往将数据来源、数据真实性、结构解释和最终结论压缩为一条判断链，从而容易把“来源被记录”误写成“内容真实”，把“表面冲突”误写成“事实矛盾”，甚至把“证据不一致”升级为“欺诈或误导”。

本文提出一个双轨研究框架：

```text
Structural Dynamics + Evidence Dynamics
```

其中，**Structural Dynamics** 研究现实系统的结构、状态与转移；**Evidence Dynamics** 研究围绕同一实体形成的公开证据、声明、观测、修订和冲突。Evidence Consistency Layer（ECL）作为 Evidence Dynamics 的核心分析层，不负责自动判断谁“说真话”，而负责回答一个更有限但可审计的问题：

> 一组被冻结的公开证据，在完成实体、时间、单位、范围与来源依赖校正之后，能否同时成立？

ECL 结合多源/多方法/多分析者/多视角三角验证思想、Analysis of Competing Hypotheses（ACH）式竞争假设分析，以及基于 provenance 的证据链冻结。框架永久区分：

```text
Artifact Integrity ≠ Content Truth
Public Claim ≠ Reality
Multiple URLs ≠ Independent Sources
Change ≠ Contradiction
Inconsistency ≠ Falsehood
Observed Contradiction ≠ Potential Falsifier
```

本文以 Strategy Inc. 2026 年公开披露为首个方法 Pilot。研究围绕 Bitcoin 作为主要 treasury reserve asset、BTC monetization、USD Reserve、资本募集、优先股义务及软件经营之间的关系建立证据链。Pilot 最终得到：

```text
Structural Dynamics:
HYBRID_ACCUMULATION_MONETIZATION

Evidence Dynamics:
SEMANTIC_TENSION_BUT_RECONCILABLE

MATERIAL_INCONSISTENCY = NO
```

这一负结果具有方法意义：ECL 没有为了“发现问题”而制造问题，而是在时间、范围、定义、数值和竞争假设校正后，将一个表面冲突降解为可协调的语义张力。

---

# 1. 研究问题

我们希望建立的不是一个“自动事实判定器”，而是一套能够处理不断变化的现实结构和不断变化的公开证据的研究基础设施。

母框架提出两个彼此独立的问题：

### Structural Dynamics

```text
What appears to be happening in the system?
```

即：

> 系统真实结构正在如何变化？

研究对象包括：

```text
Observation
→ Dimension
→ Structure
→ State
→ Transition
```

### Evidence Dynamics

```text
Are the public claims and observations about the system mutually consistent?
```

即：

> 关于该系统的公开证据是否互相协调？

研究链为：

```text
Public Artifact
→ Claim / Observation
→ Entity Resolution
→ Time / Scope Alignment
→ Cross-Evidence Matrix
→ Competing Hypotheses
→ Consistency Assessment
```

两条线共享证据基础设施，但不共享最终结论。

因此完全可能出现：

```text
Structural State = UNKNOWN

Evidence Consistency = MATERIAL_INCONSISTENCY
```

也可能出现：

```text
Structural Transition = MATERIAL

Evidence Consistency = NO MATERIAL INCONSISTENCY
```

Strategy Pilot 属于后一种。

---

# 2. 为什么必须把结构研究和证据研究分开

一个公开数据对象至少存在五个不同问题：

```text
1. 是否被真实捕获？
2. 谁发布的？
3. 内容是否准确？
4. 是否适合进入科学结构模型？
5. 是否允许公开再分发？
```

这些问题不能用一个“可信/不可信”字段解决。

因此框架冻结：

```text
DATA ACQUISITION
≠ SOURCE TRUST
≠ ARTIFACT INTEGRITY
≠ SCIENTIFIC ELIGIBILITY
≠ PUBLICATION RIGHTS
≠ SCIENTIFIC VALIDITY
```

一个后来被证明错误的公开声明，仍然可能是一个真实存在过的历史事件：

```text
FALSE IN SUBSTANCE
can still be
TRUE AS A PUBLIC-CLAIM EVENT
```

这使 Evidence Dynamics 能够研究：

- 实体的公开叙事如何变化；
- 哪些声明被修订、删除或取代；
- 不同来源之间是否存在不可协调之处；
- 一个冲突是事实冲突、时间差、口径差还是结构变化。

---

# 3. ECL 的数据对象

ECL 永久区分以下对象层级：

```text
RAW ARTIFACT
CLAIM
OBSERVATION
DERIVED FINDING
SCIENTIFIC EVIDENCE
PUBLIC FINDING
```

## 3.1 Raw Artifact

Raw Artifact 只回答：

```text
What was captured?
Where?
When?
What is its hash?
```

它不回答内容真假。

## 3.2 Claim

Claim 是来源对某个对象作出的陈述，必须保留：

- subject；
- predicate；
- object；
- qualifier；
- modality；
- scope；
- effective time；
- source artifact。

因此：

```text
"primary treasury reserve asset"
```

不会被模型擅自转换成：

```text
"never sell"
```

## 3.3 Observation

Observation 是可标准化的观测，例如：

- BTC holdings；
- BTC sold；
- USD Reserve；
- ATM proceeds；
- dividend payments；
- quarterly revenue。

Claim 与 Observation 可以关联，但不是同一对象。

---

# 4. Provenance 与冻结

ECL 继承 RTP 的 provenance 原则。

每个 material artifact 至少保留：

```text
artifact_id
publisher
source_url
published_at
retrieved_at
content_hash
capture_type
verification_method
```

首个 Pilot 还暴露出一个重要问题：文件扩展名并不能证明我们获得了完整原始页面。

因此 S6.1a 冻结：

```text
FULL_RAW
≠ VERIFIED_EXTRACT
≠ HASH_METADATA_ONLY
```

Strategy Investor Relations 的两个短捕获对象由于完整网页未被原始抓取保存，最终被明确分类为：

```text
VERIFIED_EXTRACT
```

而不是 `FULL_RAW`。

这一设计让 provenance 本身也可以被审计。

---

# 5. 来源独立性

ECL 不以 URL 数量代表独立证据数量。

冻结：

```text
MULTIPLE URLs ≠ INDEPENDENT SOURCES
```

需要区分：

```text
HOSTING_INDEPENDENCE
AUTHORSHIP_INDEPENDENCE
OBSERVATION_INDEPENDENCE
```

例如，Nasdaq 页面可能提供独立的 hosting 或 listing context，但如果核心事实仍源自 issuer-filed SEC disclosure，则不能自动升级为“独立验证了公司经营事实”。

首个 Pilot 因此最终保留：

```text
INDEPENDENT_SOURCE_COVERAGE = PARTIAL
```

而没有为了通过 Gate 人为寻找一个形式上的“第三来源”。

---

# 6. 五类一致性分析

ECL v0.1 使用五类核心分析。

## 6.1 Temporal Consistency

判断两个陈述是否处于同一时间条件。

冻结：

```text
CHANGE ≠ CONTRADICTION
```

后来的政策变化不自动否定较早时期的声明。

## 6.2 Numerical Consistency

用可重演公式检查公开数字。

例如 Strategy Pilot：

```text
1,363 BTC × $59,256 ≈ $80.8M
2,225 BTC × $60,773 ≈ $135.2M
846,000 BTC - 2,225 BTC = 843,775 BTC
```

这些关系被标记为：

```text
RECONCILED
```

而当 aggregate cost basis 缺少必要分配信息时，系统返回：

```text
INSUFFICIENT_DATA
```

而不是补造数字。

## 6.3 Semantic Consistency

判断两个声明在语义上是否真正冲突。

Strategy Pilot 的关键例子：

```text
PRIMARY TREASURY RESERVE ASSET
≠
NEVER SELL
```

因此 BTC sale 本身不能直接构成“放弃 Bitcoin treasury policy”的证明。

## 6.4 Cross-Source Consistency

比较不同来源和方法，但必须先消除 source dependency。

## 6.5 Structural Consistency

检查公开叙事是否与更广的结构变化相协调，例如：

```text
Capital
Reserve
Liquidity
Fixed obligations
Operations
Securities structure
```

结构一致性不是诚信判断。

---

# 7. Triangulation

ECL 使用 triangulation 思想，但不把“三个来源”机械地当作证明。

研究维度包括：

```text
Source triangulation
Method triangulation
Analyst triangulation
Perspective / theory triangulation
```

一个来源可以在“证券上市事实”上独立，却在“公司 treasury policy”上依赖公司披露。因此 independence 必须 issue-specific。

首个 Pilot 的重要负面发现是：

> SEC issuer filings 和 Strategy IR 具有很高的正式性和 provenance，但它们在“实体自己描述自己的 treasury policy”这一问题上不能被误写成完全独立的两条现实验证链。

这也是为什么 Public Evidence Report 继续显著披露：

```text
Independent-source triangulation remains partial.
```

---

# 8. ACH：竞争假设，而不是寻找支持材料

ECL 对 material tension 使用 ACH-style competing hypotheses。

Strategy Pilot 冻结六个解释：

| ID | Hypothesis |
|---|---|
| H1 | Coherent Treasury Evolution |
| H2 | Structural Shift to Hybrid Treasury Management |
| H3 | Cash-Obligation Pressure |
| H4 | Financing Flexibility Dominates |
| H5 | Semantic / Narrative Lag |
| H6 | Apparent Conflict Caused by Scope / Timing |

ACH 不通过“支持证据计数”选冠军。

相反，它问：

> 哪个假设面临最严重的反证？

状态只能是：

```text
VIABLE
WEAKENED
MATERIALLY_CONTRADICTED
UNRESOLVED
```

首个 Pilot 最终状态：

```text
H1 = VIABLE
H2 = VIABLE
H3 = WEAKENED
H4 = VIABLE
H5 = VIABLE
H6 = VIABLE
```

没有所谓“最终真相假设”。

---

# 9. Observed Contradiction 与 Potential Falsifier

这是首个 Pilot 中通过真实错误暴露并修正的一项方法规则。

初版 ACH 曾把类似：

> 如果未来出现正式放弃 Bitcoin reserve policy 的证据……

错误地放进 `contradicting_evidence`。

但这不是已经存在的反证，而是未来可能推翻假设的条件。

因此 S6.1a 正式拆分：

```text
observed_contradicting_evidence
```

和：

```text
potential_falsifiers
```

永久冻结：

```text
OBSERVED CONTRADICTION
≠
POTENTIAL FALSIFIER
```

当不存在现实反证时：

```text
observed_contradicting_evidence = []
observed_contradicting_evidence_status = NONE_FOUND
```

不能用一句“尚未发现反证”冒充反证对象。

---

# 10. Counter-Evidence Search

ECL 要求对每一个 materially used hypothesis 主动寻找使它失败的证据。

Strategy Pilot 对 H1–H6 分别建立 falsifying question。

例如 H3：

> USD Reserve buffer 和 financing capacity 是否削弱“现金义务压力是主要解释”的观点？

冻结证据显示：

- USD Reserve 增长；
- ATM funding 能力持续存在；
- 部分 common ATM proceeds 被用于 USD Reserve；
- 因而“stress-only explanation”被削弱。

最终：

```text
H3 = WEAKENED
```

这一过程的目标不是证明另一个假设，而是防止系统只寻找支持当前叙事的材料。

---

# 11. Conflict Taxonomy

ECL 不使用一个 universal truth score。

冲突被分类为：

```text
TEMPORAL_CONFLICT
NUMERICAL_CONFLICT
SEMANTIC_CONFLICT
SCOPE_CONFLICT
SOURCE_CONFLICT
STRUCTURAL_CONFLICT
PROVENANCE_CONFLICT
REVISION_CONFLICT
```

最终研究结论使用：

```text
CONSISTENT
COMPLEMENTARY
TEMPORAL_CHANGE
POTENTIAL_CONFLICT
MATERIAL_INCONSISTENCY
UNRESOLVED
INSUFFICIENT_DATA
```

永久禁止自动把 `MATERIAL_INCONSISTENCY` 翻译为：

```text
fraud
lying
deception
misconduct
```

---

# 12. 首个方法 Pilot：Strategy Inc.

研究 ID：

```text
ECL.COMPANY.STRATEGY_INC.2026.001
```

观察窗口主要覆盖 2025-12-31 至 2026-08-31。

Pilot 研究的不是 MSTR 股票价格，也不是 Bitcoin 是否值得投资，而是：

> Strategy 在 2026 年关于 Bitcoin reserve policy、BTC monetization、USD Reserve、资本募集、preferred obligations 和软件经营的公开披露，是否能够在时间、数值、语义和结构上互相协调？

同时生成独立的 Structural Dynamics 问题：

> Strategy 的资本架构在 2026 年发生了什么结构性变化？

---

# 13. Pilot 结果

Structural Dynamics 得到：

```text
HYBRID_ACCUMULATION_MONETIZATION
```

其含义不是“公司放弃积累”，而是：

> BTC reserve、BTC monetization、USD liquidity buffer、common/preferred capital raising、fixed cash obligations 和 software operations 已经同时进入同一资本结构。

Evidence Dynamics 得到：

```text
SEMANTIC_TENSION_BUT_RECONCILABLE
MATERIAL_INCONSISTENCY = NO
```

关键原因包括：

1. 公司公开同时保留“Bitcoin as primary treasury reserve asset”和 monetization framework；
2. “primary reserve asset”并不语义等价于“never sell”；
3. BTC sales、USD Reserve、ATM funding 和 preferred obligations 可以在现有披露框架中协调；
4. holdings roll-forward 和已披露 sale math 能够对账；
5. 没有发现经过 scope/time normalization 后仍然存活的 same-date same-scope material conflict；
6. independent-source coverage 仍为 `PARTIAL`，因此结论不能扩大为“现实世界已独立证明所有公司披露真实”。

---

# 14. 为什么“没有发现重大矛盾”是一个有价值的结果

一个公共监督系统如果只能输出批判性结论，它很快会退化为冲突生成器。

ECL 的第一轮真实 Pilot 反而证明：

```text
Apparent Conflict
→ Time / Scope Alignment
→ Numerical Reconciliation
→ Semantic Analysis
→ ACH
→ Counter-Evidence Search
→ No Material Inconsistency
```

是允许发生的。

这说明系统目标不是：

> 找到可以攻击的公司。

而是：

> 判断冲突到底是不是真的存在。

这是方法可信度的重要条件。

---

# 15. 与 Structural Dynamics 的关系

ECL 不是 MDL 的替代品。

二者是两个平行层：

```text
                RDL
                 │
                RTP
                 │
        ┌────────┴────────┐
        ▼                 ▼
Structural Dynamics   Evidence Dynamics
        │                 │
       MDL               ECL
```

Structural Dynamics 可以使用高质量授权数据研究真实市场结构。

Evidence Dynamics 则可以在公开证据层研究实体的叙事、数值和历史一致性。

同一 artifact 可以：

```text
Structural Dynamics:
SCIENTIFIC_INPUT_ELIGIBILITY = REJECTED

Evidence Dynamics:
PUBLIC_CLAIM_EVENT = ACCEPTED
```

这是双轨架构的核心价值。

---

# 16. 局限

v0.1 仍有明确局限：

### 16.1 Independent-source coverage partial

Strategy Pilot 的 material facts 主要来自 issuer-authored SEC filings 与 Strategy IR。

这意味着当前结果只能表述为：

> 在被冻结的公开披露记录内部，未发现 material inconsistency。

不能扩大为：

> 所有经营事实已经被外部独立世界验证。

### 16.2 ECL 不是法律判断系统

ECL 输出证据关系和冲突状态，不判断证券违法、欺诈、受托责任或主观意图。

### 16.3 语义分析仍需要人工审核

Claim extraction 可以模型辅助，但 material claim 必须可追溯到 frozen artifact，并保留 human-review gate。

### 16.4 单一 Pilot 不能证明跨领域泛化

Strategy Pilot 证明了工程链和方法链能够工作，但尚未证明在制造企业、公共机构、医院、政府实体或其他市场中具有相同表现。

---

# 17. 下一阶段研究问题

ECL 下一阶段需要测试：

1. 不同实体类型是否需要不同 conflict taxonomy；
2. independent-source graph 如何自动识别 syndicated / quoted / derived evidence；
3. numerical reconciliation 是否可以建立领域模块；
4. source history 是否能够在不构建 universal trust score 的情况下积累长期事实画像；
5. 如何设计 entity right-of-reply；
6. 如何对公共报告实施 append-only correction / supersession；
7. 如何在更多实体上测试 false-positive rate；
8. 如何邀请权威数据提供方接入 licensed evidence stream。

---

# 18. 阶段性结论

本文提出并通过一个真实公司 Pilot 初步验证了以下原则：

```text
PUBLIC CLAIM ≠ REALITY

ARTIFACT INTEGRITY ≠ CONTENT TRUTH

MULTIPLE URLs ≠ INDEPENDENT SOURCES

HOSTING INDEPENDENCE ≠ EVIDENCE INDEPENDENCE

CHANGE ≠ CONTRADICTION

INCONSISTENCY ≠ FALSEHOOD

OBSERVED CONTRADICTION ≠ POTENTIAL FALSIFIER

APPARENT CONFLICT ≠ MATERIAL INCONSISTENCY
```

ECL v0.1 的承诺不是自动找到“真相”。

它承诺：

> 保存观察到的公开证据；区分声明与现实；识别来源依赖；检查时间、数值、语义与结构关系；让多个解释竞争；主动寻找反证；保留无法解决的不确定性；并让所有公共结论可以被审计、纠正和取代。

这构成 Structural Dynamics + Evidence Dynamics 的第一个阶段性方法成果。

---

# 附录 A：首个 Pilot 的核心冻结结果

```text
Research ID:
ECL.COMPANY.STRATEGY_INC.2026.001

Structural Dynamics:
HYBRID_ACCUMULATION_MONETIZATION

Evidence Dynamics:
SEMANTIC_TENSION_BUT_RECONCILABLE

Material Inconsistency:
NO

Independent Source Coverage:
PARTIAL

ACH:
H1 VIABLE
H2 VIABLE
H3 WEAKENED
H4 VIABLE
H5 VIABLE
H6 VIABLE

Publication Readiness:
METHOD_PILOT_READY

Entity Response:
NOT_REQUESTED
```

---

# 附录 B：研究证据基础

首个 Pilot 的主要冻结来源包括：

- SEC 2025 Form 10-K；
- SEC Q1 2026 Form 10-Q；
- SEC Q2 2026 Form 10-Q；
- SEC 2026-07-06 Form 8-K；
- SEC 2026-07-13 Form 8-K；
- SEC 2026-08-03 Form 8-K；
- SEC 2026-08-10 Form 8-K；
- Strategy Digital Credit Capital Framework（VERIFIED_EXTRACT）；
- Strategy Q2 2026 results（VERIFIED_EXTRACT）。

研究中保留原始 source locator、artifact ID、retrieval time、capture type 和 SHA-256 provenance。
