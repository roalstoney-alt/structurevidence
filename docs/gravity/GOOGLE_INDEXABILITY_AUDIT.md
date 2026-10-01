# Google indexability audit

## Baseline

- `robots.txt`: HTTP 200; `User-agent: *`, `Allow: /`; sitemap referenced.
- `sitemap.xml`: HTTP 200; homepage, case index, both flagship cases, and change surface included.
- Canonicals: present on homepage and flagship cases.
- Titles and descriptions: present on homepage and flagship cases.
- Structured data: absent from the baseline flagship case pages.
- `lastmod`: absent from the baseline sitemap.
- Search Console: `NOT_AVAILABLE`; no credentials or connected API were available.

## Implementation target

The gravity layer adds deterministic titles/descriptions where needed, JSON-LD that matches visible page content, breadcrumbs, explicit question/state/as-of headers, machine-readable `index.json` records, atomic evidence URLs, meaningful sitemap `lastmod` values, and tests that parse these surfaces.
