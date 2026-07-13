# LunaSeis-1 roadmap

The detailed roadmap and constraints are in `PROJECT_CONTEXT.md`, section 26.

## Current phase: Phase 1 — literature and data audit

Success criterion: starting from one verified catalogued event timestamp, automatically identify and obtain its Apollo waveform, load it with correct station/channel metadata, and produce a scientifically valid waveform plot. **Achieved for the Apollo 15 S-IVB pilot on 2026-07-13.**

1. Establish permanent context and repository foundation.
2. Verify official waveform bundle and event catalog identifiers, versions, formats, archive structure, stations, channels, timestamps, sample rates, and redistribution guidance.
3. Implement and test a catalog/metadata downloader.
4. Select one verified event and download the smallest practical corresponding waveform sample. Completed for Apollo 15 S-IVB.
5. Validate metadata, align the event, and plot the waveform window. Completed with explicit nominal/ATT timing and gap audit.
6. Record the feasibility decision before proceeding to Phase 1. Completed in `docs/phase0_alignment_result.md`.

Phase 1 initial scoping completed on 2026-07-13:

- decoded PDS event types, grades, visibility fields, and initial counts;
- audited exact duplicate minutes and repeating deep-family structure;
- froze binary detection as primary and broad multiclass as unsupported for the PDS-only pilot;
- designed event/family-disjoint leave-one-station-out evaluation;
- completed the first systematic literature search pass and revised candidate novelty;
- recorded conservative publication policy pending written PDS clarification for catalog-derived datasets.

Phase 1 remains active for updated-catalog reconciliation, waveform coverage/artifact inventory, exhaustive literature chaining, and final protocol freeze.

Later phases: literature/data audit; reproducible preprocessing; baselines; compact neural models; generalization/calibration; continuous scanning/retention simulation; reproduction audit; paper; public release.
