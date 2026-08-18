"""Figure 1: commitment maturity and recovery maturity as functions of training step."""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import ROOT, STEPS, SG_SUITES, seed_trajectory
import pandas as pd

SUITE_LABEL = {"npz_ambig": "NP/Z", "mvrr": "MV/RR"}


def maturity_curves(items, suite, mode="full"):
    seeds = sorted(items.seed.unique())
    Cm, Rm = [], []
    for sd in seeds:
        tr = seed_trajectory(items, sd, suite, mode, do_ci=False)
        C, B = tr["C"], tr["B"]
        c_late = tr["C_late"]
        cm = [C.get(s, np.nan) / c_late if c_late else np.nan for s in STEPS]
        # recovery maturity: 1 - R/R_max, using the same normalisation for all seeds
        R = {s: (B[s] / C[s] if (s in C and C[s] > 0 and np.isfinite(B.get(s, np.nan)))
                 else np.nan) for s in STEPS if s in C}
        vals = np.array([R.get(s, np.nan) for s in STEPS], float)
        hi = np.nanmax(vals) if np.any(np.isfinite(vals)) else np.nan
        lo = np.nanmin(vals) if np.any(np.isfinite(vals)) else np.nan
        rm = (hi - vals) / (hi - lo) if np.isfinite(hi) and hi > lo else vals * np.nan
        Cm.append(cm); Rm.append(rm)
    return np.array(Cm, float), np.array(Rm, float)


def main():
    items = pd.read_parquet(os.path.join(ROOT, "results", "item_effects.parquet"))
    fig, axes = plt.subplots(1, len(SG_SUITES), figsize=(11, 4), sharey=True)
    for ax, suite in zip(np.atleast_1d(axes), SG_SUITES):
        Cm, Rm = maturity_curves(items, suite)
        x = np.array(STEPS, float)
        for arr, col, lab in [(Cm, "#1f77b4", "commitment maturity"),
                              (Rm, "#d62728", "recovery maturity")]:
            m = np.nanmedian(arr, axis=0)
            lo = np.nanpercentile(arr, 25, axis=0)
            hi = np.nanpercentile(arr, 75, axis=0)
            ax.plot(x, m, "-o", color=col, ms=4, label=lab)
            ax.fill_between(x, lo, hi, color=col, alpha=0.18, lw=0)
        ax.set_xscale("log"); ax.axhline(0.5, color="gray", lw=.7, ls=":")
        ax.set_title(SUITE_LABEL[suite]); ax.set_xlabel("training step")
        ax.grid(alpha=.25)
    np.atleast_1d(axes)[0].set_ylabel("maturity (fraction of final)")
    np.atleast_1d(axes)[0].legend(frameon=False, fontsize=9)
    fig.tight_layout()
    out = os.path.join(ROOT, "figures", "fig1_commitment_vs_recovery.png")
    fig.savefig(out, dpi=170)
    print("wrote", out)


if __name__ == "__main__":
    main()
