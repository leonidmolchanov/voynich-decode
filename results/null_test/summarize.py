#!/usr/bin/env python3
"""Reads results.json (produced by nulltest.py) and prints the decisive
real-vs-null comparison tables used in FINDINGS.md. Read-only, no data
mutation. Run after nulltest.py."""
import json, os

OUT = os.path.dirname(os.path.abspath(__file__))

with open(OUT + "/results.json", encoding="utf-8") as f:
    R = json.load(f)

HEADLINE_KEYS = ["MI1", "repeat_rate", "heaps", "burstiness", "MI_boundary"]


def fmt(d):
    if d["z"] != d["z"]:  # nan
        return "n/a"
    return f"real={d['real']:.4f} null_mean={d['null_mean']:.4f} sd={d['null_sd']:.4f} z={d['z']:7.2f} p={d['p']:.3f}"


def main():
    for arm_name, arm in R.items():
        real = arm["real_raw"]
        print("=" * 80)
        print(f"{arm_name}  V={arm['V']} n_lines={arm['n_lines']} n_tokens={arm['n_tokens']}")
        print(f"  real: H1={real['H1']:.4f} H2={real['H2']:.4f} MI1={real['MI1']:.4f} "
              f"({100*real['MI1']/real['H1']:.2f}% of H1)  repeat_rate={real['repeat_rate']:.4f} "
              f"heaps={real['heaps']:.4f}  burstiness={real['burstiness']:.4f}  ttr={real['ttr']:.5f}")
        for gname in ["iid", "perm", "markov1"]:
            print(f"  vs {gname}:")
            s = arm["stats"][gname]
            for k in HEADLINE_KEYS:
                print(f"    {k:14s} {fmt(s[k])}")
        print("  MI at lag d=1..10 (real / markov1 z,p):")
        for d in range(1, 11):
            k = f"MI_lag{d}"
            mk = arm["stats"]["markov1"][k]
            npr = real["npairs_lag"][str(d)]
            rv = real["milags"][str(d)]
            print(f"    lag{d:2d}  n={npr:6d}  real={rv:7.4f}  markov1_z={mk['z']:7.2f} p={mk['p']:.3f}")


if __name__ == "__main__":
    main()
