# AMPHENOL_EOL_CONNECTOR Research Record v0.1

## Research Question

What technical decision is currently defensible for `10081811-101-07LF` under reviewed public evidence?

## Target

Amphenol Communications Solutions / `10081811-101-07LF` / HPL-578 BERGSTIK.

## Primary Evidence

- [Amphenol Communications Solutions: AMPHENOL_PCN_26027](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/8899/PCN-26027.pdf)

## Event Chronology

- Effective at: `2027-03-15T00:00:00Z`
- Known at: `2026-03-16T00:00:00Z`
- Event: `EOL_DECLARED`
- PCN 26 027 lists the part in an end-of-life action with last-time buy 2026-09-15 and last shipment 2027-09-15.

## Technical Requirements and Known Dependency

Existing PCB footprint, mating half, contact geometry, plating and electrical loading may constrain migration.

## Known Facts

- SOURCE_FACT: PCN 26 027 lists four affected BERGSTIK part numbers, including the exact MPN.
- SOURCE_FACT: Last-time buy is 2026-09-15; effective change is 2027-03-15; last shipment is 2027-09-15.
- SOURCE_FACT: The available-alternatives field is blank in the reviewed notice.

## OEM Replacement and Alternative Paths

`OEM_REPLACEMENT_NOT_LISTED`. No candidate is represented as qualified. Supported management paths: LIFETIME_BUY, QUALIFY_SECOND_SOURCE, REDESIGN.

## Compatibility and Verification

- Mechanical drawing comparison
- PCB footprint inspection
- Contact resistance
- Insulation resistance
- Dielectric withstand
- Solderability
- Insertion and retention force
- Thermal cycling
- Mating compatibility

## Counter-Evidence

A later public Amphenol EOL list appears to include the same MPN under PCN 26043 with a different effective date. This may be an overlapping notice or later schedule and must be reconciled with Amphenol before procurement action.

## Unknowns

- An OEM-approved replacement is not established by the reviewed evidence.
- Exact footprint, mating and plating equivalence for any third-party candidate is not established.
- A second Amphenol EOL listing with a different effective date requires manufacturer clarification.

## Recommended Action

Confirm remaining demand before the stated LTB boundary and begin a scope-bound second-source or redesign qualification. No qualified substitute is established.

## Freshness

`EVENT_DRIVEN_CURRENT_WITH_SOURCE_CONFLICT` as evaluated `2026-09-16T00:00:00Z`. No universal CML max-age rule is used.

## Limitations

Public-evidence pilot only. No client BOM, application envelope, samples, bench data, supplier qualification or universal-equivalence conclusion is present.
