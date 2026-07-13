# Nonshallow Batch 1 download and window audit

Audit date: 2026-07-13

## Download integrity

Batch 1 contains 5,398 products across 845 station-days and totals exactly 2,142,346,643 bytes. Every MiniSEED/XML product passed exact-size and official NASA PDS MD5 verification. Server throttling produced several invalid/partial responses during acquisition; none was accepted. The shared verifier was hardened to delete and retry completed responses that fail integrity, and the final low-concurrency reconciliation verified all products.

## Covered data

The batch fully covers 658 physical events, 842 event-station requests, and 2,234 positively reported channel windows: 334 assigned deep moonquakes, two unclassified deep moonquakes, 314 natural impacts, four LM artificial impacts, and four S-IVB artificial impacts.

Only requests whose ATT and positive-channel MiniSEED/XML products for every required boundary day belong to Batch 1 were audited.

## Integrity result

The provisional integrity gates are applied channel-wise: at most 20% gaps and nearest valid ATT within 1 s is usable; at most 50% and 10 s is questionable; larger loss/displacement is rejected. Signal amplitude and raw min/max occupancy remain descriptive.

| Level | Usable | Questionable | Rejected | Total |
|---|---:|---:|---:|---:|
| Channel window | 2,195 | 7 | 32 | 2,234 |
| Event-station request | 827 | 3 | 12 | 842 |
| Physical event | 648 | 2 | 8 | 658 |

## Suspicious-case review

The two questionable events have small gaps but ATT displacement above 1 s: `levent-04549` (natural impact, S12/S14, 5.617 s) and `levent-06219` (assigned deep, S12, 4.268 s).

| Rejected event | Class | Main integrity evidence |
|---|---|---|
| `levent-01686` | Assigned deep | 79.9% gaps; ATT displacement 5,254 s |
| `levent-02343` | Natural impact | ATT displacement 37,041 s |
| `levent-02705` | Natural impact | 81.2% gaps; ATT displacement 335 s |
| `levent-06818` | Natural impact | 79.9% gaps; ATT displacement 8,942 s |
| `levent-06879` | Assigned deep | 79.9% gaps; ATT displacement 317 s |
| `levent-07904` | Natural impact | 79.9% gaps; ATT displacement 1,102 s |
| `levent-07944` | Assigned deep | ATT displacement 338 s |
| `levent-09154` | Natural impact | 100% waveform loss despite valid nearby ATT |

The overview figure was visually reviewed. Most windows cluster below the 20% gap threshold, with a small separated high-gap population. Constant/extreme-dominated windows are recorded by `edge_value_fraction_descriptive` but are not independently rejected or relabeled.

## Registry effect

The registry marks 648 Batch 1 nonshallow events `candidate_integrity_audited`, two `candidate_questionable_integrity`, and eight `excluded_failed_integrity`. The remaining 582 nonshallow candidates are pending; physical labels and leakage groups are unchanged.

Artifacts: `nonshallow_batch_1_download_receipt.json`, `nonshallow_batch_1_window_quality.csv`, `nonshallow_batch_1_request_quality.csv`, `nonshallow_batch_1_quality_summary.json`, and `nonshallow_batch_1_quality_overview.png` in their standard manifest/results directories.
