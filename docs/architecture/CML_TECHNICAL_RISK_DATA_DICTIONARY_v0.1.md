# CML Technical Risk Data Dictionary v0.1

| Field | Type | Required | Boundary | Meaning | Allowed values / source | Freshness | Supersession |
| --- | --- | --- | --- | --- | --- | --- | --- |
| record_id | string | yes | public | Permanent evidence record ID | Evidence Core | immutable | successor points backward |
| subject_id | string | yes | public | Permanent technical item ID | Evidence Core | immutable | never reused |
| manufacturer_part_number | string | yes | public | Exact maker spelling and punctuation | manufacturer | identity review | no silent merge |
| technical_item_type | enum | yes | public | Domain item category | schema enum | schema-versioned | retained |
| effective_at | UTC datetime | yes | public | When event/state applies | primary evidence | event-driven | retained |
| known_at | UTC datetime | yes | public | When evidence became known | retrieval/notice | no lookahead | retained |
| event_domain | enum | yes | public | Scope of state mutation | SUBJECT/EVIDENCE/RESEARCH/AUTHORIZATION | event-driven | scoped |
| lifecycle_state | enum | yes | public | Manufacturer lifecycle state | primary lifecycle evidence | event-driven | current successor |
| oem_replacement_status | enum | yes | public | Whether OEM lists replacement | OEM evidence | event-driven | current successor |
| dependency.context | text | yes | public-safe | Operational/engineering dependency | evidence + judgment | review on design change | versioned |
| compatibility_matrix | array | yes | public-safe | Dimension-level comparison | MATCH/DIFFERENCE/MISMATCH/UNKNOWN/TEST/N/A | test/revision driven | scope-bound |
| qualification_state | enum | yes | public-safe | Evidence-backed qualification stage | CML taxonomy | invalidated by scope/revision events | scope-bound |
| known_facts | array | yes | public | Typed supported claims | sources | source-family policy | corrected explicitly |
| unknowns | array | yes | public | Unresolved material questions | research review | re-evaluated | retained in history |
| candidates | array | yes | public-safe | Replacement paths | exact evidence | source/test driven | status history retained |
| decision.supported_paths | array | yes | public-safe | Defensible current actions | CML actions | evidence change | new release |
| customer_bom | object | no | private | Client component list | client | engagement policy | never public |
| client_usage/pricing/drawings | object | no | private | Customer operational context | client/NDA | engagement policy | never public |
| input_hash | SHA-256 | yes | public | Canonical source + payload commitment | generated | immutable | successor gets new hash |
| record_hash | SHA-256 | yes | public | Canonical record commitment | generated | immutable | successor gets new hash |
