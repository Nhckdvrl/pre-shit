# 04 — Context use vs. semantic distractor filtering

**Status: all four gates passed. The one topic here still standing.**

> During natural pretraining, does the ability to exploit relevant context emerge
> together with the ability to reject semantically competing context?

![context use vs filtering](figures/fig1_context_use_vs_filtering.png)

All knowledge needed is in the context — there is no parametric-vs-context
conflict, which is a separately studied question and is excluded by design.

**K1** `base` accuracy **0.886** [0.838, 0.920] against chance 0.20; 86.8% of items
eligible, selected on `base` alone.

**K2** `D* = M_unrelated - M_semantic` is **+2.68** (distractor before the relevant
fact) and **+5.05** (after), CIs excluding 0, **10/10 seeds**. Critically the
*indirect* distractor — which names a competing country and never the competing
answer — carries about three quarters of it, so this is not the mentioned-token
copying that sank topic 02.

**K3** Present at both distractor positions; position modulates size, not existence.

**K4** From step 4,000 on, context use grows **x2.22** while the `before`
distractor cost grows **x1.12**. Relative vulnerability falls from 0.89 to 0.45.
The pre-registered confound — the model's own knowledge of the decoy relation —
is dispatched at the item level: **94%** of the trajectory survives controlling
for it.

The claim, stated no more strongly than the data allow: **the two abilities emerge
in the same window and then part company, because context use keeps developing
and the distractor cost does not.** `D*` still grows in absolute terms; the model
never becomes less vulnerable, only relatively so.

Full numbers and the remaining caveat: `docs/PHASE_A.md`. Protocol: `PREREG.md`.

```bash
./code/fetch_data.sh
../env/bin/python code/build_stimuli.py
../env/bin/python code/score.py --seeds 0,1,2,3,4,5,6,7,8,9 \
    --steps 128,512,1000,2000,4000,8000,16000,32000,64000,96000,128000,143000
../env/bin/python code/report.py && ../env/bin/python code/plot.py
```
