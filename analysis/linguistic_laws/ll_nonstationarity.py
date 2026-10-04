#!/usr/bin/env python3
"""
DECISIVE follow-up to the long-range result: is real Voynich's long-range
correlation a GENUINE sequential dependency, or COMPOSITIONAL NONSTATIONARITY
(topic / section / hand / scribal drift)? The task says nonstationarity is
meaning-free-reproducible (a drift generator makes it) and must NOT be counted
as a pro-language breaker.

Three tests:
  (1) NONSTATIONARITY MAGNITUDE  I(glyph;block) and I(wlen-bin;block):
      how much do glyph-frequency and word-length DISTRIBUTIONS drift across the
      manuscript?  real vs generator vs English vs Latin.
  (2) TREND+IID SURROGATE (decisive): rebuild the word-length series as
      slow_moving_average(W) + shuffled_residuals -> keeps real's slow drift
      profile but ZERO genuine sequential dependency in the fluctuations. If its
      DFA alpha ~= real's alpha, the long-range persistence IS the slow drift.
  (3) BLOCK-LOCAL SHUFFLE: shuffle within consecutive blocks of size B (keeps
      coarse profile > B, destroys all order < B). If long-range alpha survives
      at small B, the signal lives in coarse drift, not fine sequential grammar.
"""
import json, time
import numpy as np
import ll_common as C

t0 = time.time()
def log(*a): print(*a, flush=True)

rows, wm, ws, wg = C.load_real()
import generator as G
laafu = G.build_laafu(rows)
real = C.Corpus("REAL", wm, wg)
gens = [C.gen_corpus(rows, laafu, s) for s in range(21, 27)]
gens = [C.Corpus("GEN%d" % i, w, g) for i, (w, g) in enumerate(gens)]
eng = C.nl_corpus("ENG", [C.ENG_TXT], len(real.words))
lat = C.nl_corpus("LAT", [C.LAT_TXT1, C.LAT_TXT2], len(real.words))
DFA_SCALES = np.unique(np.round(np.logspace(np.log10(8), np.log10(5000), 26)).astype(int))
RI_SCALES  = np.unique(np.round(np.logspace(np.log10(4), np.log10(2000), 24)).astype(int))

# ============================================ (1) nonstationarity magnitude ===
def I_symbol_block(seq_codes, K, nblocks):
    """I(symbol; contiguous-block-id) in bits, minus its own shuffle floor."""
    N = len(seq_codes)
    blk = np.minimum((np.arange(N) * nblocks) // N, nblocks - 1)
    def mi(codes):
        idx = codes * nblocks + blk
        joint = np.bincount(idx, minlength=K * nblocks).astype(float).reshape(K, nblocks)
        joint /= N
        ps = joint.sum(1); pb = joint.sum(0)
        nz = joint > 0
        out = np.outer(ps, pb)
        return float((joint[nz] * np.log2(joint[nz] / out[nz])).sum())
    obs = mi(seq_codes)
    fl = []
    r = np.random.default_rng(7)
    for _ in range(6):
        c = seq_codes.copy(); r.shuffle(c); fl.append(mi(c))
    return obs - np.mean(fl)

def glyph_block_drift(corp, nblocks=20):
    codes, s2i = corp.flat_codes()
    return I_symbol_block(codes, len(s2i), nblocks)

def wlen_block_drift(corp, nblocks=20, nbins=6):
    # bin word length into nbins quantile bins, then I(lenbin; block)
    wl = corp.wlen
    qs = np.quantile(wl, np.linspace(0, 1, nbins + 1)[1:-1])
    binned = np.digitize(wl, qs)
    K = binned.max() + 1
    return I_symbol_block(binned.astype(np.int64), K, nblocks)

log("(1) NONSTATIONARITY (drift) magnitude, excess I(.;block=20) over shuffle floor [bits]")
log("            glyph-freq drift   word-length drift")
for nm, cp in [("REAL", real), ("ENG", eng), ("LAT", lat)]:
    log("  %-6s   %10.4f        %10.4f" % (nm, glyph_block_drift(cp), wlen_block_drift(cp)))
gd = [glyph_block_drift(g) for g in gens]; ld = [wlen_block_drift(g) for g in gens]
log("  GEN      %10.4f±%.4f  %10.4f±%.4f" % (np.mean(gd), np.std(gd), np.mean(ld), np.std(ld)))

# ============================================ (2) trend + iid surrogate =======
def dfa_a(x): return C.dfa(np.asarray(x, float), DFA_SCALES)[2]

def moving_avg(x, W):
    x = np.asarray(x, float)
    k = np.ones(W) / W
    return np.convolve(x, k, mode='same')

def trend_iid_surrogate(x, W, rng):
    x = np.asarray(x, float)
    tr = moving_avg(x, W)
    res = x - tr
    rng.shuffle(res)                # destroy ALL dependency in fluctuations
    return tr + res

log("\n(2) TREND+IID surrogate of REAL word-length series (keeps slow drift, iid fluctuations)")
log("    real wlen DFA alpha = %.3f ;  full word-order shuffle alpha ~ 0.506" % dfa_a(real.wlen))
rng = np.random.default_rng(11)
for W in [50, 100, 200, 400, 800, 1600]:
    a = np.mean([dfa_a(trend_iid_surrogate(real.wlen, W, rng)) for _ in range(6)])
    log("    trend+iid  W=%5d ->  alpha = %.3f  (matches real if slow drift explains LRC)" % (W, a))

# ============================================ (3) block-local shuffle =========
def block_shuffle(x, B, rng):
    x = np.array(x, float); N = len(x)
    for i in range(0, N, B):
        seg = x[i:i+B]; rng.shuffle(seg); x[i:i+B] = seg
    return x

def block_shuffle_codes(codes, B, rng):
    c = codes.copy(); N = len(c)
    for i in range(0, N, B):
        seg = c[i:i+B]; rng.shuffle(seg); c[i:i+B] = seg
    return c

log("\n(3) BLOCK-LOCAL shuffle of REAL (destroys order < B, keeps coarse profile > B)")
log("    word-length DFA alpha (real=%.3f):" % dfa_a(real.wlen))
rng = np.random.default_rng(3)
for B in [20, 50, 100, 300, 1000]:
    a = np.mean([dfa_a(block_shuffle(real.wlen, B, rng)) for _ in range(6)])
    log("      B=%5d -> alpha = %.3f" % (B, a))

codes, s2i = real.flat_codes(); K = len(s2i)
base_ri = C.dfa_returnintervals(codes, K, RI_SCALES, topk=6, min_occ=300)[0]
log("    return-interval (glyph gaps) DFA alpha, real = %.3f:" % base_ri)
rng = np.random.default_rng(5)
for B in [50, 200, 1000, 5000]:
    aa = []
    for _ in range(4):
        cs = block_shuffle_codes(codes, B, rng)
        aa.append(C.dfa_returnintervals(cs, K, RI_SCALES, topk=6, min_occ=300)[0])
    log("      char block B=%5d -> return-interval alpha = %.3f" % (B, np.mean(aa)))

log("\ntotal t=%.1fs" % (time.time() - t0))
