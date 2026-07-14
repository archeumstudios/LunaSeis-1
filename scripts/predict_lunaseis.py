#!/usr/bin/env python3
"""Score or scan one Apollo MH MiniSEED file with LunaSeis-1."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from lunaseis.cli import main


if __name__=="__main__":main()
