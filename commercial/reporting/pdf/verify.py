from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_pdf_hash(path: Path, expected_sha256: str) -> bool:
    return sha256_file(path) == expected_sha256
