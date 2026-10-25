# SE-DUAL-SITE-UPGRADE-002 implementation inventory

Status: RECON frozen on 2026-10-25. No production write, deployment, price
change, customer outreach, or historical-record rewrite was performed.

## Baseline and branch safety

- Repository: `roalstoney-alt/structurevidence`.
- PR #45 is merged at `f09bee956bdcb22aece9552e86093a47e137fad1`.
  During recon, PR #46 and PR #47 appended the 2026-10-25 watch and delivery
  records. The branch was rebased and the latest fetched `origin/main` freeze is
  `2ed24ed1d62394b8485fb175c083bcceca0618b0`.
- Implementation branch: `codex/se-002-source-dependency-model`, created in an
  isolated managed worktree from that exact commit.
- The user's original checkout was not switched or cleaned. At recon it was on
  local `main`, ahead of and behind `origin/main`, with pre-existing modified
  and untracked files. Those files are outside this branch's diff.
- Frozen brand copy remains exactly: **Verify Your Verify — Lower the cost of
  knowing what you can trust.**

The machine-readable pre-change public-record hash freeze is
`docs/implementation/SE-DUAL-SITE-002-BASELINE-SHA256.json`. It captures the
same path set as `scripts/check_public_record_drift.py`; it does not replace the
existing case-watch baseline.

## Observed site and deployment boundaries

| Surface | Observed source | Deployment evidence | Data boundary |
| --- | --- | --- | --- |
| `structurevidence.org` | Repository-root static pages plus mirrored `docs/`; both `CNAME` files name `structurevidence.org` | Live headers report `Server: GitHub.com`; apex resolves to GitHub Pages IPs and `www` is a CNAME to `roalstoney-alt.github.io` | Public methodology, cases, evidence, gaps, changes, stable citations and append-only public state history |
| `structevidence.com` | `deploy/cloudflare-landing/worker.js`, `commercial-ui.js`, `commercial-upgrade.js`, `gaps.js`, `gap-service.js`, locales and migrations | `wrangler.jsonc` names Worker `structevidence-commercial` with custom-domain routes for apex and `www`; live headers report Cloudflare | Commercial pages, same-origin intake, protected admin review, public gap challenge references, and D1-backed private customer request records |
| `api.structurevidence.org` | `deploy/cloudflare-evidence-resolver/worker.js`, `claims.js`, `question-protocol.js` | `wrangler.jsonc` names Worker `structurevidence-public-claim-resolver` with a custom-domain route | Public read-only claim/question resolver; no admin route or customer-data binding is declared |

No repository workflow deploys either site. `.org` publication settings and the
currently deployed Worker version IDs are therefore **UNKNOWN** from repository
evidence alone. Cloudflare secrets and their values are intentionally not read.

### `.com` storage and access controls observed in code

- D1 binding: `CUSTOMER_CASES_DB` → database
  `structurevidence-customer-cases`, ID
  `aee10591-536a-47af-8ee0-957551ba2360`.
- `0001_customer_intake.sql` stores private customer/contact/request scope. New
  requests start `SUBMITTED`, `CUSTOMER_PRIVATE`, `NOT_AUTHORIZED`, with an
  append-only `REQUEST_SUBMITTED` event.
- `0002_open_evidence_gaps.sql` stores public-reference challenge intake,
  append-only challenge events and separately authorized public changes.
  Submission cannot change a claim, gap, case or evidence state.
- Admin UI/API paths require separate Cloudflare Access audiences plus an email
  allowlist. Configuration failure is fail-closed.
- No customer record is copied into public CML, RDL, case, evidence or timeline
  data. Public challenge intake accepts a URL/document reference only, not file
  uploads. The remote migration state and production D1 contents were not read.

## Routes and production read-only smoke

Read-only HTTP checks on 2026-10-25 produced:

| URL | Result |
| --- | --- |
| `https://structurevidence.org/` | 200 HTML |
| `https://structurevidence.org/cases/800vdc/` | 200 HTML |
| `https://structurevidence.org/method.html` | 200 HTML |
| `https://structevidence.com/` | 200 HTML |
| `https://structevidence.com/verify/` | 200 HTML |
| `https://structevidence.com/api/gaps` | 200 JSON |
| `https://api.structurevidence.org/` | 404 JSON at the intentionally undefined root route |

No POST, PATCH, admin, D1, deployment or cache-purge operation was performed.

## 800VDC grounded-data readiness

The case is `CML-PDRE-001`, canonical URL
`https://structurevidence.org/cases/800vdc/`, with accepted public evidence ID
`L1-EV-CML-PDRE-001-FIELD-DEPLOYMENT-001`. The accepted state remains
`HUMAN-REVIEWED SINGLE-INSTANCE EVIDENCE` as of
`2026-09-20T10:46:47Z`.

Real attributable source records are present, including:

- Chindata's operator publication supporting one named commercial deployment;
- Siemens/Reinhausen and Vertiv development/planning records;
- SolarEdge's origin release, official PDF rendering and derived Business Wire
  distribution copy, with explicit lineage in the October 15 review;
- Sungrow's attributable certification announcement with access/issuer
  verification limitations preserved;
- Power Integrations/Ideal Power's supplier collaboration source note; and
- Vantage/Heron's future manufacturing-capacity agreement.

The existing gap definitions are real, not CC example data:

- `OEG-CML-001` / `CML-PDRE-001.INDEPENDENT_VALIDATION` remains
  `NOT_ESTABLISHED`.
- `OEG-CML-002` / `CML-PDRE-001.MULTI_ENTITY_REPLICATION` remains
  `NOT_ESTABLISHED`.

The records are sufficient for a grounded dependency pilot, but later events
must not be backdated into the September evidence cutoff or promoted into a
state change. PR-A therefore creates the empty versioned registry and rules;
the first classified rows and reader-visible view remain an append-only PR-B
change after PR-A approval. No illustrative seven-source/percentage figures
are treated as case facts.

## Open pull requests observed during recon

Open PRs were #15, #23, #26, #32, #36, #37 and #44. Their boundary,
append-only monitoring or
reconciliation scopes overlap protected history and/or mirrors. PR-A does not
import, rewrite, close or merge any of them.

## Regression baseline before PR-A edits

Passing gates:

- `scripts/check_public_record_drift.py`: `PUBLIC_RECORD_DRIFT = PASS`.
- `scripts/audit_internal_links.py`: 0 orphan pages, broken links, cases without
  state or evidence without parent.
- `tests.test_history_immutability`: 6/6 pass.
- brand identity, SEO, public export and public/commercial boundary focused
  checks: pass.
- Cloudflare commercial Worker: 31/31 Node tests pass after lockfile-pinned
  dependency installation.
- Cloudflare evidence resolver: 27/27 Node tests pass without a package install.

Pre-existing failures on the unmodified `origin/main` baseline:

- `scripts/test_public_case_primitives_v01.py`: 9 tests, 3 failures caused by
  root/`docs` mirror drift.
- `scripts/test_commercial_domain_split.py`: 5 tests, 1 failure because the
  older test expects only the commercial origin while live config also permits
  the two research origins for gap challenge CORS.
- `python3 -m unittest discover -s tests -p 'test_*.py'`: 41 tests, 11 failures,
  primarily stale protected hashes and root/`docs` drift, plus one sandbox-only
  write denial in the otherwise passing deterministic public-record exporter.
- `python3 -m unittest discover -s scripts -p 'test_*.py'`: 412 tests,
  37 failures and 11 errors, including the same mirror/hash drift, historical
  milestone assumptions and absent OIL artifacts.

These failures are baseline debt, not authorized PR-A scope. Acceptance is no
new failures, preservation of each pre-existing green suite, zero protected
record drift, and a green new source-dependency suite.

## Risks, stop points and UNKNOWNs

- Production deployment ownership/version receipts are not stored in this
  repository; deployment remains human-gated.
- The remote D1 migration level and row contents are unknown and were not read.
- Open monitoring PRs can advance `main`; every later phase must fetch and start
  from the then-current approved `main`.
- Source dependency is issue-specific. Host count, URL count and publisher
  count cannot substitute for authorship/observation independence.
- Reviewer conflict must remain visible. Unknown authorship/dependency is
  recorded as `UNKNOWN`, not guessed.
- Existing public case/gap states, evidence IDs, canonical URLs, DOI records,
  prices and conclusions are frozen unless a separately approved append-only
  event and human gate authorize a later change.
