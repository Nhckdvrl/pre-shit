# When do language models learn to recover from a garden path?

A pre-registered training-dynamics study on Pythia / PolyPythias.

**Question.** Does susceptibility to a garden path emerge *before* the ability to
recover from it? That is: does a model first learn to form the locally plausible
but ultimately wrong syntactic expectation, and only later learn to revise it once
disambiguating evidence arrives?

The claim under test is a **behavioural** commitment→recovery dissociation across
pretraining. It does not assume the model maintains a single serial parse.

## Layout

```
PREREG.md          the locked protocol: metrics, acquisition-time rules, kill gates
DEVIATIONS.md      forced design decisions the protocol did not anticipate
code/              build_stimuli.py -> score.py -> analyze.py
data/raw/          SyntaxGym npz_ambig + mvrr; Christianson 2001; Alternates 2022
data/processed/    stimuli.jsonl (region-aligned, word-indexed)
models/hf_cache/   all model weights (git-ignored)
results/           per-checkpoint word surprisals + derived item effects
docs/              one report per kill gate
figures/
```

## Design in one paragraph

Word surprisal (bits, summed over BPE sub-tokens, region-aligned) is measured at
the disambiguator and at the words that follow it. **Commitment** `C` is the 2x2
interaction the SyntaxGym suites themselves specify — how much *more* the early
disambiguating cue helps in the ambiguous condition than in the unambiguous one —
so a bare comma effect cannot produce it. **Recovery** uses the identical
interaction at post-disambiguator positions: `B = mean_k max(G_k, 0)`, normalised
by the initial disruption as `R = B / C`. Acquisition times `T_commit` and
`T_recover` are read off the 12-checkpoint grid under sustain rules fixed in
advance, and the quantity of interest is `D = log2(T_recover / T_commit)`.
Item is the stimulus replication unit, seed the training replication unit; all
intervals come from a hierarchical bootstrap over both.

## Reproducing

```bash
uv venv env && VIRTUAL_ENV=env uv pip install torch transformers accelerate pandas pyarrow scipy matplotlib
./env/bin/python code/build_stimuli.py
./env/bin/python code/score.py --seeds 0,1,2,3,4,5,6,7,8,9 --steps 143000
./env/bin/python code/analyze.py --phase 0
```

## Status

See `docs/` — one report per gate, written as each gate is reached.
