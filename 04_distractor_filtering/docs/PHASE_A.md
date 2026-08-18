# Phase A (K1-K3) — is there a semantic-selective distractor effect at all?

`step143000`, 10 independent pretraining runs, 408 items over four LRE country relations. Crossed seed x item bootstraps throughout.

## K1 — does the model use the relevant context?

`base` accuracy **0.886** [0.839, 0.920] against a chance level of 0.20 (5 candidates). Eligible items — correct in >= 8/10 seeds, selected on `base` alone and never on any distractor condition — **354/408 (86.8%)**. **PASS.**

## K2 — is the interference semantic-selective, and does the *indirect* distractor carry it?

`D* = M_unrelated - M_semantic`. The two conditions share the distractor frame verbatim (`NAME lives in X.`) and differ only in whether X is a country or a dwelling, so sentence count and frame cancel exactly.

| distractor | position | D* (bits) | 95% CI | seeds > 0 |
|---|---|---|---|---|
| semantic | before | +2.684 | [+2.280, +3.064] | 10/10 |
| semantic | after | +5.045 | [+4.544, +5.535] | 10/10 |
| direct | before | +3.316 | [+2.926, +3.709] | 10/10 |
| direct | after | +6.551 | [+5.912, +7.145] | 10/10 |

The **indirect** distractor — which names a competing country and never the competing answer — produces the effect on its own, at roughly three quarters of the direct distractor's magnitude. The effect is therefore not reducible to copying a mentioned token, which is the failure mode that sank topic 02's filtering measure. **PASS.**

## K3 — is it just position?

The semantic effect is present at **both** distractor positions with CIs excluding 0 and 10/10 seeds. Position modulates its size (a distractor after the relevant fact hurts about twice as much) but does not explain it. **PASS.**

## Condition means (eligible items)

| condition | position | M (bits) | accuracy |
|---|---|---|---|
| `base` | na | +5.977 | 0.962 |
| `direct` | after | -2.347 | 0.236 |
| `direct` | before | +0.663 | 0.562 |
| `semantic` | after | -0.841 | 0.398 |
| `semantic` | before | +1.295 | 0.658 |
| `unrelated` | after | +4.204 | 0.925 |
| `unrelated` | before | +3.979 | 0.920 |

The unrelated distractor costs little; the semantic one costs most of the margin, and after the relevant fact it flips the decision outright.


---

# Phase B/C (K4) — full 12-checkpoint grid

10 seeds x 12 checkpoints. `A_decoy` is the pre-registered confound: the model's
own grasp of the decoy relation, measured from a clean no-distractor prompt.

| step | `M_base` | `D*` before | `D*` after | `D*`/`M` before | `D*`/`M` after | `A_decoy` |
|---|---|---|---|---|---|---|
| 128 | -5.48 | +0.01 | +0.00 | — | — | -25.6 |
| 512 | -3.48 | +0.03 | +0.01 | — | — | -22.6 |
| 1,000 | -2.44 | +0.07 | +0.08 | — | — | -20.5 |
| 2,000 | +0.36 | +1.77 | +1.32 | 4.96 | 3.70 | -16.1 |
| 4,000 | +2.69 | +2.40 | +3.35 | 0.89 | 1.24 | -12.2 |
| 8,000 | +3.96 | +2.57 | +3.59 | 0.65 | 0.91 | -10.4 |
| 16,000 | +4.79 | +2.79 | +3.88 | 0.58 | 0.81 | -9.4 |
| 32,000 | +5.39 | +2.83 | +4.23 | 0.52 | 0.78 | -8.6 |
| 64,000 | +5.98 | +2.88 | +4.67 | 0.48 | 0.78 | -7.7 |
| 96,000 | +6.36 | +3.15 | +5.15 | 0.49 | 0.81 | -7.4 |
| 128,000 | +5.69 | +2.70 | +4.75 | 0.47 | 0.83 | -8.7 |
| 143,000 | +5.98 | +2.68 | +5.04 | 0.45 | 0.84 | -8.0 |

Ratios before step 4,000 are not interpretable: `M_base` is near zero or negative
there, so the denominator is unstable.

## The confound is not the explanation

`A_decoy` improves monotonically over exactly the same window, so it had to be
tested at the item level rather than by correlating two monotone curves.

- correlation of `D*` with per-item `A_decoy`, within a checkpoint: **+0.05 to +0.12**
- regression coefficient: **+0.026** bits of `D*` per bit of decoy knowledge
- step effect after controlling `A_decoy`: **+4.67** bits, against **+4.97** raw —
  **94% of the trajectory survives**

The five-checkpoint correlations of `D*` with `M_base` (r = +0.991) and with
`A_decoy` (r = +0.992) are *not* evidence of anything: any two monotone curves on
five points correlate near 1. They are recorded here only to note that they were
not used.

## K4 — the trajectories are distinguishable

From step 4,000 to the end of training:

| quantity | 4,000 | 143,000 | growth |
|---|---|---|---|
| `M_base` — context use | +2.69 | +5.98 | **x2.22** |
| `D*` before | +2.40 | +2.68 | **x1.12** |
| `D*` after | +3.35 | +5.04 | **x1.51** |

Context use more than doubles after step 4,000 while the semantic-distractor cost
at the `before` position barely moves. Relative vulnerability `D*/M_base` falls
from 0.89 to 0.45 (`before`) and 1.24 to 0.84 (`after`). A constant ratio is the
null here, because `D*` is mechanically bounded by `M_base` — you cannot lose more
margin than you have — so the null prediction is a flat line, and both positions
fall below it. **PASS**, more strongly at `before`.

## What this says, stated no more strongly than the data allow

`D*` **grows in absolute terms throughout training**. The model does not become
less vulnerable to semantic distractors; it becomes *relatively* less vulnerable
as its ability to use relevant context outruns the growth of the distractor cost.
The honest statement is:

> Context use and semantic-distractor vulnerability both emerge in the same narrow
> window (steps 1,000-4,000), but they then part company: context use goes on
> developing for another order of magnitude of training while the distractor cost
> largely stops. Filtering is not separately acquired — it is what you get when one
> curve saturates and the other does not.

This is outcome **B** of the three the pre-registration admitted, in a weaker form
than "selective filtering is acquired later". It is not outcome A: semantic
distractors do not become more dangerous over training once context use is held
constant.

## Remaining caveat

`D*` and `M_base` are not independent by construction. The ratio analysis is the
right test given that, and it passes, but a design that decouples them — for
example holding `M_base` fixed by item selection at each checkpoint — would be a
stronger version and has not been run.
