#!/usr/bin/env python3
"""Small observer-feeling switcher for "strangely familiar" vs "strangely foreign".

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import ghp_boundary_access_local_switcher as local_switcher


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_strange_familiar_switcher_outputs"

AXIS_NAMES = [
    "familiarity",
    "surprise",
    "strangely_familiar",
    "strangely_foreign",
]

PACKS = {
    "familiarity_only": [0],
    "surprise_only": [1],
    "two_feelings": [0, 1],
    "strange_compass": [2, 3],
    "all_four": [0, 1, 2, 3],
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


def derive_axes(row: dict[str, object]) -> np.ndarray:
    features = np.asarray(row["features"], dtype=float)
    damage_wake_cos = float(features[1])
    helper_wake_cos = float(features[3])
    helper_deep_cos = float(features[4])
    entropy_gap = float(features[9])

    familiarity = 0.5 * (helper_wake_cos + helper_deep_cos)
    surprise = 0.5 * ((1.0 - damage_wake_cos) + entropy_gap)
    strangely_familiar = familiarity * surprise
    strangely_foreign = (1.0 - familiarity) * surprise
    return np.array(
        [familiarity, surprise, strangely_familiar, strangely_foreign],
        dtype=float,
    )


def select_axes(rows: list[dict[str, object]], indices: list[int]) -> list[dict[str, object]]:
    selected: list[dict[str, object]] = []
    for row in rows:
        chosen = dict(row)
        axes = derive_axes(row)
        chosen["axes"] = axes
        chosen["features"] = axes[indices]
        selected.append(chosen)
    return selected


def evaluate_pack(
    name: str,
    indices: list[int],
    train_rows: list[dict[str, object]],
    test_rows: list[dict[str, object]],
) -> dict[str, float | str]:
    train_selected = select_axes(train_rows, indices)
    test_selected = select_axes(test_rows, indices)
    mean, std, weights = local_switcher.fit_linear_probe(train_selected)
    chosen = [
        "fibonacci"
        if local_switcher.predict_linear_probe(np.asarray(row["features"], dtype=float), mean, std, weights) == 1
        else "generic_ternary"
        for row in test_selected
    ]
    accuracy = np.mean([choice == row["target_family"] for choice, row in zip(chosen, test_selected)])
    return {
        "pack": name,
        "target_family_accuracy": float(accuracy),
    }


def evaluate_heuristic(test_rows: list[dict[str, object]]) -> dict[str, float | str]:
    chosen: list[str] = []
    for row in test_rows:
        familiarity, surprise, strangely_familiar, strangely_foreign = derive_axes(row)
        if strangely_familiar >= strangely_foreign and familiarity >= 0.53 and surprise >= 0.10:
            chosen.append("fibonacci")
        else:
            chosen.append("generic_ternary")
    accuracy = np.mean([choice == row["target_family"] for choice, row in zip(chosen, test_rows)])
    return {
        "pack": "simple_compass_heuristic",
        "target_family_accuracy": float(accuracy),
    }


def summarize_axes(rows: list[dict[str, object]]) -> list[dict[str, float | str]]:
    summary: list[dict[str, float | str]] = []
    for key, subset in [
        ("fibonacci_target", [row for row in rows if row["target_family"] == "fibonacci"]),
        ("generic_ternary_target", [row for row in rows if row["target_family"] == "generic_ternary"]),
        ("coherent_variant", [row for row in rows if row["variant"] == "cross_family"]),
        ("internal_scramble", [row for row in rows if row["variant"] != "cross_family"]),
    ]:
        axes = np.vstack([derive_axes(row) for row in subset])
        mean_axes = axes.mean(axis=0)
        summary.append(
            {
                "group": key,
                "familiarity": float(mean_axes[0]),
                "surprise": float(mean_axes[1]),
                "strangely_familiar": float(mean_axes[2]),
                "strangely_foreign": float(mean_axes[3]),
            }
        )
    return summary


def main() -> None:
    ensure_dir(OUT)
    words = local_switcher.build_words()
    vocab = local_switcher.base.collect_vocabulary(words, local_switcher.base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}

    train_rows: list[dict[str, object]] = []
    test_rows: list[dict[str, object]] = []
    for seed in local_switcher.TRAIN_SEEDS:
        train_rows.extend(local_switcher.collect_events_for_seed(seed, words, vocab_index))
    for seed in local_switcher.TEST_SEEDS:
        test_rows.extend(local_switcher.collect_events_for_seed(seed, words, vocab_index))

    rows = [
        evaluate_pack(name, indices, train_rows, test_rows)
        for name, indices in PACKS.items()
    ]
    rows.append(evaluate_heuristic(test_rows))
    rows = sorted(rows, key=lambda row: float(row["target_family_accuracy"]), reverse=True)
    write_csv(rows, OUT / "strange_familiar_summary.csv")

    axis_rows = summarize_axes(test_rows)
    write_csv(axis_rows, OUT / "axis_summary.csv")

    best = rows[0]
    lines = [
        "# Boundary Access Strange-Familiar Switcher",
        "",
        f"- best compact pack: `{best['pack']}` `{float(best['target_family_accuracy']):.3f}`",
        "",
        "Ranking:",
    ]
    for row in rows:
        lines.append(f"- {row['pack']}: `{float(row['target_family_accuracy']):.3f}`")
    lines.extend(
        [
            "",
            "Held-out axis means:",
        ]
    )
    for row in axis_rows:
        lines.append(
            "- "
            f"{row['group']}: familiarity `{float(row['familiarity']):.3f}`, "
            f"surprise `{float(row['surprise']):.3f}`, "
            f"strangely_familiar `{float(row['strangely_familiar']):.3f}`, "
            f"strangely_foreign `{float(row['strangely_foreign']):.3f}`"
        )
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
