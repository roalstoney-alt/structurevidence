from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUBJECT_PAGES = ["strategy-2026.html", "bnb.html", "sol.html", "trx.html", "xlm.html"]
FORBIDDEN_POSITIVE_CLAIMS = [
    "leaderboard",
    "top performers",
    "best asset",
    "worst asset",
    "rank #",
    "ranked list",
    "buy signal",
    "sell signal",
    "long signal",
    "short signal",
    "entry signal",
    "exit signal",
    "stop loss",
    "take profit",
    "risk-on",
    "risk-off",
    "30 days",
    "7 days",
    "24 hours",
    "max_age_days",
    "expires after",
    "expired by policy",
    "breached threshold",
]


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {"href", "src"} and value:
                self.links.append(value)


def fail(message: str) -> None:
    raise SystemExit(f"TIMELINE_UI_TEST_FAIL: {message}")


def main() -> None:
    js = (ROOT / "assets" / "site.js").read_text(encoding="utf-8")
    css = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")
    for marker in ["renderTimelinePanel", "data-resolution", "timeline-heatmap", "timeline-events", "loadResolution", "datasets"]:
        if marker not in js + css:
            fail(f"missing UI component marker {marker}")
    for page in SUBJECT_PAGES:
        text = (ROOT / page).read_text(encoding="utf-8")
        if 'class="dynamics-panel"' not in text or "data-timeline-subject" not in text:
            fail(f"missing dynamics panel in {page}")
        if "RDL freshness policy is not configured" not in text:
            fail(f"missing freshness boundary in {page}")
    if 'class="dynamics-panel"' in (ROOT / "index.html").read_text(encoding="utf-8"):
        fail("homepage was overloaded with timeline panel")
    scanned_paths = [
        ROOT / "assets" / "site.js",
        ROOT / "assets" / "style.css",
        ROOT / "dynamics.html",
        *(ROOT / page for page in SUBJECT_PAGES),
        *sorted((ROOT / "timeline").glob("**/*.json")),
        *sorted((ROOT / "docs" / "timeline").glob("**/*.json")),
        *sorted((ROOT / "docs" / "execution").glob("TIMELINE_*.md")),
        ROOT / "docs" / "execution" / "PRE_TIMELINE_DESIGN_NOTE.md",
    ]
    for path in scanned_paths:
        text = path.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_POSITIVE_CLAIMS:
            if phrase in text:
                fail(f"forbidden ranking/trading/threshold phrase in {path.relative_to(ROOT)}: {phrase}")
    for page in SUBJECT_PAGES + ["dynamics.html"]:
        parser = LinkParser()
        parser.feed((ROOT / page).read_text(encoding="utf-8"))
        for link in parser.links:
            target = link.split("#", 1)[0].split("?", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            if not (ROOT / target).exists():
                fail(f"missing link target {page}: {link}")
    print("TIMELINE_UI_TESTS_PASS")


if __name__ == "__main__":
    main()
