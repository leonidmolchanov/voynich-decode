#!/usr/bin/env python3
"""Download one Yale IIIF image selected by folio label."""
from __future__ import annotations

import argparse
import csv
import hashlib
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "metadata/folio_inventory.tsv"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--folio", required=True, help="folio label, for example 78r")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    with INVENTORY.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    matches = [row for row in rows if row["folio_label"].lower() == args.folio.lower()]
    if len(matches) != 1:
        raise SystemExit(f"expected one inventory row for {args.folio!r}, found {len(matches)}")
    row = matches[0]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(row["image_url"], args.output)
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    expected = row["sha256"]
    print(f"downloaded {args.output}\nsha256={digest}")
    if expected and digest != expected:
        raise SystemExit(f"checksum mismatch: expected {expected}")


if __name__ == "__main__":
    main()

