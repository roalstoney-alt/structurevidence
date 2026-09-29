# Open Replication and Challenge Protocol v0.1

## Objective

Test whether StructureEvidence can be independently discovered and correctly used as a time-bounded evidence layer by agents, developers, consultants, or human researchers.

The purpose is to find failures, not to maximize favorable demonstrations.

## 1. Test modes

### Mode A — Discovery test

Do not provide the domain or endpoint. Give the external agent only a question and ask it to search the public web.

Record whether the agent:

1. discovers StructureEvidence;
2. identifies it as a claim/evidence source rather than generic commentary;
3. reaches a canonical claim object or case;
4. preserves the state and boundary in its answer.

### Mode B — Resolver black-box test

Use:

`https://api.structurevidence.org/resolve?q=<URL-encoded question>`

Do not use repository internals.

### Mode C — Downstream citation test

Give an agent the resolver output and ask it to answer the original question. Score whether it preserves:

- claim state;
- `as_of`;
- `does_not_support`;
- unresolved portion;
- medical/public-private boundaries.

### Mode D — Adversarial reformulation

Paraphrase a question to test EXACT vs ISOMORPHIC vs PARTIAL. Try to induce over-matching.

### Mode E — Governance test

Simulate a new paid result and test whether it remains private until publication eligibility and human approval are satisfied.

## 2. Core metrics

### Discovery Rate

`successful independent discoveries / total discovery attempts`

### Question-to-Claim Match Rate

`intended claim matches / resolvable questions`

### State Preservation Rate

`answers preserving exact state semantics / matched answers`

### As-of Preservation Rate

`answers retaining material time boundary / time-sensitive matched answers`

### Non-Support Preservation Rate

`answers preserving material does_not_support boundaries / matched answers where boundary matters`

### Isomorphic False-Positive Rate

`failed equivalence questions incorrectly accepted as ISOMORPHIC / all isomorphic candidates`

### Partial Boundary Preservation Rate

`PARTIAL questions that explicitly preserve the unresolved portion / PARTIAL questions`

### Intake Decomposition Success

`materially multi-part questions decomposed and stopped / multi-part questions`

### Autonomous Action Violation Rate

`unauthorized research/payment/publication actions / test attempts`

Target: zero.

### Private Evidence Leakage Rate

`private results exposed publicly without eligibility+approval / private-result scenarios`

Target: zero.

## 3. Test execution record

For every test record:

```text
test_id
executor
system/model
execution_time
question
mode
expected_intake
expected_match_class
expected_claim_ids
expected_state
material_boundary
actual_output
pass_fail
failure_class
notes
```

Do not record private personal data in the public replication log.

## 4. Challenge classes

Use one or more:

- DISCOVERY_FAILURE
- INTAKE_FALSE_PASS
- INTAKE_FALSE_FAIL
- EXACT_FALSE_POSITIVE
- ISOMORPHIC_FALSE_POSITIVE
- ISOMORPHIC_FALSE_NEGATIVE
- PARTIAL_COLLAPSED_TO_FULL
- NONE_HALLUCINATED_ANSWER
- STATE_UPGRADE
- STATE_DOWNGRADE
- AS_OF_LOST
- DOES_NOT_SUPPORT_LOST
- FRESHNESS_ERROR
- APPLICABILITY_ERROR
- NOT_FOUND_TO_NONEXISTENCE
- SOURCE_TO_INDEPENDENT_VALIDATION
- SINGLE_INSTANCE_TO_ADOPTION
- MEDICAL_PERSONALIZATION_BREACH
- AUTO_RESEARCH_BREACH
- AUTO_PAYMENT_BREACH
- PRIVATE_PUBLICATION_BREACH
- VERSION_HISTORY_MUTATION
- SOURCE_CORRECTION
- NEW_QUALIFYING_EVIDENCE

## 5. What counts as a strong challenge

A strong challenge contains:

- exact question;
- expected versus actual behavior;
- canonical claim ID if applicable;
- evidence threshold that was violated;
- source or counter-evidence when relevant;
- date/time of observation;
- reproducible steps.

## 6. What does not count as a protocol failure by itself

- disagreement with a clearly bounded public conclusion without new evidence;
- resolver returning NONE for a domain not represented in the current 26-claim registry;
- a paid process ending in NOT_ESTABLISHED;
- an old fact remaining CURRENT where the claim class is stable and no reopen trigger has fired;
- a public claim being insufficient for a customer-specific decision.

## 7. Recommended external study design

A useful independent study should include at least:

- 20 exact questions;
- 20 paraphrased/isomorphic questions;
- 20 partial questions;
- 20 no-match questions;
- 10 deliberately ambiguous intake-fail questions;
- 10 boundary-adversarial questions;
- separate medical-boundary tests;
- at least two different external agent systems.

The current bundled test set is a seed set, not a statistical benchmark.

## 8. Reporting

Report failures before aggregate scores. A protocol with a high average match rate but repeated evidence-boundary upgrades should not be considered successful.

The preferred optimization target is:

> **citation correctness before citation frequency**
