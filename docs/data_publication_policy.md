# NASA/PDS data publication and attribution policy audit

Audit date: 2026-07-13

Status: operational guidance, not legal advice. Recheck before public release because policies can change.

## Authoritative policy findings

NASA's Science Data Portal states that scientific data supplied by a NASA repository fall into three cases: an attached license controls when present; unmarked observations, engineering, calibration, and auxiliary data from NASA-led missions are licensed as CC0; other data are supplied as-is and users should validate source rights. NASA encourages citation regardless of license.

The Apollo PSE waveform bundle is NASA-led mission observational data and no restrictive notice was found in its bundle label, product labels, README, or specification. The operational interpretation is therefore that the waveform data are reusable under CC0. This removes copyright restrictions but does not remove scientific citation duties, provenance requirements, or the need to avoid implying NASA endorsement.

The expanded event catalog is a derived compilation incorporating information from multiple publications. No explicit license field or restrictive notice was found, but the NASA-led-observation CC0 rule does not clearly describe every literature-derived catalog field. Until PDS Geosciences confirms the intended license, LunaSeis-1 will treat bulk republication of the catalog and catalog-derived labeled windows as permission-uncertain.

PDS citation guidance says data citations should let researchers find the precise data used and credit those who prepared, curated, and archived them. Bundle DOI, LIDVID/version, access date, source-product path, and checksums will be preserved.

NASA's media guidance separately protects NASA insignia/logotypes and prohibits implied endorsement. Open data status is not permission to brand LunaSeis-1 as a NASA product.

## What may be published now

| Artifact | GitHub | Hugging Face | Conditions |
|---|---|---|---|
| LunaSeis-1 source code/configuration/tests | Yes | Optional | Use an open-source license selected for Archeum Studios; cite dependencies |
| Download scripts and official URLs | Yes | Yes | Preserve bundle versions and citations |
| Checksums, source paths, schema descriptions, aggregate counts | Yes | Yes | Cite both PDS bundles; avoid copying unnecessary catalog content |
| Independently generated figures and aggregate analyses | Yes | Yes | Cite source bundles; label processing and limitations |
| Model weights created by LunaSeis-1 | Yes | Yes | Model card, training-data provenance, limitations, project license |
| Tiny waveform test fixture from PSE | Technically supported by CC0, but defer | Defer | Add source path/checksum/citation; confirm release packaging first |
| Full raw PSE files | Do not mirror | Do not mirror | Link to PDS and provide downloader; avoid needless duplication |
| Expanded event-catalog CSVs | Do not mirror yet | Do not mirror yet | Obtain written PDS clarification |
| Processed labeled waveform windows | Not yet | Not yet | Requires catalog-license clarification and a documented derivative license |
| NASA logos/insignia | No | No | Separate brand rules; never imply endorsement |

## Required attribution plan

Every data-facing release should cite:

1. Apollo Seismic Data Bundle, `urn:nasa:pds:apollo_pse::1.0`, DOI `10.17189/9ykc-er91`.
2. Apollo Passive Seismic Experiment Expanded Event Catalog, `urn:nasa:pds:apollo_seismic_event_catalog::1.0`, DOI `10.17189/1520573`.
3. Nunn et al. (2022), *A New Archive of Apollo's Lunar Seismic Data*, DOI `10.3847/PSJ/ac87af`, when describing restored waveforms/processing.
4. Relevant original catalog publications for labels used in an analysis.

Add a plain disclaimer: “LunaSeis-1 is an independent Archeum Studios project using public NASA PDS data. It is not affiliated with or endorsed by NASA.”

## Authoritative URLs

- NASA Science Data Licenses: https://science.data.nasa.gov/about/license
- PDS guidance for citing PDS4 data: https://pds.nasa.gov/datastandards/citing/
- NASA Science Information Policy: https://science.nasa.gov/researchers/science-information-policy/
- NASA Images and Media Usage Guidelines: https://www.nasa.gov/nasa-brand-center/images-and-media/
- PSE bundle: https://pds-geosciences.wustl.edu/Lunar/urn-nasa-pds-apollo_pse/
- Event catalog bundle: https://pds-geosciences.wustl.edu/Lunar/urn-nasa-pds-apollo_seismic_event_catalog/

## Required clarification before dataset release

Contact the PDS Geosciences Node and ask whether the expanded event-catalog bundle and labeled derivatives may be redistributed under CC0 or another license, and what attribution they recommend for a Hugging Face dataset. Preserve the written response in project records. Until then, distribute reproducible construction code rather than labeled waveform data.
