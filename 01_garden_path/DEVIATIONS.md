# Deviations and forced design decisions

Each entry was settled **before** any dynamics result was computed, and is
recorded here because the original protocol did not anticipate the data.

## D1 — the 3-word recovery window is not always available

The protocol fixes the recovery window at the first 3 post-disambiguator words.
SyntaxGym's region 6 is the sentence remainder and is often shorter than that.
Words available after the disambiguator, counted per item as the minimum across
the item's four conditions:

| suite | 0 words | 1 | 2 | >=3 |
|---|---|---|---|---|
| `npz_ambig` (24 items) | 0 | 2 | 10 | 12 |
| `mvrr` (28 items) | 1 | 1 | 3 | 23 |
| Christianson 2001 (24) | 0 | 6 | 4 | 14 |
| Alternates 2022 (24) | 0 | 7 | 7 | 10 |

**Decision.** The window is the first `min(3, available)` words of that item, and
`B = mean_k max(G_k, 0)` averages over exactly the positions that exist. Every
item therefore contributes one `B` value, and the window is a property of the
item, never of the result. Restricting to the strict 3-word subset would leave
NP/Z with 12 items, which is too few to carry a primary gate; that subset is
still reported as a robustness check.

## D2 — `mvrr` item 27 is malformed upstream

In `mvrr` item 27 the `unreduced_ambig` condition ends at the disambiguator
("The airplane that was landed in the mountains broke down") while the other
three conditions continue ("... broke down during the ice storm"). The recovery
interaction is undefined for this item.

**Decision.** Item 27 is excluded from the recovery analysis and retained for the
commitment analysis, where region 5 is intact and identical across conditions.
MV/RR is therefore 28 items for `C` and 27 for `B`/`R`.

## D3 — checkpoint count

The protocol text says 13 analysis checkpoints but lists 12. The 12 listed steps
are used; `step0` is scored as a sanity check only and never enters `T_commit`
or `T_recover`.

## D4 — the local-4 baseline is degenerate on the external sets

In Christianson 2001 and Alternates 2022 the disambiguating comma sits more than
four words before the matrix verb, so the GP and control sentences have
*identical* 4-word local contexts and the local-4 garden-path effect is exactly
0 by construction. K7 is therefore evaluated on the SyntaxGym suites. There the
baseline is informative: for NP/Z the comma falls inside the 4-word window, and
for MV/RR the reduction manipulation partly does.

## D5 — surprisal units and context

Surprisal is reported in **bits** (log base 2), and `<|endoftext|>` is prepended
as context so that the first word of every sentence is scorable. Models are run
in float32 rather than bfloat16, because the effects of interest are of the order
of a few bits and bf16 rounding is not obviously negligible at that scale.

## D6 — the commitment gate inside the hierarchical bootstrap

The commitment gate requires the item-level paired-bootstrap CI of `C` to exclude
0. Evaluating that *inside* each of the 10,000 hierarchical draws would mean a
nested bootstrap (10,000 x 10 seeds x an inner resample per checkpoint).

**Decision.** On the real data the gate is applied exactly as pre-registered,
including the nested CI. Inside the hierarchical bootstrap the criterion is
reduced to its point form `C > 0` (the other two clauses, `C >= 0.5*C_late` and
the 3-checkpoint sustain rule, are unchanged). The outer resampling already
carries the sampling uncertainty that the inner interval would express, so this
is a computational simplification, not a loosening of the gate.

> **Correction, 2026-08-19.** As originally written this entry was false. The
> Phase 1 report path (`report.py` -> `dynamics.observed` -> `times_from_curves`)
> never called the CI gate on real data either; the correct implementation existed
> in `analyze.seed_trajectory` but was not the one the report used. Fixed in
> `dynamics.ci_gate`, now applied on real data as this entry always claimed. The
> corrected `T_commit` is unchanged at a median of 4,000 steps on both suites,
> so the defect did not affect any conclusion — but the document asserted a
> property the code did not have, which is worse than a wrong number.

## D7 — reporting a checkpoint grid, not a continuous time

`T_commit` and `T_recover` can only take values on the 12-checkpoint grid, which
is roughly geometric. `D = log2(T_recover/T_commit)` is therefore coarse: the
smallest non-zero `D` that the grid can express in the dense region is about 1.
This is the reason Phase 3 exists, and it means K3's threshold of `D >= 1` is
the smallest resolvable separation rather than a large effect.


## D8 — the burden was rectified at the wrong level (found on review, after Phase 1)

`PREREG.md` defines

    B(t) = mean_k max(G_k(t), 0)

where `G_k(t)` is the **population** interaction at post-disambiguator word `k`:
it is a function of the checkpoint, not of the item. The Phase 1 implementation
instead rectified per item and then averaged:

    B = mean_i mean_k max(G_ki, 0)          # what was computed
    B = mean_k max(mean_i G_ki, 0)          # what PREREG.md specifies

Rectifying inside the item loop makes `B` strictly positive whenever item-level
interactions are merely noisy, and — the serious risk — lets `B` track `C`
through item-level *variance* alone, which would manufacture the flat `R = B/C`
that Phase 1 reported. Measured inflation at `step143000` was **3.8x** (NP/Z) and
**3.4x** (MV/RR) relative to the signed population mean.

**Decision.** Fixed to the pre-registered population-level form, and the audit in
`docs/AUDIT_PHASE1.md` re-runs the trajectory under five burden definitions
(`rect_pop`, `rect_item`, `signed`, `auc`, `g1`) and on the strict 3-word subset,
so that the conclusion can be checked against the choice rather than resting on
it. The verdict is unchanged under every variant.

## D9 — sustain rule at the tail of the grid

`_first_sustained` clipped its window at the end of the array, so the last
checkpoint needed one `True` to count as "sustained over 3". Fixed to require a
full 3-long window, which means the final two checkpoints can no longer be
acquisition times. `T_commit` is unaffected; this only ever mattered for late
`T_recover`.

## D10 — per-position significance used a pooled bootstrap

The Phase 1 "does the measure have range" check bootstrapped 10 seeds x 24 items
as one flat item-level sample — the pseudo-replication `PREREG.md` explicitly
forbids. Replaced with a crossed seed x item bootstrap
(`dynamics.crossed_bootstrap_mean`). `G1` remains positive on both constructions
under the correct interval, but more narrowly, and NP/Z's `G3` no longer clears 0.

## D11 — strict 3-word robustness check, promised in D1

D1 promised the strict 3-word subset as a robustness check and Phase 1 did not
report it. It is now in `docs/AUDIT_PHASE1.md` (NP/Z 12 items, MV/RR 23 items).
