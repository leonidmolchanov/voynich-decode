#!/usr/bin/env python3
"""Regenerate data/factorization/full_surface_factorization.tsv from the locked,
audited strict-v82 core — a fully traceable projection, not a hand-edit.

The FACTOR layer is updated from `data/strict/strict_anonymous_factor_v82.tsv`
(the official 100% immutable core, coverage_percent 100.0, 23 859/23 859,
independent completion audit PASS). The SURFACE layer (the EVA transcription
reading per cell) is stable and is carried from the existing factorization file,
with v82's audited-surface corrections overlaid where v82 recorded one. Every
value is therefore traceable (surface = shipped transcription layer + v82
corrections; factor/tier = v82 locked core). The transform is idempotent.

  surface                    <- existing surface, overridden by v82 audited_surface where set
  symbolic_factor            <- v82 audited_factor
  assignment_tier            <- STRICT_ACCEPTED   (v82 lock: all cells are P0 zero-error core)
  assignment_source          <- strict_v82_core
  direct_transcription_factor<- v82 original_factor
  direct_agreement           <- 1 if v82 original_factor == audited_factor else 0
  shadow_wave                <- "" (not applicable under the v82 flat core)

Run from the release root:  python3 scripts/build_full_surface_from_v82.py
Then verify:                python3 scripts/summarize_factorization.py
                            python3 scripts/verify_release.py   (after build_manifest.py)
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V82 = ROOT / "data" / "strict" / "strict_anonymous_factor_v82.tsv"
DENOM = ROOT / "data" / "reference" / "aligned_cell_denominator_v1.tsv"
OUT = ROOT / "data" / "factorization" / "full_surface_factorization.tsv"
COLUMNS = ["record_id", "folio", "surface", "symbolic_factor", "assignment_tier",
           "assignment_source", "shadow_wave", "direct_transcription_factor", "direct_agreement"]


def main() -> None:
    src = list(csv.DictReader(V82.open(encoding="utf-8", newline=""), delimiter="\t"))
    denom_ids = {r["record_id"] for r in csv.DictReader(DENOM.open(encoding="utf-8", newline=""), delimiter="\t")}
    # surface base = existing transcription layer (stable EVA reading per cell)
    base_surface = {r["record_id"]: (r["surface"] or "").strip()
                    for r in csv.DictReader(OUT.open(encoding="utf-8", newline=""), delimiter="\t")}

    out_rows = []
    for r in src:
        rid = r["record_id"]
        surface = (r["audited_surface"] or "").strip() or base_surface.get(rid, "") \
            or (r["original_surface"] or "").strip()
        factor = (r["audited_factor"] or "").strip()
        out_rows.append({
            "record_id": rid,
            "folio": r["folio"],
            "surface": surface,
            "symbolic_factor": factor,
            "assignment_tier": "STRICT_ACCEPTED",
            "assignment_source": "strict_v82_core",
            "shadow_wave": "",
            "direct_transcription_factor": (r["original_factor"] or "").strip(),
            "direct_agreement": "1" if (r["original_factor"] or "").strip() == factor else "0",
        })

    # validation — refuse to write a broken projection
    ids = {r["record_id"] for r in out_rows}
    assert len(out_rows) == 23859, f"expected 23859 rows, got {len(out_rows)}"
    assert ids == denom_ids, "record_id set does not match the canonical denominator"
    blank_surface = [r["record_id"] for r in out_rows if not r["surface"]]
    blank_factor = [r["record_id"] for r in out_rows if not r["symbolic_factor"]]
    assert not blank_surface, f"blank surface for {len(blank_surface)} cells, e.g. {blank_surface[:3]}"
    assert not blank_factor, f"blank factor for {len(blank_factor)} cells"

    with OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)

    agree = sum(1 for r in out_rows if r["direct_agreement"] == "1")
    print(f"wrote {OUT} : {len(out_rows)} rows, all STRICT_ACCEPTED, "
          f"direct_agreement 1={agree}/0={len(out_rows)-agree}, 0 blank")


if __name__ == "__main__":
    main()
