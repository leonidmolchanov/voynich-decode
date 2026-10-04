# Universal ladder of internal forms

> **Scope of the numbers.** The percentages below are diagnostics of TEMPLATE
> coverage of FORMS (what fraction of the word-form mass the v2/v3 template
> describes) and of local structure — **not** the headline strict-cell coverage.
> Strict cell coverage is separate: **strict-v82 = 23,859/23,859 = 100%** (see
> `data/strict/`, `results/strict_v82_*`). The numbers in this section are a
> snapshot of the analysis on the accepted layer; under v82 the "full layer" and
> the "strict layer" coincide (all cells are strict), and the historical
> "full/strict" distinction refers to earlier steps in the lineage.

## Verifiable result

The source object is 23,859 aligned cells. For each, the visible form is
decomposed into an initial sign, an internal frame, and a final state. Over the
1,819 distinct internal frames, an edit-distance-1 graph was built.

The heaviest monotone chain of single insertions:

```text
∅ (2323) → o (1781) → ok (213) → oke (138) → okee (326) → okeed (303)
```

Total mass of the six steps: 5,107/23,859 = 21.40%. The same chain, after
strict filtering, retains 4,292–4,293 occurrences.

## Compact derivation of forms

A five-slot v2 template uses about 27 primitive choices and covers:

- 20,243/21,536 = 94.0% of the non-empty mass of the full layer;
- 96.8% of the non-empty mass of the strict layer.

The extended v3 template covers 97.9% of the full and 99.6% of the strict layer,
but requires 39 primitives and is therefore worse in the compactness-to-coverage
ratio. V2 is the most economical of the tested variants, not the only possible
historical algorithm.

## Null control

A single giant component is not treated as confirmation of a generator.
Preserving length and sign frequencies, a random null produces 89.9–90.3% of
types in the giant component versus 86.7% in the real data. What is significant
is not overall connectivity but the concentration of the stock of forms, the
mass of the specific chain, and local order:

- real adjacent frames are closer than the null by 2.24% in the full layer and
  by 1.44% in strict;
- the fraction of adjacent pairs differing by exactly one change: 16.54% versus
  15.99% in the null, z = 3.13;
- the effect is robust but small and must not be described as the sole mechanism
  of the whole text.

## States S8 and S4

In the current layer, S8 is the final `y`, S4 is the final `l`. S8 dominates; S4
is a strong branch. In the 107-page atlas, S8→S4 accounts for 4.9% and S4→S8 for
4.8% of all transitions. In the earlier six-part version S4 had a different
meaning, so the historical state numbers are not stable class names.

The adjacent mutual information of the state sequence is 0.071 bits (3.3% of H1).
This rules out a strong claim of a single deterministic S-sequence. The
universal object is a compact grammar of internal form plus a local ending
channel and a line reset.

## Derived artifacts in this release

The ladder of internal forms is derived from the corpus; the public release
provides the corresponding verifiable artifacts:
- `data/factorization/full_surface_factorization.tsv` — the full factor layer;
- `results/null_test/` — the null tests;
- `src/voynich_generator/` + `docs/GENERATOR_SPEC.md` — the generator and its
  specification.

Detailed working notes (ladders, edge-state-machine) belong to the research
archive and are not part of the public release.
