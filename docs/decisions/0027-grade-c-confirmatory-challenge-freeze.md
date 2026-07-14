# Decision 0027: freeze the event-rich Grade-C impact challenge

Date: 2026-07-14

Freeze 64 model-unseen Grade-C natural-impact station-day observations—16 per Apollo station—as a lower-confidence confirmatory challenge. These represent 63 unique physical events because `levent-08466` was independently selected at S12 and S14. Selection uses a fixed SHA-256 rank, requires positive catalog MH visibility, excludes all 3,426 station-days exposed by prior manifests, and occurs before waveform inspection or model scoring. All 64 selected days have ATT plus the reported primary MH channel; the checksum-backed plan contains 256 products totaling 97,596,992 bytes.

Pre-inference integrity auditing retained all 64 event-station observations and yielded 1,505.35 scannable station-hours. The complete catalog context contains 102 additional known-event references that are protected from false-trigger counting. No model was loaded during these audits.

The already selected 2,761-parameter depthwise model and its four validation thresholds are frozen for this challenge. Missing products or integrity failures will not be replaced. Because Grade C is weaker evidence than the prior Grade-A/B pool, these results must remain a separate sensitivity/confirmation analysis and cannot by themselves establish an operational detector.
