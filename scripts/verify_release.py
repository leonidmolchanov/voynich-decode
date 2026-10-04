#!/usr/bin/env python3
"""Verify file hashes and critical release invariants."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "PUBLIC_RELEASE_MANIFEST.json"


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures = []
    for item in manifest["files"]:
        path = ROOT / item["path"]
        if not path.is_file():
            failures.append(f"missing: {item['path']}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != item["sha256"]:
            failures.append(f"hash mismatch: {item['path']}")

    with (ROOT / "data/factorization/full_surface_factorization.tsv").open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    if len(rows) != manifest["denominator"]:
        failures.append(f"factorization rows: {len(rows)} != {manifest['denominator']}")
    if any(not row["symbolic_factor"].strip() for row in rows):
        failures.append("blank symbolic_factor found")

    # __pycache__/.DS_Store are transient build/OS artifacts (gitignored, never shipped,
    # created by running any script) and must not fail verification; flag only real leaks.
    forbidden = {"PRIVATE_RECORDS", ".idea", "web_cache"}
    present = sorted({part for path in ROOT.rglob("*") for part in path.parts if part in forbidden})
    if present:
        failures.append(f"forbidden path components: {present}")

    if failures:
        print("FAIL")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print(f"PASS: {len(manifest['files'])} files, denominator {manifest['denominator']}")


if __name__ == "__main__":
    main()

