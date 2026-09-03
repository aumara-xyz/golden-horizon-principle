"""Zero-data prolate candidate for the Round-5 Weil bridge.

The module implements the convention frozen in PREDICTIONS-codex-r5.md:

* solve the regular even angular prolate problem on [-lambda, lambda];
* L2-normalize h_0 and h_4 and make their values at zero positive;
* form the L2-normalized combination with exactly zero integral;
* extend that combination by zero and apply E(h)(u) = sqrt(u) sum h(m u);
* project E(h) onto the multiplicative Fourier basis V_n, -N <= n <= N.

No reference spectrum is imported or stored here.  The implementation is also
independent of any Round-5 implementation outside the codex-r5 directory.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import ceil, exp, floor, log, pi, sqrt
from typing import Iterable, Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.linalg import eigh, eigh_tridiagonal
from scipy.special import eval_legendre, roots_legendre


FloatArray = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]


def _legendre_raise(l: int) -> float:
    """Coefficient of p_{l+1} in z p_l for orthonormal Legendre p_l."""

    return (l + 1.0) / sqrt((2.0 * l + 1.0) * (2.0 * l + 3.0))


def _even_prolate_tridiagonal(x: float, lmax: int) -> tuple[FloatArray, FloatArray, NDArray[np.int64]]:
    """Even-sector matrix of -d((1-z^2)d/dz) + (2*pi*x)^2 z^2.

    The basis is p_0, p_2, ..., where p_l is the L2[-1,1]-normalized
    Legendre polynomial.  Multiplication by z^2 is tridiagonal in parity.
    """

    if x <= 1.0:
        raise ValueError("x=lambda^2 must exceed 1")
    if lmax < 8:
        raise ValueError("lmax must be at least 8")
    if lmax % 2:
        lmax -= 1
    degrees = np.arange(0, lmax + 1, 2, dtype=np.int64)
    c2 = (2.0 * pi * x) ** 2
    diagonal = np.empty(degrees.size, dtype=np.float64)
    off_diagonal = np.empty(degrees.size - 1, dtype=np.float64)
    for j, l0 in enumerate(degrees):
        l = int(l0)
        down = _legendre_raise(l - 1) if l else 0.0
        up = _legendre_raise(l)
        diagonal[j] = l * (l + 1.0) + c2 * (down * down + up * up)
        if j + 1 < degrees.size:
            off_diagonal[j] = c2 * up * _legendre_raise(l + 1)
    return diagonal, off_diagonal, degrees


def _normalized_legendre_values(degrees: NDArray[np.int64], z: ArrayLike) -> FloatArray:
    z_array = np.asarray(z, dtype=np.float64)
    flat = z_array.reshape(-1)
    values = np.empty((degrees.size, flat.size), dtype=np.float64)
    for j, l0 in enumerate(degrees):
        l = int(l0)
        values[j] = sqrt((2.0 * l + 1.0) / 2.0) * eval_legendre(l, flat)
    return values.reshape((degrees.size,) + z_array.shape)


def _evaluate_legendre_series(
    degrees: NDArray[np.int64], coefficients: FloatArray, z: ArrayLike
) -> FloatArray:
    """Stable Clenshaw evaluation of a normalized-Legendre expansion."""

    standard = np.zeros(int(degrees[-1]) + 1, dtype=np.float64)
    standard[degrees] = coefficients * np.sqrt((2.0 * degrees + 1.0) / 2.0)
    return np.asarray(np.polynomial.legendre.legval(np.asarray(z), standard), dtype=np.float64)


@dataclass(frozen=True)
class ProlateMode:
    """One regular, even, L2[-lambda,lambda]-normalized prolate mode."""

    x: float
    label: int
    eigenvalue: float
    degrees: NDArray[np.int64]
    coefficients: FloatArray
    truncation_residual: float

    @property
    def lambda_(self) -> float:
        return sqrt(self.x)

    @property
    def c(self) -> float:
        return 2.0 * pi * self.x

    @property
    def integral(self) -> float:
        # Only normalized p_0 has a nonzero integral on [-1,1].  The
        # lambda^{-1/2} coordinate scaling contributes sqrt(lambda).
        return sqrt(self.lambda_) * sqrt(2.0) * float(self.coefficients[0])

    def values(self, y: ArrayLike, *, zero_extension: bool = True) -> FloatArray:
        """Evaluate h_{label,lambda}(y), optionally with the frozen zero extension."""

        y_array = np.asarray(y, dtype=np.float64)
        z = y_array / self.lambda_
        output = np.zeros_like(z, dtype=np.float64)
        mask = np.abs(z) <= 1.0 if zero_extension else np.ones_like(z, dtype=bool)
        if np.any(mask):
            output[mask] = _evaluate_legendre_series(
                self.degrees, self.coefficients, z[mask]
            ) / sqrt(self.lambda_)
        return output


@dataclass(frozen=True)
class ProlateCandidate:
    """The normalized zero-integral h_lambda built from prolate labels 0 and 4."""

    x: float
    h0: ProlateMode
    h4: ProlateMode
    coefficients: FloatArray
    h0_weight: float
    h4_weight: float

    @property
    def lambda_(self) -> float:
        return sqrt(self.x)

    @property
    def degrees(self) -> NDArray[np.int64]:
        return self.h0.degrees

    @property
    def integral(self) -> float:
        return sqrt(self.lambda_) * sqrt(2.0) * float(self.coefficients[0])

    def values(self, y: ArrayLike) -> FloatArray:
        y_array = np.asarray(y, dtype=np.float64)
        z = y_array / self.lambda_
        output = np.zeros_like(z, dtype=np.float64)
        mask = np.abs(z) <= 1.0
        if np.any(mask):
            output[mask] = _evaluate_legendre_series(
                self.degrees, self.coefficients, z[mask]
            ) / sqrt(self.lambda_)
        return output


@lru_cache(maxsize=128)
def prolate_mode(x: float, label: int, *, lmax: int = 320) -> ProlateMode:
    """Return h_{label,lambda}; labels 0 and 4 select even eigenmodes 1 and 3."""

    if label not in (0, 4):
        raise ValueError("this experiment registers only labels 0 and 4")
    diagonal, off_diagonal, degrees = _even_prolate_tridiagonal(x, lmax)
    ordinal = label // 2
    eigenvalues, eigenvectors = eigh_tridiagonal(
        diagonal,
        off_diagonal,
        select="i",
        select_range=(0, ordinal),
        check_finite=True,
        lapack_driver="stebz",
    )
    vector = np.asarray(eigenvectors[:, ordinal], dtype=np.float64)
    values_at_zero = _normalized_legendre_values(degrees, np.array([0.0]))[:, 0]
    if float(vector @ values_at_zero) < 0.0:
        vector = -vector

    # Residual in the next omitted normalized Legendre mode.  The in-block
    # residual is at floating-point roundoff after the tridiagonal solve.
    last_l = int(degrees[-1])
    next_coupling = (2.0 * pi * x) ** 2 * _legendre_raise(last_l) * _legendre_raise(last_l + 1)
    truncation_residual = abs(next_coupling * float(vector[-1]))
    return ProlateMode(
        x=float(x),
        label=label,
        eigenvalue=float(eigenvalues[ordinal]),
        degrees=degrees,
        coefficients=vector,
        truncation_residual=truncation_residual,
    )


@lru_cache(maxsize=64)
def prolate_candidate(x: float, *, lmax: int = 320) -> ProlateCandidate:
    """Form the unique normalized h0/h4 combination with zero integral."""

    h0 = prolate_mode(x, 0, lmax=lmax)
    h4 = prolate_mode(x, 4, lmax=lmax)
    i0, i4 = h0.integral, h4.integral
    # i0*h4 - i4*h0 has zero integral and tends to the sign convention in
    # Eq. (7.4): positive h4 coefficient and negative h0 coefficient.
    raw = i0 * h4.coefficients - i4 * h0.coefficients
    raw_norm = float(np.linalg.norm(raw))
    coefficients = raw / raw_norm
    return ProlateCandidate(
        x=float(x),
        h0=h0,
        h4=h4,
        coefficients=coefficients,
        h0_weight=-i4 / raw_norm,
        h4_weight=i0 / raw_norm,
    )


def hermite_modes(y: ArrayLike) -> tuple[FloatArray, FloatArray]:
    """L2-normalized limiting Hermite modes h0 and h4 in the paper's convention."""

    y_array = np.asarray(y, dtype=np.float64)
    gaussian = np.exp(-pi * y_array * y_array)
    h0 = 2.0 ** 0.25 * gaussian
    h4 = (2.0 ** 0.25 / sqrt(24.0)) * (
        16.0 * pi * pi * y_array**4 - 24.0 * pi * y_array**2 + 3.0
    ) * gaussian
    return h0, h4


def hermite_candidate_values(y: ArrayLike) -> FloatArray:
    """L2-normalized undeformed zero-integral h0/h4 combination."""

    h0, h4 = hermite_modes(y)
    i0 = 2.0**0.25
    i4 = 3.0 * 2.0**0.25 / sqrt(24.0)
    return (i0 * h4 - i4 * h0) / sqrt(i0 * i0 + i4 * i4)


def e_map_values(
    candidate: ProlateCandidate,
    u: ArrayLike,
) -> FloatArray:
    """Evaluate E(h_lambda)(u) using the exact finite sum from zero extension."""

    u_array = np.asarray(u, dtype=np.float64)
    flat = u_array.reshape(-1)
    if np.any(flat <= 0.0):
        raise ValueError("u must be positive")
    output = np.zeros_like(flat)
    lam = candidate.lambda_
    maximum_count = int(floor(lam / float(np.min(flat)) + 8.0 * np.finfo(float).eps))
    for m in range(1, maximum_count + 1):
        output += candidate.values(m * flat)
    output *= np.sqrt(flat)
    return output.reshape(u_array.shape)


def hermite_e_map_values(u: ArrayLike, *, tail_tolerance: float = 1e-15) -> FloatArray:
    """Undeformed-Hermite control E(h), summed until a Gaussian tail bound is tiny."""

    u_array = np.asarray(u, dtype=np.float64)
    flat = u_array.reshape(-1)
    if np.any(flat <= 0.0):
        raise ValueError("u must be positive")
    output = np.zeros_like(flat)
    # The polynomial-Gaussian tail is safely negligible after exp(-pi y^2)
    # falls several orders below the requested tolerance.  The +4 margin
    # controls the quartic polynomial multiplying the Gaussian.
    cutoff_y = sqrt(max(1.0, -log(tail_tolerance) / pi)) + 4.0
    maximum_count = max(1, int(ceil(cutoff_y / float(np.min(flat)))))
    for m in range(1, maximum_count + 1):
        output += hermite_candidate_values(m * flat)
    output *= np.sqrt(flat)
    return output.reshape(u_array.shape)


def _multiplicative_breakpoints(x: float) -> FloatArray:
    """All E-sum change points in t=log(u), including interval endpoints."""

    lam = sqrt(x)
    a = log(lam)
    points = [-a, a]
    for m in range(1, int(floor(x)) + 1):
        t = log(lam / m)
        if -a < t < a:
            points.append(t)
    ordered = sorted(points)
    collapsed = [ordered[0]]
    tolerance = 64.0 * np.finfo(float).eps * max(1.0, abs(a))
    for point in ordered[1:]:
        if point - collapsed[-1] > tolerance:
            collapsed.append(point)
    # Preserve the exact registered endpoints after collapsing roundoff-level
    # duplicates such as log(lambda/floor(x)) == -log(lambda) for integer x.
    collapsed[0], collapsed[-1] = -a, a
    return np.asarray(collapsed, dtype=np.float64)


@dataclass(frozen=True)
class FourierProjection:
    x: float
    n_max: int
    indices: NDArray[np.int64]
    raw_coefficients: ComplexArray
    coefficients: ComplexArray
    raw_norm: float
    quadrature_order: int
    panels_per_nyquist_cycle: int | None
    mode_lmax: int | None
    source: str

    @property
    def inversion_defect(self) -> float:
        # In the paper's V_n convention inversion-even functions have real
        # coefficients.  The zero-extended prolate construction is expected
        # to have only a numerical-sized defect in this range.
        return float(np.max(np.abs(self.coefficients.imag)))


def project_e_map(
    x: float,
    n_max: int,
    *,
    quadrature_order: int = 160,
    panels_per_nyquist_cycle: int | None = None,
    mode_lmax: int = 320,
    source: str = "prolate",
    hermite_tail_tolerance: float = 1e-15,
) -> FourierProjection:
    """Project a registered E-map candidate onto V_{-N},...,V_N.

    Gauss-Legendre quadrature is performed separately between all finite-sum
    change points.  The returned coefficient vector is Euclidean-normalized,
    as frozen for the bridge residual.
    """

    if n_max < 0:
        raise ValueError("n_max must be nonnegative")
    if quadrature_order < 12:
        raise ValueError("quadrature_order must be at least 12")
    if panels_per_nyquist_cycle is not None and panels_per_nyquist_cycle < 1:
        raise ValueError("panels_per_nyquist_cycle must be positive")
    if source not in ("prolate", "hermite"):
        raise ValueError("source must be 'prolate' or 'hermite'")
    candidate = prolate_candidate(x, lmax=mode_lmax) if source == "prolate" else None
    nodes, weights = roots_legendre(quadrature_order)
    breakpoints = _multiplicative_breakpoints(x)
    indices = np.arange(-n_max, n_max + 1, dtype=np.int64)
    L = log(x)
    a = L / 2.0
    coefficients = np.zeros(indices.size, dtype=np.complex128)
    for original_left, original_right in zip(breakpoints[:-1], breakpoints[1:]):
        if panels_per_nyquist_cycle is None or n_max == 0:
            panel_edges = np.asarray([original_left, original_right])
        else:
            maximum_width = L / (panels_per_nyquist_cycle * n_max)
            panel_count = max(1, int(ceil((original_right - original_left) / maximum_width)))
            panel_edges = np.linspace(original_left, original_right, panel_count + 1)
        left = panel_edges[:-1, None]
        right = panel_edges[1:, None]
        t = ((right - left) * nodes[None, :] / 2.0 + (right + left) / 2.0).reshape(-1)
        quadrature_weights = ((right - left) * weights[None, :] / 2.0).reshape(-1)
        u = np.exp(t)
        if source == "prolate":
            assert candidate is not None
            k_values = e_map_values(candidate, u)
        else:
            k_values = hermite_e_map_values(u, tail_tolerance=hermite_tail_tolerance)
        weighted = quadrature_weights * k_values
        # Chunk the phase matrix to keep the factor-eight convergence run well
        # below 100 MiB while retaining vectorized candidate evaluation.
        for start in range(0, t.size, 4096):
            stop = min(t.size, start + 4096)
            phase = np.exp(-2j * pi * np.outer(indices, (t[start:stop] + a) / L))
            # Explicit reduction avoids a spurious Accelerate/BLAS floating-point
            # status warning observed for the otherwise identical complex GEMV.
            coefficients += np.sum(
                phase * weighted[None, start:stop], axis=1
            ) / sqrt(L)
    raw_norm = float(np.linalg.norm(coefficients))
    if not np.isfinite(raw_norm) or raw_norm == 0.0:
        raise ArithmeticError("candidate projection has invalid norm")
    normalized = coefficients / raw_norm
    return FourierProjection(
        x=float(x),
        n_max=n_max,
        indices=indices,
        raw_coefficients=coefficients,
        coefficients=normalized,
        raw_norm=raw_norm,
        quadrature_order=quadrature_order,
        panels_per_nyquist_cycle=panels_per_nyquist_cycle,
        mode_lmax=mode_lmax if source == "prolate" else None,
        source=source,
    )


def transform_basis_values(z: complex, x: float, indices: ArrayLike) -> ComplexArray:
    """Stable values of the Fourier-transform functionals on V_n.

    This is Eq. (5.25) with every removable lattice singularity evaluated via
    the entire sinc form.
    """

    index_array = np.asarray(indices, dtype=np.int64)
    L = log(x)
    lattice = 2.0 * pi * index_array / L
    argument = (complex(z) - lattice) * L / (2.0 * pi)
    # numpy.sinc is entire only for real arrays, so use sin(pi z)/(pi z)
    # with an explicit removable value at zero.
    sinc = np.ones_like(argument, dtype=np.complex128)
    mask = np.abs(argument) > 1e-12
    sinc[mask] = np.sin(pi * argument[mask]) / (pi * argument[mask])
    signs = np.where(index_array % 2 == 0, 1.0, -1.0)
    return sqrt(L) * signs * sinc


def transform_value(projection: FourierProjection, z: complex) -> complex:
    return complex(transform_basis_values(z, projection.x, projection.indices) @ projection.coefficients)


def rectangle_transform_operator_bound(x: float, imaginary_half_height: float = 0.25) -> float:
    """Rigorous L2 functional bound uniform in the rectangle's real part.

    Bessel's inequality bounds the finite Fourier-vector norm by the L2 norm
    of exp(-i z t) on [-log(lambda), log(lambda)].  For |Im z| <= b this is
    sqrt(sinh(b log(x))/b), with its continuous b=0 limit sqrt(log(x)).
    """

    b = abs(float(imaginary_half_height))
    L = log(x)
    if b == 0.0:
        return sqrt(L)
    return sqrt(np.sinh(b * L) / b)


def transform_uniform_bound_from_sin_angle(
    x: float,
    sin_angle_bound: float,
    *,
    imaginary_half_height: float = 0.25,
) -> float:
    """Uniform transform bound after optimal phase alignment of unit vectors."""

    eta = min(1.0, max(0.0, float(sin_angle_bound)))
    vector_distance = sqrt(max(0.0, 2.0 - 2.0 * sqrt(max(0.0, 1.0 - eta * eta))))
    return rectangle_transform_operator_bound(x, imaginary_half_height) * vector_distance


def parity_blocks(matrix: ArrayLike) -> tuple[ComplexArray, ComplexArray, ComplexArray, ComplexArray]:
    """Return even/odd blocks and their isometries for -N,...,N ordering."""

    m = np.asarray(matrix, dtype=np.complex128)
    if m.ndim != 2 or m.shape[0] != m.shape[1] or m.shape[0] % 2 != 1:
        raise ValueError("matrix must be odd-dimensional and square")
    size = m.shape[0]
    n_max = (size - 1) // 2
    even_map = np.zeros((size, n_max + 1), dtype=np.complex128)
    odd_map = np.zeros((size, n_max), dtype=np.complex128)
    even_map[n_max, 0] = 1.0
    for n in range(1, n_max + 1):
        even_map[n_max - n, n] = 1.0 / sqrt(2.0)
        even_map[n_max + n, n] = 1.0 / sqrt(2.0)
        odd_map[n_max - n, n - 1] = 1.0 / sqrt(2.0)
        odd_map[n_max + n, n - 1] = -1.0 / sqrt(2.0)
    even_block = even_map.conj().T @ m @ even_map
    odd_block = odd_map.conj().T @ m @ odd_map
    return even_block, odd_block, even_map, odd_map


def bridge_metrics(matrix: ArrayLike, candidate_coefficients: ArrayLike, *, x: float) -> dict[str, float | bool]:
    """Compute residual/gap/angle data once a zero-free Weil matrix is supplied."""

    m = np.asarray(matrix, dtype=np.complex128)
    m = (m + m.conj().T) / 2.0
    k = np.asarray(candidate_coefficients, dtype=np.complex128)
    k = k / np.linalg.norm(k)
    if m.shape != (k.size, k.size):
        raise ValueError("matrix and candidate dimensions differ")
    even_block, odd_block, even_map, _ = parity_blocks(m)
    even_values, even_vectors = eigh(even_block)
    odd_values = eigh(odd_block, eigvals_only=True)
    ground = even_map @ even_vectors[:, 0]
    mu = float(np.real(np.vdot(k, m @ k)))
    residual = float(np.linalg.norm(m @ k - mu * k))
    gap = float(min(even_values[1], odd_values[0]) - even_values[0])
    competitors = np.concatenate((even_values[1:], odd_values))
    separation = float(np.min(np.abs(competitors - mu)))
    ratio = residual / gap if gap > 0.0 else float("inf")
    sin_bound = min(1.0, residual / separation) if separation > 0.0 else float("inf")
    overlap = min(1.0, abs(complex(np.vdot(ground, k))))
    actual_sin = sqrt(max(0.0, 1.0 - overlap * overlap))
    transform_bound = (
        transform_uniform_bound_from_sin_angle(x, sin_bound)
        if np.isfinite(sin_bound)
        else float("inf")
    )
    return {
        "mu": mu,
        "residual": residual,
        "gap": gap,
        "residual_over_gap": ratio,
        "separation_from_competitors": separation,
        "sin_angle_bound": sin_bound,
        "actual_sin_angle": actual_sin,
        "uniform_transform_bound_imag_quarter": transform_bound,
        "mu_closer_to_ground_than_competitors": bool(
            abs(mu - float(even_values[0])) < separation
        ),
    }


def coefficient_distance(a: Sequence[complex], b: Sequence[complex]) -> float:
    """Phase-aligned Euclidean distance between two nonzero coefficient vectors."""

    av = np.asarray(a, dtype=np.complex128)
    bv = np.asarray(b, dtype=np.complex128)
    av /= np.linalg.norm(av)
    bv /= np.linalg.norm(bv)
    overlap = np.vdot(av, bv)
    phase = np.conj(overlap) / abs(overlap) if overlap else 1.0 + 0.0j
    return float(np.linalg.norm(av - phase * bv))
