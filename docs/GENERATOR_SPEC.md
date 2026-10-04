# The generative "machine" behind Voynichese — a sufficient minimal generator

Date 2026-09-30. Read-only on source data; all writes under this directory.
No meaning / plaintext claim is made anywhere. This note **exhibits a SUFFICIENT
minimal generator** whose explicit emission tables, word-template automaton, and
copy-mutate/reset process reproduce the REAL manuscript signals identified by the
prior shadow-analysis — it is **not** a claim of THE unique historical device
(generator-level observational equivalence is stated plainly in §6).

Data: `data/factorization/full_surface_factorization.tsv` (23,859 tokens),
joined to the Currier A/B markup in `metadata/currier_ab_map.md`. **Currier A and
B are a statistical language/dialect distinction in Voynichese, not a proven
scribal-hand assignment** — the number of scribes is contested (see
`PRIOR_WORK.md`); the generator is simply fit separately for the A and B token
sets. (A/B token totals differ between the molecule layer and the word layer
because they count different units.) The tokenizer and the 9-state ending table
are implemented in `vgen_lib.py`; null baselines are in `results/null_test/` and
the Montemurro code in `src/montemurro/`.

Files (in `src/voynich_generator/`): `vgen_lib.py` (loader/tokenizer/slot view),
`generator.py` (the machine + `spec.json` emitter), `spec.json` (emission tables),
`validate.py` (writes `validation_results.json`), `freechoice.py`
(`results/freechoice_results.json`), `heldout.py`, `calibrate.py`, `eda.py`.

---

## 1. The machine, in brief (the "generation set")

A word (molecule = `body glyph-tokens => S<ending-state>`) is produced by, per
physical line in manuscript order:

```
for each token slot in the line:
  DECIDE  copy-or-fresh          (Bernoulli p_copy, per hand)
    COPY : pick a molecule from the rolling recency buffer at lag k
           (near-weighted: with prob w_near k∈{1,2,3}, else k~U[1..window]);
           with prob p_mut apply ONE structured single-glyph edit
           (del 35% / sub 34% / ins 31%, edited glyph from the vowel+gallows
            operator set {o,e,a,k,t,ch,d,i,l}; rare 5% ending-state flip).
    FRESH: WORD-TEMPLATE AUTOMATON — draw body LENGTH from the per-hand length
           distribution, then fill that many interior glyph-tokens with a
           glyph-token Markov chain (2nd-order where the context is well
           supported, else 1st-order; ^=start), then draw the ENDING STATE from
           P(state | last-body-token) with a line-initial (LAAFU) blend.
  append to rolling buffer; reconstruct surface = first-glyph + body + last-glyph
    via P(first | body-first-token)  [the qo- rule]  and  P(last | state).
```

Two timescales, both taken from the data: the **ending/state channel resets each
line** (LAAFU line-initial prior — `machine_structure` "reset at line boundary");
the **copy/vocabulary memory is a long rolling buffer** (drift window) that
carries across lines and pages — this is what manufactures section-scale
Montemurro clustering *without* any positional key. The **glyph-token transition
table IS the emission set**; the interpretable slots (prefix-o / onset / e-ladder
/ i-ladder / coda / ending) are induced views of it, tabulated in `spec.json`.

### Emission tables — the A vs B contrast (full tables in `spec.json`)

| quantity | Currier A | Currier B |
|---|---|---|
| ending-state marginal S8 (`-y`) | **0.369** | **0.577** |
| next-most endings | S4 .186, S6 .170, S5 .166 | S4 .142, S5 .116, S6 .104 |
| H(state) / H(state\|body) | 2.42 / 1.06 b | 1.94 / 0.68 b |
| body-Markov start `^→` | o .31, a .13, e .11, k .09, t/ch .07 | o .29, **e .20**, k .10, t .07, a .07 |
| qo- rule: P(first=`q` \| body starts `o`) | **0.34** | **0.76** |
| e-ladder (#e in body: 0/1/2) | .75 / .18 / .07 | **.46 / .36 / .16** |
| i-ladder (#i: 0/1/2) | .85 / .04 / **.12** | .89 / .06 / .05 |
| mean body length (tokens) | 2.70 | 3.06 |
| copy-mutate params (fit) | p_copy .60, p_mut .55, w_near .24, win 600 | p_copy .58, p_mut .58, w_near .20, win 650 |

This is the classical A/B "dialect" as a **coordinated shift of a shared
skeleton**: same 9-state ending alphabet, same glyph inventory, same
qok-/qot-/ch-/gallows template — B just turns up S8/`-y`, the `qo-` prefix, and
the `e`-ladder (the `-edy` machine), while A keeps more S6/S4/S5 endings, benched
gallows, and the `ii`/`aiin` family. The generator reproduces this by fitting the
two hands separately; nothing else in the architecture differs.

---

## 2. Validation fidelity — what it hits and misses (honest)

Synthetic corpus generated at matched size (23,859 tokens) over the **real
page/line/section/AB layout** (so section labels overlay by position, exactly as
Montemurro requires) and, separately, on **held-out unseen pages** (fit on 92
pages, generate over the other 92). Raw numbers in `validation_results.json`.

> **Read this table correctly (important).** The in-sample rows — ending-state,
> H(state), glyph-unit JS, body-length, local copy — are **fit diagnostics**: the
> emission/length/state tables are maximum-likelihood *fit on the full corpus and
> then measured on it*, so close agreement there is largely built-in and is NOT
> independent evidence. The **validation of record is the held-out result** (fit on
> 92 pages, test on the unseen 92 — `results/heldout_validation_results.json`;
> reproduce with `python3 src/voynich_generator/heldout.py`): copy/state structure
> **transfers** to unseen pages (S8, exact-repeat, edit-1 close), while vocabulary
> concentration misses out of sample too. On every quantity NOT directly fit (V,
> TTR, hapax, Zipf, Currier-A/B Montemurro) the model misses — the honest pattern of
> a *sufficient*, not a *fitted-perfect*, generator.
>
> **On Montemurro significance.** The excess-MI z-scores in `validation_results.json`
> (z≈100+) are **not** meaningful effect sizes — they reflect the tiny across-shuffle
> SD at `n_shuffle=100`; read them only as empirical *p* < 1/(n_shuffle+1). The excess
> is moreover **reproduced by the meaning-free generator** (0.58–0.96×), so it is
> **non-diagnostic** of language either way. The lag-MI null fully shuffles the stream
> (conflates composition with sequence — see the note after the table and `results/null_test/`).

| statistic | REAL | SYNTH | verdict |
|---|---:|---:|---|
| ending-state S8 share | 0.493 | 0.479 | **HIT** |
| H(state), bits | 2.165 | 2.234 | **HIT** |
| body glyph-unit freq (JS vs real) | — | **0.005 b** | **HIT** (near-identical) |
| body-length dist (len 0/1/2/3/4) | .097/.192/.235/.236/.151 | .059/.226/.230/.224/.156 | **HIT** (mode + tail; slightly few empties) |
| local copy: exact-repeat (mol, adj) | 0.0245 | 0.0273 | **HIT** |
| local copy: edit-1 body (adj) | 0.166 | 0.149 | **HIT** (near) |
| MI-excess by lag (mol) | lag1 .18, lag2-3 ~.09 | lag1-3 .04-.05, **lag≥4 ~0** | **HIT** (local only; see note) |
| Montemurro section-6 excess (mol) | 0.273 | 0.193 | ~HIT (0.71×) |
| Montemurro block-20 excess (mol) | 0.296 | 0.286 | **HIT** (0.96×) |
| Montemurro Currier A/B excess (mol) | 0.194 | 0.113 | PARTIAL (0.58×) |
| molecule TTR / vocab V | 0.102 / 2432 | 0.188 / 4475 | **MISS** (see below) |
| molecule hapax rate | 0.635 | 0.542 | **MISS** (undershoot) |
| Zipf slope (mol) | −1.19 | −0.96 | **MISS** (shallower) |
| held-out S8 / exact-repeat / edit-1 | 0.489 / .024 / .163 | 0.473 / .027 / .160 | **HIT** (transfers to unseen leaves) |

**The one honest, structural MISS — vocabulary concentration.** The generator
over-produces distinct types (V, TTR too high) and under-produces hapax and the
Zipf steepness. This is **exactly** the manuscript-real signal that
`shadow_of_null` and `montemurro` independently flagged: the real corpus draws
from a **more concentrated stock** than any local-statistics generator (real
needs only ~1,800-2,400 types where a bigram/copy model needs ~4,500). It is a
genuine property the machine does **not** capture, and raising mutation to fix
hapax only worsens V (the hapax↔V trade is intrinsic: real is *simultaneously*
high-hapax and low-V, i.e. its non-hapax mass is unusually re-concentrated). This
is reported as a real negative, not swept under the rug.

**Note on "no long-range MI."** My crude metric (raw MI minus a full-shuffle
floor) conflates local copy with topic/section composition, so REAL stays ~0.08-
0.09 at *all* lags (its section clustering contributes MI everywhere). The
generator, by contrast, shows excess only at lag ≤ 3 and ~0 at lag ≥ 4 — it has
**no long-range mechanism by construction** (memoryless drift buffer, no
positional key). The definitive "no long-range sequential structure" result lives
in `null_test/` (real ≤ composition-preserving null at lag ≥ 4); the generator
satisfies it trivially. The generator also reproduces the near-zero **category
grammar** (state adjacent-MI) by design.

**Currier A/B undershoot (0.58×) and surface-layer undershoot.** A single
homogeneous drift process per hand does not fully reproduce the sharpness of the
A/B partition (`montemurro` predicted this: a two-drift-regime model would be
needed). Surface-layer Montemurro undershoots more than molecule because surface
reconstruction (first/last-glyph re-attachment) adds variance — the molecule
layer is the primary, clean target and the fitted layer.

---

## 3. What was "fed on input" — operator free-choice entropy & driver tests

`freechoice_results.json`. Two questions: how many bits/word did the operator have
to *decide*, and is any of that decision *recoverable* from a driver?

### (A) Free-choice budget
- **~7.4 bits/word (molecule)** had to be supplied, model-free estimate: 68% of
  real tokens are **not** locally copyable (fresh, priced at the memoryless
  entropy of that subset, ~8.6 b), 7% are exact repeats of the last 3 words, 24%
  are edit-1 of the last 3. Local copy compresses the stream by only **~0.8
  bits/word** below the memoryless bound (8.16 b) — i.e. ~90% of the per-word
  information is *not* delivered by local copying; it is free draw from the
  template.
- Under the fitted machine, the "free invention" branch (fresh word) costs
  **~8.5-8.8 bits/word** (body ~7.4-7.9 + ending ~1.0), incurred on the ~40-42%
  of slots that are generated fresh; the copy branch is cheap local reuse
  (pick a recent word ± one glyph). Copy-vs-fresh is a ~1-bit coin.

### (B) Driver tests on the real stream — is the choice driven or random?
| candidate driver | measured | verdict |
|---|---:|---|
| previous ending-state → current (category grammar) | **0.013 b = 0.6% of H(state)** | **no grammar** |
| line-position → ending-state (LAAFU reset) | 0.018 b | tiny, real |
| line-position → body-length | 0.007 b | negligible |
| local copy: token is exact/edit-1 of last 3 (within line) | **31.5%** (41.9% within page) | **the one real local driver** |
| f57v period-17 cycle → state (global) | MI 0.0075 b vs null 0.0079±0.0006, **z = −0.72** | **no period-17 key** |
| strongest period 2..30 → state | T29, 0.012 b | negligible (≈ line-length artifact) |

**Answer to "what was fed on input":** ≈ 7-8 bits/word of operator free choice,
of which roughly **two-thirds is genuinely fresh word-invention** (a draw from the
word-template automaton) and **one-third is local reuse** of a recent word ± a
single-glyph tweak. The **only recoverable drivers are LOCAL** (a copyable recent
word, ~1/3 of tokens) and a **weak line-position reset** (< 0.02 b). There is **no
category-level grammar** (0.6%), **no repeating cycle / key** (period-17 at null,
z ≈ 0; no period 2-30 stands out), and **no long-range structure**. The "input"
is operator free-choice + local copy + line resets — **it does not look like a
decodable message stream**. (The global period test does not examine the f57v
*locus* itself, which prior work froze as a separate secondary apparatus
candidate; it only rules out a *manuscript-wide* period-17 driver, and finds
none.)

---

## 4. Physical-procedure sketch (ONE sufficient realization, not THE device)

A fifteenth-century operator could implement this spec with paper tools alone
(tying to the machine's H_t/C_t control-stream framing used above):

- **A word-template table / grille** (the emission set): columns for prefix-o,
  onset consonant (k/t/ch/sh/gallows…), a vowel-run box, an e-tally and i-tally
  (how many `e`/`i` to lay down — the ladders), a coda, and an **ending wheel**
  of the ~8 terminal glyphs skewed to `-y`. Reading a row = writing a word. Two
  such tables (or two settings of one) = Currier A vs B.
- **A "recent words" strip** = the rolling buffer: the operator frequently just
  re-copies a word written a few tokens back and changes one stroke
  (+e / +d / k↔t / +o) — the dominant real edit operators. This supplies the
  local-copy signal and, via copy-of-copy, the section-scale drift.
- **A line-reset rule**: at each new physical line, bias the first word's ending
  (LAAFU) — a soft re-initialization of the "ending wheel," exactly the H_t reset
  at the line boundary the machine notes require.
- No key, no volvelle offset schedule, no lookup of an external message is needed
  to match the statistics — the operator's own free choices (which template row,
  copy-or-invent, which one-glyph tweak) are the entire "input."

A volvelle/grille with an offset **key** is *also* a sufficient realization (it
would look identical on these statistics) — which is the point of §6.

---

## 5-6. Honest bounds — how completely are the mechanics recovered?

**Recovered (high confidence):** the layered architecture is pinned down — a
compact per-hand word-template automaton (glyph-token transitions with an
explicit length model and a low-entropy, body-conditioned ending channel), riding
a local copy-with-single-glyph-mutation process, with a per-line ending reset and
a page-scale vocabulary drift. This reproduces the *real* signals the project
isolated: skewed S8 ending channel, glyph-unit frequencies, body-length shape,
the small-but-real local copy at lag ≤ 3, near-zero category grammar, Montemurro
block clustering at real level — and it *transfers to held-out pages*.

**Under-determined / not recovered:** (1) **Vocabulary concentration** — the real
lexicon is markedly more re-used (lower V / higher hapax / steeper Zipf) than a
local-statistics generator produces; some extra concentration mechanism (a
genuinely small closed word-stock, or heavier memorized reuse) is real and
missing. (2) The **sharpness of the A/B split** (a single drift regime per hand
undershoots it). (3) **Which** physical mechanism, if any — table vs grille vs
keyed volvelle — is completely under-determined; no device is claimed to exist.

**Observational-equivalence ceiling (stated plainly):** many generators reproduce
the same statistics. We exhibit a **sufficient minimal generator**, not the unique
historical one. On the "input" question the evidence (this note + `results/null_test/`
+ `analysis/montemurro/` + `analysis/payload_mdl/`) converges: the recoverable content of Voynichese
is **operator free choice + local copy + line/page resets**, ~7-8 bits/word of
largely undriven decision — **not** a decodable long-range message, and **no**
deterministic driver (previous-state grammar, positional key, or period-17 cycle)
was found above its null. This does not *prove* the absence of a per-word verbose
cipher (that wall stands — see `LIMITATIONS.md` and `analysis/payload_mdl/`), but it shows the machine's
"input" is behaviourally indistinguishable from free choice with local reuse.
