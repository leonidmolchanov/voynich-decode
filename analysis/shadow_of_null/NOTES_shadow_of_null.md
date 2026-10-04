# Shadow layer vs strict null-gate: is "shadow" a method hallucination?

Date: 2026-09-30. Read-only. No merge/promotion run. No GPU/remote process touched.
Data source for Part 2: `WORKING/hypotheses/x10u_full_symbolic_factorization_v3/full_symbolic_factorization.tsv`
(23,859 rows). Script: `build_shadow_of_null_metrics.py` in this directory. Raw numbers:
`metrics_shadow_of_null.json`. (Internal paths like `WORKING/…` are the original
inputs; they are not shipped — the shipped script reads
`data/factorization/full_surface_factorization.tsv`, per `../README.md`.)

## 0. Key structural fact discovered while doing this (governs the whole verdict)

`audited_factor` in `MASTER/accepted/strict_anonymous_factor_v1.tsv` (the thing the strict
null-gate predicts) **is literally the same string** as the "molecule"
(`<body glyphs>=>S<state>`) that `tmp/shadow_analysis/FINDINGS.md` calls the shadow layer.
Example: surface `pcheol` -> `audited_factor = "ch e o=>S4"` = shadow's `body=>state` for that
surface. Confirmed by independently re-implementing the tokenizer (the project's internal
`edge_state_machine` tokenizer — not shipped; the same `MULTI=("cth","ckh","cph","cfh","ch","sh")`
rule is reimplemented in the shipped `src/voynich_generator/vgen_lib.py` and in
`build_shadow_of_null_metrics.py`) + a last-glyph state table, and reproducing
`audited_factor` from nothing but the raw surface string on **16,684/16,684 = 100.000%** of
`STRICT_ACCEPTED` rows (99.36% body-match / 99.79% state-match across all tiers, the small gap
being ensemble/forced arbitration cells, exactly the risk zone the task asked to weight).

Consequence: shadow and strict are **not two independent things to cross-validate** — strict's
null gate scores a classifier's ability to recover the very body+state re-encoding that shadow's
EDA studies. This matters for the verdict in section 3.

## 1. Strict null-gate baseline (existing result, NOT recomputed; only read + smoke-verified)

Source: `family_gate.json` under the accepted production directory
(`artifacts/vast_53223571_mirror/x10s_safe/data/x_v10s_full_chain_null_amended_prod_v1/`,
independently byte-verified in `COMPAT/reports/X_V10S_CORRECTED_999_NULL_REUSE_VERIFICATION.md`)
and `ANALYSIS_REPORTS/results/X_V10S_CANDIDATE_ACCEPTANCE_AUDIT.md`.

- 999 deterministic null replicates, all present and hash-verified (`null_0000.json`..`null_0998.json`).
- 15 eligible calibration families (>=100 OOF calls, every fold >=20 calls); **15/15 pass**.
- **Observed precision = 1.000000 for every one of the 15 families** (e.g. 2993/2993, 965/965,
  432/432, down to the smallest eligible family 144/144) — zero OOF errors, comfortably above the
  0.999 gate and the per-fold 0.995 floor.
- **Null max correct vs observed correct**: null replicates never got close. Worst case, family
  `S2|...|G`: observed 212/212 vs null max 23/999 replicates; most families: observed in the
  hundreds-to-thousands vs null max single digits or 0.
- **Null median <= 10% of observed**: satisfied everywhere; worst case 5.66% (`S2|...|G`), most
  families 0.0-1.6%.
- **Studentized score vs Westfall-Young max-T threshold**: threshold (99.9th pct of the 999
  replicates' omnibus max-T) = **22.3159**. Observed family T ranges **72.26 (min) to 4997.57
  (max)** — every family clears the threshold by >=3.2x, the top family by ~224x.
- Finite-randomization Westfall-Young adjusted p-value = **exactly 0.001** for all 15 families
  (the floor of a 999-replicate test: `(1+0)/(999+1)`, since 0 of 999 null max-T values reached
  ANY observed family T).
- Gate output status: `"FAMILY_AUTHORIZED_NOT_TRUTH_SCORED_NOT_PROMOTED"` — 319 residual rows
  (43 `S_NEW`) authorized, **not yet truth-scored at gate time**. The later, separately audited
  step (`X_V10S_CANDIDATE_ACCEPTANCE_AUDIT.md`, `MASTER/accepted/strict_anonymous_factor_v1.lock.json`)
  opened the reference and reports 284 exact / 35 blank / **0 mismatches**, growing the accepted
  core 16,556 -> 16,684 (+128, +0.536 pp coverage of the 23,859-cell universe).
- **Harness smoke check (run this session, `--stage smoke`, PASS)**: reconstructs the exact
  locked 15,154-call OOF prediction tape byte-for-byte (`observed_lock_exact_equal=true`),
  reproduces identical stats when run directly vs. via a spawned worker
  (`serial_spawn_exact_equal=true`), and the Fisher-Yates sampler correctly reaches both orderings
  of a swap and handles a singleton. This confirms the code+locked-input bytes are intact and
  match what produced the numbers above; it is not a re-run of the 999-null battery itself
  (not performed, per instructions — the existing hash-verified battery was read instead).

### What this gate DOES guarantee
Given the accepted `audited_factor` core as ground truth, the locked `FULL_CHAIN` propagation
classifier recovers held-out (physical-folio OOF) factor values, for well-populated calibration
families, at a rate that is astronomically improbable under a null that preserves the exact
algorithm, exact OOF folds, and exact stratification (hand/section/register/fold/factor-length/
freq-band) and only rotates *which already-accepted factor value* sits on *which cell within a
stratum*. It rules out: chance-level performance, fold leakage, and multiple-comparison
inflation across families (Westfall-Young). It is a **within-framework generalization /
leakage-control** result.

### What this gate does NOT guarantee
It says nothing about whether the **categorical scheme itself** (9 S-states from the last glyph,
body = interior glyphs) is a real linguistic/generative joint in the manuscript versus an
arbitrary-but-consistently-computed re-description of the surface. The null only permutes
*labels already drawn from the accepted factor vocabulary*; it never substitutes a different
categorization, and — as section 0 shows — since the factor value is a **deterministic, lossless
function of the surface string itself**, a classifier that is good at recovering/agreeing on
*surfaces* across independent transcription/architecture passes will automatically look "good" at
recovering *any* deterministic re-encoding of those surfaces, including an arbitrary one. The
gate is best read as strong evidence of **cross-architecture transcription-recovery consistency**,
not as validation of the 9-state/body-split scheme's meaningfulness. That is exactly the gap
Part 2 probes.

## 2. Shadow-of-null control (new, this task)

Same deterministic rule (tokenize EVA surface with the project's own multi-glyph tokenizer;
body = interior tokens; state = table(last token), catch-all `U[glyph]` for anything outside the
9-class table) applied to three corpora, matched word count (23,859), 50 replicates each for
the two nulls:

- **(a) REAL**: actual surfaces from the TSV.
- **(b) WORD-INTERNAL SHUFFLE null**: each word's own glyph tokens permuted in place (same
  per-word length + glyph multiset, order destroyed).
- **(c) GENERATOR null**: 1st-order glyph Markov chain incl. START/END, trained on the real
  corpus's own glyph-bigram statistics, sampled to the same word count.

| metric | real | shuffle mean±sd | z (real vs shuffle) | generator mean±sd | z (real vs gen) | verdict |
|---|---:|---:|---:|---:|---:|---|
| H(state), bits | 2.169 | 3.388±0.006 | **-202.9** | 2.169±0.009 | 0.08 | ending-channel skew is REAL (shuffle destroys it; generator trivially matches because it was trained on this exact stat) |
| top-1 state share | 0.4925 | 0.2130±0.0021 | **+131.6** | 0.4927±0.0028 | -0.09 | same — REAL positional effect (word-final glyph identity), not a labeling artifact |
| n distinct body types | 1,836 | 6,261±30 | -146.7 | 4,570±61 | -44.7 | real vocabulary far more concentrated than either null — REAL reuse |
| TTR (body types / tokens) | 0.0770 | 0.2624±0.0013 | -146.7 | 0.1915±00026 | -44.7 | same |
| hapax rate (of body types) | 63.2% | 71.4%±0.3 | -23.9 | 80.9%±0.5 | -37.6 | real repeats specific bodies more than either null — REAL |
| empty-body rate | 9.64% | 9.64%±0.00 | 0.00 (trivial: shuffle can't change word length) | 27.4%±0.4 | -50.5 | shuffle comparison mechanically uninformative here; generator's length distribution is not well matched (flags a generator-calibration caveat, not a manuscript finding) |
| H(body), bits | 7.302 | 9.771±0.007 | **-380.6** | 7.266±0.040 | **+0.89 (n.s.)** | real's raw entropy shape is statistically indistinguishable from a memoryless bigram generator — the gross "how much information is in body-type frequencies" is largely a generic consequence of local glyph statistics, NOT evidence of extra structure by itself |
| top-10 coverage (non-empty bodies) | 32.4% | 19.0%±0.1 | +112.7 | 33.0%±0.4 | **-1.8 (n.s.)** | at the *small*-template scale, "a handful of templates cover a third of body mass" is essentially reproduced by a corpus-matched Markov generator with zero knowledge of real words — **method/statistics-imposed, hallucination risk** |
| top-50 coverage (non-empty bodies) | 62.8% | 35.3%±0.1 | +191.5 | 52.8%±0.4 | **+22.9 (real > both, but generator closes most of the shuffle gap)** | real exceeds both nulls, but roughly 2/3 of real's edge over shuffle is already explained by local bigram statistics alone; a real, smaller (~10 pp), statistically solid residual remains above the generator |
| edit-1 "has a neighbor", fraction of DISTINCT non-empty body TYPES | 90.5% | 91.4%±0.2 | **-4.0 (real < shuffle!)** | 70.1%±0.7 | +30.3 | the headline "almost every template has a near-neighbor" (paradigm-ladder claim) is **NOT manuscript-specific at the type level** — a pure letter-shuffle null reproduces (in fact slightly exceeds) it; this is a small-alphabet/short-string combinatorial inevitability, a genuine **hallucination-risk** metric |
| edit-1 neighbor, fraction of non-empty body TOKEN MASS | 99.19% | 97.49%±0.06 | +27.9 | 92.10%±0.20 | +35.0 | statistically real but the absolute gap vs shuffle is tiny (1.7 pp) and all three corpora sit near a ceiling (92-99%) — significance here is a sample-size effect (sd~0.0006), not a large practical effect |

Full per-metric real/null-mean/null-sd/z/min/max is in `metrics_shadow_of_null.json`.

### Bottom line on "how much of shadow's structure survives on null corpora"

Split roughly into three buckets:

1. **Manuscript-real, survives both nulls, large effect**: the skewed 9-state ending-channel
   distribution (final-glyph identity is genuinely non-random — some glyph, in this scheme
   named S8/"y", disproportionately occupies the LAST position of a word, and this evaporates
   the instant word-internal order is scrambled even though the same letters are still in the
   same word). Also: the degree of exact body-string reuse (TTR/hapax/type-count) is far beyond
   either null, including the bigram-matched generator — i.e., real scribes repeat specific
   multi-glyph strings more than local letter-transition statistics would predict (consistent
   with FINDINGS.md's independent "molecule-sequence adjacent MI = 38% of H1" local-copying
   result, now corroborated by an unrelated method).
2. **Partly real, partly generic**: top-50-scale "template coverage of body mass." Real exceeds
   both nulls, but most of its excess over pure letter-shuffle is already delivered by a
   memoryless bigram generator; only a smaller residual (~10 pp, still solid, z~23) is left once
   you control for generic local-statistics templating.
3. **Method-imposed / hallucination-risk, reproduced by null almost as well or better**: (a) the
   overall entropy/"shape" of the body-frequency distribution (matches a bigram generator, z=0.89);
   (b) the small-template (~10) coverage number (matches generator, z=-1.8); (c) the "almost every
   template has an edit-1 neighbor" ladder/paradigm claim at the type level (matches or is
   exceeded by a pure letter-shuffle null, z=-4.0). These three numbers, taken alone, would look
   identical on scrambled or synthetic inputs and should NOT be cited as evidence of a designed
   templating/paradigm system without the caveat above.

## 3. Honest verdict

**Is the strip-first/last-glyph relabeling itself invented content?** No. It is a lossless,
deterministic, verified-bijective re-encoding of the surface (surface = first-glyph + body +
last-glyph, exactly, for every word; empirically confirmed at 100% fidelity on all 16,684
strict-accepted cells by reproducing `audited_factor` from nothing but the raw surface string).
No information is hallucinated by the relabeling step, and no meaning is being claimed by it
either.

**Is the shadow layer partly a hallucination of the method?** Partly, yes — specifically in the
IMPOSED 9-state categorical scheme and in several of its most narratively appealing claims:
- The "paradigm ladder" claim (near-universal edit-1 connectivity of body templates) is largely
  or entirely a combinatorial inevitability of a small alphabet and short strings — a pure
  within-word letter-shuffle null reproduces it fully.
- The "small template covers a big chunk of body mass" claim, at the scale actually usually
  quoted (top ~10), is reproduced by a generator that has zero access to real word identity and
  only knows the corpus's own glyph-bigram statistics — this is a property of skewed local
  transition probabilities, not of authored templating.
- The overall entropy/shape of the body-type distribution is statistically unremarkable relative
  to that same generator.

**Is any of it manuscript-real, not method-imposed?** Yes, and it survives the harshest control
used here (the generator, which shares the corpus's own local statistics): the skew/dominance of
the ending-channel (final-glyph class) is a genuine positional regularity, not an artifact of
labeling; and the sheer degree of literal body-string reuse (low TTR/hapax, small realized
vocabulary versus a matched generator) shows real local copying/repetition beyond what
one-step glyph statistics predict — the same phenomenon FINDINGS.md flagged independently via
adjacent-word mutual information.

**Does the strict null-gate rule out the hallucination-risk part?** No, and it was never designed
to. The strict gate is a within-framework label-permutation/leakage/multiplicity control on a
classifier that predicts `audited_factor` values that ALREADY use the 9-state/body scheme — and
since that scheme is a deterministic, lossless function of the raw surface, the gate's
extraordinary significance (T up to ~5000, p_adj = 0.001 floor) mainly demonstrates that
independent transcription/architecture passes converge on the same surface glyphs (a real and
useful cross-architecture consistency result), not that the 9-class ending scheme or the
body/edge split carve the manuscript at a linguistically or generatively meaningful joint. A
gate PASS and a "partly method-imposed categorization" finding are logically compatible; they
answer different questions. The new shadow-of-null control in this note is the more relevant
(and considerably less favorable, in places) test for the hallucination question, and it should
be read alongside, not replaced by, the strict PASS.

No meaning/plaintext claims are made anywhere in this note, consistent with the project's own
`official_plaintext_claim: false` framing.
