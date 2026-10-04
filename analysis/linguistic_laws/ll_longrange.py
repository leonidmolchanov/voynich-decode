#!/usr/bin/env python3
"""
LONG-RANGE CORRELATION test (the highest-stakes challenge).

Question: do papers' "Voynich has long-range structure like natural language"
claims survive a fair meaning-free generator null? For each method we report
REAL / GENERATOR(8 seeds) / global-shuffle floor / word-shuffle / English /
Latin, and ask specifically: does REAL EXCEED the drift GENERATOR (=breaker),
or only the shuffle (=drift-reproducible, not a breaker)?

Methods (as used in the literature):
  (A) Long-range mutual information I(d) on the CHARACTER/glyph stream, reported
      as EXCESS over each corpus's own global-shuffle floor (removes MI bias).
  (B) DFA on the WORD-LENGTH series (alpha; 0.5=white, >0.5=long-range).
  (C) DFA on symbol RETURN-INTERVAL (gap) series (Arutyunov et al. Hurst method),
      frequency-weighted over top glyphs -- mapping-free.
  (D) Power-spectral slope beta of the word-length series (S(f)~f^-beta).
"""
import json, sys, time
import numpy as np
import ll_common as C

t0 = time.time()
SEEDS = list(range(11, 19))          # 8 generator seeds
NSHUF = 12
MI_LAGS = [1,2,3,4,5,7,10,15,20,30,50,80,130,210,340,550,900,1500,2500]
DFA_SCALES = np.unique(np.round(np.logspace(np.log10(8), np.log10(5000), 26)).astype(int))
RI_SCALES  = np.unique(np.round(np.logspace(np.log10(4), np.log10(2000), 24)).astype(int))

def log(*a): print(*a, flush=True)

# ---------------------------------------------------------------- build data --
rows, wm, ws, wg = C.load_real()
laafu = C.G.build_laafu(rows)
real = C.Corpus("REAL_mol", wm, wg)
Nw = len(real.words)
log("REAL words", Nw, "glyphs", len(real.glyphs))

gens = []
for s in SEEDS:
    gwm, gwg = C.gen_corpus(rows, laafu, s)
    gens.append(C.Corpus("GEN%d" % s, gwm, gwg))
log("built", len(gens), "generator corpora  t=%.1fs" % (time.time()-t0))

rng = np.random.default_rng(20260930)
shuf_word = [C.shuffle_word_corpus(real, rng) for _ in range(NSHUF)]
shuf_glyph = [C.shuffle_glyph_corpus(real, rng) for _ in range(NSHUF)]

eng = C.nl_corpus("ENG", [C.ENG_TXT], Nw)
lat = C.nl_corpus("LAT", [C.LAT_TXT1, C.LAT_TXT2], Nw)
log("ENG words", len(eng.words), "glyphs", len(eng.glyphs),
    "| LAT words", len(lat.words), "glyphs", len(lat.glyphs))

# ============================================================ (A) char MI(d) ==
def mi_curve_excess(corp, floor_shufs=8):
    codes, sym2i = corp.flat_codes()
    K = len(sym2i)
    raw = C.mi_curve(codes, K, MI_LAGS)
    # own global-shuffle floor
    r2 = np.random.default_rng(hash(corp.name) % (2**31))
    floors = {d: [] for d in MI_LAGS}
    for _ in range(floor_shufs):
        c2 = codes.copy(); r2.shuffle(c2)
        for d in MI_LAGS:
            floors[d].append(C.mi_at_lag(c2, d, K)[0])
    floor_mean = {d: float(np.mean(floors[d])) for d in MI_LAGS}
    floor_sd = {d: float(np.std(floors[d])) for d in MI_LAGS}
    excess = {d: raw[d] - floor_mean[d] for d in MI_LAGS}
    return dict(raw=raw, floor=floor_mean, floor_sd=floor_sd, excess=excess, K=K)

log("\n(A) CHARACTER-STREAM long-range MI(d)  [excess over own global-shuffle floor, bits]")
miA = {}
miA['REAL'] = mi_curve_excess(real)
# generator mean over seeds
gen_ex = {d: [] for d in MI_LAGS}
for g in gens:
    m = mi_curve_excess(g, floor_shufs=4)
    for d in MI_LAGS: gen_ex[d].append(m['excess'][d])
miA['GEN'] = dict(excess={d: float(np.mean(gen_ex[d])) for d in MI_LAGS},
                  excess_sd={d: float(np.std(gen_ex[d])) for d in MI_LAGS})
miA['SHUF_word'] = mi_curve_excess(shuf_word[0])
miA['ENG'] = mi_curve_excess(eng)
miA['LAT'] = mi_curve_excess(lat)

hdr = "lag |   REAL   |  GEN(mean±sd)      | SHUF_word |   ENG    |   LAT"
log(hdr); log("-"*len(hdr))
for d in MI_LAGS:
    log("%4d | %8.4f | %7.4f ± %6.4f | %8.4f | %8.4f | %8.4f" % (
        d, miA['REAL']['excess'][d],
        miA['GEN']['excess'][d], miA['GEN']['excess_sd'][d],
        miA['SHUF_word']['excess'][d], miA['ENG']['excess'][d], miA['LAT']['excess'][d]))
log("(REAL raw MI floor level ~ %.4f bits; floor_sd@lag1 %.5f)" %
    (miA['REAL']['floor'][MI_LAGS[0]], miA['REAL']['floor_sd'][MI_LAGS[0]]))

# ============================================================ (B) DFA wlen ====
def dfa_alpha_wlen(corp):
    _, _, a = C.dfa(corp.wlen, DFA_SCALES)
    return a
log("\n(B) DFA alpha on WORD-LENGTH series (0.5=uncorrelated, >0.5=long-range persistent)")
gen_a = [dfa_alpha_wlen(g) for g in gens]
sw_a = [dfa_alpha_wlen(s) for s in shuf_word]
dfaB = dict(REAL=dfa_alpha_wlen(real),
            GEN_mean=float(np.mean(gen_a)), GEN_sd=float(np.std(gen_a)),
            SHUF_word_mean=float(np.mean(sw_a)), SHUF_word_sd=float(np.std(sw_a)),
            ENG=dfa_alpha_wlen(eng), LAT=dfa_alpha_wlen(lat))
log("  REAL       alpha = %.3f" % dfaB['REAL'])
log("  GEN        alpha = %.3f ± %.3f" % (dfaB['GEN_mean'], dfaB['GEN_sd']))
log("  SHUF_word  alpha = %.3f ± %.3f  (expect ~0.5)" % (dfaB['SHUF_word_mean'], dfaB['SHUF_word_sd']))
log("  ENG        alpha = %.3f" % dfaB['ENG'])
log("  LAT        alpha = %.3f" % dfaB['LAT'])

# ============================================================ (C) DFA gaps ====
def dfa_alpha_ri(corp):
    codes, sym2i = corp.flat_codes()
    a, det = C.dfa_returnintervals(codes, len(sym2i), RI_SCALES, topk=6, min_occ=300)
    return a
log("\n(C) DFA alpha on SYMBOL RETURN-INTERVAL (gap) series [Arutyunov Hurst], freq-weighted top-6")
gen_ri = [dfa_alpha_ri(g) for g in gens]
sg_ri = [dfa_alpha_ri(s) for s in shuf_glyph]
dfaC = dict(REAL=dfa_alpha_ri(real),
            GEN_mean=float(np.mean(gen_ri)), GEN_sd=float(np.std(gen_ri)),
            SHUF_glyph_mean=float(np.mean(sg_ri)), SHUF_glyph_sd=float(np.std(sg_ri)),
            ENG=dfa_alpha_ri(eng), LAT=dfa_alpha_ri(lat))
log("  REAL        alpha = %.3f" % dfaC['REAL'])
log("  GEN         alpha = %.3f ± %.3f" % (dfaC['GEN_mean'], dfaC['GEN_sd']))
log("  SHUF_glyph  alpha = %.3f ± %.3f  (expect ~0.5)" % (dfaC['SHUF_glyph_mean'], dfaC['SHUF_glyph_sd']))
log("  ENG         alpha = %.3f" % dfaC['ENG'])
log("  LAT         alpha = %.3f" % dfaC['LAT'])

# ============================================================ (D) PSD beta ====
log("\n(D) Power-spectral slope beta of WORD-LENGTH series (0=white, >0=long-range)")
gen_b = [C.psd_slope(g.wlen) for g in gens]
sw_b = [C.psd_slope(s.wlen) for s in shuf_word]
dfaD = dict(REAL=C.psd_slope(real.wlen),
            GEN_mean=float(np.mean(gen_b)), GEN_sd=float(np.std(gen_b)),
            SHUF_word_mean=float(np.mean(sw_b)), SHUF_word_sd=float(np.std(sw_b)),
            ENG=C.psd_slope(eng.wlen), LAT=C.psd_slope(lat.wlen))
log("  REAL       beta = %.3f" % dfaD['REAL'])
log("  GEN        beta = %.3f ± %.3f" % (dfaD['GEN_mean'], dfaD['GEN_sd']))
log("  SHUF_word  beta = %.3f ± %.3f" % (dfaD['SHUF_word_mean'], dfaD['SHUF_word_sd']))
log("  ENG        beta = %.3f" % dfaD['ENG'])
log("  LAT        beta = %.3f" % dfaD['LAT'])

# ---------------------------------------------------------------- dump ---------
out = dict(miA={k: (v if 'excess_sd' in v else {kk: v[kk] for kk in ('raw','floor','floor_sd','excess','K')})
                for k, v in miA.items()},
           dfaB=dfaB, dfaC=dfaC, dfaD=dfaD,
           meta=dict(seeds=SEEDS, nshuf=NSHUF, mi_lags=MI_LAGS,
                     real_words=Nw, real_glyphs=len(real.glyphs)))
with open("longrange_results.json", "w") as f:
    json.dump(out, f, indent=1, default=float)
log("\nwrote longrange_results.json  total t=%.1fs" % (time.time()-t0))
