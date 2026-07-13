# KO-SMQ-26 representative waveform audit

Audit date: 2026-07-13

## Selection and integrity

KO-SMQ-26 at S15 (1975 day 082, corrected catalog start `21:10:13`) was selected because later work identifies it and KO-SMQ-40 as a repeating pair. Four PDS products—SHZ and ATT MiniSEED plus both XML labels—were downloaded from the checksum-pinned shallow plan. All four matched their official MD5 values and exact sizes, totaling 7,391,202 bytes.

## Timing and gaps

The nearest valid ATT sample is `21:10:12.710`, 0.290 s before the corrected catalog reference. That ATT sample occurs at nominal MiniSEED time `21:10:17.098717`, a +4.099 s nominal offset relative to the catalog reference. The catalog value is an event start reference, not a published phase pick, so this mapping must not be interpreted as travel time.

The ten-minute audit window has no ATT sentinel. SHZ contains 3,976 `-1` sentinels among 31,802 inspected samples (12.5%). Independent run analysis shows these are isolated one-sample gaps rather than one long outage. They are masked only for plotting and excluded from the simple visibility statistic; they were not interpolated.

## Visibility

The raw waveform shows a clear emergent amplitude increase after the ATT-mapped catalog start, building toward a broad maximum roughly 200–350 s later. Raw RMS after the reference is 3.56 times the pre-reference RMS. This supports waveform usability for the selected event, but it is not a trained detection result or proof that all 74 events are usable.

## Decision

The representative check passes integrity, timing trace, and visual-signal feasibility. The full 0.73 GiB shallow selection may proceed in a later task, followed by automated per-window gap and signal-quality screening. No interpolation or model training is authorized by this result.

Artifacts:

- `data/manifests/ko_smq_26_sample_download.json`
- `results/predictions/ko_smq_26_waveform_audit.json`
- `results/figures/ko_smq_26_raw_shz.png`
- `scripts/download_shallow_sample.py`
- `scripts/audit_shallow_sample.py`
