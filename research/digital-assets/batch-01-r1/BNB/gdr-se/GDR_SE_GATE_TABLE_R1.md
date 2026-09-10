# GDR-SE Runtime Gate Table R1

| Gate | Status | Severity | Validator | Rule Version | Reason |
| --- | --- | --- | --- | --- | --- |
| G1_SCHEMA_INTEGRITY | PARTIAL | HARD | validate_g1_schema | GDR_SE_RUNTIME_RULES_v0.1-R1 | Required runtime fields are present, but no formal profile JSON Schema is frozen. |
| G2_RTP_PROVENANCE | PASS | HARD | validate_g2_provenance | GDR_SE_RUNTIME_RULES_v0.1-R1 | Required artifacts exist, are readable, non-empty, hashed and match recorded hashes. |
| G3_EVIDENCE_FRESHNESS | UNRESOLVED | SOFT | validate_g3_freshness | GDR_SE_RUNTIME_RULES_v0.1-R1 | RDL freshness policy not configured for category L1_NETWORK. |
| G4_SOURCE_DEPENDENCY | PARTIAL | SOFT | validate_g4_source_dependency | GDR_SE_RUNTIME_RULES_v0.1-R1 | Source dependency was derived from declared coverage and dependency artifacts, not URL count. |
| G5_NUMERICAL_RECONCILIATION | PASS | SOFT | validate_g5_numerical | GDR_SE_RUNTIME_RULES_v0.1-R1 | All material numerical reconciliation rows are reconciled. |
| G6_ECL_CONSISTENCY | PASS | SOFT | validate_g6_ecl | GDR_SE_RUNTIME_RULES_v0.1-R1 | Evidence state was mapped without subject-specific exceptions. |
| G7_COUNTER_EVIDENCE_COMPLETENESS | PARTIAL | HARD | validate_g7_counter_evidence | GDR_SE_RUNTIME_RULES_v0.1-R1 | Counter-evidence exists but contains repeated boilerplate patterns. |
| G8_INDEPENDENT_REVIEW | PARTIAL | SOFT | validate_g8_review | GDR_SE_RUNTIME_RULES_v0.1-R1 | Independent review agreement classification was read from the frozen review artifact. |
| G9_SENSITIVITY_RIGHT_OF_REPLY | NOT_APPLICABLE | SOFT | validate_g9_sensitivity | GDR_SE_RUNTIME_RULES_v0.1-R1 | No sensitivity/right-of-reply trigger is present in runtime context. |
| G10_EXPIRY_SUPERSESSION | PASS | HARD | validate_g10_supersession | GDR_SE_RUNTIME_RULES_v0.1-R1 | Supersession/correction artifacts do not block this current runtime overlay. |

Authorization: `HUMAN_REVIEW_REQUIRED`

Input Bundle SHA-256: `a947f5c38a1bf5cfcead303c63f79785d523cef9dd4a9560ffb13cd302297021`
