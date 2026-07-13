# Literature search log

## 2026-07-13 - Initial systematic scoping pass

Purpose: establish prior lunar seismic detection/classification work, archive/canonical catalog work, recent catalog changes, and direct overlap with LunaSeis-1 before freezing novelty or labels.

Sources searched: NASA PDS, NASA NTRS, publisher pages (AGU/Wiley, Oxford Academic, IOP/Planetary Science Journal), institutional repositories, DOI/Crossref-indexed search, and conference repositories for discovery. Peer-reviewed versions were preferred when found.

Search strings:

- `"Apollo seismic" machine learning moonquake detection neural network DOI`
- `"moonquake detection" machine learning Apollo seismic`
- `"lunar seismic" neural network classification Apollo`
- `"Apollo passive seismic" machine learning`
- `"deep moonquake" machine learning`
- `"Apollo seismic" convolutional neural network`
- `"moonquake" Fourier neural operator`
- `"Apollo 16" Hidden Markov event detection classification`
- `"New events discovered" Apollo lunar seismic data`
- `"New archive" Apollo lunar seismic data`
- `"short-period" Apollo new moonquake catalog`
- `"temperature-related long-period" lunar seismic deep learning`
- `seismic detection cross-station generalization false alarms`

Initial records found: 12 directly relevant lunar papers/datasets and several adjacent terrestrial-generalization/false-alarm papers. Ten priority lunar records were extracted into `literature_matrix.csv`; remaining candidates are retained in `screening_log.csv`.

Important search outcome: a 2026 peer-reviewed FNO paper already studies lightweight 1D waveform moonquake detection, cross-domain training, fewer parameters, and fast inference. A 2024 short-period analysis expands known shallow moonquakes from 28 to 74. Both materially weaken assumptions in the original project handoff.

This is an initial scoping pass, not a completed systematic review. Citation chaining, database-specific reproducible result exports, calibration/uncertainty literature, and exhaustive cross-station seismic ML coverage remain required before any “to our knowledge” statement.
