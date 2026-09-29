# CODEX PUBLICATION WORKFLOW
# STRUCTEVIDENCE_METHOD_PAPER_AND_REPLICATION_KIT_v0.1

## Objective

Publish the method paper, protocol specification, and replication kit without changing any public evidence state.

## Hard boundaries

Do not:

- modify existing public claim semantics;
- regenerate case state merely for publication;
- add new research claims without verification;
- publish customer-private data;
- create a new public version of any case;
- change resolver behavior in the same release unless a publication-blocking defect is found.

## Phase 0 — Preflight

1. `git fetch origin`
2. Record current `origin/main`.
3. Confirm baseline `94ee5dc8670b8132979846c815b400f8cef17ab1` is reachable.
4. If main has advanced, compare changes and determine whether the paper's implementation-state statements remain accurate.
5. If claim count, endpoint semantics, match classes, or authorization boundaries changed, update the paper before publication.

## Phase 1 — Add package

Recommended repository path:

`research/method-paper/STRUCTEVIDENCE_METHOD_PAPER_AND_REPLICATION_KIT_v0.1/`

Add the package unchanged except for approved author metadata, license, and final canonical paper URL.

## Phase 2 — Resolve placeholders

Required human inputs before release:

- author name(s);
- affiliation, if any;
- preferred contact;
- chosen license;
- canonical citation format;
- preprint location, if any.

Do not invent author credentials or affiliations.

## Phase 3 — Validation

Check:

- all public URLs resolve;
- resolver endpoint remains read-only;
- test case claim IDs still exist;
- claim count remains 26 or update paper and manifest explicitly;
- no private/customer paths are present in the package;
- no API keys or credentials;
- no unsupported claim of superiority;
- medical case is explicitly described as public research only;
- references are correctly formatted.

## Phase 4 — Release commit

Suggested commit:

`docs(research): publish StructureEvidence method paper and replication kit v0.1`

Use normal fast-forward push only.

## Phase 5 — Optional archival publication

Recommended order:

1. GitHub canonical source;
2. DOI-backed archive such as Zenodo or an institutional archive, if desired;
3. preprint server if scope and submission rules fit;
4. Medium / Zhihu communication pieces linking to the canonical artifact.

Do not state "peer reviewed" unless peer review has actually occurred.

## Phase 6 — Open challenge intake

Create a clearly labeled public challenge route or issue template.

Challenge submissions should request:

- exact query;
- observed output;
- expected behavior;
- failure class;
- canonical claim ID;
- supporting evidence;
- reproduction steps.

Do not invite users to post confidential customer information or personal health records publicly.

## Final return

PROJECT = STRUCTEVIDENCE_METHOD_PAPER_AND_REPLICATION_KIT_v0.1

ENTRY_SHA =
REMOTE_MAIN_BEFORE =
PACKAGE_PATH =
AUTHOR_METADATA_COMPLETE = YES/NO
LICENSE_SELECTED = YES/NO
PUBLIC_URL_VALIDATION = PASS/FAIL
CLAIM_INVENTORY_VALIDATION = PASS/FAIL
PRIVATE_DATA_SCAN = PASS/FAIL
MEDICAL_BOUNDARY = PASS/FAIL
UNSUPPORTED_SUPERIORITY_CLAIMS = NONE/FOUND
FILES_ADDED =
FILES_MODIFIED =
FINAL_DIFF_SCOPE = CLEAN/CONTAMINATED
LOCAL_HEAD_AFTER =
REMOTE_MAIN_AFTER =
PUSH_RESULT =
FINAL_STATUS = PUBLICATION_PACKAGE_RELEASED / STOPPED_<REASON>
