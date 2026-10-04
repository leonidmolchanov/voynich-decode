#!/usr/bin/env python3
"""
Common loaders / stream builders / estimators for the linguistic-laws deep test.

Goal: try to BREAK the meaningless-generator hypothesis with published
"pro-language" signatures (Menzerath, Brevity residual, LONG-RANGE
correlations via DFA / spectral / MI-decay, and recent-paper claims).

READ-ONLY on all source data. All source access goes through the project's own
generator_spec/vgen_lib.py so the tokenizer / molecule decomposition are
IDENTICAL to the rest of the project.

Corpora produced (each: word-token list + flat glyph/char stream + per-word
glyph lists so we can build word-order-shuffle char nulls and length series):

  REAL      : Voynich, manuscript order. words = molecules AND surfaces.
  GEN       : generator_spec/generator.py output (copy+drift+grammar), the
              STRONGEST available meaning-free null (its rolling drift buffer is
              exactly the mechanism that could manufacture long-range structure)
              -> fairest to the generator = hardest test for "generator FAILS".
  SHUF_glyph: global shuffle of REAL glyph stream  (destroys ALL order -> floor)
  SHUF_word : shuffle REAL word order, keep words intact (destroys only
              INTER-word order -> isolates genuine long-range word dependency)
  ENG       : English prose (J.Q.Adams, Ford ed.)      [illustrative NL control]
  LAT       : Latin prose (Caesar, De Bello Gallico)   [illustrative NL control]
"""
import sys, os, re, collections, math, random
import numpy as np
from pathlib import Path

RELEASE_ROOT = Path(__file__).resolve().parents[2]       # PUBLIC_RELEASE
GS = str(RELEASE_ROOT / "src" / "voynich_generator")
sys.path.insert(0, GS)
import vgen_lib as L          # project tokenizer + molecule decomposition
import generator as G         # fitted copy+drift+grammar generator

ROOT = str(RELEASE_ROOT)
ENG_TXT = str(RELEASE_ROOT / "analysis" / "controls" / "english_jqadams.txt")
LAT_TXT1 = str(RELEASE_ROOT / "analysis" / "controls" / "latin_caesar_218.txt")
LAT_TXT2 = str(RELEASE_ROOT / "analysis" / "controls" / "latin_caesar_18837.txt")


# --------------------------------------------------------------- containers ---
class Corpus:
    def __init__(self, name, words, wordglyphs):
        """words: list[str] token labels (for word-level stats / MI).
           wordglyphs: list[list[str]] the glyph/char tokens of each word,
                       in the SAME order -> flat stream + length series + the
                       word-order-shuffle char null all derive from this."""
        self.name = name
        self.words = words
        self.wordglyphs = wordglyphs
        self.wlen = np.array([len(w) for w in wordglyphs], dtype=float)  # length in glyph-tokens
        self.glyphs = [g for wg in wordglyphs for g in wg]              # flat, NO spaces
    def flat_codes(self, sym2i=None):
        if sym2i is None:
            syms = sorted(set(self.glyphs))
            sym2i = {s: i for i, s in enumerate(syms)}
        return np.array([sym2i[g] for g in self.glyphs], dtype=np.int64), sym2i
    def word_codes(self):
        syms = sorted(set(self.words))
        w2i = {s: i for i, s in enumerate(syms)}
        return np.array([w2i[w] for w in self.words], dtype=np.int64), w2i


# --------------------------------------------------------------- REAL / GEN ---
def load_real():
    rows = L.load()                       # manuscript order, 23859 tokens
    words_mol = [r['mol'] for r in rows]
    words_surf = [r['surface'] for r in rows]
    wg = [L.tokenize(r['surface']) for r in rows]   # glyph-token list per word
    return rows, words_mol, words_surf, wg


def gen_corpus(rows, laafu, seed):
    syn, _ = G.generate(rows, laafu=laafu, seed=seed)
    words_mol = [s['mol'] for s in syn]
    wg = [L.tokenize(s['surface']) for s in syn]
    return words_mol, wg


# ---------------------------------------------------------------- NL corpora --
_word_re = re.compile(r"[a-z]+")

def _load_text_words(paths, strip_gutenberg=True):
    txt = []
    for p in paths:
        with open(p, encoding='utf-8', errors='ignore') as f:
            txt.append(f.read())
    s = "\n".join(txt).lower()
    # crude front/back matter strip for gutenberg-style: keep the bulk middle
    toks = _word_re.findall(s)
    return toks

def nl_corpus(name, paths, n_words, seed=0):
    toks = _load_text_words(paths)
    # take a contiguous middle chunk of n_words to avoid front/back matter
    if len(toks) > n_words + 4000:
        start = 2000
        toks = toks[start:start + n_words]
    else:
        toks = toks[:n_words]
    wg = [list(w) for w in toks]           # char list per word
    return Corpus(name, list(toks), wg)


# ---------------------------------------------------------------- shuffles ----
def shuffle_glyph_corpus(real, rng):
    """global shuffle of the glyph stream -> destroys ALL sequential order.
    Rebuild fake 'words' by re-segmenting with the real word-length sequence so
    length series is preserved but content is order-random."""
    g = list(real.glyphs)
    rng.shuffle(g)
    wg, i = [], 0
    for L_ in real.wlen.astype(int):
        wg.append(g[i:i + L_]); i += L_
    return Corpus("SHUF_glyph", ["".join(x) for x in wg], wg)

def shuffle_word_corpus(real, rng):
    """shuffle WORD ORDER, keep each word intact -> destroys only inter-word
    order. Kills genuine long-range word dependency but preserves word-internal
    structure + word-length + type frequencies."""
    idx = list(range(len(real.wordglyphs)))
    rng.shuffle(idx)
    wg = [real.wordglyphs[i] for i in idx]
    words = [real.words[i] for i in idx]
    return Corpus("SHUF_word", words, wg)


# ================================================================ ESTIMATORS ==
def mi_at_lag(codes, d, K):
    """Plug-in mutual information (bits) between symbols at distance d."""
    if d >= len(codes):
        return 0.0, 0
    a = codes[:-d]; b = codes[d:]
    n = len(a)
    idx = a * K + b
    joint = np.bincount(idx, minlength=K * K).astype(float).reshape(K, K)
    joint /= n
    pa = joint.sum(1); pb = joint.sum(0)
    nz = joint > 0
    outer = np.outer(pa, pb)
    mi = float((joint[nz] * np.log2(joint[nz] / outer[nz])).sum())
    return mi, n

def mi_curve(codes, K, lags):
    return {d: mi_at_lag(codes, d, K)[0] for d in lags}


def dfa(x, scales, order=1):
    """Detrended Fluctuation Analysis. x: 1-D series.
    Returns (scales_used, F(scales), alpha) with alpha the log-log slope.
    Integrated profile, non-overlapping windows from both ends, order-1 detrend.
    alpha=0.5 uncorrelated; >0.5 persistent long-range; ~1.0 = 1/f."""
    x = np.asarray(x, float)
    x = x - x.mean()
    y = np.cumsum(x)
    N = len(y)
    Fs, ss = [], []
    for s in scales:
        if s < 4 or s > N // 4:
            continue
        nseg = N // s
        # from start and from end (doubles segments)
        segs = []
        for k in range(nseg):
            segs.append(y[k * s:(k + 1) * s])
        for k in range(nseg):
            segs.append(y[N - (k + 1) * s:N - k * s])
        t = np.arange(s)
        rms = []
        for seg in segs:
            c = np.polyfit(t, seg, order)
            fit = np.polyval(c, t)
            rms.append(np.mean((seg - fit) ** 2))
        F = math.sqrt(np.mean(rms))
        if F > 0:
            Fs.append(F); ss.append(s)
    ss = np.array(ss, float); Fs = np.array(Fs, float)
    if len(ss) < 3:
        return ss, Fs, float('nan')
    alpha = float(np.polyfit(np.log(ss), np.log(Fs), 1)[0])
    return ss, Fs, alpha


def return_interval_series(codes, sym):
    """Arutyunov et al.: series of GAPS (distances) between successive
    occurrences of one symbol. Long-range memory in a symbol's spacing ->
    DFA alpha of the gap series > 0.5."""
    pos = np.where(codes == sym)[0]
    if len(pos) < 20:
        return None
    return np.diff(pos).astype(float)

def dfa_returnintervals(codes, K, scales, topk=6, min_occ=200):
    """Average DFA alpha over the gap-series of the top-k most frequent symbols
    (frequency-weighted). Mapping-free (does not depend on any glyph->number
    coding)."""
    counts = np.bincount(codes, minlength=K)
    order = np.argsort(counts)[::-1]
    alphas, wts, detail = [], [], {}
    for sym in order[:topk]:
        if counts[sym] < min_occ:
            continue
        ri = return_interval_series(codes, sym)
        if ri is None or len(ri) < 60:
            continue
        _, _, a = dfa(ri, scales)
        if not math.isnan(a):
            alphas.append(a); wts.append(counts[sym]); detail[int(sym)] = (a, int(counts[sym]))
    if not alphas:
        return float('nan'), {}
    alphas = np.array(alphas); wts = np.array(wts, float)
    return float((alphas * wts).sum() / wts.sum()), detail


def psd_slope(x, fmax_frac=0.15, detrend=True):
    """Power spectral density slope beta (S(f) ~ f^-beta) fit on the low-freq
    band [1/N, fmax_frac] via periodogram in log-log. beta~0 white; beta>0
    long-range (beta ~ 2*alpha-1)."""
    x = np.asarray(x, float)
    if detrend:
        x = x - x.mean()
    N = len(x)
    ps = np.abs(np.fft.rfft(x)) ** 2
    freqs = np.fft.rfftfreq(N, d=1.0)
    m = (freqs > 0) & (freqs <= fmax_frac)
    f = freqs[m]; p = ps[m]
    # log-bin average to stabilise the fit
    lf = np.log(f); lp = np.log(p)
    nb = 30
    bins = np.linspace(lf.min(), lf.max(), nb + 1)
    xs, ys = [], []
    for i in range(nb):
        sel = (lf >= bins[i]) & (lf < bins[i + 1])
        if sel.sum() >= 2:
            xs.append(lf[sel].mean()); ys.append(lp[sel].mean())
    if len(xs) < 4:
        return float('nan')
    beta = -float(np.polyfit(xs, ys, 1)[0])
    return beta


if __name__ == "__main__":
    rows, wm, ws, wg = load_real()
    real = Corpus("REAL_mol", wm, wg)
    print("REAL words:", len(real.words), "glyph stream:", len(real.glyphs),
          "|alphabet|:", len(set(real.glyphs)))
    print("mean word len (glyph-tokens):", real.wlen.mean())
