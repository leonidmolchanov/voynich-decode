# Deep test: can published "pro-language" signatures BREAK the meaning-free generator?

Date 2026-09-30. READ-ONLY on all source data; every write under this folder.
No meaning / plaintext claim is made anywhere. The goal was adversarial: **try
to break the meaning-free generator hypothesis** with the literature's strongest
"Voynich behaves like a natural language" signatures — Menzerath–Altmann,
Brevity/Zipf-abbreviation residual, and above all **long-range correlations**
(DFA / spectral / long-range MI), plus the recent pastiche-grammar paper.

## Data, generator, controls (all imported, not copied)
- **REAL**: `WORKING/hypotheses/x10u_full_symbolic_factorization_v3/full_symbolic_factorization.tsv`
  via `generator_spec/vgen_lib.py::load()` — 23,859 tokens, manuscript order,
  identical tokenizer/molecule decomposition as the rest of the project. Char
  stream = greedy multi-glyph tokenization of the surfaces (`cth ckh cph cfh ch
  sh` first), **105,735 glyph-tokens, alphabet 41**.
- **GENERATOR** = `generator_spec/generator.py` (the copy + **drift** + grammar
  machine, fit per Currier hand). Chosen over the simpler `machine_data.json`
  parts model **on purpose**: its rolling recency/drift buffer (window ≈600–650)
  is exactly the mechanism that could manufacture long-range structure, so it is
  the *strongest, fairest* meaning-free null — the hardest case for "generator
  FAILS". 6–8 seeds per test, mean±sd reported.
- **Nulls**: global glyph-shuffle (destroys all order → floor), **word-order
  shuffle** (keeps each word intact, destroys only inter-word order → isolates
  genuine long-range word dependency).
- **Natural-language controls** (illustrative): English prose (J.Q. Adams, Ford
  ed.) and Latin prose (Caesar, *De Bello Gallico*), each cut to 23,859 words.
- Code: `ll_common.py` (loaders/streams/DFA/MI/PSD), `ll_longrange.py`,
  `ll_nonstationarity.py`, `ll_wordlevel.py`, `ll_menzerath_brevity.py`.
  Raw: `longrange_results.json`.

---

## 1. Menzerath–Altmann law — **generator FAILS (clearest gap), interpretation orthographic**

MAL: longer constructs are built of shorter constituents (negative slope).

**M1 (word length in glyph-tokens vs mean constituent size in EVA chars):**

| | Spearman ρ(len, mean-token-size) |
|---|---:|
| **REAL** | **−0.248** (p≈0) |
| GENERATOR | **+0.023 ± 0.014** |
| English (syllable-based, illustrative) | −0.056 |
| Latin (syllable-based, illustrative) | −0.073 |

Real has a clean Menzerath effect; **the generator does not reproduce it at all**
(wrong sign). Mechanism, pinned down: the generator matches the *marginal*
multi-glyph rate (REAL 0.120 / GEN 0.116) but not its **length-conditioning** —
real concentrates multi-glyph ligatures (`ch, cth, …`) in short/mid words and
thins them out in long words (fraction L2=0.16, L3=0.22 → L7=0.06), while the
generator keeps that fraction nearly flat across lengths (L3=0.14 → L7=0.10) and
structurally almost never emits a **2-token surface** (P(len=2)=0.000 vs real
0.080) because its surface reconstruction is `first+body+last` (length = body+2
or 1). So the miss is a **length-conditioned orthographic / surface-layer
regularity** (where the benches/gallows sit), traceable to the crude
molecule→surface map — a real fidelity gap, but *about glyph shape placement,
not semantics*, and notably **stronger in Voynich than in my NL controls**.

**M2 (line length in words vs mean word length):** REAL ρ = **−0.079** (p≈2e-6,
weak but real); GENERATOR **+0.058 ± 0.020** — again misses the sign. The
generator preserves the line layout but draws word lengths i.i.d. per hand, so
it has no line-length↔word-length coupling (a LAAFU/line-filling effect).

**Verdict M1/M2: generator FAILS.** This is the clearest signature the current
generator misses. Honest caveat: both realizations are mechanical/orthographic
(ligature placement, line-filling), not evidence of meaning, and the M1 metric
has a mild built-in `size = chars/tokens` tendency — but the generator's flat
sign shows the real negative slope is a *genuine length-conditioned structure*
the spec doesn't capture, not just the metric.

## 2. Brevity / Zipf abbreviation residual — **generator REPRODUCES (minor residual)**

Type-level Spearman(log freq, length) — note this is **order-invariant**, so the
word-order shuffle null equals real exactly (brevity is not a sequence effect).

| | ρ(log f, len) | mean len hapax | 2–5 | 6–20 | 21+ |
|---|---:|---:|---:|---:|---:|
| **REAL** | **−0.394** | 6.46 | 5.56 | 5.17 | 4.61 |
| GENERATOR | −0.331 ± 0.009 | 6.24 ± 0.06 | — | — | 4.72 |
| English | −0.192 | | | | |
| Latin | −0.293 | | | | |

The generator **reproduces the abbreviation law** (same monotone direction, ~85%
of the slope). The much-touted residual — "Voynich's rare words are longer than
the generator makes" — is **real but small on the molecule tokenization: +0.21
glyph-tokens for hapaxes** (6.46 vs 6.24), and the slope is only modestly steeper
(−0.39 vs −0.33). Real abbreviation is **stronger than English/Latin**, matching
the earlier finding that Voynich is *more* concentrated than natural prose — i.e.
the residual points away from "ordinary language", not toward it.

**Verdict: generator reproduces** (small honest residual, not a breaker).

## 3. LONG-RANGE CORRELATIONS — the highest-stakes test → **NOT a breaker (it is drift/nonstationarity)**

### 3a. The signal is real and replicates the papers
Real Voynich shows long-range persistence far above the shuffle floor on every
method (α=0.5 uncorrelated; >0.5 = long-range persistent):

| method (α = DFA exponent) | REAL | GENERATOR | shuffle | English | Latin |
|---|---:|---:|---:|---:|---:|
| **word-length series (DFA)** | **0.667** | 0.604 ± 0.014 | 0.506 | 0.610 | 0.649 |
| **symbol return-interval / Hurst (Arutyunov)** | **0.724** | 0.577 ± 0.003 | 0.507 | 0.554 | 0.626 |
| **word log-frequency series (DFA)** | **0.670** | 0.563 ± 0.013 | 0.498 | 0.600 | 0.582 |
| **top-word return-interval (DFA)** | **0.659** | 0.599 ± 0.026 | 0.523 | 0.634 | 0.555 |
| word-length **spectral** slope β (S∝f^−β) | **0.307** | 0.207 ± 0.035 | 0.033 | 0.281 | 0.214 |

Character-stream **long-range MI(d)** (excess over each corpus's own shuffle
floor, bits): real stays elevated (~0.002–0.005) out to lag **2500**, while the
generator and the word-order shuffle collapse to the floor by lag ~10; Latin also
stays elevated, English does not:

```
 lag     REAL    GEN(mean)  SHUF_word   ENG      LAT
   1    1.3825    0.8984     1.3433    0.5887   0.5228
  10    0.0080    0.0015     0.0010    0.0035   0.0069
  50    0.0049    0.0002     0.0002    0.0002   0.0030
 550    0.0019   -0.0001    -0.0001    0.0002   0.0023
2500    0.0022    0.0001    -0.0005    0.0003   0.0023
```

So **yes, real has long-range correlations that the shuffle does not, and the
current generator statistically under-produces them** (word-length 0.667 vs
0.604 ≈ 4.5σ; word-logfreq 0.670 vs 0.563 ≈ 8σ). Taken naively this *looks* like
a breaker. It is not — see 3b.

### 3b. The decisive test: it is NONSTATIONARITY (drift), not sequential dependency
Two independent surrogate tests show the long-range α is **entirely the slow
compositional trend**, with **no genuine long-range sequential dependency**:

- **Trend + i.i.d. surrogate.** Rebuild the series as `moving_average(W) +
  shuffled_residuals` — keeps the slow drift profile, destroys ALL dependency in
  the fluctuations. It reproduces real's α *exactly at every scale*:
  word-length α: real 0.667 → surrogate 0.67–0.71 for W∈[50..1600];
  word-logfreq α: real 0.670 → surrogate 0.67–0.70. (Full word-order shuffle,
  which also kills the trend, gives α≈0.50.) The persistence lives 100% in the
  slow trend.
- **Block-local shuffle** (destroy order inside blocks of size B, keep coarse
  profile). Word-length α is unchanged for B up to 100 (0.667→0.668) and only
  erodes at B=1000 (0.588); return-interval α: 0.724→0.699 at B=50, still 0.688
  at B=1000. Destroying all *local* order leaves the exponent intact ⇒ the
  structure is coarse drift at scales ≫ a hundred words, not fine word-to-word
  grammar.

**Where the drift comes from, quantified** — excess I(·; 20 contiguous blocks):

| | glyph-frequency drift | word-length drift |
|---|---:|---:|
| **REAL** | **0.0538** | **0.0294** |
| GENERATOR | 0.0104 ± 0.001 | 0.0122 ± 0.002 |
| English | 0.0048 | 0.0096 |
| Latin | 0.0353 | 0.0125 |

Real Voynich's glyph/word-length *distributions* drift more across the book than
the generator's — and **more than natural-language prose**. That is exactly why
the generator under-shoots the α's: `generator.py` has only **two** stationary
regimes (Currier A/B), so its base glyph/length statistics barely drift; real
Voynich drifts continuously (topic/section/hand/scribal). This is
**topic-drift / vocabulary nonstationarity — the very thing the brief says a
drift generator reproduces and that must NOT be scored as a language signal.**

### 3c. Why this is not a breaker
1. The effect is **nonstationarity, not sequential dependency** (3b, two surrogate
   tests) — no long-range grammar to find.
2. Nonstationarity is **meaning-free-reproducible**: the project's own
   `montemurro/` result already shows a drift generator **matches or exceeds**
   real word–section clustering at every scale. The current spec's shortfall is a
   **drift-granularity parameter** (2 regimes instead of continuous per-section/
   per-page drift), a mechanical refinement — not evidence of language.
3. Real's long-range magnitude is often **stronger than natural language**
   (return-interval α 0.72 vs NL 0.55–0.63; glyph nonstationarity 0.054 vs NL
   0.005–0.035). Per Arutyunov et al., over-strong long-range memory argues
   *against* a natural language and *toward* an artificial/mechanical process —
   i.e., toward a generator (with richer drift), not toward meaning.
4. The char-stream comparison is partly **unfair to the generator** anyway: it is
   a molecule-layer model whose surface glyph stream is a crude `first+body+last`
   reconstruction (hence the L2 gap and the depressed short-range char-MI). At the
   layer it was actually fit for (word/molecule), the gaps are smaller and the
   trend+iid decomposition still fully explains them.

**Verdict long-range: generator reproduces the phenomenon (LRC present, ≫shuffle,
in/above the NL band); the current spec under-shoots the drift *magnitude*
(honest fidelity gap), but the signal is nonstationarity, is meaning-free-
reproducible, and does NOT constitute genuine long-range linguistic dependency.
It does not overturn the meaning-free (sufficiency) null.**

## 4. Recent-paper claims

- **Pastiche / generative-grammar (arXiv:2609.20835, Turenne).** Its thesis —
  "a *structured imitation* of natural language", a position-dependent generative
  grammar, **not** a genuine language — is a *fellow-traveller* of the meaning-free
  generator, not a challenger. Its concrete distributional claims all favour the
  generator family: **Zipf-like** (gen −0.96 vs real −1.19, reproduced);
  **word-length resembling a tight/syllabic (binomial-like) distribution** — real
  var/mean = **0.53** (under-dispersed), generator **0.58**, both far from
  over-dispersed natural language (English 1.50, Latin 1.45), so the generator
  reproduces it and it is *un-language-like*; position-dependent structure is
  already in the generator (LAAFU line-initial prior + slot grammar). **Verdict:
  consistent with / reproduced by the generator.**
- **Weak word order + low conditional entropy** (claimed to favour the generator —
  confirmed): state (ending-class) adjacent MI = **0.015 bits = 0.7% of H1**, and
  the generator matches it (0.016 ± 0.002); molecule H(next|current) is low
  (real 5.18 bits vs H1 8.16) and the generator reproduces/over-predicts it
  (4.44). **Verdict: generator reproduces; favours generator.**

---

## Overall verdict

**No published pro-language signature genuinely breaks the meaning-free generator
hypothesis.**

- **Long-range correlations — the one that could have overturned it — do not.**
  They are real and replicate the papers, but two surrogate tests prove they are
  **compositional nonstationarity (drift), not sequential dependency**; drift is
  meaning-free and already shown reproducible (montemurro); and the magnitude
  exceeds natural language, pointing to a mechanical origin. The current spec
  under-parameterizes the drift (2 regimes) — a fidelity knob, not meaning.
- **Brevity** and the **pastiche/word-length/entropy/word-order** claims are
  **reproduced** by the generator (and several are *more* extreme in Voynich than
  in real language, i.e., un-language-like).
- **The only genuine fidelity GAP is Menzerath (M1/M2)** — plus, from the prior
  `null_test/`, short-range local repetition. Both are **local, mechanical /
  orthographic** (length-conditioned ligature placement; adjacent paradigm
  copying), traceable in part to the crude surface-reconstruction layer, and
  **neither requires meaning or long-range grammar**. They are refinements a
  meaning-free generator would need, not evidence of language.

The observational-equivalence wall stands: every "language-like" statistic tested
is matched — or exceeded in an un-language-like direction — by a meaning-free
drift+copy generator. Where the current generator falls short (Menzerath, drift
magnitude, local repetition) the misses are mechanical and fixable without
invoking meaning.
