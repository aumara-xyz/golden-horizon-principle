#!/usr/bin/env python3
"""Join the zero-data prolate candidate to finite Weil parity matrices."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.linalg import eigh
from scipy.stats import theilslopes

from prolate_candidate import (
    project_e_map,
    rectangle_transform_operator_bound,
    transform_uniform_bound_from_sin_angle,
)
from weil_core import parity_blocks as build_weil_parity_blocks
from weil_core import prime_power_terms, pseudo_prime_terms


X_GRID = (5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 18, 20)
FINAL_FIVE = (13, 14, 16, 18, 20)
PRIMARY_N = 120
MUTATION_N = (96, 144)
DPS = 60


def _mp_matrix_to_float(matrix) -> np.ndarray:
    complex_matrix = np.asarray(matrix.tolist(), dtype=np.complex128)
    imaginary_defect = float(np.max(np.abs(complex_matrix.imag)))
    scale = float(max(1.0, np.max(np.abs(complex_matrix.real))))
    if imaginary_defect > 1e-12 * scale:
        raise ArithmeticError(f"unexpected Weil-matrix imaginary defect {imaginary_defect}")
    return np.asarray(complex_matrix.real, dtype=np.float64)


def _split_coefficients(full: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Map -N,...,N coefficients to the orthonormal even and odd bases."""

    full = np.asarray(full, dtype=np.complex128)
    n_max = (full.size - 1) // 2
    even = np.empty(n_max + 1, dtype=np.complex128)
    odd = np.empty(n_max, dtype=np.complex128)
    even[0] = full[n_max]
    root2 = np.sqrt(2.0)
    for n in range(1, n_max + 1):
        negative, positive = full[n_max - n], full[n_max + n]
        even[n] = (negative + positive) / root2
        odd[n - 1] = (negative - positive) / root2
    return even, odd


def _metrics(
    even_matrix: np.ndarray,
    odd_matrix: np.ndarray,
    full: np.ndarray,
    x: int,
    *,
    coefficient_uncertainty: float,
) -> dict:
    even_values, even_vectors = eigh(even_matrix)
    odd_values = eigh(odd_matrix, eigvals_only=True)
    even, odd = _split_coefficients(full)
    coefficient_norm = float(np.sqrt(np.vdot(even, even).real + np.vdot(odd, odd).real))
    even /= coefficient_norm
    odd /= coefficient_norm
    # Use explicit reductions: on the host Accelerate's complex GEMV reports
    # stale floating-point status flags after the high-precision build even
    # when all operands and outputs are finite.
    me = np.sum(even_matrix * even[None, :], axis=1)
    mo = np.sum(odd_matrix * odd[None, :], axis=1)
    mu = float(np.real(np.vdot(even, me) + np.vdot(odd, mo)))
    residual = float(np.sqrt(np.linalg.norm(me - mu * even) ** 2 + np.linalg.norm(mo - mu * odd) ** 2))
    gap = float(min(even_values[1], odd_values[0]) - even_values[0])
    competitors = np.concatenate((even_values[1:], odd_values))
    separation = float(np.min(np.abs(competitors - mu)))
    ground_distance = abs(mu - float(even_values[0]))
    identifies_ground = bool(ground_distance < separation)
    raw_sin_bound = residual / separation if separation > 0.0 else float("inf")
    asserted_sin_bound = min(1.0, raw_sin_bound) if identifies_ground and separation > 0 else None
    overlap = abs(complex(np.vdot(even_vectors[:, 0], even)))
    overlap = min(1.0, overlap)
    actual_sin_angle = float(np.sqrt(max(0.0, 1.0 - overlap * overlap)))
    spectral_scale = float(max(np.max(np.abs(even_values)), np.max(np.abs(odd_values))))
    binary64_floor = float(200.0 * np.finfo(float).eps * max(1.0, spectral_scale))
    candidate_floor = float(spectral_scale * coefficient_uncertainty)
    effective_floor = max(binary64_floor, candidate_floor)
    transform_bounds = {}
    for width in (32, 64, 128):
        transform_bounds[str(width)] = (
            transform_uniform_bound_from_sin_angle(x, asserted_sin_bound)
            if asserted_sin_bound is not None
            else None
        )
    ordering_resolved = bool(abs(gap) > effective_floor)
    ratio_resolved = bool(ordering_resolved and residual > effective_floor)
    return {
        "mu": mu,
        "even_ground_eigenvalue": float(even_values[0]),
        "even_second_eigenvalue": float(even_values[1]),
        "odd_ground_eigenvalue": float(odd_values[0]),
        "residual": residual,
        "gap": gap,
        "residual_over_gap": residual / gap if gap != 0.0 else None,
        "separation_from_competitors": separation,
        "ground_distance_from_mu": ground_distance,
        "mu_identifies_even_ground": identifies_ground,
        "raw_residual_over_separation": raw_sin_bound,
        "asserted_sin_angle_bound": asserted_sin_bound,
        "actual_sin_angle": actual_sin_angle,
        "uniform_transform_bounds": transform_bounds,
        "rectangle_imaginary_half_height": 0.25,
        "uniform_functional_norm_bound": rectangle_transform_operator_bound(x, 0.25),
        "binary64_residual_floor": binary64_floor,
        "candidate_coefficient_uncertainty": coefficient_uncertainty,
        "candidate_action_uncertainty_bound": candidate_floor,
        "effective_residual_floor": effective_floor,
        "residual_at_or_below_effective_floor": bool(residual <= effective_floor),
        "gap_at_or_below_effective_floor": bool(abs(gap) <= effective_floor),
        "near_null_ordering_resolved": ordering_resolved,
        "residual_over_gap_status": "MEASURED" if ratio_resolved else "UNVERIFIED",
        "finite_ground_angle_status": "MEASURED" if ordering_resolved else "UNVERIFIED",
        "candidate_even_norm": float(np.linalg.norm(even)),
        "candidate_odd_norm": float(np.linalg.norm(odd)),
    }


def _cache_matrix(
    directory: Path,
    name: str,
    even: np.ndarray,
    odd: np.ndarray,
    metadata: dict,
) -> tuple[str, str]:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.npz"
    np.savez_compressed(
        path,
        even=even,
        odd=odd,
        metadata=np.asarray(json.dumps(metadata, sort_keys=True)),
    )
    return str(path.name), hashlib.sha256(path.read_bytes()).hexdigest()


def _load_matrix(directory: Path, name: str) -> tuple[np.ndarray, np.ndarray, dict] | None:
    path = directory / f"{name}.npz"
    if not path.exists():
        return None
    with np.load(path, allow_pickle=False) as archive:
        even = np.asarray(archive["even"], dtype=np.float64)
        odd = np.asarray(archive["odd"], dtype=np.float64)
        metadata = json.loads(str(archive["metadata"].item()))
    return even, odd, metadata


def _fit_power(rows: list[dict]) -> dict:
    usable = [
        row for row in rows
        if row["metrics"]["residual_over_gap"] is not None
        and row["metrics"]["residual_over_gap"] > 0.0
        and row["metrics"]["near_null_ordering_resolved"]
    ]
    if len(usable) != len(rows):
        return {
            "status": "UNVERIFIED",
            "reason": "one or more registered gaps were nonpositive or below the binary64/projection floor, so log-log decay is not identified",
            "x_values": [row["x"] for row in rows],
            "usable_x_values": [row["x"] for row in usable],
        }
    lambdas = np.sqrt(np.asarray([row["x"] for row in usable], dtype=float))
    ratios = np.asarray([row["metrics"]["residual_over_gap"] for row in usable], dtype=float)
    log_lam, log_ratio = np.log(lambdas), np.log(ratios)
    slope, intercept = np.polyfit(log_lam, log_ratio, 1)
    robust = theilslopes(log_ratio, log_lam)
    fitted = intercept + slope * log_lam
    constant = np.full_like(log_ratio, np.mean(log_ratio))
    rss_power = float(np.sum((log_ratio - fitted) ** 2))
    rss_constant = float(np.sum((log_ratio - constant) ** 2))

    def aic(rss: float, parameters: int) -> float:
        return float(len(usable) * np.log(max(rss, np.finfo(float).tiny) / len(usable)) + 2 * parameters)

    return {
        "model": "log(r/gap)=log(C)-p*log(lambda)",
        "status": "MEASURED",
        "x_values": [row["x"] for row in usable],
        "ols_p": float(-slope),
        "ols_C": float(np.exp(intercept)),
        "theil_sen_p": float(-robust.slope),
        "theil_sen_p_interval": [float(-robust.high_slope), float(-robust.low_slope)],
        "rss_log_power": rss_power,
        "rss_log_constant": rss_constant,
        "aic_log_power": aic(rss_power, 2),
        "aic_log_constant": aic(rss_constant, 1),
        "power_delta_aic_vs_constant": aic(rss_power, 2) - aic(rss_constant, 1),
    }


def build(output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    matrix_dir = output / "matrices"
    log_lines: list[str] = []
    result: dict = {
        "schema": "codex-r5-prolate-bridge-v1",
        "status": "UNVERIFIED",
        "candidate_construction_status": "MEASURED",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "matrix_construction_dps": DPS,
        "matrix_analysis_precision": "binary64",
        "primary": [],
        "n_mutations": [],
        "hermite_control": [],
        "pseudo_control": [],
        "matrix_cache": [],
    }

    pseudo_terms, pseudo_attempts = pseudo_prime_terms(52025001, 13.0)
    result["pseudo_control_definition"] = {
        "seed": 52025001,
        "attempts": pseudo_attempts,
        "comb": [term.__dict__ for term in pseudo_terms],
        "application": "same accepted x=13 comb retained for the registered final-five mutation",
    }

    cases = [(x, PRIMARY_N, "primary") for x in X_GRID]
    cases += [(x, n_max, "n_mutation") for n_max in MUTATION_N for x in FINAL_FIVE]
    for x, n_max, kind in cases:
        terms = prime_power_terms(x)
        cache_name = f"weil-true-x{x}-N{n_max}-dps{DPS}"
        cached = _load_matrix(matrix_dir, cache_name)
        if cached is None:
            even_mp, odd_mp, meta = build_weil_parity_blocks(n_max, x, terms, DPS)
            even, odd = _mp_matrix_to_float(even_mp), _mp_matrix_to_float(odd_mp)
            filename, digest = _cache_matrix(matrix_dir, cache_name, even, odd, meta)
        else:
            even, odd, meta = cached
            filename = f"{cache_name}.npz"
            digest = hashlib.sha256((matrix_dir / filename).read_bytes()).hexdigest()
        result["matrix_cache"].append({
            "kind": "true",
            "x": x,
            "N": n_max,
            "file": filename,
            "sha256": digest,
        })

        projection = project_e_map(
            x, n_max, quadrature_order=20, panels_per_nyquist_cycle=4, mode_lmax=400
        )
        projection_check = project_e_map(
            x, n_max, quadrature_order=20, panels_per_nyquist_cycle=8, mode_lmax=400
        )
        overlap = np.vdot(projection.coefficients, projection_check.coefficients)
        phase = np.conj(overlap) / abs(overlap) if overlap else 1.0
        coefficient_uncertainty = float(
            np.linalg.norm(projection.coefficients - phase * projection_check.coefficients)
        )
        metrics = _metrics(
            even,
            odd,
            projection.coefficients,
            x,
            coefficient_uncertainty=coefficient_uncertainty,
        )
        row = {"x": x, "lambda": float(np.sqrt(x)), "N": n_max, "metrics": metrics}
        result["primary" if kind == "primary" else "n_mutations"].append(row)

        hermite = project_e_map(
            x, n_max, quadrature_order=20, panels_per_nyquist_cycle=4, source="hermite"
        )
        hermite_check = project_e_map(
            x, n_max, quadrature_order=20, panels_per_nyquist_cycle=8, source="hermite"
        )
        h_overlap = np.vdot(hermite.coefficients, hermite_check.coefficients)
        h_phase = np.conj(h_overlap) / abs(h_overlap) if h_overlap else 1.0
        h_uncertainty = float(
            np.linalg.norm(hermite.coefficients - h_phase * hermite_check.coefficients)
        )
        result["hermite_control"].append({
            "x": x,
            "lambda": float(np.sqrt(x)),
            "N": n_max,
            "metrics": _metrics(
                even,
                odd,
                hermite.coefficients,
                x,
                coefficient_uncertainty=h_uncertainty,
            ),
        })
        message = (
            f"{metrics['residual_over_gap_status']} true x={x} N={n_max} "
            f"r/gap={metrics['residual_over_gap']:.12e} "
            f"actual_sin={metrics['actual_sin_angle']:.12e}"
        )
        print(message, flush=True)
        log_lines.append(message)

        if n_max == PRIMARY_N and x in FINAL_FIVE:
            pseudo_meta = dict(meta)
            pseudo_meta.update({"control": "pseudo", "seed": "52025001"})
            p_name = f"weil-pseudo52025001-x{x}-N{n_max}-dps{DPS}"
            p_cached = _load_matrix(matrix_dir, p_name)
            if p_cached is None:
                even_p_mp, odd_p_mp, _ = build_weil_parity_blocks(n_max, x, pseudo_terms, DPS)
                even_p, odd_p = _mp_matrix_to_float(even_p_mp), _mp_matrix_to_float(odd_p_mp)
                p_file, p_digest = _cache_matrix(matrix_dir, p_name, even_p, odd_p, pseudo_meta)
            else:
                even_p, odd_p, _ = p_cached
                p_file = f"{p_name}.npz"
                p_digest = hashlib.sha256((matrix_dir / p_file).read_bytes()).hexdigest()
            result["matrix_cache"].append({
                "kind": "pseudo",
                "x": x,
                "N": n_max,
                "file": p_file,
                "sha256": p_digest,
            })
            p_metrics = _metrics(
                even_p,
                odd_p,
                projection.coefficients,
                x,
                coefficient_uncertainty=coefficient_uncertainty,
            )
            result["pseudo_control"].append({
                "x": x,
                "lambda": float(np.sqrt(x)),
                "N": n_max,
                "metrics": p_metrics,
            })
            p_message = (
                f"{p_metrics['residual_over_gap_status']} pseudo x={x} N={n_max} "
                f"r/gap={p_metrics['residual_over_gap']:.12e}"
            )
            print(p_message, flush=True)
            log_lines.append(p_message)

    primary_last_five = [row for row in result["primary"] if row["x"] in FINAL_FIVE]
    result["power_fit_primary_last_five"] = _fit_power(primary_last_five)
    result["power_fit_by_N"] = {str(PRIMARY_N): result["power_fit_primary_last_five"]}
    for n_max in MUTATION_N:
        rows = [row for row in result["n_mutations"] if row["N"] == n_max]
        result["power_fit_by_N"][str(n_max)] = _fit_power(rows)

    hermite_final = [
        row["metrics"]["residual_over_gap"]
        for row in result["hermite_control"]
        if row["N"] == PRIMARY_N and row["x"] in FINAL_FIVE
    ]
    true_final = [row["metrics"]["residual_over_gap"] for row in primary_last_five]
    pseudo_final = [row["metrics"]["residual_over_gap"] for row in result["pseudo_control"]]
    result["final_five_signed_ratio_diagnostics"] = {
        "status": "UNVERIFIED",
        "reason": "near-null gaps are below the effective numerical floor; signed medians are retained only as diagnostics",
        "true_prolate_prime": float(np.median(true_final)),
        "undeformed_hermite_prime": float(np.median(hermite_final)),
        "prolate_pseudo": float(np.median(pseudo_final)),
    }
    summary_path = output / "bridge-summary.json"
    summary_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output / "bridge-run.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "summary": str(summary_path),
        "primary_cases": len(result["primary"]),
        "mutation_cases": len(result["n_mutations"]),
    }, indent=2))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "prolate-bridge-data",
    )
    args = parser.parse_args()
    build(args.output)


if __name__ == "__main__":
    main()
