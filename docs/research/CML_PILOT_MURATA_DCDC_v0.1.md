# MURATA_DCDC_NRND Research Record v0.1

## Research Question

What technical decision is currently defensible for `MYMGM5R012ELA5RND` under reviewed public evidence?

## Target

Murata Manufacturing / `MYMGM5R012ELA5RND` / MonoBK 12 A DC-DC converter series.

## Primary Evidence

- [Murata Manufacturing: MURATA_MYMGM5R012_DS](https://pim.murata.com/asset/pim4/nonIsolatedDCDCconverter/MYMGM5R012ELA5RN_PDF_NONISOLATEDDCDCCONVERTER)
- [Murata Manufacturing: MURATA_POWER_EOL_INDEX](https://www.murata.com/en-global/products/power/discontinued-and-not-recommended)

## Event Chronology

- Effective at: `2025-07-07T00:00:00Z`
- Known at: `2026-09-16T00:00:00Z`
- Event: `NRND_DECLARED`
- The reviewed Murata datasheet identifies the D-suffix variant as NRND; an earlier effective date is not established, so the document revision date is used as the observable boundary with limitation.

## Technical Requirements and Known Dependency

Input range, output voltage/current, regulation, efficiency, control polarity, pinout, thermal derating and board layout define migration scope.

## Known Facts

- SOURCE_FACT: MYMGM5R012ELA5RND is marked NRND in the manufacturer datasheet.
- SOURCE_FACT: The series is a 12 A non-isolated DC-DC converter with 7.5-15 V input and a 10.5 x 9.0 x 5.0 mm package class.
- SOURCE_FACT: Murata maintains a separate discontinued/NRND index and a DC-DC cross-reference surface.

## OEM Replacement and Alternative Paths

`OEM_REPLACEMENT_UNRESOLVED`. No candidate is represented as qualified. Supported management paths: MONITOR, QUALIFY_SECOND_SOURCE, REDESIGN.

## Compatibility and Verification

- No-load and full-load
- Load transient
- Line transient
- Startup and shutdown
- Ripple and noise
- Efficiency
- Thermal derating
- Short circuit
- EMI/EMC
- Temperature sweep

## Counter-Evidence

The base series remains documented and only a specific suffix is visibly marked NRND. This may reduce immediate operational impact if the customer uses another orderable suffix; BOM identity must be exact.

## Unknowns

- An exact OEM successor for this suffix is not established in the reviewed snapshot.
- Customer output setpoint, transient limits, EMI class and thermal environment are unknown.
- No bench comparison or customer qualification evidence is present.

## Recommended Action

Freeze the exact suffix and customer operating envelope, then request Murata cross-reference confirmation. Any candidate remains paper-level until electrical, thermal and EMI verification is complete.

## Freshness

`POLICY_NOT_CONFIGURED_EVENT_REVIEWED` as evaluated `2026-09-16T00:00:00Z`. No universal CML max-age rule is used.

## Limitations

Public-evidence pilot only. No client BOM, application envelope, samples, bench data, supplier qualification or universal-equivalence conclusion is present.
