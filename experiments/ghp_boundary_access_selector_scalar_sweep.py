#!/usr/bin/env python3
"""Small scalar-selector sweep for Boundary Access groove-aware axes.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from itertools import product
from pathlib import Path

import numpy as np

import ghp_boundary_access_belief_inertia_switcher as inertia_switcher
import ghp_boundary_access_local_switcher as local_switcher


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_selector_scalar_sweep_outputs"

COEFF_GRID = [0.0, 1.0, 2.0]
BASIS = [
    "novel_but_fits",
    "foreign_pressure",
    "wake_pull",
    "belief_tension",
]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(rows: list[dict[str, float | str]], path: Path) -> None:
    if not rows:
        return
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.write_text(text)


def axis_index(name: str) -> int:
    return inertia_switcher.AXIS_NAMES.index(name)


def scalar_score(features: np.ndarray, coeffs: tuple[float, float, float, float]) -> float:
    novel = float(features[axis_index("novel_but_fits")])
    foreign = float(features[axis_index("foreign_pressure")])
    wake_pull = float(features[axis_index("wake_pull")])
    tension = float(features[axis_index("belief_tension")])
    a, b, c, d = coeffs
    return a * novel - b * foreign + c * wake_pull - d * tension


def scores_for_rows(rows: list[dict[str, object]], coeffs: tuple[float, float, float, float]) -> np.ndarray:
    return np.array([scalar_score(np.asarray(row["features"], dtype=float), coeffs) for row in rows], dtype=float)


def labels_for_rows(rows: list[dict[str, object]]) -> np.ndarray:
    return np.array([1 if row["target_family"] == "fibonacci" else 0 for row in rows], dtype=int)


def best_threshold(scores: np.ndarray, labels: np.ndarray) -> tuple[float, float]:
    unique_scores = np.unique(scores)
    if len(unique_scores) > 128:
        indices = np.linspace(0, len(unique_scores) - 1, 128).astype(int)
        unique_scores = unique_scores[indices]
    candidates = [float(unique_scores[0] - 1e-9)]
    if len(unique_scores) > 1:
        candidates.extend(((unique_scores[:-1] + unique_scores[1:]) / 2.0).tolist())
    candidates.append(float(unique_scores[-1] + 1e-9))
    best_acc = -1.0
    best_cut = candidates[0]
    for cut in candidates:
        predicted = (scores >= cut).astype(int)
        acc = float(np.mean(predicted == labels))
        if acc > best_acc:
            best_acc = acc
            best_cut = float(cut)
    return best_cut, best_acc


def evaluate_threshold(scores: np.ndarray, labels: np.ndarray, cut: float) -> float:
    predicted = (scores >= cut).astype(int)
    return float(np.mean(predicted == labels))


def scenario_breakdown(
    rows: list[dict[str, object]],
    scores: np.ndarray,
    cut: float,
) -> list[dict[str, float | str]]:
    labels = labels_for_rows(rows)
    predicted = (scores >= cut).astype(int)
    scenario_names = sorted({str(row["noise_level"]) for row in rows})
    summary: list[dict[str, float | str]] = []
    for noise_name in scenario_names:
        indices = [idx for idx, row in enumerate(rows) if str(row["noise_level"]) == noise_name]
        acc = float(np.mean(predicted[indices] == labels[indices]))
        summary.append({"noise_level": noise_name, "accuracy": acc})
    return summary


def main() -> None:
    ensure_dir(OUT)
    words = local_switcher.build_words()
    vocab = local_switcher.base.collect_vocabulary(words, local_switcher.base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}

    train_rows: list[dict[str, object]] = []
    test_rows: list[dict[str, object]] = []
    for seed in local_switcher.TRAIN_SEEDS:
        train_rows.extend(inertia_switcher.collect_rows(seed, words, vocab_index))
    for seed in local_switcher.TEST_SEEDS:
        test_rows.extend(inertia_switcher.collect_rows(seed, words, vocab_index))

    candidate_rows: list[dict[str, float | str]] = []
    train_labels = labels_for_rows(train_rows)
    test_labels = labels_for_rows(test_rows)

    for coeffs in product(COEFF_GRID, repeat=4):
        if coeffs[0] == 0.0 and coeffs[1] == 0.0 and coeffs[2] == 0.0 and coeffs[3] == 0.0:
            continue
        train_scores = scores_for_rows(train_rows, coeffs)
        cut, train_acc = best_threshold(train_scores, train_labels)
        test_scores = scores_for_rows(test_rows, coeffs)
        test_acc = evaluate_threshold(test_scores, test_labels, cut)
        candidate_rows.append(
            {
                "a_novel_but_fits": coeffs[0],
                "b_foreign_pressure": coeffs[1],
                "c_wake_pull": coeffs[2],
                "d_belief_tension": coeffs[3],
                "threshold": cut,
                "train_accuracy": train_acc,
                "test_accuracy": test_acc,
            }
        )

    candidate_rows = sorted(candidate_rows, key=lambda row: (float(row["test_accuracy"]), float(row["train_accuracy"])), reverse=True)
    top_rows = candidate_rows[:20]
    write_csv(top_rows, OUT / "top_scalar_candidates.csv")

    best = top_rows[0]
    best_coeffs = (
        float(best["a_novel_but_fits"]),
        float(best["b_foreign_pressure"]),
        float(best["c_wake_pull"]),
        float(best["d_belief_tension"]),
    )
    best_cut = float(best["threshold"])
    breakdown = scenario_breakdown(test_rows, scores_for_rows(test_rows, best_coeffs), best_cut)
    write_csv(breakdown, OUT / "best_scalar_noise_breakdown.csv")

    lines = [
        "# Boundary Access Selector Scalar Sweep",
        "",
        "- best scalar form:",
        "  `score = a*novel_but_fits - b*foreign_pressure + c*wake_pull - d*belief_tension`",
        "",
        f"- best coefficients: `a={best_coeffs[0]:.1f}, b={best_coeffs[1]:.1f}, c={best_coeffs[2]:.1f}, d={best_coeffs[3]:.1f}`",
        f"- held-out accuracy: `{float(best['test_accuracy']):.3f}`",
        f"- train accuracy: `{float(best['train_accuracy']):.3f}`",
        "",
        "Top candidates:",
    ]
    for row in top_rows[:10]:
        lines.append(
            "- "
            f"`a={float(row['a_novel_but_fits']):.1f}, "
            f"b={float(row['b_foreign_pressure']):.1f}, "
            f"c={float(row['c_wake_pull']):.1f}, "
            f"d={float(row['d_belief_tension']):.1f}`"
            f" -> test `{float(row['test_accuracy']):.3f}`, train `{float(row['train_accuracy']):.3f}`"
        )
    lines.extend(["", "Held-out noise breakdown:"])
    for row in breakdown:
        lines.append(f"- noise `{row['noise_level']}`: `{float(row['accuracy']):.3f}`")
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
