#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("publisher", ROOT / "scripts/publish_cml_v01.py")
publisher = importlib.util.module_from_spec(spec); spec.loader.exec_module(publisher)
_, derived = publisher.generate_data_dictionary()
stored = json.loads((ROOT / "technical-risk/validation/CML_DATA_DICTIONARY_INDEX.json").read_text())
assert derived["authoritative_paths"] == stored["authoritative_paths"]
assert derived["row_count"] == stored["row_count"]
markdown = (ROOT / "docs/architecture/CML_TECHNICAL_RISK_DATA_DICTIONARY_v0.1.md").read_text()
for path in derived["authoritative_paths"]:
    assert f"`{path}`" in markdown, path
print("CML_DATA_DICTIONARY_DRIFT_PASS")
