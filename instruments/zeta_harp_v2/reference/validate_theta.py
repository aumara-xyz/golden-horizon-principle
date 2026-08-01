#!/usr/bin/env python3
"""Gate 2 validator: browser asymptotic theta vs exact reference.

Re-implements, in pure float64 (the arithmetic the browser will use), the
working asymptotic of MATH_SPEC.md section 2:

    theta(t)  ~ (t/2)*ln(t/(2*pi)) - t/2 - pi/8 + 1/(48*t) + 7/(5760*t^3)
    theta'(t) ~ (1/2)*ln(t/(2*pi)) - 1/(48*t^2) - 7/(1920*t^4)

and reports max / RMS error against the high-precision fixture values
(mp.siegeltheta at dps=80, VALIDATION_PLAN.md metric 3). A later stage runs
this same script against the browser formulas; any browser implementation
must match this float64 reference implementation term for term.

The error is decomposed honestly into two parts:

  series truncation : asymptotic formula evaluated at dps=50 vs exact theta
                      (the cost of the truncated series itself)
  float64 total     : float64 asymptotic vs exact theta (adds rounding)

Because theta(t) grows (~5.5e6 rad at t=1e6, ~8.0e8 rad at t=1e8), NO
float64 implementation can beat ~1 ulp of theta in absolute terms at the
high windows. Targets are therefore absolute for W1/W2 and ulp-relative
for W3/W4; W4 sitting at ~1 ulp documents the float64 phase-accuracy
frontier -- where the instrument's honest range ends (VALIDATION_PLAN W4).

Exit status 0 iff every window meets its target.
"""

import json
import math
import os
import sys

from mpmath import mp

mp.dps = 50

HERE = os.path.dirname(os.path.abspath(__file__))
FIXDIR = os.path.join(HERE, "fixtures")

# max-abs theta error targets (VALIDATION_PLAN metric 3):
#   ("abs", x)  -> float64-total max error < x radians
#   ("ulp", k)  -> float64-total max error < k * ulp_f64(theta(t))
TARGETS = {
    "window_W1": ("abs", 1e-6),
    "window_W2": ("abs", 1e-9),
    "window_W3": ("ulp", 4.0),
    "window_W4": ("ulp", 4.0),
}


def ulp_f64(x):
    """Spacing of float64 numbers at magnitude |x|."""
    return math.ulp(abs(float(x)))

TWO_PI = 2.0 * math.pi


def theta_asym_f64(t):
    """Browser working asymptotic, float64 (MATH_SPEC section 2)."""
    return (t / 2.0) * math.log(t / TWO_PI) - t / 2.0 - math.pi / 8.0 \
        + 1.0 / (48.0 * t) + 7.0 / (5760.0 * t ** 3)


def theta_prime_asym_f64(t):
    """Browser working asymptotic derivative, float64 (MATH_SPEC section 2)."""
    return 0.5 * math.log(t / TWO_PI) - 1.0 / (48.0 * t ** 2) \
        - 7.0 / (1920.0 * t ** 4)


def theta_asym_hp(t_hp):
    """Same asymptotic series evaluated in high precision (isolates truncation)."""
    return (t_hp / 2) * mp.log(t_hp / (2 * mp.pi)) - t_hp / 2 - mp.pi / 8 \
        + mp.mpf(1) / (48 * t_hp) + mp.mpf(7) / (5760 * t_hp ** 3)


def stats(errs):
    mx = max(errs)
    rms = math.sqrt(sum(e * e for e in errs) / len(errs))
    return mx, rms


def check_window(path):
    with open(path) as f:
        fx = json.load(f)
    name = fx["fixture"]
    errs_f64, errs_series, errs_ulp, errs_thp = [], [], [], []
    for row in fx["rows"]:
        t_hp = mp.mpf(row["t"])
        t = float(t_hp)
        th_exact = mp.mpf(row["theta"])
        # float64 total: float64 asymptotic minus dps-80 exact, measured in hp
        e_f64 = abs(mp.mpf(repr(theta_asym_f64(t))) - th_exact)
        # series truncation only: asymptotic evaluated at dps=50 minus exact
        e_ser = abs(theta_asym_hp(t_hp) - th_exact)
        e_thp = abs(mp.mpf(repr(theta_prime_asym_f64(t))) - mp.mpf(row["theta_prime"]))
        errs_f64.append(float(e_f64))
        errs_series.append(float(e_ser))
        errs_ulp.append(float(e_f64) / ulp_f64(th_exact))
        errs_thp.append(float(e_thp))

    mx_f64, rms_f64 = stats(errs_f64)
    mx_ser, rms_ser = stats(errs_series)
    mx_ulp, _ = stats(errs_ulp)
    mx_thp, rms_thp = stats(errs_thp)
    kind, bound = TARGETS.get(name, ("abs", math.inf))
    if kind == "abs":
        ok = mx_f64 < bound
        tgt = f"target abs < {bound:g} rad"
    else:
        ok = mx_ulp < bound
        tgt = f"target < {bound:g} ulp of theta"
    print(f"{name}: theta float64-total  max={mx_f64:.3e} rms={rms_f64:.3e} rad"
          f" = {mx_ulp:.2f} ulp  ({tgt}: {'PASS' if ok else 'FAIL'})")
    print(f"{name}: theta series-trunc   max={mx_ser:.3e} rms={rms_ser:.3e} rad")
    print(f"{name}: theta' float64       max={mx_thp:.3e} rms={rms_thp:.3e} rad/unit-t")
    return ok


def main():
    paths = sorted(
        os.path.join(FIXDIR, f) for f in os.listdir(FIXDIR)
        if f.startswith("window_") and f.endswith(".json")
    )
    if not paths:
        print("no window fixtures found; run generate_fixtures.py first")
        return 2
    all_ok = all([check_window(p) for p in paths])
    print("theta validation:", "PASS" if all_ok else "FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
