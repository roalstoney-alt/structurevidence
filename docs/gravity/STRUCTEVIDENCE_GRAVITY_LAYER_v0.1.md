# STRUCTEVIDENCE_GRAVITY_LAYER_v0.1

## 0. PROJECT

```text
PROJECT =
STRUCTEVIDENCE_GRAVITY_LAYER_v0.1

PRIMARY_DOMAIN =
https://structurevidence.org

COMMERCIAL_DOMAIN =
https://structevidence.com

PRIMARY_OBJECTIVE =
Turn StructEvidence from a website containing evidence records
into a discoverable, citable, reproducible public evidence network.

PRIMARY_CHANNELS =
1. Google Search / other search engines
2. GitHub
3. Canonical StructEvidence case pages

HUMAN_CHANNELS_OUTSIDE_THIS_WORKFLOW =
LinkedIn
X

EXECUTION_PRINCIPLE =
REALITY_FIRST
EVIDENCE_FIRST
CANONICAL_RECORD_FIRST
NO_SEO_SPAM
NO_SYNTHETIC_ENGAGEMENT
NO_AUTO_OUTREACH
```

---

# 1. STRATEGIC MODEL

Do NOT treat Google or GitHub as marketing channels.

Treat them as discovery and verification infrastructure.

Target architecture:

```text
REALITY
   ↓
PUBLIC EVENT
   ↓
EVIDENCE
   ↓
STRUCTEVIDENCE CANONICAL RECORD
   ↓
STATE / CHANGE / UNKNOWN
   ↓
 ┌────────────┬──────────────┐
 ↓            ↓              ↓
GOOGLE      GITHUB        SOCIAL
Search      Verify        X / LinkedIn
Intent      Reproduce     Human distribution
 ↓            ↓              ↓
 └────────────┴──────┬───────┘
                     ↓
                  OBSERVER
                     ↓
         Citation / Challenge / Evidence
                     ↓
             STRUCTEVIDENCE
```

The system must optimize for:

```text
DISCOVERABLE
CITABLE
REPRODUCIBLE
UPDATEABLE
CHALLENGEABLE
```

Not:

```text
PAGEVIEWS
SEO CONTENT VOLUME
SOCIAL FOLLOWER COUNT
KEYWORD STUFFING
```

---

# 2. NON-NEGOTIABLE RULES

Codex MUST preserve the existing StructEvidence evidence philosophy.

## Rule 2.1

Never convert:

```text
NOT_FOUND
```

into:

```text
DOES_NOT_EXIST
```

Use controlled evidence terminology.

---

## Rule 2.2

Search-facing text MUST NOT overstate conclusions.

Allowed:

```text
Field deployment evidence found
Public evidence not established
One qualifying deployment record identified
Current evidence supports X
Current evidence does not establish Y
```

Disallowed:

```text
Proven forever
Definitely false
No such deployment exists
Industry has adopted X
```

unless the evidence state explicitly supports the claim.

---

## Rule 2.3

Google-facing content and human-facing content MUST use the same factual state.

No SEO-specific factual variant.

---

## Rule 2.4

Every discoverable claim must resolve back to a canonical record.

Preferred structure:

```text
/cases/{case-slug}/
/e/{evidence-id}/
/s/{state-id}/
```

If existing routing makes this expensive, preserve current routes and add aliases only where justified.

Do NOT break existing URLs.

---

# 3. PHASE A — BASELINE DISCOVERY AUDIT

Before changing production, create:

```text
docs/gravity/
    GRAVITY_BASELINE_AUDIT.md
    GOOGLE_INDEXABILITY_AUDIT.md
    GITHUB_DISCOVERY_AUDIT.md
```

Record:

```text
BASELINE_SHA =
DATE =
PRODUCTION_DOMAIN =
ROBOTS_STATUS =
SITEMAP_STATUS =
CANONICAL_STATUS =
STRUCTURED_DATA_STATUS =
INDEXABLE_CASE_COUNT =
PUBLIC_CASE_COUNT =
GITHUB_PUBLIC_REPO =
GITHUB_CITATION_STATUS =
GITHUB_TOPICS_STATUS =
MACHINE_READABLE_CASE_STATUS =
```

Audit at minimum:

```text
/
 /cases/
 /cases/800vdc/
 /cases/sodium-ion-bess/
 /verify/
 /state/
 /change/
 /evidence/
 /unknown/
 /history/
```

Only include routes that actually exist.

Do not invent successful status.

Record HTTP status for every route tested.

---

# 4. PHASE B — GOOGLE DISCOVERY FOUNDATION

## B1. robots.txt

Verify:

```text
https://structurevidence.org/robots.txt
```

Requirements:

- production pages crawlable;
- private/admin/API routes excluded where appropriate;
- no accidental global `Disallow: /`;
- sitemap referenced.

Preferred:

```text
User-agent: *
Allow: /

Sitemap: https://structurevidence.org/sitemap.xml
```

Add targeted exclusions only where necessary.

---

# 5. SITEMAP ARCHITECTURE

Create or normalize:

```text
/sitemap.xml
```

If scale later requires:

```text
/sitemap-index.xml
/sitemaps/cases.xml
/sitemaps/evidence.xml
/sitemaps/state.xml
```

For current scale, a single sitemap is acceptable.

Each canonical public URL should include:

```xml
<url>
  <loc>...</loc>
  <lastmod>...</lastmod>
</url>
```

`lastmod` MUST reflect meaningful content/state change.

Do NOT rewrite `lastmod` simply because a deploy happened.

---

# 6. CANONICALIZATION

Every public evidence/state/case page must declare one canonical URL.

Example:

```html
<link
  rel="canonical"
  href="https://structurevidence.org/cases/800vdc/"
/>
```

Rules:

```text
HTTP → HTTPS canonical
www → apex canonical
language variants self-canonical where applicable
duplicate routes resolve to canonical
query-string tracking does not become canonical
```

Do not canonicalize different factual records onto one page.

---

# 7. SEARCH-FIRST CASE PAGE MODEL

Every important case needs a search-readable header.

Current priority:

```text
CASE 001
800V DC / AI Data Center Power Architecture

CASE 002
Sodium-Ion BESS Commercialization
```

Future cases follow the same format.

Above-the-fold information should expose:

```text
CASE TITLE
CURRENT STATE
LAST MATERIAL CHANGE
AS-OF DATE
ONE-SENTENCE QUESTION
ONE-SENTENCE ANSWER
```

Example:

```text
Question:
Has 800VDC power architecture moved from proposal to independently
attributable field deployment?

Current state:
FIELD_DEPLOYMENT_EVIDENCE_FOUND

As of:
2026-xx-xx
```

Do NOT require the crawler or visitor to infer the primary question from long prose.

---

# 8. SEARCH INTENT BLOCK

For every flagship case, generate a controlled `Search Context` section.

Example:

```text
## Questions this record addresses

- Is 800V DC being deployed in data centers?
- Has 800VDC reached real field deployment?
- Is 800VDC still only a proposed architecture?
- What public evidence exists for 800VDC deployment?
```

These questions are not FAQ marketing copy.

They must correspond to genuine search intent and the evidence record.

Answers must link to:

```text
State
Evidence
Counter-evidence
Unknowns
History
```

---

# 9. TITLE AND DESCRIPTION STANDARD

Generate deterministic metadata.

Example:

```html
<title>
800V DC Data Center Deployment Evidence | StructEvidence
</title>
```

Description pattern:

```text
Public evidence record tracking field deployment,
counter-evidence, unresolved questions and state changes
for 800V DC data-center power architecture.
```

Do not use:

```text
Best
Ultimate
Revolutionary
No.1
Complete Truth
```

unless literally part of a sourced claim.

---

# 10. STRUCTURED DATA

Implement only structured data matching actual page content.

## Homepage

Use:

```text
Organization
WebSite
```

Where justified.

Organization name:

```text
StructEvidence
```

Canonical URL:

```text
https://structurevidence.org/
```

---

## Case Pages

Evaluate:

```text
Article
Dataset
BreadcrumbList
```

Use `Dataset` only if the page genuinely exposes a structured evidence dataset.

Do not use unsupported semantic inflation.

Possible Dataset fields:

```json
{
  "@type": "Dataset",
  "name": "...",
  "description": "...",
  "dateModified": "...",
  "url": "...",
  "creator": {
    "@type": "Organization",
    "name": "StructEvidence"
  }
}
```

Validate generated JSON-LD.

---

# 11. BREADCRUMBS

Implement consistent hierarchy.

Example:

```text
StructEvidence
  >
Cases
  >
800V DC
```

Or:

```text
StructEvidence
  >
Evidence
  >
L1-EV-CML-PDRE-001-FIELD-DEPLOYMENT-001
```

Render visual breadcrumbs and matching structured data.

---

# 12. INTERNAL LINK GRAPH

Every flagship case must link to:

```text
CURRENT STATE
CHANGE HISTORY
EVIDENCE
COUNTER-EVIDENCE
UNKNOWNS
SEARCH PROVENANCE
RELATED CASES
```

Every evidence record links back to parent case.

Every change record links:

```text
PREVIOUS STATE
NEW STATE
TRIGGERING EVIDENCE
PARENT CASE
```

Avoid orphan records.

Create audit script:

```text
scripts/audit_internal_links.py
```

Output:

```text
ORPHAN_PAGE_COUNT
BROKEN_INTERNAL_LINK_COUNT
CASE_WITHOUT_STATE_COUNT
EVIDENCE_WITHOUT_PARENT_COUNT
```

Target:

```text
0
0
0
0
```

---

# 13. MACHINE-READABLE PUBLIC RECORD

For every flagship case expose machine-readable state.

Preferred:

```text
/cases/800vdc/index.json
/cases/sodium-ion-bess/index.json
```

Or equivalent API endpoint.

Minimum schema:

```json
{
  "case_id": "",
  "title": "",
  "canonical_url": "",
  "question": "",
  "current_state": "",
  "as_of": "",
  "last_material_change": "",
  "evidence": [],
  "counter_evidence": [],
  "unknowns": [],
  "search_provenance": [],
  "history": []
}
```

Do not expose private/admin information.

---

# 14. PUBLIC CHANGE FEED

Create:

```text
/changes/
```

This becomes the primary search-visible chronological surface.

Each item:

```text
DATE
CASE
PREVIOUS STATE
NEW STATE
WHY IT CHANGED
TRIGGERING EVIDENCE
```

Example:

```text
2026-09-xx
800V DC Data Center Power

Previous:
FIELD_DEPLOYMENT_NOT_ESTABLISHED

New:
FIELD_DEPLOYMENT_EVIDENCE_ACCEPTED_SINGLE_INSTANCE

Trigger:
L1-EV-CML-PDRE-001-FIELD-DEPLOYMENT-001
```

Do NOT create a new entry for cosmetic website changes.

Only material evidence/state changes belong here.

---

# 15. GOOGLE DISCOVERY TEST SUITE

Create:

```text
tests/test_seo_surface.py
```

Check:

```text
200 canonical case
canonical exists
title exists
description exists
JSON-LD parses
sitemap includes case
robots does not block case
breadcrumb exists
case has as-of timestamp
case links evidence
case links history
```

Minimum:

```text
SEO_SURFACE_TESTS = PASS
```

---

# 16. PHASE C — GITHUB AS VERIFICATION LAYER

GitHub must NOT become a second canonical truth source.

Canonical truth remains:

```text
structurevidence.org
```

GitHub purpose:

```text
REPRODUCE
INSPECT
CHALLENGE
CITE
CONTRIBUTE
```

---

# 17. REPOSITORY POSITIONING

If the existing repository is suitable, preserve it.

Otherwise create a dedicated public repository only after explicit human approval.

Preferred identity:

```text
structurevidence
```

or:

```text
structurevidence-public-records
```

README opening:

```text
# StructEvidence

StructEvidence records how public evidence changes the state
of real-world technical and industrial claims.

It does not attempt to replace judgment.

It preserves:

- claims
- evidence
- counter-evidence
- unknowns
- search boundaries
- state transitions
- verification history
```

Then link:

```text
Canonical records:
https://structurevidence.org
```

---

# 18. GITHUB DIRECTORY STANDARD

Recommended public structure:

```text
/
├── README.md
├── LICENSE
├── CITATION.cff
├── CONTRIBUTING.md
├── SECURITY.md
├── methodology/
│   ├── README.md
│   ├── state-model.md
│   ├── evidence-model.md
│   └── search-provenance.md
│
├── cases/
│   ├── 800vdc/
│   │   ├── README.md
│   │   ├── case.yaml
│   │   ├── evidence.json
│   │   ├── counter_evidence.json
│   │   ├── unknowns.json
│   │   ├── state_history.json
│   │   └── search_provenance.json
│   │
│   └── sodium-ion-bess/
│       └── ...
│
└── schemas/
    ├── case.schema.json
    ├── evidence.schema.json
    ├── state.schema.json
    └── search-provenance.schema.json
```

---

# 19. CASE.YAML STANDARD

Example:

```yaml
case_id: CML-PDRE-001

title: >
  800V DC Data Center Power Architecture

canonical_url: >
  https://structurevidence.org/cases/800vdc/

question: >
  Is there independently attributable public evidence
  of real field deployment?

current_state: >
  R5_ARCHITECTURE_FIELD_DEPLOYMENT_EVIDENCE_ACCEPTED_SINGLE_INSTANCE

as_of: YYYY-MM-DD

evidence_count: 1

counter_evidence_count: 2

unknown_count: X
```

Values MUST be generated from canonical records.

Do not maintain divergent manual copies.

---

# 20. CITATION.CFF

Add:

```text
CITATION.cff
```

The repository must provide a stable citation mechanism.

Include:

```text
title
authors / organization where appropriate
url
repository-code
version
date-released
license
```

Do not invent DOI.

If no DOI exists:

```text
DOI = NONE
```

---

# 21. GITHUB TOPICS

Configure relevant repository topics.

Candidate set:

```text
evidence
evidence-engineering
open-research
verification
research-infrastructure
provenance
industrial-research
technology-research
structured-data
reproducible-research
```

Do not use unrelated high-traffic topics.

---

# 22. SOCIAL PREVIEW

Prepare one repository social preview image.

Text only:

```text
StructEvidence

Claims change.
Evidence accumulates.
States are versioned.

structurevidence.org
```

If image generation assets are unavailable, produce specification only.

Do not block deployment on artwork.

---

# 23. CONTRIBUTING MODEL

Create:

```text
CONTRIBUTING.md
```

Contribution types:

```text
NEW_EVIDENCE
COUNTER_EVIDENCE
SOURCE_CORRECTION
STATE_CHALLENGE
SEARCH_SCOPE_CHALLENGE
REPRODUCTION_RESULT
```

Explicitly state:

```text
Submitting evidence does not imply acceptance.

Every submission must be evaluated under
the StructEvidence evidence protocol.
```

---

# 24. ISSUE TEMPLATES

Create:

```text
.github/ISSUE_TEMPLATE/
```

Templates:

```text
new-evidence.yml
counter-evidence.yml
state-challenge.yml
source-correction.yml
```

Minimum evidence submission fields:

```text
Case
Claim affected
Source URL
Source date
Evidence description
Why it changes or may change the current state
Known limitations
Relationship to source
```

Never ask contributors to claim certainty they do not possess.

---

# 25. CHANGE SYNCHRONIZATION

Create a deterministic export process.

Preferred:

```text
Canonical StructEvidence data
        ↓
export_public_records.py
        ↓
GitHub public records
```

NOT:

```text
Website manually edited
+
GitHub manually edited
```

Create:

```text
scripts/export_public_records.py
```

Output only approved public fields.

Generate:

```text
case.yaml
evidence.json
counter_evidence.json
unknowns.json
state_history.json
search_provenance.json
```

---

# 26. DRIFT DETECTION

Create:

```text
scripts/check_public_record_drift.py
```

Check:

```text
WEBSITE_STATE
GITHUB_STATE
CANONICAL_URL
AS_OF
EVIDENCE_COUNT
LAST_CHANGE
```

If mismatch:

```text
PUBLIC_RECORD_DRIFT = FAIL
```

Deployment must not silently continue.

---

# 27. VERSIONING

Use releases only for meaningful protocol/data snapshots.

Examples:

```text
v0.1-public-record
v0.2-search-provenance
v0.3-state-history
```

Do NOT create GitHub releases for every evidence update.

Individual evidence changes belong in commits/history.

---

# 28. COMMIT FORMAT

Use meaningful prefixes:

```text
evidence:
state:
case:
provenance:
schema:
method:
seo:
infra:
```

Examples:

```text
evidence: add qualifying 800V field deployment record

state: update 800V deployment state after human review

provenance: publish controlled search boundary for CML-PDRE-001

seo: expose canonical case metadata and sitemap entry
```

---

# 29. PHASE D — DISCOVERY PAGE ARCHITECTURE

Build a lightweight discovery index:

```text
/cases/
```

Not a marketing gallery.

Display:

```text
CASE
QUESTION
CURRENT STATE
LAST MATERIAL CHANGE
AS OF
```

Sort default:

```text
LAST MATERIAL CHANGE DESC
```

Also create:

```text
/changes/
```

These two surfaces serve different search intentions:

```text
/cases/
= what is being tracked?

/changes/
= what changed?
```

---

# 30. FLAGSHIP CASE PRIORITY

Do NOT scale to dozens of cases yet.

Initial controlled set:

```text
P0
800V DC Data Center Power

P0
Sodium-Ion BESS

P1
one additional high-ambiguity,
high-economic-impact,
rapidly-changing technology case
```

Before adding Case #3, verify:

```text
800V_INDEXABLE = YES
800V_MACHINE_READABLE = YES
800V_GITHUB_REPRODUCIBLE = YES

SODIUM_INDEXABLE = YES
SODIUM_MACHINE_READABLE = YES
SODIUM_GITHUB_REPRODUCIBLE = YES
```

---

# 31. CASE #3 SELECTION RULE

Do not select based on social virality alone.

Score candidate internally on:

```text
ECONOMIC_IMPORTANCE
PUBLIC_INTEREST
EVIDENCE_AMBIGUITY
CHANGE_VELOCITY
PUBLIC_SOURCE_AVAILABILITY
DECISION_RELEVANCE
```

Do NOT publish the score as objective truth.

Preferred case characteristics:

```text
widely discussed
+
material economic consequence
+
current state unclear
+
new evidence arriving
+
public verification possible
```

---

# 32. QUERY DISCOVERY

For every case maintain:

```text
search_queries.yaml
```

Example:

```yaml
primary:
  - 800V DC data center deployment
  - 800VDC field deployment
  - 800V DC power architecture data center

questions:
  - has 800V DC been deployed in data centers
  - real 800VDC deployment
  - 800VDC production deployment evidence
```

These queries are research/discovery metadata.

Do NOT automatically insert every phrase into visible page copy.

---

# 33. SEARCH RESULTS OBSERVATION

Create:

```text
docs/gravity/SEARCH_DISCOVERY_LOG.csv
```

Fields:

```text
observed_at
query
engine
country_or_locale_if_known
structevidence_visible
position_if_observable
landing_url
notes
```

Important:

If position cannot be reliably measured:

```text
position = UNKNOWN
```

Never fabricate rankings.

---

# 34. GOOGLE SEARCH CONSOLE

If credentials or Search Console access are available:

verify:

```text
PROPERTY_CONNECTED
SITEMAP_SUBMITTED
INDEXING_ERRORS
CRAWLED_NOT_INDEXED
DISCOVERED_NOT_INDEXED
DUPLICATE_CANONICAL
```

If access is unavailable:

```text
SEARCH_CONSOLE_ACCESS = NOT_AVAILABLE
```

and generate human action instructions.

Do not block all other work.

---

# 35. HUMAN ACTION REQUIRED FILE

Create:

```text
docs/gravity/HUMAN_ACTION_REQUIRED.md
```

Only tasks Codex cannot safely perform.

Possible items:

```text
[ ] Connect/verify Google Search Console property
[ ] Submit sitemap if API authorization unavailable
[ ] Approve GitHub repository becoming public
[ ] Approve repository topics
[ ] Approve social preview
```

Keep list minimal.

---

# 36. PHASE E — CITATION PRIMITIVES

Every evidence item should ultimately have one stable URL.

Preferred:

```text
https://structurevidence.org/e/{evidence-id}
```

Example:

```text
/e/L1-EV-CML-PDRE-001-FIELD-DEPLOYMENT-001
```

Every state:

```text
https://structurevidence.org/s/{state-id}
```

Where architecture permits.

Each evidence page must expose:

```text
EVIDENCE ID
PARENT CASE
SOURCE
SOURCE DATE
OBSERVED DATE
CLASSIFICATION
WHAT IT SUPPORTS
WHAT IT DOES NOT ESTABLISH
ACCESSIBILITY
SEARCH RUN / PROVENANCE
```

This is the atomic citation layer.

---

# 37. COPY CITATION

Add lightweight UI:

```text
Copy link
Copy citation
```

Example generated citation:

```text
StructEvidence.
“800V DC Data Center Power Architecture:
Field Deployment Evidence.”
Evidence ID: L1-EV-CML-PDRE-001-FIELD-DEPLOYMENT-001.
Accessed YYYY-MM-DD.
https://structurevidence.org/e/...
```

Do not claim academic citation standards unless implemented.

---

# 38. PHASE F — CHANGE VELOCITY

Homepage should expose factual activity.

Add a compact section:

```text
RECENT MATERIAL CHANGES
```

Possible counts:

```text
Cases changed in last 30 days
New qualifying evidence
Unknowns resolved
States changed
```

Counts MUST derive from data.

Never hard-code marketing numbers.

Example:

```text
Last 30 days

2 cases changed
4 evidence items added
1 unknown resolved
1 state changed
```

If zero:

display zero.

This is important.

Zero is valid evidence.

---

# 39. CHANGE FEED FORMAT

Each material update should be exportable into a short canonical summary:

```text
WHAT CHANGED
PREVIOUS STATE
NEW STATE
WHY
EVIDENCE
AS OF
```

This same object can later feed:

```text
X
LinkedIn
RSS
email
API
```

But those publishing integrations are OUT OF SCOPE for v0.1.

---

# 40. RSS / ATOM

If low-cost to implement, create:

```text
/feed.xml
```

Feed only:

```text
MATERIAL_CASE_CHANGE
NEW_QUALIFYING_EVIDENCE
STATE_CHANGE
MAJOR_UNKNOWN_RESOLVED
```

Do not publish every commit.

RSS is preferred because it is open, machine-readable and platform-independent.

---

# 41. PHASE G — OBSERVER PARTICIPATION

Each case page should contain:

```text
Have evidence that could change this state?
```

CTA:

```text
Submit Evidence
```

Possible second CTA:

```text
Challenge Current State
```

Submissions must enter existing controlled verification workflow.

No direct public state mutation.

Architecture:

```text
OBSERVER
   ↓
SUBMISSION
   ↓
PENDING REVIEW
   ↓
CONTROLLED VERIFICATION
   ↓
ACCEPT / REJECT / RESCOPE
   ↓
STATE CHANGE if justified
```

---

# 42. MEASUREMENT MODEL

Do NOT judge the system primarily by traffic.

Track:

## Discovery

```text
INDEXED_CASE_COUNT
INDEXED_EVIDENCE_COUNT
SEARCH_QUERY_VISIBILITY
GITHUB_CLONES
GITHUB_STARS
GITHUB_FORKS
```

## Utility

```text
EXTERNAL_CITATIONS_FOUND
DIRECT_LINK_REFERRALS
EVIDENCE_SUBMISSIONS
STATE_CHALLENGES
RETURNING_VISITORS
```

## Structural quality

```text
ORPHAN_RECORDS
BROKEN_LINKS
PUBLIC_RECORD_DRIFT
STALE_AS_OF_RECORDS
UNRESOLVED_HIGH_PRIORITY_UNKNOWNS
```

The most important future metrics are:

```text
EXTERNAL_CITATIONS
EVIDENCE_SUBMISSIONS
STATE_CHALLENGES
RETURNING_OBSERVERS
```

Not raw impressions.

---

# 43. 90-POINT GATE

Define internal Gravity readiness gate.

Do not call this an objective product score.

Pass when all are true:

```text
[ ] Flagship cases are Google indexable

[ ] Canonical URLs stable

[ ] Sitemap valid

[ ] Structured metadata valid

[ ] Machine-readable public records available

[ ] GitHub verification layer public and synchronized

[ ] CITATION mechanism exists

[ ] Every flagship case has evidence + counter-evidence + unknowns

[ ] Material state changes generate public change records

[ ] Observer can submit evidence/challenge

[ ] No website/GitHub state drift

[ ] Search provenance exposed for controlled searches

[ ] At least one external discovery path works without
    direct StructEvidence promotion
```

Last condition is important.

A real gravity signal is:

```text
UNKNOWN PERSON
    ↓
SEARCH / LINK / GITHUB
    ↓
STRUCTEVIDENCE
```

without manual outreach to that person.

---

# 44. DO NOT DO

Codex MUST NOT:

```text
create hundreds of SEO pages

generate synthetic keyword articles

auto-comment on GitHub projects

spam issue trackers

create backlinks through fake profiles

mass-submit StructEvidence to directories

buy backlinks

fake stars/forks

rewrite evidence conclusions for SEO

hide negative evidence

remove counter-evidence to improve conversion

create unsupported FAQ claims

auto-post to LinkedIn

auto-DM people

change X strategy
```

---

# 45. IMPLEMENTATION ORDER

Execute strictly:

```text
PHASE A
Baseline audit

↓

PHASE B
Google technical foundation

↓

PHASE C
GitHub verification layer

↓

PHASE D
Cases + Changes discovery surfaces

↓

PHASE E
Citation primitives

↓

PHASE F
Change velocity + optional RSS

↓

PHASE G
Observer participation

↓

FINAL VERIFICATION
```

Do not begin large new case acquisition before core infrastructure passes.

---

# 46. REQUIRED TESTS

At minimum:

```text
GOOGLE_SURFACE_TESTS
GITHUB_EXPORT_TESTS
SCHEMA_VALIDATION_TESTS
INTERNAL_LINK_TESTS
PUBLIC_RECORD_DRIFT_TESTS
SITEMAP_TESTS
CANONICAL_TESTS
```

Run existing test suite too.

Existing failures must be classified as:

```text
PRE_EXISTING
NEW_REGRESSION
ENVIRONMENTAL
```

Never hide failures.

---

# 47. PRODUCTION SMOKE TEST

After deploy check:

```text
GET /
GET /cases/
GET /changes/
GET /cases/800vdc/
GET /cases/sodium-ion-bess/
GET /robots.txt
GET /sitemap.xml
GET /feed.xml    if implemented
```

Verify:

```text
STATUS
CANONICAL
TITLE
DESCRIPTION
JSON-LD
INTERNAL LINKS
MOBILE RENDER
LANGUAGE SWITCHER where applicable
```

---

# 48. FINAL EXECUTION REPORT

Generate:

```text
docs/gravity/STRUCTEVIDENCE_GRAVITY_LAYER_v0.1_EXECUTION_REPORT.md
```

Mandatory final output:

```text
PROJECT =
STRUCTEVIDENCE_GRAVITY_LAYER_v0.1

BASELINE_SHA =

FINAL_SHA =

GOOGLE_FOUNDATION =
PASS / PARTIAL / FAIL

GITHUB_VERIFICATION_LAYER =
PASS / PARTIAL / FAIL

CANONICAL_CASES =
N

MACHINE_READABLE_CASES =
N

CITABLE_EVIDENCE_RECORDS =
N

SITEMAP =
PASS / FAIL

ROBOTS =
PASS / FAIL

STRUCTURED_DATA =
PASS / PARTIAL / FAIL

INTERNAL_LINK_GRAPH =
PASS / FAIL

PUBLIC_RECORD_DRIFT =
PASS / FAIL

RSS =
PASS / NOT_IMPLEMENTED

EVIDENCE_SUBMISSION =
PASS / NOT_IMPLEMENTED

SEARCH_CONSOLE =
CONNECTED / HUMAN_ACTION_REQUIRED / NOT_AVAILABLE

NEW_TESTS =
x/x

FULL_TEST_SUITE =
x/x

PRODUCTION_SMOKE =
PASS / PARTIAL / FAIL

HUMAN_ACTION_REQUIRED =
N

REPOSITORY_CLEAN =
YES / NO

READY_FOR_GRAVITY_OBSERVATION =
YES / NO
```

---

# 49. STOP CONDITIONS

STOP rather than improvise if:

```text
production data may be overwritten

canonical URL migration would break existing links

private evidence may become public

GitHub repo visibility must change without approval

Search Console requires account authorization

existing evidence IDs would change

existing canonical records would become ambiguous
```

Output:

```text
STOP_REASON =
REQUIRED_HUMAN_DECISION =
SAFE_NEXT_ACTION =
```

---

# 50. SUCCESS DEFINITION

v0.1 is NOT successful because:

```text
traffic increased
followers increased
posts increased
```

v0.1 is successful when:

```text
A person searching for a real technical claim
can discover StructEvidence.

A technical user can inspect the underlying record.

A researcher can cite an evidence object.

A developer can reproduce the public state.

An observer can challenge the state.

A new piece of reality can update the record.

And every surface still points back to one canonical truth.
```

Final architectural objective:

```text
REALITY
   ↓
EVIDENCE
   ↓
CANONICAL STATE
   ↓
DISCOVERY
   ↓
OBSERVER
   ↓
CHALLENGE / NEW EVIDENCE
   ↓
CANONICAL STATE
```

That loop — not social reach — is the first real StructEvidence vortex.