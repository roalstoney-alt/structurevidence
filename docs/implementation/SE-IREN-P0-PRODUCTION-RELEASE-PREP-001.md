# SE-IREN-P0-PRODUCTION-RELEASE-PREP-001 · Owner preflight v0.1

Status: PREPARATION_ONLY / NOT AUTHORIZED TO MERGE OR DEPLOY
Review based on PR #54 HEAD `35a4ac93fc9bd7dcd3f3b6571edebf098d334266`, main `56f8e345ddfc697855c8eb9492dc0b49d24c6fcc`.
Observed staging acceptance: real Access admin GET 200, real valid Turnstile 201 and invalid 400, other fault classes deterministic, 56/56 Worker tests per recorded acceptance, historical 11 Python failures. This does not certify production readiness or legal/privacy approval.

## 0. Four independent approval gates
GATE-A merge PR #54 into public GitHub repository main; source-code publication only. Requires separate explicit owner approval and immutable HEAD lock.
GATE-B authorize a dated controlled production D1 migration 0003; no migration based solely on merge.
GATE-C authorize controlled production Worker+frontend release with configured live Turnstile, Access and secrets; must not precede B.
GATE-D authorize exactly scoped synthetic production POST and Access-protected admin readback; must not occur before C. Real lead acquisition, social posting and IREN public pilot are additional independent approvals.
All gates currently CLOSED.

## 1. Change scope and immutable starting point
Review full PR diff, including non-intake tests, docs and configs. Confirm current main/head SHA and no intervening commits. Existing production name `structevidence-commercial`, route `structevidence.com`, D1 `structurevidence-customer-cases` id `aee10591-536a-47af-8ee0-957551ba2360`, existing limiter namespace `842001`. Do not substitute staging resource IDs.
Explicit observed placeholder in pr-head wrangler.jsonc: `TURNSTILE_SITE_KEY=CONFIGURE_TURNSTILE_SITE_KEY`; must replace before any deploy. `TURNSTILE_EXPECTED_HOSTNAMES=structevidence.com,www.structevidence.com`, expected action `public-intake`; the real configured widget must cover both hostnames actually used.
All deployment credentials/config preflight is **read-only** in preparation phase. Document only presence/absence of secrets, never values.

## 2. Change window and order: FUTURE, NOT EXECUTE NOW
(1) Obtain named owner approvals for GATE-A, GATE-B and GATE-C individually, named operator and rollback approver. Announce maintenance/change window, freeze unrelated intake changes, capture code versions and current live route versions. Verify D1 read-only table/row/trigger/migration inventory and availability of backup/restore mechanism.
(2) Prove recoverability of a current production database snapshot using a separate isolated restore target, without modifying production. Evidence required: backup method, timestamp, PITR bookmark or export hash, restore test ID, successful schema/row-count consistency and RPO/RTO *measured*, not invented.
(3) Confirm live Turnstile public site key and secret are provisioned for production hosts/action, Access admin audience/email allowlists match production, rate limiter and CORS correct. Validate staged frontend is compatible with deployed worker. Ensure no placeholder remains.
(4) Apply additive `0003_intake_hardening.sql` to production D1 ONLY at GATE-B after verified restore capability. Check exactly five original/new core tables (customers, requests, request_events, request_idempotency, request_consent_receipts), migrations, indexes, foreign keys, four UPDATE/DELETE guards for events+consent, no unexpected data mutation, and original customer counts.
(5) Deploy Worker and corresponding EN/ZH/ES frontend together at GATE-C, using explicit verified worker version and change record. Do not deploy server alone (old client cannot supply required idempotency/consent/Turnstile), nor client alone (old server ignores new privacy attributes). Immediately run read-only route, JS, binding and Access redirect checks. Monitoring for 5xx/429/400, D1 failures, Turnstile failures, latency and redaction must be enabled with safe logging. Avoid exposing visitor PII in logs.
(6) Only after GATE-D approve a clearly marked synthetic POST with dedicated test-controlled address and valid production Turnstile; verify 201, 200 replay, 409 conflict (if explicitly in authorized scope), authenticated GET 200 and matching private D1 event+consent. Do not perform unsolicited real-user submission or expose sensitive payload in public records.
(7) Separate owner release gate for IREN daily evidence candidate exact hash, real reviewer, legal/privacy review and human-approved X/LinkedIn release. Never auto publish based on API health.

## 3. Recovery and stop strategy
Before first production customer submission under 0003: prior Worker binary may be restored only as a controlled plan with matching old frontend; keep migration 0003 in place wherever possible. SQL DROP recipe in existing `0003_intake_hardening_ROLLBACK.md` applies only if empty and separately explicitly authorized; **never run automatically**.
After any intake submission under 0003: preserve `request_consent_receipts`, idempotency mappings and event records; no DROP/rewrite/history deletion. If Worker health fails, freeze incoming mutations or route to transparent temporary unavailability; isolate defect, roll forward with compatible code, or recover approved prior working version only after checking versioned client compatibility and implications for historical receipts.
PITR recovery of production to an earlier moment is not a routine rollback because it may lose real accepted records. Require reconciliation of post-backup accepted writes before any restore; prefer forward correction and audit.
Stop immediately: unexpected production D1 binding; missing required key/secret; D1 migration mismatch; inability to restore; old/new form mismatch; unidentified 5xx/duplicate writes; missing append-only triggers; personal data in debug logs; non-authorized Access 200; provider Turnstile accepts wrong host/action; legal/privacy reviewer rejects terms. Suspend GATE-C/D and record append-only incident event, preserve raw audit evidence in restricted store.

## 4. HUMAN_PRIVACY_LEGAL_CHECKLIST (real people, not automation)
Each must capture actual reviewer identity *privately*, role, timestamp, policy hash, approve/reject and comment. No AI can mark human signoff complete.
[ ] Consent text English, Chinese, Spanish and shared form consistent with server `SE-CUSTOMER-PRIVACY-v1`; consent is not research authorization or permission to publicly share.
[ ] Clear controller/operator identity, purpose, fields, privacy policy link, storage jurisdiction/processors, retention/deletion handling and contact channel; review for each relevant jurisdiction.
[ ] User can decline consent without a silent submission; failures preserve no unnecessary personal data.
[ ] Data minimization and no production request or identity in public evidence/marketing repository; support mail delivery remains unverified until tested.
[ ] 24h idempotency retention and permanent append-only receipts checked for legal retention, deletion/erasure requests, reversibility and synthetic record cleanup procedures.
[ ] Access policy roles, least privilege, break-glass recovery, audit logging and account offboarding; user-approved admin identity read verified separately.
[ ] Bot false positives, accessibility including keyboard/assistive technology, mobile retries, Turnstile blocked geographies, API rate-limit feedback.
[ ] Marketing consent distinct from application consent; no unsolicited email/subscription, investment recommendation, target price or performance guarantees.
[ ] Security operator verifies live secret key exists without disclosing its value.
Current HUMAN_PRIVACY_LEGAL_SIGNOFF=UNASSIGNED/NOT_COMPLETED.

## 5. FUTURE PRODUCTION SMOKE TEST RUNBOOK (not executed)
PRE: explicit GATE-D authorization, GATE-B/C completed, owner-supplied synthetic test address, privacy approval, bounded scheduled window, abort/oncall and rollback contact, code SHA and route, pre-test row count.
READ-ONLY: GET /decision-pack/ 200; frontend asset 200; OPTIONS /api/requests 204 with correct CORS; unauthenticated admin route denied/redirect; real Access authorized admin list 200, no secret recording.
MUTATION (ONLY AFTER GATE-D): consent true and correct policy version, valid Turnstile, unique idempotency header and `STAGING_TEST` forbidden on production? use `PRODUCTION_SYNTHETIC_TEST` marker; POST 201; retry identical request with new valid Turnstile and same idempotency key gives 200 original ID; same key different payload 409 if approved; verify only one logical private request, submission event, consent and active idempotency mapping; admin GET 200 and D1 row reconciliation. Keep production synthetic test record append-only, plan redaction/retention without arbitrary deletion.
NEGATIVE (prefer staging): missing consent and invalid token rejection, fail closed; do not repeatedly pressure production rate-limiter.
POST: compare records/billing/route version/latencies/error budget before and after; sign production smoke evidence hash and human approvals; if failure freeze further writes and record exact rollback choice.
NO PRODUCTION POST in preparation phase.

## 6. Evidence and report template
Report separate outcomes: PR_HEAD_VERIFIED, STAGING_REAL_ACCESS, STAGING_REAL_TURNSTILE, STAGING_FAULT_INJECTION, PROD_CONFIG_READ_ONLY, PROD_DB_BACKUP_RECOVERABILITY, HUMAN_PRIVACY_SIGNOFF, MIGRATION_0003_APPLIED_PROD, PROD_DEPLOY, PROD_SYNTHETIC_POST, LEAD_E2E, PUBLIC_CASE_PUBLISH.
At this preparatory point:
PR54_HEAD=35a4ac93fc9bd7dcd3f3b6571edebf098d334266
STAGING_REAL_ACCESS=PASS_AS_RECORDED
STAGING_REAL_TURNSTILE=PASS_LAYERED_AS_RECORDED
PRODUCTION_MIGRATION=NOT_AUTHORIZED
PRODUCTION_DEPLOYMENT=NOT_AUTHORIZED
PRODUCTION_POST=NOT_AUTHORIZED
HUMAN_PRIVACY_SIGNOFF=PENDING
PUBLIC_PILOT=HOLD
If repository head changes after this plan, re-review and update expected lock. A docs-only commit must not be mistaken for approval.

## 7. Additional checks required before owner release decision
Prove production restore drill, compatibility of historical clients/retries, Turnstile deployment secret and widget-hostname pairing, no credential value leaks, a tested operational rollback or forward-fix path. Get human/legal signoffs. No presumption these checks passed.
