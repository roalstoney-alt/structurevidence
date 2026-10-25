# SE-DUAL-SITE-UPGRADE-002 / Phase C — Citable Decision Conditions
Status: DEVELOPMENT_AUTHORIZED_ONLY; PR merge and production deployment require separate human approval.
BASELINE_MAIN_SHA=bbced95da00ed259e942aa63ebd89d93f70c54a0
Previous phase: PR #49 MERGED. Evidence determinations unchanged.

## Product purpose
Make evidence boundaries usable as decision conditions in human-controlled investment, procurement, qualification and technical deployment workflows. StructEvidence reports what is evidenced, unknown and temporally bounded—not what the client must decide.

## Initial deliverable
Implement deterministic and copyable Decision Conditions for existing 800VDC OEG-CML-001 and OEG-CML-002, using Phase B append-only ledger, current gap rules and source lineage. Allow export as human-readable HTML/Markdown and machine-readable JSON where consistent with repo architecture. Preserve stable links and IDs. No fabricated client decision or contract exposure.

## Minimum record
- decision_condition_id (stable), case_id, gap_id, claim_id, decision_type (illustrative, not an asserted real customer decision), precise scope and rule references;
- current evidence state, qualification outcome, evidence cutoff, last source check, review time, rubric and rule version;
- qualifying and disqualifying evidence with source IDs, dependency lineage, counterevidence, inaccessible sources and search-scope limits;
- exact closure test and acceptable source types, plus unresolved disputes (Chindata E3/E4 and unsupported second real reviewer);
- customer-entered decision trigger / review date / fallback fields only if distinctly marked UNSPECIFIED or CLIENT_DEFINED, never guessed;
- generated snapshot hash, supersession links and explicit 'not a decision recommendation' notice.

## Engineering requirements
1. Derive content from existing canonical source artifacts; do not duplicate independent untracked truth copies or read confidential customer D1 into public builds.
2. Add a visible 'Copy decision conditions' affordance that actually copies a self-contained citation with stable URLs, frozen cutoff, gap criteria and current unknowns. Provide accessible fallback.
3. Deterministic exports and content hashing; include export schema, provenance and explicit error/insufficient-data handling.
4. Distinguish *evidence rule* from *client action gate*: SE can report whether qualifying evidence is present; client sets proceed/hold/exit. Never silently infer the action.
5. Keep original records append-only, never rewrite old state. Changes create a new export version pointing at the previous digest, not silent updates.
6. On .org expose public illustrative conditions with no false private adoption claims. .com integration should be scoped to verified current architecture, and any not-yet-live commercial capability visibly marked proposed. Do not change pricing.
7. Honor existing three language routes, canonical/hreflang/sitemap, root/docs mirrors and SEO policies where pages are added.
8. Open Challenge can challenge rules or sources, but submission cannot change conditions or state automatically.

## Acceptance tests
- All fields grounded in current existing source packets and gap rules; no invented support/ROI/customer action.
- Zero changes to original source packets, case states, IDs, URLs, hashes, brand policy, pricing or D1.
- Stable IDs, deterministic output and hash across repeated builds.
- Negative tests: invalid/missing gap, conflicting dates, superseded source, conflicting reviewers, non-qualifying E2, issuer E4 conditional eligibility, second-site identity false positive, unavailable source, unsafe content and code injection.
- Human and machine-readable formats agree semantically; root/docs mirror and links correct.
- Legacy failures separated; NEW_REGRESSION_COUNT=0.
- Phase C PR stays Draft until explicit owner approval; production is separately gated.

## Reporting
PROJECT=SE-DUAL-SITE-UPGRADE-002
PHASE=C
BASELINE_MAIN_SHA=bbced95da00ed259e942aa63ebd89d93f70c54a0
HEAD_SHA=[actual]
DECISION_CONDITIONS_CREATED=[actual]
ORIGINAL_RECORDS_CHANGED=0
CASE_STATE_CHANGED=NO
NEW_REGRESSION_COUNT=[actual]
PRODUCTION_DEPLOY=NO
READY_FOR_OWNER_MERGE_REVIEW=[YES/NO]
BLOCKERS=[actual]
