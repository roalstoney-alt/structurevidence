# StructEvidence — Meta-Verification & Method Challenge Principle

**Principle ID:** `SE-META-VERIFICATION-001`  
**Version:** `v0.1`  
**Status:** `DRAFT_PENDING_HUMAN_REVIEW`  
**Proposed:** 2026-11-03  
**Scope:** Research governance, verification method audits, Codex/agent reviews, bounded evidence cases, prospective method changes and publication decisions.  
**Nature:** Additive operating principle; methodology effectiveness is a **research hypothesis**, not an established result.  
**Related controls:** `SE-ENG-HISTORY-001`, `SE-APPEND-ONLY-CORRECTION-001`, current RDL research authorization rules and GDR-SE release gates.

> **The verifier must remain verifiable, including the method by which it verifies.**  
> A verifier's authority is bounded by its evidence, scope, test conditions, time and governance; it does not arise from a higher position in a review hierarchy.

This supplements, but does not replace, the product position:

> **Verify Your Verify — Lower the cost of knowing what you can trust.**

## 1. Why this addition is necessary

SE presents time-bounded, citable evidence states. RDL stands behind SE as a research-governance and verification-process review layer. The next question is whether **RDL's own method** is capable of detecting its errors. A higher reviewer, another agent, more agreeing models or an internally consistent evidence chain does not automatically establish the correctness or independence of that method.

The nested-dream/director analogy motivates a question, **not evidence about the world**: if an observer audits one level, what validates the observer's assumptions? Adding a still-higher observer repeats the question. There is no automatic epistemic privilege from nesting or authority. The operational solution is not an infinite chain of agents: expose each method to challenges that can differ in provenance, measurement, method and time; preserve the limits of each challenge.

This principle does **not** claim that a final, infallible verifier is logically impossible in every imaginable formal system. It does not infer practical engineering facts directly from cinematic analogy or philosophical arguments.

## 2. Architecture and authority boundaries

| Actor/layer | Function | Not authorized by this principle |
|---|---|---|
| **SE — verifier interface** | Present evidence, counterevidence, unknowns, scoped state, cutoff and change lineage | Declare unconditional truth or select the customer's decision |
| **RDL — method/process scrutiny** | Examine how SE's evidence was selected, tested, challenged and stopped; evaluate research allocation and method limits | Self-certify its own correctness or convert a method hypothesis into a verified outcome |
| **Independent challenge pathways** | Replication, outside evidence, disconfirming examples, alternate instruments, differently sourced observations | Receive automatic superior authority solely for being external |
| **GDR-SE** | Downgrade, abstain or veto release when gates fail | Upgrade incomplete evidence to authorization |
| **Responsible human/authorized actor** | Own risk acceptance, scope, correction and final decision/publication authority | Rewrite the original immutable historical observation |

**The method is an object of verification.** The internal RDL review is one line of scrutiny, not a final judge of RDL.

## 3. Binding operating invariants

1. **Higher layer ≠ independent verification.** Shared datasets, prompts, assumptions, instruments, source originators and common model families must be mapped. Multiple agents agreeing on the same premises are not independent evidence.
2. **Method validity ≠ verifier output.** A `PASS` within selected tests cannot be advertised as universal correctness, complete safety, improved accuracy or production readiness.
3. **Method self-consistency ≠ reality correspondence.** Check the method against independently observable outcomes, negative controls, falsifiers and external reproduction where available. An external observation is itself fallible; state its measurement limitations.
4. **Temporal correction is mandatory.** Reopen when qualifying new evidence, contradictory outcomes, discovered common-mode error, revised instrumentation or material scope drift arises. Preserve original method version, assumptions, test design, false positives/negatives and the old stop point.
5. **No forced novelty or forced advantage.** `NO_DISTINCT_CONTRIBUTION`, `CHALLENGE_INCONCLUSIVE`, `METHOD_LIMIT_UNRESOLVED` and `NO_DEMONSTRATED_ADVANTAGE` are acceptable **research annotations**, not additions to public evidence-state enums.
6. **Verification cost is measured, not presumed.** Added reviewer count, agent threads, deeper gates and longer research must demonstrate decision-relevant benefit or be justified by a separate compliance/safety obligation. Account for model/tool spending, time, human review, delay, error correction and maintenance; unmeasured remains `NOT_MEASURED`.
7. **Bounded stop, not permanent certification.** Define the question, risk context, accepted sources, cutoff, unresolved unknowns, applicable method version, counterfactual conditions and observable reopening triggers. A defensible-as-of-time stop is **not** an existing SE state enum nor an eternal claim of truth.
8. **No authority escalation by analogy.** Philosophical regress, formal metatheory, human judgment and the dream-layer analogy can inform test design but never, alone, prove a scientific or commercial performance claim.
9. **Research ≠ publication authority.** No challenge or draft creates permission to publish, change paid delivery, authorize outreach, edit protected historical records, run a new automated task, or modify a production state.
10. **Append, don't erase.** A discovered methodological defect creates a new linked method-audit/correction artifact. Original source bytes, review IDs, model inputs, test outcomes and method conclusions remain retrievable within legal/privacy limits.

## 4. Three complementary challenge directions

- **Upward — method scrutiny:** Inspect criteria, threshold choice, source selection, counterevidence search, assumptions and reviewer/test-fixture failure.
- **Outward — independent reality challenge:** Test with independently sourced observations, held-out cases, alternative tools, reproducible local experiments, external critiques and disconfirming conditions. Record residual common-mode dependencies.
- **Across time — prospective revalidation:** Follow explicit triggers, new evidence and change events; compare with the frozen earlier stop point without rewriting it.

An apparently independent challenge is not sufficient if it merely republishes the same originator, shares the same unexamined premise or uses the same measurement defect.

## 5. Trigger-based meta-verification workflow

`TRIGGER -> FREEZE_METHOD_AND_RESULT -> DEFINE_SCOPE -> MAP_SHARED_DEPENDENCIES -> STATE_FALSIFIERS -> CHOOSE_INDEPENDENT_CHALLENGE -> OBSERVE -> COMPARE_WITH_BASELINE -> MEASURE_COST -> APPEND_METHOD_AUDIT -> REASSESS_STOP -> HUMAN_GATE_IF_PUBLIC`

Trigger examples: disputed SE claim, conflicting source, independent replication failure, a testing-tool/fixture defect, repeated `PASS` despite observed failure, method drift, unexplained verifier disagreement, or a justified periodic method review.

- **Freeze:** Record exact method version/commit, challenge ID, prior claims, bounded original sources and hashes when available.
- **Challenge:** State **before interpreting results** what observation could refute the method's current assertion. Record evidence originator and dependencies.
- **Observe:** Distinguish `NOT_RUN`, `SOURCE_UNAVAILABLE`, `INCONCLUSIVE`, observed failure and reproducible success. Do not convert missing evidence into a negative event.
- **Compare:** If evaluating value, use an ordinary verifier or existing method as a baseline with matched questions and comparable acceptance conditions. Record false acceptance, false rejection, time-to-detect, time-to-correct and end-to-end cost where measurable.
- **Stop or reopen:** Declare a bounded audit observation and specific next trigger. A method audit does not silently change a previously approved SE claim or public state.
- **Release:** Any public projection or protocol/schema change must pass existing GDR-SE, privacy/legal and human gates; website-first and social-publication rules remain untouched.

### Minimal supplemental method-audit record

```yaml
audit_id: unique_new_id
principle_id: SE-META-VERIFICATION-001
audit_type: METHOD_CHALLENGE
record_status: DRAFT | REVIEWED | HOLD
method_ref: { version: string, commit_or_digest: string }
audited_verifier: SE | RDL | OTHER
question_and_scope: string
knowledge_cutoff: string
prior_stop_point_ref: string
source_dependency_map: []
independence_limits: []
falsifier_or_negative_control: string
challenge_procedure_ref: string
observation_status: NOT_RUN | SOURCE_UNAVAILABLE | INCONCLUSIVE | OBSERVED
observed_result: string
result_limitations: []
competing_explanations: []
unknowns_remaining: []
cost: { tool_usd: NOT_MEASURED, human_minutes: NOT_MEASURED, elapsed_minutes: NOT_MEASURED }
delta_vs_baseline: NOT_MEASURED
method_effectiveness: UNDETERMINED
reopen_conditions: []
correction_or_supersession_ref: null
public_release_approved: false
```

These are recommended **supplemental audit fields**, **not** an instruction to migrate schemas, change existing state vocabulary or modify the machine-readable method contract.

## 6. Falsifiable pilot before any effectiveness claim

Pilot `RDL-META-VERIFICATION-001` is a proposed **offline method experiment**, not authorization to run a new automation or publish a new case.

Use three contrasting challenge classes with frozen fixtures and explicit cost measurement:

1. **Shared-source consensus:** Several agents agree because they depend on one originator; test whether the method preserves dependence rather than counting apparent agreement as validation.
2. **Verifier vs test-fixture defect:** Inject a fixture conflict and a separate actual implementation fault; test whether the audit identifies their different causes without weakening the underlying guard.
3. **Independent, delayed counterevidence:** Introduce dated, independently obtained evidence after a prior bounded stop; verify append-only correction, real time semantics and absence of retrospective rewriting.

For each case compare a declared baseline review against the meta-verification method, measuring newly detected *material* defects, false positives, time to defensible stop, human involvement, cost and unresolved limitations. A duplicated opinion is not new evidence; an untested design is not a reproduced result. Preserve negative pilots.

**Null outcome is permitted:** No independently shown accuracy/cost benefit means `NO_DEMONSTRATED_ADVANTAGE`. A mandatory compliance review may still be justified separately; explain that basis.

## 7. Non-regression and adoption gate

This addition MUST NOT:
- Rewrite or supersede prior method papers, frozen decisions, evidence snapshots, claims, source captures, evidence-state enums, research schema, GDR-SE outcome enums or historical hashes.
- Assert that RDL, SE or any AI is infallible; create a permanent `Meta-Verifier` role; or confer rating/scoring/decision authority.
- Modify automatic daily tasks, the 22:00 unified workflow, X/LinkedIn posting, paid delivery, customer outreach, production deployment or website content without separate human authorization.
- Expose private RDL, research, security or user information in public documents.

**Adoption:** This file is a reviewable policy proposal until a separate human-approved merge/release decision. Future machine-contract registration or enforcement tests require a distinct reviewed change after compatibility checks and root/docs parity checks. No new outcomes or empirical gains are claimed.

**Acceptance receipt for implementation work:**

```text
PRINCIPLE_ID=SE-META-VERIFICATION-001
VERSION=v0.1
METHOD_AUDIT_IMPLEMENTED=NO
PILOT_RESULT=NOT_RUN
OLD_METHOD_CONTRACT_CHANGED=NO
HISTORICAL_RECORDS_CHANGED=0
EXISTING_STATE_ENUM_CHANGED=NO
EXISTING_GDR_GATES_CHANGED=NO
EXTERNAL_POSTS_SENT=0_UNLESS_SEPARATELY_AUTHORIZED
PRODUCTION_DEPLOYMENT=NO
HUMAN_GATE_REQUIRED=YES
```
