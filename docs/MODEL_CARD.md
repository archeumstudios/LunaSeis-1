# LunaSeis-1 depthwise CNN — model card

## Identity

- Author: **Advaith Praveen (APRK)**
- Organization: Archeum Studios
- Version: 0.1.0 research prototype
- Architecture: 2,761-parameter depthwise-separable 1D CNN
- Checkpoints: one leave-one-station-out checkpoint for each of S12, S14, S15, and S16

## Intended use

Research, education, reproducibility studies, and candidate-window prioritization on Apollo PSE mid-period waveform data. The interface selects a model trained without the requested station.

Not intended for flight systems, autonomous scientific declarations, safety-critical decisions, discovery claims, or use on instruments other than the documented Apollo PSE channels without new validation.

## Input and output

Input is a 600-second MH waveform at native archive cadence. `-1` gap sentinels are preserved through a validity mask. Valid samples are centered by their window median, divided by `max(1, 1.4826 MAD, p90 absolute deviation / 2.5)`, clipped to ±20, and padded/cropped to 4,096 samples.

Output is a sigmoid score and a station-fold development threshold. The score is not a calibrated probability. A trigger is only a model candidate, not a confirmed moonquake.

## Development selection

The model was selected after comparing robust tiny CNN, depthwise CNN, and compact TCN candidates on 56 development-only continuous station-days. Thresholds retained at least 90% of leakage-controlled positive-validation events.

| Model | Mean development event recall | Merged triggers/hour |
|---|---:|---:|
| Depthwise CNN | 0.9115 | 0.2106 |
| Robust tiny CNN | 0.9115 | 0.4102 |
| Compact TCN | 0.9115 | 0.4558 |

These are development metrics, not untouched-test results.

A full-day S15 CLI smoke scan produced 1,429 windows, of which 1,418 passed integrity; all 1,418 scored windows exceeded the development threshold. They merge into persistent activation rather than 1,418 independent physical events. This confirms that trigger frequency alone is insufficient and the prototype does not yet provide useful retention on every day.

## Critical evaluation history

Earlier model generations failed two frozen continuous scans. Test v0.1 recovered at most 1/6 events; test v0.2 recovered 0/3. The depthwise CNN was developed afterward and is not retroactively claimed to pass those consumed frames.

## Known limitations

- No prospectively untouched event-rich test remains in the current catalog pool.
- Station quantization and artifact distributions differ greatly.
- Many catalog events have weak or unclear waveform evidence near their recorded references.
- Development thresholds may transfer poorly to new years, stations, channels, or acquisition regimes.
- Catalog-negative background may include uncatalogued seismic activity.
- Confidence calibration is not claimed because final-test recall was inadequate.

## Ethical/scientific safeguards

Do not remove the warning metadata, call scores probabilities, or claim unknown-event discovery without expert review and a new preregistered evaluation. Preserve source timestamps, station/channel identity, gaps, and data provenance.
