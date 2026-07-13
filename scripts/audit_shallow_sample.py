#!/usr/bin/env python3
"""Audit timing, gaps, and raw SHZ visibility for one shallow event sample."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from obspy import UTCDateTime, read

try:
    from scripts.audit_pilot_waveforms import att_mapping, trace_audit
except ModuleNotFoundError:  # pragma: no cover
    from audit_pilot_waveforms import att_mapping, trace_audit


def robust_rms(values: np.ndarray) -> float:
    valid = values[values != -1].astype(float)
    if not valid.size:
        return float("nan")
    centered = valid - np.median(valid)
    return float(np.sqrt(np.mean(centered ** 2)))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-id", default="KO-SMQ-26")
    parser.add_argument("--catalog-time", default="1975-03-23T21:10:13Z")
    parser.add_argument("--station", default="S15")
    parser.add_argument("--day-dir", type=Path, default=Path("data/raw/apollo_pse_v1.0/data/xa/continuous_waveform/s15/1975/082"))
    parser.add_argument("--audit-output", type=Path, default=Path("results/predictions/ko_smq_26_waveform_audit.json"))
    parser.add_argument("--plot-output", type=Path, default=Path("results/figures/ko_smq_26_raw_shz.png"))
    args = parser.parse_args()

    target = UTCDateTime(args.catalog_time)
    att = read(str(next(args.day_dir.glob("*att*.mseed"))))[0]
    shz = read(str(next(args.day_dir.glob("*shz*.mseed"))))[0]
    mapping = att_mapping(att, target)
    mapped_nominal = UTCDateTime(mapping["nominal_time_at_nearest_att"])
    pre = shz.slice(mapped_nominal - 120, mapped_nominal - 20, nearest_sample=False)
    post = shz.slice(mapped_nominal, mapped_nominal + 480, nearest_sample=False)
    pre_rms, post_rms = robust_rms(pre.data), robust_rms(post.data)

    report = {
        "event_id": args.event_id,
        "station": args.station,
        "catalog_start_time": str(target),
        "time_interpretation": "Onodera corrected start time; treated as event reference, not a published phase pick",
        "processing": "none; raw SHZ counts; -1 gap sentinel excluded only from metrics/display",
        "att_mapping": mapping,
        "traces": {
            "ATT": trace_audit(att, mapped_nominal - 120, mapped_nominal + 480),
            "SHZ": trace_audit(shz, mapped_nominal - 120, mapped_nominal + 480),
        },
        "visibility_check": {
            "pre_reference_rms": pre_rms,
            "post_reference_rms": post_rms,
            "post_to_pre_rms_ratio": post_rms / pre_rms if pre_rms else None,
            "interpretation": "A ratio above one is supporting evidence only; visual morphology and broader QA remain required.",
        },
    }
    args.audit_output.parent.mkdir(parents=True, exist_ok=True)
    args.audit_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    sliced = shz.slice(mapped_nominal - 120, mapped_nominal + 480, nearest_sample=False)
    values = sliced.data.astype(float)
    values[values == -1] = np.nan
    seconds = np.arange(values.size) / sliced.stats.sampling_rate - 120
    fig, axis = plt.subplots(figsize=(12, 4.5))
    axis.plot(seconds, values, color="#17324d", linewidth=0.55, rasterized=True)
    axis.axvline(0, color="#d1495b", linestyle="--", label="ATT-mapped catalog start")
    axis.set(title=f"{args.event_id} at {args.station}: raw Apollo SHZ", xlabel="Nominal seconds from ATT-mapped catalog start", ylabel="Raw counts")
    axis.grid(axis="x", color="#d8dee6", linewidth=0.5)
    axis.spines[["top", "right"]].set_visible(False)
    axis.legend(frameon=False)
    fig.text(0.5, 0.01, "No filtering, detrending, normalization, interpolation, or response removal.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    args.plot_output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.plot_output, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(json.dumps(report["visibility_check"], indent=2))


if __name__ == "__main__":
    main()
