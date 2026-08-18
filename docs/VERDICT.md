# Verdict: the topic is killed at Phase 1

**Date:** 2026-08-19. **Decision:** stop. Phases 2 and 3 are not run, and no
interpretability work follows.

## The question

> Does susceptibility to a garden path emerge *before* the ability to recover
> from it?

## The answer

No. There is no developmental dissociation to find. From the moment the
garden-path effect becomes measurable at all, the disruption it causes is
already confined to the disambiguator, and the small residue it leaves behind
stays a **constant fraction** of that disruption for the remaining ~97% of
pretraining.

![commitment and residual burden over training](../figures/fig1_commitment_vs_recovery.png)

## What survived, and what did not

| gate | result | |
|---|---|---|
| K0 — the effect exists | **PASS** | seed 0: C = 6.17 bits (NP/Z), 3.28 bits (MV/RR) |
| K1 — stable across seeds | **PASS** | 10/10 seeds on all four stimulus sets |
| K2 — recovery improves >=30% | **FAIL** | median improvement **-13.6%** (NP/Z), **-8.6%** (MV/RR); both CIs span 0 |
| K3 — median D >= 1 | *void* | defined in only 43% / 72.5% of bootstrap draws; conditional on the minority of resamples where a recovery time existed at all |
| K4 — >=8/10 seeds with T_recover > T_commit | **FAIL** | **0/10** (NP/Z), **1/10** (MV/RR) |
| K5 — both constructions clear K2-K4 | **FAIL** | — |

K3's nominal "PASS" is an artifact and is reported as void. `D` is only defined
in draws where some checkpoint cleared the 30% recovery bar; conditioning on
those draws and then reading the result as evidence of separation would be
exactly the selection error the pre-registration exists to prevent.

## The finding in three numbers

**1. Commitment is acquired early and with remarkable consistency.**
`T_commit` = 4,000 steps (bootstrap CI [2,000, 4,000]) on *both* constructions —
about 3% of the way through pretraining, ~8B tokens. Nine of ten seeds land on
2,000 or 4,000. Whatever produces garden-path susceptibility is in place very
early and is nearly seed-invariant.

**2. The residual burden grows in lockstep with the disruption.** Over NP/Z,
`C` goes 0.49 → 6.29 bits between steps 1k and 143k while `B` goes 0.10 → 0.47.
Both rise by roughly the same factor. The model does not learn to stop paying
the post-disambiguation cost; it pays a proportionally identical cost throughout.

**3. `R = B/C` is flat.** NP/Z sits at 0.06–0.07 from step 2,000 onward; MV/RR at
0.10–0.13. If anything both drift slightly *upward*, which is why the median
"improvement" is negative. There is no interval in which recovery matures.

## Is the null informative?

Yes — the measure has range, and this was checked before drawing the conclusion.
At the final checkpoint the spillover interaction at the first post-disambiguator
word is reliably positive (NP/Z 0.26 bits, MV/RR 0.23 bits, both with CIs
excluding 0). Models genuinely do carry a garden-path cost past the
disambiguator. That cost is simply a small, and developmentally constant,
fraction of the disruption at the disambiguator itself.

So the null is not "we could not measure recovery". It is "recovery, as behaviour
after the disambiguator, is already as good as it will ever get by the time
susceptibility appears."

## Why this kills the framing rather than just the result

The proposed story needed commitment and recovery to be *separately acquired*.
What the data show is a single quantity — the size of the garden-path effect —
scaling up over training with its post-disambiguator profile unchanged. That is
one developmental process, not two. Rescuing the story would require redefining
recovery after seeing the curves, which the pre-registration forbids and which
would not be worth believing anyway.

## What was not run

Phase 2 (local-4 baseline K7, external replication K6) and Phase 3 (dense
checkpoints) are not run: the pre-registration gates them behind K5.

The local-4 surprisals *were* already computed in the same pass and are in
`results/`, and the external sets already passed K0/K1 at the final checkpoint
(see `PHASE0_K0_K1.md`). They are left unanalysed on purpose — running them now
would be looking for a different result after the pre-registered one came back
negative.

## What would be worth asking instead

Not a rescue of this story, but the honest next questions the data raise:

* `T_commit` ≈ 4,000 steps is early and strikingly seed-invariant on two
  structurally unrelated constructions. What is acquired at that point? That is a
  question about the emergence of the effect, and it stands on its own.
* The NP/Z local-4 baseline reproduced 44% of the final commitment effect while
  MV/RR's reproduced 3%. That gap is about how much of each construction's
  garden-path effect is available from local statistics, and it is a cleaner
  question than the one asked here.
