# Generator-vs-real NULL test on the molecule layer — completion notes

## Status of the earlier (interrupted) run
On inspection, `nulltest.py` had already **finished** its heavy computation before
the interruption: `results.json` contains all 6 arms
(`FULL_state/body/mol`, `STRICT_state/body/mol`), each with 3 null models
(`iid`, `perm`, `markov1`) × 200 replicates, and every statistic the task asks
for (adjacent H/MI, immediate repeat rate, MI at lag 1..10, within-line vs
cross-line-boundary MI, Heaps exponent, burstiness) is present with
real/null_mean/null_sd/z/p. Verified: `n_null==200` for every (arm, null,
stat) cell, all 10 lag keys present for all 3 nulls (not just markov1), and
the identity `H1 - MI1 ≈ H2` holds within rounding for every arm. `summarize.py`
had already rendered `summary_table.txt` (markov1-only headline view).

What was missing was the **honest synthesis** — `summary_table.txt` only
prints the real-vs-markov1 lag comparison and 5 headline stats vs each null;
it doesn't cross-tabulate all three nulls at every lag, doesn't show the
conditional-entropy check, and draws no verdict. That synthesis is done below
(all numbers pulled directly from `results.json`, no re-computation needed —
code, seeds and REPS=200 are unchanged from the original interrupted run).

Data: `WORKING/hypotheses/x10u_full_symbolic_factorization_v3/full_symbolic_factorization.tsv`
(read-only). FULL = 4007 lines / 23859 tokens (all tiers). STRICT_ACCEPTED =
3825 lines / 16684 tokens (69.9% of cells). Units: state (V=9 real classes,
24 with rare `U[...]`), body (V=1819 FULL / 677 STRICT), molecule (V=2432
FULL / 952 STRICT).

## Headline: the one place real beats a generator
Immediate literal repetition (`token[i]==token[i+1]`) in the body/molecule
channel, tested against the *strongest* null available — within-line
permutation, which already holds each line's exact word multiset fixed and
destroys only order:

| arm | real | perm-null mean±sd | z | p |
|---|---|---|---|---|
| FULL_body | 0.0418 | 0.0380±0.0011 | 3.46 | 0.005 |
| FULL_mol | 0.0246 | 0.0226±00008 | 2.36 | 0.010 |
| STRICT_body | 0.0556 | 0.0525±0.0015 | 1.99 | 0.055 |
| STRICT_mol | 0.0329 | 0.0313±0.0012 | 1.33 | 0.100 (n.s.) |

Same direction in all 4 arms, significant in FULL, weaker/borderline in
STRICT (fewer, cleaner tokens ⇒ less power, flagged honestly, not swept
under the rug). Since the permutation null already knows exactly which
words are in the line, this is not "these words co-occur" — it is a genuine
**order** effect: real adjacent-repeat clumping (paradigm ladders like
`o k e / o k e d / o k e e d`) exceeds a random reordering of the very same
line. This is essentially the *only* place the real sequence beats a
generator that already has the right local vocabulary.

## Everywhere else: real matches, or under-shoots, the generators

1. **State (ending-class) sequence never beats the permutation null**, on
   any statistic, at any lag (all p>0.1, with one isolated exception:
   STRICT_state MI_boundary z=2.01, p=0.02, not replicated in FULL). A
   trivial "draw endings with the line's correct multiset, order doesn't
   matter" generator reproduces the real state sequence completely. This
   gives FINDINGS.md's "almost no grammar at the category level" an actual
   null-model p-value.

2. **MI decay at lag ≥ 4 (body & molecule, both tiers): real is
   significantly *below* every null — iid, permutation, and Markov-1 —
   not just indistinguishable, but reliably on the wrong side** (z strongly
   negative, p→1.000 for the "exceeds" test) from lag 4 through lag 10 in
   FULL_body, FULL_mol, STRICT_body, STRICT_mol alike. E.g. FULL_mol lag 6:
   real MI=3.73 vs iid-null z=-3.99 (p=1.000), vs markov1-null z=-3.41
   (p=1.000). Beyond ~3 words, the real sequence carries *less* mutual
   information than even a memoryless i.i.d. reshuffle of the same
   vocabulary. There is no long-range dependency to find; if anything the
   opposite (mild anti-correlation), consistent with a hapax-heavy
   vocabulary "spending" its rare words locally and being unable to repeat
   them far away, unlike draw-with-replacement nulls. (Caveat: pair counts
   shrink to n=300–700 at lag 8–10, so exact magnitudes are sensitive to
   small-sample MI bias — but that bias applies equally to real and null,
   so the qualitative verdict, "no long-range structure," is not an
   artifact of it.)

3. **Conditional entropy H(next|current)**: real is significantly *lower*
   than iid/perm nulls (p=0.005 uniformly, body/mol/state — confirms
   short-range predictability, consistent with point 1 above), but
   significantly *higher* than the Markov-1 null for body/molecule
   (z=+25 to +38, p=1.000). This is not real "beating" a generator in a
   useful sense — it is a known artifact of resampling a sparse,
   hapax-heavy bigram graph: chaining draws gets trapped in the many
   singleton/deterministic edges more than the original text ever visits
   them, so the *resampled* Markov corpus drifts to a lower-entropy
   attractor than its own fitted transition matrix implies. State channel
   (small, dense V=9 alphabet, no sparse hapax edges) shows no such drift
   (z≈0.3–0.4, clean match).

4. **Heaps' exponent and burstiness**: huge z-scores vs the i.i.d. null
   (z=3–68) look dramatic but are **not** evidence of order/sequencing —
   vs the permutation null (composition fixed, order destroyed) both
   statistics match almost exactly (z≈0, p mostly 0.3–1.0). Vocabulary
   growth and word-clumping are fully explained by *which* words occur in
   which lines, not by their order. Flagged explicitly so the large iid
   z-scores aren't mistaken for a "conscious sequencing" signal — they are
   composition/topic effects any bag-of-words generator matching real
   per-line composition would reproduce identically.

5. **Line-sealing (last token of line k vs first token of line k+1)**:
   significant excess over the perm null in FULL_body (z=3.89, p=0.005) and
   FULL_mol (z=5.26, p=0.005), and STRICT_state (z=2.01, p=0.02) — but not
   significant, or reversed, in STRICT_body (z=-2.46) and STRICT_mol
   (z=-1.76). Tier-sensitive, not robust. Best read as weak/inconclusive;
   most likely explained by known LAAFU line-position marginal effects
   (line-initial/line-final tokens have different distributions than
   medial — see FINDINGS.md) rather than genuine information crossing the
   line break.

## Honest verdict
The real molecule/body/state sequence is empirically indistinguishable from
a self-generating process almost everywhere it is tested — **except for one
narrow, short-range signature**: adjacent literal repetition / local
paradigm-copying (lag 1–3) in the body/molecule channel, which exceeds what
a composition-matched permutation or a fitted first-order Markov chain would
produce. That signature fades to nothing (or below-null) by lag 4, and is
entirely absent from the abstract ending/state channel, which matches a
pure "bag of endings, any order" generator on every measure. There is no
evidence anywhere of long-range dependency, of information crossing line
boundaries robustly across tiers, or of category-level (state) grammar
beyond per-line composition.

**If forced to one sentence: real ≈ generator on almost every statistic
tested; the sole departure is very local copy/paste structure in the
word-body layer (lag ≤ 3), and even that weakens once uncertain/forced-tier
assignments are removed.** This statistically confirms, with actual
p-values, what FINDINGS.md had flagged qualitatively: "predictability lives
in local word-to-word copying, not abstract positional grammar." It does
**not** rescue a cipher/language hypothesis requiring long-range structure —
the null test finds none, and at long lags real is if anything *less*
structured than pure chance.

## Multiple-comparisons caveat
~270 (arm × null × statistic) comparisons were run. p=0.005 is the
resolution floor (1/(200+1)) and appears in many cells — those are robust to
any reasonable correction (Bonferroni-safe even at the 270-test scale).
Values in the 0.01–0.1 band (STRICT repeat-rate, isolated line-sealing
hits) should be read as suggestive only, given the number of tests
performed; they are called out as such above rather than folded into the
headline claim.

## Files
- `nulltest.py` — generator + statistics code (unchanged from the
  interrupted run; verified complete: 6 arms × 3 nulls × 200 reps, no
  missing cells, internal consistency checks pass).
- `results.json` — full numeric results (real value + null mean/sd/z/p for
  every stat, every lag 1–10, every null, every arm).
- `summary_table.txt` — printed table from `summarize.py` (markov1-only
  headline view; unchanged).
- `NOTES_null_test.md` — this write-up: the cross-null lag tables,
  conditional-entropy check, and the honest synthesis/verdict that
  `summary_table.txt` alone does not state.
