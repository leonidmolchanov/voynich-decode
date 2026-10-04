#!/usr/bin/env python3
"""Offline reproduction of the strict 999-matched-null gates — NO GPU, NO scans.

The CV observers that PRODUCE the out-of-fold (OOF) predictions need PyTorch + the
Yale scans/crops (weights + crops are on Hugging Face; see docs/STRICT_GATE_REPRODUCTION.md).
But the INFERENTIAL step — "the observed OOF accuracy beats all 999 matched-random
null permutations, so the accepted strict additions are not chance" — is fully
reproducible here from the frozen `data/strict/gates/<model>/` bundles (the observed
OOF result + 999 null replicate counts). This script recomputes, per accepted model:

  observed precision, null max/median, "observed beats all 999 nulls", and the
  Westfall-Young-style empirical p = (1 + #{null >= observed}) / (1 + n_null)

and checks it against the frozen gate verdict. Pure standard library.

    python3 scripts/verify_strict_gate.py
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "data" / "strict" / "gates"


def arm_counts(gate):
    """Return list of (arm_name, observed_calls, observed_correct, frozen_null_max, frozen_beats)."""
    if "arms" in gate:
        out = []
        for name, a in gate["arms"].items():
            out.append((name, a["observed"]["calls"], a["observed"]["correct"],
                        a.get("null_max_correct"), a["checks"].get("beats_all_999_nulls")))
        return out
    o = gate["observed"]
    frozen_beats = gate.get("checks", {}).get("observed_exceeds_all_999_null")
    return [("(single)", o["calls"], o["correct"], gate.get("null_max_correct"), frozen_beats)]


def null_correct(nj, arm):
    return nj["arms"][arm]["correct"] if arm != "(single)" and "arms" in nj else nj["correct"]


def main() -> int:
    if not GATES.is_dir():
        print("no data/strict/gates/ — nothing to verify"); return 1
    models = sorted(p for p in GATES.iterdir() if p.is_dir())
    all_pass = True
    print(f"{'model/arm':52} {'obs_corr':>9} {'prec':>7} {'null_max':>8} {'beats999':>8} {'emp_p':>7}")
    for m in models:
        gate = json.loads((m / "oof_null_gate.json").read_text())
        nulls = [json.loads(Path(f).read_text()) for f in sorted(glob.glob(str(m / "nulls" / "null_*.json")))]
        n = len(nulls)
        for arm, calls, obs, frozen_max, frozen_beats in arm_counts(gate):
            try:
                nc = [null_correct(x, arm) for x in nulls]
            except (KeyError, TypeError):
                print(f"  {m.name}/{arm}: null schema mismatch"); all_pass = False; continue
            nmax = max(nc) if nc else None
            beats = all(obs > c for c in nc) and n > 0
            ge = sum(1 for c in nc if c >= obs)
            emp_p = (1 + ge) / (1 + n) if n else float("nan")
            prec = obs / calls if calls else float("nan")
            # consistency vs frozen record
            ok = beats and (frozen_beats in (True, None)) and (frozen_max is None or nmax == frozen_max)
            all_pass = all_pass and ok
            flag = "" if ok else "  <-- MISMATCH"
            print(f"{m.name+'/'+arm:52} {obs:>9} {prec:>7.4f} {nmax:>8} {str(beats):>8} {emp_p:>7.4f}{flag}")
    print()
    print("OVERALL:", "PASS ✅ — every accepted gate reproduces offline (observed beats all 999 nulls, p=0.001 floor)"
          if all_pass else "FAIL ❌ — see mismatches above")
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
