# SE-GTM-002 outreach review queue

STATUS = `HUMAN_REVIEW_REQUIRED`

OUTREACH_SENT = `0`

## Pipeline A — direct

No direct candidate is send-ready.

| Candidate | Score | Gate result | Action |
|---|---:|---|---|
| SE-GTM-002-CAND-001 | 70 | HOLD — no named affected company, active decision or route | Research further or stop |
| SE-GTM-002-CAND-002 | 72 | HOLD — no named affected company, active decision or route | Research further or stop |
| SE-GTM-002-CAND-003 | 58 | HOLD — no named affected company, urgency or route | Research further or stop |
| SE-GTM-002-CAND-004 | 45 | REJECT — no actual RFQ or buyer | Retain as negative control |

No Decision Blocker Brief was instantiated because no candidate passed every
qualification gate.

## Pipeline B — partners

These are research candidates, not approved recipients.

| Partner | Purpose-fit route | Review question |
|---|---|---|
| TTI | ROUTABLE official contact page | Does StructEvidence add a decision-state layer beyond existing EOL customer workflows? |
| Rochester Electronics | ROUTABLE official contact form | Is a bounded evidence brief useful before lifecycle-extension or replacement discussions? |
| SiliconExpert | ROUTABLE official sales route | Is the method complementary, overlapping or competitive with existing BOM-risk intelligence? |
| SGS | ROUTABLE service contact | Could a pre-audit evidence-boundary brief improve vendor-assessment scoping? |
| Intertek | ROUTABLE service contact | Could a structured Stop-Point reduce ambiguity before technical supplier audits? |

## Send gate

Before any message:

1. Recheck current capability and contact-route evidence.
2. Identify the exact receiving function honestly.
3. Prepare one boundary and one ask.
4. Obtain explicit human approval for the exact organization, route and copy.
5. Record authorization in a new append-only event.

Until then, `SEND = PROHIBITED`.
