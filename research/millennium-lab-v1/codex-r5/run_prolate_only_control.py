#!/usr/bin/env python3
"""Blind high-precision prolate-only hostile control for R5.2.

The construction uses only x=13, N, the prolate differential operator, the
integer-dilation E map, and fixed quadrature/root grids.  It does not import a
reference spectrum or call a zeta-function evaluator.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import mpmath as mp


X = 13
PRIMARY_N = 120
ROOT_COUNT = 70
WORK_DPS = 100
PRIMARY_LMAX = 200
PRIMARY_QUADRATURE_ORDER = 24
PRIMARY_PANELS_PER_CYCLE = 4


def _legendre_raise(l: int) -> mp.mpf:
    return mp.mpf(l + 1) / mp.sqrt((2 * l + 1) * (2 * l + 3))


def _mode_matrix(x: int, lmax: int) -> tuple[mp.matrix, list[int]]:
    degrees = list(range(0, lmax + 1, 2))
    matrix = mp.matrix(len(degrees))
    c2 = (2 * mp.pi * x) ** 2
    for j, l in enumerate(degrees):
        down = _legendre_raise(l - 1) if l else mp.mpf(0)
        up = _legendre_raise(l)
        matrix[j, j] = l * (l + 1) + c2 * (down**2 + up**2)
        if j + 1 < len(degrees):
            matrix[j, j + 1] = matrix[j + 1, j] = c2 * up * _legendre_raise(l + 1)
    return matrix, degrees


def _normalized_legendre_at_zero(l: int) -> mp.mpf:
    return mp.sqrt(mp.mpf(2 * l + 1) / 2) * mp.legendre(l, 0)


def high_precision_candidate(x: int, lmax: int) -> dict:
    matrix, degrees = _mode_matrix(x, lmax)
    eigenvalues, eigenvectors = mp.eigsy(matrix)
    vectors = []
    for ordinal in (0, 2):
        vector = eigenvectors[:, ordinal]
        value_zero = mp.fsum(
            vector[j] * _normalized_legendre_at_zero(l)
            for j, l in enumerate(degrees)
        )
        if value_zero < 0:
            vector = -vector
        vectors.append(vector)
    h0, h4 = vectors
    lam = mp.sqrt(x)
    i0 = mp.sqrt(lam) * mp.sqrt(2) * h0[0]
    i4 = mp.sqrt(lam) * mp.sqrt(2) * h4[0]
    raw = i0 * h4 - i4 * h0
    norm = mp.sqrt(mp.fsum(value**2 for value in raw))
    combination = raw / norm
    standard = [mp.mpf(0)] * (lmax + 1)
    for coefficient, l in zip(combination, degrees):
        standard[l] = coefficient * mp.sqrt(mp.mpf(2 * l + 1) / 2) / mp.sqrt(lam)
    return {
        "x": x,
        "lambda": lam,
        "degrees": degrees,
        "standard_legendre_coefficients": standard,
        "h0_eigenvalue": eigenvalues[0],
        "h4_eigenvalue": eigenvalues[2],
        "zero_integral_residual": mp.sqrt(lam) * mp.sqrt(2) * combination[0],
        "last_coefficient": combination[-1],
    }


def evaluate_h(candidate: dict, y: mp.mpf) -> mp.mpf:
    lam = candidate["lambda"]
    if abs(y) > lam:
        return mp.mpf(0)
    z = y / lam
    coefficients = candidate["standard_legendre_coefficients"]
    p_previous = mp.mpf(1)
    total = coefficients[0]
    if len(coefficients) == 1:
        return total
    p_current = z
    total += coefficients[1] * p_current
    for l in range(1, len(coefficients) - 1):
        p_next = ((2 * l + 1) * z * p_current - l * p_previous) / (l + 1)
        total += coefficients[l + 1] * p_next
        p_previous, p_current = p_current, p_next
    return total


def e_map(candidate: dict, u: mp.mpf) -> mp.mpf:
    lam = candidate["lambda"]
    count = int(mp.floor(lam / u))
    return mp.sqrt(u) * mp.fsum(evaluate_h(candidate, m * u) for m in range(1, count + 1))


def positive_even_breakpoints(x: int) -> list[mp.mpf]:
    lam = mp.sqrt(x)
    half = mp.log(lam)
    points = [mp.mpf(0), half]
    for m in range(1, x + 1):
        point = abs(mp.log(lam / m))
        if point < half:
            points.append(point)
    points.sort()
    distinct = [points[0]]
    for point in points[1:]:
        if point - distinct[-1] > 100 * mp.eps:
            distinct.append(point)
    distinct[0], distinct[-1] = mp.mpf(0), half
    return distinct


def project_even_candidate(
    candidate: dict,
    coefficient_n: int,
    *,
    quadrature_order: int,
    panels_per_cycle: int,
) -> list[mp.mpf]:
    """Return real coefficients c_0,...,c_N of the inversion-even projection."""

    length = mp.log(candidate["x"])
    half = length / 2
    nodes, weights = mp.gauss_quadrature(quadrature_order, "legendre")
    totals = [mp.mpf(0)] * (coefficient_n + 1)
    maximum_width = length / (panels_per_cycle * coefficient_n)
    breakpoints = positive_even_breakpoints(candidate["x"])
    for segment_left, segment_right in zip(breakpoints[:-1], breakpoints[1:]):
        panel_count = max(1, int(mp.ceil((segment_right - segment_left) / maximum_width)))
        for panel in range(panel_count):
            left = segment_left + (segment_right - segment_left) * panel / panel_count
            right = segment_left + (segment_right - segment_left) * (panel + 1) / panel_count
            midpoint = (left + right) / 2
            radius = (right - left) / 2
            for q in range(quadrature_order):
                t = midpoint + radius * nodes[q]
                weight = radius * weights[q]
                u = mp.exp(t)
                k_even = (e_map(candidate, u) + e_map(candidate, 1 / u)) / 2
                theta = 2 * mp.pi * t / length
                cosine = mp.cos(theta)
                cos_previous = mp.mpf(1)
                totals[0] += weight * k_even
                if coefficient_n:
                    cos_current = cosine
                    totals[1] += weight * k_even * cos_current
                    for n in range(1, coefficient_n):
                        cos_next = 2 * cosine * cos_current - cos_previous
                        totals[n + 1] += weight * k_even * cos_next
                        cos_previous, cos_current = cos_current, cos_next
    coefficients = [
        2 * ((-1) ** n) * totals[n] / mp.sqrt(length)
        for n in range(coefficient_n + 1)
    ]
    norm = mp.sqrt(coefficients[0] ** 2 + 2 * mp.fsum(c**2 for c in coefficients[1:]))
    return [c / norm for c in coefficients]


def sinc(value: mp.mpf) -> mp.mpf:
    return mp.mpf(1) if value == 0 else mp.sin(mp.pi * value) / (mp.pi * value)


def transform_value(z: mp.mpf, coefficients: list[mp.mpf], n_max: int, x: int) -> mp.mpf:
    """Evaluate the finite transform, using its removable-pole formula.

    The direct sinc sum is retained only in tiny neighbourhoods of the Fourier
    lattice.  Away from that lattice, Eq. (5.25)'s rational form saves roughly
    2N high-precision trigonometric evaluations per root-search sample.
    """

    length = mp.log(x)
    lattice_step = 2 * mp.pi / length
    nearest = int(mp.nint(abs(z) / lattice_step))
    near_lattice = (
        nearest <= n_max
        and abs(abs(z) - nearest * lattice_step) < mp.mpf("1e-55")
    )
    if near_lattice:
        total = coefficients[0] * sinc(z * length / (2 * mp.pi))
        for n in range(1, n_max + 1):
            lattice = lattice_step * n
            sign = -1 if n % 2 else 1
            total += coefficients[n] * sign * (
                sinc((z - lattice) * length / (2 * mp.pi))
                + sinc((z + lattice) * length / (2 * mp.pi))
            )
        return mp.sqrt(length) * total

    secular = coefficients[0] / z
    z_squared = z * z
    for n in range(1, n_max + 1):
        lattice = lattice_step * n
        secular += 2 * z * coefficients[n] / (z_squared - lattice * lattice)
    return 2 * mp.sin(z * length / 2) * secular / mp.sqrt(length)


def enumerate_roots(coefficients: list[mp.mpf], n_max: int, count: int) -> dict:
    """Enumerate from zero on a grid fixed only by x and the Fourier lattice."""

    lattice_step = 2 * mp.pi / mp.log(X)
    scan_step = lattice_step / 32
    maximum = lattice_step * n_max
    left = scan_step / 11
    f_left = transform_value(left, coefficients, n_max, X)
    roots: list[mp.mpf] = []
    brackets: list[tuple[mp.mpf, mp.mpf]] = []
    while left < maximum and len(roots) < count:
        right = min(maximum, left + scan_step)
        f_right = transform_value(right, coefficients, n_max, X)
        if f_left == 0 or f_left * f_right < 0:
            lo, hi = left, right
            flo, fhi = f_left, f_right
            if flo == 0:
                root = lo
            else:
                # Fourteen safe bisections make the subsequent secant solve
                # local.  If secant ever leaves its sign bracket, finish by
                # bisection instead of accepting an unbracketed zero.
                for _ in range(14):
                    middle = (lo + hi) / 2
                    f_middle = transform_value(middle, coefficients, n_max, X)
                    if f_middle == 0:
                        lo = hi = middle
                        break
                    if flo * f_middle < 0:
                        hi, fhi = middle, f_middle
                    else:
                        lo, flo = middle, f_middle
                if lo == hi:
                    root = lo
                else:
                    try:
                        root = mp.findroot(
                            lambda value: transform_value(value, coefficients, n_max, X),
                            (lo, hi),
                            solver="secant",
                            tol=mp.mpf("1e-78"),
                            maxsteps=60,
                            verify=False,
                        )
                    except (ValueError, ZeroDivisionError):
                        root = (lo + hi) / 2
                    if not (lo <= root <= hi):
                        for _ in range(220):
                            middle = (lo + hi) / 2
                            f_middle = transform_value(middle, coefficients, n_max, X)
                            if f_middle == 0:
                                lo = hi = middle
                                break
                            if flo * f_middle < 0:
                                hi, fhi = middle, f_middle
                            else:
                                lo, flo = middle, f_middle
                            if hi - lo < mp.mpf("1e-75"):
                                break
                        root = (lo + hi) / 2
            if root > 0 and (not roots or root - roots[-1] > scan_step / 8):
                roots.append(root)
                brackets.append((left, right))
        left, f_left = right, f_right
    if len(roots) < count:
        raise RuntimeError(f"only {len(roots)} roots found before the intrinsic cutoff")
    residuals = [abs(transform_value(root, coefficients, n_max, X)) for root in roots]
    # A fixed symmetric difference checks that the sign-changing roots are not
    # numerically flat.  It is a diagnostic, not a proof of exact simplicity.
    derivative_step = mp.mpf("1e-35")
    derivatives = [
        abs(
            (transform_value(root + derivative_step, coefficients, n_max, X)
             - transform_value(root - derivative_step, coefficients, n_max, X))
            / (2 * derivative_step)
        )
        for root in roots
    ]
    return {
        "roots": roots,
        "residuals": residuals,
        "derivatives": derivatives,
        "scan_step": scan_step,
        "brackets": brackets,
    }


def coefficient_distance(first: list[mp.mpf], second: list[mp.mpf], n_max: int) -> mp.mpf:
    return mp.sqrt(
        (first[0] - second[0]) ** 2
        + 2 * mp.fsum((first[n] - second[n]) ** 2 for n in range(1, n_max + 1))
    )


def candidate_probe_distance(first: dict, second: dict) -> mp.mpf:
    """Fixed-grid mode-cutoff diagnostic, independent of any output roots."""

    lam = first["lambda"]
    probes = [lam * j / 32 for j in range(33)]
    return max(abs(evaluate_h(first, y) - evaluate_h(second, y)) for y in probes)


def serialized_root_run(run: dict) -> dict:
    roots = run["roots"]
    return {
        "positive_roots": [mp.nstr(root, 90) for root in roots],
        "positive_roots_float64": [float(root) for root in roots],
        "transform_residuals": [mp.nstr(value, 12) for value in run["residuals"]],
        "absolute_derivative_diagnostics": [mp.nstr(value, 12) for value in run["derivatives"]],
        "scan_step": mp.nstr(run["scan_step"], 40),
        "minimum_adjacent_spacing": mp.nstr(min(b - a for a, b in zip(roots[:-1], roots[1:])), 40),
    }


def main() -> None:
    directory = Path(__file__).resolve().parent
    output = directory / "outputs" / "prolate-only-blind.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with mp.workdps(WORK_DPS):
        print("building primary degree-200 prolate candidate", flush=True)
        primary_candidate = high_precision_candidate(X, PRIMARY_LMAX)
        print("projecting primary candidate", flush=True)
        coefficients = project_even_candidate(
            primary_candidate,
            128,
            quadrature_order=PRIMARY_QUADRATURE_ORDER,
            panels_per_cycle=PRIMARY_PANELS_PER_CYCLE,
        )
        print("projecting quadrature mutation", flush=True)
        quadrature_mutation = project_even_candidate(
            primary_candidate,
            128,
            quadrature_order=18,
            panels_per_cycle=3,
        )
        print("building degree-160 cutoff probe", flush=True)
        cutoff_candidate = high_precision_candidate(X, 160)

        print("enumerating blind primary and mutation roots", flush=True)
        runs = {
            "primary_N120": enumerate_roots(coefficients, 120, ROOT_COUNT),
            "N112": enumerate_roots(coefficients, 112, ROOT_COUNT),
            "N128": enumerate_roots(coefficients, 128, ROOT_COUNT),
            "quadrature_mutation_N120": enumerate_roots(quadrature_mutation, 120, ROOT_COUNT),
        }
        primary_roots = runs["primary_N120"]["roots"]
        mutations = {}
        for name, run in runs.items():
            if name == "primary_N120":
                continue
            displacements = [abs(a - b) for a, b in zip(primary_roots, run["roots"])]
            mutations[name] = {
                "run": serialized_root_run(run),
                "ordinal_displacements_from_primary": [mp.nstr(value, 20) for value in displacements],
                "maximum_ordinal_displacement": mp.nstr(max(displacements), 20),
            }
        payload = {
            "schema": "codex-r5-prolate-only-blind-v1",
            "status": "MEASURED",
            "blind_artifact": True,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "construction": {
                "x": X,
                "N": PRIMARY_N,
                "working_decimal_digits": WORK_DPS,
                "prolate_legendre_cutoff": PRIMARY_LMAX,
                "quadrature_order_per_panel": PRIMARY_QUADRATURE_ORDER,
                "panels_per_shortest_fourier_cycle": PRIMARY_PANELS_PER_CYCLE,
                "even_projection": "orthogonal inversion-even projection before normalization",
                "root_scan": "from zero with lattice_step/32; intrinsic maximum 2*pi*N/log(x)",
                "reference_spectrum_input": False,
                "special_function_zero_finder": False,
            },
            "candidate_diagnostics": {
                "h0_eigenvalue": mp.nstr(primary_candidate["h0_eigenvalue"], 60),
                "h4_eigenvalue": mp.nstr(primary_candidate["h4_eigenvalue"], 60),
                "zero_integral_residual": mp.nstr(primary_candidate["zero_integral_residual"], 20),
                "last_legendre_coefficient": mp.nstr(primary_candidate["last_coefficient"], 20),
                "quadrature_coefficient_distance": mp.nstr(
                    coefficient_distance(coefficients, quadrature_mutation, 128), 20
                ),
                "legendre_cutoff_mode_probe_distance": mp.nstr(
                    candidate_probe_distance(primary_candidate, cutoff_candidate), 20
                ),
            },
            "primary": serialized_root_run(runs["primary_N120"]),
            "mutations": mutations,
        }
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    payload["construction_source_sha256"] = source_hash
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "blind_artifact": payload["blind_artifact"],
        "root_count": len(payload["primary"]["positive_roots"]),
        "quadrature_coefficient_distance": payload["candidate_diagnostics"]["quadrature_coefficient_distance"],
        "legendre_cutoff_mode_probe_distance": payload["candidate_diagnostics"]["legendre_cutoff_mode_probe_distance"],
        "output": str(output),
    }, indent=2))


if __name__ == "__main__":
    main()
