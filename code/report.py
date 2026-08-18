"""Generate the markdown report for a kill gate from the stored surprisals.

Reports are regenerated from data, never hand-edited, so docs/ and results/
cannot drift apart.
"""
import argparse, os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import (ROOT, STEPS, LATE_STEPS, SG_SUITES, EXT_SUITES,
                     load_surprisals, item_effects, paired_bootstrap_mean,
                     RECOVERY_IMPROVEMENT_MIN)
from dynamics import build_arrays, observed, hierarchical_bootstrap

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


def fmt_step(x):
    return "—" if not np.isfinite(x) else f"{int(x):,}"


def curve_table(items, suite, mode="full"):
    """Median across seeds of C, B and R at every analysis checkpoint."""
    seeds, itemlist, C, B = build_arrays(items, suite, mode)
    c = np.nanmean(C, axis=2)                     # [seed, step]
    with np.errstate(invalid="ignore"):
        b = np.nanmean(B, axis=2)
    r = np.where(c > 0, b / c, np.nan)
    lines = ["| step | C (bits) | B (bits) | R = B/C |", "|---|---|---|---|"]
    for i, st in enumerate(STEPS):
        lines.append(f"| {st:,} | {np.nanmedian(c[:, i]):.2f} | "
                     f"{np.nanmedian(b[:, i]):.2f} | {np.nanmedian(r[:, i]):.3f} |")
    return "\n".join(lines)


def phase1(items, n_boot=10000):
    L = []
    A = L.append
    A("# Gates K2-K5 - are commitment and recovery acquired at separable times?\n")
    A("Pythia-410M, 10 independent training runs, 12 pre-registered analysis "
      "checkpoints (`step0` scored for sanity only, excluded here).\n")
    A("`C` is the commitment interaction at the disambiguator. `B = mean_k max(G_k, 0)` "
      "is the residual burden over the post-disambiguation window, using the identical "
      "2x2 interaction. `R = B/C` is what a mature reanalyser drives toward 0: it is "
      "large when a garden path keeps costing surprisal after the evidence has arrived.\n")

    A("\n## Does the recovery window have any dynamic range?\n")
    A("A null recovery result is only informative if post-disambiguator spillover is "
      "measurable in the first place. Per-position interaction at `step143000`, pooled "
      "over seeds, item-level bootstrap (`*` = 95% CI excludes 0):\n")
    A("| suite | C | G1 | G2 | G3 |")
    A("|---|---|---|---|---|")
    for suite in SG_SUITES:
        sub = items[(items.suite == suite) & (items["mode"] == "full") & (items.step == 143000)]
        cells = []
        for col in ["C", "G1", "G2", "G3"]:
            v = sub[col].dropna().values
            m, lo, hi = paired_bootstrap_mean(v, 5000)
            cells.append(f"{m:.2f}{'*' if lo > 0 else ''}")
        A(f"| {SUITE_LABEL[suite]} | " + " | ".join(cells) + " |")
    A("")
    A("Spillover at the first post-disambiguator word is real and reliably positive, "
      "but it is only a few percent of the disruption at the disambiguator itself. "
      "The measure is not degenerate: it has range, and the range is small.\n")

    verdict = {}
    for suite in SG_SUITES:
        seeds, itemlist, C, B = build_arrays(items, suite, "full")
        obs = observed(C, B)
        obs["seed"] = [seeds[i] for i in obs.seed_index]
        boot = hierarchical_bootstrap(C, B, n_boot=n_boot)
        A(f"\n## {SUITE_LABEL[suite]} (`{suite}`, {len(itemlist)} items, {len(seeds)} seeds)\n")
        A("### Median curves across seeds\n")
        A(curve_table(items, suite) + "\n")
        A("\n### Per-seed acquisition times\n")
        A("| seed | T_commit | T_recover | R_early | R_late | improvement | D = log2 ratio |")
        A("|---|---|---|---|---|---|---|")
        for _, r in obs.sort_values("seed").iterrows():
            imp = "—" if not np.isfinite(r.improvement) else f"{r.improvement*100:.0f}%"
            A(f"| {int(r.seed)} | {fmt_step(r.T_commit)} | {fmt_step(r.T_recover)} | "
              f"{r.R_early:.3f} | {r.R_late:.3f} | {imp} | "
              f"{'—' if not np.isfinite(r.D) else f'{r.D:.2f}'} |")
        n_later = int(((obs.T_recover > obs.T_commit) & np.isfinite(obs.D)).sum())
        n_imp = int((obs.improvement >= RECOVERY_IMPROVEMENT_MIN).sum())
        A("")
        A(f"Seeds with a >={RECOVERY_IMPROVEMENT_MIN*100:.0f}% recovery improvement: "
          f"**{n_imp}/{len(obs)}**. Seeds with `T_recover > T_commit`: **{n_later}/{len(obs)}**.\n")
        A("\n### Hierarchical bootstrap "
          f"({n_boot:,} draws: resample seeds, then items within each resampled seed)\n")
        A("| quantity | median | 95% CI | draws where defined |")
        A("|---|---|---|---|")
        for k, lab, f in [("improvement", "recovery improvement (early→late)", "{:.1%}"),
                          ("D", "D = log2(T_recover / T_commit)", "{:.2f}"),
                          ("T_commit", "T_commit (steps)", "{:,.0f}"),
                          ("T_recover", "T_recover (steps)", "{:,.0f}")]:
            m, lo, hi, frac = boot[k]
            if not np.isfinite(m):
                A(f"| {lab} | — | — | {frac:.1%} |")
            else:
                A(f"| {lab} | {f.format(m)} | [{f.format(lo)}, {f.format(hi)}] | {frac:.1%} |")
        d_frac = boot["D"][3]
        k2_here = bool(np.isfinite(boot["improvement"][0])
                       and boot["improvement"][0] >= RECOVERY_IMPROVEMENT_MIN
                       and boot["improvement"][1] > 0)
        if d_frac < 0.9 or not k2_here:
            A("")
            A(f"> `D` and `T_recover` are undefined in {1-d_frac:.0%} of draws, because "
              f"in those draws no checkpoint ever cleared the 30% recovery-improvement "
              f"requirement. The `D` row above is therefore conditioned on the minority "
              f"of resamples in which a recovery time existed at all, and must not be "
              f"read as evidence of separation. K3 is reported for completeness but is "
              f"**void once K2 fails**.")
        k2 = bool(np.isfinite(boot["improvement"][0])
                  and boot["improvement"][0] >= RECOVERY_IMPROVEMENT_MIN
                  and boot["improvement"][1] > 0)
        k3 = bool(np.isfinite(boot["D"][0]) and boot["D"][0] >= 1 and boot["D"][1] > 0)
        k4 = n_later >= 8
        verdict[suite] = dict(k2=k2, k3=k3, k4=k4, boot=boot, obs=obs)
        A("")
        A(f"- **K2** (recovery improves >=30%, CI > 0): **{'PASS' if k2 else 'FAIL'}**")
        A(f"- **K3** (median D >= 1, CI > 0): **{'PASS' if k3 else 'FAIL'}**")
        A(f"- **K4** (>=8/10 seeds with T_recover > T_commit): **{'PASS' if k4 else 'FAIL'}**")

    k5 = all(v["k2"] and v["k3"] and v["k4"] for v in verdict.values())
    A("\n## Verdict\n")
    for suite, v in verdict.items():
        A(f"- {SUITE_LABEL[suite]}: K2 {'PASS' if v['k2'] else 'FAIL'}, "
          f"K3 {'PASS' if v['k3'] else 'FAIL'}, K4 {'PASS' if v['k4'] else 'FAIL'}")
    A(f"- **K5** (both constructions clear K2-K4): **{'PASS' if k5 else 'FAIL'}**\n")
    if not k5:
        A("Under the pre-registration this is where the developmental-dissociation "
          "story stops. The failing gate is reported as-is; no control is added to "
          "rescue it, and no interpretability work follows. Phases 2 and 3 are not run.")
    else:
        A("Proceed to Phase 2: the local-4-word baseline (K7) and the two external "
          "stimulus sets (K6).")
    return "\n".join(L), k5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="0")
    ap.add_argument("--n-boot", type=int, default=10000)
    args = ap.parse_args()
    items = item_effects(load_surprisals(os.path.join(ROOT, "results", "surprisals")))
    items.to_parquet(os.path.join(ROOT, "results", "item_effects.parquet"), index=False)
    if args.phase == "0":
        text, k0, k1 = phase0(items)
        path = os.path.join(ROOT, "docs", "PHASE0_K0_K1.md")
        open(path, "w").write(text + "\n")
        print(text)
        print("\nwrote", path)
    elif args.phase == "1":
        text, k5 = phase1(items, n_boot=args.n_boot)
        path = os.path.join(ROOT, "docs", "PHASE1_K2_K5.md")
        open(path, "w").write(text + "\n")
        print(text)
        print("\nwrote", path)


if __name__ == "__main__":
    main()
