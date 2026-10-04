# The machine tape: a new data layer

## What changed

Conventional analysis starts from a transcription and implicitly treats
space-separated groups as words. Here that assumption is dropped. The base unit
is an aligned cell: a physical location in the manuscript that can be found in
several independent transcriptions and, where coordinates exist, on the scan.

A cell need not be a word or a letter. Mismatched boundaries are stored as 1:1,
1:2, or 2:1 blocks. Ambiguity is not removed by majority vote. The source
transcriptions remain unchanged; accepted corrections exist only as versioned
overlays.

## Layer numbers

- full reversible tape: 38,761 visible units, 5,359 loci, 203 leaf sides,
  zero round-trip errors;
- auditable denominator: 23,859 cells, 188 sides, 98 physical leaves;
- three transcription representations: 14,441 cells;
- four representations: 9,418 cells;
- visible surface types: 8,127;
- anonymous internal `X` types: 3,691;
- exact operations: 1,527;
- compact operations: 568.

These are the canonical counts; different documents measure different objects, so
the page/leaf numbers are not all the same by design: the **auditable denominator
is 188 leaf-sides (98 physical leaves)**; the **full reversible tape's 203 sides**
is a superset (it includes units the strict denominator excludes); the "202
folios" in some analysis `NOTES_*.md` is the earlier working snapshot; the "225
leaf-sides" in `metadata/currier_ab_map.md` counts every markup row including
foldouts; and the generator's "92 + 92 pages" (`GENERATOR_SPEC.md`) is the
held-out split of the denominator's sides.

## The universal production ladder

After removing the first and last sign, an internal frame remains. For 1,819
distinct frames a graph was built in which an edge means one insertion, deletion,
or substitution of a sign. The heaviest monotone chain of insertions is derived
without any given words:

`∅ → o → o k → o k e → o k e e → o k e e d`

The six steps have a total mass of 5,107 tokens, i.e. 21.4% of all 23,859 cells.
Filtered to strict, the same chain keeps 4,292–4,293 occurrences. A five-slot
template with 27 primitive choices covers 94.0% of the non-empty mass of internal
forms and 96.8% of the strict mass; an extended template — 97.9% and 99.6%
respectively.

This is not proven by graph connectivity alone. Under a length/unigram null,
short random strings also form a large connected component. What is scientifically
substantive is the specific heavy chain, the high concentration of re-used forms,
the survival of the chain after the strict filter, and the measured excess of
local one-edit neighbours.

## Why this is not "the S4 sequence"

The state number depends on the markup version. In the current nine-component
layer S8 means the ending `y` and S4 means the ending `l`; in an early
six-component automaton S4 denoted a different group. State numbers therefore
cannot be compared literally between versions.

In the full factorization S8 occupies 49.3% and S4 occupies 16.0%. In the
107-page overall atlas S8 is the central node, and the S8→S4 and S4→S8
transitions are almost mirror-symmetric: 4.9% and 4.8% of all transitions.
Meanwhile the adjacent mutual information of the state channel is only 0.071 bits,
or 3.3% of its single-symbol entropy. Consequently, what is universal is not a
fixed route over S-numbers but the production frame: a ladder of internal forms,
a short ending choice, and a state reset at the physical-line boundary.

## What a cell stores

For each cell the following are stored:

1. the physical address and leaf ID;
2. the source blocks IT2a, GC2a, FG2a, and CD2a;
3. the observed surface and segmentation alternatives;
4. the input and output line state;
5. the internal anonymous part `X`;
6. the structural factor and the provenance of its assignment;
7. the evidence status: soft, strict, or abstain;
8. the provenance of corrections and visual decisions.

`X` is a stable technical identifier, not a letter, a sound, or a translation.
The same internal form receives the same code on different leaves.

## Why factor and strict must not be mixed

The factor answers the question "which structural operation is observed here?".
Strict answers a different question: "by what evidence is this assignment
confirmed?". A soft model can give a factor to the whole corpus and still have no
right to promote a single new cell into strict.

Strict requires splitting by whole physical leaves, a closed target, predeclared
thresholds, matched nulls, independent observers, source/canonical auditing,
quarantine of disputed locations, and repeated replay.

## How the scientific question changes

Before factorization, similarity to language usually served as the initial reason
to look for language. After factorization, most of that similarity enters the
generative baseline: the slot frame, the line reset, short memory, re-use of
forms, the A/B modes, and local drift.

The new null hypothesis is therefore:

> The observed surface is produced by a compact structural process; the presence
> of a message is an additional hypothesis about the choice within that process.

To show meaning, it is not enough to reproduce Zipf's law, long-range
correlation, or a few plausible words again. A model is needed that:

- predeclares a key or mapping;
- works on the anonymous residual `X`, not only on raw EVA;
- predicts held-out physical leaves;
- is preserved across transcriptions and is consistent with the scan;
- explains the line reset, A/B, local memory, and the corrected boundaries;
- gives additional compression or accuracy beyond the generative baseline.

This is not a ban on decipherment and not a logical proof that there is no
message. It is a shift of the burden of empirical proof from external similarity
to a new predictive signal.

## Current and publication state

The release authority is **strict-v82: 23,859/23,859 cells = 100% structural
coverage**. The lock and audits are attached in the release:
`data/strict/strict_anonymous_factor_v82.tsv`
(SHA-256 `8a81b7a611f0f033f1072e8a5e67d0e9c7411807eee39d3715d02336e4112c56`) +
`.lock.json`, `results/strict_v82_v273_f27v_novel_interior_release_v1.json`,
`results/strict_v82_v273_postpublish_audit_v1.json` (`PASS_OFFICIAL_STRICT_V82_ACTIVE`,
residual 0) and the independent completion audit
`results/strict_v82_completion_audit.json` (`PASS_OFFICIAL_STRICT_100_COMPLETE`,
26/26 checks). The condition for declaring 100% (confirmatory folds + prediction
lock + independent audit of the last residual) has been met.

The historical step **strict-v21 (22,106/23,859 ≈ 92.65%)** is attached
separately as the previous step of the line and is not the current authority.
"100%" here is **structural coverage** (each cell has a reproducible anonymous
machine outcome), NOT translation, reading, or proven meaning.
