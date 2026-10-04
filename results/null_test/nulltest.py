#!/usr/bin/env python3
"""
Generator-vs-real NULL TEST on the Voynich "molecule" (shadow) layer.

Question: does the REAL per-line sequence of (state | body | molecule) units
contain structure that a self-generation / Markov process CANNOT reproduce?

READ-ONLY over:
  WORKING/hypotheses/x10u_full_symbolic_factorization_v3/full_symbolic_factorization.tsv

Writes all output under tmp/shadow_analysis/null_test/ only.

Method
------
For each subset in {FULL, STRICT} x unit in {state, body, mol}:
  1. Build the real per-line token sequence (line order = folio, then line
     number, tokens ordered by intra-line position).
  2. Compute a battery of real statistics (see `compute_stats`).
  3. Build three null generators, each producing >=200 synthetic corpora
     with IDENTICAL line-length structure to the real corpus:
       - iid      : each line resampled i.i.d. from the real unigram marginal
       - perm     : each line's own real tokens permuted in place (preserves
                    exact per-line multiset, destroys order)
       - markov1  : first-order Markov chain fit to the real within-line
                    transition matrix + real line-initial distribution
  4. For every statistic, report real value, null mean +/- sd, z-score, and
     a one-sided permutation p-value (fraction of null replicates >= real,
     for statistics where the a-priori structural hypothesis is "real has
     MORE structure than a memoryless/short-memory generator").

All randomness is seeded (SEED=20260930) for reproducibility.
"""
import csv, math, json, time, bisect, collections, os, sys
import numpy as np

import pathlib
RELEASE_ROOT = pathlib.Path(__file__).resolve().parents[2]  # PUBLIC_RELEASE
FULL_TSV = str(RELEASE_ROOT / "data" / "factorization" / "full_surface_factorization.tsv")
OUT = str(pathlib.Path(__file__).resolve().parent)  # results/null_test (frozen outputs live here)
os.makedirs(OUT, exist_ok=True)

SEED = 20260930
REPS = 200          # required minimum replicates per null model
MAXLAG = 10

rng_master = np.random.default_rng(SEED)


# ---------------------------------------------------------------- parsing --
def parse_mol(s):
    if "=>" in s:
        body, state = s.rsplit("=>", 1)
    else:
        body, state = s, ""
    body = body.strip()
    glyphs = [] if body in ("<EMPTY>", "") else body.split()
    return glyphs, state.strip()


def load_rows():
    rows = []
    with open(FULL_TSV, encoding="utf-8") as f:
        for d in csv.DictReader(f, delimiter="\t"):
            g, st = parse_mol(d["symbolic_factor"])
            rid = d["record_id"]
            left, _, pos = rid.partition(":")
            folio, _, line = left.rpartition(".")
            try:
                posi = int(pos)
            except ValueError:
                posi = 0
            rows.append(dict(
                folio=folio or d.get("folio", ""), line=line, pos=posi,
                body=" ".join(g), state=st, mol=d["symbolic_factor"].strip(),
                tier=d["assignment_tier"],
            ))
    return rows


def build_lines(rows, unit):
    """Return list of lines (global folio/line order), each a list of token
    strings ordered by intra-line position. Rows already filtered by tier."""
    data = sorted(rows, key=lambda r: (r["folio"], r["line"], r["pos"]))
    lines = collections.OrderedDict()
    for r in data:
        lines.setdefault((r["folio"], r["line"]), []).append(r)
    out = []
    for k, lst in lines.items():
        lst.sort(key=lambda r: r["pos"])
        out.append([r[unit] for r in lst])
    return out


# ------------------------------------------------------------- statistics --
def entropy_counts(counts):
    tot = counts.sum()
    if tot == 0:
        return 0.0
    p = counts[counts > 0] / tot
    return float(-(p * np.log2(p)).sum())


def joint_stats(a, b):
    """a,b: int arrays of equal length (paired observations).
    Returns (H(a), H(b), H(a,b), MI, H(b|a))."""
    n = len(a)
    if n == 0:
        return (0.0, 0.0, 0.0, 0.0, 0.0)
    # combine via unique on paired tuples using a 2-col view -> structured sort
    combo = np.stack([a, b], axis=1)
    _, joint_counts = np.unique(combo, axis=0, return_counts=True)
    Hab = entropy_counts(joint_counts)
    _, ac = np.unique(a, return_counts=True)
    _, bc = np.unique(b, return_counts=True)
    Ha = entropy_counts(ac)
    Hb = entropy_counts(bc)
    MI = Ha + Hb - Hab
    HbGivenA = Hab - Ha
    return (Ha, Hb, Hab, MI, HbGivenA)


def lag_pairs(lines_ids, d):
    """Within-line pairs (x_i, x_{i+d}) for lag d, pooled over all lines."""
    xs, ys = [], []
    for arr in lines_ids:
        L = len(arr)
        if L > d:
            xs.append(arr[:-d] if d > 0 else arr)
            ys.append(arr[d:])
    if not xs:
        return np.array([], dtype=np.int64), np.array([], dtype=np.int64)
    return np.concatenate(xs), np.concatenate(ys)


def heaps_fit(lines_ids, checkpoints=20):
    """Concatenate lines in given order; sample vocabulary-size growth at
    `checkpoints` points; fit log-log slope (Heaps' exponent)."""
    stream = np.concatenate(lines_ids) if lines_ids else np.array([], dtype=np.int64)
    n = len(stream)
    if n < checkpoints * 2:
        return float("nan")
    idxs = np.unique(np.linspace(max(10, n // checkpoints), n, checkpoints).astype(int))
    xs, ys = [], []
    for i in idxs:
        vt = len(np.unique(stream[:i]))
        if i > 0 and vt > 0:
            xs.append(math.log(i))
            ys.append(math.log(vt))
    if len(xs) < 3:
        return float("nan")
    xs = np.array(xs); ys = np.array(ys)
    mx, my = xs.mean(), ys.mean()
    num = ((xs - mx) * (ys - my)).sum()
    den = ((xs - mx) ** 2).sum()
    return float(num / den) if den else float("nan")


def burstiness(lines_ids):
    """Goh-Barabasi burstiness B=(sigma-mu)/(sigma+mu) of inter-occurrence
    gaps (in token-position units along the concatenated stream), averaged
    over types with >=5 occurrences, weighted by occurrence count."""
    stream = np.concatenate(lines_ids) if lines_ids else np.array([], dtype=np.int64)
    n = len(stream)
    if n == 0:
        return float("nan")
    order = np.argsort(stream, kind="stable")
    sorted_ids = stream[order]
    sorted_pos = order
    # split by id
    uniq, start_idx = np.unique(sorted_ids, return_index=True)
    start_idx = list(start_idx) + [len(sorted_ids)]
    total_w = 0.0
    total_b = 0.0
    for k in range(len(uniq)):
        pos = np.sort(sorted_pos[start_idx[k]:start_idx[k + 1]])
        if len(pos) < 5:
            continue
        gaps = np.diff(pos).astype(float)
        mu = gaps.mean()
        sd = gaps.std()
        if mu + sd == 0:
            continue
        b = (sd - mu) / (sd + mu)
        w = len(pos)
        total_b += b * w
        total_w += w
    return float(total_b / total_w) if total_w else float("nan")


def compute_stats(lines_ids, V):
    """lines_ids: list of int arrays (one per line). V: vocab size."""
    stream = np.concatenate(lines_ids) if lines_ids else np.array([], dtype=np.int64)
    n = len(stream)
    counts = np.bincount(stream, minlength=V) if n else np.zeros(V)
    H1 = entropy_counts(counts)

    x1, y1 = lag_pairs(lines_ids, 1)
    Ha, Hb, Hab, MI1, H2 = joint_stats(x1, y1) if len(x1) else (0, 0, 0, 0, 0)
    repeat_rate = float((x1 == y1).mean()) if len(x1) else float("nan")

    milags = {}
    npairs = {}
    for d in range(1, MAXLAG + 1):
        xd, yd = lag_pairs(lines_ids, d)
        npairs[d] = len(xd)
        if len(xd) >= 10:
            _, _, _, mi, _ = joint_stats(xd, yd)
            milags[d] = mi
        else:
            milags[d] = float("nan")

    # boundary (cross-line) pairs: last token of line k, first token of line k+1
    bx, by = [], []
    for k in range(len(lines_ids) - 1):
        a = lines_ids[k]; b = lines_ids[k + 1]
        if len(a) and len(b):
            bx.append(a[-1]); by.append(b[0])
    bx = np.array(bx, dtype=np.int64); by = np.array(by, dtype=np.int64)
    if len(bx) >= 10:
        _, _, _, MI_boundary, _ = joint_stats(bx, by)
    else:
        MI_boundary = float("nan")

    heaps = heaps_fit(lines_ids)
    burst = burstiness(lines_ids)
    ttr = float(len(np.unique(stream)) / n) if n else float("nan")

    return dict(
        n=n, H1=H1, H2=H2, MI1=MI1, repeat_rate=repeat_rate,
        milags=milags, npairs_lag=npairs, MI_boundary=MI_boundary,
        n_boundary_pairs=len(bx), heaps=heaps, burstiness=burst, ttr=ttr,
    )


# -------------------------------------------------------------- null gens --
def make_iid_generator(lines_ids, V, rng):
    counts = np.bincount(np.concatenate(lines_ids), minlength=V).astype(float)
    p = counts / counts.sum()
    lens = [len(a) for a in lines_ids]
    total = sum(lens)

    def gen():
        stream = rng.choice(V, size=total, p=p)
        out = []
        i = 0
        for L in lens:
            out.append(stream[i:i + L])
            i += L
        return out
    return gen


def make_perm_generator(lines_ids, rng):
    def gen():
        out = []
        for a in lines_ids:
            b = a.copy()
            rng.shuffle(b)
            out.append(b)
        return out
    return gen


def make_markov_generator(lines_ids, V, rng):
    # fit transition counts (within-line adjacent pairs) and initial dist
    trans = [collections.Counter() for _ in range(V)]
    init = collections.Counter()
    marg = np.bincount(np.concatenate(lines_ids), minlength=V).astype(float)
    for a in lines_ids:
        if len(a) == 0:
            continue
        init[a[0]] += 1
        for i in range(len(a) - 1):
            trans[a[i]][a[i + 1]] += 1

    fallback_ids = np.arange(V)
    fallback_cum = np.cumsum(marg / marg.sum())

    trans_ids = [None] * V
    trans_cum = [None] * V
    for v in range(V):
        c = trans[v]
        if c:
            ids = np.array(sorted(c.keys()))
            cnts = np.array([c[i] for i in ids], dtype=float)
            trans_ids[v] = ids
            trans_cum[v] = np.cumsum(cnts / cnts.sum())

    init_ids = np.array(sorted(init.keys())) if init else fallback_ids
    if init:
        icnts = np.array([init[i] for i in init_ids], dtype=float)
        init_cum = np.cumsum(icnts / icnts.sum())
    else:
        init_cum = fallback_cum

    lens = [len(a) for a in lines_ids]

    # convert cumulative arrays to python lists for fast bisect
    fb_ids_l = fallback_ids.tolist(); fb_cum_l = fallback_cum.tolist()
    init_ids_l = init_ids.tolist(); init_cum_l = init_cum.tolist()
    trans_ids_l = [t.tolist() if t is not None else None for t in trans_ids]
    trans_cum_l = [t.tolist() if t is not None else None for t in trans_cum]

    def draw(ids_l, cum_l, u):
        idx = bisect.bisect_left(cum_l, u)
        if idx >= len(ids_l):
            idx = len(ids_l) - 1
        return ids_l[idx]

    def gen():
        total = sum(lens)
        us = rng.random(total).tolist()
        out = []
        ui = 0
        for L in lens:
            if L == 0:
                out.append(np.array([], dtype=np.int64))
                continue
            seq = [0] * L
            first = draw(init_ids_l, init_cum_l, us[ui]); ui += 1
            seq[0] = first
            prev = first
            for i in range(1, L):
                ids_l = trans_ids_l[prev]; cum_l = trans_cum_l[prev]
                if ids_l is None:
                    ids_l, cum_l = fb_ids_l, fb_cum_l
                nxt = draw(ids_l, cum_l, us[ui]); ui += 1
                seq[i] = nxt
                prev = nxt
            out.append(np.array(seq, dtype=np.int64))
        return out
    return gen


# --------------------------------------------------------------- driver ----
def run_arm(name, lines_tokens, reps=REPS, seed_offset=0):
    """lines_tokens: list of lines, each a list of token strings (real)."""
    vocab = sorted(set(t for line in lines_tokens for t in line))
    V = len(vocab)
    idx = {t: i for i, t in enumerate(vocab)}
    lines_ids = [np.array([idx[t] for t in line], dtype=np.int64) for line in lines_tokens]

    t0 = time.time()
    real = compute_stats(lines_ids, V)

    rng = np.random.default_rng(SEED + seed_offset)
    generators = {
        "iid": make_iid_generator(lines_ids, V, rng),
        "perm": make_perm_generator(lines_ids, rng),
        "markov1": make_markov_generator(lines_ids, V, rng),
    }

    null_results = {}
    for gname, gen in generators.items():
        samples = collections.defaultdict(list)
        for r in range(reps):
            rep_lines = gen()
            s = compute_stats(rep_lines, V)
            samples["H1"].append(s["H1"])
            samples["H2"].append(s["H2"])
            samples["MI1"].append(s["MI1"])
            samples["repeat_rate"].append(s["repeat_rate"])
            samples["MI_boundary"].append(s["MI_boundary"])
            samples["heaps"].append(s["heaps"])
            samples["burstiness"].append(s["burstiness"])
            samples["ttr"].append(s["ttr"])
            for d in range(1, MAXLAG + 1):
                samples[f"MI_lag{d}"].append(s["milags"][d])
        null_results[gname] = {k: v for k, v in samples.items()}
    dt = time.time() - t0
    return dict(name=name, V=V, n_lines=len(lines_ids), n_tokens=sum(len(a) for a in lines_ids),
                real=real, null=null_results, seconds=dt)


def summarize_stat(real_val, null_vals, higher_is_structure=True):
    arr = np.array([v for v in null_vals if not (isinstance(v, float) and math.isnan(v))], dtype=float)
    if len(arr) == 0 or (isinstance(real_val, float) and math.isnan(real_val)):
        return dict(real=real_val, null_mean=float("nan"), null_sd=float("nan"),
                    z=float("nan"), p=float("nan"), n_null=len(arr))
    mean = arr.mean(); sd = arr.std(ddof=1) if len(arr) > 1 else 0.0
    z = (real_val - mean) / sd if sd > 0 else float("inf") if real_val != mean else 0.0
    if higher_is_structure:
        p = (1 + (arr >= real_val).sum()) / (len(arr) + 1)
    else:
        p = (1 + (arr <= real_val).sum()) / (len(arr) + 1)
    return dict(real=real_val, null_mean=float(mean), null_sd=float(sd),
                z=float(z) if math.isfinite(z) else z, p=float(p), n_null=len(arr))


def build_report(arm):
    real = arm["real"]
    rep = dict(name=arm["name"], V=arm["V"], n_lines=arm["n_lines"], n_tokens=arm["n_tokens"],
               seconds=arm["seconds"], stats={})
    keys_higher = ["MI1", "repeat_rate", "burstiness"]
    keys_either = ["H1", "H2", "heaps", "ttr", "MI_boundary"]
    for gname, samples in arm["null"].items():
        rep["stats"].setdefault(gname, {})
        for k in keys_higher:
            rep["stats"][gname][k] = summarize_stat(real[k], samples[k], higher_is_structure=True)
        for k in ["H1", "ttr"]:
            rep["stats"][gname][k] = summarize_stat(real[k], samples[k], higher_is_structure=True)
        rep["stats"][gname]["H2"] = summarize_stat(real["H2"], samples["H2"], higher_is_structure=False)
        rep["stats"][gname]["heaps"] = summarize_stat(real["heaps"], samples["heaps"], higher_is_structure=True)
        rep["stats"][gname]["MI_boundary"] = summarize_stat(real["MI_boundary"], samples["MI_boundary"], higher_is_structure=True)
        for d in range(1, MAXLAG + 1):
            rep["stats"][gname][f"MI_lag{d}"] = summarize_stat(real["milags"][d], samples[f"MI_lag{d}"], higher_is_structure=True)
    rep["real_raw"] = real
    return rep


def main():
    rows = load_rows()
    strict_rows = [r for r in rows if r["tier"] == "STRICT_ACCEPTED"]
    units = ["state", "body", "mol"]
    subsets = {"FULL": rows, "STRICT": strict_rows}

    all_reports = {}
    seed_off = 0
    for subname, subrows in subsets.items():
        for unit in units:
            arm_name = f"{subname}_{unit}"
            print(f"=== running {arm_name} ===", flush=True)
            lines_tokens = build_lines(subrows, unit)
            arm = run_arm(arm_name, lines_tokens, reps=REPS, seed_offset=seed_off)
            seed_off += 1
            print(f"    V={arm['V']} n_lines={arm['n_lines']} n_tokens={arm['n_tokens']} "
                  f"time={arm['seconds']:.1f}s", flush=True)
            all_reports[arm_name] = build_report(arm)

    with open(OUT + "/results.json", "w", encoding="utf-8") as f:
        json.dump(all_reports, f, indent=1, default=lambda o: None)
    print("wrote", OUT + "/results.json")
    return all_reports


if __name__ == "__main__":
    main()
