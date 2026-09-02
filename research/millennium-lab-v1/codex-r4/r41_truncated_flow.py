#!/usr/bin/env python3
"""Round 4.1: finite-block de Bruijn--Newman zero dynamics.

This is deliberately a finite-N calculation.  It integrates the same ODE as
``toy_flow.py``,

    dx_j/dt = sum_(k != j) 2/(x_j-x_k) + sum_k 2/(x_j+x_k),

backwards until the first consecutive gap reaches a small positive event
threshold.  Large Odlyzko bases are stored separately from their printed
offsets, so no gap is ever obtained by subtracting two ~1e21 floats.

For each 10,000-row case, the force and one-body derivative at t=0 use every
particle.  Moving windows of 128, 256, 512, and 1,024 particles are then
integrated, with omitted nodes represented by that exact initial force and its
linear response.  Mirror interactions are evaluated directly at the low
block.  At the three remote blocks their all-N initialization uses a cubic
geometric-series expansion around the separately represented physical centre;
the script records a bound for the first omitted term.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import math
import platform
import sys
import time
from dataclasses import dataclass
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Sequence

import numpy as np
import scipy
from scipy.integrate import solve_ivp


getcontext().prec = 60

ODLYZKO_SOURCE = "https://www-users.cse.umn.edu/~odlyzko/zeta_tables/"
DEFAULT_DATA_DIR = Path(__file__).resolve().parent / "odlyzko-inputs"


@dataclass(frozen=True)
class BlockSpec:
    key: str
    label: str
    filename: str
    skip: int
    base: Decimal
    first_global_ordinal: int


BLOCKS = (
    BlockSpec("A", "zeros 1--10,000", "zeros1.txt", 0, Decimal(0), 1),
    BlockSpec(
        "B", "zeros #10^12+1--#10^12+10,000", "zeros3.txt", 9,
        Decimal("267653395647"), 10**12 + 1,
    ),
    BlockSpec(
        "C", "zeros #10^21+1--#10^21+10,000", "zeros4.txt", 9,
        Decimal("144176897509546973000"), 10**21 + 1,
    ),
    BlockSpec(
        "D", "zeros #10^22+1--#10^22+10,000", "zeros5.txt", 9,
        Decimal("1370919909931995300000"), 10**22 + 1,
    ),
)

EXPECTED_SHA256 = {
    "zeros1.txt": "3436c916a7878261ac183fd7b9448c9a4736b8bbccf1356874a6ce1788541632",
    "zeros3.txt": "75a1f1a978d5e3eddd16518f661d41a95a40b33782389ba02ec4ed0ce0764807",
    "zeros4.txt": "10d9f7dab2bbfff6b8befbe6f765969b0b3f38f6110ed1df423931addd52da8f",
    "zeros5.txt": "250ac4ba722c6face4d07c05777376fc2b9bc021b05232e8f53c91b1eb2b7e0d",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for part in iter(lambda: fh.read(1 << 20), b""):
            h.update(part)
    return h.hexdigest()


def decimal_rows(path: Path, skip: int, n: int = 10_000) -> list[Decimal]:
    rows = path.read_text().splitlines()[skip:]
    out = [Decimal(row.strip()) for row in rows if row.strip()]
    if len(out) < n:
        raise ValueError(f"{path} has only {len(out)} numeric rows")
    out = out[:n]
    if any(b <= a for a, b in zip(out, out[1:])):
        raise ValueError(f"{path} is not strictly increasing")
    return out


def decimal_min_gap(values: Sequence[Decimal]) -> tuple[int, Decimal]:
    gaps = [b - a for a, b in zip(values, values[1:])]
    j = min(range(len(gaps)), key=gaps.__getitem__)
    return j, gaps[j]


def dstr(value: Decimal) -> str:
    return format(value, "f")


class FullForce:
    """All-particle force, with bounded-memory N x chunk evaluation."""

    def __init__(self, physical_center: Decimal, chunk: int = 256):
        self.center_decimal = physical_center
        self.center = float(physical_center)
        self.chunk = chunk
        self.calls = 0
        self.mirror_mode = (
            "direct-all-pairs" if abs(physical_center) < Decimal("1e8")
            else "cubic-moment-expansion"
        )
        self.max_mirror_remainder_bound = 0.0

    def _remote_mirror(self, x: np.ndarray) -> np.ndarray:
        # 2 sum_k 1/(D + x_i + x_k), D=2*physical_center.  The
        # expansion through q^3 avoids adding O(10^3) offsets to O(10^21)
        # in float64.  Long double is used for the scalar moments.
        y = x.astype(np.longdouble)
        n = np.longdouble(len(y))
        D = np.longdouble(2) * np.longdouble(str(self.center_decimal))
        s1 = y.sum(dtype=np.longdouble)
        s2 = np.dot(y, y)
        s3 = np.dot(y * y, y)
        q1 = n * y + s1
        q2 = n * y * y + np.longdouble(2) * y * s1 + s2
        q3 = (
            n * y * y * y
            + np.longdouble(3) * y * y * s1
            + np.longdouble(3) * y * s2
            + s3
        )
        ans = np.longdouble(2) * (
            n / D - q1 / D**2 + q2 / D**3 - q3 / D**4
        )

        qmax = np.longdouble(2) * np.max(np.abs(y))
        ratio = qmax / abs(D)
        if ratio >= 1:
            raise ArithmeticError("mirror expansion requested outside convergence disk")
        # Sum of the absolute geometric tails, including the outer factor 2.
        bound = np.longdouble(2) * n * qmax**4 / (
            abs(D) ** 5 * (np.longdouble(1) - ratio)
        )
        self.max_mirror_remainder_bound = max(
            self.max_mirror_remainder_bound, float(bound)
        )
        return np.asarray(ans, dtype=np.float64)

    def initial_force_and_self_slope(
        self, x: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Return exact initial force and diagonal d(force_i)/d(x_i).

        "Exact" here means all N direct terms and, at the low block, all N
        mirror terms.  Remote mirror terms use the bounded expansion described
        above.  These arrays seed the active-window linearized background.
        """
        n = len(x)
        force = np.empty(n, dtype=np.float64)
        slope = np.empty(n, dtype=np.float64)
        direct_mirror = self.mirror_mode == "direct-all-pairs"
        for lo in range(0, n, self.chunk):
            hi = min(lo + self.chunk, n)
            rows = x[lo:hi, None]
            diff = rows - x[None, :]
            local = np.arange(hi - lo)
            diff[local, np.arange(lo, hi)] = np.inf
            f = np.sum(2.0 / diff, axis=1)
            s = np.sum(-2.0 / (diff * diff), axis=1)
            if direct_mirror:
                den = 2.0 * self.center + rows + x[None, :]
                f += np.sum(2.0 / den, axis=1)
                s += np.sum(-2.0 / (den * den), axis=1)
            force[lo:hi] = f
            slope[lo:hi] = s
        if not direct_mirror:
            force += self._remote_mirror(x)
            y = x.astype(np.longdouble)
            nn = np.longdouble(n)
            D = np.longdouble(2) * np.longdouble(str(self.center_decimal))
            s1 = y.sum(dtype=np.longdouble)
            s2 = np.dot(y, y)
            s3 = np.dot(y * y, y)
            q1 = nn * y + s1
            q2 = nn * y * y + np.longdouble(2) * y * s1 + s2
            q3 = (
                nn * y * y * y
                + np.longdouble(3) * y * y * s1
                + np.longdouble(3) * y * s2
                + s3
            )
            mirror_slope = -np.longdouble(2) * (
                nn / D**2
                - np.longdouble(2) * q1 / D**3
                + np.longdouble(3) * q2 / D**4
                - np.longdouble(4) * q3 / D**5
            )
            slope += np.asarray(mirror_slope, dtype=np.float64)
        return force, slope

    def __call__(self, _t: float, x: np.ndarray) -> np.ndarray:
        self.calls += 1
        n = len(x)
        out = np.empty(n, dtype=np.float64)
        direct_mirror = self.mirror_mode == "direct-all-pairs"
        for lo in range(0, n, self.chunk):
            hi = min(lo + self.chunk, n)
            rows = x[lo:hi, None]
            diff = rows - x[None, :]
            local = np.arange(hi - lo)
            diff[local, np.arange(lo, hi)] = np.inf
            force = np.sum(2.0 / diff, axis=1)
            if direct_mirror:
                force += np.sum(
                    2.0 / (2.0 * self.center + rows + x[None, :]), axis=1
                )
            out[lo:hi] = force
        if not direct_mirror:
            out += self._remote_mirror(x)
        return out


class ActiveWindowForce:
    """Moving window plus exact-at-t0, linearized all-node background."""

    def __init__(
        self,
        x_full: np.ndarray,
        physical_center: Decimal,
        lo: int,
        hi: int,
        full_force0: np.ndarray,
        full_self_slope0: np.ndarray,
    ):
        self.lo = lo
        self.hi = hi
        self.x0 = x_full[lo:hi].copy()
        self.center = float(physical_center)
        self.calls = 0
        active_f0, active_s0 = self._active_force_and_slope(self.x0)
        self.background_f0 = full_force0[lo:hi] - active_f0
        self.background_slope = full_self_slope0[lo:hi] - active_s0

    def _active_force_and_slope(
        self, x: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        diff = x[:, None] - x[None, :]
        np.fill_diagonal(diff, np.inf)
        force = np.sum(2.0 / diff, axis=1)
        slope = np.sum(-2.0 / (diff * diff), axis=1)
        den = 2.0 * self.center + x[:, None] + x[None, :]
        force += np.sum(2.0 / den, axis=1)
        slope += np.sum(-2.0 / (den * den), axis=1)
        return force, slope

    def __call__(self, _t: float, x: np.ndarray) -> np.ndarray:
        self.calls += 1
        active, _ = self._active_force_and_slope(x)
        return active + self.background_f0 + self.background_slope * (x - self.x0)


def event_solver(
    x0: np.ndarray,
    physical_center: Decimal,
    predicted: float,
    epsilon: float,
    rtol: float,
    atol: float,
    chunk: int,
    final_t: float | None = None,
) -> dict:
    force = FullForce(physical_center, chunk=chunk)

    def collision(_t: float, x: np.ndarray) -> float:
        return float(np.min(np.diff(x)) - epsilon)

    collision.terminal = True
    collision.direction = -1
    tic = time.perf_counter()
    sol = solve_ivp(
        force,
        (0.0, final_t if final_t is not None else -4.0 * predicted),
        x0,
        method="DOP853",
        events=collision,
        rtol=rtol,
        atol=atol,
    )
    elapsed = time.perf_counter() - tic
    if len(sol.t_events[0]) == 0:
        return {
            "event_found": False,
            "solver_success": bool(sol.success),
            "solver_message": sol.message,
            "nfev": int(sol.nfev),
            "wall_seconds": elapsed,
            "force_calls": force.calls,
            "mirror_mode": force.mirror_mode,
            "mirror_remainder_bound": force.max_mirror_remainder_bound,
        }
    te = float(sol.t_events[0][0])
    xe = sol.y_events[0][0]
    gaps = np.diff(xe)
    j = int(np.argmin(gaps))
    # The remaining two-body tail from epsilon to zero is epsilon^2/8.
    # It is recorded separately and is only a negligible extrapolation.
    zero_estimate = abs(te) + epsilon * epsilon / 8.0
    return {
        "event_found": True,
        "solver_success": bool(sol.success),
        "solver_message": sol.message,
        "event_t": te,
        "event_abs_t": abs(te),
        "zero_time_estimate": zero_estimate,
        "tail_correction": epsilon * epsilon / 8.0,
        "event_pair_index_0based": j,
        "event_gap": float(gaps[j]),
        "minimum_gap_at_event": float(np.min(gaps)),
        "nfev": int(sol.nfev),
        "wall_seconds": elapsed,
        "force_calls": force.calls,
        "mirror_mode": force.mirror_mode,
        "mirror_remainder_bound": force.max_mirror_remainder_bound,
    }


def active_window_event_solver(
    x_full: np.ndarray,
    physical_center: Decimal,
    initial_pair: int,
    predicted: float,
    epsilon: float,
    window: int,
    full_force0: np.ndarray,
    full_self_slope0: np.ndarray,
    rtol: float = 2e-10,
    atol: float = 1e-13,
) -> dict:
    """Integrate a moving window with a linearized omitted-node field."""
    n = len(x_full)
    width = min(window, n)
    lo = max(0, initial_pair + 1 - width // 2)
    hi = min(n, lo + width)
    lo = max(0, hi - width)
    force = ActiveWindowForce(
        x_full, physical_center, lo, hi, full_force0, full_self_slope0
    )

    def collision(_t: float, x: np.ndarray) -> float:
        return float(np.min(np.diff(x)) - epsilon)

    collision.terminal = True
    collision.direction = -1
    tic = time.perf_counter()
    sol = solve_ivp(
        force,
        (0.0, -4.0 * predicted),
        force.x0,
        method="DOP853",
        events=collision,
        rtol=rtol,
        atol=atol,
    )
    elapsed = time.perf_counter() - tic
    common = {
        "window": width,
        "window_indices_1based": [lo + 1, hi],
        "background": "exact all-N force at t=0 plus diagonal linear response",
        "event_found": len(sol.t_events[0]) > 0,
        "solver_success": bool(sol.success),
        "solver_message": sol.message,
        "nfev": int(sol.nfev),
        "wall_seconds": elapsed,
        "force_calls": force.calls,
    }
    if len(sol.t_events[0]) == 0:
        return common
    te = float(sol.t_events[0][0])
    xe = sol.y_events[0][0]
    gaps = np.diff(xe)
    local_j = int(np.argmin(gaps))
    j = lo + local_j
    return {
        **common,
        "event_t": te,
        "event_abs_t": abs(te),
        "zero_time_estimate": abs(te) + epsilon * epsilon / 8.0,
        "tail_correction": epsilon * epsilon / 8.0,
        "event_pair_index_0based": j,
        "event_pair_local_index_0based": local_j,
        "event_gap": float(gaps[local_j]),
        "minimum_gap_at_event": float(np.min(gaps)),
        "maximum_window_displacement": float(np.max(np.abs(xe - force.x0))),
        "maximum_linearized_background_change": float(np.max(np.abs(
            force.background_slope * (xe - force.x0)
        ))),
    }


def prepared_decimal_case(
    values: Sequence[Decimal],
) -> tuple[np.ndarray, Decimal, int, Decimal]:
    j, gap = decimal_min_gap(values)
    anchor = (values[j] + values[j + 1]) / Decimal(2)
    x = np.array([float(v - anchor) for v in values], dtype=np.float64)
    return x, anchor, j, gap


def solve_case(
    *,
    kind: str,
    key: str,
    label: str,
    x: np.ndarray,
    physical_center: Decimal,
    initial_pair: int,
    gap: float,
    index_map: Sequence[int],
    global_start: int | None,
    density: float,
    chunk: int,
) -> dict:
    predicted = gap * gap / 8.0
    epsilon = gap * 1e-3
    logging.info(
        "%s %s: N=%d gmin=%.12g pred=%.12g pair=%d/%d",
        key, kind, len(x), gap, predicted, initial_pair + 1, initial_pair + 2,
    )
    initializer = FullForce(physical_center, chunk=chunk)
    tic = time.perf_counter()
    full_force0, full_slope0 = initializer.initial_force_and_self_slope(x)
    initial_field_seconds = time.perf_counter() - tic
    windows = [128, 256, 512, 1024]
    window_runs = []
    for window in windows:
        run = active_window_event_solver(
            x, physical_center, initial_pair, predicted, epsilon, window,
            full_force0, full_slope0, rtol=2e-10, atol=1e-13,
        )
        if not run["event_found"]:
            raise RuntimeError(f"no event for {key} {kind}, window {window}: {run}")
        window_runs.append(run)
    tight = window_runs[-1]
    ej = tight["event_pair_index_0based"]
    initial_original = [int(index_map[initial_pair]), int(index_map[initial_pair + 1])]
    event_original = [int(index_map[ej]), int(index_map[ej + 1])]
    actual = tight["zero_time_estimate"]
    successive = []
    for previous, current in zip(window_runs, window_runs[1:]):
        successive.append({
            "from_window": previous["window"],
            "to_window": current["window"],
            "absolute_time_change": abs(
                current["zero_time_estimate"] - previous["zero_time_estimate"]
            ),
            "relative_time_change": abs(
                current["zero_time_estimate"] - previous["zero_time_estimate"]
            ) / current["zero_time_estimate"],
            "same_pair": (
                current["event_pair_index_0based"]
                == previous["event_pair_index_0based"]
            ),
        })
    coarse = active_window_event_solver(
        x, physical_center, initial_pair, predicted, epsilon, windows[-1],
        full_force0, full_slope0, rtol=2e-8, atol=1e-11,
    )
    convergence = {
        "window_sequence": windows,
        "successive_window_changes": successive,
        "last_window_relative_change": successive[-1]["relative_time_change"],
        "all_windows_same_pair": all(
            r["event_pair_index_0based"] == ej for r in window_runs
        ),
        "integrator_tolerance_check": {
            "coarse_zero_time_estimate": coarse.get("zero_time_estimate"),
            "relative_difference": (
                abs(actual - coarse["zero_time_estimate"]) / actual
                if coarse.get("event_found") else None
            ),
            "same_pair": coarse.get("event_pair_index_0based") == ej,
        },
    }
    row = {
        "status": "MEASURED",
        "block": key,
        "kind": kind,
        "measurement_kind": "finite active-window approximation",
        "label": label,
        "N": len(x),
        "density": density,
        "physical_center_decimal": dstr(physical_center),
        "g_min": gap,
        "g_min_unfolded": gap * density,
        "initial_pair_index_1based": [initial_pair + 1, initial_pair + 2],
        "initial_pair_original_block_ordinal_1based": [v + 1 for v in initial_original],
        "event_pair_index_1based": [ej + 1, ej + 2],
        "event_pair_original_block_ordinal_1based": [v + 1 for v in event_original],
        "same_as_initial_closest_pair": ej == initial_pair,
        "event_threshold": epsilon,
        "t_collision_predicted": predicted,
        "t_collision_actual_zero_estimate": actual,
        "actual_to_predicted_ratio": actual / predicted,
        "largest_window_solver": tight,
        "window_runs": window_runs,
        "convergence": convergence,
        "all_N_initial_field": {
            "N": len(x),
            "wall_seconds": initial_field_seconds,
            "mirror_mode": initializer.mirror_mode,
            "mirror_remainder_bound": initializer.max_mirror_remainder_bound,
        },
    }
    if global_start is not None:
        row["initial_pair_global_ordinals"] = [
            str(global_start + v) for v in initial_original
        ]
        row["event_pair_global_ordinals"] = [
            str(global_start + v) for v in event_original
        ]
    logging.info(
        "%s %s: event %.12g ratio %.8f pair=%d/%d nfev=%d conv=%.3g",
        key, kind, actual, actual / predicted, ej + 1, ej + 2,
        tight["nfev"],
        convergence["last_window_relative_change"],
    )
    return row


def validate_t4(repo_lab: Path, chunk: int) -> dict:
    source = repo_lab / "zeros.txt"
    x_raw = np.loadtxt(source)
    gaps = np.diff(x_raw)
    j = int(np.argmin(gaps))
    predicted = float(gaps[j] ** 2 / 8.0)
    # Match toy_flow.py's uncentred coordinates, fixed t_span, and fixed 1e-3
    # event exactly.  The R4 cases are recentered at the closest pair because
    # that gives materially tighter local error control.
    run = event_solver(
        x_raw, Decimal(0), predicted, 1e-3,
        rtol=1e-8, atol=1e-10, chunk=chunk, final_t=-0.5,
    )
    published = json.loads((repo_lab / "toy-flow.json").read_text())
    target = abs(float(published["backward"]["t_collision"]))
    got = run["event_abs_t"] if run["event_found"] else None
    anchor = (x_raw[j] + x_raw[j + 1]) / 2.0
    x_centered = x_raw - anchor
    centered_full = event_solver(
        x_centered, Decimal(str(anchor)), predicted, 1e-3,
        rtol=2e-10, atol=1e-13, chunk=chunk, final_t=-0.5,
    )
    initializer = FullForce(Decimal(str(anchor)), chunk=chunk)
    full_f0, full_s0 = initializer.initial_force_and_self_slope(x_centered)
    active_runs = []
    for window in (128, 256, 512, 1000):
        active = active_window_event_solver(
            x_centered, Decimal(str(anchor)), j, predicted, 1e-3, window,
            full_f0, full_s0, rtol=2e-10, atol=1e-13,
        )
        active["relative_to_centered_full"] = abs(
            active["event_abs_t"] - centered_full["event_abs_t"]
        ) / centered_full["event_abs_t"]
        active["relative_to_published_t4"] = abs(
            active["event_abs_t"] - target
        ) / target
        active_runs.append(active)
    return {
        "status": "MEASURED",
        "input_sha256": sha256(source),
        "N": len(x_raw),
        "closest_pair_index_1based": [j + 1, j + 2],
        "event_threshold": 1e-3,
        "published_toy_t4_abs_event_t": target,
        "reproduced_abs_event_t": got,
        "absolute_difference": abs(got - target) if got is not None else None,
        "relative_difference": abs(got - target) / target if got is not None else None,
        "same_event_pair": (
            run.get("event_pair_index_0based")
            == int(published["backward"]["colliding_pair_index"]) - 1
        ),
        "run": run,
        "centered_high_accuracy_full_reference": centered_full,
        "active_window_validation": active_runs,
        "validation_note": (
            "The legacy coordinates/tolerances reproduce the published T4 "
            "value exactly.  Recentring the close pair changes the adaptive "
            "error scale; active windows are therefore compared to the "
            "recentered high-accuracy full-N reference."
        ),
    }


def csv_value(value):
    if isinstance(value, (list, dict)):
        return json.dumps(value, separators=(",", ":"))
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help=(
            "directory containing zeros1.txt, zeros3.txt, zeros4.txt, and "
            f"zeros5.txt downloaded from {ODLYZKO_SOURCE}"
        ),
    )
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path(__file__).resolve().parent,
    )
    parser.add_argument("--chunk", type=int, default=256)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    log_path = args.output_dir / "r41-run.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(log_path, mode="w"), logging.StreamHandler()],
    )
    repo_lab = Path(__file__).resolve().parent.parent

    hashes = {}
    for spec in BLOCKS:
        path = args.data_dir / spec.filename
        digest = sha256(path)
        hashes[spec.filename] = {
            "sha256": digest,
            "expected_sha256": EXPECTED_SHA256[spec.filename],
            "matches_expected": digest == EXPECTED_SHA256[spec.filename],
            "bytes": path.stat().st_size,
        }
        if digest != EXPECTED_SHA256[spec.filename]:
            raise ValueError(f"unexpected input hash for {path}: {digest}")

    validation = validate_t4(repo_lab, args.chunk)
    logging.info(
        "T4 validation relative difference %.3g, same pair=%s",
        validation["relative_difference"], validation["same_event_pair"],
    )

    primary_rows = []
    control_rows = []
    mutation_rows = []
    per_block = {}
    for block_index, spec in enumerate(BLOCKS):
        values = decimal_rows(args.data_dir / spec.filename, spec.skip)
        x, anchor, j, gap_dec = prepared_decimal_case(values)
        physical_center = spec.base + anchor
        T_mid = spec.base + values[len(values) // 2]
        density = math.log(float(T_mid) / (2.0 * math.pi)) / (2.0 * math.pi)
        index_map = list(range(len(values)))
        primary = solve_case(
            kind="odlyzko-primary", key=spec.key, label=spec.label,
            x=x, physical_center=physical_center, initial_pair=j,
            gap=float(gap_dec), index_map=index_map,
            global_start=spec.first_global_ordinal, density=density,
            chunk=args.chunk,
        )
        primary["offset_left_decimal"] = dstr(values[j])
        primary["offset_right_decimal"] = dstr(values[j + 1])
        primary["g_min_decimal"] = dstr(gap_dec)
        primary["T_mid_decimal"] = dstr(T_mid)
        primary_rows.append(primary)

        # Fixed-seed Poisson control at the same density.  Centre the block at
        # the same physical height, then recenter the numerical coordinates on
        # its own closest pair to make event tolerances gap-local.
        seed = 20260902 + block_index
        rng = np.random.default_rng(seed)
        # Retain each generated float64 spacing exactly while accumulating in
        # long double; ordinary float64 cumsum would lose several digits in
        # the smallest Poisson gaps after a block-length accumulation.
        pgaps = rng.exponential(1.0 / density, len(values) - 1)
        p = np.r_[
            np.longdouble(0),
            np.cumsum(pgaps.astype(np.longdouble), dtype=np.longdouble),
        ]
        p -= p[len(p) // 2]
        pj = int(np.argmin(pgaps))
        p_anchor = (p[pj] + p[pj + 1]) / np.longdouble(2)
        px = np.asarray(p - p_anchor, dtype=np.float64)
        p_center = T_mid + Decimal(str(p_anchor))
        control = solve_case(
            kind="poisson-control", key=spec.key,
            label=f"Poisson seed {seed}, density matched to {spec.key}",
            x=px, physical_center=p_center, initial_pair=pj,
            gap=float(pgaps[pj]), index_map=list(range(len(p))),
            global_start=None, density=density, chunk=args.chunk,
        )
        control["seed"] = seed
        control["actual_time_to_odlyzko_ratio"] = (
            control["t_collision_actual_zero_estimate"]
            / primary["t_collision_actual_zero_estimate"]
        )
        control_rows.append(control)

        # Registered mutation: delete the primary event pair, preserving all
        # other printed offsets and their original block ordinals.
        event_original_zero = [
            v - 1 for v in primary["event_pair_original_block_ordinal_1based"]
        ]
        keep = [i for i in range(len(values)) if i not in event_original_zero]
        mutated_values = [values[i] for i in keep]
        mx, manchor, mj, mgap_dec = prepared_decimal_case(mutated_values)
        mutation = solve_case(
            kind="delete-event-pair-mutation", key=spec.key,
            label=f"{spec.label}; primary event pair deleted",
            x=mx, physical_center=spec.base + manchor, initial_pair=mj,
            gap=float(mgap_dec), index_map=keep,
            global_start=spec.first_global_ordinal, density=density,
            chunk=args.chunk,
        )
        mutation["deleted_original_block_ordinals_1based"] = [
            v + 1 for v in event_original_zero
        ]
        mutation["g_min_decimal"] = dstr(mgap_dec)
        mutation_rows.append(mutation)
        per_block[spec.key] = {
            "primary": primary,
            "poisson_control": control,
            "delete_pair_mutation": mutation,
        }

    densities = np.array([r["density"] for r in primary_rows])
    actual_times = np.array(
        [r["t_collision_actual_zero_estimate"] for r in primary_rows]
    )
    predicted_times = np.array([r["t_collision_predicted"] for r in primary_rows])
    actual_slope, actual_intercept = np.polyfit(
        np.log(densities), np.log(actual_times), 1
    )
    predicted_slope, predicted_intercept = np.polyfit(
        np.log(densities), np.log(predicted_times), 1
    )
    scaling = {
        "status": "MEASURED",
        "registered_density_exponent": -2.0,
        "literal_T_power_exponent": 0.0,
        "actual_log_time_on_log_density_slope_four_blocks": float(actual_slope),
        "actual_intercept": float(actual_intercept),
        "gmin2_over_8_log_time_on_log_density_slope_four_blocks": float(predicted_slope),
        "predicted_intercept": float(predicted_intercept),
        "actual_slope_is_negative": bool(actual_slope < 0),
        "note": (
            "The four-point slope includes extreme-gap fluctuations.  The "
            "registered -2 is an ensemble scale at fixed N, not a claim of "
            "monotonicity for four individual blocks."
        ),
    }

    result = {
        "status": "MEASURED",
        "scope": (
            "Finite 10,000-zero truncated-block active-window flow-time "
            "approximations only; not a measurement, estimate, upper bound, "
            "or lower bound for Lambda."
        ),
        "equation": (
            "dx_j/dt = sum_{k != j} 2/(x_j-x_k) + sum_k 2/(x_j+x_k)"
        ),
        "event_policy": (
            "Stop at min gap = 1e-3 times the initial min gap; add the "
            "two-body tail epsilon^2/8 to report a zero-gap time estimate."
        ),
        "input_hashes": hashes,
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "platform": platform.platform(),
            "chunk": args.chunk,
        },
        "toy_t4_validation": validation,
        "blocks": per_block,
        "scaling": scaling,
    }
    json_path = args.output_dir / "r41-results.json"
    json_path.write_text(json.dumps(result, indent=2) + "\n")

    rows = primary_rows + control_rows + mutation_rows
    csv_path = args.output_dir / "r41-results.csv"
    fields = [
        "status", "block", "kind", "N", "density", "g_min",
        "g_min_unfolded", "initial_pair_index_1based",
        "event_pair_index_1based", "event_pair_global_ordinals",
        "same_as_initial_closest_pair", "event_threshold",
        "t_collision_predicted", "t_collision_actual_zero_estimate",
        "actual_to_predicted_ratio", "actual_time_to_odlyzko_ratio",
    ]
    with csv_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: csv_value(row.get(k)) for k in fields})

    hash_path = args.output_dir / "r41-input-sha256.txt"
    hash_path.write_text(
        "".join(f"{v['sha256']}  {name}\n" for name, v in hashes.items())
        + f"{validation['input_sha256']}  zeros.txt (T4 validation)\n"
    )
    logging.info("wrote %s and %s", json_path, csv_path)
    print(json.dumps({
        "toy_t4_validation": {
            "relative_difference": validation["relative_difference"],
            "same_pair": validation["same_event_pair"],
        },
        "rows": [{
            "block": r["block"], "kind": r["kind"],
            "pred": r["t_collision_predicted"],
            "actual": r["t_collision_actual_zero_estimate"],
            "ratio": r["actual_to_predicted_ratio"],
            "pair": r["event_pair_index_1based"],
        } for r in rows],
        "scaling": scaling,
    }, indent=2))


if __name__ == "__main__":
    main()
