# SE-IREN-P0-R3-FULL-FORM-LOCALIZATION-003 · implementation checkpoint
Date: 2026-10-27
Authorized scope: only shared intake form localization / language metadata, staging-only future deploy and browser acceptance. No production actions.
Input code SHA ec125e1b05564c0412a0d1bec960a4536f7fef17.
Changed `deploy/cloudflare-landing/commercial-upgrade.js` at commit `0c22fe33db7256073e8807388afda3b1b83f443c`: add EN-preserving exact-label locale mapping for zh-CN and es; localize field labels, hints, select option display strings, submission button, form intro and placeholders; set document lang and controls' lang on actual forms. Keep HTML API names and select option values unchanged; preserve consent policy version and privacy boundaries.
IMPORTANT: GitHub connector could edit source but cannot execute repository test runner or deploy Cloudflare Worker / real browser. Therefore SOURCE_PATCH_COMMITTED=YES, LOCAL_TESTS=NOT_RUN, STAGING_DEPLOY=NOT_RUN, REAL_BROWSER_ACCEPTANCE=NOT_RUN; should not label PASS.
## Required Codex validation prior to staging deployment
1. Lock current PR #54 head after docs commit. Check diff relative ec125e1... and ensure changes limited to localized display, accessibility and verification tests. Confirm `commercial-upgrade.js` module compiles and embedded COMMERCIAL_APP_JS_UPGRADE string remains syntactically valid.
2. Test all three `/verify/?lang=en|zh-CN|es` and any other form journeys `/context/` and `/decision-pack/`, including EN behavior preservation. Check actual DOM after JS executes, `document.documentElement.lang`, label/control associations, translated placeholders, help text, select labels and preserved option values, button/error/success copy. Audit all unmapped text (headings, success-boundary, form introduction, no JS/error fallback, navigation) and either localize or explicitly report scope gap; do not claim all-form full localization while visible text remains English.
3. Run entire existing Worker suite/focused tests, historical privacy/record guards, `git diff --check` and Wrangler staging dry-run. No fresh regressions; do not erase known baseline failure.
4. Verify exact staging D1 ID 65dc6680-0832-401d-8772-6a082b68673c, Worker `structevidence-commercial-staging`, limiter namespace 842054 and no production routes/bindings. Preserve version/restore point. Deploy only staging if local tests PASS and isolation verified.
5. Real browser EN/zh-CN/es: translated label/input pairs and aria language, consent, Turnstile, 201; separate controlled staging fixture 200 replay same ID and 409 conflict. D1 per new logical record 1 customer/request/event/consent/idempotency; append-only guards unchanged; Access admin read and CORS allow/deny (same-origin browser preflight remains N/A). Report changed D1 aggregate counts accurately; don't claim count stays 7 when inserting.
6. Update result MD/JSON append-only at new paths under docs/implementation; include exact SHA, Worker before/after, tests, localized all-visible-copy audit, staged browser findings, source/target hashes, status. Human legal review remains PENDING and production recoverability UNKNOWN. NO PR merge, production 0003, production Worker deploy/POST, public Pilot, social publication, billing or outreach.
## Current status
FORM_LOCALIZATION_SOURCE_PATCH=COMMITTED_UNTESTED
LOCAL_TESTS=NOT_EXECUTED
STAGING_DEPLOY=NOT_EXECUTED
BROWSER_E2E=NOT_EXECUTED
HUMAN_PRIVACY_LEGAL_SIGNOFF=PENDING
PRODUCTION_RECOVERABILITY=UNKNOWN
READY_FOR_OWNER_PRODUCTION_RELEASE=NO
