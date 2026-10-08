"""Safe public projection for publication-control records."""

PUBLIC_STATES = {"CURRENT", "SUPERSEDED", "CORRECTED", "RESTRICTED", "WITHDRAWN"}
SAFE_FIELDS = {"record_id", "public_status", "status_notice", "effective_at", "replacement_url"}


def public_projection(record):
    state = record.get("public_status")
    if state not in PUBLIC_STATES:
        raise ValueError("invalid public_status")
    if state in {"RESTRICTED", "WITHDRAWN"}:
        return {key: record.get(key) for key in SAFE_FIELDS if key in record}
    return {key: value for key, value in record.items() if key != "restricted_payload"}
