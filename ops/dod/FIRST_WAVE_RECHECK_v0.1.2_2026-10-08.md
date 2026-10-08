# SE-DOD-001 — first-wave recheck under protocol v0.1.2

REVIEW_DATE = 2026-10-08 Asia/Shanghai

PUBLIC_PRIVATE_BOUNDARY = Public sources reviewed; all private states remain UNKNOWN

MESSAGES_ACTUALLY_SENT = 0

Q0 must be run again immediately before any human send authorization. The results below are point-in-time review evidence only.

## OR-001 — CATL

Q0_FRESHNESS_RECHECK = PASS

FRESHNESS_NOTE = Later CATL disclosure adds a 30 MWh configuration, stated 95 percent round-trip efficiency, and IEC/UL/CE certifications. It does not establish customer acceptance or delivered volume, so the core state does not materially change.

Q1_ACTIVE_DECISION = PASS

Q2_MATERIAL_GAP = PASS

Q2B_OBSERVABLE_NOW = PASS

Q3_PUBLIC_PRIVATE_BOUNDARY = PASS

Q4_NAMED_OWNER = FAIL

Q5_VERIFIED_ROUTE = PASS

Q5B_ROUTE_PURPOSE_FIT = ROUTABLE

Q6_NO_INTERNAL_INFERENCE = PASS

Q7_ONE_BOUNDARY = PASS

Q8_ONE_ASK = PASS

Q9_MATCHING_ASSET = PASS

FINAL_RECOMMENDATION = HOLD

REASON = The reviewed public record still does not establish a person accountable for the exact order acceptance or China delivery decision.

## OR-002 — Nocera

Q0_FRESHNESS_RECHECK = PASS

FRESHNESS_NOTE = The latest reviewed SEC filing continues to describe the INERGX transaction as a non-binding LOI subject to diligence and definitive documentation, and says it has not been completed.

Q1_ACTIVE_DECISION = PASS

Q2_MATERIAL_GAP = PASS

Q2B_OBSERVABLE_NOW = PASS

Q3_PUBLIC_PRIVATE_BOUNDARY = PASS

Q4_NAMED_OWNER = PASS

Q5_VERIFIED_ROUTE = PASS

Q5B_ROUTE_PURPOSE_FIT = DIRECT

Q6_NO_INTERNAL_INFERENCE = PASS

Q7_ONE_BOUNDARY = PASS

Q8_ONE_ASK = PASS

Q9_MATCHING_ASSET = PASS

MESSAGE_REFRESH = COMPLETE — the message now reflects the latest filing and addresses Andy Jin through the direct clarification route published in the LOI.

FINAL_RECOMMENDATION = SEND_AFTER_NEW_Q0_AND_HUMAN_AUTHORIZATION

## OR-003 — Beam Global

Q0_FRESHNESS_RECHECK = REOPEN

OLD_STATE = Non-binding LOI for an unidentified European drone company, subject to diligence and definitive agreements.

NEW_EVIDENCE = Beam announced an executed Share Purchase Agreement to acquire ScoutDI and disclosed the target, approximately USD 24 million purchase price, financing commitments, named customers, intended manufacturing transfer, and earnout terms.

NEW_STATE = Definitive SPA executed; LOI-based evidence boundary and message are superseded. Transaction close and successful transfer remain unestablished.

STATE_TRANSITION_DATE = 2026-10-07

Q1_ACTIVE_DECISION = PASS

Q2_MATERIAL_GAP = PASS

Q2B_OBSERVABLE_NOW = PASS

Q3_PUBLIC_PRIVATE_BOUNDARY = PASS

Q4_NAMED_OWNER = PASS

Q5_VERIFIED_ROUTE = PASS

Q5B_ROUTE_PURPOSE_FIT = ROUTABLE

Q6_NO_INTERNAL_INFERENCE = PASS

Q7_ONE_BOUNDARY = PASS

Q8_ONE_ASK = PASS

Q9_MATCHING_ASSET = PASS

FINAL_RECOMMENDATION = REOPEN

SEND = PROHIBITED

## OR-004 — Vertiv

Q0_FRESHNESS_RECHECK = PASS

FRESHNESS_NOTE = The reviewed official record still describes an acquisition agreement awaiting regulatory approvals, customary conditions, and expected Q4 2026 closing.

Q1_ACTIVE_DECISION = PASS

Q2_MATERIAL_GAP = FAIL

Q2B_OBSERVABLE_NOW = FAIL

OBSERVABILITY_CLASS = FUTURE_OBSERVABLE

Q3_PUBLIC_PRIVATE_BOUNDARY = PASS

Q4_NAMED_OWNER = PASS

Q5_VERIFIED_ROUTE = PASS

Q5B_ROUTE_PURPOSE_FIT = ROUTABLE

Q6_NO_INTERNAL_INFERENCE = PASS

Q7_ONE_BOUNDARY = PASS

Q8_ONE_ASK = PASS

Q9_MATCHING_ASSET = PASS

FINAL_RECOMMENDATION = HOLD

REASON = The current message relies too heavily on realized post-close integration, customer outcomes, and earnout performance that should not yet exist before closing.

## OR-005 — ABB

Q0_FRESHNESS_RECHECK = PASS

FRESHNESS_NOTE = No later official close, correction, or retraction was identified in the reviewed boundary. ABB's current public “up to 99 percent efficiency” claim remains the relevant evidence boundary.

Q1_ACTIVE_DECISION = PASS

Q2_MATERIAL_GAP = PASS

Q2B_OBSERVABLE_NOW = PASS

Q3_PUBLIC_PRIVATE_BOUNDARY = PASS

Q4_NAMED_OWNER = PASS

Q5_VERIFIED_ROUTE = PASS

Q5B_ROUTE_PURPOSE_FIT = ROUTABLE

Q6_NO_INTERNAL_INFERENCE = PASS

Q7_ONE_BOUNDARY = PASS

Q8_ONE_ASK = PASS

Q9_MATCHING_ASSET = PASS

MESSAGE_REFRESH = COMPLETE — the message addresses ABB Investor Relations as a routing function and limits the ask to the current efficiency claim's test boundary.

FINAL_RECOMMENDATION = SEND_AFTER_NEW_Q0_AND_HUMAN_AUTHORIZATION

## Result

SEND_RECOMMENDATIONS = OR-002, OR-005

HOLD = OR-001, OR-004

REOPEN = OR-003

SEND_EXECUTED = NO
