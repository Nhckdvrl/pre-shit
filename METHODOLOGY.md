# What killed 01, 02 and 03 — and the rules that follow

Three topics died. In none of them was the model or the data at fault. **All three
failures were in the comparison**: the contrast I computed was not the single
thing I had named it.

| topic | what I claimed to measure | what the number actually contained |
|---|---|---|
| 01 | residual garden-path burden `B` | positive mass left by rectifying item-level noise; `B` could track `C` through variance alone |
| 02 | semantic filtering `F` | a log-space ceiling artifact, correlated `-0.48` with parametric knowledge in the wrong direction |
| 03 | overwrite-specific interference | a control that was easy for an unrelated reason and got easier as the model learned category type constraints |

Two of the three I did not catch myself. In 01 and 03 I also **wrote down a claim
I had not verified** — that the CI gate was applied on real data when the code
never called it, and that the control "differed only in whether those mentions
overwrote the queried key" when it differed in four ways.

## Rules for every topic from here

1. **Run the tightest matched control first, at the final checkpoint, before any
   dynamics.** 03 cost a 12-checkpoint x 10-seed grid on a contrast that one
   control erased. The adversarial control is Phase A, not Phase C.

2. **Write the difference table before scoring.** One row per condition, one
   column per dimension on which conditions could differ (tokens, length,
   category, position, candidate set, repetition count, surface frame). Every
   column except the target must be constant, or the effect is not attributable
   to the target. No condition pair ships without this table.

3. **Never write "differs only in X"** unless that table exists and is in the repo.

4. **Ask what the metric returns under the null — including derived quantities.**
   Any rectification, `max`, ratio or normalisation gets an explicit answer to
   "what does this produce when there is no effect?" before it is used.
   `max(G,0)` and `B/C` both failed this. Topic 04 failed it a second way: the
   null was correctly stated for `D*` and then never asked of `D*/M_base`, the
   ratio the claim actually rested on. A large intercept and a sub-unit slope
   make a falling ratio the *null*, not the effect. Every quantity a claim rests
   on, including ones formed downstream, needs its null stated before use.

5. **Track the control's own trajectory, not just the difference.** In 03 the
   difference grew entirely because the control improved. A contrast whose two
   arms are never plotted separately can hide this completely.

6. **A claim in a README is a result.** It gets checked like one, and when it is
   wrong it gets an explicit retraction in place, not a quiet edit.

7. **An effect that only exists against one control is not an effect.** Budget
   for two independent controls per claim from the start.

## Rule 8 — a checkpoint must explain something competence cannot

This rule exists because topics 01-04 died four different deaths that were all the
same death: a "developmental dissociation" that turned out to be a function of one
underlying quantity, with training step adding nothing.

Before any dynamics claim, fit the **checkpoint-free null** first:

    M0:  Y = f(X)

where `X` contains every reasonable measure of overall competence, confidence and
prerequisite ability that could drive `Y`. Then fit

    M1:  Y = f(X, t)

and compare them by **leave-one-checkpoint-out** cross-validation. `t` may be
called a learning dynamic only if all of the following hold:

* `M1` predicts a held-out checkpoint materially better than `M0`;
* the improvement's bootstrap CI excludes 0;
* at least 8/10 seeds agree in direction;
* the effect is not an artifact of a ratio or normalisation (rule 4).

Otherwise the honest statement is that the model is moving along a fixed
competence manifold, and training stage is not doing explanatory work.

Concretely, this would have killed topic 04 at Phase A instead of Phase C: a
single line `D* = 1.64 + 0.22*M_base`, fitted with no step term, already reproduced
the entire result.
