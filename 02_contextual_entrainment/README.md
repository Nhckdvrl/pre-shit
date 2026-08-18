# 02 — Mechanical copying vs. semantic filtering

**Status: killed at Phase A.**

> Models scale toward stronger semantic filtering but stronger mechanical copying.
> When during pretraining do these two opposing forms of context sensitivity emerge?

At Pythia-410M only one of the two behaviours exists. Contextual entrainment of
semantically inert tokens is large and unambiguous (`E_copy = +4.75` bits,
control-corrected, 10/10 seeds). Resistance to a false claim is at floor: on facts
the model gets right without context, it still prefers the truth after being
contradicted only **~5%** of the time — and no more often on the facts it knows
best, so this is not a knowledge floor.

You cannot study the emergence of a behaviour that is absent at the end of
training. See `docs/PHASE_A.md`; the protocol is `PREREG.md` and the metric
problems found along the way are in `DEVIATIONS.md`.

```bash
./code/fetch_data.sh
../env/bin/python code/build_stimuli.py
../env/bin/python code/score.py --seeds 0,1,2,3,4,5,6,7,8,9 --steps 143000
../env/bin/python code/report.py
```
