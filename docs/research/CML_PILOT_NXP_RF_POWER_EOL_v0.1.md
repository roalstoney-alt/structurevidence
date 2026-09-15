# NXP_RF_POWER_EOL Research Record v0.1

## Research Question

What technical decision is currently defensible for `RADIO-POWER-2026-FAMILY` under reviewed public evidence?

## Target

NXP Semiconductors / `RADIO-POWER-2026-FAMILY` / Radio Power discontinuance / selected representatives.

## Primary Evidence

- [NXP Semiconductors: NXP_202603037DN](https://www.nxp.com/pcn/202603037DN)
- [NXP Semiconductors: NXP_MRF101AN_DS](https://www.nxp.com/docs/en/data-sheet/MRF101AN.pdf)
- [NXP Semiconductors: NXP_MW6S010N_PAGE](https://www.nxp.com/products/radio-frequency-rf/legacy-rf/legacy-rf-power/450-1500-mhz-10-w-28-v-lateral-n-channel-broadband-rf-power-mosfets%3AMW6S010N)
- [NXP Semiconductors: NXP_MMRF1009H_DS](https://www.nxp.com/docs/en/data-sheet/MMRF1009H.pdf)

## Event Chronology

- Effective at: `2026-04-01T00:00:00Z`
- Known at: `2026-03-31T00:00:00Z`
- Event: `EOL_DECLARED`
- Final Radio Power discontinuance notice lists full withdrawal, limited availability, sole-source classification, 2026-09-30 LTB and 2027-09-30 last delivery for selected representatives.

## Technical Requirements and Known Dependency

Device package, bias, frequency, power, thermal path, matching network, PCB layout and ruggedness form a board-level dependency.

## Known Facts

- SOURCE_FACT: NXP's final notice states the Radio Power product line is being ramped down.
- SOURCE_FACT: MRF101AN, MW6S010GNR1 and MMRF1009HR5 are listed with no replacement and a 2026-09-30 LTB.
- SOURCE_FACT: MRF101AN is a 50 V wideband 1.8-250 MHz device; MW6S010GNR1 is a 28 V 450-1500 MHz 10 W class device; MMRF1009HR5 is a 50 V 960-1215 MHz 500 W pulse device.

## OEM Replacement and Alternative Paths

`OEM_REPLACEMENT_NOT_LISTED`. No candidate is represented as qualified. Supported management paths: LIFETIME_BUY, QUALIFY_ALTERNATIVE, REDESIGN.

## Compatibility and Verification

- S-parameters where applicable
- Small-signal stability
- Gain and output power
- PAE or drain efficiency
- Harmonics
- Thermal characterization
- Load-mismatch ruggedness
- Temperature sweep
- Long-duration operation

## Counter-Evidence

Some NXP overview surfaces have retained an Active label for MRF101AN. The later dated discontinuance notice and package status are treated as stronger lifecycle evidence, while the conflict remains visible.

## Unknowns

- No reviewed evidence establishes a board drop-in successor for any selected device.
- Application-specific matching networks, thermal margins and stability criteria are unknown.
- The MRF101AN overview has shown an inconsistent Active label while package/quality and the discontinuance notice indicate EOL.

## Recommended Action

Treat the notice as a lifecycle trigger. Separate lifetime-buy analysis from engineering migration; any alternate device requires board-level RF and thermal qualification.

## Freshness

`CURRENT_WITH_LIMITATIONS` under `EVENT_DRIVEN` because `MANUFACTURER_INTERFACE_STATUS_CONFLICT`, as evaluated `2026-09-16T00:00:00Z`. No universal CML max-age rule is used.

## Limitations

Public-evidence pilot only. No client BOM, application envelope, samples, bench data, supplier qualification or universal-equivalence conclusion is present.
