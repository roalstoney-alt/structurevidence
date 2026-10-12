## Problem

Public featured-case copy did not consistently show its source, evidence cut-off, review completeness and inference boundary in the same view. Commercial intake combined legal acknowledgements and could place optional customer narrative in an append-only event note. Correction/new-research rules and public restriction states also needed a clearer boundary.

## Changes

- makes the three approved homepage cases explicit and bounded in English, Simplified Chinese and Spanish, with matching root/docs mirrors;
- keeps NSCLC off the homepage while preserving its URL and research history;
- adds a shared public-evidence presentation projection without editing canonical case evidence or deadlines;
- adds privacy, terms, refund, corrections/publication and source-rights materials without asserting unverified region, retention, deletion or AI-training facts;
- separates privacy-notice acknowledgement from confidentiality acknowledgement; marketing/publication authorization remain separate and false;
- adds migration 0003 for versioned notices and isolated private context, with server-side enforcement and Access-protected review;
- makes confirmed StructEvidence error correction independent of purchasing new research, while allowing a new question/source universe/cut-off to be separately scoped;
- adds operator-fact, counsel-review, migration and release/rollback packages.

## Validation

- focused legal-boundary suite: PASS;
- direct Worker test suite: PASS;
- case-review, case-watch, Irkutsk publication/alias, public/commercial boundary, i18n and commercial readiness suites: PASS;
- migrations 0001–0003 applied to a synthetic SQLite database: PASS;
- Worker dry-run bundle: PASS;
- root/docs mirrors: byte-identical for affected home/legal pages;
- diff under `cases/` and `docs/cases/`: empty;
- new regressions: 0.

Three pre-existing repository assertions remain failing and are recorded in `VALIDATION_REPORT.md`; they reproduce on the base SHA and were not weakened or hidden.

These are engineering validation results, not a legal-compliance certification.

## Production migration requirement

The new Worker must not deploy until D1 migration `0003_legal_boundary_notices.sql` is explicitly authorized, applied and verified. Migration 0003 is additive, but becomes operationally irreversible once it holds records. Legacy `request_events.note` content is not migrated or deleted by this PR and requires a separate, authorized aggregate assessment and disposition design. See `PRODUCTION_DATA_MIGRATION_PLAN.md`.

## Pending operator facts and counsel review

Before affected terms/privacy claims or commercial intake are released, the operator must confirm corporate documents/address roles, actual customer territories and B2B/B2C scope, Cloudflare location/log/backup settings, mailbox/payment retention, AI/agent processing and contract versions. Counsel review remains pending for Hong Kong/served-region requirements, publication/reputation boundaries, customer/AI processing, refund/error/liability/dispute terms and third-party content rights.

## Release boundary

This PR does not deploy, migrate production data, change case state, advance an evidence cut-off, alter monitoring tasks or retroactively amend existing customer contracts. `.org`, `.com` and D1 have separate approval, verification and rollback gates in `RELEASE_CHECKLIST.md`.
