#!/usr/bin/env python3
"""Add every known catalog reference on frozen challenge days before scoring."""

from __future__ import annotations
import csv,hashlib,json
from datetime import datetime
from pathlib import Path


def main()->None:
    days={(r["station"],int(r["year"]),int(r["doy"])) for r in csv.DictReader(Path("data/manifests/grade_c_challenge_station_days.csv").open(newline=""))}
    selected={(r["source_event_id"],r["station"]) for r in csv.DictReader(Path("data/manifests/grade_c_challenge_catalog.csv").open(newline=""))};rows=[]
    for event in csv.DictReader(Path("data/manifests/events_audit.csv").open(newline="")):
        when=datetime.fromisoformat(event["catalog_start_minute"]);doy=int(when.strftime("%j"))
        for station in event["positive_visibility_stations"].split(";"):
            if not station or (station,when.year,doy) not in days:continue
            eligible=(event["event_key"],station) in selected
            rows.append({"station":station,"block_id":event["event_key"] if eligible else f"{station}_{when.year}_{doy:03d}","catalog_source":"PDS_levent","source_event_id":event["event_key"],"reference_time":event["catalog_start_minute"]+":00","unified_candidate_id":event["event_key"],"event_class":event["event_class"],"evaluation_group":"grade_c_"+event["event_key"] if eligible else "protected_"+event["event_key"],"existing_fold_roles":"none" if eligible else "catalog_context_only","prior_pilot_fold_exposed":0 if eligible else 1,"prospective_event_recall_eligibility":"eligible_integrity_audited" if eligible else "catalog_exclusion_only"})
    rows.sort(key=lambda r:(r["station"],r["reference_time"],r["source_event_id"]));path=Path("data/manifests/grade_c_challenge_catalog_context.csv")
    with path.open("w",newline="") as stream:writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator="\n");writer.writeheader();writer.writerows(rows)
    summary={"status":"frozen_catalog_context_before_model_inference","catalog_reference_rows":len(rows),"selected_eligible_rows":sum(r["prospective_event_recall_eligibility"]=="eligible_integrity_audited" for r in rows),"protected_context_rows":sum(r["prospective_event_recall_eligibility"]=="catalog_exclusion_only" for r in rows),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()};Path("results/predictions/grade_c_challenge_catalog_context.json").write_text(json.dumps(summary,indent=2)+"\n");print(json.dumps(summary,indent=2))


if __name__=="__main__":main()
