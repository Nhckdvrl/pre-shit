# Stimuli

Not redistributed here — run `code/fetch_data.sh` to pull each set from its
original source, then `code/build_stimuli.py` to produce the region-aligned
`data/processed/stimuli.jsonl`.

| set | source | items |
|---|---|---|
| SyntaxGym `npz_ambig` | `cpllab/syntactic-generalization` | 24 x 4 conditions |
| SyntaxGym `mvrr` | same | 28 x 4 conditions |
| Christianson 2001 | `microsoft/turing-experiments` | 24 GP/control pairs |
| Alternates 2022 | same | 24 GP/control pairs |

`build_stimuli.py` records, per stimulus, the word list, each word's character
span, the disambiguator word indices and the recovery-window indices, so every
contrast downstream is region-aligned rather than tokenizer-aligned.
