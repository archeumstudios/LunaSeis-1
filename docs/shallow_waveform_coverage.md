# Shallow-event waveform coverage and storage plan

Audit date: 2026-07-13

The availability audit checks daily Apollo PSE directories for SHZ MiniSEED, ATT timing MiniSEED, and both PDS XML labels. It does not download waveform data and does not claim that an event window is gap-free or usable.

## Result

- Events: 74; all have at least one complete station-day.
- Requested event-station pairs: 136; complete pairs: 128; unavailable pairs: 8.
- Unique complete station-days after deduplication: 127.
- Exact download plan: 508 products, 779,909,406 bytes (743.78 MiB; 0.72635 GiB).
- Every planned product has its expected MD5 from the official PDS bundle manifest.

The unavailable pairs are expected archive/deployment gaps, including pre-deployment station-days; they do not remove an event when another reported/audited station is available. Full Earth-day files are necessary because PDS distributes these channels as daily products. The exact paths, sizes, URLs, and expected MD5 values are in `data/manifests/shallow_pilot_download_plan.json`; pair-level results are in `data/manifests/onodera_2024_shallow_coverage.csv`.

This is a storage plan, not authorization to download. Budget at least 1.5 GiB of free working space for the 0.73 GiB raw selection plus temporary files, indexes, and processed event windows. Model checkpoints and caches require a separate later budget.

Rebuild with:

```bash
.venv/bin/python scripts/build_shallow_download_plan.py
```
