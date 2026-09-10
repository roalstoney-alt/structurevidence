from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def isoformat_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_as_of(as_of: datetime | str | None = None) -> datetime:
    if as_of is None:
        return utc_now()
    if isinstance(as_of, str):
        parsed = as_of
        if parsed.endswith("Z"):
            parsed = parsed[:-1] + "+00:00"
        try:
            as_of = datetime.fromisoformat(parsed)
        except ValueError as exc:
            raise ValueError(f"INVALID_GDR_SE_AS_OF:{as_of}") from exc
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("GDR_SE_AS_OF_MUST_BE_TIMEZONE_AWARE")
    return as_of.astimezone(timezone.utc)
