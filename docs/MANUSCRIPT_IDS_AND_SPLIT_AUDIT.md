# Numbering reference and split-unit audit

This file records the numerical audit of the split unit (the physical leaf) for
the visual corpus — so that folds do not leak between the recto/verso of the
same leaf.

## Normal forms

- physical leaf: `fN`;
- folio side: `fNr` or `fNv`;
- foldout panel: `fNr1`, `fNr2`, ...; normalized first to a side `fNr`, then to a
  leaf `fN`;
- locus: `<panel-or-side>.<source locus number>`;
- record ID: `<locus>:<aligned cell position>`;
- special: `fRos`, a separate group.

## The actual X10U audit

The training visual corpus (x10u image-reranker) contains:

- 199 `source_panel`;
- 185 values in the `physical_folio` column, which are actually side IDs;
- 96 true physical leaves after normalization to `fN`;
- 89 leaves have both sides in the corpus;
- of those 89 leaves, 64 have their sides assigned to different outer folds.

The builder code computes the fold as
`SHA256("X10U-OUTER|" + physical_folio) mod 5`, without normalizing `fNr/fNv` to
`fN`. This diverges from the preregistration text, which requires keeping the
whole physical leaf together.

## Scientific consequence

The current 30-epoch X10U run is a side-held-out engineering baseline. Its
checkpoints and predictions should be kept, but its OOF/null cannot be used for
strict-promotion under a physical-leaf held-out claim.

## Resolution (status in the strict-v82 release)

This audit is kept for transparency about a **defect in the superseded
engineering baseline (X10U)** and does NOT describe the current accepted core.
The accepted authority — **strict-v82 (23,859/23,859)** — rests on the corrected
leaf-held runs (outer/inner split strictly by `leaf_id`, recto/verso/foldout held
together, a new preregistration hash, clean OOF models), NOT on X10U. In other
words, the requirements in the "A corrected run must…" list below were satisfied
in the subsequent lineages, whose locks and audits are attached
(`data/strict/strict_anonymous_factor_v82.*`, `results/strict_v82_*`). X10U
remains an engineering baseline for speed/format tests but is excluded from the
strict evidence base.

A corrected run must:

1. add explicit `source_panel`, `side_id`, `leaf_id` fields;
2. build the outer and inner split by `leaf_id` only;
3. verify that the leaf sets in fit/calibration/OOF are pairwise disjoint;
4. keep recto, verso and all foldout panels together;
5. obtain a new preregistration hash before training;
6. run with clean OOF models that have not seen the opposite side of a held-out leaf.

Old X10U weights may be used for engineering speed and format tests, but not as
the OOF-parent of a corrected strict run, because they may already have seen the
verso/recto of the same held-out physical leaf.
