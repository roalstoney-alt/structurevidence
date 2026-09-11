#!/usr/bin/env python3
from monitoring_test_common import ROOT, pass_message, require, sha256, snapshot


def main() -> None:
    data = snapshot()
    require(len(data["rtp_provenance_refs"]) >= 10, "provenance input chain is incomplete")
    for row in data["rtp_provenance_refs"]:
        path = ROOT / row["path"]
        require(path.is_file(), f"missing input: {path}")
        require(sha256(path) == row["sha256"], f"input hash mismatch: {path}")
    pass_message("MONITORING_PROVENANCE_TESTS")


if __name__ == "__main__": main()
