# Null models and controls — is the "language-like" structure real or reproducible?

This is the adversarial core of the investigation and the part most exposed to a
skeptical statistical reviewer: **are the Voynich's language-like signatures genuine
linguistic structure, or are they reproduced by a meaning-free process and/or imposed
by the measurement?** Every analysis here compares the manuscript against (a) fair
null models and (b) **positive controls on real natural language** (English, Latin)
run through the identical pipeline. Code, raw results, and per-suite notes are under
`analysis/`. Honest framing throughout: no plaintext/meaning is claimed; the
observational-equivalence ceiling is stated explicitly.

> Provenance note: the frozen result files (`*_results.json`, `metrics_*.json`,
> `*.json`, `report.txt`) were computed on an earlier factorization snapshot; the
> scripts here are repointed to the shipped v82 `data/factorization/full_surface_factorization.tsv`
> and the controls in `analysis/controls/`. Re-running reproduces the same qualitative
> verdicts with minor numeric differences.

---

## 1. `analysis/shadow_of_null/` — three-null battery (is the structure a method artifact?)

Applies the project's own deterministic re-encoding to three corpora matched at
23,859 words: **REAL**, a **word-internal shuffle null** (same per-word glyph
multiset, order destroyed), and a **bigram-generator null** (1st-order glyph Markov
fit to the real glyph statistics). Verdict, bucketed honestly:

- **Manuscript-real (survives both nulls, large effect):** the skewed word-final
  ending-channel (z ≈ −200 vs shuffle), and the degree of exact body-string reuse
  (low TTR/hapax, far beyond even the bigram generator) — real local copying.
- **Partly real, partly generic:** top-50 template coverage (real exceeds both nulls,
  but most of its edge over a shuffle is already delivered by local bigram statistics).
- **Method-imposed / hallucination-risk (reproduced by a null as well or better):**
  the overall body-entropy *shape* (matches the bigram generator, z≈0.9), the
  small-template (~top-10) coverage (z≈−1.8), and the "paradigm-ladder" edit-1
  connectivity claim (a letter-shuffle null **matches or exceeds** it, z≈−4) — these
  must NOT be cited as designed structure. This self-critical result is a strength,
  not a weakness.

## 2. `analysis/montemurro/` — does the famous "genuine message" signal survive a fair null?

Reconstructs Montemurro & Zanette (2013): words carry information about *where* they
occur (clustering by section/block), reported as **excess** over each corpus's own
word-order-shuffle floor (removes finite-sample MI bias — the fairness requirement).

- **The signal replicates** (real word–section MI ≫ shuffle; excess ≈ 0.33 surface /
  0.27 molecule at 6 sections; z ≈ 100). Clustering is real.
- **But it is generator-reproducible.** Section-blind **floor generators** (iid,
  Markov-1) give ≈ 0 clustering. A meaning-free **self-citation / drift generator**
  (Timm–Schinner style), calibrated ONLY to mechanical stats (TTR/hapax/repeat/Zipf),
  **reproduces or exceeds** the signal: real/generator ≈ 0.66 (surface) / 0.57
  (molecule), p(gen ≥ real) = **1.000**; across the whole drift range (window 10→2000)
  the generator stays ≥ real. Section clustering survives netting out Currier A/B
  (~62%), but that residual is also exceeded by the dialect-blind generator.
- **Verdict:** the Montemurro signal does **not**, by itself, prove meaning; it is
  fully consistent with meaning-free local copying + drift. (Reported with empirical
  p, own-shuffle bias correction, window sweep, and the observational-equivalence
  ceiling stated.) The only structure the single-population generator misses is the
  classical Currier A/B split — a known two-sub-system fact, not semantic content.

## 3. `analysis/linguistic_laws/` — pro-language signatures vs real-language controls

The strongest literature "Voynich behaves like a language" signatures, tested against
**English (J.Q. Adams)** and **Latin (Caesar)** controls (`analysis/controls/`) and
the generator:

- **Menzerath–Altmann:** REAL ρ = −0.248; **generator FAILS** (ρ ≈ +0.02, wrong
  sign) — the one clear fidelity gap, but it is a length-conditioned **orthographic**
  regularity (ligature placement), *stronger in Voynich than in the NL controls*, not
  evidence of meaning.
- **Brevity/abbreviation law:** generator reproduces (~85% of the slope); the residual
  points *away* from ordinary language (Voynich is more concentrated than English/Latin).
- **Long-range correlations (highest stakes):** real shows persistence above shuffle
  (DFA α ≈ 0.67; return-interval Hurst ≈ 0.72) — *replicating the papers* — but two
  surrogate tests (trend+iid; block-local shuffle) prove it is **compositional
  nonstationarity (drift), not sequential dependency**, and the magnitude often
  **exceeds** English/Latin → points to a mechanical origin, not language.
- **Verdict:** no published pro-language signature breaks the meaning-free generator;
  the only gaps (Menzerath, drift granularity, local repetition) are mechanical and
  meaning-free.

## 4. `analysis/payload_mdl/` — does the text CARRY a message, or exhaust it?

Information-theoretic floor↔ceiling discriminator, held-out by folio, with **positive
controls**: self-generation **floors** and, as **message ceilings**, a real English
message mapped through a verbose cipher + a homophonic letter cipher.

- The manuscript sits **at its self-generation floor** on held-out cross-entropy
  (9.21 bits/token = its page-local floor exactly), on non-stationarity, and — the
  sharpest axis — on long-range mutual information, where a real message (even 2×
  verbose) shows ~1.5–2× the manuscript's MI. REAL is **≈ 0% of the way** from the
  self-gen floor to the message ceiling on all three discriminating axes.
- **Observational-equivalence ceiling made concrete:** a marginal-matched homophonic
  letter cipher that genuinely carries a message also collapses to the floor — so an
  information-thin cipher cannot be excluded by internal statistics.
- **Probabilistic verdict (information content only):** ≈ 85% self-generation OR an
  information-thin/context-free cipher observationally equivalent to it; ≈ 15% carries
  an enciphered text; a **redundancy-preserving** message cipher < ~3%. A narrowing of
  odds, not a proof — the clean break needs an external anchor, which the project
  searched for and did not find.

## 5. Supporting: `analysis/state_independence/`, `analysis/word_frequency/`
Category-level state-transition (near-zero grammar) and word-frequency / hybrid
analyses that corroborate the above (low conditional entropy, concentrated vocabulary).

---

## What this battery establishes (and its limits)
- **Fair nulls + real-language positive controls** are provided and reproducible — the
  two things a skeptical reviewer most demands in the meaning-vs-gibberish debate.
- Every language-like statistic tested is **matched, or exceeded in an un-language-like
  direction, by a meaning-free drift+copy generator**; the few fidelity gaps are
  mechanical (orthographic ligature placement, drift granularity, local copying), not
  semantic.
- **Limit (stated plainly):** internal statistics cannot exclude an information-thin,
  redundancy-destroying cipher — it is observationally equivalent to self-generation.
  The claim is therefore **sufficiency and parsimony** ("no detectable message-shaped
  payload above the self-generation floor; a real message of the kind a 15th-century
  text would encode would have been detectable"), never "proven hoax."
