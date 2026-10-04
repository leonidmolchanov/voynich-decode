# Reproducing the strict 100% coverage and its 999-null gate

The strict layer claims that each of the 23,859 cells receives a structural outcome
(strict-v82 = 23,859/23,859), and that the accepted additions are **not chance**:
each promotion wave's out-of-fold (OOF) accuracy beats **all 999 matched-random null
permutations** (Westfall-Young-style, empirical p = 0.001 floor). This document makes
that claim reproducible by colleagues in **two tiers** — one GPU-free, one full.

## Tier 1 — the inferential gate, OFFLINE, GPU-free (run this first)

The statistic that actually carries the "not chance" claim is recomputed from frozen,
shipped data — no PyTorch, no scans:

```bash
python3 scripts/verify_strict_gate.py
```

It reads `data/strict/gates/<model>/`:
- `oof_null_gate.json` — the observed OOF result (calls, correct, precision),
- `nulls/null_0000.json … null_0998.json` — the 999 matched-random null replicates,

and recomputes, per accepted model (and per observer arm): observed precision, the null
max/median, whether **observed beats all 999 nulls**, and the empirical
p = (1 + #{null ≥ observed}) / (1 + n_null). Reproduced result on the shipped bundles:

| model / arm | observed correct | precision | null max | beats all 999 | empirical p |
|---|---:|---:|---:|:--:|---:|
| leaf_clean_highres arm_a / arm_b | 8216 / 11524 | 0.9987 / 0.9978 | 3217 / 4242 | ✅ | 0.001 |
| strict_v2 arm_a / arm_b | 1994 / 2916 | 0.9990 / 0.9983 | 639 / 895 | ✅ | 0.001 |
| strict_v3 | 2222 | 0.9955 | 540 | ✅ | 0.001 |
| strict_v4 | 1820 | 0.9989 | 520 | ✅ | 0.001 |
| strict_v5 | 3528 | 0.9975 | 1420 | ✅ | 0.001 |
| strict_v6 | 1752 | 0.9977 | 500 | ✅ | 0.001 |

The matched-random null preserves the exact algorithm, OOF folds, and stratification
(hand/section/register/fold/factor-length/freq-band) and only rotates *which accepted
factor value* sits on *which cell within a stratum* — so a PASS rules out chance-level
performance, fold leakage, and multiple-comparison inflation across families
(Westfall-Young). What it does **not** by itself establish is that the 9-state/body
scheme carves a linguistically meaningful joint — see `NULL_MODELS_AND_CONTROLS.md`
(`analysis/shadow_of_null/`) for the honest limit; the gate is a within-framework
leakage/multiplicity control, read alongside that self-critical control.

## Tier 2 — the full CV pipeline (needs PyTorch + GPU)

Reproduces the UPSTREAM step that *produces* the OOF predictions the gate scores — the
blind leaf-held visual observers reading the glyphs off the Yale scans. Inputs are now
public:
- **Observer weights:** Hugging Face `LeonidMolchanov1987/voynich-decode-models`
  (`snapshot_download`, SHA-256 in the bundle's weight manifest).
- **Leaf crops / OOF training bundles:** Hugging Face dataset
  `LeonidMolchanov1987/voynich-decode-data`.
- **Page scans:** Beinecke MS 408, Yale (public domain) via IIIF (`scripts/fetch_yale_iiif.py`).
- **Gate / null / observer code (reference):** `analysis/strict_gate/`
  (`strict_oof_gate.py`, `strict_null_gate.py`, `strict_matched_null.py`) — the actual
  OOF-gate, null-construction, and matched-null code, with headers noting their inputs.

Pipeline: fetch scans (IIIF) → load observer weights (HF) → run leaf-held inference on
crops (HF) to regenerate the OOF prediction tape → feed it to the gate/null code →
obtain `oof_null_gate.json` + the 999 nulls → which Tier 1 then verifies. Leaf-held
split discipline (recto/verso/foldout of one physical leaf kept together) is documented
in `MANUSCRIPT_IDS_AND_SPLIT_AUDIT.md`.

## What this closes
A colleague can, **with no GPU**, reproduce the inferential claim that the strict
additions beat all 999 nulls (Tier 1), and, **with a GPU**, regenerate the OOF
predictions from public weights + crops + IIIF scans and re-run the gate end-to-end
(Tier 2). Honest boundary unchanged: 100% is **structural** coverage, not plaintext;
the gate controls chance/leakage/multiplicity, not semantic meaningfulness.
