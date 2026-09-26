#!/usr/bin/env python3
"""Validate an SE-FRR v0.1 object bundle."""
from __future__ import annotations

import argparse
from pathlib import Path

from se_frr_protocol import load_objects, validate_bundle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("tests/se_frr/fixtures"))
    args = parser.parse_args()
    result = validate_bundle(load_objects(args.root))
    print(f"OBJECTS_CHECKED {result['objects_checked']}")
    print(f"SCHEMA_ERRORS {result['schema_errors']}")
    print(f"REFERENCE_ERRORS {result['reference_errors']}")
    print(f"HASH_ERRORS {result['hash_errors']}")
    print(f"CHAIN_ERRORS {result['chain_errors']}")
    print(f"PRIVACY_ERRORS {result['privacy_errors']}")
    print(f"RESULT {result['result']}")
    if result["result"] != "PASS":
        for category, errors in result["errors"].items():
            for error in errors:
                print(f"ERROR {category} {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
