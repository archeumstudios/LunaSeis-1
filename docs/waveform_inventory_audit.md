# Phase 0 pilot waveform inventory audit

Audit date: 2026-07-13

Source bundle: `urn:nasa:pds:apollo_pse::1.0`, DOI `10.17189/9ykc-er91`.

Target: Apollo 15 S-IVB artificial impact, Earth day 1971-210 (1971-07-29), with published P arrivals at stations 12 and 14.

## Availability

Both `s12/1971/210` and `s14/1971/210` exist in the official `XA` continuous-waveform archive.

| Station | Available MiniSEED channels | Location | MiniSEED + PDS labels |
|---|---|---|---:|
| S12 | ATT, MH1, MH2, MHZ | ATT blank; mid-period `00` peaked mode | 1,077,350 bytes |
| S14 | ATT, SHZ, MH1, MH2, MHZ | ATT/SHZ blank; mid-period `00` peaked mode | 6,657,111 bytes |
| Shared metadata | StationXML and its PDS label | network XA | 190,448 bytes |
| **Planned total** | 9 waveform files, 9 PDS labels, StationXML + label | | **7,924,909 bytes (about 7.6 MiB)** |

The equivalent GeoCSV waveform files exceed 250 MB. MiniSEED is therefore the storage-efficient scientific representation for the pilot, with StationXML and PDS labels retained for metadata and provenance.

## Verified channel metadata at the event date

StationXML reports:

- `MH1`, `MH2`, `MHZ`: 6.625 Hz.
- `SHZ`: 53.0 Hz.
- `ATT`: 1.65625 Hz.
- Stations S12 and S14 were active at the candidate time.

Station 12's archive directory has no SHZ product for this day. This absence must be recorded, not imputed.

## Timing interpretation from the official specification

- Waveform sample times use nominal sampling intervals.
- `ATT` records the timestamp at the head of each transmitted frame and represents reception time on Earth.
- Nominal sample time can diverge from the original timestamp by a few seconds over 24 hours.
- The archive does not correct the 1.2-1.4 second Moon-to-Earth transmission delay.
- Station recording timestamps may occasionally be out of synchronization; archive producers corrected identifiable errors where possible.
- Day files are divided by Earth day, and samples can slightly overrun midnight because of timestamp divergence.
- Gap sentinels are `-1` on seismic channels and `-1.0` on ATT. They must be masked, never treated as physical samples.

Consequently, the first plot must show catalog origin, published station arrival, nominal MiniSEED time, and ATT-derived timing separately. We must not silently shift the signal to make the catalog pick look correct.

## Integrity plan

NASA's bundle MD5 manifest contains entries for all selected products. Their expected checksums are stored in `data/manifests/pilot_waveform_inventory.json`. The downloader must verify every selected file before use.

## Archive-scale context

The official 2022 specification reports approximately 53 GB of MiniSEED in the complete archive. LunaSeis-1 will not download the full bundle during Phase 0. The pilot remains below 8 MB plus already-downloaded documentation.
