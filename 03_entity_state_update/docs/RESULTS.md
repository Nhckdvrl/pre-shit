# Entity state update — binding is learned early, interference is learned late

Pythia-410M, 10 independent pretraining runs, 12 checkpoints, 920 trials over 46 categories. All intervals are crossed seed x trial bootstraps.

## Accuracy by condition (median over seeds)

| step | `update_1` | `update_2` | `update_3` | `control_2` | `control_3` |
|---|---|---|---|---|---|
| 128 | 0.512 | 0.327 | 0.202 | 0.297 | 0.191 |
| 512 | 0.535 | 0.354 | 0.208 | 0.318 | 0.189 |
| 1,000 | 0.898 | 0.691 | 0.384 | 0.521 | 0.371 |
| 2,000 | 0.982 | 0.876 | 0.449 | 0.698 | 0.543 |
| 4,000 | 0.992 | 0.752 | 0.451 | 0.691 | 0.570 |
| 8,000 | 0.992 | 0.705 | 0.427 | 0.672 | 0.545 |
| 16,000 | 0.995 | 0.735 | 0.382 | 0.657 | 0.586 |
| 32,000 | 0.996 | 0.714 | 0.341 | 0.691 | 0.626 |
| 64,000 | 0.997 | 0.765 | 0.335 | 0.676 | 0.650 |
| 96,000 | 0.995 | 0.773 | 0.326 | 0.684 | 0.649 |
| 128,000 | 0.993 | 0.797 | 0.336 | 0.721 | 0.652 |
| 143,000 | 0.993 | 0.741 | 0.333 | 0.712 | 0.654 |

## The two abilities

`update_1` accuracy is **binding**: can the model report a state it was just given? `PI cost = accuracy(control_n) - accuracy(update_n)` is **interference**: what does it cost that the earlier sentences overwrote the queried key, rather than merely occupying the same context?

| step | binding | PI cost @2 states | PI cost @3 states | seeds with PI@3 > 0 |
|---|---|---|---|---|
| 128 | 0.513 | -0.027 [-0.037, -0.017] | -0.012 [-0.020, -0.005] | 0/10 |
| 512 | 0.535 | -0.034 [-0.043, -0.024] | -0.019 [-0.028, -0.011] | 0/10 |
| 1,000 | 0.898 | -0.164 [-0.217, -0.119] | -0.018 [-0.035, -0.002] | 1/10 |
| 2,000 | 0.979 | -0.170 [-0.200, -0.139] | +0.088 [+0.051, +0.128] | 9/10 |
| 4,000 | 0.987 | -0.081 [-0.123, -0.035] | +0.107 [+0.059, +0.157] | 10/10 |
| 8,000 | 0.991 | -0.071 [-0.102, -0.037] | +0.120 [+0.072, +0.166] | 9/10 |
| 16,000 | 0.994 | -0.061 [-0.106, -0.016] | +0.215 [+0.173, +0.256] | 10/10 |
| 32,000 | 0.995 | -0.040 [-0.096, +0.012] | +0.266 [+0.227, +0.304] | 10/10 |
| 64,000 | 0.996 | -0.074 [-0.106, -0.035] | +0.317 [+0.277, +0.359] | 10/10 |
| 96,000 | 0.994 | -0.072 [-0.115, -0.026] | +0.337 [+0.296, +0.373] | 10/10 |
| 128,000 | 0.991 | -0.075 [-0.111, -0.041] | +0.301 [+0.256, +0.339] | 10/10 |
| 143,000 | 0.991 | -0.067 [-0.101, -0.033] | +0.297 [+0.243, +0.345] | 10/10 |

Binding reaches 95% of its final value by **step 2,000** and is flat thereafter. PI cost at 3 states is still near zero at that point and keeps growing for more than an order of magnitude more training.

## Why this is not just 'longer context is harder'

The control has the same number of sentences, the same number of previously mentioned values, and the queried binding in the same (final) position. It differs only in whether those earlier mentions bound the queried key. Over training the two move in **opposite directions**:

- `control_3` improves from 0.191 to 0.654
- `update_3` **declines** from its peak 0.451 (step 4,000) to 0.333

General multi-sentence retrieval gets better while overwrite-specific retrieval gets worse. Pretraining is strengthening memory and manufacturing interference at the same time.

## What the errors are

| condition | errors -> obsolete/unbound value | errors -> never-mentioned value |
|---|---|---|
| `update_1` | 0 | 10,449 |
| `update_2` | 28,112 | 6,283 |
| `update_3` | 63,821 | 7,942 |
| `control_2` | 36,470 | 6,542 |
| `control_3` | 44,737 | 8,637 |

Errors are re-retrievals of a superseded binding, not random misses.

Which superseded state comes back, however, is **recency-weighted, not primacy-weighted** — about 70% of intrusions are the most recently overwritten value, not the oldest:

| step | oldest | most recent superseded | fraction oldest |
|---|---|---|---|
| 128 | 1,884 | 1,881 | 0.500 |
| 512 | 1,825 | 1,926 | 0.487 |
| 1,000 | 1,567 | 3,599 | 0.303 |
| 2,000 | 739 | 4,232 | 0.149 |
| 4,000 | 1,325 | 3,705 | 0.263 |
| 8,000 | 1,772 | 3,510 | 0.335 |
| 16,000 | 1,855 | 3,920 | 0.321 |
| 32,000 | 2,198 | 3,776 | 0.368 |
| 64,000 | 2,054 | 4,022 | 0.338 |
| 96,000 | 1,890 | 4,294 | 0.306 |
| 128,000 | 1,792 | 4,164 | 0.301 |
| 143,000 | 1,776 | 4,115 | 0.301 |

This differs from the primacy-biased profile reported for long key-value streams. At three states and 410M the intrusion is the previous value, not the first one. The framing is proactive interference; the error profile is not the one a primacy account predicts, and is reported as found.

## Where the interference actually lives

Splitting `update_3` by candidate slot separates two things that accuracy conflates: telling mentioned values from unmentioned ones, and ordering the mentioned values correctly.

| step | current − unmentioned | current − most-recent obsolete | current − oldest obsolete |
|---|---|---|---|
| 128 | -4.90 | +0.47 | +0.33 |
| 512 | -3.75 | +0.35 | +0.56 |
| 1,000 | +9.03 | +0.11 | +2.73 |
| 2,000 | +13.00 | -0.14 | +3.90 |
| 4,000 | +10.62 | +0.19 | +2.47 |
| 8,000 | +9.69 | +0.16 | +1.59 |
| 16,000 | +9.60 | -0.31 | +1.24 |
| 32,000 | +8.74 | -0.42 | +0.77 |
| 64,000 | +8.15 | -0.54 | +0.78 |
| 96,000 | +8.40 | -0.72 | +0.94 |
| 128,000 | +8.21 | -0.53 | +1.18 |
| 143,000 | +8.29 | -0.42 | +1.29 |

With crossed seed x trial intervals at selected checkpoints:

| step | current − most-recent obsolete | current − unmentioned |
|---|---|---|
| 1,000 | +0.11 [-0.14, +0.37] | +9.03 [+8.12, +9.98] |
| 4,000 | +0.19 [-0.30, +0.62] | +10.62 [+9.87, +11.36] |
| 16,000 | -0.31 [-0.62, +0.00] | +9.60 [+8.90, +10.30] |
| 64,000 | -0.54 [-0.77, -0.31] | +8.15 [+7.78, +8.52] |
| 143,000 | -0.42 [-0.62, -0.19] | +8.29 [+7.68, +9.00] |

**This is the core finding.** The margin over never-mentioned values stays at roughly +8 to +10 bits across the whole of training: retrieval does not degrade, and the model never loses track of which values were in the context at all. What changes is the *ordering among the mentioned values*. The margin over the most recently superseded value starts slightly positive, crosses zero around step 16,000, and becomes reliably negative thereafter — the model ends pretraining **preferring the value it was told to replace**.

Note this is not surface recency: the current value is the *last* thing said, so a positional-recency account predicts the opposite ordering.

## Gates

- **K1** — binding >= 0.75 at the final checkpoint: **PASS** (0.991)
- **K2** — selective interference at 3 states, CI excluding 0, errors preferentially obsolete: **PASS** (+0.297 [+0.243, +0.345], 10/10 seeds)
- **K3** — PI cost has its own trajectory once binding is acquired: **PASS**. Binding is flat from step 2,000 onward while PI cost at 3 states goes -0.012 -> +0.337.

### Honest caveats

- At **two** states the PI cost is *negative*: repeating the queried key twice helps more than the single overwrite hurts. Selective interference appears only at three states. Any claim here is about accumulating overwrites, not about overwriting as such.
- Intrusions are recency-weighted (see above).
- `update_1` is near ceiling from step 2,000, so this study can say when binding *saturates*, not how it is internally organised.
- Candidate-set sizes differ by condition (2 candidates in `update_1`/`control_1`, 3 at two states, 5 at three states), so chance is 0.50, 0.33 and 0.20 respectively. Raw accuracies are therefore **not** comparable across state counts. Every reported contrast — `PI cost` and every margin — is between conditions with identical candidate sets.
- The oldest state appears in a different surface frame (`The X is v1.`) from the later ones (`The X is now v2.`). The oldest-vs-recent asymmetry is therefore partly confounded with that frame. The central contrast, current vs. most-recent-obsolete, is not: both sit in identical `is now` frames.
