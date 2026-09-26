# SE-FRR-001 Phase 1 Open Issues

Date: 2026-09-26

No issue blocks Phase 1 acceptance or Phase 2 entry.

## Deferred items

1. `TECH_DEBT_SE_001`: replace deprecated `jsonschema.RefResolver` use in the historical CML validator with the `referencing` API. This predates Phase 1 and remains a warning only.
2. Canonical JSON v0.1 is a precisely documented local strategy, not a claim of RFC 8785 conformance. Any cross-language implementation must reproduce its Unicode, numeric, array-order, and excluded-field rules or introduce a versioned migration.
3. Hash chains provide tamper evidence, not signer identity. Signing, key management, and external anchoring are outside Phase 1.
4. Phase 1 adapters prove compatibility for two representative CML/RDL records only. Corpus-wide mapping, collision policy, and migration tooling belong to a later authorized phase.
5. Request and Outcome fixtures are synthetic. Live D1/customer data remains outside Git and was neither inspected nor migrated.

`STATE_VOCABULARY_GAP`: none observed in the Phase 1 fixtures. Future additions require explicit vocabulary review and a version change.
