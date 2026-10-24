import unittest

from scripts.se_unified_ops import validate_event_record


class CompactInformationEventCompatibilityTest(unittest.TestCase):
    def test_compact_information_event_remains_compatible(self):
        compact = {
            "schema_version": "se-information-event-v1",
            "event_id": "EV-COMPACT-1",
            "case_id": "CML-PDRE-001",
            "event_at": "2026-10-21",
            "published_at": "2026-10-21",
            "retrieved_at": "2026-10-22T14:02:00Z",
            "original_url": "https://origin.example/compact-event",
            "public_url": "https://structurevidence.org/cases/800vdc/events/compact-event/",
            "snapshot_file": "snapshot-v1.json",
            "snapshot_sha256": "b" * 64,
            "verification_status": "PRIMARY_SOURCE_READ",
            "classifications": ["NEW_EVENT", "NO_STATE_CHANGE", "HUMAN_GATE_REQUIRED"],
            "old_stop": "UNCHANGED",
            "candidate_stop": "UNCHANGED",
            "state_changed": False,
        }
        validate_event_record(compact)


if __name__ == "__main__":
    unittest.main()
