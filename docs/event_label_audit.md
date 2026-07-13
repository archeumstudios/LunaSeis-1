# Event labels, grades, counts, and leakage audit

Audit date: 2026-07-13

Source: `levent.1008weber.csv` in `urn:nasa:pds:apollo_seismic_event_catalog::1.0`.

## Authoritative decoding

The PDS4 product label defines `T2` as the current event type:

| Code | Meaning | LunaSeis working class |
|---|---|---|
| A | Deep moonquake with assigned cluster number | `deep_moonquake_assigned` |
| M | Unclassified deep moonquake | `deep_moonquake_unclassified` |
| C | Meteoroid impact | `natural_impact` |
| H | Shallow moonquake | `shallow_moonquake` |
| L | Lunar-module impact | `artificial_impact_lm` |
| S | S-IVB impact | `artificial_impact_sivb` |
| T | Suspected long-period thermal event with assigned number | `suspected_thermal_long_period` |
| Z | Mostly short-period event | `mostly_short_period` |
| X | Special type | `special` |
| blank | No T2 classification | `unclassified_blank` |

The label defines Bulow grades as: A = high SNR and generally impulsive; B = lower SNR/more gradual but distinct envelope; C = inferior SNR and often one-bit dominated. Ungraded does not mean false.

Station-specific `Q1`-`Q4` quality codes mean: 1 no data; 2 noisy; 3 masked by a larger event; 4 compressed plot clipped (digital data may not be); 5 consult comments; 6 computer-generated/inexact recorded time. These flags are exclusion/quality metadata, not event classes.

## Full catalog counts

| Class | Events |
|---|---:|
| Assigned deep moonquake | 7,082 |
| Unclassified deep moonquake | 317 |
| Natural impact | 1,743 |
| Shallow moonquake | 28 |
| Artificial LM impact | 4 |
| Artificial S-IVB impact | 5 |
| Suspected thermal long-period | 266 |
| Mostly short-period | 255 |
| Special | 34 |
| Blank T2 classification | 3,323 |

Grades: A 263; B 1,018; C 7,123; ungraded 4,653.

## Conservative pilot eligibility

The pilot rule is deliberately strict: valid catalog minute, a primary physical T2 class, grade A or B, and at least one positive Bulow channel-visibility flag. Blank visibility means unclear, not confirmed absence.

| Class | Eligible independent events |
|---|---:|
| Assigned deep moonquake | 604 |
| Unclassified deep moonquake | 5 |
| Natural impact | 623 |
| Shallow moonquake | 18 |
| Artificial LM impact | 4 |
| Artificial S-IVB impact | 4 |

These are event counts, not station-window counts. One event visible at several stations must remain one sampling/splitting unit.

## Station support among eligible events

| Station | Assigned deep | Unclassified deep | Natural impact | Shallow | LM | S-IVB |
|---|---:|---:|---:|---:|---:|---:|
| S12 | 405 | 2 | 367 | 14 | 3 | 4 |
| S14 | 509 | 3 | 455 | 17 | 4 | 3 |
| S15 | 348 | 1 | 337 | 16 | 3 | 2 |
| S16 | 364 | 3 | 256 | 13 | 1 | 1 |

Machine-readable channel/year breakdowns are in `data/manifests/event_label_audit.json`.

## Duplicate and repeating-family findings

- No two `levent` rows share the same exact year/day/start-minute key.
- Source-specific location/arrival tables overlap intentionally with `levent`; they are metadata/picks for some of the same physical events, not extra independent events.
- The 7,082 assigned deep events span 319 catalog family IDs. The largest groups are A1 (443), A8 (327), A10 (230), A18 (214), and A6 (178).
- Similar waveforms within a deep-moonquake family create a severe shortcut risk. All events from one family must remain in one split.
- The catalog documentation notes that historical A24 events were reclassified as A10. Normalization must preserve that relationship.

## Multiclass feasibility decision

A broad deep/shallow/natural/artificial four-class headline experiment is not supported by the conservative counts. Shallow (18) and artificial impacts (8 combined) are too sparse for a reliable station-held-out neural classifier, especially after grouping and chronological constraints.

Primary research remains binary event detection. An exploratory secondary classifier may compare deep moonquakes against natural impacts because both have roughly 600 eligible events, but only with event-disjoint, family-grouped, station-held-out evaluation. Shallow and artificial impacts remain descriptive case studies or an explicit `other/abstain` evaluation set; they must not be oversampled into apparent adequacy.

## Important limitations

- Catalog `S` is a minute-resolution signal-start guide, not a precise phase arrival.
- Visibility flags are positive evidence only; blanks are ambiguous.
- This audit counts catalog metadata, not successfully extracted waveform windows. Product availability/gap checks may reduce counts.
- Grade A/B is a conservative pilot choice, not a permanent definition of scientific validity.
