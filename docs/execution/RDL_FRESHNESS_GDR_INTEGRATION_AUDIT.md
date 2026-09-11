# RDL Freshness GDR Integration Audit

GDR-SE G3 consumes `rdl/freshness/gdr_g3_adapter.json` and per-subject `research/freshness/*/FRESHNESS_EVALUATION_v0.1a.json`. EVENT_INVALIDATED and UNDER_REVIEW now set explicit fail-safe facts consumed by aggregation. Other GDR-SE gates and aggregation precedence remain unchanged.
