#!/usr/bin/env python3
"""Ablation pass for the belief-inertia switcher.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import ghp_boundary_access_belief_inertia_switcher as belief_switcher
import ghp_boundary_access_local_switcher as local_switcher


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_belief_inertia_ablation_outputs"

ABLATIONS = {
    "all_axes": belief_switcher.PACKS["all_axes"],
    "groove_compass": belief_switcher.PACKS["groove_compass"],
    "pull_only": [4, 5],
    "scaled_fit_only": [6, 7],
    "raw_fit_only": [8, 9],
    "pull_plus_scaled_fit": [4, 5, 6, 7],
    "pull_plus_raw_fit": [4, 5, 8, 9],
    "pull_plus_feelings": [0, 1, 4, 5],
    "pull_plus_tension": [4, 5, 10],
    "tension_only": [10],
}


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


def select_features(rows: list[dict[str, object]], indices: list[int]) -> list[dict[str, object]]:
    selected: list[dict[str, object]] = []
    for row in rows:
        chosen = dict(row)
        features = np.asarray(row["features"], dtype=float)
        chosen["features"] = features[indices]
        selected.append(chosen)
    return selected


def evaluate_pack(
    name: str,
    indices: list[int],
    train_rows: list[dict[str, object]],
    test_rows: list[dict[str, object]],
) -> dict[str, float | str]:
    train_selected = select_features(train_rows, indices)
    test_selected = select_features(test_rows, indices)
    mean, std, weights = local_switcher.fit_linear_probe(train_selected)
    chosen = [
        "fibonacci"
        if local_switcher.predict_linear_probe(np.asarray(row["features"], dtype=float), mean, std, weights) == 1
        else "generic_ternary"
        for row in test_selected
    ]
    accuracy = np.mean([choice == row["target_family"] for choice, row in zip(chosen, test_selected)])
    return {
        "ablation": name,
        "target_family_accuracy": float(accuracy),
    }


def main() -> None:
    ensure_dir(OUT)
    words = local_switcher.build_words()
    vocab = local_switcher.base.collect_vocabulary(words, local_switcher.base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}

    train_rows: list[dict[str, object]] = []
    test_rows: list[dict[str, object]] = []
    for seed in local_switcher.TRAIN_SEEDS:
        train_rows.extend(belief_switcher.collect_rows(seed, words, vocab_index))
    for seed in local_switcher.TEST_SEEDS:
        test_rows.extend(belief_switcher.collect_rows(seed, words, vocab_index))

    rows = [
        evaluate_pack(name, indices, train_rows, test_rows)
        for name, indices in ABLATIONS.items()
    ]
    rows = sorted(rows, key=lambda row: float(row["target_family_accuracy"]), reverse=True)
    write_csv(rows, OUT / "belief_inertia_ablation_summary.csv")

    best = rows[0]
    lines = [
        "# Boundary Access Belief-Inertia Ablation",
        "",
        f"- best ablation: `{best['ablation']}` `{float(best['target_family_accuracy']):.3f}`",
        "- compare to full local switcher: about `0.890`",
        "- compare to strange-familiar compact pack: about `0.837`",
        "",
        "Ranking:",
    ]
    for row in rows:
        lines.append(f"- {row['ablation']}: `{float(row['target_family_accuracy']):.3f}`")
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
