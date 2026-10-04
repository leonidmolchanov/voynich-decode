# Transcription-correction reference

All paths are release-relative (inside this repository).

## Summary

| Layer | Count | Status | File |
|---|---:|---|---|
| Raw ZL3b corrections | 13 | accepted and applied | `data/corrections/ZL3b_corrections_v13.tsv` |
| Aligned-reference corrections | 27 | accepted, part of the strict core | `data/corrections/aligned_reference_corrections_x10b_v1.tsv` |
| Non-core visual resolutions | 7 | 2 candidate, 2 reference, 3 sets | `data/corrections/noncore_visual_resolutions_x10c_v1.tsv` |
| Open ambiguities | 7 | not corrected, excluded | `data/corrections/ZL3b_ambiguities_v7.tsv` |
| Analytical surface restorations | 1,910 | not source corrections; applied when building the factorization layer | — |

Single line-by-line index of the first four layers:
`data/corrections/TRANSCRIPTION_DECISION_REGISTER.tsv` — 54 decisions.
Correction inventory: `data/corrections/TRANSCRIPTION_CORRECTION_INVENTORY.json`.

## Which text to read

- Historical published source: the Zandbergen–Landini ZL3b transliteration
  (voynich.nu; not included in the release — obtained from the source, with attribution).
- Our accepted updated representation: reconstruct it by applying the 13-edit
  overlay (`data/corrections/ZL3b_corrections_v13.tsv`) to the source — see
  `data/transcriptions/README.md`. The corrected `.txt` is not redistributed (it
  embeds the full third-party transcription); its expected SHA-256 is in the manifest.
- Build evidence:
  `data/transcriptions/ZL3b_corrected_v13.manifest.json`.

The manifest records the source SHA-256, the overlay SHA-256, all 13 replacements,
the line numbers, the resulting SHA-256, and the fact that the seven disputed
loci were left unchanged.

## Verification

Integrity of the corrected transcription and of the decision register is checked
against the SHA-256 values in `PUBLIC_RELEASE_MANIFEST.json` (`scripts/verify_release.py`).
The full correction sequence (`ZL3B-0001…0013`, `AMBIG-0001…0007`) is fixed in
the decision register; any gap is visible on verification.
