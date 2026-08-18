# Holding `M_base` fixed

`D*` is bounded by the margin an item has to lose, so it is not independent of `M_base` by construction. The ratio analysis in `PHASE_A.md` is the right test given that coupling, but it is still a ratio. Here `M_base` is held fixed instead, three ways.


## Distractor before the relevant fact

### (a) `D*` within fixed `M_base` bins

| step | (0.0, 2.0] | (2.0, 4.0] | (4.0, 6.0] | (6.0, 8.0] | (8.0, 10.0] |
|---|---|---|---|---|---|
| 4,000 | +2.02 | +2.42 | +2.91 | +3.30 | — |
| 8,000 | +1.83 | +2.04 | +2.84 | +3.38 | +3.87 |
| 16,000 | +1.78 | +2.14 | +2.69 | +3.44 | +4.30 |
| 32,000 | +1.70 | +2.15 | +2.65 | +3.32 | +3.85 |
| 64,000 | +1.80 | +2.10 | +2.62 | +3.10 | +3.60 |
| 96,000 | +1.86 | +2.23 | +2.80 | +3.36 | +3.70 |
| 128,000 | +1.72 | +2.08 | +2.74 | +2.80 | +3.35 |
| 143,000 | +1.60 | +2.19 | +2.57 | +2.83 | +3.22 |

(cells with fewer than 200 observations are suppressed)

### (b) `D* ~ M_base + step`

Coefficient on `M_base`: **+0.225** bits per bit — the coupling is strong, as expected.

| step | raw `D*` | step effect with `M_base` held fixed |
|---|---|---|
| 4,000 | +2.40 | 0 (reference) |
| 8,000 | +2.57 | -0.121 |
| 16,000 | +2.79 | -0.081 |
| 32,000 | +2.83 | -0.183 |
| 64,000 | +2.88 | -0.268 |
| 96,000 | +3.15 | -0.080 |
| 128,000 | +2.70 | -0.380 |
| 143,000 | +2.68 | -0.458 |

Raw growth from step 4,000: **+0.75** bits. With `M_base` held fixed the step effects span **0.46** bits.

### (c) items resampled to a common `M_base` distribution

| step | matched mean `M_base` | matched `D*` | 95% CI |
|---|---|---|---|
| 4,000 | +5.10 | +2.93 | [+2.59, +3.27] |
| 8,000 | +5.14 | +2.86 | [+2.68, +3.05] |
| 16,000 | +5.18 | +2.83 | [+2.56, +3.10] |
| 32,000 | +5.19 | +2.76 | [+2.51, +2.99] |
| 64,000 | +5.16 | +2.66 | [+2.44, +2.86] |
| 96,000 | +5.20 | +2.80 | [+2.48, +3.12] |
| 128,000 | +5.20 | +2.52 | [+2.23, +2.79] |
| 143,000 | +5.16 | +2.57 | [+2.25, +2.84] |

Across checkpoints at matched `M_base`, `D*` spans **+2.52 to +2.93** bits (raw span +2.40 to +3.15).


## Distractor after the relevant fact

### (a) `D*` within fixed `M_base` bins

| step | (0.0, 2.0] | (2.0, 4.0] | (4.0, 6.0] | (6.0, 8.0] | (8.0, 10.0] |
|---|---|---|---|---|---|
| 4,000 | +2.59 | +3.30 | +4.15 | +4.99 | — |
| 8,000 | +2.20 | +2.72 | +3.85 | +5.12 | +6.11 |
| 16,000 | +2.24 | +2.66 | +3.76 | +5.14 | +6.26 |
| 32,000 | +2.31 | +3.00 | +3.81 | +5.03 | +6.11 |
| 64,000 | +2.61 | +3.02 | +3.89 | +5.05 | +6.15 |
| 96,000 | +2.50 | +3.11 | +4.12 | +5.41 | +6.68 |
| 128,000 | +2.23 | +3.08 | +4.32 | +5.40 | +6.48 |
| 143,000 | +2.56 | +3.50 | +4.38 | +5.45 | +6.59 |

(cells with fewer than 200 observations are suppressed)

### (b) `D* ~ M_base + step`

Coefficient on `M_base`: **+0.463** bits per bit — the coupling is strong, as expected.

| step | raw `D*` | step effect with `M_base` held fixed |
|---|---|---|
| 4,000 | +3.35 | 0 (reference) |
| 8,000 | +3.59 | -0.347 |
| 16,000 | +3.88 | -0.437 |
| 32,000 | +4.23 | -0.368 |
| 64,000 | +4.67 | -0.198 |
| 96,000 | +5.15 | +0.099 |
| 128,000 | +4.75 | +0.009 |
| 143,000 | +5.04 | +0.176 |

Raw growth from step 4,000: **+1.80** bits. With `M_base` held fixed the step effects span **0.61** bits.

### (c) items resampled to a common `M_base` distribution

| step | matched mean `M_base` | matched `D*` | 95% CI |
|---|---|---|---|
| 4,000 | +5.10 | +4.29 | [+3.80, +4.87] |
| 8,000 | +5.14 | +4.05 | [+3.61, +4.49] |
| 16,000 | +5.18 | +4.04 | [+3.58, +4.51] |
| 32,000 | +5.19 | +4.12 | [+3.80, +4.43] |
| 64,000 | +5.16 | +4.15 | [+3.74, +4.58] |
| 96,000 | +5.20 | +4.42 | [+4.08, +4.74] |
| 128,000 | +5.20 | +4.27 | [+3.49, +4.80] |
| 143,000 | +5.16 | +4.61 | [+4.31, +4.98] |

Across checkpoints at matched `M_base`, `D*` spans **+4.04 to +4.61** bits (raw span +3.35 to +5.15).


---

# The ratio test was wrong, and K4 does not survive

## What the matched analyses show

At fixed `M_base`, `D*` barely moves across training:

| position | matched `D*` at 4,000 | at 143,000 | change |
|---|---|---|---|
| before | +2.93 [+2.59, +3.27] | +2.57 [+2.25, +2.84] | **-12%**, CIs overlap |
| after | +4.29 [+3.80, +4.87] | +4.61 [+4.31, +4.98] | **+7%**, if anything *up* |

The within-bin tables say the same thing, and the regression step effects span
0.46 and 0.61 bits against raw growths of 0.75 and 1.80.

## Why the ratio fell anyway

`PHASE_A.md` claimed "a constant ratio is the null here". **That claim is wrong.**
Fit one line, pooled over all checkpoints, with **no step term at all**:

    before:  D* = 1.635 + 0.218 * M_base
    after:   D* = 1.948 + 0.467 * M_base

Because the intercept is large and the slope is well below 1, the ratio
`D*/M_base = a/M_base + b` **must** fall as `M_base` grows, with no change in
filtering whatsoever. That checkpoint-independent line predicts the observed
ratios almost exactly:

| step | `M_base` | observed `D*`/`M` (before) | predicted by the fixed line | observed (after) | predicted |
|---|---|---|---|---|---|
| 4,000 | +2.69 | 0.89 | 0.83 | 1.24 | 1.19 |
| 8,000 | +3.96 | 0.65 | 0.63 | 0.91 | 0.96 |
| 16,000 | +4.79 | 0.58 | 0.56 | 0.81 | 0.87 |
| 32,000 | +5.39 | 0.52 | 0.52 | 0.78 | 0.83 |
| 64,000 | +5.98 | 0.48 | 0.49 | 0.78 | 0.79 |
| 96,000 | +6.36 | 0.49 | 0.48 | 0.81 | 0.77 |
| 128,000 | +5.69 | 0.47 | 0.51 | 0.83 | 0.81 |
| 143,000 | +5.98 | 0.45 | 0.49 | 0.84 | 0.79 |

The whole "relative vulnerability halves" result is reproduced by a relationship
between `D*` and `M_base` that does not depend on training step. There is no
filtering trajectory to explain.

## Verdict

**K4 fails. The developmental claim is retracted.**

`D*` grows with training only because `M_base` grows; at matched `M_base` it is
flat. Context use and semantic-distractor vulnerability do not part company — they
sit on one fixed curve, and training moves the model along it.

**K1-K3 stand and are unaffected.** At the final checkpoint the semantic-selective
distractor effect is large (+2.68 / +5.05 bits), present in 10/10 seeds, carried by
the *indirect* distractor rather than by copying, and robust to distractor
position. That is a solid statement about a mature model. It is not a
training-dynamics result.

## The methodological failure, named

`../METHODOLOGY.md` rule 4 says: ask what the metric returns under the null. I
asked that of `D*` — a signed difference, correctly null at 0 — and then built the
K4 argument on `D*/M_base`, a **ratio**, without asking the same question of it.
The rule was applied to one metric and not to the derived one that carried the
claim. Rule 4 now reads: every quantity a claim rests on, including ratios and
normalisations formed downstream, needs its null stated before use.
