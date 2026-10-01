# Contributing public evidence

StructEvidence records how public evidence changes the bounded state of technical and industrial claims. The canonical public records are at [structurevidence.org](https://structurevidence.org/); this repository is the verification and reproduction layer.

## Contribution types

- `NEW_EVIDENCE`
- `COUNTER_EVIDENCE`
- `SOURCE_CORRECTION`
- `STATE_CHALLENGE`
- `SEARCH_SCOPE_CHALLENGE`
- `REPRODUCTION_RESULT`

Submitting evidence does not imply acceptance. Every submission is evaluated under the StructEvidence evidence protocol. A failed search or absent public record is not evidence that an event does not exist.

Use the matching issue template and identify the affected case and claim. Include a public source URL, source date, what the source supports, known limitations, and any relationship you have to the source. Do not submit personal medical records, trade secrets, customer-confidential material, or private identifying information.

Accepted changes preserve prior states. Corrections and superseding evidence are appended; history is not silently overwritten.

## Reproducing public exports

```sh
python3 scripts/export_public_records.py
python3 scripts/check_public_record_drift.py
python3 scripts/audit_internal_links.py
python3 -m unittest tests.test_seo_surface tests.test_public_record_export
```
