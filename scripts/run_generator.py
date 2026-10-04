#!/usr/bin/env python3
"""Generate one synthetic surface aligned to the public manuscript layout."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_DIR = ROOT / "src" / "voynich_generator"
sys.path.insert(0, str(MODULE_DIR))

import generator as G  # noqa: E402
import vgen_lib as L  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260930)
    parser.add_argument("--output", type=Path, default=Path("generated_surface.tsv"))
    args = parser.parse_args()

    rows = L.load()
    synthetic, log = G.generate(rows, seed=args.seed, laafu=G.build_laafu(rows))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t", lineterminator="\n")
        writer.writerow(["record_id", "folio", "line", "surface", "symbolic_factor", "currier", "is_copy", "is_mutation"])
        for source, generated, decision in zip(rows, synthetic, log):
            writer.writerow([
                f"{source['raw_folio']}.{source['line']}:{source['pos']}",
                generated["folio"], generated["line"], generated["surface"],
                generated["mol"], generated["ab"], decision["is_copy"], decision["is_mut"],
            ])
    print(f"generated {len(synthetic)} rows -> {args.output}")


if __name__ == "__main__":
    main()

