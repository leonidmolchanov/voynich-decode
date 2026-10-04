# Data provenance

## Manuscript

- Object: Beinecke MS 408, Yale University Library.
- Catalogue: https://collections.library.yale.edu/catalog/2002046
- IIIF manifest: https://collections.library.yale.edu/manifests/2002046
- Local scans are not included in the public release (fetch via IIIF).

`metadata/folio_inventory.tsv` contains the folio name, IIIF URL, dimensions,
SHA-256, and the local verification result. The absolute-path column has been
removed.

## Transcription

The archival source is kept separate from the corrections. The raw
Zandbergen–Landini (EVA/IVTFF) transcription is **not redistributed** here
(© R. Zandbergen); see `data/transcriptions/README.md` for the upstream pointer
(voynich.nu), the 13-edit overlay, and the expected SHA-256 checksums. The
corrections overlay and the decision register (accepted, rejected, and
unresolvable cases) are provided in `data/corrections/`.

## Derived tables

- `aligned_cell_denominator_v1.tsv` — the fixed set of cells;
- `full_surface_factorization.tsv` — the full structural layer (regenerated as a
  traceable projection of the strict-v82 core);
- `data/strict/strict_anonymous_factor_v82.tsv` — the current immutable strict
  core (100%); `strict_anonymous_factor_v21.tsv` — the historical strict step;
- JSON files in `results/` — release and post-publish audits (including the
  strict-v82 release, post-publish, and independent completion audits).

## Illustrations

Illustrative figures (coverage charts, correction triptychs) are not bundled in
this English release. Where used, correction triptychs consist only of unaltered
Yale-scan pixels — cropping, magnification, frames, and captions; no glyph was
drawn in. They can be regenerated from the shipped data and the public IIIF scans.
