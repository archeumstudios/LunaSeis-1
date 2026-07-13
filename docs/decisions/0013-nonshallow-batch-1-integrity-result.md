# 0013 — Attach Batch 1 integrity outcomes without amplitude-based label filtering

Date: 2026-07-13

## Decision

Attach Batch 1 event/station/channel integrity outcomes to the unified registry. Retain 648 covered events as integrity-audited candidates, flag two as questionable, and exclude eight from the usable candidate pool for severe gap/ATT integrity failures. Preserve every audit record and original physical label. Do not use raw RMS or min/max occupancy to accept, reject, or relabel events.

## Rationale

Gap and ATT failures directly prevent reliable extraction of the intended catalog-reference window. Signal-conditioned filtering would create selection bias and could erase genuine low-SNR events. The questionable ATT offsets require later timing sensitivity rather than automatic acceptance or rejection.

## Consequences

Batch 2 may proceed using the same integrity gate. Thresholds remain provisional until all batches are audited and sensitivity-tested. No model training or background sampling is authorized yet.
