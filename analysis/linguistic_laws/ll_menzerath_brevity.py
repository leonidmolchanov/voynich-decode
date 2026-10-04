#!/usr/bin/env python3
"""
Menzerath-Altmann law, Brevity/Zipf-abbreviation residual, word-length
distribution (pastiche-paper claim), and confirmation of the generator-FAVOURING
points (weak word order + low conditional entropy).

For each: real value / generator(seeds) / within-line or word-order shuffle /
English / Latin, and a verdict.
"""
import collections, math, time
import numpy as np
from scipy import stats
import ll_common as C
import generator as G

def log(*a): print(*a, flush=True)
t0 = time.time()

rows, wm, ws, wg = C.load_real()
laafu = G.build_laafu(rows)
real = C.Corpus("REAL", wm, wg)             # words=molecules, wordglyphs=surface glyph tokens
SEEDS = list(range(31, 37))

def gen_full(seed):
    syn, _ = G.generate(rows, laafu=laafu, seed=seed)
    return syn
gens_syn = [gen_full(s) for s in SEEDS]
def syn_corpus(syn):
    return C.Corpus("GEN", [s['mol'] for s in syn], [C.L.tokenize(s['surface']) for s in syn])
gens = [syn_corpus(s) for s in gens_syn]

eng = C.nl_corpus("ENG", [C.ENG_TXT], len(real.words))
lat = C.nl_corpus("LAT", [C.LAT_TXT1, C.LAT_TXT2], len(real.words))

VOW = set("aeiouy")
def syllabify_count(word):
    """crude: number of maximal vowel groups = syllable count (>=1)."""
    n, prev = 0, False
    for ch in word:
        v = ch in VOW
        if v and not prev: n += 1
        prev = v
    return max(n, 1)

# ================================================================ MENZERATH ===
# M1 word -> constituent size.
#   Voynich: constituent = glyph-token; size = its EVA char length; x = #tokens.
#   NL:      constituent = syllable;    size = letters/syllable;  x = #syllables.
def menzerath_word(corp, nl=False):
    xs, ys = [], []
    for wgi, w in zip(corp.wordglyphs, corp.words):
        if nl:
            wordstr = "".join(wgi)
            ns = syllabify_count(wordstr)
            if ns < 1: continue
            xs.append(ns); ys.append(len(wordstr) / ns)     # mean letters per syllable
        else:
            if not wgi: continue
            xs.append(len(wgi)); ys.append(np.mean([len(t) for t in wgi]))  # mean EVA chars/token
    xs = np.array(xs, float); ys = np.array(ys, float)
    r, p = stats.spearmanr(xs, ys)
    # mean-y per x (the Menzerath curve)
    curve = {}
    for x in sorted(set(xs.astype(int))):
        m = xs == x
        if m.sum() >= 20: curve[int(x)] = float(ys[m].mean())
    return dict(spearman=float(r), p=float(p), curve=curve, n=len(xs))

log("=== MENZERATH-ALTMANN (M1: word length in constituents  vs  mean constituent size) ===")
log("MAL predicts NEGATIVE slope (longer words -> shorter constituents).")
mreal = menzerath_word(real)
mg = [menzerath_word(g) for g in gens]
log("  REAL   rho = %+.3f (p=%.1e)   curve(len->size): %s" % (
    mreal['spearman'], mreal['p'], {k: round(v,3) for k,v in list(mreal['curve'].items())[:8]}))
log("  GEN    rho = %+.3f ± %.3f" % (np.mean([m['spearman'] for m in mg]), np.std([m['spearman'] for m in mg])))
log("  ENG    rho = %+.3f  (syllable-based, illustrative)" % menzerath_word(eng, nl=True)['spearman'])
log("  LAT    rho = %+.3f  (syllable-based, illustrative)" % menzerath_word(lat, nl=True)['spearman'])

# M2 line -> word.  x = line length in words; y = mean word length (glyph-tokens).
def menzerath_line_real(rows):
    lines = C.L.group_lines(rows)
    xs, ys = [], []
    for ln in lines:
        toks = [C.L.tokenize(r['surface']) for r in ln]
        toks = [t for t in toks if t]
        if len(toks) < 2: continue
        xs.append(len(toks)); ys.append(np.mean([len(t) for t in toks]))
    return np.array(xs,float), np.array(ys,float)

def menzerath_line_gen(syn):
    lines = collections.OrderedDict()
    for s in syn:
        lines.setdefault((s['folio'], s['line']), []).append(C.L.tokenize(s['surface']))
    xs, ys = [], []
    for ln in lines.values():
        toks=[t for t in ln if t]
        if len(toks) < 2: continue
        xs.append(len(toks)); ys.append(np.mean([len(t) for t in toks]))
    return np.array(xs,float), np.array(ys,float)

xr, yr = menzerath_line_real(rows)
rr, pr = stats.spearmanr(xr, yr)
glist=[]
for syn in gens_syn:
    xg,yg = menzerath_line_gen(syn); glist.append(stats.spearmanr(xg,yg)[0])
log("\n=== MENZERATH (M2: LINE length in words vs mean word length) ===")
log("  REAL   rho = %+.3f (p=%.1e)" % (rr, pr))
log("  GEN    rho = %+.3f ± %.3f" % (np.mean(glist), np.std(glist)))

# ================================================================ BREVITY =====
def brevity(corp):
    cnt = collections.Counter(corp.words)
    typ = list(cnt)
    length = {w: len(wgi) for w, wgi in zip(corp.words, corp.wordglyphs)}
    f = np.array([cnt[w] for w in typ], float)
    ln = np.array([length[w] for w in typ], float)
    rho_type, _ = stats.spearmanr(np.log(f), ln)   # type-level
    # frequency-binned mean length
    bins = {"hapax(=1)": (f==1), "2-5": (f>=2)&(f<=5), "6-20": (f>=6)&(f<=20), "21+": (f>=21)}
    binmean = {k: (float(ln[m].mean()) if m.sum() else float('nan'), int(m.sum())) for k,m in bins.items()}
    return dict(rho_type=float(rho_type), binmean=binmean,
                hapax_len=float(ln[f==1].mean()), common_len=float(ln[f>=6].mean()))

log("\n=== BREVITY / ZIPF ABBREVIATION (type-level Spearman(log freq, length); note: ORDER-INVARIANT => word-shuffle == real) ===")
br = brevity(real); bg = [brevity(g) for g in gens]
log("  REAL  rho(logf,len) = %+.3f   mean len: hapax=%.2f common(>=6)=%.2f" %
    (br['rho_type'], br['hapax_len'], br['common_len']))
log("        binned mean length: " + ", ".join("%s=%.2f(n%d)"%(k,v[0],v[1]) for k,v in br['binmean'].items()))
log("  GEN   rho(logf,len) = %+.3f ± %.3f   hapax=%.2f±%.2f common=%.2f±%.2f" % (
    np.mean([b['rho_type'] for b in bg]), np.std([b['rho_type'] for b in bg]),
    np.mean([b['hapax_len'] for b in bg]), np.std([b['hapax_len'] for b in bg]),
    np.mean([b['common_len'] for b in bg]), np.std([b['common_len'] for b in bg])))
log("        GEN binned hapax mean len = %.2f (real %.2f)  -> residual real-gen = %+.2f glyph-tokens" % (
    np.mean([b['binmean']['hapax(=1)'][0] for b in bg]), br['binmean']['hapax(=1)'][0],
    br['binmean']['hapax(=1)'][0]-np.mean([b['binmean']['hapax(=1)'][0] for b in bg])))
log("  ENG   rho(logf,len) = %+.3f (illustrative)" % brevity(eng)['rho_type'])
log("  LAT   rho(logf,len) = %+.3f (illustrative)" % brevity(lat)['rho_type'])

# ================================================= WORD-LENGTH DISTRIBUTION ====
# pastiche-paper claim: word-length ~ binomial, under-representation of short/long
def wlen_dist(corp):
    wl = corp.wlen.astype(int)
    mx = wl.max()
    hist = np.array([np.mean(wl==k) for k in range(mx+1)])
    mean, var = wl.mean(), wl.var()
    return hist, mean, var
hr, mr, vr = wlen_dist(real)
log("\n=== WORD-LENGTH DISTRIBUTION (pastiche paper: 'resembles syllabic/binomial, under-rep short&long') ===")
log("  REAL word length (glyph-tokens): mean=%.2f var=%.2f  var/mean=%.2f (Poisson=1; <1 => under-dispersed/binomial-like)" %
    (mr, vr, vr/mr))
mg2 = np.mean([g.wlen.mean() for g in gens]); vg2 = np.mean([g.wlen.var() for g in gens])
log("  GEN  word length: mean=%.2f var=%.2f var/mean=%.2f" % (mg2, vg2, vg2/mg2))
log("  ENG  word length (letters): mean=%.2f var=%.2f var/mean=%.2f" % (eng.wlen.mean(), eng.wlen.var(), eng.wlen.var()/eng.wlen.mean()))
log("  LAT  word length (letters): mean=%.2f var=%.2f var/mean=%.2f" % (lat.wlen.mean(), lat.wlen.var(), lat.wlen.var()/lat.wlen.mean()))
log("  REAL hist P(len=k) k=0..8: " + " ".join("%.3f"%x for x in hr[:9]))
log("  GEN  hist P(len=k) k=0..8: " + " ".join("%.3f"%np.mean([ (g.wlen.astype(int)==k).mean() for g in gens]) for k in range(9)))

# ================================= WEAK WORD ORDER + LOW CONDITIONAL ENTROPY ===
def cond_entropy(seq):
    """H(next|current) in bits, plug-in."""
    big = collections.Counter(zip(seq[:-1], seq[1:]))
    uni = collections.Counter(seq[:-1])
    H = 0.0; N = sum(big.values())
    for (a,b),c in big.items():
        pab = c/N; pb_a = c/uni[a]
        H -= pab*math.log2(pb_a)
    return H
def adj_mi_states(seq):
    uni = collections.Counter(seq); N=len(seq)
    H1 = -sum((v/N)*math.log2(v/N) for v in uni.values())
    Hc = cond_entropy(seq)
    return H1, Hc, H1-Hc
states_real = [m.split("=>")[-1] for m in real.words]
H1r,Hcr,MIr = adj_mi_states(states_real)
gm=[]
for g in gens:
    st=[m.split("=>")[-1] for m in g.words]; gm.append(adj_mi_states(st))
log("\n=== WEAK WORD ORDER + LOW CONDITIONAL ENTROPY (should FAVOUR generator) ===")
log("  STATE (ending-class) channel:  H1=%.3f  H(next|cur)=%.3f  adjacent MI=%.3f bits (=%.1f%% of H1)" %
    (H1r,Hcr,MIr,100*MIr/H1r))
log("  GEN  state adjacent MI = %.3f ± %.3f bits (%.1f%% of H1)" % (
    np.mean([x[2] for x in gm]), np.std([x[2] for x in gm]), 100*np.mean([x[2] for x in gm])/np.mean([x[0] for x in gm])))
# molecule-level cond entropy
Hc_mol_real = cond_entropy(real.words)
Hc_mol_gen = np.mean([cond_entropy(g.words) for g in gens])
log("  MOLECULE H(next|cur): REAL=%.3f  GEN=%.3f bits (generator reproduces low per-word conditional entropy)" %
    (Hc_mol_real, Hc_mol_gen))

log("\ntotal t=%.1fs"%(time.time()-t0))
