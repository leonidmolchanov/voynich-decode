#!/usr/bin/env python3
"""One-command offline verification of the headline claims — NumPy only, no GPU.

Runs the integrity check, the regression test-suite (which asserts factorization
100%, generator determinism, the strict 999-null gate, artifact presence, and
clean controls), and the strict-gate recompute, then prints OVERALL PASS/FAIL.

    python3 scripts/verify_all.py

This is the turnkey check a reviewer runs first. For the step-by-step runbook and
what each step proves, see docs/REPRODUCIBILITY.md; for the full dependency map
and the GPU (Tier 2) path, docs/FULL_REPRODUCTION.md.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

STEPS = [
    ("release integrity (hashes + no forbidden material)",
     [PY, "scripts/verify_release.py"], "PASS:"),
    ("regression tests (factorization 100%, generator determinism, strict gate, controls)",
     [PY, "-B", "-m", "unittest", "discover", "-s", "tests"], "OK"),
    ("strict 999-null gate recompute (offline)",
     [PY, "scripts/verify_strict_gate.py"], "OVERALL: PASS"),
    ("factorization summary (23859 cells, 0 empty)",
     [PY, "scripts/summarize_factorization.py"], '"missing_symbolic_factors": 0'),
]


def main() -> int:
    results = []
    for name, cmd, needle in STEPS:
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        ok = r.returncode == 0 and needle in (r.stdout + r.stderr)
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        if not ok:
            tail = (r.stdout + r.stderr).strip().splitlines()[-3:]
            print("        " + " | ".join(tail))
        results.append(ok)
    allok = all(results)
    print("\nOVERALL:",
          "PASS ✅ — headline claims reproduce offline (NumPy only, no GPU)." if allok
          else "FAIL ❌ — see the failing step(s) above.")
    print("Next: generator stats  -> src/voynich_generator/validate.py + heldout.py;")
    print("      null battery + controls -> analysis/ (see docs/NULL_MODELS_AND_CONTROLS.md);")
    print("      full CV (GPU)    -> docs/STRICT_GATE_REPRODUCTION.md (Tier 2).")
    return 0 if allok else 1


if __name__ == "__main__":
    raise SystemExit(main())
