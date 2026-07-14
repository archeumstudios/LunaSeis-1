"""Public inference interface for the LunaSeis-1 research prototype."""

from __future__ import annotations

import json
from datetime import datetime,timedelta
from pathlib import Path

import numpy as np
import torch
from obspy import UTCDateTime,read

from .model import DepthwiseCNN,preprocess

STATIONS=("S12","S14","S15","S16")


class LunaSeisDetector:
    def __init__(self,station:str,checkpoint_root:Path|str="models/checkpoints/compact_model_suite_v0.1") -> None:
        station=station.upper()
        if station not in STATIONS:raise ValueError(f"station must be one of {STATIONS}")
        path=Path(checkpoint_root)/f"depthwise_cnn_holdout_{station}.pt";checkpoint=torch.load(path,map_location="cpu",weights_only=True);self.model=DepthwiseCNN();self.model.load_state_dict(checkpoint["state_dict"]);self.model.eval();self.threshold=float(checkpoint["threshold"]);self.station=station;self.checkpoint=path

    def score_values(self,values:np.ndarray)->float|None:
        sample=preprocess(values)
        if sample is None:return None
        with torch.no_grad():return float(torch.sigmoid(self.model(torch.from_numpy(sample[None])))[0])

    def predict_values(self,values:np.ndarray)->dict:
        score=self.score_values(values)
        return {"station":self.station,"score":score,"threshold":self.threshold,"triggered":None if score is None else bool(score>=self.threshold),"status":"rejected_gap_integrity" if score is None else "scored_research_prototype"}

    def scan_mseed(self,path:Path|str,window_seconds:int=600,stride_seconds:int=60)->list[dict]:
        trace=read(str(path))[0];rate=float(trace.stats.sampling_rate);window=max(1,round(window_seconds*rate));stride=max(1,round(stride_seconds*rate));rows=[]
        for left in range(0,max(0,len(trace.data)-window+1),stride):
            start=trace.stats.starttime+left/rate;result=self.predict_values(np.asarray(trace.data[left:left+window]));rows.append({**result,"window_start":str(start),"window_end":str(start+window_seconds),"inferred_reference_time":str(start+120)})
        return rows

    def metadata(self)->dict:
        return {"name":"LunaSeis-1 depthwise CNN research prototype","version":"0.1.0","author":"Advaith Praveen (APRK)","station_fold":f"holdout_{self.station}","parameters":sum(p.numel() for p in self.model.parameters()),"threshold":self.threshold,"checkpoint":str(self.checkpoint),"warning":"Research prototype. Both frozen continuous tests failed event-recall requirements; not operational or flight ready."}


def write_scan_json(detector:LunaSeisDetector,mseed:Path|str,output:Path|str)->None:
    Path(output).write_text(json.dumps({"metadata":detector.metadata(),"windows":detector.scan_mseed(mseed)},indent=2)+"\n")
