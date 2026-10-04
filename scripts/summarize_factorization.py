#!/usr/bin/env python3
"""Print a deterministic summary of the public full-surface layer."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACTOR = ROOT / "data/factorization/full_surface_factorization.tsv"
DENOMINATOR = ROOT / "data/reference/aligned_cell_denominator_v1.tsv"


def read_rows(path: Path):
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def main() -> None:
    rows = read_rows(FACTOR)
    denom = read_rows(DENOMINATOR)
    ids = [row["record_id"] for row in rows]
    denom_ids = {row["record_id"] for row in denom}
    factors = [row["symbolic_factor"].strip() for row in rows]
    agreement = Counter(row["direct_agreement"] for row in rows)
    report = {
        "rows": len(rows),
        "unique_record_ids": len(set(ids)),
        "denominator_rows": len(denom),
        "ids_match_denominator": set(ids) == denom_ids,
        "missing_symbolic_factors": sum(not value for value in factors),
        "unique_symbolic_factors": len(set(factors)),
        "assignment_tiers": dict(sorted(Counter(row["assignment_tier"] for row in rows).items())),
        "direct_agreement": dict(sorted(agreement.items())),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    if report["rows"] != 23859 or not report["ids_match_denominator"] or report["missing_symbolic_factors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

