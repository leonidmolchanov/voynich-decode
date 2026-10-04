#!/usr/bin/env python3
"""
TASKS 2 & 3: the DECISIVE generator-null comparison.

For each unit (surface, molecule):
  * calibrate the self-citation drift generator to MECHANICAL stats only
    (TTR, hapax, repeat-rate, Zipf) -- report fidelity incl. the floor gens;
  * compute the REAL Montemurro excess-MI for sections(6), Currier A/B, blocks(6,20);
  * for each generator {iid_bag, markov1_tok, self_citation@calibrated}, run NREPS
    reps, compute each rep's own-shuffle-corrected excess, aggregate, and z/p of REAL
    vs the generator distribution;
  * sweep the self-citation WINDOW (drift scale) and report section-MI excess vs window
    -> exposes the observational-equivalence ceiling (which window reproduces real).

Fair-comparison note: every corpus (real and each generated rep) is compared to ITS
OWN word-order-shuffle floor, so different vocabularies/frequency spectra do not bias
the excess.  Section labels are overlaid by position; no generator ever sees them.
"""
import json, time, itertools
import numpy as np
from mz_common import (load_tokens, _codes, mi_word_part, excess_mi,
                       make_parts_blocks, label_parts, corpus_stats)
import generators as G

SEED = 20260930
NREPS = 60          # >=50 required
GEN_SHUF = 25       # shuffles per generated rep for its own floor
REAL_SHUF = 500


def build_partitions(d):
    N = len(d['surface'])
    parts = {}
    sp, P, _ = label_parts(d['section']); parts['sections6'] = (sp, P)
    ap, P2, _ = label_parts(d['ab']); parts['currierAB'] = (ap, P2)
    parts['blocks6'] = (make_parts_blocks(N, 6), 6)
    parts['blocks20'] = (make_parts_blocks(N, 20), 20)
    return parts


def excess_of_tokens(tokens, parts_defs, rng, n_shuffle):
    wids, V = _codes(tokens)
    res = {}
    for pname, (parts, P) in parts_defs.items():
        res[pname] = excess_mi(wids, parts, V, P, rng, n_shuffle=n_shuffle)['excess']
    return res


def calibrate(real, innovate, mutate, rng, keys=('TTR', 'hapax_rate', 'repeat_rate', 'zipf_slope')):
    tgt = corpus_stats(real)
    N = len(real)
    grid = list(itertools.product([0.05, 0.1, 0.15, 0.2, 0.3],
                                  [0.1, 0.2, 0.4],
                                  [50, 100, 250, 500]))
    best = None
    for pn, pm, w in grid:
        s = corpus_stats(G.gen_self_citation(N, innovate, mutate, rng, pn, pm, w))
        loss = sum(((s[k] - tgt[k]) / abs(tgt[k])) ** 2 for k in keys)
        if best is None or loss < best[0]:
            best = (loss, pn, pm, w, s)
    return dict(loss=best[0], p_new=best[1], p_mut=best[2], window=best[3],
                stats={k: float(v) for k, v in best[4].items()}, target=tgt)


def z_p(real_val, gen_vals):
    arr = np.array(gen_vals, float)
    m, sd = arr.mean(), arr.std(ddof=1)
    z = (real_val - m) / sd if sd > 0 else float('inf')
    p = (1 + (arr >= real_val).sum()) / (len(arr) + 1)   # P(gen excess >= real)
    return float(m), float(sd), float(z), float(p)


def run_unit(unit, d, parts_defs):
    print(f"\n########## UNIT = {unit} ##########", flush=True)
    real = d[unit]
    rng = np.random.default_rng(SEED)
    if unit == 'surface':
        innovate, mutate = G.surface_closures(real)
    else:
        innovate, mutate = G.mol_closures(real)

    # ---- calibrate ----
    t0 = time.time()
    cal = calibrate(real, innovate, mutate, rng)
    print(f"calibrated ({time.time()-t0:.0f}s): p_new={cal['p_new']} p_mut={cal['p_mut']} "
          f"window={cal['window']} loss={cal['loss']:.3f}")
    tgt = cal['target']
    print("  fidelity  metric     real     selfcite")
    for k in ('V', 'TTR', 'hapax_rate', 'repeat_rate', 'zipf_slope', 'H1'):
        print(f"    {k:12s} {tgt[k]:8.4f} {cal['stats'][k]:8.4f}")

    # floor-gen fidelity
    floor_stats = {}
    for name, fn in [('iid_bag', G.gen_iid_bag), ('markov1_tok', G.gen_markov1_tok)]:
        floor_stats[name] = {k: float(v) for k, v in corpus_stats(fn(real, rng)).items()}

    # ---- real excess ----
    real_ex = excess_of_tokens(real, parts_defs, rng, REAL_SHUF)
    print("  REAL excess-MI:", {k: round(v, 4) for k, v in real_ex.items()})

    # ---- generator distributions ----
    gens = {
        'iid_bag': lambda: G.gen_iid_bag(real, rng),
        'markov1_tok': lambda: G.gen_markov1_tok(real, rng),
        'self_citation': lambda: G.gen_self_citation(len(real), innovate, mutate, rng,
                                                     cal['p_new'], cal['p_mut'], cal['window']),
    }
    gen_ex = {g: {p: [] for p in parts_defs} for g in gens}
    for gname, gfn in gens.items():
        t0 = time.time()
        for r in range(NREPS):
            ex = excess_of_tokens(gfn(), parts_defs, rng, GEN_SHUF)
            for p in parts_defs:
                gen_ex[gname][p].append(ex[p])
        print(f"  gen {gname:14s} {NREPS} reps in {time.time()-t0:.0f}s", flush=True)

    # ---- decisive table ----
    decisive = {}
    for gname in gens:
        decisive[gname] = {}
        for p in parts_defs:
            m, sd, z, pv = z_p(real_ex[p], gen_ex[gname][p])
            decisive[gname][p] = dict(real=real_ex[p], gen_mean=m, gen_sd=sd, z=z, p=pv,
                                      ratio=real_ex[p] / m if m > 0 else float('inf'))

    # ---- window sweep (drift scale) on sections6 ----
    windows = [10, 25, 50, 100, 250, 500, 1000, 2000]
    sweep = {}
    t0 = time.time()
    for w in windows:
        vals = []
        for r in range(30):
            g = G.gen_self_citation(len(real), innovate, mutate, rng, cal['p_new'], cal['p_mut'], w)
            ex = excess_of_tokens(g, {'sections6': parts_defs['sections6']}, rng, GEN_SHUF)
            vals.append(ex['sections6'])
        sweep[w] = dict(mean=float(np.mean(vals)), sd=float(np.std(vals, ddof=1)))
    print(f"  window sweep in {time.time()-t0:.0f}s")

    return dict(calibration=cal, floor_stats=floor_stats, real_excess=real_ex,
                decisive=decisive, window_sweep=sweep)


def main():
    d = load_tokens()
    parts_defs = build_partitions(d)
    out = {}
    for unit in ('surface', 'molecule'):
        out[unit] = run_unit(unit, d, parts_defs)
    json.dump(out, open('decisive_results.json', 'w'), indent=1)
    print("\nwrote decisive_results.json")

    # concise console summary
    for unit in ('surface', 'molecule'):
        print(f"\n===== DECISIVE SUMMARY [{unit}] =====")
        dec = out[unit]['decisive']
        for p in ('sections6', 'currierAB', 'blocks6', 'blocks20'):
            print(f"  [{p}] real_excess={out[unit]['real_excess'][p]:.4f}")
            for g in ('iid_bag', 'markov1_tok', 'self_citation'):
                s = dec[g][p]
                print(f"      {g:14s} gen={s['gen_mean']:.4f}±{s['gen_sd']:.4f}  "
                      f"real/gen={s['ratio']:.2f}  z={s['z']:.1f}  p={s['p']:.3f}")
        print("  window sweep (sections6 excess):",
              {w: round(v['mean'], 4) for w, v in out[unit]['window_sweep'].items()})


if __name__ == "__main__":
    main()
