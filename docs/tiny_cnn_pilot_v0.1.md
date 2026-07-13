# Tiny 1D CNN pilot v0.1

Date: 2026-07-14

## Method

The deterministic pilot trains one model per leakage-safe held-out-station fold. Each ten-minute MH window retains its native samples in a 4,096-element tensor; shorter traces are zero-padded and gap sentinels are represented only by a second validity channel. No gap interpolation is used. The waveform is median-centered per window and divided by one scalar standard deviation computed only from the training fold. The model has three convolutions, global mean/max pooling, and 3,057 parameters. Model selection uses validation log loss and decision thresholds use validation F1. Background rows exactly match the deterministic balanced subsets used by the independent-background baselines.

## Pilot results

| Held-out station | Tiny CNN F1 | PR-AUC | FP h⁻¹ | Logistic F1 | Logistic FP h⁻¹ |
|---|---:|---:|---:|---:|---:|
| S12 | 0.874 | 0.943 | 0.462 | 0.795 | 2.123 |
| S14 | 0.714 | 0.563 | 3.154 | 0.766 | 2.954 |
| S15 | 0.632 | 0.686 | 5.731 | 0.651 | 5.274 |
| S16 | 0.663 | 0.685 | 1.553 | 0.754 | 1.805 |

H1 is not supported by this pilot: the CNN does not consistently outperform handcrafted logistic regression across held-out stations. S12 is promising but cannot be generalized. The first 512-bin averaging implementation stayed near random loss and predicted nearly every window positive; it is preserved as a failed ablation because temporal averaging suppressed useful structure.

## Shortcut and efficiency audit

Waveform-zero counterfactual F1 ranges from 0.008 to 0.121, while score-gap correlations range from 0.024 to 0.071. Setting the validity channel to all-valid retains broadly similar behavior, including S12 F1 0.860, so missingness alone does not explain the result. Score–RMS correlation is weak at S12/S15/S16 but 0.500 at S14, requiring later acquisition/amplitude analysis.

Each fold has 3,057 parameters. State checkpoints are about 16 KB and TorchScript exports about 30 KB. Measured single-window CPU latency is approximately 0.20–0.25 ms under this local microbenchmark; it is not a cross-platform deployment claim. Fold training took approximately 4.5–11.4 seconds after waveform tensors were loaded.

## Boundaries

These are balanced-window pilot metrics, not continuous trigger metrics or paper results. No calibration, merged-trigger evaluation, confidence interval, untouched contiguous scan, or retention simulation has been performed. Decision 0018 freezes those scanning rules prospectively and requires a new untouched contiguous-day evaluation frame.
