#!/usr/bin/env python3
"""Run the frozen depthwise CNN once on the Grade-C impact challenge."""

from __future__ import annotations
import csv,gzip,hashlib,io,json
from collections import defaultdict
from datetime import datetime,timedelta
from pathlib import Path
import numpy as np
from obspy import UTCDateTime,read
from lunaseis import LunaSeisDetector
from scripts.audit_contiguous_evaluation_data import local_gap_fraction,merged_duration_seconds
from scripts.run_contiguous_scanning_v0_1 import catalog_references,match_triggers,merge_triggers
from scripts.run_tiny_cnn_pilot import predict
from scripts.train_artifact_robust_models import robust_transform

ROOT=Path("data/raw/apollo_pse_v1.0")


def main()->None:
    plan=json.loads(Path("data/manifests/grade_c_challenge_download_plan.json").read_text());days=list(csv.DictReader(Path("data/manifests/grade_c_challenge_day_quality.csv").open(newline="")));groups=defaultdict(list)
    for item in plan["products"]:
        path=Path(item["path"]);groups[(path.parts[-4].upper(),int(path.parts[-3]),int(path.parts[-2]))].append(item)
    detectors={station:LunaSeisDetector(station) for station in ("S12","S14","S15","S16")};predictions=[]
    for number,day in enumerate(days,1):
        station,year,doy=day["station"],int(day["year"]),int(day["doy"]);paths=[ROOT/item["path"] for item in groups[(station,year,doy)] if item["path"].endswith(".mseed")];att=read(str(next(p for p in paths if ".att." in p.name)))[0];wave=read(str(next(p for p in paths if ".att." not in p.name)))[0];start=UTCDateTime(datetime(year,1,1)+timedelta(days=doy-1));samples=[];meta=[]
        for offset in range(0,86400-600+1,60):
            left=start+offset;ag=local_gap_fraction(att,left);wg=local_gap_fraction(wave,left)
            if ag>.2 or wg>.2:continue
            values=np.asarray(wave.slice(left,left+600,nearest_sample=False).data,dtype=float);sample=robust_transform(values,"robust_level")
            if sample is None:continue
            samples.append(sample);meta.append((left,ag,wg))
        scores=predict(detectors[station].model,np.asarray(samples,dtype=np.float32),256)
        for (left,ag,wg),score in zip(meta,scores):predictions.append({"station":station,"block_id":day["block_id"],"year":year,"doy":f"{doy:03d}","window_start":str(left).replace("Z",""),"window_end":str(left+600).replace("Z",""),"inferred_reference_time":str(left+120).replace("Z",""),"att_gap_fraction":ag,"waveform_gap_fraction":wg,"depthwise_cnn_score":float(score)})
        print(f"[{number}/{len(days)}] scored {station} {year}-{doy:03d}: {len(meta)}",flush=True)
    expected=sum(int(r["passing_scan_window_count"]) for r in days)
    if len(predictions)!=expected:raise RuntimeError(f"Expected {expected}, got {len(predictions)}")
    score_path=Path("results/predictions/grade_c_challenge_window_scores.csv.gz")
    with score_path.open("wb") as raw:
        with gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0) as compressed:
            with io.TextIOWrapper(compressed,newline="") as stream:writer=csv.DictWriter(stream,fieldnames=list(predictions[0]),lineterminator="\n");writer.writeheader();writer.writerows(predictions)
    event_quality=list(csv.DictReader(Path("data/manifests/grade_c_challenge_event_quality.csv").open(newline="")));eligible={r["unified_candidate_id"] for r in event_quality if r["event_window_integrity_status"]=="usable_integrity"};context=list(csv.DictReader(Path("data/manifests/grade_c_challenge_catalog_context.csv").open(newline="")));catalogs=catalog_references(context,eligible);triggers=[];retained=0
    for station in detectors:
        threshold=detectors[station].threshold;rows=[r for r in predictions if r["station"]==station];triggers.extend(merge_triggers(rows,"depthwise_cnn",threshold))
        for block in {r["block_id"] for r in rows}:
            chosen=[r for r in rows if r["block_id"]==block];base=min(datetime.fromisoformat(r["window_start"]) for r in chosen);starts=sorted(int((datetime.fromisoformat(r["window_start"])-base).total_seconds()) for r in chosen if r["depthwise_cnn_score"]>=threshold);retained+=merged_duration_seconds(starts)
    hours=sum(int(r["scannable_union_seconds"]) for r in days)/3600;sensitivities={};primary=[]
    for tolerance in (60,180,300):
        annotated,count=match_triggers(triggers,catalogs,tolerance);tp=count["eligible_true_triggers"];fp=count["false_triggers"];recall=tp/len(eligible);precision=tp/max(1,tp+fp);count.update({"eligible_event_recall":recall,"precision_excluding_protected_catalog_triggers":precision,"f1":2*precision*recall/max(1e-12,precision+recall),"false_triggers_per_hour":fp/hours,"false_triggers_per_day":fp/(hours/24)});sensitivities[str(tolerance)]=count
        if tolerance==180:primary=annotated
    trigger_path=Path("results/predictions/grade_c_challenge_triggers.csv")
    with trigger_path.open("w",newline="") as stream:writer=csv.DictWriter(stream,fieldnames=list(primary[0]),lineterminator="\n");writer.writeheader();writer.writerows(primary)
    report={"status":"frozen_grade_c_challenge_consumed_no_retuning","label_scope":"lower_confidence_confirmatory_challenge_not_grade_ab_ground_truth","eligible_event_count":len(eligible),"scannable_union_hours":hours,"parameters":2761,"trigger_count":len(triggers),"retained_fraction_of_scannable_duration":retained/(hours*3600),"matching_sensitivities":sensitivities,"station_thresholds":{s:d.threshold for s,d in detectors.items()},"window_score_sha256":hashlib.sha256(score_path.read_bytes()).hexdigest(),"trigger_csv_sha256":hashlib.sha256(trigger_path.read_bytes()).hexdigest()};Path("results/predictions/grade_c_challenge_results.json").write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report,indent=2))


if __name__=="__main__":main()
