#!/usr/bin/env python3
"""Gate 2 reference engine: fixture generation for Zeta Harp v2.

Implements MATH_SPEC.md exactly. All values are computations compared to
computations (CLAIM_BOUNDARY.md): main-sum sign changes are computed
reference crossings, never certified zeros; amplitudes are computed
spectral, never measured; the zeros fixture is a "reference zero list
(Odlyzko table, refined)" -- refined by high-precision root finding on
mpmath's siegelz, NOT certified (no interval arithmetic here).

Backend: mpmath at mp.dps = 80 for theta / Z values. python-flint is used
if importable; otherwise mpmath alone. The backend actually used is
recorded in every fixture header.

Outputs (JSON) under reference/fixtures/:
  window_W1.json  t in [100, 160]           step 0.25   (dense, low-t stress)
  window_W2.json  t in [9990, 10060]        step 0.5
  window_W3.json  t in [999990, 1000060]    step 0.5
  window_W4.json  t in [1e8, 1e8 + 20]      step 0.5    (short window near 1e8)
  zeros_reference.json  ~40 refined ordinates from the in-repo Odlyzko table
  MANIFEST.txt    SHA-256 of every fixture file

Each window row: t, theta(t) (mp.siegeltheta), theta'(t) (numeric
derivative at working precision), N(t), M(t) (main sum at high precision),
Z_ref(t) (mp.siegelz), R_ref(t) = Z_ref(t) - M(t).
"""

import hashlib
import json
import os
import sys
import time

from mpmath import mp, mpf

try:
    import flint  # noqa: F401
    HAVE_FLINT = True
except ImportError:
    HAVE_FLINT = False

BACKEND = "mpmath+python-flint" if HAVE_FLINT else "mpmath only (python-flint not importable)"

mp.dps = 80

HERE = os.path.dirname(os.path.abspath(__file__))
FIXDIR = os.path.join(HERE, "fixtures")
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ZEROS_TABLE = os.path.join(REPO_ROOT, "experiments", "zeta_cube_null", "zeros1.txt")

DIGITS = 40  # digits stored in fixtures (computed at dps=80)


def ns(x, digits=DIGITS):
    return mp.nstr(x, digits, strip_zeros=False)


def theta(t):
    """Riemann-Siegel theta, exact (mpmath siegeltheta = Im loggamma form)."""
    return mp.siegeltheta(t)


def theta_prime(t):
    """Numeric derivative of exact theta at working precision (dps=80)."""
    return mp.diff(mp.siegeltheta, t)


def n_of_t(t):
    """N(t) = floor(sqrt(t / (2*pi))) -- MATH_SPEC section 3."""
    return int(mp.floor(mp.sqrt(t / (2 * mp.pi))))


def main_sum(t, th=None):
    """M(t) = sum_{n=1}^{N(t)} (2/sqrt(n)) * cos(theta(t) - t*ln(n)).

    High-precision evaluation of MATH_SPEC sections 3-5. Amplitudes are
    computed spectral quantities.
    """
    if th is None:
        th = theta(t)
    N = n_of_t(t)
    s = mpf(0)
    for n in range(1, N + 1):
        s += (2 / mp.sqrt(n)) * mp.cos(th - t * mp.log(n))
    return s, N


def window_fixture(name, t_lo, t_hi, step):
    t0 = time.time()
    rows = []
    npts = int(round((mpf(t_hi) - mpf(t_lo)) / mpf(step))) + 1
    for i in range(npts):
        t = mpf(t_lo) + i * mpf(step)
        th = theta(t)
        thp = theta_prime(t)
        M, N = main_sum(t, th)
        Z = mp.siegelz(t)
        R = Z - M
        rows.append({
            "t": ns(t),
            "theta": ns(th),
            "theta_prime": ns(thp),
            "N": N,
            "M": ns(M),
            "Z_ref": ns(Z),
            "R_ref": ns(R),
        })
    fixture = {
        "fixture": name,
        "kind": "window",
        "t_range": [str(t_lo), str(t_hi)],
        "step": str(step),
        "points": len(rows),
        "mp_dps": mp.dps,
        "stored_digits": DIGITS,
        "backend": BACKEND,
        "spec": "instruments/zeta_harp_v2/MATH_SPEC.md",
        "labels": {
            "M": "main sum (high precision); sign changes are computed reference crossings",
            "Z_ref": "Hardy Z via mp.siegelz (high-precision reference)",
            "R_ref": "honest residual Z_ref - M (defined by subtraction, not by the RS correction series)",
            "theta": "Riemann-Siegel theta, exact (mp.siegeltheta)",
            "theta_prime": "numeric derivative of exact theta at dps=80",
        },
        "rows": rows,
    }
    dt = time.time() - t0
    print(f"  {name}: {len(rows)} points in {dt:.1f}s "
          f"(N(t) at left edge = {rows[0]['N']})")
    return fixture


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def zeros_fixture(n_select=40, refine_dps=50, t_min=14.0, t_max=75000.0):
    """Reference zero list (Odlyzko table, refined).

    Selects ~n_select ordinates spread across [t_min, t_max] from the
    in-repo table, refines each with mp.findroot on siegelz to 30+ digits,
    and records the refined ordinate plus Z'(gamma) (numeric derivative).
    NOT certified: no interval arithmetic is performed.
    """
    table_sha = sha256_file(ZEROS_TABLE)
    with open(ZEROS_TABLE) as f:
        table = [float(line) for line in f if line.strip()]
    usable = [g for g in table if t_min <= g <= t_max]
    # even spread by index across the usable range
    idxs = [round(i * (len(usable) - 1) / (n_select - 1)) for i in range(n_select)]
    idxs = sorted(set(idxs))

    rows = []
    t0 = time.time()
    for i in idxs:
        g0 = usable[i]
        with mp.workdps(refine_dps):
            gamma = mp.findroot(mp.siegelz, mpf(repr(g0)))
            zp = mp.diff(mp.siegelz, gamma)
            resid = mp.siegelz(gamma)
        rows.append({
            "table_index": i + 1,           # 1-based index into the table
            "table_value": repr(g0),
            "gamma_refined": mp.nstr(gamma, 35, strip_zeros=False),
            "Z_prime_at_gamma": mp.nstr(zp, 30, strip_zeros=False),
            "abs_Z_at_gamma": mp.nstr(abs(resid), 5),
            "refine_offset": mp.nstr(gamma - mpf(repr(g0)), 8),
        })
    dt = time.time() - t0
    print(f"  zeros: {len(rows)} ordinates refined in {dt:.1f}s")
    return {
        "fixture": "zeros_reference",
        "kind": "reference zero list (Odlyzko table, refined)",
        "status": "NOT certified; refined by mp.findroot on siegelz at dps="
                  f"{refine_dps} (30+ digit targets), no interval arithmetic",
        "source_table": "experiments/zeta_cube_null/zeros1.txt",
        "source_table_sha256": table_sha,
        "source_table_lines": len(table),
        "source_table_range": [repr(table[0]), repr(table[-1])],
        "selection": f"{len(rows)} ordinates spread across [{t_min}, {t_max}]",
        "backend": BACKEND,
        "rows": rows,
    }


def main():
    os.makedirs(FIXDIR, exist_ok=True)
    print(f"backend: {BACKEND}; mp.dps = {mp.dps}")

    windows = [
        ("window_W1", 100, 160, mpf("0.25")),
        ("window_W2", 9990, 10060, mpf("0.5")),
        ("window_W3", 999990, 1000060, mpf("0.5")),
        ("window_W4", 100000000, mpf("100000020"), mpf("0.5")),
    ]

    written = []
    for name, lo, hi, step in windows:
        fx = window_fixture(name, lo, hi, step)
        path = os.path.join(FIXDIR, name + ".json")
        with open(path, "w") as f:
            json.dump(fx, f, indent=1)
        written.append(path)

    zf = zeros_fixture()
    zpath = os.path.join(FIXDIR, "zeros_reference.json")
    with open(zpath, "w") as f:
        json.dump(zf, f, indent=1)
    written.append(zpath)

    manifest = os.path.join(FIXDIR, "MANIFEST.txt")
    with open(manifest, "w") as f:
        f.write("# SHA-256 manifest, Zeta Harp v2 reference fixtures (Gate 2)\n")
        f.write(f"# backend: {BACKEND}; mp.dps = {mp.dps}\n")
        for path in written:
            f.write(f"{sha256_file(path)}  {os.path.basename(path)}\n")
    print("wrote", manifest)


if __name__ == "__main__":
    sys.exit(main())
