from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


FORBIDDEN_TERMS = {
    "buy", "sell", "long", "short", "entry", "stop", "target", "position size",
    "take profit", "leverage", "signal", "recommendation",
}


@dataclass(frozen=True)
class MosCommercialContext:
    asset: str
    as_of: str
    market_context: dict[str, str]
    source_provenance: list[dict[str, Any]] = field(default_factory=list)
    method_version: str = "MOS_COMMERCIAL_ADAPTER_V0.9"
    limitations: list[str] = field(default_factory=list)


def _contains_trading_instruction(value: Any) -> bool:
    text = str(value).lower()
    return any(term in text for term in FORBIDDEN_TERMS)


def validate_no_trading_instruction(payload: dict[str, Any]) -> None:
    if _contains_trading_instruction(payload):
        raise ValueError("MOS_COMMERCIAL_OUTPUT_CONTAINS_TRADING_INSTRUCTION")


def build_market_context(asset: str, allowed_data: dict[str, Any] | None = None, as_of: str | None = None) -> dict[str, Any]:
    """Return market-context-only MOS output. This adapter never emits actions."""
    allowed_data = allowed_data or {}
    context = MosCommercialContext(
        asset=asset,
        as_of=as_of or datetime.now(timezone.utc).isoformat(),
        market_context={
            "regime": str(allowed_data.get("regime", "UNAVAILABLE")),
            "liquidity_context": str(allowed_data.get("liquidity_context", "UNAVAILABLE")),
            "absorption_context": str(allowed_data.get("absorption_context", "UNAVAILABLE")),
            "rotation_context": str(allowed_data.get("rotation_context", "UNAVAILABLE")),
            "persistence": str(allowed_data.get("persistence", "UNAVAILABLE")),
            "data_freshness": str(allowed_data.get("data_freshness", "UNAVAILABLE")),
        },
        source_provenance=list(allowed_data.get("source_provenance", [])),
        limitations=list(allowed_data.get("limitations", ["MOS source integration is not enabled in Commercial V0.9."])),
    )
    payload = {
        "asset": context.asset,
        "as_of": context.as_of,
        "market_context": context.market_context,
        "source_provenance": context.source_provenance,
        "method_version": context.method_version,
        "limitations": context.limitations,
    }
    validate_no_trading_instruction(payload)
    return payload
