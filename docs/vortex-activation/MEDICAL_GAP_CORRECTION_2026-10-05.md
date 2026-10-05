# VORTEX Medical Gap Correction — 2026-10-05

```ini
ACTION = FIX_MEDICAL_GAP
PUBLIC_GAP_COUNT = 6
MEDICAL_PUBLIC_BOUNDARY = PASS
PATIENT_SPECIFIC_PROBABILITY_PUBLIC_GAP = ABSENT
INDIVIDUALIZED_RECOMMENDATION_PUBLIC_GAP = ABSENT
```

## Decision

`OEG-ONC-002` no longer targets `SE-ONC-NSQNSCLC-CN-001.PATIENT_SPECIFIC_SUCCESS_PROBABILITY`. That claim remains part of the frozen medical case boundary, but it is not a public solicitation target.

The gap now targets the already-existing canonical claim:

```ini
CLAIM_ID = SE-ONC-NSQNSCLC-CN-001.IVONESCIMAB_APPROVAL
CLAIM_CLASS = REGULATORY_STATUS / INDICATION_SCOPE
CURRENT_STATE = SUPPORTED
SCOPE = Population-level regulatory status in China for the regulator-defined post-EGFR-TKI non-squamous NSCLC indication
```

The replacement is public-research appropriate, aggregate/population scoped, falsifiable, and challengeable through official primary regulatory evidence. A qualifying challenge would require an official regulator update, expansion, narrowing, suspension, withdrawal, correction, or an authoritative correction/retraction of the cited approval source.

## Frozen gap audit

The following hashes are the SHA-256 of each gap's JSON serialization before and after correction:

| Gap | Before | After | Result |
|---|---|---|---|
| OEG-CML-001 | `1b93172c76b6f6eca76380fd92bf185806d1ad14eb99c32b5693a3d8c81a895b` | `1b93172c76b6f6eca76380fd92bf185806d1ad14eb99c32b5693a3d8c81a895b` | UNCHANGED |
| OEG-CML-002 | `defa59b1a9d9eebe3799dc47773f9c9762493e21d34651749eea6a170934f941` | `defa59b1a9d9eebe3799dc47773f9c9762493e21d34651749eea6a170934f941` | UNCHANGED |
| OEG-BESS-001 | `19bf13f252597f84757e49ea04794335a3dd53f1c14737cad7b07b7fa8d9b461` | `19bf13f252597f84757e49ea04794335a3dd53f1c14737cad7b07b7fa8d9b461` | UNCHANGED |
| OEG-BESS-002 | `c90d65b054e78ec7249d446d67efde39b7c1dffb29534d1b20ff0d1b3ffd4446` | `391ca899538359dbe9c66754a5f13c05092b9a2ed818969469385e0c548980e8` | WORDING ONLY |
| OEG-ONC-001 | `5a884c147daef52d6bfdfd557cf9959de3c09d15eef5fd4e0e56acf2f338ea30` | `5a884c147daef52d6bfdfd557cf9959de3c09d15eef5fd4e0e56acf2f338ea30` | UNCHANGED |
| OEG-ONC-002 | `f18966796038aef618b34791a110d397f05bafa93913015a941b2ad660088f42` | `2dfdce67e1009a217e121793abef83e18dab0922216a94ca4b963765b01738f0` | REPLACED |

## BESS-002 wording review

The canonical claim, state, scope, and evidence cut-off are unchanged. External wording now explicitly requires attributable independent field-operation or performance evidence collected after commissioning. Operating duration, availability, delivered capacity or energy, degradation, cycle history, and reliability are examples; they are not an all-at-once checklist.

Manufacturer brochures, generic specifications, lab-only tests, simulations, planned deployments, shipment without commissioning, and unattributed charts do not establish independent field performance.

## Regression protection

The Worker test suite now fails if any public medical Gap contains patient-specific probability, personalized prognosis, individualized treatment, personal success, patient-specific benefit, or patient-specific survival semantics. It also verifies:

- the unsafe claim ID is absent from the public gap registry;
- the replacement matches the existing canonical claim file;
- ECMO is not represented as tumor therapy;
- the four hard-frozen gaps retain their exact serialization hashes;
- OEG-BESS-002 retains its canonical claim while applying wording-only changes.
