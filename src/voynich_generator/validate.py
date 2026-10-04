#!/usr/bin/env python3
"""Validation: real manuscript vs synthetic corpus, matched size, aligned layout.
Reports which real statistics the generator reproduces vs misses (honestly)."""
import collections, math, json, sys, os
import numpy as np
import vgen_lib as L
import generator as G

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "montemurro"))
import mz_common as MZ

rng = np.random.default_rng(20260930)
rows = L.load()
laafu = G.build_laafu(rows)
syn, log = G.generate(rows, laafu=laafu, seed=20260930)

# ---- parallel arrays ----
def arrs(recs, key):
    return [r[key] for r in recs]

real_mol = [r['mol'] for r in rows]
real_surf = [r['surface'] for r in rows]
syn_mol = [r['mol'] for r in syn]
syn_surf = [r['surface'] for r in syn]
section = [r['section'] for r in rows]     # aligned to both

lines = L.group_lines(rows)

def line_groups(recs):
    """group aligned synthetic/real records back into lines by matching real layout"""
    out = []
    idx = 0
    for ln in lines:
        out.append(recs[idx:idx + len(ln)])
        idx += len(ln)
    return out

def edit1(a, b):
    if a == b: return False
    la, lb = len(a), len(b)
    if abs(la - lb) > 1: return False
    if la == lb: return sum(1 for x, y in zip(a, b) if x != y) == 1
    if la > lb: a, b, la, lb = b, a, lb, la
    i = j = skips = 0
    while i < la and j < lb:
        if a[i] == b[j]: i += 1; j += 1
        else:
            skips += 1; j += 1
            if skips > 1: return False
    return True

def copy_sig(mols, bodies):
    lg_m = line_groups(mols); lg_b = line_groups(bodies)
    ex_m = ex_b = ed_b = pairs = 0
    for lm, lb in zip(lg_m, lg_b):
        for i in range(len(lm) - 1):
            pairs += 1
            if lm[i] == lm[i + 1]: ex_m += 1
            if lb[i] == lb[i + 1]: ex_b += 1
            elif edit1(lb[i], lb[i + 1]): ed_b += 1
    return dict(exact_mol=ex_m / pairs, exact_body=ex_b / pairs, edit1_body=ed_b / pairs)

def state_dist(mols):
    c = collections.Counter(m.rsplit("=>", 1)[1] for m in mols)
    tot = sum(c.values())
    return {s: c[s] / tot for s in c}, L.entropy(c)

def blen_dist(bodies):
    c = collections.Counter(len(b) for b in bodies)
    tot = sum(c.values())
    return {k: c[k] / tot for k in sorted(c)}

def glyph_freq(bodies):
    c = collections.Counter(g for b in bodies for g in b)
    tot = sum(c.values())
    return {g: c[g] / tot for g in c}

def js_div(p, q):
    keys = set(p) | set(q)
    p = np.array([p.get(k, 0) for k in keys]); q = np.array([q.get(k, 0) for k in keys])
    m = 0.5 * (p + q)
    def kl(a, b):
        mask = a > 0
        return float((a[mask] * np.log2(a[mask] / b[mask])).sum())
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)

# ---- MI by lag (whole stream) with within-corpus shuffle floor ----
def mi_by_lag(tokens, lags, n_shuf=20):
    codes, V = MZ._codes(tokens)
    N = len(codes)
    def mi(a, b):
        joint = collections.Counter(zip(a.tolist(), b.tolist()))
        na = collections.Counter(a.tolist()); nb = collections.Counter(b.tolist())
        M = len(a); m = 0.0
        for (x, y), n in joint.items():
            pxy = n / M
            m += pxy * math.log2(pxy / ((na[x] / M) * (nb[y] / M)))
        return m
    out = {}
    for lag in lags:
        a = codes[:-lag]; b = codes[lag:]
        obs = mi(a, b)
        floors = []
        for _ in range(n_shuf):
            perm = codes.copy(); rng.shuffle(perm)
            floors.append(mi(perm[:-lag], perm[lag:]))
        fm = float(np.mean(floors))
        out[lag] = dict(mi=obs, floor=fm, excess=obs - fm)
    return out

bodies_real = [r['body'] for r in rows]
bodies_syn = [r['body'] for r in syn]

report = {}
# corpus stats
report['mol_stats'] = dict(real=L.corpus_stats(real_mol), syn=L.corpus_stats(syn_mol))
report['surf_stats'] = dict(real=L.corpus_stats(real_surf), syn=L.corpus_stats(syn_surf))
# state
sr, hr = state_dist(real_mol); ss, hs = state_dist(syn_mol)
report['state'] = dict(real_S8=sr.get('S8'), syn_S8=ss.get('S8'),
                       real_H=hr, syn_H=hs, real=sr, syn=ss)
# body length
report['blen'] = dict(real=blen_dist(bodies_real), syn=blen_dist(bodies_syn))
# glyph freq JS
report['glyph_JS'] = js_div(glyph_freq(bodies_real), glyph_freq(bodies_syn))
# copy
report['copy_real'] = copy_sig(real_mol, bodies_real)
report['copy_syn'] = copy_sig(syn_mol, bodies_syn)
# MI by lag (molecule)
lags = [1, 2, 3, 4, 5, 6, 8, 10]
report['mi_lag_real'] = mi_by_lag(real_mol, lags)
report['mi_lag_syn'] = mi_by_lag(syn_mol, lags)

# ---- Montemurro section(6) and blocks(20), molecule + surface ----
def montemurro(tokens, section_labels):
    wids, V = MZ._codes(tokens)
    res = {}
    parts, P, _ = MZ.label_parts(section_labels)
    res['sections6'] = MZ.excess_mi(wids, parts, V, P, rng, n_shuffle=100)
    partsB = MZ.make_parts_blocks(len(tokens), 20)
    res['blocks20'] = MZ.excess_mi(wids, partsB, V, 20, rng, n_shuffle=100)
    ab = [r['ab'] for r in rows]
    partsAB, Pab, _ = MZ.label_parts(ab)
    res['currierAB'] = MZ.excess_mi(wids, partsAB, V, Pab, rng, n_shuffle=100)
    return res

report['mz_mol_real'] = montemurro(real_mol, section)
report['mz_mol_syn'] = montemurro(syn_mol, section)
report['mz_surf_real'] = montemurro(real_surf, section)
report['mz_surf_syn'] = montemurro(syn_surf, section)

with open("validation_results.json", "w", encoding="utf-8") as fh:
    json.dump(report, fh, ensure_ascii=False, indent=1, default=float)

# ---- pretty print ----
def fmt(d, keys):
    return "  ".join("%s=%.4f" % (k, d[k]) if isinstance(d[k], float) else "%s=%s" % (k, d[k]) for k in keys)

print("==== MOLECULE corpus stats ====")
print("real:", fmt(report['mol_stats']['real'], ['N','V','TTR','hapax_rate','repeat_rate','H1','zipf_slope']))
print("syn :", fmt(report['mol_stats']['syn'], ['N','V','TTR','hapax_rate','repeat_rate','H1','zipf_slope']))
print("==== SURFACE corpus stats ====")
print("real:", fmt(report['surf_stats']['real'], ['N','V','TTR','hapax_rate','repeat_rate','H1','zipf_slope']))
print("syn :", fmt(report['surf_stats']['syn'], ['N','V','TTR','hapax_rate','repeat_rate','H1','zipf_slope']))
print("==== STATE ====")
print("real S8=%.4f H=%.3f | syn S8=%.4f H=%.3f" % (report['state']['real_S8'], report['state']['real_H'], report['state']['syn_S8'], report['state']['syn_H']))
print("==== BODY LENGTH (frac) ====")
for k in sorted(set(report['blen']['real']) | set(report['blen']['syn'])):
    print("  len %s: real %.4f  syn %.4f" % (k, report['blen']['real'].get(k,0), report['blen']['syn'].get(k,0)))
print("glyph-freq JS divergence (bits):", round(report['glyph_JS'], 4))
print("==== LOCAL COPY (within-line adjacent) ====")
print("real:", {k: round(v,4) for k,v in report['copy_real'].items()})
print("syn :", {k: round(v,4) for k,v in report['copy_syn'].items()})
print("==== MI by lag (molecule; excess over shuffle floor, bits) ====")
print(" lag | real_mi real_exc | syn_mi syn_exc")
for lag in lags:
    r = report['mi_lag_real'][lag]; s = report['mi_lag_syn'][lag]
    print("  %2d | %.3f  %.3f  | %.3f  %.3f" % (lag, r['mi'], r['excess'], s['mi'], s['excess']))
print("==== MONTEMURRO excess (bits) ====")
for lay in ['mol','surf']:
    for cut in ['sections6','blocks20','currierAB']:
        rr = report['mz_%s_real'%lay][cut]['excess']; sc = report['mz_%s_syn'%lay][cut]['excess']
        print("  %-5s %-10s real=%.3f  syn=%.3f  (syn/real=%.2f)" % (lay, cut, rr, sc, sc/rr if rr else 0))
