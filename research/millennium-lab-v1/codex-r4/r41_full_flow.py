#!/usr/bin/env python3
"""R4.1 all-node finite-block de Bruijn--Newman flow.

Unlike ``r41_truncated_flow.py``'s active-window diagnostic, this runner
dynamically evolves every retained node and places the collision event on the
minimum of every consecutive gap.  PyTorch is used only as a fast float64 CPU
backend for the dense Cauchy sums; SciPy controls the DOP853 integration.

The three remote blocks keep their large decimal bases separate from their
printed offsets.  Their mirror field is evaluated with a cubic moment
expansion whose first omitted geometric tail is bounded on every force call.
This remains a finite 10,000-zero system, not the infinite heat-flow zero set.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import math
import platform
import time
from decimal import Decimal
from pathlib import Path
from typing import Sequence

import numpy as np
import scipy
from scipy.integrate import solve_ivp
import torch

import r41_truncated_flow as active


HERE = Path(__file__).resolve().parent
LAB = HERE.parent


class TorchFullForce:
    """Dense all-node force with bounded-memory float64 CPU chunks."""

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
        value = np.longdouble(2) * (
            n / D - q1 / D**2 + q2 / D**3 - q3 / D**4
        )
        qmax = np.longdouble(2) * np.max(np.abs(y))
        ratio = qmax / abs(D)
        if ratio >= 1:
            raise ArithmeticError("remote mirror expansion outside convergence disk")
        bound = np.longdouble(2) * n * qmax**4 / (
            abs(D) ** 5 * (np.longdouble(1) - ratio)
        )
        self.max_mirror_remainder_bound = max(
            self.max_mirror_remainder_bound, float(bound)
        )
        return np.asarray(value, dtype=np.float64)

    def __call__(self, _t: float, x: np.ndarray) -> np.ndarray:
        self.calls += 1
        n = len(x)
        tx = torch.from_numpy(x)
        out = torch.empty(n, dtype=torch.float64)
        direct_mirror = self.mirror_mode == "direct-all-pairs"
        with torch.no_grad():
            for lo in range(0, n, self.chunk):
                hi = min(lo + self.chunk, n)
                rows = tx[lo:hi, None]
                diff = rows - tx[None, :]
                local = torch.arange(hi - lo)
                diff[local, torch.arange(lo, hi)] = math.inf
                force = torch.sum(2.0 / diff, dim=1)
                if direct_mirror:
                    force += torch.sum(
                        2.0 / (2.0 * self.center + rows + tx[None, :]), dim=1
                    )
                out[lo:hi] = force
        answer = out.numpy()
        if not direct_mirror:
            answer += self._remote_mirror(x)
        return answer


def full_event(
    x0: np.ndarray,
    physical_center: Decimal,
    predicted: float,
    *,
    threshold_fraction: float,
    rtol: float,
    atol: float,
    chunk: int,
    final_multiplier: float = 4.0,
) -> dict:
    """Integrate all nodes until the global minimum gap reaches threshold."""
    force = TorchFullForce(physical_center, chunk)
    initial_gap = float(np.min(np.diff(x0)))
    epsilon = threshold_fraction * initial_gap

    def collision(_t: float, x: np.ndarray) -> float:
        return float(np.min(np.diff(x)) - epsilon)

    collision.terminal = True
    collision.direction = -1
    started = time.perf_counter()
    sol = solve_ivp(
        force,
        (0.0, -final_multiplier * predicted),
        x0,
        method="DOP853",
        events=collision,
        rtol=rtol,
        atol=atol,
    )
    elapsed = time.perf_counter() - started
    common = {
        "all_nodes_dynamically_evolved": True,
        "global_minimum_gap_event": True,
        "N": len(x0),
        "event_found": len(sol.t_events[0]) > 0,
        "solver_success": bool(sol.success),
        "solver_message": sol.message,
        "nfev": int(sol.nfev),
        "force_calls": force.calls,
        "wall_seconds": elapsed,
        "rtol": rtol,
        "atol": atol,
        "event_threshold": epsilon,
        "event_threshold_fraction_of_initial_minimum": threshold_fraction,
        "mirror_mode": force.mirror_mode,
        "mirror_remainder_bound": force.max_mirror_remainder_bound,
    }
    if len(sol.t_events[0]) == 0:
        return common
    event_t = float(sol.t_events[0][0])
    event_x = sol.y_events[0][0]
    event_gaps = np.diff(event_x)
    pair = int(np.argmin(event_gaps))
    # For an isolated colliding pair dg/dt=4/g, so the final threshold-to-zero
    # interval is epsilon^2/8.  External terms are regular at the collision;
    # the correction is 1e-4 of g_min^2/8 at the chosen 1% threshold.
    tail = epsilon * epsilon / 8.0
    return {
        **common,
        "event_t": event_t,
        "event_abs_t": abs(event_t),
        "zero_time_estimate": abs(event_t) + tail,
        "two_body_tail_correction": tail,
        "tail_fraction_of_two_body_prediction": tail / predicted,
        "event_pair_index_0based": pair,
        "event_pair_index_1based": [pair + 1, pair + 2],
        "event_gap": float(event_gaps[pair]),
        "minimum_gap_at_event": float(np.min(event_gaps)),
        "maximum_displacement": float(np.max(np.abs(event_x - x0))),
    }


def solve_case(
    *,
    block: active.BlockSpec,
    kind: str,
    x: np.ndarray,
    physical_center: Decimal,
    pair: int,
    gap: float,
    index_map: Sequence[int],
    density: float,
    chunk: int,
    active_reference: dict | None,
) -> dict:
    predicted = gap * gap / 8.0
    logging.info(
        "%s %s full-N start N=%d pair=%d/%d g=%.12g pred=%.12g",
        block.key, kind, len(x), pair + 1, pair + 2, gap, predicted,
    )
    run = full_event(
        x,
        physical_center,
        predicted,
        threshold_fraction=0.01,
        rtol=2e-9,
        atol=2e-12,
        chunk=chunk,
    )
    if not run["event_found"]:
        raise RuntimeError(f"no full-N event for {block.key} {kind}: {run}")
    event_pair = run["event_pair_index_0based"]
    original_pair = [int(index_map[event_pair]), int(index_map[event_pair + 1])]
    initial_original = [int(index_map[pair]), int(index_map[pair + 1])]
    actual = run["zero_time_estimate"]
    row = {
        "status": "MEASURED",
        "measurement_kind": "all-retained-node finite-block flow",
        "block": block.key,
        "kind": kind,
        "N": len(x),
        "density": density,
        "physical_center_decimal": active.dstr(physical_center),
        "g_min": gap,
        "g_min_unfolded": gap * density,
        "initial_pair_index_1based": [pair + 1, pair + 2],
        "event_pair_index_1based": [event_pair + 1, event_pair + 2],
        "initial_pair_original_block_ordinal_1based": [v + 1 for v in initial_original],
        "event_pair_original_block_ordinal_1based": [v + 1 for v in original_pair],
        "same_as_initial_closest_pair": event_pair == pair,
        "t_collision_predicted": predicted,
        "t_collision_full_flow_zero_estimate": actual,
        "actual_to_predicted_ratio": actual / predicted,
        "solver": run,
    }
    if kind != "poisson-control":
        row["initial_pair_global_ordinals"] = [
            str(block.first_global_ordinal + v) for v in initial_original
        ]
        row["event_pair_global_ordinals"] = [
            str(block.first_global_ordinal + v) for v in original_pair
        ]
    if active_reference is not None:
        surrogate = active_reference["t_collision_actual_zero_estimate"]
        row["active_window_crosscheck"] = {
            "surrogate_zero_time_estimate": surrogate,
            "relative_difference_from_full_flow": abs(surrogate - actual) / actual,
            "same_pair": active_reference["event_pair_index_1based"]
            == row["event_pair_index_1based"],
        }
    logging.info(
        "%s %s full-N event %.12g ratio %.8f pair=%d/%d nfev=%d wall=%.1fs",
        block.key, kind, actual, actual / predicted, event_pair + 1,
        event_pair + 2, run["nfev"], run["wall_seconds"],
    )
    return row


def load_active_results() -> dict:
    path = HERE / "r41-results.json"
    return json.loads(path.read_text()) if path.exists() else {"blocks": {}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=active.DEFAULT_DATA_DIR,
        help=(
            "directory containing zeros1.txt, zeros3.txt, zeros4.txt, and "
            f"zeros5.txt downloaded from {active.ODLYZKO_SOURCE}"
        ),
    )
    parser.add_argument("--chunk", type=int, default=256)
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()
    torch.set_num_threads(args.threads)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(HERE / "r41-full-run.log", mode="w"),
            logging.StreamHandler(),
        ],
    )
    surrogate = load_active_results()
    started = time.perf_counter()

    # Validate the exact source files in this runner too.  The active-window
    # artifact is only a numerical cross-check; it is not trusted for input
    # provenance.
    input_hashes = {}
    for block in active.BLOCKS:
        path = args.data_dir / block.filename
        digest = active.sha256(path)
        expected = active.EXPECTED_SHA256[block.filename]
        input_hashes[block.filename] = {
            "sha256": digest,
            "expected_sha256": expected,
            "matches_expected": digest == expected,
            "bytes": path.stat().st_size,
        }
        if digest != expected:
            raise ValueError(f"unexpected input hash for {path}: {digest}")

    # Exact reproduction control on Fable's full N=1000 T4 calculation.
    z = np.loadtxt(LAB / "zeros.txt")
    zg = np.diff(z)
    zj = int(np.argmin(zg))
    zpred = float(zg[zj] ** 2 / 8.0)
    t4 = full_event(
        z, Decimal(0), zpred, threshold_fraction=1e-3 / float(zg[zj]),
        rtol=1e-8, atol=1e-10, chunk=args.chunk, final_multiplier=160.0,
    )
    published_t4 = json.loads((LAB / "toy-flow.json").read_text())
    t4["published_event_abs_t"] = abs(published_t4["backward"]["t_collision"])
    t4["published_pair_index_1based"] = published_t4["backward"]["colliding_pair_index"]
    t4["event_time_absolute_difference"] = abs(
        t4["event_abs_t"] - t4["published_event_abs_t"]
    )
    t4["same_pair_as_published"] = (
        t4["event_pair_index_1based"][0] == t4["published_pair_index_1based"]
    )

    blocks = {}
    for block_index, block in enumerate(active.BLOCKS):
        values = active.decimal_rows(args.data_dir / block.filename, block.skip)
        x, anchor, pair, gap_dec = active.prepared_decimal_case(values)
        center = block.base + anchor
        t_mid = block.base + values[len(values) // 2]
        density = math.log(float(t_mid) / (2 * math.pi)) / (2 * math.pi)
        active_block = surrogate.get("blocks", {}).get(block.key, {})
        primary = solve_case(
            block=block, kind="odlyzko-primary", x=x,
            physical_center=center, pair=pair, gap=float(gap_dec),
            index_map=list(range(len(values))), density=density,
            chunk=args.chunk, active_reference=active_block.get("primary"),
        )
        primary["g_min_decimal"] = active.dstr(gap_dec)
        primary["T_mid_decimal"] = active.dstr(t_mid)

        seed = 20260902 + block_index
        rng = np.random.default_rng(seed)
        pgaps = rng.exponential(1.0 / density, len(values) - 1)
        p = np.r_[
            np.longdouble(0),
            np.cumsum(pgaps.astype(np.longdouble), dtype=np.longdouble),
        ]
        p -= p[len(p) // 2]
        pj = int(np.argmin(pgaps))
        panchor = (p[pj] + p[pj + 1]) / np.longdouble(2)
        px = np.asarray(p - panchor, dtype=np.float64)
        control = solve_case(
            block=block, kind="poisson-control", x=px,
            physical_center=t_mid + Decimal(str(panchor)), pair=pj,
            gap=float(pgaps[pj]), index_map=list(range(len(p))), density=density,
            chunk=args.chunk, active_reference=active_block.get("poisson_control"),
        )
        control["seed"] = seed
        control["actual_time_to_odlyzko_ratio"] = (
            control["t_collision_full_flow_zero_estimate"]
            / primary["t_collision_full_flow_zero_estimate"]
        )

        deleted = [v - 1 for v in primary["event_pair_original_block_ordinal_1based"]]
        keep = [i for i in range(len(values)) if i not in deleted]
        mvalues = [values[i] for i in keep]
        mx, manchor, mj, mgap_dec = active.prepared_decimal_case(mvalues)
        mutation = solve_case(
            block=block, kind="delete-event-pair-mutation", x=mx,
            physical_center=block.base + manchor, pair=mj,
            gap=float(mgap_dec), index_map=keep, density=density,
            chunk=args.chunk, active_reference=active_block.get("delete_pair_mutation"),
        )
        mutation["deleted_original_block_ordinals_1based"] = [v + 1 for v in deleted]
        mutation["g_min_decimal"] = active.dstr(mgap_dec)
        blocks[block.key] = {
            "primary": primary,
            "poisson_control": control,
            "delete_pair_mutation": mutation,
        }

    primary_rows = [blocks[k]["primary"] for k in "ABCD"]
    densities = np.array([row["density"] for row in primary_rows])
    times = np.array([row["t_collision_full_flow_zero_estimate"] for row in primary_rows])
    slope, intercept = np.polyfit(np.log(densities), np.log(times), 1)
    result = {
        "schema": "codex-r4-r41-full-v1",
        "status": "MEASURED",
        "scope": (
            "All retained nodes dynamically evolved in each finite block; "
            "omitted exterior zeros make these neither measurements nor bounds for Lambda."
        ),
        "equation": "dx_j/dt=sum_{k!=j}2/(x_j-x_k)+sum_k2/(x_j+x_k)",
        "prediction_commit": "c6f9358",
        "input_hashes": input_hashes,
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "torch": torch.__version__,
            "torch_threads": torch.get_num_threads(),
            "platform": platform.platform(),
            "chunk": args.chunk,
        },
        "toy_t4_full_node_reproduction": t4,
        "blocks": blocks,
        "scaling": {
            "status": "MEASURED",
            "registered_ensemble_density_exponent": -2.0,
            "literal_T_power_exponent": 0.0,
            "four_block_log_time_on_log_density_slope": float(slope),
            "four_block_intercept": float(intercept),
            "slope_is_negative": bool(slope < 0),
            "note": "Four realized extreme gaps do not measure the ensemble exponent.",
        },
        "elapsed_seconds": time.perf_counter() - started,
    }
    (HERE / "r41-full-results.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    with (HERE / "r41-full-results.csv").open("w", newline="") as handle:
        fields = [
            "block", "kind", "N", "g_min", "t_collision_predicted",
            "t_collision_full_flow_zero_estimate", "actual_to_predicted_ratio",
            "event_pair_index_1based", "same_as_initial_closest_pair",
            "nfev", "wall_seconds", "active_window_relative_difference",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for key in "ABCD":
            for kind in ("primary", "poisson_control", "delete_pair_mutation"):
                row = blocks[key][kind]
                writer.writerow({
                    "block": key,
                    "kind": row["kind"],
                    "N": row["N"],
                    "g_min": row["g_min"],
                    "t_collision_predicted": row["t_collision_predicted"],
                    "t_collision_full_flow_zero_estimate": row["t_collision_full_flow_zero_estimate"],
                    "actual_to_predicted_ratio": row["actual_to_predicted_ratio"],
                    "event_pair_index_1based": json.dumps(row["event_pair_index_1based"]),
                    "same_as_initial_closest_pair": row["same_as_initial_closest_pair"],
                    "nfev": row["solver"]["nfev"],
                    "wall_seconds": row["solver"]["wall_seconds"],
                    "active_window_relative_difference": row.get("active_window_crosscheck", {}).get("relative_difference_from_full_flow"),
                })
    logging.info("all full-N cases complete in %.1fs", result["elapsed_seconds"])


if __name__ == "__main__":
    main()
