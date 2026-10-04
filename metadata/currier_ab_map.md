# Currier A / B "language" labeling across the manuscript

_Structural classification (no semantics). Source: `doc_loci.txt` (H/Takahashi transcription); word forms and kclass from `KLASS_ASSIGNMENT.tsv`. Date: 2026-09-27._

## 0. Summary

- **225 leaf-sides** analyzed (recto/verso, including the foldouts f68/f85/f86).
- **Currier A: 151 sides** (67%), **Currier B: 74 sides** (33%).
- Tokens: A = 18,185, B = 23,140 (B pages are denser in text).
- The split is clean and reproduces the classic Currier diagnostics: the A core (`daiin/chol/chor`, endings -ol/-or) vs. the B core (`chedy/qokeedy/qokeey`, endings -edy/-eedy, prefix qo-).

## 1. Method and features

For each leaf-side a vector was built (fractions of the leaf token count):
- **B markers**: fraction of tokens ending in -dy / -edy / -eedy / -eey;
- **A markers**: fraction of tokens ending in -ol / -or / -aiin / -ain;
- **gallows rate**: fraction of tokens containing a gallows glyph (k t p f and the benched gallows cTh cKh cPh cFh);
- **qo rate**: fraction of tokens with the qo- prefix;
- **-edy : -aiin**: ratio of the count of -edy(+eedy) words to the count of -aiin words.

**Classifier (primary): 2-means (k=2)** on the standardized vector [B, A, gallows, qo, log(1+edy/aiin)]; the cluster with the higher mean B marker = B.
An anchor check confirmed the method: opening herbal (f1r–f3) → A, pharma (f88–f102) → A, biology (f75–f84) → B, recipes (f103–f116) → B.

> **Caveat.** The "naive" rule "B if B markers > A markers" is biased toward A, because -aiin/-ol/-or are frequent in BOTH languages (a single `daiin`/`ol` outweighs rare -edy). It yields 154 A / 71 B and misclassifies recipes. Hence 2-means is taken as primary; see §6.

## 2. Leaf → A/B table (all sides, in manuscript order)

`N` — tokens; `B`,`A` — marker fractions; `g` — gallows; `qo` — qo-; `e/a` — edy:aiin; `±` — B-index (>0 → toward B).

| folio | sect. | N | B | A | g | qo | e/a | ± | class |
|---|---|--:|--:|--:|--:|--:|--:|--:|:--:|
| f1r | herbal | 224 | 0.05 | 0.32 | 0.45 | 0.00 | 0.0 | -4.0 | **A** |
| f1v | herbal | 93 | 0.12 | 0.34 | 0.39 | 0.01 | 0.0 | -4.2 | **A** |
| f2r | herbal | 102 | 0.10 | 0.40 | 0.36 | 0.04 | 0.0 | -4.7 | **A** |
| f2v | herbal | 61 | 0.05 | 0.48 | 0.31 | 0.05 | 0.0 | -6.2 | **A** |
| f3r | herbal | 116 | 0.06 | 0.46 | 0.38 | 0.19 | 0.0 | -2.9 | **A** |
| f3v | herbal | 83 | 0.02 | 0.37 | 0.51 | 0.06 | 0.0 | -3.1 | **A** |
| f4r | herbal | 65 | 0.09 | 0.52 | 0.45 | 0.11 | 0.0 | -3.6 | **A** |
| f4v | herbal | 87 | 0.15 | 0.30 | 0.44 | 0.09 | 0.0 | -1.6 | **A** |
| f5r | herbal | 56 | 0.21 | 0.23 | 0.45 | 0.16 | 0.0 | +0.8 | **A** |
| f5v | herbal | 48 | 0.00 | 0.62 | 0.46 | 0.06 | 0.0 | -5.9 | **A** |
| f6r | herbal | 87 | 0.00 | 0.43 | 0.45 | 0.03 | 0.0 | -4.8 | **A** |
| f6v | herbal | 119 | 0.07 | 0.28 | 0.40 | 0.06 | 0.0 | -3.1 | **A** |
| f7r | herbal | 67 | 0.12 | 0.30 | 0.42 | 0.09 | 0.0 | -2.1 | **A** |
| f7v | herbal | 78 | 0.14 | 0.37 | 0.40 | 0.09 | 0.0 | -2.8 | **A** |
| f8r | herbal | 152 | 0.11 | 0.32 | 0.39 | 0.02 | 0.0 | -3.9 | **A** |
| f8v | herbal | 119 | 0.03 | 0.49 | 0.38 | 0.01 | 0.0 | -6.4 | **A** |
| f9r | herbal | 87 | 0.07 | 0.36 | 0.51 | 0.05 | 0.0 | -2.7 | **A** |
| f9v | herbal | 85 | 0.09 | 0.46 | 0.58 | 0.08 | 0.0 | -1.9 | **A** |
| f10r | herbal | 93 | 0.06 | 0.46 | 0.52 | 0.12 | 0.0 | -2.4 | **A** |
| f10v | herbal | 59 | 0.07 | 0.49 | 0.51 | 0.19 | 0.0 | -1.6 | **A** |
| f11r | herbal | 61 | 0.10 | 0.38 | 0.43 | 0.05 | 0.0 | -3.5 | **A** |
| f11v | herbal | 50 | 0.20 | 0.22 | 0.46 | 0.12 | 0.0 | +0.3 | **A** |
| f13r | herbal | 80 | 0.09 | 0.33 | 0.46 | 0.10 | 0.0 | -2.0 | **A** |
| f13v | herbal | 71 | 0.03 | 0.27 | 0.56 | 0.11 | 0.0 | -0.6 | **A** |
| f14r | herbal | 82 | 0.15 | 0.32 | 0.41 | 0.07 | 0.0 | -2.3 | **A** |
| f14v | herbal | 77 | 0.16 | 0.25 | 0.56 | 0.03 | 0.0 | -0.6 | **A** |
| f15r | herbal | 96 | 0.04 | 0.46 | 0.48 | 0.07 | 0.0 | -3.7 | **A** |
| f15v | herbal | 75 | 0.03 | 0.51 | 0.40 | 0.07 | 0.0 | -5.3 | **A** |
| f16r | herbal | 85 | 0.11 | 0.27 | 0.49 | 0.07 | 0.0 | -1.4 | **A** |
| f16v | herbal | 77 | 0.06 | 0.34 | 0.57 | 0.06 | 0.0 | -1.5 | **A** |
| f17r | herbal | 80 | 0.09 | 0.25 | 0.47 | 0.11 | 0.0 | -1.0 | **A** |
| f17v | herbal | 140 | 0.08 | 0.60 | 0.44 | 0.05 | 0.0 | -5.4 | **A** |
| f18r | herbal | 86 | 0.08 | 0.47 | 0.49 | 0.07 | 0.0 | -3.3 | **A** |
| f18v | herbal | 72 | 0.04 | 0.25 | 0.50 | 0.25 | 0.0 | +1.1 | **A** |
| f19r | herbal | 82 | 0.10 | 0.40 | 0.38 | 0.12 | 0.0 | -3.2 | **A** |
| f19v | herbal | 81 | 0.01 | 0.48 | 0.58 | 0.14 | 0.0 | -2.0 | **A** |
| f20r | herbal | 93 | 0.18 | 0.31 | 0.40 | 0.13 | 0.0 | -1.3 | **A** |
| f20v | herbal | 91 | 0.04 | 0.33 | 0.43 | 0.04 | 0.0 | -3.7 | **A** |
| f21r | herbal | 104 | 0.12 | 0.46 | 0.56 | 0.11 | 0.0 | -1.6 | **A** |
| f21v | herbal | 57 | 0.04 | 0.40 | 0.51 | 0.11 | 0.0 | -2.5 | **A** |
| f22r | herbal | 110 | 0.04 | 0.49 | 0.47 | 0.06 | 0.0 | -4.3 | **A** |
| f22v | herbal | 78 | 0.05 | 0.45 | 0.58 | 0.13 | 0.0 | -1.5 | **A** |
| f23r | herbal | 110 | 0.05 | 0.38 | 0.42 | 0.11 | 0.0 | -3.1 | **A** |
| f23v | herbal | 98 | 0.02 | 0.48 | 0.33 | 0.08 | 0.0 | -5.8 | **A** |
| f24r | herbal | 114 | 0.02 | 0.32 | 0.38 | 0.13 | 0.0 | -3.1 | **A** |
| f24v | herbal | 92 | 0.04 | 0.28 | 0.41 | 0.02 | 0.0 | -3.9 | **A** |
| f25r | herbal | 49 | 0.08 | 0.39 | 0.47 | 0.12 | 0.0 | -2.1 | **A** |
| f25v | herbal | 58 | 0.02 | 0.50 | 0.38 | 0.16 | 0.0 | -4.2 | **A** |
| f26r | herbal | 91 | 0.43 | 0.12 | 0.44 | 0.12 | 3.2 | +5.2 | **B** |
| f26v | herbal | 95 | 0.43 | 0.11 | 0.47 | 0.11 | 5.2 | +6.2 | **B** |
| f27r | herbal | 93 | 0.09 | 0.26 | 0.32 | 0.02 | 0.0 | -4.4 | **A** |
| f27v | herbal | 72 | 0.08 | 0.08 | 0.40 | 0.01 | 2.0 | -0.4 | **A** |
| f28r | herbal | 72 | 0.07 | 0.50 | 0.58 | 0.08 | 0.0 | -2.4 | **A** |
| f28v | herbal | 68 | 0.04 | 0.43 | 0.38 | 0.13 | 0.0 | -3.7 | **A** |
| f29r | herbal | 68 | 0.06 | 0.29 | 0.51 | 0.16 | 0.0 | -0.4 | **A** |
| f29v | herbal | 101 | 0.06 | 0.34 | 0.43 | 0.04 | 0.0 | -3.7 | **A** |
| f30r | herbal | 104 | 0.09 | 0.33 | 0.30 | 0.09 | 0.0 | -4.2 | **A** |
| f30v | herbal | 66 | 0.11 | 0.48 | 0.47 | 0.06 | 0.0 | -3.6 | **A** |
| f31r | herbal | 105 | 0.30 | 0.21 | 0.47 | 0.17 | 2.0 | +3.9 | **B** |
| f31v | herbal | 112 | 0.21 | 0.21 | 0.57 | 0.04 | 1.2 | +1.7 | **B** |
| f32r | herbal | 80 | 0.05 | 0.46 | 0.39 | 0.11 | 0.1 | -4.0 | **A** |
| f32v | herbal | 88 | 0.02 | 0.48 | 0.34 | 0.06 | 0.0 | -6.0 | **A** |
| f33r | herbal | 76 | 0.26 | 0.33 | 0.57 | 0.08 | 0.5 | +1.2 | **A** |
| f33v | herbal | 117 | 0.30 | 0.22 | 0.38 | 0.01 | 0.6 | -0.8 | **A** |
| f34r | herbal | 152 | 0.22 | 0.14 | 0.50 | 0.09 | 2.0 | +2.7 | **B** |
| f34v | herbal | 124 | 0.32 | 0.20 | 0.44 | 0.08 | 1.4 | +2.0 | **B** |
| f35r | herbal | 94 | 0.07 | 0.49 | 0.38 | 0.10 | 0.0 | -4.5 | **A** |
| f35v | herbal | 90 | 0.03 | 0.40 | 0.42 | 0.06 | 0.0 | -4.3 | **A** |
| f36r | herbal | 64 | 0.05 | 0.41 | 0.44 | 0.11 | 0.0 | -3.2 | **A** |
| f36v | herbal | 75 | 0.03 | 0.39 | 0.63 | 0.08 | 0.0 | -1.4 | **A** |
| f37r | herbal | 81 | 0.09 | 0.51 | 0.49 | 0.17 | 0.0 | -1.9 | **A** |
| f37v | herbal | 89 | 0.07 | 0.54 | 0.46 | 0.12 | 0.0 | -3.6 | **A** |
| f38r | herbal | 42 | 0.07 | 0.43 | 0.57 | 0.05 | 0.0 | -2.5 | **A** |
| f38v | herbal | 65 | 0.17 | 0.40 | 0.34 | 0.06 | 0.0 | -3.9 | **A** |
| f39r | herbal | 167 | 0.23 | 0.27 | 0.39 | 0.08 | 0.7 | -0.5 | **A** |
| f39v | herbal | 151 | 0.19 | 0.34 | 0.46 | 0.05 | 0.6 | -1.0 | **A** |
| f40r | herbal | 100 | 0.18 | 0.30 | 0.52 | 0.08 | 0.4 | +0.0 | **A** |
| f40v | herbal | 107 | 0.24 | 0.33 | 0.57 | 0.15 | 0.8 | +2.5 | **B** |
| f41r | herbal | 104 | 0.49 | 0.04 | 0.66 | 0.18 | 34.0 | +13.5 | **B** |
| f41v | herbal | 70 | 0.33 | 0.29 | 0.59 | 0.11 | 1.3 | +3.7 | **B** |
| f42r | herbal | 146 | 0.05 | 0.45 | 0.42 | 0.03 | 0.0 | -4.9 | **A** |
| f42v | herbal | 119 | 0.08 | 0.29 | 0.45 | 0.05 | 0.0 | -2.8 | **A** |
| f43r | herbal | 161 | 0.38 | 0.18 | 0.55 | 0.10 | 2.5 | +5.0 | **B** |
| f43v | herbal | 166 | 0.34 | 0.14 | 0.53 | 0.06 | 3.1 | +4.3 | **B** |
| f44r | herbal | 81 | 0.07 | 0.21 | 0.58 | 0.15 | 0.0 | +1.1 | **A** |
| f44v | herbal | 102 | 0.06 | 0.47 | 0.60 | 0.06 | 0.0 | -2.4 | **A** |
| f45r | herbal | 92 | 0.07 | 0.37 | 0.52 | 0.11 | 0.0 | -1.7 | **A** |
| f45v | herbal | 90 | 0.07 | 0.31 | 0.50 | 0.08 | 0.0 | -1.9 | **A** |
| f46r | herbal | 169 | 0.26 | 0.20 | 0.48 | 0.08 | 1.1 | +1.8 | **B** |
| f46v | herbal | 120 | 0.35 | 0.12 | 0.47 | 0.07 | 2.5 | +3.8 | **B** |
| f47r | herbal | 86 | 0.05 | 0.44 | 0.34 | 0.02 | 0.0 | -6.1 | **A** |
| f47v | herbal | 89 | 0.11 | 0.25 | 0.33 | 0.03 | 0.0 | -3.8 | **A** |
| f48r | herbal | 100 | 0.26 | 0.26 | 0.64 | 0.08 | 1.1 | +3.2 | **B** |
| f48v | herbal | 130 | 0.36 | 0.15 | 0.60 | 0.02 | 8.3 | +6.0 | **B** |
| f49r | herbal | 121 | 0.08 | 0.42 | 0.31 | 0.12 | 0.0 | -4.2 | **A** |
| f49v | herbal | 175 | 0.06 | 0.33 | 0.40 | 0.06 | 0.0 | -3.5 | **A** |
| f50r | herbal | 105 | 0.22 | 0.22 | 0.59 | 0.11 | 0.7 | +2.8 | **B** |
| f50v | herbal | 106 | 0.27 | 0.24 | 0.60 | 0.10 | 1.0 | +3.4 | **B** |
| f51r | herbal | 92 | 0.16 | 0.34 | 0.61 | 0.15 | 0.1 | +1.4 | **A** |
| f51v | herbal | 83 | 0.19 | 0.40 | 0.55 | 0.19 | 0.0 | +1.0 | **A** |
| f52r | herbal | 73 | 0.12 | 0.18 | 0.55 | 0.12 | 0.0 | +1.0 | **A** |
| f52v | herbal | 81 | 0.12 | 0.49 | 0.53 | 0.07 | 0.0 | -2.6 | **A** |
| f53r | herbal | 62 | 0.08 | 0.18 | 0.61 | 0.13 | 0.0 | +1.5 | **A** |
| f53v | herbal | 75 | 0.20 | 0.35 | 0.49 | 0.11 | 0.0 | -0.6 | **A** |
| f54r | herbal | 115 | 0.07 | 0.41 | 0.40 | 0.03 | 0.0 | -4.8 | **A** |
| f54v | herbal | 95 | 0.09 | 0.34 | 0.43 | 0.15 | 0.0 | -1.6 | **A** |
| f55r | herbal | 130 | 0.15 | 0.29 | 0.48 | 0.08 | 0.3 | -0.6 | **A** |
| f55v | herbal | 109 | 0.17 | 0.36 | 0.47 | 0.07 | 0.2 | -1.6 | **A** |
| f56r | herbal | 106 | 0.12 | 0.29 | 0.54 | 0.06 | 0.1 | -0.9 | **A** |
| f56v | herbal | 90 | 0.13 | 0.47 | 0.53 | 0.10 | 0.0 | -1.8 | **A** |
| f57r | herbal | 94 | 0.32 | 0.04 | 0.52 | 0.06 | 2.5 | +4.7 | **B** |
| f57v | herbal | 185 | 0.02 | 0.07 | 0.33 | 0.01 | 0.0 | -3.6 | **A** |
| f58r | herbal | 380 | 0.09 | 0.21 | 0.47 | 0.07 | 0.1 | -1.1 | **A** |
| f58v | herbal | 387 | 0.08 | 0.24 | 0.58 | 0.19 | 0.1 | +1.6 | **A** |
| f65r | herbal | 3 | 0.00 | 0.00 | 0.33 | 0.00 | 0.0 | -3.2 | **A** |
| f65v | herbal | 46 | 0.35 | 0.09 | 0.65 | 0.11 | 4.0 | +7.4 | **B** |
| f66r | herbal | 358 | 0.26 | 0.18 | 0.50 | 0.13 | 2.2 | +3.6 | **B** |
| f66v | herbal | 120 | 0.24 | 0.12 | 0.62 | 0.07 | 1.0 | +3.7 | **B** |
| f67r1 | astro | 165 | 0.15 | 0.16 | 0.45 | 0.01 | 0.3 | -1.1 | **A** |
| f67r2 | astro | 193 | 0.11 | 0.24 | 0.40 | 0.04 | 0.0 | -2.7 | **A** |
| f67v1 | astro | 85 | 0.19 | 0.14 | 0.46 | 0.04 | 0.0 | -0.5 | **A** |
| f67v2 | astro | 64 | 0.06 | 0.27 | 0.47 | 0.02 | 0.0 | -3.0 | **A** |
| f68r1 | astro | 71 | 0.27 | 0.24 | 0.70 | 0.03 | 3.0 | +4.4 | **B** |
| f68r2 | astro | 89 | 0.07 | 0.28 | 0.51 | 0.07 | 0.0 | -1.8 | **A** |
| f68r3 | astro | 113 | 0.22 | 0.19 | 0.52 | 0.08 | 0.8 | +1.8 | **B** |
| f68v1 | astro | 103 | 0.20 | 0.15 | 0.48 | 0.00 | 0.2 | -0.4 | **A** |
| f68v2 | astro | 111 | 0.32 | 0.08 | 0.52 | 0.05 | 0.4 | +2.6 | **B** |
| f68v3 | astro | 170 | 0.18 | 0.26 | 0.55 | 0.06 | 0.4 | +0.5 | **A** |
| f69r | astro | 185 | 0.10 | 0.11 | 0.42 | 0.02 | 0.1 | -1.8 | **A** |
| f69v | astro | 147 | 0.19 | 0.07 | 0.47 | 0.01 | 0.5 | +0.5 | **A** |
| f70r1 | astro | 125 | 0.18 | 0.10 | 0.52 | 0.01 | 1.0 | +1.1 | **A** |
| f70r2 | astro | 272 | 0.11 | 0.12 | 0.41 | 0.02 | 0.4 | -1.4 | **A** |
| f70v1 | astro | 95 | 0.17 | 0.15 | 0.53 | 0.01 | 0.1 | -0.2 | **A** |
| f70v2 | astro | 152 | 0.13 | 0.14 | 0.53 | 0.01 | 0.3 | -0.3 | **A** |
| f71r | astro | 100 | 0.18 | 0.14 | 0.67 | 0.00 | 0.5 | +2.0 | **A** |
| f71v | astro | 102 | 0.18 | 0.25 | 0.59 | 0.00 | 0.0 | -0.5 | **A** |
| f72r1 | astro | 114 | 0.08 | 0.27 | 0.53 | 0.01 | 0.2 | -2.0 | **A** |
| f72r2 | astro | 118 | 0.13 | 0.17 | 0.58 | 0.03 | 0.0 | +0.0 | **A** |
| f72r3 | astro | 182 | 0.16 | 0.25 | 0.45 | 0.00 | 0.3 | -1.9 | **A** |
| f72v1 | astro | 113 | 0.15 | 0.12 | 0.61 | 0.00 | 0.6 | +1.3 | **A** |
| f72v2 | astro | 121 | 0.15 | 0.18 | 0.57 | 0.01 | 0.6 | +0.4 | **A** |
| f72v3 | astro | 129 | 0.18 | 0.16 | 0.56 | 0.00 | 0.7 | +0.7 | **A** |
| f73r | astro | 103 | 0.18 | 0.10 | 0.55 | 0.01 | 0.5 | +1.2 | **A** |
| f73v | astro | 102 | 0.25 | 0.14 | 0.64 | 0.07 | 1.4 | +4.2 | **B** |
| f75r | bio | 488 | 0.30 | 0.16 | 0.43 | 0.22 | 18.0 | +7.5 | **B** |
| f75v | bio | 414 | 0.27 | 0.20 | 0.41 | 0.23 | 10.6 | +6.0 | **B** |
| f76r | bio | 647 | 0.26 | 0.17 | 0.36 | 0.17 | 4.3 | +3.4 | **B** |
| f76v | bio | 433 | 0.41 | 0.18 | 0.45 | 0.16 | 4.2 | +5.7 | **B** |
| f77r | bio | 347 | 0.38 | 0.31 | 0.41 | 0.31 | 2.4 | +5.6 | **B** |
| f77v | bio | 362 | 0.34 | 0.25 | 0.36 | 0.27 | 3.7 | +4.8 | **B** |
| f78r | bio | 325 | 0.36 | 0.27 | 0.52 | 0.18 | 5.1 | +5.9 | **B** |
| f78v | bio | 324 | 0.35 | 0.28 | 0.40 | 0.18 | 9.8 | +5.0 | **B** |
| f79r | bio | 444 | 0.23 | 0.23 | 0.41 | 0.18 | 2.7 | +2.7 | **B** |
| f79v | bio | 426 | 0.31 | 0.20 | 0.50 | 0.21 | 5.8 | +6.5 | **B** |
| f80r | bio | 539 | 0.14 | 0.20 | 0.52 | 0.20 | 2.2 | +3.7 | **B** |
| f80v | bio | 458 | 0.18 | 0.25 | 0.46 | 0.21 | 2.6 | +3.1 | **B** |
| f81r | bio | 239 | 0.31 | 0.24 | 0.37 | 0.16 | 9.8 | +4.3 | **B** |
| f81v | bio | 297 | 0.30 | 0.23 | 0.44 | 0.14 | 3.6 | +3.6 | **B** |
| f82r | bio | 321 | 0.37 | 0.24 | 0.44 | 0.27 | 2.6 | +5.8 | **B** |
| f82v | bio | 382 | 0.25 | 0.20 | 0.48 | 0.25 | 4.6 | +5.9 | **B** |
| f83r | bio | 387 | 0.38 | 0.18 | 0.44 | 0.20 | 4.1 | +5.9 | **B** |
| f83v | bio | 286 | 0.29 | 0.23 | 0.43 | 0.29 | 3.0 | +5.5 | **B** |
| f84r | bio | 402 | 0.36 | 0.20 | 0.49 | 0.18 | 7.5 | +6.5 | **B** |
| f84v | bio | 376 | 0.39 | 0.24 | 0.47 | 0.16 | 5.8 | +5.7 | **B** |
| f85r1 | rosettes | 350 | 0.32 | 0.23 | 0.51 | 0.12 | 1.4 | +3.3 | **B** |
| f85r2 | rosettes | 167 | 0.24 | 0.31 | 0.40 | 0.13 | 1.1 | +0.5 | **B** |
| f86v3 | rosettes | 296 | 0.32 | 0.27 | 0.51 | 0.15 | 0.7 | +2.9 | **B** |
| f86v4 | rosettes | 203 | 0.23 | 0.29 | 0.35 | 0.07 | 1.1 | -0.9 | **A** |
| f86v5 | rosettes | 402 | 0.17 | 0.27 | 0.57 | 0.09 | 0.2 | +0.8 | **A** |
| f86v6 | rosettes | 507 | 0.16 | 0.28 | 0.55 | 0.17 | 0.5 | +2.0 | **B** |
| f87r | pharma | 104 | 0.15 | 0.32 | 0.49 | 0.04 | 0.1 | -1.8 | **A** |
| f87v | pharma | 102 | 0.10 | 0.23 | 0.45 | 0.09 | 0.0 | -1.4 | **A** |
| f88r | pharma | 153 | 0.09 | 0.45 | 0.39 | 0.11 | 0.0 | -3.7 | **A** |
| f88v | pharma | 159 | 0.23 | 0.28 | 0.45 | 0.14 | 0.2 | +0.5 | **A** |
| f89r1 | pharma | 155 | 0.14 | 0.28 | 0.32 | 0.14 | 0.2 | -2.1 | **A** |
| f89r2 | pharma | 264 | 0.15 | 0.38 | 0.34 | 0.11 | 0.1 | -3.1 | **A** |
| f89v1 | pharma | 170 | 0.13 | 0.37 | 0.45 | 0.11 | 0.0 | -2.0 | **A** |
| f89v2 | pharma | 200 | 0.09 | 0.26 | 0.35 | 0.07 | 0.0 | -3.1 | **A** |
| f90r1 | pharma | 73 | 0.10 | 0.36 | 0.63 | 0.23 | 0.0 | +2.0 | **A** |
| f90r2 | pharma | 51 | 0.10 | 0.37 | 0.35 | 0.16 | 0.0 | -2.7 | **A** |
| f90v1 | pharma | 101 | 0.17 | 0.38 | 0.49 | 0.09 | 0.0 | -1.5 | **A** |
| f90v2 | pharma | 73 | 0.18 | 0.25 | 0.37 | 0.10 | 0.0 | -1.6 | **A** |
| f93r | pharma | 178 | 0.08 | 0.33 | 0.37 | 0.05 | 0.0 | -3.9 | **A** |
| f93v | pharma | 92 | 0.18 | 0.27 | 0.54 | 0.13 | 0.0 | +0.9 | **A** |
| f94r | pharma | 86 | 0.21 | 0.26 | 0.55 | 0.12 | 0.5 | +1.7 | **B** |
| f94v | pharma | 105 | 0.28 | 0.22 | 0.60 | 0.12 | 1.1 | +3.9 | **B** |
| f95r1 | pharma | 108 | 0.27 | 0.35 | 0.56 | 0.13 | 0.5 | +1.9 | **B** |
| f95r2 | pharma | 86 | 0.22 | 0.30 | 0.57 | 0.12 | 1.0 | +2.1 | **B** |
| f95v1 | pharma | 131 | 0.22 | 0.19 | 0.60 | 0.13 | 0.8 | +3.4 | **B** |
| f95v2 | pharma | 81 | 0.17 | 0.20 | 0.43 | 0.07 | 0.2 | -0.6 | **A** |
| f96r | pharma | 93 | 0.14 | 0.45 | 0.48 | 0.06 | 0.0 | -2.8 | **A** |
| f96v | pharma | 64 | 0.11 | 0.23 | 0.45 | 0.03 | 0.0 | -2.2 | **A** |
| f99r | pharma | 206 | 0.15 | 0.37 | 0.54 | 0.08 | 0.0 | -1.1 | **A** |
| f99v | pharma | 184 | 0.12 | 0.45 | 0.55 | 0.15 | 0.1 | -0.7 | **A** |
| f100r | pharma | 127 | 0.13 | 0.40 | 0.40 | 0.09 | 0.0 | -3.0 | **A** |
| f100v | pharma | 97 | 0.12 | 0.37 | 0.46 | 0.07 | 0.0 | -2.4 | **A** |
| f101r1 | pharma | 219 | 0.09 | 0.51 | 0.42 | 0.05 | 0.0 | -4.8 | **A** |
| f101v2 | pharma | 237 | 0.14 | 0.42 | 0.35 | 0.08 | 0.0 | -3.8 | **A** |
| f102r1 | pharma | 116 | 0.18 | 0.46 | 0.42 | 0.13 | 0.1 | -2.1 | **A** |
| f102r2 | pharma | 143 | 0.17 | 0.34 | 0.48 | 0.11 | 0.0 | -0.9 | **A** |
| f102v1 | pharma | 138 | 0.20 | 0.36 | 0.43 | 0.15 | 0.0 | -0.7 | **A** |
| f102v2 | pharma | 198 | 0.17 | 0.31 | 0.44 | 0.08 | 0.0 | -1.7 | **A** |
| f103r | recipes | 576 | 0.30 | 0.16 | 0.55 | 0.20 | 3.4 | +6.4 | **B** |
| f103v | recipes | 495 | 0.27 | 0.15 | 0.47 | 0.15 | 2.4 | +4.0 | **B** |
| f104r | recipes | 466 | 0.21 | 0.24 | 0.53 | 0.20 | 0.7 | +3.0 | **B** |
| f104v | recipes | 483 | 0.26 | 0.26 | 0.43 | 0.22 | 1.1 | +2.8 | **B** |
| f105r | recipes | 381 | 0.35 | 0.20 | 0.51 | 0.12 | 1.4 | +3.8 | **B** |
| f105v | recipes | 405 | 0.19 | 0.31 | 0.52 | 0.08 | 0.4 | -0.1 | **A** |
| f106r | recipes | 456 | 0.23 | 0.27 | 0.50 | 0.15 | 1.1 | +2.2 | **B** |
| f106v | recipes | 505 | 0.24 | 0.22 | 0.46 | 0.13 | 0.8 | +1.8 | **B** |
| f107r | recipes | 534 | 0.17 | 0.27 | 0.54 | 0.12 | 0.4 | +1.0 | **A** |
| f107v | recipes | 510 | 0.20 | 0.29 | 0.61 | 0.17 | 0.5 | +3.0 | **B** |
| f108r | recipes | 529 | 0.38 | 0.15 | 0.60 | 0.18 | 3.8 | +7.6 | **B** |
| f108v | recipes | 631 | 0.33 | 0.18 | 0.49 | 0.19 | 2.4 | +5.2 | **B** |
| f111r | recipes | 685 | 0.32 | 0.12 | 0.52 | 0.15 | 3.0 | +5.4 | **B** |
| f111v | recipes | 699 | 0.17 | 0.12 | 0.45 | 0.14 | 1.7 | +2.5 | **B** |
| f112r | recipes | 436 | 0.34 | 0.16 | 0.52 | 0.14 | 2.6 | +5.1 | **B** |
| f112v | recipes | 476 | 0.26 | 0.23 | 0.47 | 0.15 | 1.3 | +2.6 | **B** |
| f113r | recipes | 565 | 0.21 | 0.27 | 0.52 | 0.12 | 0.7 | +1.5 | **B** |
| f113v | recipes | 516 | 0.20 | 0.30 | 0.59 | 0.11 | 0.6 | +1.8 | **A** |
| f114r | recipes | 493 | 0.22 | 0.26 | 0.42 | 0.14 | 0.7 | +0.8 | **B** |
| f114v | recipes | 400 | 0.24 | 0.24 | 0.52 | 0.21 | 0.8 | +3.6 | **B** |
| f115r | recipes | 498 | 0.25 | 0.21 | 0.41 | 0.22 | 2.1 | +3.5 | **B** |
| f115v | recipes | 458 | 0.26 | 0.15 | 0.50 | 0.16 | 2.8 | +4.6 | **B** |
| f116r | recipes | 633 | 0.19 | 0.11 | 0.40 | 0.13 | 4.1 | +3.1 | **B** |

## 3. Section composition A vs B

| section | leaves | A | B | majority |
|---|--:|--:|--:|:--:|
| herbal | 118 | 97 | 21 | **A** |
| astro | 26 | 22 | 4 | **A** |
| bio | 20 | 0 | 20 | **B** |
| rosettes | 6 | 2 | 4 | **B** |
| pharma | 32 | 27 | 5 | **A** |
| recipes | 23 | 3 | 20 | **B** |
| **TOTAL** | 225 | 151 | 74 | — |

The herbal sections are taken by leaf numbering (n≤66); the real herbal is mixed — see §5. Astro/zodiac is the most disputed section (many borderline pages, little running text, labels dominate).

## 4a. kclass distribution (token fraction, A vs B)

| kclass | sense profile (from KLASS.md) | A % | B % | B/A |
|--:|---|--:|--:|--:|
| -1 | rare/unassigned | 32.9 | 24.8 | 0.75 |
| 0 | oteedy/olchedy (B recipe) | 1.8 | 4.0 | 2.22 |
| 1 |  | 1.5 | 1.2 | 0.79 |
| 2 | chey/qokeey/cheey (B) | 4.9 | 15.8 | 3.26 |
| 3 |  | 1.4 | 1.3 | 0.92 |
| 4 | daiin/chol/chor/Shol (A core) | 14.9 | 4.7 | 0.31 |
| 5 | okeol/chodaiin (A) | 2.6 | 1.1 | 0.44 |
| 6 |  | 1.1 | 1.6 | 1.50 |
| 7 | tol/choky/odar (A) | 1.6 | 0.8 | 0.47 |
| 8 |  | 3.7 | 3.0 | 0.80 |
| 9 | chedy/Shedy/qokeedy/qokedy (B core) | 1.9 | 14.1 | 7.25 |
| 10 |  | 1.5 | 2.0 | 1.36 |
| 11 |  | 1.5 | 1.7 | 1.10 |
| 12 |  | 1.7 | 1.6 | 0.95 |
| 13 |  | 0.9 | 0.6 | 0.64 |
| 14 | ol/aiin/or/ar function words | 14.4 | 13.4 | 0.93 |
| 15 | chear/cThor/kor (A) | 1.4 | 0.3 | 0.25 |
| 16 | oty/sar/tar (A) | 2.5 | 1.6 | 0.63 |
| 17 | Shor/otol/qotal (A) | 2.2 | 1.3 | 0.57 |
| 18 |  | 1.7 | 2.2 | 1.29 |
| 19 | single glyphs y/r/l | 3.6 | 2.8 | 0.79 |
| ? |  | 0.3 | 0.0 | 0.11 |

**What dominates:**
- **A:** kclass 4 (`daiin/chol/chor/Shol/dol` — A core) — 14.9% vs. 4.7% in B (B/A=0.31); plus an A tilt at 5,7,15,16,17 (`okeol, tol, chear, oty, Shor/otol`).
- **B:** kclass 9 (`chedy/Shedy/qokeedy/qokedy/otedy` — B core) — 14.1% vs. 1.9% (**B/A=7.25**); kclass 2 (`chey/qokeey/cheey/okeey`) — 15.8% vs. 4.9% (B/A=3.26); kclass 0 (`oteedy/olchedy`) B/A=2.22.
- The function-word kclass 14 (`ol/aiin/or/ar/s`) is nearly identical (14.4% vs 13.4%) — as expected for particles.

## 4b. Ending inventory (token fraction)

| | top endings |
|--|--|
| **A** | -y 14.7%, -ol 11.4%, -aiin 10.8%, -or 8.2%, -dy 6.8%, -ar 6.4%, -∅ 5.4%, -s 5.3%, -o 5.2%, -al 5.0%, -ey 4.5%, -eey 3.7% |
| **B** | -edy 11.7%, -y 9.6%, -aiin 8.0%, -ol 7.7%, -∅ 7.2%, -ar 6.7%, -dy 6.1%, -ey 5.5%, -al 5.5%, -eey 5.2%, -eedy 4.8%, -n 4.8% |

Key shift: in A the first content ending is **-ol (11.4%)**, then -aiin, -or; in B the first is **-edy (11.7%)** and -eedy appears (4.8%), which is absent from the A top list. Prefixes: **qo- 4.2% (A) → 11.2% (B)**, and in B Sh-, che-, qok- also rise.

## 4c. Diagnostic-word frequencies (per 1000 tokens)

| word | A | B | | word | A | B |
|--|--:|--:|--|--|--:|--:|
| chol | 17.6 | 4.8 | | chedy | 2.1 | 22.6 |
| chor | 11.2 | 1.3 | | Shedy | 1.2 | 18.8 |
| daiin | 34.1 | 12.4 | | qokeedy | 0.4 | 12.7 |
| dair | 3.6 | 2.2 | | qokedy | 0.3 | 11.5 |
| dar | 9.3 | 7.7 | | qokeey | 2.5 | 11.4 |
| ol | 10.2 | 21.0 | | qokaiin | 3.0 | 9.0 |
| or | 11.2 | 10.5 | | dy | 12.8 | 5.9 |
| aiin | 13.6 | 13.5 | | dair | 3.6 | 2.2 |

A words (`chol` 17.6→4.8, `chor` 11.2→1.3, `daiin` 34→12) fall sharply in B; B words (`chedy` 2.1→22.6, `Shedy` 1.2→18.8, `qokeedy` 0.4→12.7, `qokedy` 0.3→11.5) mirror this.

## 5. Where A and B physically sit

Blocks (run-length) in manuscript order:

```
A ×48      f1r .. f25v   
B × 2     f26r .. f26v   
A × 8     f27r .. f30v   
B × 2     f31r .. f31v   
A × 4     f32r .. f33v   
B × 2     f34r .. f34v   
A ×11     f35r .. f40r   
B × 3     f40v .. f41v   
A × 2     f42r .. f42v   
B × 2     f43r .. f43v   
A × 4     f44r .. f45v   
B × 2     f46r .. f46v   
A × 2     f47r .. f47v   
B × 2     f48r .. f48v   
A × 2     f49r .. f49v   
B × 2     f50r .. f50v   
A ×12     f51r .. f56v   
B × 1     f57r .. f57r   
A × 4     f57v .. f65r   
B × 3     f65v .. f66v   
A × 4    f67r1 .. f67v2  
B × 1    f68r1 .. f68r1  
A × 1    f68r2 .. f68r2  
B × 1    f68r3 .. f68r3  
A × 1    f68v1 .. f68v1  
B × 1    f68v2 .. f68v2  
A ×16    f68v3 .. f73r   
B ×24     f73v .. f86v3  
A × 2    f86v4 .. f86v5  
B × 1    f86v6 .. f86v6  
A ×14     f87r .. f93v   
B × 5     f94r .. f95v1  
A ×13    f95v2 .. f102v2 
B × 5    f103r .. f105r  
A × 1    f105v .. f105v  
B × 2    f106r .. f106v  
A × 1    f107r .. f107r  
B × 8    f107v .. f113r  
A × 1    f113v .. f113v  
B × 5    f114r .. f116r  
```

**Observations:**
- **Herbal (f1–66) — interleaved.** A long A block f1r–f25v (quires 1–3), then A and B alternate in short 2-side blocks — the classic "Herbal-A" and "Herbal-B" bifolios mixed within quires. Herbal-B sides: f26, f31, f34, f40v–f41, f43, f46, f48, f50, f57r, f65v–f66.
- **Cosmology + biology (f73v–f86, quire 13) — solid B** (the longest B run, 24 sides). This is the core of "language B".
- **Pharma (f87–f102) — solid A** (with one B inclusion f94–f95).
- **Recipes (f103–f116) — solid B**, three A anomalies (f105v, f107r, f113v).
- **Astro/zodiac (f67–f73r) — a borderline zone:** many pages with |B-index|≈0, the method is unstable (2-means on 4 vs 5 features diverges precisely here). Treat the astro labeling as indicative.
- Bottom line: A and B are **not randomly interleaved** — within sections they are homogeneous (pharma=A, biology=B, recipes=B), and the mixing is concentrated in the herbal (bifolios of different scribes) and in the transitional astro section.

## 6. Methodological caveats

- The primary classifier is 2-means (5 features). The "naive" marker count yields 154 A / 71 B and wrongly assigns recipes to A because of the high base frequency of -aiin/-ol; the two methods disagree on 42 leaves (mostly astro and the borderline herbal).
- The B-index (± in the table) is a continuous confidence measure; leaves with |±|<0.5 are borderline (f72r2, f40r, f105v, f70v1/2, f11v, f68v1/3, f69v etc.), almost all astro.
- Foldout sides (f68*, f85*, f86*) contain little connected text → classification relies on labels and is less reliable.
- No semantics: classes, endings and prefixes are purely formal (morphology and distribution), without translations.
