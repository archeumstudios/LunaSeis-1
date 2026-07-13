#!/usr/bin/env python3
"""Download one event/station day from the checksum-pinned shallow plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath

try:
    from scripts.download_catalog import fetch, md5sum
    from scripts.download_pilot_waveforms import validate_product
except ModuleNotFoundError:  # pragma: no cover
    from download_catalog import fetch, md5sum
    from download_pilot_waveforms import validate_product


def select_products(plan: dict, station: str, year: int, doy: int) -> list[dict]:
    marker = f"/{station.lower()}/{year}/{doy:03d}/"
    products = [item for item in plan["products"] if marker in str(item["path"]).lower()]
    if len(products) != 4:
        raise RuntimeError(f"Expected four ATT/SHZ products for {marker}, found {len(products)}")
    return products


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-id", default="KO-SMQ-26")
    parser.add_argument("--station", default="S15")
    parser.add_argument("--year", type=int, default=1975)
    parser.add_argument("--doy", type=int, default=82)
    parser.add_argument("--plan", type=Path, default=Path("data/manifests/shallow_pilot_download_plan.json"))
    parser.add_argument("--destination", type=Path, default=Path("data/raw/apollo_pse_v1.0"))
    parser.add_argument("--receipt", type=Path, default=Path("data/manifests/ko_smq_26_sample_download.json"))
    args = parser.parse_args()

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    products = select_products(plan, args.station, args.year, args.doy)
    verified = []
    for product in products:
        relative, expected_bytes, expected_md5 = validate_product(product)
        target = args.destination.joinpath(*PurePosixPath(relative).parts)
        if not (target.exists() and target.stat().st_size == expected_bytes and md5sum(target) == expected_md5):
            fetch(str(product["url"]), target)
        actual_md5 = md5sum(target)
        if target.stat().st_size != expected_bytes or actual_md5 != expected_md5:
            raise RuntimeError(f"Integrity failure for {relative}")
        verified.append({**product, "local_path": str(target), "verified_md5": actual_md5})
        print(f"verified {relative} ({expected_bytes:,} bytes)")

    receipt = {
        "event_id": args.event_id,
        "station": args.station,
        "year": args.year,
        "doy": args.doy,
        "verified_product_count": len(verified),
        "verified_total_bytes": sum(int(item["bytes"]) for item in verified),
        "products": verified,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.receipt}")


if __name__ == "__main__":
    main()
