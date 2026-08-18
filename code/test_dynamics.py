"""Sanity checks for the acquisition-time extraction, on synthetic curves.

These guard the thing the whole study rests on: that T_commit and T_recover are
read off a curve the way the pre-registration says, and that a curve where the
two abilities arrive together does *not* produce a spurious separation.
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import STEPS
from dynamics import times_from_curves

n = len(STEPS)


def test_dissociated():
    """Commitment saturates at step 4000, recovery only much later."""
    c = np.array([0.1, 0.2, 0.5, 1.0, 3.0] + [3.0] * (n - 5))
    b = np.array([0.05, 0.1, 0.3, 0.7, 2.4, 2.4, 2.1, 1.2, 0.5, 0.3, 0.3, 0.3])
    r = times_from_curves(c, b)
    assert r["T_commit"] == 4000, r
    assert r["T_recover"] is not None and r["T_recover"] > 4000, r
    assert r["D"] > 0, r
    print("  dissociated:", {k: r[k] for k in ("T_commit", "T_recover", "improvement", "D")})


def test_simultaneous():
    """Both arrive at the same checkpoint: R is already flat, so no T_recover."""
    c = np.array([0.1, 0.2, 0.5, 1.0, 3.0] + [3.0] * (n - 5))
    b = c * 0.1
    r = times_from_curves(c, b)
    assert r["T_commit"] == 4000, r
    assert not np.isfinite(r["T_recover"]), r
    assert not np.isfinite(r["D"]), r
    print("  simultaneous: no T_recover, improvement =", r["improvement"])


def test_no_commitment():
    """A model that never shows the interaction yields nothing at all."""
    r = times_from_curves(np.zeros(n) - 0.1, np.zeros(n))
    assert not np.isfinite(r["T_commit"]), r
    print("  no commitment: T_commit is nan")


def test_transient_spike_ignored():
    """A single early oscillation must not be mistaken for acquisition."""
    c = np.array([0.1, 3.5, 0.1, 0.2, 0.5, 1.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0])
    b = c * 0.5
    r = times_from_curves(c, b)
    # step512 holds the spike but fails the sustain rule; step8000 is still
    # below half the late plateau, so acquisition is only credited at step16000.
    assert r["T_commit"] == 16000, r
    print("  transient spike ignored: T_commit =", r["T_commit"])


if __name__ == "__main__":
    for f in [test_dissociated, test_simultaneous, test_no_commitment,
              test_transient_spike_ignored]:
        print(f.__name__)
        f()
    print("\nall sanity checks passed")
