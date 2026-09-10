from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from timeline.validation.gate_runner import run  # noqa: E402


def main() -> None:
    run()
    print("TIMELINE_R1_1A_VALIDATION_PASS")


if __name__ == "__main__":
    main()
