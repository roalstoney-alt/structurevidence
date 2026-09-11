#!/usr/bin/env python3
import jsonschema

from monitoring_test_common import ROOT, pass_message, read_json, snapshot


def main() -> None:
    snap = snapshot()
    jsonschema.validate(snap, read_json("monitoring/schema/monitoring_snapshot.schema.json"))
    ledger = read_json("monitoring/subjects/bnb/INFORMATION_EVENT_LEDGER.json")
    event_schema = read_json("monitoring/schema/information_event.schema.json")
    for event in ledger["events"]:
        jsonschema.validate(event, event_schema)
    transitions = read_json("monitoring/subjects/bnb/STATE_TRANSITION_INDEX.json")
    transition_schema = read_json("monitoring/schema/state_transition.schema.json")
    for transition in transitions["transitions"]:
        jsonschema.validate(transition, transition_schema)
    jsonschema.validate(read_json("monitoring/subjects/bnb/MONITORING_BUILD_MANIFEST.json"), read_json("monitoring/schema/monitoring_build_manifest.schema.json"))
    pass_message("MONITORING_SCHEMA_TESTS")


if __name__ == "__main__": main()
