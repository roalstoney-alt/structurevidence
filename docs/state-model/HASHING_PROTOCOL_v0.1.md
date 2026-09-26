# SE-FRR Hashing Protocol v0.1

Status: frozen for SE-FRR-001 Phase 1.

Objects are serialized as UTF-8 JSON with recursively sorted object keys, no insignificant whitespace, Unicode preserved, and non-finite numbers rejected. Array order remains significant. This produces deterministic bytes for semantically identical JSON object-key orderings.

## Object hashes

- Evidence `content_hash`: SHA-256 of the full Evidence object excluding only `content_hash`.
- State `state_hash`: SHA-256 of the full State object excluding only `state_hash` and `chain_hash`.
- Change `change_hash`: SHA-256 of the full Change object excluding only `change_hash`.

All substantive timestamps, review data, references, visibility, and provenance participate. Pretty-printing and object key order do not.

## State chain

For the first State, `chain_hash = SHA256(state_hash)`. For every later State, `chain_hash = SHA256(previous_chain_hash + state_hash)`, where the concatenated values are lowercase ASCII hexadecimal. `previous_state_id` and `previous_state_hash` must identify the immediately preceding State for the subject when ordered by `recorded_at`, then stable ID.

Any content mutation changes `state_hash`; the verifier then reports the altered object and all chain consequences. Hashing provides tamper evidence, not identity authentication or digital signatures.
