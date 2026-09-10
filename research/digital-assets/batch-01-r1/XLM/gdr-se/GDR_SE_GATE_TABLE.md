# GDR-SE Gate Table

| Gate | Status | Severity | Reason |
| --- | --- | --- | --- |
| G1_SCHEMA_INTEGRITY | PASS | HARD | Required IDs, versions and report metadata are present. |
| G2_RTP_PROVENANCE | PASS | HARD | GDR-SE references RTP-style manifests and registries instead of creating a second provenance system. |
| G3_EVIDENCE_FRESHNESS | PASS | SOFT | Freshness category L1_NETWORK is configured without a universal threshold. |
| G4_SOURCE_DEPENDENCY | PASS | SOFT | Source dependency gate passed. |
| G5_NUMERICAL_RECONCILIATION | PASS | SOFT | Material arithmetic is traceable or not used as a release upgrade. |
| G6_ECL_CONSISTENCY | PASS | SOFT | Evidence state is reconcilable and is not treated as a truth score. |
| G7_COUNTER_EVIDENCE_COMPLETENESS | PASS | HARD | Counter-evidence log exists; paid delivery cannot proceed without it. |
| G8_INDEPENDENT_REVIEW | PASS | SOFT | Independent review artifact is frozen for R1. |
| G9_SENSITIVITY_RIGHT_OF_REPLY | NOT_APPLICABLE | SOFT | No material inconsistency or specific allegation is authorized by GDR-SE. |
| G10_EXPIRY_SUPERSESSION | PASS | HARD | No GDR-SE supersession or correction blocks this overlay. |

Authorization: `ALLOW_PUBLICATION`

Public status: `CURRENT`
