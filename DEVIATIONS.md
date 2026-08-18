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

## D7 — reporting a checkpoint grid, not a continuous time

`T_commit` and `T_recover` can only take values on the 12-checkpoint grid, which
is roughly geometric. `D = log2(T_recover/T_commit)` is therefore coarse: the
smallest non-zero `D` that the grid can express in the dense region is about 1.
This is the reason Phase 3 exists, and it means K3's threshold of `D >= 1` is
the smallest resolvable separation rather than a large effect.
