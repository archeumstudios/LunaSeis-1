# Data dictionary

## `data/manifests/events_audit.csv`

This is a local analytical index derived from `levent.1008weber.csv`; it is not a final training manifest or a replacement for the official catalog.

| Field | Meaning |
|---|---|
| `source_row` | One-based row number in the source CSV after its header |
| `event_key` | Stable LunaSeis audit identifier derived from source row |
| `catalog_start_minute` | Parsed `Y/JD/S` catalog start minute without a timezone suffix; exact time basis remains under audit |
| `type_code_t2` | PDS-defined current event type code |
| `event_class` | Lossless LunaSeis decoding of T2 |
| `family_id` | Deep-moonquake family `A{N2}` where assigned |
| `grade` | Bulow A/B/C grade or `ungraded` |
| `trace_count_reported` | Catalog's reported number of visible traces, when present |
| `positive_visibility_channels` | Semicolon-separated modern station/channel mapping of positive Bulow flags |
| `positive_visibility_stations` | Stations with at least one positive flag |
| `conservative_pilot_eligible` | `1` only under the documented A/B primary-class visibility rule |

Important: blanks in source visibility fields mean unclear/not positively marked, not confirmed absence. `catalog_start_minute` is not a phase pick.

## `data/manifests/event_label_audit.json`

Contains authoritative code/grade decoding, full and conservative counts, year/station/channel breakdowns, exact duplicate-minute checks, assigned deep-family sizes, and limitations. Counts describe catalog metadata and may shrink after waveform availability and gap validation.
