#!/usr/bin/env python3
"""
Rigorous test: is the S-state (word-final-glyph class) channel a memoryless
side-channel, or does it carry cross-word sequential structure beyond its own
marginal frequency and beyond line-position bias?

READ-ONLY on the shipped release data:
  ../../data/factorization/full_surface_factorization.tsv   (23,859 cells)
  (the folio-level hand/section consensus is an internal input, not shipped; its
  absence is handled gracefully — see load_folio_hand_section below.)

Writes beside this script (this folder):
  results.json   -- all numbers (both FULL and STRICT tiers)
  report.txt     -- captured stdout (the human-readable narrative)

Method summary
--------------
- States are encoded as small ints; the 15 rare "U[...]" classes (37/23859
  cells, 0.15%) are pooled into a single "U" bucket to keep the higher-order
  context space tractable. This does not affect the 9 real states (S0..S8),
  which is where all interpretive weight sits.
- "Adjacent" = consecutive entries in a line's word list AS STORED in the
  factorization table (same convention as tmp/shadow_analysis/analyze.py),
  not necessarily consecutive raw word-position numbers (illegible words are
  simply absent from the table).
- Three permutation nulls, all of which exactly preserve the unigram
  histogram of states (so H1 is identical for every null and the real data
  by construction -- only H(next|prev) / conditional entropies can differ):
    Null A "GLOBAL"   -- states shuffled uniformly across the whole corpus.
    Null B "IN-LINE"  -- states shuffled only within each line (preserves
                         line composition & length, destroys within-line
                         order).
    Null C "IN-POS"   -- states shuffled only within the same position
                         category (INIT / MED / FINAL), across the whole
                         corpus (preserves P(state | position-category)
                         exactly, destroys all line/order structure). This
                         is the null that isolates "pure positional artifact"
                         magnitude for question 3.
  All three are exact permutations of the true multiset, done with numpy,
  N_REP replicates each (>=1000).
"""
import csv
import json
import math
import os
import sys
import collections

import numpy as np

from pathlib import Path
RELEASE_ROOT = Path(__file__).resolve().parents[2]       # PUBLIC_RELEASE
FULL_TSV = str(RELEASE_ROOT / "data" / "factorization" / "full_surface_factorization.tsv")
CONS_TSV = ""   # edge-factor consensus TSV is not shipped in the public release
OUT = str(Path(__file__).resolve().parent)               # state_independence/
os.makedirs(OUT, exist_ok=True)

N_REP = 1000
SEED = 20260930
rng = np.random.default_rng(SEED)

LOG2 = math.log(2.0)


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------

def parse_mol(s):
    if "=>" in s:
        body, state = s.rsplit("=>", 1)
    else:
        body, state = s, ""
    body = body.strip()
    glyphs = [] if body in ("<EMPTY>", "") else body.split()
    return " ".join(glyphs), state.strip()


def canon_state(st):
    return "U" if st.startswith("U[") else st


def load_rows():
    rows = []
    with open(FULL_TSV, encoding="utf-8") as f:
        for d in csv.DictReader(f, delimiter="\t"):
            body, st = parse_mol(d["symbolic_factor"])
            rid = d["record_id"]
            left, _, pos = rid.partition(":")
            folio, _, line = left.rpartition(".")
            try:
                posi = int(pos)
            except ValueError:
                posi = 0
            rows.append(dict(
                folio=folio or d.get("folio", ""), line=line, pos=posi,
                body=body, state=canon_state(st), raw_state=st,
                tier=d["assignment_tier"],
            ))
    return rows


def load_folio_hand_section():
    """Folio-level hand/section map built from the edge-consensus file.
    Verified uniform within folio (no folio has >1 distinct hand or section
    value in this file) -- so a plain overwrite-per-row reduction is exact,
    not a majority-vote approximation."""
    fh, fs = {}, {}
    if not CONS_TSV or not os.path.exists(CONS_TSV):
        # edge-consensus file not shipped in the public release; the hand/section
        # (Q5) sub-analysis is skipped — the core state-independence nulls do not need it.
        return fh, fs
    with open(CONS_TSV, encoding="utf-8") as f:
        for d in csv.DictReader(f, delimiter="\t"):
            folio = d["record_id"].split(".")[0]
            fh[folio] = d["hand"]
            fs[folio] = d["section"]
    return fh, fs


# --------------------------------------------------------------------------
# Core sequence structure: build index-adjacency arrays per line
# --------------------------------------------------------------------------

def build_arrays(rows):
    """Sort rows by (folio,line,pos); assign line_id (0..) in order of first
    appearance and seqpos (0..L-1) = index within that line's stored word
    list. Returns dict of aligned numpy arrays plus code<->state maps."""
    rows = sorted(rows, key=lambda r: (r["folio"], r["line"], r["pos"]))
    states_sorted = sorted(set(r["state"] for r in rows))
    code_of = {s: i for i, s in enumerate(states_sorted)}
    K = len(states_sorted)

    line_id = []
    seqpos = []
    cur_key = None
    cur_id = -1
    cur_pos = 0
    for r in rows:
        key = (r["folio"], r["line"])
        if key != cur_key:
            cur_key = key
            cur_id += 1
            cur_pos = 0
        line_id.append(cur_id)
        seqpos.append(cur_pos)
        cur_pos += 1

    n = len(rows)
    states = np.array([code_of[r["state"]] for r in rows], dtype=np.int64)
    line_id = np.array(line_id, dtype=np.int64)
    seqpos = np.array(seqpos, dtype=np.int64)
    bodies = [r["body"] for r in rows]
    body_code = {}
    body_ids = np.empty(n, dtype=np.int64)
    for i, b in enumerate(bodies):
        c = body_code.get(b)
        if c is None:
            c = len(body_code)
            body_code[b] = c
        body_ids[i] = c

    # line length lookup per row (for position category)
    nlines = cur_id + 1
    counts = np.bincount(line_id, minlength=nlines)
    line_len_per_row = counts[line_id]

    pos_cat = np.where(seqpos == 0, 0, np.where(seqpos == line_len_per_row - 1, 2, 1))
    # 0=INIT, 1=MED, 2=FINAL  (a length-1 line is INIT==FINAL; we tag it 0,
    # it has no adjacent pairs anyway so this never affects pair statistics)

    folio_of_line = {}
    cur_key = None
    cur_id = -1
    for r in rows:
        key = (r["folio"], r["line"])
        if key != cur_key:
            cur_key = key
            cur_id += 1
            folio_of_line[cur_id] = r["folio"]

    return dict(
        n=n, K=K, code_of=code_of, states_sorted=states_sorted,
        states=states, line_id=line_id, seqpos=seqpos, pos_cat=pos_cat,
        line_len_per_row=line_len_per_row, nlines=nlines,
        body_ids=body_ids, n_bodies=len(body_code),
        folio_of_line=folio_of_line,
    )


# --------------------------------------------------------------------------
# Entropy machinery (numpy / vectorized)
# --------------------------------------------------------------------------

def entropy_of_counts(counts):
    counts = np.asarray(counts, dtype=np.float64)
    tot = counts.sum()
    if tot <= 0:
        return 0.0
    p = counts[counts > 0] / tot
    return float(-(p * np.log2(p)).sum())


def unigram_entropy(states, K):
    counts = np.bincount(states, minlength=K)
    return entropy_of_counts(counts), counts


def cond_entropy_pairs(prev, cur, K):
    """H(cur|prev) via plug-in estimator, vectorized."""
    idx = prev * K + cur
    joint = np.bincount(idx, minlength=K * K).astype(np.float64)
    tot = joint.sum()
    if tot <= 0:
        return 0.0
    px = joint.reshape(K, K).sum(axis=1)
    nz = joint > 0
    p_joint = joint[nz] / tot
    denom = px[(np.arange(K * K) // K)][nz]
    p_cond = joint[nz] / denom
    return float(-(p_joint * np.log2(p_cond)).sum())


def cond_entropy_context(ctx_codes, cur, n_ctx, K):
    """H(cur | ctx) plug-in, ctx already encoded as ints in [0, n_ctx)."""
    idx = ctx_codes.astype(np.int64) * K + cur
    joint = np.bincount(idx, minlength=n_ctx * K).astype(np.float64)
    tot = joint.sum()
    if tot <= 0:
        return 0.0
    pctx = joint.reshape(n_ctx, K).sum(axis=1)
    nz = joint > 0
    p_joint = joint[nz] / tot
    denom = pctx[(np.arange(n_ctx * K) // K)][nz]
    p_cond = joint[nz] / denom
    return float(-(p_joint * np.log2(p_cond)).sum())


def adjacent_pairs(states, line_id):
    prev = states[:-1]
    cur = states[1:]
    mask = line_id[:-1] == line_id[1:]
    return prev[mask], cur[mask]


# --------------------------------------------------------------------------
# Permutation null generators (each returns a full-length shuffled `states`
# array aligned to the same line_id/seqpos/pos_cat structure)
# --------------------------------------------------------------------------

def shuffle_global(states, rng):
    return rng.permutation(states)


def shuffle_within_line(states, line_id, rng, n):
    """Permute states within each line, preserving line boundaries.
    Since line_id is already sorted ascending (lines appear in original
    order, one contiguous block each), sorting indices by (line_id, random
    tiebreak) regroups each block internally at random while leaving block
    order/sizes untouched -- so the result stays index-aligned with the
    original line_id/seqpos arrays."""
    key = rng.random(n)
    order = np.lexsort((key, line_id))
    return states[order]


def shuffle_within_category(states, cat, rng, n_cats):
    out = states.copy()
    for c in range(n_cats):
        idx = np.where(cat == c)[0]
        if len(idx) > 1:
            out[idx] = rng.permutation(states[idx])
    return out


# --------------------------------------------------------------------------
# Higher-order context builder
# --------------------------------------------------------------------------

def build_context(states, seqpos, k, K):
    """Return (ctx_codes, cur, n_ctx) for order-k contexts fully inside a
    line (seqpos >= k). Index-adjacency, same convention as pairs."""
    n = len(states)
    valid = np.where(seqpos >= k)[0]
    ctx = np.zeros(len(valid), dtype=np.int64)
    for i in range(1, k + 1):
        ctx = ctx * K + states[valid - i]
    cur = states[valid]
    n_ctx = K ** k
    return ctx, cur, n_ctx, valid


# --------------------------------------------------------------------------
# Report assembly
# --------------------------------------------------------------------------

def summarize_null(real_val, null_vals, greater_is_signal=True):
    null_vals = np.asarray(null_vals, dtype=np.float64)
    mean = float(null_vals.mean())
    sd = float(null_vals.std(ddof=1))
    z = float((real_val - mean) / sd) if sd > 0 else float("inf")
    if greater_is_signal:
        p = (1 + np.sum(null_vals >= real_val)) / (len(null_vals) + 1)
    else:
        p = (1 + np.sum(null_vals <= real_val)) / (len(null_vals) + 1)
    return dict(real=real_val, null_mean=mean, null_sd=sd, z=z, p=float(p),
                null_min=float(null_vals.min()), null_max=float(null_vals.max()))


def run_pipeline(rows, label, folio_hand, folio_section):
    R = {}
    A = build_arrays(rows)
    n, K = A["n"], A["K"]
    states, line_id, seqpos, pos_cat = A["states"], A["line_id"], A["seqpos"], A["pos_cat"]

    h1, uni_counts = unigram_entropy(states, K)
    prev, cur = adjacent_pairs(states, line_id)
    h2_real = cond_entropy_pairs(prev, cur, K)
    mi_real = h1 - h2_real
    R["n_tokens"] = n
    R["n_lines"] = A["nlines"]
    R["n_pairs"] = int(len(prev))
    R["K_states"] = K
    R["states_sorted"] = A["states_sorted"]
    R["H1"] = h1
    R["H2_real"] = h2_real
    R["MI_real"] = mi_real
    R["MI_real_pct_H1"] = 100.0 * mi_real / h1 if h1 else float("nan")

    # ---- Q1: significance via 3 permutation nulls -----------------------
    null_A, null_B, null_C = [], [], []
    for _ in range(N_REP):
        sA = shuffle_global(states, rng)
        pA, cA = adjacent_pairs(sA, line_id)
        null_A.append(h1 - cond_entropy_pairs(pA, cA, K))

        sB = shuffle_within_line(states, line_id, rng, n)
        pB, cB = adjacent_pairs(sB, line_id)
        null_B.append(h1 - cond_entropy_pairs(pB, cB, K))

        sC = shuffle_within_category(states, pos_cat, rng, 3)
        pC, cC = adjacent_pairs(sC, line_id)
        null_C.append(h1 - cond_entropy_pairs(pC, cC, K))

    R["Q1_null_global"] = summarize_null(mi_real, null_A)
    R["Q1_null_within_line"] = summarize_null(mi_real, null_B)
    R["Q1_null_within_position"] = summarize_null(mi_real, null_C)

    # ---- Q2: higher-order conditional entropy k=1..4 ---------------------
    R["Q2_orders"] = {}
    for k in range(1, 5):
        ctx, curk, n_ctx, valid = build_context(states, seqpos, k, K)
        h_k_real = cond_entropy_context(ctx, curk, n_ctx, K)
        mi_k_real = h1 - h_k_real
        null_mi_k = []
        for _ in range(N_REP):
            sB = shuffle_within_line(states, line_id, rng, n)
            ctxB, curB, _, _ = build_context(sB, seqpos, k, K)
            h_k_null = cond_entropy_context(ctxB, curB, n_ctx, K)
            null_mi_k.append(h1 - h_k_null)
        R["Q2_orders"][k] = dict(
            n_contexts_used=int(len(valid)),
            H_k_real=h_k_real,
            MI_k_real=mi_k_real,
            **{"null_" + kk: vv for kk, vv in summarize_null(mi_k_real, null_mi_k).items()}
        )

    # ---- Q3: positional vs sequential -------------------------------------
    # (a) conditional MI given (isPrevInit,isCurFinal) stratum, real data
    strata_key = (pos_cat[:-1] == 0).astype(np.int64) * 2 + (pos_cat[1:] == 2).astype(np.int64)
    mask_line = line_id[:-1] == line_id[1:]
    strata_key = strata_key[mask_line]
    prev_m, cur_m = prev, cur  # already masked equivalently
    cmi_real = 0.0
    strat_report = {}
    tot_pairs = len(prev_m)
    for s in range(4):
        idx = strata_key == s
        cnt = int(idx.sum())
        if cnt < 20:
            continue
        h2_s = cond_entropy_pairs(prev_m[idx], cur_m[idx], K)
        # use cur-marginal within stratum for a fair local H1 (predicting cur from its own stratum marginal)
        h1_cur_s, _ = unigram_entropy(cur_m[idx], K)
        mi_s = h1_cur_s - h2_s
        w = cnt / tot_pairs
        cmi_real += w * mi_s
        strat_report[int(s)] = dict(n=cnt, weight=w, H1_cur=h1_cur_s, H2=h2_s, MI=mi_s)
    R["Q3_strata"] = strat_report
    R["Q3_conditional_MI_given_position_real"] = cmi_real

    # (b) same conditional-MI-given-position statistic computed under Null C
    #     (position-marginal-preserving shuffle): this is the *expected*
    #     conditional MI given position under pure positional artifact with
    #     zero genuine sequential coupling.
    null_cmi_C = []
    for _ in range(N_REP):
        sC = shuffle_within_category(states, pos_cat, rng, 3)
        pC, cC = adjacent_pairs(sC, line_id)
        cmi = 0.0
        for s in range(4):
            idx = strata_key == s
            cnt = int(idx.sum())
            if cnt < 20:
                continue
            h1_cur_s, _ = unigram_entropy(cC[idx], K)
            h2_s = cond_entropy_pairs(pC[idx], cC[idx], K)
            cmi += (cnt / tot_pairs) * (h1_cur_s - h2_s)
        null_cmi_C.append(cmi)
    R["Q3_conditional_MI_given_position_vs_nullC"] = summarize_null(cmi_real, null_cmi_C)

    # (c) also report the "pure positional artifact" MI magnitude directly:
    #     unconditional adjacent MI computed ON Null C draws themselves,
    #     i.e. R["Q1_null_within_position"] mean IS that quantity already.

    # ---- Q4: internal (body) vs sequential (neighbor) --------------------
    body_ids = A["body_ids"]
    nB = A["n_bodies"]
    # restrict to rows with a predecessor in the same line (seqpos>=1)
    valid1 = np.where(seqpos >= 1)[0]
    cur_b = states[valid1]
    body_b = body_ids[valid1]
    prev_b = states[valid1 - 1]

    h_state_given_body = cond_entropy_context(body_b, cur_b, nB, K)
    # joint context (body, prev_state) -> code body*K+prev
    joint_ctx = body_b * K + prev_b
    h_state_given_body_prev = cond_entropy_context(joint_ctx, cur_b, nB * K, K)
    real_drop = h_state_given_body - h_state_given_body_prev

    null_drops = []
    for _ in range(N_REP):
        prev_shuf = rng.permutation(prev_b)
        joint_ctx_shuf = body_b * K + prev_shuf
        h_shuf = cond_entropy_context(joint_ctx_shuf, cur_b, nB * K, K)
        null_drops.append(h_state_given_body - h_shuf)

    R["Q4_H_state_given_body"] = h_state_given_body
    R["Q4_H_state_given_body_and_prev"] = h_state_given_body_prev
    R["Q4_real_drop_from_neighbor_given_body"] = real_drop
    R["Q4_vs_null"] = summarize_null(real_drop, null_drops)
    R["Q4_H_state_marginal"] = h1

    # ---- Q5: per-section / per-hand uniformity ----------------------------
    per_group = {}
    for gname, fmap in (("section", folio_section), ("hand", folio_hand)):
        groups = collections.defaultdict(list)
        for lid, fo in A["folio_of_line"].items():
            g = fmap.get(fo)
            if g is None:
                continue
            groups[g].append(lid)
        gres = {}
        for g, lids in groups.items():
            lidset = set(lids)
            row_mask = np.array([lid in lidset for lid in line_id])
            sub_states = states[row_mask]
            sub_line_id = line_id[row_mask]
            if len(sub_states) < 100:
                gres[g] = dict(n_tokens=int(len(sub_states)), skipped="too_small")
                continue
            h1_g, _ = unigram_entropy(sub_states, K)
            pg, cg = adjacent_pairs(sub_states, sub_line_id)
            if len(pg) < 30:
                gres[g] = dict(n_tokens=int(len(sub_states)), skipped="too_few_pairs")
                continue
            h2_g = cond_entropy_pairs(pg, cg, K)
            mi_g = h1_g - h2_g
            nrep_g = 300
            nulls_g = []
            for _ in range(nrep_g):
                sB = shuffle_within_line(sub_states, sub_line_id, rng, len(sub_states))
                pgB, cgB = adjacent_pairs(sB, sub_line_id)
                nulls_g.append(h1_g - cond_entropy_pairs(pgB, cgB, K))
            summ = summarize_null(mi_g, nulls_g)
            gres[g] = dict(
                n_tokens=int(len(sub_states)), n_lines=len(lids), n_pairs=int(len(pg)),
                H1=h1_g, MI=mi_g, MI_pct_H1=100.0 * mi_g / h1_g if h1_g else float("nan"),
                **{"null_" + k: v for k, v in summ.items()}
            )
        per_group[gname] = gres
    R["Q5_groups"] = per_group

    return R


def main():
    all_rows = load_rows()
    strict_rows = [r for r in all_rows if r["tier"] == "STRICT_ACCEPTED"]
    folio_hand, folio_section = load_folio_hand_section()

    results = {}
    for label, rows in (("FULL", all_rows), ("STRICT", strict_rows)):
        print(f"\n### Running pipeline: {label} (n={len(rows)}) ###", file=sys.stderr)
        results[label] = run_pipeline(rows, label, folio_hand, folio_section)

    with open(OUT + "/results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # ---- Human-readable report to stdout ----
    for label in ("FULL", "STRICT"):
        R = results[label]
        print("\n" + "=" * 78)
        print(f"[{label}]  n_tokens={R['n_tokens']}  n_lines={R['n_lines']}  n_pairs={R['n_pairs']}  K={R['K_states']}")
        print("=" * 78)
        print(f"H1 (unigram)         = {R['H1']:.4f} bits")
        print(f"H2 (H[next|prev])    = {R['H2_real']:.4f} bits")
        print(f"MI adjacent (real)   = {R['MI_real']:.4f} bits  ({R['MI_real_pct_H1']:.2f}% of H1)")
        print("\n-- Q1: significance of adjacent MI vs 3 nulls --")
        for k in ("Q1_null_global", "Q1_null_within_line", "Q1_null_within_position"):
            d = R[k]
            print(f"  {k:28s} null_mean={d['null_mean']:.5f} null_sd={d['null_sd']:.5f} "
                  f"z={d['z']:7.2f}  p={d['p']:.4f}  null_range=[{d['null_min']:.5f},{d['null_max']:.5f}]")
        print("\n-- Q2: higher-order conditional structure --")
        for k, d in R["Q2_orders"].items():
            print(f"  k={k}  n_ctx_obs={d['n_contexts_used']:6d}  H_k={d['H_k_real']:.4f}  "
                  f"MI_k={d['MI_k_real']:.4f}  null_mean={d['null_null_mean']:.4f} "
                  f"z={d['null_z']:7.2f} p={d['null_p']:.4f}")
        print("\n-- Q3: positional vs sequential --")
        print(f"  conditional MI | position (real) = {R['Q3_conditional_MI_given_position_real']:.4f} bits "
              f"(unconditional real MI = {R['MI_real']:.4f})")
        d = R["Q3_conditional_MI_given_position_vs_nullC"]
        print(f"  vs Null-C (position-marginal-preserving) : null_mean={d['null_mean']:.4f} "
              f"z={d['z']:.2f} p={d['p']:.4f}")
        for s, sd in R["Q3_strata"].items():
            print(f"    stratum {s} (0=med-med,1=med-final,2=init-med,3=init-final): "
                  f"n={sd['n']:5d} w={sd['weight']:.3f} MI={sd['MI']:.4f}")
        print("\n-- Q4: body-explained vs neighbor-explained --")
        print(f"  H(state)                 = {R['Q4_H_state_marginal']:.4f}")
        print(f"  H(state|body)            = {R['Q4_H_state_given_body']:.4f}")
        print(f"  H(state|body,prev_state) = {R['Q4_H_state_given_body_and_prev']:.4f}")
        print(f"  real drop from neighbor  = {R['Q4_real_drop_from_neighbor_given_body']:.5f}")
        d = R["Q4_vs_null"]
        print(f"  null drop (shuffled prev, same sparsity): mean={d['null_mean']:.5f} sd={d['null_sd']:.5f} "
              f"z={d['z']:.2f} p={d['p']:.4f}")
        print("\n-- Q5: per-section / per-hand uniformity --")
        for gname, gres in R["Q5_groups"].items():
            print(f"  [{gname}]")
            for g, d in sorted(gres.items()):
                if "skipped" in d:
                    print(f"    {g:10s} n={d['n_tokens']:6d}  SKIPPED ({d['skipped']})")
                else:
                    print(f"    {g:10s} n_tok={d['n_tokens']:6d} n_pairs={d['n_pairs']:5d} "
                          f"MI={d['MI']:.4f} ({d['MI_pct_H1']:.1f}% H1) "
                          f"z={d['null_z']:6.2f} p={d['null_p']:.4f}")

    print("\nDONE. Wrote results.json", file=sys.stderr)


if __name__ == "__main__":
    main()
