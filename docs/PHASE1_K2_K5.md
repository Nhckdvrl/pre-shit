# Gates K2-K5 - are commitment and recovery acquired at separable times?

Pythia-410M, 10 independent training runs, 12 pre-registered analysis checkpoints (`step0` scored for sanity only, excluded here).

`C` is the commitment interaction at the disambiguator. `B = mean_k max(G_k, 0)` is the residual burden over the post-disambiguation window, using the identical 2x2 interaction. `R = B/C` is what a mature reanalyser drives toward 0: it is large when a garden path keeps costing surprisal after the evidence has arrived.


## Does the recovery window have any dynamic range?

A null recovery result is only informative if post-disambiguator spillover is measurable in the first place. Per-position interaction at `step143000`, pooled over seeds, item-level bootstrap (`*` = 95% CI excludes 0):

| suite | C | G1 | G2 | G3 |
|---|---|---|---|---|
| NP/Z | 6.17* | 0.26* | -0.07 | 0.15* |
| MV/RR | 3.28* | 0.23* | 0.14* | -0.03 |

Spillover at the first post-disambiguator word is real and reliably positive, but it is only a few percent of the disruption at the disambiguator itself. The measure is not degenerate: it has range, and the range is small.


## NP/Z (`npz_ambig`, 24 items, 10 seeds)

### Median curves across seeds

| step | C (bits) | B (bits) | R = B/C |
|---|---|---|---|
| 128 | -0.01 | 0.01 | 2.682 |
| 512 | 0.19 | 0.02 | 0.124 |
| 1,000 | 0.49 | 0.10 | 0.160 |
| 2,000 | 2.80 | 0.17 | 0.061 |
| 4,000 | 4.02 | 0.19 | 0.044 |
| 8,000 | 5.12 | 0.32 | 0.064 |
| 16,000 | 5.60 | 0.37 | 0.063 |
| 32,000 | 6.08 | 0.44 | 0.074 |
| 64,000 | 6.45 | 0.41 | 0.063 |
| 96,000 | 6.47 | 0.44 | 0.065 |
| 128,000 | 6.33 | 0.43 | 0.068 |
| 143,000 | 6.29 | 0.47 | 0.074 |


### Per-seed acquisition times

| seed | T_commit | T_recover | R_early | R_late | improvement | D = log2 ratio |
|---|---|---|---|---|---|---|
| 0 | 4,000 | — | 0.064 | 0.073 | -15% | — |
| 1 | 4,000 | — | 0.054 | 0.053 | 2% | — |
| 2 | 4,000 | — | 0.072 | 0.081 | -14% | — |
| 3 | 2,000 | — | 0.072 | 0.058 | 20% | — |
| 4 | 4,000 | — | 0.057 | 0.050 | 12% | — |
| 5 | 4,000 | — | 0.039 | 0.045 | -15% | — |
| 6 | 4,000 | — | 0.074 | 0.076 | -3% | — |
| 7 | 4,000 | — | 0.062 | 0.070 | -13% | — |
| 8 | 4,000 | — | 0.037 | 0.073 | -97% | — |
| 9 | 2,000 | — | 0.045 | 0.090 | -98% | — |

Seeds with a >=30% recovery improvement: **0/10**. Seeds with `T_recover > T_commit`: **0/10**.


### Hierarchical bootstrap (10,000 draws: resample seeds, then items within each resampled seed)

| quantity | median | 95% CI | draws where defined |
|---|---|---|---|
| recovery improvement (early→late) | -13.6% | [-49.7%, 8.5%] | 100.0% |
| D = log2(T_recover / T_commit) | 4.50 | [2.00, 6.00] | 43.0% |
| T_commit (steps) | 4,000 | [2,000, 4,000] | 100.0% |
| T_recover (steps) | 96,000 | [16,000, 143,000] | 43.0% |

> `D` and `T_recover` are undefined in 57% of draws, because in those draws no checkpoint ever cleared the 30% recovery-improvement requirement. The `D` row above is therefore conditioned on the minority of resamples in which a recovery time existed at all, and must not be read as evidence of separation. K3 is reported for completeness but is **void once K2 fails**.

- **K2** (recovery improves >=30%, CI > 0): **FAIL**
- **K3** (median D >= 1, CI > 0): **PASS**
- **K4** (>=8/10 seeds with T_recover > T_commit): **FAIL**

## MV/RR (`mvrr`, 28 items, 10 seeds)

### Median curves across seeds

| step | C (bits) | B (bits) | R = B/C |
|---|---|---|---|
| 128 | -0.01 | 0.03 | 7.063 |
| 512 | 0.02 | 0.07 | 1.419 |
| 1,000 | 0.44 | 0.09 | 0.192 |
| 2,000 | 1.26 | 0.13 | 0.104 |
| 4,000 | 2.34 | 0.21 | 0.085 |
| 8,000 | 2.75 | 0.26 | 0.096 |
| 16,000 | 3.04 | 0.36 | 0.109 |
| 32,000 | 2.91 | 0.35 | 0.132 |
| 64,000 | 3.15 | 0.36 | 0.116 |
| 96,000 | 3.16 | 0.34 | 0.102 |
| 128,000 | 3.16 | 0.34 | 0.107 |
| 143,000 | 3.30 | 0.33 | 0.100 |


### Per-seed acquisition times

| seed | T_commit | T_recover | R_early | R_late | improvement | D = log2 ratio |
|---|---|---|---|---|---|---|
| 0 | 2,000 | — | 0.121 | 0.105 | 13% | — |
| 1 | 4,000 | — | 0.077 | 0.073 | 5% | — |
| 2 | 8,000 | 96,000 | 0.118 | 0.069 | 41% | 3.58 |
| 3 | 2,000 | — | 0.073 | 0.128 | -76% | — |
| 4 | 2,000 | — | 0.063 | 0.093 | -46% | — |
| 5 | 4,000 | — | 0.104 | 0.143 | -36% | — |
| 6 | 4,000 | — | 0.103 | 0.098 | 5% | — |
| 7 | 4,000 | — | 0.113 | 0.122 | -8% | — |
| 8 | 4,000 | — | 0.108 | 0.102 | 5% | — |
| 9 | 4,000 | — | 0.093 | 0.106 | -14% | — |

Seeds with a >=30% recovery improvement: **1/10**. Seeds with `T_recover > T_commit`: **1/10**.


### Hierarchical bootstrap (10,000 draws: resample seeds, then items within each resampled seed)

| quantity | median | 95% CI | draws where defined |
|---|---|---|---|
| recovery improvement (early→late) | -8.6% | [-47.0%, 16.3%] | 100.0% |
| D = log2(T_recover / T_commit) | 4.16 | [3.00, 5.37] | 72.5% |
| T_commit (steps) | 4,000 | [2,000, 4,000] | 100.0% |
| T_recover (steps) | 96,000 | [64,000, 143,000] | 72.5% |

> `D` and `T_recover` are undefined in 27% of draws, because in those draws no checkpoint ever cleared the 30% recovery-improvement requirement. The `D` row above is therefore conditioned on the minority of resamples in which a recovery time existed at all, and must not be read as evidence of separation. K3 is reported for completeness but is **void once K2 fails**.

- **K2** (recovery improves >=30%, CI > 0): **FAIL**
- **K3** (median D >= 1, CI > 0): **PASS**
- **K4** (>=8/10 seeds with T_recover > T_commit): **FAIL**

## Verdict

- NP/Z: K2 FAIL, K3 PASS, K4 FAIL
- MV/RR: K2 FAIL, K3 PASS, K4 FAIL
- **K5** (both constructions clear K2-K4): **FAIL**

Under the pre-registration this is where the developmental-dissociation story stops. The failing gate is reported as-is; no control is added to rescue it, and no interpretability work follows. Phases 2 and 3 are not run.
