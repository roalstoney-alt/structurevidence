# GDR-SE Runtime Gate Table R1.1

| Gate | Status | Severity | Validator | Rule Version | Reason |
| --- | --- | --- | --- | --- | --- |
| G1_SCHEMA_INTEGRITY | PARTIAL | HARD | validate_g1_schema | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | Required runtime fields are present, but no formal profile JSON Schema is frozen. |
| G2_RTP_PROVENANCE | PASS | HARD | validate_g2_provenance | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | Required artifacts exist, are readable, non-empty, hashed and match recorded hashes. |
| G3_EVIDENCE_FRESHNESS | UNRESOLVED | SOFT | validate_g3_freshness | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | RDL freshness policy not configured for category L1_NETWORK. |
| G4_SOURCE_DEPENDENCY | LIMITED | SOFT | validate_g4_source_dependency | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | Source dependency was derived from declared coverage and dependency artifacts, not URL count. |
| G5_NUMERICAL_RECONCILIATION | PASS | SOFT | validate_g5_numerical | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | All material numerical reconciliation rows are reconciled. |
| G6_ECL_CONSISTENCY | PASS | SOFT | validate_g6_ecl | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | Evidence state was mapped without subject-specific exceptions. |
| G7_COUNTER_EVIDENCE_COMPLETENESS | PARTIAL | HARD | validate_g7_counter_evidence | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | Counter-evidence exists but contains repeated boilerplate patterns. |
| G8_INDEPENDENT_REVIEW | PARTIAL | SOFT | validate_g8_review | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | Independent review agreement classification was read from the frozen review artifact. |
| G9_SENSITIVITY_RIGHT_OF_REPLY | NOT_APPLICABLE | SOFT | validate_g9_sensitivity | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | No sensitivity/right-of-reply trigger is present in runtime context. |
| G10_EXPIRY_SUPERSESSION | PASS | HARD | validate_g10_supersession | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | Supersession/correction artifacts do not block this current runtime overlay. |

Authorization: `HUMAN_REVIEW_REQUIRED`

Evaluation As Of: `2026-09-10T14:18:35.507637Z`

Input Bundle SHA-256: `449c15d98333b685e234a9568cb28fc24987191c98764a6c43137a819136d410`
