# Prior work and the boundary of the claimed contribution

This document separates published priority from the results of this project. It
does not judge authors as being "for" or "against" meaning; it records which
thesis appeared where, and how strong a conclusion the source supports.

## Short summary

The idea that the surface of the manuscript could have been produced by copying
already-written forms with small modifications is **not** a new result of this
project. It was proposed in detail by Torsten Timm in 2014 and, jointly with
Andreas Schinner, formalized as a self-citation generator in a peer-reviewed
2020 paper. The authors supported the meaningless-strings hypothesis and
reproduced some statistical properties of the manuscript, including both Zipf
laws.

The general thesis of statistical indistinguishability is not new either. Its
parts were long ago stated from both sides: human gibberish can look
language-like, and some reversible ciphers can look Voynich-like. As early as
April 2017, René Zandbergen described a thought experiment in which a meaningful
and a shuffled text, after the same frequency substitution, cannot be
distinguished by the distribution of words and their lengths. The project
therefore claims priority neither over self-citation nor over the statement that
"statistics by themselves do not prove meaning or meaninglessness."

## Peer-reviewed and conference works

| Source | What it establishes | What the source does not establish |
|---|---|---|
| [Timm 2014](https://arxiv.org/abs/1407.6639) | Analysis of closely written forms and the hypothesis of text generation by copying with modification. | It is a preprint; it does not test the factorization and protocol of this project. |
| [Timm & Schinner 2020](https://doi.org/10.1080/01611194.2019.1596999) | Self-citation, achievable without complex tools; support for the hoax hypothesis; the generator reproduces some key properties, especially both Zipf laws. | It does not prove that this particular algorithm produced MS 408, and does not reproduce every observed dependency. |
| [Gaskell & Bowern 2022](https://ceur-ws.org/Vol-3313/paper4.pdf) | 42 participants wrote meaningless samples; such samples could imitate almost all tested low-level metrics, and ML more often classified Voynich transcriptions as gibberish. | The authors explicitly note that short samples do not test page and quire structure. |
| [Bowern & Gaskell 2022](https://ceur-ws.org/Vol-3313/paper6.pdf) | Several kinds of transformation of a meaningful text reduce conditional entropy; unusual word predictability is not conclusive proof of meaninglessness. | Does not claim that MS 408 is enciphered by any specific tested method. |
| [Greshko 2025](https://doi.org/10.1080/01611194.2025.2566408) | A reversible, verbose homophonic Naibbe cipher, implementable with 15th-century materials, reproduces many properties of MS 408 when enciphering Latin and Italian texts. | It is a proof of concept, not a decipherment of the manuscript; matching statistics does not identify the historical mechanism. |
| [Timm & Schinner 2024](https://doi.org/10.1080/01611194.2023.2225716) | Discussion of text-creation hypotheses and the dispute over the presence of linguistic structures. | Not an independent confirmation of this project's specific model. |
| [Turenne 2026](https://arxiv.org/abs/2609.20835) | A preprint proposing a generative grammar / pastiche hypothesis, combining probabilistic modeling and image analysis. | As of October 2026 it is a preprint; it has not passed journal peer review and does not reproduce our factorization. |
| Currier 1976 (seminar; transcript in D'Imperio 1978) | Statistically distinguishable "languages"/hands A and B — the basis of the Currier A/B markup we use. | Not a generation model; does not distinguish language vs. gibberish and does not fix the number of scribes. |
| [Montemurro & Zanette 2013](https://doi.org/10.1371/journal.pone.0066344) | Information structure and long-range correlations of words and sections, compatible with meaningful text organization. | This signal is also reproduced by generative processes (including ours); on its own it does not prove language. |
| [Rugg 2004](https://doi.org/10.1080/0161-110491892755) | A hoax hypothesis: a syllable table + a Cardan grille could produce Voynich-like text. | A demonstration of possibility, not proof that the manuscript was created this way. |
| Reddy & Knight 2011, "What We Know About the Voynich Manuscript" (ACL LaTeCH workshop) | A summary of statistical properties of MS 408 (entropy, morphology, Zipf, bigrams). | A survey of properties; not a generation mechanism and not a decipherment. |

## Early independent computational lines

- [Donald Fisk, *Explaining the Voynich Manuscript* (2017)](https://www.fmjlang.co.uk/voynich/Explaining.html)
  states directly that meaninglessness is hard to prove and that a mechanism
  must reproduce the statistical properties of the text.
- [Donald Fisk, *Zipf's Law and Word Length Distributions* (2017)](https://www.fmjlang.co.uk/voynich/VoynichZipf.html)
  shows that a transition-table generator yields almost the same Zipf
  distribution and a similar word-length distribution.
- [Donald Fisk, *Voynich Word Order* (2017)](https://www.fmjlang.co.uk/voynich/VoynichWordOrder.html)
  finds that a simple model does not reproduce all word-pair dependencies, and
  revises it after a remark about the link between `-y` endings and `qo-`
  beginnings.
- [DonaldFisk, forum, 10 April 2017](https://www.voynich.ninja/archive/index.php/thread-1812.html)
  presents a state-transition generator as a quantitative generative null
  hypothesis, but leaves labels, paragraph and line structure, and some local
  regularities unresolved.
- [DonaldFisk, forum, 22 April 2017](https://www.voynich.ninja/archive/index.php/thread-1812-3.html)
  reports obtaining the relationships between page types and some words
  previously found by Montemurro, and explains them by section-dependent
  generation. This should not be retold as an independent replication of
  Montemurro's exact information measure on a synthetic corpus: the post does
  not establish that.

## Forum formulations

Forum posts are not equivalent to peer-reviewed publication. They are included
as a log of objections and for correct attribution of formulations.

| Author | Exact point | Supported thesis | Limitation |
|---|---|---|---|
| ReneZ | [11 April 2017](https://www.voynich.ninja/archive/index.php/thread-1812-2.html) | A meaningful and a shuffled text, after the same frequency substitution, can have identical distributions; by these features they cannot be distinguished. | The thought experiment shows the insufficiency of the metrics, not the nature of MS 408. |
| ReneZ | [14 April 2017](https://www.voynich.ninja/thread-1845.html) | Fisk's analysis does not justify a conclusion of meaninglessness; absence of proof of meaning does not prove meaninglessness; proving it is "almost impossible." | A methodological objection, not a model of the text. |
| ReneZ | [25 April 2017](https://www.voynich.ninja/archive/index.php/thread-1812-5.html) | The signs for and against meaning remain inconclusive; benchmark metrics and an estimate of their natural variability are missing. | Does not claim equal probabilities of the hypotheses and does not endorse a single generator. |
| RenegadeHealer | [11 February 2021](https://www.voynich.ninja/archive/index.php/thread-3476.html) | Poses the direct question of which tests can reliably distinguish an unknown meaningful message from deliberately language-like gibberish; without such tests, excluding either side is premature. | Does not propose a specific statistical solution. |
| RenegadeHealer | [11 February 2021](https://www.voynich.ninja/thread-3510.html) | Compares a quack's prop book with a genuine enciphered medical reference and asks how to reliably distinguish them. | A historical scenario, not an experiment; the author gives no documented precedent of exactly such a prop. |
| ReneZ | [11 February 2021](https://www.voynich.ninja/thread-3510.html) | Auto-copy is not identical to meaninglessness; a mixture of meaningful text and meaningless padding is possible. | Does not confirm the proportion of padding and does not establish the mechanism. |
| Jorge_Stolfi | [4–5 July 2025](https://www.voynich.ninja/archive/index.php/thread-4765-5.html) | One cannot logically infer the absence of a message from the operation of a generator: the stream of its random decisions may itself be an information input. | Does not prove that such an input was actually used in MS 408. |
| Jorge_Stolfi | [24 August 2025](https://www.voynich.ninja/printthread.php?page=6&tid=4877) | Points to a logical leap: a generator that reproduced properties X, Y, Z does not prove the meaninglessness of the original. | A critique of the sufficiency of the argument, not a refutation of self-citation as a possible process. |
| Jorge_Stolfi | [11 April 2026](https://voynich.ninja/thread-5500-page-3.html) | Formulates a strong algorithmic criterion: a short algorithm must produce exactly the text, not merely similar statistics. | The criterion is extremely strict; it does not show that a message exists. |
| ReneZ | [16 August 2025](https://www.voynich.ninja/showthread.php?mode=threaded&pid=69730&tid=1555) | Zipf's law does not prove meaningfulness, but it constrains the family of possible generators. | A single law does not distinguish competing mechanisms. |
| Torsten | [2019–2025 paper discussion](https://voynich.ninja/thread-2790.html) | Defends self-citation as a reconstructed process and links recursiveness to local and long-range correlations. | Forum extensions do not replace independent replication. |

Based on the available primary sources, the claim that DonaldFisk supposedly
fully reproduced Montemurro's test on a meaningless text is too strong. He writes
that he obtained the same relationships between page types and some words and
explained them by different generation regimes. This is a serious generative
alternative, but not a documented replication of Montemurro's exact information
measure on an independent synthetic corpus.

## What this project claims

The project does not limit itself to a survey synthesis and does not claim the
discovery of the original self-citation idea. Its central goal is to test that
idea, separate the working part from the insufficient part, and bring the
confirmed principle up to a complete, reproducible algorithm.

### Confirmed

- local copying of already-existing forms with small modifications does indeed
  explain a substantial part of the observed similarity;
- language-like frequencies and correlations can arise without a necessarily
  continuous message;
- the generative hypothesis survives transfer between leaves and several
  transcription traditions after introducing the measured constraints.

### Refuted as a sufficient explanation

- simple copy-mutate / self-citation without additional channels failed five of
  six frozen diagnostics;
- a single transition table, a single grille, or a single slot dictionary does
  not simultaneously reproduce the whole set of observations;
- a match in Zipf, entropy, or a single correlation does not identify the
  historical mechanism and does not prove the absence of a message.

### Completed

The confirmed principle is refined by a form automaton, a separate ending
channel with a reset on the physical line, a local memory band, A/B regime
parameters, and an explicit abstention on unresolvable signs. It is then tested
on held-out leaves, independent transcriptions, data errors, and the full
publication denominator.

The reproducible package includes:

1. a cross-transcription factorization of 23,859 aligned cells;
2. a quantitative physical line reset and a short dependency horizon;
3. a train/test split by physical leaves and a fail-closed audit;
4. structure-based detection of transcription errors and disputed boundaries,
   followed by verification on scans and independent transcriptions;
5. a frozen comparison of several generative and cipher families;
6. a compact generator, tested on the same set of diagnostics;
7. a full publication structural outcome for each cell, including an explicit
   abstain where the image does not allow an honest choice of sign.

The scientific conclusion is deliberately bounded: the surface features studied
support a compact generative procedure better than the tested simple language
and cipher nulls. They do not prove the fundamental absence of a hidden message.
A sufficiently complex or verbose cipher remains logically possible and must be
compared against the full set of constraints, not against a single convenient
statistic.
