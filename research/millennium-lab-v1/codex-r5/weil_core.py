#!/usr/bin/env python3
"""Zero-blind finite Weil-matrix construction for Codex Round 5.

This module implements equations (2.9), (4.2)--(4.4), (4.12)--(4.14),
and (5.25) of Connes--Consani--Moscovici, arXiv:2511.22755v1.  It has no
scoring code and no dependency on a table or evaluator of Riemann ordinates.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable, Sequence

import mpmath as mp
import numpy as np
from scipy.optimize import brentq


@dataclass(frozen=True)
class ArithmeticTerm:
    """One prime-power-like atom in the finite explicit-formula comb."""

    location: str
    weight: str
    base: str
    exponent: int
    weight_mode: str = "literal"

    def mp_location(self) -> mp.mpf:
        return mp.mpf(self.location)

    def mp_weight(self) -> mp.mpf:
        if self.weight_mode == "base_log_over_sqrt":
            return mp.log(mp.mpf(self.base)) / mp.sqrt(mp.mpf(self.location))
        return mp.mpf(self.weight)


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def prime_power_terms(x: int, omitted_base: int | None = None) -> list[ArithmeticTerm]:
    """Return Lambda(q)/sqrt(q) atoms for every q=p**a <= x."""

    terms: list[ArithmeticTerm] = []
    with mp.workdps(90):
        for p in range(2, x + 1):
            if not _is_prime(p) or p == omitted_base:
                continue
            q = p
            exponent = 1
            while q <= x:
                weight = mp.log(p) / mp.sqrt(q)
                terms.append(
                    ArithmeticTerm(
                        str(q),
                        mp.nstr(weight, 80),
                        str(p),
                        exponent,
                        "base_log_over_sqrt",
                    )
                )
                exponent += 1
                q *= p
    return sorted(terms, key=lambda term: mp.mpf(term.location))


def pseudo_prime_terms(seed: int, x: float = 13.0) -> tuple[list[ArithmeticTerm], int]:
    """Draw the preregistered six-base/nine-power pseudo-prime comb."""

    rng = np.random.Generator(np.random.PCG64DXSM(seed))
    log2 = math.log(2.0)
    attempts = 0
    while True:
        attempts += 1
        bases: list[float] = []
        while len(bases) < 6:
            candidate = float(rng.uniform(2.0, x))
            if rng.random() <= log2 / math.log(candidate):
                bases.append(candidate)
        bases.sort()
        powers: list[tuple[float, float, int]] = []
        for base in bases:
            exponent = 1
            value = base
            while value <= x * (1.0 + 8.0 * np.finfo(float).eps):
                powers.append((value, base, exponent))
                exponent += 1
                value *= base
        if len(powers) == 9:
            break
        if attempts > 1_000_000:
            raise RuntimeError("pseudo-prime rejection sampler did not terminate")

    terms = [
        ArithmeticTerm(
            format(value, ".17g"),
            format(math.log(base) / math.sqrt(value), ".17g"),
            format(base, ".17g"),
            exponent,
            "base_log_over_sqrt",
        )
        for value, base, exponent in sorted(powers)
    ]
    return terms, attempts


def permuted_weight_terms(x: int = 13, seed: int = 52025999) -> list[ArithmeticTerm]:
    """Keep true support locations while permuting the weight multiset."""

    terms = prime_power_terms(x)
    rng = np.random.Generator(np.random.PCG64DXSM(seed))
    weights = [term.weight for term in terms]
    rng.shuffle(weights)
    return [
        ArithmeticTerm(term.location, weight, term.base, term.exponent, "literal")
        for term, weight in zip(terms, weights)
    ]


def q_entry(n: int, m: int, y: mp.mpf, length: mp.mpf) -> mp.mpf:
    """Equation (2.9)/(2.10), including the diagonal limit."""

    if n == m:
        return 2 * (1 - y / length) * mp.cos(2 * mp.pi * n * y / length)
    numerator = mp.sin(2 * mp.pi * m * y / length) - mp.sin(
        2 * mp.pi * n * y / length
    )
    return numerator / (mp.pi * (n - m))


def pole_entry(n: int, m: int, length: mp.mpf) -> mp.mpf:
    """Equation (4.2)."""

    pi2 = mp.pi**2
    numerator = 32 * length * mp.sinh(length / 4) ** 2
    numerator *= length**2 - 16 * pi2 * m * n
    denominator = (length**2 + 16 * pi2 * m * m) * (
        length**2 + 16 * pi2 * n * n
    )
    return numerator / denominator


def archimedean_arrays(
    n_max: int, length: mp.mpf, dps: int
) -> tuple[list[mp.mpf], list[mp.mpf], list[mp.mpf]]:
    """Evaluate alpha, beta, gamma via Proposition 4.2."""

    with mp.workdps(dps):
        length = mp.mpf(length)
        z = mp.exp(-2 * length)
        decay = mp.exp(-length / 2)

        def hyper_unit(a: mp.mpc) -> mp.mpc:
            # 2F1(1,a;a+1;z) = sum_{k>=0} a*z**k/(a+k).
            total = mp.mpc(0)
            power = mp.mpf(1)
            k = 0
            while True:
                term = a * power / (a + k)
                total += term
                power *= z
                k += 1
                if abs(term) * z / (1 - z) <= mp.eps * max(1, abs(total)):
                    return total

        def lerch_two(a: mp.mpc) -> mp.mpc:
            # Phi(z,2,a) converges geometrically because z=e**(-2L)<=1/25.
            total = mp.mpc(0)
            power = mp.mpf(1)
            k = 0
            while True:
                term = power / (a + k) ** 2
                total += term
                power *= z
                k += 1
                if abs(term) * z / (1 - z) <= mp.eps * max(1, abs(total)):
                    return total

        f0 = mp.re(hyper_unit(mp.mpf(1) / 4))
        c_plus_w = (
            mp.log((mp.exp(length / 2) - 1) / (mp.exp(length / 2) + 1)) / 2
            + mp.atan(mp.exp(length / 2))
            - mp.pi / 4
            + mp.euler / 2
            + mp.log(8 * mp.pi) / 2
        )
        alpha: list[mp.mpf] = []
        beta: list[mp.mpf] = []
        gamma: list[mp.mpf] = []
        for n in range(n_max + 1):
            nn = mp.mpf(n)
            a = mp.mpf(1) / 4 + mp.j * mp.pi * nn / length
            hyp = hyper_unit(a)
            sin_integral = decay * mp.im(2 * length * hyp / (length + 4 * mp.pi * mp.j * nn))
            sin_integral += mp.im(mp.digamma(a)) / 2

            xcos_integral = -length * decay * mp.im(
                2 * length * hyp / (4 * mp.pi * nn - mp.j * length)
            )
            xcos_integral -= decay * mp.re(lerch_two(a)) / 4
            xcos_integral += mp.re(mp.polygamma(1, a)) / 4

            cos_minus_one = -decay * mp.re(
                2 * length * hyp / (length + 4 * mp.pi * mp.j * nn)
            )
            cos_minus_one += 2 * decay * f0
            cos_minus_one -= mp.re(mp.digamma(a) - mp.digamma(mp.mpf(1) / 4)) / 2

            alpha.append(+sin_integral / mp.pi)
            beta.append(+xcos_integral / length)
            gamma.append(+cos_minus_one + c_plus_w)
        return alpha, beta, gamma


def archimedean_entry_from_arrays(
    n: int,
    m: int,
    alpha: Sequence[mp.mpf],
    beta: Sequence[mp.mpf],
    gamma: Sequence[mp.mpf],
) -> mp.mpf:
    """Equation (4.3), with parity extension of alpha/beta/gamma."""

    if n == m:
        return 2 * gamma[abs(n)] - 2 * beta[abs(n)]
    alpha_n = alpha[abs(n)] if n >= 0 else -alpha[abs(n)]
    alpha_m = alpha[abs(m)] if m >= 0 else -alpha[abs(m)]
    return (alpha_m - alpha_n) / (n - m)


def direct_archimedean_entry(n: int, m: int, length: mp.mpf, dps: int) -> mp.mpf:
    """Independent direct quadrature of Eq. (4.4)."""

    with mp.workdps(dps):
        length = mp.mpf(length)
        omega0 = mp.mpf(2) if n == m else mp.mpf(0)

        def integrand(y: mp.mpf) -> mp.mpf:
            if y == 0:
                return mp.mpf(1) / 2 - 1 / length if n == m else -1 / length
            omega = q_entry(n, m, y, length)
            return (mp.exp(y / 2) * omega - omega0) / (mp.exp(y) - mp.exp(-y))

        constant = omega0 / 2 * (
            mp.euler
            + mp.log(4 * mp.pi * (mp.exp(length) - 1) / (mp.exp(length) + 1))
        )
        integral = mp.quad(
            integrand, [0, length / 8, length / 3, 2 * length / 3, length]
        )
        return constant + integral


def arithmetic_entry(
    n: int, m: int, length: mp.mpf, terms: Iterable[ArithmeticTerm]
) -> mp.mpf:
    """Equation (4.3) for an explicitly supplied finite comb."""

    total = mp.mpf(0)
    for term in terms:
        total += term.mp_weight() * q_entry(n, m, mp.log(term.mp_location()), length)
    return total


def weil_entry(
    n: int,
    m: int,
    length: mp.mpf,
    terms: Sequence[ArithmeticTerm],
    alpha: Sequence[mp.mpf],
    beta: Sequence[mp.mpf],
    gamma: Sequence[mp.mpf],
) -> mp.mpf:
    """One matrix entry with the explicit-formula sign convention."""

    return (
        pole_entry(n, m, length)
        - archimedean_entry_from_arrays(n, m, alpha, beta, gamma)
        - arithmetic_entry(n, m, length, terms)
    )


def parity_blocks(
    n_max: int,
    x: str | float | int,
    terms: Sequence[ArithmeticTerm],
    dps: int,
) -> tuple[mp.matrix, mp.matrix, dict[str, str]]:
    """Build orthonormal even and odd blocks without forming the full matrix."""

    with mp.workdps(dps):
        length = mp.log(mp.mpf(str(x)))
        alpha, beta, gamma = archimedean_arrays(n_max, length, dps)
        even, odd = parity_blocks_from_arrays(
            n_max, length, terms, alpha, beta, gamma, dps
        )
        meta = {
            "x": str(x),
            "length": mp.nstr(length, dps),
            "n_max": str(n_max),
            "dps": str(dps),
            "term_count": str(len(terms)),
        }
        return even, odd, meta


def parity_blocks_from_arrays(
    n_max: int,
    length: mp.mpf,
    terms: Sequence[ArithmeticTerm],
    alpha: Sequence[mp.mpf],
    beta: Sequence[mp.mpf],
    gamma: Sequence[mp.mpf],
    dps: int,
) -> tuple[mp.matrix, mp.matrix]:
    """Build parity blocks while reusing a frozen archimedean evaluation."""

    with mp.workdps(dps):
        even = mp.matrix(n_max + 1)
        odd = mp.matrix(n_max)
        sqrt2 = mp.sqrt(2)
        prepared_terms = [
            (mp.log(term.mp_location()), term.mp_weight()) for term in terms
        ]
        off_diagonal_numerators: dict[int, mp.mpf] = {}
        diagonal_arithmetic: dict[int, mp.mpf] = {}
        for n in range(-n_max, n_max + 1):
            alpha_n = alpha[abs(n)] if n >= 0 else -alpha[abs(n)]
            sine_sum = mp.fsum(
                weight * mp.sin(2 * mp.pi * n * y / length) / mp.pi
                for y, weight in prepared_terms
            )
            off_diagonal_numerators[n] = alpha_n + sine_sum
            diagonal_arithmetic[n] = mp.fsum(
                weight
                * 2
                * (1 - y / length)
                * mp.cos(2 * mp.pi * n * y / length)
                for y, weight in prepared_terms
            )

        def entry(n: int, m: int) -> mp.mpf:
            if n == m:
                return (
                    pole_entry(n, n, length)
                    - (2 * gamma[abs(n)] - 2 * beta[abs(n)])
                    - diagonal_arithmetic[n]
                )
            numerator = off_diagonal_numerators[n] - off_diagonal_numerators[m]
            return pole_entry(n, m, length) + numerator / (n - m)

        even[0, 0] = entry(0, 0)
        for n in range(1, n_max + 1):
            value = sqrt2 * entry(0, n)
            even[0, n] = value
            even[n, 0] = value
        for n in range(1, n_max + 1):
            for m in range(n, n_max + 1):
                even_value = entry(n, m) + entry(n, -m)
                odd_value = entry(n, m) - entry(n, -m)
                even[n, m] = even_value
                even[m, n] = even_value
                odd[n - 1, m - 1] = odd_value
                odd[m - 1, n - 1] = odd_value
        return even, odd


def float_ground(even: mp.matrix) -> tuple[float, np.ndarray, np.ndarray]:
    """Binary64 eigensolve used only as a blind root-enumeration seed."""

    array = np.array(even.tolist(), dtype=float)
    values, vectors = np.linalg.eigh(array)
    vector = vectors[:, 0]
    if np.sum(vector) < 0:
        vector = -vector
    return float(values[0]), vector, values


def full_coefficients_from_even(even_vector: Sequence[float]) -> np.ndarray:
    """Expand an orthonormal parity-basis vector into indices -N,...,N."""

    n_max = len(even_vector) - 1
    full = np.zeros(2 * n_max + 1, dtype=float)
    full[n_max] = float(even_vector[0])
    for n in range(1, n_max + 1):
        value = float(even_vector[n]) / math.sqrt(2.0)
        full[n_max - n] = value
        full[n_max + n] = value
    return full


def full_coefficients_from_even_mp(even_vector: mp.matrix) -> mp.matrix:
    """Arbitrary-precision parity expansion in index order -N,...,N."""

    n_max = even_vector.rows - 1
    full = mp.matrix(2 * n_max + 1, 1)
    full[n_max] = even_vector[0]
    for n in range(1, n_max + 1):
        value = even_vector[n] / mp.sqrt(2)
        full[n_max - n] = value
        full[n_max + n] = value
    return full


def normalize_vector(vector: mp.matrix) -> mp.matrix:
    """Return a unit vector with a deterministic sign."""

    norm = mp.sqrt(mp.fsum(abs(vector[j]) ** 2 for j in range(vector.rows)))
    result = vector / norm
    if mp.fsum(result[j] for j in range(result.rows)) < 0:
        result = -result
    return result


def refine_ground(
    matrix: mp.matrix, initial: mp.matrix, iterations: int = 5
) -> tuple[mp.mpf, mp.matrix, mp.mpf]:
    """Rayleigh-quotient iteration from a lower-precision ground vector."""

    vector = normalize_vector(initial)
    identity = mp.eye(matrix.rows)
    rayleigh = (vector.T * matrix * vector)[0]
    for _ in range(iterations):
        shifted = matrix - rayleigh * identity
        try:
            updated = mp.lu_solve(shifted, vector)
        except ZeroDivisionError:
            shifted = matrix - (rayleigh + 16 * mp.eps) * identity
            updated = mp.lu_solve(shifted, vector)
        vector = normalize_vector(updated)
        rayleigh = (vector.T * matrix * vector)[0]
    residual = mp.sqrt(
        mp.fsum(
            abs(value) ** 2
            for value in (matrix * vector - rayleigh * vector)
        )
    )
    return rayleigh, vector, residual


def transform_mp(z: mp.mpf | mp.mpc, full: mp.matrix, length: mp.mpf) -> mp.mpc:
    """Arbitrary-precision centered sinc evaluation of Eq. (5.25)."""

    n_max = (full.rows - 1) // 2
    total = mp.mpc(0)
    for offset, n in enumerate(range(-n_max, n_max + 1)):
        lattice = 2 * mp.pi * n / length
        argument = (lattice - z) * length / (2 * mp.pi)
        total += full[offset] * ((-1) ** n) * mp.sincpi(argument)
    return mp.sqrt(length) * total


def secular_mp(z: mp.mpf, full: mp.matrix, length: mp.mpf) -> mp.mpf:
    """Real secular factor in Eq. (5.25), away from Fourier-lattice poles."""

    n_max = (full.rows - 1) // 2
    total = full[n_max] / z
    for n in range(1, n_max + 1):
        lattice = 2 * mp.pi * n / length
        coefficient = full[n_max + n]
        total += 2 * z * coefficient / (z * z - lattice * lattice)
    return mp.re(total)


def enumerate_positive_roots_mp(
    full: mp.matrix,
    length: mp.mpf,
    count: int = 60,
    subdivisions: int = 24,
) -> list[mp.mpf]:
    """Enumerate secular roots interval-by-interval without external seeds."""

    n_max = (full.rows - 1) // 2
    lattice_step = 2 * mp.pi / length
    roots: list[mp.mpf] = []
    tolerance = mp.power(10, -max(30, mp.mp.dps - 12))
    for interval in range(n_max):
        left_pole = interval * lattice_step
        right_pole = (interval + 1) * lattice_step
        endpoint_offset = (right_pole - left_pole) * mp.power(
            10, -min(30, max(12, mp.mp.dps // 3))
        )
        points = [left_pole + endpoint_offset]
        points.extend(
            left_pole + (right_pole - left_pole) * k / subdivisions
            for k in range(1, subdivisions)
        )
        points.append(right_pole - endpoint_offset)
        values = [secular_mp(point, full, length) for point in points]
        for left, right, f_left, f_right in zip(
            points[:-1], points[1:], values[:-1], values[1:]
        ):
            if f_left == 0:
                root = left
            elif f_right == 0:
                root = right
            elif f_left * f_right > 0:
                continue
            else:
                lo, hi = left, right
                flo = f_left
                for _ in range(16):
                    mid = (lo + hi) / 2
                    fmid = secular_mp(mid, full, length)
                    if flo * fmid <= 0:
                        hi = mid
                    else:
                        lo, flo = mid, fmid
                try:
                    root = mp.findroot(
                        lambda value: secular_mp(value, full, length),
                        (lo, hi),
                        tol=tolerance,
                        maxsteps=max(80, mp.mp.dps),
                        verify=False,
                    )
                    if not (lo < root < hi) or abs(secular_mp(root, full, length)) > mp.sqrt(
                        tolerance
                    ):
                        raise ValueError("secant refinement escaped its certified bracket")
                except (ValueError, ZeroDivisionError):
                    for _ in range(4 * mp.mp.dps + 80):
                        mid = (lo + hi) / 2
                        fmid = secular_mp(mid, full, length)
                        if fmid == 0 or hi - lo <= tolerance:
                            lo = hi = mid
                            break
                        if flo * fmid <= 0:
                            hi = mid
                        else:
                            lo, flo = mid, fmid
                    root = (lo + hi) / 2
            if root > 0 and (not roots or abs(root - roots[-1]) > tolerance * 100):
                roots.append(root)
                if len(roots) >= count:
                    return roots
    raise RuntimeError(f"found only {len(roots)} positive roots before the intrinsic cutoff")


def refine_positive_roots(
    full: mp.matrix,
    length: mp.mpf,
    approximations: Sequence[float],
    dps: int,
) -> list[mp.mpf]:
    """Refine zero-blind float roots using only their construction-derived seeds."""

    roots: list[mp.mpf] = []
    tolerance = mp.power(10, -max(30, dps - 15))
    for approximation in approximations:
        center = mp.mpf(str(approximation))
        half_width = mp.mpf("1e-5") * max(1, abs(center))
        root = mp.findroot(
            lambda value: transform_mp(value, full, length),
            (center - half_width, center + half_width),
            tol=tolerance,
            maxsteps=100,
            verify=False,
        )
        root = mp.re(root)
        if root <= 0:
            raise RuntimeError("refinement left the positive axis")
        if roots and root <= roots[-1]:
            raise RuntimeError("refined roots are not strictly ordered")
        roots.append(root)
    return roots


def transform_float(z: float, full: np.ndarray, length: float) -> float:
    """Stable centered sinc evaluation of Eq. (5.25)."""

    n_max = (len(full) - 1) // 2
    indices = np.arange(-n_max, n_max + 1, dtype=float)
    lattice = 2.0 * np.pi * indices / length
    phases = np.where((indices.astype(int) % 2) == 0, 1.0, -1.0)
    arguments = (lattice - z) * length / (2.0 * np.pi)
    return float(math.sqrt(length) * np.dot(full * phases, np.sinc(arguments)))


def enumerate_positive_roots(
    full: np.ndarray, length: float, count: int = 60
) -> list[float]:
    """Enumerate roots on a grid determined solely by N and the Fourier lattice."""

    n_max = (len(full) - 1) // 2
    lattice_step = 2.0 * np.pi / length
    maximum = lattice_step * n_max
    step = lattice_step / 128.0
    grid = np.arange(step / 7.0, maximum + step, step)
    values = np.array([transform_float(float(z), full, length) for z in grid])
    roots: list[float] = []
    for left, right, f_left, f_right in zip(grid[:-1], grid[1:], values[:-1], values[1:]):
        if not (np.isfinite(f_left) and np.isfinite(f_right)):
            continue
        if f_left == 0.0:
            candidate = float(left)
        elif f_left * f_right < 0:
            candidate = brentq(
                lambda value: transform_float(value, full, length),
                float(left),
                float(right),
                xtol=1e-13,
                rtol=8 * np.finfo(float).eps,
                maxiter=100,
            )
        else:
            continue
        if candidate > 1e-8 and (not roots or abs(candidate - roots[-1]) > step / 20):
            roots.append(candidate)
            if len(roots) >= count:
                return roots
    raise RuntimeError(f"found only {len(roots)} positive roots before the intrinsic cutoff")


def matrix_digest(matrix: mp.matrix, digits: int = 80) -> str:
    """Hash a canonical decimal serialization of a matrix."""

    payload = "\n".join(
        mp.nstr(matrix[i, j], digits)
        for i in range(matrix.rows)
        for j in range(matrix.cols)
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def write_json(path: Path, payload: object) -> None:
    """Write deterministic JSON used by the experiment scripts."""

    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
