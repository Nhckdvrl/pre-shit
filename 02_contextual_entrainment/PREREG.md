# Pre-registration — when do mechanical copying and semantic filtering diverge?

**Locked 2026-08-19, before any scoring.** Deviations go in `DEVIATIONS.md`.

## Background and the gap

*Llama See, Llama Do* (ACL 2025) established **contextual entrainment**: a model
raises the probability of any token that just appeared in context, including
random ones, and the effect is modulated by semantics. *Better and Worse with
Scale* (ACL Findings 2026) then found an opposing scaling result on Cerebras-GPT
111M–13B and **Pythia 410M–12B**: larger models resist *semantically false*
context more, while copying *non-semantic* context more. It reads these as two
functions — mechanical copying and semantic filtering — and does not decompose them.

Both papers characterise final models. Neither asks how the split arises inside a
single pretraining run.

## Question

> Models scale toward stronger semantic filtering but stronger mechanical
> copying. **When during pretraining do these two opposing forms of context
> sensitivity emerge?**

No direction is predicted. Copying-then-filtering, filtering-then-copying, and
simultaneous emergence are all admissible outcomes.

## Stimuli

LRE (`evandez/relations`), **factual subset: 26 relations**, capped at 40
subject-object pairs per relation with a fixed seed. No new items are written.

For an item with relation template `T`, subject `s`, gold object `g`:

| condition | context prepended to the query | distractor `d` |
|---|---|---|
| `none` | — | — |
| `related` | `T(s) g.` — the true fact | `g` |
| `irrelevant` | `T(s') g'.` — a true fact, different subject, same relation | `g'` |
| `random` | a random common noun, as a bare sentence | that noun |
| `counterfactual` | `T(s) d.` — the same fact made false | `d` |

`counterfactual` distractors are drawn from the same relation's object inventory
and matched on sub-token length to `g` where possible, so that `K` below is not a
length contrast.

## Measures

For candidate `x` and condition `c`, `l_c(x)` is the summed log-probability of
`x`'s sub-tokens given the (context + query) prefix. Entrainment is

    D_x^c = l_c(x) - l_none(x)

Token count cancels in this difference, so no length normalisation is applied.

**Mechanical copying** — a token with no semantic reason to be favoured:

    E_copy = D_d^random

**Semantic filtering** — resistance to context that is false rather than merely
present:

    F = (D_g - D_d)^counterfactual

**Parametric knowledge (the dangerous confound)**:

    K = l_none(g) - l_none(d)

An early checkpoint that fails to resist "the capital of Germany is Munich" may
simply not know Berlin yet. `F` is therefore never interpreted without `K`.

## Kill gates

| gate | requirement | if failed |
|---|---|---|
| **K1** (Phase A, final checkpoint) | `E_copy > 0` with a crossed seed x item bootstrap CI excluding 0; counterfactual context shifts gold vs. distractor (`F` reliably non-zero); both hold in >=7/10 seeds | kill — the phenomenon is absent at 410M |
| **K2** (Phase A) | `F` is not fully explained by `K`: with `K` as a covariate, the partial effect of checkpoint on `F` survives, and `F` remains non-zero within `K`-matched strata | kill the independent-semantic-filtering claim |
| **K3** (Phase B, 5 checkpoints) | after knowledge control, `E_copy(t)` and `F(t)` have distinguishable trajectories — opposite signs of change, different emergence times, or a `checkpoint x context-type` interaction | kill — one curve, not two |

Phase B checkpoints: `1000, 4000, 16000, 64000, 143000`.
Phase C (full 12-point grid, acquisition times, any mechanistic work) only if K3 passes.

## Statistics

Item = stimulus replication unit, seed = training replication unit. All intervals
come from a **crossed seed x item bootstrap** (resample seeds, then items within
each resampled seed). Pooling seeds x items as independent observations is not
permitted — that error was made and corrected in `01_garden_path` and will not be
repeated here.

## Known risk

Pythia-410M is the *smallest* model in the ACL 2026 range. If semantic filtering
is what grows with scale, 410M is where it is weakest, so K1/K2 failing is a live
possibility. That is a reason to run Phase A first and cheaply, not a reason to
prefer a larger model — the 10-seed replication only exists at this size.
