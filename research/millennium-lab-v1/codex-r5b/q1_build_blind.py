#!/usr/bin/env python3
"""Build one Round-5b Q1 prolate spectrum without reference ordinates.

The parameter grid, precision, mode cutoff, root count, and continuation rule
are frozen in PREDICTIONS-codex-r5b.md.  This file deliberately contains no
scoring or reference-spectrum code.  The separate q1_score.py process is the
only consumer of reference ordinates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import mpmath as mp


HERE = Path(__file__).resolve().parent
R5 = HERE.parent / "codex-r5"
sys.path.insert(0, str(R5))

import weil_core as core  # noqa: E402
from run_prolate_exact_bridge import exact_e_projection  # noqa: E402
from run_prolate_only_control import high_precision_candidate  # noqa: E402
from run_prolate_only_raw_control import (  # noqa: E402
    rational_value_and_derivative,
    track_homotopy,
)


ALLOWED_X = (9, 13, 14)
N_MAX = 120
WORK_DPS = 200
LEGENDRE_CUTOFF = 200
ROOT_COUNT = 60
GUARD_COUNT = ROOT_COUNT + 1
PRIMARY_HOMOTOPY_STEPS = 8


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--x", type=int, choices=ALLOWED_X, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_audit() -> dict[str, object]:
    inspected = [
        Path(__file__),
        R5 / "weil_core.py",
        R5 / "run_prolate_exact_bridge.py",
        R5 / "run_prolate_only_control.py",
        R5 / "run_prolate_only_raw_control.py",
    ]
    banned = [
        "zeta" + "zero",
        "zeros" + ".txt",
        "14.134" + "725",
        "reference" + "_roots",
    ]
    findings: list[dict[str, str]] = []
    for path in inspected:
        source = path.read_text(encoding="utf-8").lower()
        for token in banned:
            if token.lower() in source:
                findings.append({"file": path.name, "token": token})
    return {
        "inspected": [str(path.relative_to(HERE.parent)) for path in inspected],
        "banned_tokens": banned,
        "findings": findings,
        "passed": not findings,
    }


def mp_column(values: list[mp.mpf | mp.mpc]) -> mp.matrix:
    result = mp.matrix(len(values), 1)
    for index, value in enumerate(values):
        result[index] = value
    return result


def serialize_real(value: mp.mpf, digits: int = 170) -> str:
    return mp.nstr(value, digits)


def serialize_complex(value: mp.mpc, digits: int = 170) -> dict[str, str]:
    return {
        "real": mp.nstr(mp.re(value), digits),
        "imaginary": mp.nstr(mp.im(value), digits),
    }


def main() -> None:
    args = parse_args()
    audit = source_audit()
    if not audit["passed"]:
        raise RuntimeError(f"construction source audit failed: {audit['findings']}")

    started = time.perf_counter()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with mp.workdps(WORK_DPS):
        x = args.x
        length = mp.log(x)
        lattice = [
            2 * mp.pi * n / length for n in range(-N_MAX, N_MAX + 1)
        ]

        print(f"x={x}: solving degree-{LEGENDRE_CUTOFF} prolate modes", flush=True)
        candidate = high_precision_candidate(x, LEGENDRE_CUTOFF)
        print(f"x={x}: exact analytic projection of E(h)", flush=True)
        projection = exact_e_projection(candidate, N_MAX)
        raw_coefficients = projection["full"]
        even_coefficients = projection["even_projected"]["full"]
        raw_column = mp_column(raw_coefficients)
        even_column = mp_column(even_coefficients)

        print(f"x={x}: enumerating even roots at 32/64 subdivisions", flush=True)
        even_32 = core.enumerate_positive_roots_mp(
            even_column, length, GUARD_COUNT, 32
        )
        even_64 = core.enumerate_positive_roots_mp(
            even_column, length, GUARD_COUNT, 64
        )

        print(f"x={x}: continuing raw roots at 4/8/16 steps", flush=True)
        raw_4, iterations_4 = track_homotopy(
            even_coefficients, raw_coefficients, even_32, lattice, 4
        )
        raw_8, iterations_8 = track_homotopy(
            even_coefficients, raw_coefficients, even_32, lattice, 8
        )
        raw_16, iterations_16 = track_homotopy(
            even_coefficients, raw_coefficients, even_32, lattice, 16
        )

        even_differences = [abs(a - b) for a, b in zip(even_32, even_64)]
        raw_4_differences = [abs(a - b) for a, b in zip(raw_8, raw_4)]
        raw_16_differences = [abs(a - b) for a, b in zip(raw_8, raw_16)]

        even_transform_residuals = [
            abs(core.transform_mp(root, even_column, length)) for root in even_32
        ]
        raw_transform_residuals: list[mp.mpf] = []
        raw_rational_residuals: list[mp.mpf] = []
        raw_relative_rational_residuals: list[mp.mpf] = []
        raw_derivatives: list[mp.mpf] = []
        for root in raw_8:
            transform_residual = abs(core.transform_mp(root, raw_column, length))
            value, derivative, absolute_sum = rational_value_and_derivative(
                root, raw_coefficients, lattice
            )
            raw_transform_residuals.append(transform_residual)
            raw_rational_residuals.append(abs(value))
            raw_relative_rational_residuals.append(abs(value) / absolute_sum)
            raw_derivatives.append(abs(derivative))

        raw_real_ordered = all(
            mp.re(second) > mp.re(first)
            for first, second in zip(raw_8[:-1], raw_8[1:])
        )
        diagnostics_pass = bool(
            max(even_differences) < mp.mpf("1e-150")
            and max(raw_4_differences) < mp.mpf("1e-140")
            and max(raw_16_differences) < mp.mpf("1e-140")
            and max(raw_relative_rational_residuals) < mp.mpf("1e-150")
            and raw_real_ordered
        )


        primary_rows = []
        for ordinal in range(ROOT_COUNT):
            primary_rows.append(
                {
                    "ordinal": ordinal + 1,
                    "even_root": serialize_real(even_32[ordinal]),
                    "raw_root": serialize_complex(raw_8[ordinal]),
                    "even_32_vs_64": serialize_real(
                        even_differences[ordinal], 60
                    ),
                    "raw_8_vs_4": serialize_real(
                        raw_4_differences[ordinal], 60
                    ),
                    "raw_8_vs_16": serialize_real(
                        raw_16_differences[ordinal], 60
                    ),
                    "even_transform_residual": serialize_real(
                        even_transform_residuals[ordinal], 60
                    ),
                    "raw_transform_residual": serialize_real(
                        raw_transform_residuals[ordinal], 60
                    ),
                    "raw_relative_rational_residual": serialize_real(
                        raw_relative_rational_residuals[ordinal], 60
                    ),
                }
            )

        dependencies = [
            Path(__file__),
            R5 / "weil_core.py",
            R5 / "run_prolate_exact_bridge.py",
            R5 / "run_prolate_only_control.py",
            R5 / "run_prolate_only_raw_control.py",
        ]
        payload = {
            "schema": "codex-r5b-q1-blind-v1",
            "status": "MEASURED" if diagnostics_pass else "UNVERIFIED",
            "scope": "finite degree-200, N=120 prolate construction",
            "parameters": {
                "x": x,
                "N": N_MAX,
                "working_decimal_digits": WORK_DPS,
                "legendre_cutoff": LEGENDRE_CUTOFF,
                "retained_root_count": ROOT_COUNT,
                "guard_root_count": 1,
                "primary_even_subdivisions": 32,
                "even_mutation_subdivisions": 64,
                "primary_raw_homotopy_steps": PRIMARY_HOMOTOPY_STEPS,
                "raw_homotopy_checks": [4, 16],
            },
            "construction": {
                "candidate": "normalized zero-integral span(h_0,h_4)",
                "projection": "exact Legendre-to-power antiderivative projection of E(h)",
                "raw_convention": "normalized complex coefficients",
                "even_convention": "orthogonal inversion-even projection before normalization",
                "raw_root_label": (
                    "8-step coefficient homotopy from the corresponding ordered "
                    "even root; labels retained without resorting"
                ),
                "raw_root_label_status": "UNVERIFIED",
            },
            "roots": primary_rows,
            "guards": {
                "even_root_61": serialize_real(even_32[-1]),
                "raw_root_61": serialize_complex(raw_8[-1]),
            },
            "diagnostics": {
                "all_checks_passed": diagnostics_pass,
                "raw_roots_strictly_ordered_by_real_part": raw_real_ordered,
                "maximum_even_32_vs_64": serialize_real(
                    max(even_differences), 80
                ),
                "maximum_raw_8_vs_4": serialize_real(
                    max(raw_4_differences), 80
                ),
                "maximum_raw_8_vs_16": serialize_real(
                    max(raw_16_differences), 80
                ),
                "maximum_even_transform_residual": serialize_real(
                    max(even_transform_residuals), 80
                ),
                "maximum_raw_transform_residual": serialize_real(
                    max(raw_transform_residuals), 80
                ),
                "maximum_raw_rational_residual": serialize_real(
                    max(raw_rational_residuals), 80
                ),
                "maximum_raw_relative_rational_residual": serialize_real(
                    max(raw_relative_rational_residuals), 80
                ),
                "minimum_raw_rational_derivative": serialize_real(
                    min(raw_derivatives), 80
                ),
                "maximum_absolute_raw_imaginary_part": serialize_real(
                    max(abs(mp.im(root)) for root in raw_8), 80
                ),
                "maximum_newton_iterations": {
                    "4_steps": iterations_4,
                    "8_steps": iterations_8,
                    "16_steps": iterations_16,
                },
                "projection_inversion_odd_norm": serialize_real(
                    projection["inversion_odd_norm"], 100
                ),
                "zero_integral_residual": serialize_real(
                    candidate["zero_integral_residual"], 100
                ),
            },
            "source_audit": audit,
            "source_sha256": {
                str(path.relative_to(HERE.parent)): sha256(path)
                for path in dependencies
            },
            "target_data_present": False,
            "scoring_present": False,
            "elapsed_seconds": time.perf_counter() - started,
        }

    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "status": payload["status"],
                "x": args.x,
                "root_count": len(payload["roots"]),
                "all_checks_passed": payload["diagnostics"]["all_checks_passed"],
                "seconds": payload["elapsed_seconds"],
            },
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
