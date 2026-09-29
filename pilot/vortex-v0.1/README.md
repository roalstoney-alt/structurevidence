# Vortex Discovery Pilot v0.1

Status: `READY_FOR_HUMAN_LAUNCH`
Baseline: `82b335d581c94965514bfc7407bb6414e8fe3747`
Duration: 14 days from the human-approved launch date
Paid marketing authorization: `USD 0`

## Experiment boundary

This pilot tests whether a time-bounded evidence object is discovered, cited, reused, challenged, or used to request further verification. It does not test broad awareness, academic validation, scaled product-market fit, or follower growth.

The propagation unit is:

`CLAIM + STATE + AS_OF + PROTOCOL + HASH + CANONICAL URL + BOUNDARY`

StructureEvidence provides the evidence state. An agent may retrieve, compare, explain, and trace it. The responsible actor owns the final judgment.

## Frozen controls

- Use only the 26 existing claims across the three existing cases.
- Industrial cases are the public discovery surfaces.
- The NSCLC records are safety/boundary tests only.
- Do not add claims, cases, external research, recommendations, or autonomous decisions.
- Do not tune the protocol after every failed test; record the failure first.
- Do not treat `NOT_ESTABLISHED` as false, a single instance as adoption, or a trial-population result as an individual outcome.

## Human approval gates

Human approval is required before any public post, direct outreach, research authorization, claim-state change, or publication change. The drafts in `outreach/INITIAL_DRAFTS.md` have not been sent.

## Attribution

Use the canonical claim URL with:

`?src=<x|linkedin|direct>&pilot=vx01&q=<VX-Qnnn>`

Do not add personal identifiers to URLs. Record observable behavior in `events.csv`; keep private notes minimal and free of unnecessary personal information.

## 14-day operating cadence

| Day | Minimum action |
| --- | --- |
| 1 | Human approves and publishes one industrial question. |
| 2 | Human approves outreach to 2–3 qualified people. |
| 3 | Human approves a second industrial question. |
| 4 | Observe and classify only. |
| 5 | Human approves one LinkedIn question. |
| 6 | Human-approved direct outreach. |
| 7 | Complete `WEEK_1_REVIEW.md`. |
| 8–13 | Repeat narrowly, informed by Week 1; re-engage meaningful interest only. |
| 14 | Complete `FINAL_REPORT.md` and choose one permitted decision state. |

Maximum is one public post per channel per day. Lower volume is preferred when it improves question/audience fit.

## Event and challenge handling

Allowed event types are `VIEW_OBSERVED`, `CLAIM_OPEN`, `CANONICAL_LINK_CLICK`, `CITATION_OBSERVED`, `SHARE_OBSERVED`, `RETURN_USE`, `SECOND_QUERY`, `CHALLENGE_SUBMITTED`, `CHALLENGE_QUALIFIED`, `VERIFY_INTENT`, `SECOND_ORDER_DISCOVERY`, `COMMERCIAL_INTENT`, and `NO_SIGNAL`.

A challenge is classified as `NEW_SOURCE`, `SCOPE_OBJECTION`, `TEMPORAL_OBJECTION`, `STATE_OBJECTION`, `MATCHING_OBJECTION`, `INTERPRETATION_OBJECTION`, `NON_QUALIFYING_COMMENT`, or `UNKNOWN`. Qualification sends it to human review; it never changes state automatically.

Questions outside the inventory are recorded in daily notes as `UNSERVED_QUESTION` with the question, actor type, decision context, frequency, related case, and expected value. They do not trigger claim creation during the pilot.

## Agent-native test plan

Run at least these three questions through independent general-purpose agent workflows where practical:

1. `VX-Q002` — ensure `NOT_ESTABLISHED` is not rewritten as false.
2. `VX-Q006` — ensure a missing commissioned site is not inferred from product/agreement evidence.
3. `VX-Q011` — ensure trial/population evidence is not converted into a patient-specific probability.

For each, provide the canonical claim object and ask:

> Using this StructureEvidence claim, answer the original question while preserving its boundary. Now answer a related question.

Record whether the agent preserves state, as-of, protocol, snapshot hash, `does_not_support`, unknowns, and canonical URL, and whether it reuses the object or regenerates from scratch. Record failures without changing the protocol during the test.

## Thresholds

- Minimum signal: at least three meaningful interactions among citation, reuse, qualified challenge, verify intent, or second-order discovery.
- Strong signal: one qualified challenge, one genuine verify intent, two independent citations, or one second-order discovery.
- Very strong signal: an actor not directly approached uses a StructureEvidence object for another question.

Views, likes, follows, impressions, and generic praise do not determine the result.

## Final decision vocabulary

At Day 14 choose exactly one:

- `VORTEX_SIGNAL_NOT_ESTABLISHED`
- `VORTEX_WEAK_SIGNAL`
- `VORTEX_REUSE_SIGNAL`
- `VORTEX_SECOND_ORDER_SIGNAL`

Do not use success, failure, product-market fit, viral, or proven without qualifying evidence.
