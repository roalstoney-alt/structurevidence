# Question-to-Evidence Resolution Protocol Specification v0.1

**Status:** Public draft specification
**Compatibility baseline:** StructureEvidence implementation `94ee5dc8670b8132979846c815b400f8cef17ab1`

## Scholarly Reference

- Version DOI (exact v0.1 publication): https://doi.org/10.5281/zenodo.23033588
- Concept DOI (all versions): https://doi.org/10.5281/zenodo.23033587
- Zenodo record: https://zenodo.org/records/23033588

This specification is described by method paper v0.1 and implemented by `QUESTION_TO_EVIDENCE_COMMERCE_PROTOCOL_v0.1` at baseline `94ee5dc8670b8132979846c815b400f8cef17ab1`.

## 1. Scope

This specification defines a protocol for resolving natural-language questions to governed evidence states while preserving temporal, inferential, authorization, and publication boundaries.

It does not define a universal truth ontology, a ranking of sources, a general-purpose search engine, or an autonomous research agent.

## 2. Normative terms

The keywords **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are used normatively within this specification.

## 3. Required principles

An implementation conforming to this protocol MUST preserve the following distinctions:

- fact / claim / evidence / decision;
- event time / knowledge time;
- not-found-within-scope / non-existence;
- single instance / adoption;
- source statement / independent validation;
- unknown / supported.

## 4. Question intake

An incoming question SHOULD be evaluated for:

- atomicity;
- falsifiability;
- scope;
- time boundary.

If a material criterion fails, the implementation MUST NOT silently select a narrower question. It SHOULD return a decomposition draft and require human selection or reframing.

## 5. Match classes

### EXACT

The question and governed claim have equivalent subject, predicate, evidence threshold, material scope, and temporal semantics.

### ISOMORPHIC

The natural-language form differs but the resolving evidence structure is equivalent. The implementation MUST check subject, predicate, evidence threshold, scope, temporal meaning, and decision implication. A failed equivalence check MUST downgrade the result to PARTIAL.

### PARTIAL

Existing public evidence resolves only a subset of the requested proposition. The implementation MUST expose the resolved boundary and unresolved portion separately.

### NONE

No governed public claim resolves the question. The implementation MUST NOT generate a new evidence state merely to answer the question.

## 6. Public stop-point

A public stop-point SHOULD contain:

```text
state
supports
does_not_support
as_of
freshness
verification_depth
applicability
unknowns
next_observable
canonical_url
```

`does_not_support` MUST be treated as a first-class semantic boundary.

## 7. Freshness

Allowed public freshness states:

- CURRENT
- REVIEW_DUE
- STALE
- UNKNOWN

Age alone MUST NOT determine staleness.

## 8. Sufficiency

Allowed sufficiency states:

- SUFFICIENT
- PARTIALLY_SUFFICIENT
- INSUFFICIENT
- UNKNOWN

If the public stop-point is sufficient and acceptably fresh, the implementation SHOULD return `CITE_AND_STOP` and MUST NOT require paid continuation.

## 9. Minimum missing evidence

When evidence is insufficient, the implementation SHOULD identify the minimum evidence that could resolve the bounded question. It SHOULD NOT create an unconstrained research agenda.

## 10. Candidate research depth

A system MAY map minimum missing evidence to a candidate research level. A candidate level MUST NOT be interpreted as authorized research.

Reference mapping in the current implementation:

- L0_REUSE
- L1_VERIFY
- L2_INVESTIGATE
- L3_DEEP

## 11. Verification quote

A quote MAY specify:

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
- publication-rights status.

A quote MUST state that human authorization is required and MUST NOT guarantee the research outcome.

## 12. Authorization

Generating a quote MUST NOT authorize research.

Research SHOULD begin only after the required explicit authorization state is present.

## 13. Paid research outcome

A paid cycle may legitimately end in supported, not established, contradicted, public-data-insufficient, access-restricted, or another controlled result.

The process is purchased; the outcome is not.

## 14. Publication eligibility

New evidence MUST NOT automatically become public.

Evidence SHOULD be classified into publication states such as:

- PUBLIC_ELIGIBLE
- CUSTOMER_PRIVATE
- MIXED_REDACTABLE
- CONFIDENTIAL
- SOURCE_CONTROLLED

Only public-eligible evidence plus human publication approval MAY create a new public stop-point version.

## 15. Versioning

Public versions MUST be append-only. Previous public states MUST remain recoverable and MUST NOT be silently overwritten.

## 16. Agent behavior

A public resolver MUST NOT autonomously:

- create a paid request;
- spend research resources;
- authorize L1/L2/L3 work;
- publish customer evidence;
- modify public claim state;
- generate patient-specific medical advice from public claims.

## 17. Medical boundary

For public medical research claims, population-level evidence MUST NOT be converted into a personal probability, treatment ranking, diagnosis, or prognosis unless a separately governed clinical workflow explicitly supports such action.

## 18. Interoperability target

The protocol is intended to be implementable independently of the StructureEvidence codebase. A conforming third-party implementation may use different storage, retrieval, or runtime technologies provided the semantic and governance boundaries above are preserved.

## 19. Conformance testing

Minimum conformance tests SHOULD include:

- intake-fail decomposition;
- exact match;
- isomorphic equivalence pass and fail;
- partial match;
- no match;
- state preservation;
- `as_of` preservation;
- `does_not_support` preservation;
- no autonomous research;
- publication eligibility;
- private evidence protection;
- append-only version behavior.
