# RF40_CABLE_ASSEMBLY Research Record v0.1

## Research Question

What technical decision is currently defensible for `095-725-134-006` under reviewed public evidence?

## Target

Amphenol RF / `095-725-134-006` / 2.92 mm plug to SMPM plug cable assemblies.

## Primary Evidence

- [Amphenol RF: AMPHENOL_RF_40GHZ_PRODUCT](https://www.amphenolrf.com/en-us/part/095-725-134-006/10205/)
- [Amphenol RF: AMPHENOL_RF_40GHZ_CUTSHEET](https://www.amphenolrf.com/library/download/link/link_id/600711/)

## Event Chronology

- Effective at: `2026-05-07T00:00:00Z`
- Known at: `2026-09-16T00:00:00Z`
- Event: `CANDIDATE_IDENTIFIED`
- Active manufacturer reference assembly selected as a qualification benchmark; this is not an EOL event.

## Technical Requirements and Known Dependency

Complete-assembly electrical performance depends on both connectors, cable, termination process, bend history, length and calibration reference plane.

## Known Facts

- SOURCE_FACT: The exact assembly is listed Active, 6.00 in (153 mm), 50 ohm, and 40 GHz maximum.
- SOURCE_FACT: Interfaces are 2.92 mm straight plug to SMPM straight plug on 0.085-inch conformable cable.
- SOURCE_FACT: The family cutsheet states DC-40 GHz interface ranges and warns specifications may vary by exact part number.

## OEM Replacement and Alternative Paths

`OEM_REPLACEMENT_UNRESOLVED`. No candidate is represented as qualified. Supported management paths: QUALIFY_SECOND_SOURCE, MONITOR.

## Compatibility and Verification

- Calibrated VNA with defined reference planes
- S11 and return loss
- S21 and insertion loss
- VSWR
- Mating repeatability
- Mechanical inspection
- Flex behavior
- Temperature behavior
- Phase stability only when required

## Counter-Evidence

The item is an active off-the-shelf assembly, so substitution may not be operationally necessary. The pilot tests whether CML can structure qualification evidence without inventing a lifecycle crisis.

## Unknowns

- No independent VNA trace, per-unit insertion-loss limit or return-loss acceptance curve is present.
- Power handling, phase stability and flex-life limits are not established in reviewed evidence.
- No alternate supplier assembly has been qualified against this benchmark.

## Recommended Action

Use the exact assembly as a benchmark, not as proof that any cable using 40 GHz-capable connectors is equivalent. Freeze VNA method and acceptance limits before supplier comparison.

## Freshness

`POLICY_NOT_CONFIGURED_ACTIVE_BASELINE` as evaluated `2026-09-16T00:00:00Z`. No universal CML max-age rule is used.

## Limitations

Public-evidence pilot only. No client BOM, application envelope, samples, bench data, supplier qualification or universal-equivalence conclusion is present.
