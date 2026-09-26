#!/usr/bin/env python3
"""Verify tamper-evident SE-FRR State chains."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from se_frr_protocol import verify_state_chain


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--states", type=Path, default=Path("tests/se_frr/fixtures/states"))
    args = parser.parse_args()
    states = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(args.states.glob("*.json"))]
    result = verify_state_chain(states)
    print(f"SUBJECTS_CHECKED {result['subjects_checked']}")
    print(f"STATES_CHECKED {result['states_checked']}")
    print(f"CHAINS_VALID {result['chains_valid']}")
    print(f"CHAINS_INVALID {result['chains_invalid']}")
    print(f"BROKEN_LINKS {len(result['broken_links'])}")
    print(f"HASH_MISMATCHES {len(result['hash_mismatches'])}")
    print(f"RESULT {result['result']}")
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
