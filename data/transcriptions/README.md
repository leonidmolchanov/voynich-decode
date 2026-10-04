# Transcription (Z–L EVA) — source and our overlay

The full Voynich transcription (Zandbergen–Landini, EVA/IVTFF) is
**© René Zandbergen** and is **deliberately NOT redistributed** here in full — to
respect the rights and the project's policy. Instead, everything needed for exact
reconstruction is provided:

1. **Source (download from the rights holder):** https://www.voynich.nu/transcr.html
   — file `ZL3b-n.txt`.
   Expected source SHA-256: `bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc`
2. **Our correction overlay (13 edits):** `../corrections/ZL3b_corrections_v13.tsv`
   (full register with loci and positions in `ZL3b_corrected_v13.manifest.json`).
3. **Apply the overlay** to the source → the corrected transcription `ZL3b_corrected_v13`.
   Expected result SHA-256: `146334424138cd8ee7bd745ea221187fd4f6006a780e746cb3cf35457c3361b6`.

Attribution: the transliteration is by Gabriel Landini & René Zandbergen (EVA);
EVA signs denote forms, not a translation. The raw transcription itself is **not
required** to reproduce the analysis: the per-character EVA surfaces are already
included in `../factorization/full_surface_factorization.tsv` (a derived
analytical layer), and `ZL3b_corrected_v13.manifest.json` records all 13 edits and
the checksums.
