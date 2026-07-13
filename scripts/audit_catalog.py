#!/usr/bin/env python3
"""Create a machine-readable structural audit of Apollo catalog CSV files."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def audit_csv(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        columns = reader.fieldnames or []
    nonempty = {column: sum(bool((row.get(column) or "").strip()) for row in rows) for column in columns}
    unique = {
        column: len({(row.get(column) or "").strip() for row in rows if (row.get(column) or "").strip()})
        for column in columns
    }
    return {
        "path": path.name,
        "row_count": len(rows),
        "columns": columns,
        "nonempty_count": nonempty,
        "unique_nonempty_count": unique,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--catalog-dir",
        type=Path,
        default=Path("data/raw/apollo_seismic_event_catalog_v1.0/data"),
    )
    parser.add_argument(
        "--output", type=Path, default=Path("data/manifests/catalog_schema_audit.json")
    )
    args = parser.parse_args()
    csv_paths = sorted(
        path for path in args.catalog_dir.glob("*.csv") if "inventory" not in path.name
    )
    report = {
        "source_bundle": "urn:nasa:pds:apollo_seismic_event_catalog::1.0",
        "files": [audit_csv(path) for path in csv_paths],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for item in report["files"]:
        print(f"{item['path']}: {item['row_count']} rows; {len(item['columns'])} columns")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
