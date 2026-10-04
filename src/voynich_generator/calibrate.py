#!/usr/bin/env python3
"""Fast calibration sweep: score cheap stats (V, hapax, repeat, exact/edit1
adjacency) per-hand generation vs real targets, to pick copy-mutate params.
Section clustering (drift scale = window) is tuned separately (see validate)."""
import collections, itertools, json
import numpy as np
import vgen_lib as L
import generator as G

rows = L.load()
lines = L.group_lines(rows)
laafu = G.build_laafu(rows)

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

# real per-hand targets
def hand_targets(hand):
    sub = [r for r in rows if r['ab'] == hand]
    mols = [r['mol'] for r in sub]
    c = collections.Counter(mols)
    V = len(c); hpx = sum(1 for v in c.values() if v == 1) / V
    return dict(V=V, TTR=V/len(mols), hapax=hpx)

TARG = {h: hand_targets(h) for h in ('A', 'B')}
# adjacency targets (per hand) from EDA
ADJ = {'A': dict(exact_mol=0.0326, edit1_body=0.2019),
       'B': dict(exact_mol=0.0193, edit1_body=0.1430)}

def score_params(params):
    syn, log = G.generate(rows, params=params, laafu=laafu, seed=12345)
    res = {}
    for h in ('A', 'B'):
        sub = [s for s in syn if s['ab'] == h]
        mols = [s['mol'] for s in sub]
        c = collections.Counter(mols)
        V = len(c); hpx = sum(1 for v in c.values() if v == 1) / V
        res[h] = dict(V=V, hapax=hpx)
    # adjacency within line, per hand
    idx = 0; ex = {'A': [0,0], 'B': [0,0]}; ed = {'A': [0,0], 'B': [0,0]}
    for ln in lines:
        seg = syn[idx:idx+len(ln)]; idx += len(ln)
        for i in range(len(seg)-1):
            h = seg[i]['ab']
            if h != seg[i+1]['ab']: continue
            ex[h][1] += 1; ed[h][1] += 1
            if seg[i]['mol'] == seg[i+1]['mol']: ex[h][0] += 1
            if edit1(seg[i]['body'], seg[i+1]['body']): ed[h][0] += 1
    for h in ('A','B'):
        res[h]['exact_mol'] = ex[h][0]/max(1,ex[h][1])
        res[h]['edit1_body'] = ed[h][0]/max(1,ed[h][1])
    return res

# sweep
grid = dict(p_copy=[0.55, 0.65, 0.72], p_mut=[0.45, 0.6, 0.72], w_near=[0.2, 0.35])
best = None
print("p_copy p_mut w_near |  A: V hapax exact ed1  |  B: V hapax exact ed1")
for pc, pm, wn in itertools.product(grid['p_copy'], grid['p_mut'], grid['w_near']):
    params = {'A': dict(p_copy=pc, p_mut=pm, w_near=wn, window=300),
              'B': dict(p_copy=pc, p_mut=pm, w_near=wn, window=350)}
    r = score_params(params)
    # loss: relative V error + hapax err + adjacency err, summed over hands
    loss = 0
    for h in ('A','B'):
        loss += abs(r[h]['V']-TARG[h]['V'])/TARG[h]['V']
        loss += abs(r[h]['hapax']-TARG[h]['hapax'])
        loss += 3*abs(r[h]['exact_mol']-ADJ[h]['exact_mol'])
        loss += 2*abs(r[h]['edit1_body']-ADJ[h]['edit1_body'])
    print("%.2f  %.2f  %.2f  | A:%4d %.3f %.4f %.3f | B:%4d %.3f %.4f %.3f | loss=%.3f" % (
        pc, pm, wn, r['A']['V'], r['A']['hapax'], r['A']['exact_mol'], r['A']['edit1_body'],
        r['B']['V'], r['B']['hapax'], r['B']['exact_mol'], r['B']['edit1_body'], loss))
    if best is None or loss < best[0]:
        best = (loss, (pc, pm, wn), r)

print("\nBEST:", best[1], "loss=%.3f" % best[0])
print("targets A:", TARG['A'], ADJ['A'])
print("targets B:", TARG['B'], ADJ['B'])
