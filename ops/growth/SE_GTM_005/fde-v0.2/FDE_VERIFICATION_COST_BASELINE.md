# SE-GTM-005 v0.2 — FDE Verification Cost Baseline

STATUS = `MODELED_ONLY_NO_OBSERVED_CUSTOMER_COST`

CURRENCY = `USD`

## Measurement boundary

No reviewed provider published comparable engineering hours, customer review
hours, clarification rounds, evidence rework or independent verification fees.
Therefore:

OBSERVED_COST_REDUCTION = `NOT_ESTABLISHED`

The model below is an editable planning scenario, not a quote, forecast,
benchmark, sales claim or evidence of reduced CAC or faster sales cycles.

## Formula

For each work category:

`cost = provider_hours × provider_loaded_rate + customer_hours × customer_loaded_rate + external_fees`

The only valid real comparison uses the same deployment scope and quality gate
before and after StructEvidence. Removed safeguards do not count as savings.

## Base modeled scenario: one customer acceptance cycle

Assumptions:

- provider loaded rate: `$160/hour`;
- customer reviewer loaded rate: `$180/hour`;
- StructEvidence fee: `$2,000` for the modeled cycle;
- all hours and rates are invented planning inputs.

| Work category | Baseline hours / cost | With StructEvidence hours / cost | Modeled change |
| --- | ---: | ---: | ---: |
| Provider evidence preparation | 28 h / $4,480 | 12 h / $1,920 | -$2,560 |
| Customer technical/security review | 20 h / $3,600 | 14 h / $2,520 | -$1,080 |
| Provider clarification rounds | 12 h / $1,920 | 5 h / $800 | -$1,120 |
| Customer-specific pack preparation | 8 h / $1,280 | 10 h / $1,600 | +$320 |
| Evidence-related rework | 12 h / $1,920 | 6 h / $960 | -$960 |
| Verification maintenance | 4 h / $640 | 3 h / $480 | -$160 |
| StructEvidence fee | $0 | $2,000 | +$2,000 |
| **Total** | **$13,840** | **$10,280** | **-$3,560 / -25.7%** |

MODELED_COST_REDUCTION_BASE = `$3,560_PER_ACCEPTANCE_CYCLE`

MODELED_PERCENT_REDUCTION_BASE = `25.7%`

## Sensitivity and break-even

The modeled gross labor reduction before the StructEvidence fee is `$5,560`.
At these invented rates and hours, the fee must stay below `$5,560` to produce
nominal savings. That is not a market price or willingness-to-pay result.

| Scenario | Baseline cost | With-SE cost | Modeled reduction | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Low reuse / high tailoring | $13,840 | $13,300 | $540 / 3.9% | Weak case; one variance can erase savings. |
| Base | $13,840 | $10,280 | $3,560 / 25.7% | Hypothesis worth measuring, not claiming. |
| High reuse / repeated customer | $13,840 | $8,600 | $5,240 / 37.9% | Depends on lawful, technically valid reuse. |

## Required real measurements

1. Provider engineering hours by activity and role.
2. Customer reviewer hours by technical, security, GRC and business role.
3. Number and duration of clarification rounds.
4. Rework attributable specifically to missing, inconsistent or stale evidence.
5. Pack-maintenance effort across product/model versions.
6. Customer-specific tests that cannot be reused.
7. Quality outcomes: defects found, exceptions, false acceptance and missed
   counterevidence.
8. StructEvidence time and fee.

## Quality and risk safeguards

- Never count a faster review caused by omitted tests or reduced scrutiny.
- Preserve UNKNOWN, NOT_ESTABLISHED and contradictory evidence.
- Separate provider claims from customer-observed outcomes.
- Compare equivalent versions, scopes and acceptance conditions.
- Attribute savings only after the customer confirms the baseline and result.
- Do not claim CAC reduction, sales acceleration or ROI from this model.
