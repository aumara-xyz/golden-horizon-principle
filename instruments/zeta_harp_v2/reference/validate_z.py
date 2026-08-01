#!/usr/bin/env python3
"""Gate 2 validator: float64 main sum vs high-precision reference.

Re-implements the browser pipeline in pure float64 -- asymptotic theta
(MATH_SPEC section 2) feeding the main sum M(t) (sections 3-5) -- and
reports, per fixture window:

  1. reconstruction error  max/RMS of (M_hp + R_ref) - Z_ref  (fixture
     self-consistency; numerical noise by construction, guards wiring bugs)
  2. implementation error  max/RMS of M_f64 - M_hp             (float64 +
     asymptotic-theta cost of the browser pipeline)
  3. remainder scale       max/RMS of |M_f64 - Z_ref| and of |R_ref|
     (demonstrates how large the un-drawn remainder is; the main sum alone
     is NOT Z, and its sign changes are computed reference crossings only)

All quantities are computed spectral values compared against computed
references; nothing here certifies a zero.
"""

import json
import math
import os
import sys

from mpmath import mp

mp.dps = 50

HERE = os.path.dirname(os.path.abspath(__file__))
FIXDIR = os.path.join(HERE, "fixtures")

TWO_PI = 2.0 * math.pi


def theta_asym_f64(t):
    """Browser working asymptotic, float64 (same as validate_theta.py)."""
    return (t / 2.0) * math.log(t / TWO_PI) - t / 2.0 - math.pi / 8.0 \
        + 1.0 / (48.0 * t) + 7.0 / (5760.0 * t ** 3)


def main_sum_f64(t):
    """Float64 main sum with asymptotic theta (browser pipeline).

    M(t) = sum_{n=1}^{N(t)} (2/sqrt(n)) * cos(theta(t) - t*ln(n)),
    N(t) = floor(sqrt(t/(2*pi))).
    """
    th = theta_asym_f64(t)
    N = int(math.floor(math.sqrt(t / TWO_PI)))
    s = 0.0
    for n in range(1, N + 1):
        s += (2.0 / math.sqrt(n)) * math.cos(th - t * math.log(n))
    return s, N


def stats(errs):
    mx = max(errs)
    rms = math.sqrt(sum(e * e for e in errs) / len(errs))
    return mx, rms


def check_window(path):
    with open(path) as f:
        fx = json.load(f)
    name = fx["fixture"]
    recon, impl, m_vs_z, r_ref, n_mismatch = [], [], [], [], 0
    for row in fx["rows"]:
        t_hp = mp.mpf(row["t"])
        M_hp = mp.mpf(row["M"])
        Z = mp.mpf(row["Z_ref"])
        R = mp.mpf(row["R_ref"])
        recon.append(abs(float((M_hp + R) - Z)))
        M64, N64 = main_sum_f64(float(t_hp))
        if N64 != row["N"]:
            n_mismatch += 1
        impl.append(abs(float(mp.mpf(repr(M64)) - M_hp)))
        m_vs_z.append(abs(float(mp.mpf(repr(M64)) - Z)))
        r_ref.append(abs(float(R)))

    mx_rec, rms_rec = stats(recon)
    mx_imp, rms_imp = stats(impl)
    mx_mz, rms_mz = stats(m_vs_z)
    mx_r, rms_r = stats(r_ref)
    ok = mx_rec < 1e-30 and n_mismatch == 0
    print(f"{name}:")
    print(f"  reconstruction (M_hp+R_ref)-Z_ref : max={mx_rec:.3e} rms={rms_rec:.3e}"
          f"  ({'PASS' if mx_rec < 1e-30 else 'FAIL'} < 1e-30)")
    print(f"  implementation M_f64 - M_hp       : max={mx_imp:.3e} rms={rms_imp:.3e}")
    print(f"  main sum vs Z_ref |M_f64 - Z_ref| : max={mx_mz:.3e} rms={rms_mz:.3e}")
    print(f"  reference remainder |R_ref|       : max={mx_r:.3e} rms={rms_r:.3e}")
    print(f"  N(t) f64-vs-fixture mismatches    : {n_mismatch}"
          f"  ({'PASS' if n_mismatch == 0 else 'FAIL'})")
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
    print("Z validation:", "PASS" if all_ok else "FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
