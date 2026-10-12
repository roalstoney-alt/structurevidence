# Data-flow inventory

| Surface | Data | Necessity / purpose | Recipient / location | Retention principle | Access / cleanup | Status |
|---|---|---|---|---|---|---|
| Static `.org` hosting | ordinary HTTP metadata; public evidence pages | deliver public research | Cloudflare/GitHub configuration as deployed | platform/config facts not fully verified | platform controls | NEEDS_OPERATOR_FACTS |
| Commercial Worker | contact, organization, decision/claim, optional bounded context | human scoping and service administration | Worker then bound D1 | retain only while reasonably needed for scoping, contract, accounting, dispute and legal duties; schedule not yet confirmed | Access-protected admin; request handling process | PARTLY_VERIFIED |
| D1 | customer/request rows, notice acknowledgement, private context, minimal event trail | operate intake and auditable authorization states | Cloudflare D1 binding | production schedule and backup behavior need operator confirmation | JWT audience + allowlist; controlled lifecycle plan required | NEEDS_OPERATOR_FACTS |
| Access | administrator identity/token claims | protect admin routes | Cloudflare Access | provider configuration | allowlist/audience review and offboarding | CONFIG_PRESENT_NOT_PRODUCTION_VERIFIED |
| Logs/rate limiting | error metadata; transient client key for rate limiting | security and abuse control | Worker runtime | no full customer text should be logged; provider retention unknown | provider/operator controls | NEEDS_OPERATOR_FACTS |
| Email | support and fallback correspondence | support, complaints and scoping continuity | configured mail provider | mailbox retention and processors unknown | mailbox access/cleanup | NEEDS_OPERATOR_FACTS |
| Payment records | invoice/transaction/accounting references | settlement and accounting | operator/payment rails | applicable accounting/legal period | operator accounting process | NEEDS_OPERATOR_FACTS |
| AI/Agent | only task-specific material explicitly supplied by authorized operator | assist research/operations | actual providers/configuration not established in repository | do not claim no training or a location until verified | minimize, isolate, human review | NEEDS_OPERATOR_FACTS |
| Backups | possible D1, host, mailbox or repository backups | resilience/audit | provider-specific | schedule/deletion propagation unknown | recovery and deletion procedures needed | NEEDS_OPERATOR_FACTS |
| Evidence challenges | challenge text, source URL, attribution preference, hashed rate-limit key | human review of defined gaps | D1/admin review | governed separately by Vortex controls | Access-protected review; append-only public state | VERIFIED_IN_CODE_NOT_PRODUCTION_FACT |

Initial scoping does not require patient records, identity documents, passwords, private keys, full customer databases, or unauthorized trade secrets. Obvious unsuitable material is routed for human isolation; no regex or automated filter is claimed to detect every sensitive item.

This inventory is a technical draft, not a representation that unverified provider, location, retention, deletion or AI-use facts have been confirmed.

## Intake compatibility boundary

The form and API change are designed for one atomic Worker release. The legacy unversioned client is accepted only before that cut-over; after cut-over it receives a validation error and must reload the current form. No supported external API client was identified in the repository. This fail-closed transition is intentional because silently accepting an unacknowledged notice would defeat the control.
