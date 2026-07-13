# Full shallow-event raw-window quality audit

Audit date: 2026-07-13

## Download integrity

All 508 products in the corrected shallow-event plan were downloaded or reused and then verified against exact planned sizes and official NASA PDS MD5 values. The verified total is 779,909,406 bytes across 127 unique station-days. The local raw waveform tree occupies approximately 752 MiB on disk and remains excluded from Git.

## Window definition and timing

The audit covers 128 complete event-station pairs for all 74 corrected shallow events. Each raw SHZ window spans 120 s before through 480 s after the event reference. The closest valid ATT sample maps the corrected reference onto the nominal MiniSEED clock. Onodera values are event start references, not phase picks; ATT offsets are provenance/quality measurements and must not be interpreted as travel times.

Integrity status is provisional but deterministic:

- `usable_integrity`: SHZ gap fraction at most 0.20 and nearest valid ATT sample within 1 s of the reference.
- `questionable_integrity`: SHZ gap fraction at most 0.50 and nearest valid ATT sample within 10 s, but the usable thresholds are exceeded.
- `reject_integrity`: larger SHZ loss or timing displacement.

Scattered ATT sentinels elsewhere in the window are reported but do not cause automatic rejection when a valid ATT mapping exists near the event reference.

## Results

- 123 usable event-station windows.
- One questionable window: YN-SMQ-12/S14 (27.9% SHZ gaps; longest gap 124.4 s).
- Four rejected windows: YN-SMQ-5/S15, YN-SMQ-5/S16, YN-SMQ-7/S14, and YN-SMQ-11/S14.
- All 74 events retain at least one usable station window.

The rejected windows have either 81.8–100% SHZ loss or ATT displacement of roughly 95–250 s. They must not be used merely because their daily files exist.

## Descriptive signal check

Raw post-reference versus pre-reference RMS provides a screening indicator only:

- 88 windows have ratio at least 2 (`strong_ratio`).
- 23 have ratio from 1.2 to below 2 (`weak_ratio`).
- 15 have ratio below 1.2 (`no_clear_ratio`).
- Two cannot be quantified because valid comparison samples are absent.

These categories do not change physical labels, establish detections, or authorize cherry-picking. Later waveform review, preprocessing frozen on training data, and leakage-safe evaluation are still required.

Artifacts:

- `data/manifests/shallow_plan_download_receipt.json`
- `data/manifests/shallow_window_quality.csv`
- `results/predictions/shallow_window_quality_summary.json`
- `results/figures/shallow_window_quality_overview.png`
