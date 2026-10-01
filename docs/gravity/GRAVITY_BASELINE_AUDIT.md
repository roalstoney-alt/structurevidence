# Gravity baseline audit

```text
BASELINE_SHA = 82314541f563d7f2fe9243197145758914fe036a
DATE = 2026-10-01
PRODUCTION_DOMAIN = https://structurevidence.org
ROBOTS_STATUS = 200; global crawl allowed; sitemap declared
SITEMAP_STATUS = 200; flagship cases present; lastmod absent
CANONICAL_STATUS = PRESENT_ON_FLAGSHIP_CASES
STRUCTURED_DATA_STATUS = NOT_PRESENT_ON_FLAGSHIP_CASES
INDEXABLE_CASE_COUNT = 3 public case HTML pages in sitemap
PUBLIC_CASE_COUNT = 3
GITHUB_PUBLIC_REPO = https://github.com/roalstoney-alt/structurevidence (PUBLIC)
GITHUB_CITATION_STATUS = CITATION.cff PRESENT; DOI PRESENT
GITHUB_TOPICS_STATUS = NONE
MACHINE_READABLE_CASE_STATUS = FROZEN STATE SIDECARS PRESENT; CANONICAL index.json ABSENT
```

## Live route baseline

| Route | HTTP status | Baseline note |
|---|---:|---|
| `/` | 200 | Public home |
| `/cases/` | 200 | Case discovery index |
| `/cases/800vdc/` | 200 | Flagship case |
| `/cases/sodium-ion-bess/` | 200 | Flagship case |
| `/verify/` | 200 | Verification workflow |
| `/state/` | 404 | Route does not exist; not invented |
| `/change/` | 404 | Singular route does not exist |
| `/changes/` | 200 | Existing chronological surface |
| `/evidence/` | 404 | Aggregate route does not exist |
| `/unknown/` | 404 | Route does not exist |
| `/history/` | 404 | Route does not exist |

HTTP checks were made against production on 2026-10-01. A 404 is recorded as observed; it is not converted into a successful status.
