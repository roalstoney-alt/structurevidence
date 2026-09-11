from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from monitoring.runtime.builder import build_monitoring_artifacts  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", default="bnb")
    parser.add_argument("--as-of", default="2026-09-11T00:00:00Z")
    args = parser.parse_args()
    outputs = build_monitoring_artifacts(args.subject, args.as_of)
    print(json.dumps({key: str(value) for key, value in outputs.items()}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
