# SE-CEPE-001 product issue backlog

STATUS = `ONE_REPRODUCED_PILOT_INFRASTRUCTURE_ISSUE`

SITE_OR_API_STATUS = `NO_REPRODUCED_PRODUCT_ISSUE`

## SE-CEPE-ISSUE-001

```yaml
issue_id: SE-CEPE-ISSUE-001
observed_problem: A successful retrieval is classified NO_MATERIAL_CHANGE without comparing its content hash with the prior successful task observation.
evidence_or_reproduction: SE-CEPE-20261013T090308Z produced changed WHO hashes for SE-TECP-007 and SE-TECP-008 while assigning NO_MATERIAL_CHANGE; the postcheck reproduced both new hashes.
affected_route_or_task: scripts/run_se_cepe_001.py and SE-TECP-007/008
user_cost_hypothesis: A potentially material source revision could be missed until manual review.
smallest_fix: Compare each successful task retrieval with its previous successful content hash and emit INTERPRETATION_REVIEW_REQUIRED when bytes change.
expected_effect: Source-version changes fail closed into semantic review without changing a claim automatically.
rollback_steps: Revert only the isolated runner patch; retain all append-only run and audit records.
required_tests: Add stable-hash and changed-hash fixtures, rerun SE-CEPE and protected case regressions.
rights_and_privacy_impact: None; public-source hashes and bounded metadata only.
approval_gate: HUMAN_REVIEW_REQUIRED
```

At most one independently testable low-risk change may be implemented per
week, and only after reproduction and human review. No change is an acceptable
weekly result.
