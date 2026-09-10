from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_sha256(value: Any) -> str:
    return sha256_bytes(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8"))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_sha256sums(path: Path | None) -> dict[str, str]:
    if path is None or not path.exists():
        return {}
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) >= 2:
            values[parts[-1]] = parts[0]
    return values


def artifact_metadata(role: str, path: Path | None, root: Path, expected_hashes: dict[str, str]) -> dict[str, Any]:
    if path is None:
        return {"role": role, "path": None, "exists": False, "readable": False, "size_bytes": 0, "sha256": None, "expected_sha256": None, "hash_match": False}
    exists = path.exists()
    size = path.stat().st_size if exists else 0
    if exists and path.is_absolute():
        try:
            rel = str(path.relative_to(root))
        except ValueError:
            rel = str(path)
    else:
        rel = str(path)
    local_name = path.name
    expected = expected_hashes.get(local_name) or expected_hashes.get(rel)
    digest = sha256_file(path) if exists and size > 0 else None
    return {
        "role": role,
        "path": rel,
        "exists": exists,
        "readable": exists,
        "size_bytes": size,
        "sha256": digest,
        "expected_sha256": expected,
        "hash_match": bool(expected and digest == expected),
    }


def find_duplicate_ids(rows: Any, id_keys: tuple[str, ...]) -> list[str]:
    seen: set[str] = set()
    dupes: set[str] = set()

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for key in id_keys:
                if isinstance(value.get(key), str):
                    ident = value[key]
                    if ident in seen:
                        dupes.add(ident)
                    seen.add(ident)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(rows)
    return sorted(dupes)
