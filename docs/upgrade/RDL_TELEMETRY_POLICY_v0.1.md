# RDL Telemetry Policy v0.1

## Raw telemetry

The research record requires:

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

Each quantitative field is a measurement containing `status`, `value`, and `source_ref`.

## Status semantics

| Status | Value rule |
| --- | --- |
| `OBSERVED` | Non-negative numeric value plus a source reference |
| `ESTIMATED` | Non-negative numeric value plus an estimation source reference |
| `UNKNOWN` | `null`; never silently zero |
| `NOT_APPLICABLE` | `null` |

Estimated-token and estimated-cost fields cannot claim observed status. Observed input/output token, observed model cost, and data-cost fields cannot claim estimated status.

## Prohibited inference

Unavailable usage must not be inferred from file size, message count, wall-clock time, test duration, or Git history. Phase 1 records preserve missing telemetry as `UNKNOWN`.

## Reconciliation

A later observed value is written as a correction/successor record referencing the original. The original UNKNOWN or estimate remains preserved. Telemetry reconciliation must not rewrite research history.

## Cost boundaries

Research cost is distinct from product, migration, customer, payment, and commercial economics. Inventory and customer-specific research remain separately classified. Billing credentials, API keys and raw private prompts are prohibited.
