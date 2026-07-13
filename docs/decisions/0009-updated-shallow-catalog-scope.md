# 0009 — Integrate corrected shallow catalog without promoting headline multiclass claims

Date: 2026-07-13

## Decision

Use the 2026-corrected Onodera tables as a provenance-preserving 74-event shallow-moonquake audit manifest. Retain binary detection as the primary task and shallow classification as descriptive/exploratory. Do not train from this manifest until event-window, ATT timing, gap, and label QA are complete. Group KO-SMQ-26 and KO-SMQ-40 as one repeating-source unit in any split.

## Rationale

All 28 legacy times reconcile exactly with PDS shallow rows, and the 46 KO events are genuinely absent at the same-minute level. All 74 have at least one archived SHZ+ATT station-day. Nevertheless, most new detections are S15-centric, daily-file presence does not establish waveform quality, and 74 events remain too few and too correlated for a robust four-class headline result under station-held-out, event/family-disjoint evaluation.

## Consequences

The updated catalog can guide reproducible waveform QA and sensitivity analysis. It does not change the frozen pilot split rules, permit leakage across the repeating pair, or justify a claim that four-class classification is solved.
