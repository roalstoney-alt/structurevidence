#!/usr/bin/env python3
from monitoring_test_common import pass_message, require
from monitoring.runtime.builder import build_view_model
from monitoring.runtime.hash import canonical_hash


def main() -> None:
    one = build_view_model()
    two = build_view_model()
    require(one == two, "builder output must be deterministic")
    hashable = dict(one); hashable["snapshot_sha256"] = None
    require(canonical_hash(hashable) == one["snapshot_sha256"], "snapshot content hash mismatch")
    pass_message("MONITORING_BUILDER_TESTS")


if __name__ == "__main__": main()
