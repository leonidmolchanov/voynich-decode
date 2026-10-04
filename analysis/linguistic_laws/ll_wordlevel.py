#!/usr/bin/env python3
"""
Word/molecule-LEVEL long-range check (the layer the generator was actually fit
for -> the FAIREST long-range test; the char stream is a crude surface
reconstruction and is unfair to a molecule-layer generator).

  (E) DFA alpha on the word-LOG-FREQUENCY series (each token -> log10 global
      freq of its type; a scalar 'commonness' series). 0.5=white, >0.5=LRC.
  (F) DFA alpha on return-interval series of the top frequent WORD types.
  (G) trend+iid surrogate of the log-freq series: does slow drift explain it?
"""
import collections, time
import numpy as np
import ll_common as C
import generator as G

def log(*a): print(*a, flush=True)
t0=time.time()
rows, wm, ws, wg = C.load_real()
laafu=G.build_laafu(rows)
real=C.Corpus("REAL", wm, wg)
gens=[C.gen_corpus(rows,laafu,s) for s in range(41,47)]
gens=[C.Corpus("GEN",w,g) for w,g in gens]
rng=np.random.default_rng(1)
sw=[C.shuffle_word_corpus(real,rng) for _ in range(6)]
eng=C.nl_corpus("ENG",[C.ENG_TXT],len(real.words))
lat=C.nl_corpus("LAT",[C.LAT_TXT1,C.LAT_TXT2],len(real.words))
DFA=np.unique(np.round(np.logspace(np.log10(8),np.log10(5000),26)).astype(int))
RI =np.unique(np.round(np.logspace(np.log10(4),np.log10(1500),22)).astype(int))

def logfreq_series(corp):
    c=collections.Counter(corp.words)
    return np.array([np.log10(c[w]) for w in corp.words],float)
def dfa_a(x): return C.dfa(np.asarray(x,float),DFA)[2]

log("(E) DFA alpha on WORD-LOG-FREQUENCY ('commonness') series (0.5=white; >0.5=LRC)")
log("  REAL      alpha = %.3f" % dfa_a(logfreq_series(real)))
ga=[dfa_a(logfreq_series(g)) for g in gens]
log("  GEN       alpha = %.3f ± %.3f" % (np.mean(ga),np.std(ga)))
sa=[dfa_a(logfreq_series(s)) for s in sw]
log("  SHUF_word alpha = %.3f ± %.3f (expect ~0.5)" % (np.mean(sa),np.std(sa)))
log("  ENG       alpha = %.3f" % dfa_a(logfreq_series(eng)))
log("  LAT       alpha = %.3f" % dfa_a(logfreq_series(lat)))

# (F) word return-interval DFA (top-5 types, freq weighted)
def word_ri_alpha(corp):
    c=collections.Counter(corp.words)
    top=[w for w,_ in c.most_common(5)]
    al,wt=[],[]
    for w in top:
        pos=np.where(np.array(corp.words)==w)[0]
        if len(pos)<60: continue
        a=C.dfa(np.diff(pos).astype(float),RI)[2]
        if a==a: al.append(a); wt.append(len(pos))
    if not al: return float('nan')
    return float(np.average(al,weights=wt))
log("\n(F) DFA alpha on return-intervals of top-5 WORD types (freq-weighted)")
log("  REAL      alpha = %.3f" % word_ri_alpha(real))
gf=[word_ri_alpha(g) for g in gens]
log("  GEN       alpha = %.3f ± %.3f" % (np.mean(gf),np.std(gf)))
sf=[word_ri_alpha(s) for s in sw]
log("  SHUF_word alpha = %.3f ± %.3f (expect ~0.5)" % (np.mean(sf),np.std(sf)))
log("  ENG       alpha = %.3f" % word_ri_alpha(eng))
log("  LAT       alpha = %.3f" % word_ri_alpha(lat))

# (G) trend+iid surrogate of real logfreq series
def moving_avg(x,W): return np.convolve(x,np.ones(W)/W,mode='same')
log("\n(G) trend+iid surrogate of REAL word-log-freq series (keeps slow drift, iid fluctuations)")
xr=logfreq_series(real); rng=np.random.default_rng(9)
log("  real logfreq DFA alpha = %.3f" % dfa_a(xr))
for W in [100,400,1600]:
    tr=moving_avg(xr,W); vals=[]
    for _ in range(6):
        res=(xr-tr).copy(); rng.shuffle(res); vals.append(dfa_a(tr+res))
    log("  trend+iid W=%5d -> alpha = %.3f" % (W,np.mean(vals)))
log("\ntotal t=%.1fs"%(time.time()-t0))
