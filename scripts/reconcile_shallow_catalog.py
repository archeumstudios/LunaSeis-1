#!/usr/bin/env python3
"""Reconcile corrected Onodera shallow events with the PDS levent catalog."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

YN_EVENTS = """
YN-SMQ-1 1971 107 07:04
YN-SMQ-2 1971 140 17:29
YN-SMQ-3 1971 192 13:27
YN-SMQ-4 1972 002 22:32
YN-SMQ-5 1972 261 14:38
YN-SMQ-6 1972 341 23:10
YN-SMQ-7 1972 344 03:52
YN-SMQ-8 1973 039 22:53
YN-SMQ-9 1973 072 08:01
YN-SMQ-10 1973 171 20:25
YN-SMQ-11 1973 274 04:00
YN-SMQ-12 1974 054 21:17
YN-SMQ-13 1974 086 09:11
YN-SMQ-14 1974 109 13:39
YN-SMQ-15 1974 149 20:45
YN-SMQ-16 1974 192 00:52
YN-SMQ-17 1975 003 01:47
YN-SMQ-18 1975 012 03:17
YN-SMQ-19 1975 013 00:28
YN-SMQ-20 1975 044 22:05
YN-SMQ-21 1975 127 06:40
YN-SMQ-22 1975 147 23:32
YN-SMQ-23 1975 314 07:56
YN-SMQ-24 1976 004 11:20
YN-SMQ-25 1976 012 08:22
YN-SMQ-26 1976 066 10:16
YN-SMQ-27 1976 068 14:44
YN-SMQ-28 1976 137 12:36
"""

KO_EVENTS = """
KO-SMQ-1 1971 334 01:07:57 S15
KO-SMQ-2 1972 005 22:42:33 S14;S15
KO-SMQ-3 1972 154 16:49:07 S15;S14
KO-SMQ-4 1972 170 19:34:31 S14;S15;S16
KO-SMQ-5 1972 176 12:27:49 S15
KO-SMQ-6 1972 255 00:54:27 S14;S15;S16
KO-SMQ-7 1972 298 14:25:25 S14
KO-SMQ-8 1973 129 11:02:13 S15
KO-SMQ-9 1973 168 12:59:43 S15
KO-SMQ-10 1973 226 19:10:25 S15
KO-SMQ-11 1973 236 04:07:35 S15
KO-SMQ-12 1973 257 04:31:37 S15
KO-SMQ-13 1973 287 23:07:04 S15
KO-SMQ-14 1973 294 20:23:02 S15
KO-SMQ-15 1973 307 17:37:13 S15
KO-SMQ-16 1973 346 08:39:31 S15
KO-SMQ-17 1973 360 07:37:04 S15
KO-SMQ-18 1973 363 08:50:41 S15
KO-SMQ-19 1974 172 19:17:30 S15
KO-SMQ-20 1974 187 18:44:53 S14
KO-SMQ-21 1974 242 10:47:49 S15
KO-SMQ-22 1974 245 17:59:37 S15
KO-SMQ-23 1974 338 03:43:17 S15
KO-SMQ-24 1975 029 09:57:38 S15
KO-SMQ-25 1975 078 03:05:53 S15
KO-SMQ-26 1975 082 21:10:13 S15
KO-SMQ-27 1975 093 05:21:57 S15
KO-SMQ-28 1975 304 04:03:28 S15
KO-SMQ-29 1975 325 16:10:49 S15
KO-SMQ-30 1976 002 12:28:19 S15
KO-SMQ-31 1976 018 13:20:35 S15
KO-SMQ-32 1976 044 20:44:14 S15
KO-SMQ-33 1976 060 21:09:51 S15
KO-SMQ-34 1976 093 09:39:05 S15
KO-SMQ-35 1976 175 19:26:18 S15
KO-SMQ-36 1976 206 17:24:10 S15
KO-SMQ-37 1976 220 00:18:59 S15
KO-SMQ-38 1976 220 15:19:07 S15
KO-SMQ-39 1976 269 22:22:25 S15
KO-SMQ-40 1976 337 12:45:41 S15
KO-SMQ-41 1977 008 16:20:31 S15
KO-SMQ-42 1977 050 10:21:24 S15
KO-SMQ-43 1977 169 15:37:25 S15
KO-SMQ-44 1977 179 02:13:40 S15
KO-SMQ-45 1977 183 02:01:29 S15
KO-SMQ-46 1977 207 18:19:45 S15
"""

SP_COLUMNS = {
    "14SPZ": "S14", "15SPZ": "S15", "16SPZ": "S16",
}


def calendar_time(year: int, doy: int, clock: str) -> datetime:
    parts = [int(value) for value in clock.split(":")]
    hour, minute = parts[:2]
    second = parts[2] if len(parts) == 3 else 0
    return datetime(year, 1, 1) + timedelta(
        days=doy - 1, hours=hour, minutes=minute, seconds=second
    )


def pds_time(row: dict[str, str]) -> datetime:
    hhmm = int(row["S"])
    return calendar_time(1900 + int(row["Y"]), int(row["JD"]), f"{hhmm // 100:02d}:{hhmm % 100:02d}")


def parse_lines(text: str) -> list[list[str]]:
    return [line.split() for line in text.strip().splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pds-catalog", type=Path,
        default=Path("data/raw/apollo_seismic_event_catalog_v1.0/data/levent.1008weber.csv"),
    )
    parser.add_argument(
        "--events-output", type=Path,
        default=Path("data/manifests/onodera_2024_shallow_events.csv"),
    )
    parser.add_argument(
        "--summary-output", type=Path,
        default=Path("data/manifests/onodera_2024_reconciliation.json"),
    )
    args = parser.parse_args()

    with args.pds_catalog.open(encoding="utf-8-sig", newline="") as stream:
        pds_rows = list(csv.DictReader(stream))
    pds_by_minute: dict[datetime, list[tuple[int, dict[str, str]]]] = {}
    for number, row in enumerate(pds_rows, start=1):
        pds_by_minute.setdefault(pds_time(row), []).append((number, row))

    records: list[dict[str, str]] = []
    for event_id, year_text, doy_text, clock in parse_lines(YN_EVENTS):
        year, doy = int(year_text), int(doy_text)
        timestamp = calendar_time(year, doy, clock)
        matches = pds_by_minute.get(timestamp, [])
        shallow = [(number, row) for number, row in matches if row["T2"].strip() == "H"]
        if len(shallow) != 1:
            raise RuntimeError(f"Expected one PDS H match for {event_id}, found {len(shallow)}")
        number, row = shallow[0]
        stations = sorted({station for column, station in SP_COLUMNS.items() if row[column].strip() == "1"})
        station_basis = "positive_pds_sp_visibility"
        if not stations:
            stations = ["S14", "S15", "S16"]
            station_basis = "fallback_all_onodera_sp_stations_no_positive_pds_sp_flag"
        records.append({
            "event_id": event_id, "source_group": "legacy_yn", "year": str(year),
            "doy": f"{doy:03d}", "start_time_utc": clock + ":00" if len(clock) == 5 else clock,
            "reported_stations": "S14;S15;S16",
            "station_basis": "all_onodera_sp_stations_for_legacy_coverage_audit",
            "positive_pds_sp_stations": ";".join(stations) if not station_basis.startswith("fallback") else "",
            "pds_match_event_key": f"levent-{number:05d}", "pds_match_type_code": "H",
            "reconciliation_status": "exact_year_doy_start_minute_match",
        })

    ko_minute_overlap = Counter()
    for event_id, year_text, doy_text, clock, station_text in parse_lines(KO_EVENTS):
        year, doy = int(year_text), int(doy_text)
        timestamp = calendar_time(year, doy, clock)
        matches = pds_by_minute.get(timestamp.replace(second=0), [])
        match_keys = ";".join(f"levent-{number:05d}" for number, _ in matches)
        match_types = ";".join((row["T2"] or "blank").strip() or "blank" for _, row in matches)
        status = "new_no_pds_same_start_minute" if not matches else "new_same_minute_as_existing_pds_row"
        ko_minute_overlap[status] += 1
        records.append({
            "event_id": event_id, "source_group": "new_ko", "year": str(year),
            "doy": f"{doy:03d}", "start_time_utc": clock,
            "reported_stations": station_text, "station_basis": "corrected_onodera_table_a1_station_field",
            "positive_pds_sp_stations": "",
            "pds_match_event_key": match_keys, "pds_match_type_code": match_types,
            "reconciliation_status": status,
        })

    args.events_output.parent.mkdir(parents=True, exist_ok=True)
    with args.events_output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)

    content_sha256 = hashlib.sha256(args.events_output.read_bytes()).hexdigest()
    no_positive_pds_sp = [
        row["event_id"] for row in records
        if row["source_group"] == "legacy_yn" and not row["positive_pds_sp_stations"]
    ]
    summary = {
        "article_doi": "10.1029/2023JE008153",
        "preprint_doi": "10.22541/essoar.169841663.38914436/v1",
        "correction_publication_date": "2026-02-09",
        "license": "CC BY-NC (article and embedded tables)",
        "schema": list(records[0]),
        "total_events": len(records),
        "legacy_yn_events": sum(row["source_group"] == "legacy_yn" for row in records),
        "new_ko_events": sum(row["source_group"] == "new_ko" for row in records),
        "legacy_exact_pds_matches": sum(row["reconciliation_status"].startswith("exact") for row in records),
        "new_event_pds_minute_overlap": dict(ko_minute_overlap),
        "legacy_events_without_positive_pds_sp_flag": no_positive_pds_sp,
        "events_csv_sha256": content_sha256,
        "integrity_note": (
            "Times and KO station fields transcribed from the corrected 2026 Tables 1/2; "
            "legacy times independently match PDS H rows exactly at minute resolution."
        ),
    }
    args.summary_output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
