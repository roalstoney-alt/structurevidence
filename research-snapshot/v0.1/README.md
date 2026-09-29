# StructureEvidence Minimal Research Snapshot v0.1

This offline-readable snapshot freezes the StructureEvidence method contract, 26 public claim objects, orthogonal state-normalization mapping, required protocol schemas, and six representative resolver expectations before the Vortex Discovery Pilot.

- Repository baseline: `85f625b1f1eec890bd9980e51d5e4da1078d7313`
- Protocol: `QUESTION_TO_EVIDENCE_COMMERCE_PROTOCOL_v0.1`
- Version DOI: `10.5281/zenodo.23033588`
- Concept DOI: `10.5281/zenodo.23033587`
- Claim inventory: 26 total (`CML-PDRE-001`: 9, `SE-BESS-SODIUM-001`: 9, `SE-ONC-NSQNSCLC-CN-001`: 8)

Start with `MANIFEST.json`, then inspect `method-contract.json`, `claims/index.json`, `protocol/state-normalization-v0.1.json`, and `resolver-examples.json`. Verify integrity with `SHA256SUMS.txt` from this directory.

Legacy claim `state` values are preserved. Normalized axes are additive and do not change evidence conclusions. The inference policy is closed-boundary: only explicit support authorizes reuse; undeclared inference is `OUT_OF_BOUNDARY`.
