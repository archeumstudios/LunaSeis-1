#!/usr/bin/env python3
"""Create ATT/gap/raw-signal QA records for all complete shallow event windows."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from obspy import UTCDateTime, read

try:
    from scripts.audit_pilot_waveforms import att_mapping
except ModuleNotFoundError:  # pragma: no cover
    from audit_pilot_waveforms import att_mapping


def event_time(year: int, doy: int, clock: str) -> UTCDateTime:
    parts = [int(item) for item in clock.split(":")]
    base = datetime(year, 1, 1, tzinfo=timezone.utc) + timedelta(days=doy - 1)
    return UTCDateTime(base.replace(hour=parts[0], minute=parts[1], second=parts[2]))


def gap_statistics(values: np.ndarray, sentinel: float = -1) -> dict[str, float | int]:
    missing = np.asarray(values) == sentinel
    edges = np.diff(np.r_[False, missing, False].astype(np.int8))
    runs = np.flatnonzero(edges == -1) - np.flatnonzero(edges == 1)
    return {
        "sample_count": int(missing.size),
        "gap_sample_count": int(missing.sum()),
        "gap_fraction": float(missing.mean()) if missing.size else 1.0,
        "gap_run_count": int(runs.size),
        "longest_gap_samples": int(runs.max()) if runs.size else 0,
    }


def robust_rms(values: np.ndarray) -> float | None:
    valid = np.asarray(values)[np.asarray(values) != -1].astype(float)
    if not valid.size:
        return None
    valid -= np.median(valid)
    return float(np.sqrt(np.mean(valid ** 2)))


def integrity_status(gap_fraction: float, nearest_att_offset_seconds: float) -> str:
    offset = abs(nearest_att_offset_seconds)
    if gap_fraction > 0.5 or offset > 10:
        return "reject_integrity"
    if gap_fraction > 0.2 or offset > 1:
        return "questionable_integrity"
    return "usable_integrity"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, default=Path("data/manifests/onodera_2024_shallow_events.csv"))
    parser.add_argument("--coverage", type=Path, default=Path("data/manifests/onodera_2024_shallow_coverage.csv"))
    parser.add_argument("--day-root", type=Path, default=Path("data/raw/apollo_pse_v1.0/data/xa/continuous_waveform"))
    parser.add_argument("--output", type=Path, default=Path("data/manifests/shallow_window_quality.csv"))
    parser.add_argument("--summary", type=Path, default=Path("results/predictions/shallow_window_quality_summary.json"))
    parser.add_argument("--figure", type=Path, default=Path("results/figures/shallow_window_quality_overview.png"))
    args = parser.parse_args()

    with args.events.open(encoding="utf-8", newline="") as stream:
        events = {row["event_id"]: row for row in csv.DictReader(stream)}
    with args.coverage.open(encoding="utf-8", newline="") as stream:
        coverage = [row for row in csv.DictReader(stream) if row["all_data_and_labels_available"] == "1"]

    records = []
    for number, item in enumerate(coverage, start=1):
        event = events[item["event_id"]]
        station, year, doy = item["station"], int(item["year"]), int(item["doy"])
        directory = args.day_root / station.lower() / str(year) / f"{doy:03d}"
        att = read(str(next(directory.glob("*att*.mseed"))))[0]
        shz = read(str(next(directory.glob("*shz*.mseed"))))[0]
        target = event_time(year, doy, event["start_time_utc"])
        mapping = att_mapping(att, target)
        mapped = UTCDateTime(mapping["nominal_time_at_nearest_att"])
        window = shz.slice(mapped - 120, mapped + 480, nearest_sample=False).data
        before = shz.slice(mapped - 120, mapped - 20, nearest_sample=False).data
        after = shz.slice(mapped, mapped + 480, nearest_sample=False).data
        att_window = att.slice(mapped - 120, mapped + 480, nearest_sample=False).data
        gaps = gap_statistics(window)
        att_gaps = int(np.count_nonzero(att_window == -1.0))
        pre_rms, post_rms = robust_rms(before), robust_rms(after)
        ratio = post_rms / pre_rms if pre_rms and post_rms is not None else None
        signal_support = "not_quantifiable" if ratio is None else ("strong_ratio" if ratio >= 2 else "weak_ratio" if ratio >= 1.2 else "no_clear_ratio")
        records.append({
            "event_id": item["event_id"], "source_group": event["source_group"], "station": station,
            "catalog_reference_time": str(target), "nearest_att_minus_reference_seconds": mapping["att_minus_target_seconds"],
            "nominal_minus_reference_seconds": mapping["nominal_minus_target_seconds"],
            "att_minus_nominal_seconds": mapping["att_minus_nominal_seconds"],
            "shz_sample_rate_hz": float(shz.stats.sampling_rate), **gaps,
            "longest_gap_seconds": gaps["longest_gap_samples"] / float(shz.stats.sampling_rate),
            "att_gap_sample_count": att_gaps, "pre_reference_rms": pre_rms, "post_reference_rms": post_rms,
            "post_to_pre_rms_ratio": ratio, "signal_support": signal_support,
            "integrity_status": integrity_status(float(gaps["gap_fraction"]), float(mapping["att_minus_target_seconds"])),
        })
        print(f"[{number}/{len(coverage)}] {item['event_id']} {station}", flush=True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(records)
    integrity = Counter(row["integrity_status"] for row in records)
    signals = Counter(row["signal_support"] for row in records)
    event_status = {}
    for event_id in events:
        rows = [row for row in records if row["event_id"] == event_id]
        event_status[event_id] = "usable" if any(row["integrity_status"] == "usable_integrity" for row in rows) else "questionable" if any(row["integrity_status"] == "questionable_integrity" for row in rows) else "rejected"
    summary = {
        "event_station_windows": len(records), "events": len(events),
        "integrity_status_counts": dict(integrity), "signal_support_counts": dict(signals),
        "event_level_integrity_counts": dict(Counter(event_status.values())),
        "thresholds": {
            "usable_max_gap_fraction": 0.2, "questionable_max_gap_fraction": 0.5,
            "usable_max_nearest_att_offset_seconds": 1.0, "questionable_max_nearest_att_offset_seconds": 10.0,
            "att_gap_policy": "report ATT gaps; judge timing integrity by distance to nearest valid ATT sample",
        },
        "scientific_warning": "Signal ratio is descriptive and never changes the physical label or integrity status.",
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    ratios = [row["post_to_pre_rms_ratio"] for row in records if row["post_to_pre_rms_ratio"] is not None]
    gap_fractions = [row["gap_fraction"] for row in records]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    axes[0].hist(gap_fractions, bins=20, color="#315b7d"); axes[0].axvline(0.2, color="#d1495b", linestyle="--")
    axes[0].set(xlabel="SHZ gap fraction in 10-minute window", ylabel="Event-station windows")
    axes[1].hist(np.clip(ratios, 0, 10), bins=20, color="#587b55"); axes[1].axvline(2, color="#d1495b", linestyle="--")
    axes[1].set(xlabel="Post/pre raw RMS ratio (clipped at 10)", ylabel="Event-station windows")
    for axis in axes: axis.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Corrected shallow catalog: raw window QA overview")
    fig.tight_layout(); args.figure.parent.mkdir(parents=True, exist_ok=True); fig.savefig(args.figure, dpi=180); plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
