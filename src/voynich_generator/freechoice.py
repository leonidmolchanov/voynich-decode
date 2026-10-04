#!/usr/bin/env python3
"""
TASK 3 -- "what was fed on input".
(A) The operator's per-word FREE-CHOICE ENTROPY budget under the fitted machine,
    decomposed by decision, per hand.
(B) DRIVER tests on the REAL manuscript stream: is any of that choice recoverable
    from previous-state / line-position / a repeating cycle (f57v period-17) /
    local copy, vs effectively random?
"""
import collections, math, json
import numpy as np
import vgen_lib as L
import generator as G

rows = L.load()
lines = L.group_lines(rows)
rng = np.random.default_rng(20260930)

def Hbin(p):
    if p <= 0 or p >= 1: return 0.0
    return -(p*math.log2(p) + (1-p)*math.log2(1-p))

def Hcounter(c):
    return L.entropy(c)

def mi(pairs):
    """MI(X;Y) in bits from list of (x,y)."""
    N = len(pairs)
    cx = collections.Counter(x for x, _ in pairs)
    cy = collections.Counter(y for _, y in pairs)
    cxy = collections.Counter(pairs)
    m = 0.0
    for (x, y), n in cxy.items():
        pxy = n / N
        m += pxy * math.log2(pxy / ((cx[x]/N)*(cy[y]/N)))
    return m

# ============================ (A) FREE-CHOICE BUDGET =========================
# Measure fresh-body path entropy empirically from the generator, per hand.
rows_A = [r for r in rows if r['ab'] == 'A']
rows_B = [r for r in rows if r['ab'] == 'B']
budget = {}
for h, rr in (('A', rows_A), ('B', rows_B)):
    fit = G.fit_hand(rr)
    m = G.HandModel(fit, G.DEFAULT_PARAMS[h], rng)
    # sample many fresh words -> mean bits for body + state
    bb = []; bs = []
    for _ in range(4000):
        body, state, d = m.fresh('medial')
        bb.append(d['bits_body']); bs.append(d['bits_state'])
    L_body = float(np.mean(bb)); L_state = float(np.mean(bs))
    p = G.DEFAULT_PARAMS[h]
    # lag entropy: mixture w_near*U{1,2,3} + (1-w_near)*U{1..window}
    win = p['window']; wn = p['w_near']
    lag_p = np.zeros(win)
    lag_p[:3] += wn / 3
    lag_p += (1 - wn) / win
    lag_p /= lag_p.sum()
    H_lag = float(-(lag_p*np.log2(lag_p)).sum())
    # mutation op entropy: op(del/sub/ins ~1.58) + glyph(~log2 op-set) + pos(~1)
    H_mut_op = Hcounter(collections.Counter({'del':35,'sub':34,'ins':31})) \
               + math.log2(9) * 0.66 + 1.0*0.31   # rough: glyph on sub/ins, pos on ins
    copy_bits = H_lag + Hbin(p['p_mut']) + p['p_mut']*H_mut_op
    fresh_bits = L_body + L_state
    total = Hbin(p['p_copy']) + p['p_copy']*copy_bits + (1-p['p_copy'])*fresh_bits
    budget[h] = dict(p_copy=p['p_copy'], H_decision=round(Hbin(p['p_copy']),3),
                     H_lag=round(H_lag,3), copy_branch_bits=round(copy_bits,3),
                     L_freshbody=round(L_body,3), L_state=round(L_state,3),
                     fresh_branch_bits=round(fresh_bits,3),
                     TOTAL_bits_per_word=round(total,3),
                     free_fraction_from_fresh=round((1-p['p_copy'])*fresh_bits/total,3))

# ============================ (B) DRIVER TESTS (REAL) ========================
drivers = {}

# unconditional info scales
mol_all = [r['mol'] for r in rows]
state_all = [r['state'] for r in rows]
drivers['H1_mol'] = round(L.corpus_stats(mol_all)['H1'], 3)
drivers['H1_state'] = round(Hcounter(collections.Counter(state_all)), 3)

# (1) previous-state -> current-state (category grammar?)
sp = []
for ln in lines:
    s = [r['state'] for r in ln]
    sp += list(zip(s[:-1], s[1:]))
drivers['MI_prevstate_curstate_bits'] = round(mi(sp), 4)
drivers['MI_prevstate_frac_of_H1state'] = round(mi(sp)/drivers['H1_state'], 4)

# previous MOLECULE -> current molecule (local copy shows here)
mp = []
for ln in lines:
    mm = [r['mol'] for r in ln]
    mp += list(zip(mm[:-1], mm[1:]))
drivers['MI_prevmol_curmol_bits'] = round(mi(mp), 3)

# (2) line-position -> state / body-length
def posbucket(i, n):
    return 'init' if i == 0 else ('final' if i == n-1 else 'med')
sp_pos = []; bl_pos = []
for ln in lines:
    n = len(ln)
    for i, r in enumerate(ln):
        sp_pos.append((posbucket(i, n), r['state']))
        bl_pos.append((posbucket(i, n), min(len(r['body']), 5)))
drivers['MI_linepos_state_bits'] = round(mi(sp_pos), 4)
drivers['MI_linepos_blen_bits'] = round(mi(bl_pos), 4)

# (3) LOCAL-COPY determinism: fraction of tokens exactly/edit<=1 present in the
#     previous W tokens (same line, then same page) -> "supplied by copy, not free"
def edit1(a, b):
    if a == b: return True
    la, lb = len(a), len(b)
    if abs(la-lb) > 1: return False
    if la == lb: return sum(1 for x,y in zip(a,b) if x!=y) == 1
    if la > lb: a,b,la,lb = b,a,lb,la
    i=j=sk=0
    while i<la and j<lb:
        if a[i]==b[j]: i+=1;j+=1
        else:
            sk+=1;j+=1
            if sk>1:return False
    return True
for scope, key in (('line', 'line_key'), ('page', 'folio')):
    exact = ed1 = tot = 0
    prev = {}
    buf = collections.deque(maxlen=3)
    cur = None
    for r in rows:
        g = r[key]
        if g != cur:
            buf = collections.deque(maxlen=3); cur = g
        tot += 1
        b = r['body']
        if any(b == pb for pb in buf): exact += 1
        elif any(edit1(b, pb) for pb in buf): ed1 += 1
        buf.append(b)
    drivers['copyable_within3_%s' % scope] = dict(
        exact=round(exact/tot, 4), edit1=round(ed1/tot, 4),
        exact_or_edit1=round((exact+ed1)/tot, 4))

# (4) PERIODICITY / repeating-key test (f57v 17-cycle) on the real stream.
#     For period T, measure how well position-mod-T predicts state (MI), vs a
#     block-shuffle null band; flag any T (esp. 17) that stands out.
state_codes, _ = np.unique(np.array(state_all), return_inverse=True)
sc = np.array([list(np.unique(state_all)).index(s) for s in state_all])
def periodic_mi(codes, T):
    pos = np.arange(len(codes)) % T
    return mi(list(zip(pos.tolist(), codes.tolist())))
periods = list(range(2, 31))
per_mi = {T: periodic_mi(sc, T) for T in periods}
# null: shuffle the whole stream, recompute (destroys any real period)
null_band = []
for _ in range(30):
    perm = sc.copy(); rng.shuffle(perm)
    null_band.append(periodic_mi(perm, 17))
null_mean = float(np.mean(null_band)); null_sd = float(np.std(null_band))
drivers['periodicity'] = dict(
    period_mi_bits={str(T): round(v, 4) for T, v in per_mi.items()},
    period17_mi=round(per_mi[17], 4),
    period17_null_mean=round(null_mean, 4), period17_null_sd=round(null_sd, 5),
    period17_z=round((per_mi[17]-null_mean)/null_sd, 2) if null_sd else None,
    max_period=max(per_mi, key=per_mi.get), max_period_mi=round(max(per_mi.values()), 4))

# ---- (A2) model-free empirical "bits fed in" per word (molecule layer) ------
# Price each REAL token by how cheaply local context could have supplied it:
#   exact repeat of last-3  -> ~log2(3) bits ("which recent word")
#   edit1 of last-3         -> ~log2(3)+log2(#edit ops~16) bits
#   otherwise (fresh)       -> H1 of the fresh subset (memoryless invention)
c = drivers['copyable_within3_line']
f_exact = c['exact']; f_ed1 = c['edit1']; f_fresh = 1 - f_exact - f_ed1
# entropy of the fresh (non-locally-copyable) molecule subset
buf = collections.deque(maxlen=3); cur = None; fresh_mols = []
for r in rows:
    if r['line_key'] != cur:
        buf = collections.deque(maxlen=3); cur = r['line_key']
    b = r['body']
    if not (any(b == pb for pb in buf) or any(edit1(b, pb) for pb in buf)):
        fresh_mols.append(r['mol'])
    buf.append(b)
H_fresh = L.corpus_stats(fresh_mols)['H1'] if fresh_mols else 0.0
cost_exact = math.log2(3)
cost_ed1 = math.log2(3) + math.log2(16)
empirical_bits = f_exact*cost_exact + f_ed1*cost_ed1 + f_fresh*H_fresh
drivers['empirical_bits_fed_per_word'] = dict(
    f_exact=round(f_exact,4), f_edit1=round(f_ed1,4), f_fresh=round(f_fresh,4),
    H_fresh_subset=round(H_fresh,3), H1_memoryless=drivers['H1_mol'],
    bits_fed_per_word=round(empirical_bits,3),
    note="fraction 'fresh' priced at memoryless H1 of the non-locally-copyable "
         "subset; copies priced as local pick + optional single edit")

out = dict(free_choice_budget=budget, drivers=drivers)
with open("freechoice_results.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print("==== (A) OPERATOR FREE-CHOICE BUDGET (bits/word) ====")
for h in ('A', 'B'):
    b = budget[h]
    print(" hand %s: fresh-branch(free invention)=%.2f b [freshbody %.2f + state %.2f], on ~%.0f%% of words;"
          " copy-branch=local reuse (pick+tweak). copy-vs-fresh coin=%.2f b."
          % (h, b['fresh_branch_bits'], b['L_freshbody'], b['L_state'],
             100*(1-b['p_copy']), b['H_decision']))
e = drivers['empirical_bits_fed_per_word']
print(" EMPIRICAL bits fed/word (molecule) = %.2f  (fresh %.0f%% @ H=%.2f ; exact %.0f%% ; edit1 %.0f%%)"
      % (e['bits_fed_per_word'], 100*e['f_fresh'], e['H_fresh_subset'],
         100*e['f_exact'], 100*e['f_edit1']))
print(" vs memoryless H1(mol)=%.2f -> local copy saves ~%.2f b/word" %
      (drivers['H1_mol'], drivers['H1_mol']-e['bits_fed_per_word']))
print("\n==== (B) DRIVER TESTS ON REAL STREAM ====")
print(" H1(mol)=%.2f  H1(state)=%.2f" % (drivers['H1_mol'], drivers['H1_state']))
print(" prev-state -> cur-state MI = %.4f bits (%.2f%% of H1_state)  [category grammar]"
      % (drivers['MI_prevstate_curstate_bits'], 100*drivers['MI_prevstate_frac_of_H1state']))
print(" prev-mol   -> cur-mol   MI = %.3f bits  [local copy shows here]" % drivers['MI_prevmol_curmol_bits'])
print(" line-position -> state MI = %.4f bits ; -> body-length MI = %.4f bits" %
      (drivers['MI_linepos_state_bits'], drivers['MI_linepos_blen_bits']))
print(" locally copyable within last-3 (line):", drivers['copyable_within3_line'])
print(" locally copyable within last-3 (page):", drivers['copyable_within3_page'])
p = drivers['periodicity']
print(" period-17 (f57v) state-MI = %.4f bits ; null %.4f±%.5f ; z=%s" %
      (p['period17_mi'], p['period17_null_mean'], p['period17_null_sd'], p['period17_z']))
print(" strongest period 2..30 = T%s (MI=%.4f bits)" % (p['max_period'], p['max_period_mi']))
