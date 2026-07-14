# LunaSeis-1 data and manifest card

## Sources

- NASA PDS Apollo Passive Seismic Experiment bundle: `urn:nasa:pds:apollo_pse::1.0`, DOI `10.17189/9ykc-er91`
- NASA PDS Apollo seismic event catalog: `urn:nasa:pds:apollo_seismic_event_catalog::1.0`, DOI `10.17189/1520573`
- Corrected Onodera shallow-moonquake tables, transcribed with provenance described in the catalog audit

## Contents of this repository

The repository contains code, checksums, source-selection manifests, derived quality summaries, split assignments, predictions, and small model checkpoints. Raw NASA waveform files are excluded from Git.

The unified registry contains 1,314 physical-event candidates: 609 deep moonquakes, 623 natural impacts, 74 shallow moonquakes, and eight artificial impacts. Candidate presence does not imply every observation is waveform-usable.

## Construction safeguards

- Official NASA sizes and MD5 hashes are checked for downloaded products.
- Physical events and identified repeating families remain indivisible within an evaluation fold.
- Held-out-station statistics do not determine normalization.
- Background days are selected independently of event dates where required.
- Catalog-negative means only that no catalog event lies within the exclusion rule; it does not prove physical noise.
- ATT-derived and nominal MiniSEED timing fields remain separate.

## Redistribution

NASA-led observational products without restrictive notices have an operational CC0 reuse basis, but the integrated event catalog includes literature-derived material. LunaSeis-1 therefore does not mirror raw archives or publish a bulk ready-made labeled-window dataset. Users reconstruct inputs from official sources using the included checksum manifests.

Written PDS clarification is still recommended before redistributing catalog-derived labeled waveform collections. The Onodera article material has separate attribution/noncommercial constraints documented in `docs/data_publication_policy.md` and `docs/onodera_2024_catalog_audit.md`.

## Biases and limitations

- Station deployment dates and channel availability are uneven.
- Artifact and quantization patterns are strongly station/year dependent.
- Catalog completeness and timing semantics vary by source.
- Weak events may be indistinguishable from background in a single channel/window.
- Shallow-event additions are concentrated around S15 discovery conditions.

## Citation

Any use must cite the relevant NASA PDS bundles and original catalog literature, not only LunaSeis-1.
