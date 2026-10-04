# analysis/ — null models, controls, and adversarial tests

The adversarial battery behind the honest conclusion: fair null models + real
natural-language positive controls that test whether the Voynich's language-like
signatures are genuine structure or reproducible by a meaning-free process.
Narrative summary and verdicts: `../docs/NULL_MODELS_AND_CONTROLS.md`.

Each suite ships its code, raw results (`*.json` / report), and an English write-up —
a `NOTES_*.md` (for `state_independence/`, the narrative is `report.txt`).
Scripts are repointed to the shipped data (`../data/factorization/full_surface_factorization.tsv`,
the generator in `../src/voynich_generator/`, and the controls in `controls/`).

**Provenance note.** The `NOTES_*.md` describe the original investigation and may cite
internal project paths (`WORKING/…`, `MASTER/…`, `ANALYSIS_REPORTS/…`,
`tmp/shadow_analysis/…`, `FINDINGS.md`). Those internal inputs are **not shipped**; the
release scripts use the paths above instead. All result JSONs here were **re-generated on
the shipped strict-v82 factorization** (so they reproduce from the release); where a NOTES
narrative quotes a number from the earlier ~70% snapshot, the shipped JSON is authoritative
and the qualitative verdict is unchanged.

| suite | question | key result |
|---|---|---|
| `shadow_of_null/` | is the structure a measurement artifact? | 3-null battery; ending-skew + body-reuse REAL, several "ladder"/coverage claims are null-reproducible |
| `montemurro/` | does the "genuine message" clustering prove meaning? | replicates, but a meaning-free drift generator reproduces/exceeds it (p(gen≥real)=1.000) |
| `linguistic_laws/` | do pro-language signatures break the generator? | vs English/Latin controls: no — long-range = drift/nonstationarity, often > NL |
| `payload_mdl/` | does the text carry a message or exhaust it? | sits at the self-generation floor, ~0% toward a message ceiling (positive cipher controls) |
| `state_independence/` | is there category-level grammar? | near-zero (local copying only) |
| `word_frequency/` | vocabulary concentration | corroborates concentrated reuse |

`controls/` — public-domain English (J.Q. Adams) and Latin (Caesar) corpora used as
natural-language positive controls (see `controls/README.md`).

Honest limit (same everywhere): internal statistics cannot exclude an information-thin
cipher observationally equivalent to self-generation; the claim is sufficiency/parsimony,
not "proven hoax".
