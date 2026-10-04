#!/usr/bin/env python3
"""TASK 1: reproduce the BASIC Montemurro-Zanette result.
Real word-section information (MI, bits) vs the word-order-shuffle null, for
SURFACE words (their unit) AND the molecule layer, across partitions:
  sections (6), Currier A/B (2), and equal-length word blocks P in {2,5,6,10,20}.
Shuffle null destroys clustering -> the finite-sample MI floor. Excess = obs - floor.
"""
import json
import numpy as np
from mz_common import (load_tokens, _codes, excess_mi, make_parts_blocks,
                       label_parts, corpus_stats)

SEED = 20260930
N_SHUF = 500


def main():
    d = load_tokens()
    N = len(d['surface'])
    rng = np.random.default_rng(SEED)
    out = {}
    for unit in ('surface', 'molecule'):
        toks = d[unit]
        wids, V = _codes(toks)
        out[unit] = {'stats': corpus_stats(toks), 'V': V, 'partitions': {}}
        # partitions
        parts_defs = {}
        sp, P, _ = label_parts(d['section']); parts_defs['sections6'] = (sp, P)
        ap, P2, _ = label_parts(d['ab']); parts_defs['currierAB'] = (ap, P2)
        for Pb in (2, 5, 6, 10, 20):
            parts_defs[f'blocks{Pb}'] = (make_parts_blocks(N, Pb), Pb)
        for pname, (parts, P) in parts_defs.items():
            r = excess_mi(wids, parts, V, P, rng, n_shuffle=N_SHUF)
            out[unit]['partitions'][pname] = r
            print(f"{unit:9s} {pname:11s} P={P:2d}  MI={r['obs']:.4f}  "
                  f"floor={r['floor_mean']:.4f}±{r['floor_sd']:.4f}  "
                  f"excess={r['excess']:.4f}  z={r['z_vs_floor']:.1f}")
    with open('basic_results.json', 'w') as f:
        json.dump(out, f, indent=1)
    print("\nwrote basic_results.json")


if __name__ == "__main__":
    main()
