#!/usr/bin/env python3
"""Two decisive extra controls, identical pipeline:

FLOOR_perfolio  : within-folio permutation of the REAL corpus. Preserves each
                  physical page's exact molecule multiset (its "theme"), destroys
                  all order. The self-gen floor that reproduces the manuscript's
                  page-level non-stationarity WITHOUT any message.

CEILING_word    : a genuine natural-language message (real English prose, word
                  stream, in order) mapped 1:1 to Voynich molecules by frequency
                  rank (a nomenclator/verbose substitution) and laid out onto the
                  real page/line structure IN ORDER, so topical/long-range/page
                  structure is fully preserved. The "message is really there"
                  positive control (the ceiling).

Compares REAL to both on held-out bits/token, non-stationarity KL, long-range
molecule MI, and per-page surprisal quantum.
"""
import json, os, collections, re, glob
import numpy as np
import pipeline as P
import floor_ceiling as FC

ROOT, OUT, SEED, BOS = P.ROOT, P.OUT, P.SEED, P.BOS


def gen_perfolio_perm(rows, rng):
    """Permute each folio's tokens across its own positions; keep line lengths."""
    byf = collections.OrderedDict()
    for r in rows:
        byf.setdefault(r["folio"], []).append(r)
    corpus = P.rows_to_corpus(rows)
    # build per-folio pools and line templates
    pools = {f: [dict(glyphs=r["glyphs"], mol=r["mol"]) for r in lst]
             for f, lst in byf.items()}
    for f in pools:
        rng.shuffle(pools[f])
    ptr = {f: 0 for f in pools}
    out = []
    for ln in corpus:
        f = ln["folio"]; n = len(ln["words"])
        words = pools[f][ptr[f]:ptr[f] + n]; ptr[f] += n
        out.append(dict(folio=f, words=words))
    return out


def english_word_stream(n_needed):
    """English word stream from the shipped public-domain control corpus
    (analysis/controls/english_jqadams.txt) — the natural-language message ceiling."""
    try:
        txt = open(P.ENGLISH_CONTROL, encoding="utf-8").read()
    except Exception:
        txt = ""
    words = [w.lower() for w in re.findall(r"[A-Za-z]{2,}", txt)]
    if not words:
        raise SystemExit("English control corpus missing/empty: " + P.ENGLISH_CONTROL)
    return words[:n_needed]


def gen_ceiling_word(gen, rows, rng, expansion=1):
    """Map English words -> molecules by frequency-rank; lay onto real structure
    in order. expansion=1 -> 1 molecule/word (max signal)."""
    struct = FC.line_structure(rows)
    N = sum(nw for _, nw in struct)
    n_words_needed = (N + expansion - 1) // expansion
    ptext = english_word_stream(n_words_needed + 5)
    # codebook: english type rank -> molecule rank
    etypes = [w for w, _ in collections.Counter(ptext).most_common()]
    mols = [m for m, _ in gen["uni"].most_common()]
    nm = len(mols)
    code = {w: mols[i % nm] for i, w in enumerate(etypes)}
    # emit stream (with expansion-1 nulls from marginal between signal tokens)
    uni_items = list(gen["uni"].items())
    uni_p = np.array([c for _, c in uni_items], float); uni_p /= uni_p.sum()
    tokens = []
    for w in ptext:
        tokens.append(code[w])
        for _ in range(expansion - 1):
            tokens.append(uni_items[rng.choice(len(uni_items), p=uni_p)][0])
    tokens = tokens[:N]
    lines = []; ti = 0
    for folio, nw in struct:
        ws = []
        for _ in range(nw):
            mol = tokens[ti]; ti += 1
            ws.append(dict(glyphs=FC.sample_spelling(gen, mol, rng), mol=mol))
        lines.append(dict(folio=folio, words=ws))
    return lines, len(ptext)


def summarize_runs(runs):
    def m(key):
        return float(np.mean([r[key] for r in runs]))
    def s(key):
        return float(np.std([r[key] for r in runs], ddof=1)) if len(runs) > 1 else 0.0
    mi = collections.defaultdict(list)
    for r in runs:
        for k, v in r["mi_lag"].items():
            if v is not None:
                mi[k].append(v)
    return dict(
        bt_mean=m("bt"), bt_sd=s("bt"), bg_mean=m("bg"),
        r2_mean=m("r2"), bpw_std_mean=m("bpw_std"),
        ns_mean=m("ns"), ns_sd=s("ns"),
        mi_lag_mean={k: float(np.mean(v)) for k, v in mi.items()},
        nrep=len(runs))


def run_one(corpus):
    res = P.summarize(P.eval_corpus(corpus, FC.BEST))
    best = min(res.values(), key=lambda x: x["bits_token"])
    H1, mi = FC.mol_mi_decay(corpus)
    reg = FC.page_surprisal_regression(corpus)
    ns, _ = FC.nonstationarity(corpus)
    return dict(bt=best["bits_token"], bg=best["bits_glyph"],
                r2=reg["r2"], bpw_std=reg["bpw_std"], ns=ns,
                mi_lag={str(k): v for k, v in mi.items()})


if __name__ == "__main__":
    rows = P.load()
    gen = FC.learn_generators(rows)
    out = {}

    print("== FLOOR_perfolio (within-folio permutation, n=8) ==")
    runs = []
    for rep in range(8):
        rng = np.random.default_rng(SEED + 5000 + rep)
        runs.append(run_one(gen_perfolio_perm(rows, rng)))
    out["FLOOR_perfolio"] = summarize_runs(runs)
    b = out["FLOOR_perfolio"]
    print(f"   bits/tok={b['bt_mean']:.3f}±{b['bt_sd']:.3f}  nsKL={b['ns_mean']:.3f}±{b['ns_sd']:.3f}"
          f"  page_R2={b['r2_mean']:.4f}  bpw_std={b['bpw_std_mean']:.3f}")

    for exp in (1, 2):
        print(f"== CEILING_word expansion={exp} (n=6) ==")
        runs = []; plen = None
        for rep in range(6):
            rng = np.random.default_rng(SEED + 6000 + 100 * exp + rep)
            corp, plen = gen_ceiling_word(gen, rows, rng, expansion=exp)
            runs.append(run_one(corp))
        lab = f"CEILING_word_r{exp}"
        out[lab] = summarize_runs(runs) | {"plaintext_words": plen, "expansion": exp}
        b = out[lab]
        print(f"   plaintext={plen} words  bits/tok={b['bt_mean']:.3f}±{b['bt_sd']:.3f}"
              f"  nsKL={b['ns_mean']:.3f}±{b['ns_sd']:.3f}  page_R2={b['r2_mean']:.4f}"
              f"  bpw_std={b['bpw_std_mean']:.3f}")

    # MI decay comparison table (incl REAL from prior file)
    fc = json.load(open(OUT + "/floor_ceiling.json"))
    real = fc["REAL"]
    out["_REAL_ref"] = dict(bt=real["best_bits_token"], ns=real["nonstationarity_kl"],
                            r2=real["page_reg"]["r2"], bpw_std=real["page_reg"]["bpw_std"],
                            mi_lag=real["mi_lag"])
    print("\nMI decay (bits): lag  REAL  FLOOR_pf  CEIL_w_r1  CEIL_w_r2")
    for lag in range(1, 11):
        k = str(lag)
        def g(d):
            v = d.get(k); return f"{v:.3f}" if isinstance(v, (int, float)) else "  -"
        print(f"  {lag:>2}  {g(real['mi_lag']):>6} {g(out['FLOOR_perfolio']['mi_lag_mean']):>8}"
              f" {g(out['CEILING_word_r1']['mi_lag_mean']):>9} {g(out['CEILING_word_r2']['mi_lag_mean']):>9}")

    json.dump(out, open(OUT + "/control2.json", "w"), indent=2)
    print("\nwrote control2.json")
