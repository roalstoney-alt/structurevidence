from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_as_of(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("as_of timestamp must include an explicit timezone")
        return value.astimezone(timezone.utc)
    if not isinstance(value, str) or not value:
        raise ValueError("as_of timestamp must be a non-empty ISO-8601 string")
    source = value
    if source.endswith("Z"):
        source = source[:-1] + "+00:00"
    parsed = datetime.fromisoformat(source)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("as_of timestamp must include an explicit timezone")
    return parsed.astimezone(timezone.utc)


def isoformat_z(value: datetime) -> str:
    normalized = normalize_as_of(value)
    return normalized.isoformat().replace("+00:00", "Z")


def parse_as_of(value: str | None) -> datetime:
    return utc_now() if value is None else normalize_as_of(value)
