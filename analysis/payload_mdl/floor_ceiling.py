#!/usr/bin/env python3
"""Self-gen FLOOR and cipher CEILING corpora, evaluated by the identical
pipeline (pipeline.eval_corpus) as the real manuscript. Also structural
discriminators (long-range MI, per-page/line surprisal quantum, non-stationarity)
computed identically on real vs floor vs ceiling.

READ-ONLY over data. Writes only under payload_mdl/.
"""
import csv, math, json, os, collections, random, re, glob
import numpy as np
import pipeline as P

ROOT = P.ROOT
OUT = P.OUT
SEED = P.SEED
BOS = P.BOS


# ------------------------------------------------ learn generators ---------
def learn_generators(rows):
    # last-glyph -> state (deterministic table from real data)
    lg2state = collections.defaultdict(collections.Counter)
    for r in rows:
        if r["glyphs"]:
            lg2state[r["glyphs"][-1]][r["state"]] += 1
    lg2state = {g: c.most_common(1)[0][0] for g, c in lg2state.items()}
    # molecule -> spelling (glyph-tuple) empirical distribution
    mol_spell = collections.defaultdict(collections.Counter)
    for r in rows:
        mol_spell[r["mol"]][r["glyphs"]] += 1
    mol_spell = {m: (list(c.keys()), np.array(list(c.values()), float))
                 for m, c in mol_spell.items()}
    # molecule unigram + within-line bigram (+ line-initial)
    uni = collections.Counter()
    bi = collections.defaultdict(collections.Counter)
    init = collections.Counter()
    corpus = P.rows_to_corpus(rows)
    for ln in corpus:
        prev = BOS
        for i, w in enumerate(ln["words"]):
            uni[w["mol"]] += 1
            if i == 0:
                init[w["mol"]] += 1
            bi[prev][w["mol"]] += 1
            prev = w["mol"]
    return dict(lg2state=lg2state, mol_spell=mol_spell,
                uni=uni, bi=bi, init=init)


def sample_spelling(gen, mol, rng):
    keys, w = gen["mol_spell"][mol]
    return keys[rng.choice(len(keys), p=w / w.sum())]


def line_structure(rows):
    """Return list of (folio, n_words) mirroring the real corpus lines."""
    corpus = P.rows_to_corpus(rows)
    return [(ln["folio"], len(ln["words"])) for ln in corpus]


# ---- Floor-B: self-citation (molecule Markov-1 + real spellings) ----------
def gen_floor_selfcite(gen, struct, rng):
    init_items = list(gen["init"].items())
    init_p = np.array([c for _, c in init_items], float); init_p /= init_p.sum()
    lines = []
    for folio, nw in struct:
        words = []
        prev = BOS
        for i in range(nw):
            if i == 0 or prev not in gen["bi"]:
                mol = init_items[rng.choice(len(init_items), p=init_p)][0]
            else:
                cnt = gen["bi"][prev]
                items = list(cnt.items())
                p = np.array([c for _, c in items], float); p /= p.sum()
                mol = items[rng.choice(len(items), p=p)][0]
            gl = sample_spelling(gen, mol, rng)
            words.append(dict(glyphs=gl, mol=mol))
            prev = mol
        lines.append(dict(folio=folio, words=words))
    return lines


# ---- Floor-A: minimal machine (molecule unigram i.i.d. + real spellings) --
def gen_floor_iid(gen, struct, rng):
    items = list(gen["uni"].items())
    p = np.array([c for _, c in items], float); p /= p.sum()
    lines = []
    for folio, nw in struct:
        idx = rng.choice(len(items), size=nw, p=p)
        words = []
        for j in idx:
            mol = items[j][0]
            words.append(dict(glyphs=sample_spelling(gen, mol, rng), mol=mol))
        lines.append(dict(folio=folio, words=words))
    return lines


# ------------------------------------------------ cipher ceiling -----------
def load_plaintext(n_symbols):
    """Real English letter+space stream from the shipped public-domain control
    corpus (analysis/controls/english_jqadams.txt). This is the "message ceiling":
    genuine natural-language prose run through a verbose cipher onto the layout."""
    try:
        txt = open(P.ENGLISH_CONTROL, encoding="utf-8").read()
    except Exception:
        txt = ""
    ws = re.findall(r"[A-Za-z]{2,}", txt)
    if not ws:
        raise SystemExit("English control corpus missing/empty: " + P.ENGLISH_CONTROL)
    stream = " ".join(w.lower() for w in ws)
    return stream[:n_symbols]  # letters a-z and spaces


def build_codebook(gen, plaintext):
    """Assign each molecule to exactly one plaintext symbol (homophonic), so
    that molecule-mass per symbol ~ symbol frequency in the plaintext."""
    symbols = sorted(set(plaintext))
    freq = collections.Counter(plaintext)
    tot = sum(freq.values())
    target = {s: freq[s] / tot for s in symbols}
    # molecules by descending mass
    mols = gen["uni"].most_common()
    molmass = sum(c for _, c in mols)
    assigned = {s: [] for s in symbols}
    cur = {s: 0.0 for s in symbols}
    # greedy: give each molecule to the symbol most under its target share
    order = symbols[:]
    for mol, c in mols:
        share = c / molmass
        # pick symbol with largest remaining deficit relative to target
        s = max(symbols, key=lambda s: target[s] - cur[s])
        assigned[s].append((mol, c))
        cur[s] += share
    # within-class sampling distributions
    classdist = {}
    for s in symbols:
        if not assigned[s]:
            # ensure every symbol has at least one molecule (steal the rarest)
            donor = max(symbols, key=lambda x: len(assigned[x]))
            assigned[s].append(assigned[donor].pop())
        ms = [m for m, _ in assigned[s]]
        w = np.array([c for _, c in assigned[s]], float)
        classdist[s] = (ms, w / w.sum())
    return classdist


def gen_cipher(gen, struct, plaintext, r, rng):
    """Verbose homophonic cipher at expansion r (r Voynich tokens per plaintext
    symbol: 1 signal + (r-1) nulls sampled from the molecule marginal)."""
    classdist = build_codebook(gen, plaintext)
    uni_items = list(gen["uni"].items())
    uni_p = np.array([c for _, c in uni_items], float); uni_p /= uni_p.sum()
    N = sum(nw for _, nw in struct)
    tokens = []
    pi = 0  # plaintext index
    while len(tokens) < N:
        s = plaintext[pi % len(plaintext)]
        pi += 1
        ms, w = classdist[s]
        mol = ms[rng.choice(len(ms), p=w)]
        tokens.append(mol)
        for _ in range(r - 1):
            if len(tokens) >= N + (r - 1):
                break
            mol_n = uni_items[rng.choice(len(uni_items), p=uni_p)][0]
            tokens.append(mol_n)
    tokens = tokens[:N]
    # glyphs for each molecule
    lines = []
    ti = 0
    for folio, nw in struct:
        words = []
        for _ in range(nw):
            mol = tokens[ti]; ti += 1
            words.append(dict(glyphs=sample_spelling(gen, mol, rng), mol=mol))
        lines.append(dict(folio=folio, words=words))
    return lines, len(plaintext)


# ------------------------------------------------ discriminators -----------
def mol_mi_decay(corpus_lines, maxlag=10):
    """Adjacent mutual information at lags 1..maxlag over the molecule stream,
    computed WITHIN lines only (no cross-line pairs)."""
    seqs = [[w["mol"] for w in ln["words"]] for ln in corpus_lines]
    def H(counter):
        t = sum(counter.values()); h = 0.0
        for c in counter.values():
            if c:
                p = c / t; h -= p * math.log2(p)
        return h
    out = {}
    uni = collections.Counter(m for s in seqs for m in s)
    H1 = H(uni)
    for lag in range(1, maxlag + 1):
        pairs = collections.Counter()
        xm = collections.Counter(); ym = collections.Counter()
        for s in seqs:
            for i in range(len(s) - lag):
                a, b = s[i], s[i + lag]
                pairs[(a, b)] += 1; xm[a] += 1; ym[b] += 1
        n = sum(pairs.values())
        if n < 50:
            out[lag] = None; continue
        mi = 0.0
        for (a, b), c in pairs.items():
            pab = c / n; pa = xm[a] / n; pb = ym[b] / n
            mi += pab * math.log2(pab / (pa * pb))
        out[lag] = mi
    return H1, out


def page_surprisal_regression(corpus_lines, model_order=3):
    """Fit best model (mol_uni w/ spell3) on ALL data, then per-page total
    surprisal. Regress on n_words (and n_glyphs). Report R^2 and residual std.
    A pure length-driven process -> R^2~1; a per-page message quantum ->
    residual structure / intercept."""
    m = P.MolUnigram(P.GlyphNGram(model_order)).fit(corpus_lines)
    pages = collections.OrderedDict()
    for ln in corpus_lines:
        pages.setdefault(ln["folio"], []).append(ln)
    S = []; NW = []; NG = []
    for folio, lns in pages.items():
        s = 0.0; nw = 0; ng = 0
        for ln in lns:
            for w in ln["words"]:
                b, e = m.word_bits(w)
                s += b; nw += 1; ng += e
        S.append(s); NW.append(nw); NG.append(ng)
    S = np.array(S); NW = np.array(NW, float); NG = np.array(NG, float)
    # regression S ~ a*NW (through origin vs with intercept)
    # with intercept:
    Xd = np.column_stack([np.ones_like(NW), NW])
    beta, *_ = np.linalg.lstsq(Xd, S, rcond=None)
    pred = Xd @ beta
    ss_res = ((S - pred) ** 2).sum()
    ss_tot = ((S - S.mean()) ** 2).sum()
    r2 = 1 - ss_res / ss_tot
    resid = S - pred
    # per-page bits/word variability beyond length: std of (S/NW)
    bpw = S / NW
    return dict(n_pages=len(S), slope=float(beta[1]), intercept=float(beta[0]),
                r2=float(r2), resid_std=float(resid.std(ddof=1)),
                resid_std_per_word=float((resid / NW).std(ddof=1)),
                bpw_mean=float(bpw.mean()), bpw_std=float(bpw.std(ddof=1)))


def nonstationarity(corpus_lines):
    """Mean KL(page molecule dist || pooled dist) — topic drift proxy.
    A carried message about different topics -> pages differ from pooled more
    than a stationary generator would produce."""
    pooled = collections.Counter()
    pages = collections.OrderedDict()
    for ln in corpus_lines:
        for w in ln["words"]:
            pooled[w["mol"]] += 1
            pages.setdefault(ln["folio"], collections.Counter())[w["mol"]] += 1
    tot = sum(pooled.values())
    kls = []
    for folio, c in pages.items():
        n = sum(c.values())
        if n < 30:
            continue
        kl = 0.0
        for m, k in c.items():
            p = k / n
            q = pooled[m] / tot
            kl += p * math.log2(p / q)
        kls.append(kl)
    return float(np.mean(kls)), len(kls)


# ------------------------------------------------ driver -------------------
BEST = {"glyph2": ("glyph", 2), "mol_uni": ("mol1", 3), "mol_bi": ("mol2", 3)}


def eval_and_report(name, corpus_lines):
    res = P.summarize(P.eval_corpus(corpus_lines, BEST))
    best = min(res.values(), key=lambda s: s["bits_token"])
    H1, mi = mol_mi_decay(corpus_lines)
    reg = page_surprisal_regression(corpus_lines)
    ns, npg = nonstationarity(corpus_lines)
    return dict(ladder=res,
                best_bits_token=best["bits_token"], best_bits_glyph=best["bits_glyph"],
                best_bt_ci=best["bt_ci"],
                mol_H1=H1, mi_lag={str(k): v for k, v in mi.items()},
                page_reg=reg, nonstationarity_kl=ns, n_pages_ns=npg)


if __name__ == "__main__":
    rows = P.load()
    gen = learn_generators(rows)
    struct = line_structure(rows)
    real_corpus = P.rows_to_corpus(rows)
    report = {}

    print("== REAL ==")
    report["REAL"] = eval_and_report("REAL", real_corpus)
    r = report["REAL"]
    print(f"  best held-out: {r['best_bits_token']:.3f} bits/tok "
          f"({r['best_bits_glyph']:.3f} bits/glyph)  "
          f"page-R2={r['page_reg']['r2']:.4f} nsKL={r['nonstationarity_kl']:.3f}")

    NREP = 8
    for label, genfn in [("FLOOR_selfcite", gen_floor_selfcite),
                         ("FLOOR_iid", gen_floor_iid)]:
        accs = collections.defaultdict(list)
        mi_acc = collections.defaultdict(list)
        for rep in range(NREP):
            rng = np.random.default_rng(SEED + rep)
            corp = genfn(gen, struct, rng)
            rr = eval_and_report(label, corp)
            accs["bt"].append(rr["best_bits_token"])
            accs["bg"].append(rr["best_bits_glyph"])
            accs["r2"].append(rr["page_reg"]["r2"])
            accs["bpw_std"].append(rr["page_reg"]["bpw_std"])
            accs["ns"].append(rr["nonstationarity_kl"])
            for k, v in rr["mi_lag"].items():
                if v is not None:
                    mi_acc[k].append(v)
        report[label] = dict(
            best_bits_token_mean=float(np.mean(accs["bt"])),
            best_bits_token_sd=float(np.std(accs["bt"], ddof=1)),
            best_bits_glyph_mean=float(np.mean(accs["bg"])),
            page_r2_mean=float(np.mean(accs["r2"])),
            page_bpw_std_mean=float(np.mean(accs["bpw_std"])),
            nonstationarity_kl_mean=float(np.mean(accs["ns"])),
            nonstationarity_kl_sd=float(np.std(accs["ns"], ddof=1)),
            mi_lag_mean={k: float(np.mean(v)) for k, v in mi_acc.items()},
            nrep=NREP)
        b = report[label]
        print(f"== {label} (n={NREP}) ==")
        print(f"  best held-out: {b['best_bits_token_mean']:.3f}±{b['best_bits_token_sd']:.3f} "
              f"bits/tok  page-R2={b['page_r2_mean']:.4f} "
              f"nsKL={b['nonstationarity_kl_mean']:.3f}±{b['nonstationarity_kl_sd']:.3f}")

    # cipher ceiling
    N = sum(nw for _, nw in struct)
    for r_exp in (1, 3):
        pt = load_plaintext(N * 2)  # enough symbols
        accs = collections.defaultdict(list)
        mi_acc = collections.defaultdict(list)
        plen = None
        for rep in range(6):
            rng = np.random.default_rng(SEED + 1000 + rep)
            corp, plen = gen_cipher(gen, struct, pt, r_exp, rng)
            rr = eval_and_report(f"CIPHER_r{r_exp}", corp)
            accs["bt"].append(rr["best_bits_token"])
            accs["bg"].append(rr["best_bits_glyph"])
            accs["r2"].append(rr["page_reg"]["r2"])
            accs["bpw_std"].append(rr["page_reg"]["bpw_std"])
            accs["ns"].append(rr["nonstationarity_kl"])
            for k, v in rr["mi_lag"].items():
                if v is not None:
                    mi_acc[k].append(v)
        label = f"CIPHER_r{r_exp}"
        report[label] = dict(
            expansion=r_exp, plaintext_symbols=plen,
            best_bits_token_mean=float(np.mean(accs["bt"])),
            best_bits_token_sd=float(np.std(accs["bt"], ddof=1)),
            best_bits_glyph_mean=float(np.mean(accs["bg"])),
            page_r2_mean=float(np.mean(accs["r2"])),
            page_bpw_std_mean=float(np.mean(accs["bpw_std"])),
            nonstationarity_kl_mean=float(np.mean(accs["ns"])),
            nonstationarity_kl_sd=float(np.std(accs["ns"], ddof=1)),
            mi_lag_mean={k: float(np.mean(v)) for k, v in mi_acc.items()},
            nrep=6)
        b = report[label]
        print(f"== {label} (plaintext={plen} symbols, n=6) ==")
        print(f"  best held-out: {b['best_bits_token_mean']:.3f}±{b['best_bits_token_sd']:.3f} "
              f"bits/tok  page-R2={b['page_r2_mean']:.4f} "
              f"nsKL={b['nonstationarity_kl_mean']:.3f}±{b['nonstationarity_kl_sd']:.3f}")

    json.dump(report, open(OUT + "/floor_ceiling.json", "w"), indent=2)
    print("\nwrote floor_ceiling.json")
