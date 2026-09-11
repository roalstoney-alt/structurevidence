# Static vs Runtime Authorization Audit

| Subject | Old Static Authorization | New Runtime Authorization | Changed? | Gate Causing Difference | Reason |
| --- | --- | --- | --- | --- | --- |
| STRATEGY | ALLOW_WITH_LIMITATIONS | ALLOW_WITH_LIMITATIONS | NO | G1_SCHEMA_INTEGRITY | Required runtime fields are present, but no formal profile JSON Schema is frozen. |
| BNB | ALLOW_WITH_LIMITATIONS | ALLOW_WITH_LIMITATIONS | NO | G1_SCHEMA_INTEGRITY | Required runtime fields are present, but no formal profile JSON Schema is frozen. |
| SOL | ALLOW_WITH_LIMITATIONS | ALLOW_WITH_LIMITATIONS | NO | G1_SCHEMA_INTEGRITY | Required runtime fields are present, but no formal profile JSON Schema is frozen. |
| TRX | ALLOW_WITH_LIMITATIONS | ALLOW_WITH_LIMITATIONS | NO | G1_SCHEMA_INTEGRITY | Required runtime fields are present, but no formal profile JSON Schema is frozen. |
| XLM | ALLOW_PUBLICATION | ALLOW_WITH_LIMITATIONS | YES | G1_SCHEMA_INTEGRITY | Required runtime fields are present, but no formal profile JSON Schema is frozen. |
