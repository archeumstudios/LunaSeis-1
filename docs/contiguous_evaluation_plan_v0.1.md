# Untouched contiguous evaluation plan v0.1

Date: 2026-07-14

## Selection

The frame was selected before reading catalog coverage or model scores. For each of S12, S14, S15, and S16, the planner enumerated official PDS archive days, excluded 3,146 station-days already exposed by committed manifests, hash-ranked all valid 14-day contiguous starts using seed `lunaseis-contiguous-evaluation-v0.1`, and retained two nonoverlapping blocks. Blocks are never replaced after channel or catalog inspection.

The resulting frame contains 112 station-days—28 per station and 2,688 station-hours. All 112 days have ATT plus a primary MH channel. The minimum plan contains the MiniSEED and PDS label for ATT and the preferred available MHZ/MH1/MH2 channel: 448 products, 171,375,344 bytes (163.44 MiB / 0.15961 GiB). Every product has an archive-listed size and official NASA MD5. No waveform was downloaded during planning.

## Blocks

| Block | Dates by year/day-of-year | Days | Bytes |
|---|---|---:|---:|
| S12_B1 | 1975/006–019 | 14 | 21,418,334 |
| S12_B2 | 1976/033–046 | 14 | 21,422,430 |
| S14_B1 | 1975/287–300 | 14 | 21,516,638 |
| S14_B2 | 1975/346–359 | 14 | 21,381,470 |
| S15_B1 | 1973/314–327 | 14 | 21,422,430 |
| S15_B2 | 1975/347–360 | 14 | 21,401,950 |
| S16_B1 | 1976/040–053 | 14 | 21,381,470 |
| S16_B2 | 1976/303–316 | 14 | 21,430,622 |

## Post-selection catalog audit

The selected station-days contain 315 station-specific references to 263 unique PDS or corrected-Onodera catalog times. These references did not influence selection. All catalog times will be protected from false-positive accounting using the frozen matching sensitivities.

Only seven unified candidates have no prior role in that station fold and are therefore prospectively eligible for untouched event recall: five natural impacts and two assigned deep moonquakes. Sixteen candidate occurrences are excluded from event-recall claims because their groups appeared in prior train, validation, or inspected pilot-test outputs. The remaining 292 references are catalog-exclusion-only. The seven candidates still require downloaded station waveform QA; their presence does not guarantee visibility.

Seven possible events are too few for a stable headline recall estimate. The frame is nevertheless substantial for the primary continuous false-trigger audit. Event recall will be reported descriptively with exact counts and uncertainty, not generalized beyond this frame.

## Authorization

The plan passes prior-day overlap, station balance, channel completeness, checksum, storage, and post-selection exposure audits. Download is authorized, but model scoring remains prohibited until all 448 products pass size/MD5 verification and every day passes the frozen waveform/ATT integrity audit.
