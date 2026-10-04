#!/usr/bin/env python3
"""
Word-frequency / vocabulary-concentration investigation driver.
Read-only over project data (full_symbolic_factorization.tsv, the generator_spec
machine, and two pre-existing local natural-language text files used elsewhere
in the project). All new computation/writes stay under this directory.

Produces wf_results.json with every number quoted in NOTES_word_frequency.md.
"""
import sys, os, collections, hashlib, json, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
GEN_DIR = os.path.join(HERE, "..", "..", "src", "voynich_generator")
sys.path.insert(0, GEN_DIR)
sys.path.insert(0, HERE)

import vgen_lib as L
import generator as G
import wf_common as C

RESULTS = {}
SEED0 = 20260930
rng_global = np.random.default_rng(SEED0)

# ============================================================ 0. LOAD REAL =
rows = L.load()
laafu = G.build_laafu(rows)
real_mol_full = [r["mol"] for r in rows]
real_body_full = [" ".join(r["body"]) if r["body"] else "<EMPTY>" for r in rows]
real_surf_full = [r["surface"] for r in rows]
N_FULL = len(rows)
print("Loaded", N_FULL, "real tokens")

real_mol_stats = C.corpus_stats_extended(real_mol_full)
real_body_stats = C.corpus_stats_extended(real_body_full)
real_surf_stats = C.corpus_stats_extended(real_surf_full)
print("REAL molecule stats:", real_mol_stats)
print("REAL body stats:", real_body_stats)
print("REAL surface stats:", real_surf_stats)
RESULTS["real"] = dict(mol=real_mol_stats, body=real_body_stats, surf=real_surf_stats)

TARGET_V = real_mol_stats["V"]
TARGET_SLOPE = real_mol_stats["zipf_slope"]
print("TARGET_V(mol)=", TARGET_V, "TARGET_SLOPE=", TARGET_SLOPE)

real_heaps = C.heaps_curve(real_mol_full)
print("REAL heaps exponent (mol):", real_heaps["heaps_exponent"])
RESULTS["real"]["heaps_mol"] = real_heaps

# ============================================================ 1. NATURAL LANG
print("\n--- natural language baselines ---")
en_tok = C.load_english_tokens()
la_tok = C.load_latin_tokens()
la2_tok = C.load_latin_picatrix_tokens()
REPS_NL = 20

def nl_block(tokens, name, n=N_FULL, reps=REPS_NL, seed=1):
    wins = C.bootstrap_windows(tokens, n, reps, seed)
    stats = [C.corpus_stats_extended(w) for w in wins]
    agg = C.mean_sd(stats, ["N", "V", "TTR", "hapax_rate", "zipf_slope",
                             "top10", "top50", "top100", "zm_alpha", "zm_beta", "zm_r2"])
    hc = C.heaps_curve(tokens[:min(len(tokens), n * 3)] if len(tokens) > n else tokens)
    print(name, "source_len=", len(tokens), "heaps_exp=", hc["heaps_exponent"])
    for k in ["V", "TTR", "hapax_rate", "zipf_slope", "zm_alpha", "zm_beta"]:
        print("   ", k, "%.4f +/- %.4f" % (agg[k]["mean"], agg[k]["sd"]))
    return dict(agg=agg, heaps_exponent=hc["heaps_exponent"], source_len=len(tokens))

RESULTS["english"] = nl_block(en_tok, "ENGLISH (JQA writings)")
RESULTS["latin_caesar"] = nl_block(la_tok, "LATIN (Caesar, De Bello Gallico)")
if la2_tok:  # optional corpus; not shipped in the public release
    RESULTS["latin_picatrix"] = nl_block(la2_tok, "LATIN (Picatrix, medieval)")

# ============================================================ 2. GENERATOR =
print("\n--- generator (local-copy machine, DEFAULT_PARAMS) ---")
REPS_GEN = 10

def gen_block(params, name, reps=REPS_GEN):
    stats = []
    for s in range(reps):
        syn, _ = G.generate(rows, params=params, laafu=laafu, seed=SEED0 + s)
        syn_mol = [r["mol"] for r in syn]
        stats.append(C.corpus_stats_extended(syn_mol))
    agg = C.mean_sd(stats, ["N", "V", "TTR", "hapax_rate", "zipf_slope",
                             "top10", "top50", "top100", "zm_alpha", "zm_beta", "zm_r2"])
    # heaps on one representative run
    syn, _ = G.generate(rows, params=params, laafu=laafu, seed=SEED0)
    hc = C.heaps_curve([r["mol"] for r in syn])
    print(name)
    for k in ["V", "TTR", "hapax_rate", "zipf_slope", "zm_alpha", "zm_beta"]:
        print("   ", k, "%.4f +/- %.4f" % (agg[k]["mean"], agg[k]["sd"]))
    print("    heaps_exp", hc["heaps_exponent"])
    return dict(agg=agg, heaps_exponent=hc["heaps_exponent"])

RESULTS["gen_default"] = gen_block(G.DEFAULT_PARAMS, "GENERATOR default (grammar + local-recency copy)")

NOCOPY_PARAMS = {h: dict(p_copy=0.0, p_mut=0.0, w_near=0.0, window=1)
                 for h in G.DEFAULT_PARAMS}
RESULTS["gen_nocopy"] = gen_block(NOCOPY_PARAMS, "GENERATOR no-copy (grammar/PATHS only, mechanism i)")

# ============================================================ 3. CRP (ii) ==
print("\n--- mechanism (ii): CRP / Polya urn, global preferential attachment ---")
theta_fit = C.fit_theta_for_V(N_FULL, TARGET_V)
print("fitted theta =", theta_fit, " E[V]=", C.expected_V_crp(N_FULL, theta_fit))
crp_stats = []
for s in range(REPS_GEN):
    rr = np.random.default_rng(1000 + s)
    assign = C.simulate_crp(N_FULL, theta_fit, rr)
    crp_stats.append(C.corpus_stats_extended(assign.tolist()))
crp_agg = C.mean_sd(crp_stats, ["N", "V", "TTR", "hapax_rate", "zipf_slope",
                                 "top10", "top50", "top100", "zm_alpha", "zm_beta", "zm_r2"])
rr = np.random.default_rng(1000)
assign = C.simulate_crp(N_FULL, theta_fit, rr)
crp_heaps = C.heaps_curve(assign.tolist())
print("CRP theta=%.2f" % theta_fit)
for k in ["V", "TTR", "hapax_rate", "zipf_slope", "zm_alpha", "zm_beta"]:
    print("   ", k, "%.4f +/- %.4f" % (crp_agg[k]["mean"], crp_agg[k]["sd"]))
print("    heaps_exp", crp_heaps["heaps_exponent"])
RESULTS["crp"] = dict(theta=theta_fit, agg=crp_agg, heaps_exponent=crp_heaps["heaps_exponent"])

# ============================================================ 4. FIXED DICT (iii)
print("\n--- mechanism (iii): fixed finite Zipfian dictionary (bounded stock) ---")
fit_rng = np.random.default_rng(2000)
best = C.fit_fixed_dictionary(N_FULL, TARGET_V, TARGET_SLOPE, fit_rng, reps=3)
print("fit grid best:", best)
K_fit, alpha_fit = best["K"], best["alpha"]
dict_stats = []
for s in range(REPS_GEN):
    rr = np.random.default_rng(3000 + s)
    idx = C.simulate_fixed_dictionary(N_FULL, K_fit, alpha_fit, rr)
    dict_stats.append(C.corpus_stats_extended(idx.tolist()))
dict_agg = C.mean_sd(dict_stats, ["N", "V", "TTR", "hapax_rate", "zipf_slope",
                                   "top10", "top50", "top100", "zm_alpha", "zm_beta", "zm_r2"])
rr = np.random.default_rng(3000)
idx = C.simulate_fixed_dictionary(N_FULL, K_fit, alpha_fit, rr)
dict_heaps = C.heaps_curve(idx.tolist())
print("FIXED-DICT K=%d alpha=%.2f" % (K_fit, alpha_fit))
for k in ["V", "TTR", "hapax_rate", "zipf_slope", "zm_alpha", "zm_beta"]:
    print("   ", k, "%.4f +/- %.4f" % (dict_agg[k]["mean"], dict_agg[k]["sd"]))
print("    heaps_exp", dict_heaps["heaps_exponent"])
RESULTS["fixed_dict"] = dict(K=K_fit, alpha=alpha_fit, agg=dict_agg, heaps_exponent=dict_heaps["heaps_exponent"])

# sensitivity: literal "few hundred" K, and K=target_V sweep over alpha
print("\n--- fixed-dict sensitivity: literal 'few hundred' K=300 ---")
lit_stats = []
for s in range(REPS_GEN):
    rr = np.random.default_rng(4000 + s)
    idx = C.simulate_fixed_dictionary(N_FULL, 300, 1.0, rr)
    lit_stats.append(C.corpus_stats_extended(idx.tolist()))
lit_agg = C.mean_sd(lit_stats, ["V", "TTR", "hapax_rate", "zipf_slope"])
print("K=300 alpha=1.0:", {k: round(v["mean"], 4) for k, v in lit_agg.items()})
RESULTS["fixed_dict_K300"] = lit_agg

print("\n--- fixed-dict sensitivity: K forced = real V, alpha sweep ---")
sweep = {}
for a in [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5]:
    ss = []
    for s in range(6):
        rr = np.random.default_rng(5000 + s)
        idx = C.simulate_fixed_dictionary(N_FULL, TARGET_V, a, rr)
        ss.append(C.corpus_stats_extended(idx.tolist()))
    agg = C.mean_sd(ss, ["V", "TTR", "hapax_rate", "zipf_slope"])
    sweep[a] = {k: round(v["mean"], 4) for k, v in agg.items()}
    print(" alpha=%.1f" % a, sweep[a])
RESULTS["fixed_dict_Kreal_sweep"] = sweep

# ============================================================ 5. HYBRID ====
print("\n--- bonus: hybrid = grammar-fresh (i) + GLOBAL preferential-attachment copy (ii), no recency window ---")

def simulate_hybrid(n, p_fresh, fresh_pool, rng):
    out = []
    for i in range(n):
        if i == 0 or rng.random() < p_fresh:
            val = fresh_pool[rng.integers(0, len(fresh_pool))] if i > 0 else fresh_pool[0]
            # actually consume sequentially for variety; fallback random draw ok since
            # fresh_pool itself is i.i.d.-ish grammar output
            out.append(val)
        else:
            j = int(rng.integers(0, i))
            out.append(out[j])
    return out

# build a large pool of grammar-fresh molecules to draw from (from mechanism i)
fresh_syn, _ = G.generate(rows, params=NOCOPY_PARAMS, laafu=laafu, seed=999)
fresh_pool = [r["mol"] for r in fresh_syn]

def hybrid_target_V(p_fresh, seed):
    rr = np.random.default_rng(seed)
    seq = simulate_hybrid(N_FULL, p_fresh, fresh_pool, rr)
    return len(set(seq)), seq

# small grid search on p_fresh to hit TARGET_V
grid = [0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.22, 0.28, 0.35]
best_pf, best_err = None, None
for pf in grid:
    Vs = []
    for s in range(3):
        v, _ = hybrid_target_V(pf, 6000 + s)
        Vs.append(v)
    err = abs(np.mean(Vs) - TARGET_V)
    print("  p_fresh=%.2f -> V~%.0f" % (pf, np.mean(Vs)))
    if best_err is None or err < best_err:
        best_err, best_pf = err, pf
print("best p_fresh ~", best_pf)

hyb_stats = []
for s in range(REPS_GEN):
    _, seq = hybrid_target_V(best_pf, 7000 + s)
    hyb_stats.append(C.corpus_stats_extended(seq))
hyb_agg = C.mean_sd(hyb_stats, ["N", "V", "TTR", "hapax_rate", "zipf_slope",
                                 "top10", "top50", "top100", "zm_alpha", "zm_beta", "zm_r2"])
_, seq = hybrid_target_V(best_pf, 7000)
hyb_heaps = C.heaps_curve(seq)
print("HYBRID p_fresh=%.2f" % best_pf)
for k in ["V", "TTR", "hapax_rate", "zipf_slope", "zm_alpha", "zm_beta"]:
    print("   ", k, "%.4f +/- %.4f" % (hyb_agg[k]["mean"], hyb_agg[k]["sd"]))
print("    heaps_exp", hyb_heaps["heaps_exponent"])
RESULTS["hybrid"] = dict(p_fresh=best_pf, agg=hyb_agg, heaps_exponent=hyb_heaps["heaps_exponent"])

# ============================================================ 6. HELD-OUT ==
print("\n--- held-out (page fold, same recipe as generator_spec/heldout.py) ---")

def fold(folio):
    return int(hashlib.md5(folio.encode()).hexdigest(), 16) % 2

train_rows = [r for r in rows if fold(r["folio"]) == 0]
test_rows = [r for r in rows if fold(r["folio"]) == 1]
train_mol = [r["mol"] for r in train_rows]
test_mol = [r["mol"] for r in test_rows]
print("train N=%d test N=%d" % (len(train_rows), len(test_rows)))

train_set = set(train_mol)
test_oov_tokens = sum(1 for m in test_mol if m not in train_set)
test_oov_types = sum(1 for m in set(test_mol) if m not in train_set)
real_oov = dict(token_rate=test_oov_tokens / len(test_mol),
                type_rate=test_oov_types / len(set(test_mol)))
print("REAL held-out OOV (test tokens/types unseen in train):", real_oov)

# generator: fit on train, generate over test layout
syn_test, _ = G.generate(test_rows, laafu=laafu, fit_rows=train_rows, seed=777)
syn_test_mol = [r["mol"] for r in syn_test]
syn_oov_tokens = sum(1 for m in syn_test_mol if m not in train_set)
syn_oov_types = sum(1 for m in set(syn_test_mol) if m not in train_set)
gen_test_stats = C.corpus_stats_extended(syn_test_mol)
gen_oov = dict(token_rate=syn_oov_tokens / len(syn_test_mol),
               type_rate=syn_oov_types / len(set(syn_test_mol)))
real_test_stats = C.corpus_stats_extended(test_mol)
print("REAL test stats:", real_test_stats)
print("GEN(fit on train) test stats:", gen_test_stats, "OOV:", gen_oov)

# fixed-dictionary literally fit as train's OWN empirical distribution, resample len(test)
train_counts = collections.Counter(train_mol)
train_types = list(train_counts.keys())
train_p = np.array([train_counts[t] for t in train_types], dtype=float)
train_p /= train_p.sum()
rr = np.random.default_rng(8000)
dict_test_stats_list = []
dict_oov_list = []
for s in range(REPS_GEN):
    rr = np.random.default_rng(8000 + s)
    draw_idx = rr.choice(len(train_types), size=len(test_mol), p=train_p)
    draw = [train_types[i] for i in draw_idx]
    dict_test_stats_list.append(C.corpus_stats_extended(draw))
    dict_oov_list.append(sum(1 for m in draw if m not in train_set) / len(draw))
dict_test_agg = C.mean_sd(dict_test_stats_list, ["V", "TTR", "hapax_rate", "zipf_slope"])
print("FIXED-DICT(=train empirical dist) resampled-to-test-length stats:",
      {k: round(v["mean"], 4) for k, v in dict_test_agg.items()}, "OOV(mean)=", np.mean(dict_oov_list))

# CRP continued from train: fit theta on TRAIN's own V, then continue simulation
# for len(test) MORE draws (global memory carries across the fold boundary),
# measure the NEW segment's stats + the analytic new-type ("OOV") rate.
V_train = len(train_types)
theta_train = C.fit_theta_for_V(len(train_mol), V_train)
crp_cont_stats = []
crp_cont_newrate = []
for s in range(REPS_GEN):
    rr = np.random.default_rng(9000 + s)
    n_total = len(train_mol) + len(test_mol)
    assign = C.simulate_crp(n_total, theta_train, rr)
    seg = assign[len(train_mol):]
    crp_cont_stats.append(C.corpus_stats_extended(seg.tolist()))
    train_ids = set(assign[:len(train_mol)].tolist())
    new_in_seg = sum(1 for x in seg.tolist() if x not in train_ids)
    crp_cont_newrate.append(new_in_seg / len(seg))
crp_cont_agg = C.mean_sd(crp_cont_stats, ["V", "TTR", "hapax_rate", "zipf_slope"])
print("CRP continued from train (theta=%.2f): test-segment stats:" % theta_train,
      {k: round(v["mean"], 4) for k, v in crp_cont_agg.items()},
      "new-type(OOV) rate mean=", np.mean(crp_cont_newrate))

RESULTS["heldout"] = dict(
    train_N=len(train_mol), test_N=len(test_mol),
    real_test=real_test_stats, real_oov=real_oov,
    gen_test=gen_test_stats, gen_oov=gen_oov,
    fixed_dict_train_fit_test=dict_test_agg, fixed_dict_train_fit_oov=float(np.mean(dict_oov_list)),
    crp_theta_train=theta_train,
    crp_continued_test=crp_cont_agg, crp_continued_newrate=float(np.mean(crp_cont_newrate)),
)

# ============================================================ SAVE =========
with open(os.path.join(HERE, "wf_results.json"), "w", encoding="utf-8") as fh:
    json.dump(RESULTS, fh, indent=1, default=float)
print("\nWrote wf_results.json")
