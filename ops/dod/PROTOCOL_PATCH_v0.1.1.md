# SE-DOD-001 protocol patch v0.1.1 application

Applied: 2026-10-08 (Asia/Shanghai)

Result: `PASS_WITH_PROTOCOL_PATCH`

## Calibration boundary

The 2026-10-08 run reviewed five events in each frozen vertical. It is a calibration run, not market coverage. It does not support tier relaxation, vertical expansion, scarcity claims, or a conclusion that market demand is absent. Tier relaxation remains prohibited until at least 20 relevant events per vertical have been reviewed with documented rejection reasons.

## Material-gap rule

The raw claim inventory remains in `CLAIM_GAPS.csv`. `MATERIAL_DECISION_EVIDENCE_GAPS.csv` records the patched qualification: a gap is material only when resolving it could change a named decision category. DE-C-005 is retained as radar evidence but does not qualify as a material decision opportunity because no exact contractor acquisition or candidate-source decision is identified.

## Public/private boundary

Every row in the patched opportunity and material-gap ledgers records the reviewed public state separately from `INTERNAL_OR_PRIVATE_STATE = UNKNOWN`. No record concludes that an organization lacks internal evidence.

## Owner resolution and first wave

- `NAMED_ACCOUNTABLE_PERSON`: 4
- `ACCOUNTABLE_ROLE_ONLY`: 7
- `COMPANY_ROUTE_ONLY`: 4
- `UNRESOLVED`: 5

Only four rows pass the named-owner gate after manual evidence-chain review. Six selected role-only rows remain `REVIEW`. Company-route-only and unresolved rows are `HOLD`. A verified corporate route is not treated as evidence of decision responsibility.

Four messages pass the nine pre-send gates after the v0.1.1 manual review recorded in `FIRST_WAVE_MANUAL_REVIEW_2026-10-08.md`. OR-001 fails the named-owner gate because Amanda Xu's ESS role is relevant but the reviewed public record does not establish that she owns the 60 GWh order acceptance or China delivery decision. The four passing messages are recommended for send only after explicit human authorization; no outreach is authorized or sent. The first ten outreach messages require manual review.

The review also corrected DE-D-001 to the operative SEC-filed LOI boundary. The LOI is largely non-binding apart from specified provisions; neither the opportunity ledger nor the first message describes the proposed investment as completed or fully binding.

## Best-opportunity decision

DE-D-002 remains the best reviewed decision opportunity because the public filing establishes an active acquisition decision, the unresolved facts could change go/no-go, price, conditions, and risk allocation, the cost of error is high, the CEO is named, and the official route is expressly used to arrange CEO meetings. The conclusion is limited to the reviewed public record; private diligence may establish more.

DE-A-005 is separately recorded as the most interesting evidence gap because the boundary between announced order/production readiness and attributable accepted field performance is unusually clear. It is not selected as best merely because the gap is large.
