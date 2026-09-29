# 从检索到可辩护决策：一种面向时间边界证据状态的协议

**方法论文 / 工作论文 — v0.1**
**实现冻结点：** `94ee5dc8670b8132979846c815b400f8cef17ab1`
**作者：** Stone Zhu / 朱柏樂
**项目：** StructureEvidence
**日期：** 2026-09-29

## 学术记录

**论文题目：**《从信息检索到可辩护决策：一种面向时间边界证据状态的协议》

**版本：** v0.1

**发布日期：** 2026-09-29

**版本 DOI：** https://doi.org/10.5281/zenodo.23033588

**概念 DOI / 全版本 DOI：** https://doi.org/10.5281/zenodo.23033587

**Zenodo Record：** https://zenodo.org/records/23033588

**项目主页：** https://structurevidence.org

**方法协议：** https://structurevidence.org/method-contract.json

**公开解析接口：** https://api.structurevidence.org/resolve

**GitHub：** https://github.com/roalstoney-alt/structurevidence

**实现基线：** `94ee5dc8670b8132979846c815b400f8cef17ab1`

## 摘要

检索系统可以找到信息，但“找到信息”并不等于已经建立了一个可用于决策的事实。被检索到的主张可能已经过时，可能只有单一来源，可能只支持一个实例，可能不适用于当前使用场景，也可能仍存在关键未知项。本文提出 StructureEvidence：一种面向 Agent、顾问和人类决策者的时间化证据协议，用于把现实问题转换成可版本化、可复用、边界明确的证据状态。该协议区分事件时间与知识时间，区分主张、证据、决策和未知项，并要求每个公开 claim 同时暴露状态、`as_of`、支持项、`does_not_support`、来源、未知项和下一最小可观测证据。问题首先通过原子性、可证伪性、范围和时间边界检查，再被匹配为 EXACT、ISOMORPHIC、PARTIAL 或 NONE。公开证据不足时，系统仅识别最小缺失证据、候选研究深度和受控验证报价，并要求人工授权。付费购买的是受控研究过程，而不是预设结论；新获得的证据也不会自动公开，而必须经过公开资格判断与人工发布门槛。当前生产实现覆盖三个异质 pilot，共 26 个可机器解析 claim，并提供公开方法契约、claim registry、确定性 resolver 和变更 feed。本文只主张方法与系统结构的可实现性，不主张已经证明其在准确率、成本或普适性上优于其他方案。配套开放 replication/challenge kit 用于外部验证。

---

## 1. 问题：检索并不等于证据成立

Agent 时代最容易被忽略的问题，并不是“模型找不到资料”，而是模型常常把不同证据层级压缩成一句流畅结论。

例如：公开资料显示一个 800VDC / SST 数据中心供电架构已经在一个具名场地投入商业运行。这个事实可以支持“存在一个具名部署实例”，但它不能自动支持：

- 已完成独立验证；
- 已形成多主体复制；
- 已有长期运行历史；
- 已形成重复采购；
- 经济性已经优于传统架构；
- 已经成为行业采用路线。

同样，储能领域中的“产品发布”“合作协议”“计划产能”“客户交付”“并网投运”“长期运行”不是同一个状态；临床研究中的群体统计结果也不能自动变成个人生存概率或跨疗法排序。

因此，StructureEvidence 的目标不是让 Agent 更“自信”，而是让它更**有边界**：知道当前证据支持到哪里，哪里仍然未知，什么时候证据已经过期或不适用，以及还缺少哪一条最小证据才能继续推进。

---

## 2. 方法定位

StructureEvidence 不是搜索引擎，也不是通用问答系统，而是一层：

> **Temporal Evidence Resolution Layer — 时间化证据解析层**

它接收一个已经存在的问题，并尝试把问题解析到一个受治理的公开 claim state。

核心链路是：

```text
QUESTION
→ INTAKE
→ CLAIM MATCH
→ PUBLIC STOP-POINT
→ FRESHNESS / SUFFICIENCY
→ MINIMUM MISSING EVIDENCE
→ RDL
→ VERIFICATION QUOTE
→ HUMAN AUTHORIZATION
→ PAID CYCLE
→ PUBLICATION ELIGIBILITY
→ APPEND-ONLY PUBLIC VERSION / PRIVATE MEMORY
```

这条链路的关键不是“尽量回答”，而是“知道什么时候应该停止回答”。

---

## 3. 方法约束

当前方法契约冻结如下规则：

- `FACT != CLAIM != EVIDENCE != DECISION`
- `EVENT_TIME != KNOWLEDGE_TIME`
- `NOT_FOUND_WITHIN_SCOPE != DOES_NOT_EXIST`
- `SINGLE_INSTANCE != INDUSTRY_ADOPTION`
- `ORDER != DELIVERY`
- `DELIVERY != COMMISSIONING`
- `COMMISSIONING != OPERATING_HISTORY`
- `SOURCE_STATEMENT != INDEPENDENT_VALIDATION`
- `UNKNOWN MUST NOT BE INFERRED`

这些不是宣称不可质疑的“公理”，而是防止 Agent 在证据链中越权推断的**操作约束**。

商业边界同样冻结为：

> **Process bought; outcome not bought.**
>
> 购买的是受控研究过程，不是预设结果。

---

## 4. Claim 是最小机器对象

Case 是容器，Claim 才是机器解析和引用的最小单位。

每个公开 claim 至少包含：

```json
{
  "claim_id": "...",
  "case_id": "...",
  "statement": "...",
  "state": "...",
  "as_of": "...",
  "supports": [],
  "does_not_support": [],
  "unknowns": [],
  "provenance": [],
  "next_observable": "...",
  "canonical_url": "..."
}
```

其中 `does_not_support` 与 `state` 同样重要。如果下游 Agent 只引用“支持项”而丢掉关键的“不支持项”，就可能把一个单实例证据误写成产业采用。

---

## 5. Public Stop-Point

当问题命中 claim 后，系统返回公开 stop-point：

- STATE
- SUPPORTS
- DOES_NOT_SUPPORT
- AS_OF
- FRESHNESS
- VERIFICATION_DEPTH
- APPLICABILITY
- UNKNOWNS
- NEXT_OBSERVABLE

Stop-point 的含义是：

> 在没有新的合格证据或授权研究之前，当前证据支持的结论应该停在这里。

---

## 6. Question Intake Gate

并非所有自然语言问题都适合直接进入 claim matching。

问题必须尽量满足：

1. Atomic — 原子化；
2. Falsifiable — 可证伪；
3. Scoped — 有明确范围；
4. Time-bounded — 有时间边界。

例如：

> “800VDC 是不是已经商业化、成本最低、最可靠而且未来最好？”

这是一个多命题问题。系统不应该偷偷选择其中一个问题，而应该输出 decomposition draft，然后停下来让人选择。

---

## 7. 四种 Claim Match

### EXACT

问题与已有 claim 在主体、谓词、证据门槛、范围和时间语义上相同。

### ISOMORPHIC

自然语言不同，但需要的证据结构完全等价。必须额外检查：

- same subject；
- same predicate；
- same evidence threshold；
- same scope；
- same temporal meaning；
- same decision implication。

只要关键字段不等价，就降级为 PARTIAL。

### PARTIAL

已有公开 claim 只能回答问题的一部分。系统必须返回已解决部分与未解决部分，而不是把部分证据包装成完整答案。

### NONE

没有受治理的公开 claim 可以回答问题。系统不生成新的“事实答案”，也不自动启动研究。

---

## 8. Freshness、Verification Depth 与 Applicability

### Freshness

旧证据不等于 stale。稳定事实可能多年有效，而快速变化的技术状态可能几周就需要重审。

当前状态：

- CURRENT
- REVIEW_DUE
- STALE
- UNKNOWN

### Verification Depth

记录证据推进到哪一层，例如：

- source statement；
- multi-source corroborated；
- named operator source；
- independent validation；
- field deployed single instance；
- field deployed multi-entity；
- operating history；
- repeat procurement。

### Applicability

一个公开事实成立，不代表它已经适用于某家公司、某地理区域、某临床人群或某技术架构。因此适用性必须与事实状态分开。

---

## 9. Sufficiency 与 Minimum Missing Evidence

系统不问“还能继续研究什么”，而问：

> **最少再知道什么，才能改变当前决策状态？**

如果当前证据足够且 freshness 可接受：

> **CITE AND STOP**

如果不足，则只输出最小缺失证据，并映射到候选 RDL：

- L0_REUSE：已有证据足够；
- L1_VERIFY：验证一个狭窄事实；
- L2_INVESTIGATE：多个关联未知项；
- L3_DEEP：客户特定的资格、集成、经济性或 RFQ。

Resolver 只能建议 candidate level，不能自动授权。

---

## 10. Verification Quote

当最小缺失证据已经足够清楚，可以形成一个受控报价对象：

- scope；
- minimum missing evidence；
- research level candidate；
- source scope；
- search envelope；
- knowledge cutoff；
- stop condition；
- deliverables；
- delivery window；
- cost cap；
- publication rights status。

报价的本质不是“买结论”，而是：

> 在给定范围、截止点与停止条件下，购买一次受控验证过程。

---

## 11. Paid Cycle 与 Publication Eligibility

付费研究可以得到支持、否定、仍未建立、公开资料不足、访问受限等不同结果。任何结果都可能是合格交付。

但新的付费证据不自动进入 public case。

必须先分类：

- PUBLIC_ELIGIBLE
- CUSTOMER_PRIVATE
- MIXED_REDACTABLE
- CONFIDENTIAL
- SOURCE_CONTROLLED
- 其他受限状态

只有 `PUBLIC_ELIGIBLE + HUMAN PUBLICATION APPROVAL` 才允许生成新的 public stop-point version。

旧版本不覆盖，只能 append-only supersede。

---

## 12. 三层生产架构

当前生产架构：

### Public Research / Trust Plane

`structurevidence.org`

存放：method contract、claim registry、public cases、versioned claim object、changes feed。

### Runtime Resolution Plane

`api.structurevidence.org`

负责：确定性 question → claim resolution。当前 resolver 不需要外部搜索、数据库、LLM 或管理接口来完成公开解析。

### Commercial Action Plane

`structevidence.com`

提供：VERIFY_CLAIM、CUSTOMER_CONTEXT、DECISION_PACK，并要求人类授权。

---

## 13. 当前实现状态

冻结点 `94ee5dc8670b8132979846c815b400f8cef17ab1` 下，共有 26 个公开机器 claim：

| Pilot | Claims |
|---|---:|
| 800VDC / SST 数据中心供电架构 | 9 |
| 钠离子固定式 BESS 商业化 | 9 |
| 中国非鳞 NSCLC 公开研究 | 8 |
| **合计** | **26** |

这三个 pilot 并不是统计学意义上的代表样本，而是三个边界差异很大的结构验证案例。

---

## 14. 三个 Pilot 的方法价值

### 800VDC / SST

用来测试：

> “单实例现场部署”是否会被错误升级成“产业采用”。

当前公开状态明确分开了架构可能性、单实例部署、长期运行、多主体复制、独立验证、重复采购和行业采用。

### 钠离子 BESS

用来测试：

> “发布、协议、产能、交付、投运和长期运行”是否会被压成同一个商业化状态。

### NSCLC

用来测试：

> 一个通用证据协议能否在医疗公开研究中保留临床上下文和个人推断边界。

该 pilot 不构成个人医疗决策服务。

---

## 15. 本文真正主张什么

本文只提出三个受限主张：

1. 可以把现实世界主张表达为同时包含状态、时间、支持项、不支持项、未知项和来源的机器对象。
2. 可以把一个问题受控地经过 intake、match、stop-point、sufficiency、minimum missing evidence 和 human authorization，而不自动修改公开事实。
3. 同一结构可以在至少三个异质 pilot 中实例化，同时保留不同领域的边界。

本文**不主张**已经证明 StructureEvidence 比其他检索系统更准确、更便宜、更快或更普适。

---

## 16. 外部 Replication 指标

公开测试应优先测：

- DISCOVERY_RATE：不给 URL 时能否找到；
- QUESTION_TO_CLAIM_MATCH_RATE：能否命中正确 claim；
- STATE_PRESERVATION_RATE：是否保留原状态；
- AS_OF_PRESERVATION_RATE：是否保留时间边界；
- DOES_NOT_SUPPORT_PRESERVATION_RATE：是否保留关键不支持项；
- ISOMORPHIC_FALSE_POSITIVE_RATE；
- PARTIAL_BOUNDARY_PRESERVATION_RATE；
- PRIVATE_EVIDENCE_LEAK_RATE；
- AUTO_ACTION_VIOLATION_RATE。

目标不是“被引用最多”，而是“被正确引用”。

---

## 17. 可证伪条件

以下情况应被视为协议失败：

- 不同证据门槛的问题被标为 EXACT；
- ISOMORPHIC 在范围或时间语义不同的情况下通过；
- PARTIAL 被输出成完整答案；
- NOT_ESTABLISHED 被改写为已建立；
- 单实例被改写为行业采用；
- 未搜到被改写成不存在；
- stale 证据被无条件当成当前证据；
- public claim 被直接当成 customer-specific applicability；
- 群体医疗研究被转成个人概率；
- 未授权即启动研究或付款；
- 客户私有结果自动公开；
- 历史 public version 被覆盖。

---

## 18. 局限

当前只有 26 个 claims；resolver 的语义匹配仍然刻意保持简单；freshness 还需要更多经验数据校准；没有独立第三方 replication；quote/commerce 层尚未证明市场支付意愿；publication eligibility 在真实客户项目中可能涉及合同或法律判断；医疗 pilot 不能推导为临床有效性验证。

因此最合理的下一步不是继续堆功能，而是让外部 Agent、研究者、工程师和潜在用户来攻击这套方法。

---

## 19. 结论

StructureEvidence 试图解决的不是“信息太少”，而是：

> **检索之后，证据边界在进入判断和行动之前被丢失。**

因此它把公开证据表达为时间化、可版本化的 claim state；要求问题先变得可解析；区分 EXACT、ISOMORPHIC、PARTIAL 与 NONE；把 `does_not_support` 与 `state` 同时暴露；在证据足够时停止，在证据不足时只识别最小缺口，并保留人类对研究、付款和公开发布的最终授权。

它不试图替代搜索引擎、LLM、顾问或专家，而是希望成为这些系统在问题出现时可以解析的一层底层事实边界。

> **不要在问题出现前争夺注意力；在问题出现时成为可解析的证据边界。**

> **已有证据复用，缺失证据定界，研究必须授权，结果从不预售。**

---

## 参考文献

1. Lewis, P. et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS 2020.
2. W3C (2013). PROV-O: The PROV Ontology.
3. Özsoyoğlu, G. & Snodgrass, R. T. (1995). Temporal and Real-Time Databases: A Survey. IEEE TKDE.
4. Jensen, C. S. & Snodgrass, R. T. (2018). Temporal Data Models. Encyclopedia of Database Systems.
5. Wilkinson, M. D. et al. (2016). The FAIR Guiding Principles for scientific data management and stewardship. Scientific Data 3, 160018.
6. Autio, C. et al. (2024). Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile. NIST AI 600-1.

## 可复现入口

- https://structurevidence.org
- https://structurevidence.org/method-contract.json
- https://structurevidence.org/claims/index.json
- https://api.structurevidence.org/resolve
- https://structevidence.com/capabilities.json
- 实现冻结点：`94ee5dc8670b8132979846c815b400f8cef17ab1`
