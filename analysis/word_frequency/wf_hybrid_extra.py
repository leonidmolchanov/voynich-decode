#!/usr/bin/env python3
"""
Follow-up to wf_run.py: (1) properly brackets p_fresh so the HYBRID mechanism
(grammar-fresh draws + GLOBAL, non-mutating, unbounded-window preferential-
attachment copy -- i.e. mechanism (i)+(ii) with the recency window and
mutation removed) is compared to REAL at matched V, not undershooting it as
the coarse grid in wf_run.py did; (2) computes the frequency-of-frequencies
spectrum (fraction of types with exactly k occurrences, k=1..8) for real vs
every mechanism, which is the more granular diagnostic behind the aggregate
hapax_rate numbers. Read-only over project data; writes only wf_hybrid.json
in this directory.
"""
import sys, os, collections, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src", "voynich_generator"))
sys.path.insert(0, HERE)
import vgen_lib as L
import generator as G
import wf_common as C

rows = L.load()
laafu = G.build_laafu(rows)
real_mol = [r["mol"] for r in rows]
N_FULL = len(real_mol)
TARGET_V = len(set(real_mol))

NOCOPY_PARAMS = {h: dict(p_copy=0.0, p_mut=0.0, w_near=0.0, window=1) for h in G.DEFAULT_PARAMS}
fresh_syn, _ = G.generate(rows, params=NOCOPY_PARAMS, laafu=laafu, seed=999)
fresh_pool = [r["mol"] for r in fresh_syn]


def simulate_hybrid(n, p_fresh, pool, rng):
    out = []
    for i in range(n):
        if i == 0 or rng.random() < p_fresh:
            out.append(pool[rng.integers(0, len(pool))])
        else:
            out.append(out[int(rng.integers(0, i))])
    return out


def spectrum(tokens, kmax=8):
    c = collections.Counter(tokens)
    V = len(c)
    spec = collections.Counter(c.values())
    return {str(k): spec.get(k, 0) / V for k in range(1, kmax + 1)}


# ---- 1. bracket p_fresh to match TARGET_V, then report full stats ----------
coarse = [0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70, 0.80, 0.85, 0.87, 0.88, 0.90, 1.00]
scan = {}
for pf in coarse:
    Vs = []
    for s in range(3):
        rr = np.random.default_rng(6000 + s)
        seq = simulate_hybrid(N_FULL, pf, fresh_pool, rr)
        Vs.append(len(set(seq)))
    scan[pf] = float(np.mean(Vs))
    print("p_fresh=%.2f -> V~%.0f" % (pf, scan[pf]))

best_pf = min(coarse, key=lambda pf: abs(scan[pf] - TARGET_V))
print("chosen p_fresh =", best_pf, "(V~%.0f vs target %d)" % (scan[best_pf], TARGET_V))

stats = []
for s in range(10):
    rr = np.random.default_rng(9500 + s)
    seq = simulate_hybrid(N_FULL, best_pf, fresh_pool, rr)
    stats.append(C.corpus_stats_extended(seq))
agg = C.mean_sd(stats, ["N", "V", "TTR", "hapax_rate", "zipf_slope",
                         "top10", "top50", "top100", "zm_alpha", "zm_beta", "zm_r2"])
rr = np.random.default_rng(9500)
seq_rep = simulate_hybrid(N_FULL, best_pf, fresh_pool, rr)
heaps = C.heaps_curve(seq_rep)
print("HYBRID matched-V (p_fresh=%.2f):" % best_pf)
for k, v in agg.items():
    print("   %-10s %.4f +/- %.4f" % (k, v["mean"], v["sd"]))
print("   heaps_exponent", heaps["heaps_exponent"])

# ---- 2. frequency-of-frequencies spectrum, all mechanisms ------------------
theta = C.fit_theta_for_V(N_FULL, TARGET_V)
rr = np.random.default_rng(1)
crp_assign = C.simulate_crp(N_FULL, theta, rr)

rr = np.random.default_rng(1)
hyb_seq = simulate_hybrid(N_FULL, best_pf, fresh_pool, rr)

syn_default, _ = G.generate(rows, laafu=laafu, seed=20260930)
gen_default_mol = [r["mol"] for r in syn_default]

en_tok = C.load_english_tokens()
en_win = C.bootstrap_windows(en_tok, N_FULL, 1, seed=5)[0]

la_tok = C.load_latin_tokens()
la_win = C.bootstrap_windows(la_tok, N_FULL, 1, seed=5)[0]

spec_table = dict(
    real=spectrum(real_mol),
    gen_default=spectrum(gen_default_mol),
    gen_nocopy=spectrum(fresh_pool),
    crp=spectrum(crp_assign.tolist()),
    hybrid=spectrum(hyb_seq),
    english=spectrum(en_win),
    latin=spectrum(la_win),
)
print("\nfrequency-of-frequencies (fraction of TYPES with count=k):")
print("%-12s" % "k=", *(["%d" % k for k in range(1, 9)]))
for name, spec in spec_table.items():
    print("%-12s" % name, *("%.4f" % spec[str(k)] for k in range(1, 9)))

out = dict(hybrid_scan=scan, hybrid_best_pf=best_pf, hybrid_agg=agg,
           hybrid_heaps_exponent=heaps["heaps_exponent"], spectrum=spec_table)
with open(os.path.join(HERE, "wf_hybrid.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1, default=float)
print("\nWrote wf_hybrid.json")
