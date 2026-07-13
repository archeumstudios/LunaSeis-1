#!/usr/bin/env python3
"""Audit tiny-CNN reliance on waveform amplitude and missing-sample coverage."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import torch

try:
    from scripts.run_pilot_baselines import metrics
    from scripts.run_tiny_cnn_pilot import TinyCNN, build_role, deterministic_negative_rows, predict
except ModuleNotFoundError:  # pragma: no cover
    from run_pilot_baselines import metrics
    from run_tiny_cnn_pilot import TinyCNN, build_role, deterministic_negative_rows, predict


def safe_correlation(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.corrcoef(left,right)[0,1]) if np.std(left)>0 and np.std(right)>0 else 0.0


def main() -> None:
    report=json.loads(Path("results/predictions/tiny_cnn_pilot_v0.1.json").read_text())
    positives=list(csv.DictReader(Path("data/manifests/preprocessing_positive_windows.csv").open(newline="")))
    backgrounds=list(csv.DictReader(Path("data/manifests/independent_background_windows.csv").open(newline="")))
    audit={"status":"pilot_shortcut_sensitivity_not_paper_result","folds":{}}
    for fold,fold_report in report["folds"].items():
        pos=[row for row in positives if row["fold"]==fold and row["role"]=="test"]
        neg=[row for row in backgrounds if row["fold"]==fold and row["role"]=="test"]
        x,y,_=build_role(pos,deterministic_negative_rows(neg,len(pos)))
        checkpoint=torch.load(f"models/checkpoints/tiny_cnn_pilot_v0.1/{fold}.pt",weights_only=True)
        model=TinyCNN();model.load_state_dict(checkpoint["state_dict"]);scale=float(checkpoint["waveform_training_std"])
        scaled=x.copy();scaled[:,0]/=scale;threshold=float(fold_report["validation_selected_threshold"])
        normal=predict(model,scaled)
        no_mask=scaled.copy();no_mask[:,1]=1
        only_mask=scaled.copy();only_mask[:,0]=0
        zero_mask=scaled.copy();zero_mask[:,1]=0
        gap_fraction=1-np.mean(scaled[:,1],axis=1);rms=np.sqrt(np.mean(scaled[:,0]**2,axis=1))
        audit["folds"][fold]={
            "normal":metrics(normal,y,threshold),
            "coverage_all_valid":metrics(predict(model,no_mask),y,threshold),
            "coverage_all_zero":metrics(predict(model,zero_mask),y,threshold),
            "coverage_only_waveform_zero":metrics(predict(model,only_mask),y,threshold),
            "score_gap_fraction_correlation":safe_correlation(normal,gap_fraction),
            "score_waveform_rms_correlation":safe_correlation(normal,rms),
        }
        print(f"audited {fold}",flush=True)
    Path("results/predictions/tiny_cnn_shortcut_audit_v0.1.json").write_text(json.dumps(audit,indent=2)+"\n")
    print(json.dumps(audit,indent=2))


if __name__=="__main__":main()
