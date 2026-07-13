# Current status

Last updated: 2026-07-13 (Asia/Kolkata)

## State

Phase 0 catalog acquisition and structural audit are complete. One artificial-impact event is selected as the candidate for the first waveform alignment. No waveform data have been downloaded, no models trained, and no scientific results produced.

## Completed

- Inspected the initial workspace: it was empty and was not a Git repository.
- Preserved the complete supplied handoff in `docs/PROJECT_CONTEXT.md`.
- Created the permanent context document set and repository directory skeleton.
- Initialized Git and created commit `2683cd8` (`chore: initialize LunaSeis-1 research repository`).
- Verified waveform bundle `urn:nasa:pds:apollo_pse::1.0`, DOI `10.17189/9ykc-er91`.
- Verified event catalog bundle `urn:nasa:pds:apollo_seismic_event_catalog::1.0`, DOI `10.17189/1520573`.
- Recorded formats, archive layout, timing warning, documented instrument sample rates, and remaining uncertainties in `docs/source_verification.md`.
- Confirmed 47 GiB free before downloading; the catalog required only 2.2 MB.
- Added a manifest-driven catalog downloader and verified all 32 NASA-listed products (2,226,558 bytes) by MD5.
- Audited 11 catalog CSV schemas and generated a machine-readable schema report.
- Inspected the official four-page catalog-description PDF by text extraction and rendered-page review.
- Selected the Apollo 15 S-IVB artificial impact (1971, Julian day 210) as the Phase 0 pilot candidate, with published P arrivals at stations 12 and 14.

## Files changed

- Initial context/skeleton files in commit `2683cd8`.
- `docs/source_verification.md`
- `docs/CURRENT_STATUS.md`
- `scripts/download_catalog.py`
- `scripts/audit_catalog.py`
- `tests/test_download_catalog.py`
- `data/manifests/catalog_schema_audit.json`
- `data/manifests/pilot_event.json`
- `docs/catalog_audit.md`
- `docs/DECISIONS.md`
- `docs/decisions/0004-phase-0-pilot-event.md`

## Commands and verification

- Inspected with `ls -la`, `find`, `rg --files`, and `git status`.
- Compared the permanent context against the supplied handoff byte-for-byte before commit.
- Reviewed repository status and required files before commit.
- Queried official NASA PDS pages and inspected both official PDS4 bundle XML labels and READMEs.
- Inspected the official catalog and waveform collection directory listings without downloading the archive.
- Ran `python3 scripts/download_catalog.py`; all 32 product checksums passed.
- Ran `python3 -m unittest discover -s tests -p 'test_download_catalog.py' -v`; 2 tests passed.
- Ran `python3 scripts/audit_catalog.py`; audited 11 CSV files and wrote the schema manifest.
- Converted Julian day 210 of 1971 independently to 1971-07-29 for the candidate record.

## Decisions

- The supplied handoff is the canonical stable project context.
- Work begins at Phase 0; modelling remains prohibited until event-to-waveform alignment is verified.
- Treat the PDS event catalog as multiple source tables requiring semantic reconciliation, not an immediately usable flat label file.
- Product metadata, not only instrument-level documentation, will determine actual processing sample rates.
- Use a known artificial impact with two published station arrivals for the first alignment test; this is a feasibility choice, not a final taxonomy choice.

## Unresolved uncertainties

- Product-level station/channel metadata, timing semantics, availability, gaps, and sample rates remain to be audited.
- Full `levent` class/grade decoding, duplicate reconciliation, and final label mappings remain to be audited.
- The candidate event's time standard and precise relationship to waveform/timing-trace time remain unresolved.
- Redistribution/licensing guidance remains unresolved; no republication is authorized by assumption.
- The local Python/dependency environment has not yet been audited.

## Exact next task

Inspect the Apollo PSE inventory and StationXML for 1971 Julian day 210, calculate the exact size of only the station 12 and 14 candidate-day products, and document the correct channels/timing interpretation before downloading waveform samples.
