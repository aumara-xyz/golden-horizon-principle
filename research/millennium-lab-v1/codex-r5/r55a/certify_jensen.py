#!/usr/bin/env python3
"""Arb/Sturm/Hermite replay for selected rogue Jensen polynomials.

This program never evaluates zeta and never reads a zero table.  It computes
Taylor coefficients of ``8 xi(1/2+z)`` from Riemann's positive theta kernel,
adds the preregistered off-line quartet, and subjects selected degree-2/3/4
Jensen polynomials to three independent checks.

The integral enclosures use ``acb.integral`` on a saddle-centred variable.
The logarithmic derivative of every positive theta summand is strictly
decreasing, which supplies explicit exponential bounds for both omitted
u-tails.  The theta sum is truncated after k=2 (k=8 for the small moments),
with the remaining positive summands bounded by their pointwise geometric
ratio at u=0.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

import mpmath as mp
import sympy as sp
from flint import acb, arb, arb_mat, arb_poly, ctx


DELTA = mp.mpf("0.25")
GAMMA_STRINGS = ("14.13", "100", "1000")
DEGREES = (2, 3, 4)


def mp_saddle(moment: int, theta_index: int, digits: int) -> tuple[mp.mpf, mp.mpf, mp.mpf]:
    """Return saddle and rigorous-tail endpoints for one theta summand."""
    mp.mp.dps = digits + 40
    k = mp.mpf(theta_index)
    pi = mp.pi

    def derivative(u: mp.mpf) -> mp.mpf:
        a = 2 * pi * k * k * mp.exp(2 * u)
        moment_term = 0 if moment == 0 else 2 * moment / u
        return moment_term + mp.mpf("2.5") + 2 * a / (a - 3) - a

    if moment == 0 and derivative(mp.mpf("0")) <= 0:
        saddle = mp.mpf("0")
    else:
        lo = mp.mpf("1e-40")
        hi = max(mp.mpf("1"), mp.mpf("0.5") * mp.lambertw(2 * max(1, moment) / (pi * k * k)))
        while derivative(hi) > 0:
            hi *= mp.mpf("1.3")
        for _ in range(300):
            mid = (lo + hi) / 2
            if derivative(mid) > 0:
                lo = mid
            else:
                hi = mid
        saddle = (lo + hi) / 2

    def log_integrand(u: mp.mpf) -> mp.mpf:
        a = 2 * pi * k * k * mp.exp(2 * u)
        value = mp.log(pi * k * k) + mp.mpf("2.5") * u + mp.log(a - 3) - a / 2
        if moment:
            value += 2 * moment * mp.log(u)
        return value

    peak = log_integrand(saddle)
    drop = mp.log(10) * (digits + 25)
    target = peak - drop

    if saddle == 0 or (moment == 0 and log_integrand(mp.mpf("0")) > target):
        left = mp.mpf("0")
    else:
        lo = max(mp.mpf("1e-80"), saddle / 2)
        while log_integrand(lo) > target:
            lo /= 2
        hi = saddle
        for _ in range(300):
            mid = (lo + hi) / 2
            if log_integrand(mid) < target:
                lo = mid
            else:
                hi = mid
        left = (lo + hi) / 2

    lo = max(mp.mpf("0.1"), saddle + mp.mpf("0.1"))
    hi = max(mp.mpf("1"), saddle + mp.mpf("1"))
    while log_integrand(hi) > target:
        hi = saddle + 2 * (hi - saddle)
    lo = saddle
    for _ in range(300):
        mid = (lo + hi) / 2
        if log_integrand(mid) > target:
            lo = mid
        else:
            hi = mid
    right = (lo + hi) / 2
    return saddle, left, right


def add_symmetric_error(value: arb, error: arb) -> arb:
    """Enlarge a ball by a nonnegative error bound."""
    return value + arb(0, str(error.abs_upper()))


def theta_ratio_bound(index: int) -> arb:
    """Uniform bound for phi_{k+1}(u)/phi_k(u), u >= 0."""
    k = arb(index)
    kp = arb(index + 1)
    pi = arb.pi()
    return (
        (kp / k) ** 2
        * (2 * pi * kp**2 - 3)
        / (2 * pi * k**2 - 3)
        * (-pi * (2 * index + 1)).exp()
    )


class ThetaCoefficientCertificate:
    """Cache Arb-enclosed theta moments and xi coefficients."""

    def __init__(self, digits: int) -> None:
        self.digits = digits
        self.log_gamma_cache: dict[int, arb] = {}
        self.integral_audit: dict[str, Any] = {}

    def _term_integral(self, moment: int, theta_index: int) -> tuple[arb, dict[str, Any]]:
        saddle, left, right = mp_saddle(moment, theta_index, self.digits)
        k = arb(theta_index)
        pi = arb.pi()
        u0 = arb(mp.nstr(saddle, self.digits + 30))
        left_a = arb(mp.nstr(left, self.digits + 30))
        right_a = arb(mp.nstr(right, self.digits + 30))
        a0 = 2 * pi * k**2 * (2 * u0).exp()
        p0 = a0 / 2

        if moment == 0:
            scale = arb(1)

            def relative(x: acb, analytic: bool) -> acb:
                h = x - u0
                ex2 = (2 * h).exp()
                return (
                    arb("2.5") * h
                    + ((a0 * ex2 - 3) / (a0 - 3)).log(analytic=analytic)
                    - p0 * (ex2 - 1)
                )

            def integrand(x: acb, analytic: bool) -> acb:
                return relative(x, analytic).exp()

            lower_t = left_a
            upper_t = right_a
        else:
            # Standardize the narrow saddle to width one.  The centred formula
            # is algebraically exact; d0 retains the tiny residual caused by
            # representing the numerical saddle with a finite Arb midpoint.
            m = arb(moment)
            second = -2 * m / u0**2 - 12 * a0 / (a0 - 3) ** 2 - 2 * a0
            scale = 1 / (-second).sqrt()
            d0 = 2 * m / u0 + arb("2.5") + 2 * a0 / (a0 - 3) - a0

            def relative(t: acb, analytic: bool) -> acb:
                h = scale * t
                q = h / u0
                ex2 = (2 * h).exp()
                return (
                    2 * m * ((1 + q).log(analytic=analytic) - q)
                    + ((a0 * ex2 - 3) / (a0 - 3)).log(analytic=analytic)
                    - 2 * a0 / (a0 - 3) * h
                    - p0 * (ex2 - 1 - 2 * h)
                    + d0 * h
                )

            def integrand(t: acb, analytic: bool) -> acb:
                return relative(t, analytic).exp() * scale

            lower_t = (left_a - u0) / scale
            upper_t = (right_a - u0) / scale

        # Splitting into unit pieces prevents wide complex evaluation discs
        # from obscuring the very narrow high-moment saddle.
        lo_float = float(lower_t.mid())
        hi_float = float(upper_t.mid())
        cuts = [lower_t]
        first_integer = math.floor(lo_float) + 1
        last_integer = math.ceil(hi_float) - 1
        cuts.extend(arb(j) for j in range(first_integer, last_integer + 1))
        cuts.append(upper_t)
        central = acb(0)
        for a, b in zip(cuts, cuts[1:]):
            central += acb.integral(
                integrand,
                a,
                b,
                rel_tol=arb(f"1e-{self.digits - 25}"),
                abs_tol=arb(f"1e-{self.digits + 5}"),
                eval_limit=250_000,
            )
        if not central.imag.contains(0):
            raise ArithmeticError("real-axis integral acquired a nonzero imaginary enclosure")
        central_real = central.real

        def derivative_at(u: arb) -> arb:
            a = 2 * pi * k**2 * (2 * u).exp()
            moment_term = arb(0) if moment == 0 else 2 * moment / u
            return moment_term + arb("2.5") + 2 * a / (a - 3) - a

        # Relative endpoint values are evaluated through the same exact
        # centred expression used by the quadrature.
        if moment == 0:
            right_rel = relative(acb(right_a), False).real.exp()
            left_tail = arb(0)
        else:
            left_rel = relative(acb(lower_t), False).real.exp()
            right_rel = relative(acb(upper_t), False).real.exp()
            left_tail = arb(0) if left == 0 else left_rel / derivative_at(left_a)
        right_tail = right_rel / (-derivative_at(right_a))
        scaled = add_symmetric_error(central_real, left_tail + right_tail)

        log_peak = (pi * k**2).log() + arb("2.5") * u0 + (a0 - 3).log() - p0
        if moment:
            log_peak += 2 * moment * u0.log()
        value = log_peak.exp() * scaled
        audit = {
            "moment": moment,
            "theta_index": theta_index,
            "saddle": str(u0),
            "left": str(left_a),
            "right": str(right_a),
            "central_scaled": str(central_real),
            "left_tail_scaled_bound": str(left_tail),
            "right_tail_scaled_bound": str(right_tail),
            "integral_ball": str(value),
        }
        return value, audit

    def log_gamma(self, moment: int) -> arb:
        """Enclose log(gamma(moment)) from the full positive theta sum."""
        if moment in self.log_gamma_cache:
            return self.log_gamma_cache[moment]
        last_index = 8 if moment <= 10 else 2
        total = arb(0)
        audits = []
        last_value = arb(0)
        for theta_index in range(1, last_index + 1):
            last_value, audit = self._term_integral(moment, theta_index)
            total += last_value
            audits.append(audit)
        ratio = theta_ratio_bound(last_index)
        theta_tail = last_value * ratio / (1 - ratio)
        total = add_symmetric_error(total, theta_tail)
        log_gamma = (
            arb(32).log()
            + arb(moment + 1).lgamma()
            - arb(2 * moment + 1).lgamma()
            + total.log()
        )
        self.log_gamma_cache[moment] = log_gamma
        self.integral_audit[str(moment)] = {
            "summands": audits,
            "theta_tail_bound": str(theta_tail),
            "theta_integral_ball": str(total),
            "log_gamma_ball": str(log_gamma),
        }
        return log_gamma


def rogue_polynomial(
    coefficients: ThetaCoefficientCertificate,
    shift: int,
    degree: int,
    gamma: mp.mpf,
) -> list[arb]:
    first = max(0, shift - 2)
    logs = {j: coefficients.log_gamma(j) for j in range(first, shift + degree + 1)}
    anchor = logs[first]
    base = {j: (logs[j] - anchor).exp() for j in logs}
    gamma_a = arb(mp.nstr(gamma, 30))
    delta = arb("0.25")
    a = gamma_a**2 + delta**2
    b = 2 * (gamma_a**2 - delta**2) / a**2
    c = 1 / a**2
    modified = []
    for j in range(shift, shift + degree + 1):
        value = base[j]
        if j >= 1:
            value += b * j * base[j - 1]
        if j >= 2:
            value += c * j * (j - 1) * base[j - 2]
        modified.append(value)
    ratio = modified[1] / modified[0]
    return [
        arb(math.comb(degree, j)) * modified[j] / modified[0] / ratio**j
        for j in range(degree + 1)
    ]


def discriminant(coefficients: list[arb]) -> arb:
    if len(coefficients) == 3:
        e, d, c = coefficients
        return d**2 - 4 * c * e
    if len(coefficients) == 4:
        d, c, b, a = coefficients
        return 18 * a * b * c * d - 4 * b**3 * d + b**2 * c**2 - 4 * a * c**3 - 27 * a**2 * d**2
    e, d, c, b, a = coefficients
    return (
        256 * a**3 * e**3
        - 192 * a**2 * b * d * e**2
        - 128 * a**2 * c**2 * e**2
        + 144 * a**2 * c * d**2 * e
        - 27 * a**2 * d**4
        + 144 * a * b**2 * c * e**2
        - 6 * a * b**2 * d**2 * e
        - 80 * a * b * c**2 * d * e
        + 18 * a * b * c * d**3
        + 16 * a * c**4 * e
        - 4 * a * c**3 * d**2
        - 27 * b**4 * e**2
        + 18 * b**3 * c * d * e
        - 4 * b**3 * d**3
        - 4 * b**2 * c**3 * e
        + b**2 * c**2 * d**2
    )


def arb_hermite_minors(coefficients: list[arb]) -> list[arb]:
    """Leading minors of the Hermite power-sum matrix over Arb balls."""
    degree = len(coefficients) - 1
    leading = coefficients[-1]
    monic = [coefficients[degree - j] / leading for j in range(1, degree + 1)]
    powers = [arb(degree)]
    for k in range(1, 2 * degree - 1):
        value = arb(0)
        for j in range(1, min(k, degree) + 1):
            if j == k:
                value += k * monic[j - 1]
            else:
                value += monic[j - 1] * powers[k - j]
        powers.append(-value)
    matrix = [[powers[i + j] for j in range(degree)] for i in range(degree)]
    return [arb_mat([row[:k] for row in matrix[:k]]).det() for k in range(1, degree + 1)]


def rational_midpoint(value: arb) -> sp.Rational:
    """Convert the exact binary Arb midpoint into a rational number."""
    midpoint = value.mid()
    mantissa, exponent = midpoint.man_exp()
    return sp.Rational(int(mantissa)) * sp.Rational(2) ** int(exponent)


def rational_certificate(coefficients: list[arb]) -> dict[str, Any]:
    x = sp.Symbol("X")
    rationals = [rational_midpoint(value) for value in coefficients]
    expression = sum(rationals[j] * x**j for j in range(len(rationals)))
    polynomial = sp.Poly(expression, x, domain=sp.QQ)
    sturm_count = int(sp.polys.polytools.count_roots(polynomial, inf=None, sup=None))

    degree = polynomial.degree()
    leading = rationals[-1]
    monic = [rationals[degree - j] / leading for j in range(1, degree + 1)]
    powers: list[sp.Rational] = [sp.Rational(degree)]
    for k in range(1, 2 * degree - 1):
        value = sp.Rational(0)
        for j in range(1, min(k, degree) + 1):
            if j == k:
                value += k * monic[j - 1]
            else:
                value += monic[j - 1] * powers[k - j]
        powers.append(-value)
    hermite = sp.Matrix(degree, degree, lambda i, j: powers[i + j])
    minors = [sp.factor(hermite[:k, :k].det()) for k in range(1, degree + 1)]
    pivots = [minors[0]] + [sp.factor(minors[k] / minors[k - 1]) for k in range(1, degree)]
    positive = sum(1 for pivot in pivots if pivot > 0)
    negative = sum(1 for pivot in pivots if pivot < 0)
    return {
        "sturm_real_root_count": sturm_count,
        "hermite_inertia": [positive, negative, degree - positive - negative],
        "hermite_leading_minor_signs": [int(sp.sign(minor)) for minor in minors],
        "coefficient_rational_numerators_sha256": hashlib.sha256(
            "\n".join(str(value) for value in rationals).encode()
        ).hexdigest(),
    }


def certify_one(
    engine: ThetaCoefficientCertificate,
    gamma: mp.mpf,
    shift: int,
    degree: int,
) -> dict[str, Any]:
    coefficients = rogue_polynomial(engine, shift, degree, gamma)
    disc = discriminant(coefficients)
    roots = arb_poly(coefficients).complex_roots()
    minors = arb_hermite_minors(coefficients)
    rational = rational_certificate(coefficients)
    all_minors_positive = all(minor.lower() > 0 for minor in minors)
    arb_real_root_boxes = all(root.imag.contains(0) for root in roots)
    classification = "hyperbolic" if all_minors_positive and rational["sturm_real_root_count"] == degree else "unresolved"
    return {
        "gamma": str(gamma),
        "shift": shift,
        "degree": degree,
        "classification": classification,
        "coefficient_balls_low_to_high": [str(value) for value in coefficients],
        "coefficient_outward_rational_intervals": [
            {"lower": str(value.lower()), "upper": str(value.upper())} for value in coefficients
        ],
        "discriminant_ball": str(disc),
        "discriminant_positive": bool(disc.lower() > 0),
        "arb_complex_root_balls": [str(root) for root in roots],
        "arb_all_root_boxes_meet_real_axis": arb_real_root_boxes,
        "arb_hermite_leading_minors": [str(minor) for minor in minors],
        "arb_hermite_positive_definite": all_minors_positive,
        "rational_midpoint_checks": rational,
    }


def selected_shifts(gamma: mp.mpf) -> list[int]:
    gamma_float = float(gamma)
    return sorted(
        {
            0,
            max(1, int(math.floor(gamma_float * math.log(max(gamma_float, 2.0))))),
            int(math.floor(gamma_float * gamma_float)),
            int(math.floor(256.0 * gamma_float * gamma_float)),
        }
    )


def run(output: Path, digits: int) -> None:
    ctx.dps = digits
    mp.mp.dps = digits + 40
    started = time.time()
    engine = ThetaCoefficientCertificate(digits)
    certificates = []
    for gamma_text in GAMMA_STRINGS:
        gamma = mp.mpf(gamma_text)
        for shift in selected_shifts(gamma):
            for degree in DEGREES:
                certificates.append(certify_one(engine, gamma, shift, degree))
    payload = {
        "status": "UNVERIFIED",
        "reason": "No degree-2, degree-3, or degree-4 nonhyperbolic polynomial was located; finite spot certificates do not certify every intervening shift.",
        "precision_decimal_digits": digits,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "python_flint": "0.8.0",
            "mpmath": mp.__version__,
            "sympy": sp.__version__,
        },
        "normalization": "8 xi(1/2+z) = 32 integral Phi(u) cosh(zu) du",
        "certificates": certificates,
        "integral_audit": engine.integral_audit,
        "elapsed_seconds": time.time() - started,
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--digits", type=int, default=100)
    parser.add_argument("--output", type=Path, default=Path("certificates.json"))
    args = parser.parse_args()
    run(args.output, args.digits)


if __name__ == "__main__":
    main()
