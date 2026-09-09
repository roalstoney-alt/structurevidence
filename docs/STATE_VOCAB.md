# StructEvidence State Vocabulary

## Structural State Axes
- issuance/burn
- settlement object
- governance dependence
- client/validator structure
- treasury dependence

New structural labels must register at least one axis before use. Future batches fail closed on free-form labels.

## Evidence State Enum
`ALIGNED | TEMPORAL_CHANGE | POTENTIAL_CONFLICT | UNRECONCILED | INSUFFICIENT`

## Supersession Enum
`UNCHANGED | REFINED | SUPERSEDED | WITHDRAWN`

## Current R1 Label Axis Map
- `BURN_LINKED_ECOSYSTEM_UTILITY_REGIME`: issuance/burn, settlement object, governance dependence
- `EXECUTION_SCALE_WITH_PARTIAL_CLIENT_DIVERSITY`: client/validator structure, governance dependence
- `STABLECOIN_RESOURCE_SETTLEMENT_REGIME`: settlement object, governance dependence
- `SDF_TREASURY_DEPENDENT_PAYMENT_NETWORK`: treasury dependence, settlement object, client/validator structure

These labels are not renamed in this commit. `R1 RESEARCH SUPPORT` identifies method version and publication status only; it is not evidence strength, ranking, rating or decision usefulness.
