# Full reproduction and dependency map

How everything was obtained, what depends on what, what serves what, and how to
reproduce it — from data to result. Honest framing: what is reconstructed is the
**writing mechanism**, not a message; no plaintext/translation is claimed.

Related documents: `METHODS.md`, `GENERATOR_SPEC.md`, `DATA_PROVENANCE.md`,
`REPRODUCIBILITY.md`, `LIMITATIONS.md`, `AI_USE.md`, `UNIVERSAL_LADDER.md`.

External resources (not stored in this repo):
- **Model weights:** HF `LeonidMolchanov1987/voynich-decode-models`
- **Working datasets (crops/training):** HF dataset `LeonidMolchanov1987/voynich-decode-data`
- **Scans:** Beinecke MS 408, Yale (Public Domain) — IIIF `collections.library.yale.edu/manifests/2002046`
- **Archive/DOI:** Zenodo `10.5281/zenodo.23140803`

---

## 1. Dependencies

### 1.1 Software
| layer | dependencies |
|---|---|
| factorization + generator + Montemurro | **Python ≥3.11, NumPy** (only) |
| CV observers (weights) | **PyTorch** (+ CUDA for training/inference), partly scikit-learn (rankers) |
| downloading weights/datasets | `huggingface_hub` |
| scans | IIIF (HTTP) |

The core result (the factorization numbers, the generator) **reproduces offline
with NumPy alone, without a GPU and without the weights** (see §4, Track A).

### 1.2 Data (provenance — see `DATA_PROVENANCE.md`; licenses — `DATASET_GENERATION.md`)
| data | role | source / license |
|---|---|---|
| Yale MS 408 scans | pixel input for CV | Yale, **Public Domain**, IIIF |
| Z–L EVA transcription (+ our overlay) | cell labels | voynich.nu, © Zandbergen (attribution) |
| voynichese coordinates | cell/word boxes | voynichese.com |
| our crops / OOF sets | CV train/eval | **ours**, PD-derived → HF dataset |
| DECODE/DECRYPT ciphers | auxiliary benchmark (an unsuccessful solver attempt) | CC BY 4.0 |
| Pliny and other corpora | comparison | PD text |

### 1.3 Model lineage (registry — in the HF model repo `voynich-decode-models`)
```
leaf_clean_highres_shadow_gate_v1   (root, clean init)
├── strict_v2_broad_shadow_gate_v1
├── strict_v3_consensus_gate_v1
│    └── strict_v4_direct_factor_gate_v1
│         ├── strict_v5_short_factor_gate_v1
│         └── strict_v6_continued_direct_gate_v1
strict_v15_image_candidate_ranker_v1   (independent, image-only)
baselines: x10u_segmental / x10u_metric / leaf_clean_segmental   (independent, not strict)
```

---

## 2. What serves what (role map)

| component | purpose |
|---|---|
| Yale scans | source pixels of the glyphs |
| transcription + `data/corrections/` | cell labels / ground truth and their corrections |
| CV observers (weights on HF) | "read" disputed glyphs and confirm cells for strict |
| null gates (999 matched) | show the confirmations are not chance |
| `data/factorization/` + `data/strict/` | the result itself — the structural "writing machine" (anonymous factor) |
| `src/voynich_generator/` | a sufficient meaning-free generator reproducing the statistics |
| `src/montemurro/` | test of the long-range "meaning" signal (excess MI) |
| `scripts/*` | summary, release verification, running the generator, fetching scans |
| HF dataset (crops) | inputs for training/inference of the observers |

---

## 3. How things are generated

- **Datasets** (crops from PD scans + labels + coordinates → leaf-held split): detailed in `DATASET_GENERATION.md`.
- **Text generator** (emission tables + a word-template automaton + copy/mutate/reset, fit per Currier hand A/B): `GENERATOR_SPEC.md`.
- **Strict factorization** (blind observers → OOF/999-null → promotion by ≥2 witnesses): `METHODS.md`.

---

## 4. Full reproduction

### Track A — the text layer (offline, NumPy only; NO weights, NO GPU)
```bash
cd PUBLIC_RELEASE
python -m pip install -r requirements.txt
python scripts/summarize_factorization.py          # expect: 23,859 rows, 0 empty factors
python scripts/run_generator.py --seed 20260930 --output generated_surface.tsv   # 23,859 rows
cd src/voynich_generator && python validate.py      # REAL vs SYNTH, compare with results/generator_validation_results.json
cd ../.. && python -m unittest discover -s tests
```
The same seed → **byte-for-byte** identical output. Metric references are in
`results/`.

### Track B — the visual strict pipeline (needs scans + weights + GPU/PyTorch)
```bash
# 1) scans (Public Domain, via IIIF)
python scripts/fetch_yale_iiif.py --folio 78r --output downloaded_scans/f78r.jpg
# 2) observer weights
hf download LeonidMolchanov1987/voynich-decode-models --local-dir models
# 3) working datasets (crops/OOF)
hf download --repo-type dataset LeonidMolchanov1987/voynich-decode-data --local-dir data_work
#    tar xf data_work/*.tar
# 4) observer inference/gates — per-model runner / *_oof_gate / *_matched_null (PyTorch, CUDA)
```
This track reproduces the *visual confirmation* of cells. Its frozen results
(OOF/999-null gate JSON + hash locks) can also simply be **verified** as
artifacts, without retraining: see `results/` (strict-v82 release/postpublish/completion
audits) and `results/null_test/`.

---

## 5. Integrity check
- Weights: SHA-256 in the HF repo cards `voynich-decode-models` (per-model `MANIFEST.sha256`).
- Scans: SHA-256 in `metadata/folio_inventory.tsv` (+ `OFFICIAL_SCAN_SOURCE_AUDIT.md`).
- Factorization/release: `scripts/verify_release.py` against `PUBLIC_RELEASE_MANIFEST.json`;
  `scripts/summarize_factorization.py` → 23,859 cells, strict-v82, 0 empty.
- Strict coverage: `data/strict/strict_anonymous_factor_v82.lock.json` (100%, 23,859/23,859)
  + audits in `results/` (release, postpublish, independent completion 26/26).

## 6. Boundary of the claim
A sufficient mechanism is reconstructed and reproducible (strict factorization +
a sufficient generator — not THE unique historical device). **The message is not
read**; hoax vs. a verbose cipher is
undecidable from the text (`LIMITATIONS.md`). AI/ML is a tool (CV over scans +
ranking), not the author of the conclusion (`AI_USE.md`).
