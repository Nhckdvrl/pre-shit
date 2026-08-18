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
data/              stimuli, fetched by code/fetch_data.sh (not redistributed)
models/hf_cache/   Pythia + PolyPythia weights, ~190 GB (not in git)
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
uv venv env && VIRTUAL_ENV=env uv pip install -r requirements.txt
./code/fetch_data.sh
./env/bin/python code/build_stimuli.py
./env/bin/python code/test_dynamics.py
./env/bin/python code/score.py --seeds 0,1,2,3,4,5,6,7,8,9 --steps 143000
./env/bin/python code/analyze.py --phase 0
```

## Status: killed at Phase 1

The effect is robustly present (K0/K1: 10/10 seeds, all four stimulus sets), but
commitment and recovery are **not** separately acquired. `R = B/C` is flat from
the moment commitment appears; the median recovery improvement is negative on
both constructions, and 0/10 and 1/10 seeds respectively met the pre-registered
30% bar. K2 and K4 fail, so K5 fails and the study stops here.

See `docs/VERDICT.md` for the full reasoning, `docs/PHASE0_K0_K1.md` and
`docs/PHASE1_K2_K5.md` for the gate reports.

## What is and is not in this repository

Everything needed to rerun the study is here: the protocol, all analysis and
scoring code, the sanity checks, the per-checkpoint surprisal tables and the
reports. Deliberately absent:

* **Model weights** (`models/hf_cache/`, ~190 GB) — see `models/README.md`.
* **Stimuli** (`data/`) — third-party sets, not redistributed here. Run
  `code/fetch_data.sh`, which pulls each from its original source.
* **Run logs** (`logs/`) — download progress bars, nothing the results depend on.
