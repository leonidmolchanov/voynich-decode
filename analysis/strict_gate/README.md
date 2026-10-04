# analysis/strict_gate/ — the strict 999-null gate (reference code)

Upstream, GPU-tier reference code for the strict promotion gate:
- `strict_oof_gate.py` — out-of-fold (OOF) gate over the leaf-held folds;
- `strict_null_gate.py` — null-threshold construction;
- `strict_matched_null.py` — the 999 matched-random null battery.

These need PyTorch + the leaf crops (HF dataset `voynich-decode-data`) + observer
weights (HF model `voynich-decode-models`) + Yale IIIF scans to run — they produce the
OOF predictions and the 999 null replicates.

**The GPU-free, offline reproduction of the gate's inferential claim** (observed OOF
accuracy beats all 999 nulls, empirical p = 0.001) is `scripts/verify_strict_gate.py`,
run against the frozen bundles in `data/strict/gates/`. Full two-tier instructions:
`docs/STRICT_GATE_REPRODUCTION.md`.
