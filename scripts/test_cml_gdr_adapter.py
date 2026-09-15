#!/usr/bin/env python3
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("cml_adapter", ROOT / "gdr-se/engine/domain_adapters/cml.py")
adapter = importlib.util.module_from_spec(spec); spec.loader.exec_module(adapter)
folder = ROOT / "technical-risk/records/amphenol-10081811-101-07lf"
record = json.loads((folder / "11_PUBLIC_RECORD.json").read_text())
sources = json.loads((folder / "01_SOURCE_REGISTER.json").read_text())

def effect(mutator=None, source_value=None):
    value = copy.deepcopy(record)
    if mutator: mutator(value)
    return adapter.release_effect(value, source_value or sources)

assert effect()["public_release"] == "ALLOW_WITH_LIMITATIONS"
assert effect()["paid_delivery"] == "BLOCK"
assert effect(lambda r: r["cml"].update(freshness_state="EVENT_INVALIDATED"))["public_release"] == "BLOCK"
assert effect(lambda r: r["cml"].update(freshness_state="UNDER_REVIEW"))["public_release"] == "ALLOW_WITH_LIMITATIONS"
assert effect(lambda r: r["cml"].update(freshness_state="POLICY_NOT_CONFIGURED"))["paid_delivery"] == "BLOCK"
assert effect(lambda r: r["core"].update(correction_status="MATERIAL_CORRECTION_OPEN"))["public_release"] == "BLOCK"
assert effect(lambda r: r["cml"].update(counter_evidence=""))["public_release"] == "BLOCK"
assert effect(lambda r: r["cml"]["evidence"].update(unknowns=["critical"]))["paid_delivery"] == "BLOCK"
assert effect(lambda r: r["cml"]["verification"].update(qualification_state="LAB_VERIFICATION_REQUIRED"))["paid_delivery"] == "BLOCK"
assert effect(lambda r: r["core"].update(supersession_status="SUPERSEDED"))["public_release"] == "BLOCK"
assert effect(source_value={"sources": [{"source_type": "AUTHORIZED_DISTRIBUTOR", "publisher": "x"}]})["public_release"] == "BLOCK"
for key in adapter.PRIVATE_KEYS:
    assert effect(lambda r, k=key: r["cml"].update({k: "PRIVATE"}))["public_release"] == "BLOCK", key
assert effect(lambda r: r["cml"]["alternative"].update(candidates=[{"relationship_type": "DROP_IN"}]))["public_release"] == "BLOCK"
print("CML_GDR_ADAPTER_PASS")
