#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / "index.html").read_text()
for token in ['name="description"', 'property="og:description"', 'name="twitter:description"', "structural intelligence", "technical risk"]:
    assert token.lower() in text.lower(), token
print("CML_SITE_METADATA_PASS")
