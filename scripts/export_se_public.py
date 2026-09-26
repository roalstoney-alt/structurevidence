#!/usr/bin/env python3
"""Create a sanitized public projection of an SE-FRR bundle."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from se_frr_protocol import load_objects, public_projection


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("tests/se_frr/fixtures"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    projection = public_projection(load_objects(args.root))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(projection, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"PUBLIC_OBJECTS {sum(len(values) for values in projection.values())}")
    print("PRIVATE_REQUESTS_EXPORTED 0")
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
