# Deviations and self-checks — topic 03

## D1 — candidate-set sizes differ across conditions

`update_1`/`control_1` present 2 candidates, the 2-state conditions 3, the 3-state
conditions 5, so chance accuracy is 0.50 / 0.33 / 0.20. Raw accuracies are
therefore **not** comparable across state counts, and none of the reported
contrasts do that: `PI cost` compares `control_n` with `update_n` at the same `n`,
and every log-probability margin is between candidates within one trial.
`update_1` is used only to date the saturation of binding.

## D2 — the oldest state sits in a different surface frame

State 1 is introduced as `The X is v1.` while later states use `The X is now v2.`
The oldest-vs-recent asymmetry is therefore partly confounded with that frame, and
the "which obsolete value intrudes" result should be read with that in mind. The
central contrast — current vs. **most-recent** obsolete — is not affected: both
appear in identical `is now` frames, and the current value is additionally the
*later* of the two, so surface recency predicts the opposite of what is observed.

## D3 — a concat bug caught in the first intrusion analysis

The first pass at classifying which obsolete state intrudes returned *identical*
counts at every checkpoint, which is impossible. Cause: `pd.concat` over the
per-checkpoint parquet files without `ignore_index=True` produced duplicate index
labels, so `.loc[groupby(...).idxmax()]` returned a cross-product rather than one
row per group. Fixed before any reported number used it; `analyze.load` now
concatenates with `ignore_index=True` throughout.

## D4 — PI cost at two states is negative, and is reported as such

`PI_2` is negative at **every** checkpoint (-0.03 early, -0.17 at its most
negative, settling near -0.07). A single overwrite is a net *benefit*: repeating
the queried key twice helps more than superseding one value hurts. The
pre-registration expected interference to appear with the first overwrite. It does
not. The finding is therefore about interference **accumulating** across multiple
obsolete states, and the write-up says so rather than quoting only the 3-state
number.


## D5 — the category control was not sufficient, and the README overclaimed it

An earlier version of `README.md` said the control differed from `update`
"only in whether those mentions overwrote the queried key". That was false: it
also changed the previous key, the semantic category of the previous values, the
repetition count of the queried key, and the plausibility of the distractors for
the query. The claim was corrected and then tested directly with the
entity-matched control (`docs/ENTITY_CONTROL.md`), which showed the entire
reported effect came from the control rather than from overwriting.

## D6 — `control_distinct_e2` and `control_other_e2` are identical by construction

At two states both controls reduce to a single earlier sentence about one other
entity, so they coincide. Their accuracies are identical in every table, which is
expected rather than a bug. The two controls only differ at three states.

## D7 — the conservative direction of the remaining asymmetry

In the entity-matched design the queried key appears three times in `update` and
once in the controls. Repeating the key makes the query more predictable, which
*helps* `update`, so a positive PI* would have been an underestimate. PI* came out
at zero, so this does not rescue anything — but it does mean the null is not an
artifact of the update condition being handicapped.
