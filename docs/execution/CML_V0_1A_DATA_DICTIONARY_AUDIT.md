# CML v0.1a Data Dictionary Audit

`CML_TECHNICAL_RISK_DATA_DICTIONARY_v0.1.md` is generated from the Evidence Core schema, CML public-record schema, test-requirement schema, release-manifest schema and public/private boundary configuration.

The machine-readable path index is `technical-risk/validation/CML_DATA_DICTIONARY_INDEX.json`. `scripts/test_cml_dictionary_drift.py` independently derives the authoritative path set and fails when a schema/config path is absent from the dictionary or when the stored index drifts.

Private-reserved engagement fields are included as prohibited Public Verify paths rather than being modeled as public-record properties.
