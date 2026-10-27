# SE-IREN-P0-R5-OWNER-PRODUCTION-RELEASE-DIRECTION-002
Date: 2026-10-27. Supersedes any draft suggestion to globally disable customer POST. Locked PR #54 source HEAD aade57e2f1abdc040dcd7e6878baa35459da0663. Owner expressly authorizes continuing the previously planned production release with normal customer intake submissions and accepts responsibility for product/service legal obligations. This does not assert legal compliance or supply a missing privacy signature.

## Correct interpretation of POST
- Public customer submission POST /api/requests is ALLOWED when hardened server is deployed, with required consent, Turnstile, idempotency, rate limiting, CUSTOMER_PRIVATE, NOT_AUTHORIZED, unassigned owner and append-only consent/event records. Do NOT add a global kill switch for this route.
- Separate /api/gaps/{gap_id}/challenge may remain under its existing controls; any public publication is a separate approval.
- Publishing case evidence, site status changes, social media posts or outbound communications requires exact reviewed content, source cutoff, human approval and release record; submission of customer information NEVER grants research/publication authorization.
- Existing admin review and status-change routes must retain Access and audit controls. Public-change action requires its existing explicit human publication gate.

## Production release preflight — required, not yet executed here
1. Verify PR #54 HEAD, latest main SHA, branch scope, tests, known legacy guard failures, and no accidental public customer data. Merge cannot be inferred from a documentation commit.
2. Production source bindings: Worker structevidence-commercial, D1 structurevidence-customer-cases ID aee10591-536a-47af-8ee0-957551ba2360, limiter namespace 842001, domain structevidence.com. Never use staging D1 ID 65dc6680-0832-401d-8772-6a082b68673c.
3. Production deploy config currently has placeholder TURNSTILE_SITE_KEY=CONFIGURE_TURNSTILE_SITE_KEY, and R1 reported no live TURNSTILE_SECRET_KEY. Before deployment configure real production widget for structevidence.com and www.structevidence.com, action public-intake, and Worker secret using secure credential interface. No values in GitHub.
4. D1 migration 0003 is PENDING and additive. Check current production snapshot/bookmark, database schema/aggregate baseline, emergency recovery plan and explicit owner residual-risk acceptance: production PITR restore cannot clone, production recoverability UNKNOWN, synthetic export/import PASS but not production RPO/RTO. Do not perform destructive in-place PITR.
5. Apply 0003 only after production preflight and decision to proceed; then deploy matching hardened Worker and EN/zh-CN/es frontend as one window. Capture version and deployment logs; ensure compatibility and ability to roll forward while preserving append-only history.
6. Postrelease smoke: read-only GET/OPTIONS/Access checks first; then controlled **owner-approved synthetic** production request, fresh real Turnstile, HTTP201, HTTP200 idempotent replay, HTTP409 conflict, private D1 readback and append-only checks. This bounded diagnostic POST is distinct from future normal client submissions. Never publish private test payload or customer IDs publicly.
7. Monitor errors, challenge fail-closed, rate-limits, source-privacy handling, and maintain explicit rollback/incident stop criteria. No automated release of evidence or social drafts.

## Governance
HUMAN_PRIVACY_LEGAL_SIGNOFF=PENDING; owner chooses to proceed at own accountability but does not convert PENDING to PASS.
PRODUCTION_RECOVERABILITY=UNKNOWN; owner acceptance of residual risk must be documented in restricted operations decision record, not claimed as verified recovery.
PUBLIC_CASE_STATUS_PUBLISH=HUMAN_GATE_REQUIRED.
SOCIAL_POST=HUMAN_GATE_REQUIRED / AUTO_PUBLISH_PAUSED.
RESEARCH_AUTHORIZATION_FROM_FORM=NO.
PAYMENT_AND_OUTREACH=HOLD unless separately approved.
CURRENT_PR54=Draft/unmerged. PROD_0003=NOT_APPLIED; PROD_WORKER=NOT_DEPLOYED; PROD_POST_COUNT=0 as last verified R1/R3 reporting; fresh Cloudflare status must be rechecked prior to release.
This document records release intent and precise gates; it does not claim a production deployment occurred.
