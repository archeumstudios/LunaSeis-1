# Current status

Last updated: 2026-07-13 (Asia/Kolkata)

## State

Phase 0 feasibility is achieved and Phase 1 has begun. Publication policy, PDS event labels/grades/counts, repeating-family leakage, multiclass feasibility, pilot split design, and the initial structured literature landscape are documented. No models have been trained and no performance results exist.

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
- Verified candidate-day availability for S12 and S14 and enumerated all products and official MD5 values.
- Selected MiniSEED plus StationXML/PDS labels: 7,924,909 bytes (about 7.6 MiB), versus over 250 MB for equivalent GeoCSV waveforms.
- Verified product metadata rates: 6.625 Hz mid-period, 53 Hz SHZ, and 1.65625 Hz ATT; corrected the earlier 15 Hz discovery-stage note.
- Documented ATT reception-time semantics, nominal-time drift, uncorrected 1.2-1.4 s Moon-Earth delay, station synchronization risk, and gap sentinels.
- Added and tested a manifest-driven pilot downloader; all 20 products and 7,924,909 planned bytes passed size and NASA MD5 verification.
- Created a Python 3.12 virtual environment with pinned ObsPy/Matplotlib dependencies; pinned setuptools below 81 for ObsPy compatibility.
- Loaded all nine MiniSEED traces and recorded coverage, sample rates, sample counts, full-day sentinels, and event-window sentinels.
- Matched published arrivals through ATT: nominal mapped time is +0.330 s at S12 and +5.233 s at S14 relative to published arrival.
- Generated and visually verified the first unprocessed LunaSeis-1 waveform plot; a strong event signal is visible at both stations.
- Recorded the Phase 0 feasibility result and the scientific limits of this one-event validation.
- Audited NASA science-data, PDS citation, and NASA brand policies; raw PSE observations are operationally treated as CC0, while bulk event-catalog/labeled-derivative republication is deferred pending written PDS clarification.
- Decoded all PDS `T2` event codes, A/B/C grade meanings, quality codes, and station/channel visibility fields from the official XML label.
- Parsed all 13,057 `levent` rows into a local analytical manifest and produced class/year/station/channel counts.
- Found no exact duplicate catalog start-minute keys; identified 319 assigned deep-family IDs and quantified the largest repeating families.
- Defined a conservative A/B pilot pool: 609 deep events, 623 natural impacts, 18 shallow events, and 8 artificial impacts.
- Rejected broad four-class classification for the initial pilot; retained deep-versus-natural-impact only as exploratory secondary work.
- Designed event-disjoint and deep-family-disjoint leave-one-station-out evaluation with chronological validation and no final-station tuning.
- Completed an initial systematic scoping search and extracted ten priority peer-reviewed records plus four screened/background records.
- Established that 2026 FNO work already overlaps lightweight raw-waveform detection/efficiency and that a 2024 short-period catalog expands shallow events from 28 to 74; candidate novelty and labels were revised accordingly.

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
- `data/manifests/pilot_waveform_inventory.json`
- `docs/waveform_inventory_audit.md`
- `docs/source_verification.md`
- `docs/decisions/0005-pilot-waveform-format.md`
- `scripts/download_pilot_waveforms.py`
- `tests/test_download_pilot_waveforms.py`
- `scripts/audit_pilot_waveforms.py`
- `results/predictions/phase0_waveform_audit.json`
- `results/figures/phase0_apollo15_sivb_raw_waveforms.png`
- `pyproject.toml`
- `requirements-lock.txt`
- `docs/phase0_alignment_result.md`
- `docs/decisions/0006-att-aware-window-timing.md`
- `docs/ROADMAP.md`
- `docs/data_publication_policy.md`
- `scripts/audit_event_labels.py`
- `tests/test_audit_event_labels.py`
- `data/manifests/event_label_audit.json`
- `data/manifests/events_audit.csv`
- `docs/event_label_audit.md`
- `docs/data_dictionary.md`
- `configs/data/pilot.yaml`
- `configs/experiment/leave_one_station_out.yaml`
- `docs/decisions/0007-primary-task-and-multiclass-scope.md`
- `docs/decisions/0008-event-and-family-disjoint-loso.md`
- `literature/search_log.md`
- `literature/screening_log.csv`
- `literature/literature_matrix.csv`
- `literature/state_of_the_field.md`

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
- Inspected official S12/S14 day directories, StationXML, PDS MD5 manifest, and the 41-page 2022 Software Interface Specification.
- Checksum-verified the locally cached StationXML, its PDS label, and the specification PDF.
- Recomputed the planned product total from every listed file size: 7,924,909 bytes.
- Ran five downloader/parser unit tests successfully.
- Reran the pilot downloader after download to verify idempotent integrity checks.
- Ran `scripts/audit_pilot_waveforms.py` with pinned Python dependencies and inspected its JSON output.
- Visually inspected the full-resolution plot for signal visibility, correct channel labeling, markers, gaps, and disclosure of absent preprocessing.
- Queried official NASA Science Data License, PDS citation, NASA science-information, and NASA media/brand guidance.
- Parsed field descriptions directly from the PDS4 `levent.1008weber.xml` label.
- Ran `scripts/audit_event_labels.py` across all 13,057 rows and independently checked headline counts/family sizes.
- Searched NASA/PDS/NTRS, publisher, DOI, and institutional sources with documented queries; extracted the initial literature matrix.
- Added and ran catalog-time conversion tests, including invalid-HHMM rejection.

## Decisions

- The supplied handoff is the canonical stable project context.
- Work begins at Phase 0; modelling remains prohibited until event-to-waveform alignment is verified.
- Treat the PDS event catalog as multiple source tables requiring semantic reconciliation, not an immediately usable flat label file.
- Product metadata, not only instrument-level documentation, will determine actual processing sample rates.
- Use a known artificial impact with two published station arrivals for the first alignment test; this is a feasibility choice, not a final taxonomy choice.
- Use MiniSEED with StationXML and PDS labels for the pilot; include ATT and preserve explicit gaps.
- Treat nominal and ATT-derived timestamps as separate provenance fields; no silent global timing shift.
- Publish code, manifests, aggregate analyses, and models with PDS citations; do not mirror raw archives or catalog-derived labeled datasets before release review/PDS clarification.
- Keep binary detection primary; broad multiclass is unsupported by the initial conservative PDS-only counts.
- Treat physical event and deep-family ID as indivisible split groups, including across stations in LOSO evaluation.

## Unresolved uncertainties

- Exact scalable ATT correction/interpolation policy and catalog-pick time-basis reconciliation remain unresolved.
- The Onodera 2024 updated short-period catalog is not yet integrated with the 2019 PDS catalog; final shallow counts/labels remain open.
- Written PDS clarification is still required before publishing catalog CSVs or catalog-derived labeled windows.
- Source-specific catalog overlap is documented conceptually but full row-level reconciliation remains for the updated event manifest.
- The candidate event's time standard and precise relationship to waveform/timing-trace time remain unresolved.
- Waveform reuse has an operational CC0 basis; catalog and catalog-derived dataset licensing still requires written PDS clarification before republication.
- Full environment portability beyond the tested Apple Silicon Python 3.12 setup remains to be verified later in Colab/Linux.

## Exact next task

Obtain and schema-audit the Onodera 2024 updated Apollo short-period event catalog, verify its license/access path, and reconcile its 74 shallow events against the 28-event PDS table without changing the frozen pilot split rules.
