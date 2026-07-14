#!/usr/bin/env python3
"""Verify manuscript headline evidence and write uncertainty intervals."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from scipy.stats import beta, chi2

ROOT = Path(__file__).resolve().parents[1]


def binomial_exact(successes: int, trials: int, alpha: float = 0.05) -> tuple[float, float]:
    lower = 0.0 if successes == 0 else float(beta.ppf(alpha / 2, successes, trials - successes + 1))
    upper = 1.0 if successes == trials else float(beta.ppf(1 - alpha / 2, successes + 1, trials - successes))
    return lower, upper


def poisson_rate_exact(count: int, exposure_hours: float, alpha: float = 0.05) -> tuple[float, float]:
    lower = 0.0 if count == 0 else float(chi2.ppf(alpha / 2, 2 * count) / (2 * exposure_hours))
    upper = float(chi2.ppf(1 - alpha / 2, 2 * (count + 1)) / (2 * exposure_hours))
    return lower, upper


def main() -> None:
    v1 = json.loads((ROOT / "results/predictions/continuous_scanning_results_v0.1.json").read_text())
    v2 = json.loads((ROOT / "results/predictions/continuous_scanning_results_v0.2.json").read_text())
    v3 = json.loads((ROOT / "results/predictions/grade_c_challenge_results.json").read_text())
    sources = [
        ("v0.1", "tiny_cnn", v1["scannable_union_hours"], v1["eligible_event_count"], v1["models"]["tiny_cnn"]),
        ("v0.2", "artifact_robust_cnn", v2["scannable_union_hours"], v2["eligible_event_count"], v2["models"]["artifact_robust_cnn"]),
        ("v0.3_grade_c", "depthwise_cnn", v3["scannable_union_hours"], v3["eligible_event_count"], v3),
    ]
    table_rows = list(csv.DictReader((ROOT / "paper/tables/continuous_tests.csv").open(newline="")))
    by_key = {(row["frame"], row["method"]): row for row in table_rows}
    interval_rows = []
    for frame, method, hours, eligible, model in sources:
        primary = model["matching_sensitivities"]["180"]
        recalled = int(primary["eligible_true_triggers"])
        false = int(primary["false_triggers"])
        row = by_key[(frame, method)]
        assert int(row["eligible_events"]) == eligible
        assert int(row["recalled_events"]) == recalled
        assert int(row["false_triggers"]) == false
        assert math.isclose(float(row["station_hours"]), hours, rel_tol=0, abs_tol=5e-4)
        assert math.isclose(float(row["false_triggers_per_hour"]), false / hours, rel_tol=0, abs_tol=5e-7)
        recall_low, recall_high = binomial_exact(recalled, eligible)
        rate_low, rate_high = poisson_rate_exact(false, hours)
        interval_rows.append({
            "frame": frame,
            "method": method,
            "recalled_events": recalled,
            "eligible_events": eligible,
            "recall": recalled / eligible,
            "recall_95ci_low": recall_low,
            "recall_95ci_high": recall_high,
            "false_triggers": false,
            "station_hours": hours,
            "false_triggers_per_hour": false / hours,
            "false_trigger_rate_95ci_low": rate_low,
            "false_trigger_rate_95ci_high": rate_high,
        })
    output = ROOT / "paper/tables/statistical_intervals.csv"
    with output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(interval_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(interval_rows)
    summary = {
        "status": "passed",
        "scope": "headline_primary_180_second_continuous_results",
        "intervals": "two-sided 95% Clopper-Pearson recall and exact Poisson false-trigger-rate intervals",
        "verified_frames": len(interval_rows),
        "combined_station_hours": sum(float(item[2]) for item in sources),
        "output": str(output.relative_to(ROOT)),
    }
    (ROOT / "results/predictions/manuscript_evidence_audit.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
