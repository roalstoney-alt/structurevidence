# SE-IREN-P0-R3 privacy/legal human signoff checklist

Status: `HUMAN_PRIVACY_LEGAL_SIGNOFF=PENDING`

This is an unsigned review checklist. It is not a legal opinion, a privacy approval, or evidence that a qualified human reviewer has approved production release. A completed signature record must remain in an access-controlled internal location; do not commit names, signatures, credentials, customer data, JWTs, OTPs, or private findings to this public repository.

## Artifact lock

- Consent version: `SE-CUSTOMER-PRIVACY-v1`
- Source copy file SHA-256: `1ce655d7167a7ac45682d1b924f4c1cf2a9c152ef7b09371085f2dd3e904cd4f`
- Worker file SHA-256: `2218d1dbbeb182b21edb989b48f399c6841c8f247d19cd79f9a48bbd7736f21e`
- Review scope: English, Simplified Chinese, and Spanish consent, challenge guidance, request errors, confirmation boundary, privacy page, intake storage, and admin access controls.
- Repository result record: `docs/implementation/SE-IREN-P0-R3-CORS-PRIVACY-CLOSURE-001-RESULT.md`

The responsible reviewer must independently recompute hashes from the exact release candidate. Any hash change invalidates the review and requires a new signature record.

## Consent meaning and language equivalence

- [ ] English copy clearly states all three independent conditions: customer-private submission; no research authorization; no publication without separate written authorization.
- [ ] Simplified Chinese copy is materially equivalent to all three English conditions and does not imply research or publication authorization.
- [ ] Spanish copy is materially equivalent to all three English conditions and does not imply research or publication authorization.
- [ ] A qualified human language reviewer has checked the Simplified Chinese copy in context.
- [ ] A qualified human language reviewer has checked the Spanish copy in context.
- [ ] `consent_accepted` remains mandatory and the server requires the exact `SE-CUSTOMER-PRIVACY-v1` version before any D1 write.
- [ ] Consent to intake is not combined with research authorization, public-release authorization, marketing consent, or payment acceptance.

## User comprehension and failure behavior

- [ ] EN, zh-CN, and ES challenge guidance states that no request is submitted when verification cannot load.
- [ ] EN, zh-CN, and ES invalid-verification, oversized-request, conflict, validation, and service-unavailable messages do not imply that data was recorded.
- [ ] Confirmation copy keeps `CUSTOMER_PRIVATE` and `NOT_AUTHORIZED` visible and says that the form does not start research.
- [ ] Email fallback does not claim to have the same transport, retention, idempotency, or deletion controls as the web intake.
- [ ] Turnstile and error UI is usable with keyboard navigation and assistive technology, including an intelligible fallback when the challenge cannot load.

## Privacy governance

- [ ] The legal controller/operator identity and privacy contact are accurate and reachable.
- [ ] Purpose and lawful basis have been reviewed for each intended jurisdiction; no jurisdiction-specific compliance is inferred from this checklist.
- [ ] Retention is defined separately for raw requests, consent receipts, idempotency records, and append-only events.
- [ ] Access, correction, erasure, objection, and complaint handling are documented, including where append-only audit obligations constrain deletion.
- [ ] Cross-border transfers, Cloudflare/D1/Turnstile subprocessors, processing locations, and applicable contractual safeguards have been reviewed.
- [ ] Incident and breach escalation owners, time limits, evidence preservation, and notification decisions are documented.
- [ ] Minor/age-sensitive submissions, prohibited data, secrets, and unnecessary personal data have explicit handling rules.
- [ ] No analytics, logs, error reporting, or support fallback exposes raw customer fields, tokens, IP-derived identifiers, or challenge responses beyond the approved purpose and retention boundary.

## Access and release control

- [ ] Cloudflare Access UI/API audiences remain separate and least-privilege administrator membership has been reviewed.
- [ ] Staging and production D1/Worker resources are isolated; no synthetic staging record is present in production.
- [ ] Production migration `0003`, Worker deployment, and public release each have an identified human owner and explicit rollback/no-go decision.
- [ ] Production recovery limitations and the synthetic-only restore evidence are accepted or remediated by the accountable owner.
- [ ] A second qualified human has independently reviewed any must-fix findings before release.

## Restricted signature record fields

Complete these fields only in the restricted system of record, never in this repository:

```text
REVIEWER_IDENTITY_PRIVATE:
ROLE_AND_AUTHORITY:
QUALIFICATIONS_OR_REVIEW_BASIS:
POLICY_AND_COPY_HASHES:
JURISDICTIONS_AND_SCOPE:
FINDINGS_AND_MUST_FIX:
RESIDUAL_RISKS_ACCEPTED:
DECISION=APPROVED/CONDITIONALLY_APPROVED/REJECTED:
SIGNED_AT_UTC:
RECORD_LOCATION_RESTRICTED:
```

Until an authorized human completes the restricted record and records only a non-sensitive approval reference in the PR, `HUMAN_PRIVACY_LEGAL_SIGNOFF=PENDING` and `READY_FOR_OWNER_PRODUCTION_RELEASE=NO`.
