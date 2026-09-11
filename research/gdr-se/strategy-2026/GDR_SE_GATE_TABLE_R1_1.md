# GDR-SE Runtime Gate Table R1.1

| Gate | Status | Severity | Validator | Rule Version | Reason |
| --- | --- | --- | --- | --- | --- |
| G1_SCHEMA_INTEGRITY | PARTIAL | HARD | validate_g1_schema | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | Required runtime fields are present, but no formal profile JSON Schema is frozen. |
| G2_RTP_PROVENANCE | PARTIAL | HARD | validate_g2_provenance | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | Required artifacts exist and are hashed, but legacy records do not carry all expected hashes. |
| G3_EVIDENCE_FRESHNESS | PASS | SOFT | validate_g3_freshness | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | G3 consumed RDL_FRESHNESS_v0.1a release state CURRENT. |
| G4_SOURCE_DEPENDENCY | PARTIAL | SOFT | validate_g4_source_dependency | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | Source dependency was derived from declared coverage and dependency artifacts, not URL count. |
| G5_NUMERICAL_RECONCILIATION | NOT_APPLICABLE | SOFT | validate_g5_numerical | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | No profile-required numerical reconciliation artifact exists for this legacy profile. |
| G6_ECL_CONSISTENCY | PASS | SOFT | validate_g6_ecl | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | Evidence state was mapped without subject-specific exceptions. |
| G7_COUNTER_EVIDENCE_COMPLETENESS | PASS | HARD | validate_g7_counter_evidence | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | Targeted counter-evidence exists for required hypotheses with queries, sources and uncertainty. |
| G8_INDEPENDENT_REVIEW | NOT_APPLICABLE | SOFT | validate_g8_review | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | Independent review is not required for this profile. |
| G9_SENSITIVITY_RIGHT_OF_REPLY | NOT_APPLICABLE | SOFT | validate_g9_sensitivity | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | No sensitivity/right-of-reply trigger is present in runtime context. |
| G10_EXPIRY_SUPERSESSION | PASS | HARD | validate_g10_supersession | GDR_SE_RUNTIME_RULES_v0.1-R1.1 | Supersession/correction artifacts do not block this current runtime overlay. |

Authorization: `ALLOW_WITH_LIMITATIONS`

Evaluation As Of: `2026-09-11T03:55:43.713607Z`

Input Bundle SHA-256: `673152115b4063c9bb6fd555f6e34d99362cec5f741f6f8f8768558283e418d2`
