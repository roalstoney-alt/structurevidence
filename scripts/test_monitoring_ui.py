#!/usr/bin/env python3
import re

from monitoring_test_common import ROOT, pass_message, require


def main() -> None:
    pages = ["index.html", "monitor.html", "verify.html", "reports.html", "customize.html", "checkout.html"]
    for name in pages:
        text = (ROOT / name).read_text(encoding="utf-8")
        require('name="viewport"' in text, f"viewport missing: {name}")
        require("assets/monitor.css" in text, f"monitor stylesheet missing: {name}")
    css = (ROOT / "assets/monitor.css").read_text(encoding="utf-8")
    require("@media(max-width:1050px)" in css and "@media(max-width:700px)" in css, "responsive breakpoints missing")
    require("clamp(" not in css, "monitor typography must not scale with viewport width")
    require(".executive-layout" in css and "data-executive-headline" in (ROOT / "monitor.html").read_text(encoding="utf-8"), "executive insight module missing")
    require(".change-chart" in css and "data-change-detail" in (ROOT / "monitor.html").read_text(encoding="utf-8"), "structure change visualization missing")
    require(".data-pack" in css and "data-market-pack-state" in (ROOT / "monitor.html").read_text(encoding="utf-8"), "collapsed data extension pack missing")
    require('stateCard("Market Dynamics"' not in (ROOT / "assets/monitor.js").read_text(encoding="utf-8"), "unmeasured market card must not occupy the primary state grid")
    for name in pages:
        root = (ROOT / name).read_bytes(); published = (ROOT / "docs" / name).read_bytes()
        require(root == published, f"root/docs divergence: {name}")
    pass_message("MONITORING_UI_TESTS")


if __name__ == "__main__": main()
