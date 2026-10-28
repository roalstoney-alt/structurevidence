# Human-gated case-index and sitemap wiring

This file is a release instruction, not authorization and not an applied patch. Existing `cases/index.html` and `sitemap.xml` projections remain byte-identical because the historic baseline guard does not authorize their mutation in this candidate.

After row review, stale-baseline reconciliation, and owner approval for the exact candidate SHA, a separate append-only publication change should:

1. Add one clearly labeled IREN entry to `cases/index.html` and its identical `docs/cases/index.html` mirror. It must say `PENDING_HUMAN_REVIEW` until a real approval record exists and must not increase the accepted-tracker count before approval.
2. Add these English-only sitemap entries to both `sitemap.xml` and `docs/sitemap.xml`:
   - `https://structurevidence.org/cases/iren-ai-cloud-transition/`
   - `https://structurevidence.org/cases/iren-ai-cloud-transition/index.json`
   - `https://structurevidence.org/cases/iren-ai-cloud-transition/source-registry-v0.1.json`
   - `https://structurevidence.org/cases/iren-ai-cloud-transition/events-v0.1.json`
3. Add no translated route or hreflang until an actual reviewed translation exists.
4. Recompute any authorized projection baseline instead of weakening or bypassing the history guard.
5. Re-run mirror, SEO, canonical, link, history, mobile, and production Pages checks against the exact approved SHA.

Until then, `ORG_CASE_INDEX=FAIL` and `SITEMAP_CANONICAL=FAIL` are deliberate stop states, not hidden passes.
