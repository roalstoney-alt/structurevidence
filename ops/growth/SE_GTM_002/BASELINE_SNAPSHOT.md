# SE-GTM-002 baseline snapshot

BASELINE_SHA = `b53abeedbf2926f90ef6acad59563132fddcc8fc`

AUTHORITATIVE_BRANCH = `origin/main`

PILOT_BRANCH = `codex/se-gtm-002-decision-pressure-pilot`

CAPTURE_DATE = `2026-10-11` Asia/Shanghai

## Reused implementations

- CML public technical records:
  `technical-risk/records/`
- CML opportunity-validation records:
  `technical-risk/records/*/opportunity-validation/`
- RDL research and freshness policies:
  `rdl/`, `whitepapers/RDL/`
- Claim Intake:
  `protocol/question-intake/`, `research-snapshot/v0.1/protocol/question-intake/`
- Decision Memory:
  `evidence/decision-memory/`
- Decision Pack:
  `decision-pack/`, `deploy/cloudflare-landing/commercial-upgrade.js`

No reused file was edited.

## Baseline validation

Passing:

- `scripts/test_decision_memory_v01.py`
- `scripts/test_public_commercial_boundary.py`

Pre-existing failures on baseline:

- `scripts/test_cml_v01.py`: 33 PASS, 6 FAIL, 1 NOT_EVALUATED.
- `scripts/test_cml_v11_regression_harness.py`: historical-mutation
  assertions fail for previously changed CML files.
- `scripts/test_rdl_research_record.py`: one failure caused by the same
  historical-mutation assertion.
- `scripts/test_customer_intake_phase_b.py`: one stale protected-surface
  expectation still requires the former `/verify/` CTA on the current .org
  homepage.

SE-GTM-002 does not modify those baselines or weaken their assertions.
