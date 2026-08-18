"""Metric audit of the Phase 1 recovery result. No model inference: everything
is recomputed from results/item_effects.parquet.

Fixes three implementation defects found on review, then re-runs the recovery
trajectory under several definitions of the post-disambiguation burden:

  rect_item   mean_i mean_k max(G_ki, 0)      <- what Phase 1 actually computed
  rect_pop    mean_k max(mean_i G_ki, 0)      <- what PREREG.md actually specifies
  signed      mean_k mean_i G_ki              <- no rectification at all
  auc         sum_k mean_i G_ki               <- cumulative excess surprisal
  g1          mean_i G_1i                     <- the single cleanest position

Fixes applied:
  F1  rectification moved to the population level (PREREG conformance)
  F2  the sustain rule requires a full SUSTAIN-long window, also at the tail
  F3  the commitment CI gate is applied on real data, as DEVIATIONS.md D6 claims
  F4  per-position significance uses a crossed seed x item hierarchical bootstrap
"""
import os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import (ROOT, STEPS, LATE_STEPS, SUSTAIN, SG_SUITES,
                     RECOVERY_IMPROVEMENT_MIN, RECOVERY_REACH_FRAC)
from dynamics import (build_arrays as build_G, burden, ci_gate,
                      times_from_curves, crossed_bootstrap_mean,
                      _first_sustained as first_sustained)

LATE_IDX = [STEPS.index(s) for s in LATE_STEPS]
VARIANTS = ["rect_item", "rect_pop", "signed", "auc", "g1"]


# ------------------------------------------------------------------ F2






def run_audit(items, n_boot=10000):
    lines = []
    A = lines.append
    rng = np.random.default_rng(20260819)

    A("# Metric audit of the Phase 1 recovery result\n")
    A("No model was re-run. Everything below is recomputed from the stored "
      "per-checkpoint surprisals.\n")
    A("## Defects found on review\n")
    A("| # | defect | effect |")
    A("|---|---|---|")
    A("| F1 | `B` rectified `max(G_k, 0)` **per item**, but `PREREG.md` defines "
      "`G_k(t)` as the population interaction, so the rectification belongs at the "
      "population level | inflates `B` whenever item-level interactions are noisy, "
      "and can make `B` track `C` through variance alone |")
    A("| F2 | the sustain rule clipped its window at the end of the grid, so the "
      "final checkpoint needed 1 True to count as '3 sustained' | makes late "
      "`T_recover` easier to define |")
    A("| F3 | the Phase 1 path (`observed` -> `times_from_curves`) never applied the "
      "commitment CI gate, although `DEVIATIONS.md` D6 states it is applied on real "
      "data | `T_commit` was not computed as pre-registered |")
    A("| F4 | per-position `G_k` significance pooled 10 seeds x items into one "
      "item-level bootstrap | pseudo-replication; overstates the evidence that "
      "spillover is reliably positive |")

    A("\n## How large is the rectification bias?\n")
    A("Population-level signed interaction vs. the rectified quantity actually used, "
      "at `step143000`, median over seeds:\n")
    A("| suite | signed mean_k G_k | rect_pop | rect_item (used in Phase 1) | inflation |")
    A("|---|---|---|---|---|")
    for suite in SG_SUITES:
        seeds, il, C, G = build_G(items, suite, "full")
        t = STEPS.index(143000)
        vals = {}
        for v in ["signed", "rect_pop", "rect_item"]:
            vals[v] = np.median([burden(G[s], v)[t] for s in range(len(seeds))])
        A(f"| {suite} | {vals['signed']:.3f} | {vals['rect_pop']:.3f} | "
          f"{vals['rect_item']:.3f} | {vals['rect_item']/max(vals['signed'],1e-9):.1f}x |")

    A("\n## Per-position interaction with a crossed seed x item bootstrap (F4)\n")
    A("`*` = 95% CI excludes 0. The pooled column is the Phase 1 (pseudo-replicated) "
      "interval, shown for comparison.\n")
    A("| suite | position | mean (bits) | crossed CI | pooled CI (wrong) |")
    A("|---|---|---|---|---|")
    from analyze import paired_bootstrap_mean
    for suite in SG_SUITES:
        sub = items[(items.suite == suite) & (items["mode"] == "full") & (items.step == 143000)]
        codes = {v: i for i, v in enumerate(sorted(sub.item.unique()))}
        for col in ["C", "G1", "G2", "G3"]:
            v = sub[col].values.astype(float)
            si = sub.seed.values
            ii = np.array([codes[x] for x in sub.item.values])
            m, lo, hi = crossed_bootstrap_mean(v, si, ii, n=n_boot, rng=rng)
            pm, plo, phi = paired_bootstrap_mean(sub[col].dropna().values, 5000)
            star = "*" if lo > 0 else ""
            A(f"| {suite} | {col} | {m:.3f}{star} | [{lo:.3f}, {hi:.3f}] | "
              f"[{plo:.3f}, {phi:.3f}] |")

    A("\n## Recovery trajectory under every burden definition\n")
    A("`R = B/C`, median over the 10 seeds, with the commitment CI gate (F3) and the "
      "corrected sustain rule (F2) applied throughout.\n")

    summary = []
    for suite in SG_SUITES:
        for strict3 in [False, True]:
            seeds, il, C, G = build_G(items, suite, "full", strict3=strict3)
            tag = f"{suite}{' (strict 3-word window)' if strict3 else ''}"
            A(f"\n### {tag} — {len(il)} items\n")
            gates = [ci_gate(C[s], rng=np.random.default_rng(100 + s)) for s in range(len(seeds))]
            A("| step | C | " + " | ".join(f"R_{v}" for v in VARIANTS) + " |")
            A("|---" * (2 + len(VARIANTS)) + "|")
            cs = np.array([np.nanmean(C[s], axis=1) for s in range(len(seeds))])
            bs = {v: np.array([burden(G[s], v) for s in range(len(seeds))]) for v in VARIANTS}
            for i, st in enumerate(STEPS):
                cmed = np.nanmedian(cs[:, i])
                row = [f"| {st:,} | {cmed:.2f} "]
                for v in VARIANTS:
                    with np.errstate(invalid="ignore", divide="ignore"):
                        r = np.where(cs[:, i] > 0.5, bs[v][:, i] / cs[:, i], np.nan)
                    row.append(f"| {np.nanmedian(r):+.3f} " if np.any(np.isfinite(r)) else "| — ")
                A("".join(row) + "|")
            A("")
            A("| variant | T_commit (median) | seeds with improvement >=30% | "
              "median improvement | seeds with T_recover > T_commit |")
            A("|---|---|---|---|---|")
            for v in VARIANTS:
                res = [times_from_curves(cs[s], bs[v][s], gates[s]) for s in range(len(seeds))]
                tc = np.nanmedian([r["T_commit"] for r in res])
                imps = np.array([r["improvement"] for r in res], float)
                nimp = int(np.sum(imps >= RECOVERY_IMPROVEMENT_MIN))
                nlater = int(np.sum([np.isfinite(r["T_recover"]) and r["T_recover"] > r["T_commit"]
                                     for r in res]))
                mi = np.nanmedian(imps) if np.any(np.isfinite(imps)) else np.nan
                A(f"| {v} | {tc:,.0f} | {nimp}/{len(seeds)} | "
                  f"{'—' if not np.isfinite(mi) else f'{mi:+.1%}'} | {nlater}/{len(seeds)} |")
                summary.append(dict(suite=suite, strict3=strict3, variant=v,
                                    T_commit=tc, n_imp=nimp, med_imp=mi, n_later=nlater,
                                    n_seeds=len(seeds)))
    return "\n".join(lines), pd.DataFrame(summary)


if __name__ == "__main__":
    items = pd.read_parquet(os.path.join(ROOT, "results", "item_effects.parquet"))
    text, summ = run_audit(items, n_boot=int(sys.argv[1]) if len(sys.argv) > 1 else 10000)
    open(os.path.join(ROOT, "docs", "AUDIT_PHASE1.md"), "w").write(text + "\n")
    summ.to_csv(os.path.join(ROOT, "results", "audit_summary.csv"), index=False)
    print(text)
