# 0005 - Pilot waveform format

Date: 2026-07-13

Status: accepted.

Use MiniSEED waveform products with StationXML metadata and matching PDS4 labels for the Phase 0 pilot. The selected products total 7,924,909 bytes, whereas equivalent GeoCSV waveform tables exceed 250 MB. MiniSEED is the archive's standard compact seismic representation. Preserve ATT and explicit gap masks; do not silently treat nominal MiniSEED sample times as corrected lunar event times.
