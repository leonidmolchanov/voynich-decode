# Montemurro–Zanette "genuine message" signal vs a fair drift-generator null

Date 2026-09-30. READ-ONLY on source data; all writes under this directory.
No meaning/plaintext claims. Numbers below are from the scripts in this folder
(`mz_common.py`, `run_basic.py`, `generators.py`, `run_decisive.py`,
`run_register.py`, `probe_map.py`) with fixed seed 20260930; raw results in the
`*_results.json` / `*.json` files.

## The question
Montemurro & Zanette (2013, PLOS ONE) showed that Voynich words carry information
about *where* in the text they occur (they cluster by section/part) at a level like
real languages and far above a word-order shuffle — read as "supports a genuine
message." Timm & Schinner's self-citation critique: a MEANING-FREE generator whose
internal state DRIFTS along the text (copy + mutate recent words) also makes words
cluster by region. **Does the Montemurro signal survive a fair, meaning-free
drift-generator null, or is it generator-reproducible?**

## Method (reconstructed M&Z measure)
Partition the text (manuscript reading order) into P parts. For each word type `w`
with part-distribution `q_{w,p}=n_{w,p}/n_w` and part-size weights `g_p=N_p/N`, the
information the word's location carries is the KL divergence `D_w=Σ_p q log2(q/g)`;
aggregated over words by frequency this is exactly the mutual information
`I(W;Part)`. MI has a positive finite-sampling bias (a random scatter of a finite
corpus still gives MI>0), so the reported statistic is the **excess** above each
corpus's OWN word-order-shuffle floor:

    Excess(C) = I(W;Part)_observed − mean_over_shuffles I(W;Part)_shuffled

Comparing each corpus to its own shuffle floor is essential for fairness: corpora
with different vocabularies / frequency spectra have different MI bias, and the own-
shuffle correction removes it. Generators produce a positional stream; the real
manuscript's part labels (section / Currier A-B / positional blocks) are **overlaid
by position** — no generator ever sees a section label.

- Units: **SURFACE words** (M&Z's units) AND the **molecule layer**
  (`<body glyphs>=>S<state>`, the shadow re-encoding).
- Partitions: 6 semantic sections (Herbal/Astro/Bio/Cosmo/Pharma/Recipes), Currier
  A/B (2-way), and equal-length word blocks P∈{2,5,6,10,20}.
- Section + A/B per folio come from the project's own structural markup
  (`metadata/currier_ab_map.md`, 225 folio-sides in
  manuscript order), joined to the 23,859-token factorization TSV. Base-folio
  resolution (strip panel digits) gives a **100% token join**. Token counts:
  Herbal 9117, Bio 6129, Recipes 5706, Pharma 2042, Cosmo 666, **Astro 199**
  (Astro is tiny — flagged); A 9563 / B 14296.

## Task 1 — basic Montemurro result REPLICATES (real ≫ word-order shuffle)
`basic_results.json`. Real word-section MI sits far above the shuffle floor at every
partition and on both layers:

| unit | partition | obs MI | shuffle floor | **excess** | z vs floor |
|---|---|---:|---:|---:|---:|
| surface | sections (6) | 0.742 | 0.410±0.003 | **0.333** | 105.7 |
| surface | Currier A/B | 0.394 | 0.159±0.002 | **0.235** | 126.6 |
| surface | blocks 6 | 0.799 | 0.520±0.003 | 0.279 | 100.3 |
| surface | blocks 20 | 1.447 | 1.120±0.004 | 0.327 | 94.5 |
| molecule | sections (6) | 0.520 | 0.247±0.003 | **0.273** | 102.1 |
| molecule | Currier A/B | 0.289 | 0.095±0.002 | **0.194** | 130.2 |
| molecule | blocks 6 | 0.543 | 0.312±0.002 | 0.231 | 103.8 |
| molecule | blocks 20 | 0.977 | 0.681±0.003 | 0.296 | 105.1 |

**Verdict T1: replicates decisively (z ≈ 65–130, all P; surface and molecule).**
Word-section clustering in the Voynich is real and large — the shuffle trivially
destroys it, exactly as M&Z reported. (This was never in doubt; it only confirms
clustering exists. It says nothing yet about *meaning*.)

## Task 2 — the generators + fidelity (the calibration crux)
Two floor generators (no drift, section-blind, **stationary**) and one principled
drift generator; all matched to N=23,859 tokens.

- **iid_bag**: each token i.i.d. from the real unigram.
- **markov1_tok**: 1st-order Markov over token types, global transitions.
- **self_citation** (Timm–Schinner style): copy a string from a recency window over
  already-emitted tokens (+ single-glyph mutation), with rare glyph-level innovation
  (1st-order glyph Markov fit to the real glyph-bigram stats). **Drift/localization
  emerges from copying** — a string appearing/mutated near position t can only be
  copied within ~window of t, and copy-of-copy chains extend that — NOT from any
  section label. Knobs: `p_new` (innovation → type count/TTR/drift strength),
  `p_mut` (mutation → exact-repeat rate / near-duplicate vocabulary), `window`
  (memory → SCALE of drift).

**Calibration is deliberately to MECHANICAL stats only (TTR, hapax, repeat-rate,
Zipf slope) — never to section-MI.** Best fits (grid search):

| unit | params | V | TTR | hapax | repeat | Zipf | H1 |
|---|---|---:|---:|---:|---:|---:|---:|
| surface REAL | — | 4054 | 0.170 | **0.642** | 0.0111 | −1.05 | 9.64 |
| surface self-cite | p_new .3, p_mut .2, win 250 | 4556 | 0.191 | 0.488 | 0.0124 | −0.95 | 9.89 |
| molecule REAL | — | 2432 | 0.102 | **0.635** | 0.0232 | −1.19 | 8.16 |
| molecule self-cite | p_new .3, p_mut .1, win 100 | 2646 | 0.111 | 0.405 | 0.0265 | −1.17 | 8.95 |

Fidelity is good on TTR/repeat/Zipf. **Honest fidelity limit:** the self-citation
model **undershoots the hapax fraction** (0.49 vs 0.64 surface; 0.41 vs 0.64
molecule). Real Voynich has an unusually high proportion of once-only word types
that simple copy+mutate under-produces at matched TTR (raising mutation to fix hapax
overshoots TTR). This means the generator is, if anything, *less* locally
idiosyncratic than the real text — it does not inflate the clustering test in the
generator's favour. The floor generators are also honestly imperfect: iid/markov
undershoot TTR (0.127) and hapax (~0.38, V≈3040) because they draw from a fixed bag
— which is exactly why a string-level innovator is needed for the drift model.

## Task 3 — the DECISIVE comparison
`decisive_results.json`. 60 generator reps each; every rep bias-corrected against its
own shuffle floor; z and p compare REAL excess to the generator distribution
(p = fraction of gen reps with excess ≥ real; floor 1/61 ≈ 0.016).

### Floor generators: no drift → NO section clustering
Both iid and markov1 give section-MI excess ≈ **0.000–0.003 bits** (real 0.33/0.27),
z ≈ 75–110, p = 0.016. A section-blind, non-drifting process produces essentially
zero word-section information. This is the baseline: without drift there is no
signal at all.

### Self-citation drift generator: REPRODUCES and EXCEEDS the signal
| unit | partition | real excess | self-cite excess | real/gen | z | p(gen≥real) |
|---|---|---:|---:|---:|---:|---:|
| surface | **sections 6** | 0.333 | **0.508±0.014** | 0.66 | **−12.1** | **1.000** |
| surface | blocks 6 | 0.279 | 0.655±0.018 | 0.43 | −21.0 | 1.000 |
| surface | blocks 20 | 0.327 | 0.883±0.022 | 0.37 | −25.2 | 1.000 |
| surface | **Currier A/B** | 0.235 | 0.180±0.008 | **1.31** | **+7.3** | 0.016 |
| molecule | **sections 6** | 0.273 | **0.477±0.013** | 0.57 | **−15.8** | **1.000** |
| molecule | blocks 6 | 0.231 | 0.619±0.016 | 0.37 | −24.7 | 1.000 |
| molecule | blocks 20 | 0.297 | 0.992±0.019 | 0.30 | −37.2 | 1.000 |
| molecule | **Currier A/B** | 0.194 | 0.176±0.007 | 1.10 | +2.3 | 0.016 |

The meaning-free drift generator, calibrated only to mechanical stats, produces **at
least as much section/block clustering as the real Voynich, and usually more.** The
real value never significantly exceeds it (p=1.000 for every section/block cut).

### Window sweep — the drift-scale knob (section-6 excess)
| window | 10 | 25 | 50 | 100 | 250 | 500 | 1000 | 2000 |
|---|---|---|---|---|---|---|---|---|
| surface gen | .536 | .537 | .536 | .524 | .509 | .477 | .440 | **.372** |
| molecule gen | .485 | .489 | .487 | .478 | .456 | .424 | .381 | **.318** |

Across the **entire** plausible drift range (window 10→2000) the generator's section
excess stays **above** real (0.333 / 0.273). There is no drift setting where a
mechanically-matched generator undershoots the real signal.

### Fairness probe (`probe_map.json`, surface, window 250)
Section excess spans 0.084–1.30 over the (p_new,p_mut) plane. Within the
mechanically-plausible box (TTR∈[.14,.20], repeat∈[.008,.016]) the generator gives
**≈0.41–0.51**, all ≥ real 0.334. To force gen section-excess BELOW real you must set
p_new=0.7 (TTR blows up to 0.21–0.32, hapax off) or p_mut=0.6 (TTR 0.35) — i.e. leave
the mechanically-plausible region. **Real sits at/below the meaning-free achievable
floor**, not above a meaning-free ceiling. The generator is not a straw-man in either
direction (no-drift floor gives 0; matched-mechanics drift gives ~1.2–1.5× real).

## Task 4 — netting out register (content-clustering vs dialect)
`register_results.json`. Bias-corrected excess; conditional uses a within-A/B-stratum
shuffle (destroys only finer-than-dialect clustering).

| | real I(W;AB) | real I(W;Sec) | real **I(W;Sec\|AB)** | survives netting A/B |
|---|---:|---:|---:|---:|
| surface | 0.235 | 0.333 | **0.204** | **61%** |
| molecule | 0.194 | 0.272 | **0.175** | **64%** |

So yes — section clustering **does** survive netting out Currier A/B: ~62% of it is
finer-than-dialect. **But that residual is ALSO generator-reproducible:** the dialect-
blind self-citation generator's conditional I(W;Sec|AB) is **0.372 (surface) / 0.379
(molecule)**, well above real's 0.204 / 0.175. And note the generator, which has
**zero dialect knowledge**, still manufactures I(W;AB)=0.178/0.175 purely from
positional drift (vs real 0.235/0.194) — because A/B are contiguous positional
regions and drifting vocabulary mimics them. Real A/B exceeds the single-population
generator only by a modest margin (the genuine two-dialect difference), which is the
one component not reducible to a single homogeneous drift process.

## Honesty: limits and observational-equivalence ceiling
- **Calibration is the whole game, handled principledly.** Drift emerges from the
  copy dynamics, not from fitting section labels (confirmed: no-drift floor gens →
  0 section-MI; window controls the effect). Fit is to mechanical stats only; the
  generator's hapax undershoot is reported and works *against* over-clustering.
- **Observational-equivalence ceiling stated plainly:** for the section/block signal
  there is NO daylight for a "meaning" inference — a meaning-free generator matched
  to Voynich's mechanics reproduces or exceeds the signal at every drift scale, and
  real is near the low edge of the achievable range. The section-clustering statistic
  simply cannot discriminate "genuine message" from "local self-citation drift."
- **What the generator canNOT reproduce:** the raw Currier A/B contrast (real > single-
  population generator). That is a real two-sub-system structural fact (the classical
  A/B dialect split — different endings/prefixes/core words), independently known and
  NOT semantic content in Montemurro's sense. A meaning-free model with two drift
  regimes would close even this gap; it was not built here (out of scope).
- **Coverage caveats:** Astro = 199 tokens (underpowered as a section; the markup
  itself flags Astro as its least reliable zone). Section/A-B labels are structural
  (folio-level morphology-based), not semantic. The molecule layer is a deterministic
  re-encoding of the surface (per `shadow_of_null`), so surface and molecule results
  are not independent — they agree, as expected. A natural-language positive control
  (calibrate the same generator to English/Latin mechanics) is the clean next step to
  anchor the ~1.2–1.5× overshoot; the internal probe map already shows the generator
  is not pathologically over-clustered.

## VERDICT
1. **Basic Montemurro result replicates** — real word-section MI ≫ word-order shuffle
   (excess 0.333 surface / 0.273 molecule at 6 sections; z ≈ 100). Clustering is real.
2. **Decisive number:** real does NOT exceed the meaning-free self-citation/drift
   generator. Section excess real/gen = 0.66 (surface) / 0.57 (molecule), z = −12 to
   −16, p(gen ≥ real) = 1.000; blocks even more one-sided (real/gen 0.30–0.43). Across
   window 10→2000 the generator stays ≥ real. Generator fidelity is honest (TTR/
   repeat/Zipf matched; hapax undershot, which if anything disfavours the generator).
3. **Content beyond register:** section clustering survives netting out A/B (~62%,
   conditional excess 0.204/0.175) — but that residual is likewise reproduced and
   exceeded by the dialect-blind generator (conditional 0.37). So it is drift, not
   demonstrably content.
4. **Does the published "genuine message" signal prove meaning? No.** On this test it
   is **generator-reproducible**: a principled, meaning-free self-citation/drift
   process calibrated only to the manuscript's mechanical statistics matches or
   exceeds the Montemurro word-section information at every partition and every drift
   scale. The famous signal is fully consistent with meaning-free local copying with
   drift; it does not, by itself, constitute evidence of a linguistic message. The
   Timm–Schinner critique holds. (The only structure the single-population generator
   misses is the classical Currier A/B split — a known two-sub-system fact, not
   semantic content.)
