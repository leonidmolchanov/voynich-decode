# Reported measurements and interpretation

These notes document project results cited in the accompanying article. Except
for the two corrections and 19-cell sample, the underlying datasets and complete
experiments are not distributed here. Report names identify the private research
archive; the [artifact register](FUTURE_RELEASE.md) records selected file hashes.
This is not a claim that the full study can be reproduced from this repository.

## Manuscript and exploratory diagram tests

The reported radiocarbon interval, 1404–1438, dates the parchment rather than the
application of ink. See [the 2011 University of Arizona report](https://phys.org/news/2011-02-experts-age.html)
and [Yale's manuscript description](https://beinecke.library.yale.edu/beinecke/collections/beinecke-cipher-voynich-manuscript).

Zodiac panels f70v–f73v, the 28-position diagram f69v and the rings on f57v are
different objects. The Aries panel f71r contains fifteen figures. The general
iconography and divided Aries/Taurus sequence predate this project; see
[Rene Zandbergen](https://www.voynich.nu/illustr.html).

The zodiac re-audit recorded 299 labels, 290 readable. On most panels, 93–100%
of complete labels were unique. Earlier comparisons had conflated full labels
with their components. The f69v set contained 28 positions and 25 distinct compact
labels. No exact transferable historical diagram was found within the searched
collection; this negative result is limited to that search.

Lunar-mansion name order gave discovery rho = 0.2620, max-T p = 0.1046 across
56 orientations. Rotation 25, direction +1, fixed for an independent Latin list,
gave rho = -0.00144, p = 0.4987; the sign was positive in 3/7 jackknife blocks.
The repeated label `okeod` at positions 11/15/24 would require Nathra/Sarfa/Balda
under that candidate mapping. This does not support a one-label/one-name dictionary;
it does not exclude every contextual cipher.

The historical reference was *Picatrix*, Latin edition by David Pingree (1986),
I.iv.2–29 and IV.ix.29–56: [Warburg copy](https://resources.warburg.sas.ac.uk/pdf/fbh295b2205454.pdf).
Properties/actions gave fixed rho = 0.0172, p = 0.4151; the best of 336 traversals
gave max-T p = 0.4469. Mansion-lord names retained 27/28 records: fixed
rho = -0.0541, p = 0.7724; best-of-336 max-T p = 0.1646. Neither met the
predeclared key criterion.

A specific 28-letter to 17-rasm-form mapping gave unadjusted p = 0.00033 but
max-T p = 0.1788 after accounting for tested rotations, reflections and mappings.
These are tail frequencies under the specified controls, not probabilities that
a hypothesis is false. Transfer from f57v to f67v1 did not outperform its control.
Selected masked-image/label tests gave p values from 0.9766 to 1; that particular
negative result does not exclude every relationship between images and labels.

## Line boundaries

`LINE_BOUNDARY_RESET_V2` matched 3,884 pairs in each of three positions:
line end, cross-line boundary and next-line start. About 5.4% of the measured
within-line excess mutual information remained across the boundary; the relevant
permutation test gave p = 0.000999. This is not a claim that 94.6% of all
information in the manuscript disappears at a line break.

For discrete variables, I(X;Y) = sum p(x,y) log2[p(x,y)/(p(x)p(y))]. Excess MI
subtracts the mean MI of the composition-preserving control.

## Internal forms, templates and states

The preliminary layer contains 23,859 cells and 1,819 distinct internal forms.
An edit-graph edge represents one insertion, deletion or substitution. An
insertion-only chain has counts: empty (2,323), `o` (1,781), `ok` (213),
`oke` (138), `okee` (326), `okeed` (303). Total: 5,107/23,859 = 21.40%.
The corresponding historical strict subset retains 4,292–4,293 occurrences.
An empty internal form does not mean a blank area on the manuscript.

The five-slot v2 template, with 27 primitive choices, covers 20,243/21,536 = 94.0%
of nonempty mass, or 96.8% in its historical strict subset. Broader v3 coverage
is 97.9% and 99.6%, respectively. These are descriptive coverage results, not
translation rates or blind predictions on new folios. Do not substitute a later
strict release for the subset used in that experiment.

Random strings preserving length and sign frequency gave comparable or greater
graph connectivity. Connectivity is therefore not counted as evidence of
generation. Real adjacent internal forms had 2.24% lower mean edit distance than
the shuffled control. One-edit pairs were 16.54% versus 15.99%. The small effect
does not establish that the whole manuscript was copied word by word.

In the referenced current mapping, S8 is final `y` and S4 final `l`. Their full-layer
shares are 49.3% and 16.0%; an atlas sample of 107 pages gives 39.6% and 14.6%.
S8-to-S4 and S4-to-S8 account for 4.9% and 4.8% of atlas transitions. State numbers
changed between versions, so an earlier S4 is not automatically the current S4.
Adjacent-state MI is 0.071 bits, or 3.3% of H1. These numbers do not establish
one obligatory state sequence or a unique historical algorithm.

## Corrections, segmentation and validation

The full decision register contains 54 decisions: 13 source corrections,
27 aligned-reference corrections, seven noncore visual resolutions and seven
unresolved ambiguities. This repository exposes two source corrections:
`checthy` to `checkhy` (high confidence) and `ykeol` to `yteol` (medium_high).
The original ZL3b is retained; corrections are an overlay with source, overlay
and output hashes. The separate 1,910 analytical-surface restorations must not
be described as 1,910 corrected manuscript signs.

Segmentation allowed 1:1, 2:1 and 1:2 mappings, omissions, insertions and a
`<DOUBLE_SPACE>` path. The frozen final set contained no literal `<DOUBLE_SPACE>`
events. Errors concerned empty cells and boundaries in the modern representation.
For f49v.19:0, a true empty cell was rejected, but the o/qo boundary remained open.

Splits were by physical leaf: an out-of-fold prediction came from a model not
trained on that leaf. X-v10D reported 52,310/52,310 correct calls across five
frozen splits. Dependence between repetitions prevents treating this count as
an unconditional probability of error-free reading of the entire manuscript.
After predictions were locked, the residual scorer gave 1,910/1,926; sixteen
disagreements were excluded. This is not external replication.

Historical strict v21, accepted on 1 October 2026, contains 22,106/23,859 cells
(92.6527%), leaving 1,753. The preliminary layer covers all 23,859. A future
strict completion cannot replace the recorded audit. Accepted factors and
explicit rejections must be counted separately.

## Model comparison and generator

`MODEL_COMPETITION_S1` tested specific implementations and settings:

| Candidate | Failed diagnostics | Pooled RMS z |
|---|---:|---:|
| Table/grille | 5/6 | 1.473 |
| Fixed slots | 5/6 | 1.515 |
| Hybrid | 6/6 | 1.710 |
| Copy/mutate | 5/6 | 1.748 |
| Tested ordinary-text transformation | 6/6 | 2.238 |

These failures do not exclude entire classes of languages, ciphers or generators.

The saved generator benchmark reports 23,859 cells, seed 20260930 and 2.595288 s
using Python/NumPy on 1 October 2026. Validation compared observed with generated:

| Statistic | Observed | Generated |
|---|---:|---:|
| Dominant ending | 49.3% | 47.9% |
| Exact adjacent repeats | 2.45% | 2.73% |
| One-edit neighbors | 16.6% | 14.9% |
| Local clusters, window 20 | 29.6% | 28.6% |
| Distinct forms | 2,432 | 4,475 |

The distinct-form mismatch is substantial. Machine runtime was not a controlled
comparison of scribal copying, composition and encryption. It does not establish
that historical generation was faster.

## Prior work and scope of contribution

Self-citation and generative explanations are not original to this project:

- Torsten Timm (2014), [How the Voynich Manuscript Was Created](https://arxiv.org/abs/1407.6639).
- Torsten Timm and Andreas Schinner (online 2019; journal issue 2020),
  [A Possible Generating Algorithm of the Voynich Manuscript](https://doi.org/10.1080/01611194.2019.1596999).
- Gordon Rugg (2004), [An Elegant Hoax?](https://doi.org/10.1080/0161-110491892755).
- Marcelo A. Montemurro and Damian H. Zanette (2013),
  [Keywords and Co-Occurrence Patterns in the Voynich Manuscript](https://doi.org/10.1371/journal.pone.0066344).

These authors did not validate this project's particular factorization or tests.
Statistical resemblance does not settle whether a message exists. Relevant
counterexamples include [Gaskell and Bowern (2022)](https://ceur-ws.org/Vol-3313/paper4.pdf),
[Bowern and Gaskell (2022)](https://ceur-ws.org/Vol-3313/paper6.pdf), and
[Michael A. Greshko's Naibbe cipher (2025)](https://doi.org/10.1080/01611194.2025.2566408)
with [author code](https://github.com/greshko/naibbe-cipher).

Related questions also appear in forum discussions by
[Rene Zandbergen (2017)](https://www.voynich.ninja/archive/index.php/thread-1812-2.html),
[RenegadeHealer (2021)](https://www.voynich.ninja/archive/index.php/thread-3476.html)
and [Jorge Stolfi (2025)](https://www.voynich.ninja/archive/index.php/thread-4765-5.html).
These establish discussion history, not peer-reviewed validation.
[Donald Fisk's generative work](https://www.fmjlang.co.uk/voynich/Explaining.html)
must not automatically be described as reproducing Montemurro's exact measure.
[Nicolas Turenne's 2026 preprint](https://arxiv.org/abs/2609.20835) is not an
independent validation of this model.

The claimed contribution is the aligned data layer, audit procedures, explicit
handling of errors and ambiguities, structural measurements and a testable
generative candidate. A copying workshop, commercial transaction or motive has
not been established by text measurements. For historical context, see
[Raymond Clemens, ed., The Voynich Manuscript](https://yalebooks.yale.edu/book/9780300217230/the-voynich-manuscript/).
