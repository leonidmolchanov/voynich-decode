#!/usr/bin/env python3
"""Fairness probe: map section6 excess-MI AND mechanical fidelity across the
self-citation (p_new,p_mut) plane at a fixed window, for the SURFACE unit.
Shows (a) drift emerges from copying not from section-fitting, (b) whether ANY
mechanically-plausible setting lands section-excess BELOW the real value, i.e.
whether real is at/below the meaning-free achievable floor (observational-equiv
ceiling)."""
import json
import numpy as np
from mz_common import load_tokens, _codes, mi_word_part, label_parts, corpus_stats
import generators as G

SEED = 20260930
WINDOW = 250
NSHUF = 25


def sec_excess(tokens, parts, V, P, rng):
    wids, Vt = _codes(tokens)
    obs = mi_word_part(wids, parts, Vt, P)
    p = parts.copy()
    fl = np.empty(NSHUF)
    for i in range(NSHUF):
        rng.shuffle(p)
        fl[i] = mi_word_part(wids, p, Vt, P)
    return obs - fl.mean()


def main():
    d = load_tokens()
    real = d['surface']
    tgt = corpus_stats(real)
    sec, P, _ = label_parts(d['section'])
    real_ex = sec_excess(real, sec, None, P, np.random.default_rng(1))
    print(f"REAL surface section6 excess = {real_ex:.4f}  (TTR={tgt['TTR']:.3f} "
          f"hapax={tgt['hapax_rate']:.3f} rep={tgt['repeat_rate']:.4f})")
    innovate, mutate = G.surface_closures(real)
    rng = np.random.default_rng(SEED)
    print(f"\nwindow={WINDOW}. cols: p_new x p_mut -> section_excess | TTR | rep | hapax "
          f"(mech OK if TTR in [.14,.20], rep in [.008,.016])")
    grid = {}
    for pn in [0.02, 0.05, 0.1, 0.2, 0.4, 0.7]:
        row = []
        for pm in [0.0, 0.1, 0.3, 0.6]:
            ex, ttr, rep, hap = [], [], [], []
            for r in range(4):
                g = G.gen_self_citation(len(real), innovate, mutate, rng, pn, pm, WINDOW)
                ex.append(sec_excess(g, sec, None, P, rng))
                s = corpus_stats(g)
                ttr.append(s['TTR']); rep.append(s['repeat_rate']); hap.append(s['hapax_rate'])
            e, t, rp, h = np.mean(ex), np.mean(ttr), np.mean(rep), np.mean(hap)
            mech = (0.14 <= t <= 0.20) and (0.008 <= rp <= 0.016)
            flag = "  <-mech-plausible" if mech else ""
            below = " BELOW_REAL" if e < real_ex else ""
            row.append((pn, pm, float(e), float(t), float(rp), float(h), bool(mech)))
            print(f"  p_new={pn:<4} p_mut={pm:<4} exc={e:.3f} TTR={t:.3f} rep={rp:.4f} "
                  f"hap={h:.3f}{flag}{below}")
        grid[pn] = row
    json.dump(dict(real_excess=float(real_ex), window=WINDOW, grid=grid),
              open('probe_map.json', 'w'), indent=1)
    print("\nwrote probe_map.json")


if __name__ == "__main__":
    main()
