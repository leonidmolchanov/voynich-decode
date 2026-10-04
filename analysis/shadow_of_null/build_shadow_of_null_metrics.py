#!/usr/bin/env python3
"""Shadow-of-null control.

Applies the SAME deterministic factorization rule used by the shadow layer
(body = strip first+last glyph token; state = f(last glyph token)) to three
corpora:
  (a) REAL Voynich surfaces (from full_symbolic_factorization.tsv);
  (b) WORD-INTERNAL glyph-shuffle null (shuffle glyph order within each word,
      50 replicates);
  (c) 1st-order glyph-Markov GENERATOR null, trained on the real corpus's own
      glyph bigram (incl. START/END) statistics, matched word count,
      50 replicates.

Read-only over the project's existing TSV. All outputs written under this
same directory. Does not touch MASTER/accepted, does not run the strict
merge/promotion step, does not call any GPU/remote process.
"""
from __future__ import annotations
import csv, json, math, random, statistics, os
from collections import Counter, defaultdict

from pathlib import Path
RELEASE_ROOT = Path(__file__).resolve().parents[2]  # PUBLIC_RELEASE
FULL = str(RELEASE_ROOT / "data" / "factorization" / "full_surface_factorization.tsv")
OUT = str(Path(__file__).resolve().parent)  # this suite's directory
os.makedirs(OUT, exist_ok=True)

N_REPLICATES = 50
MAX_GEN_LEN = 40  # safety cap on generator word length

# ---------------------------------------------------------------------------
# 1. Tokenizer: verbatim from scripts/edge_state_machine.py (the project's own
#    canonical EVA multi-glyph tokenizer). Same rule for all three corpora.
# ---------------------------------------------------------------------------
MULTI = ("cth", "ckh", "cph", "cfh", "ch", "sh")


def glyphs(word: str) -> tuple:
    out = []
    cursor = 0
    while cursor < len(word):
        unit = next((g for g in MULTI if word.startswith(g, cursor)), None)
        if unit:
            out.append(unit)
            cursor += len(unit)
        else:
            out.append(word[cursor])
            cursor += 1
    return tuple(out)


# ---------------------------------------------------------------------------
# 2. State rule: deterministic last-glyph -> S-class table, per
#    tmp/shadow_analysis/FINDINGS.md, extended with the empirically-verified
#    majority mapping (g -> S1, confirmed 23/23 pure in the real corpus).
#    Anything not in the table gets a lossless catch-all U[<glyph>] label
#    (carries the raw glyph forward; not a forced/arbitrary bucket).
# ---------------------------------------------------------------------------
STATE_TABLE = {
    "y": "S8", "l": "S4", "r": "S6", "n": "S5", "m": "S5", "s": "S7",
    "o": "S0", "a": "S0", "d": "S2", "k": "S3", "t": "S3", "p": "S3",
    "e": "S1", "sh": "S1", "g": "S1",
}


def state_of(tok_tuple):
    last = tok_tuple[-1]
    return STATE_TABLE.get(last, f"U[{last}]")


def body_of(tok_tuple):
    return tok_tuple[1:-1]


def entropy(counter):
    tot = sum(counter.values())
    if tot == 0:
        return 0.0
    h = 0.0
    for c in counter.values():
        if c > 0:
            p = c / tot
            h -= p * math.log2(p)
    return h


# ---------------------------------------------------------------------------
# 3. Load real corpus + verify the rule against the project's own STRICT
#    symbolic_factor column (sanity gate on the tokenizer/state table).
# ---------------------------------------------------------------------------
real_words = []
verify_total = 0
verify_body_match = 0
verify_state_match = 0
verify_strict_total = 0
verify_strict_body_match = 0
verify_strict_state_match = 0

with open(FULL, encoding="utf-8") as f:
    for d in csv.DictReader(f, delimiter="\t"):
        surf = d["surface"]
        toks = glyphs(surf)
        real_words.append(toks)
        sym = d["symbolic_factor"]
        body_str, _, st = sym.rpartition("=>")
        body_str = body_str.strip()
        exp_body = tuple() if body_str in ("", "<EMPTY>") else tuple(body_str.split())
        got_body = body_of(toks)
        got_state = state_of(toks)
        verify_total += 1
        bm = got_body == exp_body
        sm = got_state == st
        verify_body_match += bm
        verify_state_match += sm
        if d["assignment_tier"] == "STRICT_ACCEPTED":
            verify_strict_total += 1
            verify_strict_body_match += bm
            verify_strict_state_match += sm

N = len(real_words)
print(f"loaded {N} real words")
print(f"tokenizer+body reproduction vs project symbolic_factor (ALL tiers): "
      f"{verify_body_match}/{verify_total} = {100*verify_body_match/verify_total:.3f}%")
print(f"state-table reproduction vs project symbolic_factor (ALL tiers): "
      f"{verify_state_match}/{verify_total} = {100*verify_state_match/verify_total:.3f}%")
print(f"tokenizer+body reproduction on STRICT_ACCEPTED only: "
      f"{verify_strict_body_match}/{verify_strict_total} = {100*verify_strict_body_match/verify_strict_total:.3f}%")
print(f"state-table reproduction on STRICT_ACCEPTED only: "
      f"{verify_strict_state_match}/{verify_strict_total} = {100*verify_strict_state_match/verify_strict_total:.3f}%")

# ---------------------------------------------------------------------------
# 4. Edit-distance-<=1 neighbor detection over a body vocabulary (deletion-
#    index / SymSpell-style trick; exact for edit distance <= 1).
# ---------------------------------------------------------------------------

def edit1_neighbor_stats(body_counts):
    """body_counts: dict[tuple, int], NON-EMPTY bodies only.
    Returns (frac_distinct_types_with_neighbor, frac_token_mass_with_neighbor).
    """
    vocab = set(body_counts.keys())
    if not vocab:
        return 0.0, 0.0
    delete_index = defaultdict(set)
    for t in vocab:
        for i in range(len(t)):
            key = t[:i] + t[i + 1:]
            delete_index[key].add(t)
    has_neighbor = set()
    for t in vocab:
        candidates = set()
        for i in range(len(t)):
            key = t[:i] + t[i + 1:]
            candidates |= delete_index.get(key, set())
            if key in vocab:
                candidates.add(key)
        candidates |= delete_index.get(t, set())
        candidates.discard(t)
        if candidates:
            has_neighbor.add(t)
    total_mass = sum(body_counts.values())
    mass_with = sum(body_counts[t] for t in has_neighbor)
    return len(has_neighbor) / len(vocab), (mass_with / total_mass if total_mass else 0.0)


# ---------------------------------------------------------------------------
# 5. Metric bundle for a corpus (list of glyph-tuples).
# ---------------------------------------------------------------------------

def compute_metrics(words):
    n = len(words)
    states = [state_of(w) for w in words]
    st_counts = Counter(states)
    h_state = entropy(st_counts)
    top1_state_share = max(st_counts.values()) / n
    n_states_used = len(st_counts)

    bodies = [body_of(w) for w in words]
    body_counts = Counter(bodies)
    n_body_types = len(body_counts)
    empty_body_rate = body_counts.get((), 0) / n
    hapax_types = sum(1 for c in body_counts.values() if c == 1)
    hapax_rate_of_types = hapax_types / n_body_types
    ttr = n_body_types / n
    h_body = entropy(body_counts)

    sorted_counts = sorted(body_counts.values(), reverse=True)
    def topk_cov(k):
        return sum(sorted_counts[:k]) / n
    cov1, cov10, cov50 = topk_cov(1), topk_cov(10), topk_cov(50)

    nonempty_body_counts = {b: c for b, c in body_counts.items() if len(b) > 0}
    neigh_frac_types, neigh_frac_mass = edit1_neighbor_stats(nonempty_body_counts)

    ne_total = sum(nonempty_body_counts.values())
    ne_sorted = sorted(nonempty_body_counts.values(), reverse=True)
    def ne_topk_cov(k):
        return sum(ne_sorted[:k]) / ne_total if ne_total else 0.0
    ne_cov10, ne_cov50 = ne_topk_cov(10), ne_topk_cov(50)

    return {
        "n_words": n,
        "H_state_bits": h_state,
        "n_states_used": n_states_used,
        "top1_state_share": top1_state_share,
        "n_body_types": n_body_types,
        "TTR": ttr,
        "hapax_rate_of_body_types": hapax_rate_of_types,
        "empty_body_rate": empty_body_rate,
        "H_body_bits": h_body,
        "top1_body_coverage": cov1,
        "top10_body_coverage": cov10,
        "top50_body_coverage": cov50,
        "top10_nonempty_body_coverage": ne_cov10,
        "top50_nonempty_body_coverage": ne_cov50,
        "edit1_neighbor_frac_of_nonempty_body_types": neigh_frac_types,
        "edit1_neighbor_frac_of_nonempty_body_mass": neigh_frac_mass,
    }


real_metrics = compute_metrics(real_words)
print("\nREAL metrics:")
for k, v in real_metrics.items():
    print(f"  {k:42s} {v}")

# ---------------------------------------------------------------------------
# 6(b). WORD-INTERNAL glyph-shuffle null. Preserves per-word length + glyph
# multiset; destroys within-word order. 50 replicates, seeded, reproducible.
# ---------------------------------------------------------------------------

def shuffle_replicate(words, seed):
    rng = random.Random(f"SHUFFLE|{seed}")
    out = []
    for w in words:
        if len(w) <= 1:
            out.append(w)
            continue
        lst = list(w)
        rng.shuffle(lst)
        out.append(tuple(lst))
    return out


shuffle_reps = []
for r in range(N_REPLICATES):
    rep_words = shuffle_replicate(real_words, r)
    shuffle_reps.append(compute_metrics(rep_words))
    print(f"shuffle replicate {r+1}/{N_REPLICATES} done", end="\r")
print()

# ---------------------------------------------------------------------------
# 6(c). 1st-order glyph Markov GENERATOR null, trained on the real corpus's
# own glyph-bigram (incl. START/END) statistics. Matched word count.
# ---------------------------------------------------------------------------
START, END = "<S>", "<E>"
trans_counts = defaultdict(Counter)
for w in real_words:
    seq = [START] + list(w) + [END]
    for a, b in zip(seq[:-1], seq[1:]):
        trans_counts[a][b] += 1

# precompute cumulative distributions for fast sampling
cum_dist = {}
for a, ctr in trans_counts.items():
    items = sorted(ctr.items())  # deterministic order
    total = sum(c for _, c in items)
    acc = []
    running = 0.0
    for sym, c in items:
        running += c / total
        acc.append((running, sym))
    cum_dist[a] = acc


def sample_next(rng, state):
    acc = cum_dist[state]
    x = rng.random()
    for cum, sym in acc:
        if x <= cum:
            return sym
    return acc[-1][1]


def generate_replicate(n_words, seed):
    rng = random.Random(f"GENERATE|{seed}")
    out = []
    for _ in range(n_words):
        seq = []
        state = START
        steps = 0
        while True:
            nxt = sample_next(rng, state)
            steps += 1
            if nxt == END:
                break
            seq.append(nxt)
            state = nxt
            if steps >= MAX_GEN_LEN:
                break
        if not seq:
            # resample once to avoid a degenerate empty word (never observed
            # in the real corpus, min length 1); extremely rare.
            state = START
            nxt = sample_next(rng, state)
            if nxt != END:
                seq = [nxt]
            else:
                seq = [rng.choice(list(trans_counts[START].keys()))]
        out.append(tuple(seq))
    return out


gen_reps = []
for r in range(N_REPLICATES):
    rep_words = generate_replicate(N, r)
    gen_reps.append(compute_metrics(rep_words))
    print(f"generator replicate {r+1}/{N_REPLICATES} done", end="\r")
print()

# ---------------------------------------------------------------------------
# 7. Aggregate: mean/sd across replicates, z = (real - null_mean)/null_sd.
# ---------------------------------------------------------------------------

def aggregate(rep_list, real_val_dict):
    keys = rep_list[0].keys()
    agg = {}
    for k in keys:
        vals = [r[k] for r in rep_list]
        mean = statistics.mean(vals)
        sd = statistics.stdev(vals) if len(set(vals)) > 1 else 0.0
        real_v = real_val_dict[k]
        z = (real_v - mean) / sd if sd > 0 else (float("inf") if real_v != mean else 0.0)
        agg[k] = {"real": real_v, "null_mean": mean, "null_sd": sd, "z": z,
                  "null_min": min(vals), "null_max": max(vals)}
    return agg


shuffle_agg = aggregate(shuffle_reps, real_metrics)
gen_agg = aggregate(gen_reps, real_metrics)

result = {
    "n_real_words": N,
    "n_replicates": N_REPLICATES,
    "tokenizer_verification": {
        "all_tiers_body_match_rate": verify_body_match / verify_total,
        "all_tiers_state_match_rate": verify_state_match / verify_total,
        "strict_accepted_body_match_rate": verify_strict_body_match / verify_strict_total,
        "strict_accepted_state_match_rate": verify_strict_state_match / verify_strict_total,
        "strict_accepted_n": verify_strict_total,
    },
    "real": real_metrics,
    "vs_word_internal_shuffle_null": shuffle_agg,
    "vs_generator_1st_order_markov_null": gen_agg,
}

with open(OUT + "/metrics_shadow_of_null.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, sort_keys=True)

print("\nWrote", OUT + "/metrics_shadow_of_null.json")

# ---------------------------------------------------------------------------
# 8. Human-readable side-by-side table on stdout.
# ---------------------------------------------------------------------------
print("\n" + "=" * 100)
print(f"{'metric':42s} {'real':>12s} {'shuffle_mean±sd':>22s} {'z':>8s} {'gen_mean±sd':>22s} {'z':>8s}")
print("=" * 100)
for k in real_metrics:
    rv = real_metrics[k]
    sa = shuffle_agg[k]
    ga = gen_agg[k]
    rv_s = f"{rv:.4f}" if isinstance(rv, float) else str(rv)
    print(f"{k:42s} {rv_s:>12s} "
          f"{sa['null_mean']:.4f}±{sa['null_sd']:.4f}".rjust(22) + f" {sa['z']:8.2f} "
          f"{ga['null_mean']:.4f}±{ga['null_sd']:.4f}".rjust(22) + f" {ga['z']:8.2f}")
