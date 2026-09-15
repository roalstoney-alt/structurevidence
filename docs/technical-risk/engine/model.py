"""Thin CML domain model over the shared StructEvidence Evidence Core envelope."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


def canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class TechnicalRiskRecord:
    core: dict
    domain_payload: dict

    @property
    def identity(self) -> dict:
        return self.domain_payload["identity"]

    @property
    def event(self) -> dict:
        return self.domain_payload["event"]

    def verify_record_hash(self) -> bool:
        core = dict(self.core)
        expected = core.pop("record_hash")
        return expected == canonical_hash({"core": core, "payload": self.domain_payload})


def load_public_record(path: str | Path) -> TechnicalRiskRecord:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if set(payload) != {"core", "cml"}:
        raise ValueError("CML_PUBLIC_RECORD_SHAPE_INVALID")
    record = TechnicalRiskRecord(core=payload["core"], domain_payload=payload["cml"])
    if record.core.get("domain") != "TECHNICAL_RISK" or record.core.get("protocol") != "CML":
        raise ValueError("CML_DOMAIN_MISMATCH")
    if not record.verify_record_hash():
        raise ValueError("CML_RECORD_HASH_MISMATCH")
    return record
