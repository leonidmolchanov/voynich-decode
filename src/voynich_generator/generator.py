#!/usr/bin/env python3
"""
Explicit generative "machine" for Voynichese (shadow / molecule layer), fitted
separately for Currier A (hand 1) and B (hands 2-5).

THE MACHINE (one sufficient minimal realization, NOT the unique historical device):

  For each physical line, in manuscript order (page-level recency buffer, reset
  at page boundary; LAAFU line-initial state bias):
    for each of L token-slots:
      DECIDE  copy-or-fresh  (Bernoulli p_copy)
        COPY : pick lag k from recency buffer (near-weighted to k in {1,2,3};
               else uniform over the drift window) -> take that molecule;
               with prob p_mut apply ONE single-glyph-token edit (sub/ins/del)
               and/or (rare) flip the ending state.
        FRESH: WORD-TEMPLATE AUTOMATON = 1st-order glyph-token Markov over the
               BODY with ^(start)/$(end) [induces prefix-o, onset, e-ladder,
               i-ladder, coda, body-length]; then draw the ENDING STATE from
               P(state | last-body-token) blended with a line-position (LAAFU)
               marginal.  Surface is reconstructed first-glyph + body + last-glyph
               from per-hand P(first|body-first) (qo- rule) and P(last|state).

The body glyph-token Markov transition table IS the emission/"generation" set;
the copy layer supplies the local self-citation; the buffer reset supplies the
page/line structure.  All tables are fit from the real corpus, per hand.
"""
import collections, math, json, sys
import numpy as np
import vgen_lib as L

# ---- default copy-mutate parameters (calibrated in calibrate.py) -------------
DEFAULT_PARAMS = {
    'A': dict(p_copy=0.60, p_mut=0.55, w_near=0.24, window=600),
    'B': dict(p_copy=0.58, p_mut=0.58, w_near=0.20, window=650),
}
NEAR_LAGS = (1, 2, 3)

# Structured single-token edit operators (from real edit-1 adjacent-pair stats):
# insert/substitute glyphs are drawn from the vowel+gallows "operator" set that
# dominates the real ladders, NOT the full glyph marginal -> mutants stay inside
# the attested paradigm and do not inflate the type inventory.
OP_INS_GLYPH = (['o', 'e', 'a', 'k', 't', 'ch', 'd', 'i', 'l'],
                np.array([.26, .22, .10, .10, .08, .09, .07, .05, .03]))
OP_SUB_GLYPH = (['e', 'o', 'a', 'k', 't', 'ch', 'd'],
                np.array([.27, .27, .16, .10, .08, .07, .05]))


# ============================================================ FITTING =========
def _norm_counter(c):
    tot = sum(c.values())
    syms = list(c.keys())
    p = np.array([c[s] for s in syms], float) / tot
    return syms, p


def fit_hand(rows_h):
    """Fit all emission tables for one hand's token rows."""
    # body glyph-token Markov (^ .. $): 1st-order + 2nd-order (with backoff).
    trans = collections.defaultdict(collections.Counter)
    trans2 = collections.defaultdict(collections.Counter)
    body_marg = collections.Counter()
    for r in rows_h:
        g = ["^"] + r['body'] + ["$"]
        for a, b in zip(g[:-1], g[1:]):
            trans[a][b] += 1
        for a, b, c in zip(g[:-2], g[1:-1], g[2:]):
            trans2[(a, b)][c] += 1
        for t in r['body']:
            body_marg[t] += 1
    markov = {a: _norm_counter(c) for a, c in trans.items()}
    # 2nd-order kept only where the context is well-supported (>=5) so novel-combo
    # closure shrinks toward the real concentrated vocabulary; else back off to 1st.
    markov2 = {ctx: _norm_counter(c) for ctx, c in trans2.items() if sum(c.values()) >= 5}

    # state | last-body-token  (+ marginal, + line-position LAAFU marginals)
    st_by_last = collections.defaultdict(collections.Counter)
    st_marg = collections.Counter()
    for r in rows_h:
        last = r['body'][-1] if r['body'] else "<EMPTY>"
        st_by_last[last][r['state']] += 1
        st_marg[r['state']] += 1
    st_by_last = {k: _norm_counter(c) for k, c in st_by_last.items()}
    st_marg_t = _norm_counter(st_marg)

    # surface reconstruction: P(first-glyph | body-first-token), P(last-glyph|state)
    first_by_bf = collections.defaultdict(collections.Counter)
    last_by_state = collections.defaultdict(collections.Counter)
    for r in rows_h:
        g = L.tokenize(r['surface'])
        if not g:
            continue
        bf = r['body'][0] if r['body'] else "<EMPTY>"
        first_by_bf[bf][g[0]] += 1
        last_by_state[r['state']][g[-1]] += 1
    first_by_bf = {k: _norm_counter(c) for k, c in first_by_bf.items()}
    last_by_state = {k: _norm_counter(c) for k, c in last_by_state.items()}

    # body-length distribution (for length-controlled fresh generation)
    blen = collections.Counter(len(r['body']) for r in rows_h)
    blen_syms = sorted(blen)
    blen_p = np.array([blen[k] for k in blen_syms], float); blen_p /= blen_p.sum()

    # Markov transitions with the $ (end) removed + renormalised, for length-
    # controlled interior sampling (we decide length up front, then fill).
    def strip_end(tbl):
        out = {}
        for a, (syms, p) in tbl.items():
            keep = [(s, pr) for s, pr in zip(syms, p) if s != '$']
            if keep:
                ss = [s for s, _ in keep]; pp = np.array([pr for _, pr in keep], float)
                pp /= pp.sum()
                out[a] = (ss, pp)
        return out
    markov_noend = strip_end(markov)
    markov2_noend = strip_end(markov2)

    body_marg_t = _norm_counter(body_marg)
    return dict(markov=markov, markov2=markov2, markov_noend=markov_noend,
                markov2_noend=markov2_noend, st_by_last=st_by_last,
                st_marg=st_marg_t, first_by_bf=first_by_bf,
                last_by_state=last_by_state, body_marg=body_marg_t,
                blen=(blen_syms, blen_p))


# ============================================================ SAMPLING ========
class HandModel:
    def __init__(self, fit, params, rng):
        self.f = fit
        self.p = params
        self.rng = rng
        # LAAFU line-initial state marginal computed lazily by caller via set_laafu
        self.laafu_init = None  # (syms, p) for line-initial state marginal

    def _draw(self, table_entry):
        syms, p = table_entry
        return syms[self.rng.choice(len(syms), p=p)]

    # -- fresh word: returns (body list, state, decisions dict with bits) -------
    def fresh(self, line_pos=None):
        # 1) draw body LENGTH from empirical per-hand distribution
        lsyms, lp = self.f['blen']
        jl = self.rng.choice(len(lsyms), p=lp)
        Ltarget = lsyms[jl]
        bits_body = -math.log2(lp[jl])
        # 2) fill L interior tokens with the ($-removed) glyph-token Markov:
        #    2nd-order where context is well-supported, else back off to 1st.
        mk = self.f['markov_noend']; mk2 = self.f['markov2_noend']
        prev2, prev1 = "^", "^"
        body = []
        for _ in range(Ltarget):
            entry = mk2.get((prev2, prev1)) if body else mk.get(prev1)
            if entry is None:
                entry = mk.get(prev1)
            if entry is None:
                break
            syms, p = entry
            j = self.rng.choice(len(syms), p=p)
            bits_body += -math.log2(p[j])
            prev2, prev1 = prev1, syms[j]
            body.append(syms[j])
        # ending state
        last = body[-1] if body else "<EMPTY>"
        if line_pos == 'initial' and self.laafu_init is not None and self.rng.random() < 0.5:
            syms, p = self.laafu_init
        else:
            syms, p = self.f['st_by_last'].get(last, self.f['st_marg'])
        j = self.rng.choice(len(syms), p=p)
        bits_state = -math.log2(p[j])
        state = syms[j]
        return body, state, dict(bits_body=bits_body, bits_state=bits_state)

    def _op_glyph(self, table):
        syms, p = table
        return syms[self.rng.choice(len(syms), p=p)]

    def mutate(self, body, state):
        """ONE structured single-token edit (del 35% / sub 34% / ins 31%),
        the affected glyph drawn from the vowel+gallows operator set that
        dominates the real ladders (keeps mutants inside the attested stock).
        Rarely (5%) flip the ending state instead."""
        body = list(body)
        if self.rng.random() < 0.05 and body:     # rare state flip
            s2, p2 = self.f['st_marg']
            state = s2[self.rng.choice(len(s2), p=p2)]
            return body, state, 'state'
        u = self.rng.random()
        if not body:
            body = [self._op_glyph(OP_INS_GLYPH)]
            return body, state, 'ins'
        pos = int(self.rng.integers(len(body)))
        if u < 0.35 and len(body) > 1:             # delete
            body.pop(pos)
            return body, state, 'del'
        elif u < 0.69:                             # substitute
            body[pos] = self._op_glyph(OP_SUB_GLYPH)
            return body, state, 'sub'
        else:                                      # insert (bias toward start)
            ipos = 0 if self.rng.random() < 0.55 else pos
            body.insert(ipos, self._op_glyph(OP_INS_GLYPH))
            return body, state, 'ins'

    def reconstruct_surface(self, body, state):
        bf = body[0] if body else "<EMPTY>"
        fe = self.f['first_by_bf'].get(bf, self.f['first_by_bf'].get("<EMPTY>"))
        first = self._draw(fe) if fe else ''
        le = self.f['last_by_state'].get(state)
        last = self._draw(le) if le else 'y'
        if not body:
            # single/short word: surface is just the ending glyph (avoid doubling)
            return last
        return first + "".join(body) + last


# ============================================================ GENERATION ======
def generate(rows, params=None, seed=20260930, laafu=None, fit_rows=None):
    """Generate a synthetic corpus aligned 1:1 to the real token LAYOUT of `rows`
    (same page/line/section/AB per position). Emission tables are fit on
    `fit_rows` (defaults to `rows`); pass a disjoint train set for a held-out
    test. Returns (list of token dicts, per-token free-choice decision log)."""
    if params is None:
        params = DEFAULT_PARAMS
    rng = np.random.default_rng(seed)
    src = fit_rows if fit_rows is not None else rows
    rows_A = [r for r in src if r['ab'] == 'A']
    rows_B = [r for r in src if r['ab'] == 'B']
    models = {}
    for h, rr in (('A', rows_A), ('B', rows_B)):
        m = HandModel(fit_hand(rr), params[h], rng)
        if laafu and h in laafu:
            m.laafu_init = laafu[h]
        models[h] = m

    lines = L.group_lines(rows)
    out = []
    # Two timescales (matches the data): (1) the ENDING/state channel resets each
    # line (LAAFU line-initial prior below); (2) the copy/vocabulary memory is a
    # long ROLLING buffer (drift window) that carries across lines & pages -> this
    # is what produces section-scale Montemurro clustering without long-range
    # fixed-lag token MI (copies concentrate at near lags).
    buf = []             # rolling recency buffer of generated molecules (body,state)
    log = []             # per-token free-choice record
    for ln in lines:
        page = ln[0]['folio']
        for i, r in enumerate(ln):
            h = r['ab']
            m = models[h]
            n = len(ln)
            line_pos = 'initial' if i == 0 else ('final' if i == n - 1 else 'medial')
            rec = dict(hand=h, line_pos=i, is_copy=0, lag=0, is_mut=0,
                       bits=0.0, mut_op='')
            do_copy = (len(buf) >= 1) and (rng.random() < m.p['p_copy'])
            if do_copy:
                # choose lag
                if rng.random() < m.p['w_near']:
                    cand = [k for k in NEAR_LAGS if k <= len(buf)]
                    k = cand[rng.integers(len(cand))]
                else:
                    k = 1 + int(rng.integers(min(len(buf), m.p['window'])))
                body, state = buf[-k]
                body = list(body)
                rec['is_copy'] = 1; rec['lag'] = k
                # bits: copy decision + lag choice
                rec['bits'] += -math.log2(m.p['p_copy'])
                rec['bits'] += math.log2(min(len(buf), m.p['window']))  # ~lag entropy
                if rng.random() < m.p['p_mut']:
                    body, state, opn = m.mutate(body, state)
                    rec['is_mut'] = 1; rec['mut_op'] = opn
                    rec['bits'] += -math.log2(m.p['p_mut'])
                    rec['bits'] += math.log2(29)  # ~ which edit
                else:
                    rec['bits'] += -math.log2(1 - m.p['p_mut'])
            else:
                body, state, d = m.fresh(line_pos)
                if len(buf) >= 1:
                    rec['bits'] += -math.log2(1 - m.p['p_copy'])
                rec['bits'] += d['bits_body'] + d['bits_state']
            buf.append((tuple(body), state))
            surf = m.reconstruct_surface(body, state)
            mol = (" ".join(body) if body else "<EMPTY>") + "=>" + state
            out.append(dict(surface=surf, mol=mol, body=body, state=state,
                            section=r['section'], ab=h, folio=page, line=r['line']))
            log.append(rec)
    return out, log


# ============================================================ SPEC EMIT ========
def build_laafu(rows):
    laafu = {}
    lines = L.group_lines(rows)
    for h in ('A', 'B'):
        c = collections.Counter()
        for ln in lines:
            toks = [r for r in ln if r['ab'] == h]
            if toks:
                c[toks[0]['state']] += 1
        laafu[h] = _norm_counter(c)
    return laafu


def _table_to_json(t, topn=None):
    syms, p = t
    items = sorted(zip(syms, p.tolist()), key=lambda x: -x[1])
    if topn:
        items = items[:topn]
    return {s: round(pr, 5) for s, pr in items}


def emit_spec(rows, params, path):
    rows_A = [r for r in rows if r['ab'] == 'A']
    rows_B = [r for r in rows if r['ab'] == 'B']
    spec = dict(description="Sufficient minimal generator for Voynichese "
                "(shadow/molecule layer). Fit per Currier hand. NOT a claim of "
                "the unique historical device.",
                params=params, hands={})
    for h, rr in (('A', rows_A), ('B', rows_B)):
        f = fit_hand(rr)
        # slot-view emission tables (human-readable "generation set")
        elad = collections.Counter(); ilad = collections.Counter()
        prefix = collections.Counter(); onset = collections.Counter()
        coda = collections.Counter()
        for r in rr:
            d = L.slot_decompose(r['body'])
            elad[min(d['elad'], 4)] += 1
            ilad[min(d['ilad'], 4)] += 1
            prefix[d['prefix'] or '<none>'] += 1
            onset[d['onset'] or '<none>'] += 1
            coda[d['coda'] or '<none>'] += 1
        tot = len(rr)
        spec['hands'][h] = dict(
            n_tokens=tot,
            state_marginal=_table_to_json(f['st_marg']),
            body_glyph_marginal=_table_to_json(f['body_marg'], 20),
            markov_start=_table_to_json(f['markov']['^'], 12),   # prefix/onset rule
            markov_from_e=_table_to_json(f['markov'].get('e', (['$'], np.array([1.0]))), 8),
            markov_from_o=_table_to_json(f['markov'].get('o', (['$'], np.array([1.0]))), 8),
            markov_to_end_examples={g: round(dict(zip(*f['markov'][g])).get('$', 0), 4)
                                    for g in ['e', 'd', 'l', 'r', 'n', 'y', 'k'] if g in f['markov']},
            state_given_last_examples={g: _table_to_json(f['st_by_last'][g], 4)
                                       for g in ['d', 'e', 'l', 'r', 'o', 'k']
                                       if g in f['st_by_last']},
            elad_dist={str(k): round(elad[k] / tot, 4) for k in sorted(elad)},
            ilad_dist={str(k): round(ilad[k] / tot, 4) for k in sorted(ilad)},
            prefix_dist={k: round(v / tot, 4) for k, v in prefix.most_common(6)},
            coda_dist={k: round(v / tot, 4) for k, v in coda.most_common(8)},
            first_glyph_given_o=_table_to_json(f['first_by_bf'].get('o', (['?'], np.array([1.0]))), 6),
        )
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(spec, fh, ensure_ascii=False, indent=1)
    return spec


if __name__ == "__main__":
    rows = L.load()
    laafu = build_laafu(rows)
    spec = emit_spec(rows, DEFAULT_PARAMS, "spec.json")
    syn, log = generate(rows, laafu=laafu)
    print("generated", len(syn), "tokens; spec.json written")
    # quick sanity
    from collections import Counter
    print("syn state top:", Counter(s['state'] for s in syn).most_common(5))
    print("syn copy frac:", sum(r['is_copy'] for r in log) / len(log))
    print("syn mean bits/word:", sum(r['bits'] for r in log) / len(log))
