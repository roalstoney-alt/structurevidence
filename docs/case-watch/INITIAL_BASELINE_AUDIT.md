# Daily Case Watch initial baseline audit

Audit date: 2026-09-29
Repository entry SHA: `2356c9327ba5b40995435eca952edd706fd944fc`

## Scope and controls

This audit covers only the three frozen case IDs in the operating workflow. It did
not perform external research, mutate a public case, create a new public case, or
change CML v1.1, RDL, publication-control, or frozen evidence history. Existing
unrelated working-tree changes were left untouched.

## Required case inventory

| Case | Public surface | Current public version | Knowledge cutoff | State snapshot | Stop point | Publication control |
|---|---|---|---|---|---|---|
| `CML-PDRE-001` | Present in root and docs | Unversioned public projection | `2026-09-20T10:46:47Z` | Missing public `state-v*.json` | Missing versioned `stop-v*.html` | Present |
| `SE-BESS-SODIUM-001` | Present in root and docs | `v0.1` | `2026-09-24` | Present and mirrored | Missing versioned `stop-v*.html` | Missing |
| `SE-ONC-NSQNSCLC-CN-001` | Missing | Missing | Expected `2026-09-28`, not verifiable | Missing | Missing | Missing |

The CML case also has a canonical internal v0.1 record, but this is not treated as a
versioned public snapshot. Its existing publication-control record authorizes an
active public projection while explicitly preserving the historical canonical state.

## Root/docs parity

- Existing 800VDC root/docs pages: `PASS` (identical SHA-256).
- Existing sodium-ion root/docs page and state v0.1: `PASS` (identical SHA-256).
- Required three-case public inventory: `FAIL` because the NSCLC case is absent.
- Versioned-snapshot requirement: `FAIL` because the 800VDC public state snapshot and
  both required stop-point artifacts are absent.

Overall `ROOT_DOCS_PARITY` is reported as `FAIL` for the required controlled set. This
does not mean that the two existing mirrored surfaces drift from each other.

## Backfill result

The repository-local, L0 reuse scan found no qualifying evidence collected after the
audited cutoffs. This means `NOT FOUND WITHIN DEFINED SEARCH SCOPE`; it does not mean
that no later evidence exists. No synthetic daily observation was created.

The NSCLC case requires the minimum baseline evidence listed in the weekly candidate
before its state can be compared. Recommended level: `L1_VERIFY`, only after
`AUTHORIZE_VERIFICATION`.

## Publication gate

The generated weekly manifest has `publication_approved: false` for every case and
`human_decision: PENDING`. Therefore no public file, sitemap, public state, or deploy
target may be changed by this execution.
