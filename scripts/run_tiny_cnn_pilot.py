#!/usr/bin/env python3
"""Train a deterministic tiny 1D CNN on the frozen LunaSeis pilot folds."""

from __future__ import annotations

import csv
import hashlib
import json
import random
import resource
import time
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from obspy import Stream, UTCDateTime, read
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

try:
    from scripts.build_nonshallow_download_plan import product_names
    from scripts.run_pilot_baselines import best_threshold, metrics
except ModuleNotFoundError:  # pragma: no cover
    from build_nonshallow_download_plan import product_names
    from run_pilot_baselines import best_threshold, metrics

ROOT = Path("data/raw/apollo_pse_v1.0/data/xa/continuous_waveform")
SEED = 20260714
TARGET_SAMPLES = 4096


def set_deterministic(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)


@lru_cache(maxsize=4096)
def load_day(station: str, year: int, doy: int, channel: str):
    name = product_names(station, year, doy, channel)[0]
    return read(str(ROOT / station.lower() / str(year) / f"{doy:03d}" / name))[0]


def bin_valid_means(values: np.ndarray, missing: np.ndarray, bins: int = TARGET_SAMPLES) -> tuple[np.ndarray, np.ndarray]:
    """Reduce a trace to fixed bins without interpolating gap sentinels."""
    edges = np.linspace(0, len(values), bins + 1, dtype=int)
    output = np.zeros(bins, dtype=np.float32)
    coverage = np.zeros(bins, dtype=np.float32)
    for index, (left, right) in enumerate(zip(edges[:-1], edges[1:])):
        valid = ~missing[left:right]
        if np.any(valid):
            output[index] = float(np.mean(values[left:right][valid]))
            coverage[index] = float(np.mean(valid))
    return output, coverage


def fixed_length(values: np.ndarray, missing: np.ndarray, length: int = TARGET_SAMPLES) -> tuple[np.ndarray, np.ndarray]:
    """Pad or crop at native cadence while preserving a separate validity mask."""
    signal=np.zeros(length,dtype=np.float32);coverage=np.zeros(length,dtype=np.float32)
    count=min(length,len(values));valid=~missing[:count]
    signal[:count][valid]=values[:count][valid]
    coverage[:count][valid]=1.0
    return signal,coverage


def waveform(station: str, channel: str, start: datetime) -> np.ndarray | None:
    utc = UTCDateTime(start.isoformat() + "Z")
    end = utc + 600
    days = [(utc.year, utc.julday)]
    if (end.year, end.julday) != days[0]:
        days.append((end.year, end.julday))
    try:
        stream = Stream([load_day(station, year, doy, channel).copy() for year, doy in days])
    except FileNotFoundError:
        return None
    stream.merge(method=0, fill_value=-1)
    if len(stream) != 1:
        return None
    values = np.asarray(stream[0].slice(utc, end, nearest_sample=False).data, dtype=np.float64)
    if not values.size:
        return None
    missing = values == -1
    if float(np.mean(missing)) > 0.2 or np.all(missing):
        return None
    values[~missing] -= np.median(values[~missing])
    signal, coverage = fixed_length(values, missing)
    return np.stack([signal, coverage], axis=0)


class TinyCNN(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv1d(2, 8, 9, stride=2, padding=4), nn.ReLU(),
            nn.Conv1d(8, 16, 7, stride=2, padding=3), nn.ReLU(),
            nn.Conv1d(16, 24, 5, stride=2, padding=2), nn.ReLU(),
        )
        self.classifier = nn.Linear(48, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        learned=self.features(x)
        pooled=torch.cat([learned.mean(dim=-1),learned.amax(dim=-1)],dim=1)
        return self.classifier(pooled).squeeze(-1)


def deterministic_negative_rows(rows: list[dict[str, str]], count: int) -> list[dict[str, str]]:
    return sorted(rows, key=lambda row: hashlib.sha256(("baseline-v0.1|" + row["station"] + row["channel"] + row["start_time"]).encode()).hexdigest())[:count]


def build_role(positive_rows, negative_rows) -> tuple[np.ndarray, np.ndarray, list[dict[str, str]]]:
    arrays: list[np.ndarray] = []
    labels: list[int] = []
    provenance: list[dict[str, str]] = []
    for label, rows, key in ((1, positive_rows, "window_start_nominal"), (0, negative_rows, "start_time")):
        for row in rows:
            sample = waveform(row["station"], row["channel"], datetime.fromisoformat(row[key]))
            if sample is not None:
                arrays.append(sample); labels.append(label); provenance.append(row)
    return np.asarray(arrays, dtype=np.float32), np.asarray(labels, dtype=np.int64), provenance


def predict(model: nn.Module, x: np.ndarray, batch_size: int = 128) -> np.ndarray:
    model.eval(); scores=[]
    with torch.no_grad():
        for (batch,) in DataLoader(TensorDataset(torch.from_numpy(x)), batch_size=batch_size):
            scores.append(torch.sigmoid(model(batch)).numpy())
    return np.concatenate(scores)


def average_precision(scores: np.ndarray, labels: np.ndarray) -> float:
    order=np.argsort(-scores,kind="stable"); ranked=labels[order]
    positives=int(np.sum(ranked==1))
    if positives==0:return 0.0
    precision=np.cumsum(ranked==1)/np.arange(1,len(ranked)+1)
    return float(np.sum(precision[ranked==1])/positives)


def train_fold(train_x, train_y, val_x, val_y, epochs: int = 20) -> tuple[TinyCNN, list[dict[str, float]], float]:
    scale = float(np.std(train_x[:, 0]))
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError("Training-fold waveform scale is invalid")
    train_x = train_x.copy(); val_x = val_x.copy()
    train_x[:, 0] /= scale; val_x[:, 0] /= scale
    model=TinyCNN(); optimizer=torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    loss_fn=nn.BCEWithLogitsLoss(); history=[]; best_state=None; best_loss=float("inf")
    generator=torch.Generator().manual_seed(SEED)
    loader=DataLoader(TensorDataset(torch.from_numpy(train_x),torch.from_numpy(train_y.astype(np.float32))),batch_size=64,shuffle=True,generator=generator)
    for epoch in range(1, epochs+1):
        model.train(); losses=[]
        for batch, labels in loader:
            optimizer.zero_grad(); loss=loss_fn(model(batch),labels); loss.backward(); optimizer.step(); losses.append(float(loss.detach()))
        val_scores=predict(model,val_x); val_loss=float(np.mean(-(val_y*np.log(val_scores+1e-7)+(1-val_y)*np.log(1-val_scores+1e-7))))
        history.append({"epoch":epoch,"train_loss":float(np.mean(losses)),"validation_loss":val_loss})
        if val_loss < best_loss:
            best_loss=val_loss; best_state={key:value.detach().clone() for key,value in model.state_dict().items()}
    assert best_state is not None
    model.load_state_dict(best_state)
    return model, history, scale


def main() -> None:
    set_deterministic()
    positives=list(csv.DictReader(Path("data/manifests/preprocessing_positive_windows.csv").open(newline="")))
    backgrounds=list(csv.DictReader(Path("data/manifests/independent_background_windows.csv").open(newline="")))
    output_root=Path("results/predictions/tiny_cnn_pilot_v0.1"); output_root.mkdir(parents=True,exist_ok=True)
    checkpoint_root=Path("models/checkpoints/tiny_cnn_pilot_v0.1"); checkpoint_root.mkdir(parents=True,exist_ok=True)
    report={"status":"pilot_only_not_paper_result","seed":SEED,"target_samples":TARGET_SAMPLES,"folds":{}}
    for fold in sorted({row["fold"] for row in positives}):
        set_deterministic()
        datasets={}; provenance={}
        for role in ("train","validation","test"):
            pos=[row for row in positives if row["fold"]==fold and row["role"]==role]
            neg=[row for row in backgrounds if row["fold"]==fold and row["role"]==role]
            neg=deterministic_negative_rows(neg,len(pos))
            x,y,p=build_role(pos,neg); datasets[role]=(x,y); provenance[role]=p
        train_x,train_y=datasets["train"]; val_x,val_y=datasets["validation"]; test_x,test_y=datasets["test"]
        started=time.perf_counter(); model,history,scale=train_fold(train_x,train_y,val_x,val_y); train_seconds=time.perf_counter()-started
        scaled_val=val_x.copy(); scaled_val[:,0]/=scale
        scaled_test=test_x.copy(); scaled_test[:,0]/=scale
        val_scores=predict(model,scaled_val); threshold=best_threshold(val_scores,val_y)
        test_scores=predict(model,scaled_test); result=metrics(test_scores,test_y,threshold);result["pr_auc"]=average_precision(test_scores,test_y)
        prediction_rows=[]
        for index,(score,label,row) in enumerate(zip(test_scores,test_y,provenance["test"])):
            prediction_rows.append({"fold":fold,"row_index":index,"label":int(label),"score":float(score),"predicted":int(score>=threshold),"station":row["station"],"channel":row["channel"],"source_id":row.get("event_id",row.get("start_time",""))})
        prediction_path=output_root/f"{fold}_predictions.csv"
        with prediction_path.open("w",newline="") as stream:
            writer=csv.DictWriter(stream,fieldnames=list(prediction_rows[0]),lineterminator="\n");writer.writeheader();writer.writerows(prediction_rows)
        checkpoint=checkpoint_root/f"{fold}.pt"
        torch.save({"state_dict":model.state_dict(),"waveform_training_std":scale,"seed":SEED,"target_samples":TARGET_SAMPLES},checkpoint)
        scripted=torch.jit.trace(model,torch.zeros(1,2,TARGET_SAMPLES)); exported=checkpoint_root/f"{fold}.torchscript.pt"; scripted.save(str(exported))
        parameters=sum(value.numel() for value in model.parameters())
        benchmark=torch.randn(1,2,TARGET_SAMPLES)
        with torch.no_grad():
            for _ in range(20): model(benchmark)
            tic=time.perf_counter()
            for _ in range(200): model(benchmark)
            latency_ms=(time.perf_counter()-tic)*1000/200
        fold_report={"counts":{role:{"event":int(np.sum(y==1)),"background":int(np.sum(y==0))} for role,(_,y) in datasets.items()},"waveform_training_std":scale,"validation_selected_threshold":threshold,"test_metrics":result,"parameters":parameters,"checkpoint_bytes":checkpoint.stat().st_size,"torchscript_bytes":exported.stat().st_size,"cpu_single_window_latency_ms":latency_ms,"training_seconds":train_seconds,"peak_process_rss_bytes":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,"history":history,"prediction_sha256":hashlib.sha256(prediction_path.read_bytes()).hexdigest()}
        report["folds"][fold]=fold_report
        print(f"completed {fold}: F1={result['f1']:.3f}, FP/h={result['false_positives_per_hour']:.3f}",flush=True)
    report_path=Path("results/predictions/tiny_cnn_pilot_v0.1.json");report_path.write_text(json.dumps(report,indent=2)+"\n")
    baseline=json.loads(Path("results/predictions/independent_background_baselines_v0.1.json").read_text())
    folds=list(report["folds"]); fig,axes=plt.subplots(1,2,figsize=(11,4.2)); x=np.arange(len(folds)); width=.35
    cnn=[report["folds"][fold]["test_metrics"] for fold in folds]; logistic=[baseline["folds"][fold]["logistic_handcrafted"] for fold in folds]
    for axis,key,title,ylabel in ((axes[0],"f1","Held-out-station F1","F1"),(axes[1],"false_positives_per_hour","Catalog-negative false alarms","False positives/hour")):
        axis.bar(x-width/2,[row[key] for row in logistic],width,label="logistic");axis.bar(x+width/2,[row[key] for row in cnn],width,label="tiny CNN")
        axis.set_xticks(x,folds,rotation=20);axis.set_title(title);axis.set_ylabel(ylabel);axis.spines[["top","right"]].set_visible(False)
    axes[0].legend(frameon=False);fig.suptitle("LunaSeis-1 tiny-CNN pilot (not paper results)");fig.tight_layout();fig.savefig("results/figures/tiny_cnn_pilot_v0.1.png",dpi=180);plt.close(fig)
    print(json.dumps({fold:report["folds"][fold]["test_metrics"] for fold in folds},indent=2))


if __name__=="__main__": main()
