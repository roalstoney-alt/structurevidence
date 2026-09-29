# Daily Case Watch refreshed baseline audit

Audit date: 2026-09-29
Current-main baseline SHA: `0cf2340d66c95f986f91466b8746c9e666535820`
Original workflow entry SHA: `2356c9327ba5b40995435eca952edd706fd944fc`

## Scope and controls

This audit was rerun in an isolated clean worktree after the Case Watch implementation
was applied to current `origin/main`. It covers only the three frozen case IDs. It did
not perform external research, mutate a public case, publish, deploy, or change CML
v1.1, RDL, publication-control, Decision Memory, or frozen evidence history.

## Required case inventory

| Case | Public surface | Public version | Knowledge cutoff | State snapshot | Stop point | Publication control | Decision Memory |
|---|---|---|---|---|---|---|---|
| `CML-PDRE-001` | Present | `v0.1` stop-point projection | `2026-09-20T10:46:47Z` | Missing public `state-v*.json` | `stop-v0.1.html` present | Present in CML v1.1 | Not present |
| `SE-BESS-SODIUM-001` | Present | `v0.1` | `2026-09-24` | `state-v0.1.json` present | `stop-v0.1.html` present | Missing | `decision-memory-v0.1.json` present |
| `SE-ONC-NSQNSCLC-CN-001` | Present | `v0.1` public research preview | `2026-09-28` | `state-v0.1.json` present | `stop-v0.1.html` present | Missing | Not present |

The previously reported missing NSCLC baseline and missing 800VDC and sodium-ion stop
points are obsolete and removed. The three public baselines now support bounded weekly
comparison. This does not mean the full versioned-snapshot model is complete.

## Versioned snapshot semantics

- `CML-PDRE-001`: public v0.1 stop point and current projection exist, with canonical
  publication control. A public frozen `state-v0.1.json` does not exist, so the full
  public snapshot primitive set is incomplete.
- `SE-BESS-SODIUM-001`: state, stop point, current projection, and Decision Memory v0.1
  exist. A case publication-control artifact does not exist, so the full primitive set
  is incomplete.
- `SE-ONC-NSQNSCLC-CN-001`: state, stop point, and current projection v0.1 exist. A
  publication-control artifact and Decision Memory sidecar do not exist, so the full
  primitive set is incomplete.

Overall `VERSIONED_SNAPSHOTS` is `PARTIAL`: every case has a public version, but no case
individually demonstrates every listed primitive.

## Root/docs parity

`PARITY_PASS`:

- 800VDC: `index.html`, `stop-v0.1.html`.
- Sodium-ion: `index.html`, `state-v0.1.json`, `stop-v0.1.html`,
  `decision-memory-v0.1.json`.
- NSCLC: `index.html`, `state-v0.1.json`, `stop-v0.1.html`.

`PARITY_FAIL`: none.

`NOT_MIRRORED_BY_DESIGN`: CML v1.1 canonical records, its publication-control record,
and RDL history are internal governance artifacts rather than public root/docs pairs.

Overall `ROOT_DOCS_PARITY` is `PASS` for all intended public mirrors.

## Backfill result

The repository-local L0 reuse scan found no qualifying evidence collected after the
three verified cutoffs. Derived stop points and the sodium-ion Decision Memory sidecar
were baseline controls, not new evidence. The result means `NOT FOUND WITHIN DEFINED
SEARCH SCOPE`; it does not mean that later evidence does not exist. No synthetic daily
observation was created.

## Publication gate

All three proposed decisions are `NO_STATE_CHANGE`. The manifest remains
`publication_approved: false` with `human_decision: PENDING`; therefore no public file,
sitemap, snapshot, or deployment target may be changed by this execution.
