# Gate K0 / K1 — does the garden-path effect exist at all, and across seeds?

Checkpoint `step143000` (end of pretraining), Pythia-410M, 10 independent training runs (`pythia-410m` = seed 0, PolyPythias `-seed1..9`).

**Measure.** Commitment `C` = the 2x2 interaction at the disambiguator,

```
C = [S(ambig, cue absent) - S(ambig, cue present)]
  - [S(unambig, cue absent) - S(unambig, cue present)]
```

in bits, one value per item. A bare comma effect or a bare reduced-relative effect cancels out of this contrast; only the *extra* difficulty the early cue removes specifically in the ambiguous condition survives.

**Pass rule (pre-registered).** A seed passes if its item-level paired-bootstrap 95% CI excludes 0 and at least 65% of items are positive. K0 = seed 0 passes on both primary suites; K1 = at least 8/10 seeds pass on both.


## Primary suites (SyntaxGym)


### NP/Z (`npz_ambig`, 24 items)

| seed | mean C (bits) | 95% CI | items positive | passes |
|---|---|---|---|---|
| 0 | 6.26 | [4.50, 8.04] | 92% (22/24) | yes |
| 1 | 6.84 | [5.33, 8.34] | 96% (23/24) | yes |
| 2 | 6.92 | [5.26, 8.45] | 92% (22/24) | yes |
| 3 | 5.84 | [4.27, 7.44] | 92% (22/24) | yes |
| 4 | 4.41 | [2.73, 6.06] | 83% (20/24) | yes |
| 5 | 5.60 | [3.88, 7.28] | 96% (23/24) | yes |
| 6 | 7.04 | [5.40, 8.66] | 96% (23/24) | yes |
| 7 | 6.32 | [4.82, 7.81] | 92% (22/24) | yes |
| 8 | 6.50 | [4.82, 8.08] | 92% (22/24) | yes |
| 9 | 5.96 | [4.52, 7.39] | 96% (23/24) | yes |


Seeds passing: **10/10**. Across-seed mean C = 6.17 bits (range 4.41–7.04).


### MV/RR (`mvrr`, 28 items)

| seed | mean C (bits) | 95% CI | items positive | passes |
|---|---|---|---|---|
| 0 | 2.99 | [1.84, 4.18] | 79% (22/28) | yes |
| 1 | 3.62 | [2.59, 4.64] | 86% (24/28) | yes |
| 2 | 3.56 | [2.34, 4.77] | 75% (21/28) | yes |
| 3 | 3.12 | [2.11, 4.16] | 82% (23/28) | yes |
| 4 | 2.70 | [1.77, 3.61] | 75% (21/28) | yes |
| 5 | 2.60 | [1.37, 3.85] | 71% (20/28) | yes |
| 6 | 4.11 | [2.75, 5.51] | 79% (22/28) | yes |
| 7 | 3.44 | [2.18, 4.70] | 79% (22/28) | yes |
| 8 | 3.44 | [2.06, 4.87] | 75% (21/28) | yes |
| 9 | 3.16 | [1.89, 4.48] | 75% (21/28) | yes |


Seeds passing: **10/10**. Across-seed mean C = 3.28 bits (range 2.60–4.11).


## External replication sets


### Christianson 2001 (`Christianson_2001`, 24 items)

| seed | mean C (bits) | 95% CI | items positive | passes |
|---|---|---|---|---|
| 0 | 8.32 | [7.31, 9.27] | 100% (24/24) | yes |
| 1 | 7.32 | [6.42, 8.21] | 100% (24/24) | yes |
| 2 | 7.50 | [6.30, 8.65] | 100% (24/24) | yes |
| 3 | 7.95 | [6.93, 8.87] | 100% (24/24) | yes |
| 4 | 6.22 | [5.44, 6.97] | 100% (24/24) | yes |
| 5 | 8.12 | [7.11, 9.02] | 100% (24/24) | yes |
| 6 | 9.16 | [8.04, 10.22] | 100% (24/24) | yes |
| 7 | 8.90 | [7.76, 9.99] | 100% (24/24) | yes |
| 8 | 7.20 | [6.10, 8.30] | 100% (24/24) | yes |
| 9 | 7.62 | [6.25, 8.98] | 100% (24/24) | yes |


Seeds passing: **10/10**. Across-seed mean C = 7.83 bits (range 6.22–9.16).


### Alternates 2022 (`Alternates_2022`, 24 items)

| seed | mean C (bits) | 95% CI | items positive | passes |
|---|---|---|---|---|
| 0 | 7.67 | [6.50, 8.77] | 100% (24/24) | yes |
| 1 | 7.55 | [6.57, 8.48] | 100% (24/24) | yes |
| 2 | 7.47 | [6.32, 8.58] | 100% (24/24) | yes |
| 3 | 7.18 | [6.14, 8.18] | 100% (24/24) | yes |
| 4 | 6.69 | [5.77, 7.62] | 100% (24/24) | yes |
| 5 | 7.83 | [6.78, 8.85] | 100% (24/24) | yes |
| 6 | 8.44 | [7.33, 9.55] | 100% (24/24) | yes |
| 7 | 7.96 | [6.91, 9.04] | 100% (24/24) | yes |
| 8 | 6.56 | [5.53, 7.58] | 96% (23/24) | yes |
| 9 | 7.29 | [6.01, 8.53] | 100% (24/24) | yes |


Seeds passing: **10/10**. Across-seed mean C = 7.46 bits (range 6.56–8.44).


## Local-4-word context (preview of K7)

The same contrast with only the 4 preceding words as context. This is not the K7 decision — that needs the full dynamics — but it shows the baseline is live.


| suite | full context | local-4 | local-4 / full |
|---|---|---|---|
| NP/Z | 6.17 | 2.74 | 44% |
| MV/RR | 3.28 | 0.11 | 3% |
| Christianson 2001 | 7.83 | -0.00 | -0% |
| Alternates 2022 | 7.46 | 0.00 | 0% |

## Verdict

- **K0** (original Pythia-410M passes on both NP/Z and MV/RR): **PASS**
- **K1** (>=8/10 seeds pass on both): **PASS**

Both gates pass. Proceed to Phase 1: score the 12-checkpoint grid on all 10 seeds and evaluate K2–K5.
