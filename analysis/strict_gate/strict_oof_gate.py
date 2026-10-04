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
"""Development/confirmatory OOF gate for short exact-factor specialist."""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];TRAIN=ROOT/"WORKING/hypotheses/strict_v4_short_factor_scope_v1/train_short_supported.tsv";RUNNER=ROOT/"scripts/strict_v4_short_factor_runner.py";PROTOCOL=ROOT/"ANALYSIS_REPORTS/protocols/PREDECLARED_STRICT_V4_SHORT_FACTOR_SPECIALIST.md";SEEDS=(26101,26117,26129);THRESHOLDS=(.50,.55,.60,.65,.70,.75,.80,.85,.90,.95,.97,.98,.99)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 with Path(p).open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def wilson(c,n,z=1.6448536269514722):
 if not n:return 0
 p=c/n;d=1+z*z/n;return (p+z*z/(2*n)-z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)))/d
def metrics(rows,total,folds,th):
 calls=[r for r in rows if r["unanimous"] and r["confidence"]>=th];c=sum(r["prediction"]==r["truth"] for r in calls);err=len(calls)-c;el=Counter(r["leaf_id"] for r in calls if r["prediction"]!=r["truth"]);bf={}
 for fold in folds:
  p=[r for r in calls if r["outer_fold"]==fold];h=sum(r["prediction"]==r["truth"] for r in p);bf[str(fold)]={"calls":len(p),"correct":h,"precision":h/len(p) if p else 0.0}
 return {"threshold":th,"population":total,"calls":len(calls),"coverage":len(calls)/total if total else 0,"correct":c,"errors":err,"precision":c/len(calls) if calls else 0,"wilson_lower_95_one_sided":wilson(c,len(calls)),"by_fold":bf,"max_error_leaf_share":max(el.values(),default=0)/err if err else 0}
def passm(m,confirm=False):return m["precision"]>=.995 and m["wilson_lower_95_one_sided"]>=.99 and m["coverage"]>=.10 and all(v["calls"]>0 and v["precision"]>=.99 for v in m["by_fold"].values()) and (not confirm or m["max_error_leaf_share"]<=.30)
def main():
 p=argparse.ArgumentParser();p.add_argument("--results",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args()
 if a.out.exists():raise FileExistsError(a.out)
 truth={r["record_id"]:r for r in read(TRAIN)};pred=defaultdict(list);hashes={};files=sorted(a.results.glob("fold*_seed*.json"))
 if len(files)!=15:raise RuntimeError(f"15 results required, found {len(files)}")
 for f in files:
  d=json.loads(f.read_text());hashes[f.name]=sha(f)
  if d.get("status")!="SHORT_FACTOR_OOF_LOCKED" or d.get("target_inferred") is not False or d.get("runner_sha256")!=sha(RUNNER):raise RuntimeError(f"artifact {f}")
  for x in d["oof_predictions"]:pred[x["record_id"]].append((int(d["seed"]),x))
 if set(pred)!=set(truth):raise RuntimeError("roster")
 rows=[]
 for rid in sorted(pred):
  v=sorted(pred[rid]);t=truth[rid]
  if tuple(s for s,_ in v)!=SEEDS:raise RuntimeError(f"seeds {rid}")
  factors=[x["prediction"] for _,x in v];u=len(set(factors))==1;factor=factors[0] if u else "";rows.append({"record_id":rid,"leaf_id":t["leaf_id"],"outer_fold":int(t["outer_fold"]),"hand":t["hand"],"section":t["section"],"truth":t["factor"],"prediction":factor,"confidence":min(float(x["confidence"]) for _,x in v),"unanimous":u})
 dev=[r for r in rows if r["outer_fold"] in (0,1)];con=[r for r in rows if r["outer_fold"] in (2,3,4)];grid=[metrics(dev,len(dev),(0,1),th) for th in THRESHOLDS];eligible=[m for m in grid if passm(m)];winner=min(eligible,key=lambda m:m["threshold"]) if eligible else None;cm=metrics(con,len(con),(2,3,4),winner["threshold"]) if winner else None;ok=bool(winner and passm(cm,True));status="PASS_SHORT_FACTOR_CONFIRMATORY_AWAITING_999_NULL" if ok else "FAIL_SHORT_FACTOR_OOF_NO_TARGET_INFERENCE"
 a.out.mkdir(parents=True);tp=a.out/"oof_consensus.tsv";fields=list(rows[0])+["gate_split","selected_threshold_pass"]
 with tp.open("x",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter="\t",lineterminator="\n");w.writeheader()
  for r in rows:w.writerow({**r,"gate_split":"development" if r["outer_fold"] in (0,1) else "confirmatory","selected_threshold_pass":int(bool(winner) and r["unanimous"] and r["confidence"]>=winner["threshold"])})
 payload={"schema":"STRICT_V4_SHORT_FACTOR_OOF_GATE_V1","status":status,"threshold_grid":grid,"selected_development":winner,"confirmatory":cm,"checks":{"development_pass":bool(winner),"confirmatory_pass":ok,"target_not_inferred":True,"strict_core_unchanged":True},"artifact_hashes":hashes,"oof_consensus_sha256":sha(tp),"protocol_sha256":sha(PROTOCOL),"runner_sha256":sha(RUNNER),"target_inferred":False,"strict_core_mutated":False};(a.out/"oof_gate.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print(json.dumps(payload,indent=2,sort_keys=True));return 0 if ok else 2
if __name__=="__main__":raise SystemExit(main())

