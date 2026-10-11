# SE-GTM-005 v0.2 — Competitor and Substitute Assessment

STATUS = `RESEARCH_ONLY`

## Direct and adjacent substitutes

| Substitute | Public capability | Where it may replace StructEvidence | Remaining possible gap |
| --- | --- | --- | --- |
| Provider's own FDE practice | Discovery, architecture, build, evals, controls, deployment and handover | Produces evidence inside the engagement with full technical context. | Provider-authored evidence may not satisfy an independent-review requirement. |
| Model/platform vendor FDE | OpenAI, AWS, Palantir and Atlassian combine product knowledge with deployment support. | Deep access to product roadmaps, tooling and controls. | Vendor independence and portability across stacks may be limited. |
| Systems integrator / consultancy | Strategy, transformation, systems integration, GRC and managed delivery. | Can bundle evidence and approval work into a larger program. | May be too broad or expensive for one bounded verification question. |
| Customer security and GRC tools | Questionnaires, control mappings, access reviews, audit logs and policy workflows. | Strong for compliance/control evidence and accountable approvals. | Often weaker on claim-level technical evidence and temporal interpretation. |
| Evaluation / observability platforms | Test runs, model metrics, traces and production monitoring. | Primary source for technical behavior and regression evidence. | Does not by itself resolve business relevance, source rights or decision ownership. |
| Contract acceptance artifacts | SOW, acceptance criteria, sign-off and service credits. | Binding customer-specific decision record. | Usually not reusable and may omit public evidence provenance/counterevidence. |
| Manual evidence pack | Documents, spreadsheets, tickets and presentations. | Low tooling cost and already familiar. | Version drift, provenance gaps and repeated preparation may remain. |
| Certification / audit provider | Accredited or recognized independent assurance. | Required when formal certification or audit opinion is needed. | StructEvidence must not substitute for authority it does not possess. |

## Named market anchors

- Palantir's FDE model is mature and integrated with its platforms:
  <https://www.palantir.com/careers/open-positions/>
- OpenAI FDEs own end-to-end deployments and work with GRC and security:
  <https://openai.com/careers/forward-deployed-engineer-%28fde%29-seattle-seattle/>
- AWS embeds FDEs with business, engineering and security teams:
  <https://www.aboutamazon.com/news/aws/aws-1-billion-forward-deployed-ai-engineers>
- Atlassian includes permissions, guardrails, audit trails and human oversight:
  <https://www.atlassian.com/enterprise/success/fde>
- Entrans publicly offers model evaluation, security validation and audit logs:
  <https://www.entrans.ai/technologies/ai-integration>
- ADEL describes decision records and evaluation evidence as normal outputs:
  <https://www.weareadel.ai/forward-deployed-engineers>

## Positioning boundary

StructEvidence should not position this pilot as a replacement for engineering,
security review, certification, a customer's acceptance authority, or model
observability. The narrow hypothesis is that an independent, append-only,
claim-level evidence layer could reduce repeated preparation and clarification
without weakening those gates.

COMPETITIVE_ADVANTAGE_ESTABLISHED = `NO`

SUBSTITUTE_RISK = `HIGH`
