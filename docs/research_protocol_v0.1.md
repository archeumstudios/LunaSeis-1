# Research protocol v0.1

Status: provisional and preregistration-like; freeze only after the literature and Phase 1 data audits.

## Objective

Evaluate whether lightweight 1D models operating on Apollo PSE waveforms can detect catalogued lunar seismic events with low false-alarm rates and retain useful performance at stations excluded entirely from training. Secondary work may classify broad event groups. Operational retention is explicitly a simulation, not a spacecraft bandwidth claim.

## Phase 0 gate

No model training is allowed until one authoritative catalogued event can be mapped automatically to its source waveform, loaded with verified station/channel/timing metadata, and plotted correctly.

## Data and labels

Use official NASA PDS sources, whose identifiers and versions must be verified before encoding them as facts. Initial stations are Apollo 12, 14, 15, and 16 PSE, subject to audit. Apollo 17 LSPE is excluded from the primary benchmark. Non-event samples are called `catalog-negative background`; their physical noisiness is not assumed.

## Leakage controls

Split before augmentation. Prevent overlap, same-event leakage, augmented-copy leakage, repeating-family leakage where identifiers permit grouping, held-out-station normalization leakage, unjustified chronological-neighbour splitting, and duplicate catalog records. Preserve sample-level provenance.

## Evaluation

- Chronological within-station evaluation.
- Leave-one-station-out folds supported by audited coverage.
- Long continuous scanning with predeclared window, stride, trigger merging, matching tolerance, and false positives per unit time.
- Detection: precision, recall, F1, PR-AUC, event recall, false positives/hour or day, and latency where applicable.
- Classification if supported: macro-F1, balanced accuracy, per-class metrics, confusion matrix, counts, and practical bootstrap intervals.
- Calibration: Brier score, ECE, reliability and risk-coverage analyses; temperature scaling first.
- Efficiency under fixed conditions: parameters, serialized size, CPU latency, peak memory, and throughput.

## Initial comparisons

Energy/amplitude threshold, STA/LTA, logistic regression on documented handcrafted features, optionally random forest, tiny residual 1D CNN, depthwise-separable 1D CNN, and small TCN. Advanced models require a scientific reason after the pipeline is stable.

## Reporting safeguards

Do not claim novelty, state of the art, unknown-event discovery, deployment/flight readiness, or real bandwidth savings without appropriate evidence. Unexpectedly strong results trigger explicit leakage, duplicate, metadata, artifact, timing, family, and label-correlation audits. Preserve negative results and exact configurations.

For full hypotheses, risks, metrics, retention simulation definitions, and stop conditions, see `PROJECT_CONTEXT.md`.
