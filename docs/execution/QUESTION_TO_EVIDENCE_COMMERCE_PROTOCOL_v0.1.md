# Question-to-Evidence Commerce Protocol v0.1

Status: active

Entry baseline: `79b21a0ded70af2a6b8bcd81ae097f81ea256357`

Implementation commits: `33a6d8e`, `d2b4024`

## Protocol

The existing read-only resolver now applies a deterministic governed sequence:

`QUESTION_INTAKE → CLAIM_MATCH → PUBLIC_STOP_POINT → MINIMUM_MISSING_EVIDENCE → HUMAN_AUTHORIZED_VERIFY`

Question intake evaluates atomicity, falsifiability, scope, and time boundary. Failed intake returns a decomposition draft, requires human selection, and stops before claim matching. Passing questions are classified as EXACT, ISOMORPHIC, PARTIAL, or NONE. ISOMORPHIC reuse requires an explicit six-dimension equivalence check and downgrades to PARTIAL if any dimension fails.

The public stop point preserves the existing state, supports, does-not-support boundary, as-of time, unknowns, next observable, and canonical URL. Freshness, verification depth, applicability, and sufficiency are additive protocol metadata; none modifies the 26 public claim objects.

## Commerce boundary

Sufficient current public evidence returns `CITE_AND_STOP` with no quote. Partial or unresolved evidence identifies only the minimum resolving evidence and a candidate RDL level. A generated verification quote defines process scope, source envelope, cutoff, cap status, and stop conditions; its price remains `TO_BE_DEFINED`, research remains `NOT_AUTHORIZED`, and `outcome_guaranteed` is false.

The commercial Verify page accepts safe query-string prefill for question, claim ID, match class, missing evidence, and candidate RDL level. The user must still explicitly submit. Submission starts human review only and does not authorize research or payment.

Paid-cycle authorization requires all three states: `QUOTE_ACCEPTED`, `PAYMENT_CONFIRMED`, and an explicit `RESEARCH_AUTHORIZED` authorization record.

Publication eligibility is separately classified as PUBLIC_ELIGIBLE, CUSTOMER_PRIVATE, MIXED_REDACTABLE, or another restricted state. Every classification requires human publication review and returns `public_transition_authorized: false`. Existing public versions and `changes.json` remain append-only and unchanged.

## Versioned primitives

- `protocol/question-intake/schema-v0.1.json`
- `protocol/claim-match/schema-v0.1.json`
- `protocol/freshness/schema-v0.1.json`
- `protocol/applicability/schema-v0.1.json`
- `protocol/verification-quote/schema-v0.1.json`
- `protocol/publication-eligibility/schema-v0.1.json`

## Deployment

- Resolver Worker: `structurevidence-public-claim-resolver`
- Resolver version: `0da1fedf-da85-41f5-bb30-6db03f9f86ed`
- Commercial Worker: `structevidence-commercial`
- Commercial version: `24efd0bc-0e0d-430d-b200-84f5191bc470`
- Production endpoint: `https://api.structurevidence.org/resolve`

## Acceptance

- Scenario 1, EXACT → CITE_AND_STOP: PASS.
- Scenario 2, PARTIAL → minimum missing evidence → quote-ready handoff: PASS.
- Scenario 3, NONE → NO_PUBLIC_MATCH: PASS.
- Scenario 4, ISOMORPHIC → equivalence PASS → public stop-point reuse: PASS.
- Scenario 5, simulated CUSTOMER_PRIVATE result → no public transition: PASS.
- Failed multi-part intake → decomposition and STOP: PASS.
- Commercial prefill with no auto-submit: PASS.
- Personal medical query with no quote or commercial action: PASS.
- Resolver backward compatibility: PASS.
- Capabilities manifest boundary: PASS.
- Root/docs parity and deterministic generation: PASS.
- Public claim files changed: 0.
- Public primitives, CML history, RDL history, and changes feed changed: 0.
- Automatic research authorization, payment, or publication: NO.
- Outcome guaranteed: NO.

The pre-push suite completed 80 local tests plus both Worker bundle validations. Production acceptance fetched and validated the resolver, method contract, agent page, commercial capabilities, and commercial client script.
