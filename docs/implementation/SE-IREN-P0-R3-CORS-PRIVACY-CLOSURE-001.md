# SE-IREN-P0-R3-CORS-PRIVACY-CLOSURE-001 · 2026-10-27
Status: PARTIAL — STATIC_CODE_REVIEW_PASS; LIVE_BROWSER_PREFLIGHT_BLOCKED; HUMAN_PRIVACY_SIGNOFF_PENDING.
Repository and evidence lock: PR #54 `337fbdb8cd7a4332dc482b264af383389ece7fd5`, main `56f8e345ddfc697855c8eb9492dc0b49d24c6fcc`; no merges/migrations/deploys/production POST authorized.

## Track A: Staging CORS and three-language review
**Static code observations** from the PR:
- `deploy/cloudflare-landing/worker.js` `corsHeaders` for allowlisted Origin advertises `POST, OPTIONS` and `content-type, idempotency-key`.
- `deploy/cloudflare-landing/commercial-upgrade.js` fetch uses both `content-type: application/json` and `idempotency-key`. Client uses `SE-CUSTOMER-PRIVACY-v1` and `consent_accepted`.
- EN/zh-CN/es chrome localization exists; the shared consent checkbox and the shared form's Turnstile guidance are English text within the shared component. Do **not** claim full consent localization in each language.
- Production R1 observed older deployed Worker responds OPTIONS with `content-type` only. That is **old production**, not proof of new-code CORS failure.
**Live verification NOT performed**: web/browser retrieval for staging was inaccessible in this tool environment; DNS from container failed. Never elevate source-code inspection to actual browser E2E or claim 200/204 observed.

### Codex browser/HTTP acceptance — STAGING ONLY
1. Reverify current HEAD and isolated staging URL `https://structevidence-commercial-staging.roalstoney.workers.dev`; don't modify or probe production.
2. Perform real cross-origin OPTIONS from an Origin allowlisted by staging config (if actual staging frontend is same-origin, that route may be browser same-origin and not trigger CORS preflight; use a dedicated authorized test Origin or explicitly identify absence of preflight). Send `Origin: <allowlisted>`, `Access-Control-Request-Method: POST`, `Access-Control-Request-Headers: content-type,idempotency-key`. Expect 204 with correct allow-origin and allow-headers. Prove disallowed Origin does not receive approval; record sanitized status only.
3. Inspect EN/zh-CN/es live routes and form: language markers, consent checkboxes, policy version, Turnstile action, legal policy links; trace actual submission flow using synthetic staging identities only and a valid challenge. Confirm 201 → retry 200 with same ID → conflicting payload 409, without changing synthetic record counts beyond authorized test.
4. Explicitly audit whether shared-form consent and accessibility/error text remain English on zh-CN and es routes. If yes, classify `LOCALIZED_CONSENT=INCOMPLETE` and propose localized copy + native-speaker review without altering the frozen consent meaning. Preserve versioning; no translation should imply research/publication authorization.
5. Record real request/response metadata, no tokens, cookies, admin emails, PII or test fixture raw fields in public GitHub. If no authorized cross-origin test page exists, mark `BROWSER_PREFLIGHT_NOT_APPLICABLE_SAME_ORIGIN` separately from HTTP OPTIONS response.
Result: `CORS_STATIC=PASS`, `CORS_REAL_STAGING=BLOCKED_TOOL_ACCESS`, `THREE_LANGUAGE_ROUTE_PRIOR_STAGING=PASS_AS_PREVIOUSLY_REPORTED`, `LOCALIZED_SHARED_CONSENT=INCOMPLETE_IN_SOURCE`.

## Track B: human privacy review and signoff
Technical precheck only; cannot claim a real human/legal approval:
- Current shared checkbox: `I understand that this submission remains customer-private, does not authorize research, and will not be published without separate written authorization.` Required checkbox. Server consent version `SE-CUSTOMER-PRIVACY-v1` and research status `NOT_AUTHORIZED`.
- Review user-visible document links/versions on **all** language routes, with exact hashes and accessibility; inspect controller identity, contact, purpose, legal basis as applicable, retention for raw request vs append-only event/consent, erasure/access rights, transfer/subprocessor location and emergency breach handling. Do not silently assume compliance with specific jurisdictions.
- Human reviewer must verify EN/zh-CN/es legal equivalent meaning; shared consent currently in English in code. Decide whether localized consent is a must-fix before production; record as a known user comprehension risk pending signoff.
- Review admin Access least privilege, API/UI audience separation, analytics/redaction, idempotency 24h vs historical consent retention, Turnstile fallback for accessibility, age/minor data safeguards where applicable, separate marketing opt-in.
- Signed approval remains in a **restricted internal record**, with named human identity, qualifications/role, timestamp, exact policy hash/version, scope, decision, tracked remediation items; public PR contains ONLY status, hashes, and non-sensitive reason codes.
- No auto-approval by Codex/assistant. Reviewer `UNASSIGNED`, `HUMAN_PRIVACY_LEGAL_SIGNOFF=PENDING`.

### Minimal private approval template (do not fill fictitiously)
REVIEWER_IDENTITY_PRIVATE:
ROLE_AND_AUTHORITY:
POLICY_AND_COPY_HASHES:
JURISDICTIONS:
FINDINGS_AND_MUST_FIX:
DECISION=APPROVED/CONDITIONALLY_APPROVED/REJECTED:
SIGNED_AT_UTC:
RECORD_LOCATION_RESTRICTED:

## Combined gate
`STAGING_CORS_BROWSER_E2E=NOT_VERIFIED`
`SHARED_FORM_CONSENT_TRANSLATION=NEEDS_REVIEW`
`HUMAN_PRIVACY_LEGAL_SIGNOFF=PENDING`
`PRODUCTION_RECOVERABILITY=UNKNOWN`
`READY_FOR_OWNER_PRODUCTION_RELEASE=NO`
`PR54_DRAFT=YES`; `PR54_MERGED=NO`; `PROD_D1_0003=NOT_APPLIED`; `PROD_WORKER_DEPLOY=NO`; `PROD_POST=0`.
