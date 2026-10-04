# Reproducibility — reviewer runbook

This is the single, ordered checklist for an outside reviewer. Steps **A–D run
offline with NumPy alone — no GPU, no weights, a few minutes total**; step **E**
is the optional GPU re-run of the computer-vision pipeline from the public
weights. For the full dependency map ("what serves what") see
`FULL_REPRODUCTION.md`.

> **What is being verified.** The headline claim is **structural**: 23,859/23,859
> cells carry a concrete factor (100% *coverage*), that layer is reversible, and
> the manuscript's language-like statistics are reproduced by a meaning-free
> generator that beats a 999-sample matched-random null. This is **not** a
> translation, a plaintext, or a decipherment, and the hoax-vs-information-thin-
> cipher question is not settled by the text alone. See `LIMITATIONS.md`.

## Requirements

- Python 3.11 or newer;
- NumPy (`python -m pip install -r requirements.txt`);
- about 20 MB of free space (without the downloadable scans);
- steps A–D need no network, no GPU, and no model weights.

## Step 0 — one command (turnkey)

```bash
python -m pip install -r requirements.txt
python scripts/verify_all.py
```

This runs, and prints `OVERALL: PASS` only if all of them pass:

1. **release integrity** — every shipped file matches its SHA-256 in
   `PUBLIC_RELEASE_MANIFEST.json`, and no private/cache material is present;
2. **regression tests** — the `tests/` suite, which asserts the factorization is
   100%, the generator is byte-deterministic, every accepted strict gate beats all
   999 nulls, the analysis artifacts parse, and the controls are boilerplate-free;
3. **strict 999-null gate** — the offline recompute (same as step C);
4. **factorization summary** — 23,859 cells, 0 empty factors.

If you only have one minute, this is the check. Steps A–E below are the same
checks broken out, with the expected numbers and what each one proves.

## Step A — integrity and the 100% structural claim

```bash
python scripts/summarize_factorization.py      # -> 23859 rows, 0 missing factors, 100%
python scripts/verify_release.py                # -> PASS: N files, denominator 23859
python -m unittest discover -s tests -v         # -> OK
```

- Denominator: **23,859** unique `record_id` values (the immutable count in
  `data/reference/`). Empty `symbolic_factor` values: **0**.
- The full layer is `data/factorization/full_surface_factorization.tsv`; every row
  is `STRICT_ACCEPTED`. The strict-v82 lock
  (`data/strict/strict_anonymous_factor_v82.lock.json`) declares the same 100%.
- *Proves:* the structural description is complete and reversible, and the shipped
  bytes are exactly those that were measured.

## Step B — the generator (determinism + fit)

```bash
python scripts/run_generator.py --seed 20260930 --output generated_surface.tsv
```

The output has **23,859 rows + a header**, and the same seed yields a
byte-for-byte identical file on the same NumPy version. Then:

```bash
cd src/voynich_generator
python validate.py        # writes validation_results.json
python heldout.py         # writes ../../results/heldout_validation_results.json
```

- `validate.py` writes `src/voynich_generator/validation_results.json` (beside
  itself); compare it against the shipped reference
  `results/generator_validation_results.json`.
- `heldout.py` is the **validation of record**: fit on one half of the pages,
  generate over the unseen half. In-sample diagnostics are labelled as fit, not as
  held-out evidence.
- Stochastic null checks can vary slightly between NumPy versions; the *direction*
  and *order of magnitude* of the effects must be preserved.
- *Proves:* the generator is a fixed, reproducible mechanism, and its agreement
  with the manuscript survives on pages it never saw.

## Step C — the strict 999-null significance gate (offline)

```bash
python scripts/verify_strict_gate.py            # -> OVERALL: PASS
```

Recomputes, with the standard library only, the Westfall–Young max-T gate (a
permutation test with multiple-testing control: the observed statistic is compared
to the **maximum** statistic over the matched-random nulls) from the shipped
out-of-fold (OOF — scored on held-out folds) bundles in
`data/strict/gates/<model>/` (each: `oof_null_gate.json` + 999
`nulls/null_####.json`). Every accepted arm must beat **all 999** matched-random
nulls, giving the empirical floor p = (1+0)/(1+999) = **0.001** (strict `>`; ties
fail). Narrative and the GPU upstream: `STRICT_GATE_REPRODUCTION.md`.

- *Proves:* the acceptance decisions are statistically significant against a fair
  null, reproducibly and without a GPU.

## Step D — null models and real-language controls

The adversarial battery that keeps the conclusion honest. Each suite ships its
code, its result JSON, and an English `NOTES_*.md`; all JSONs were regenerated on
the shipped strict-v82 layer. Narrative + verdicts: `NULL_MODELS_AND_CONTROLS.md`.

Run each suite **from its own directory** (some scripts write their result JSON
beside themselves with a bare filename). `*_common.py` files are shared libraries,
not entry points.

```bash
(cd analysis/shadow_of_null     && python build_shadow_of_null_metrics.py)              # -> metrics_shadow_of_null.json
(cd analysis/montemurro         && python run_basic.py && python run_decisive.py && python run_register.py)  # -> *_results.json
(cd analysis/linguistic_laws    && python ll_longrange.py)                              # -> longrange_results.json (also ll_nonstationarity.py / ll_wordlevel.py / ll_menzerath_brevity.py)
(cd analysis/payload_mdl        && python floor_ceiling.py && python control2.py)       # run order matters: control2.py reads floor_ceiling.json
(cd analysis/state_independence && python analyze_state_independence.py)                # -> results.json (+ report.txt)
(cd analysis/word_frequency     && python wf_run.py)                                    # -> wf_results.json
```

Each command regenerates that suite's shipped result JSON. The verdict for each
suite is written up in `NULL_MODELS_AND_CONTROLS.md` and in the suite's
`NOTES_*.md` (for `state_independence`, the narrative is `report.txt`);
`analysis/controls/` holds the public-domain English/Latin positive controls.

- *Proves:* the "language-like" signatures are reproduced by a meaning-free
  process and sit at the self-generation floor — the basis for the sufficiency
  (not "proven hoax") claim.

## Step E — optional: full CV pipeline (GPU, external artifacts)

Only needed to re-run the computer-vision observers end to end. Pulls the public
weights and crops and (optionally) the Yale scans:

```bash
python -m pip install -U huggingface_hub        # only needed for this step
python scripts/fetch_weights.py                 # -> ./models/ (public repo: LeonidMolchanov1987/voynich-decode-models)
python scripts/fetch_weights.py --dataset        # also the crops/training dataset (public)
python scripts/fetch_yale_iiif.py --folio 78r --output downloaded_scans/f78r.jpg
```

- Weights: `LeonidMolchanov1987/voynich-decode-models`; datasets:
  `LeonidMolchanov1987/voynich-decode-data`; scans: Beinecke MS 408 (Public
  Domain) via IIIF. Full steps: `STRICT_GATE_REPRODUCTION.md` (Tier 2) and
  `FULL_REPRODUCTION.md`.
- *Note:* the headline result (steps A–D) does **not** depend on this step; the CV
  stage produced the candidate observations that the offline gate then judged.
