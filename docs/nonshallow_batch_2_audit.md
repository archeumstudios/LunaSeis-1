# Nonshallow Batch 2 waveform-integrity audit

Date: 2026-07-13

## Scope and receipt

Batch 2 contains 3,270 planned PDS products across 502 station-days. All products were downloaded or reused and independently re-read from disk against their exact planned size and official NASA MD5. The verified total is 2,145,595,149 bytes. Raw waveform files remain ignored and are not committed.

## ATT-aware window audit

The unchanged Batch 1 procedure audited 599 physical events, 599 event-station requests, and 1,337 positive-channel windows. Integrity classification uses only waveform gaps and nearest valid ATT displacement around the catalog reference. Raw range, edge-value occupancy, and pre/post RMS are descriptive and do not alter labels.

| Level | Usable | Questionable | Rejected |
|---|---:|---:|---:|
| Channel window | 1,306 | 5 | 26 |
| Event-station request | 586 | 3 | 10 |
| Physical event within Batch 2 | 586 | 3 | 10 |

Covered physical classes are 315 assigned deep moonquakes, one unclassified deep moonquake, 280 natural impacts, two LM impacts, and one S-IVB impact.

## Suspicious-case review

The three questionable requests are `levent-05491` (37.7% SHZ gaps but close ATT mapping), `levent-06219` (nearest ATT offset 5.053 s), and `levent-11383` (25% SHZ gaps and nearest ATT offset 7.677 s). These remain explicit sensitivity-analysis cases.

The ten rejected requests are `levent-05363`, `levent-05474`, `levent-05476`, `levent-05634`, `levent-06620`, `levent-06623`, `levent-08545`, `levent-09548`, `levent-10250`, and `levent-10548`. Their evidence is severe local waveform loss and/or ATT displacement, not signal amplitude. Some events also occur in Batch 1 at another station; the unified event-level registry accepts an event if at least one audited station is usable while preserving rejected stations in provenance.

The aggregate figure was visually inspected. Most windows have low gap fractions, with a separated high-gap tail. The RMS and edge-occupancy panels remain descriptive and are not exclusion gates.

## Registry result

After attaching Batches 1 and 2, 946 nonshallow events have at least one usable audited station, three are questionable, nine have only rejected audited requests, and 282 remain uncovered by the audited batches. Together with 74 shallow events, the unified candidate statuses are 1,020 integrity-audited, three questionable, nine failed-integrity exclusions, and 282 pending waveform QA. All event labels and evaluation groups are unchanged.

The thresholds remain provisional until all batches are complete and a sensitivity analysis is performed.
