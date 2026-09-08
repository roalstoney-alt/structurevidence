# Strategy Inc. 2026：Public Evidence Research Report
## 公共证据一致性研究报告 v0.1

**Research ID：** `ECL.COMPANY.STRATEGY_INC.2026.001`  
**Entity：** Strategy Inc.（NASDAQ: MSTR）  
**Observation Window：** 主要覆盖 2025-12-31 至 2026-08-31  
**Method：** ECL — Evidence Consistency Layer  
**Final Assessment：** `SEMANTIC_TENSION_BUT_RECONCILABLE`  
**Material Inconsistency：** `NO`  
**Independent-source coverage：** `PARTIAL`  
**Entity response：** `NOT_REQUESTED`  
**声明：** 本报告研究公开证据之间的一致性，不判断欺诈、误导、违法或管理层主观意图，不构成投资建议。

---

# 1. Executive Finding

本 Pilot 从一个表面上非常容易形成质疑的问题开始：

> Strategy 一方面公开保持 Bitcoin 为其 primary treasury reserve asset，另一方面在 2026 年建立 BTC monetization framework 并实际出售 Bitcoin。这两组证据是否互相矛盾？

经过：

```text
Artifact Freeze
→ Claim Extraction
→ Entity / Scope Resolution
→ Time Alignment
→ Numerical Reconciliation
→ Semantic Consistency
→ Source Dependency
→ ACH
→ Counter-Evidence Search
```

当前冻结结论是：

```text
SEMANTIC_TENSION_BUT_RECONCILABLE
MATERIAL_INCONSISTENCY = NO
```

即：

> 公开材料中存在值得研究的语义张力，但在目前 observation window 内，没有发现经过时间、范围、定义和数值校正后仍然存活的重大不一致。

这不是对 Strategy 公开披露“真实性”的全面背书。

更准确的说法是：

> 在当前被冻结的 issuer disclosure record 内，这些公开证据可以被协调。

---

# 2. Research Question

研究问题被冻结为：

> Strategy Inc. 2026 年关于维持 Bitcoin 为主要 treasury reserve asset、保留长期 Bitcoin exposure、资本募集、USD Reserve、preferred obligations 与 BTC monetization 的公开披露，是否与其披露的融资、BTC 买卖、储备和软件经营数据互相一致？

明确不研究：

```text
Is Strategy lying?
Will MSTR rise or fall?
Is Strategy insolvent?
Is Bitcoin a good investment?
```

---

# 3. Evidence Set

主要 frozen source classes：

```text
REGULATORY_FILING
COMPANY_PRESS_RELEASE / IR
PARTIALLY_DEPENDENT_EXTERNAL_CONTEXT
DERIVED_NUMERICAL_RECONCILIATION
```

主要事实来源：

- SEC 2025 Form 10-K；
- SEC Q1 2026 Form 10-Q；
- SEC Q2 2026 Form 10-Q；
- SEC July/August 2026 Forms 8-K；
- Strategy Digital Credit Capital Framework；
- Strategy Q2 2026 results。

需要显著披露：

```text
Independent-source triangulation remains partial.
```

大多数 material facts 来自 issuer-authored regulatory filings 与 issuer IR。

因此本报告不声称这些事实已经被完全独立验证。

---

# 4. Artifact Capture Boundary

S6.1a 对 provenance 做了纠偏。

Strategy IR 的短捕获对象被分类为：

```text
VERIFIED_EXTRACT
```

而不是：

```text
FULL_RAW
```

这意味着：

> 对相关 claim 的 bounded extract 已经针对 source locator 做验证，但没有把一个短文件伪装成完整原始网页。

永久规则：

```text
FULL_RAW ≠ VERIFIED_EXTRACT
```

---

# 5. Evidence Timeline

## 2026-03-31 / Q1 disclosure

冻结记录包括：

```text
USD Reserve = $2.14B
Q1 total revenue = $124.3M
cash dividends paid = $229.527M
```

## 2026-06-29

Strategy IR 的 Digital Credit framework 同时出现：

```text
Bitcoin remains primary treasury reserve asset
```

以及：

```text
BTC monetization program
```

并记录 USD Reserve 的 liquidity-use policy。

这是整个 Pilot 的核心语义 tension。

## 2026-06-29 至 2026-07-05

7 月 6 日 Form 8-K 披露：

```text
1,363 BTC sold June 29–30 for $80.8M
2,225 BTC sold July 1–5 for $135.2M
843,775 BTC held as of July 5
USD Reserve = $2.55B
```

## 2026-07-13

披露：

```text
$466.7M net proceeds July 6–12
```

## 2026-07-30

Q2 issuer results 披露：

```text
843,775 BTC as of July 26
USD Reserve = $3.75B
$17.06B YTD ATM capital raised
$1.06B cumulative preferred dividends
Q2 revenue = $122.4M
```

## 2026-08-03

Q2 Form 10-Q 与 8-K 继续披露：

```text
$8.24B MSTR ATM net proceeds in six months ended June 30
$1.52B common ATM proceeds used for USD Reserve
$546.0M common ATM proceeds used for preferred dividends
1,638 BTC sold July 27–August 2 for $104.73M
```

## 2026-08-10

披露：

```text
1,690 BTC sold August 3–9 for $108.6M
840,447 BTC as of August 9
```

---

# 6. Numerical Reconciliation

ECL 对能够确定性检查的数字进行重演。

### BTC sale A

```text
1,363 × $59,256 ≈ $80.8M
```

结果：

```text
RECONCILED
```

### BTC sale B

```text
2,225 × $60,773 ≈ $135.2M
```

结果：

```text
RECONCILED
```

### Holdings

```text
846,000 - 2,225 = 843,775
```

结果：

```text
RECONCILED
```

### Cost basis

需要 sale allocation 等缺失信息，因此：

```text
INSUFFICIENT_DATA
```

系统不从缺失信息中生成一个“看似完整”的 cost-basis 结论。

---

# 7. Semantic Consistency

核心 claim pair：

```text
CLM-S6-001:
Bitcoin as primary treasury reserve asset

CLM-S6-002:
BTC monetization program
```

表面上它们可能被叙事化为：

```text
hold Bitcoin
vs
sell Bitcoin
```

但这种压缩会改变原始 claim 的语义。

ECL 冻结：

```text
PRIMARY RESERVE ASSET
≠
NEVER SELL
```

因此：

```text
BTC SALE
≠
AUTOMATIC ABANDONMENT OF TREASURY POLICY
```

当前最准确的分类是：

```text
SEMANTIC_TENSION_BUT_RECONCILABLE
```

而不是：

```text
MATERIAL_INCONSISTENCY
```

---

# 8. Structural Consistency

与 companion Structural Dynamics Report 对照，冻结证据显示：

```text
BTC reserve stock remains large
BTC monetization exists
USD Reserve increases
ATM financing remains active
preferred obligations consume cash
software operations continue
```

这组结构更像：

```text
HYBRID_ACCUMULATION_MONETIZATION
```

而不是：

```text
binary accumulation / abandonment
```

因此结构证据没有迫使 ECL 把 treasury-policy language 判为 material contradiction。

---

# 9. Competing Hypotheses

ECL 不选择单一故事，而是保留多个解释。

| ID | Hypothesis | Status |
|---|---|---|
| H1 | Coherent Treasury Evolution | VIABLE |
| H2 | Structural Shift to Hybrid Treasury Management | VIABLE |
| H3 | Cash-Obligation Pressure | WEAKENED |
| H4 | Financing Flexibility Dominates | VIABLE |
| H5 | Semantic / Narrative Lag | VIABLE |
| H6 | Apparent Conflict Caused by Scope / Timing | VIABLE |

---

# 10. H1 — Coherent Treasury Evolution

**Hypothesis：**

> BTC monetization 可以作为 treasury framework 的一个工具，同时维持 Bitcoin 为 primary reserve asset。

当前状态：

```text
VIABLE
```

冻结记录中没有发现 formal abandonment。

但 ECL 不把：

> “没有发现放弃”

写成“反证”。

S6.1a 明确修正：

```text
observed_contradicting_evidence = []
status = NONE_FOUND
```

Potential falsifiers 包括：

- formal abandonment；
- sustained liquidation materially inconsistent with framework；
- same-scope policy language explicitly excluding monetization。

---

# 11. H2 — Hybrid Treasury Management

**Hypothesis：**

> 2026 年 Strategy 已经从 predominantly accumulation-oriented behavior 进入 accumulation + monetization 的混合管理模式。

状态：

```text
VIABLE
```

支持原因：

- monetization 被框架化；
- 出现多个 sale period；
- reserve 与 liquidity management 同时存在。

未来若 sales 被证明只是 isolated/exception-only，则 H2 会被削弱。

这属于：

```text
potential falsifier
```

而不是已经存在的 observed contradiction。

---

# 12. H3 — Cash-Obligation Pressure

**Hypothesis：**

> Preferred dividends、interest 等 cash obligations materially pressure liquidity behavior。

状态：

```text
WEAKENED
```

实际 counter-evidence 包括：

- USD Reserve 增长；
- common ATM funding；
- reserve funding；
- 资本市场融资仍然可见。

因此 ECL 认为：

> cash obligations 是真实结构变量，但当前证据不足以把“压力”作为唯一或主导解释。

---

# 13. H4 — Financing Flexibility Dominates

**Hypothesis：**

> observable behavior 主要反映融资灵活性，而不是结构性压力。

状态：

```text
VIABLE
```

ATM proceeds 与 reserve funding 支持该解释。

但 BTC monetization 和 fixed obligations 的共同存在，使“纯 financing-only explanation”不能吸收全部现象。

因此 H4 保持 viable，而不是 winner。

---

# 14. H5 — Semantic / Narrative Lag

**Hypothesis：**

> Strategy 的 headline identity 仍以 Bitcoin-centric narrative 为中心，而 operating policy 已经扩展得更复杂。

状态：

```text
VIABLE
```

但重要 counter-evidence 是：

> Digital Credit framework 本身已经公开整合 monetization language。

因此 semantic gap 被缩小。

此外，S6.1a 修复了一处 source-independence 标注：

Nasdaq 相关材料在 treasury-policy 语义问题上只能算：

```text
PARTIALLY_DEPENDENT_EXTERNAL_CONTEXT
```

不能算独立验证。

永久冻结：

```text
HOSTING INDEPENDENCE
≠
EVIDENCE INDEPENDENCE
```

---

# 15. H6 — Scope / Timing

**Hypothesis：**

> 很多表面冲突在对齐时间、口径、security class 和 measurement scope 后消失。

状态：

```text
VIABLE
```

当前 Pilot 没有记录 same-date same-scope material contradiction。

Cost basis 问题则是：

```text
INSUFFICIENT_DATA
```

而不是 conflict。

未来如果出现经 normalization 后仍不能协调的同日同口径声明，则 H6 会受到直接反证。

---

# 16. Counter-Evidence Search

S6.1 对 H1–H6 均执行 falsifying search。

关键结果：

```text
H1:
NO_MATERIAL_COUNTER_EVIDENCE_FOUND

H2:
NO_MATERIAL_COUNTER_EVIDENCE_FOUND

H3:
COUNTER_EVIDENCE_FOUND

H4:
NO_MATERIAL_COUNTER_EVIDENCE_FOUND

H5:
COUNTER_EVIDENCE_FOUND

H6:
NO_MATERIAL_COUNTER_EVIDENCE_FOUND
```

这并不意味着 H1/H2/H4/H6 已被“证明”。

它只意味着：

> 在当前 bounded search 和 frozen record 内，没有发现足以 materially weaken 它们的现存反证。

---

# 17. Source Dependency

这是当前研究最重要的限制。

SEC filings 与 Strategy IR 虽然是高价值 primary issuer records，但在很多问题上属于：

```text
same issuer evidence chain
```

Nasdaq 只在 listing/security context 上具有部分独立性。

因此：

```text
INDEPENDENT_SOURCE_COVERAGE = PARTIAL
```

必须保留。

我们不能说：

> 多个外部独立来源已经验证 Strategy 的真实运营状态。

只能说：

> 多个被冻结 issuer disclosures 在当前分析中没有出现 material internal inconsistency。

---

# 18. What Is Consistent

当前可以明确记录：

1. BTC monetization framework 与实际 BTC sales 在时间上相邻；
2. sale math 可重演；
3. holdings roll-forward 可重演；
4. USD Reserve 存在增长；
5. ATM funding、reserve funding 和 preferred dividends 同时出现在 disclosure chain 中；
6. treasury-policy language 并没有在 frozen record 中陈述“Bitcoin 永不出售”。

---

# 19. What Remains Difficult to Interpret

仍存在需要长期研究的张力：

1. Bitcoin-centric identity 与 increasingly complex monetization/capital-management policy 之间的叙事重心；
2. BTC monetization 在未来究竟是 structural tool 还是阶段性工具；
3. cash obligations 在资本行为中的真实边际作用；
4. external independent observation 对 issuer disclosures 的覆盖仍不足；
5. future KPI / treasury language 是否进一步变化。

这些是：

```text
research questions
```

而不是：

```text
misconduct findings
```

---

# 20. What Would Change the Conclusion

以下证据可能使当前结论改变：

### 更支持 material inconsistency

- same-date, same-scope policy statements that cannot coexist；
- disclosed action explicitly prohibited by contemporaneous policy；
- numerical discrepancy surviving unit/time normalization；
- independently generated evidence contradicting material issuer disclosure；
- formal historical correction showing prior material fact was wrong。

### 更支持 coherent evolution

- future filings explicitly integrate accumulation and monetization；
- continued transparent reporting of reserve/sale rules；
- independent evidence corroborating capital/reserve observations；
- stable definitions across periods。

---

# 21. Right of Reply

当前：

```text
ENTITY_RESPONSE_STATUS = NOT_REQUESTED
```

由于最终结论不是 Level 3 Public Challenge，也没有形成 misconduct allegation，本 Pilot 尚未启动 entity response process。

后续如果报告升级到：

```text
MATERIAL_INCONSISTENCY_REQUIRES_CLARIFICATION
```

则应由 human publication gate 决定是否请求回应。

---

# 22. Final Assessment

最终冻结：

```text
ECL_RESULT =
SEMANTIC_TENSION_BUT_RECONCILABLE

MATERIAL_INCONSISTENCY =
NO

INDEPENDENT_SOURCE_COVERAGE =
PARTIAL
```

这意味着：

> Strategy 2026 的公开证据展示出从 accumulation-centric identity 向更复杂资本管理框架扩展所产生的语义张力，但当前被冻结记录没有支持把这一张力升级为重大公共证据矛盾。

---

# 23. Methodological Significance

这一首例的意义不是“Strategy 没问题”。

它证明的是：

> ECL 可以从一个看起来容易形成质疑的案例出发，在经过 provenance、scope/time alignment、numerical reconciliation、ACH 和 counter-evidence search 后，主动拒绝一个过度结论。

因此 ECL 的第一条公开经验可以写成：

```text
APPARENT CONFLICT
≠
MATERIAL INCONSISTENCY
```

---

## Evidence Index

主要冻结 source artifacts：

```text
ART-S6-SEC-2025-10K
ART-S6-SEC-Q1-2026-10Q
ART-S6-SEC-Q2-2026-10Q
ART-S6-SEC-2026-0706-8K
ART-S6-SEC-2026-0713-8K
ART-S6-SEC-2026-0803-8K
ART-S6-SEC-2026-0810-8K
ART-S6-IR-DIGITAL-CREDIT
ART-S6-IR-Q2-2026
```

关键 provenance correction：

```text
Strategy IR captures = VERIFIED_EXTRACT
Nasdaq treasury-policy context = PARTIALLY_DEPENDENT_EXTERNAL_CONTEXT
Observed contradiction ≠ Potential falsifier
```

S6/S6.1/S6.1a 的完整 manifest、SHA-256、hypothesis assessments、counter-evidence logs、source-dependency graph 和 audit records 构成本报告的可审计底层证据。
