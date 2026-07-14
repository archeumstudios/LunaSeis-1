#!/usr/bin/env python3
"""Compare compact depthwise and temporal CNNs on continuous development data."""

from __future__ import annotations

import csv,gzip,hashlib,json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader,TensorDataset

try:
    from scripts.run_contiguous_scanning_v0_1 import merge_triggers,recall_threshold
    from scripts.run_tiny_cnn_pilot import average_precision,deterministic_negative_rows,predict
    from scripts.train_artifact_robust_models import SEED,build,ranked,scan_scores,set_deterministic
except ModuleNotFoundError:  # pragma: no cover
    from run_contiguous_scanning_v0_1 import merge_triggers,recall_threshold
    from run_tiny_cnn_pilot import average_precision,deterministic_negative_rows,predict
    from train_artifact_robust_models import SEED,build,ranked,scan_scores,set_deterministic


class DepthwiseCNN(nn.Module):
    def __init__(self) -> None:
        super().__init__();self.stem=nn.Sequential(nn.Conv1d(2,16,9,stride=2,padding=4),nn.ReLU())
        layers=[]
        for dilation in (1,2,4):
            layers.extend([nn.Conv1d(16,16,7,stride=2,padding=3*dilation,dilation=dilation,groups=16),nn.Conv1d(16,24,1),nn.ReLU()]);
            if dilation!=4:layers.append(nn.Conv1d(24,16,1))
        self.features=nn.Sequential(*layers);self.classifier=nn.Linear(48,1)
    def forward(self,x):
        z=self.features(self.stem(x));return self.classifier(torch.cat([z.mean(-1),z.amax(-1)],1)).squeeze(-1)


class ResidualTCNBlock(nn.Module):
    def __init__(self,channels,dilation):
        super().__init__();self.net=nn.Sequential(nn.Conv1d(channels,channels,5,padding=2*dilation,dilation=dilation),nn.ReLU(),nn.Conv1d(channels,channels,5,padding=2*dilation,dilation=dilation),nn.ReLU())
    def forward(self,x):return x+self.net(x)


class CompactTCN(nn.Module):
    def __init__(self) -> None:
        super().__init__();self.stem=nn.Sequential(nn.Conv1d(2,12,9,stride=4,padding=4),nn.ReLU());self.blocks=nn.Sequential(*(ResidualTCNBlock(12,d) for d in (1,2,4,8)));self.classifier=nn.Linear(24,1)
    def forward(self,x):
        z=self.blocks(self.stem(x));return self.classifier(torch.cat([z.mean(-1),z.amax(-1)],1)).squeeze(-1)


MODELS={"depthwise_cnn":DepthwiseCNN,"compact_tcn":CompactTCN}


def train(model,x,y,epochs=14):
    set_deterministic();optimizer=torch.optim.AdamW(model.parameters(),lr=7e-4,weight_decay=3e-4);loss_fn=nn.BCEWithLogitsLoss();history=[];generator=torch.Generator().manual_seed(SEED)
    loader=DataLoader(TensorDataset(torch.from_numpy(x),torch.from_numpy(y.astype(np.float32))),batch_size=64,shuffle=True,generator=generator)
    for _ in range(epochs):
        model.train();losses=[]
        for batch,labels in loader:
            optimizer.zero_grad();loss=loss_fn(model(batch),labels);loss.backward();optimizer.step();losses.append(float(loss.detach()))
        history.append(float(np.mean(losses)))
    return history


def score_rows(model,rows):
    # Temporarily provide a model compatible with the shared batching implementation.
    output=[]
    try:
        from scripts.train_artifact_robust_models import extract
    except ModuleNotFoundError:  # pragma: no cover
        from train_artifact_robust_models import extract
    for station_day in sorted({(r["station"],r["year"],r["doy"]) for r in rows}):
        chosen=[r for r in rows if (r["station"],r["year"],r["doy"])==station_day];samples=[];kept=[]
        for row in chosen:
            sample=extract(row,"window_start","robust_level")
            if sample is not None:samples.append(sample);kept.append(row)
        if samples:
            scores=predict(model,np.asarray(samples,dtype=np.float32),256)
            for row,score in zip(kept,scores):output.append({**row,"score":float(score),"inferred_reference_time":(datetime.fromisoformat(row["window_start"])+__import__('datetime').timedelta(seconds=120)).isoformat()})
    return output


def main():
    set_deterministic();positives=list(csv.DictReader(Path("data/manifests/preprocessing_positive_windows.csv").open(newline="")));backgrounds=list(csv.DictReader(Path("data/manifests/independent_background_windows.csv").open(newline="")))
    with gzip.open("data/manifests/continuous_validation_windows_v0.1.csv.gz","rt",newline="") as stream:continuous=list(csv.DictReader(stream))
    by_station=defaultdict(list)
    for row in continuous:by_station[row["station"]].append((int(row["year"]),int(row["doy"])))
    cutoff={s:sorted(set(v))[len(set(v))//2] for s,v in by_station.items()};root=Path("models/checkpoints/compact_model_suite_v0.1");root.mkdir(parents=True,exist_ok=True);report={"status":"development_only_no_claim_on_consumed_tests","seed":SEED,"models":{}}
    for name,constructor in MODELS.items():
        report["models"][name]={};total_fp=0;total_hours=0;recalls=[]
        for heldout in ("S12","S14","S15","S16"):
            fold=f"holdout_{heldout}";stations={"S12","S14","S15","S16"}-{heldout};pos_train=[r for r in positives if r["fold"]==fold and r["role"]=="train"];pos_val=[r for r in positives if r["fold"]==fold and r["role"]=="validation"]
            neg=deterministic_negative_rows([r for r in backgrounds if r["fold"]==fold and r["role"]=="train"],len(pos_train));hard=[r for r in continuous if r["station"] in stations and (int(r["year"]),int(r["doy"]))<cutoff[r["station"]]];hard=ranked(hard,len(pos_train),f"{name}|{fold}|hard");hard_val=[r for r in continuous if r["station"] in stations and (int(r["year"]),int(r["doy"]))>=cutoff[r["station"]]]
            px,py=build(pos_train,1,"window_start_nominal","robust_level");nx,ny=build(neg,0,"start_time","robust_level");hx,hy=build(hard,0,"window_start","robust_level");x=np.asarray(px+nx+hx,dtype=np.float32);y=np.asarray(py+ny+hy);model=constructor();history=train(model,x,y)
            vx,vy=build(pos_val,1,"window_start_nominal","robust_level");event_scores=predict(model,np.asarray(vx,dtype=np.float32));threshold=recall_threshold(event_scores,np.asarray(vy),.9);scored=score_rows(model,hard_val);rows=[{**r,f"{name}_score":r["score"],"block_id":f"{r['station']}_VAL"} for r in scored];triggers=merge_triggers(rows,name,threshold)
            starts=defaultdict(list)
            for r in hard_val:starts[r["station"]].append(datetime.fromisoformat(r["window_start"]))
            hours=sum((max(v)-min(v)).total_seconds()/3600+1/6 for v in starts.values());recall=float(np.mean(event_scores>=threshold));recalls.append(recall);total_fp+=len(triggers);total_hours+=hours
            checkpoint=root/f"{name}_{fold}.pt";torch.save({"state_dict":model.state_dict(),"model":name,"preprocessing":"robust_level","threshold":threshold,"seed":SEED},checkpoint)
            report["models"][name][fold]={"parameters":sum(p.numel() for p in model.parameters()),"threshold":threshold,"validation_event_count":len(vy),"validation_event_recall":recall,"validation_event_pr_auc":average_precision(event_scores,np.asarray(vy)),"continuous_validation_windows":len(scored),"continuous_validation_hours":hours,"merged_false_triggers":len(triggers),"false_triggers_per_hour":len(triggers)/hours,"history":history,"checkpoint_sha256":hashlib.sha256(checkpoint.read_bytes()).hexdigest()};print(name,fold,recall,len(triggers)/hours,flush=True)
        report["models"][name]["aggregate"]={"mean_validation_event_recall":float(np.mean(recalls)),"merged_false_triggers":total_fp,"fold_hours":total_hours,"false_triggers_per_hour":total_fp/total_hours}
    prior=json.load(open("results/predictions/artifact_robust_model_selection_v0.1.json"));candidates={"robust_tiny_cnn":prior["candidates"]["robust_level"]["aggregate"],**{n:v["aggregate"] for n,v in report["models"].items()}};selected=min(candidates,key=lambda n:candidates[n]["false_triggers_per_hour"]);report["all_candidate_aggregates"]=candidates;report["selected_model"]=selected;report["selection_rule"]="lowest merged continuous-development triggers/hour subject to >=0.90 mean positive-validation recall"
    Path("results/predictions/compact_model_suite_v0.1.json").write_text(json.dumps(report,indent=2)+"\n");print(json.dumps({"selected":selected,"aggregates":candidates},indent=2))


if __name__=="__main__":main()
