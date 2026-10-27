# SE-IREN-P0-R4-HUMAN-PRIVACY-REVIEW-001 · Human review package v0.1
Review cutoff: 2026-10-27. Locked source PR #54 HEAD `75b4c82bb27a0c2fd6172a4835e1cfe872f819a5`. NO LEGAL SIGNOFF REPRESENTED.
This public-safe artifact records review prompts, exact frozen consent source text, schema-derived categories and open questions. Actual human identity, sensitive operational findings, actual request data and signed records must be kept exclusively in a restricted evidence system.

## A. EN / zh-CN / ES consent comparison — exact source text
Source: `deploy/cloudflare-landing/commercial-upgrade.js` `INTAKE_COPY` at locked HEAD.
- EN: "I understand that this submission remains customer-private, does not authorize research, and will not be published without separate written authorization."
- zh-CN: "我理解：本次提交内容将保持为客户私有信息；本次提交不授权开展研究；未经另行书面授权，提交内容不会公开发布。"
- es: "Entiendo que este envío permanecerá privado para el cliente, no autoriza la realización de ninguna investigación y no se publicará sin una autorización escrita independiente."

Core equivalence grid:
| Meaning | EN | zh-CN | ES | Signoff |
|---|---|---|---|---|
| Customer submitted content remains private | present | present | present | human linguistic/legal review PENDING |
| Does not authorize research | present | present | present | PENDING |
| Publication requires separate written authorization | present | present | present | PENDING |
| Consent purpose is intake acknowledgement only | code-supported; verify notice in context | code-supported; verify context | code-supported; verify context | PENDING |

The stable server version is `SE-CUSTOMER-PRIVACY-v1`; the actual page content and associated policy URLs must be archived by reviewer with hashes. The page's headline/marketing body outside intake remains partly English and Cloudflare-hosted Turnstile may display English. Do not represent the commercial site as fully localized.

## B. Source-derived data inventory and retention mapping
Sources: `migrations/0001_customer_intake.sql`, `0003_intake_hardening.sql`, frontend intake payload, Worker `submitRequest`.
| Record class | Fields / sensitivity supported by schema | Documented enforcement | Retention/legal unknowns for human reviewer |
|---|---|---|---|
| customers | customer_id; contact_name; email; company; created_at, updated_at; directly identifying | restricted CUSTOMER_CASES_DB | retention term, correction/erasure handling, lawful basis, contact channel UNSET |
| requests | request_id, customer_id, decision, claim_or_question, technical_object, dependency, alternative, deadline, case_reference, requested_output; private commercial context; state fields | privacy_class CUSTOMER_PRIVATE; research_authorization_status NOT_AUTHORIZED; human_owner initially NULL | free-text minimization, prohibited submissions, closure/deletion or redaction rules, lifecycle term UNSET |
| request_events | event_id, request_id, event_type, state transitions, actor, note, event_at | UPDATE/DELETE prohibited by trigger | retention and privacy/erasure vs append-only reconciliation, note minimization UNSET |
| request_consent_receipts | receipt_id, request_id, consent_version, accepted=1, accepted_at, actor CUSTOMER | exact version; append-only UPDATE/DELETE guard | proof duration, rights requests, policy archiving, audit obligations UNSET |
| request_idempotency | SHA-256 of normalized scope, key and fingerprint, request_id, created/expires_at | raw idempotency key not stored; TTL default 86400 seconds | whether expired rows purged automatically, minimum/maximum actual retention, legal basis and cryptographic linkage UNVERIFIED |
| Cloudflare Access / Turnstile / Worker logging | request metadata, access identity and security-check processing may exist outside D1 | admin API/UI audience separation tested; secrets/tokens excluded from public reports | subprocessors, IP data/telemetry, service retention, data residency, contractual DPA and transfers require external account-specific review |

**Important distinction:** idempotency expiration is a validity window; it does **not by itself prove automatic record deletion**. Do not infer indefinite retention simply because an append-only trigger exists; identify actual policies and table-level law/rights handling before signoff.

## C. Rights request and deletion handling — review-required procedure
1. Publish verified privacy contact and authenticated intake for access/correction/deletion/objection where applicable; no actual legal mailbox or retention SLA is evidenced by the source materials.
2. Intake request privately; verify requester identity proportionately, protect against account enumeration. Log legal jurisdiction, scope and due date only in restricted system.
3. Locate records across customers, requests, linked append-only events, consent receipts, idempotency mappings, Cloudflare security logs and any email fallback records. Do not claim encrypted backup, processor or analytics deletion until independently verified.
4. Determine legal retention obligations and allowed redaction/anonymization method with responsible human counsel. Triggers forbid direct UPDATE/DELETE for event and consent; do not bypass for convenience. If irreconcilable, mark blocker, design an auditable rights-compliant evolution separately and do not deploy.
5. Respond and document actual resolution with restricted record ID, exact dispositions and legal reasoning, public-safe result status only. Define appeal/correction channel and breach escalation.

## D. Cloudflare boundary inventory / questions to verify
Staging and production are isolated Worker/D1 configurations. Cloudflare D1 is the storage processor of requests, and Access is the protected admin gate; Turnstile verifies submitted challenges server-side. Existing isolated staging tests evidence application behavior, not Cloudflare's full contractual terms.
Human reviewer must obtain, using account-specific approved sources: DPA and subprocessors, controller/processor roles, residency and transfer locations (APAC D1 is NOT proof that all processing/logging remains APAC), Access identity provider and token handling, Turnstile information processing, network/security logs and retention, incident notification terms, production backup/PITR access and retention, and deletion mechanism for ephemeral exports.
No Cloudflare secret, cookie, raw identity, real client data, private bookmark or DPA attachment may be committed publicly.

## E. Mandatory human gates and restricted signature packet
Roles: responsible data controller/owner, qualified privacy/legal reviewer, qualified zh-CN and ES reviewers, independent must-fix reviewer. A person may fill multiple roles only if independent review requirement is still satisfied and recorded.
Each reviewer records privately:
- REVIEW_CASE_ID; ROLE/QUALIFICATION; IDENTITY; DATE_UTC; JURISDICTION; SOURCE_PR_HEAD and DOCUMENT hashes
- exact policy versions/URLs, notices, evidence consulted, findings, severity, remediation, privacy data map and retention decisions
- residual unknowns including `PRODUCTION_RECOVERABILITY=UNKNOWN`, data subject rights treatment, controller identity, logging/Cloudflare processing
- APPROVE / CONDITIONALLY_APPROVE / REJECT decision, required changes, signature/time, separate approver for production release
Only public-safe signature reference/hash plus decision status may later be appended to PR. Never insert the reviewer's identity or signed payload in GitHub.

## F. Owner decision table and must-fix blockers
| Item | Evidence state | Release decision |
|---|---|---|
| Three-language full intake form browser tests | STAGING_PASS_AS_RECORDED | engineering gate closed |
| Human consent semantic equivalence | NOT_SIGNED | NO-GO |
| Controller/contact, policy and rights procedures | NOT_SIGNED / NOT_ESTABLISHED | NO-GO |
| Data retention and append-only/erasure treatment | NOT_DECIDED | NO-GO |
| Cloudflare processing/DPA/account-specific residency | NOT_VERIFIED | NO-GO |
| Real human privacy/legal approval | PENDING | NO-GO |
| Production data recoverability | UNKNOWN | separate owner residual-risk decision; no RPO/RTO claim |
| Production Turnstile/CORS/migration/deploy | NOT_AUTHORIZED | NO-GO |
| Public IREN case/social posts and outbound | NOT_AUTHORIZED | HOLD |

## G. Execution restrictions and output schema
`R4_DOCUMENT_PACKAGE=PREPARED`
`HUMAN_PRIVACY_LEGAL_SIGNOFF=PENDING`
`PRODUCTION_RECOVERABILITY=UNKNOWN`
`READY_FOR_OWNER_PRODUCTION_RELEASE=NO`
`PR54_DRAFT=YES`
`PRODUCTION_MIGRATION_0003=NOT_APPLIED`
`PRODUCTION_WORKER_DEPLOYMENT=NO`
`PRODUCTION_POST_COUNT=0`
`PUBLIC_PILOT=HOLD`
A future review can append a new decision record, never overwrite an earlier rejection/unknown. Any change to localized consent or Worker source requires new hashes and review of the changed scope.
