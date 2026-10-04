#!/usr/bin/env python3
"""EDA dump: per-hand emission tables + calibration targets for the generator."""
import collections, json, math
import numpy as np
import vgen_lib as L

rows = L.load()
lines = L.group_lines(rows)

def edit1(a, b):
    """True if glyph-token lists a,b are within Levenshtein distance 1."""
    if a == b:
        return False  # exact handled separately
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:  # substitution
        return sum(1 for x, y in zip(a, b) if x != y) == 1
    if la > lb:
        a, b = b, a; la, lb = lb, la
    # la == lb-1 : one insertion into a
    i = j = 0; skips = 0
    while i < la and j < lb:
        if a[i] == b[j]:
            i += 1; j += 1
        else:
            skips += 1; j += 1
            if skips > 1:
                return False
    return True

def hand_stats(hand):
    sub = [r for r in rows if hand == 'ALL' or r['ab'] == hand]
    N = len(sub)
    # state
    st = collections.Counter(r['state'] for r in sub)
    Hstate = L.entropy(st)
    # body length
    blen = collections.Counter(len(r['body']) for r in sub)
    # body glyph unigram
    bg = collections.Counter(g for r in sub for g in r['body'])
    # first surface glyph (prefix) distribution
    firstg = collections.Counter(L.tokenize(r['surface'])[0] for r in sub if r['surface'])
    # qo- rule: among words whose body starts with 'o', how often first glyph == 'q'
    o_start = [r for r in sub if r['body'] and r['body'][0] == 'o']
    q_before_o = sum(1 for r in o_start if L.tokenize(r['surface'])[0] == 'q')
    # e-ladder: count of consecutive e in body nucleus / i-ladder
    def erun(body):
        return sum(1 for g in body if g == 'e')
    def irun(body):
        return sum(1 for g in body if g == 'i')
    elad = collections.Counter(min(erun(r['body']), 4) for r in sub)
    ilad = collections.Counter(min(irun(r['body']), 4) for r in sub)
    # molecule / surface corpus stats
    mol_stats = L.corpus_stats([r['mol'] for r in sub])
    surf_stats = L.corpus_stats([r['surface'] for r in sub])
    # body-conditional state entropy H(state|body)
    bysbody = collections.defaultdict(collections.Counter)
    for r in sub:
        bysbody[tuple(r['body'])][r['state']] += 1
    Hs_body = sum(sum(c.values()) * L.entropy(c) for c in bysbody.values()) / N
    return dict(N=N, states=dict(st.most_common()), Hstate=Hstate,
                Hstate_given_body=Hs_body,
                blen={k: blen[k] for k in sorted(blen)},
                body_glyph=dict(bg.most_common(25)), n_body_glyph=len(bg),
                first_glyph=dict(firstg.most_common(15)),
                qo_rule=dict(o_start=len(o_start), q_before_o=q_before_o,
                             frac=q_before_o / max(1, len(o_start))),
                elad={k: elad[k] for k in sorted(elad)},
                ilad={k: ilad[k] for k in sorted(ilad)},
                mol_stats=mol_stats, surf_stats=surf_stats)

# copy signal: adjacent within-line, exact + edit1 (body & molecule), per hand & all
def copy_signal(hand):
    ex_body = ed_body = ex_mol = pairs = 0
    for ln in lines:
        toks = [r for r in ln if hand == 'ALL' or r['ab'] == hand]
        for i in range(len(toks) - 1):
            pairs += 1
            a, b = toks[i]['body'], toks[i + 1]['body']
            if a == b:
                ex_body += 1
            elif edit1(a, b):
                ed_body += 1
            if toks[i]['mol'] == toks[i + 1]['mol']:
                ex_mol += 1
    return dict(pairs=pairs, exact_body=ex_body / pairs, edit1_body=ed_body / pairs,
                exact_or_edit1_body=(ex_body + ed_body) / pairs,
                exact_mol=ex_mol / pairs)

# line-length distribution (tokens per line) per hand
def line_len_dist(hand):
    lens = []
    for ln in lines:
        toks = [r for r in ln if hand == 'ALL' or r['ab'] == hand]
        if toks:
            lens.append(len(toks))
    arr = np.array(lens)
    return dict(n_lines=len(lens), mean=float(arr.mean()), sd=float(arr.std()),
                dist=dict(collections.Counter(lens).most_common(12)))

# LAAFU line-position state bias (initial / medial / final) ALL & per hand
def laafu(hand):
    pos = {'initial': collections.Counter(), 'medial': collections.Counter(),
           'final': collections.Counter()}
    for ln in lines:
        toks = [r for r in ln if hand == 'ALL' or r['ab'] == hand]
        n = len(toks)
        for i, r in enumerate(toks):
            k = 'initial' if i == 0 else ('final' if i == n - 1 else 'medial')
            pos[k][r['state']] += 1
    out = {}
    for k, c in pos.items():
        tot = sum(c.values())
        out[k] = {s: round(c[s] / tot, 4) for s in sorted(c, key=lambda x: -c[x])[:5]}
    return out

# body-conditional adjacent-state MI (near independence check), ALL
def state_seq_mi():
    seq = []
    for ln in lines:
        seq.extend(r['state'] for r in ln)
    c1 = collections.Counter(seq)
    c2 = collections.Counter()
    for ln in lines:
        s = [r['state'] for r in ln]
        for a, b in zip(s, s[1:]):
            c2[(a, b)] += 1
    N2 = sum(c2.values())
    H1 = L.entropy(c1)
    mi = 0.0
    for (a, b), n in c2.items():
        pab = n / N2
        pa = c1[a] / sum(c1.values()); pb = c1[b] / sum(c1.values())
        mi += pab * math.log2(pab / (pa * pb))
    return dict(H1_state=H1, adjacent_MI=mi, frac=mi / H1)

out = {}
for h in ['ALL', 'A', 'B']:
    out[h] = hand_stats(h)
    out[h]['copy'] = copy_signal(h)
    out[h]['line_len'] = line_len_dist(h)
    out[h]['laafu'] = laafu(h)
out['state_seq'] = state_seq_mi()

print(json.dumps(out, ensure_ascii=False, indent=1))
