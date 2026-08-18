# Deviations — topic 02

## D1 — LRE "47 relations" is the full set; the factual subset is 26

`PREREG.md` was written expecting the 47 relations of LRE. 47 is the total across
all four LRE categories (factual, commonsense, bias, linguistic). The
entrainment setting needs subject-object facts with a parametric answer, i.e. the
**factual** subset: 26 relations, 9,696 pairs, capped at 40 pairs per relation
with a fixed seed -> 898 items.

## D2 — an unseen-random control was added before any seed beyond 0 was scored

`E_copy = D_d^random` as pre-registered cannot separate "this token was copied
because it was in context" from "random nouns became likelier overall at this
checkpoint" — a real risk when comparing checkpoints whose output distributions
differ in sharpness. A second random noun that appears in **no** context is now
scored in every condition, and copying is the difference:

    E_copy = [l_random(d) - l_none(d)] - [l_random(ctrl) - l_none(ctrl)]

At `step143000` the seen word gains +5.39 bits and the unseen control +0.64, so
the control is doing real work. This tightens the gate rather than loosening it.

## D3 — the pre-registered `F` is confounded with `K` by construction

`F = (D_g - D_d)^counterfactual` correlates **-0.48** with the parametric
knowledge margin `K`, and in the wrong direction: `F` is *more* negative when the
model knows the fact *better*. This is a ceiling artifact, not resistance — a
gold object that is already near-certain without context has little room to gain
and much to lose, while a distractor that was near-impossible has enormous room
to gain.

**Decision.** Resistance is reported as the post-context margin
`l_cf(gold) - l_cf(distractor)` on items with `K > 0` — does the model still
prefer the truth after being told otherwise. Its correlation with `K` is +0.11.
`F` is still reported alongside, so the two can be compared.

This change was made after seeing `step143000` and **before any other checkpoint
was scored**, so it cannot have been tuned to produce a trajectory. It is
declared here rather than quietly substituted.
