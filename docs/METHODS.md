# Methods

## Aligned cells

A cell is an addressable segment in aligned transcriptions, not a proven word or
semantic unit. Its `record_id` combines folio, line and zero-based position.

The sample contains all 19 available full-factorization records for `f108r.10`
and `f115r.23`. This is a purposive selection, not a random sample or complete
pages. Missing aligned positions have not been filled by inference.

The structural representation separates internal form from ending class. State
labels such as `S4` are identifiers, not translations. Assignment tiers are
preserved: `STRICT_ACCEPTED`, `ENSEMBLE_OR_CHAIN_CANDIDATE` and
`FORCED_TRANSCRIPTION_SYMBOLIC` are different evidence levels.
The provenance table supplies IT2a, GC2a, FG2a and CD2a readings.

## Correction overlay

| Decision | Address | Original | Accepted |
|---|---|---|---|
| ZL3B-0001 | f115r.23:6 | checthy | checkhy |
| ZL3B-0003 | f108r.10:4 | ykeol | yteol |

The characters are EVA sign labels, not pronunciation or translation.
`data/transcription_excerpts.tsv` preserves each source line and its corrected
view. The verifier replaces one token while preserving the prefix, other tokens
and separators. It supports the period/comma separators in these examples, not
every IVTFF feature.

`data/corrections.tsv` supplies confidence, supporting readings and Yale scan
URLs. Seven entries in `data/ambiguities.tsv` remain unresolved; they are not
applied as accepted corrections.

The scripts verify bytes and table consistency, not the paleographic truth of a
decision. [Technical notes](TECHNICAL_NOTES.md) report broader experiments whose
complete inputs and implementations are not included here.
