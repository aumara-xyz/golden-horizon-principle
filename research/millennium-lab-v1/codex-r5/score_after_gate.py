#!/usr/bin/env python3
"""Score frozen ordinal targets only after validating the pseudo-prime gate."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Sequence

import mpmath as mp

import weil_core as core


HERE = Path(__file__).resolve().parent
GATE = HERE / "pseudo-gate.json"
BLIND = HERE / "blind-pseudo-spectra.json"
OUTPUT = HERE / "accuracy-after-pseudo-gate.json"
INDICES = list(range(20, 51))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def score(label: str, roots: Sequence[str], targets: Sequence[mp.mpf]) -> dict[str, object]:
    selected = [mp.mpf(roots[index - 1]) for index in INDICES]
    errors = [candidate - target for candidate, target in zip(selected, targets)]
    absolute = [abs(error) for error in errors]
    ordered = sorted(absolute)
    rmse = mp.sqrt(mp.fsum(error * error for error in errors) / len(errors))
    mae = mp.fsum(absolute) / len(absolute)
    median = ordered[len(ordered) // 2]
    maximum = max(absolute)
    return {
        "label": label,
        "indices": INDICES,
        "errors": [mp.nstr(value, 90) for value in errors],
        "absolute_errors": [mp.nstr(value, 90) for value in absolute],
        "rmse": mp.nstr(rmse, 90),
        "mae": mp.nstr(mae, 90),
        "median_absolute_error": mp.nstr(median, 90),
        "maximum_absolute_error": mp.nstr(maximum, 90),
        "lands": bool(rmse <= mp.mpf("0.01") and maximum <= mp.mpf("0.05")),
    }


def score_complex(
    label: str,
    roots: Sequence[dict[str, str]],
    targets: Sequence[mp.mpf],
) -> dict[str, object]:
    """Score continuation-labelled complex roots by Euclidean distance."""

    selected = [
        mp.mpc(roots[index - 1]["real"], roots[index - 1]["imaginary"])
        for index in INDICES
    ]
    errors = [candidate - target for candidate, target in zip(selected, targets)]
    absolute = [abs(error) for error in errors]
    ordered = sorted(absolute)
    rmse = mp.sqrt(mp.fsum(error**2 for error in absolute) / len(absolute))
    mae = mp.fsum(absolute) / len(absolute)
    median = ordered[len(ordered) // 2]
    maximum = max(absolute)
    return {
        "label": label,
        "indices": INDICES,
        "error_convention": "absolute complex distance |z_j-gamma_j|",
        "complex_errors": [
            {
                "real": mp.nstr(mp.re(value), 90),
                "imaginary": mp.nstr(mp.im(value), 90),
            }
            for value in errors
        ],
        "absolute_errors": [mp.nstr(value, 90) for value in absolute],
        "rmse": mp.nstr(rmse, 90),
        "mae": mp.nstr(mae, 90),
        "median_absolute_error": mp.nstr(median, 90),
        "maximum_absolute_error": mp.nstr(maximum, 90),
        "maximum_absolute_imaginary_part": mp.nstr(
            max(abs(mp.im(value)) for value in selected), 90
        ),
        "lands": bool(rmse <= mp.mpf("0.01") and maximum <= mp.mpf("0.05")),
    }


def smooth_quantile(index: int) -> mp.mpf:
    """Parameter-free inversion of the leading Riemann--von Mangoldt count."""

    target = mp.mpf(index) - mp.mpf(7) / 8
    guess = 2 * mp.pi * target / mp.lambertw(target / mp.e)
    return mp.findroot(
        lambda height: height / (2 * mp.pi) * (mp.log(height / (2 * mp.pi)) - 1)
        + mp.mpf(7) / 8
        - index,
        guess,
    )


def main() -> None:
    gate = json.loads(GATE.read_text())
    if not gate.get("gate_complete") or gate.get("run_count") != 10:
        raise RuntimeError("pseudo-prime gate is incomplete")
    if sha256(BLIND) != gate.get("blind_output_sha256"):
        raise RuntimeError("pseudo-prime blind output hash mismatch")
    if not gate.get("static_audit", {}).get("passed"):
        raise RuntimeError("pseudo-prime source audit did not pass")

    mp.mp.dps = 110
    targets = [mp.im(mp.zetazero(index)) for index in INDICES]
    blind = json.loads(BLIND.read_text())

    pseudo_scores = [
        score(f"pseudo-prime seed {run['seed']}", run["roots"], targets)
        for run in blind["runs"]
    ]
    # This is intentionally the first metric output emitted by the process.
    print(
        json.dumps(
            {
                "first_reported_accuracy_kind": "pseudo-prime control",
                "seeds": [item["label"] for item in pseudo_scores],
                "rmse": [item["rmse"] for item in pseudo_scores],
                "lands": [item["lands"] for item in pseudo_scores],
            }
        ),
        flush=True,
    )

    hostile_scores: list[dict[str, object]] = []
    hostile_paths = [
        HERE / "hostile-arch-only.json",
        HERE / "hostile-permuted.json",
        *[HERE / f"hostile-delete-{prime}.json" for prime in (2, 3, 5, 7, 11, 13)],
    ]
    optional_prolate = HERE / "outputs" / "prolate-only-blind.json"
    optional_raw_prolate = HERE / "outputs" / "prolate-only-raw-blind.json"
    for path in hostile_paths:
        payload = json.loads(path.read_text())
        hostile_scores.append(score(payload["label"], payload["positive_roots"], targets))
    prolate_payload: dict[str, object] | None = None
    if optional_prolate.exists():
        prolate_payload = json.loads(optional_prolate.read_text())
        hostile_scores.insert(
            1,
            score(
                "prolate-only x=13, N=120",
                prolate_payload["primary"]["positive_roots"],
                targets,
            ),
        )
    if optional_raw_prolate.exists():
        raw_prolate_payload = json.loads(optional_raw_prolate.read_text())
        raw_score = score_complex(
            "prolate-only raw E(h), x=13, N=120 (post-hoc continuation labels)",
            [row["raw_root"] for row in raw_prolate_payload["roots"]],
            targets,
        )
        raw_score["blind_artifact_sha256"] = sha256(optional_raw_prolate)
        raw_score["root_definition_status"] = raw_prolate_payload[
            "root_definition_status"
        ]
        raw_score["root_definition_limit"] = raw_prolate_payload[
            "root_definition_limit"
        ]
        hostile_scores.insert(1, raw_score)

    mutation_scores: list[dict[str, object]] = []
    for x in (12, 13, 14):
        for n_max in (112, 128):
            path = HERE / f"mutation-x{x}-N{n_max}-dps100.json"
            payload = json.loads(path.read_text())
            mutation_scores.append(
                score(f"true primes x={x}, N={n_max}, dps=100", payload["positive_roots"], targets)
            )
    for name in ("prime13-plus5", "delete13-survivors-plus5", "cutoff13.25"):
        path = HERE / f"survivor-{name}.json"
        payload = json.loads(path.read_text())
        mutation_scores.append(score(payload["label"], payload["positive_roots"], targets))
    if prolate_payload is not None:
        for name, record in prolate_payload["mutations"].items():
            mutation_scores.append(
                score(
                    f"prolate-only {name}",
                    record["run"]["positive_roots"],
                    targets,
                )
            )

    path_scores: list[dict[str, object]] = []
    reused_paths = {
        (12, 120): HERE / "true-x12-N120-dps100.json",
        (14, 112): HERE / "mutation-x14-N112-dps100.json",
    }
    for x in (8, 10, 12, 14, 16):
        for multiplier in (8, 10, 12):
            n_max = multiplier * x
            path = reused_paths.get(
                (x, n_max), HERE / f"npath-x{x}-N{n_max}-dps100.json"
            )
            if not path.exists():
                continue
            payload = json.loads(path.read_text())
            row = score(
                f"authentic path N=ceil({multiplier}x), x={x}, N={n_max}",
                payload["positive_roots"],
                targets,
            )
            row["x"] = x
            row["N"] = n_max
            row["path_multiplier"] = multiplier
            path_scores.append(row)

    true_scores: list[dict[str, object]] = []
    precision_diffs: list[dict[str, str | int]] = []
    for x in [9, 12, 13, 14]:
        payloads: dict[int, dict[str, object]] = {}
        for dps in [100, 200, 400]:
            path = HERE / f"true-x{x}-N120-dps{dps}.json"
            payloads[dps] = json.loads(path.read_text())
            true_scores.append(
                score(
                    f"true primes x={x}, N=120, dps={dps}",
                    payloads[dps]["positive_roots"],
                    targets,
                )
            )
        for low, high in [(100, 200), (200, 400)]:
            # Precision comparisons must not inherit the 110-digit target
            # precision, or a genuine ~1e-149 displacement rounds to zero.
            with mp.workdps(450):
                differences = [
                    abs(mp.mpf(a) - mp.mpf(b))
                    for a, b in zip(
                        payloads[low]["positive_roots"],
                        payloads[high]["positive_roots"],
                    )
                ]
            precision_diffs.append(
                {
                    "x": x,
                    "low_dps": low,
                    "high_dps": high,
                    "maximum_root_difference_1_to_60": mp.nstr(max(differences), 90),
                    "maximum_root_difference_20_to_50": mp.nstr(
                        max(differences[19:50]), 90
                    ),
                }
            )

    smooth_roots = [mp.nstr(smooth_quantile(index), 110) for index in range(1, 61)]
    smooth_score = score("smooth counting-law quantiles", smooth_roots, targets)
    payload = {
        "gate_validation": {
            "path": GATE.name,
            "gate_sha256": sha256(GATE),
            "blind_sha256": sha256(BLIND),
            "completed_before_scorer": True,
            "pseudo_was_first_metric_output": True,
        },
        "target_indices": INDICES,
        "targets": [mp.nstr(value, 110) for value in targets],
        "landing_rule": {"rmse_at_most": "0.01", "maximum_at_most": "0.05"},
        "pseudo_prime_scores": pseudo_scores,
        "hostile_control_scores": hostile_scores,
        "survivor_mutation_scores": mutation_scores,
        "n_path_scores": path_scores,
        "smooth_control": smooth_score,
        "true_prime_scores": true_scores,
        "precision_differences": precision_diffs,
    }
    core.write_json(OUTPUT, payload)
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "pseudo_landing_count": sum(item["lands"] for item in pseudo_scores),
                "hostile_landing_count": sum(item["lands"] for item in hostile_scores),
                "true_landing_count": sum(item["lands"] for item in true_scores),
                "smooth_rmse": smooth_score["rmse"],
            }
        )
    )


if __name__ == "__main__":
    main()
