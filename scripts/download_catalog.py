#!/usr/bin/env python3
"""Download and checksum-verify the official Apollo event catalog bundle."""

from __future__ import annotations

import argparse
import hashlib
import re
import ssl
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath

import certifi

BASE_URL = (
    "https://pds-geosciences.wustl.edu/Lunar/"
    "urn-nasa-pds-apollo_seismic_event_catalog/"
)
MANIFEST_NAME = "urn-nasa-pds-apollo_seismic_event_catalog.md5"
MANIFEST_LINE = re.compile(r"^([0-9A-Fa-f]{32})\s+(.+)$")
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def parse_manifest(text: str) -> list[tuple[str, PurePosixPath]]:
    """Parse the PDS MD5 manifest and normalize its Windows path separators."""
    entries: list[tuple[str, PurePosixPath]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        match = MANIFEST_LINE.match(line)
        if match is None:
            raise ValueError(f"Invalid manifest line {line_number}: {line!r}")
        relative = PurePosixPath(match.group(2).strip().replace("\\", "/").lstrip("/"))
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Unsafe manifest path on line {line_number}: {relative}")
        entries.append((match.group(1).lower(), relative))
    if not entries:
        raise ValueError("Manifest contained no products")
    return entries


def md5sum(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "LunaSeis-1/0.1"})
    with urllib.request.urlopen(request, timeout=60, context=SSL_CONTEXT) as response, temporary.open("wb") as output:
        while block := response.read(1024 * 1024):
            output.write(block)
    temporary.replace(destination)


def download_bundle(destination: Path) -> tuple[int, int]:
    destination.mkdir(parents=True, exist_ok=True)
    manifest_path = destination / MANIFEST_NAME
    fetch(urllib.parse.urljoin(BASE_URL, MANIFEST_NAME), manifest_path)
    entries = parse_manifest(manifest_path.read_text(encoding="utf-8-sig"))

    total_bytes = 0
    for expected_md5, relative in entries:
        target = destination.joinpath(*relative.parts)
        if not target.exists() or md5sum(target) != expected_md5:
            fetch(urllib.parse.urljoin(BASE_URL, relative.as_posix()), target)
        actual_md5 = md5sum(target)
        if actual_md5 != expected_md5:
            raise RuntimeError(
                f"Checksum mismatch for {relative}: expected {expected_md5}, got {actual_md5}"
            )
        total_bytes += target.stat().st_size
        print(f"verified {relative} ({target.stat().st_size:,} bytes)")
    return len(entries), total_bytes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--destination",
        type=Path,
        default=Path("data/raw/apollo_seismic_event_catalog_v1.0"),
    )
    args = parser.parse_args()
    count, total_bytes = download_bundle(args.destination)
    print(f"verified {count} products totaling {total_bytes:,} bytes")


if __name__ == "__main__":
    main()
