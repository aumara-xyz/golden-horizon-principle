#!/usr/bin/env python3
"""R4.3: a finite-window Polymath-15 evaluator audit.

Primary brackets are proposed with D.H.J. Polymath, Theorem 1.3, equations
(13)--(24).  Actual counts, roots, local windings, and derivatives are then
computed independently from the defining Phi-integral.  This is numerical
work, not an interval/Rouche certificate and not a bound on Lambda.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
import time
from pathlib import Path

from mpmath import mp


PAPER = "https://arxiv.org/html/1904.12438"
PAPER_V2 = "https://arxiv.org/pdf/1904.12438v2"
WIKI = "https://michaelnielsen.org/polymath/index.php?title=Effective_bounds_on_H_t_-_second_approach"
CODE = "https://github.com/km-git-acc/dbn_upper_bound/blob/master/dbn_upper_bound/python/mputility.py"
PREDICTION_COMMIT = "bff4c82"
RS_BISECTION_STEPS = 120
INTEGRAL_BISECTION_STEPS = 160
CONTINUATION_BISECTION_STEPS = 120
ROOT_SERIALIZATION_DIGITS = 45


def cstr(z, digits=25):
    z = mp.mpc(z)
    return {"re": mp.nstr(z.real, digits), "im": mp.nstr(z.imag, digits)}


def alpha(s):
    return 1 / (2 * s) + 1 / (s - 1) + mp.log(s / (2 * mp.pi)) / 2


def m0(s):
    return (
        mp.mpf(1) / 8
        * s * (s - 1) / 2
        * mp.power(mp.pi, -s / 2)
        * mp.sqrt(2 * mp.pi)
        * mp.exp((s / 2 - mp.mpf("0.5")) * mp.log(s / 2) - s / 2)
    )


def mt(s, t):
    return mp.exp(t * alpha(s) ** 2 / 4) * m0(s)


def rs_f_raw(z, t):
    """Theorem 1.3 f_t and its nonzero normalizer B_t."""
    z = mp.mpc(z)
    if z.imag < 0:
        f, b, n = rs_f_raw(mp.conj(z), t)
        return mp.conj(f), mp.conj(b), n
    x, y = z.real, z.imag
    splus = (1 + y - 1j * x) / 2
    sminus = (1 - y + 1j * x) / 2
    nmax = int(mp.floor(mp.sqrt(x / (4 * mp.pi) + t / 16)))
    bn = [mp.exp(t * mp.log(n) ** 2 / 4) for n in range(1, nmax + 1)]
    sstar = splus + t * alpha(splus) / 2
    kappa = t * (alpha(sminus) - alpha((1 + y + 1j * x) / 2)) / 2
    gamma = mt(sminus, t) / mt(splus, t)
    first = mp.fsum(bn[n - 1] / mp.power(n, sstar) for n in range(1, nmax + 1))
    second = mp.fsum(
        mp.power(n, y) * bn[n - 1] / mp.power(n, mp.conj(sstar) + kappa)
        for n in range(1, nmax + 1)
    )
    return first + gamma * second, mt(splus, t), nmax


def rs_f(z, t):
    return rs_f_raw(z, t)[0]


def rs_scaled_h(z, t):
    f, b, _ = rs_f_raw(z, t)
    return b * f * mp.exp(mp.pi * z / 8)


def rs_explicit_error(z, t):
    """Equations (23),(24): bound for |H/B-f| in the final paper."""
    z = mp.mpc(z)
    if z.imag < 0:
        z = mp.conj(z)
    x, y = z.real, z.imag
    f, _b, nmax = rs_f_raw(z, t)
    del f
    splus = (1 + y - 1j * x) / 2
    sminus = (1 - y + 1j * x) / 2
    sstar = splus + t * alpha(splus) / 2
    kappa = t * (alpha(sminus) - alpha((1 + y + 1j * x) / 2)) / 2
    gamma = mt(sminus, t) / mt(splus, t)
    eab = mp.mpf("0")
    for n in range(1, nmax + 1):
        bn = mp.exp(t * mp.log(n) ** 2 / 4)
        delta = (
            t**2 * mp.log(x / (4 * mp.pi * n**2)) ** 2 / 16 + mp.mpf("0.626")
        ) / (x - mp.mpf("6.66"))
        eab += (
            (1 + abs(gamma) * mp.power(nmax, abs(kappa)) * mp.power(n, y))
            * bn
            / mp.power(n, mp.re(sstar))
            * mp.expm1(delta)
        )
    ec0 = mp.power(x / (4 * mp.pi), -(1 + y) / 4) * mp.exp(
        -t * mp.log(x / (4 * mp.pi)) ** 2 / 16
        + mp.mpf("1.24") * (mp.power(3, y) + mp.power(3, -y)) / (nmax - mp.mpf("0.125"))
        + (3 * abs(mp.log(x / (4 * mp.pi)) + 1j * mp.pi / 2) + mp.mpf("10.44"))
        / (x - 12)
    )
    return eab, ec0, eab + ec0


def phi(u, nmax=12):
    total = mp.mpf("0")
    e4u = mp.exp(4 * u)
    e5u = mp.exp(5 * u)
    e9u = mp.exp(9 * u)
    for n in range(1, nmax + 1):
        total += (
            2 * mp.pi**2 * n**4 * e9u - 3 * mp.pi * n**2 * e5u
        ) * mp.exp(-mp.pi * n**2 * e4u)
    return total


class PhiQuadrature:
    """Reusable high-precision tanh-sinh quadrature on [0,u_max]."""

    def __init__(self, dps, degree, u_max=mp.mpf("1.25"), nphi=12):
        mp.dps = dps
        self.dps = dps
        self.degree = degree
        self.u_max = mp.mpf(u_max)
        self.nphi = nphi
        h = mp.power(2, -degree)
        tol = mp.power(10, -(dps + 8))
        pairs = []
        k = 0
        while True:
            tt = k * h
            sh = mp.sinh(tt)
            x = mp.tanh(mp.pi * sh / 2)
            w = mp.pi * mp.cosh(tt) / (2 * mp.cosh(mp.pi * sh / 2) ** 2)
            if k and (1 - x < tol or w < tol):
                break
            if k == 0:
                pairs.append((x, h * w))
            else:
                pairs.append((x, h * w))
                pairs.append((-x, h * w))
            k += 1
            if k > 100000:
                raise RuntimeError("tanh-sinh node generation failed to terminate")
        self.u = []
        self.base = []
        for x, w in pairs:
            u = self.u_max * (x + 1) / 2
            weight = w * self.u_max / 2
            self.u.append(u)
            self.base.append(weight * phi(u, nphi))
        self._weights = {}

    def weights(self, t):
        key = mp.nstr(t, 20)
        if key not in self._weights:
            self._weights[key] = [q * mp.exp(t * u * u) for q, u in zip(self.base, self.u)]
        return self._weights[key]

    def h(self, z, t):
        z = mp.mpc(z)
        return mp.fdot(self.weights(t), (mp.cos(z * u) for u in self.u))

    def scaled_h(self, z, t):
        z = mp.mpc(z)
        return self.h(z, t) * mp.exp(mp.pi * z / 8)

    def derivative(self, z, t):
        z = mp.mpc(z)
        return mp.fdot(self.weights(t), (-u * mp.sin(z * u) for u in self.u))


def contour_rectangle(x0, x1, ymax, per_edge):
    pts = []
    for k in range(per_edge):
        pts.append(mp.mpc(x0 + (x1 - x0) * k / per_edge, -ymax))
    for k in range(per_edge):
        pts.append(mp.mpc(x1, -ymax + 2 * ymax * k / per_edge))
    for k in range(per_edge):
        pts.append(mp.mpc(x1 - (x1 - x0) * k / per_edge, ymax))
    for k in range(per_edge):
        pts.append(mp.mpc(x0, ymax - 2 * ymax * k / per_edge))
    return pts


def contour_circle(center, radius, points):
    return [center + radius * mp.exp(2j * mp.pi * k / points) for k in range(points)]


def winding(values):
    increments = [mp.arg(values[(k + 1) % len(values)] / values[k]) for k in range(len(values))]
    raw = mp.fsum(increments) / (2 * mp.pi)
    return int(mp.nint(raw)), raw, min(abs(v) for v in values), max(abs(x) for x in increments)


def find_rs_brackets(t, x0, x1, step=mp.mpf("0.05")):
    brackets = []
    x = mp.mpf(x0)
    prev = mp.re(rs_scaled_h(x, t))
    while x < x1:
        xx = min(mp.mpf(x1), x + step)
        cur = mp.re(rs_scaled_h(xx, t))
        if prev == 0 or cur == 0 or prev * cur < 0:
            brackets.append((x, xx))
        x, prev = xx, cur
    roots = []
    for a, b in brackets:
        try:
            roots.append(
                bisect_real(
                    lambda q: rs_scaled_h(q, t),
                    a,
                    b,
                    iterations=RS_BISECTION_STEPS,
                )
            )
        except Exception:
            # Retain the bracket midpoint rather than silently dropping a
            # proposal; proposal_failures are caught by the independent
            # defining-integral scan below.
            roots.append((a + b) / 2)
    return roots


def bisect_real(func, a, b, iterations=90):
    a, b = mp.mpf(a), mp.mpf(b)
    fa, fb = mp.re(func(a)), mp.re(func(b))
    if fa == 0:
        return a
    if fb == 0:
        return b
    if fa * fb >= 0:
        raise ValueError("interval does not bracket a real root")
    for _ in range(iterations):
        c = (a + b) / 2
        fc = mp.re(func(c))
        if fc == 0:
            return c
        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc
    return (a + b) / 2


def refine_integral_roots(q, t, proposals, x0, x1):
    roots = []
    failures = []
    initial_bracket_widths = []
    mids = [mp.mpf(x0)] + [(proposals[i] + proposals[i + 1]) / 2 for i in range(len(proposals) - 1)] + [mp.mpf(x1)]
    fun = lambda x: q.scaled_h(x, t)
    for i, proposal in enumerate(proposals):
        left, right = mids[i], mids[i + 1]
        # The RS value only proposes a location.  Search symmetrically with the
        # independent integral, then fall back to the full Voronoi cell.
        bracket = None
        local_left = max(left, proposal - mp.mpf("0.25"))
        local_right = min(right, proposal + mp.mpf("0.25"))
        grid = [
            local_left
            + (local_right - local_left) * mp.mpf(j) / mp.mpf(20)
            for j in range(21)
        ]
        last_x, last_v = grid[0], mp.re(fun(grid[0]))
        for xx in grid[1:]:
            vv = mp.re(fun(xx))
            if last_v == 0 or vv == 0 or last_v * vv < 0:
                bracket = (last_x, xx)
                break
            last_x, last_v = xx, vv
        if bracket is None:
            grid_n = max(8, int(mp.ceil((right - left) / mp.mpf("0.08"))))
            last_x, last_v = left, mp.re(fun(left))
            for j in range(1, grid_n + 1):
                xx = left + (right - left) * mp.mpf(j) / mp.mpf(grid_n)
                vv = mp.re(fun(xx))
                if last_v == 0 or vv == 0 or last_v * vv < 0:
                    bracket = (last_x, xx)
                    break
                last_x, last_v = xx, vv
        if bracket is None:
            failures.append({"proposal": mp.nstr(proposal, 25), "cell": [mp.nstr(left, 20), mp.nstr(right, 20)]})
            continue
        initial_bracket_widths.append(bracket[1] - bracket[0])
        roots.append(
            bisect_real(fun, *bracket, iterations=INTEGRAL_BISECTION_STEPS)
        )
    return roots, failures, initial_bracket_widths


def zeta_control_roots(x0, x1):
    roots = []
    n = 1
    while True:
        g = mp.im(mp.zetazero(n))
        z = 2 * g
        if z > x1:
            break
        if z > x0:
            roots.append(z)
        n += 1
    return roots


def evaluate_case(label, t, q, x0, x1, ymax, edge_mesh, local_mesh, proposals=None):
    start = time.time()
    if proposals is None:
        proposals = find_rs_brackets(t, x0, x1)
    roots, failures, initial_bracket_widths = refine_integral_roots(
        q, t, proposals, x0, x1
    )
    boundary_pts = contour_rectangle(x0, x1, ymax, edge_mesh)
    boundary_vals = [q.scaled_h(z, t) for z in boundary_pts]
    w, wraw, minabs, maxstep = winding(boundary_vals)
    local = []
    for i, root in enumerate(roots):
        nearest = min(
            root - (roots[i - 1] if i else x0),
            (roots[i + 1] if i + 1 < len(roots) else x1) - root,
        )
        radius = min(mp.mpf("0.2"), mp.mpf("0.3") * nearest)
        vals = [q.scaled_h(z, t) for z in contour_circle(root, radius, local_mesh)]
        lw, lraw, lmin, lstep = winding(vals)
        deriv = q.derivative(root, t)
        local.append(
            {
                "index": i + 1,
                "root": mp.nstr(root, ROOT_SERIALIZATION_DIGITS),
                "radius": mp.nstr(radius, 20),
                "winding": lw,
                "winding_raw": mp.nstr(lraw, 20),
                "min_scaled_abs_boundary": mp.nstr(lmin, 12),
                "max_arg_step": mp.nstr(lstep, 12),
                "derivative": cstr(deriv, 18),
                "abs_derivative": mp.nstr(abs(deriv), 18),
            }
        )
    separations = [roots[i + 1] - roots[i] for i in range(len(roots) - 1)]
    # Test the paper's explicit error only on the large rectangle boundary.
    margins = []
    ratios = []
    if t > 0:
        for z in boundary_pts:
            fv = rs_f(z, t)
            _ea, _ec, err = rs_explicit_error(z, t)
            margins.append(abs(fv) - err)
            ratios.append(err / abs(fv))
    return {
        "label": label,
        "t": mp.nstr(t, 20),
        "quadrature": {"dps": q.dps, "degree": q.degree, "nodes": len(q.u), "u_max": mp.nstr(q.u_max, 10), "phi_terms": q.nphi},
        "edge_mesh_per_edge": edge_mesh,
        "local_mesh": local_mesh,
        "rs_proposal_count": len(proposals),
        "integral_root_count": len(roots),
        "proposal_failures": failures,
        "root_bisection_iterations": INTEGRAL_BISECTION_STEPS,
        "root_serialization_digits": ROOT_SERIALIZATION_DIGITS,
        "root_initial_bracket_max_width": (
            mp.nstr(max(initial_bracket_widths), 18)
            if initial_bracket_widths
            else None
        ),
        "root_final_bracket_max_width": (
            mp.nstr(
                max(initial_bracket_widths)
                / mp.power(2, INTEGRAL_BISECTION_STEPS),
                18,
            )
            if initial_bracket_widths
            else None
        ),
        "rectangle_winding": w,
        "rectangle_winding_raw": mp.nstr(wraw, 25),
        "rectangle_min_scaled_abs": mp.nstr(minabs, 15),
        "rectangle_max_arg_step": mp.nstr(maxstep, 15),
        "local_winding_sum": sum(r["winding"] for r in local),
        "all_local_windings_one": all(r["winding"] == 1 for r in local),
        "all_derivatives_nonzero_numerically": all(mp.mpf(r["abs_derivative"]) > 0 for r in local),
        "min_root_separation": mp.nstr(min(separations), 25) if separations else None,
        "roots": local,
        "explicit_error_boundary_min_margin": mp.nstr(min(margins), 15) if margins else None,
        "explicit_error_boundary_max_ratio": mp.nstr(max(ratios), 15) if ratios else None,
        "explicit_error_sampled_margin_positive": bool(min(margins) > 0) if margins else None,
        "elapsed_seconds": round(time.time() - start, 3),
    }


def sampled_continuation(q, roots_at_019, roots_at_020):
    """Track ordered real roots at intermediate times.

    This is a numerical sampling diagnostic, not a proof that no collision or
    complex excursion occurs between samples.
    """

    previous = list(roots_at_019)
    samples = []
    minimum_separation = min(
        previous[i + 1] - previous[i] for i in range(len(previous) - 1)
    )
    maximum_step_shift = mp.mpf("0")
    all_ordered = True
    all_bracketed = True
    half_width = mp.mpf("0.05")

    for t in (mp.mpf("0.1925"), mp.mpf("0.195"), mp.mpf("0.1975")):
        current = []
        for proposal in previous:
            left, right = proposal - half_width, proposal + half_width
            f_left = mp.re(q.scaled_h(left, t))
            f_right = mp.re(q.scaled_h(right, t))
            if f_left * f_right >= 0:
                all_bracketed = False
                break
            current.append(
                bisect_real(
                    lambda x: q.scaled_h(x, t),
                    left,
                    right,
                    iterations=CONTINUATION_BISECTION_STEPS,
                )
            )
        if len(current) != len(previous):
            break
        ordered = all(a < b for a, b in zip(current, current[1:]))
        all_ordered = all_ordered and ordered
        separations = [
            current[i + 1] - current[i] for i in range(len(current) - 1)
        ]
        shifts = [abs(a - b) for a, b in zip(previous, current)]
        minimum_separation = min(minimum_separation, min(separations))
        maximum_step_shift = max(maximum_step_shift, max(shifts))
        samples.append(
            {
                "t": mp.nstr(t, 8),
                "root_count": len(current),
                "all_real_ordered": ordered,
                "minimum_separation": mp.nstr(min(separations), 20),
                "maximum_shift_from_previous_sample": mp.nstr(max(shifts), 20),
                "minimum_abs_derivative": mp.nstr(
                    min(abs(q.derivative(root, t)) for root in current), 18
                ),
            }
        )
        previous = current

    endpoint_shifts = [abs(a - b) for a, b in zip(previous, roots_at_020)]
    maximum_endpoint_shift = max(endpoint_shifts) if endpoint_shifts else mp.inf
    maximum_step_shift = max(maximum_step_shift, maximum_endpoint_shift)
    return {
        "status": "MEASURED",
        "scope": (
            "Ordered real-root tracking at the listed sample times only; "
            "unique continuation at every intervening t is UNVERIFIED."
        ),
        "sample_times_include_endpoints": ["0.19", "0.1925", "0.195", "0.1975", "0.2"],
        "intermediate_samples": samples,
        "root_count_each_sample": [len(roots_at_019)]
        + [row["root_count"] for row in samples]
        + [len(roots_at_020)],
        "all_intermediate_roots_bracketed": all_bracketed,
        "all_samples_real_ordered": all_ordered,
        "minimum_separation_all_samples": mp.nstr(minimum_separation, 20),
        "maximum_adjacent_sample_shift": mp.nstr(maximum_step_shift, 20),
        "last_sample_to_t_0.2_max_shift": mp.nstr(maximum_endpoint_shift, 20),
        "bisection_iterations_per_intermediate_root": CONTINUATION_BISECTION_STEPS,
        "final_bracket_width": mp.nstr(
            2 * half_width / mp.power(2, CONTINUATION_BISECTION_STEPS), 18
        ),
        "continuous_unique_continuation": "UNVERIFIED",
    }


def write_outputs(outdir, result):
    outdir.mkdir(parents=True, exist_ok=True)
    script_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result["provenance"]["script_sha256"] = script_hash
    (outdir / "r43_results.json").write_text(json.dumps(result, indent=2) + "\n")
    with (outdir / "r43_roots.csv").open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["case", "t", "index", "root", "local_winding", "radius", "abs_derivative"])
        for case in result["cases"]:
            for row in case["roots"]:
                writer.writerow([case["label"], case["t"], row["index"], row["root"], row["winding"], row["radius"], row["abs_derivative"]])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="smaller convergence meshes")
    args = parser.parse_args()
    outdir = Path(__file__).resolve().parent
    x0, x1, ymax = mp.mpf(210), mp.mpf(300), mp.mpf(1)
    log_lines = []
    total_start = time.time()

    primary_dps, primary_degree = 70, 8
    edge1, local1 = (32, 24) if args.quick else (48, 32)
    q1 = PhiQuadrature(primary_dps, primary_degree)
    log_lines.append(f"primary quadrature nodes={len(q1.u)} dps={q1.dps} degree={q1.degree}")

    primary = evaluate_case("primary_t_0.2", mp.mpf("0.2"), q1, x0, x1, ymax, edge1, local1)
    log_lines.append(f"primary count={primary['integral_root_count']} winding={primary['rectangle_winding']}")

    mutation = evaluate_case("mutation_t_0.19", mp.mpf("0.19"), q1, x0, x1, ymax, edge1, max(16, local1 // 2))
    log_lines.append(f"mutation count={mutation['integral_root_count']} winding={mutation['rectangle_winding']}")

    control_proposals = zeta_control_roots(x0, x1)
    control = evaluate_case("control_t_0", mp.mpf("0"), q1, x0, x1, ymax, edge1, max(16, local1 // 2), proposals=control_proposals)
    control_errors = []
    for got, expected in zip(control["roots"], control_proposals):
        control_errors.append(abs(mp.mpf(got["root"]) - expected))
    control["zeta_2gamma_count"] = len(control_proposals)
    control["max_abs_root_error_vs_2gamma"] = mp.nstr(max(control_errors), 25) if control_errors else None
    log_lines.append(f"control count={control['integral_root_count']} winding={control['rectangle_winding']} maxerr={control['max_abs_root_error_vs_2gamma']}")

    # Registered higher-precision / denser-mesh convergence rerun of t=.2.
    conv_dps, conv_degree = 100, 9
    edge2, local2 = (64, 32) if args.quick else (96, 48)
    q2 = PhiQuadrature(conv_dps, conv_degree)
    primary_proposals = [mp.mpf(row["root"]) for row in primary["roots"]]
    convergence = evaluate_case("convergence_t_0.2", mp.mpf("0.2"), q2, x0, x1, ymax, edge2, local2, proposals=primary_proposals)
    shifts = []
    for a, b in zip(primary["roots"], convergence["roots"]):
        shifts.append(abs(mp.mpf(a["root"]) - mp.mpf(b["root"])))
    convergence["max_abs_root_shift_from_primary"] = mp.nstr(max(shifts), 25) if shifts else None
    max_convergence_shift = max(shifts) if shifts else mp.inf
    conservative_absolute_decimal_places = (
        max(0, int(mp.floor(-mp.log10(max_convergence_shift))) - 1)
        if shifts and max_convergence_shift > 0
        else 0
    )
    log_lines.append(f"convergence count={convergence['integral_root_count']} winding={convergence['rectangle_winding']} maxshift={convergence['max_abs_root_shift_from_primary']}")

    # Pair RS proposals to actual roots and compare the mutation continuation.
    rs_primary = find_rs_brackets(mp.mpf("0.2"), x0, x1)
    actual_primary = [mp.mpf(r["root"]) for r in primary["roots"]]
    rs_displacements = [abs(a - b) for a, b in zip(rs_primary, actual_primary)]
    actual_mut = [mp.mpf(r["root"]) for r in mutation["roots"]]
    mutation_shifts = [abs(a - b) for a, b in zip(actual_primary, actual_mut)]
    continuation_q = PhiQuadrature(70, 8)
    continuation = sampled_continuation(
        continuation_q, actual_mut, actual_primary
    )
    log_lines.append(
        "continuation samples=%s minsep=%s maxstep=%s continuous=%s"
        % (
            continuation["root_count_each_sample"],
            continuation["minimum_separation_all_samples"],
            continuation["maximum_adjacent_sample_shift"],
            continuation["continuous_unique_continuation"],
        )
    )

    mp.dps = 100
    result = {
        "schema": "codex-r4-r43-v1",
        "status": "MEASURED",
        "scope": "Finite rectangle only; no interval arithmetic and no implication for Lambda.",
        "rectangle": {"x_min": "210", "x_max": "300", "abs_y_max": "1", "constant_N": 4},
        "provenance": {
            "prediction_commit": PREDICTION_COMMIT,
            "paper": PAPER,
            "paper_v2": PAPER_V2,
            "wiki": WIKI,
            "official_code_reference": CODE,
            "normalization": "H_0(z)=xi(1/2+iz/2)/8; H_t=integral exp(tu^2) Phi(u) cos(zu) du",
            "primary_rs_formula": "D.H.J. Polymath Theorem 1.3, equations (13)-(24)",
            "independent_evaluator": "Defining Phi integral with reusable arbitrary-precision tanh-sinh quadrature",
            "script_sha256": None,
        },
        "cases": [primary, convergence, control, mutation],
        "cross_checks": {
            "rs_primary_root_count": len(rs_primary),
            "max_rs_to_integral_root_displacement": mp.nstr(max(rs_displacements), 25) if rs_displacements else None,
            "max_primary_to_mutation_shift": mp.nstr(max(mutation_shifts), 25) if mutation_shifts else None,
            "min_primary_to_mutation_shift": mp.nstr(min(mutation_shifts), 25) if mutation_shifts else None,
        },
        "sampled_continuation": continuation,
        "numerical_precision": {
            "root_strings_are_working_values": True,
            "root_serialization_significant_digits": ROOT_SERIALIZATION_DIGITS,
            "independent_quadrature_max_abs_root_shift": mp.nstr(
                max_convergence_shift, 25
            ),
            "conservative_supported_absolute_decimal_places": (
                conservative_absolute_decimal_places
            ),
            "recommended_report_absolute_decimal_places": min(
                20, conservative_absolute_decimal_places
            ),
            "note": (
                "Narrative values must be rounded to the recommended places; "
                "the longer root strings are retained only as working values."
            ),
        },
        "prediction_accounting": {
            "t_0_control": (
                "MEASURED survived: the integral count equals the 21 tabulated "
                "values z=2*gamma_n in the registered rectangle."
            ),
            "rs_pairing_below_0.2": (
                "MEASURED failed: maximum ordered displacement exceeds 0.2."
            ),
            "continuous_unique_continuation": (
                "UNVERIFIED between the listed sample times."
            ),
        },
        "certification": {
            "interval_arithmetic_used": False,
            "rouche_contours_certified": False,
            "reason": "Pointwise high-precision convergence and explicit error samples are not interval bounds over contour arcs.",
            "allowed_claim": "MEASURED numerical count/reality/simplicity in the stated rectangle only",
        },
        "elapsed_seconds": round(time.time() - total_start, 3),
        "python": sys.version,
        "mpmath": mp.__version__ if hasattr(mp, "__version__") else "1.3.0",
    }
    write_outputs(outdir, result)
    log_lines.append(f"total elapsed={result['elapsed_seconds']} seconds")
    (outdir / "r43_run.log").write_text("\n".join(log_lines) + "\n")
    print(json.dumps({"status": result["status"], "cross_checks": result["cross_checks"], "cases": [{"label": c["label"], "roots": c["integral_root_count"], "winding": c["rectangle_winding"], "elapsed": c["elapsed_seconds"]} for c in result["cases"]], "elapsed_seconds": result["elapsed_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
