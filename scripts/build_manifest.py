#!/usr/bin/env python3
"""Build PUBLIC_RELEASE_MANIFEST.json from the current allowlisted tree."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "PUBLIC_RELEASE_MANIFEST.json"
EXCLUDED_PARTS = {"__pycache__", ".git", ".pytest_cache"}
EXCLUDED_NAMES = {".DS_Store"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def main() -> None:
    files = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == OUT or any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        if path.name in EXCLUDED_NAMES or path.suffix in EXCLUDED_SUFFIXES:
            continue
        rel = path.relative_to(ROOT).as_posix()
        data = path.read_bytes()
        files.append({"path": rel, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    payload = {
        "schema": "master-public-release-manifest-v1",
        "release_status": "release-candidate",
        "release_date": "2026-10-05",
        "denominator": 23859,
        "publication_structural_coverage": 1.0,
        "claim_scope": "structural outcome or explicit abstention; not semantic decryption",
        "files": files,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT} with {len(files)} files")


if __name__ == "__main__":
    main()

