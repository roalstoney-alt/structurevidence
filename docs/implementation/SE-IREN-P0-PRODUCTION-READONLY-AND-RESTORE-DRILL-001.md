# SE-IREN-P0-PRODUCTION-READONLY-AND-RESTORE-DRILL-001 · v0.1
Status: REVIEW/PREFLIGHT ONLY. NO PRODUCTION MUTATION AUTHORIZED.
Written 2026-10-27; source PR #54 reviewed HEAD 14c55da406af4385ab0178aaf3b24e77ae539416; main 56f8e345ddfc697855c8eb9492dc0b49d24c6fcc.
Cloudflare admin actions, commands touching a production D1 binding, snapshots, exports, bookmarks, new D1 restore targets, migration application, Worker deploy, real POST, and cleanup require appropriate privileges and their exact corresponding authorization. No Cloudflare connector was accessible during this documentation task, so no direct production observation or restore exercise is claimed.

## R0 — invariant snapshot
Reconfirm PR #54 and main exact SHAs, staged change only, Cloudflare staging evidence unchanged. Baseline expected production D1 name structurevidence-customer-cases, database ID aee10591-536a-47af-8ee0-957551ba2360; Worker structevidence-commercial; rate-limit namespace 842001. Expected pending migration 0003 is prior reported observation only, not verified today.
Do not store secrets, auth headers or PII in a GitHub report. Use number/count summaries only, no customer rows.

## R1 — production READ-ONLY verification (permitted only with appropriate access; do not mistake this file for live results)
- Cloudflare deployment inventory: deployed Worker version, time, scripts/routes, env var NAMES, required secret NAMES, bindings (D1 ID and limiter), live Turnstile public sitekey configured? Expected hostnames/action: structevidence.com and www.structevidence.com, public-intake. Do not retrieve secret values.
- Production D1 remote migrations LIST only. Query schema read-only: sqlite_master DDL for five relevant entities as applicable; PRAGMA foreign_key_check or equivalent read-only check, indexes/triggers, and aggregate row counts before migration. Do not query private payloads.
- Confirm production has only previous migrations; verify 0003 remains unapplied.
- Read-only HTTP GET for /, /verify/, /context/, /decision-pack/, frontend JS; OPTIONS /api/requests; unauthenticated admin challenge/redirect; never authenticate to disclose records in public reports.
- Contrast exact production binding IDs vs staging d1 65dc6680-0832-401d-8772-6a082b68673c and distinct workers and rate limits.
- Evidence per check: UTC time, method, endpoint, safe status, scope, observed/blocked, actor authority, error if any. A tool failure is RETRIEVAL_INCOMPLETE, not PASS.

## R2 — controlled backup/recovery DRILL, separate authorization required to create snapshot or restore resources
A backup alone is not evidence of recoverability. The operator must:
1. Select supported Cloudflare D1 backup/PITR approach documented for this exact production database and verify coverage, RPO boundary, restore target, and legal/retention permission.
2. Require explicit owner approval before any backup/export/creation step. Exporting production customer data is sensitive; use Cloudflare native restore to a separately access-controlled isolated database where possible, avoid workstation/local download, public logs and repo attachments. Do not expose real customer rows to staging.
3. Restore to a purpose-built isolated private recovery target, not the existing staging D1. Protect it with strict access, no HTTP worker routes, no public records, time-limited retention.
4. Check schema versions, safe aggregate row counts, foreign keys and trigger definitions; never publish row-level identifiers. Record snapshot identifier privately, sanitized operation receipt, exact start/end UTC, observed duration, restore errors and data gap, actual measured RPO/RTO.
5. Test *read-only* consistency in restored environment and leave restored data private. Destroy/retain only under separately approved retention procedure; document cleanup outcome, never claim deletion unobserved.
6. Never restore the live production D1 backwards to 'roll back' 0003. After first production intake under 0003, preserve append-only consent/events; repair with a forward-compatible Worker.

## R3 — privacy checklist / human gate
Human reviewer needed (identity and evidence private, not committed to public repo):
- Operator/controller, applicable notices per locality, privacy policy URL and exact hash, processor/storage description, retention and erasure obligations, opt-in and research authorization distinction, marketing consent separately.
- EN/zh-CN/es frontend and shared form text, consent version SE-CUSTOMER-PRIVACY-v1; links actual and working.
- Restricted private intake storage; Access API/UI audience separation, least privilege/offboarding, no private details in logs/analytics; security policy.
- Turnstile accessibility, false-positive fallback, mobile, rate-limit messaging; verify proper sitekey/hostname/action and required secret without printing.
- Reviewer result APPROVED / REJECTED / PENDING, timestamp, scope, content hashes. Automated PASS != human approval. Reviewer remains UNASSIGNED until real signoff.

## R4 — future production deploy playbook (NOT AUTHORIZED NOW)
Gate B remote D1 migration 0003 only after proved backup/restorability and owner written approval.
Gate C Worker + frontend combined release only after gate B, provisioned real Turnstile config, and reviewed compat/abort.
Gate D a single scoped synthetic production request + admin D1 read requires separate explicit approval after C.
Record read-only baseline first. Never deploy via docs PR merging unless exact linkage, deploy hooks and effects rechecked.

## Evidence JSON template
{
  "project": "SE-IREN-P0-PRODUCTION-READONLY-AND-RESTORE-DRILL-001",
  "reviewed_pr_head": "14c55da406af4385ab0178aaf3b24e77ae539416",
  "pr_54_merged": false,
  "production_readonly_observation": "NOT_PERFORMED",
  "production_d1_migration_0003": "NOT_AUTHORIZED",
  "recovery_drill": "NOT_AUTHORIZED_NOT_PERFORMED",
  "production_backup_recoverability": "UNKNOWN",
  "human_privacy_review": "PENDING",
  "real_turnstile_production_config": "UNVERIFIED",
  "production_post_count": 0,
  "production_worker_deployed": false,
  "approval_gates": {"merge":false,"migration":false,"deployment":false,"synthetic_post":false},
  "ready_for_owner_production_release": false
}

## STOP conditions
Missing permissions; uncertain account/database ID; production-vs-staging binding ambiguity; backups requiring raw customer export outside authorized restricted cloud; no secure recovery target; unchanged/unknown secret settings; failed read-only check; changes in PR HEAD after review; any report that implies unperformed operations succeeded.
Report blockers and stop. Do not treat inability to invoke Cloudflare as a failed restore drill or as approval to bypass it.
