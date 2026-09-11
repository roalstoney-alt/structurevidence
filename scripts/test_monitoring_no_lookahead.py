#!/usr/bin/env python3
from monitoring_test_common import pass_message, require, snapshot
from monitoring.runtime.validators import visible_at


def main() -> None:
    require(not visible_at("2026-09-12T00:00:00Z", "2026-09-11T00:00:00Z"), "future-known event leaked")
    data = snapshot()
    require(all(visible_at(row["known_at"], data["known_at_cutoff"]) for row in data["recent_events"]), "snapshot contains future-known events")
    pass_message("MONITORING_NO_LOOKAHEAD_TESTS")


if __name__ == "__main__": main()
