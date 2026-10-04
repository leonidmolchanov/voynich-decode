# Strict release lineage

This folder stores the immutable strict steps together with their locks. It is
needed to verify the provenance of decisions.

**Current authority — strict-v82: 23,859/23,859 = 100% structural coverage.**
- core: `strict_anonymous_factor_v82.tsv`
  (SHA-256 `8a81b7a611f0f033f1072e8a5e67d0e9c7411807eee39d3715d02336e4112c56`),
  lock `strict_anonymous_factor_v82.lock.json` (`coverage_percent` 100.0,
  `denominator` 23859), `strict_anonymous_factor_v82_additions.tsv`;
- audits: `../../results/strict_v82_v273_f27v_novel_interior_release_v1.json`,
  `../../results/strict_v82_v273_postpublish_audit_v1.json`
  (`PASS_OFFICIAL_STRICT_V82_ACTIVE`, residual 0), plus the independent
  `../../results/strict_v82_completion_audit.json`
  (`PASS_OFFICIAL_STRICT_100_COMPLETE`, 26/26);
Note on version numbers: `v82` is the accepted-core generation (the coverage
milestone). The `v273` in the release-artifact names and the `V87…V273` tags in the
audited factor's `resolution` column are internal audit/run identifiers of the
promotion lineage — NOT separate coverage states. The per-wave promotion evidence
(how the ~1,753 cells moved from unresolved to accepted between v21 and v82) is the
six 999-null gate bundles under `gates/`.

**Provenance of the lock/audit records.** The `*.lock.json` files here and the
related release/audit JSONs (under `../../results/`, `../transcriptions/`,
`../corrections/`) are frozen records: some of their internal fields cite the
original build-tree paths (e.g. `MASTER/accepted/…`) and intermediate generations
(v80/v81) that are **not shipped**. Those path strings are immutable provenance,
not something to resolve — the shipped authority is the files named here by their
relative release paths, and `scripts/verify_release.py` checks them by SHA-256.

- `../factorization/full_surface_factorization.tsv` — a derived projection of v82
  (see `../../scripts/build_full_surface_from_v82.py`).

**Previous step in the lineage — strict-v21: 22,106/23,859 ≈ 92.65%**
(`strict_anonymous_factor_v21.*`) — kept as a historical immutable step, NOT as
the current authority. "100%" is structural coverage, not a translation and not a
reading of a language.
