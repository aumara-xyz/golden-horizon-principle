#!/usr/bin/env python3
"""Score the frozen Round-5b Q1 spectra and draw the error profiles.

This is intentionally the sole Round-5b consumer of reference ordinates.
All candidate spectra must already exist as hashed blind artifacts.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import mpmath as mp  # noqa: E402


HERE = Path(__file__).resolve().parent
R5 = HERE.parent / "codex-r5"
OUTPUTS = HERE / "outputs"
X_VALUES = (9, 13, 14)
N_MAX = 120
ROOT_COUNT = 60
TARGET_DPS = 180
THRESHOLD = mp.mpf("1e-30")
PREDICTIONS = {
    9: {"raw_below_1e-30": False, "even_below_1e-30": False},
    13: {"raw_below_1e-30": False, "even_below_1e-30": False},
    14: {"raw_below_1e-30": True, "even_below_1e-30": True},
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def as_complex(record: dict[str, str]) -> mp.mpc:
    return mp.mpc(record["real"], record["imaginary"])


def serialize(value: mp.mpf | mp.mpc, digits: int = 110) -> str:
    return mp.nstr(value, digits)


def validate_blind_artifact(path: Path, x: int) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    parameters = payload.get("parameters", {})
    if payload.get("schema") != "codex-r5b-q1-blind-v1":
        raise RuntimeError(f"unexpected schema in {path}")
    if payload.get("target_data_present") is not False:
        raise RuntimeError(f"target data flag failed in {path}")
    if payload.get("scoring_present") is not False:
        raise RuntimeError(f"scoring flag failed in {path}")
    if not payload.get("source_audit", {}).get("passed"):
        raise RuntimeError(f"source audit failed in {path}")
    if not payload.get("diagnostics", {}).get("all_checks_passed"):
        raise RuntimeError(f"numerical audit failed in {path}")
    expected = {
        "x": x,
        "N": N_MAX,
        "working_decimal_digits": 200,
        "legendre_cutoff": 200,
        "retained_root_count": ROOT_COUNT,
    }
    for key, value in expected.items():
        if parameters.get(key) != value:
            raise RuntimeError(
                f"parameter {key}={parameters.get(key)!r}, expected {value!r} in {path}"
            )
    if len(payload.get("roots", [])) != ROOT_COUNT:
        raise RuntimeError(f"wrong root count in {path}")
    for relative, expected_hash in payload.get("source_sha256", {}).items():
        source = HERE.parent / relative
        if sha256(source) != expected_hash:
            raise RuntimeError(f"source hash mismatch for {source}")
    return payload


def validate_true_artifact(path: Path, x: int) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    expected = {"x": x, "N": N_MAX, "dps": 400}
    if payload.get("parameters") != expected:
        raise RuntimeError(f"unexpected true-Weil parameters in {path}")
    if payload.get("target_data_present") is not False:
        raise RuntimeError(f"true artifact has target data in {path}")
    if payload.get("scoring_present") is not False:
        raise RuntimeError(f"true artifact has scoring in {path}")
    if len(payload.get("positive_roots", [])) < ROOT_COUNT:
        raise RuntimeError(f"true artifact has too few roots in {path}")
    return payload


def discriminator_band(log10_ratio: mp.mpf) -> str:
    if log10_ratio <= 10:
        return "VOID"
    if log10_ratio > 20:
        return "MEASURED"
    return "UNVERIFIED"


def score_case(
    x: int,
    blind: dict[str, object],
    true_payload: dict[str, object],
    targets: list[mp.mpf],
) -> dict[str, object]:
    true_roots = [
        mp.mpf(value) for value in true_payload["positive_roots"][:ROOT_COUNT]
    ]
    raw_roots = [as_complex(row["raw_root"]) for row in blind["roots"]]
    even_roots = [mp.mpf(row["even_root"]) for row in blind["roots"]]

    true_errors = [abs(root - target) for root, target in zip(true_roots, targets)]
    raw_errors = [abs(root - target) for root, target in zip(raw_roots, targets)]
    even_errors = [abs(root - target) for root, target in zip(even_roots, targets)]
    if any(value == 0 for value in true_errors + raw_errors + even_errors):
        raise RuntimeError(f"a reported x={x} error rounded to exact zero")

    rows = []
    for ordinal in range(ROOT_COUNT):
        true_error = true_errors[ordinal]
        raw_error = raw_errors[ordinal]
        even_error = even_errors[ordinal]
        raw_ratio = raw_error / true_error
        even_ratio = even_error / true_error
        rows.append(
            {
                "ordinal": ordinal + 1,
                "target": serialize(targets[ordinal]),
                "true_weil_root": serialize(true_roots[ordinal]),
                "raw_prolate_root": {
                    "real": serialize(mp.re(raw_roots[ordinal])),
                    "imaginary": serialize(mp.im(raw_roots[ordinal])),
                },
                "even_prolate_root": serialize(even_roots[ordinal]),
                "true_weil_absolute_error": serialize(true_error),
                "raw_prolate_absolute_complex_error": serialize(raw_error),
                "raw_to_weil_error_ratio": serialize(raw_ratio),
                "raw_to_weil_log10_ratio": serialize(mp.log10(raw_ratio), 50),
                "even_prolate_absolute_error": serialize(even_error),
                "even_to_weil_error_ratio": serialize(even_ratio),
                "even_to_weil_log10_ratio": serialize(mp.log10(even_ratio), 50),
            }
        )

    raw_log_ratio = mp.log10(raw_errors[0] / true_errors[0])
    even_log_ratio = mp.log10(even_errors[0] / true_errors[0])
    raw_below = bool(raw_errors[0] < THRESHOLD)
    even_below = bool(even_errors[0] < THRESHOLD)
    if raw_log_ratio <= 10 or even_log_ratio <= 10:
        combined_status = "VOID"
        combined_reason = (
            "at least one prime-free first candidate is within the frozen ten-order band"
        )
    elif raw_log_ratio > 20 and even_log_ratio > 20:
        combined_status = "MEASURED"
        combined_reason = (
            "both prime-free variants are more than twenty orders worse at k=1"
        )
    else:
        combined_status = "UNVERIFIED"
        combined_reason = "the variants do not jointly satisfy either frozen decisive band"

    return {
        "x": x,
        "N": N_MAX,
        "first_zero": {
            "true_weil_absolute_error": serialize(true_errors[0]),
            "raw_prolate_absolute_error": serialize(raw_errors[0]),
            "even_prolate_absolute_error": serialize(even_errors[0]),
            "raw_below_1e-30": raw_below,
            "even_below_1e-30": even_below,
            "predicted_raw_below_1e-30": PREDICTIONS[x]["raw_below_1e-30"],
            "predicted_even_below_1e-30": PREDICTIONS[x]["even_below_1e-30"],
            "raw_prediction_held": raw_below
            == PREDICTIONS[x]["raw_below_1e-30"],
            "even_prediction_held": even_below
            == PREDICTIONS[x]["even_below_1e-30"],
            "raw_to_weil_log10_ratio": serialize(raw_log_ratio, 60),
            "even_to_weil_log10_ratio": serialize(even_log_ratio, 60),
            "raw_band": discriminator_band(raw_log_ratio),
            "even_band": discriminator_band(even_log_ratio),
            "combined_discriminator_status": combined_status,
            "combined_reason": combined_reason,
            "raw_root_label_status": "UNVERIFIED",
        },
        "rows_1_to_60": rows,
        "plot_values": {
            "true": true_errors,
            "raw": raw_errors,
            "even": even_errors,
        },
    }


def draw_figure(cases: list[dict[str, object]]) -> tuple[Path, Path]:
    figure, axes = plt.subplots(1, 3, figsize=(14.2, 4.65), sharex=True)
    ordinals = list(range(1, ROOT_COUNT + 1))
    colors = {"true": "#172554", "raw": "#dc2626", "even": "#059669"}
    labels = {
        "true": "true Weil ground",
        "raw": "raw prolate (complex distance)",
        "even": "even-projected prolate",
    }
    for axis, case in zip(axes, cases):
        values = case["plot_values"]
        for key in ("true", "raw", "even"):
            axis.semilogy(
                ordinals,
                [float(value) for value in values[key]],
                color=colors[key],
                linewidth=1.35,
                marker="o",
                markersize=2.1,
                markevery=3,
                label=labels[key],
            )
        axis.set_title(rf"$x=\lambda^2={case['x']}$")
        axis.set_xlim(1, ROOT_COUNT)
        axis.margins(y=0.08)
        axis.grid(True, which="both", linewidth=0.35, alpha=0.32)
        axis.set_xlabel("zero ordinal k")
    axes[0].set_ylabel("absolute error")
    handles, legend_labels = axes[0].get_legend_handles_labels()
    figure.legend(
        handles,
        legend_labels,
        loc="upper center",
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.5, 1.02),
    )
    figure.suptitle("Round 5b Q1: unsmoothed zero-error profiles, N=120", y=1.09)
    figure.tight_layout()
    png = OUTPUTS / "q1-error-profiles.png"
    svg = OUTPUTS / "q1-error-profiles.svg"
    figure.savefig(png, dpi=220, bbox_inches="tight")
    figure.savefig(svg, bbox_inches="tight")
    plt.close(figure)
    svg.write_text(
        "\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines())
        + "\n",
        encoding="utf-8",
    )
    return png, svg


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    with mp.workdps(TARGET_DPS):
        # This is the only target-data evaluation in Round 5b.
        targets = [mp.im(mp.zetazero(index)) for index in range(1, ROOT_COUNT + 1)]
        cases: list[dict[str, object]] = []
        input_artifacts = []
        for x in X_VALUES:
            blind_path = OUTPUTS / f"q1-blind-x{x}.json"
            true_path = R5 / f"true-x{x}-N120-dps400.json"
            blind = validate_blind_artifact(blind_path, x)
            true_payload = validate_true_artifact(true_path, x)
            case = score_case(x, blind, true_payload, targets)
            cases.append(case)
            input_artifacts.append(
                {
                    "x": x,
                    "blind_path": str(blind_path.relative_to(HERE.parent)),
                    "blind_sha256": sha256(blind_path),
                    "true_weil_path": str(true_path.relative_to(HERE.parent)),
                    "true_weil_sha256": sha256(true_path),
                }
            )

        png, svg = draw_figure(cases)
        for case in cases:
            case.pop("plot_values")
        payload = {
            "schema": "codex-r5b-q1-scored-v1",
            "status": "MEASURED",
            "scope": "frozen per-ordinal comparison at x=9,13,14; N=120",
            "target_decimal_digits": TARGET_DPS,
            "target_ordinals": [1, ROOT_COUNT],
            "error_conventions": {
                "true_and_even": "absolute real difference",
                "raw": "absolute complex distance under the preregistered continuation label",
                "ratio": "candidate absolute error divided by true-Weil absolute error at the same ordinal",
            },
            "frozen_discriminator": {
                "d_at_most_10": "VOID",
                "d_greater_than_20_for_both_variants": "MEASURED",
                "otherwise": "UNVERIFIED",
                "boundary_rule": "equality belongs to the lower band",
            },
            "inputs": input_artifacts,
            "cases": cases,
            "figure": {
                "png": str(png.relative_to(HERE.parent)),
                "png_sha256": sha256(png),
                "svg": str(svg.relative_to(HERE.parent)),
                "svg_sha256": sha256(svg),
                "panels": list(X_VALUES),
                "profiles": ["true Weil", "raw prolate", "even-projected prolate"],
                "unsmoothed": True,
                "logarithmic_error_axis": True,
            },
            "scorer_sha256": sha256(Path(__file__)),
            "sole_reference_ordinate_consumer": True,
        }
    output = OUTPUTS / "q1-scored.json"
    output.write_text(
        json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "cases": [
                    {
                        "x": case["x"],
                        "raw_error_1": case["first_zero"]["raw_prolate_absolute_error"],
                        "even_error_1": case["first_zero"]["even_prolate_absolute_error"],
                        "status": case["first_zero"]["combined_discriminator_status"],
                    }
                    for case in cases
                ],
                "figure_png": str(png),
                "figure_svg": str(svg),
            },
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
