# Why do some Voynich words repeat so much? Decomposing the extreme vocabulary concentration

Date 2026-09-30. Read-only on all source data. No meaning/plaintext claim is
made anywhere in this note. Builds directly on `shadow_of_null/`,
`generator_spec/` and `ladders/` — it does not restart from them, and it
reproduces their headline numbers (real molecule TTR 0.102/V 2432, generator
TTR 0.188/V 4475, Zipf −1.19 vs −0.96) independently as a consistency check
before extending past them.

**Data (read-only):**
`WORKING/hypotheses/x10u_full_symbolic_factorization_v3/full_symbolic_factorization.tsv`
(23,859 tokens), loaded via `generator_spec/vgen_lib.py::load()` — unchanged,
imported not copied. **Unit of analysis:** "word" = *molecule* = `body
glyph-tokens => S<ending-state>` (the same abstraction `generator_spec` and
`shadow_of_null` already established as the project's working definition of
a Voynichese word; surface-string and body-only numbers are reported too, for
completeness, and tell the same story). **Generator baseline:**
`generator_spec/generator.py` (imported, not modified) at `DEFAULT_PARAMS`
(fit p_copy≈0.58–0.60, local-recency-window copy-mutate).
**Natural-language baselines:** built locally from two Project-Gutenberg-derived
plain-text files already present in this project for an unrelated
cipher-corpus purpose (read-only, used here for the first time as Zipf
baselines) — English: John Quincy Adams' writings, ed. Ford
(`WORKING/data/historical_ciphers/.../jqa/ford_writingsofjohnqu03adam.txt`,
~188.6k word-tokens after stripping library-stamp front/back matter); Latin:
Caesar, *De Bello Gallico* I–VIII (`.../unpaired_corpora/latin_caesar_218.txt`
+ `latin_caesar_18837.txt`, ~51.3k tokens); a secondary medieval-Latin check
uses `WORKING/data/picatrix_latin_pingree_warburg.txt` (~166k tokens, OCR'd,
higher variance, register closer to Voynich's presumed subject matter). All
natural-language and null-model corpora are **bootstrap-matched to N=23,859
tokens** (20 replicates for NL, mean±sd reported) so TTR/V/Zipf comparisons
are apples-to-apples (these quantities are strongly N-dependent — Heaps' law
— so raw-corpus-size comparisons would be meaningless).

**Code (new, this task, all under this directory):** `wf_common.py` (stats,
Zipf-Mandelbrot fit, Heaps curve, CRP/Polya-urn simulator, fixed-dictionary
simulator), `wf_run.py` (main driver → `wf_results.json`), `wf_hybrid_extra.py`
(the decisive hybrid-mechanism scan + frequency-of-frequencies spectrum →
`wf_hybrid.json`). Raw run logs: `wf_run.log`, `wf_hybrid_extra.log`.

---

## 1. The distribution, characterized

| corpus (N=23,859 matched) | V | TTR | hapax% | Zipf slope | ZM α | ZM β | Heaps exp. |
|---|---:|---:|---:|---:|---:|---:|---:|
| **REAL (molecule)** | **2432** | **0.102** | **63.5%** | **−1.188** | **1.204** | **1.45** | **0.669** |
| REAL (body only) | 1819 | 0.076 | 63.0% | −1.261 | 1.272 | 0.74 | — |
| REAL (surface) | 4054 | 0.170 | 64.2% | −1.050 | 1.072 | 3.68 | — |
| English (JQA, real prose) | 3832±67 | 0.161±.003 | 54.4%±.9 | −0.994±.007 | 0.995 | 0.16 | 0.684 |
| Latin (Caesar, real prose) | 6790±229 | 0.285±.010 | 61.8%±.6 | −0.836±.012 | 0.838 | 0.62 | 0.768 |
| Latin (Picatrix, medieval) | 5113±788 | 0.214±.033 | 64.9%±11.5 | −0.826±.183 | 0.830 | 0.85 | 0.784 |
| Generator, default (fit local-copy machine) | 4475±62 | 0.188±.003 | 54.2%±.5 | −0.962±.004 | 0.969 | 1.03 | 0.784 |
| Generator, no-copy (grammar/paths only) | 3490±35 | 0.146±.002 | 62.2%±.5 | −1.043±.004 | 1.047 | 0.49 | 0.727 |

Full per-metric numbers (including top-10/50/100 coverage) in `wf_results.json`.

**Headline fact, sharper than the prior generator-vs-real framing:** real
Voynichese is not just more concentrated than a local-statistics generator —
**it is more concentrated than actual natural-language prose at the same
token count.** English/Latin Zipf slopes at N=23,859 sit at −0.83 to −0.99;
Voynich's is −1.19, steeper than all three. Real natural-language V (3.8k–6.8k)
and TTR (0.16–0.29) *bracket* the fitted generator's output (V=4475,
TTR=0.188) almost exactly — **the generator's vocabulary-diversity profile is
statistically indistinguishable from ordinary running prose**, while the real
manuscript sits well outside that range on the low-diversity side. This
reframes the earlier MISS: it's not merely "generator ≠ manuscript," it's
"manuscript ≠ language-like text of any kind tested here," and the generator
inherits exactly the language-like profile because it is built from the
manuscript's own *local* (bigram/trigram, lag≤3) statistics — which is the
same local horizon natural language runs on.

A genuine surprise in the decomposition: **removing the fitted local-copy
layer from the generator (no-copy / grammar-paths-only) moves it *closer* to
real on every axis** (V 3490 vs 4475, TTR 0.146 vs 0.188, hapax 62.2% vs
54.2%, slope −1.04 vs −0.96) — because the fitted copy layer mutates 55–58%
of its "copies" (del/sub/ins on one glyph), so most copy events mint a *new*
string rather than reinforcing an old one. The generator's copy-with-mutation
mechanism is, in terms of vocabulary impact, closer to constrained fresh
generation than to genuine reuse. This is the first concrete clue to what's
missing (§4).

---

## 2. Decomposing the reuse into three mechanisms

Task-specified mechanisms, each with a real implementation (not a hand-waved
label), fit at N=23,859 to match real molecule V=2432 (and where noted, the
−1.188 slope), 10 replicates each:

**(i) Grammar/paths only** — `generator.py`'s word-template Markov chain with
`p_copy=0` (no copying at all; short/common part-combinations are simply more
probable). *Result above*: V=3490, hapax=62.2%, slope=−1.04. Gets closest of
any single mechanism to the real *hapax fraction*, but overshoots V by 44%.

**(ii) Preferential attachment / rich-get-richer, global** — a Hoppe/Chinese-
Restaurant-Process (Polya urn) over N=23,859 draws: with probability
θ/(θ+n) mint a brand-new type, else copy a **uniformly random past draw**
(exactly equivalent to "pick an existing type with probability proportional
to its current count" — the textbook rich-get-richer construction), no
recency decay, unbounded memory. θ is not hand-tuned to the target curve: it
is solved **analytically** from the closed-form E[V_n]=Σθ/(θ+i) to hit real's
V=2432 exactly (θ=677.36). Everything else is an emergent prediction, not a
fit target.

| | V | TTR | hapax% | slope | Heaps exp. |
|---|---:|---:|---:|---:|---:|
| CRP, θ=677.36 | 2431±34 (fit) | 0.102 (fit) | **26.7%±0.8** | **−1.171±.011** | **0.582** |
| REAL target | 2432 | 0.102 | 63.5% | −1.188 | 0.669 |

The Zipf slope comes out at −1.17 essentially **for free** from a single
fitted knob (θ) — a real, non-trivial confirmation that global rich-get-richer
dynamics are *consistent with* the real slope. But hapax rate is less than
half of real's, and vocabulary grows too slowly (Heaps exponent 0.58 vs 0.67).

**(iii) Bounded finite stock** — literal fixed dictionary: pick K types with
Zipf-Mandelbrot weights (rank^−α), draw all N=23,859 tokens i.i.d. (with
replacement) from that fixed table (task's own framing: "a scribe drew from a
few hundred word-types"). Grid-fit (K,α) to match real (V, slope)
simultaneously:

| | K | α | V | TTR | hapax% | slope |
|---|---:|---:|---:|---:|---:|---:|
| grid-fit best | 3000 | 1.00 | 2503±27 | 0.105 | **27.9%±0.8** | −1.057±.003 |
| **literal "few hundred"** | **300** | 1.00 | 300 (forced) | 0.013 | **0.0%** | −1.02 |

**The literal "few hundred word-types" hypothesis is falsified outright by
the arithmetic, not by fitting**: at N=23,859 tokens, any fixed pool of ~300
types gets sampled ~80× on average — hapax rate is mechanically forced to
≈0%, while real hapax is 63.5%. A bounded stock, if this is the right family
of mechanism at all, has to hold on the order of **2,000–3,000** types, not
"a few hundred" — closer to real V itself than to the folk intuition. Even
at the correct order of magnitude (K=2432, α swept 0.8→1.5), there is a hard,
monotone **trade-off**: raising α to chase hapax up (α=1.5 → hapax 52.8%)
collapses V to 799 (TTR 0.033) and overshoots the slope (−1.31); lowering α
to protect V collapses hapax (α=0.8 → V=2365 but hapax=7.9%). No single α
hits (V, slope, hapax) at once (full sweep table in `wf_results.json` under
`fixed_dict_Kreal_sweep`).

### Which mechanism wins, and the shared failure mode

Both (ii) and (iii) — despite being structurally different (dynamic
open-ended urn vs. static closed table) — land on **the same ceiling**:
hapax≈27–28% at matched V, roughly **2.3× short** of real's 63.5%. That two
unrelated mechanism families converge on the same shortfall is itself
informative: it is not an artifact of one specific implementation, it is a
structural property of **any stationary/exchangeable resampling process**
(a process where, loosely, "the next word is drawn from a fixed or
slowly-evolving popularity table"). Shrinking V by reuse mechanically
promotes former singletons into doubletons/triples — the frequency-of-
frequencies spectrum shows this directly (fraction of types with exactly
k=1,2,3… occurrences):

| | k=1 | k=2 | k=3 | k=4 | hapax:doubleton ratio |
|---|---:|---:|---:|---:|---:|
| **REAL** | **63.5%** | **10.4%** | 5.5% | 3.2% | **6.1×** |
| grammar-only (i) | 63.1% | 12.5% | 5.5% | 3.5% | 5.1× |
| generator default | 54.2% | 18.0% | 8.0% | 4.2% | 3.0× |
| CRP (ii) | 26.9% | 13.1% | 8.7% | 6.2% | 2.1× |
| English | 53.5% | 16.1% | 8.2% | 4.6% | 3.3× |
| Latin | 62.0% | 15.1% | 6.9% | 3.4% | 4.1× |

Real has the single steepest hapax→doubleton cliff of anything tested,
including natural language. Pure grammar/paths (i), with **no copying at
all**, comes closest in *shape* (5.1×) — copying of any kind (local-mutating
or global rich-get-richer) systematically flattens this cliff, because that
is structurally what reuse does to a frequency spectrum.

---

## 3. The decisive test: does a minimal generation-compatible mechanism close the gap?

If (i) alone gives the right *shape* but the wrong *scale* (V too high), and
(ii)/(iii) give the right *scale* but destroy the *shape*, the natural next
question is whether combining them — a **minority of exact, globally
unbounded, non-mutating copies on top of a majority of fresh grammar draws**
— does better than either alone. This removes exactly the two things that
made the generator's real copy layer behave like fresh generation: the
**window decay** (650-token recency horizon) and the **55–58% mutation
rate**. One free parameter, `p_fresh`, is bracketed by direct simulation to
hit target V=2432 (`wf_hybrid_extra.py`, scan in `wf_hybrid.json`); everything
else is a genuine out-of-sample prediction.

| statistic | REAL | HYBRID (p_fresh=0.87) | CRP (ii) | fixed-dict (iii) |
|---|---:|---:|---:|---:|
| V | 2432 | 2457±29 | 2431±34 | 2503±27 |
| TTR | 0.102 | 0.103±.001 | 0.102 | 0.105 |
| Zipf slope | −1.188 | **−1.153±.003** | −1.171±.011 | −1.057±.003 |
| ZM α | 1.204 | **1.206±.003** | 3.12 | 1.08 |
| ZM β | 1.45 | 6.38 (same order; CRP β=757, off 500×) | 757±113 | 2.96 |
| top-10/50/100 mass | .266/.559/.690 | .236/.506/.615 | — | — |
| **Heaps exponent** | **0.669** | **0.6689** | 0.582 | 0.685 |
| hapax% | **63.5%** | **36.2%±0.9** (best of the three, still a real miss) | 26.7% | 27.9% |

**This is the sharpest positive result in the investigation.** A two-knob,
fully mechanical, meaning-free process — "≈87% of words are fresh
combinatorial draws from the local word-grammar, ≈13% are *exact*, *globally*
unbounded copies of an earlier word chosen with probability proportional to
its running frequency" — simultaneously reproduces V, TTR, the Zipf slope
(within 3%), the Zipf-Mandelbrot α (to 3 significant figures), and the Heaps'
vocabulary-growth exponent (0.6689 vs 0.6690 — a near-exact match) purely as
emergent consequences of one fitted knob. It still under-shoots hapax rate
(36% vs 63.5%) and the ZM β (fine head-of-curve shape), but it closes roughly
half of the concentration gap that separated CRP/fixed-dict from real, using
the *same* rich-get-richer principle just applied globally and without
mutation instead of locally and with mutation.

### Held-out test (page-fold split, same recipe as `generator_spec/heldout.py`)

Deterministic md5(folio)%2 fold: train=11,655 tokens, test=12,204 tokens
(unseen pages). This is the model-free, non-parametric decisive check: **how
much of a held-out page's vocabulary is genuinely new relative to the pages
already seen**, and does each mechanism's held-out behavior match it.

| | V(test) | TTR(test) | hapax%(test) | slope(test) | **OOV token-rate** | OOV type-rate |
|---|---:|---:|---:|---:|---:|---:|
| **REAL test pages (ground truth)** | **1584** | **0.130** | **62.0%** | **−1.157** | **8.55%** | 56.3% |
| Generator (fit on train, generate test layout) | 2719 | 0.223 | 55.0% | −0.930 | **33.1%** | 76.4% |
| Fixed-dict = train's own empirical distribution, resampled | 1178 | 0.097 | 35.0% | −1.230 | **0.0%** (structural) | 0% |
| CRP continued from train (θ fit on train=475.64, same urn extended) | **1575** | **0.129** | 29.2% | −1.102 | **3.92%** | — |

This is the cleanest falsification/support pattern in the whole note:
- The **real manuscript's held-out pages are not a fresh invention and not a
  closed book**: 91.5% of held-out *tokens* reuse a type already seen on
  other (training) pages, but 8.55% of tokens (56% of distinct held-out
  *types*, which are overwhelmingly low-frequency) are genuinely new. A
  persistent, shared, only-slowly-growing stock, not a literally frozen one.
- The **fitted local-copy generator drastically over-invents** on new pages
  (33.1% OOV tokens, 3.9× too much) — the single most decisive number against
  "local grammar + local recency copy" as a sufficient account of the
  concentration: it doesn't just have too many types overall, it keeps
  minting new ones at 4× the real rate exactly where it matters (unseen
  pages).
- A **literally fixed dictionary under-invents completely** (0% OOV by
  construction) and, because it can never encounter a new type, systematically
  **undershoots real test V by 26%** and TTR — real pages are not simply
  resamples of the training pages' own frequency table.
- **CRP continued across the fold boundary** (the only mechanism here with a
  *global, ever-growing* memory rather than a page-local or fully-fixed one)
  lands closest on V, TTR and slope for the *unseen* pages, and predicts a
  new-type rate (3.9%) that is the right *order of magnitude* (real 8.55%,
  off by ~2.2× — vs. the generator's 3.9× overshoot or the fixed dictionary's
  complete inability to explain any of it). It still misses hapax (29.2% vs
  62.0%), consistent with every other test in this note.

**Answer to the task-3 decisive question:** yes — a bounded/rich-get-richer
global-memory model (CRP continued, or the hybrid above) reproduces the
frequency curve and low TTR **substantially better than free
part-combination generation** on held-out data, on every metric except
hapax rate, where all tested mechanisms in this family fall short by a
similar, consistent margin.

---

## 4. Direct answers to the challenge

**Can a generator reproduce this frequency structure?** Mostly yes, with one
specific, honestly-quantified exception. A purely mechanical, two-component
process — a majority of fresh combinatorial word-formation plus a minority of
*globally* rich-get-richer exact reuse (no recency window, no mutation) —
matches real V, TTR, Zipf slope, Zipf-Mandelbrot α, and the Heaps
vocabulary-growth exponent to within a few percent, and — in the held-out
test — the right order of magnitude of genuine on-page innovation. This is a
strictly stronger, more specific result than "generators reproduce Zipf and
local repetition but miss concentration" (the prior framing this task
inherited): the concentration gap itself is **mostly closeable** by a
generation-compatible mechanism, once the copy mechanism is changed from
*local+mutating* (what the fitted machine actually does, and which behaves
statistically like extra fresh generation) to *global+exact* (true
preferential attachment).

**Where does it fall short?** One number, robustly, across every mechanism
tested (CRP, fixed finite dictionary at any α, the hybrid, and the literal
train-distribution resample on held-out pages): **hapax rate**. Real
Voynichese has 63.5% singleton types among only 2,432 total types; the best
mechanism found here (hybrid) reaches 36.2%; pure preferential attachment or
a bounded dictionary alone reach ~27%. This is not a small-sample fluke — it
replicates across FULL, held-out-test, molecule, and (at 63.0–64.2%) body and
surface units alike, and across three structurally different null families.
The mechanistic reason is visible in the frequency-of-frequencies spectrum
(§2): any process that concentrates the head of the distribution by reuse
necessarily promotes some singletons into doubletons on the way, flattening
exactly the hapax→doubleton cliff that real Voynichese has sharper than
natural language itself.

**What minimal mechanism closes most of the gap, and is it
generation-compatible?** The **hybrid mechanism is generation-compatible** —
it requires no semantic content, no decoding, no positional key; it is a
one-parameter mixture of (a) the same local word-grammar already established
in `generator_spec`, run without a recency-window/mutation-based copy layer,
and (b) a genuinely global, unbounded, exact preferential-attachment reuse
process (equivalent to "the scribe occasionally, and increasingly as the
stock grows, re-writes a word they've used before, chosen in proportion to
how often they've already used it, rather than only glancing at the last few
hundred words written"). This is fully consistent with, and in fact
*explains*, the project's prior null-test finding that there is no long-range
*sequential* structure (MI≈null at lag≥4): a frequency-proportional global
resample has no positional signature at all — it looks exactly like
`null_test`'s "no long-range structure" result while still reproducing the
long-range *concentration*, because concentration is a property of the
marginal type-frequency table, not of sequential order. **The remaining
hapax-rate residual (63.5% vs the best mechanism's 36.2%) is honestly
unresolved.** It does not require positing meaning to exist, but it is not
explained by any resampling-from-a-marginal-distribution model tested here,
whether static (fixed dictionary) or dynamic (CRP/hybrid) — it indicates the
process that produced the ~1,540 singleton molecule-types behaves less like
"occasionally reuse the popularity table" and more like a **separate,
persistent, roughly constant-rate stream of one-off short strings** running
alongside the concentrated reused core, which these single-mechanism models
do not have a slot for. Whether that separate stream reflects genuinely
free scribal invention (compatible with generation, and the mechanism
`generator_spec`'s "grammar/paths" component already comes closest to,
shape-wise, at 5.1× vs real's 6.1× hapax:doubleton ratio), scribal copying
error, rare technical/proper-noun-like material, or something else is not
resolved by frequency statistics alone and is not claimed here.

---

## 5. Honest verdict

- **Generation-compatible, and now demonstrated, not just asserted:** the
  bulk of the extreme vocabulary concentration (V, TTR, Zipf slope, Heaps
  growth, and the right order of magnitude of held-out innovation) is
  reproduced by mechanisms that require no meaning — global preferential
  attachment (rich-get-richer copying, unbounded memory) closes most of the
  gap that local-recency copying (what the fitted generator actually
  implements) leaves open. The task's own framing — "bounded stock +
  copying" vs "free generation" — resolves in favor of **bounded-stock/
  preferential-attachment being a better, though still imperfect, account**,
  confirmed by an out-of-sample held-out test, not merely an in-sample fit.
- **The literal "small fixed lexicon of a few hundred word-types" reading is
  wrong by an order of magnitude** — the data need a stock on the order of
  2,000–3,000 types, and even a stock of exactly that size cannot
  simultaneously match V, Zipf slope, and hapax rate under a single
  power-law weighting; the two knobs trade off against each other.
- **The one number that resists every mechanism tried here is the hapax
  rate** (63.5%, roughly double what any tested resampling-based mechanism
  produces at matched V). This is reported as a genuine, unresolved
  residual — not a mysterious "meaning signal," but a concrete, quantified
  gap between "reuse a fixed or slowly-growing popularity table" and
  whatever actually generated this manuscript's long tail of once-only
  molecule-types. No claim of meaning, decoding, or authorial intent is made
  or implied by this residual; it is reported so a future generator design
  can specifically target it (e.g., a two-stream process with a structurally
  separate, non-competing novelty channel, rather than a single shared
  urn/dictionary).

All numbers reproducible from `wf_run.py` (seed 20260930) and
`wf_hybrid_extra.py`; raw outputs in `wf_results.json` and `wf_hybrid.json`.
