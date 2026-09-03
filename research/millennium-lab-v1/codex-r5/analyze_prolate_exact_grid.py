#!/usr/bin/env python3
"""Add zero-free model comparisons to the exact-projection bridge grid."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import statistics


HERE = Path(__file__).resolve().parent
FINAL_FIVE = (13, 14, 16, 18, 20)


def linear_fit(predictor: list[float], response: list[float]) -> dict:
    count = len(response)
    x_mean = sum(predictor) / count
    y_mean = sum(response) / count
    centered_x = [value - x_mean for value in predictor]
    slope = sum(dx * (y - y_mean) for dx, y in zip(centered_x, response)) / sum(
        dx * dx for dx in centered_x
    )
    intercept = y_mean - slope * x_mean
    residuals = [
        y - intercept - slope * x for x, y in zip(predictor, response)
    ]
    rss = sum(value * value for value in residuals)
    pairwise = [
        (response[j] - response[i]) / (predictor[j] - predictor[i])
        for i in range(count)
        for j in range(i + 1, count)
    ]
    return {
        "slope": slope,
        "intercept": intercept,
        "theil_sen_slope": statistics.median(pairwise),
        "rss_log": rss,
        "aic": count * math.log(max(rss, float.fromhex("0x0.0000000000001p-1022")) / count) + 4,
    }


def compare(rows: list[dict], n_max: int) -> dict:
    selected = sorted(
        (
            row for row in rows
            if row["N"] == n_max and row["x"] in FINAL_FIVE
            and row["metrics"]["ratio_status"] == "MEASURED"
        ),
        key=lambda row: row["x"],
    )
    if len(selected) != len(FINAL_FIVE):
        return {"status": "UNVERIFIED", "available_x": [row["x"] for row in selected]}
    x_values = [float(row["x"]) for row in selected]
    lambda_values = [math.sqrt(value) for value in x_values]
    response = [math.log(float(row["metrics"]["residual_over_gap"])) for row in selected]
    mean = sum(response) / len(response)
    constant_rss = sum((value - mean) ** 2 for value in response)
    constant_aic = len(response) * math.log(constant_rss / len(response)) + 2
    power = linear_fit([math.log(value) for value in lambda_values], response)
    exponential_x = linear_fit(x_values, response)
    exponential_lambda = linear_fit(lambda_values, response)
    models = {
        "constant_log_ratio": {"rss_log": constant_rss, "aic": constant_aic},
        "power_in_lambda": {
            **power,
            "form": "ratio=C*lambda^(-p)",
            "p": -power["slope"],
            "C": math.exp(power["intercept"]),
        },
        "exponential_in_x": {
            **exponential_x,
            "form": "ratio=C*exp(a*x)",
            "a": exponential_x["slope"],
            "C": math.exp(exponential_x["intercept"]),
        },
        "exponential_in_lambda": {
            **exponential_lambda,
            "form": "ratio=C*exp(a*lambda)",
            "a": exponential_lambda["slope"],
            "C": math.exp(exponential_lambda["intercept"]),
        },
    }
    best = min(models, key=lambda name: models[name]["aic"])
    return {
        "status": "MEASURED",
        "x": list(FINAL_FIVE),
        "models": models,
        "lowest_aic_model": best,
        "interpretation": (
            "the measured ratio grows; negative p denotes growth and is not a decay law"
        ),
    }


def main() -> None:
    path = HERE / "prolate-bridge-data" / "exact-projection-grid.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["model_comparison_last_five"] = {
        str(n_max): compare(payload["rows"], n_max) for n_max in (96, 120, 144)
    }
    payload["analysis_source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    binary_path = HERE / "prolate-bridge-data" / "bridge-summary.json"
    binary = json.loads(binary_path.read_text(encoding="utf-8"))
    hermite_rows = [
        row for row in binary["hermite_control"]
        if row["x"] in FINAL_FIVE and row["N"] in (96, 120, 144)
    ]
    pseudo_rows = [
        row for row in binary["pseudo_control"]
        if row["x"] in FINAL_FIVE and row["N"] == 120
    ]
    pseudo_signed = sorted(row["metrics"]["residual_over_gap"] for row in pseudo_rows)
    payload["registered_control_resolution"] = {
        "undeformed_hermite": {
            "status": "UNVERIFIED",
            "reason": (
                "only the binary64/composite-quadrature run exists; its candidate "
                "uncertainty and matrix floor dominate the true-prime near-null gaps"
            ),
            "final_five_rows_by_N": {
                str(n_max): sum(row["N"] == n_max for row in hermite_rows)
                for n_max in (96, 120, 144)
            },
            "all_existing_ratio_statuses": sorted({
                row["metrics"]["residual_over_gap_status"] for row in hermite_rows
            }),
        },
        "pseudo_prime_seed_52025001": {
            "non_nullness_status": "MEASURED",
            "residual_range_N120": [
                min(row["metrics"]["residual"] for row in pseudo_rows),
                max(row["metrics"]["residual"] for row in pseudo_rows),
            ],
            "parity_gap_N120": {
                str(row["x"]): row["metrics"]["gap"] for row in pseudo_rows
            },
            "signed_ratio_median_N120": pseudo_signed[len(pseudo_signed) // 2],
            "r_over_positive_gap_comparison_status": "UNVERIFIED",
            "reason": (
                "the pseudo matrix is far from null, but Delta is negative at "
                "x=16,18,20 because the even ground is not globally lowest; its "
                "signed median is not a Davis--Kahan ratio comparable to the primary"
            ),
        },
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    log_lines = [
        "status x N residual gap residual_over_gap cutoff_action_bound"
    ]
    for row in payload["rows"]:
        metrics = row["metrics"]
        log_lines.append(
            f"{metrics['ratio_status']} {row['x']} {row['N']} "
            f"{metrics['residual']} {metrics['gap']} "
            f"{metrics['residual_over_gap']} {metrics['legendre_cutoff_action_bound']}"
        )
    for n_max, comparison in payload["model_comparison_last_five"].items():
        models = comparison["models"]
        log_lines.append(
            f"FIT N={n_max} best={comparison['lowest_aic_model']} "
            f"constant_AIC={models['constant_log_ratio']['aic']:.12g} "
            f"power_AIC={models['power_in_lambda']['aic']:.12g} "
            f"exp_x_AIC={models['exponential_in_x']['aic']:.12g}"
        )
    (path.parent / "exact-projection-grid.log").write_text(
        "\n".join(log_lines) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload["model_comparison_last_five"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
