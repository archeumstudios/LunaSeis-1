#!/usr/bin/env python3
"""Resumably download and verify every product in the shallow waveform plan."""

from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path, PurePosixPath

try:
    from scripts.download_catalog import fetch, md5sum
    from scripts.download_pilot_waveforms import validate_product
except ModuleNotFoundError:  # pragma: no cover
    from download_catalog import fetch, md5sum
    from download_pilot_waveforms import validate_product


def verify_one(product: dict, destination: Path) -> tuple[str, int, bool]:
    relative, expected_bytes, expected_md5 = validate_product(product)
    target = destination.joinpath(*PurePosixPath(relative).parts)
    reused = target.exists() and target.stat().st_size == expected_bytes and md5sum(target) == expected_md5
    if not reused:
        for attempt in range(4):
            try:
                fetch(str(product["url"]), target)
                break
            except Exception:
                target.with_suffix(target.suffix + ".part").unlink(missing_ok=True)
                if attempt == 3:
                    raise
                time.sleep(1.5 * (attempt + 1))
    if target.stat().st_size != expected_bytes or md5sum(target) != expected_md5:
        raise RuntimeError(f"Integrity failure for {relative}")
    return str(relative), expected_bytes, reused


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=Path("data/manifests/shallow_pilot_download_plan.json"))
    parser.add_argument("--destination", type=Path, default=Path("data/raw/apollo_pse_v1.0"))
    parser.add_argument("--receipt", type=Path, default=Path("data/manifests/shallow_plan_download_receipt.json"))
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    products = plan["products"]
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(verify_one, item, args.destination): item for item in products}
        for number, future in enumerate(as_completed(futures), start=1):
            path, size, reused = future.result()
            results.append((path, size, reused))
            print(f"[{number}/{len(products)}] {'reused' if reused else 'downloaded'} {path} ({size:,} bytes)", flush=True)
    verified_bytes = sum(size for _, size, _ in results)
    if len(results) != int(plan["product_count"]) or verified_bytes != int(plan["total_bytes"]):
        raise RuntimeError("Verified totals do not match the pinned plan")
    receipt = {
        "source_plan": str(args.plan),
        "verified_product_count": len(results),
        "verified_total_bytes": verified_bytes,
        "downloaded_product_count_this_run": sum(not reused for _, _, reused in results),
        "reused_product_count_this_run": sum(reused for _, _, reused in results),
        "integrity": "exact size and MD5 verified for every product",
    }
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
