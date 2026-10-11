# FDE Decision Clearance Pack v0.1

STATUS = `SYNTHETIC_DEMONSTRATION`

PRODUCTION_USE = `PROHIBITED`

CERTIFICATION_OR_SECURITY_APPROVAL = `NOT_PROVIDED`

## 1. Demonstration boundary

This pack demonstrates how a bounded evidence record could support an
enterprise decision about an AI-agent PoC. There is no authentic customer,
deployment, private dataset or enterprise test result behind it.

The fictitious names, thresholds, volumes, dates and test IDs below are
invented scenario parameters. The public references only establish that FDE
work commonly covers discovery, scoping, evaluation, security/governance and
production deployment. They do not validate this synthetic agent.

## 2. Customer decision

SYNTHETIC_DECISION_ID = `FDE-DC-SYN-001`

Decision: whether a fictional enterprise, `ExampleCo`, should authorize a
limited production trial of an AI contract-intake assistant after PoC review.

Decision owner: ExampleCo Director of Legal Operations, with separate technical
and security approvals.

Evidence cutoff: `2026-10-11T20:42:33+08:00`.

## 3. Synthetic deployment scope and assumptions

- The assistant reads synthetic, non-confidential supplier agreements.
- It proposes normalized fields and risk flags for human review.
- It cannot sign, send, approve or alter a contract.
- All tool calls are allowlisted and logged.
- A human must approve every record before export.
- The PoC uses 200 invented test documents; this is a scenario value, not an
  observed dataset.
- No production customer, employee or supplier data is used.

## 4. Claims requiring verification

| Claim ID | Normalized claim | Current state | Why |
| --- | --- | --- | --- |
| FDE-DC-SYN-001.SCOPE_BOUNDARY | The assistant is technically prevented from autonomous contract approval or external transmission. | NOT_ESTABLISHED | A design statement exists in the scenario, but no executable policy or adversarial test result exists. |
| FDE-DC-SYN-001.FIELD_EXTRACTION | The assistant reaches at least 95% field-level precision on the agreed synthetic evaluation set. | UNKNOWN | No test has been run. |
| FDE-DC-SYN-001.RISK_RECALL | The assistant reaches the customer-defined minimum recall for critical risk flags. | UNKNOWN | The threshold and labeled evaluation have not been accepted by the customer. |
| FDE-DC-SYN-001.PROVENANCE | Every proposed field and flag can be traced to a source span, model/version and evaluation event. | NOT_ESTABLISHED | Required schema is described but no output log exists. |
| FDE-DC-SYN-001.ACCESS_CONTROL | Customer identity, authorization and logging requirements are satisfied. | NOT_ESTABLISHED | Customer-specific control evidence is absent. |
| FDE-DC-SYN-001.BUSINESS_IMPACT | The assistant reduces contract-intake review cost without unacceptable quality loss. | UNKNOWN | No baseline or comparable outcome has been measured. |

## 5. Existing public reference evidence

| Evidence ID | Public source | Supports | Does not support |
| --- | --- | --- | --- |
| FDE-PUB-001 | <https://openai.com/careers/forward-deployed-engineer-%28fde%29-seattle-seattle/> | FDE engagements may span discovery, scoping, system design, build, rollout and eval-driven feedback. | Any ExampleCo result or customer acceptance. |
| FDE-PUB-002 | <https://www.aboutamazon.com/news/aws/aws-1-billion-forward-deployed-ai-engineers> | AWS describes FDE collaboration with customer business, engineering and security teams using customer data, governance and processes. | Security approval for this synthetic system. |
| FDE-PUB-003 | <https://www.atlassian.com/enterprise/success/fde> | Permissions, guardrails, audit trails and human oversight are relevant to production FDE work. | That this synthetic system implements those controls. |

COUNTEREVIDENCE = `NONE_OBSERVED_BECAUSE_NO_SYSTEM_EXISTS`

That absence is not positive evidence. The entire demonstration remains
non-operational.

## 6. Required customer-specific tests

1. Freeze an approved labeled evaluation set and acceptance thresholds.
2. Run field-level precision and critical-risk recall tests, including
   stratification by contract type and failure mode.
3. Attempt unauthorized sign, send, modify and external-transfer actions.
4. Verify tenant, role, token, logging and retention behavior in the actual
   customer environment.
5. Trace each output to source span, configuration, model and test version.
6. Run human-review usability and override tests with responsible operators.
7. Define baseline review cost and compare like-for-like work without removing
   quality controls.
8. Document rollback, incident escalation and owner acceptance.

## 7. Reusable versus customer-specific evidence

Reusable core:

- normalized claim definitions;
- product and model version;
- generic architecture and allowed-action policy;
- evaluation harness and dataset-construction procedure;
- generic failure taxonomy;
- change log and known limitations.

Customer-specific overlay:

- data fields, document types and risk definitions;
- actual access-control mapping;
- accepted evaluation set and thresholds;
- environment, integration and retention configuration;
- business baseline and outcome evidence;
- authorized decision owners and final acceptance.

## 8. Critical stop-points

STOP if any of the following applies:

- the customer cannot lawfully provide the required evaluation material;
- critical-risk labels or acceptance thresholds are not agreed;
- autonomous actions cannot be technically bounded;
- private context would enter a public evidence record;
- security or governance reviewers are unavailable;
- the efficiency case depends on removing human review or other safeguards;
- a result is generalized beyond the tested product version, data or
  environment;
- accreditation or certification is required beyond StructEvidence authority.

## 9. Responsibility map

| Decision element | Responsible role |
| --- | --- |
| Workflow and outcome definition | Customer process owner |
| Build and remediation | FDE provider |
| Test-set and metric acceptance | Customer process owner plus independent reviewer if required |
| Security and data controls | Customer security / GRC |
| Commercial terms | Customer procurement / legal and FDE provider |
| Evidence normalization | StructEvidence, if separately engaged |
| Final deployment authorization | Customer decision owner |

## 10. Next observable events

- acceptance criteria approved;
- synthetic test set frozen and hashed;
- first evaluation completed;
- control tests completed;
- exception remediation recorded;
- decision owner accepts, rejects or limits the trial.

## 11. Versioned evidence-change log

| Version | Date | Change | Claim-state effect |
| --- | --- | --- | --- |
| v0.1 | 2026-10-11 | Synthetic pack structure created; no system evidence added. | None; all claims remain UNKNOWN or NOT_ESTABLISHED. |
