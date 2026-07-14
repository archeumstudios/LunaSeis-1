"""Command-line interface for LunaSeis-1 inference."""

from __future__ import annotations

import argparse,json
from pathlib import Path

from .inference import LunaSeisDetector,write_scan_json


def main()->None:
    parser=argparse.ArgumentParser(description="Scan one Apollo MH MiniSEED file with LunaSeis-1.");parser.add_argument("mseed",type=Path);parser.add_argument("--station",required=True,choices=("S12","S14","S15","S16"));parser.add_argument("--output",type=Path,default=Path("lunaseis_predictions.json"));args=parser.parse_args();detector=LunaSeisDetector(args.station);write_scan_json(detector,args.mseed,args.output);print(json.dumps({"output":str(args.output),**detector.metadata()},indent=2))
