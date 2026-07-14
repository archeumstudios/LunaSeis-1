#!/usr/bin/env python3
"""Create consistent publication figures from committed LunaSeis evidence."""

from __future__ import annotations
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT=Path("paper/figures");OUT.mkdir(parents=True,exist_ok=True)
COLORS={"cnn":"#0072B2","robust":"#009E73","logistic":"#E69F00","sta":"#666666","fail":"#D55E00","ink":"#1F2933","light":"#E8EDF2"}


def style():
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9,"axes.titlesize":10,"axes.labelsize":9,"figure.titlesize":12,"axes.spines.top":False,"axes.spines.right":False,"pdf.fonttype":42,"ps.fonttype":42})


def save(fig,name):
    fig.savefig(OUT/f"{name}.pdf",bbox_inches="tight");fig.savefig(OUT/f"{name}.png",dpi=300,bbox_inches="tight");plt.close(fig)


def workflow():
    fig,ax=plt.subplots(figsize=(7.2,2.8));ax.axis("off")
    labels=[("PDS source\nverification","MD5 + metadata"),("Provenance-aware\nwindows","ATT + gaps"),("Leakage-controlled\ndevelopment","family + station"),("Frozen continuous\ntests","6,748.2 h"),("Operational\nassessment","recall + FP h⁻¹")]
    xs=np.linspace(.1,.9,len(labels))
    for i,(title,sub) in enumerate(labels):
        ax.add_patch(plt.Rectangle((xs[i]-.075,.34),.15,.38,facecolor="#F5F7FA",edgecolor=COLORS["ink"],lw=1.1,transform=ax.transAxes));ax.text(xs[i],.58,title,ha="center",va="center",weight="bold",fontsize=7.0,transform=ax.transAxes);ax.text(xs[i],.42,sub,ha="center",va="center",fontsize=6.8,color="#52606D",transform=ax.transAxes)
        if i<len(labels)-1:ax.annotate("",xy=(xs[i+1]-.09,.53),xytext=(xs[i]+.09,.53),xycoords=ax.transAxes,arrowprops={"arrowstyle":"->","lw":1.2,"color":COLORS["cnn"]})
    ax.text(.5,.12,"Every test frame was selected and frozen before inference; consumed frames were never reused for tuning.",ha="center",color=COLORS["fail"],weight="bold",transform=ax.transAxes)
    save(fig,"figure_1_study_design")


def continuous():
    v1=json.load(open("results/predictions/continuous_scanning_results_v0.1.json"));v2=json.load(open("results/predictions/continuous_scanning_results_v0.2.json"));v3=json.load(open("results/predictions/grade_c_challenge_results.json"))
    labels=["A/B v0.1\n(n=6)","A/B v0.2\n(n=3)","Grade-C v0.3\n(n=63)"]
    recall=[v1["models"]["tiny_cnn"]["matching_sensitivities"]["180"]["eligible_event_recall"],v2["models"]["artifact_robust_cnn"]["matching_sensitivities"]["180"]["eligible_event_recall"],v3["matching_sensitivities"]["180"]["eligible_event_recall"]]
    fp=[v1["models"]["tiny_cnn"]["matching_sensitivities"]["180"]["false_triggers_per_hour"],v2["models"]["artifact_robust_cnn"]["matching_sensitivities"]["180"]["false_triggers_per_hour"],v3["matching_sensitivities"]["180"]["false_triggers_per_hour"]]
    retain=[v1["models"]["tiny_cnn"]["retained_fraction_of_scannable_duration"],v2["models"]["artifact_robust_cnn"]["retained_fraction_of_scannable_duration"],v3["retained_fraction_of_scannable_duration"]]
    fig,axes=plt.subplots(1,3,figsize=(7.2,2.65));x=np.arange(3)
    for ax,values,title,ylabel,ylim in zip(axes,[recall,fp,retain],["Event recall","False-trigger burden","Retention simulation"],["Recall","False triggers per hour","Retained fraction"],[(0,1),(0,1.25),(0,1)]):
        bars=ax.bar(x,values,color=[COLORS["cnn"],COLORS["robust"],COLORS["fail"]],width=.66);ax.set_xticks(x,labels,fontsize=7.0);ax.set_title(title,weight="bold");ax.set_ylabel(ylabel);ax.set_ylim(*ylim);ax.grid(axis="y",color=COLORS["light"],lw=.8)
        for bar,value in zip(bars,values):ax.text(bar.get_x()+bar.get_width()/2,value+ylim[1]*.025,f"{value:.3f}",ha="center",va="bottom",fontsize=7.5)
    fig.suptitle("Frozen continuous evaluations remained below operational requirements",weight="bold");fig.tight_layout();save(fig,"figure_2_frozen_continuous_results")


def development_gap():
    suite=json.load(open("results/predictions/compact_model_suite_v0.1.json"));challenge=json.load(open("results/predictions/grade_c_challenge_results.json"));dev=suite["models"]["depthwise_cnn"]["aggregate"]
    fig,axes=plt.subplots(1,2,figsize=(7.2,2.7));labels=["Development\nvalidation","Frozen Grade-C\nchallenge"]
    vals=[dev["mean_validation_event_recall"],challenge["matching_sensitivities"]["180"]["eligible_event_recall"]];bars=axes[0].bar(labels,vals,color=[COLORS["cnn"],COLORS["fail"]],width=.55);axes[0].set_ylim(0,1);axes[0].set_ylabel("Event recall");axes[0].set_title("Recall transfer gap",weight="bold")
    for b,v in zip(bars,vals):axes[0].text(b.get_x()+b.get_width()/2,v+.03,f"{v:.1%}",ha="center",weight="bold")
    vals=[dev["false_triggers_per_hour"],challenge["matching_sensitivities"]["180"]["false_triggers_per_hour"]];bars=axes[1].bar(labels,vals,color=[COLORS["cnn"],COLORS["fail"]],width=.55);axes[1].set_ylabel("Merged triggers per hour");axes[1].set_title("Continuous trigger shift",weight="bold")
    for b,v in zip(bars,vals):axes[1].text(b.get_x()+b.get_width()/2,v+.025,f"{v:.3f}",ha="center",weight="bold")
    for ax in axes:ax.grid(axis="y",color=COLORS["light"],lw=.8)
    fig.suptitle("Development selection substantially overstated operational transfer",weight="bold");fig.tight_layout();save(fig,"figure_3_development_to_challenge_gap")


def inventory():
    classes=["Deep moonquake","Natural impact","Shallow moonquake","Artificial impact"];counts=[609,623,74,8]
    fig,ax=plt.subplots(figsize=(5.8,2.8));bars=ax.barh(classes,counts,color=["#4C78A8","#F58518","#54A24B","#B279A2"]);ax.invert_yaxis();ax.set_xlabel("Physical-event candidates");ax.set_title("Unified positive-candidate registry (n=1,314)",weight="bold");ax.grid(axis="x",color=COLORS["light"],lw=.8)
    for b,v in zip(bars,counts):ax.text(v+10,b.get_y()+b.get_height()/2,f"{v:,}",va="center",weight="bold")
    ax.set_xlim(0,700);fig.tight_layout();save(fig,"figure_4_event_inventory")


if __name__=="__main__":style();workflow();continuous();development_gap();inventory();print(f"wrote figures to {OUT}")
