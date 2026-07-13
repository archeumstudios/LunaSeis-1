#!/usr/bin/env python3
"""Decode and audit the Weber/Nakamura event catalog for pilot design."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

TYPE_MAP = {
    "A": "deep_moonquake_assigned",
    "M": "deep_moonquake_unclassified",
    "C": "natural_impact",
    "H": "shallow_moonquake",
    "L": "artificial_impact_lm",
    "S": "artificial_impact_sivb",
    "T": "suspected_thermal_long_period",
    "Z": "mostly_short_period",
    "X": "special",
    "": "unclassified_blank",
}

CHANNEL_COLUMNS = {
    "12LPX": ("S12", "MH1"), "12LPY": ("S12", "MH2"), "12LPZ": ("S12", "MHZ"),
    "14SPZ": ("S14", "SHZ"), "14LPX": ("S14", "MH1"), "14LPY": ("S14", "MH2"),
    "14LPZ": ("S14", "MHZ"), "15SPZ": ("S15", "SHZ"), "15LPX": ("S15", "MH1"),
    "15LPY": ("S15", "MH2"), "15LPZ": ("S15", "MHZ"), "16SPZ": ("S16", "SHZ"),
    "16LPX": ("S16", "MH1"), "16LPY": ("S16", "MH2"), "16LPZ": ("S16", "MHZ"),
}

PRIMARY_CLASSES = {
    "deep_moonquake_assigned", "deep_moonquake_unclassified", "natural_impact",
    "shallow_moonquake", "artificial_impact_lm", "artificial_impact_sivb",
}


def event_time(row: dict[str, str]) -> datetime:
    year = 1900 + int(row["Y"])
    day = int(row["JD"])
    hhmm = int(row["S"])
    hour, minute = divmod(hhmm, 100)
    if hour > 23 or minute > 59:
        raise ValueError(f"Invalid HHMM {row['S']} for {row['Y']}-{row['JD']}")
    return datetime(year, 1, 1) + timedelta(
        days=day - 1, hours=hour, minutes=minute
    )


def nested_counts(counter: Counter[tuple[str, str]]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = defaultdict(dict)
    for (left, right), count in sorted(counter.items()):
        result[left][right] = count
    return dict(result)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--catalog", type=Path,
        default=Path("data/raw/apollo_seismic_event_catalog_v1.0/data/levent.1008weber.csv"),
    )
    parser.add_argument(
        "--summary", type=Path, default=Path("data/manifests/event_label_audit.json")
    )
    parser.add_argument(
        "--events", type=Path, default=Path("data/manifests/events_audit.csv")
    )
    args = parser.parse_args()

    with args.catalog.open(encoding="utf-8-sig", newline="") as stream:
        source_rows = list(csv.DictReader(stream))

    decoded = []
    class_counts = Counter()
    grade_counts = Counter()
    year_class_counts = Counter()
    usable_class_counts = Counter()
    usable_station_class = Counter()
    usable_channel_class = Counter()
    timestamps = Counter()
    family_sizes = Counter()

    for index, row in enumerate(source_rows, start=1):
        timestamp = event_time(row)
        code = (row["T2"] or "").strip()
        event_class = TYPE_MAP[code]
        grade = (row["Grade"] or "").strip() or "ungraded"
        visible = [column for column in CHANNEL_COLUMNS if (row[column] or "").strip() == "1"]
        stations = sorted({CHANNEL_COLUMNS[column][0] for column in visible})
        channels = sorted({f"{station}.{channel}" for column in visible for station, channel in [CHANNEL_COLUMNS[column]]})
        family = ""
        if code == "A" and (row["N2"] or "").strip():
            family = f"A{int(row['N2'])}"
            family_sizes[family] += 1
        usable = grade in {"A", "B"} and event_class in PRIMARY_CLASSES and bool(visible)

        class_counts[event_class] += 1
        grade_counts[grade] += 1
        year_class_counts[(str(timestamp.year), event_class)] += 1
        timestamps[timestamp.isoformat()] += 1
        if usable:
            usable_class_counts[event_class] += 1
            for station in stations:
                usable_station_class[(station, event_class)] += 1
            for channel in channels:
                usable_channel_class[(channel, event_class)] += 1

        decoded.append({
            "source_row": index,
            "event_key": f"levent-{index:05d}",
            "catalog_start_minute": timestamp.isoformat(timespec="minutes"),
            "type_code_t2": code,
            "event_class": event_class,
            "family_id": family,
            "grade": grade,
            "trace_count_reported": (row["Traces"] or "").strip(),
            "positive_visibility_channels": ";".join(channels),
            "positive_visibility_stations": ";".join(stations),
            "conservative_pilot_eligible": "1" if usable else "0",
        })

    duplicate_timestamps = {key: value for key, value in timestamps.items() if value > 1}
    family_distribution = Counter(family_sizes.values())
    assigned_events = sum(family_sizes.values())
    summary = {
        "source_bundle": "urn:nasa:pds:apollo_seismic_event_catalog::1.0",
        "source_file": args.catalog.name,
        "total_rows": len(source_rows),
        "type_code_mapping": TYPE_MAP,
        "grade_definition": {
            "A": "high SNR, generally impulsive onset; phases may be visible",
            "B": "lower SNR and more gradual emergence; distinct envelope",
            "C": "inferior SNR, often dominated by one-digital-unit fluctuations",
            "ungraded": "no Bulow grade; not equivalent to false event",
        },
        "all_event_counts_by_class": dict(sorted(class_counts.items())),
        "all_grade_counts": dict(sorted(grade_counts.items())),
        "counts_by_year_and_class": nested_counts(year_class_counts),
        "conservative_pilot_rule": (
            "valid catalog time AND T2 in primary physical classes AND grade A/B AND at least one "
            "positive Bulow channel-visibility flag"
        ),
        "conservative_pilot_counts_by_class": dict(sorted(usable_class_counts.items())),
        "conservative_pilot_counts_by_station_and_class": nested_counts(usable_station_class),
        "conservative_pilot_counts_by_channel_and_class": nested_counts(usable_channel_class),
        "exact_duplicate_catalog_start_minutes": duplicate_timestamps,
        "deep_assigned_family_audit": {
            "assigned_events": assigned_events,
            "unique_family_ids": len(family_sizes),
            "largest_families": dict(family_sizes.most_common(20)),
            "family_size_distribution": {str(size): count for size, count in sorted(family_distribution.items())},
            "split_requirement": "all events from one family_id must remain in one split",
        },
        "limitations": [
            "Catalog start time is minute-resolution and is not necessarily a phase arrival.",
            "Blank visibility means unclear/not positively marked, not confirmed absence.",
            "A/B-only eligibility is a conservative pilot definition, not a final scientific exclusion.",
            "Source-specific arrival/location tables intentionally overlap with levent and are not extra independent events.",
        ],
    }

    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    args.events.parent.mkdir(parents=True, exist_ok=True)
    with args.events.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(decoded[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(decoded)
    print(f"decoded {len(decoded)} events")
    print("pilot counts", dict(usable_class_counts))
    print(f"deep assigned families {len(family_sizes)}; exact duplicate minutes {len(duplicate_timestamps)}")
    print(f"wrote {args.summary} and {args.events}")


if __name__ == "__main__":
    main()
