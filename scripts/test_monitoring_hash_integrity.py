#!/usr/bin/env python3
from monitoring_test_common import pass_message, read_json, require, sha256, snapshot
from monitoring.runtime.hash import canonical_hash


def main() -> None:
    data = snapshot(); hashable = dict(data); hashable["snapshot_sha256"] = None
    require(canonical_hash(hashable) == data["snapshot_sha256"], "snapshot hash mismatch")
    manifest = read_json("monitoring/subjects/bnb/MONITORING_BUILD_MANIFEST.json")
    for row in manifest["outputs"]:
        require(sha256(__import__('pathlib').Path(__file__).resolve().parents[1] / row["path"]) == row["sha256"], f"output hash mismatch: {row['path']}")
    pass_message("MONITORING_HASH_INTEGRITY_TESTS")


if __name__ == "__main__": main()
