# Further technical artifacts

The [register](../data/artifact-commitments-2026-10-02-v2.json) identifies 44 existing
artifacts. Their contents are not distributed here.

| Group | Registered material |
|---|---|
| Data and audits | 23,859-cell denominator, strict v21 and audits, preliminary factorization |
| Transcription | Correction overlay, corrected view, manifest, decisions and ambiguities |
| Measurements | Line-boundary results, model comparison and internal-form experiments |
| Generator | Implementation, library, validation code and results |
| Visual model | v15 metadata, training/gating code and all 15 saved checkpoints |

Each entry records an ID, filename, archive path, purpose, size, SHA-256 and
observation time. Filesystem modification time is separate and is not a certified
creation date. Strict v21 also records its acceptance event and audit source.
The historical v15 model and strict v21 dataset are different stages of work.

This English metadata revision preserves all 44 IDs, sizes, hashes, archive paths
and observation timestamps from the earlier unpublished registry. Only metadata
wording changed. The earlier registry remains in the private archive.

Future packaging may change files. Such changes require new hashes and an
explanation, not silent replacement of existing commitments. Reproducing training
also requires inputs, configuration and protocols; a checkpoint alone is insufficient.

Use [the verification instructions](REPRODUCIBILITY.md) after obtaining a file.
Release dates are not fixed.
