"""Figure 1: binding saturates early; interference is acquired late and keeps growing."""
import os, sys, glob, json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import ROOT, FULL_STEPS, load, trial_measures
from report import pi_cost, slot_table

BLUE, RED, GREY, PURPLE = "#1f77b4", "#d62728", "#7f7f7f", "#6a3d9a"


def main():
    t = trial_measures(load())
    steps = [s for s in FULL_STEPS if s in set(t.step)]
    x = np.array(steps, float)
    fig, ax = plt.subplots(1, 3, figsize=(14, 4.2))

    b = [t[(t.step == s) & (t.condition == "update_1")].groupby("seed").correct.mean() for s in steps]
    p3 = [pi_cost(t, s, 3, nb=400)[3] for s in steps]
    p2 = [pi_cost(t, s, 2, nb=400)[3] for s in steps]

    def band(a, arrs, color, label):
        med = [np.median(v) for v in arrs]
        lo = [np.percentile(v, 10) for v in arrs]
        hi = [np.percentile(v, 90) for v in arrs]
        a.plot(x, med, "-o", color=color, ms=4, label=label)
        a.fill_between(x, lo, hi, color=color, alpha=.18, lw=0)

    band(ax[0], b, BLUE, "binding (update_1 accuracy)")
    ax[0].axhline(0.5, color=GREY, ls=":", lw=.8)
    ax[0].text(150, 0.52, "chance (2 candidates)", fontsize=7, color=GREY)
    ax[0].set_ylim(0.4, 1.02); ax[0].set_title("Binding saturates by step 2,000")

    band(ax[1], p3, RED, "PI cost, 3 states")
    band(ax[1], p2, "#ff9896", "PI cost, 2 states")
    ax[1].axhline(0, color="k", lw=.8)
    ax[1].set_title("Interference is acquired later, and keeps growing")

    sl = slot_table()
    for key, col, lab in [("unmentioned", GREY, "vs never-mentioned"),
                          ("obsolete_oldest", "#2ca02c", "vs oldest obsolete"),
                          ("obsolete_recent", PURPLE, "vs most-recent obsolete")]:
        arrs = [(sl[sl.step == s]["current"] - sl[sl.step == s][key]).groupby(
            sl[sl.step == s].seed).mean().values for s in steps]
        band(ax[2], arrs, col, lab)
    ax[2].axhline(0, color="k", lw=.8)
    ax[2].set_yscale("symlog", linthresh=1)
    ax[2].set_title("Retrieval holds; ordering among\nmentioned values inverts")

    for a in ax:
        a.set_xscale("log"); a.set_xlabel("training step"); a.grid(alpha=.25)
        a.legend(frameon=False, fontsize=8)
    ax[0].set_ylabel("accuracy"); ax[1].set_ylabel("control − update accuracy")
    ax[2].set_ylabel("log2-prob margin (bits, symlog)")
    fig.suptitle("Pythia-410M, 10 pretraining runs: learning to remember is not learning to forget",
                 fontsize=11)
    fig.tight_layout()
    out = os.path.join(ROOT, "figures", "fig1_binding_vs_interference.png")
    fig.savefig(out, dpi=170); print("wrote", out)


if __name__ == "__main__":
    main()
