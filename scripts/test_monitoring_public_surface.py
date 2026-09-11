#!/usr/bin/env python3
from monitoring_test_common import ROOT, pass_message, require


def main() -> None:
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    monitor = (ROOT / "monitor.html").read_text(encoding="utf-8")
    combined = (home + monitor).lower()
    for required in ["monitor structural change", "monitor.html", "structural and evidence state", "not measured", "executive insight", "provenance"]:
        require(required in combined, f"missing public monitoring language: {required}")
    forbidden = ["buy signal", "sell signal", "hold rating"]
    for phrase in forbidden:
        require(phrase not in combined, f"forbidden output language: {phrase}")
    require("Monitoring is not prediction" in home + monitor, "monitoring boundary missing")
    for required in ["Executive insight", "Risk flags", "Decision relevance, not a trading signal"]:
        require(required in monitor, f"missing L1 decision view: {required}")
    for required in ["How the observed structure changed", "Established Delta", "Comparison open", "data-change-chart"]:
        require(required in monitor, f"missing simplified structure timeline: {required}")
    for required in [">Monitor</a>", ">Export PDF</a>", ">Login</a>", ">About Us</a>", ">Pricing</a>", ">Contact Us</a>"]:
        require(required in home, f"missing focused homepage navigation: {required}")
    monitor_js = (ROOT / "assets/monitor.js").read_text(encoding="utf-8")
    require("Ask Audit" in monitor_js and "customize.html?subject=" in monitor_js, "unsupported subject must route to customization")
    require('<details class="data-pack" data-market-pack>' in monitor, "market extension pack must use a collapsed disclosure")
    require('<details class="data-pack" data-market-pack open>' not in monitor, "market extension pack must be closed by default")
    pass_message("MONITORING_PUBLIC_SURFACE_TESTS")


if __name__ == "__main__": main()
