#!/usr/bin/env python3
"""Audit frozen continuous-scan false triggers without changing decisions."""

from __future__ import annotations

import csv
import gzip
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from obspy import UTCDateTime, read

MODELS=("tiny_cnn","logistic_handcrafted","sta_lta")
ROOT=Path("data/raw/apollo_pse_v1.0")


def safe_correlation(left, right) -> float:
    left=np.asarray(left,dtype=float);right=np.asarray(right,dtype=float)
    return float(np.corrcoef(left,right)[0,1]) if np.std(left)>0 and np.std(right)>0 else 0.


def main() -> None:
    thresholds=json.loads(Path("results/predictions/continuous_scanning_thresholds_v0.1.json").read_text())["folds"]
    with gzip.open("results/predictions/continuous_scanning_window_scores_v0.1.csv.gz","rt",newline="") as stream:windows=list(csv.DictReader(stream))
    triggers=list(csv.DictReader(Path("results/predictions/continuous_scanning_triggers_v0.1.csv").open(newline="")))
    audit={"status":"post_result_error_audit_no_retuning","window_count":len(windows),"models":{}}
    for model in MODELS:
        station_summary={}
        for station in ("S12","S14","S15","S16"):
            rows=[row for row in windows if row["station"]==station];scores=np.array([float(row[f"{model}_score"]) for row in rows]);threshold=float(thresholds[f"holdout_{station}"][model]["primary"]);positive=scores>=threshold
            station_summary[station]={"window_count":len(rows),"positive_window_count":int(np.sum(positive)),"positive_window_fraction":float(np.mean(positive)),"score_waveform_gap_correlation":safe_correlation(scores,[float(row["waveform_gap_fraction"]) for row in rows]),"score_att_gap_correlation":safe_correlation(scores,[float(row["att_gap_fraction"]) for row in rows])}
        false=[row for row in triggers if row["model"]==model and row["match_status"]=="false_trigger"]
        block_counts=Counter(row["block_id"] for row in false);sizes=[int(row["merged_positive_window_count"]) for row in false]
        audit["models"][model]={"by_station":station_summary,"false_triggers_by_block":dict(sorted(block_counts.items())),"false_trigger_merged_window_count_median":float(np.median(sizes)) if sizes else 0,"false_trigger_merged_window_count_max":max(sizes,default=0),"top_false_triggers":sorted(false,key=lambda row:-float(row["peak_score"]))[:20]}

    plan=json.loads(Path("data/manifests/contiguous_evaluation_download_plan.json").read_text());wave_paths={}
    for item in plan["products"]:
        if not item["path"].endswith(".mseed") or ".att." in item["path"]:continue
        path=Path(item["path"]);wave_paths[(path.parts[-4].upper(),int(path.parts[-3]),int(path.parts[-2]))]=ROOT/item["path"]
    panels=[]
    for model in MODELS:
        for row in audit["models"][model]["top_false_triggers"][:3]:
            target=UTCDateTime(row["trigger_time"]+"Z");trace=read(str(wave_paths[(row["station"],target.year,target.julday)]))[0];window=trace.slice(target-120,target+480,nearest_sample=False);values=np.asarray(window.data,dtype=float);values[values==-1]=np.nan;seconds=np.arange(len(values))/float(trace.stats.sampling_rate)-120;panels.append((model,row,seconds,values))
    fig,axes=plt.subplots(len(panels),1,figsize=(12,1.75*len(panels)),sharex=True)
    for axis,(model,row,seconds,values) in zip(axes,panels):
        axis.plot(seconds,values,color="#304f6d",linewidth=.5,rasterized=True);axis.axvline(0,color="#d1495b",linewidth=1);axis.set_ylabel(f"{row['station']}\ncounts");axis.set_title(f"{model}: {row['trigger_time']} score={float(row['peak_score']):.4g}",loc="left",fontsize=8);axis.spines[["top","right"]].set_visible(False)
    axes[-1].set_xlabel("Seconds relative to false-trigger peak reference");fig.suptitle("Highest-scoring false triggers by method (post-result audit)");fig.tight_layout();fig.savefig("results/figures/continuous_scanning_top_false_triggers_v0.1.png",dpi=180);plt.close(fig)
    Path("results/predictions/continuous_scanning_error_audit_v0.1.json").write_text(json.dumps(audit,indent=2)+"\n");print(json.dumps(audit,indent=2))


if __name__=="__main__":main()
