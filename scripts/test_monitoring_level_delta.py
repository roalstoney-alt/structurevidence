#!/usr/bin/env python3
from monitoring_test_common import pass_message, require, snapshot
from monitoring.runtime.validators import establish_delta


def main() -> None:
    require(establish_delta(None, "CURRENT", comparable=True) == "NOT_ESTABLISHED", "one snapshot established Delta")
    require(establish_delta("PRIOR", "CURRENT", comparable=False) == "NOT_ESTABLISHED", "incomparable states established Delta")
    require(establish_delta("PRIOR", "CURRENT", comparable=True) == "ESTABLISHED", "comparable change not established")
    data = snapshot()
    levels = data["structural_level"]["dimensions"]
    deltas = data["structural_delta"]["dimensions"]
    require(levels is not deltas and any(row["state"] == "NOT_ESTABLISHED" for row in deltas), "Level and Delta collapsed")
    pass_message("MONITORING_LEVEL_DELTA_TESTS")


if __name__ == "__main__": main()
