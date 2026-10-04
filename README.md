# Voynich Manuscript (Beinecke MS 408) — a structural investigation

Public repository: https://github.com/leonidmolchanov/voynich-decode
Archived release (DOI): [`10.5281/zenodo.23140803`](https://doi.org/10.5281/zenodo.23140803) · version 0.2.0 · dual MIT / CC BY 4.0

> **In one line:** we do not claim to *read* the Voynich Manuscript. We give a
> complete, reversible **structural** description of its text and show that its
> famous "language-like" behaviour can be **reproduced by a simple meaning-free
> process** — and we ship the data, code, and a one-command check so anyone can
> verify every number themselves.

This repository contains only materials that can be verified and shown openly:
no caches, checkpoints, training logs, or private records. Programming,
statistics, and machine learning are used here as tools for testing hypotheses —
not as a substitute for historical expertise, and not as the author of any
conclusion.

---

## What this is (TL;DR)

A full, reversible **structural** description of the manuscript's text: every one
of the **23,859** script cells is factored by a deterministic, zero-error machine
(strict-v82 = 23,859/23,859 = **100% structural coverage**). The text's
language-like statistics — word structure, local repetition, section-scale drift,
the Montemurro-style "meaning" signal — are then **reproduced by a compact,
meaning-free generator** that passes a 999-sample matched-random null gate
(empirical p = 0.001).

**What this is NOT.** This is **not** a translation, a plaintext, or a
decipherment, and "100%" is coverage of a chosen structural description — not of
meaning. The generator is **a sufficient mechanism, not THE unique historical
device**, and the evidence cannot settle **hoax vs. an information-thin cipher**
from the text alone. The honest boundary is in `docs/LIMITATIONS.md`.

---

## The idea — how we turned "decipherment" into a testable question

The Voynich Manuscript is an early-15th-century codex in an unknown script that
has resisted a century of attempts to read it. Proposed "solutions" appear
regularly and almost always fail for the same reason: they **overfit** — a scheme
is tuned until a few lines look meaningful, but it does not generalise and cannot
be reproduced by anyone else. Over-claiming is the single most common reason such
work is rejected.

So we deliberately **did not** try to produce a reading. Instead we split the
famous question "what does it say?" into two questions that can actually be
**measured and falsified**:

1. **Can the whole script surface be described by a compact, reversible machine?**
   We build a structural *factorization*: each visible cell is decomposed into an
   anonymous internal form by a deterministic tokenizer + state table, with a
   round-trip check (reconstruct the original from the factor). The answer is
   yes — **strict-v82 covers 23,859/23,859 cells with zero round-trip errors.**
   This is a precise, checkable statement about *form*, and it says nothing about
   meaning.

2. **Are the manuscript's "language-like" regularities evidence of a message, or
   can a mindless process fake them?** Voynichese has real, striking statistics
   (word-template structure, a skewed ending channel, strong local word reuse,
   page/section vocabulary drift, even a Montemurro-style "semantic" clustering).
   We build a **meaning-free generator** — template choice + local copy-with-one-
   edit + line/page resets, with **no key, no plaintext, no message** — and test
   whether it reproduces those statistics. It does, and it **beats a 999-sample
   matched-random null** and matches real natural-language controls (English,
   Latin) under the identical measurements.

### The honesty principle (the rule we never break)

- **"100%" means structural coverage, never translation, meaning, or a solution.**
- We exhibit **a sufficient** meaning-free mechanism, **not THE** unique historical
  device — many processes could produce the same statistics
  (*observational equivalence*).
- From the internal statistics **alone**, an elaborate hoax and an information-thin
  verbose cipher are **indistinguishable**; we do **not** declare which. Settling
  that would need external evidence (a crib, a key, a corroborating document).
- Nothing rests on trusting a particular model or author: every claim ships with
  the data, the code, the frozen splits, and a one-command verifier. AI was an
  amplifier of speed and scale, not the author of the conclusion (`docs/AI_USE.md`).

Full method in `docs/METHODS.md`; the exact limits in `docs/LIMITATIONS.md`; what
was known before and our precise contribution in `docs/PRIOR_WORK.md`.

### What "100% coverage" means, precisely

In the publication model each of the 23,859 cells receives a structural outcome:
a confirmed factor, or a predeclared abstention for a physically unresolvable
sign. In strict-v82 that safety valve is **allowed but unused** — every cell
carries a concrete factor and none abstain. The historical release **v21**
(22,106/23,859 ≈ 92.65%) is retained as a verifiable step of the audit line. The
full layer is `data/factorization/full_surface_factorization.tsv`.

---

## Quick check (reviewer runbook)

One command verifies every headline claim **offline** — Python 3.11+, NumPy only,
no GPU, no weights, a few minutes:

```bash
python -m pip install -r requirements.txt
python scripts/verify_all.py          # -> OVERALL: PASS
```

It runs the integrity check, the regression tests (factorization 100%, generator
determinism, the strict 999-null gate, clean controls), the offline strict-gate
recompute, and the factorization summary. The individual steps, their expected
numbers, and what each one proves are the ordered **A–E runbook** in
**`docs/REPRODUCIBILITY.md`**; the strict gate and the null/controls battery are
detailed in `docs/STRICT_GATE_REPRODUCTION.md` and
`docs/NULL_MODELS_AND_CONTROLS.md`.

To run the generator on its own:

```bash
python scripts/run_generator.py --seed 20260930 --output generated_surface.tsv
```

---

## Repository layout

- `data/factorization/` — the full structural layer of 23,859 cells;
- `data/strict/` — the frozen strict releases, locks, audits, and the 999-null
  gate bundles (`data/strict/gates/`);
- `data/transcriptions/` — the correction overlay and a pointer to the source transcription;
- `data/corrections/` — the register of corrections and disputed decisions;
- `data/reference/` — the immutable denominator (23,859);
- `src/voynich_generator/` — the compact, reproducible meaning-free generator;
- `scripts/` — verification (`verify_all`, `verify_release`, `verify_strict_gate`),
  factorization summary, generator runner, weight/scan fetchers, manifest builder;
- `tests/` — composition and reproducibility checks;
- `analysis/` — null models, real-language (English/Latin) positive controls, and
  adversarial tests of every "language-like" signature;
- `metadata/` — image source, folio inventory, and Currier A/B markup;
- `results/` — audits and saved control-run results;
- `docs/` — the full written record (index below);
- `CITATION.cff`, `LICENSE`, `CHANGELOG.md`, `requirements.txt`,
  `PUBLIC_RELEASE_MANIFEST.json` — citation, license, history, dependencies, checksums.

## Documentation (`docs/`)

**Start here — reproduction**
- `REPRODUCIBILITY.md` — the step-by-step reviewer runbook (A–E);
- `FULL_REPRODUCTION.md` — the full dependency map, "what serves what", end to end;
- `STRICT_GATE_REPRODUCTION.md` — reproduce the strict 100% gate (offline + GPU);
- `NULL_MODELS_AND_CONTROLS.md` — the null/controls battery and its verdicts.

**Method and definitions**
- `METHODS.md` — how the factorization was built and why v82 is the authority;
- `DATA_ABSTRACTION.md` — the cell, the machine tape, and the testable question of meaning;
- `GENERATOR_SPEC.md` — the meaning-free generator spec and honest recovery bounds;
- `UNIVERSAL_LADDER.md` — template coverage of internal forms (a diagnostic, not strict coverage).

**Data, provenance, rights**
- `DATA_PROVENANCE.md` — where the data comes from;
- `DATASET_GENERATION.md` — how the datasets are built (ours + third-party) and the licenses;
- `OFFICIAL_SCAN_SOURCE_AUDIT.md` — audit of the Yale/Beinecke IIIF scan source;
- `MANUSCRIPT_IDS_AND_SPLIT_AUDIT.md` — numbering reference and the leaf-held split audit;
- `TRANSCRIPTION_CORRECTIONS.md` — the transcription-correction register.

**Honesty, boundaries, context**
- `LIMITATIONS.md` — what the result does and does not establish;
- `PRIOR_WORK.md` — prior scientific priority vs. this project's contribution;
- `AI_USE.md` — the role of AI/ML and the decisions that stayed with the human.

---

## Images

Full scans are not included. `metadata/folio_inventory.tsv` holds the IIIF links
and SHA-256 values, and `scripts/fetch_yale_iiif.py` downloads only the requested
folio. Rights and terms for the images are governed by Yale University Library;
the Beinecke MS 408 scans are Public Domain.

## Full reproduction and external resources

The full dependency map, model lineage, "what serves what", and end-to-end
reproduction (data → models → gates → generator → verification) are in
**`docs/FULL_REPRODUCTION.md`**. Data provenance, licenses, and the dataset-build
pipeline are in **`docs/DATASET_GENERATION.md`**.

The core result (the factorization numbers + the generator) reproduces offline
with NumPy alone — no weights, no GPU. Only the optional computer-vision re-run
needs the heavy artifacts, which are stored separately (not in git):

- **CV-observer weights:** Hugging Face — `LeonidMolchanov1987/voynich-decode-models` (public)
- **Working datasets (crops/training):** Hugging Face dataset — `LeonidMolchanov1987/voynich-decode-data` (public)
- **Scans:** Beinecke MS 408, Yale (Public Domain) — via IIIF, `scripts/fetch_yale_iiif.py`
- **Archive / DOI:** Zenodo — `10.5281/zenodo.23140803`

## How to cite and license

Please cite the archived version (Zenodo DOI) and the release version — the
machine-readable record is in `CITATION.cff`:

- **DOI:** `10.5281/zenodo.23140803` (version 0.2.0)
- **Author:** Leonid Olegovich Molchanov

**License (dual — see `LICENSE`):** source code in `src/`, `scripts/`, `tests/` is
**MIT**; original text, annotations, and project-produced tables are **CC BY 4.0**.
Third-party scans, transcriptions, and fonts keep their own terms
(`docs/DATA_PROVENANCE.md`); the Yale/Beinecke scans are Public Domain via IIIF.

## Integrity

Checksums of all files are recorded in `PUBLIC_RELEASE_MANIFEST.json` and verified
by `scripts/verify_release.py`. The manifest is rebuilt (`scripts/build_manifest.py`)
after any replacement of data or text.
