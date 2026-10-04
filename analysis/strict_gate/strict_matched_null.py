# UPSTREAM CV-gate reference code (GPU tier) — for method transparency.
# This is the actual observer / matched-null / OOF-gate code. Its inputs (leaf crops,
# OOF predictions, protocols) are GPU-tier artifacts: crops are on the Hugging Face
# dataset LeonidMolchanov1987/voynich-decode-data, observer weights on
# LeonidMolchanov1987/voynich-decode-models, page scans via Yale IIIF. The WORKING/...
# and ANALYSIS_REPORTS/... paths below are the original project layout and are NOT
# shipped in this offline package (they need PyTorch + a GPU to run).
# For the OFFLINE, GPU-free reproduction of the inferential gate (observed OOF accuracy
# beats all 999 matched-random nulls), run:  python3 scripts/verify_strict_gate.py
# See docs/STRICT_GATE_REPRODUCTION.md.

#!/usr/bin/env python3
"""Confirmatory target-matched 999-null gate for strict-v3 Arm E."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

from scripts import strict_v3_consensus_oof_gate as consensus


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "ANALYSIS_REPORTS/protocols/PREDECLARED_STRICT_V3_CONSENSUS_EXTENSION_GATE.md"
IMPLEMENTATION = ROOT / "ANALYSIS_REPORTS/protocols/PREDECLARED_STRICT_V3_CONSENSUS_NULL_IMPLEMENTATION.md"
OOF_GATE = ROOT / "WORKING/validation/strict_v3_consensus_oof_gate_v1/oof_consensus_gate.json"
QUEUE = ROOT / "WORKING/hypotheses/strict_v3_consensus_extension_scope_v1/consensus_extension_queue.tsv"
SCOPE = ROOT / "WORKING/hypotheses/strict_v3_consensus_extension_scope_v1/manifest.json"
TRAIN = ROOT / "WORKING/data/leaf_clean_highres_crops_v1/train_crop_index.tsv"
OUT = ROOT / "WORKING/validation/strict_v3_consensus_matched_null_v1"
NULLS = 999


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def write(path: Path, items: list[dict], fields: list[str]) -> None:
    with path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(items)


def atomic_json(path: Path, value: dict) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)
    return sha(path)


def normalize(value: str) -> str:
    return "".join(value.split()).replace(".", "")


def edge(factor: str) -> str:
    return factor.split("=>", 1)[1] if "=>" in factor else "UNKNOWN"


def length_bin(surface: str) -> str:
    size = len(normalize(surface))
    return str(size) if size <= 5 else "6+"


def physical_leaf(folio: str) -> str:
    match = re.match(r"^(f\d+)", folio)
    return match.group(1) if match else folio


def wilson(correct: int, calls: int, z: float = 1.6448536269514722) -> float:
    if not calls:
        return 0.0
    p = correct / calls
    denominator = 1 + z*z/calls
    centre = p + z*z/(2*calls)
    radius = z * math.sqrt(p*(1-p)/calls + z*z/(4*calls*calls))
    return (centre-radius)/denominator


def main() -> int:
    if OUT.exists():
        raise RuntimeError(f"refusing to overwrite: {OUT}")
    OUT.mkdir(parents=True)
    gate = json.loads(OOF_GATE.read_text(encoding="utf-8"))
    scope = json.loads(SCOPE.read_text(encoding="utf-8"))
    if (
        gate.get("status") != "PASS_DISCOVERY_AND_CONFIRMATORY_CONSENSUS_RULE_FROZEN_AWAITING_999_NULL"
        or gate.get("winner") != "E"
        or not gate.get("confirmatory", {}).get("pass")
        or gate.get("target_inferred") is not False
        or gate.get("residual_truth_opened") is not False
        or gate.get("protocol_sha256") != sha(PROTOCOL)
    ):
        raise RuntimeError("passing frozen Arm E OOF gate required")
    if scope.get("status") != "PASS_STRICT_V3_CONSENSUS_SCOPE_FROZEN_NO_TARGET_INFERENCE_NO_SOURCE_AUDIT" or scope.get("target_rows") != 3729:
        raise RuntimeError("frozen strict-v3 scope required")
    queue = read(QUEUE)
    train = {row["record_id"]: row for row in read(TRAIN)}
    oof, artifact_hashes = consensus.load()
    confirm = [row for row in oof if row["split"] == "confirmatory"]

    def oof_stratum(row):
        meta = train[row["record_id"]]
        return (meta["hand"], meta["section"], edge(meta["factor"]), length_bin(meta["surface"]))

    def target_stratum(row):
        return (row["hand"], row["section"], edge(row["factor_candidate"]), length_bin(row["surface_candidate"]))

    target_counts = Counter(target_stratum(row) for row in queue)
    oof_groups: dict[tuple[str, ...], list[dict]] = defaultdict(list)
    for row in confirm:
        oof_groups[oof_stratum(row)].append(row)
    supported_strata = {
        key for key, items in oof_groups.items()
        if len({item["leaf_id"] for item in items}) >= 2 and target_counts.get(key, 0) >= 2
    }
    matched = []
    for key in sorted(supported_strata):
        items = sorted(
            oof_groups[key],
            key=lambda row: hashlib.sha256(f"STRICT-V3-MATCH|{row['record_id']}".encode()).hexdigest(),
        )
        limit = min(len(items), target_counts[key])
        by_leaf: dict[str, list[dict]] = defaultdict(list)
        for item in items:
            by_leaf[item["leaf_id"]].append(item)
        leaf_order = sorted(
            by_leaf,
            key=lambda value: hashlib.sha256(f"STRICT-V3-MATCH-LEAF|{key}|{value}".encode()).hexdigest(),
        )
        chosen = [by_leaf[leaf_order[0]][0], by_leaf[leaf_order[1]][0]]
        chosen_ids = {row["record_id"] for row in chosen}
        chosen.extend(row for row in items if row["record_id"] not in chosen_ids)
        matched.extend(chosen[:limit])
    matched_ids = {row["record_id"] for row in matched}
    if len(matched_ids) != len(matched):
        raise RuntimeError("matched OOF duplicate")
    supported_targets = [row for row in queue if target_stratum(row) in supported_strata]

    called = [row for row in matched if row["calls"]["E"]]
    correct = sum(row["calls"]["E"] == row["truth_factor"] for row in called)
    errors = [row for row in called if row["calls"]["E"] != row["truth_factor"]]
    error_leaves = Counter(row["leaf_id"] for row in errors)
    observed = {
        "matched_rows": len(matched), "calls": len(called), "correct": correct,
        "errors": len(called)-correct, "precision": correct/len(called) if called else 0.0,
        "wilson_lower_95_one_sided": wilson(correct,len(called)),
        "error_physical_leaves": len(error_leaves),
        "max_error_leaf_share": max(error_leaves.values(),default=0)/max(1,len(errors)),
    }
    strata: dict[tuple[str, ...], dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for row in matched:
        strata[oof_stratum(row)][row["leaf_id"]].append(row)
    null_dir = OUT / "nulls"; null_dir.mkdir()
    null_correct_values = []
    for index in range(NULLS):
        labels = {}
        for key, leaves_map in sorted(strata.items()):
            leaves = sorted(leaves_map)
            sources = list(leaves)
            rng = random.Random(int.from_bytes(hashlib.sha256(f"STRICT-V3-NULL|{index}|{'|'.join(key)}".encode()).digest()[:8],"big"))
            rng.shuffle(sources)
            if any(a == b for a,b in zip(leaves,sources)):
                shift = 1 + index % (len(leaves)-1)
                sources = leaves[shift:]+leaves[:shift]
            for target_leaf, source_leaf in zip(leaves,sources):
                targets = sorted(leaves_map[target_leaf],key=lambda row:row["record_id"])
                values = [row["truth_factor"] for row in sorted(leaves_map[source_leaf],key=lambda row:row["record_id"])]
                for position,row in enumerate(targets): labels[row["record_id"]]=values[position%len(values)]
        null_correct = sum(row["calls"]["E"] == labels[row["record_id"]] for row in called)
        null_correct_values.append(null_correct)
        atomic_json(null_dir / f"null_{index:04d}.json", {
            "schema":"STRICT_V3_CONSENSUS_MATCHED_NULL_V1","index":index,
            "calls":len(called),"correct":null_correct,"target_inferred":False,
            "residual_truth_opened":False,"strict_core_mutated":False,
        })

    checks = {
        "calls": observed["calls"] >= 200,
        "precision": observed["precision"] >= 0.995,
        "wilson": observed["wilson_lower_95_one_sided"] >= 0.990,
        "error_leaf_concentration": observed["max_error_leaf_share"] <= 0.5,
        "beats_all_999_nulls": observed["correct"] > max(null_correct_values),
    }
    matched_rows = []
    for row in matched:
        meta=train[row["record_id"]]
        matched_rows.append({
            "record_id":row["record_id"],"leaf_id":row["leaf_id"],"outer_fold":row["outer_fold"],
            "hand":meta["hand"],"section":meta["section"],"edge_state":edge(meta["factor"]),
            "length_bin":length_bin(meta["surface"]),"arm_e_call":int(bool(row["calls"]["E"])),
            "arm_e_factor":row["calls"]["E"],"arm_e_correct":int(row["calls"]["E"]==row["truth_factor"] and bool(row["calls"]["E"])),
        })
    supported_id_rows=[{"record_id":row["record_id"]} for row in sorted(supported_targets,key=lambda row:row["record_id"])]
    matched_path=OUT/"matched_confirmatory_oof.tsv"; supported_path=OUT/"oof_supported_target_ids.tsv"
    write(matched_path,matched_rows,list(matched_rows[0])); write(supported_path,supported_id_rows,["record_id"])
    null_paths=sorted(null_dir.glob("null_*.json"))
    result = {
        "schema":"STRICT_V3_CONSENSUS_MATCHED_OOF_NULL_GATE_V1",
        "status":"PASS_STRICT_V3_CONSENSUS_999_NULL_AUTHORIZE_TARGET_LOCK_ONLY" if all(checks.values()) else "FAIL_STRICT_V3_CONSENSUS_NO_TARGET_LOCK",
        "winner":"E","target_rows":len(queue),"supported_target_rows":len(supported_targets),
        "unsupported_target_rows":len(queue)-len(supported_targets),"supported_strata":len(supported_strata),
        "observed":observed,"checks":checks,"null_files":NULLS,
        "null_min_correct":min(null_correct_values),"null_median_correct":sorted(null_correct_values)[NULLS//2],"null_max_correct":max(null_correct_values),
        "protocol_sha256":sha(PROTOCOL),"implementation_sha256":sha(IMPLEMENTATION),
        "oof_gate_sha256":sha(OOF_GATE),"scope_sha256":sha(SCOPE),"queue_sha256":sha(QUEUE),
        "matched_oof_sha256":sha(matched_path),"supported_target_ids_sha256":sha(supported_path),
        "null_merkle_sha256":hashlib.sha256("".join(sha(path) for path in null_paths).encode()).hexdigest(),
        "artifact_hashes":artifact_hashes,"target_inferred":False,"residual_truth_opened":False,
        "source_audit_opened":False,"strict_core_mutated":False,"strict_promotion_authorized":False,
    }
    digest=atomic_json(OUT/"oof_null_gate.json",result)
    print(json.dumps({"status":result["status"],"supported_target_rows":len(supported_targets),"observed":observed,"checks":checks,"null_max_correct":max(null_correct_values),"sha256":digest},sort_keys=True))
    return 0 if all(checks.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
