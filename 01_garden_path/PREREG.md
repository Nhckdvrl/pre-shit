# Pre-registration — Garden-path commitment vs. recovery in pretraining

**Locked 2026-08-19, before any dynamics result was inspected.** Nothing below may
be changed after Phase 1 starts. Deviations are recorded in `DEVIATIONS.md`.

## Main question

Are garden-path **susceptibility** (commitment) and garden-path **recovery**
acquired at separable points in pretraining? Concretely: does a model first learn
to form the locally plausible but ultimately wrong syntactic expectation, and only
later learn to recover from it once disambiguating evidence arrives?

This is a claim about *behavioural* commitment→recovery dissociation. It does not
assume a serial single-parse mechanism.

## Data (no new sentences are written)

| set | items | conditions | role |
|---|---|---|---|
| SyntaxGym `npz_ambig` | 24 | 4 (2x2) | primary A |
| SyntaxGym `mvrr` | 28 | 4 (2x2) | primary B |
| Christianson 2001 (microsoft/turing-experiments) | 24 pairs | 2 | external replication |
| Alternates 2022 (same repo) | 24 pairs | 2 | external replication |

Primary = 52 items x 4 conditions = 208 stimuli per checkpoint.
Factor coding: `ambiguity` ∈ {ambig, unambig}; `cue` ∈ {absent, present}
(`cue=present` is comma for NP/Z, unreduced RC for MV/RR).

## Models

`EleutherAI/pythia-410m` (seed 0) plus PolyPythias `pythia-410m-seed1..9` = 10
independent training runs. Base LMs only; no prompting, no QA, token probability only.

Analysis checkpoints (fixed):
`128, 512, 1000, 2000, 4000, 8000, 16000, 32000, 64000, 96000, 128000, 143000`.
`step0` is scored as a sanity check only and never enters acquisition-time estimates.

## Measure

Word surprisal in bits, summed over the word's BPE sub-tokens:
`S(w) = -sum_i log2 P(w_i | w_<i)`. `<|endoftext|>` is prepended as context.
All contrasts are aligned by **region**, never by tokenizer index.

**Commitment** at the disambiguator (SyntaxGym region 5):

    C = [S(ambig, cue-absent) - S(ambig, cue-present)]
      - [S(unambig, cue-absent) - S(unambig, cue-present)]

i.e. the 2x2 interaction that both original suites specify — not a bare comma effect.
For the two-condition external sets, `C = S(GP) - S(comma control)`.

**Recovery.** The same interaction is computed at each post-disambiguator word `k`,
giving `G_k`. Residual burden and recovery ratio:

    B = mean_k max(G_k, 0)        over the recovery window
    R = B / C                     computed only where the commitment gate passes

## Acquisition times

`C_late = median(C at 96k, 128k, 143k)`.
A checkpoint has **commitment acquired** iff all hold:
1. `C > 0` and the item-level paired-bootstrap 95% CI excludes 0;
2. `C >= 0.5 * C_late`;
3. the next two scheduled checkpoints also satisfy 1–2.

`T_commit` = earliest such checkpoint.

`R_early` = median `R` over the first 3 valid checkpoints from `T_commit`;
`R_late` = median `R` at 96k/128k/143k.
Recovery counts as having improved only if `(R_early - R_late)/R_early >= 0.30`.
If so, `T_recover` = earliest checkpoint with
`R <= R_late + 0.25*(R_early - R_late)`, sustained 3 checkpoints.

`D = log2(T_recover / T_commit)`. Pythia's per-step token count is constant, so a
step ratio is a training-token ratio.

## Statistics

Item = stimulus replication unit; seed = training replication unit.
Hierarchical bootstrap, 10,000 draws: resample seeds with replacement, then items
within each resampled seed, then recompute `C`, `R`, `T_commit`, `T_recover`, `D`.
Never pool 52 items x 10 seeds as 520 independent observations.

## Kill gates

| gate | requirement | if failed |
|---|---|---|
| K0 | final 410M shows `C>0` on both NP/Z and MV/RR, paired-bootstrap 95% CI excludes 0, and >=65% of items positive | kill the topic |
| K1 | >=8/10 seeds satisfy K0 on both suites at the final checkpoint | kill the robust training-dynamics claim |
| K2 | `R` improves >=30% from early to late, hierarchical-bootstrap CI of the improvement > 0 | kill "the model later learns to reanalyse" |
| K3 | median `D >= 1` on both suites (i.e. `T_recover/T_commit >= 2`), hierarchical-bootstrap 95% CI of `D` > 0 | kill the distinct-developmental-phase story |
| K4 | >=8/10 seeds show `T_recover > T_commit` | kill |
| K5 | both constructions pass K0–K4 | kill the general-syntactic-reanalysis framing |
| K6 | Christianson + Alternates (48 pairs) show the final GP effect and the same `T_commit < T_recover` ordering | SyntaxGym-specific; stop |
| K7 | full-context dissociation clearly exceeds a **local-4-word context** baseline: kill if local-4 reproduces >=80% of the commitment effect **and** the recovery curves differ by <20% | kill the hierarchical/syntactic-reanalysis interpretation |

## Execution order

- **Phase 0** — final checkpoint, 10 seeds, 208 stimuli. Check K0, K1.
- **Phase 1** — 12 analysis checkpoints, 10 seeds. Check K2–K5.
- **Phase 2** — local-4 baseline and both external sets. Check K6, K7.
- **Phase 3** — only if K0–K7 all pass: dense (every-1000-step) checkpoints
  between `T_commit` and `T_recover`.

No interpretability work (probes, SAEs, activation patching) before K0–K7 pass.
