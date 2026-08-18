"""Decouple D* from M_base by conditioning on it, three ways.

D* = M_unrelated - M_semantic is mechanically bounded by how much margin the item
has to lose, i.e. by M_base. A falling D*/M_base ratio is the right test given
that coupling, but it is still a ratio. Here M_base is instead held fixed:

  (a) stratified   compare D* across checkpoints *within* M_base bins
  (b) regression   D* ~ M_base + step, reading the step effect
  (c) matched      resample items at each checkpoint to a common M_base
                   distribution, then recompute D*

If D* at fixed M_base is flat across training, there is no filtering trajectory
and the ratio result is an artifact of the coupling. If it falls, filtering
genuinely improves.
"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import ROOT, FULL_STEPS, eligible, crossed_bootstrap

BINS = np.arange(0, 11, 2.0)
REF_STEP = 143000


def paired(p, elig, position):
    """One row per (seed, step, item): M_base and D* at that position."""
    q = p[p.item.isin(elig)]
    b = q[q.condition == "base"].set_index(["seed", "step", "item"]).M.rename("M_base")
    u = q[(q.condition == "unrelated") & (q.position == position)] \
        .set_index(["seed", "step", "item"]).M
    s = q[(q.condition == "semantic") & (q.position == position)] \
        .set_index(["seed", "step", "item"]).M
    j = b.index.intersection(u.index).intersection(s.index)
    return pd.DataFrame({"M_base": b[j], "Dstar": (u[j] - s[j])}).reset_index()


def main():
    p = pd.read_parquet(os.path.join(ROOT, "results", "margins.parquet"))
    elig = eligible(p)
    L, A = [], None; A = L.append
    A("# Holding `M_base` fixed\n")
    A("`D*` is bounded by the margin an item has to lose, so it is not independent "
      "of `M_base` by construction. The ratio analysis in `PHASE_A.md` is the right "
      "test given that coupling, but it is still a ratio. Here `M_base` is held fixed "
      "instead, three ways.\n")

    for position in ("before", "after"):
        d = paired(p, elig, position)
        d = d[d.step >= 4000]                       # M_base is near zero before this
        A(f"\n## Distractor {position} the relevant fact\n")

        # ---- (a) stratified
        d["bin"] = pd.cut(d.M_base, BINS)
        tab = d.pivot_table(index="step", columns="bin", values="Dstar",
                            aggfunc="mean", observed=True)
        cnt = d.pivot_table(index="step", columns="bin", values="Dstar",
                            aggfunc="size", observed=True)
        A("### (a) `D*` within fixed `M_base` bins\n")
        A("| step | " + " | ".join(str(c) for c in tab.columns) + " |")
        A("|---" * (len(tab.columns) + 1) + "|")
        for st in tab.index:
            cells = []
            for c in tab.columns:
                v, n = tab.loc[st, c], cnt.loc[st, c]
                cells.append(f"{v:+.2f}" if n >= 200 else "—")
            A(f"| {int(st):,} | " + " | ".join(cells) + " |")
        A("\n(cells with fewer than 200 observations are suppressed)\n")

        # ---- (b) regression
        # dummies must be built from numerically sorted steps with an explicit
        # reference; get_dummies on stringified steps sorts "128000" before "4000"
        steps_sorted = sorted(d.step.unique())
        ref_step = steps_sorted[0]
        X = pd.DataFrame({f"step_{st}": (d.step == st).astype(float)
                          for st in steps_sorted[1:]})
        X.insert(0, "M_base", d.M_base.values)
        X.insert(0, "const", 1.0)
        beta, *_ = np.linalg.lstsq(X.values, d.Dstar.values, rcond=None)
        raw = d.groupby("step").Dstar.mean()
        names = list(X.columns[2:])
        eff = dict(zip(names, beta[2:]))
        A("### (b) `D* ~ M_base + step`\n")
        A(f"Coefficient on `M_base`: **{beta[1]:+.3f}** bits per bit — the coupling is "
          f"strong, as expected.\n")
        A("| step | raw `D*` | step effect with `M_base` held fixed |")
        A("|---|---|---|")
        A(f"| {ref_step:,} | {raw.loc[ref_step]:+.2f} | 0 (reference) |")
        for n in sorted(names, key=lambda z: int(z.split("_")[1])):
            st = int(n.split("_")[1])
            A(f"| {st:,} | {raw.loc[st]:+.2f} | {eff[n]:+.3f} |")
        span_raw = raw.max() - raw.loc[ref_step]
        span_adj = max(list(eff.values()) + [0.0]) - min(list(eff.values()) + [0.0])
        A(f"\nRaw growth from step {ref_step:,}: **{span_raw:+.2f}** bits. "
          f"With `M_base` held fixed the step effects span **{span_adj:.2f}** bits.\n")

        # ---- (c) distribution matching
        A("### (c) items resampled to a common `M_base` distribution\n")
        ref = d[d.step == REF_STEP]
        rng = np.random.default_rng(20260819)
        ref_hist, edges = np.histogram(ref.M_base, bins=BINS)
        ref_w = ref_hist / ref_hist.sum()
        rows = []
        for st, g in d.groupby("step"):
            idx = np.digitize(g.M_base, edges) - 1
            picks = []
            for b in range(len(ref_w)):
                pool = g.index[(idx == b)]
                if len(pool) == 0:
                    continue
                k = int(round(ref_w[b] * 4000))
                picks.append(rng.choice(pool, size=k, replace=True))
            if not picks:
                continue
            sel = d.loc[np.concatenate(picks)]
            m, lo, hi = crossed_bootstrap(sel.Dstar.values, sel.seed.values, n=1500)
            rows.append((st, sel.M_base.mean(), m, lo, hi))
        A("| step | matched mean `M_base` | matched `D*` | 95% CI |")
        A("|---|---|---|---|")
        for st, mb, m, lo, hi in rows:
            A(f"| {int(st):,} | {mb:+.2f} | {m:+.2f} | [{lo:+.2f}, {hi:+.2f}] |")
        vals = [r[2] for r in rows]
        A(f"\nAcross checkpoints at matched `M_base`, `D*` spans "
          f"**{min(vals):+.2f} to {max(vals):+.2f}** bits "
          f"(raw span {raw.min():+.2f} to {raw.max():+.2f}).\n")

    txt = "\n".join(L)
    open(os.path.join(ROOT, "docs", "MATCHED_MBASE.md"), "w").write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
