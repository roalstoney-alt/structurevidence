"""Safe synthetic renderers for publication-control records.

These helpers are deliberately independent of production customer data. They
exercise the disclosure boundary shared by HTML, JSON, legacy-URL and feed
representations without claiming that any particular cache has been purged.
"""

import html
import json

PUBLIC_STATES = {"CURRENT", "SUPERSEDED", "CORRECTED", "RESTRICTED", "WITHDRAWN"}
SAFE_FIELDS = {"record_id", "public_status", "status_notice", "effective_at", "replacement_url"}


def public_projection(record):
    state = record.get("public_status")
    if state not in PUBLIC_STATES:
        raise ValueError("invalid public_status")
    if state in {"RESTRICTED", "WITHDRAWN"}:
        return {key: record.get(key) for key in SAFE_FIELDS if key in record}
    return {key: value for key, value in record.items() if key != "restricted_payload"}


def render_public_surface(record, surface):
    """Render a safe synthetic public representation for regression tests."""
    projected = public_projection(record)
    if surface == "json":
        return json.dumps(projected, sort_keys=True)
    if surface == "legacy_url":
        notice = html.escape(projected.get("status_notice", ""))
        state = html.escape(projected["public_status"])
        return f"<main data-public-status=\"{state}\"><p>{notice}</p></main>"
    if surface == "feed":
        identifier = html.escape(projected.get("record_id", ""))
        notice = html.escape(projected.get("status_notice", ""))
        state = html.escape(projected["public_status"])
        return f"<entry><id>{identifier}</id><category term=\"{state}\"/><summary>{notice}</summary></entry>"
    raise ValueError("unsupported public surface")
