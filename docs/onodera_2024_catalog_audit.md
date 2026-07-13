# Onodera shallow-moonquake catalog audit

Audit date: 2026-07-13

## Authority and access

The authoritative work is Onodera (2024), *New Views of Lunar Seismicity Brought by Analysis of Newly Discovered Moonquakes in Apollo Short-Period Seismic Data*, DOI `10.1029/2023JE008153` (preprint DOI `10.22541/essoar.169841663.38914436/v1`). Its embedded event tables are under the article's CC BY-NC terms. No separately deposited machine-readable catalog with its own DOI, license, schema, or checksum was located. Consequently, LunaSeis treats the corrected article tables as the catalog source and records its own transcription checksum; this is not represented as an official author-produced data file.

The publisher issued a correction on 2026-02-09 for transcription errors in Tables 1 and A1. The local manifest uses only those corrected tables. The correction says the scientific conclusions are unaffected.

## Reconciliation result

`data/manifests/onodera_2024_shallow_events.csv` contains 74 events:

- 28 `YN-SMQ` legacy events. Every corrected year/day/start minute has exactly one `H` row in PDS `levent.1008weber.csv`.
- 46 `KO-SMQ` events newly reported by Onodera. None shares its start minute with any row in that PDS table.

The manifest preserves event ID, provenance group, year, day of year, corrected UTC clock as reported, reported/detection stations, PDS match fields, and reconciliation status. For legacy events, all S14/S15/S16 station-days are audited because the PDS visibility flags are incomplete: four legacy events have no positive SP flag. `positive_pds_sp_stations` preserves the flags separately rather than silently treating blank fields as absence.

Integrity and counts are recorded in `data/manifests/onodera_2024_reconciliation.json`. The generated event CSV SHA-256 is `4fc3cbc7a9ecb93fef5901525fa984bdc7987888122e9e92332fdd2ba11a7153`.

## Scientific scope decision

The update improves shallow-event coverage from the conservative 18 A/B PDS pilot events to 74 reported shallow events, but it does not make shallow classification a defensible headline task. The 46 additions are detected mainly at S15, labels originate from a targeted discovery analysis, and waveform availability is not equivalent to independent confirmation or gap-free event windows. Shallow classification remains descriptive/exploratory until event-window QA, timing reconciliation, uncertainty handling, and grouped evaluation are complete. KO-SMQ-26 and KO-SMQ-40 must be kept together because later work identifies them as a repeating pair.

## Reproduction

Run:

```bash
.venv/bin/python scripts/reconcile_shallow_catalog.py
```

This requires the locally checksum-verified PDS event catalog. Public redistribution of this derived CSV must retain article attribution, comply with CC BY-NC, and pass the repository's release/licensing review.
