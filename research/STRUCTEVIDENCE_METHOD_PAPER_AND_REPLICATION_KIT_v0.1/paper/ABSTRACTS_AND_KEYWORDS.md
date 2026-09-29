# Abstracts and Keywords

## Recommended title

**From Retrieval to Defensible Decisions: A Protocol for Time-Bounded Evidence States**

Alternative product-linked title:

**StructureEvidence: A Temporal Evidence Protocol for Agentic Decision Support**

## Standard abstract (~220 words)

Retrieval systems can find information, but retrieval alone does not establish whether a claim is supported, current, independently validated, applicable to a specific use, or sufficient for a decision. This paper presents StructureEvidence, a temporal evidence protocol for converting real-world questions into versioned, bounded evidence states that can be inspected and reused by agents, consultants, and humans. The protocol separates event time from knowledge time; distinguishes claims, evidence, decisions, and unresolved unknowns; and represents each public claim with an explicit state, `as_of` boundary, supporting evidence, `does_not_support` constraints, provenance, and next observable. Incoming questions pass an intake gate and are matched as EXACT, ISOMORPHIC, PARTIAL, or NONE. Where public evidence is insufficient, the protocol identifies minimum missing evidence, proposes a candidate research depth, and can generate a bounded verification quote while requiring explicit human authorization. Paid research purchases a controlled process rather than a predetermined outcome, and new evidence is classified for publication eligibility before any append-only public state transition. We report a production implementation spanning three heterogeneous pilot domains, 26 machine-resolvable claims, a deterministic public resolver, a method contract, and a public change feed. The present work is a methods and systems contribution, not a comparative performance claim. An open replication and challenge kit is released to test discovery, claim matching, boundary preservation, freshness, partial-match behavior, and public/private evidence controls.

## Short abstract (~90 words)

StructureEvidence is a protocol for converting retrieved information into time-bounded evidence states without silently upgrading uncertainty into fact. It exposes versioned claims containing state, `as_of`, support, non-support boundaries, provenance, and unresolved evidence gaps. Questions are gated and matched as EXACT, ISOMORPHIC, PARTIAL, or NONE; insufficient evidence can trigger a human-authorized verification process, while paid results remain private unless independently eligible and approved for publication. A production implementation currently exposes 26 machine-resolvable claims across three heterogeneous pilot domains and is released with an open replication kit.

## One-sentence abstract

StructureEvidence turns questions into versioned evidence states with explicit temporal, inferential, authorization, and publication boundaries so that agents can reuse evidence without silently reasoning beyond it.

## Keywords

- agentic research
- evidence provenance
- temporal evidence
- claim verification
- retrieval-augmented systems
- decision support
- uncertainty representation
- provenance
- human-in-the-loop
- reproducibility
- append-only evidence
- public/private evidence boundary
