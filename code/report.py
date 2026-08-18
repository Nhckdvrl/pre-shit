"""Generate the markdown report for a kill gate from the stored surprisals.

Reports are regenerated from data, never hand-edited, so docs/ and results/
cannot drift apart.
"""
import argparse, os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import (ROOT, STEPS, SG_SUITES, EXT_SUITES, load_surprisals,
                     item_effects, paired_bootstrap_mean)

SUITE_LABEL = {"npz_ambig": "NP/Z", "mvrr": "MV/RR",
               "Christianson_2001": "Christianson 2001",
               "Alternates_2022": "Alternates 2022"}


def seed_table(items, suite, mode, step):
    sub = items[(items.suite == suite) & (items["mode"] == mode) & (items.step == step)]
    rows = []
    for seed, g in sub.groupby("seed"):
        m, lo, hi = paired_bootstrap_mean(g["C"].values)
        frac = float(np.mean(g["C"].values > 0))
        rows.append(dict(seed=int(seed), C=m, lo=lo, hi=hi, frac_pos=frac,
                         n_items=len(g), passes=bool(lo > 0 and frac >= 0.65)))
    return pd.DataFrame(rows).sort_values("seed").reset_index(drop=True)


def md_table(t):
    out = ["| seed | mean C (bits) | 95% CI | items positive | passes |",
           "|---|---|---|---|---|"]
    for _, r in t.iterrows():
        out.append(f"| {int(r.seed)} | {r.C:.2f} | [{r.lo:.2f}, {r.hi:.2f}] | "
                   f"{r.frac_pos*100:.0f}% ({int(round(r.frac_pos*r.n_items))}/{int(r.n_items)}) | "
                   f"{'yes' if r.passes else '**no**'} |")
    return "\n".join(out)


def phase0(items, step=143000):
    L = []
    A = L.append
    A("# Gate K0 / K1 — does the garden-path effect exist at all, and across seeds?\n")
    A("Checkpoint `step143000` (end of pretraining), Pythia-410M, 10 independent "
      "training runs (`pythia-410m` = seed 0, PolyPythias `-seed1..9`).\n")
    A("**Measure.** Commitment `C` = the 2x2 interaction at the disambiguator,\n")
    A("```\nC = [S(ambig, cue absent) - S(ambig, cue present)]\n"
      "  - [S(unambig, cue absent) - S(unambig, cue present)]\n```\n")
    A("in bits, one value per item. A bare comma effect or a bare reduced-relative "
      "effect cancels out of this contrast; only the *extra* difficulty the early "
      "cue removes specifically in the ambiguous condition survives.\n")
    A("**Pass rule (pre-registered).** A seed passes if its item-level paired-bootstrap "
      "95% CI excludes 0 and at least 65% of items are positive. "
      "K0 = seed 0 passes on both primary suites; K1 = at least 8/10 seeds pass on both.\n")

    verdicts = {}
    for group, suites, title in [("primary", SG_SUITES, "Primary suites (SyntaxGym)"),
                                 ("external", EXT_SUITES, "External replication sets")]:
        A(f"\n## {title}\n")
        for suite in suites:
            t = seed_table(items, suite, "full", step)
            n_items = int(t.n_items.iloc[0])
            A(f"\n### {SUITE_LABEL[suite]} (`{suite}`, {n_items} items)\n")
            A(md_table(t) + "\n")
            npass = int(t.passes.sum())
            A(f"\nSeeds passing: **{npass}/{len(t)}**. "
              f"Across-seed mean C = {t.C.mean():.2f} bits "
              f"(range {t.C.min():.2f}–{t.C.max():.2f}).\n")
            verdicts[suite] = t

    A("\n## Local-4-word context (preview of K7)\n")
    A("The same contrast with only the 4 preceding words as context. This is not the "
      "K7 decision — that needs the full dynamics — but it shows the baseline is live.\n")
    A("\n| suite | full context | local-4 | local-4 / full |")
    A("|---|---|---|---|")
    for suite in SG_SUITES + EXT_SUITES:
        f = seed_table(items, suite, "full", step).C.mean()
        l = seed_table(items, suite, "local4", step).C.mean()
        A(f"| {SUITE_LABEL[suite]} | {f:.2f} | {l:.2f} | {l/f*100:.0f}% |")

    k0 = all(bool(verdicts[s].loc[verdicts[s].seed == 0, "passes"].iloc[0]) for s in SG_SUITES)
    k1 = all(int(verdicts[s].passes.sum()) >= 8 for s in SG_SUITES)
    A("\n## Verdict\n")
    A(f"- **K0** (original Pythia-410M passes on both NP/Z and MV/RR): **{'PASS' if k0 else 'FAIL'}**")
    A(f"- **K1** (>=8/10 seeds pass on both): **{'PASS' if k1 else 'FAIL'}**")
    A("")
    if k0 and k1:
        A("Both gates pass. Proceed to Phase 1: score the 12-checkpoint grid on all "
          "10 seeds and evaluate K2–K5.")
    else:
        A("A gate failed. Under the pre-registration this kills the topic at Phase 0; "
          "no dynamics run follows.")
    return "\n".join(L), k0, k1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="0")
    args = ap.parse_args()
    items = item_effects(load_surprisals(os.path.join(ROOT, "results", "surprisals")))
    items.to_parquet(os.path.join(ROOT, "results", "item_effects.parquet"), index=False)
    if args.phase == "0":
        text, k0, k1 = phase0(items)
        path = os.path.join(ROOT, "docs", "PHASE0_K0_K1.md")
        open(path, "w").write(text + "\n")
        print(text)
        print("\nwrote", path)


if __name__ == "__main__":
    main()
