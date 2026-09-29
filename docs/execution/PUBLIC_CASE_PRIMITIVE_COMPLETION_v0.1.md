# Public Case Primitive Completion v0.1

Entry SHA: `8d4b028d3d0e113290ed5309e868fe300b5b9efd`

## Scope

This completion adds only missing versioned governance primitives for the three
existing public cases. It uses already published or frozen repository records. It
does not add external research, change a research conclusion, change an evidence
state, alter CML v1.1 or RDL history, change the Case Watch weekly decisions, publish
new substantive evidence, or deploy a site.

## Completed primitives

- `CML-PDRE-001`: added a mirrored public `state-v0.1.json` derived from the current
  public page, stop point, publication control, and approved L1 record.
- `SE-BESS-SODIUM-001`: added a mirrored `publication-control-v0.1.json`; human
  authority and decision date are `NOT_RECORDED` because the source artifacts do not
  explicitly record them.
- `SE-ONC-NSQNSCLC-CN-001`: added a mirrored
  `publication-control-v0.1.json` preserving the public-research and medical boundary.
- `SE-ONC-NSQNSCLC-CN-001`: added a mirrored Decision Memory using the existing
  `STRUCTEVIDENCE_DECISION_MEMORY_v0.1` schema. It is a public research-case memory,
  not a patient decision record.

No index or sitemap change was required. The existing site does not list individual
JSON governance artifacts in the sitemap, and every public case already exposes its
current state or stop point.

## Preserved boundaries

- 800VDC remains `HUMAN-REVIEWED SINGLE-INSTANCE EVIDENCE`; full PDRE validation,
  operating history, replication, independent validation, repeat procurement, and
  industry adoption remain unestablished.
- Sodium-ion remains product-and-agreement supported with named commissioned site not
  established.
- NSCLC remains a public research preview with no patient-specific recommendation,
  probability, prognosis, or cross-modality ranking.
- Publication state is recorded separately from research state; every new primitive
  explicitly records zero research-state and historical mutation.

## Validation

The focused test suite checks primitive existence, byte-for-byte root/docs parity,
historical immutability against the entry SHA, CML/RDL non-mutation, bounded-state
preservation, no new external URLs, medical boundaries, publication semantics,
Decision Memory schema and hashes, and Case Watch compatibility.
