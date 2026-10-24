# StructEvidence — Append-Only Correction Principle

**Principle ID:** `SE-APPEND-ONLY-CORRECTION-001`  
**Status:** `OWNER_CONFIRMED`  
**Effective:** 2026-10-24 (prospective adoption; no historical data rewrite)  
**Relationship:** Supplement to [SE-ENG-HISTORY-001](SE_HISTORICAL_RECORD_IMMUTABILITY_STANDARD_v1.0.md); not a replacement.  
**Scope:** All active, folded and provisional StructEvidence observations and all subsequently registered research cases, including privately held and externally hosted case projections. Applies to humans, Codex/agents, case-watch, evidence intake, scientific/engineering reviews, website publications, corrections and social-content preparation.

> **We can be wrong. We must remain auditable.**

## 1. What this principle authorizes — and what it does not

Good-faith error, missing information or provisional interpretation is **not by itself a reason to stop research, case observation or bounded communication**. The system must be able to discover errors, make corrections and improve its method as new evidence appears. An error is a fact about the research process to preserve, not an embarrassment to erase.

This is **not** permission to publish unsupported allegations, hide source limitations, present a failed search as non-existence, declare a provisional observation certified, or bypass authorization, privacy, safety and legal review. When an individual claim is not releaseable, hold **that claim or artifact**, record why, and allow unrelated, approved work to continue.

The aim is not infallibility. It is to reduce the effort needed to reconstruct **what a decision-maker could responsibly have known, relied on, questioned and rechecked at a specific cutoff**. The claim that SE actually reduces decision cost must be measured; this principle does not establish a cost-reduction outcome.

## 2. Non-negotiable invariants

1. **Preserve source bytes and search history.** Keep original source references, URL, access classification, capture/hash where available, query/scope, unavailable sources, and the event/publication/observation/review clocks. Never retrofit a later fact to an earlier knowledge cutoff.
2. **Preserve the reasoning and stop-point as issued.** The original claims, inference chain, source dependencies, counterevidence, assumptions, limitations, accepted or provisional state, review ID and release receipt remain addressable. Never edit, overwrite, delete or silently repurpose an immutable original record.
3. **Correct by adding, not substituting.** Create a new uniquely identified correction, linked to the exact prior record path, ID, commit/blob hash and source cutoff; identify the detected error, new evidence or methodological defect, revised interpretation and remaining uncertainty. Do not call a new correction the old record.
4. **Distinguish research, process, and publication errors.** A false inference, missing `sources_checked`, inaccessible primary source, stale public page, and a confirmed changed real-world state are different observations. A verification-process defect can warrant `REVIEW_INCOMPLETE_FOR_PROVENANCE` **as supplemental audit metadata**; it does not silently rewrite an approved RDL status or imply a real-world event occurred.
5. **Keep the actual review clock.** `NO_STATE_CHANGE` requires a completed bounded review with real inspected sources and explicit counts under the existing freshness contract. If evidence was unavailable, checks were not run, or provenance was incomplete, record `REVIEW_INCOMPLETE`, `SOURCE_UNAVAILABLE`, `CHECK_FAILED` or `NOT_RUN` in the appropriate layer instead of asserting that nothing changed.
6. **Keep valid observations flowing.** A new attributable event may be published as `NEW_EVENT + NO_STATE_CHANGE`, subject to the existing review and website-first gates. Publication of a bounded observation is not certification of a broad conclusion.
7. **Make correction visible to readers who saw the old claim.** Once approved for public release, link the new correction to the corresponding public case/snapshot and visibly identify the former conclusion, corrected statement, difference, and effective observation/correction date. Retain old-version access and an honest change trail; do not silently replace a webpage with a contradictory statement.
8. **Protect sensitive and regulated records.** Privacy, personal safety, security, confidentiality, court orders and applicable erasure/redaction obligations override indiscriminate public retention. In those exceptional cases, follow a separately approved restricted audit/redaction process with minimum necessary public description; do not leak protected material to satisfy append-only ideals.

## 3. Correction workflow

`DETECT -> FREEZE_ORIGINAL_REFERENCE -> CLASSIFY -> REVERIFY -> APPEND_CORRECTION -> REASSESS_STOP_POINT -> HUMAN_RELEASE_GATE -> PUBLISH_LINKED_CORRECTION_IF_APPROVED -> VERIFY_DELIVERY -> MONITOR`

- **Detect:** Capture the challenge, new source or test failure as an observation; distinguish allegation, source statement, independently reviewed evidence and inference.
- **Freeze original reference:** Record the original `case_id`, `claim_id`/`review_id`/`event_id`, path/URL, repository commit and old content hash where available. No edits to the original.
- **Classify:** At least one of `SOURCE_CORRECTION`, `REVIEW_PROVENANCE_DEFECT`, `INFERENCE_CORRECTION`, `EVIDENCE_CONFLICT`, `SOURCE_WITHDRAWN`, `PUBLICATION_DELIVERY_DEFECT`, or `STATE_REOPEN_PROPOSAL`. These are **workflow descriptors**, not additions to RDL's evidence-state enum.
- **Reverify:** Scope the search and counterevidence; identify true event date, document publication date, first discovery, actual review date, and source accessibility. A future or unverified event cannot be backdated.
- **Append:** Add a new immutable correction artifact; record exact prior IDs and causal relationship (`corrects` / `supersedes` / `derived_from`) without deleting the prior record.
- **Reassess:** Clearly distinguish (a) corrected audit/provenance quality, (b) updated available knowledge and (c) any proposed new accepted stop-point. An accepted state changes only with the separate authorized decision artifact.
- **Release:** For an approved public correction, update only regenerateable projections and link from the old public page. Preserve the original public state and publish a dated, citable correction with a human gate.
- **Verify:** Confirm public URL/body marker/version, Git merge SHA and posting receipt. GitHub Pages `success` alone is not proof of the external site's final body; X/LinkedIn drafts are not posts.

### Minimum append-only correction fields

```yaml
correction_id: unique_new_id
principle_id: SE-APPEND-ONLY-CORRECTION-001
case_id: existing_case_id
corrects:
  record_id: original_id
  path_or_url: original_location
  original_commit_or_hash: original_digest_or_UNKNOWN
detected_at: actual_observation_time
event_at: known_time_or_UNKNOWN
source_published_at: known_time_or_UNKNOWN
reviewed_at: actual_review_time_or_NOT_RUN
old_statement: exact_or_traceable_reference
issue_class: SOURCE_CORRECTION | REVIEW_PROVENANCE_DEFECT | INFERENCE_CORRECTION | EVIDENCE_CONFLICT | SOURCE_WITHDRAWN | PUBLICATION_DELIVERY_DEFECT | STATE_REOPEN_PROPOSAL
new_evidence_refs: [] # source IDs, URLs, and capture integrity where available
evidence_access_limits: []
correction_statement: bounded_new_interpretation
old_stop_point: unchanged_historical_reference
proposed_stop_point: unchanged_or_separate_human_approval
unknowns_remaining: []
decision_impact: YES | NO | UNKNOWN | NOT_APPLICABLE
public_projection_approved: false
website_verified: false
social_post_sent: false
```

Field names here describe a **correction-record recommendation**, not an automatic migration of existing schemas. Follow the currently authorized canonical schema and release contract when implementing a typed artifact.

## 4. Existing and future cases

- **Current observations:** The active 800V DC/SST, sodium-ion BESS, Irkutsk and the folded NSCLC track, plus the two separate public research projections (Figure AI × BMW and IREN), are all within scope **without changing their previously frozen/provisional/FOLDED status**.
- **Future cases:** At case registration, attach this principle by ID in the case intake/research plan or applicable case registry. Before any first public release, define original-record locations, immutable IDs, correction lineage, provenance limits, source cutoff and human release gates. Every new case remains capable of explicit correction from its first observation.
- **Independent repos:** A reference to this principle does not authorize importing private source bytes, private Git history or protected data into a public case repository. Each independent release retains its own rights and approval gate.
- **Existing examples:** The appended 2026-10-24 review-provenance correction records for PR #39 and PR #40 document incomplete `sources_checked` support without rewriting the earlier reviews. They demonstrate **audit correction**, not a newly established technical/medical event or an automatic stop-point change.

## 5. Communication rule

Public corrections should follow **question -> original bounded evidence -> discovered limitation/error -> revised state or unresolved gap -> next check -> linked versions**.

Keep the positioning verbatim:

> **Verify Your Verify — Lower the cost of knowing what you can trust.**

No marketing claim about demonstrated accuracy, automatic decision approval, economic savings or company wrongdoing follows from an audit correction. X and LinkedIn remain human-reviewed and website-first under the existing operational contract; do not turn a privately detected error into public news before the approved public correction has been verified.

## 6. Conformance and boundaries

A case/review workflow conforms when: (1) original record hashes are preserved; (2) correction has a new identity and predecessor link; (3) clocks and access limits remain honest; (4) a process mistake does not silently change evidence status; (5) the separate authorization gate is honored; (6) new approved correction pages link to old states and vice versa where permitted; and (7) no existing task, case registry, schedule, protected source or history is implicitly rewritten.

**This principle is additive.** `SE-ENG-HISTORY-001`, canonical RDL schemas, existing case-specific permissions, accepted stop-points, the 22:00 unified task, and the manual X/LinkedIn publication boundary remain in force. It authorizes no retrospective source edits, automatic public release, outreach, paid research or production deployment beyond the specifically reviewed governance addition.
