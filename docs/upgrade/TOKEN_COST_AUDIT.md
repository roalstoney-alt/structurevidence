# Token and Research-Cost Audit

## Result

Research-process cost telemetry is not implemented in the committed repository.

Repository inspection found no canonical fields for:

- `model_calls`;
- `tool_calls`;
- `estimated_tokens` or actual token usage;
- `estimated_model_cost` or actual model cost;
- research data cost;
- human research minutes;
- engineering minutes;
- total research cost.

Searches for these concepts across RDL, scripts, CML, research, timeline, monitoring, GDR-SE, and commercial source records did not find an implemented research record. Cost fields that do exist describe industrial, migration, product, payment, or commercial economics and must not be misclassified as the cost of doing research.

## Currently observable proxies

| Observable | Availability | Limitation |
| --- | --- | --- |
| Query text | Present in some search/counter-evidence logs | Not universal; no model/tool attribution |
| Search/retrieval timestamps | Present in some packages | Not enough to derive duration or labor |
| Sources checked/used | Present in some packages | Rejected/duplicate semantics inconsistent |
| Evidence and artifact counts | Reconstructable | Does not measure research expense |
| Test runtime | Observable during execution | Engineering validation time is not research cost |
| Git history | Available | Commit duration and human effort cannot be inferred safely |

No token or dollar estimate was inferred from file size, elapsed command time, message count, or test duration.

## Minimum Phase 1 telemetry

The RDL research record should include raw nullable fields:

```text
model_calls
tool_calls
estimated_tokens
observed_input_tokens
observed_output_tokens
estimated_model_cost
observed_model_cost
data_cost
human_minutes
engineering_minutes
currency
cost_source
cost_limit
```

Rules:

- use `UNKNOWN`, not zero, when telemetry is unavailable;
- distinguish estimate from observed value;
- store model/tool counts per research round;
- do not include secrets, prompts containing private customer data, or billing credentials;
- preserve raw dimensions rather than an opaque aggregate efficiency score;
- separate inventory-research cost from customer-specific cost;
- allow later reconciliation without rewriting the original observation.

## Phase 0 telemetry

`RESEARCH_LEVEL = L0_REUSE`

`EXTERNAL_RESEARCH_COST = 0` because no external research was performed.

`MODEL_TOKEN_COST = UNKNOWN`

`TOOL_COST = UNKNOWN`

`HUMAN_MINUTES = UNKNOWN`

`ENGINEERING_MINUTES = UNKNOWN`
