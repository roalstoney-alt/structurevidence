# CML-PDRE-001 Dependency Transfer Reconstruction

Canonical machine-readable mapping: `rdl/research/records/CML-PDRE-001-PHASE-2/dependency-mappings.json`.

## PDRE-001A

| Layer | Reconstructed repository state |
| --- | --- |
| Old dependency | 54V rack-level high-current distribution and rack-local conversion |
| Constraint | Current, copper, rack space, thermal, power-shelf space |
| Alternative path | 800VDC sidecar / power rack |
| Dependency released | Candidate only |
| Directly referenced new dependencies | DC/DC conversion, DC protection, energy storage |
| Packet classifications without item-level references | DC arc flash, HVDC connector/busway, insulation, fault isolation, thermal management |
| New bottleneck severity | `UNKNOWN` |
| Migration readiness | Existing CML `R3` |
| Structural exposure | `UNKNOWN` |

The latter packet classifications are preserved as classifications, not promoted to independently evidenced facts.

## PDRE-001B

The old and alternative path scopes exist, but constraint, release, dependency creation, new bottleneck, readiness, and structural exposure remain `UNKNOWN` or `NOT_ASSIGNED`. No PDRE-001A evidence is merged into this unit.

## Law

`DEPENDENCY_RELEASE != DEPENDENCY_TRANSFER`. RDL reconstructs references; CML retains structural interpretation authority.
