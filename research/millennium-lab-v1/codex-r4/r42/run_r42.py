#!/usr/bin/env python3
"""Round 4.2: exact 2011 Berry--Keating and Sierra--Rodriguez-Laguna spectra.

This runner deliberately uses the published quantum problems, not either
paper's semiclassical counting rule.  It writes JSON, CSV, and a plain log in
the same directory as this file.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable

import mpmath as mp
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq


HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
ZEROS_PATH = LAB / "zeros.txt"
LOG_PATH = HERE / "run-r42.log"
JSON_PATH = HERE / "metrics-r42.json"
CSV_PATH = HERE / "spectra-r42.csv"

TWOPI = 2.0 * math.pi
ETA = 1.0 / TWOPI
HBAR = 1.0 / TWOPI
H_SRL = 1.0

BK_SOURCE = "https://doi.org/10.1088/1751-8113/44/28/285203"
SRL_SOURCE = "https://doi.org/10.1103/PhysRevLett.106.200201"


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("r42")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    file_handler = logging.FileHandler(LOG_PATH, mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(stream)
    logger.addHandler(file_handler)
    return logger


LOGGER = setup_logging()


@dataclass(frozen=True)
class BKConfig:
    alpha: float
    x_max: float
    rtol: float
    atol: float
    scan_step: float = 0.02
    max_step: float = 0.12


@dataclass(frozen=True)
class SRLConfig:
    theta: float
    mesh: float
    dps: int


def load_zeros(n: int = 20) -> np.ndarray:
    values = np.loadtxt(ZEROS_PATH, dtype=float)
    if values.size < n:
        raise RuntimeError(f"Need {n} zeta ordinates, found {values.size}")
    return values[:n]


# ---------------------------------------------------------------------------
# Berry--Keating, J. Phys. A 44 (2011), Eqs. (2.7)--(2.9), (2.22), (3.2).
# ---------------------------------------------------------------------------


def bk_coefficient(x: float, energy: float) -> complex:
    one_plus = 1.0 + x * x
    h_x = 1.0 - (energy * energy * x * x) / (4.0 * one_plus * one_plus)
    g_x = energy * (1.0 - x * x) / (2.0 * one_plus * one_plus)
    return h_x / (ETA * ETA) + 1j * g_x / ETA


def bk_reverse_solution(
    energy: float,
    config: BKConfig,
    *,
    with_integral: bool = False,
) -> tuple[complex, complex, complex | None, int]:
    """Integrate the decaying solution from x_max back to the origin.

    The terminal data chi=1, chi'=-1/eta are Eq. (3.2)'s decaying branch;
    their arbitrary common scale cancels from all residuals.  If requested,
    J'=phi is integrated too, with phi=chi*(1+x^2)^(iE/(4 eta)).
    """

    if with_integral:
        y0 = np.array([1.0 + 0j, -1.0 / ETA + 0j, 0j], dtype=complex)

        def rhs(x: float, y: np.ndarray) -> np.ndarray:
            phase = np.exp(1j * energy * math.log1p(x * x) / (4.0 * ETA))
            return np.array([y[1], bk_coefficient(x, energy) * y[0], y[0] * phase])

    else:
        y0 = np.array([1.0 + 0j, -1.0 / ETA + 0j], dtype=complex)

        def rhs(x: float, y: np.ndarray) -> np.ndarray:
            return np.array([y[1], bk_coefficient(x, energy) * y[0]])

    sol = solve_ivp(
        rhs,
        (config.x_max, 0.0),
        y0,
        method="DOP853",
        rtol=config.rtol,
        atol=config.atol,
        max_step=config.max_step,
    )
    if not sol.success:
        raise RuntimeError(f"BK reverse integration failed at E={energy}: {sol.message}")
    chi0 = complex(sol.y[0, -1])
    dchi0 = complex(sol.y[1, -1])
    j0 = complex(sol.y[2, -1]) if with_integral else None
    return chi0, dchi0, j0, int(sol.nfev)


def bk_m_value(energy: float, config: BKConfig) -> complex:
    chi0, dchi0, _, _ = bk_reverse_solution(energy, config)
    return ETA * dchi0 / chi0


def bk_crossing_function(energy: float, config: BKConfig) -> float:
    rotated = bk_m_value(energy, config) * np.exp(-1j * config.alpha)
    return float(rotated.imag)


def bk_roots(config: BKConfig, count: int = 20, e_max: float = 24.0) -> list[float]:
    """Bracket phase crossings and retain only m(E)=exp(i alpha), not its antipode."""

    roots: list[float] = []
    left = 1.0e-8
    f_left = bk_crossing_function(left, config)
    energy = left + config.scan_step
    scan_points = 1
    while energy <= e_max + 0.5 * config.scan_step and len(roots) < count:
        f_right = bk_crossing_function(energy, config)
        scan_points += 1
        if f_left == 0.0 or f_left * f_right < 0.0:
            a = left
            b = energy
            try:
                root = brentq(
                    lambda value: bk_crossing_function(value, config),
                    a,
                    b,
                    xtol=2.0e-12,
                    rtol=2.0e-14,
                    maxiter=80,
                )
            except ValueError:
                root = math.nan
            if math.isfinite(root):
                aligned = bk_m_value(root, config) * np.exp(-1j * config.alpha)
                if aligned.real > 0.0 and (not roots or abs(root - roots[-1]) > 1.0e-7):
                    roots.append(float(root))
                    LOGGER.info(
                        "BK alpha=%.6f L=%.0f root %02d E=%.12f |m|-1=%+.3e",
                        config.alpha,
                        config.x_max,
                        len(roots),
                        root,
                        abs(aligned) - 1.0,
                    )
        left = energy
        f_left = f_right
        energy += config.scan_step
    LOGGER.info(
        "BK alpha=%.6f L=%.0f scan points=%d roots=%d",
        config.alpha,
        config.x_max,
        scan_points,
        len(roots),
    )
    if len(roots) != count:
        raise RuntimeError(f"BK found {len(roots)} roots below E={e_max}, expected {count}")
    return roots


def bk_integral_residual(energy: float, config: BKConfig) -> dict[str, float]:
    """Check the nonlocal integral identity (2.16), independent of root bracketing."""

    chi0, dchi0, j0, nfev = bk_reverse_solution(energy, config, with_integral=True)
    assert j0 is not None
    # J(0) = integral_{x_max}^0 phi dx = - integral_0^{x_max} phi dx.
    lhs = ETA * ETA * dchi0
    rhs = j0
    denominator = abs(lhs) + abs(rhs)
    nonlocal_residual = abs(lhs - rhs) / denominator if denominator else math.inf
    m_value = ETA * dchi0 / chi0
    phase_residual = abs(m_value - np.exp(1j * config.alpha))
    return {
        "nonlocal_relative": float(nonlocal_residual),
        "phase_absolute": float(phase_residual),
        "m_modulus_error": float(abs(abs(m_value) - 1.0)),
        "nfev": nfev,
    }


# ---------------------------------------------------------------------------
# Sierra--Rodriguez-Laguna, PRL 106 (2011), Eqs. (11), (12), (14), (24).
# ---------------------------------------------------------------------------


def srl_secular_mp(energy: mp.mpf, theta: mp.mpf) -> mp.mpf:
    hbar = mp.mpf(1) / (2 * mp.pi)
    order = mp.mpf("0.5") + 1j * energy / (2 * hbar)
    argument = mp.mpf(1) / hbar
    term = mp.exp(-0.5j * theta) * mp.besselk(order, argument)
    return 2 * mp.re(term)


def mp_bisect(
    function: Callable[[mp.mpf], mp.mpf],
    left: mp.mpf,
    right: mp.mpf,
    *,
    iterations: int,
) -> mp.mpf:
    f_left = function(left)
    f_right = function(right)
    if f_left == 0:
        return left
    if f_right == 0:
        return right
    if mp.sign(f_left) == mp.sign(f_right):
        raise ValueError("Bisection interval does not change sign")
    for _ in range(iterations):
        middle = (left + right) / 2
        f_middle = function(middle)
        if f_middle == 0:
            return middle
        if mp.sign(f_middle) == mp.sign(f_left):
            left = middle
            f_left = f_middle
        else:
            right = middle
            f_right = f_middle
    return (left + right) / 2


def srl_roots(config: SRLConfig, count: int = 20, e_max: float = 24.0) -> list[mp.mpf]:
    roots: list[mp.mpf] = []
    with mp.workdps(config.dps):
        theta = mp.mpf(str(config.theta))
        mesh = mp.mpf(str(config.mesh))
        left = mp.mpf("0")
        f_left = srl_secular_mp(left, theta)
        steps = int(math.ceil(e_max / config.mesh))
        for index in range(1, steps + 1):
            right = mesh * index
            f_right = srl_secular_mp(right, theta)
            if f_left == 0 or mp.sign(f_left) != mp.sign(f_right):
                root = mp_bisect(
                    lambda value: srl_secular_mp(value, theta),
                    left,
                    right,
                    iterations=max(90, int(config.dps * 3.5)),
                )
                if root > 0 and (not roots or abs(root - roots[-1]) > mp.mpf("1e-30")):
                    roots.append(+root)
                    LOGGER.info(
                        "SRL theta=%.6f mesh=%.4g dps=%d root %02d E=%s",
                        config.theta,
                        config.mesh,
                        config.dps,
                        len(roots),
                        mp.nstr(root, 18),
                    )
                    if len(roots) == count:
                        break
            left = right
            f_left = f_right
    if len(roots) != count:
        raise RuntimeError(f"SRL found {len(roots)} roots below E={e_max}, expected {count}")
    return roots


def srl_boundary_residual(energy: float, theta: float, dps: int = 50) -> float:
    """Directly quadrature-check the nonlocal boundary condition, Eq. (11)."""

    with mp.workdps(dps):
        e = mp.mpf(str(energy))
        th = mp.mpf(str(theta))
        hbar = mp.mpf(1) / (2 * mp.pi)

        def psi(x: mp.mpf) -> mp.mpc:
            return mp.power(x, 1j * e / (2 * hbar)) * mp.besselk(
                mp.mpf("0.5") - 1j * e / (2 * hbar), x / hbar
            )

        term_local = hbar * mp.exp(1j * th) * psi(mp.mpf(1))
        integral = mp.quad(
            lambda x: mp.sqrt(x) * psi(x),
            [mp.mpf(1), mp.mpf("1.5"), mp.mpf(2), mp.mpf(3), mp.mpf(5), mp.mpf(8), mp.inf],
        )
        denominator = abs(term_local) + abs(integral)
        return float(abs(term_local + integral) / denominator)


# ---------------------------------------------------------------------------
# Controls and reporting.
# ---------------------------------------------------------------------------


def smooth_rvm_quantiles(count: int) -> np.ndarray:
    """Parameter-free midpoint quantiles: theta(T)/pi + 1 = n - 1/2."""

    output: list[float] = []
    for n in range(1, count + 1):
        target = n - 0.5

        def residual(t: float) -> float:
            return float(mp.siegeltheta(t) / mp.pi + 1 - target)

        left = 7.0 if n == 1 else output[-1] + 0.05
        right = 200.0
        output.append(float(brentq(residual, left, right, xtol=1.0e-13, rtol=1.0e-14)))
    return np.asarray(output)


def comparison(candidate: Iterable[float], truth: np.ndarray) -> dict[str, float | bool]:
    values = np.asarray(list(candidate), dtype=float)
    residual = values - truth
    return {
        "rmse": float(np.sqrt(np.mean(residual * residual))),
        "mae": float(np.mean(np.abs(residual))),
        "max_abs": float(np.max(np.abs(residual))),
        "pearson": float(np.corrcoef(values, truth)[0, 1]),
        "min_abs": float(np.min(np.abs(residual))),
        "any_within_1e-6": bool(np.any(np.abs(residual) <= 1.0e-6)),
    }


def scaled_convergence(primary: Iterable[float], refined: Iterable[float]) -> dict[str, float]:
    a = TWOPI * np.asarray(list(primary), dtype=float)
    b = TWOPI * np.asarray(list(refined), dtype=float)
    delta = np.abs(a - b)
    return {
        "max_abs": float(np.max(delta)),
        "rms": float(np.sqrt(np.mean(delta * delta))),
        "median_abs": float(np.median(delta)),
    }


def phase_mutation(primary: Iterable[float], mutated: Iterable[float]) -> dict[str, float]:
    a = TWOPI * np.asarray(list(primary), dtype=float)
    b = TWOPI * np.asarray(list(mutated), dtype=float)
    delta = np.abs(a - b)
    return {
        "max_abs_scaled_shift": float(np.max(delta)),
        "min_abs_scaled_shift": float(np.min(delta)),
        "rms_scaled_shift": float(np.sqrt(np.mean(delta * delta))),
        "count_over_0_1": int(np.sum(delta > 0.1)),
    }


def run_bk() -> dict:
    LOGGER.info("Starting Berry--Keating exact ODE")
    primary_cfg = BKConfig(alpha=0.0, x_max=30.0, rtol=1.0e-11, atol=1.0e-11)
    refined_cfg = BKConfig(alpha=0.0, x_max=40.0, rtol=1.0e-12, atol=1.0e-12)
    mutation_cfg = BKConfig(alpha=math.pi / 2, x_max=40.0, rtol=1.0e-12, atol=1.0e-12)

    primary = bk_roots(primary_cfg)
    refined = bk_roots(refined_cfg)
    mutated = bk_roots(mutation_cfg)
    residuals = [bk_integral_residual(root, refined_cfg) for root in refined]
    result = {
        "source": BK_SOURCE,
        "method": "exact published ODE, stable reverse shooting from the decaying branch",
        "primary_config": asdict(primary_cfg),
        "refined_config": asdict(refined_cfg),
        "mutation_config": asdict(mutation_cfg),
        "primary_raw": primary,
        "refined_raw": refined,
        "mutated_raw": mutated,
        "refined_scaled": (TWOPI * np.asarray(refined)).tolist(),
        "mutated_scaled": (TWOPI * np.asarray(mutated)).tolist(),
        "convergence_scaled": scaled_convergence(primary, refined),
        "independent_nonlocal_residuals": residuals,
        "independent_nonlocal_max": float(max(r["nonlocal_relative"] for r in residuals)),
        "phase_residual_max": float(max(r["phase_absolute"] for r in residuals)),
        "m_modulus_error_max": float(max(r["m_modulus_error"] for r in residuals)),
        "mutation": phase_mutation(refined, mutated),
    }
    LOGGER.info("BK scaled convergence max %.6e", result["convergence_scaled"]["max_abs"])
    LOGGER.info("BK nonlocal residual max %.6e", result["independent_nonlocal_max"])
    return result


def run_srl() -> dict:
    LOGGER.info("Starting Sierra--Rodriguez-Laguna exact Bessel secular equation")
    primary_cfg = SRLConfig(theta=math.pi / 4, mesh=0.002, dps=60)
    refined_cfg = SRLConfig(theta=math.pi / 4, mesh=0.001, dps=80)
    mutation_cfg = SRLConfig(theta=3 * math.pi / 4, mesh=0.002, dps=60)

    primary_mp = srl_roots(primary_cfg)
    refined_mp = srl_roots(refined_cfg)
    mutated_mp = srl_roots(mutation_cfg)
    primary = [float(value) for value in primary_mp]
    refined = [float(value) for value in refined_mp]
    mutated = [float(value) for value in mutated_mp]
    boundary_residuals = [srl_boundary_residual(root, refined_cfg.theta) for root in refined]
    result = {
        "source": SRL_SOURCE,
        "method": "exact published Bessel secular equation; energy mesh only brackets roots",
        "primary_config": asdict(primary_cfg),
        "refined_config": asdict(refined_cfg),
        "mutation_config": asdict(mutation_cfg),
        "primary_raw": primary,
        "refined_raw": refined,
        "refined_raw_decimal": [mp.nstr(value, 50) for value in refined_mp],
        "mutated_raw": mutated,
        "refined_scaled": (TWOPI * np.asarray(refined)).tolist(),
        "mutated_scaled": (TWOPI * np.asarray(mutated)).tolist(),
        "convergence_scaled": scaled_convergence(primary, refined),
        "independent_boundary_residuals": boundary_residuals,
        "independent_boundary_max": float(max(boundary_residuals)),
        "mutation": phase_mutation(refined, mutated),
    }
    LOGGER.info("SRL scaled convergence max %.6e", result["convergence_scaled"]["max_abs"])
    LOGGER.info("SRL boundary residual max %.6e", result["independent_boundary_max"])
    return result


def write_outputs(bk: dict, srl: dict) -> dict:
    zeros = load_zeros(20)
    smooth = smooth_rvm_quantiles(20)
    smooth_stats = comparison(smooth, zeros)

    for model in (bk, srl):
        model["raw_comparison"] = comparison(model["refined_raw"], zeros)
        model["scaled_comparison"] = comparison(model["refined_scaled"], zeros)
        model["raw_to_scaled_rmse_factor"] = (
            model["raw_comparison"]["rmse"] / model["scaled_comparison"]["rmse"]
        )
        model["scaled_rmse_over_smooth"] = (
            model["scaled_comparison"]["rmse"] / smooth_stats["rmse"]
        )

    metrics = {
        "status_vocabulary": ["MEASURED", "UNVERIFIED", "PREDICTED", "VOID"],
        "status": "MEASURED",
        "normalization": {
            "raw_energy": "E",
            "scaled_height": "t = 2*pi*E",
            "scale_is_fitted": False,
            "berry_keating": "alpha=0, eta=1/(2*pi), Berry--Keating Eq. (5.3)",
            "sierra_rodriguez_laguna": "h=1, hbar=1/(2*pi), theta=pi/4, SRL Eq. (24)",
        },
        "zeta_ordinates": zeros.tolist(),
        "smooth_control": {
            "definition": "theta(T)/pi + 1 = n - 1/2 (midpoint smooth Riemann--von Mangoldt quantile)",
            "values": smooth.tolist(),
            "comparison": smooth_stats,
        },
        "berry_keating": bk,
        "sierra_rodriguez_laguna": srl,
        "three_yeses": [
            {
                "candidate": "Berry--Keating compact Hamiltonian (2011)",
                "self_adjoint_discrete": True,
                "chaotic_without_arithmetic_degeneracy": False,
                "orbits_log_p": False,
            },
            {
                "candidate": "Sierra--Rodriguez-Laguna H=x(p+l_p^2/p) (2011)",
                "self_adjoint_discrete": True,
                "chaotic_without_arithmetic_degeneracy": False,
                "orbits_log_p": False,
            },
        ],
    }

    JSON_PATH.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "n",
            "zeta",
            "smooth_rvm",
            "bk_raw",
            "bk_scaled",
            "bk_residual",
            "bk_mutated_scaled",
            "srl_raw",
            "srl_scaled",
            "srl_residual",
            "srl_mutated_scaled",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for index in range(20):
            writer.writerow(
                {
                    "n": index + 1,
                    "zeta": f"{zeros[index]:.12f}",
                    "smooth_rvm": f"{smooth[index]:.12f}",
                    "bk_raw": f"{bk['refined_raw'][index]:.12f}",
                    "bk_scaled": f"{bk['refined_scaled'][index]:.12f}",
                    "bk_residual": f"{bk['refined_scaled'][index] - zeros[index]:+.12f}",
                    "bk_mutated_scaled": f"{bk['mutated_scaled'][index]:.12f}",
                    "srl_raw": f"{srl['refined_raw'][index]:.12f}",
                    "srl_scaled": f"{srl['refined_scaled'][index]:.12f}",
                    "srl_residual": f"{srl['refined_scaled'][index] - zeros[index]:+.12f}",
                    "srl_mutated_scaled": f"{srl['mutated_scaled'][index]:.12f}",
                }
            )
    LOGGER.info("Wrote %s and %s", JSON_PATH.name, CSV_PATH.name)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("all", "bk", "srl", "merge"), default="all")
    args = parser.parse_args()

    if args.stage == "bk":
        result = run_bk()
        (HERE / "bk-partial.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return
    if args.stage == "srl":
        result = run_srl()
        (HERE / "srl-partial.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return
    if args.stage == "merge":
        bk = json.loads((HERE / "bk-partial.json").read_text(encoding="utf-8"))
        srl = json.loads((HERE / "srl-partial.json").read_text(encoding="utf-8"))
        metrics = write_outputs(bk, srl)
        LOGGER.info("Merged independently frozen BK and SRL partial outputs")
        LOGGER.info("BK refined raw levels %s", bk["refined_raw"])
        LOGGER.info("SRL refined raw levels %s", srl["refined_raw"])
        LOGGER.info(
            "Final RMSE: smooth=%.6f BK=%.6f SRL=%.6f",
            metrics["smooth_control"]["comparison"]["rmse"],
            metrics["berry_keating"]["scaled_comparison"]["rmse"],
            metrics["sierra_rodriguez_laguna"]["scaled_comparison"]["rmse"],
        )
        return

    bk = run_bk()
    srl = run_srl()
    metrics = write_outputs(bk, srl)
    LOGGER.info(
        "Final RMSE: smooth=%.6f BK=%.6f SRL=%.6f",
        metrics["smooth_control"]["comparison"]["rmse"],
        metrics["berry_keating"]["scaled_comparison"]["rmse"],
        metrics["sierra_rodriguez_laguna"]["scaled_comparison"]["rmse"],
    )


if __name__ == "__main__":
    main()
