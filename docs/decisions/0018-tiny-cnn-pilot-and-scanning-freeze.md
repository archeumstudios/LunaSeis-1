# Decision 0018: retain the tiny-CNN pilot and freeze continuous-scanning v0.1

Date: 2026-07-14

Retain the 3,057-parameter native-cadence tiny CNN as a pilot model, including the failed 512-bin averaging run as an ablation. The final pilot does not establish H1: it improves over handcrafted logistic regression only at S12, while S14 and S15 are worse in both F1 and false alarms and S16 trades lower F1 for fewer false alarms. Counterfactual inference shows that waveform-zero performance collapses and score-gap correlations remain small, so there is no evidence that the main result is driven only by the validity mask. Strong station dependence remains unresolved.

Freeze continuous-scanning protocol v0.1 before performing a contiguous scan: 600-second windows, 60-second stride, inferred reference at window start plus 120 seconds, validation-only thresholding, 300-second trigger merging, primary ±180-second one-to-one event matching, and ±60/±300-second sensitivity reports. Require a newly selected untouched contiguous-day frame before paper-level evaluation. The current sampled independent windows remain pilot diagnostics.
