# Legal remediation baseline

- Actual base SHA: `bfeeae97babd6a245faf9b0bdee4109dd6d2417c`
- Captured at: `2026-10-08T12:05:12+08:00`
- Branch: `legal-boundary-remediation-20261008`
- Repository: `roalstoney-alt/structurevidence`
- Source audit SHA-256: `4fc3c67580fa96ce0fa11eeb830ad72132a02b8b4454f458e0fe77dd558666cd`
- Execution workflow SHA-256: `7f86c24a490ad0e6b3cfee9721af1bf7b377cb94aca0c16a2c4fc81c865917ad`
- Review memo: `MISSING_INPUT` (`StructEvidence_Legal_Rectification_Review_CN.md` was not found)
- Applicable instruction: `StructEvidence_Codex_Legal_Remediation_Workflow_CN.md`
- Production deployment authorization: `NO`

## Verification labels

`SOURCE_VERIFIED` means the cited repository source or supplied audit file was read and its hash recorded. It does not establish the accuracy of facts stated by an external publisher.

`PRODUCTION_VERIFIED` requires an authorized post-deployment check of the actual deployed SHA, status code, and response body. No production check was authorized in this task, so `PRODUCTION_VERIFIED = NOT_PERFORMED`.

Existing deployment records are evidence that a deployment action occurred, not proof that current live copy matches this branch.

## Baseline test observations

Before remediation, the focused Python suite passed case review, case-watch, Irkutsk publication/alias, public-commercial boundary, i18n, and readiness checks. Existing failures were observed in public-case snapshot parity, the English-surface CJK scan, and the single-origin assertion in `test_commercial_domain_split.py`. They are tracked separately from branch-introduced regressions.
