"""Figure 1: what actually happens to commitment and to residual burden.

Deliberately plots the raw quantities rather than a rescaled "maturity". R = B/C
is a ratio whose denominator is ~0 before commitment exists, so any min-max
normalisation of R is dominated by that degenerate region and would suggest a
recovery trajectory that is not there.
"""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import ROOT, STEPS, SG_SUITES
from dynamics import build_arrays, burden, observed

SUITE_LABEL = {"npz_ambig": "NP/Z", "mvrr": "MV/RR"}
BLUE, RED = "#1f77b4", "#d62728"


def panel(ax, x, arr, color, label):
    med = np.nanmedian(arr, axis=0)
    lo = np.nanpercentile(arr, 10, axis=0)
    hi = np.nanpercentile(arr, 90, axis=0)
    ax.plot(x, med, "-o", color=color, ms=4, label=label)
    ax.fill_between(x, lo, hi, color=color, alpha=0.18, lw=0)


def main():
    items = pd.read_parquet(os.path.join(ROOT, "results", "item_effects.parquet"))
    x = np.array(STEPS, float)
    fig, axes = plt.subplots(2, len(SG_SUITES), figsize=(11, 6.4), sharex=True)

    for col, suite in enumerate(SG_SUITES):
        seeds, itemlist, C, G = build_arrays(items, suite, "full")
        obs = observed(C, G)
        c = np.nanmean(C, axis=2)
        b = np.array([burden(G[s]) for s in range(len(seeds))])
        tc = np.nanmedian(obs.T_commit.values.astype(float))

        ax = axes[0, col]
        panel(ax, x, c, BLUE, "commitment $C$")
        panel(ax, x, b, RED, "residual burden $B$")
        ax.set_xscale("log"); ax.set_yscale("symlog", linthresh=0.1)
        ax.axvline(tc, color="k", lw=.8, ls="--")
        ax.annotate("median $T_{commit}$", (tc, ax.get_ylim()[1]), fontsize=8,
                    ha="right", va="top", rotation=90, xytext=(-3, -4),
                    textcoords="offset points")
        ax.set_title(SUITE_LABEL[suite]); ax.grid(alpha=.25)
        ax.legend(frameon=False, fontsize=9, loc="upper left")
        if col == 0:
            ax.set_ylabel("bits (symlog)")

        # R only where commitment exists; before that the ratio is meaningless
        R = np.where(c > 0.5, b / np.maximum(c, 1e-9), np.nan)
        ax = axes[1, col]
        panel(ax, x, R, "#6a3d9a", "$R = B/C$")
        ax.set_xscale("log"); ax.set_ylim(0, None)
        ax.axvline(tc, color="k", lw=.8, ls="--")
        ax.set_xlabel("training step"); ax.grid(alpha=.25)
        ax.legend(frameon=False, fontsize=9)
        if col == 0:
            ax.set_ylabel("residual burden / initial disruption")

    fig.suptitle("Commitment grows; the residual burden it leaves behind does not shrink\n"
                 "(burden rectified at the population level, as PREREG.md specifies)",
                 fontsize=10)
    fig.tight_layout()
    out = os.path.join(ROOT, "figures", "fig1_commitment_vs_recovery.png")
    fig.savefig(out, dpi=170)
    print("wrote", out)


if __name__ == "__main__":
    main()
