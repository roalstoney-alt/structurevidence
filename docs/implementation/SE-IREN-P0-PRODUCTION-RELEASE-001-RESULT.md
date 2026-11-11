# SE-IREN-P0-PRODUCTION-RELEASE-001 · production result

Completed: 2026-10-28 02:33 SGT / 2026-10-27T18:33:19Z

Repository: `roalstoney-alt/structurevidence`

This is an append-only, public-safe release record. It contains no customer row,
synthetic request ID, email address, Turnstile key or token, Access credential,
JWT, OTP, raw Time Travel bookmark, administrator identity, or private request
payload.

## Frozen source and authorization

- Locked PR #54 HEAD: `3615333d03b7df995265b3d58f66b94a60e2bb54`
- Pre-merge main: `56f8e345ddfc697855c8eb9492dc0b49d24c6fcc`
- Merge commit: `a3264420664a5c471fbc33829fc203429ca0f814`
- Merge time: `2026-10-27T19:48:35+08:00`
- Owner production-release directive SHA-256:
  `d21a1779ed5eea4c6a991635a43ac6c8b3b89fa0fcc5e344719c59ab151c1990`
- The directive preserves `PRODUCTION_RECOVERABILITY=UNKNOWN` and
  `HUMAN_PRIVACY_LEGAL_SIGNOFF=PENDING`; neither is represented as PASS.

PR #54 was verified at the locked HEAD, marked ready, and merged with the
repository's merge-commit convention. No GitHub workflow deploys this Worker on
merge, so merge did not bypass the migration or Turnstile sequence.

## Production preflight

- Worker: `structevidence-commercial`
- Domains: `structevidence.com`, `www.structevidence.com`
- D1: `structurevidence-customer-cases`
- Verified D1 ID: `aee10591-536a-47af-8ee0-957551ba2360`
- Verified production rate-limit namespace: `842001`
- Region observed: APAC / SIN
- Pre-migration aggregate counts: customers 3, requests 3, request events 5
- Pre-migration database size: 147456 bytes
- Foreign-key violations: 0
- Recovery bookmark available at `2026-10-27T11:51:03.950Z`; raw value was
  suppressed. Redacted response fingerprint:
  `4981475a95ba698a4ed42315e82b73fa1e9a166aee21510bb648b4596760bb11`
- Production RPO/RTO remain unmeasured. Native Time Travel still cannot prove an
  isolated production restore, and no in-place restore was attempted.

The production Turnstile widget is Managed, has exactly the two production
hostnames, and uses action `public-intake`. The Worker secret exists under the
expected secret name. No key value is committed or repeated here.

## Migration and deployment

Migration `0003_intake_hardening.sql` was applied only to the production D1
above. Wrangler executed eight additive DDL commands. Post-migration checks
confirmed:

- `request_idempotency` and `request_consent_receipts` exist;
- both required secondary indexes exist;
- both new foreign keys reference `requests.request_id`;
- the two existing request-event and two new consent append-only triggers exist;
- old aggregate counts remained 3 customers / 3 requests / 5 request events;
- both new tables were empty immediately after migration;
- no migration remains pending and `PRAGMA foreign_key_check` is empty.

Worker version history for this release:

- Last pre-release application version:
  `d2525a27-12bc-49a6-9328-f11af90ea7d8`
- Turnstile configuration-only version before the code deploy:
  `817ba11d-37b1-4ef9-8f5c-7f4ac232ea3a`
- Hardened application version, 100% traffic:
  `56dd16eb-4dbf-43e1-8724-2927a60652f2`
- Deployment time: `2026-10-27T11:55:49.159Z`
- Source main SHA: `a3264420664a5c471fbc33829fc203429ca0f814`
- Tag: `se-iren-p0-a326442`

The first upload attempt failed before upload because the clean release worktree
did not yet expose the already locked `jose` dependency. No version or traffic
changed. The dependency was linked in the disposable release worktree, the exact
merged-main bundle passed dry-run, and only then was the successful deployment
performed.

Wrangler warned that the no-value release config differed from Dashboard
variables. Live checks proved `keep_vars` preserved them: trying to re-add the
same names was rejected as duplicate and was cancelled without deployment. The
live EN, zh-CN and ES pages all contain a non-placeholder Turnstile site key,
and the production API passed real CORS and submission checks.

Source and live asset hashes:

- Merged `worker.js` SHA-256:
  `8a01b397a92bcf9a6183fc79f6ca7c4f1ef54ed576c157f3c4368969e8f309bd`
- Merged `commercial-upgrade.js` SHA-256:
  `4f9af20c5c36b8d47090cc14c68266c7ea529bc78d549f0709726f0b5c074ada`
- Live `/assets/app.js` SHA-256:
  `429b1c6fc476ae8cf9bd18c895d2cb890785a2f9141e6a40a75df8708fbc7953`

## Read-only production smoke

- `/`: HTTP 200
- `/verify/`: HTTP 200
- `/context/`: HTTP 200
- `/decision-pack/`: HTTP 200
- `/assets/app.js`: HTTP 200
- OPTIONS `/api/requests`: HTTP 204
- Allow origin: exact production origin
- Allow methods: `POST, OPTIONS`
- Allow headers: `content-type, idempotency-key`
- Unauthenticated `/api/admin/requests`: HTTP 302 to Cloudflare Access
- Authorized Access read: PASS; the synthetic record was visible after
  authentication. No private response content is retained in this report.

Three-language form checks passed for EN, Simplified Chinese and Spanish. Each
response has the correct `html lang`, localized Consent boundary, a real
non-placeholder Turnstile key, and the frozen no-research/no-publication meaning.

Live response hashes:

- EN Verify:
  `412755a531b8842fce240606612e34ea17900d5b7252f37d05d08e7a45f23530`
- zh-CN Context:
  `61a7c6a69723777d99491a1ace9f63bca172fb202f5af8f0ea9ee6d610ea30ad`
- ES Decision Pack:
  `c91a660cea42c6e747aea2e8c826e596e59f38ce36646d673c37e37123464713`

## Controlled synthetic submission

One legitimate production form submission completed after real human Turnstile
verification. The success UI displayed `SUBMITTED`, `CUSTOMER_PRIVATE` and
`NOT_AUTHORIZED`. Aggregate-only D1 verification proved exactly:

- target request: 1
- `REQUEST_SUBMITTED` event: 1
- `SE-CUSTOMER-PRIVACY-v1` consent receipt: 1
- active hashed idempotency mapping: 1
- human owner: NULL

Final production aggregates are customers 4, requests 4, request events 6,
consent receipts 1 and idempotency mappings 1. Foreign-key violations remain 0.
No customer-originated row was exported or copied.

No-op UPDATE attempts against the synthetic request event and consent receipt
were both rejected with `SQLITE_CONSTRAINT_TRIGGER`. `APPEND_ONLY=PASS`.

The browser success view and new D1 relationship prove a new accepted logical
submission, but the direct transport status was not captured at submission
time. Therefore this record does not relabel it as an independently observed
HTTP 201.

The client intentionally deletes the raw idempotency key after success, and D1
stores only its SHA-256 digest. The raw key was not captured before the human
submission and cannot be recovered safely. Creating a second logical production
record would violate the authorized single-record boundary. Consequently:

- `FIRST_SUBMISSION = ACCEPTED_NEW_WRITE; DIRECT_HTTP_STATUS_NOT_CAPTURED`
- `REPLAY_SAME_KEY_SAME_PAYLOAD = NOT_OBSERVED_IN_PRODUCTION`
- `REPLAY_SAME_REQUEST_ID = NOT_OBSERVED_IN_PRODUCTION`
- `SAME_KEY_DIFFERENT_PAYLOAD = NOT_OBSERVED_IN_PRODUCTION`
- `PRODUCTION_SYNTHETIC_POST = PARTIAL`
- `IDEMPOTENCY = PARTIAL`

Automated and Staging tests still prove deterministic 201/200/409 behavior, but
they are not substituted for the missing production transport observations.

## Regression and governance result

- Worker/localization/security suite: 75/75 PASS
- Production bundle dry-run from merged main: PASS
- Public record drift: PASS
- Internal links: 0 broken / 0 orphan
- Repository Python suite: 41 tests / 11 known pre-existing failures
- New regression count: 0
- Historical evidence, canonical URLs, evidence IDs, state IDs, DOI values,
  conclusions and public-brand policy: unchanged

Final release fields:

```text
PROJECT = SE-IREN-P0-PRODUCTION-RELEASE-001
LOCKED_HEAD_SHA = 3615333d03b7df995265b3d58f66b94a60e2bb54
MAIN_MERGE_SHA = a3264420664a5c471fbc33829fc203429ca0f814
PRODUCTION_WORKER_BEFORE = 817ba11d-37b1-4ef9-8f5c-7f4ac232ea3a
PRODUCTION_WORKER_AFTER = 56dd16eb-4dbf-43e1-8724-2927a60652f2
PRODUCTION_DEPLOYMENT_ID = 56dd16eb-4dbf-43e1-8724-2927a60652f2
PRODUCTION_DEPLOYMENT_TIME = 2026-10-27T11:55:49.159Z
TURNSTILE_PRODUCTION = PASS
D1_MIGRATION_0003 = PASS
THREE_LANGUAGE_FRONTEND = PASS
PRODUCTION_READONLY_SMOKE = PASS
PRODUCTION_SYNTHETIC_POST = PARTIAL
IDEMPOTENCY = PARTIAL
APPEND_ONLY = PASS
ADMIN_ACCESS = PASS
HISTORICAL_RECORD_DRIFT = PASS
NEW_REGRESSION_COUNT = 0
PRODUCTION_RECOVERABILITY = UNKNOWN
HUMAN_PRIVACY_LEGAL_SIGNOFF = PENDING
CUSTOMER_INTAKE_ENABLED = YES
PUBLIC_CASE_AUTO_PUBLISH = NO
SOCIAL_AUTO_PUBLISH = NO
OUTREACH_STARTED = NO
CHARGING_STARTED = NO
READY_FOR_CUSTOMER_INTAKE = NO
PUBLIC_PILOT_STARTED = NO
```

`CUSTOMER_INTAKE_ENABLED=YES` describes observed live behavior. The stricter
`READY_FOR_CUSTOMER_INTAKE=NO` preserves the release directive's completion
standard until a separately authorized, capture-before-submit production
exercise observes the same-key HTTP 200 replay and different-payload HTTP 409
without creating more than one logical request.
