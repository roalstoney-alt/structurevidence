# SE-DUAL-SITE-UPGRADE-002 — Phase D Commercial Integration Handoff
Status: DEVELOPMENT ONLY. NO MERGE OR PRODUCTION DEPLOY.
Baseline main SHA: f267f9dbe506cb30f95a2f21543b72b4fc31c388
Prior: PR #50 merged; no case states changed.

## Goal
Connect structevidence.com commercial front office to structurevidence.org's auditable public evidence, source dependency and citable decision conditions. Product is time-indexed, challengeable decision boundaries, not authoritative expert reports or purchase/investment recommendations.

## Frozen brand and method
Verify Your Verify — Lower the cost of knowing what you can trust.
We can be wrong. We must remain auditable.
SE-DECISION-BOUNDARY-001: Evidence Evolves. Decisions Remain Accountable.
Do not claim validated savings, unknown private subscription availability, universal absence from bounded-zero evidence or verified dual-human review. Engineering must continue without fictional evidence resolution.

## First: inventory
Inspect actual commercial source at deploy/cloudflare-landing, Worker bindings and routes, customer intake and D1 privacy boundary, EN / zh-CN / es implementation, current prices, SEO canonicals, .org reader routes and export URLs. Record source and deployment architecture before edits. No Cloudflare writes.

## Commercial homepage
- Distinguish the buyer's decision boundary from SE evidence qualification, with brief 'what is established / unknown / changed / would change it' flow.
- Position one-time scoped verification as the start of a versioned decision record, not the entirety of the product.
- Show verified, bounded public 800VDC example linked to .org Source Dependency View and Decision Conditions, with dated snapshots and explicit caveats.
- Separate LIVE, AVAILABLE_WITH_HUMAN_SCOPE, PROPOSED_NOT_LIVE features: private decision record, managed gap register, notifications, subscriptions and API as warranted by tested implementation only.
- Preserve existing published pricing and authorized intake flows. Do not add misleading checkout, estimates or invented ROI.
- No endorsements or asserted customer adoption without verifiable data.

## Cross-site boundary
.org canonical evidence stays .org, commercial CTA/intake stays .com. All links secure and functional. No rewriting .org evidence through commercial Worker. Only share public snapshots; do not leak private customer D1 or client decision/action data. Do not require external scripts or new cross-origin requests that change trust boundaries without separate review.

## Three languages
Keep EN, zh-CN and ES parity on commercial product claims, availability labels and evidence limitations. Preserve hreflang, canonical and sitemap, mobile navigation and existing conversion tracking. Do not modify .org locale routes except necessary safe links with tests.

## Acceptance
No protected source/case/registry drift, case state, ID, DOI, price or private data changes. Differential tests, HTML accessibility, keyboard/mobile, broken links, mirror/locale checks, SEO and hreflang, privacy/CORS, Worker tests, bounded-zero copy guards, accurate feature status, no new regressions. Report actual tests and existing failures separately. Create implementation commits on existing Phase D Draft PR. Owner must independently authorize merge and production deployment.

## Required report
PROJECT=SE-DUAL-SITE-UPGRADE-002
PHASE=D
BASELINE_MAIN_SHA=f267f9dbe506cb30f95a2f21543b72b4fc31c388
HEAD_SHA=[actual]
ORG_CANONICAL_DRIFT=[actual]
COMMERCIAL_FEATURE_AVAILABILITY=[actual]
ORIGINAL_RECORDS_CHANGED=0
PR_DRAFT=YES
NEW_REGRESSION_COUNT=[actual]
PRODUCTION_DEPLOY=NO
READY_FOR_OWNER_MERGE_REVIEW=[YES/NO]
