#!/usr/bin/env python3
"""
Shared loader / tokenizer / slot-decomposition for the Voynichese generator spec.

READ-ONLY over the public release files:
  data/factorization/full_surface_factorization.tsv
  metadata/currier_ab_map.md   (folio -> section + Currier A/B)

Every downstream script imports from here so the tokenizer / state table / A-B
split are identical to the project's own pipeline (edge_state_machine.py MULTI
rule + last-glyph state table; A-B markup join as in montemurro/mz_common.py).
"""
import csv, re, math, collections
from pathlib import Path
import numpy as np

RELEASE_ROOT = Path(__file__).resolve().parents[2]
TSV = RELEASE_ROOT / "data" / "factorization" / "full_surface_factorization.tsv"
MD = RELEASE_ROOT / "metadata" / "currier_ab_map.md"

# Project tokenizer (edge_state_machine.py): match these multi-glyph units first.
MULTI = ["cth", "ckh", "cph", "cfh", "ch", "sh"]

# Word-final glyph -> S-state (FINDINGS.md deterministic ending channel).
STATE_TABLE = {
    'y': 'S8', 'l': 'S4', 'r': 'S6', 'n': 'S5', 'm': 'S5', 's': 'S7',
    'o': 'S0', 'a': 'S0', 'd': 'S2', 'k': 'S3', 't': 'S3', 'p': 'S3',
    'e': 'S1', 'g': 'S1', 'sh': 'S1', 'ch': 'S1',
}

# Section-label -> display-name map. Keys match the section column of
# metadata/currier_ab_map.md; 'zodiac' is intentionally absent (those leaf-sides
# are excluded from the A/B section map, as in the original analysis).
SECNAME = {'herbal': 'Herbal', 'astro': 'Astro', 'bio': 'Bio',
           'rosettes': 'Cosmo', 'pharma': 'Pharma', 'recipes': 'Recipes'}


def tokenize(s):
    """Greedy multi-glyph tokenization of an EVA surface string -> list of glyph tokens."""
    i, out, n = 0, [], len(s)
    while i < n:
        m = next((x for x in MULTI if s.startswith(x, i)), None)
        if m:
            out.append(m); i += len(m)
        else:
            out.append(s[i]); i += 1
    return out


def state_of(last_tok):
    return STATE_TABLE.get(last_tok, "U[%s]" % last_tok)


def surface_to_mol(s):
    """Return (body_tokens list, state str). body = interior tokens (strip first+last)."""
    g = tokenize(s)
    if len(g) <= 1:
        return [], state_of(g[0]) if g else "U[]"
    return g[1:-1], state_of(g[-1])


def _base_folio(fo):
    m = re.match(r'^(f\d+[rv])\d*$', fo)
    return m.group(1) if m else fo


def load_folio_map():
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
    order, seen = [], set()
    base_sec = collections.defaultdict(collections.Counter)
    base_ab = collections.defaultdict(collections.Counter)
    for fo, sec, ab, N in panel_rows:
        b = _base_folio(fo)
        if b not in seen:
            seen.add(b); order.append(b)
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


def load():
    """Return a list of token dicts in MANUSCRIPT order, each with:
       folio, line, pos, surface, mol, body(list), state, section, ab, tier,
       line_key (folio,line), and line_idx (rank of line within its page).
    Only tokens whose folio joins the A/B markup are kept (≈100%)."""
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
            _, linei, posi = parse_line_pos(d['record_id'])
            surface = d['surface'].strip()
            mol = d['symbolic_factor'].strip()
            body, _, st = mol.rpartition("=>")
            body = body.strip()
            btoks = [] if body in ("", "<EMPTY>") else body.split()
            rows.append(dict(order=folio_order[r], folio=r, raw_folio=fo,
                             line=linei, pos=posi, surface=surface, mol=mol,
                             body=btoks, state=st.strip(),
                             section=base2sec[r], ab=base2ab[r],
                             tier=d['assignment_tier']))
    rows.sort(key=lambda x: (x['order'], x['line'], x['pos']))
    # assign within-page line rank (physical line index)
    page_lines = collections.defaultdict(list)
    for r in rows:
        page_lines[r['folio']].append(r['line'])
    page_line_rank = {}
    for folio, lines in page_lines.items():
        uniq = sorted(set(lines))
        page_line_rank[folio] = {ln: i for i, ln in enumerate(uniq)}
    for r in rows:
        r['line_idx'] = page_line_rank[r['folio']][r['line']]
        r['line_key'] = (r['folio'], r['line'])
    return rows


def group_lines(rows):
    """Return list of lines; each line is a list of token dicts, in order.
    Also tags each line with is_page_first (line_idx==0) and page key."""
    lines = []
    cur_key, cur = None, []
    for r in rows:
        if r['line_key'] != cur_key:
            if cur:
                lines.append(cur)
            cur, cur_key = [], r['line_key']
        cur.append(r)
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------- slot view -----
VOWELS = set("aeo")

def slot_decompose(body):
    """Human-readable slot parse of a body-token list (interpretable view only).
    Slots: PREFIX(o?) ONSET(consonant cluster) NUC(vowel run) ELAD(#e in nuc)
           ILAD(#i glide) CODA(tail consonants). Returns dict of slot fillers.
    This is a *descriptive* decomposition used to tabulate emission stats; the
    faithful generator uses the glyph-token Markov (which induces these)."""
    d = dict(prefix='', onset='', nuc='', elad=0, ilad=0, coda='', tail=[])
    if not body:
        return d
    toks = list(body)
    # prefix o-
    if toks and toks[0] == 'o':
        d['prefix'] = 'o'; toks = toks[1:]
    # onset: leading consonantal tokens (not a/e/o/i)
    onset = []
    while toks and toks[0] not in VOWELS and toks[0] != 'i':
        onset.append(toks[0]); toks = toks[1:]
    d['onset'] = " ".join(onset)
    # nucleus: run of a/e/o
    nuc = []
    while toks and toks[0] in VOWELS:
        nuc.append(toks[0]); toks = toks[1:]
    d['nuc'] = " ".join(nuc)
    d['elad'] = sum(1 for x in nuc if x == 'e')
    # i glide
    ilad = 0
    while toks and toks[0] == 'i':
        ilad += 1; toks = toks[1:]
    d['ilad'] = ilad
    # coda = whatever remains
    d['coda'] = " ".join(toks)
    d['tail'] = toks
    return d


def entropy(counter):
    tot = sum(counter.values())
    if tot == 0:
        return 0.0
    return float(-sum((v / tot) * math.log2(v / tot) for v in counter.values() if v))


def corpus_stats(tokens):
    """tokens: list[str]. Return N,V,TTR,hapax_rate,repeat_rate,H1,zipf_slope."""
    N = len(tokens)
    c = collections.Counter(tokens)
    V = len(c)
    freqs = np.array(sorted(c.values(), reverse=True), dtype=float)
    hapax = sum(1 for v in c.values() if v == 1)
    rep = sum(1 for i in range(N - 1) if tokens[i] == tokens[i + 1]) / (N - 1)
    p = freqs / N
    H1 = float(-(p * np.log2(p)).sum())
    ranks = np.arange(1, len(freqs) + 1)
    slope = float(np.polyfit(np.log(ranks), np.log(freqs), 1)[0])
    return dict(N=N, V=V, TTR=V / N, hapax_rate=hapax / V, repeat_rate=rep,
                H1=H1, zipf_slope=slope)


if __name__ == "__main__":
    rows = load()
    print("tokens joined:", len(rows))
    print("AB:", dict(collections.Counter(r['ab'] for r in rows)))
    print("sections:", dict(collections.Counter(r['section'] for r in rows)))
    lines = group_lines(rows)
    print("lines:", len(lines))
