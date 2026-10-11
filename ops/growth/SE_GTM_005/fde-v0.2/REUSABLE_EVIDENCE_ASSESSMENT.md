# SE-GTM-005 v0.2 — Reusable Evidence Assessment

STATUS = `LIGHTWEIGHT_PROPOSAL_ONLY`

NEW_INFRASTRUCTURE_REQUIRED = `NO`

FEASIBILITY = `CONDITIONAL`

## Finding

The existing StructEvidence concepts—claim IDs, controlled evidence states,
per-item provenance, `as_of`, counterevidence, decision memory, append-only
versions and stop-points—can represent a reusable FDE evidence core. A new
database, API or truth model is not justified by this research.

Reuse is conditional because customer environments, policies, data and
acceptance thresholds cannot be generalized from one deployment to another.

## Proposed record

| Field | Purpose | Reuse rule |
| --- | --- | --- |
| claim_id | Stable normalized assertion | Reusable only when wording and scope remain identical. |
| product_version | Software/model/configuration boundary | New material version requires review. |
| source_provenance | Source, owner, date and collection method | Preserve item-level provenance; never replace with pack date. |
| test_environment | Infrastructure, data class and integration context | Customer environment is not transferable by default. |
| validity_conditions | Conditions under which evidence applies | Omission prohibits reuse. |
| customer_dependencies | Policies, thresholds, roles and data assumptions | Always customer-specific. |
| evidence_state | SUPPORTED / OBSERVED / UNKNOWN / NOT_ESTABLISHED / CONTRADICTED | Preserve one-to-one canonical semantics. |
| counterevidence | Conflicts, exceptions and failure results | Append; never suppress for sales use. |
| review_requirement | Trigger or date for re-evaluation | Use explicit triggers; do not invent expiry scoring. |
| reuse_restrictions | Contractual, confidentiality and technical limits | Must pass rights and authority review. |
| source_rights | Publication, sharing and derivative-use boundary | Private material cannot enter public records. |
| change_log | Append-only evidence and interpretation history | Earlier evidence dates and conclusions remain visible. |

## Core and overlay architecture

`REUSABLE_CORE`

- product-level architecture and allowed-action claims;
- versioned test methodology;
- generic evaluation results where rights permit;
- known limitations and failure taxonomy;
- standard control mapping;
- public product evidence.

`CUSTOMER_OVERLAY`

- customer environment and data classification;
- approved use case, labels, thresholds and decision deadline;
- security, identity, retention and integration configuration;
- customer-observed results and acceptance record;
- private contractual and commercial context.

The overlay may reference the reusable core, but it must never inherit a
`SUPPORTED` or `OBSERVED` state without checking that version, environment,
scope and rights remain applicable.

## Invalidation and review triggers

- model, prompt, retrieval, tool or policy version changes;
- material customer-data distribution change;
- new tool permission or autonomous action;
- security control, identity or retention change;
- new counterexample or regression;
- acceptance threshold change;
- source correction, retraction or access-rights change;
- customer withdrawal or restriction of evidence use.

## Decision

REUSABLE_EVIDENCE_FEASIBILITY = `CONDITIONAL_YES`

The next implementation should be a file-level pilot using the existing model,
not a new infrastructure layer. Production implementation remains unauthorized.
