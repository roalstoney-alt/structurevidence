# SE-GTM-002 DPAL architecture decision

DECISION_DATE = `2026-10-11`

BASE_IMPLEMENTATION = `b61588b50256022ab501a9b567a930c7e3b0c0b6`

STATUS = `LIGHTWEIGHT_PROJECTION_APPROVED_FOR_PILOT`

ARCHITECTURE_CHANGED = `NO`

## Decision

Do not introduce a second opportunity, customer, evidence or commercial-state
model. The existing CDSP record already represents the trigger, pressure
evidence, affected decision, missing fact, evidence state, counterevidence,
accountable role, contact route, decision window, mandatory qualification
gates, authorization and append-only history.

DPAL v0.3 is therefore an append-only relation projection over public research.
`PRESSURE_ACCOUNTABILITY_RELATIONS.jsonl` adds only the relationships needed to
compare pressure channels:

- one candidate may carry multiple controlled pressure classes;
- the observed pressure event remains separate from inference and hypothesis;
- organization-level obligation is distinct from a verified internal owner;
- an external verification requirement is distinct from an open procurement
  need;
- an identifiable buyer role is distinct from confirmed buyer demand;
- freshness and counterevidence can prevent qualification without deleting the
  original observation.

No `DPAL_SCHEMA_v0.1.json` is created. A redundant schema would create a
parallel truth model. The controlled projection is validated by
`scripts/test_se_gtm_002_dpal_v03.py` and can be promoted into CDSP only through
a new versioned CDSP record after every original gate passes.

## Controlled pressure vocabulary

- `EXTERNAL_RISK`
- `INTERNAL_AUDIT`
- `REGULATORY_COMPLIANCE`
- `GEOPOLITICAL_POLICY`
- `GOVERNANCE_ACCOUNTABILITY`
- `COMMERCIAL_SUPPLY_CHAIN`

Multiple values are permitted. No value implies a customer requirement by
itself.

## Boundary

This projection does not modify CDSP v0.1, RDL, CML, Decision Memory,
`TRUST_BOUNDARY_30D_001`, production, historical candidate outcomes, public
claims or contact authorization.
