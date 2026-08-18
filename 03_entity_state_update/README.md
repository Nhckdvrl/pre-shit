# 03 — Entity state update

**Status: central claim retracted after the entity-matched control. See
`docs/ENTITY_CONTROL.md`.**

> When language models learn to track changing entities, do the ability to
> retrieve the current state and the ability to suppress obsolete states develop
> together?

Against a **category** control the answer looked striking: binding saturates by
step 2,000 while proactive interference at three states grows from -0.02 to +0.34
over the next 50x of training, in 10/10 seeds.

Against an **entity-matched** control — same value category, same candidate set,
same frames, differing only in whether the earlier statements were about the
queried entity — that effect is **zero at every checkpoint** (|PI*| < 0.03, seeds
split, no growth). The gap was the control being easy and getting easier, not the
update being hard.

The margin inversion is real (the model does come to prefer an earlier-mentioned
value over the one asserted last, while never confusing mentioned with
never-mentioned values) but it happens just as strongly when the competing value
was bound to a *different person*. It is mention competition, not overwrite
interference.

`docs/ENTITY_CONTROL.md` is the decisive experiment. `docs/RESULTS.md` holds the
full 12-checkpoint grid measured against the category control and must be read
with that document — its headline is superseded. Protocol: `PREREG.md`;
self-checks and corrections: `DEVIATIONS.md`.

```bash
./code/fetch_data.sh
../env/bin/python code/build_stimuli.py
../env/bin/python code/score.py --seeds 0,1,2,3,4,5,6,7,8,9 \
    --steps 128,512,1000,2000,4000,8000,16000,32000,64000,96000,128000,143000
../env/bin/python code/report.py && ../env/bin/python code/plot.py
../env/bin/python code/build_stimuli_entity.py
../env/bin/python code/score.py --seeds 0,1,2,3,4,5,6,7,8,9 \
    --steps 1000,2000,4000,8000,16000,32000,64000,143000 \
    --stimuli stimuli_entity.jsonl --out results/scores_entity
```
