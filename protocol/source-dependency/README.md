# Source Dependency Protocol v0.1

This protocol records who originated a source and whether another URL is an
independent observation or only another rendering/retelling. It does not infer
truth, alter a case state, or treat URL count as evidence count.

The v0.1 static registry is intentionally empty. PR-A establishes the
backwards-compatible row contract and gap-specific rule registry without
reclassifying historical evidence. A later append-only review may add grounded
rows for the existing 800VDC case after human approval.

## Classification boundaries

- `ISSUER_AUTHORED`: the issuer/operator authored the record, even on another host.
- `DERIVED`: the record reproduces or summarizes identified originating evidence.
- `PARTIALLY_DEPENDENT`: authorship/observation has a disclosed mixed relationship.
- `INDEPENDENT`: attributable authorship and observation are independent for the scoped issue.
- `UNKNOWN`: independence could not be established; no undisclosed interest is guessed.

Evidence levels are `E0` intent, `E1` design/specification, `E2` simulation/lab,
`E3` unattributed field-operation assertion, `E4` attributable field operation
or commissioning with the required context, and `E5` independent attributable
field evidence. Evidence level alone never determines truth or state. The
versioned gap rule controls qualification; E5 is not a universal minimum.

`scripts/source_dependency_v01.py` validates rows, hashes immutable events,
enforces append-only supersession, applies explicit qualification rules, and
computes deterministic counts with their exact row membership and scope.
Zero counts mean zero only inside the declared sample. If no denominator exists,
coverage is `INSUFFICIENT_DATA` and percentage is `null`, never `0%`.
