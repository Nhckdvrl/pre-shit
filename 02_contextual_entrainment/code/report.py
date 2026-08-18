"""Generate the Phase A (K1/K2) report from the stored scores."""
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import ROOT, load, measures, crossed_bootstrap

NB = 10000


def ci(m, col, stat=np.mean, sub=None):
    d = sub if sub is not None else m
    return crossed_bootstrap(d[col].values, d.seed.values, n=NB, stat=stat)


def main():
    m = measures(load())
    m.to_parquet(os.path.join(ROOT, "results", "measures.parquet"), index=False)
    L = []
    A = L.append
    A("# Phase A (K1/K2) — does 410M show both behaviours at all?\n")
    A("`step143000`, 10 independent pretraining runs, 898 LRE items over 26 factual "
      "relations. All intervals are crossed seed x item bootstraps (10,000 draws).\n")

    A("## Mechanical copying\n")
    A("`E_copy` compares a random noun **that appeared in context** against a second "
      "random noun that did not, both relative to no context. The control matters: "
      "without it a rise in `D_d` could just mean random nouns became likelier overall.\n")
    A("| quantity | bits | 95% CI |")
    A("|---|---|---|")
    for col, lab in [("D_rand_seen", "`D_d` — random noun present in context"),
                     ("D_rand_unseen", "`D_ctrl` — random noun absent from context"),
                     ("E_copy", "**`E_copy` = D_d − D_ctrl**")]:
        mu, lo, hi = ci(m, col)
        A(f"| {lab} | {mu:+.2f} | [{lo:+.2f}, {hi:+.2f}] |")
    per = m.groupby("seed").E_copy.mean()
    A(f"\nAll **{int((per > 0).sum())}/10** seeds positive (range {per.min():+.2f} to "
      f"{per.max():+.2f} bits). Contextual entrainment of semantically inert tokens is "
      "large and unambiguous at 410M.\n")

    A("## Semantic filtering\n")
    A("Resistance is measured where it is meaningful: on items the model already gets "
      "right without context (`K > 0`), does it still prefer the gold object after the "
      "context asserts a false one?\n")
    kn = m[m.K > 0]
    r, rlo, rhi = ci(m, "margin_cf", stat=lambda v: float(np.mean(v > 0)), sub=kn)
    mg, mlo, mhi = ci(m, "margin_cf", sub=kn)
    A(f"- items known without context: **{len(kn)/len(m)*100:.0f}%**")
    A(f"- of those, still prefer gold after the false context: "
      f"**{r*100:.1f}%** [{rlo*100:.1f}%, {rhi*100:.1f}%]")
    A(f"- mean post-context margin: **{mg:+.2f}** bits [{mlo:+.2f}, {mhi:+.2f}] "
      "(negative = the model believes the lie)\n")
    q = kn.copy()
    q["quintile"] = pd.qcut(q.K, 5, labels=False)
    A("Resistance does not recover on the facts the model knows best, so this is not a "
      "knowledge floor:\n")
    A("| K quintile | mean K (bits) | resistance rate |")
    A("|---|---|---|")
    for qq, g in q.groupby("quintile"):
        A(f"| {int(qq)+1} | {g.K.mean():.1f} | {(g.margin_cf > 0).mean()*100:.1f}% |")

    A("\n## Semantics does modulate entrainment — in the opposite direction\n")
    a, alo, ahi = ci(m, "D_cf_d")
    b, blo, bhi = ci(m, "D_irr_d")
    m2 = m.copy(); m2["sem"] = m2.D_cf_d - m2.D_irr_d
    d, dlo, dhi = ci(m2, "sem")
    A("| context | `D_d` (bits) | 95% CI |")
    A("|---|---|---|")
    A(f"| counterfactual — false fact, correct subject | {a:+.2f} | [{alo:+.2f}, {ahi:+.2f}] |")
    A(f"| irrelevant — true fact, different subject | {b:+.2f} | [{blo:+.2f}, {bhi:+.2f}] |")
    A(f"| **difference** | **{d:+.2f}** | [{dlo:+.2f}, {dhi:+.2f}] |")
    A("\nSemantic structure changes entrainment by a robust ~4 bits, but it *increases* "
      "the pull of the false claim rather than resisting it.\n")

    A("## Verdict\n")
    A("- **K1 — mechanical copying: PASS.** Large, control-corrected, 10/10 seeds.")
    A("- **K1 — semantic filtering: FAIL in substance.** The behaviour is at floor: "
      f"~{r*100:.0f}% resistance at the *end* of pretraining, and no better on the "
      "best-known facts. Read literally the gate is satisfied (counterfactual context "
      "moves gold vs. distractor enormously), but what it moves is compliance, not "
      "resistance.")
    A("- **K2 is not reached.** There is no filtering signal for the knowledge control "
      "to be applied to.\n")
    A("**Decision: kill.** The question was when two *opposing* forms of context "
      "sensitivity diverge during pretraining. Only one of them exists at 410M. Phase B "
      "would trace a single curve — mechanical copying — which is not the question and "
      "is largely known already.\n")
    A("This is the risk `PREREG.md` flagged in advance: Pythia-410M is the smallest "
      "model in the ACL 2026 scaling range, and semantic filtering is precisely the "
      "capability that paper reports as growing with scale. The 10-seed replication only "
      "exists at 410M, so the study cannot be moved up in size without losing the asset "
      "that motivated it.\n")
    A("## One finding worth keeping\n")
    A(f"Entrainment is **{d:.1f} bits stronger** for a false claim about the right "
      "subject than for a true claim about a different subject. That is a real, "
      "seed-stable semantic modulation present at 410M — but it is semantic "
      "*amplification*, not filtering, and studying its dynamics would be a different "
      "pre-registration, not a rescue of this one.")
    txt = "\n".join(L)
    open(os.path.join(ROOT, "docs", "PHASE_A.md"), "w").write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
