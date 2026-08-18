# Phase A (K1/K2) — does 410M show both behaviours at all?

`step143000`, 10 independent pretraining runs, 898 LRE items over 26 factual relations. All intervals are crossed seed x item bootstraps (10,000 draws).

## Mechanical copying

`E_copy` compares a random noun **that appeared in context** against a second random noun that did not, both relative to no context. The control matters: without it a rise in `D_d` could just mean random nouns became likelier overall.

| quantity | bits | 95% CI |
|---|---|---|
| `D_d` — random noun present in context | +5.39 | [+4.96, +5.87] |
| `D_ctrl` — random noun absent from context | +0.64 | [+0.51, +0.77] |
| **`E_copy` = D_d − D_ctrl** | +4.75 | [+4.24, +5.32] |

All **10/10** seeds positive (range +3.69 to +6.45 bits). Contextual entrainment of semantically inert tokens is large and unambiguous at 410M.

## Semantic filtering

Resistance is measured where it is meaningful: on items the model already gets right without context (`K > 0`), does it still prefer the gold object after the context asserts a false one?

- items known without context: **77%**
- of those, still prefer gold after the false context: **5.5%** [3.7%, 7.3%]
- mean post-context margin: **-9.92** bits [-10.79, -9.05] (negative = the model believes the lie)

Resistance does not recover on the facts the model knows best, so this is not a knowledge floor:

| K quintile | mean K (bits) | resistance rate |
|---|---|---|
| 1 | 1.1 | 1.8% |
| 2 | 3.5 | 2.7% |
| 3 | 6.2 | 5.8% |
| 4 | 9.3 | 9.1% |
| 5 | 19.9 | 7.9% |

## Semantics does modulate entrainment — in the opposite direction

| context | `D_d` (bits) | 95% CI |
|---|---|---|
| counterfactual — false fact, correct subject | +16.60 | [+16.16, +17.01] |
| irrelevant — true fact, different subject | +12.21 | [+11.41, +13.14] |
| **difference** | **+4.39** | [+3.33, +5.20] |

Semantic structure changes entrainment by a robust ~4 bits, but it *increases* the pull of the false claim rather than resisting it.

## Verdict

- **K1 — mechanical copying: PASS.** Large, control-corrected, 10/10 seeds.
- **K1 — semantic filtering: FAIL in substance.** The behaviour is at floor: ~5% resistance at the *end* of pretraining, and no better on the best-known facts. Read literally the gate is satisfied (counterfactual context moves gold vs. distractor enormously), but what it moves is compliance, not resistance.
- **K2 is not reached.** There is no filtering signal for the knowledge control to be applied to.

**Decision: kill.** The question was when two *opposing* forms of context sensitivity diverge during pretraining. Only one of them exists at 410M. Phase B would trace a single curve — mechanical copying — which is not the question and is largely known already.

This is the risk `PREREG.md` flagged in advance: Pythia-410M is the smallest model in the ACL 2026 scaling range, and semantic filtering is precisely the capability that paper reports as growing with scale. The 10-seed replication only exists at 410M, so the study cannot be moved up in size without losing the asset that motivated it.

## One finding worth keeping

Entrainment is **4.4 bits stronger** for a false claim about the right subject than for a true claim about a different subject. That is a real, seed-stable semantic modulation present at 410M — but it is semantic *amplification*, not filtering, and studying its dynamics would be a different pre-registration, not a rescue of this one.
