# Phase 0 source verification

Verified: 2026-07-12 against official NASA PDS/PDS Geosciences Node pages and PDS4 bundle labels.

## Apollo seismic waveform bundle

- Title: Apollo Seismic Data Bundle.
- Logical identifier and version: `urn:nasa:pds:apollo_pse::1.0`.
- DOI: `10.17189/9ykc-er91`.
- Bundle root: `https://pds-geosciences.wustl.edu/Lunar/urn-nasa-pds-apollo_pse/`.
- Collections: `data_seed`, `data_table`, and document collections.
- Representations: MiniSEED with Dataless SEED metadata, and equivalent GeoCSV tables with StationXML metadata.
- Continuous product organization: `data/[network]/continuous_waveform/[station]/[year]/[doy]/`.
- Metadata organization: `data/[network]/metadata/`.
- Network directory visible in the archive: `xa`.
- A continuous product spans one UTC Earth day. The `ATT` timing trace records reception time on Earth, not sampling time, and therefore includes Moon–Earth travel and Earth-rotation effects. Event alignment must account for the archive documentation rather than treating `ATT` naively.
- File naming and location-code rules are documented in the official bundle README. Mid-period `MH1`, `MH2`, and `MHZ` use location `00` for peaked mode and `01` for flat mode; short-period `SHZ` and timing `ATT` have no location code.
- The official PDS instrument context states long-period sampling at 6.6252 Hz and vertical short-period sampling at 15 Hz. These values are verified as instrument-level documentation but must still be checked against each selected product's metadata before processing.

## Expanded event catalog bundle

- Title: Apollo Passive Seismic Experiment Expanded Event Catalog Bundle.
- Logical identifier and version: `urn:nasa:pds:apollo_seismic_event_catalog::1.0`.
- DOI: `10.17189/1520573`.
- Author: Renee C. Weber; publication year 2019 in the PDS citation record.
- Bundle root: `https://pds-geosciences.wustl.edu/Lunar/urn-nasa-pds-apollo_seismic_event_catalog/`.
- Collections: `data` and `document`.
- The data collection consists of CSV tables, each accompanied by a PDS4 XML label. It is an integrated set of multiple source catalogs rather than one already-harmonized training-label table.
- The official PDS record associates the bundle with Apollo 12, 14, 15, and 16 PSE observing systems.
- The directory includes `levent.1008weber.csv` plus source-specific arrival/location tables from Gagnepian, Lognonné, Nakamura, and Weber. Their schemas and semantic relationships require a catalog audit before a label taxonomy or event count is frozen.

## Authoritative sources

- NASA PDS bundle record: `https://pds.nasa.gov/ds-view/pds/viewBundle.jsp?identifier=urn%3Anasa%3Apds%3Aapollo_seismic_event_catalog&version=1.0`
- PDS waveform bundle root and label: `https://pds-geosciences.wustl.edu/Lunar/urn-nasa-pds-apollo_pse/`
- PDS catalog bundle root and label: `https://pds-geosciences.wustl.edu/Lunar/urn-nasa-pds-apollo_seismic_event_catalog/`
- PDS catalog overview: `https://pds-geosciences.wustl.edu/missions/apollo/seismic_event_catalog.htm`
- PDS DOI list: `https://pds-geosciences.wustl.edu/dataserv/doi.htm`
- PDS Apollo holdings overview: `https://pds-geosciences.wustl.edu/missions/apollo/index.htm`

## Still unresolved

- The bundle label and README inspected here do not state a simple software-style license. NASA/PDS redistribution and attribution guidance must be checked explicitly before republishing any data or processed derivatives.
- Product-level station codes, time fields, channel availability, gaps, and actual sample rates remain to be audited from StationXML/PDS labels.
- The event catalog's column semantics, time standards, duplicate relationships, class mappings, uncertainty fields, and recommended primary table remain to be established from its labels and documents.
- No waveform or catalog data product has yet been committed or treated as a training input.
