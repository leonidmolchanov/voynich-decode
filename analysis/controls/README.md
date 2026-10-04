# Natural-language control corpora

Positive controls for the null/analysis battery: real natural-language texts run
through the **same** pipeline as the manuscript, so "language-like" statistics can
be compared against actual language (and against meaning-free nulls). All three are
**public-domain works**; each is truncated to the manuscript's token count (23,859
words) before comparison. They carry no relation to the Voynich content — they only
calibrate what real language looks like under the identical measurements.

| file | work | public-domain basis | digitization source |
|---|---|---|---|
| `english_jqadams.txt` | *Writings of John Quincy Adams*, ed. W. C. Ford | author/editor long out of copyright (pre-1929) | OCR of a public-library scan (New York Public / Mid-Manhattan copy); a few lines of library-stamp OCR remain at the head and are ignored by the loaders |
| `latin_caesar_218.txt` | Caesar, *De Bello Gallico* (Books I–IV) | classical text, public domain | digitization derived from **Project Gutenberg eBook #218**; the Gutenberg header/footer and license boilerplate have been removed, leaving only the public-domain Latin text |
| `latin_caesar_18837.txt` | Caesar, *De Bello Gallico* (fuller edition) | classical text, public domain | digitization derived from **Project Gutenberg eBook #18837**; Gutenberg boilerplate removed |

The loaders (`../word_frequency/wf_common.py`, `../linguistic_laws/ll_common.py`)
additionally drop any residual front/back credit tokens at read time. "Public
domain" is accurate for the shipped files: no Project Gutenberg trademark or license
text remains in them; attribution to the Gutenberg digitizations is given here.
