# How the datasets are generated (our + third-party data)

This document records the **provenance** of all data and the **pipeline** used to
assemble it: what is ours (and uploaded), and what is third-party/recoverable
(and is NOT redistributed but fetched from the source). Honest framing: training
is lawful (public-domain scans + CC-BY ciphers); the constraints concern
**redistribution**, not training.

---

## 1. Input sources

### 1.1 Third-party / external (NOT redistributed — fetched from the source)
| source | what it provides | license | how to obtain |
|---|---|---|---|
| **Beinecke MS 408**, Yale University Library | manuscript images | **Public Domain** (Yale asserts no copyright) | IIIF manifest `collections.library.yale.edu/manifests/2002046`; `scripts/fetch_yale_iiif.py` |
| **Zandbergen–Landini EVA** transliteration | text labels/markup | **© R. Zandbergen** (attribution; raw file not redistributed) | `voynich.nu`; our corrected overlay is in `data/transcriptions/` |
| **voynichese** word coordinates | mapping glyphs/words to positions | © Zandbergen (attribution) | `voynichese.com` |
| **DECODE / DECRYPT** ciphers (Copiale, Borg, etc.) | cipher benchmark (ancillary; an unsuccessful cipher-solver attempt) | **CC BY 4.0** (Megyesi et al.) | DECODE database |
| **Pliny, Naturalis Historia**, etc. | comparison corpus | text PD; attribution of the digitization source | digitization source (attribution) |
| **EVA2.ttf** (font) | glyph rendering in prototypes only | **© G. Landini 1998, free, non-commercial license** | with attribution to G. Landini |

### 1.2 Ours (derived from PD scans — uploaded to the HF dataset `voynich-decode-data`)
| dataset | size | contents |
|---|---|---|
| `strict_v4_direct_factor_crops_v1` | ~370M | cell crops for accepted strict_v4 |
| `leaf_clean_highres_crops_v1` | ~269M | high-res crops for the shadow observer |
| `strict_v2_broad_highres_targets_v1` | ~72M | v2 target crops |
| `label_hand_forensics_x1` | ~1.2G | per-word crops (hand forensics) |
| `x_v10u_epoch30_target_free_oof_v1` | ~1.0G | OOF training set (leaf-held) |
| `s1_visual_crib` | ~512M | visual "crib" |

---

## 2. Dataset generation pipeline

```
Yale IIIF scans (PD)                 Z–L transcription (labels)    voynichese coordinates
        │                                   │                              │
        ▼                                   ▼                              ▼
  folio normalization  ───────────►  text↔image alignment  ◄──── cell/word boxes
        │                                                                  │
        └──────────────────────────────►  CROP CUTTING  ◄──────────────────┘
                                                │
                              leaf-held split (5×3 fold/seed, 0 recto/verso overlap)
                                                │
                                   train / OOF / blind-target sets
                                                │
                                        observer training → gates
```

Key rules:
- **PD basis:** the crops are pixels of public-domain Yale scans; cropping adds
  no third-party rights → our crops are publishable.
- **Labels** come from the Z–L transcription (+ our correction overlay register);
  the raw transcription is not redistributed, attribution is given.
- **Coordinates** come from voynichese (attribution).
- **The split is always leaf-held** (the whole physical leaf in one fold), so that
  recto/verso do not leak between train and OOF.
- Every step is tied to `scan_index` + SHA-256 (see `OFFICIAL_SCAN_SOURCE_AUDIT.md`).

Reproduction without storing the crops is possible like this:
`fetch_yale_iiif.py` (scans) + coordinates + overlay → re-cutting yields the same
boxes.

---

## 3. Where things live
- **Our crops / training sets:** HF dataset `LeonidMolchanov1987/voynich-decode-data` (public), as `*.tar` archives.
- **Observer weights:** HF model `LeonidMolchanov1987/voynich-decode-models`.
- **Code / factorization / corrections / generator:** this repository (+ Zenodo).
- **Third-party:** not hosted — `fetch_yale_iiif.py` (scans), DECODE (ciphers), voynich.nu (transcription), the corpus source (Pliny).

## 4. Licensing summary
- Training on these data is lawful (PD scans, CC-BY ciphers).
- Do NOT redistribute: the raw Z–L transcription, the full Yale scan archive
  (fetched via IIIF). The EVA font is under a non-commercial license, with
  attribution.
- Attribution is required: Zandbergen–Landini, DECRYPT/DECODE, Landini (font),
  the corpus source, Beinecke/Yale (courtesy).
