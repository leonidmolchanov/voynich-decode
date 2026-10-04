#!/usr/bin/env python3
"""Optional: fetch the computer-vision observer weights from the Hugging Face Hub.

The weights are NOT part of this repository (the offline headline result in
docs/REPRODUCIBILITY.md steps A-D needs neither weights nor a GPU). They are only
required to re-run the CV pipeline end to end (step E / Tier 2). Both the model
and dataset repos are PUBLIC, so no login is needed.

    python -m pip install -U huggingface_hub
    python scripts/fetch_weights.py                 # -> ./models/
    python scripts/fetch_weights.py --dataset        # also fetch the crops/dataset

Afterwards, see docs/STRICT_GATE_REPRODUCTION.md (Tier 2) and
docs/FULL_REPRODUCTION.md for how the weights feed the CV observers and the gate.
"""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_REPO = "LeonidMolchanov1987/voynich-decode-models"
DATASET_REPO = "LeonidMolchanov1987/voynich-decode-data"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model-repo", default=MODEL_REPO, help="HF model repo id")
    ap.add_argument("--dataset", action="store_true",
                    help="also download the crops/training dataset repo")
    ap.add_argument("--dest", type=Path, default=ROOT / "models",
                    help="local target dir for the weights (default: ./models)")
    args = ap.parse_args()

    from huggingface_hub import snapshot_download  # lazy: only needed for step E

    args.dest.mkdir(parents=True, exist_ok=True)
    path = snapshot_download(repo_id=args.model_repo, repo_type="model",
                             local_dir=str(args.dest))
    print(f"weights: {args.model_repo} -> {path}")
    print("verify: each model card ships a MANIFEST.sha256 to check against.")

    if args.dataset:
        dpath = snapshot_download(repo_id=DATASET_REPO, repo_type="dataset",
                                  local_dir=str(ROOT / "dataset"))
        print(f"dataset: {DATASET_REPO} -> {dpath}")


if __name__ == "__main__":
    main()
