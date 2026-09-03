#!/usr/bin/env python3
"""Zero-free numerical screen for the Round-5 rogue Jensen experiment.

The Riemann xi coefficients are obtained from the theta-kernel integral

  8 xi(1/2+z) = 32 integral_0^infinity Phi(u) cosh(z u) du,

where Phi is evaluated directly.  No zeta zero or zero table is imported.
This file is a fast *screen*, not an interval proof.  The companion
``certify_jensen.py`` rebuilds selected polynomials with Arb balls and runs
the registered root/Sturm/Hermite checks.
"""

from __future__ import annotations

import argparse
import functools
import json
import math
import platform
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.optimize import brentq
from scipy.special import gammaln


DELTA = 0.25
GAMMAS = (14.13, 100.0, 1000.0)
DEGREES = (2, 3, 4)


def theta_phi(u: np.ndarray, terms: int = 24) -> np.ndarray:
    """Evaluate the standard positive theta kernel on the positive axis."""
    ans = np.zeros_like(u)
    for k in range(1, terms + 1):
        ans += (
            2.0 * np.pi**2 * k**4 * np.exp(4.5 * u)
            - 3.0 * np.pi * k**2 * np.exp(2.5 * u)
        ) * np.exp(-np.pi * k**2 * np.exp(2.0 * u))
    return ans


def low_log_coefficients(max_n: int = 96) -> list[float]:
    """Compute low xi coefficient logarithms by fixed theta quadrature."""
    nodes, weights = leggauss(2048)
    upper = 7.0
    u = (nodes + 1.0) * upper / 2.0
    weights = weights * upper / 2.0
    phi = theta_phi(u)
    logs: list[float] = []
    for n in range(max_n + 1):
        integral = float(np.sum(weights * phi * u ** (2 * n)))
        logs.append(
            math.log(32.0)
            + float(gammaln(n + 1))
            - float(gammaln(2 * n + 1))
            + math.log(integral)
        )
    return logs


@dataclass(frozen=True)
class LocalCoefficients:
    first: int
    ratios: tuple[float, ...]


class CoefficientScreen:
    """Fast local coefficient-ratio evaluator used only for screening."""

    def __init__(self, low_logs: list[float]) -> None:
        self.low_logs = low_logs
        self.nodes, self.weights = leggauss(96)

    @functools.lru_cache(maxsize=120_000)
    def local(self, n: int, degree: int) -> LocalCoefficients:
        first = max(0, n - 2)
        last = n + degree
        if last < len(self.low_logs):
            anchor = self.low_logs[first]
            return LocalCoefficients(
                first,
                tuple(math.exp(self.low_logs[j] - anchor) for j in range(first, last + 1)),
            )

        # At these shifts the k=1 theta summand dominates far beyond double
        # precision.  The Arb replay bounds all discarded theta summands.
        m = first
        pi = math.pi

        def log_integrand(u: float) -> float:
            a = 2.0 * pi * math.exp(2.0 * u)
            return (
                math.log(pi)
                + 2.5 * u
                + math.log(a - 3.0)
                - a / 2.0
                + 2.0 * m * math.log(u)
            )

        def derivative(u: float) -> float:
            a = 2.0 * pi * math.exp(2.0 * u)
            return 2.0 * m / u + 2.5 + 2.0 * a / (a - 3.0) - a

        hi = max(1.0, 0.5 * math.log(max(2.0, 2.0 * m / pi)))
        while derivative(hi) > 0.0:
            hi *= 1.3
        saddle = brentq(derivative, 1e-14, hi)
        peak = log_integrand(saddle)
        target = peak - 48.0
        lo0 = 1e-14
        left = (
            lo0
            if log_integrand(lo0) > target
            else brentq(lambda u: log_integrand(u) - target, lo0, saddle)
        )
        right = saddle * 1.1
        while log_integrand(right) > target:
            right = saddle + 1.5 * (right - saddle)
        right = brentq(lambda u: log_integrand(u) - target, saddle, right)

        u = (right - left) * self.nodes / 2.0 + (right + left) / 2.0
        base = (
            np.exp(np.array([log_integrand(float(x)) - peak for x in u]))
            * self.weights
            * (right - left)
            / 2.0
        )
        offsets = np.arange(last - first + 1)
        moments = np.sum(base[:, None] * u[:, None] ** (2 * offsets), axis=0)
        ratios = []
        for k in offsets:
            # k <= 6.  Direct short products avoid catastrophic cancellation
            # in differences of log-gamma values when m is in the millions.
            factorial_ratio = 1.0
            for j in range(1, int(k) + 1):
                factorial_ratio *= (m + j) / (2 * m + 2 * j - 1)
                factorial_ratio /= 2 * m + 2 * j
            ratios.append(factorial_ratio * float(moments[k] / moments[0]))
        return LocalCoefficients(first, tuple(ratios))


def rogue_coefficients(local: LocalCoefficients, n: int, degree: int, gamma: float) -> list[float]:
    """Return scaled gamma_Gamma(n),...,gamma_Gamma(n+d)."""
    a = gamma * gamma + DELTA * DELTA
    b = 2.0 * (gamma * gamma - DELTA * DELTA) / (a * a)
    c = 1.0 / (a * a)

    def coeff(index: int) -> float:
        return local.ratios[index - local.first]

    result = []
    for j in range(n, n + degree + 1):
        value = coeff(j)
        if j >= 1:
            value += b * j * coeff(j - 1)
        if j >= 2:
            value += c * j * (j - 1) * coeff(j - 2)
        result.append(value)
    return result


def scaled_polynomial(values: list[float], degree: int) -> list[np.longdouble]:
    """Scale X so that clustered Jensen coefficients stay near binomial size."""
    ratio = values[1] / values[0]
    return [
        np.longdouble(math.comb(degree, j))
        * np.longdouble(values[j] / values[0])
        / np.longdouble(ratio) ** j
        for j in range(degree + 1)
    ]


def discriminant(coefficients: list[np.longdouble]) -> np.longdouble:
    """Return the degree-2/3/4 discriminant (coefficients low first)."""
    if len(coefficients) == 3:
        e, d, c = coefficients
        return d * d - 4 * c * e
    if len(coefficients) == 4:
        d, c, b, a = coefficients
        return (
            18 * a * b * c * d
            - 4 * b**3 * d
            + b * b * c * c
            - 4 * a * c**3
            - 27 * a * a * d * d
        )
    if len(coefficients) == 5:
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
    raise ValueError("only degrees 2, 3, and 4 are registered")


def classify(screen: CoefficientScreen, n: int, gamma: float, degree: int) -> tuple[str, float]:
    # The degree-four request contains every coefficient needed by degrees two
    # and three, so all mutations share one cached theta evaluation per shift.
    local = screen.local(n, 4)
    values = rogue_coefficients(local, n, degree, gamma)
    disc = discriminant(scaled_polynomial(values, degree))
    # Discriminants of the Hermite-scaled limit decay rapidly and eventually
    # fall below binary64 cancellation.  Do not turn a roundoff sign into a
    # candidate: those points are explicitly indeterminate and routed to Arb.
    floors = {2: 1e-11, 3: 1e-13, 4: 1e-10}
    value = float(disc)
    if abs(value) <= floors[degree]:
        return "indeterminate", value
    return ("positive" if value > 0.0 else "negative"), value


def geometric_points(start: int, stop: int, count: int) -> list[int]:
    if stop <= start:
        return []
    raw = np.geomspace(start, stop, count)
    return sorted({int(round(x)) for x in raw if int(round(x)) >= start})


def run(output: Path, exhaustive_limit: int, log_points: int) -> None:
    started = time.time()
    low_logs = low_log_coefficients()
    screen = CoefficientScreen(low_logs)
    result: dict[str, object] = {
        "status": "UNVERIFIED",
        "method": {
            "low_coefficients": "2048-node Gauss-Legendre theta-kernel integral on [0,7]",
            "high_coefficients": "96-node saddle-local k=1 theta asymptotic screen",
            "certification": "see certify_jensen.py and certificates.json",
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
        "theta_normalization_check": {
            "computed_8xi_half": math.exp(low_logs[0]),
            "reference_decimal_not_from_zeros": 3.976966225506512,
            "absolute_difference": abs(math.exp(low_logs[0]) - 3.976966225506512),
        },
        "gamma_cases": {},
    }

    for gamma in GAMMAS:
        bound = int(math.floor(256.0 * gamma * gamma))
        full_stop = min(bound, exhaustive_limit)
        # Every integer is screened through full_stop.  Above it, use a dense
        # geometric stress grid; this is deliberately not called exhaustive.
        points = list(range(0, full_stop + 1))
        points.extend(geometric_points(full_stop + 1, bound, log_points))
        points = sorted(set(points))
        case: dict[str, object] = {
            "registered_bound": bound,
            "integer_exhaustive_through": full_stop,
            "points_above_exhaustive_limit": len([n for n in points if n > full_stop]),
            "degrees": {},
        }
        for degree in DEGREES:
            first_resolved_negative: int | None = None
            closest_n = 0
            closest_disc = math.inf
            near_zero: list[dict[str, float | int]] = []
            indeterminate_count = 0
            for n in points:
                screen_sign, disc = classify(screen, n, gamma, degree)
                if screen_sign == "negative" and first_resolved_negative is None:
                    first_resolved_negative = n
                if screen_sign == "indeterminate":
                    indeterminate_count += 1
                absolute = abs(disc)
                if absolute < closest_disc:
                    closest_n, closest_disc = n, absolute
                if absolute < 1e-12:
                    near_zero.append({"n": n, "discriminant": disc})
            case["degrees"][str(degree)] = {
                "screened_points": len(points),
                "first_resolved_negative_discriminant": first_resolved_negative,
                "indeterminate_due_to_binary64_cancellation": indeterminate_count,
                "smallest_abs_discriminant": closest_disc,
                "smallest_abs_discriminant_n": closest_n,
                "near_zero_count": len(near_zero),
                "near_zero_examples": near_zero[:10],
                "screen_conclusion": (
                    "resolved negative candidate found; requires Arb replay"
                    if first_resolved_negative is not None
                    else "no resolved nonhyperbolic candidate; Arb replay required in the indeterminate tail"
                ),
            }
        result["gamma_cases"][format(gamma, "g")] = case

    result["elapsed_seconds"] = time.time() - started
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("screen-results.json"))
    parser.add_argument(
        "--exhaustive-limit",
        type=int,
        default=100_000,
        help="screen every integer shift through this value",
    )
    parser.add_argument("--log-points", type=int, default=768)
    args = parser.parse_args()
    run(args.output, args.exhaustive_limit, args.log_points)


if __name__ == "__main__":
    main()
