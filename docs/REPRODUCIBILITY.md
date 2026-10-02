# Reproducibility

## Requirements and checks

Python 3.10 or later. No dependencies, network, credentials or private archive
access are required. From the repository root:

```sh
python3 -B scripts/verify_demo.py
python3 -B -m unittest discover -s tests -v
```

The verifier checks inventory and hashes, reproduces corrections, validates the
unresolved-reading policy and checks cell/provenance consistency. Tests also
exercise malformed inputs, extra files and hash mismatches.

`-B` prevents bytecode caches. The package deliberately rejects extra files,
caches and model payloads. Keep downloaded artifacts outside the repository.

## Check a future artifact

After obtaining the historical strict v21 file:

```sh
python3 -B scripts/verify_artifact.py --id strict-v21 --file /path/to/strict_anonymous_factor_v21.tsv
```

Select the ID from the [register](../data/artifact-commitments-2026-10-02-v2.json).
Use `--registry` for another register. The script reads bytes only: it never
unpickles or executes a model. A mismatch returns a nonzero exit status.

The register's structure can be checked now. Private-file contents can be checked
only after the corresponding files become available.

## Maintainer inventory update

After an intentional, reviewed edit:

```sh
python3 -B scripts/build_manifest.py
python3 -B scripts/verify_demo.py
```

Rebuilding the manifest records new content, not correctness. Compare against a
trusted repository revision: a manifest cannot authenticate itself.

Passing these checks does not independently replicate the manuscript study.
See [Limitations](LIMITATIONS.md).
