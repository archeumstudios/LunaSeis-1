#!/usr/bin/env python3
"""Audit PDS SHZ/ATT availability and size a shallow-moonquake pilot download."""

from __future__ import annotations

import argparse
import csv
import http.client
import json
import re
import ssl
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import certifi

BASE_URL = (
    "https://pds-geosciences.wustl.edu/Lunar/urn-nasa-pds-apollo_pse/"
    "data/xa/continuous_waveform"
)
MD5_URL = (
    "https://pds-geosciences.wustl.edu/Lunar/urn-nasa-pds-apollo_pse/"
    "urn-nasa-pds-apollo_pse.md5"
)
ENTRY = re.compile(r"([0-9]+) <A HREF=\"([^\"]+)\">([^<]+)</A>", re.IGNORECASE)
MD5_LINE = re.compile(r"^([0-9A-Fa-f]{32})\s+(.+)$")
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def fetch_listing(station: str, year: int, doy: int) -> dict[str, int]:
    url = f"{BASE_URL}/{station.lower()}/{year}/{doy:03d}/"
    for attempt in range(4):
        request = urllib.request.Request(url, headers={"User-Agent": "LunaSeis-1/0.1"})
        try:
            with urllib.request.urlopen(request, timeout=60, context=SSL_CONTEXT) as response:
                text = response.read().decode("utf-8", errors="replace")
            break
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return {}
            if attempt == 3:
                raise
        except (urllib.error.URLError, http.client.RemoteDisconnected, TimeoutError):
            if attempt == 3:
                raise
        time.sleep(1.5 * (attempt + 1))
    return {name.lower(): int(size) for size, _, name in ENTRY.findall(text)}


def expected_names(station: str, year: int, doy: int) -> list[str]:
    prefix = f"xa.{station.lower()}"
    date = f"{year}.{doy:03d}.0"
    return [
        f"{prefix}..att.{date}.mseed", f"{prefix}..att.{date}.xml",
        f"{prefix}..shz.{date}.mseed", f"{prefix}..shz.{date}.xml",
    ]


def fetch_md5_manifest() -> dict[str, str]:
    request = urllib.request.Request(MD5_URL, headers={"User-Agent": "LunaSeis-1/0.1"})
    with urllib.request.urlopen(request, timeout=120, context=SSL_CONTEXT) as response:
        text = response.read().decode("utf-8-sig")
    result = {}
    for line in text.splitlines():
        match = MD5_LINE.match(line)
        if match:
            path = match.group(2).strip().replace("\\", "/").lstrip("/").lower()
            result[path] = match.group(1).lower()
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--events", type=Path,
        default=Path("data/manifests/onodera_2024_shallow_events.csv"),
    )
    parser.add_argument(
        "--coverage-output", type=Path,
        default=Path("data/manifests/onodera_2024_shallow_coverage.csv"),
    )
    parser.add_argument(
        "--plan-output", type=Path,
        default=Path("data/manifests/shallow_pilot_download_plan.json"),
    )
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    with args.events.open(encoding="utf-8", newline="") as stream:
        events = list(csv.DictReader(stream))
    keys = sorted({
        (station, int(row["year"]), int(row["doy"]))
        for row in events for station in row["reported_stations"].split(";")
    })

    listings: dict[tuple[str, int, int], dict[str, int]] = {}
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(fetch_listing, *key): key for key in keys}
        for future in as_completed(futures):
            key = futures[future]
            listings[key] = future.result()
            print(f"inspected {key[0]} {key[1]}-{key[2]:03d}: {len(listings[key])} products")

    coverage = []
    selected_products: dict[str, dict[str, object]] = {}
    event_usable = {}
    for row in events:
        usable_count = 0
        for station in row["reported_stations"].split(";"):
            key = (station, int(row["year"]), int(row["doy"]))
            listing = listings[key]
            names = expected_names(*key)
            found = {name: listing.get(name) for name in names}
            usable = all(value is not None for value in found.values())
            usable_count += int(usable)
            coverage.append({
                "event_id": row["event_id"], "source_group": row["source_group"],
                "station": station, "year": row["year"], "doy": row["doy"],
                "start_time_utc": row["start_time_utc"],
                "att_available": "1" if found[names[0]] is not None else "0",
                "shz_available": "1" if found[names[2]] is not None else "0",
                "all_data_and_labels_available": "1" if usable else "0",
                "selected_bytes": str(sum(value or 0 for value in found.values())),
            })
            if usable:
                for name in names:
                    path = f"data/xa/continuous_waveform/{station.lower()}/{key[1]}/{key[2]:03d}/{name}"
                    selected_products[path] = {
                        "path": path,
                        "url": f"{BASE_URL}/{station.lower()}/{key[1]}/{key[2]:03d}/{name}",
                        "bytes": found[name],
                    }
        event_usable[row["event_id"]] = usable_count

    args.coverage_output.parent.mkdir(parents=True, exist_ok=True)
    with args.coverage_output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(coverage[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(coverage)

    md5_manifest = fetch_md5_manifest()
    products = [selected_products[path] for path in sorted(selected_products)]
    for product in products:
        product["md5"] = md5_manifest.get(str(product["path"]).lower(), "")
        if not product["md5"]:
            raise RuntimeError(f"Selected product missing from NASA MD5 manifest: {product['path']}")
    summary = {
        "source_bundle": "urn:nasa:pds:apollo_pse::1.0",
        "selection": "Onodera corrected shallow-event station-days; SHZ and ATT MiniSEED plus PDS labels",
        "event_count": len(events),
        "event_station_pairs_requested": len(coverage),
        "event_station_pairs_complete": sum(row["all_data_and_labels_available"] == "1" for row in coverage),
        "events_with_at_least_one_complete_station": sum(value > 0 for value in event_usable.values()),
        "events_without_complete_station": sorted(key for key, value in event_usable.items() if value == 0),
        "unique_station_days_complete": len(products) // 4,
        "product_count": len(products),
        "total_bytes": sum(int(product["bytes"]) for product in products),
        "products": products,
        "notes": [
            "Plan downloads full Earth-day SHZ and ATT files because PDS serves daily products.",
            "Products are deduplicated when multiple events share one station-day.",
            "Every selected product includes an expected MD5 from the official bundle manifest.",
            "Availability does not prove an event window is gap-free or scientifically usable.",
        ],
    }
    args.plan_output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in summary.items() if key != "products"}, indent=2))


if __name__ == "__main__":
    main()
