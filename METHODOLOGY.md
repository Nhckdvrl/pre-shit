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

4. **Ask what the metric returns under the null.** Any rectification, `max`,
   ratio or normalisation gets an explicit answer to "what does this produce when
   there is no effect?" before it is used. `max(G,0)` and `B/C` both failed this.

5. **Track the control's own trajectory, not just the difference.** In 03 the
   difference grew entirely because the control improved. A contrast whose two
   arms are never plotted separately can hide this completely.

6. **A claim in a README is a result.** It gets checked like one, and when it is
   wrong it gets an explicit retraction in place, not a quiet edit.

7. **An effect that only exists against one control is not an effect.** Budget
   for two independent controls per claim from the start.
