# Strategy Inc. 2026：Structural Dynamics Report
## 结构动力学报告 v0.1

**研究 ID：** `ECL.COMPANY.STRATEGY_INC.2026.001`  
**实体：** Strategy Inc.（NASDAQ: MSTR；former name: MicroStrategy Incorporated）  
**观察窗口：** 主要覆盖 2025-12-31 至 2026-08-31  
**报告类型：** Structural Dynamics  
**结构状态：** `HYBRID_ACCUMULATION_MONETIZATION`  
**状态：** 阶段性研究报告  
**声明：** 本报告不是 MSTR、Bitcoin 或任何相关证券的投资建议，不预测价格，不评价管理层主观意图。

---

## 1. Executive Structural View

冻结证据显示，Strategy 在 2026 年已经不能仅用“Bitcoin accumulation”单一描述解释其资本结构。

观察到的系统同时包含：

```text
Bitcoin reserve holdings
+
BTC monetization
+
MSTR common ATM financing
+
preferred financing / obligations
+
USD Reserve
+
repurchase activity
+
software operations
```

因此本 Pilot 使用结构描述：

```text
HYBRID_ACCUMULATION_MONETIZATION
```

它表达的是：

> Bitcoin 仍然是最显著的储备组成，但资本架构已经同时显式使用 Bitcoin monetization、美元流动性缓冲和多层证券融资来管理资本与现金义务。

这一结构状态不等于：

```text
ABANDONMENT_OF_BITCOIN
```

也不等于：

```text
FINANCIAL_STRESS
```

它只是对被冻结结构变量的描述。

---

# 2. Entity and Scope

实体统一解析为：

```text
ENTITY_ID = ECL.COMPANY.STRATEGY_INC
LEGAL_NAME = Strategy Inc.
FORMER_NAME = MicroStrategy Incorporated
COMMON_TICKER = MSTR
```

资本结构必须区分：

```text
MSTR common
STRK
STRF
STRD
STRC
convertible debt
```

不能把 common equity、preferred securities、debt 和 Bitcoin holdings 压缩成一个“资金”变量。

---

# 3. Capital Structure

Pilot 观察到 common ATM financing 是 2026 资本结构的重要流入渠道。

冻结记录包括：

- Q2 2026 issuer results 报告 YTD ATM capital raised 为 **$17.06B**；
- Q2 Form 10-Q 披露截至 2026-06-30 六个月期间 MSTR ATM net proceeds **$8.24B**；
- 2026-07-13 Form 8-K 记录 7 月 6–12 日约 **$466.7M net proceeds**。

这里必须保留时间与口径差异：

```text
YTD aggregate
≠
six-month MSTR ATM proceeds
≠
single-week proceeds
```

因此这些数字不构成冲突，而是不同观察窗口下的 capital-flow observations。

---

# 4. Bitcoin Reserve

Bitcoin 仍然是冻结证据中最大的显性 reserve component。

关键 holdings observations：

| 时间 | BTC holdings |
|---|---:|
| 2026-07-05 | 843,775 BTC |
| 2026-07-26 | 843,775 BTC |
| 2026-08-09 | 840,447 BTC |

Pilot 同时观察到多次 BTC monetization：

| 期间 | BTC sold | Disclosed proceeds |
|---|---:|---:|
| 2026-06-29–06-30 | 1,363 | $80.8M |
| 2026-07-01–07-05 | 2,225 | $135.2M |
| 2026-07-27–08-02 | 1,638 | $104.73M |
| 2026-08-03–08-09 | 1,690 | $108.6M |

因此结构上已经同时存在：

```text
large reserve stock
+
monetization flow
```

这就是 `HYBRID_ACCUMULATION_MONETIZATION` 的主要依据。

---

# 5. Numerical Flow Checks

ECL/Structural companion analysis执行了确定性数值对账。

### Sale reconciliation A

```text
1,363 × $59,256 ≈ $80.8M
```

结果：

```text
RECONCILED
```

### Sale reconciliation B

```text
2,225 × $60,773 ≈ $135.2M
```

结果：

```text
RECONCILED
```

### Holdings roll-forward

```text
846,000 - 2,225 = 843,775
```

结果：

```text
RECONCILED
```

### Aggregate cost basis

由于缺少 sale allocation 所需的完整分配信息：

```text
INSUFFICIENT_DATA
```

系统没有补造 cost-basis 结果。

---

# 6. USD Reserve and Liquidity

冻结观察记录：

| 时间/期间 | USD Reserve / related funding |
|---|---:|
| 2026-03-31 | $2.14B USD Reserve |
| 2026-07-05 | $2.55B USD Reserve |
| 2026-07-26 | $3.75B USD Reserve |
| Six months ended 2026-06-30 | $1.52B common ATM proceeds used for USD Reserve |

结构上，这表明 Strategy 在 Bitcoin reserve 之外建立了独立的 USD liquidity buffer。

Pilot 不把：

```text
USD Reserve
```

等同于：

```text
general cash
```

也不把它等同于：

```text
Bitcoin reserve
```

不同 stock 必须分开记录。

---

# 7. Fixed Cash Obligations

冻结记录中可见 preferred dividend obligations。

包括：

- Q1 Form 10-Q：**$229.527M cash dividends paid**；
- Q2 issuer results：截至 7 月 26 日累计 preferred dividends **$1.06B**；
- Q2 Form 10-Q：**$546.0M common ATM proceeds used to pay preferred dividends**。

这表明：

```text
fixed cash obligations
```

已经成为资本架构中的独立结构变量。

但 Pilot 不从这些数字自动推出：

```text
liquidity crisis
forced sale
financial distress
```

这些属于需要额外证据支持的解释。

---

# 8. Software Operations

软件业务没有被 Bitcoin 资产规模“抹掉”。

冻结记录包括：

```text
Q1 2026 total revenue = $124.3M
Q2 2026 total revenue = $122.4M
```

本报告仅记录：

> 软件经营仍是持续存在的 operating component。

不从 Bitcoin reserve 的规模推导软件业务“无关紧要”，也不在本 Pilot 中建立软件业务估值结论。

---

# 9. Structural Domains

本 Pilot 使用以下公司结构域：

```text
CAPITAL
BITCOIN_RESERVE
LIQUIDITY
FIXED_OBLIGATIONS
SOFTWARE_OPERATIONS
SECURITIES_STRUCTURE
```

它们不是 MDL Flow-8。

Flow-8 仍然属于市场结构域注册体系。

---

# 10. Structural Transition

冻结材料支持一个阶段性结构变化：

```text
ACCUMULATION-DOMINANT PUBLIC IDENTITY
              ↓
HYBRID CAPITAL ARCHITECTURE
```

其具体表现为：

```text
Bitcoin holdings remain large
+
BTC sales become an explicit disclosed tool
+
USD Reserve grows
+
ATM financing remains active
+
preferred obligations consume cash
+
repurchase / capital rebalancing appears
```

因此本报告描述：

> 2026 年的 Strategy 不是简单从“持有 Bitcoin”变成“不持有 Bitcoin”，而是从以 accumulation 为中心的公开身份，进入一个同时包含 accumulation、monetization、liquidity buffer 和 multi-security financing 的混合资本结构。

---

# 11. What This Report Does Not Establish

本 Structural Dynamics Report 不证明：

- BTC monetization 是被迫的；
- Strategy 出现流动性危机；
- management narrative 不真实；
- Bitcoin policy 已被放弃；
- MSTR 应买入或卖出；
- 当前结构未来一定持续。

这些需要不同证据和不同研究问题。

---

# 12. Uncertainty

主要不确定性包括：

1. 后续 BTC monetization 是否持续；
2. monetization 在总持仓中的长期结构占比；
3. USD Reserve 未来如何被使用；
4. preferred obligations 的未来路径；
5. capital-market access 的持续性；
6. software operations 的长期现金贡献；
7. company-defined Bitcoin KPI 是否继续演化。

因此本状态是一个：

```text
observed structural descriptor
```

而不是长期预测。

---

# 13. Relationship to ECL

Structural Dynamics 只回答：

> 结构发生了什么？

对应的 Public Evidence Research 报告回答：

> 关于这一结构的公开声明与公开观测是否互相协调？

两份报告必须并列阅读。

本报告：

```text
STRUCTURAL RESULT =
HYBRID_ACCUMULATION_MONETIZATION
```

对应 ECL：

```text
EVIDENCE RESULT =
SEMANTIC_TENSION_BUT_RECONCILABLE

MATERIAL_INCONSISTENCY = NO
```

这意味着：

> 结构发生明显变化，并不自动意味着公共披露存在重大矛盾。

---

# 14. Evidence Boundary

本 Pilot 的主要事实来自：

- SEC issuer filings；
- Strategy Investor Relations disclosures。

Independent-source coverage 仍为：

```text
PARTIAL
```

因此本报告描述的是**被冻结公开披露所呈现的结构**。

它不是对所有底层现实活动的独立外部审计。

---

# 15. Conclusion

Strategy 2026 Pilot 的阶段性结构结论是：

```text
HYBRID_ACCUMULATION_MONETIZATION
```

其核心不是“卖出 Bitcoin”，而是系统同时出现：

```text
large BTC reserve
BTC monetization
USD liquidity reserve
common equity financing
preferred obligations
capital rebalancing
software operations
```

这些变量共同构成一个比“Bitcoin accumulator”更复杂的资本结构。

未来研究应继续观察这些 stock、flow、obligation 与 funding channel 是否形成稳定的新结构，或只是 2026 年的阶段性状态。

---

## Evidence Index

主要冻结 artifact：

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

完整 provenance、hash、capture type、claim registry 与 reconciliation 记录保存在 S6/S6.1/S6.1a evidence-freeze。
