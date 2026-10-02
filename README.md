# Voynich Decode

Verification code and selected data accompanying Leonid Molchanov's Voynich manuscript research.

This repository contains two transcription corrections, seven unresolved readings
and 19 aligned cells from two lines. It contains no article, images, full
transcription, training data, model weights or generator.

## Run the checks

Python 3.10 or later; standard library only. From the repository root:

```sh
python3 -B scripts/verify_demo.py
python3 -B -m unittest discover -s tests -v
```

The verifier checks file hashes, reproduces the corrections and checks cell
provenance. Passing does not independently validate handwriting readings or
reproduce the full study.

## Contents

| Path | Contents |
|---|---|
| `data/corrections.tsv` | Two accepted changes, confidence, supporting readings and Yale scan URLs |
| `data/transcription_excerpts.tsv` | Original and corrected source lines |
| `data/ambiguities.tsv` | Seven unresolved readings |
| `data/cells_sample.tsv` | 19 cell addresses, readings, factors and assignment tiers |
| `data/cell_provenance.tsv` | Corresponding reference transcriptions |
| `data/provenance.json` | Selection scope and hashes of full source files |
| `data/artifact-commitments-2026-10-02-v2.json` | Metadata and SHA-256 commitments for 44 future-release artifacts |
| `scripts/`, `tests/` | Verification tools, manifest builder and tests |
| `MANIFEST.json` | Inventory and SHA-256 of distributed files |

[Methods](docs/METHODS.md) · [Limitations](docs/LIMITATIONS.md) ·
[Reproducibility](docs/REPRODUCIBILITY.md) · [Provenance](docs/DATA_PROVENANCE.md) ·
[Reported measurements](docs/TECHNICAL_NOTES.md)

## Further technical releases

The [artifact register](docs/FUTURE_RELEASE.md) identifies 44 existing files held
outside this repository: data, audits, scripts and 15 saved model checkpoints.
Each entry records its purpose, archive path, size, observation time, filesystem
modification time and SHA-256. These are file commitments, not download links.

After obtaining a registered file, check it with:

```sh
python3 -B scripts/verify_artifact.py --id strict-v21 --file strict_anonymous_factor_v21.tsv
```

The remaining technical material requires dependency packaging and documentation.
Release dates are not fixed. A hash match establishes file identity, not
authorship, scientific validity or an independently certified creation date.

## Credit and licensing

Author: **Leonid Molchanov** ([leonidmolchanov](https://github.com/leonidmolchanov)).
Please cite this repository and the version used when building on its data,
corrections, code or results. See [CITATION.cff](CITATION.cff).

Project code is under MIT. Original documentation and copyrightable project
annotations are under CC BY 4.0. Preserve the applicable credit and license
notices; identify changes when sharing adaptations of CC BY material.
Third-party transcription content is excluded from these grants.
See [LICENSE](LICENSE) and [Attribution](docs/ATTRIBUTION.md).

The citation request does not create exclusive rights over a scientific principle
or add a publication-citation condition to MIT.
