# 0010 — Separate raw-window integrity from signal strength

Date: 2026-07-13

## Decision

Gate shallow event-station windows using explicit SHZ gap and nearest-valid-ATT criteria. Keep raw post/pre RMS as descriptive evidence only; it may not change a catalog label or determine integrity acceptance.

Usable windows have at most 20% SHZ gaps and a valid ATT sample within 1 s of the reference. Questionable windows may have at most 50% SHZ gaps and a valid ATT sample within 10 s. Larger loss or timing displacement is rejected. These thresholds are provisional and must be sensitivity-tested before protocol freeze.

## Rationale

Daily-product availability overstated usable coverage. Four of 128 complete-file event-station pairs contain severe local loss or timing displacement. Conversely, rejecting a window for any scattered ATT sentinel would incorrectly discard otherwise intact data. Signal amplitude cannot be an acceptance criterion without creating label-conditioned selection bias and overstating catalog confirmation.

## Consequences

All 74 events retain at least one usable station, but rejected station windows remain excluded from downstream window construction. No model training is authorized until broader positive/background construction and split freezing are complete.
