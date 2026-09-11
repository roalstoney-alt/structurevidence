#!/usr/bin/env python3
from monitoring_test_common import pass_message, require, snapshot
from monitoring.runtime.builder import gdr_monitor_actions


def main() -> None:
    actions = gdr_monitor_actions("ALLOW_WITH_LIMITATIONS")
    require(actions["DISPLAY_OBSERVATION"] == "ALLOW", "observations should remain visible")
    require(actions["COMMERCIAL_DELIVERY"] == "BLOCK", "monitor authorization leaked into paid delivery")
    require(snapshot()["gdr_snapshot"]["actions"] == actions, "snapshot adapter output mismatch")
    pass_message("MONITORING_GDR_ADAPTER_TESTS")


if __name__ == "__main__": main()
