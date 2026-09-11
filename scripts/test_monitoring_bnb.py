#!/usr/bin/env python3
from monitoring_test_common import pass_message, require, snapshot


def main() -> None:
    data = snapshot()
    require(data["subject_id"] == "BNB", "BNB subject missing")
    require(len(data["structural_level"]["dimensions"]) == 4, "expected four observed structural dimensions")
    require(data["market_dynamics"]["state"] == "NOT_MEASURED", "missing market data must be explicit")
    require(all(row["state"] == "NOT_MEASURED" for row in data["liquidity_observations"]), "liquidity boundary weakened")
    pass_message("MONITORING_BNB_TESTS")


if __name__ == "__main__": main()
