# Methods

## Research status

This work is a semi-scientific computational investigation. It uses reproducible
measurements, closed (blind) checks, negative results, and control shuffles, but
it has not undergone independent peer review and does not replace palaeographic,
codicological, or historical expertise.

Language models and ML were used as tools for implementation, anomaly search, and
scaling the analysis. Hypothesis formulation, choice of null controls, splits by
physical leaf, the strict/abstain criteria, and interpretation of results were
determined by a human. A detailed disclosure is in `docs/AI_USE.md`.

## Unit of analysis

The denominator contains 23,859 aligned cells. A cell is tied to a physical leaf,
a line, a position, and several transcription representations. It is not declared
to be a word, letter, or morpheme. It is an addressable location in the
manuscript for which conflicting evidence and an alignment history are preserved.
The denominator spans 188 sides of 98 physical leaves: 14,441 cells have three
independent transcription representations and 9,418 have four. Alignment allows
1:1, 1:2, and 2:1 relations; unresolvable boundaries are not fixed by voting.

Splitting during training was done by physical leaf: fragments of one leaf must
not appear simultaneously in training and in independent evaluation.

## The new object of study

The full reversible tape preserves 38,761 visible units across 5,359 loci on 203
leaf sides and reconstructs the original surface with zero errors. The observed
form decomposes into an input state, an internal anonymous part `X`, an output
state, and boundary information. `X` is given no phonetic or semantic reading.

The resulting layer is needed to shift the null hypothesis. Surface properties
that are reproduced by a structural generator are no longer taken, by themselves,
as evidence of language. A semantic or cryptographic model must explain
additional signal in the `X`-and-state sequence, predict held-out physical
leaves, and beat the generative baseline. This is not a proof that there is no
message; it is a stricter formulation of the question of whether one exists.

## The structural factor

The observed surface decomposes into an internal body and a final state. The
public file `data/factorization/full_surface_factorization.tsv` contains one such
outcome for each cell of the denominator. There are no empty factors.

100% coverage means completeness of this structural layer. It does not mean that
every poorly legible sign received an invented reading: an explicit abstention is
an allowed outcome of the procedure (allowed but, in strict-v82, unused — all
23,859 cells carry a concrete factor; the seven disputed signs are left as
unforced surface readings rather than abstained). It also does not mean translation
or a proven historical purpose of the text.

The structural factor and the evidence status are different axes. The soft layer
gives a hypothesis for every cell. Strict means that a specific assignment passed
predeclared cross-transcription, OOF, null, source, and replay checks. Full soft
coverage must not be presented as strict.

## Strict and the audit line

Strict is built fail-closed: one high score is not enough. Splitting by leaf, a
closed target, source/canonical cross-checks, quarantine, repeated replay, and
conflict checking were used. **The release authority is strict-v82:
23,859/23,859 = 100% structural coverage**, with a lock
(`data/strict/strict_anonymous_factor_v82.lock.json`), release and post-publish
audits (`results/strict_v82_v273_*`, `PASS_OFFICIAL_STRICT_V82_ACTIVE`,
residual 0), and an **independent completion audit**
(`results/strict_v82_completion_audit.json`, `PASS_OFFICIAL_STRICT_100_COMPLETE`,
26/26). The closure condition (lock + confirmatory folds + independent audit of
the last residual) has been met. The strict-v21 files (22,106/23,859 ≈ 92.65%)
are retained in the release as an immutable historical step of the line, not as
the current authority.

## Transcription corrections

The source transcription is not overwritten. Corrections are applied as a
separate overlay file; a manifest records the SHA-256 of the source, of the list
of substitutions, and of the result. A decision is made from the scan and
independent readings. The model may flag a suspect location but has no right to
draw in a sign.

## The generator

The generator is trained separately for the Currier A and B modes. At each
position it chooses between a new structurally admissible form and copying a
recent form with a possible one-step change. The ending channel receives a strong
reset at the physical line, while a longer form memory creates a local, separate
drift.

The generator is a sufficient computational realization — not a claim of a found
medieval device, and not a proof that there is no message.

## The ladder and the template frame

Internal frames were compared by Levenshtein distance. The heavy chain of
single insertions was selected by dynamic programming over a length-oriented
graph and ranked by total token mass. The coverage of three nested finite
templates was measured separately. Results were checked on the full and strict
layers.

Edit-graph connectivity was not used as positive evidence: a length/unigram null
showed it is expected for short strings. Only the mass of the specific chain, the
concentration of types, the transfer into strict, and permutation checks of local
order entered the conclusion. Detailed numbers are in `docs/UNIVERSAL_LADDER.md`.
