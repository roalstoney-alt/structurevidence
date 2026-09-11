from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SNAPSHOT_PATH = ROOT / "monitoring/subjects/bnb/MONITORING_SNAPSHOT.json"


def read_json(relative: str | Path) -> object:
    path = relative if isinstance(relative, Path) and relative.is_absolute() else ROOT / relative
    return json.loads(path.read_text(encoding="utf-8"))


def snapshot() -> dict:
    return read_json(SNAPSHOT_PATH)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def pass_message(name: str) -> None:
    print(f"{name}_PASS")
