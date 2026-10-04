# Image-source audit for MS 408

Date: 2026-09-29.

## Result

The image reference set was replaced with the full official Beinecke/Yale IIIF set:

- 213 of 213 canvases downloaded;
- total JPEG volume: 560,960,374 bytes;
- every file opens as an image;
- every file's dimensions match the IIIF manifest;
- every JPEG has a SHA-256 in the folio inventory;
- names are normalized by folio, but the original Yale label and canvas ID are preserved;
- covers, edges and complex foldout exposures do not masquerade as ordinary
  pages and have explicit names.

## Why the earlier images looked bad

The working tree mixed different classes of files:

- individual official native JPEGs;
- pages downscaled to width 2048;
- browser copies 636×900;
- crops 518×518, 180×220 and smaller;
- contact sheets, masks and model inputs.

So the problem was not only resolution but the absence of a single source and
metadata: an algorithm or a person could accidentally pick a crop instead of a
page. Now only `SOURCES/manuscript_scans/yale_ms408/images/` is the source of the
full image; any resize or crop must reference a specific `scan_index` and SHA-256.

Some previously scattered "native" files were genuinely good and are byte-for-byte
identical to the new official set. For example, old copies of f1r, f57v and f69v
have the same SHA-256 as the corresponding Yale JPEGs. They were not false, but
represented an incomplete and poorly organized cache. The new set improves
completeness, naming, provenance and protection against picking the wrong scale.

## Metadata checksums

- IIIF manifest: `317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309`;
- TSV inventory: `2a6a4a4869657c1567792e5eca35368955985c0c69f2ab4c9a2803b52bbc993f`;
- JSON inventory: `e84cb2eda3a8b6efc86c23a75e8d1a79619927569d4520d465181c367ed707ac`;
- verification summary: `23517ba51ff2a0ecff7754f34a1414f5cdddca7893b5a2869f6338cec04711d1`.

## Reproducible check

Scans are not included in the release: they are fetched via IIIF
(`scripts/fetch_yale_iiif.py`), and their integrity is checked against the SHA-256
values in `metadata/folio_inventory.tsv`. Checksums of the reference tables and
metadata are verified by `scripts/verify_release.py` against
`PUBLIC_RELEASE_MANIFEST.json`.
