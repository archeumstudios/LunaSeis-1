#!/usr/bin/env python3
"""Audit ATT timing and raw positive-channel integrity for one nonshallow batch."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from obspy import UTCDateTime, read

try:
    from scripts.audit_pilot_waveforms import att_mapping
    from scripts.audit_shallow_windows import gap_statistics, integrity_status, robust_rms
    from scripts.build_nonshallow_download_plan import product_names
except ModuleNotFoundError:  # pragma: no cover
    from audit_pilot_waveforms import att_mapping
    from audit_shallow_windows import gap_statistics, integrity_status, robust_rms
    from build_nonshallow_download_plan import product_names


def load_days(root: Path, station: str, days: list[str], channel: str):
    stream = None
    for value in days:
        year, doy = (int(item) for item in value.split("-"))
        name = product_names(station, year, doy, channel)[0]
        path = root / station.lower() / str(year) / f"{doy:03d}" / name
        current = read(str(path))
        stream = current if stream is None else stream + current
    stream.sort()
    stream.merge(method=0, fill_value=-1)
    if len(stream) != 1:
        raise RuntimeError(f"Could not merge {station} {channel} {days}: {len(stream)} traces")
    return stream[0]


def complete_channels_in_batch(request: dict[str, str], product_batch: dict[str, int], batch_id: int) -> list[str]:
    days = request["required_station_days"].split(";")
    complete = []
    for channel in filter(None, request["complete_positive_channels"].split(";")):
        paths = []
        for value in days:
            year, doy = (int(item) for item in value.split("-"))
            for selected in ("ATT", channel):
                for name in product_names(request["station"], year, doy, selected):
                    paths.append(f"data/xa/continuous_waveform/{request['station'].lower()}/{year}/{doy:03d}/{name}")
        if paths and all(product_batch.get(path) == batch_id for path in paths):
            complete.append(channel)
    return complete


def edge_fraction(values: np.ndarray) -> float | None:
    valid = np.asarray(values)[np.asarray(values) != -1]
    if not valid.size:
        return None
    if valid.min() == valid.max():
        return 1.0
    return float((np.count_nonzero(valid == valid.min()) + np.count_nonzero(valid == valid.max())) / valid.size)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-id", type=int, required=True)
    parser.add_argument("--plan", type=Path, default=Path("data/manifests/nonshallow_download_plan.json"))
    parser.add_argument("--requests", type=Path, default=Path("data/manifests/nonshallow_waveform_requests.csv"))
    parser.add_argument("--day-root", type=Path, default=Path("data/raw/apollo_pse_v1.0/data/xa/continuous_waveform"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/manifests"))
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    args = parser.parse_args()

    plan = json.loads(args.plan.read_text())
    product_batch = {item["path"]: int(item["batch_id"]) for item in plan["products"]}
    with args.requests.open(encoding="utf-8", newline="") as stream:
        requests = list(csv.DictReader(stream))

    channel_rows = []
    request_rows = []
    covered = []
    for request in requests:
        channels = complete_channels_in_batch(request, product_batch, args.batch_id)
        if channels:
            covered.append((request, channels))
    for number, (request, channels) in enumerate(covered, start=1):
        days = request["required_station_days"].split(";")
        target = UTCDateTime(request["reference_time"] + "Z")
        att = load_days(args.day_root, request["station"], days, "ATT")
        mapping = att_mapping(att, target)
        mapped = UTCDateTime(mapping["nominal_time_at_nearest_att"])
        statuses = []
        usable_channels = []
        questionable_channels = []
        rejected_channels = []
        for channel in channels:
            trace = load_days(args.day_root, request["station"], days, channel)
            window = trace.slice(mapped - 120, mapped + 480, nearest_sample=False).data
            before = trace.slice(mapped - 120, mapped - 20, nearest_sample=False).data
            after = trace.slice(mapped, mapped + 480, nearest_sample=False).data
            gaps = gap_statistics(window)
            status = integrity_status(float(gaps["gap_fraction"]), float(mapping["att_minus_target_seconds"]))
            statuses.append(status)
            destination = usable_channels if status == "usable_integrity" else questionable_channels if status == "questionable_integrity" else rejected_channels
            destination.append(channel)
            pre_rms, post_rms = robust_rms(before), robust_rms(after)
            ratio = post_rms / pre_rms if pre_rms and post_rms is not None else None
            valid = np.asarray(window)[np.asarray(window) != -1]
            channel_rows.append({
                "batch_id": args.batch_id, "event_id": request["event_id"], "event_class": request["event_class"],
                "station": request["station"], "channel": channel, "reference_time": request["reference_time"],
                "nearest_att_minus_reference_seconds": mapping["att_minus_target_seconds"],
                "nominal_minus_reference_seconds": mapping["nominal_minus_target_seconds"],
                "att_minus_nominal_seconds": mapping["att_minus_nominal_seconds"],
                "sample_rate_hz": float(trace.stats.sampling_rate), **gaps,
                "longest_gap_seconds": gaps["longest_gap_samples"] / float(trace.stats.sampling_rate),
                "raw_min": float(valid.min()) if valid.size else "", "raw_max": float(valid.max()) if valid.size else "",
                "edge_value_fraction_descriptive": edge_fraction(window),
                "pre_reference_rms": pre_rms, "post_reference_rms": post_rms, "post_to_pre_rms_ratio": ratio,
                "integrity_status": status,
            })
        request_status = "usable_integrity" if usable_channels else "questionable_integrity" if questionable_channels else "reject_integrity"
        request_rows.append({
            "batch_id": args.batch_id, "event_id": request["event_id"], "event_class": request["event_class"],
            "station": request["station"], "audited_positive_channels": ";".join(channels),
            "usable_channels": ";".join(usable_channels), "questionable_channels": ";".join(questionable_channels),
            "rejected_channels": ";".join(rejected_channels), "request_integrity_status": request_status,
        })
        print(f"[{number}/{len(covered)}] {request['event_id']} {request['station']} {request_status}", flush=True)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    channel_path = args.output_dir / f"nonshallow_batch_{args.batch_id}_window_quality.csv"
    request_path = args.output_dir / f"nonshallow_batch_{args.batch_id}_request_quality.csv"
    for path, rows in ((channel_path, channel_rows), (request_path, request_rows)):
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader(); writer.writerows(rows)

    event_rows = defaultdict(list)
    for row in request_rows: event_rows[row["event_id"]].append(row)
    event_status = {
        event: "usable_integrity" if any(row["request_integrity_status"] == "usable_integrity" for row in rows)
        else "questionable_integrity" if any(row["request_integrity_status"] == "questionable_integrity" for row in rows)
        else "reject_integrity"
        for event, rows in event_rows.items()
    }
    summary = {
        "batch_id": args.batch_id, "covered_events": len(event_rows), "covered_event_station_requests": len(request_rows),
        "audited_channel_windows": len(channel_rows),
        "channel_integrity_counts": dict(Counter(row["integrity_status"] for row in channel_rows)),
        "request_integrity_counts": dict(Counter(row["request_integrity_status"] for row in request_rows)),
        "event_integrity_counts": dict(Counter(event_status.values())),
        "class_counts_for_covered_events": dict(Counter(next(row["event_class"] for row in request_rows if row["event_id"] == event) for event in event_rows)),
        "warning": "Integrity uses gaps and ATT proximity only. RMS and edge-value fractions are descriptive and never alter labels.",
    }
    prediction_dir = args.results_dir / "predictions"; prediction_dir.mkdir(parents=True, exist_ok=True)
    (prediction_dir / f"nonshallow_batch_{args.batch_id}_quality_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    gaps = [float(row["gap_fraction"]) for row in channel_rows]
    ratios = [float(row["post_to_pre_rms_ratio"]) for row in channel_rows if row["post_to_pre_rms_ratio"] not in (None, "")]
    edges = [float(row["edge_value_fraction_descriptive"]) for row in channel_rows if row["edge_value_fraction_descriptive"] not in (None, "")]
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
    axes[0].hist(gaps, bins=25, color="#315b7d"); axes[0].axvline(0.2, color="#d1495b", linestyle="--"); axes[0].set_xlabel("Gap fraction")
    axes[1].hist(np.clip(ratios, 0, 10), bins=25, color="#587b55"); axes[1].set_xlabel("Post/pre RMS ratio (clipped at 10)")
    axes[2].hist(edges, bins=25, color="#7a5c8e"); axes[2].set_xlabel("Min/max occupancy (descriptive)")
    for axis in axes: axis.set_ylabel("Channel windows"); axis.spines[["top", "right"]].set_visible(False)
    fig.suptitle(f"Nonshallow Batch {args.batch_id}: raw positive-channel QA")
    fig.tight_layout(); figure_dir = args.results_dir / "figures"; figure_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure_dir / f"nonshallow_batch_{args.batch_id}_quality_overview.png", dpi=180); plt.close(fig)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
