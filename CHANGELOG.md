# Changelog

## 0.2.0 — 2026-10-04

- authority updated to **strict-v82: 23,859/23,859 = 100% structural coverage**;
  added `data/strict/strict_anonymous_factor_v82.*` (lock, additions) and the audits
  `results/strict_v82_v273_*`, plus the independent `results/strict_v82_completion_audit.json`
  (`PASS_OFFICIAL_STRICT_100_COMPLETE`, 26/26);
- `data/factorization/full_surface_factorization.tsv` rebuilt as a traceable
  projection of v82 (`scripts/build_full_surface_from_v82.py`): all cells STRICT_ACCEPTED,
  factors from the audited v82 core;
- strict-v21 (≈92.65%) retained as a historical step of the line, not the authority;
- added held-out/calibrate/freechoice/eda scripts and `null_test` for
  independent checking; "100%" is structural coverage, not translation/reading.

## 0.1.0-staging — 2026-10-02

- created an isolated public structure without the private tree's history;
- added the denominator, the full factorization layer, and the strict-v21 lineage;
- added transcription corrections and visual examples;
- moved the generator to relative paths;
- added composition, checksum, and full-coverage checks.
