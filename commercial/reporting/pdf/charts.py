from __future__ import annotations


def structural_chart_rows(bundle: dict) -> list[str]:
    rows = []
    for row in bundle.get("freshness_snapshot", {}).get("level_freshness", [])[:6]:
        rows.append(f"{row.get('dimension_id')}: {row.get('freshness_state')}")
    for row in bundle.get("freshness_snapshot", {}).get("delta_freshness", [])[:6]:
        rows.append(f"{row.get('dimension_id')} delta: {row.get('freshness_state')}")
    return rows
