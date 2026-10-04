#!/usr/bin/env python3
"""
TASK 4: net out register. Is there word-section clustering BEYOND what Currier A/B
already forces?  We compute, bias-corrected (own-shuffle excess):
   excess I(W;AB)                      -- dialect signal
   excess I(W;Section)  [unconditional]
   excess I(W;Section|AB) [conditional] -- section clustering *within* A and within B
                                           strata (= content beyond dialect register).
The conditional floor is a WITHIN-AB word-order shuffle (permute section labels
inside each dialect stratum), which preserves I(W;AB) and the AB-forced part of the
section composition, destroying only finer within-dialect clustering.

Done for REAL and for the calibrated self-citation generator (overlaid with the real
section+AB labels by position; the generator itself is dialect-blind).
"""
import json
import numpy as np
from mz_common import load_tokens, _codes, mi_word_part, label_parts
import generators as G

SEED = 20260930
REPS_GEN = 40
NSHUF = 200
NSHUF_GEN = 25

# calibrated params from run_decisive (mechanical-stat fit)
CAL = {'surface': dict(p_new=0.3, p_mut=0.2, window=250),
       'molecule': dict(p_new=0.3, p_mut=0.1, window=100)}


def mi_excess_simple(wids, parts, V, P, rng, nshuf):
    obs = mi_word_part(wids, parts, V, P)
    p = parts.copy()
    fl = np.empty(nshuf)
    for i in range(nshuf):
        rng.shuffle(p)
        fl[i] = mi_word_part(wids, p, V, P)
    return obs - fl.mean()


def cond_mi_excess(wids, sec, ab, V, Psec, rng, nshuf):
    """Excess I(W;Section|AB): weighted within-AB-stratum section MI minus the
    within-stratum-shuffle floor."""
    N = len(wids)
    obs = 0.0
    strata = []
    for a in np.unique(ab):
        mask = ab == a
        w_a = wids[mask]
        s_a = sec[mask].copy()
        n_a = mask.sum()
        mi_a = mi_word_part(w_a, s_a, V, Psec)
        obs += (n_a / N) * mi_a
        strata.append((w_a, s_a, n_a))
    fl = np.empty(nshuf)
    for i in range(nshuf):
        tot = 0.0
        for w_a, s_a, n_a in strata:
            sp = s_a.copy()
            rng.shuffle(sp)
            tot += (n_a / N) * mi_word_part(w_a, sp, V, Psec)
        fl[i] = tot
    return obs - fl.mean()


def analyze(tokens, sec, ab, V_hint, rng, nshuf):
    wids, V = _codes(tokens)
    Psec = len(np.unique(sec))
    Pab = len(np.unique(ab))
    ex_ab = mi_excess_simple(wids, ab, V, Pab, rng, nshuf)
    ex_sec = mi_excess_simple(wids, sec, V, Psec, rng, nshuf)
    ex_cond = cond_mi_excess(wids, sec, ab, V, Psec, rng, nshuf)
    return dict(excess_AB=float(ex_ab), excess_Section=float(ex_sec),
                excess_Section_given_AB=float(ex_cond),
                frac_section_from_AB=float(1 - ex_cond / ex_sec) if ex_sec > 0 else float('nan'))


def main():
    d = load_tokens()
    sec_arr, Psec, _ = label_parts(d['section'])
    ab_arr, Pab, _ = label_parts(d['ab'])
    out = {}
    for unit in ('surface', 'molecule'):
        rng = np.random.default_rng(SEED)
        real = d[unit]
        real_res = analyze(real, sec_arr, ab_arr, None, rng, NSHUF)
        # generator
        if unit == 'surface':
            innovate, mutate = G.surface_closures(real)
        else:
            innovate, mutate = G.mol_closures(real)
        c = CAL[unit]
        gen_ab, gen_sec, gen_cond = [], [], []
        for r in range(REPS_GEN):
            g = G.gen_self_citation(len(real), innovate, mutate, rng, c['p_new'], c['p_mut'], c['window'])
            gr = analyze(g, sec_arr, ab_arr, None, rng, NSHUF_GEN)
            gen_ab.append(gr['excess_AB'])
            gen_sec.append(gr['excess_Section'])
            gen_cond.append(gr['excess_Section_given_AB'])
        gen_res = dict(
            excess_AB=dict(mean=float(np.mean(gen_ab)), sd=float(np.std(gen_ab, ddof=1))),
            excess_Section=dict(mean=float(np.mean(gen_sec)), sd=float(np.std(gen_sec, ddof=1))),
            excess_Section_given_AB=dict(mean=float(np.mean(gen_cond)), sd=float(np.std(gen_cond, ddof=1))),
        )
        out[unit] = dict(real=real_res, gen=gen_res)
        print(f"\n[{unit}]")
        print(f"  REAL  excess I(W;AB)          = {real_res['excess_AB']:.4f}")
        print(f"  REAL  excess I(W;Section)     = {real_res['excess_Section']:.4f}")
        print(f"  REAL  excess I(W;Section|AB)  = {real_res['excess_Section_given_AB']:.4f}"
              f"   ({100*(1-real_res['frac_section_from_AB']):.0f}% of unconditional survives netting out A/B)")
        print(f"  GEN   excess I(W;AB)          = {gen_res['excess_AB']['mean']:.4f}±{gen_res['excess_AB']['sd']:.4f}")
        print(f"  GEN   excess I(W;Section)     = {gen_res['excess_Section']['mean']:.4f}±{gen_res['excess_Section']['sd']:.4f}")
        print(f"  GEN   excess I(W;Section|AB)  = {gen_res['excess_Section_given_AB']['mean']:.4f}±{gen_res['excess_Section_given_AB']['sd']:.4f}")
    json.dump(out, open('register_results.json', 'w'), indent=1)
    print("\nwrote register_results.json")


if __name__ == "__main__":
    main()
