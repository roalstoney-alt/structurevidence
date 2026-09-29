# From Retrieval to Defensible Decisions: A Protocol for Time-Bounded Evidence States

**Methods preprint / working paper — v0.1**
**Implementation baseline:** `94ee5dc8670b8132979846c815b400f8cef17ab1`
**Author:** Stone Zhu / 朱柏樂
**Project:** StructureEvidence
**Date:** 2026-09-29

## Scholarly Record

**Title:** From Retrieval to Defensible Decisions: A Protocol for Time-Bounded Evidence States

**Version:** v0.1

**Published:** 2026-09-29

**Version DOI:** https://doi.org/10.5281/zenodo.23033588

**Concept DOI (all versions):** https://doi.org/10.5281/zenodo.23033587

**Zenodo record:** https://zenodo.org/records/23033588

**Project:** https://structurevidence.org

**Method contract:** https://structurevidence.org/method-contract.json

**Live resolver:** https://api.structurevidence.org/resolve

**Repository:** https://github.com/roalstoney-alt/structurevidence

**Implementation baseline:** `94ee5dc8670b8132979846c815b400f8cef17ab1`

### Preferred Citation

Stone Zhu. (2026).
*From Retrieval to Defensible Decisions: A Protocol for Time-Bounded Evidence States.*
Version 0.1. Zenodo.
https://doi.org/10.5281/zenodo.23033588

## Abstract

Retrieval systems can find information, but retrieval alone does not establish whether a claim is supported, current, independently validated, applicable to a specific use, or sufficient for a decision. This paper presents StructureEvidence, a temporal evidence protocol for converting real-world questions into versioned, bounded evidence states that can be inspected and reused by agents, consultants, and humans. The protocol separates event time from knowledge time; distinguishes claims, evidence, decisions, and unresolved unknowns; and represents each public claim with an explicit state, `as_of` boundary, supporting evidence, `does_not_support` constraints, provenance, and next observable. Incoming questions pass an intake gate and are matched as EXACT, ISOMORPHIC, PARTIAL, or NONE. Where public evidence is insufficient, the protocol identifies minimum missing evidence, proposes a candidate research depth, and can generate a bounded verification quote while requiring explicit human authorization. Paid research purchases a controlled process rather than a predetermined outcome, and new evidence is classified for publication eligibility before any append-only public state transition. We report a production implementation spanning three heterogeneous pilot domains, 26 machine-resolvable claims, a deterministic public resolver, a method contract, and a public change feed. The present work is a methods and systems contribution, not a comparative performance claim. An open replication and challenge kit is released to test discovery, claim matching, boundary preservation, freshness, partial-match behavior, and public/private evidence controls.

---

## 1. Introduction

Large language models and retrieval-augmented systems have materially improved access to external knowledge, but the act of retrieving a source is not identical to establishing a decision-relevant fact. Retrieval-augmented generation was introduced in part to improve access to non-parametric memory and factual grounding, while provenance and updating world knowledge remained explicit open problems in the original RAG framing [1]. In high-accountability settings, the gap between finding an attributable statement and establishing what may legitimately be inferred from it becomes operationally important.

Consider a simple industrial question: *Has an 800 VDC / solid-state-transformer data-center power architecture been commercially deployed?* A source may establish one named deployment. The same source does not automatically establish independent validation, multi-operator replication, long operating history, repeat procurement, economic superiority, or industry-wide adoption. A conventional answer system may compress these distinctions into a fluent summary. A decision process instead needs a bounded object that preserves them.

A similar problem appears in technology commercialization. A product announcement is not a customer delivery; a cooperation agreement is not commissioning; commissioning is not long operating history. In public medical research, trial-population results are not a patient-specific prognosis, and evidence about different treatment contexts cannot be collapsed into a cross-modality ranking without additional assumptions.

StructureEvidence is designed around the proposition that these inferential boundaries should be represented explicitly and should survive retrieval, citation, reuse, and later updates. The system therefore treats evidence as versioned state rather than as an undifferentiated document collection.

The methodological objective is not to make an agent "more confident." It is to make the agent **more bounded**: able to state what is supported, what is not established, how current the state is, how far verification has progressed, and what minimum evidence would be required to move the state.

This paper describes the protocol, its current production implementation, the principles by which public and paid evidence are separated, and a replication framework for external challenge.

---

## 2. Related foundations

### 2.1 Retrieval and provenance

Retrieval-augmented generation combines parametric generation with access to explicit non-parametric memory [1]. This improves access to external information but does not by itself define a governed claim state, an inferential boundary, or a temporal state-transition protocol. StructureEvidence is therefore complementary to retrieval: retrieval supplies candidate evidence; the protocol determines what claim state that evidence can support.

### 2.2 Provenance

The W3C PROV family provides a general model for representing and interchanging provenance across systems [2]. StructureEvidence adopts the same broad premise that derivation and source relationships should be explicit, but its public claim objects are narrower and decision-oriented: they combine provenance with state, non-support boundaries, time, unresolved unknowns, and update conditions.

### 2.3 Temporal data

Temporal database research distinguishes real-world validity from database recording time and has long emphasized that changing facts require explicit temporal semantics [3][4]. StructureEvidence uses a practical evidence-oriented distinction between **event time** and **knowledge time**: when an event occurred versus when it became attributable within the evidence system. These timestamps may coincide but must not be assumed to do so.

### 2.4 Reusability

The FAIR principles emphasize findability, accessibility, interoperability, and reusability of digital research objects, including workflows and metadata [5]. StructureEvidence adopts machine-readable discovery, stable claim identifiers, explicit provenance, and reusable public artifacts for similar reasons. It does not claim FAIR certification or conformance; rather, FAIR is a relevant design precedent.

### 2.5 Trustworthy generative AI

Risk-management guidance for generative AI emphasizes the need to manage reliability and trustworthiness rather than treating fluent model output as self-validating [6]. StructureEvidence addresses a narrow part of this problem: constraining evidence-based factual inference and preserving human authorization for research, payment, and publication.

---

## 3. Problem formulation

Let an incoming real-world question be `Q`. Let the public claim registry contain governed claims `C = {c1...cn}`. Let each claim be associated with a public evidence state at knowledge cutoff `t_k`.

A conventional retrieval pipeline asks approximately:

> Which documents are relevant to Q?

StructureEvidence asks a different sequence:

1. Is `Q` atomic, falsifiable, scoped, and time-bounded enough to resolve?
2. Does `Q` map to an existing governed claim exactly, isomorphically, partially, or not at all?
3. What does the current public claim state support?
4. What does it explicitly **not** support?
5. Is the state fresh and applicable enough for this use?
6. Is the evidence sufficient to answer the bounded question?
7. If not, what is the **minimum missing evidence**?
8. What research depth could resolve that gap?
9. Has a human authorized that research?
10. If new evidence is obtained, may it become public?

The distinction matters because failure at any one step should be observable rather than hidden inside generated prose.

---

## 4. Core principles

The current method contract freezes the following rules:

- `FACT != CLAIM != EVIDENCE != DECISION`
- `EVENT_TIME != KNOWLEDGE_TIME`
- `NOT_FOUND_WITHIN_SCOPE != DOES_NOT_EXIST`
- `SINGLE_INSTANCE != INDUSTRY_ADOPTION`
- `ORDER != DELIVERY`
- `DELIVERY != COMMISSIONING`
- `COMMISSIONING != OPERATING_HISTORY`
- `SOURCE_STATEMENT != INDEPENDENT_VALIDATION`
- `UNKNOWN MUST NOT BE INFERRED`

These are not asserted as universal epistemological axioms. They are **operational constraints** intended to prevent common evidence-to-conclusion shortcuts in agentic workflows.

The commercial counterpart is equally constrained:

> **Process bought; outcome not bought.**

A customer may authorize a defined verification process. The system must not sell or imply a predetermined research outcome.

---

## 5. The public claim object

A StructureEvidence claim is the minimum machine-resolvable public object. A case is a container; a claim is the retrieval unit.

The required claim fields are:

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

The field `does_not_support` is first-class. It is not merely a disclaimer. A citation that preserves the positive state but discards a material non-support boundary can change the meaning of the object.

### 5.1 Public stop-point

For matched questions the runtime resolver exposes a public stop-point containing:

- state;
- supports;
- does_not_support;
- `as_of`;
- freshness;
- verification depth;
- applicability;
- unknowns;
- next observable;
- canonical URL.

The term **stop-point** is deliberate: the object defines where an evidence-backed answer should stop unless additional evidence is authorized.

---

## 6. Question intake

Before claim matching, an incoming question passes an intake gate with four criteria:

1. **Atomic** — it should not silently combine multiple independently resolvable predicates.
2. **Falsifiable** — evidence could in principle support or fail to support the proposition.
3. **Scoped** — the subject and relevant context are sufficiently specified.
4. **Time-bounded** — the question has an explicit or interpretable evidence time boundary.

If intake fails, the system returns a decomposition draft and stops. It does not silently choose which sub-question the user "really" meant.

Example:

> Is 800VDC commercially proven, cheaper, more reliable, and the best future architecture?

Possible decomposition:

- Has a named 800VDC/SST system reached field deployment?
- Is there multi-entity replication?
- Is comparative CAPEX evidence established?
- Is comparative efficiency evidence established?
- Is comparative reliability evidence established?

The human selects or reframes the actual decision question.

---

## 7. Claim matching

The protocol defines four match classes.

### 7.1 EXACT

The question and governed claim share the same subject, predicate, evidence threshold, material scope, and time semantics. No new factual assumption is required.

### 7.2 ISOMORPHIC

The natural-language question differs, but the evidence required to resolve it is structurally equivalent to an existing claim. An isomorphic match must pass explicit checks for:

- same subject;
- same predicate;
- same evidence threshold;
- same scope;
- same temporal meaning;
- same decision implication.

If the equivalence check fails, the match is downgraded to PARTIAL.

### 7.3 PARTIAL

Existing public claims resolve only part of the question. The system returns the available public boundary and identifies the unresolved portion.

### 7.4 NONE

No governed public claim resolves the question. The resolver does not fabricate a new evidence answer or automatically start research.

---

## 8. Freshness, verification depth, and applicability

### 8.1 Freshness

Freshness is not equivalent to age. An old stable fact may remain current, whereas a recent high-velocity claim may already require review. The current controlled vocabulary is:

- `CURRENT`
- `REVIEW_DUE`
- `STALE`
- `UNKNOWN`

Freshness may depend on knowledge cutoff, last review, change sensitivity, reopen triggers, and watch status.

### 8.2 Verification depth

Verification depth records how far the evidence has progressed. Example controlled values include:

- source statement;
- multi-source corroborated;
- named operator source;
- independent validation;
- field-deployed single instance;
- field-deployed multi-entity;
- operating history;
- repeat procurement.

Lower depth must not be silently promoted to higher depth.

### 8.3 Applicability

A true public claim may still be insufficient for a specific user's context. The protocol therefore separates public support from use-case applicability, using states such as:

- general public scope;
- architecture-level only;
- geography-specific;
- population-specific;
- customer-specific not evaluated;
- unknown.

---

## 9. Sufficiency and minimum missing evidence

The protocol evaluates whether the current public stop-point answers the incoming bounded question. The allowed sufficiency states are:

- `SUFFICIENT`
- `PARTIALLY_SUFFICIENT`
- `INSUFFICIENT`
- `UNKNOWN`

If the evidence is sufficient and acceptably fresh, the correct action is:

> **CITE AND STOP**

There is no requirement to upsell further work.

If evidence is insufficient, the protocol identifies **minimum missing evidence** rather than generating an unconstrained research agenda. A missing-evidence object records why the evidence is needed, the current state, the required transition, the minimum resolving evidence, and a stop condition.

This design links directly to the Research Depth Ladder (RDL):

- `L0_REUSE`: existing evidence is sufficient;
- `L1_VERIFY`: one narrow fact, date, specification, or source;
- `L2_INVESTIGATE`: multiple linked uncertainties;
- `L3_DEEP`: customer-specific qualification, integration, economics, RFQ, or other deep work.

The resolver may propose a **candidate** research level. It does not authorize it.

---

## 10. Verification quote and human authorization

A verification quote is a bounded commercial object. It can include:

- scope;
- minimum missing evidence;
- research-level candidate;
- source scope;
- search envelope;
- knowledge cutoff;
- stop conditions;
- deliverables;
- delivery window;
- price status;
- research cap;
- publication rights status.

The quote must state that human authorization is required and that the outcome is not guaranteed.

A generated quote is not research authorization. Paid work starts only after the required human/commercial authorization state is satisfied.

---

## 11. Paid cycle and publication eligibility

A paid research cycle records the before state, search scope, queries, sources checked, qualifying and rejected evidence, counter-evidence, limits, stop reason, decision after, and cost telemetry where available.

A valid research result may be:

- supported;
- not established;
- contradicted;
- public data insufficient;
- access restricted;
- another controlled outcome.

All are legitimate outcomes.

Crucially, paid evidence does not automatically become public. It first passes a publication-eligibility gate:

- `PUBLIC_ELIGIBLE`
- `CUSTOMER_PRIVATE`
- `MIXED_REDACTABLE`
- `CONFIDENTIAL`
- `SOURCE_CONTROLLED`
- other restricted states.

Only public-eligible evidence plus explicit human publication approval can create a new public stop-point version. Prior public versions remain immutable.

---

## 12. System architecture

The current production system is deliberately split into three planes:

1. **Public research / trust plane** — `structurevidence.org`
   Static method contract, discovery manifest, versioned claim objects, public cases, and change feed.

2. **Runtime resolution plane** — `api.structurevidence.org`
   Public, read-only deterministic resolver. No database, external search, LLM, admin route, or autonomous research action is required for resolution.

3. **Commercial action plane** — `structevidence.com`
   Human-authorized Verify, Customer Context, and Decision Pack capabilities.

The intended flow is:

```text
QUESTION
  ↓
INTAKE
  ↓
MATCH
  ↓
PUBLIC STOP-POINT
  ↓
SUFFICIENT? ── yes → CITE AND STOP
  │
  no
  ↓
MINIMUM MISSING EVIDENCE
  ↓
HUMAN-AUTHORIZED VERIFY
  ↓
RESULT
  ↓
PUBLICATION ELIGIBILITY
  ↓
PUBLIC VERSION or PRIVATE MEMORY
```

---

## 13. Current production implementation

At the frozen implementation baseline, the public claim registry contains 26 machine-resolvable claims distributed across three heterogeneous pilot domains:

| Pilot case | Claims | Purpose |
|---|---:|---|
| 800VDC / SST data-center power architecture | 9 | Test single deployment vs validation, replication, procurement, and adoption boundaries |
| Sodium-ion stationary BESS commercialization | 9 | Test announcement, agreement, production, delivery, commissioning, field performance, history, and economics boundaries |
| China non-squamous NSCLC public research pathway | 8 | Test context-specific public research boundaries and prevention of patient-specific inference |
| **Total** | **26** | |

The public resolver is deterministic. It uses governed claim IDs, aliases, keywords, statements, and case titles. It does not perform external search during resolution and does not use a generative model to reinterpret claim meaning.

The protocol implementation passed the project's internal validation suite and production acceptance scenarios at the frozen baseline. These tests establish implementation consistency, not comparative scientific superiority.

---

## 14. Pilot examples

### 14.1 800VDC / SST

The public registry distinguishes:

- architecture possibility: supported;
- named field deployment: supported, single instance;
- long operating history: not established;
- multi-entity replication: not established;
- independent validation: not established;
- repeat procurement: not established;
- industry adoption: not established.

The central methodological point is that one deployment is a meaningful state transition without being evidence of broad adoption.

### 14.2 Sodium-ion BESS

The public registry distinguishes:

- product announced: supported;
- supply cooperation agreement: supported;
- production readiness: verification required;
- customer batch delivery: not established;
- named commissioned site: not established;
- independent field performance: not established;
- long operating history: unknown;
- lifecycle cost advantage over LFP: not established;
- universal LFP replacement: not established.

This case tests the separation of commercial signaling from deployment and operating evidence.

### 14.3 NSCLC public research

The public registry includes supported context-specific claims, trial-population evidence, and explicit negative boundaries. It does not establish a patient-specific success probability or cross-modality treatment winner. This case tests whether the same evidence protocol can preserve domain-specific limits rather than flattening them into generic answer behavior.

The medical case is a public-research implementation probe and must not be read as a clinical decision service.

---

## 15. Research claims of this paper

This paper makes three bounded claims.

### Claim A — Representation feasibility

It is technically feasible to expose real-world claims as machine-readable objects that jointly preserve evidence state, time boundary, support, non-support, unknowns, provenance, and next observable.

### Claim B — Protocol feasibility

It is technically feasible to route a question through intake, governed match classes, stop-point retrieval, sufficiency assessment, minimum-missing-evidence identification, and human-gated verification without automatically mutating public evidence state.

### Claim C — Cross-domain structural feasibility

The same protocol structure can be instantiated across at least three heterogeneous pilot domains while preserving materially different domain boundaries.

The paper does **not** claim that the current protocol is more accurate, faster, cheaper, or more trustworthy than all alternative systems. Those are empirical questions for external evaluation.

---

## 16. Open replication framework

The replication kit evaluates the system as a black box. External testers should not need repository context.

Key metrics include:

- **Discovery rate** — can an external agent find StructureEvidence without a direct URL?
- **Question-to-claim match rate** — does it identify the intended claim?
- **State preservation rate** — does the downstream answer preserve the claim state?
- **As-of preservation rate** — does it preserve the time boundary?
- **Non-support preservation rate** — does it preserve material `does_not_support` constraints?
- **Isomorphic false-positive rate** — are merely similar questions incorrectly treated as equivalent?
- **Partial-match boundary rate** — is the unresolved portion preserved?
- **Intake decomposition quality** — are multi-part questions decomposed rather than silently simplified?
- **Private-evidence leakage rate** — does any customer-private result reach a public state without eligibility and approval?
- **Autonomous-action violation rate** — does the resolver initiate research, payment, or publication without authorization?

The objective is not to maximize the number of citations. It is to maximize **citation correctness** and boundary preservation.

---

## 17. Falsification and challenge conditions

The method should be challenged, not merely demonstrated. Material failures include:

1. An EXACT match is returned when the evidence threshold differs materially.
2. An ISOMORPHIC match passes despite different scope, temporal meaning, or decision implication.
3. A PARTIAL question is presented as fully answered.
4. `NOT_ESTABLISHED` is paraphrased as established.
5. A single deployment is rendered as broad adoption.
6. `NOT_FOUND_WITHIN_SCOPE` is rendered as non-existence.
7. A stale or review-due state is presented as current without qualification.
8. A public claim is treated as customer-specific applicability without evaluation.
9. A personal medical probability is generated from a public population-level claim.
10. Research is initiated without explicit human authorization.
11. A paid result is published without publication eligibility and human approval.
12. A previous public version is overwritten rather than superseded.

A system that exhibits these failures does not satisfy the intended protocol even if it returns superficially correct prose.

---

## 18. Limitations

The current work has substantial limitations.

First, the public registry contains only 26 claims across three pilot cases. This is sufficient to test architecture, not broad domain coverage.

Second, the current resolver is deterministic and intentionally simple. It may fail to match legitimate paraphrases or may require better equivalence logic as the claim set grows.

Third, freshness is a governed state rather than a fully learned or statistically calibrated variable. Expected change rates and reopen triggers require domain-specific policy.

Fourth, current internal tests do not constitute independent replication. External black-box evaluation is necessary.

Fifth, the current commercial quote model specifies the control structure but does not establish willingness to pay, economic efficiency, or comparative research cost.

Sixth, publication eligibility depends on rights, confidentiality, and source accessibility judgments that may require legal or contractual review in real customer work.

Seventh, the medical pilot is deliberately bounded and cannot establish that the protocol is clinically validated or suitable for patient-specific medical decision support.

---

## 19. Future research

Priority research questions include:

1. How reliably can independent agents discover the method contract and claim registry without direct prompting?
2. What is the false-positive rate of ISOMORPHIC matching at larger registry scale?
3. Can freshness policies be calibrated empirically by claim class?
4. How often can existing claims resolve new questions with zero new research cost (`L0_REUSE`)?
5. Does explicit `does_not_support` metadata improve citation-boundary preservation by downstream agents?
6. How should competing or contradictory evidence states be represented without collapsing disagreement?
7. Can independent systems implement the protocol without adopting the StructureEvidence codebase?
8. What governance is required to standardize public/private evidence transitions across organizations?

---

## 20. Conclusion

The primary problem addressed by StructureEvidence is not retrieval scarcity. It is **evidence-boundary loss** between retrieval and action.

The protocol therefore treats public evidence as a set of versioned, time-bounded claim states. It requires incoming questions to be made resolvable, distinguishes exact from partial and merely isomorphic matches, preserves what evidence does not support, and stops when public evidence is sufficient. When evidence is insufficient, the system identifies the minimum missing evidence and may prepare a bounded verification process, but research remains human-authorized and outcomes remain open. New paid evidence does not automatically become public; publication is a separate governed transition.

The intended long-term role is not to replace search engines, language models, consultants, or domain experts. It is to provide a reusable evidence layer they can resolve against when a question appears.

The design objective can be summarized as:

> **Do not compete for attention before the question exists. Be resolvable when the question arrives.**

And the operational discipline is:

> **Public evidence is reused. Missing evidence is scoped. Research is authorized. Outcomes are never promised.**

---

## References

[1] Lewis, P. et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS 2020. arXiv:2005.11401.

[2] W3C (2013). *PROV-O: The PROV Ontology*. W3C Recommendation, 30 April 2013. https://www.w3.org/TR/prov-o/

[3] Özsoyoğlu, G. and Snodgrass, R. T. (1995). *Temporal and Real-Time Databases: A Survey*. IEEE Transactions on Knowledge and Data Engineering, 7(4), 513–532.

[4] Jensen, C. S. and Snodgrass, R. T. (2018). *Temporal Data Models*. Encyclopedia of Database Systems.

[5] Wilkinson, M. D. et al. (2016). *The FAIR Guiding Principles for scientific data management and stewardship*. Scientific Data 3, 160018. https://doi.org/10.1038/sdata.2016.18

[6] Autio, C. et al. (2024). *Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile*. NIST AI 600-1. https://doi.org/10.6028/NIST.AI.600-1

## Reproducibility resources

- Project site: https://structurevidence.org
- Method contract: https://structurevidence.org/method-contract.json
- Claim index: https://structurevidence.org/claims/index.json
- Resolver: https://api.structurevidence.org/resolve
- Commercial capabilities: https://structevidence.com/capabilities.json
- Frozen implementation baseline: `94ee5dc8670b8132979846c815b400f8cef17ab1`
