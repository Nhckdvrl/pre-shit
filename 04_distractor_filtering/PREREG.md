# Pre-registration — context *use* vs. context *selection*

**Locked 2026-08-19, before any scoring.** Written under `../METHODOLOGY.md`.

## Question

> During natural pretraining, does the ability to exploit relevant context emerge
> together with the ability to reject semantically competing context?

All knowledge needed is **in the context**. There is no parametric-vs-context
conflict, which is a separately studied question and is deliberately excluded.

No direction is predicted. Three outcomes are all admissible: filtering failure
growing with semantic competence, filtering arriving after context sensitivity,
or the two being one curve (which kills the topic).

## Stimuli

LRE country relations (`country_capital_city`, `country_currency`,
`country_language`, `country_largest_city`) — the subject is always a country, so
one frame serves all four. No sentences are invented beyond the frame.

```
relevant     Sebastian lives in France.
distractor   Rowan lives in Indonesia.          (semantic)
             Rowan lives in a cottage.          (unrelated)
             Rowan visited Jakarta.             (direct, secondary only)
query        The capital of Sebastian's country is ___        -> Paris
```

The **primary** distractor is *indirect*: it names a competing **country**, never
the competing answer. The competing answer (`Jakarta`) is only reachable through
the same relation. A *direct* distractor that names `Jakarta` outright is a
**secondary stress test only** — topics 02 and 03 showed how easily a mentioned
token produces copying that masquerades as a semantic effect.

## The difference table (rule 2)

| condition | sentences | frame of distractor sentence | distractor object | candidate set |
|---|---|---|---|---|
| `base` | 1 | — | — | identical |
| `semantic` | 2 | `NAME lives in X.` | a **country** | identical |
| `unrelated` | 2 | `NAME lives in X.` | a **dwelling** | identical |
| `direct` (secondary) | 2 | `NAME visited X.` | the **decoy answer** | identical |

`semantic` and `unrelated` share the verb frame verbatim (`lives in`) and differ
only in the semantic type of the object. Candidate sets are identical in every
condition, so no accuracy is compared across different candidate sets.

Each item is generated at **both distractor positions** (before and after the
relevant sentence), fixed in advance, so position is a factor rather than a
confound.

## Measures

    M = log2 P(correct) - max_j log2 P(wrong candidate_j)

    D_sem   = M_base - M_semantic
    D_unrel = M_base - M_unrelated
    D*      = D_sem - D_unrel

Note `D*` reduces algebraically to `M_unrelated - M_semantic`: a comparison
between the two **perfectly frame-matched** conditions. `base` is therefore only
used to establish that relevant context is used at all (K1), and cannot smuggle a
length effect into `D*`.

## Metric under the null (rule 4)

`M` and `D*` are signed differences of log-probabilities — no rectification, no
ratio, no normalisation. Under no effect `D*` is 0 in expectation and symmetric.
This is a deliberate departure from topic 01's `max(G, 0)`.

## The dangerous confound, locked in advance

If the model's own grasp of the decoy relation (`Indonesia -> Jakarta`) strengthens
over training, `D*` could grow with no change in filtering ability. So

    A_decoy(t) = log2 P(decoy answer | decoy relation prompt)

is measured at every checkpoint from a separate no-distractor prompt, and `D*` is
reported both raw and conditioned on `A_decoy`. Both arms of every contrast are
always plotted separately (rule 5).

## Kill gates — K1-K3 are all final-checkpoint only

| gate | requirement | if failed |
|---|---|---|
| **K1** | an eligible set survives: `base` picks the correct candidate in >= 8/10 seeds, for >= 50% of items | 410M does not use relevant context; kill the setup |
| **K2** | `D* > 0` with a crossed seed x item bootstrap CI excluding 0, in >= 8/10 seeds, **and the indirect distractor produces it on its own** | if only the direct distractor works, it is copying; kill the filtering framing |
| **K3** | the effect survives position matching | it is a position effect; kill |
| **K4** (Phase B) | `C(t) = M_base` and `F(t) = D*` have distinguishable trajectories after conditioning on `A_decoy` | one curve; kill |

Phase B: `1000, 4000, 16000, 64000, 143000`. Full grid only after K4.

## Statistics

Item = stimulus replication unit, seed = training replication unit. Every interval
is a crossed seed x item bootstrap.
