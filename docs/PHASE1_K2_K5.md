# Gates K2-K5 - are commitment and recovery acquired at separable times?

Pythia-410M, 10 independent training runs, 12 pre-registered analysis checkpoints (`step0` scored for sanity only, excluded here).

`C` is the commitment interaction at the disambiguator. `B = mean_k max(G_k, 0)` is the residual burden over the post-disambiguation window, with G_k the *population* interaction at post-disambiguator word k, rectified after averaging over items as PREREG.md specifies. `R = B/C` is what a mature reanalyser drives toward 0: it is large when a garden path keeps costing surprisal after the evidence has arrived.


## Does the recovery window have any dynamic range?

A null recovery result is only informative if post-disambiguator spillover is measurable in the first place. Per-position interaction at `step143000`, **crossed seed x item bootstrap** (`*` = 95% CI excludes 0):

| suite | C | G1 | G2 | G3 |
|---|---|---|---|---|
| NP/Z | 6.17* | 0.26* | -0.07 | 0.15 |
| MV/RR | 3.28* | 0.23* | 0.14* | -0.03 |

Spillover at the first post-disambiguator word survives a crossed seed x item bootstrap on both constructions, but only just, and later positions do not survive consistently. The measure is not degenerate, but it is weak: the signal it carries is a fraction of a bit against a disruption of several bits.


## NP/Z (`npz_ambig`, 24 items, 10 seeds)

### Median curves across seeds

| step | C (bits) | B (bits) | R = B/C |
|---|---|---|---|
| 128 | -0.01 | 0.00 | 0.266 |
| 512 | 0.19 | 0.00 | 0.000 |
| 1,000 | 0.49 | 0.02 | 0.035 |
| 2,000 | 2.80 | 0.05 | 0.018 |
| 4,000 | 4.02 | 0.04 | 0.010 |
| 8,000 | 5.12 | 0.08 | 0.016 |
| 16,000 | 5.60 | 0.12 | 0.020 |
| 32,000 | 6.08 | 0.14 | 0.022 |
| 64,000 | 6.45 | 0.16 | 0.026 |
| 96,000 | 6.47 | 0.15 | 0.023 |
| 128,000 | 6.33 | 0.12 | 0.018 |
| 143,000 | 6.29 | 0.15 | 0.023 |


### Per-seed acquisition times

| seed | T_commit | T_recover | R_early | R_late | improvement | D = log2 ratio |
|---|---|---|---|---|---|---|
| 0 | 4,000 | — | 0.013 | 0.032 | -149% | — |
| 1 | 4,000 | — | 0.023 | 0.017 | 27% | — |
| 2 | 4,000 | — | 0.020 | 0.036 | -80% | — |
| 3 | 2,000 | — | 0.022 | 0.013 | 41% | — |
| 4 | 4,000 | — | 0.000 | 0.001 | -372% | — |
| 5 | 4,000 | — | 0.002 | 0.004 | -62% | — |
| 6 | 4,000 | — | 0.027 | 0.025 | 6% | — |
| 7 | 4,000 | — | 0.016 | 0.030 | -89% | — |
| 8 | 4,000 | — | 0.006 | 0.020 | -214% | — |
| 9 | 2,000 | — | 0.008 | 0.043 | -459% | — |

Seeds with a >=30% recovery improvement: **1/10**. Seeds with `T_recover > T_commit`: **0/10**.


### Hierarchical bootstrap (10,000 draws: resample seeds, then items within each resampled seed)

| quantity | median | 95% CI | draws where defined |
|---|---|---|---|
| recovery improvement (early→late) | -28.5% | [-164.6%, 36.2%] | 100.0% |
| D = log2(T_recover / T_commit) | 4.00 | [2.00, 5.58] | 67.9% |
| T_commit (steps) | 4,000 | [2,000, 4,000] | 100.0% |
| T_recover (steps) | 80,000 | [16,000, 96,000] | 67.9% |

> `D` and `T_recover` are undefined in 32% of draws, because in those draws no checkpoint ever cleared the 30% recovery-improvement requirement. The `D` row above is therefore conditioned on the minority of resamples in which a recovery time existed at all, and must not be read as evidence of separation. K3 is reported for completeness but is **void once K2 fails**.

- **K2** (recovery improves >=30%, CI > 0): **FAIL**
- **K3** (median D >= 1, CI > 0): **PASS**
- **K4** (>=8/10 seeds with T_recover > T_commit): **FAIL**

## MV/RR (`mvrr`, 28 items, 10 seeds)

### Median curves across seeds

| step | C (bits) | B (bits) | R = B/C |
|---|---|---|---|
| 128 | -0.01 | 0.01 | 1.763 |
| 512 | 0.02 | 0.04 | 0.656 |
| 1,000 | 0.44 | 0.03 | 0.055 |
| 2,000 | 1.26 | 0.05 | 0.040 |
| 4,000 | 2.34 | 0.08 | 0.030 |
| 8,000 | 2.75 | 0.12 | 0.045 |
| 16,000 | 3.04 | 0.19 | 0.059 |
| 32,000 | 2.91 | 0.20 | 0.072 |
| 64,000 | 3.15 | 0.15 | 0.054 |
| 96,000 | 3.16 | 0.12 | 0.035 |
| 128,000 | 3.16 | 0.13 | 0.040 |
| 143,000 | 3.30 | 0.13 | 0.043 |


### Per-seed acquisition times

| seed | T_commit | T_recover | R_early | R_late | improvement | D = log2 ratio |
|---|---|---|---|---|---|---|
| 0 | 2,000 | 64,000 | 0.061 | 0.035 | 43% | 5.00 |
| 1 | 4,000 | — | 0.014 | 0.020 | -49% | — |
| 2 | 8,000 | 96,000 | 0.057 | 0.019 | 67% | 3.58 |
| 3 | 2,000 | — | 0.029 | 0.070 | -137% | — |
| 4 | 2,000 | — | 0.008 | 0.043 | -426% | — |
| 5 | 4,000 | — | 0.059 | 0.083 | -41% | — |
| 6 | 4,000 | 32,000 | 0.068 | 0.042 | 39% | 3.00 |
| 7 | 4,000 | — | 0.071 | 0.058 | 18% | — |
| 8 | 4,000 | — | 0.050 | 0.042 | 17% | — |
| 9 | 4,000 | — | 0.024 | 0.029 | -20% | — |

Seeds with a >=30% recovery improvement: **3/10**. Seeds with `T_recover > T_commit`: **3/10**.


### Hierarchical bootstrap (10,000 draws: resample seeds, then items within each resampled seed)

| quantity | median | 95% CI | draws where defined |
|---|---|---|---|
| recovery improvement (early→late) | -1.5% | [-104.2%, 42.4%] | 100.0% |
| D = log2(T_recover / T_commit) | 4.00 | [2.79, 5.00] | 90.6% |
| T_commit (steps) | 4,000 | [2,000, 4,000] | 100.0% |
| T_recover (steps) | 64,000 | [32,000, 96,000] | 90.6% |

> `D` and `T_recover` are undefined in 9% of draws, because in those draws no checkpoint ever cleared the 30% recovery-improvement requirement. The `D` row above is therefore conditioned on the minority of resamples in which a recovery time existed at all, and must not be read as evidence of separation. K3 is reported for completeness but is **void once K2 fails**.

- **K2** (recovery improves >=30%, CI > 0): **FAIL**
- **K3** (median D >= 1, CI > 0): **PASS**
- **K4** (>=8/10 seeds with T_recover > T_commit): **FAIL**

## Verdict

- NP/Z: K2 FAIL, K3 PASS, K4 FAIL
- MV/RR: K2 FAIL, K3 PASS, K4 FAIL
- **K5** (both constructions clear K2-K4): **FAIL**

Under the pre-registration this is where the developmental-dissociation story stops. The failing gate is reported as-is; no control is added to rescue it, and no interpretability work follows. Phases 2 and 3 are not run.
