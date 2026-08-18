# Metric audit of the Phase 1 recovery result

No model was re-run. Everything below is recomputed from the stored per-checkpoint surprisals.

## Defects found on review

| # | defect | effect |
|---|---|---|
| F1 | `B` rectified `max(G_k, 0)` **per item**, but `PREREG.md` defines `G_k(t)` as the population interaction, so the rectification belongs at the population level | inflates `B` whenever item-level interactions are noisy, and can make `B` track `C` through variance alone |
| F2 | the sustain rule clipped its window at the end of the grid, so the final checkpoint needed 1 True to count as '3 sustained' | makes late `T_recover` easier to define |
| F3 | the Phase 1 path (`observed` -> `times_from_curves`) never applied the commitment CI gate, although `DEVIATIONS.md` D6 states it is applied on real data | `T_commit` was not computed as pre-registered |
| F4 | per-position `G_k` significance pooled 10 seeds x items into one item-level bootstrap | pseudo-replication; overstates the evidence that spillover is reliably positive |

## How large is the rectification bias?

Population-level signed interaction vs. the rectified quantity actually used, at `step143000`, median over seeds:

| suite | signed mean_k G_k | rect_pop | rect_item (used in Phase 1) | inflation |
|---|---|---|---|---|
| npz_ambig | 0.125 | 0.153 | 0.471 | 3.8x |
| mvrr | 0.099 | 0.127 | 0.333 | 3.4x |

## Per-position interaction with a crossed seed x item bootstrap (F4)

`*` = 95% CI excludes 0. The pooled column is the Phase 1 (pseudo-replicated) interval, shown for comparison.

| suite | position | mean (bits) | crossed CI | pooled CI (wrong) |
|---|---|---|---|---|
| npz_ambig | C | 6.169* | [5.466, 6.839] | [5.639, 6.685] |
| npz_ambig | G1 | 0.263* | [0.053, 0.486] | [0.091, 0.443] |
| npz_ambig | G2 | -0.074 | [-0.205, 0.050] | [-0.176, 0.028] |
| npz_ambig | G3 | 0.146 | [-0.031, 0.318] | [0.018, 0.273] |
| mvrr | C | 3.275* | [2.813, 3.753] | [2.899, 3.649] |
| mvrr | G1 | 0.226* | [0.057, 0.412] | [0.078, 0.382] |
| mvrr | G2 | 0.136* | [0.013, 0.259] | [0.045, 0.228] |
| mvrr | G3 | -0.025 | [-0.106, 0.056] | [-0.089, 0.039] |

## Recovery trajectory under every burden definition

`R = B/C`, median over the 10 seeds, with the commitment CI gate (F3) and the corrected sustain rule (F2) applied throughout.


### npz_ambig — 24 items

| step | C | R_rect_item | R_rect_pop | R_signed | R_auc | R_g1 |
|---|---|---|---|---|---|---|
| 128 | -0.01 | — | — | — | — | — |
| 512 | 0.19 | — | — | — | — | — |
| 1,000 | 0.49 | +0.142 | +0.033 | +0.007 | +0.022 | -0.028 |
| 2,000 | 2.80 | +0.061 | +0.018 | +0.004 | +0.013 | +0.034 |
| 4,000 | 4.02 | +0.044 | +0.010 | -0.004 | -0.011 | +0.021 |
| 8,000 | 5.12 | +0.064 | +0.016 | +0.008 | +0.024 | +0.008 |
| 16,000 | 5.60 | +0.063 | +0.020 | +0.009 | +0.028 | +0.028 |
| 32,000 | 6.08 | +0.074 | +0.022 | +0.016 | +0.048 | +0.036 |
| 64,000 | 6.45 | +0.063 | +0.026 | +0.013 | +0.038 | +0.042 |
| 96,000 | 6.47 | +0.065 | +0.023 | +0.011 | +0.034 | +0.039 |
| 128,000 | 6.33 | +0.068 | +0.018 | +0.014 | +0.043 | +0.035 |
| 143,000 | 6.29 | +0.074 | +0.023 | +0.020 | +0.059 | +0.045 |

| variant | T_commit (median) | seeds with improvement >=30% | median improvement | seeds with T_recover > T_commit |
|---|---|---|---|---|
| rect_item | 4,000 | 0/10 | -13.2% | 0/10 |
| rect_pop | 4,000 | 1/10 | -84.8% | 0/10 |
| signed | 4,000 | 0/10 | -47.6% | 0/10 |
| auc | 4,000 | 0/10 | -47.6% | 0/10 |
| g1 | 4,000 | 1/10 | +23.5% | 1/10 |

### npz_ambig (strict 3-word window) — 12 items

| step | C | R_rect_item | R_rect_pop | R_signed | R_auc | R_g1 |
|---|---|---|---|---|---|---|
| 128 | -0.00 | — | — | — | — | — |
| 512 | 0.23 | — | — | — | — | — |
| 1,000 | 0.53 | +0.158 | +0.038 | +0.033 | +0.098 | +0.060 |
| 2,000 | 2.95 | +0.050 | +0.022 | +0.013 | +0.039 | +0.037 |
| 4,000 | 3.99 | +0.062 | +0.026 | +0.018 | +0.055 | +0.068 |
| 8,000 | 4.63 | +0.060 | +0.023 | +0.022 | +0.066 | +0.067 |
| 16,000 | 5.49 | +0.062 | +0.029 | +0.026 | +0.078 | +0.044 |
| 32,000 | 6.36 | +0.060 | +0.035 | +0.031 | +0.092 | +0.056 |
| 64,000 | 6.46 | +0.061 | +0.029 | +0.024 | +0.073 | +0.061 |
| 96,000 | 6.59 | +0.054 | +0.027 | +0.025 | +0.075 | +0.057 |
| 128,000 | 6.67 | +0.057 | +0.025 | +0.024 | +0.072 | +0.053 |
| 143,000 | 6.71 | +0.059 | +0.034 | +0.033 | +0.098 | +0.061 |

| variant | T_commit (median) | seeds with improvement >=30% | median improvement | seeds with T_recover > T_commit |
|---|---|---|---|---|
| rect_item | 4,000 | 0/10 | +5.7% | 0/10 |
| rect_pop | 4,000 | 2/10 | -1.1% | 1/10 |
| signed | 4,000 | 3/10 | +2.3% | 1/10 |
| auc | 4,000 | 3/10 | +2.3% | 1/10 |
| g1 | 4,000 | 3/10 | +6.7% | 1/10 |

### mvrr — 28 items

| step | C | R_rect_item | R_rect_pop | R_signed | R_auc | R_g1 |
|---|---|---|---|---|---|---|
| 128 | -0.01 | — | — | — | — | — |
| 512 | 0.02 | — | — | — | — | — |
| 1,000 | 0.44 | +0.177 | +0.057 | +0.023 | +0.070 | +0.172 |
| 2,000 | 1.26 | +0.104 | +0.040 | +0.016 | +0.049 | +0.085 |
| 4,000 | 2.34 | +0.085 | +0.030 | +0.026 | +0.078 | +0.065 |
| 8,000 | 2.75 | +0.096 | +0.045 | +0.033 | +0.100 | +0.112 |
| 16,000 | 3.04 | +0.109 | +0.059 | +0.058 | +0.173 | +0.109 |
| 32,000 | 2.91 | +0.132 | +0.072 | +0.072 | +0.217 | +0.116 |
| 64,000 | 3.15 | +0.116 | +0.054 | +0.045 | +0.135 | +0.119 |
| 96,000 | 3.16 | +0.102 | +0.035 | +0.035 | +0.106 | +0.056 |
| 128,000 | 3.16 | +0.107 | +0.040 | +0.035 | +0.105 | +0.058 |
| 143,000 | 3.30 | +0.100 | +0.043 | +0.030 | +0.091 | +0.064 |

| variant | T_commit (median) | seeds with improvement >=30% | median improvement | seeds with T_recover > T_commit |
|---|---|---|---|---|
| rect_item | 4,000 | 1/10 | -1.7% | 1/10 |
| rect_pop | 4,000 | 3/10 | -1.4% | 3/10 |
| signed | 4,000 | 4/10 | +18.5% | 4/10 |
| auc | 4,000 | 4/10 | +18.5% | 4/10 |
| g1 | 4,000 | 5/10 | +41.4% | 4/10 |

### mvrr (strict 3-word window) — 23 items

| step | C | R_rect_item | R_rect_pop | R_signed | R_auc | R_g1 |
|---|---|---|---|---|---|---|
| 128 | -0.01 | — | — | — | — | — |
| 512 | 0.05 | — | — | — | — | — |
| 1,000 | 0.41 | +0.138 | +0.046 | +0.004 | +0.011 | +0.139 |
| 2,000 | 1.19 | +0.105 | +0.049 | +0.017 | +0.050 | +0.113 |
| 4,000 | 2.20 | +0.097 | +0.034 | +0.030 | +0.090 | +0.081 |
| 8,000 | 2.76 | +0.104 | +0.056 | +0.048 | +0.143 | +0.152 |
| 16,000 | 2.97 | +0.122 | +0.074 | +0.067 | +0.202 | +0.139 |
| 32,000 | 2.87 | +0.139 | +0.084 | +0.081 | +0.244 | +0.167 |
| 64,000 | 3.25 | +0.123 | +0.068 | +0.058 | +0.174 | +0.176 |
| 96,000 | 3.15 | +0.112 | +0.047 | +0.041 | +0.122 | +0.071 |
| 128,000 | 3.13 | +0.110 | +0.050 | +0.050 | +0.150 | +0.079 |
| 143,000 | 3.41 | +0.106 | +0.051 | +0.044 | +0.132 | +0.099 |

| variant | T_commit (median) | seeds with improvement >=30% | median improvement | seeds with T_recover > T_commit |
|---|---|---|---|---|
| rect_item | 4,000 | 1/10 | -4.2% | 1/10 |
| rect_pop | 4,000 | 3/10 | +1.9% | 3/10 |
| signed | 4,000 | 3/10 | +3.7% | 3/10 |
| auc | 4,000 | 3/10 | +3.7% | 3/10 |
| g1 | 4,000 | 5/10 | +35.4% | 4/10 |
