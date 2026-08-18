# The entity-matched control — and what it kills

The category control (`control_3`) differs from `update_3` in more than one way:
the previous key, the semantic category the previous values come from, how often
the queried key is repeated, and how plausible the distractors are for the query.
The entity-matched control removes all of that. Everything is identical — value
category, candidate set, sentence count, surface frames (`is` then `is now`),
final sentence — except **who the earlier statements are about**.

```
update_e3            Wendy's African place is Santana.  Wendy's ... is now Kandi.   Wendy's ... is now Garoua.
control_distinct_e3  Nathan's African place is Santana. Frank's ... is now Kandi.   Wendy's ... is now Garoua.
control_other_e3     Nathan's African place is Santana. Nathan's ... is now Kandi.  Wendy's ... is now Garoua.
                                                   query: Wendy's African place is currently
```

`control_distinct` contains no overwrite at all. `control_other` contains exactly
as many overwrites as `update`, but of a different entity.

8 checkpoints x 10 seeds x 5,520 stimuli. Crossed seed x trial bootstraps.

## PI* = accuracy(control) − accuracy(update), 3 states

| step | vs `control_distinct` | seeds | vs `control_other` | seeds |
|---|---|---|---|---|
| 1,000 | +0.006 [+0.001, +0.011] | 8/10 | +0.004 [-0.001, +0.009] | 7/10 |
| 2,000 | +0.013 [+0.003, +0.024] | 8/10 | +0.007 [-0.004, +0.018] | 7/10 |
| 4,000 | -0.011 [-0.027, +0.004] | 3/10 | +0.008 [-0.008, +0.023] | 7/10 |
| 8,000 | -0.023 [-0.046, -0.003] | 3/10 | -0.013 [-0.030, +0.004] | 3/10 |
| 16,000 | -0.011 [-0.033, +0.007] | 4/10 | -0.018 [-0.042, +0.006] | 3/10 |
| 32,000 | -0.009 [-0.041, +0.015] | 5/10 | -0.032 [-0.066, -0.006] | 2/10 |
| 64,000 | +0.014 [-0.010, +0.040] | 7/10 | -0.017 [-0.040, +0.006] | 3/10 |
| 143,000 | +0.015 [-0.023, +0.051] | 5/10 | -0.013 [-0.048, +0.021] | 3/10 |

**PI\* is zero.** It never exceeds ±0.03, it does not grow from 4k to 64k, and the
seeds split. The +0.30 measured against the category control is entirely gone.

## Where the +0.30 came from

| | old category control | new entity control |
|---|---|---|
| `update` accuracy @143k | 0.333 | 0.314 |
| `control` accuracy @143k | **0.654** | **0.360** |

The update condition is the same in both. What changed is the control: once the
distractors are same-category values rather than obviously-wrong-category ones,
the control becomes just as hard as the update. The gap was never the update
being hard — it was the control being easy, and getting easier as the model
learned category type constraints. That is exactly the confound this control was
built to test, and it accounts for the whole effect.

## The margin inversion is real but is not about bindings

`current − most-recent-obsolete` (bits):

| step | `update_e3` | `control_distinct_e3` | `control_other_e3` |
|---|---|---|---|
| 4,000 | +0.28 | +0.26 | +0.36 |
| 16,000 | -0.32 | -0.42 | -0.64 |
| 64,000 | -0.67 [-0.92, -0.38] | -0.51 [-0.75, -0.29] | -1.02 [-1.26, -0.80] |
| 143,000 | -0.64 [-0.92, -0.29] | -0.48 [-0.78, -0.16] | -0.94 [-1.30, -0.54] |

The inversion happens just as strongly in `control_distinct_e3`, where the
competing value was **bound to a different person and never overwrote anything**.
Differencing the margins directly gives nothing entity-specific at any late
checkpoint: -0.156 [-0.325, +0.037] at 64k, -0.162 [-0.451, +0.156] at 143k.

Meanwhile `current − never-mentioned` holds at +8.1 to +9.9 bits in every
condition. So the earlier observation survives in form and dies in content:
retrieval does not degrade, and the ordering among mentioned values does invert
over training — but the competition is driven by **a value having been mentioned
in the same category**, not by its having been a superseded binding of the
queried entity.

`control_other_e3` produces the *largest* inversion (-1.02 bits), and there the
winning competitor is the current value of the *other* person. The model is
substantially blind to the possessor.

## Verdict

**The central claim is retracted.** "Proactive interference emerges after entity
binding during pretraining" is not supported. There is no overwrite-specific cost,
and the developmental growth reported against the category control was a property
of that control.

This also undermines the `update_1` measure that dated "binding" to step 2,000:
`update_1` contains no competing entity, so it never tested entity binding — only
whether the model can echo a single asserted value.

## What actually survives

One narrower finding, robust across 10 seeds and three matched conditions:

> Over pretraining, models increasingly prefer an earlier-mentioned same-category
> value over the value asserted last, while never losing the distinction between
> mentioned and never-mentioned values. The effect is possessor-blind.

That is a real training-dynamics phenomenon about mention competition and
recency, and it is *not* the question this topic pre-registered. Pursuing it would
need its own pre-registration and its own dangerous controls — starting with
whether it is anything more than the model's declining reliance on positional
recency as it learns longer-range statistics.
