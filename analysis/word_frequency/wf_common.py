#!/usr/bin/env python3
"""
Shared helpers for the word-frequency / vocabulary-concentration investigation.
READ-ONLY over project data; this module only computes statistics / runs
local synthetic simulations. No network, no GPU.
"""
import collections, math, re, json, os
import numpy as np
from scipy.optimize import curve_fit

from pathlib import Path
RELEASE_ROOT = Path(__file__).resolve().parents[2]       # PUBLIC_RELEASE
_CTRL = RELEASE_ROOT / "analysis" / "controls"

LATIN_FILES = [
    str(_CTRL / "latin_caesar_218.txt"),
    str(_CTRL / "latin_caesar_18837.txt"),
]
LATIN_PICATRIX = str(_CTRL / "picatrix_latin_pingree_warburg.txt")  # optional, not shipped
ENGLISH_FILE = str(_CTRL / "english_jqadams.txt")

# ---------------------------------------------------------------- corpora --
def _extract_gutenberg(path):
    txt = open(path, encoding="utf-8", errors="ignore").read()
    m1 = re.search(r"\*\*\* START OF.*?\*\*\*", txt)
    m2 = re.search(r"\*\*\* END OF.*?\*\*\*", txt)
    body = txt[m1.end():m2.start()] if (m1 and m2) else txt
    return body


def load_latin_tokens():
    """Real running Latin prose: Caesar, De Bello Gallico I-VIII (Project
    Gutenberg plain text, already present locally in this project for an
    unrelated cipher-corpus purpose; used here read-only as a natural-language
    baseline). First 100 tokens dropped (Gutenberg credit line, in English)."""
    txt = "\n".join(_extract_gutenberg(p) for p in LATIN_FILES)
    toks = re.findall(r"[a-zA-Z]+", txt.lower())
    return toks[100:]


def load_latin_picatrix_tokens():
    """Secondary Latin baseline: Picatrix (Warburg Institute Latin edition,
    medieval astrological/magical text -- register closer to Voynich's
    presumed technical/herbal content than classical narrative Caesar).
    OCR'd, some noise expected; used only as a robustness cross-check."""
    if not os.path.exists(LATIN_PICATRIX):
        return []  # optional corpus, not shipped in the public release
    txt = open(LATIN_PICATRIX, encoding="utf-8", errors="ignore").read()
    toks = re.findall(r"[a-zA-Z]+", txt.lower())
    # drop a large front/back buffer of title-page / apparatus-criticus noise
    return toks[2000:-2000]


def load_english_tokens():
    """Real running English prose: writings of John Quincy Adams, ed. Ford
    (Project Gutenberg-derived library scan, already present locally in this
    project for an unrelated cipher-corpus purpose; used here read-only as a
    natural-language baseline). First/last 300 lines dropped (library
    stamps / index front-and-back matter)."""
    lines = open(ENGLISH_FILE, encoding="utf-8", errors="ignore").readlines()
    body = "".join(lines[300:-300])
    return re.findall(r"[a-zA-Z]+", body.lower())


def bootstrap_windows(tokens, n, reps, seed):
    """reps contiguous windows of length n, wrapping if tokens shorter than
    reps*spacing; used to get matched-N comparisons with a variance estimate."""
    rng = np.random.default_rng(seed)
    L = len(tokens)
    out = []
    for _ in range(reps):
        if L <= n:
            # wrap around (tile) -- only triggers if source shorter than n
            reps_needed = (n // L) + 1
            seq = (tokens * reps_needed)[:n]
        else:
            start = rng.integers(0, L - n)
            seq = tokens[start:start + n]
        out.append(seq)
    return out


# ---------------------------------------------------------------- stats ----
def corpus_stats_extended(tokens):
    """N, V, TTR, hapax_rate, simple Zipf slope (OLS log-rank vs log-freq,
    full range -- SAME definition as generator_spec/vgen_lib.corpus_stats, for
    exact comparability with the already-published real=-1.19 / gen=-0.96
    numbers), top-K coverage, and a Zipf-Mandelbrot fit f(r)=C/(r+beta)^alpha."""
    N = len(tokens)
    c = collections.Counter(tokens)
    V = len(c)
    freqs = np.array(sorted(c.values(), reverse=True), dtype=float)
    hapax = sum(1 for v in c.values() if v == 1)
    ranks = np.arange(1, V + 1)
    simple_slope = float(np.polyfit(np.log(ranks), np.log(freqs), 1)[0])

    def topk(k):
        return float(freqs[:k].sum() / N) if V >= 1 else 0.0

    zm = zipf_mandelbrot_fit(ranks, freqs)
    return dict(N=N, V=V, TTR=V / N, hapax_rate=hapax / V,
                zipf_slope=simple_slope,
                top10=topk(10), top50=topk(50), top100=topk(100),
                zm_alpha=zm["alpha"], zm_beta=zm["beta"], zm_r2=zm["r2"])


def zipf_mandelbrot_fit(ranks, freqs):
    """Fit log(freq) = log(C) - alpha*log(r+beta) by nonlinear least squares.
    Returns alpha, beta, C and R^2 in log-space. Robust fallback to the plain
    Zipf (beta=0) OLS fit if the nonlinear fit fails to converge."""
    logf = np.log(freqs)

    def model(r, logC, alpha, beta):
        return logC - alpha * np.log(r + np.abs(beta))

    try:
        p0 = [logf[0], 1.0, 1.0]
        popt, _ = curve_fit(model, ranks, logf, p0=p0, maxfev=20000,
                             bounds=([-np.inf, 0.05, 0.0], [np.inf, 6.0, 5000.0]))
        logC, alpha, beta = popt
        pred = model(ranks, *popt)
        ss_res = float(np.sum((logf - pred) ** 2))
        ss_tot = float(np.sum((logf - logf.mean()) ** 2))
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
        return dict(alpha=float(alpha), beta=float(beta), logC=float(logC), r2=r2)
    except Exception:
        slope, intercept = np.polyfit(np.log(ranks), logf, 1)
        pred = intercept + slope * np.log(ranks)
        ss_res = float(np.sum((logf - pred) ** 2))
        ss_tot = float(np.sum((logf - logf.mean()) ** 2))
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
        return dict(alpha=float(-slope), beta=0.0, logC=float(intercept), r2=r2)


def heaps_curve(tokens, n_points=12):
    """V(n) at n_points log-spaced prefixes; returns (ns, Vs, heaps_exponent)."""
    N = len(tokens)
    ns = np.unique(np.geomspace(max(50, N // 200), N, n_points).astype(int))
    Vs = []
    seen = set()
    idx = 0
    ns_sorted = sorted(ns)
    out_ns = []
    for target in ns_sorted:
        while idx < target:
            seen.add(tokens[idx]); idx += 1
        Vs.append(len(seen))
        out_ns.append(target)
    beta = float(np.polyfit(np.log(out_ns), np.log(Vs), 1)[0])
    return dict(ns=out_ns, Vs=Vs, heaps_exponent=beta)


def mean_sd(dicts, keys):
    out = {}
    for k in keys:
        vals = np.array([d[k] for d in dicts], dtype=float)
        out[k] = dict(mean=float(vals.mean()), sd=float(vals.std()))
    return out


# ---------------------------------------------------------- mechanism (ii) -
def simulate_crp(n, theta, rng):
    """Hoppe/Chinese-Restaurant-Process (Polya urn) sequence of n draws with
    concentration theta. O(n): new-table w.p. theta/(theta+i); else COPY the
    table of a uniformly random EARLIER draw (exactly equivalent to picking
    an existing table with probability proportional to its current size --
    the textbook preferential-attachment / rich-get-richer construction)."""
    assign = np.empty(n, dtype=np.int64)
    n_tables = 0
    u = rng.random(n)
    for i in range(n):
        if u[i] < theta / (theta + i):
            assign[i] = n_tables
            n_tables += 1
        else:
            j = int(rng.integers(0, i))
            assign[i] = assign[j]
    return assign  # array of type-ids length n


def expected_V_crp(n, theta):
    """Exact E[V_n] for a CRP/Hoppe urn: sum_{i=0}^{n-1} theta/(theta+i)."""
    i = np.arange(n)
    return float(np.sum(theta / (theta + i)))


def fit_theta_for_V(n, target_V, lo=1e-4, hi=1e5, iters=60):
    """Root-find theta so that the exact expected V_n matches target_V."""
    for _ in range(iters):
        mid = math.sqrt(lo * hi)  # log-scale bisection
        v = expected_V_crp(n, mid)
        if v < target_V:
            lo = mid
        else:
            hi = mid
    return math.sqrt(lo * hi)


# --------------------------------------------------------- mechanism (iii) -
def zipf_weights(K, alpha):
    r = np.arange(1, K + 1, dtype=float)
    w = 1.0 / (r ** alpha)
    return w / w.sum()


def simulate_fixed_dictionary(n, K, alpha, rng):
    """i.i.d. multinomial draws (with replacement) from a FIXED, pre-set
    Zipfian-weighted dictionary of K types -- literal 'bounded finite stock'
    null: the scribe already has K templates in stock with fixed relative
    popularity, and every word is a resample (a 'copy') of one of them."""
    p = zipf_weights(K, alpha)
    idx = rng.choice(K, size=n, p=p)
    return idx


def fit_fixed_dictionary(n, target_V, target_slope, rng, K_grid=None, alpha_grid=None, reps=3):
    """Small grid search over (K, alpha) minimizing squared relative error to
    (target_V, target_slope), averaged over `reps` simulations per cell."""
    if K_grid is None:
        K_grid = [300, 500, 800, 1200, 1600, 2000, 2432, 3000]
    if alpha_grid is None:
        alpha_grid = [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
    best = None
    for K in K_grid:
        for alpha in alpha_grid:
            Vs, slopes = [], []
            for _ in range(reps):
                idx = simulate_fixed_dictionary(n, K, alpha, rng)
                c = collections.Counter(idx.tolist())
                V = len(c)
                freqs = np.array(sorted(c.values(), reverse=True), dtype=float)
                ranks = np.arange(1, V + 1)
                slope = float(np.polyfit(np.log(ranks), np.log(freqs), 1)[0])
                Vs.append(V); slopes.append(slope)
            Vm, Sm = np.mean(Vs), np.mean(slopes)
            err = ((Vm - target_V) / target_V) ** 2 + ((Sm - target_slope) / target_slope) ** 2
            if best is None or err < best[0]:
                best = (err, K, alpha, Vm, Sm)
    return dict(err=best[0], K=best[1], alpha=best[2], V_mean=best[3], slope_mean=best[4])
