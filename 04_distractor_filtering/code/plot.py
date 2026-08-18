"""Figure: context use develops longer than the semantic-distractor cost."""
import os, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import ROOT, FULL_STEPS, eligible, dstar

BLUE, RED, ORANGE, GREY = "#1f77b4", "#d62728", "#ff7f0e", "#7f7f7f"


def main():
    p = pd.read_parquet(os.path.join(ROOT, "results", "margins.parquet"))
    elig = eligible(p)
    steps = [s for s in FULL_STEPS if s in set(p.step)]
    x = np.array(steps, float)

    def per_seed(fn):
        return [fn(s) for s in steps]

    mb = per_seed(lambda s: p[(p.condition == "␟base") | ((p.condition == "base") & (p.step == s) &
                              (p.item.isin(elig)))].query("step==@s").groupby("seed").M.mean().values)
    db = per_seed(lambda s: pd.DataFrame({"v": dstar(p, elig, "before", "semantic", step=s)[0],
                                          "s": dstar(p, elig, "before", "semantic", step=s)[1]}
                                         ).groupby("s").v.mean().values)
    da = per_seed(lambda s: pd.DataFrame({"v": dstar(p, elig, "after", "semantic", step=s)[0],
                                          "s": dstar(p, elig, "after", "semantic", step=s)[1]}
                                         ).groupby("s").v.mean().values)

    fig, ax = plt.subplots(1, 3, figsize=(14, 4.2))

    def band(a, arrs, c, lab):
        m = [np.median(v) for v in arrs]
        a.plot(x, m, "-o", color=c, ms=4, label=lab)
        a.fill_between(x, [np.percentile(v, 10) for v in arrs],
                       [np.percentile(v, 90) for v in arrs], color=c, alpha=.18, lw=0)

    band(ax[0], mb, BLUE, "$M_{base}$  context use")
    band(ax[0], db, ORANGE, "$D^*$  distractor before")
    band(ax[0], da, RED, "$D^*$  distractor after")
    ax[0].axhline(0, color="k", lw=.8)
    ax[0].set_ylabel("bits"); ax[0].set_title("Both develop, but not for equally long")

    for arrs, c, lab in [(db, ORANGE, "before"), (da, RED, "after")]:
        rat = [np.median(v) / np.median(w) for v, w in zip(arrs, mb)]
        rat = [r if np.median(w) > 0.3 else np.nan for r, w in zip(rat, mb)]
        ax[1].plot(x, rat, "-o", color=c, ms=4, label=f"$D^*$/$M_{{base}}$, {lab}")
    ax[1].axhline(1, color=GREY, ls=":", lw=.8)
    ax[1].set_ylabel("$D^*$ / $M_{base}$")
    ax[1].set_title("Relative vulnerability falls\n(a flat line would be the null)")

    r = pd.read_csv(os.path.join(ROOT, "results", "trajectories.csv")).set_index("step")
    # growth *factor* since step 4,000. Normalising by each curve's 4k->143k range
    # is not usable here: D_before's range is 0.28 bits, so the denominator explodes.
    for c, col, lab in [("M_base", BLUE, "$M_{base}$"), ("D_before", ORANGE, "$D^*$ before"),
                        ("D_after", RED, "$D^*$ after")]:
        v = r[c]
        v = v[v.index >= 4000] / v.loc[4000]
        ax[2].plot(v.index, v.values, "-o", color=col, ms=4,
                   label=f"{lab}  x{r[c].loc[143000]/r[c].loc[4000]:.2f}")
    ax[2].axhline(1, color=GREY, ls=":", lw=.8)
    ax[2].set_ylabel("growth factor since step 4,000")
    ax[2].set_title("From step 4k on, context use more than\ndoubles; the `before` cost barely moves")

    for a in ax:
        a.set_xscale("log"); a.set_xlabel("training step"); a.grid(alpha=.25)
        a.legend(frameon=False, fontsize=8)
    fig.suptitle("Pythia-410M, 10 pretraining runs: semantic-distractor cost saturates before context use does",
                 fontsize=11)
    fig.tight_layout()
    out = os.path.join(ROOT, "figures", "fig1_context_use_vs_filtering.png")
    fig.savefig(out, dpi=170); print("wrote", out)


if __name__ == "__main__":
    main()
