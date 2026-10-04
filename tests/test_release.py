from __future__ import annotations

import csv
import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR_DIR = ROOT / "src" / "voynich_generator"
sys.path.insert(0, str(GENERATOR_DIR))


class ReleaseTests(unittest.TestCase):
    def test_full_factorization_matches_denominator(self):
        with (ROOT / "data/factorization/full_surface_factorization.tsv").open(encoding="utf-8", newline="") as fh:
            factor = list(csv.DictReader(fh, delimiter="\t"))
        with (ROOT / "data/reference/aligned_cell_denominator_v1.tsv").open(encoding="utf-8", newline="") as fh:
            denominator = list(csv.DictReader(fh, delimiter="\t"))
        self.assertEqual(len(factor), 23859)
        self.assertEqual({row["record_id"] for row in factor}, {row["record_id"] for row in denominator})
        self.assertTrue(all(row["symbolic_factor"].strip() for row in factor))

    def test_generator_loads_complete_layout(self):
        library = importlib.import_module("vgen_lib")
        rows = library.load()
        self.assertEqual(len(rows), 23859)
        self.assertEqual({row["ab"] for row in rows}, {"A", "B"})

    def test_no_private_or_cache_material(self):
        # Genuinely-must-not-ship material. __pycache__/.pyc/.DS_Store are transient
        # build/OS artifacts: they are gitignored, never part of the shipped archive,
        # and are created the moment any script runs — so they must not fail the suite.
        forbidden = {"PRIVATE_RECORDS", ".idea", "web_cache"}
        hits = [str(path) for path in ROOT.rglob("*")
                if any(part in forbidden for part in path.parts)]
        self.assertEqual(hits, [], f"forbidden material shipped in release: {hits}")


if __name__ == "__main__":
    unittest.main()
