# GDR-SE Gate Table

| Gate | Status | Severity | Reason |
| --- | --- | --- | --- |
| G1_SCHEMA_INTEGRITY | PASS | HARD | Required IDs, versions and report metadata are present. |
| G2_RTP_PROVENANCE | PASS | HARD | GDR-SE references RTP-style manifests and registries instead of creating a second provenance system. |
| G3_EVIDENCE_FRESHNESS | PASS | SOFT | Freshness category CORPORATE_TREASURY is configured without a universal threshold. |
| G4_SOURCE_DEPENDENCY | PARTIAL | SOFT | Source coverage is partial and must be displayed as a limitation. |
| G5_NUMERICAL_RECONCILIATION | PASS | SOFT | Material arithmetic is traceable or not used as a release upgrade. |
| G6_ECL_CONSISTENCY | PASS | SOFT | Evidence state is reconcilable and is not treated as a truth score. |
| G7_COUNTER_EVIDENCE_COMPLETENESS | PASS | HARD | Counter-evidence log exists; paid delivery cannot proceed without it. |
| G8_INDEPENDENT_REVIEW | PARTIAL | SOFT | Strategy remains a method pilot with partial review labeling. |
| G9_SENSITIVITY_RIGHT_OF_REPLY | NOT_APPLICABLE | SOFT | No material inconsistency or specific allegation is authorized by GDR-SE. |
| G10_EXPIRY_SUPERSESSION | PASS | HARD | No GDR-SE supersession or correction blocks this overlay. |

Authorization: `ALLOW_WITH_LIMITATIONS`

Public status: `CURRENT_WITH_LIMITATIONS`
