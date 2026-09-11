#!/usr/bin/env python3
from monitoring_test_common import ROOT, pass_message, require


def main() -> None:
    home = (ROOT / "index.html").read_text(encoding="utf-8")
    monitor = (ROOT / "monitor.html").read_text(encoding="utf-8")
    combined = (home + monitor).lower()
    for required in ["market-dynamics coverage", "monitor.html?subject=bnb", "asset state", "not_measured", "evidence dynamics", "provenance"]:
        require(required in combined, f"missing public monitoring language: {required}")
    forbidden = ["buy signal", "sell signal", "hold rating"]
    for phrase in forbidden:
        require(phrase not in combined, f"forbidden output language: {phrase}")
    require("Monitoring is not prediction" in home + monitor, "monitoring boundary missing")
    for required in ["Executive insight", "Risk flags", "Decision relevance, not a trading signal"]:
        require(required in monitor, f"missing L1 decision view: {required}")
    pass_message("MONITORING_PUBLIC_SURFACE_TESTS")


if __name__ == "__main__": main()
