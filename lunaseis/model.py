"""Compact depthwise model and frozen robust preprocessing."""

from __future__ import annotations

import numpy as np
import torch
from torch import nn

TARGET_SAMPLES=4096


class DepthwiseCNN(nn.Module):
    """Selected compact detector; 2,761 trainable parameters."""
    def __init__(self) -> None:
        super().__init__();self.stem=nn.Sequential(nn.Conv1d(2,16,9,stride=2,padding=4),nn.ReLU());layers=[]
        for dilation in (1,2,4):
            layers.extend([nn.Conv1d(16,16,7,stride=2,padding=3*dilation,dilation=dilation,groups=16),nn.Conv1d(16,24,1),nn.ReLU()])
            if dilation!=4:layers.append(nn.Conv1d(24,16,1))
        self.features=nn.Sequential(*layers);self.classifier=nn.Linear(48,1)
    def forward(self,x:torch.Tensor)->torch.Tensor:
        z=self.features(self.stem(x));return self.classifier(torch.cat([z.mean(-1),z.amax(-1)],1)).squeeze(-1)


def preprocess(values: np.ndarray, length: int=TARGET_SAMPLES) -> np.ndarray | None:
    values=np.asarray(values,dtype=np.float64);missing=values==-1
    if not values.size or float(np.mean(missing))>.2 or np.all(missing):return None
    valid=values[~missing];center=float(np.median(valid));deviation=valid-center;mad=float(np.median(np.abs(deviation)));p90=float(np.quantile(np.abs(deviation),.9));scale=max(1.,1.4826*mad,p90/2.5)
    signal=np.zeros(length,dtype=np.float32);coverage=np.zeros(length,dtype=np.float32);count=min(length,len(values));good=~missing[:count];signal[:count][good]=np.clip((values[:count][good]-center)/scale,-20,20);coverage[:count][good]=1
    return np.stack([signal,coverage])
