# DPAL v0.3 human review queue

STATUS = `HUMAN_REVIEW_REQUIRED`

OUTREACH_SENT = `0`

No marketing message is drafted. The following are research decisions, not
approved recipients.

| Candidate | Why retained | Blocking facts | Recommendation |
|---|---|---|---|
| GoDaddy | Final FTC order explicitly requires an independent assessor | Next assessment date, incumbent, open scope, purpose-fit route | RESEARCH_FURTHER |
| Marriott | Final FTC order defines a strong third-party assessment boundary | Next assessment boundary, incumbent, distinct StructEvidence scope, purpose-fit route | RESEARCH_FURTHER |
| Apotex | FDA expressly requested independent investigation and CAPA assessments | Current status, assessor engagement, remaining scope, purpose-fit route | REOPEN_FRESHNESS |
| TTI / TE PCN P-25-027928 | Concrete named distributor relation and downstream notification duty | Named affected end customer, current unresolved decision, independent need | REOPEN_FRESHNESS |
| Super Micro | Current 2026 filing verifies governance pressure and unresolved ICFR weakness | Unfilled scope outside incumbent audit, purpose-fit route, buyer demand | HOLD |

## Partner gate

- Rochester Electronics: `RESEARCH_ONLY_HOLD`; complementary decision-memory
  hypothesis is not yet a specific opportunity.
- TTI: `RESEARCH_ONLY_HOLD`; the PCN example supports channel observability but
  not an open customer requirement.
- SiliconExpert: `COMPETITIVE_HOLD`; substantial capability overlap.
- SGS: `HOLD`; no specific non-overlapping opportunity.
- Intertek: `HOLD`; no specific non-overlapping opportunity.

## Human decision

Choose one of:

1. authorize a bounded freshness-and-procurement-state recheck for GoDaddy,
   Marriott and Apotex, without contact;
2. authorize research for a named affected end customer behind the TTI PCN,
   without inferring private BOM data;
3. stop partner research and retain the zero-conversion result.

Any outbound message still requires separate approval for one exact recipient,
one purpose-fit route and one final message.
