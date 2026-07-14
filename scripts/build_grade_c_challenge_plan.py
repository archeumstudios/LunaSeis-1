#!/usr/bin/env python3
"""Freeze an event-rich, model-unseen Grade-C natural-impact challenge frame."""

from __future__ import annotations

import argparse,csv,hashlib,json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime
from pathlib import Path

try:
    from scripts.build_contiguous_evaluation_plan import channel_product_names,prior_station_days
    from scripts.build_shallow_download_plan import BASE_URL,fetch_listing,fetch_md5_manifest
except ModuleNotFoundError:  # pragma: no cover
    from build_contiguous_evaluation_plan import channel_product_names,prior_station_days
    from build_shallow_download_plan import BASE_URL,fetch_listing,fetch_md5_manifest

STATIONS=("S12","S14","S15","S16")
SEED="lunaseis-grade-c-impact-challenge-v0.3"


def ranked(rows:list[dict],station:str,seed:str=SEED)->list[dict]:
    return sorted(rows,key=lambda r:hashlib.sha256(f"{seed}|{station}|{r['event_key']}".encode()).hexdigest())


def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates-per-station",type=int,default=16)
    parser.add_argument("--workers",type=int,default=4)
    parser.add_argument("--cache",type=Path,default=Path("data/interim/grade_c_challenge_listing_cache.json"))
    parser.add_argument("--days-output",type=Path,default=Path("data/manifests/grade_c_challenge_station_days.csv"))
    parser.add_argument("--catalog-output",type=Path,default=Path("data/manifests/grade_c_challenge_catalog.csv"))
    parser.add_argument("--plan-output",type=Path,default=Path("data/manifests/grade_c_challenge_download_plan.json"))
    args=parser.parse_args();prior=prior_station_days(Path("data/manifests"),{args.days_output,args.catalog_output,args.plan_output})
    source=list(csv.DictReader(Path("data/manifests/events_audit.csv").open(newline="")));selected=[]
    for station in STATIONS:
        candidates=[]
        for row in source:
            if row["event_class"]!="natural_impact" or row["grade"]!="C" or station not in row["positive_visibility_stations"].split(";"):continue
            when=datetime.fromisoformat(row["catalog_start_minute"]);key=(station,when.year,int(when.strftime("%j")))
            if key in prior:continue
            if not any(value.startswith(station+".MH") for value in row["positive_visibility_channels"].split(";")):continue
            candidates.append({**row,"station":station,"year":when.year,"doy":int(when.strftime("%j"))})
        chosen=[];used=set()
        for row in ranked(candidates,station):
            day=(row["year"],row["doy"])
            if day in used:continue
            used.add(day);chosen.append(row)
            if len(chosen)==args.candidates_per_station:break
        if len(chosen)!=args.candidates_per_station:raise RuntimeError(f"Insufficient untouched candidates for {station}")
        selected.extend(chosen)
    args.cache.parent.mkdir(parents=True,exist_ok=True);cache=json.loads(args.cache.read_text()) if args.cache.exists() else {}
    missing=[(r["station"],r["year"],r["doy"]) for r in selected if f"{r['station']}:{r['year']}:{r['doy']:03d}" not in cache]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(fetch_listing,*key):key for key in missing}
        for number,future in enumerate(as_completed(futures),1):
            station,year,doy=futures[future];cache[f"{station}:{year}:{doy:03d}"]=future.result()
            if number%10==0 or number==len(missing):args.cache.write_text(json.dumps(cache,separators=(",",":"))+"\n")
            print(f"[{number}/{len(missing)}] inspected {station} {year}-{doy:03d}",flush=True)
    md5=fetch_md5_manifest();products=[];days=[];catalog=[]
    for row in sorted(selected,key=lambda r:(r["station"],r["catalog_start_minute"],r["event_key"])):
        station,year,doy=row["station"],int(row["year"]),int(row["doy"]);listing=cache[f"{station}:{year}:{doy:03d}"]
        att=channel_product_names(listing,"ATT");reported=[value.split(".",1)[1] for value in row["positive_visibility_channels"].split(";") if value.startswith(station+".MH")]
        available=[channel for channel in ("MHZ","MH1","MH2") if channel in reported and channel_product_names(listing,channel)]
        usable=bool(att and available);primary=available[0] if available else "";names=att+channel_product_names(listing,primary) if usable else []
        days.append({"station":station,"year":year,"doy":f"{doy:03d}","block_id":row["event_key"],"day_in_block":1,"selection_seed":SEED,"prior_station_day_overlap":0,"att_and_primary_mh_available":int(usable),"selected_primary_channel":primary,"selected_bytes":sum(listing[n] for n in names)})
        catalog.append({"station":station,"block_id":row["event_key"],"catalog_source":"PDS_levent_grade_C","source_event_id":row["event_key"],"reference_time":row["catalog_start_minute"]+":00","unified_candidate_id":row["event_key"],"event_class":"natural_impact_grade_C","evaluation_group":"grade_c_"+row["event_key"],"existing_fold_roles":"none","prior_pilot_fold_exposed":0,"prospective_event_recall_eligibility":"eligible_pending_waveform_QA" if usable else "archive_incomplete"})
        for name in names:
            relative=f"data/xa/continuous_waveform/{station.lower()}/{year}/{doy:03d}/{name}";digest=md5.get(relative.lower())
            if not digest:raise RuntimeError(f"Official MD5 missing for {relative}")
            products.append({"path":relative,"url":f"{BASE_URL}/{station.lower()}/{year}/{doy:03d}/{name}","bytes":listing[name],"md5":digest,"batch_id":1,"block_id":row["event_key"]})
    for path,rows in ((args.days_output,days),(args.catalog_output,catalog)):
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open("w",newline="") as stream:writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator="\n");writer.writeheader();writer.writerows(rows)
    products.sort(key=lambda r:r["path"]);plan={"status":"frozen_planned_not_downloaded","source_bundle":"urn:nasa:pds:apollo_pse::1.0","selection_seed":SEED,"selection":"16 hash-ranked Grade-C natural impacts per station with positive catalog MH visibility, unique station-days, and no prior-manifest station-day overlap; fixed before waveform/model inspection; unavailable products are not replaced","label_scope":"lower_confidence_confirmatory_challenge_not_grade_ab_ground_truth","prior_station_days_excluded":len(prior),"station_days_selected":len(days),"station_days_complete":sum(int(r["att_and_primary_mh_available"]) for r in days),"station_days_incomplete":sum(not int(r["att_and_primary_mh_available"]) for r in days),"complete_days_by_station":dict(Counter(r["station"] for r in days if int(r["att_and_primary_mh_available"]))),"product_count":len(products),"total_bytes":sum(int(r["bytes"]) for r in products),"batch_summaries":[{"batch_id":1,"station_day_count":sum(int(r["att_and_primary_mh_available"]) for r in days),"product_count":len(products),"bytes":sum(int(r["bytes"]) for r in products)}],"station_days_csv_sha256":hashlib.sha256(args.days_output.read_bytes()).hexdigest(),"catalog_csv_sha256":hashlib.sha256(args.catalog_output.read_bytes()).hexdigest(),"products":products,"notes":["No model scores were read.","Grade C is weaker catalog evidence and must remain separate from Grade A/B claims.","Selected days are never replaced for missing products."]}
    args.plan_output.write_text(json.dumps(plan,indent=2)+"\n");print(json.dumps({k:v for k,v in plan.items() if k!="products"},indent=2))


if __name__=="__main__":main()
