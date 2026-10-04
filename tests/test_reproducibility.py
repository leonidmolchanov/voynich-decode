"""Reproducibility regression tests — fast, offline, NumPy only.

Guards the headline claims so a change that breaks them fails CI loudly:
  - factorization is 100% (23,859 cells, all STRICT_ACCEPTED, no empty factor)
  - the strict-v82 lock asserts 100% coverage over 23,859
  - the generator is byte-deterministic for a fixed seed
  - every accepted strict gate still beats all 999 matched-random nulls (offline)
  - the analysis battery's result artifacts are present and parse
  - the shipped natural-language controls carry no Project Gutenberg boilerplate
Run:  python3 -B -m unittest discover -s tests
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


class Reproducibility(unittest.TestCase):
    def test_factorization_is_100pct(self):
        with (ROOT / "data/factorization/full_surface_factorization.tsv").open(encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh, delimiter="\t"))
        self.assertEqual(len(rows), 23859)
        self.assertTrue(all(r["symbolic_factor"].strip() for r in rows), "empty factor present")
        self.assertEqual({r["assignment_tier"] for r in rows}, {"STRICT_ACCEPTED"})

    def test_v82_lock_declares_100pct(self):
        d = json.loads((ROOT / "data/strict/strict_anonymous_factor_v82.lock.json").read_text())
        self.assertEqual(d["denominator"], 23859)
        self.assertEqual(d["accepted_core_rows"], 23859)
        self.assertEqual(d["coverage_percent"], 100.0)

    def test_generator_is_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            a, b = Path(td) / "a.tsv", Path(td) / "b.tsv"
            for out in (a, b):
                r = subprocess.run([PY, "scripts/run_generator.py", "--seed", "20260930", "--output", str(out)],
                                   cwd=str(ROOT), capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(hashlib.sha256(a.read_bytes()).hexdigest(),
                             hashlib.sha256(b.read_bytes()).hexdigest())
            with a.open() as fh:
                self.assertEqual(sum(1 for _ in fh) - 1, 23859)

    def test_strict_gate_beats_all_999_nulls(self):
        r = subprocess.run([PY, "scripts/verify_strict_gate.py"], cwd=str(ROOT),
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, "verify_strict_gate failed:\n" + r.stdout + r.stderr)
        self.assertIn("OVERALL: PASS", r.stdout)

    def test_analysis_result_artifacts_present(self):
        for rel in [
            "analysis/payload_mdl/floor_ceiling.json",
            "analysis/payload_mdl/control2.json",
            "analysis/shadow_of_null/metrics_shadow_of_null.json",
            "analysis/montemurro/basic_results.json",
            "analysis/montemurro/decisive_results.json",
            "analysis/linguistic_laws/longrange_results.json",
            "analysis/state_independence/results.json",
            "analysis/word_frequency/wf_results.json",
            "results/heldout_validation_results.json",
        ]:
            p = ROOT / rel
            self.assertTrue(p.exists() and p.stat().st_size > 0, f"missing/empty: {rel}")
            json.loads(p.read_text())  # must parse

    def test_controls_are_clean_public_domain(self):
        for f in ("english_jqadams.txt", "latin_caesar_218.txt", "latin_caesar_18837.txt"):
            txt = (ROOT / "analysis/controls" / f).read_text(encoding="utf-8", errors="ignore")
            self.assertNotIn("Project Gutenberg", txt, f"{f} still contains Project Gutenberg boilerplate")


if __name__ == "__main__":
    unittest.main()
