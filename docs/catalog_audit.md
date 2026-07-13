# Apollo expanded event catalog: initial audit

Audit date: 2026-07-13

Source: NASA PDS bundle `urn:nasa:pds:apollo_seismic_event_catalog::1.0`, DOI `10.17189/1520573`.

## Download integrity and storage

- NASA's MD5 manifest lists 32 products (bundle label, CSV/XML data products, documents, and README).
- All 32 products passed MD5 verification.
- Verified product bytes: 2,226,558 (2.2 MB on disk, excluding negligible filesystem variation and the downloaded manifest itself).
- Raw products are stored locally under ignored `data/raw/apollo_seismic_event_catalog_v1.0/` and are not committed.

## Catalog structure

The official description states that this is an integrated catalog of 11 CSV files based on the Nakamura catalog plus literature-derived subsets. It is not one normalized event table.

| File | Rows | Role |
|---|---:|---|
| `levent.1008weber.csv` | 13,057 | Weber-edited main event catalog; original fields plus grade/trace-quality fields |
| `gagnepian_2006_catalog.csv` | 58 | Events used by Gagnepain-Beyneix et al. (2006) |
| `lognonne_2003_catalog.csv` | 59 | Events used by Lognonné et al. (2003) |
| `nakamura_1979_sm_locations.csv` | 28 | Shallow-moonquake locations |
| `nakamura_1983_ai_arrivals.csv` | 8 | Artificial-impact arrivals |
| `nakamura_1983_ai_locations.csv` | 8 | Artificial-impact origin/location records |
| `nakamura_1983_m_arrivals.csv` | 65 | Meteorite-impact arrivals; continuation rows represent additional stations |
| `nakamura_1983_sm_arrivals.csv` | 44 | Shallow-moonquake arrivals; continuation rows represent additional stations |
| `nakamura_2005_dm_arrivals.csv` | 166 | Deep-moonquake cluster arrivals |
| `nakamura_2005_dm_locations.csv` | 106 | Deep-moonquake cluster locations |
| `weber_2011_dmq_s_picks.csv` | 38 | Selected deep-moonquake stack S picks |

The generated `data/manifests/catalog_schema_audit.json` records each table's column names, row count, non-empty counts, and unique non-empty counts.

## Time formats verified from the official description

- `levent.1008weber`: `YY JJJ HHmm`
- Gagnepian and Lognonné catalogs: `YYMMDDHHmm`
- Nakamura 1979 shallow locations: `YYYY JJJ HH mm`
- Nakamura 1983 artificial-impact locations: `YY JJJ HH mm`, with seconds in a separate field
- Nakamura 1983 meteorite/shallow arrivals: `YYYY JJJ HHmm`

Times are preserved as published. This audit does not yet assert a time standard beyond the field formats; UTC interpretation must be confirmed against waveform/archive documentation.

## Phase 0 pilot-event candidate

Selected candidate: Apollo 15 S-IVB artificial impact.

- Catalog origin fields: year `71`, Julian day `210`, `20:58:42.9`.
- Provisional calendar conversion: 1971-07-29 20:58:42.9 (time standard still to be explicitly reconciled).
- Published P arrival fields: station 12 at `20:59:37.9`; station 14 at `20:59:19.5`.
- The exact known impact and independently tabulated arrivals make this a stronger Phase 0 alignment target than an uncertain natural event.
- This is only a pipeline-validation event. Choosing an artificial impact for Phase 0 does not decide the later training taxonomy or benchmark composition.

## Important cautions

- `levent` event classes and grade codes still require formal decoding from the PDS label/source documentation before aggregate counts are reported.
- Arrival and origin tables describe different scientific quantities and must not be concatenated as equivalent rows.
- Some event-cluster naming changed historically: the catalog description warns that A24 was later reclassified as A10.
- Published location uncertainties may be underestimated, according to the catalog description.
- The origin-time/waveform time relationship must account for the Apollo archive's timing-trace documentation.
