#!/usr/bin/env python3
"""Run frozen continuous-scanning v0.1 without tuning on the scan frame."""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from obspy import UTCDateTime, read

try:
    from scripts.audit_contiguous_evaluation_data import local_gap_fraction, merged_duration_seconds
    from scripts.run_pilot_baselines import features, logistic_fit
    from scripts.run_tiny_cnn_pilot import TinyCNN, build_role, deterministic_negative_rows, fixed_length, predict
except ModuleNotFoundError:  # pragma: no cover
    from audit_contiguous_evaluation_data import local_gap_fraction, merged_duration_seconds
    from run_pilot_baselines import features, logistic_fit
    from run_tiny_cnn_pilot import TinyCNN, build_role, deterministic_negative_rows, fixed_length, predict

ROOT=Path("data/raw/apollo_pse_v1.0")
MODELS=("tiny_cnn","logistic_handcrafted","sta_lta")


def recall_threshold(scores: np.ndarray, labels: np.ndarray, target: float = .9) -> float:
    choices=np.unique(scores);valid=[]
    positives=labels==1
    for threshold in choices:
        recall=float(np.mean(scores[positives]>=threshold))
        if recall>=target:valid.append(float(threshold))
    if not valid:raise ValueError("No threshold satisfies validation recall target")
    return max(valid)


def best_f1_threshold(scores: np.ndarray, labels: np.ndarray) -> float:
    best=(-1.,float(np.min(scores)))
    for threshold in np.unique(scores):
        predicted=scores>=threshold;tp=np.sum(predicted&(labels==1));fp=np.sum(predicted&(labels==0));fn=np.sum(~predicted&(labels==1));f1=2*tp/max(1,2*tp+fp+fn)
        if f1>best[0]:best=(float(f1),float(threshold))
    return best[1]


def feature_vector(values: np.ndarray, sample_rate: float) -> np.ndarray | None:
    values=np.asarray(values,dtype=float).copy();missing=values==-1
    if not values.size or np.mean(missing)>.2 or np.all(missing):return None
    valid=values[~missing];values[missing]=np.median(valid);values-=np.median(valid)
    rms=float(np.sqrt(np.mean(values*values)))+1e-12;absolute=np.abs(values)
    short=max(1,round(5*sample_rate));long=max(short+1,round(60*sample_rate));energy=values*values;cs=np.concatenate([[0.],np.cumsum(energy)])
    sta=(cs[short:]-cs[:-short])/short;lta=(cs[long:]-cs[:-long])/long;aligned=sta[long-short:long-short+len(lta)];ratio=float(np.max(aligned/(lta+1e-12))) if len(lta) else 0.
    return np.array([np.log(rms),np.log(float(absolute.max())+1e-12),np.log(float(np.mean(np.abs(np.diff(values))))+1e-12),float(np.mean(np.signbit(values[1:])!=np.signbit(values[:-1]))),ratio])


def reconstruct_fold(fold: str, positives, backgrounds) -> tuple[dict, TinyCNN, float, np.ndarray, np.ndarray, np.ndarray]:
    role_data={};wave_data={}
    for role in ("train","validation"):
        pos=[row for row in positives if row["fold"]==fold and row["role"]==role]
        neg=deterministic_negative_rows([row for row in backgrounds if row["fold"]==fold and row["role"]==role],len(pos))
        vectors=[];labels=[]
        for label,rows,key in ((1,pos,"window_start_nominal"),(0,neg,"start_time")):
            for row in rows:
                vector=features(row["station"],row["channel"],datetime.fromisoformat(row[key]))
                if vector is not None:vectors.append(vector);labels.append(label)
        role_data[role]=(np.asarray(vectors),np.asarray(labels))
        wave_data[role]=build_role(pos,neg)[:2]
    train_x,train_y=role_data["train"];val_x,val_y=role_data["validation"]
    mean=train_x.mean(axis=0);std=train_x.std(axis=0);std[std==0]=1
    weights=logistic_fit(np.column_stack([np.ones(len(train_x)),(train_x-mean)/std]),train_y)
    val_logistic=1/(1+np.exp(-np.clip(np.column_stack([np.ones(len(val_x)),(val_x-mean)/std])@weights,-30,30)))
    checkpoint=torch.load(f"models/checkpoints/tiny_cnn_pilot_v0.1/{fold}.pt",weights_only=True);model=TinyCNN();model.load_state_dict(checkpoint["state_dict"]);scale=float(checkpoint["waveform_training_std"])
    val_wave,val_wave_y=wave_data["validation"];val_wave=val_wave.copy();val_wave[:,0]/=scale;val_cnn=predict(model,val_wave)
    if not np.array_equal(val_y,val_wave_y):raise RuntimeError(f"Validation label order mismatch in {fold}")
    thresholds={"tiny_cnn":{"primary":recall_threshold(val_cnn,val_y),"max_f1_sensitivity":best_f1_threshold(val_cnn,val_y)},"logistic_handcrafted":{"primary":recall_threshold(val_logistic,val_y),"max_f1_sensitivity":best_f1_threshold(val_logistic,val_y)},"sta_lta":{"primary":recall_threshold(val_x[:,4],val_y),"max_f1_sensitivity":best_f1_threshold(val_x[:,4],val_y)},"validation_counts":{"event":int(np.sum(val_y==1)),"background":int(np.sum(val_y==0))}}
    return thresholds,model,scale,mean,std,weights


def merge_triggers(windows: list[dict], model: str, threshold: float) -> list[dict]:
    selected=[row for row in windows if row[f"{model}_score"]>=threshold];groups=[]
    for key in sorted({(row["station"],row["block_id"]) for row in selected}):
        rows=sorted((row for row in selected if (row["station"],row["block_id"])==key),key=lambda row:row["inferred_reference_time"]);current=[];last=None
        for row in rows:
            value=datetime.fromisoformat(row["inferred_reference_time"])
            if current and (value-last).total_seconds()>300:groups.append(current);current=[]
            current.append(row);last=value
        if current:groups.append(current)
    triggers=[]
    for index,group in enumerate(groups,1):
        peak=max(group,key=lambda row:row[f"{model}_score"])
        triggers.append({"model":model,"trigger_id":f"{model}-{index:05d}","station":peak["station"],"block_id":peak["block_id"],"trigger_time":peak["inferred_reference_time"],"peak_score":peak[f"{model}_score"],"merged_positive_window_count":len(group),"first_window_start":min(row["window_start"] for row in group),"last_window_end":max(row["window_end"] for row in group)})
    return triggers


def catalog_references(rows: list[dict], eligible: set[str]) -> list[dict]:
    grouped=defaultdict(list)
    for row in rows:grouped[(row["station"],row["reference_time"])].append(row)
    output=[]
    for index,((station,time),items) in enumerate(sorted(grouped.items()),1):
        candidate_ids=sorted({row["unified_candidate_id"] for row in items if row["unified_candidate_id"]})
        output.append({"catalog_id":f"catalog-{index:04d}","station":station,"reference_time":time,"candidate_ids":candidate_ids,"eligible_candidate_ids":sorted(set(candidate_ids)&eligible)})
    return output


def match_triggers(triggers: list[dict], catalogs: list[dict], tolerance: int) -> tuple[list[dict],dict]:
    pairs=[]
    for ti,trigger in enumerate(triggers):
        tt=datetime.fromisoformat(trigger["trigger_time"])
        for ci,catalog in enumerate(catalogs):
            if catalog["station"]!=trigger["station"]:continue
            delta=(tt-datetime.fromisoformat(catalog["reference_time"])).total_seconds()
            if abs(delta)<=tolerance:pairs.append((abs(delta),-float(trigger["peak_score"]),ti,ci,delta))
    used_t=set();used_c=set();matches={}
    for _,_,ti,ci,delta in sorted(pairs):
        if ti in used_t or ci in used_c:continue
        used_t.add(ti);used_c.add(ci);matches[ti]=(ci,delta)
    annotated=[];matched_eligible=set();false_count=0;protected=0;latencies=[]
    for index,trigger in enumerate(triggers):
        row=dict(trigger)
        if index not in matches:
            row.update({"match_status":"false_trigger","matched_catalog_id":"","matched_candidate_ids":"","latency_seconds":""});false_count+=1
        else:
            ci,delta=matches[index];catalog=catalogs[ci];eligible_ids=catalog["eligible_candidate_ids"]
            if eligible_ids:matched_eligible.update(eligible_ids);status="eligible_true_trigger";latencies.append(delta)
            else:status="protected_catalog_trigger";protected+=1
            row.update({"match_status":status,"matched_catalog_id":catalog["catalog_id"],"matched_candidate_ids":";".join(catalog["candidate_ids"]),"latency_seconds":delta})
        annotated.append(row)
    return annotated,{"eligible_true_triggers":len(matched_eligible),"matched_eligible_candidate_ids":sorted(matched_eligible),"false_triggers":false_count,"protected_catalog_triggers":protected,"latencies_seconds":latencies}


def main() -> None:
    positives=list(csv.DictReader(Path("data/manifests/preprocessing_positive_windows.csv").open(newline="")));backgrounds=list(csv.DictReader(Path("data/manifests/independent_background_windows.csv").open(newline="")))
    thresholds={};fold_models={}
    for station in ("S12","S14","S15","S16"):
        fold=f"holdout_{station}";thresholds[fold],model,scale,mean,std,weights=reconstruct_fold(fold,positives,backgrounds);fold_models[station]=(model,scale,mean,std,weights);print(f"reconstructed {fold} validation-only thresholds",flush=True)
    threshold_path=Path("results/predictions/continuous_scanning_thresholds_v0.1.json");threshold_path.write_text(json.dumps({"status":"reconstructed_from_training_station_validation_only_before_scan","target_validation_recall":.9,"folds":thresholds},indent=2)+"\n")

    plan=json.loads(Path("data/manifests/contiguous_evaluation_download_plan.json").read_text());days=list(csv.DictReader(Path("data/manifests/contiguous_evaluation_day_quality.csv").open(newline="")));product_groups=defaultdict(list)
    for item in plan["products"]:
        path=Path(item["path"]);product_groups[(path.parts[-4].upper(),int(path.parts[-3]),int(path.parts[-2]))].append(item)
    predictions=[]
    for number,day in enumerate(days,1):
        station,year,doy=day["station"],int(day["year"]),int(day["doy"]);items=product_groups[(station,year,doy)];paths=[ROOT/item["path"] for item in items if item["path"].endswith(".mseed")];att=read(str(next(path for path in paths if ".att." in path.name)))[0];wave=read(str(next(path for path in paths if ".att." not in path.name)))[0]
        model,scale,mean,std,weights=fold_models[station];fold=f"holdout_{station}";day_start=UTCDateTime(datetime(year,1,1)+timedelta(days=doy-1));day_samples=[];day_features=[];metadata=[]
        for offset in range(0,86400-600+1,60):
            start=day_start+offset;att_gap=local_gap_fraction(att,start);wave_gap=local_gap_fraction(wave,start)
            if att_gap>.2 or wave_gap>.2:continue
            sliced=np.asarray(wave.slice(start,start+600,nearest_sample=False).data,dtype=float);missing=sliced==-1
            valid=sliced[~missing];centered=sliced.copy();centered[~missing]-=np.median(valid);signal,coverage=fixed_length(centered,missing);day_samples.append(np.stack([signal,coverage]));vector=feature_vector(sliced,float(wave.stats.sampling_rate))
            if vector is None:raise RuntimeError("Qualified window failed feature extraction")
            day_features.append(vector);metadata.append((start,att_gap,wave_gap))
        x=np.asarray(day_samples,dtype=np.float32);x[:,0]/=scale;cnn=predict(model,x,batch_size=256);f=np.asarray(day_features);logistic=1/(1+np.exp(-np.clip(np.column_stack([np.ones(len(f)),(f-mean)/std])@weights,-30,30)))
        for (start,att_gap,wave_gap),cnn_score,log_score,sta_score in zip(metadata,cnn,logistic,f[:,4]):
            predictions.append({"station":station,"block_id":day["block_id"],"year":year,"doy":f"{doy:03d}","window_start":str(start).replace("Z",""),"window_end":str(start+600).replace("Z",""),"inferred_reference_time":str(start+120).replace("Z",""),"att_gap_fraction":att_gap,"waveform_gap_fraction":wave_gap,"tiny_cnn_score":float(cnn_score),"logistic_handcrafted_score":float(log_score),"sta_lta_score":float(sta_score)})
        print(f"[{number}/{len(days)}] scored {station} {year}-{doy:03d}: {len(metadata)} windows",flush=True)
    if len(predictions)!=152986:raise RuntimeError(f"Expected 152986 predictions, got {len(predictions)}")
    prediction_path=Path("results/predictions/continuous_scanning_window_scores_v0.1.csv.gz")
    with prediction_path.open("wb") as raw:
        with gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0) as compressed:
            with io.TextIOWrapper(compressed,newline="") as stream:
                writer=csv.DictWriter(stream,fieldnames=list(predictions[0]),lineterminator="\n");writer.writeheader();writer.writerows(predictions)

    catalog_rows=list(csv.DictReader(Path("data/manifests/contiguous_evaluation_catalog_audit.csv").open(newline="")));event_quality=list(csv.DictReader(Path("data/manifests/contiguous_evaluation_eligible_event_quality.csv").open(newline="")));eligible={row["unified_candidate_id"] for row in event_quality if row["event_window_integrity_status"]=="usable_integrity"};catalogs=catalog_references(catalog_rows,eligible)
    scan_hours=9329280/3600;station_hours={station:sum(int(row["scannable_union_seconds"]) for row in days if row["station"]==station)/3600 for station in ("S12","S14","S15","S16")};report={"status":"frozen_untouched_contiguous_scan_v0.1","eligible_event_count":len(eligible),"scannable_union_hours":scan_hours,"models":{}}
    all_primary_triggers=[]
    for model_name in MODELS:
        triggers=[];retention=0
        for station in ("S12","S14","S15","S16"):
            threshold=thresholds[f"holdout_{station}"][model_name]["primary"];station_rows=[row for row in predictions if row["station"]==station];triggers.extend(merge_triggers(station_rows,model_name,threshold))
            for block in {row["block_id"] for row in station_rows}:
                block_rows=[row for row in station_rows if row["block_id"]==block];base=min(datetime.fromisoformat(row["window_start"]) for row in block_rows)
                starts=sorted(int((datetime.fromisoformat(row["window_start"])-base).total_seconds()) for row in block_rows if row[f"{model_name}_score"]>=threshold)
                retention+=merged_duration_seconds(starts)
        for index,trigger in enumerate(triggers,1):trigger["trigger_id"]=f"{model_name}-{index:05d}"
        sensitivities={}
        primary_rows=[]
        for tolerance in (60,180,300):
            annotated,counts=match_triggers(triggers,catalogs,tolerance);tp=counts["eligible_true_triggers"];fp=counts["false_triggers"];recall=tp/len(eligible);precision=tp/max(1,tp+fp);counts.update({"eligible_event_recall":recall,"precision_excluding_protected_catalog_triggers":precision,"f1":2*precision*recall/max(1e-12,precision+recall),"false_triggers_per_hour":fp/scan_hours,"false_triggers_per_day":fp/(scan_hours/24),"median_latency_seconds":float(np.median(counts["latencies_seconds"])) if counts["latencies_seconds"] else None});sensitivities[str(tolerance)]=counts
            if tolerance==180:primary_rows=annotated
        station_stats={}
        for station in ("S12","S14","S15","S16"):
            rows=[row for row in primary_rows if row["station"]==station];fp=sum(row["match_status"]=="false_trigger" for row in rows);station_stats[station]={"triggers":len(rows),"false_triggers":fp,"false_triggers_per_hour":fp/station_hours[station],"scan_hours":station_hours[station]}
        report["models"][model_name]={"trigger_count":len(triggers),"retained_union_seconds":retention,"retained_fraction_of_scannable_duration":retention/9329280,"matching_sensitivities":sensitivities,"primary_180s_by_station":station_stats};all_primary_triggers.extend(primary_rows)
    trigger_path=Path("results/predictions/continuous_scanning_triggers_v0.1.csv")
    with trigger_path.open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(all_primary_triggers[0]),lineterminator="\n");writer.writeheader();writer.writerows(all_primary_triggers)
    report["window_score_sha256"]=hashlib.sha256(prediction_path.read_bytes()).hexdigest();report["trigger_csv_sha256"]=hashlib.sha256(trigger_path.read_bytes()).hexdigest();report["threshold_json_sha256"]=hashlib.sha256(threshold_path.read_bytes()).hexdigest()
    report_path=Path("results/predictions/continuous_scanning_results_v0.1.json");report_path.write_text(json.dumps(report,indent=2)+"\n")
    fig,axes=plt.subplots(1,3,figsize=(13,4));names=list(MODELS);primary=[report["models"][name]["matching_sensitivities"]["180"] for name in names]
    axes[0].bar(names,[row["false_triggers_per_hour"] for row in primary],color=["#e07a3f","#2b7bba","#587b55"]);axes[0].set_ylabel("False triggers/hour");axes[0].set_title("Untouched continuous scan")
    axes[1].bar(names,[row["eligible_event_recall"] for row in primary],color=["#e07a3f","#2b7bba","#587b55"]);axes[1].set_ylim(0,1);axes[1].set_ylabel("Recall (n=6)");axes[1].set_title("Integrity-eligible events")
    axes[2].bar(names,[report["models"][name]["retained_fraction_of_scannable_duration"] for name in names],color=["#e07a3f","#2b7bba","#587b55"]);axes[2].set_ylim(0,1);axes[2].set_ylabel("Retained duration fraction");axes[2].set_title("Retention simulation")
    for axis in axes:axis.tick_params(axis="x",rotation=20);axis.spines[["top","right"]].set_visible(False)
    fig.suptitle("LunaSeis-1 continuous scanning v0.1 (frozen untouched frame)");fig.tight_layout();fig.savefig("results/figures/continuous_scanning_results_v0.1.png",dpi=180);plt.close(fig)
    audit={"top_false_triggers":{},"false_triggers_by_model_station":{"|".join(key):value for key,value in sorted(Counter((row["model"],row["station"]) for row in all_primary_triggers if row["match_status"]=="false_trigger").items())}}
    for name in MODELS:audit["top_false_triggers"][name]=sorted((row for row in all_primary_triggers if row["model"]==name and row["match_status"]=="false_trigger"),key=lambda row:-float(row["peak_score"]))[:20]
    Path("results/predictions/continuous_scanning_error_audit_v0.1.json").write_text(json.dumps(audit,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__=="__main__":main()
