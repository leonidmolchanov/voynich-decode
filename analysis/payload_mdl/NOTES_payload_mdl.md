# Payload MDL: does the Voynich machine CARRY a text, or EXHAUST it?

Information-theoretic discriminator. Date 2026-09-30. Read-only over the
factorization TSV; all output under `tmp/shadow_analysis/payload_mdl/`.
numpy only, seeded (SEED=20260930), held-out by physical folio.

Core question: after fitting the BEST mechanical model of the manuscript, is
there an irreducible residual "payload" (a real message run through a verbose
cipher), or does the machine essentially EXHAUST the text (self-generation)?

Principle: a cipher of a real message must carry AT LEAST the entropy of that
message; a self-generation process carries ~no payload beyond its own rules.

---

## Method

One pipeline (`pipeline.py`, `floor_ceiling.py`, `control2.py`), applied
IDENTICALLY to every corpus, so any modelling bias cancels in the comparisons.

- **Unit / data**: 23,859 tokens, 4,007 lines, 202 folios, 129,594 glyph-events
  (5.43 glyph-events/word incl. a word-end marker). Surface tokenised with the
  project's multi-glyph rule (`ch sh cth ckh cph cfh`); "molecule" = the
  `body=>state` string from the TSV.
- **Model ladder** (all with parameter-free Witten-Bell interpolation, so the
  same smoothing is applied to every corpus): glyph n-gram orders 0-3 (a word =
  glyphs + word-end, so it is a proper generative spelling machine); molecule
  unigram + spelling backoff; molecule bigram (within-line Markov-1) + spelling
  backoff.
- **Held-out cross-entropy**: 5-fold CV *by folio* (train on ~4/5 of folios,
  score −log2 P on the unseen 1/5). Reported bits/token and bits/glyph, with a
  t-based 95% CI over the 5 folds.
- **Corpora through the same pipeline**:
  - REAL manuscript.
  - Self-gen FLOORS: `FLOOR_selfcite` (molecule Markov-1 + real spellings),
    `FLOOR_iid` (molecule unigram i.i.d. + real spellings) — both stationary,
    global; and `FLOOR_perfolio` (within-folio permutation of the real tokens:
    keeps each page's exact word multiset / "theme", destroys all order).
  - Cipher CEILINGS: `CEILING_word` — real English prose (word stream, local
    `.md` reports) mapped 1:1 to molecules by frequency rank (a nomenclator /
    verbose substitution) and laid onto the real page/line layout IN ORDER, so
    the message's topical & long-range structure is fully preserved; expansion
    1 (max signal) and 2 (2 tokens/word, verbose). Also `CIPHER_letter` — a
    homophonic letter cipher matched to the molecule marginal (an
    intentionally information-thin cipher).

---

## Result 1 — the manuscript's compressed size under its own best machine

REAL held-out (5-fold by folio), bits/token ± CI, bits/glyph ± CI:

| model | bits/token | ±CI | bits/glyph | ±CI |
|---|---:|---:|---:|---:|
| glyph unigram (0) | 20.643 | 0.248 | 3.801 | 0.025 |
| glyph bigram (1) | 11.636 | 0.143 | 2.143 | 0.045 |
| glyph 3-gram (2) | 10.634 | 0.123 | 1.958 | 0.044 |
| glyph 4-gram (3) | 10.660 | 0.121 | 1.963 | 0.043 |
| molecule unigram + spelling | **9.213** | 0.116 | **1.696** | 0.028 |
| molecule bigram + spelling | 9.468 | 0.132 | 1.743 | 0.028 |

- **Best model = 9.21 bits/token = 1.70 bits/glyph.** Whole manuscript ≈ 220,000
  bits ≈ **27 KB** compressed under its own best machine.
- Glyph order-2 is the spelling sweet spot (order-3 does not improve held-out).
- **Word order is informationally inert**: the order-AWARE model (molecule
  bigram, 9.47) does NOT beat the order-INDEPENDENT one (molecule unigram +
  spelling, 9.21). Local copying (the one real short-range signal from the null
  test) does not yield held-out predictive gain at the token level.

## Result 2 — self-generation floors, and Result 3 — cipher ceilings

Best-model held-out bits/token (± sd over replicates):

| corpus | bits/token | non-stationarity KL | what it is |
|---|---:|---:|---|
| `FLOOR_selfcite` (mol Markov-1) | 7.470 ± 0.047 | 2.248 | stationary self-gen (resampling attractor pulls it low) |
| `FLOOR_iid` (mol unigram) | 8.690 ± 0.031 | 2.221 | stationary self-gen, right marginal, no page themes |
| `CIPHER_letter` r1 (info-thin) | 8.721 ± 0.025 | 2.248 | homophonic letter cipher of English, marginal-matched |
| `CIPHER_letter` r3 (info-thin) | 8.736 ± 0.030 | 2.257 | 3× verbose version |
| **REAL** | **9.213 ± 0.116** | **2.698** | manuscript |
| `FLOOR_perfolio` (page-local) | 9.213 ± 0.000 | 2.698 | self-gen keeping each page's exact theme, order destroyed |
| `CEILING_word` r2 (2× verbose) | 9.897 ± 0.017 | 3.165 | real English message, verbose cipher |
| `CEILING_word` r1 (1:1 nomenclator) | 10.195 ± 0.001 | 4.277 | real English message, max signal |

Two facts jump out:

1. **REAL == its page-local self-gen floor, exactly** (9.213 / 9.213; nsKL
   2.698 / 2.698). A process that keeps only each page's word multiset and
   discards all ordering reproduces the manuscript's held-out entropy AND its
   non-stationarity to the third decimal. REAL's only elevation over the
   *global* stationary floor (8.69) is per-page vocabulary novelty (section
   "themes") — which is self-generation-reproducible and is NOT ordered payload.

2. **A competent verbose cipher of a real message can sit at the floor.** The
   marginal-matched homophonic letter cipher (`CIPHER_letter`, carrying ~23k
   English letters of genuine message) collapses to **8.72 bits/token, nsKL
   2.25** — statistically identical to `FLOOR_iid` and BELOW real. This is the
   observational-equivalence ceiling made concrete: an information-thin /
   structure-flattening cipher is indistinguishable from a generator.

## Result 4 — the decisive comparison (where REAL sits, floor→ceiling)

Position of REAL between the page-local self-gen floor and the word-message
ceilings (0 = at floor, 1 = at message ceiling):

| axis | REAL | FLOOR_pf | CEIL 1:1 | CEIL 2× | pos vs 1:1 | pos vs 2× |
|---|---:|---:|---:|---:|---:|---:|
| held-out bits/token | 9.213 | 9.213 | 10.195 | 9.897 | **+0.00** | **+0.00** |
| non-stationarity KL | 2.698 | 2.698 | 4.277 | 3.165 | **+0.00** | **+0.00** |
| beyond-local MI (lag 4-10) | 3.977 | 4.208 | 7.379 | 5.904 | **−0.07** | **−0.14** |

Long-range molecule mutual information (bits) — the sharpest discriminator:

| lag | REAL | FLOOR_pf | CEIL_word 1:1 | CEIL_word 2× |
|---:|---:|---:|---:|---:|
| 1 | 2.956 | 2.964 | 6.494 | 4.290 |
| 4 | 3.329 | 3.392 | 6.845 | 5.196 |
| 6 | 3.731 | 3.865 | 7.386 | 5.735 |
| 8 | 4.030 | 4.487 | 7.765 | 6.310 |
| 10 | 4.884 | 5.125 | 7.315 | 6.329 |

(Absolute MI rises with lag from small-sample bias shared by all corpora; the
cross-corpus comparison at each lag is what matters.)

- On **every** axis REAL sits **at (or just below) the self-generation floor and
  ~0% of the way to the message ceiling** — even to the 2×-verbose message
  ceiling.
- A genuine natural-language message leaves an obvious fingerprint: persistent
  long-range MI (~6-7 bits, non-decaying), nsKL ≈ 4.3, elevated held-out
  entropy. That fingerprint **survives 2× verbosity** (MI still ~5.2-6.4,
  nsKL 3.17) and is unmistakable. It is **absent** from the manuscript: REAL's
  long-range MI is if anything slightly BELOW its own page-permutation floor
  (no long-range dependency to find; corroborates the null test).

## Result 5 — per-unit "message quantum"?

Per-page total surprisal ~ n_words: **R² = 0.989**, slope 7.98 bits/word,
intercept 29.9 bits (≈ 3-4 words). Per-line: R² = 0.878, intercept 2.7 bits.
Per-unit information is **a function of length**, with a negligible
length-independent component. There is **no stable per-page/per-line "message
quantum."** Caveat, stated honestly: this axis does not discriminate on its own,
because a 1:1 cipher is ALSO length-proportional (CEIL_word r1 has R²=0.997,
even tighter). It only becomes informative combined with the topical-structure
axes above, where REAL fails to look like a message and the ciphers succeed.

---

## Honest verdict (probabilistic, with the ceiling stated)

**From information content alone, the machine essentially EXHAUSTS the text.**
After the best mechanical model, the manuscript's residual is at the
self-generation floor on held-out cross-entropy (9.21 bits/token, exactly its
page-local self-gen floor), on non-stationarity, and — most tellingly — on
long-range structure, where a real message (even 2× verbose) shows ~1.5-2×
the mutual information the manuscript shows. The only "extra" the manuscript
carries beyond a global generator is per-page vocabulary theming, which is
itself self-generation-reproducible and far too weak/non-recurrent to be
natural-language content. Word order carries no held-out payload at all.

**The observational-equivalence ceiling is real and I hit it.** My
marginal-matched homophonic letter cipher — which genuinely carries a message —
collapses to the floor (8.72 bits/token, nsKL 2.25), indistinguishable from a
generator. So I cannot mathematically exclude that the manuscript is an
information-thin / context-free verbose cipher engineered (deliberately or by
its construction) to flatten to the marginal and destroy word-order and topical
structure. But such a cipher, precisely because it erases the redundancy every
real natural-language message carries, transmits almost no *recoverable* payload
per token — it is functionally a generator. A cipher that preserves the normal
redundancy of a real message is strongly disfavoured, because that redundancy
is measurably absent and is clearly detectable in the positive controls.

**Number.** Placing the manuscript's irreducible residual between floor (0) and
message-ceiling (1): **≈ 0.0 (95% CI roughly −0.15 … +0.10)** on all three
discriminating axes. Translating to a probabilistic verdict on
text-vs-self-generation from information content:

- **≈ 85%**: self-generation, OR an information-thin / context-free cipher that
  is observationally equivalent to it (these two cannot be split by internal
  information — the clean break needs an external anchor, which the project has
  searched for and not found).
- **≈ 15%**: carries an enciphered text — and almost all of that mass requires
  the cipher to have destroyed natural-language redundancy (topical recurrence,
  long-range dependency) that the controls show WOULD be visible; a
  redundancy-preserving message cipher is < ~3%.

This is a narrowing of the odds, not a proof. Internal information tests cannot
force the last step: a verbose cipher can be information-thin and a generator
can be rich. What they establish firmly is that **the manuscript contains no
detectable message-shaped payload above its self-generation floor**, and that a
real message of the sort a 15th-century text would encode WOULD have been
detectable here.

## Files
- `pipeline.py` — data load, Witten-Bell n-gram ladder, folio-CV harness, REAL.
- `floor_ceiling.py` — self-gen floors, letter-homophonic cipher, discriminators.
- `control2.py` — page-local floor + word-level message ceiling (decisive).
- `real_ladder.json`, `floor_ceiling.json`, `control2.json` — all numbers.
