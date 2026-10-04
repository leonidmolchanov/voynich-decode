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
"""999 physical-leaf matched nulls for short-factor confirmatory calls."""
from __future__ import annotations
import argparse,csv,hashlib,json,math,random
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PROTOCOL=ROOT/"ANALYSIS_REPORTS/protocols/PREDECLARED_STRICT_V4_SHORT_FACTOR_SPECIALIST.md"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 with Path(p).open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f,delimiter="\t"))
def lbin(f):return str(len(f.split("=>",1)[0].split()))
def key(r):return r["hand"],r["section"],r["truth"].split("=>",1)[1],lbin(r["truth"])
def shifts(x):
 leaves=[r["leaf_id"] for r in x];return [s for s in range(1,len(x)) if all(leaves[i]!=leaves[(i+s)%len(x)] for i in range(len(x)))]
def wilson(c,n,z=1.6448536269514722):
 if not n:return 0
 p=c/n;d=1+z*z/n;return (p+z*z/(2*n)-z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)))/d
def main():
 p=argparse.ArgumentParser();p.add_argument("--oof-dir",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args()
 if a.out.exists():raise FileExistsError(a.out)
 gp=a.oof_dir/"oof_gate.json";tp=a.oof_dir/"oof_consensus.tsv";g=json.loads(gp.read_text())
 if g.get("status")!="PASS_SHORT_FACTOR_CONFIRMATORY_AWAITING_999_NULL" or not all(g.get("checks",{}).values()):raise RuntimeError("short OOF gate")
 th=float(g["selected_development"]["threshold"]);calls=[r for r in read(tp) if r["gate_split"]=="confirmatory" and r["selected_threshold_pass"]=="1"];groups=defaultdict(list)
 for r in calls:groups[key(r)].append(r)
 sup={};uns={}
 for k,x in sorted(groups.items()):x=sorted(x,key=lambda r:(r["leaf_id"],r["record_id"]));s=shifts(x);(sup if s else uns)[k]=(x,s) if s else x
 obs=[r for x,_ in sup.values() for r in x];correct=sum(r["prediction"]==r["truth"] for r in obs);errors=len(obs)-correct;el=Counter(r["leaf_id"] for r in obs if r["prediction"]!=r["truth"]);bf={}
 for fold in (2,3,4):
  x=[r for r in obs if int(r["outer_fold"])==fold];h=sum(r["prediction"]==r["truth"] for r in x);bf[str(fold)]={"calls":len(x),"correct":h,"precision":h/len(x) if x else 0}
 observed={"calls":len(obs),"correct":correct,"errors":errors,"precision":correct/len(obs) if obs else 0,"wilson_lower_95_one_sided":wilson(correct,len(obs)),"confirmatory_call_retention":len(obs)/len(calls) if calls else 0,"by_fold":bf,"max_error_leaf_share":max(el.values(),default=0)/errors if errors else 0};subset=observed["confirmatory_call_retention"]>=.80 and observed["precision"]>=.995 and observed["wilson_lower_95_one_sided"]>=.99 and all(v["calls"]>0 and v["precision"]>=.99 for v in bf.values()) and observed["max_error_leaf_share"]<=.30
 a.out.mkdir(parents=True);(a.out/"nulls").mkdir();vals=[];merkle=hashlib.sha256()
 for rep in range(999):
  total=0;details=[]
  for k,(base,_) in sup.items():
   rng=random.Random(int.from_bytes(hashlib.sha256(f"SHORT-FACTOR-NULL|{rep}|{'|'.join(k)}".encode()).digest()[:8],"big"));blocks=defaultdict(list)
   for r in base:blocks[r["leaf_id"]].append(r)
   ordered=[]
   for lf in sorted(blocks):b=list(blocks[lf]);rng.shuffle(b);ordered+=b
   valid=shifts(ordered);s=valid[rng.randrange(len(valid))];h=sum(r["prediction"]==ordered[(i+s)%len(ordered)]["truth"] for i,r in enumerate(ordered));total+=h;details.append({"stratum":k,"rows":len(ordered),"shift":s,"correct":h})
  q={"replicate":rep,"correct":total,"calls":len(obs),"strata":details};fp=a.out/"nulls"/f"null_{rep:04d}.json";fp.write_text(json.dumps(q,sort_keys=True)+"\n");merkle.update(f"{fp.name}\t{sha(fp)}\n".encode());vals.append(total)
 checks={"matched_subset_pass":subset,"retention_at_least_80pct":observed["confirmatory_call_retention"]>=.80,"observed_exceeds_all_999_null":correct>max(vals),"target_not_inferred":True,"strict_core_unchanged":True};status="PASS_SHORT_FACTOR_999_NULL_AUTHORIZE_TARGET_INFERENCE_ONLY" if all(checks.values()) else "FAIL_SHORT_FACTOR_NULL_NO_TARGET_INFERENCE";payload={"schema":"STRICT_V4_SHORT_FACTOR_MATCHED_NULL_V1","status":status,"selected_threshold":th,"target_call_policy":{"three_seed_unanimous":True,"min_confidence":th},"confirmatory_calls_before_matching":len(calls),"supported_strata":len(sup),"unsupported_strata":len(uns),"observed":observed,"null_files":999,"null_min_correct":min(vals),"null_median_correct":sorted(vals)[499],"null_max_correct":max(vals),"null_merkle_sha256":merkle.hexdigest(),"checks":checks,"oof_gate_sha256":sha(gp),"oof_consensus_sha256":sha(tp),"protocol_sha256":sha(PROTOCOL),"target_inferred":False,"strict_core_mutated":False};(a.out/"oof_null_gate.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n");print(json.dumps(payload,indent=2,sort_keys=True));return 0 if status.startswith("PASS") else 2
if __name__=="__main__":raise SystemExit(main())
