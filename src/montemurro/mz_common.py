#!/usr/bin/env python3
"""
Shared loader + Montemurro-Zanette word-section information measure.

READ-ONLY over:
  data/factorization/full_surface_factorization.tsv
  metadata/currier_ab_map.md

The Montemurro-Zanette (2013) idea, reconstructed:
  Partition the text into P parts (semantic sections, Currier A/B, or equal-length
  word blocks). For each word type w, measure how much its occurrence distribution
  over the parts departs from a uniform (part-size-proportional) scatter. Aggregated
  over words weighted by frequency this is exactly the mutual information I(W;Part)
  between word-identity and part.

  MI has a positive finite-sampling bias (a random scatter of a finite corpus still
  gives MI>0). Montemurro's real move is to measure information ABOVE that floor.
  We therefore report the *excess* information:
        Excess(C) = I(W;P)_observed  -  mean_over_word-order-shuffles I(W;P)
  which is corpus-specific-bias-corrected (each corpus is compared to ITS OWN
  shuffle floor -- essential for fairness when comparing corpora with different
  vocabularies / frequency distributions).
"""
import csv, re, math, collections
from pathlib import Path
import numpy as np

RELEASE_ROOT = Path(__file__).resolve().parents[2]
TSV = RELEASE_ROOT / "data" / "factorization" / "full_surface_factorization.tsv"
MD = RELEASE_ROOT / "metadata" / "currier_ab_map.md"

# Section-label -> display-name map; keys match metadata/currier_ab_map.md.
# 'zodiac' intentionally absent (excluded from the section map, as originally).
SECNAME = {'herbal': 'Herbal', 'astro': 'Astro', 'bio': 'Bio',
           'rosettes': 'Cosmo', 'pharma': 'Pharma', 'recipes': 'Recipes'}


def _base_folio(fo):
    m = re.match(r'^(f\d+[rv])\d*$', fo)
    return m.group(1) if m else fo


def load_folio_map():
    """Return (folio_order_index, base2sec, base2ab) built from the markup, in
    manuscript reading order (markup table order)."""
    panel_rows = []
    with open(MD, encoding='utf-8') as f:
        for line in f:
            if not line.strip().startswith('|'):
                continue
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if len(cells) < 9:
                continue
            folio = cells[0]
            if not re.match(r'^f\d+', folio):
                continue
            sec = cells[1]
            cls = cells[-1].replace('*', '').strip()
            try:
                N = int(cells[2])
            except ValueError:
                N = 0
            if sec in SECNAME and cls in ('A', 'B'):
                panel_rows.append((folio, SECNAME[sec], cls, N))
    order = []
    seen = set()
    base_sec = collections.defaultdict(collections.Counter)
    base_ab = collections.defaultdict(collections.Counter)
    for fo, sec, ab, N in panel_rows:
        b = _base_folio(fo)
        if b not in seen:
            seen.add(b)
            order.append(b)
        base_sec[b][sec] += 1
        base_ab[b][ab] += max(N, 1)
    folio_order = {b: i for i, b in enumerate(order)}
    base2sec = {b: c.most_common(1)[0][0] for b, c in base_sec.items()}
    base2ab = {b: c.most_common(1)[0][0] for b, c in base_ab.items()}
    return folio_order, base2sec, base2ab


def parse_line_pos(record_id):
    left, _, pos = record_id.partition(":")
    folio, _, line = left.rpartition(".")
    try:
        posi = int(pos)
    except ValueError:
        posi = 0
    try:
        linei = int(line)
    except ValueError:
        linei = 0
    return folio, linei, posi


def load_tokens():
    """Return dict of parallel arrays in MANUSCRIPT ORDER:
       surface (list[str]), molecule (list[str]), section (list[str]),
       ab (list[str]), folio (list[str]).
    """
    folio_order, base2sec, base2ab = load_folio_map()

    def resolve(fo):
        if fo in base2sec:
            return fo
        b = _base_folio(fo)
        return b if b in base2sec else None

    rows = []
    with open(TSV, encoding='utf-8') as f:
        for d in csv.DictReader(f, delimiter='\t'):
            fo = d['folio']
            r = resolve(fo)
            if r is None:
                continue
            folioR, linei, posi = parse_line_pos(d['record_id'])
            rows.append((folio_order[r], linei, posi, d['surface'].strip(),
                         d['symbolic_factor'].strip(), base2sec[r], base2ab[r], fo))
    rows.sort(key=lambda x: (x[0], x[1], x[2]))
    surface = [r[3] for r in rows]
    molecule = [r[4] for r in rows]
    section = [r[5] for r in rows]
    ab = [r[6] for r in rows]
    folio = [r[7] for r in rows]
    return dict(surface=surface, molecule=molecule, section=section, ab=ab, folio=folio)


# ---------------------------------------------------------------- MI core ----
def _codes(tokens):
    vocab = {}
    out = np.empty(len(tokens), dtype=np.int64)
    for i, t in enumerate(tokens):
        j = vocab.get(t)
        if j is None:
            j = len(vocab)
            vocab[t] = j
        out[i] = j
    return out, len(vocab)


def mi_word_part(wids, parts, V, P):
    """Mutual information I(W;Part) in bits. wids: token->word id (len N).
    parts: token->part id (len N, values 0..P-1)."""
    N = len(wids)
    M = np.zeros((V, P), dtype=np.float64)
    np.add.at(M, (wids, parts), 1.0)
    row = M.sum(1)           # n_w
    col = M.sum(0)           # N_p
    nz = M > 0
    # MI = sum (M/N) log2( M*N / (row*col) )
    ratio = (M[nz] * N) / (row[:, None] * col[None, :])[nz]
    mi = float((M[nz] / N * np.log2(ratio)).sum())
    return mi


def excess_mi(wids, parts, V, P, rng, n_shuffle=200):
    """Observed MI minus mean word-order-shuffle MI (own-corpus bias floor).
    Returns dict(obs, floor_mean, floor_sd, excess, z_vs_floor)."""
    obs = mi_word_part(wids, parts, V, P)
    floors = np.empty(n_shuffle)
    p = parts.copy()
    for i in range(n_shuffle):
        rng.shuffle(p)
        floors[i] = mi_word_part(wids, p, V, P)
    fm = floors.mean()
    fsd = floors.std(ddof=1)
    return dict(obs=obs, floor_mean=float(fm), floor_sd=float(fsd),
                excess=float(obs - fm),
                z_vs_floor=float((obs - fm) / fsd) if fsd > 0 else float('inf'))


def make_parts_blocks(N, P):
    """Contiguous equal-length blocks over manuscript position."""
    edges = np.linspace(0, N, P + 1).astype(int)
    parts = np.empty(N, dtype=np.int64)
    for p in range(P):
        parts[edges[p]:edges[p + 1]] = p
    return parts


def label_parts(labels):
    """Map a list of string labels to (parts array, P, order list)."""
    uniq = sorted(set(labels))
    idx = {u: i for i, u in enumerate(uniq)}
    parts = np.array([idx[l] for l in labels], dtype=np.int64)
    return parts, len(uniq), uniq


# --------------------------------------------------- basic descriptive stats --
def corpus_stats(tokens):
    N = len(tokens)
    c = collections.Counter(tokens)
    V = len(c)
    freqs = np.array(sorted(c.values(), reverse=True), dtype=float)
    hapax = sum(1 for v in c.values() if v == 1)
    # adjacent literal repeat rate
    rep = sum(1 for i in range(N - 1) if tokens[i] == tokens[i + 1]) / (N - 1)
    # unigram entropy
    p = freqs / N
    H1 = float(-(p * np.log2(p)).sum())
    # zipf slope via log-log regression on rank-frequency
    ranks = np.arange(1, len(freqs) + 1)
    lr, lf = np.log(ranks), np.log(freqs)
    slope = float(np.polyfit(lr, lf, 1)[0])
    return dict(N=N, V=V, TTR=V / N, hapax_rate=hapax / V, repeat_rate=rep,
                H1=H1, zipf_slope=slope)


if __name__ == "__main__":
    d = load_tokens()
    print("tokens:", len(d['surface']))
    import collections as C
    print("section:", dict(C.Counter(d['section'])))
    print("ab:", dict(C.Counter(d['ab'])))
    print("surface stats:", corpus_stats(d['surface']))
    print("molecule stats:", corpus_stats(d['molecule']))
