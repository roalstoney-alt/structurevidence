# SE-IREN-P0-R3-PRODUCTION-RISK-REVIEW-001
Date: 2026-10-27 | Type: Owner decision dossier / no production mutation
Evidence-lock PR #54 HEAD `820af418bef7d6eac237bde84736bac65756cbd9`, base main `56f8e345ddfc697855c8eb9492dc0b49d24c6fcc`.
Status: REVIEW_COMPLETE; HUMAN_SIGNOFF_PENDING; GO/NO-GO=NO_GO_PENDING_GATES.
The report records repository documents and prior operator-reported, separately categorized evidence. It does not independently certify Cloudflare account live state or legal compliance.

## 1. Evidence and constraints
- Staging: real Access authenticated admin GET 200 and two valid real Turnstile submissions HTTP 201; invalid Turnstile 400; deterministic fault injection tests tracked separately. User records in staging synthetic and private.
- Production R0/R1 as observed: worker version `d2525a27-12bc-49a6-9328-f11af90ea7d8`, 100% traffic; D1 source `structurevidence-customer-cases`, 3 customers / 3 requests / 5 events; migration 0003 pending; old OPTIONS allows `content-type` but not `idempotency-key`; current production Turnstile key and secret absent; DDL read blocked SQLITE_AUTH; full control-plane route listing blocked. No production POST authorized.
- R2 Cloudflare-native PITR: bookmark-read PASS, isolate-clone unsupported; no in-place restore allowed, recoverability UNKNOWN.
- R2 fully synthetic: two new isolated APAC D1 instances, exported 13,825-byte unmodified SQL to independent target, five intake tables 3/3/5/3/3, migration ledger 0001-0003, source/target fixture and schema hashes match, FK errors 0, four append-only updates/deletes rejected. Synthetic integrity-ready 231.039s; synthetic static-fixture RPO zero, NOT applicable to production. Synthetic resources and export deleted as reported. Production data never exported.
- Frozen boundary: `We can be wrong. We must remain auditable.` Consent intake != research authorization != publication permission. Customer private never published in CML/case/social corpus.
- Status must remain `PRODUCTION_RECOVERABILITY=UNKNOWN`, `READY_FOR_OWNER_PRODUCTION_RELEASE=NO`.

## 2. Production-data recovery risk assessment
| ID | Risk / trigger | Impact | Evidence state | Owner action and gate |
|---|---|---|---|---|
| RR-01 | PITR restores in place only, cannot rehearse private clone | Catastrophic data loss if run on live D1 | SUPPORTED for capability; live restoration NOT_TESTED | Emergency-only under separate break-glass approval, record original bookmark and accepted writes; NEVER as routine rollback |
| RR-02 | SQL export/import of real rows to a private database | Confidentiality, data residency, retention and access-control risk | UNKNOWN for production path; synthetic PASS | Separate owner authorization and privacy/DPA determination; private cloud-only chain of custody, no local downloads or GitHub |
| RR-03 | Export may block source traffic | Outage/latency during live intake | KNOWN_POTENTIAL; production impact UNMEASURED | Measure and approve maintenance window and abort criterion; synthetic duration must not be extrapolated |
| RR-04 | No independently verified production snapshot restoration | Unknown production RPO/RTO | UNKNOWN | Do not imply production restore assurance; establish service-level risk appetite in written owner decision |
| RR-05 | Migration 0003 before paired client rollout | Old/new contract mismatch and customer intake errors | SUPPORTED by implementation | Version-paired change window after gated migration, no standalone frontend/server rollout |
| RR-06 | Current production old Worker lacks Turnstile and Idempotency-Key CORS | Existing release cannot support hardened intake until configured/deployed | OBSERVED_IN_R1 | Confirm new prospective preflight in staging, secure production site key/secret/hostnames/action before release |
| RR-07 | Append-only and deletion/erasure conflict | Regulatory requests or retention noncompliance | HUMAN_LEGAL_REVIEW_REQUIRED | Preserve integrity but provide privacy-safe retention/deletion strategy; counsel/owner signoff required |
| RR-08 | Personal data or auth secrets in reports/exports | Disclosure | NO_ISSUE_OBSERVED_IN_REDACTED_REPORTS; broad assertion not verified | Restricted logging, scoped retention, no raw rows in public repo; private access audit |
| RR-09 | Public case/social claims inferred from customer applications | False authorization and potentially misleading claims | NOT_AUTHORIZED | Separate evidence reviewer, source/provenance and publication gates, no automatic marketing launch |

Risk acceptance cannot promote UNKNOWN to PASS. The fact there were three production requests in R1 aggregate does not reduce legal obligations for those people.

## 3. Human privacy and legal signoff checklist (UNSIGNED)
All reviewer names, consent policy originals, approval timestamps and comments belong in restricted operations store, NOT public GitHub.
- [ ] Identify actual controller/operator and applicable jurisdictions, processors, storage locations, rights-request contact and privacy notice URLs; verify accessible on current EN/zh-CN/es routes.
- [ ] Verify server consent `SE-CUSTOMER-PRIVACY-v1` matches user-visible form in all entry journeys; no silent consent; policy revision and proof of acceptance aligned.
- [ ] Distinguish submission intake vs research vs publication vs marketing outreach; no implied permissions; user-facing scope and withdrawal/rights pathways.
- [ ] Approve minimization, retention schedule for customers/requests/events/consent/idempotency, encrypted restricted backups, deletion/legal hold treatment; irreversible append-only model needs documented rights/erasure reconciliation.
- [ ] Verify access least privilege, separate API/UI Cloudflare Access audiences, admin allowlists and removal procedures; reject JWT/cookie/OTP logging.
- [ ] Validate anti-bot failure handling, accessibility/keyboard path, mobile languages, retry semantics and support process if Turnstile unavailable.
- [ ] Review incident response, data breach procedure, log retention, account ownership and D1 regional controls.
- [ ] Human privacy/legal reviewer privately signs named version+hash, disposition APPROVED/REJECTED/PENDING and date.
Result at time of report: `HUMAN_PRIVACY_LEGAL_SIGNOFF=PENDING`. AI/test PASS is not a substitute.

## 4. Owner GO/NO-GO matrix
| Gate | Criteria | Result 2026-10-27 |
|---|---|---|
| G0 version lock | HEAD pinned, PR Draft, production main unmodified | PASS_AS_OF_REVIEW |
| G1 staging behavior | Access GET 200, real Turnstile, D1/idempotency/consent, 3 language entry tests | PASS_AS_RECORDED |
| G2 disaster recovery | Native clone impossible; synthetic export/import proven; production RTO/RPO measured? | PARTIAL / UNKNOWN |
| G3 schema rollback / compatibility | 0003 additive, append-only, no DROP after accepted receipt; paired deploy sequence | DESIGN_REVIEWED / PROD_UNTESTED |
| G4 production Turnstile & CORS | Live secrets and expected hostnames/action, browser OPTIONS includes idempotency-key | NOT_CONFIGURED / NOT_RELEASED |
| G5 privacy/legal signoff | Named human reviewer signs | PENDING |
| G6 operations | Restore policy, monitoring thresholds, abort plan, secrets, rollback operator, production access permissions and maintenance change window | PENDING |
| G7 distinct owner approvals | Merge / migration / Worker deploy / scoped production synthetic POST | ALL_NOT_AUTHORIZED |
| G8 IREN public communication | source state frozen, independent reviewer and exact-copy approval | HOLD |
DECISION=`NO_GO_PENDING_GATES`.
A future owner can explicitly accept residual risk of **unproven production restore** in an auditable waiver, but no such acceptance has been granted. Even such waiver cannot replace privacy approval, deployment checks or independent actions.

## 5. Recommended no-write work sequence
A. Perform prospective staging real browser preflight `Access-Control-Request-Headers: content-type,idempotency-key` and confirm new Worker response. Repeat with 3 language forms. This is NOT production CORS patch.
B. Assign a real, appropriate privacy/legal reviewer and complete checklist privately; publish only sanitized disposition and policy hash.
C. Choose a production data continuity posture: (i) separately authorize confidential export-and-private-restore risk assessment, not an actual export; or (ii) write an explicit residual-risk waiver and emergency in-place PITR break-glass policy, acknowledging recoverability remains UNKNOWN. A synthetic round trip is neither.
D. Operator constructs deployment window with live Turnstile configuration, pre-migration read-only totals, DB safety and Worker+front paired release; verify monitored rollback to old compatible frontend/Worker without dropping accepted audit rows.
E. Only after G0-G6 closure should owner consider distinct authorizations for merge, D1 0003, Worker deploy, and controlled synthetic production POST, in that order. Public pilot and marketing remain separate.

## 6. Report summary (machine-readable facts reflected in this memo)
PR54_REVIEWED_HEAD=820af418bef7d6eac237bde84736bac65756cbd9
R3_DOCUMENT_REVIEW=COMPLETE
HUMAN_PRIVACY_LEGAL_SIGNOFF=PENDING
PRODUCTION_RECOVERABILITY=UNKNOWN
PRODUCTION_RPO=NOT_MEASURED
PRODUCTION_RTO=NOT_MEASURED
PRODUCTION_RELEASE_DECISION=NO_GO_PENDING_GATES
PRODUCTION_EXPORT=NOT_AUTHORIZED_NOT_RUN
PRODUCTION_MIGRATION_0003=NOT_AUTHORIZED_NOT_APPLIED
PRODUCTION_WORKER_DEPLOY=NOT_AUTHORIZED_NOT_RUN
PRODUCTION_POST=0
PR54_MERGE=NOT_AUTHORIZED
PUBLIC_PILOT=HOLD
