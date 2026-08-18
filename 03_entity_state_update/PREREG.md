# Pre-registration — do "bind the latest state" and "suppress obsolete states" develop together?

**Locked 2026-08-19.** Deviations in `DEVIATIONS.md`.

## Background and the gap

Entity tracking is a core discourse ability (Kim & Schuster, ACL 2023): text
performs state-changing operations and the model must know what is true *now*.
PI-LLM (ICML 2025 workshop) showed the failure mode is not context access but
**proactive interference** — retrieval accuracy falls log-linearly as overwritten
values accumulate, and errors are re-retrievals of values that were explicitly
superseded. A 2026 study finds proactive interference exceeds retroactive
interference across 39 LLMs, and ICML 2026 mechanistic work finds state is
aggregated at query time rather than maintained token-by-token, with REMOVE
relying on a fragile global suppression mechanism.

All of this characterises trained models. Searching entity tracking / proactive
interference against training checkpoints turns up final-model behaviour,
mechanism and scaling — but not how binding-the-latest-state and
suppressing-obsolete-states arise during natural pretraining.

## Question

> When language models learn to track changing entities, do the ability to
> retrieve the current state and the ability to suppress obsolete states develop
> together?

No direction is predicted. It is a live possibility that better binding makes
interference *worse*, not better — that pretraining strengthens memory and
manufactures interference at the same time.

## Stimuli

Built from the PI-LLM inventory (46 categories x 400 values), 20 trials per
category = **920 trials**, each realised in five conditions:

| condition | context | current | interferers |
|---|---|---|---|
| `update_1` | `The bird is emu.` | emu | — |
| `update_2` | `... The bird is now kea.` | kea | emu |
| `update_3` | `... The bird is now ani.` | ani | emu, kea |
| `control_2` | `The material is wood. The bird is kea.` | kea | wood |
| `control_3` | `The material is wood. The dessert is cake. The bird is ani.` | ani | wood, cake |

Controls are matched on sentence count, on the number of previously mentioned
values, and on the position of the queried binding (always last). They differ
only in whether those earlier mentions *overwrite the queried key*. Candidates
are the current value, every interferer, and equally many never-mentioned values
of the same category, so an error can be classified as interference or as a miss.

Query is `The {category} is currently`, deliberately not the surface form of the
statements, so that pure induction-style copying of the preceding pattern is not
sufficient.

## Measures

    accuracy      the current value is the highest-scoring candidate
    M_interf      log P(current) - max_j log P(interferer_j)
    PI cost       accuracy(control_n) - accuracy(update_n)

`PI cost` is the quantity of interest: it subtracts off everything that mere
context length and mere prior mentions contribute, leaving only the cost of the
mentions having been *bindings of the queried key*.

## Kill gates

| gate | requirement | if failed |
|---|---|---|
| **K1** | `update_1` accuracy >= 0.75 at the final checkpoint | 410M cannot bind at all; kill the setup |
| **K2** | selective interference: `PI cost > 0` at 3 states with a crossed seed x trial bootstrap CI excluding 0, and errors preferentially the obsolete value rather than an unmentioned one | it is just "longer context is harder"; kill the PI framing |
| **K3** | after binding is acquired, `PI cost(t)` has its own trajectory — it is not a fixed proportion of `update_1` accuracy | no second developmental phenomenon; kill |

Phase B checkpoints: `1000, 4000, 16000, 64000, 143000`. Phase C (full 12-point
grid, acquisition times, mechanism) only if K3 passes.

## Statistics

Trial = stimulus replication unit, seed = training replication unit. Every
interval is a crossed seed x trial bootstrap.
