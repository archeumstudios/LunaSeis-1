#!/usr/bin/env python3
"""Audit score timing and margins around every integrity-eligible continuous-test event."""

from __future__ import annotations

import csv,gzip,json
from datetime import datetime
from pathlib import Path


def load_scores(path: Path) -> list[dict[str,str]]:
    with gzip.open(path,"rt",newline="") as stream:return list(csv.DictReader(stream))


def audit(version: str, models: dict[str,str]) -> list[dict]:
    suffix="" if version=="v0.1" else "_v0.2"
    quality=Path(f"data/manifests/contiguous_evaluation_eligible_event_quality{suffix}.csv")
    scores=load_scores(Path(f"results/predictions/continuous_scanning_window_scores_{version}.csv.gz"))
    thresholds=json.loads(Path(f"results/predictions/continuous_scanning_thresholds_{version}.json").read_text())["folds"]
    output=[]
    for event in csv.DictReader(quality.open(newline="")):
        if event["event_window_integrity_status"]!="usable_integrity":continue
        reference=datetime.fromisoformat(event["reference_time"]);near=[]
        for row in scores:
            if row["station"]!=event["station"]:continue
            delta=(datetime.fromisoformat(row["inferred_reference_time"])-reference).total_seconds()
            if abs(delta)<=7200:near.append((delta,row))
        result={"version":version,"candidate_id":event["unified_candidate_id"],"station":event["station"],"event_class":event["event_class"],"reference_time":event["reference_time"],"signal_support":event["signal_support_descriptive"],"post_to_pre_rms_ratio":event["post_to_pre_rms_ratio"]}
        for model,column in models.items():
            threshold_entry=thresholds[f"holdout_{event['station']}"][model]
            threshold=float(threshold_entry["primary"] if isinstance(threshold_entry,dict) else threshold_entry)
            closest=min(near,key=lambda item:abs(item[0]));peak=max(near,key=lambda item:float(item[1][column]))
            result[f"{model}_threshold"]=threshold;result[f"{model}_closest_score"]=float(closest[1][column]);result[f"{model}_closest_delta_seconds"]=closest[0];result[f"{model}_peak_score_2h"]=float(peak[1][column]);result[f"{model}_peak_delta_seconds_2h"]=peak[0];result[f"{model}_triggered_within_2h"]=int(float(peak[1][column])>=threshold)
        output.append(result)
    return output


def main() -> None:
    rows=audit("v0.1",{"tiny_cnn":"tiny_cnn_score","logistic_handcrafted":"logistic_handcrafted_score","sta_lta":"sta_lta_score"})
    rows+=audit("v0.2",{"artifact_robust_cnn":"artifact_robust_cnn_score","original_tiny_cnn":"original_tiny_cnn_score","logistic_handcrafted":"logistic_handcrafted_score","sta_lta":"sta_lta_score"})
    path=Path("results/predictions/missed_continuous_event_audit.json");path.write_text(json.dumps({"status":"post_test_diagnostic_no_retuning","event_count":len(rows),"events":rows,"warning":"The ±2-hour search is diagnostic after test consumption and cannot change matching metrics or thresholds."},indent=2)+"\n");print(json.dumps(rows,indent=2))


if __name__=="__main__":main()
