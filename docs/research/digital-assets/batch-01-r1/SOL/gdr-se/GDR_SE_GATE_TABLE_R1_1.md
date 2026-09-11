# GDR-SE Runtime Gate Table R1.1

| Gate | Status | Severity | Validator | Rule Version | Reason |
| --- | --- | --- | --- | --- | --- |
| G1_SCHEMA_INTEGRITY | PARTIAL | HARD | validate_g1_schema | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | Required runtime fields are present, but no formal profile JSON Schema is frozen. |
| G2_RTP_PROVENANCE | PASS | HARD | validate_g2_provenance | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | Required artifacts exist, are readable, non-empty, hashed and match recorded hashes. |
| G3_EVIDENCE_FRESHNESS | PASS | SOFT | validate_g3_freshness | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | G3 consumed RDL_FRESHNESS_v0.1a release state CURRENT. |
| G4_SOURCE_DEPENDENCY | PARTIAL | SOFT | validate_g4_source_dependency | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | Source dependency was derived from declared coverage and dependency artifacts, not URL count. |
| G5_NUMERICAL_RECONCILIATION | PASS | SOFT | validate_g5_numerical | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | All material numerical reconciliation rows are reconciled. |
| G6_ECL_CONSISTENCY | PARTIAL | SOFT | validate_g6_ecl | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | Potential conflict is not material inconsistency; limitations are required. |
| G7_COUNTER_EVIDENCE_COMPLETENESS | PARTIAL | HARD | validate_g7_counter_evidence | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | Counter-evidence exists but contains repeated boilerplate patterns. |
| G8_INDEPENDENT_REVIEW | PARTIAL | SOFT | validate_g8_review | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | Independent review agreement classification was read from the frozen review artifact. |
| G9_SENSITIVITY_RIGHT_OF_REPLY | NOT_APPLICABLE | SOFT | validate_g9_sensitivity | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | No sensitivity/right-of-reply trigger is present in runtime context. |
| G10_EXPIRY_SUPERSESSION | PASS | HARD | validate_g10_supersession | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | Supersession/correction artifacts do not block this current runtime overlay. |

Authorization: `ALLOW_WITH_LIMITATIONS`

Evaluation As Of: `2026-09-11T03:55:43.713607Z`

Input Bundle SHA-256: `6331ce51e6ecdf4dd7a664e737aaa0215c1ab9278986c5f1931cee2f04df0ee5`
