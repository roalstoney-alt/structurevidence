# STRUCTEVIDENCE_METHOD_PAPER_AND_REPLICATION_KIT_v0.1

This replication kit accompanies:

**From Retrieval to Defensible Decisions: A Protocol for Time-Bounded Evidence States**

Version: v0.1

Version DOI: https://doi.org/10.5281/zenodo.23033588

Concept DOI: https://doi.org/10.5281/zenodo.23033587

Zenodo record: https://zenodo.org/records/23033588

Protocol: `QUESTION_TO_EVIDENCE_COMMERCE_PROTOCOL_v0.1`

Implementation baseline: `94ee5dc8670b8132979846c815b400f8cef17ab1`

Status: **publication candidate / open replication package**
Implementation baseline: `94ee5dc8670b8132979846c815b400f8cef17ab1`
Date: 2026-09-29

## Purpose

This package turns the current StructureEvidence implementation into a publishable methods artifact and an externally testable replication/challenge kit.

The central research question is:

> How can an agent, consultant, or human move from retrieval to a defensible, time-bounded evidence state without silently converting missing evidence, stale evidence, single-instance evidence, or source claims into stronger conclusions?

The package treats StructureEvidence as a **question-to-evidence resolution protocol**, not as a general answer engine. Its public core is machine-readable, versioned, human-gated, and explicit about what the evidence does **not** support.

## Current production surfaces

- Public research / trust plane: `https://structurevidence.org`
- Runtime resolution plane: `https://api.structurevidence.org/resolve`
- Commercial action plane: `https://structevidence.com`
- Method contract: `https://structurevidence.org/method-contract.json`
- Claim index: `https://structurevidence.org/claims/index.json`
- Change feed: `https://structurevidence.org/changes.json`
- Discovery manifest: `https://structurevidence.org/.well-known/structurevidence.json`

## Package contents

### Paper
- `paper/STRUCTEVIDENCE_METHOD_PAPER_EN_v0.1.md` — full English methods paper.
- `paper/STRUCTEVIDENCE_METHOD_PAPER_ZH_v0.1.md` — full Chinese version.
- `paper/ABSTRACTS_AND_KEYWORDS.md` — short/standard abstracts and keywords.
- `paper/REFERENCES.bib` — bibliography starter.

### Protocol specification
- `spec/QUESTION_TO_EVIDENCE_PROTOCOL_SPEC_v0.1.md` — RFC-style protocol specification.
- `spec/METHOD_CONTRACT_PUBLIC_v0.1.md` — concise public method contract.

### Replication and challenge
- `replication/REPLICATION_AND_CHALLENGE_PROTOCOL_v0.1.md` — black-box replication procedure.
- `replication/TEST_CASES_v0.1.jsonl` — machine-readable test set.
- `replication/EXPECTED_RESULTS_v0.1.csv` — human-readable expected result summary.
- `replication/CHALLENGE_SUBMISSION_TEMPLATE.md` — external challenge template.

### Publication and communication
- `publication/MEDIUM_DRAFT_EN.md` — public-facing English article.
- `publication/ZHIHU_DRAFT_ZH.md` — public-facing Chinese article.
- `publication/PUBLIC_LAUNCH_NOTE.md` — launch note and call for replication.

### Release / workflow
- `release/CODEX_PUBLICATION_WORKFLOW.md` — controlled release workflow.
- `release/RELEASE_MANIFEST.json` — package manifest and frozen baseline.
- `release/LICENSE_RECOMMENDATION.md` — non-binding publication licensing options.

### Figures
- `figures/ARCHITECTURE.mmd` — Mermaid architecture figure.
- `figures/EVIDENCE_STATE_MACHINE.mmd` — Mermaid protocol state machine.

## Publication positioning

This should be released as a **methods preprint / working paper**, not as a claim of scientific superiority over retrieval, RAG, or other evidence systems. The current implementation demonstrates structural feasibility across three heterogeneous pilot domains and exposes a public resolver for independent testing. It does not yet establish comparative accuracy, economic benefit, or generalizability.

## Frozen methodological principles

1. `FACT != CLAIM != EVIDENCE != DECISION`
2. `EVENT_TIME != KNOWLEDGE_TIME`
3. `NOT_FOUND_WITHIN_SCOPE != DOES_NOT_EXIST`
4. `SINGLE_INSTANCE != INDUSTRY_ADOPTION`
5. `ORDER != DELIVERY != COMMISSIONING != OPERATING_HISTORY`
6. `SOURCE_STATEMENT != INDEPENDENT_VALIDATION`
7. `UNKNOWN remains UNKNOWN until qualifying evidence resolves it`
8. Public evidence may be sufficient, partially sufficient, stale, or not applicable to a specific use.
9. Research requires authorization.
10. **Process bought; outcome not bought.**
11. Paid evidence does not automatically become public.
12. Public state transitions are append-only and human-approved.

## Recommended release order

1. Freeze this package against the stated implementation baseline.
2. Publish the English preprint and protocol spec in the repository.
3. Publish the replication kit and challenge template at the same time.
4. Publish the public launch note with resolver examples.
5. Release Medium and Zhihu versions only after the canonical method paper URL is stable.
6. Collect replication failures and boundary violations before adding new product features.

## Important limitation

The three current pilot cases are not presented as statistically representative of all domains. They are heterogeneous implementation probes: industrial power architecture, stationary sodium-ion storage, and a bounded public medical research case. External replication is required.
