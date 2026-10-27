# SE-IREN-INTAKE-HARDENING-001 · v0.1
Status: IMPLEMENTATION DIRECTIVE, draft only; no prod deploy, prod POST, external outreach, live paid service or public pilot activation.
Date: 2026-10-26
BASE_MAIN_SHA=56f8e345ddfc697855c8eb9492dc0b49d24c6fcc
Private supporting audit: roalstoney-alt/se2cases Draft PR #3 HEAD d9ab0912befbc2095b3932d66b4fa26d86f6e808, source data/e2e/structurevidence-intake-audit-v0.1.json (private; do not mirror).
Responsible service: deploy/cloudflare-landing/worker.js, migrations, frontend commercial-upgrade.js, test/intake.test.js; preserve existing public website and API compatibility as far as possible.

## Verified defects and gates
1. Duplicate submissions create separate request IDs and events; idempotency absent. Implement v1 idempotency by client-generated stable token, schema validation and durable D1 unique constraints, scoped appropriately to avoid cross-user token leakage. Same key/same canonical request => same safe response/request_id with no duplicate event or customer; same key/different payload => 409 without leaking existing private data. Design storage/expiration and race/concurrent request tests. Do not dedupe merely by email, to allow legitimate distinct cases. Ensure migration works with existing production rows and has safe rollback.
2. Existing UI has acknowledgment, but public API does not enforce consent. Define explicit consent_version/consent_accepted or equivalent, verified on server before D1 mutation, with append-only receipt tied to request ID, policy version and timestamp. Never accept 'false' or missing consent. Avoid recording unnecessary sensitive information or making consent a blanket research authorization. Backward-compatibility/rollout: old UI may break if backend deployed alone; ship client/server together and test existing locale versions. Preserve privacy default CUSTOMER_PRIVATE and research_authorization_status NOT_AUTHORIZED.
3. Rate limiting and allowed Origin do not prove humans. Introduce Cloudflare Turnstile token at entry, verify token server-side via documented Siteverify, timeout/error behavior, token replay/expiry, local fake verifier, least privilege secret management. Do not commit production sitekey/secret. Include graceful accessibility/error guidance; analyze rather than assert risk must be zero. External non-browser requests may lack Origin; don't rely on Origin as authorization.
4. Unknown request JSON keys currently ignored. Explicitly reject unknown keys or version inputs with allowlist; coordinate UI fields and i18n variants. Validate types/length/privacy bounds, malformed JSON, oversized payload, unique keys, and injection-safe D1.
5. Maintain original request_events append-only constraint, administrator Access JWT allowlist, privacy handling and CORS. Do not leak private request IDs or details through anonymous GET.
6. Provide security tests: replay, simultaneous idempotency, different payload reused key, bad consent, missing/invalid/expired Turnstile, rate limits, CSRF/origin assumptions, API failure & no partial writes, DB migration rollback, admin read-after-write.
7. Run isolated local and if separately approved staging E2E; report exact tests and logs without customer data. Production POST=0 unless owner later separately authorizes a synthetic production test. No Cloudflare deployment or scheduled automation.

## Human-gated publication integration
IREN 2026-10-26 daily state SCAN_PARTIAL: accessible IR NO_QUALIFYING_CHANGE, overall RETRIEVAL_INCOMPLETE, SEC 403. New Q1 FY27 scheduled release notice for Nov 5 contains no results. If public content later approved, case status and source attribution must remain bounded. Public link and CTA cannot claim intake end-to-end works before independent production verification. Social posts require one real human reviewer and explicit owner approval of exact candidate content hash. This directive does not authorize publicity.

## Deliverable / report
- Update worker, frontend, D1 migrations and reproducible local tests in this isolated development branch and create only Draft PR targeting main.
- Frozen base SHA, exact HEAD, diff, new migration, test counts, backward-compatibility review, local/staging/production verification separately, Cloudflare deployment gate.
- P0 blockers for publication: reviewer, owner-approved exact hashes, verified production POST/admin D1 read, tested spam/accessibility and legal privacy copy. Do not assert these passed based on local fake DB.
- Keep private BMW/IREN evidence packets and review files in se2cases; never copy into public structurevidence.
- No auto merge/deploy/charge/contact/post.
