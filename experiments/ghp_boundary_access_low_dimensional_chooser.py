#!/usr/bin/env python3
"""Low-dimensional chooser search for Boundary Access selector features.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import ghp_boundary_access_belief_inertia_switcher as inertia_switcher
import ghp_boundary_access_local_switcher as local_switcher
import ghp_boundary_access_selector_generalization as generalization


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_low_dimensional_chooser_outputs"


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


def axis(row: dict[str, object], name: str) -> float:
    features = np.asarray(row["belief_features"], dtype=float)
    return float(features[inertia_switcher.AXIS_NAMES.index(name)])


def derived_features(row: dict[str, object], pack: str) -> np.ndarray:
    familiarity = axis(row, "familiarity")
    surprise = axis(row, "surprise")
    inertia = axis(row, "inertia")
    wake_pull = axis(row, "wake_pull")
    deep_pull = axis(row, "deep_pull")
    novel = axis(row, "novel_but_fits")
    foreign = axis(row, "foreign_pressure")
    tension = axis(row, "belief_tension")
    fit_balance = novel - foreign
    pull_balance = wake_pull - deep_pull
    scalar_spine = novel - 2.0 * foreign + 2.0 * wake_pull

    packs = {
        "one_scalar_spine": [scalar_spine],
        "two_fit_pull": [fit_balance, wake_pull],
        "two_fit_tension": [fit_balance, tension],
        "three_fit_pull_surprise": [fit_balance, wake_pull, surprise],
        "three_fit_inertia_pull": [fit_balance, inertia, wake_pull],
        "three_novel_foreign_pull": [novel, foreign, wake_pull],
        "four_spine_basis": [novel, foreign, wake_pull, tension],
        "five_groove_compass": [familiarity, surprise, inertia, novel, foreign],
        "six_compass_with_pull": [familiarity, surprise, inertia, novel, foreign, wake_pull],
        "seven_compass_with_pull_tension": [familiarity, surprise, inertia, novel, foreign, wake_pull, tension],
        "all_axes": np.asarray(row["belief_features"], dtype=float).tolist(),
        "pull_balance_control": [fit_balance, pull_balance, surprise],
    }
    return np.asarray(packs[pack], dtype=float)


PACKS = [
    "one_scalar_spine",
    "two_fit_pull",
    "two_fit_tension",
    "three_fit_pull_surprise",
    "three_fit_inertia_pull",
    "three_novel_foreign_pull",
    "four_spine_basis",
    "five_groove_compass",
    "six_compass_with_pull",
    "seven_compass_with_pull_tension",
    "pull_balance_control",
    "all_axes",
]


def rows_for_pack(rows: list[dict[str, object]], pack: str) -> list[dict[str, object]]:
    selected: list[dict[str, object]] = []
    for row in rows:
        selected.append(
            {
                "features": derived_features(row, pack),
                "label": row["label"],
                "target_family": row["target_family"],
                "scenario": row["scenario"],
            }
        )
    return selected


def fit_pack(train_rows: list[dict[str, object]], pack: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return local_switcher.fit_linear_probe(rows_for_pack(train_rows, pack))


def choose_family(
    row: dict[str, object],
    pack: str,
    model: tuple[np.ndarray, np.ndarray, np.ndarray],
) -> str:
    mean, std, weights = model
    prediction = local_switcher.predict_linear_probe(derived_features(row, pack), mean, std, weights)
    return "fibonacci" if prediction == 1 else "generic_ternary"


def evaluate_pack(
    train_rows: list[dict[str, object]],
    test_rows: list[dict[str, object]],
    pack: str,
) -> tuple[dict[str, float | str], list[dict[str, float | str]]]:
    model = fit_pack(train_rows, pack)
    chosen = [choose_family(row, pack, model) for row in test_rows]
    overall = float(np.mean([choice == row["target_family"] for choice, row in zip(chosen, test_rows)]))
    summary = {
        "pack": pack,
        "dimensions": int(len(derived_features(test_rows[0], pack))),
        "overall_accuracy": overall,
    }

    scenario_rows: list[dict[str, float | str]] = []
    for scenario in sorted({str(row["scenario"]) for row in test_rows}):
        subset = [row for row in test_rows if str(row["scenario"]) == scenario]
        subset_chosen = [choose_family(row, pack, model) for row in subset]
        accuracy = float(np.mean([choice == row["target_family"] for choice, row in zip(subset_chosen, subset)]))
        scenario_rows.append(
            {
                "pack": pack,
                "dimensions": int(len(derived_features(test_rows[0], pack))),
                "scenario": scenario,
                "accuracy": accuracy,
            }
        )
    return summary, scenario_rows


def main() -> None:
    ensure_dir(OUT)
    words = generalization.build_words()
    vocab = generalization.base.collect_vocabulary(words, generalization.base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}

    train_rows: list[dict[str, object]] = []
    test_rows: list[dict[str, object]] = []
    for seed in local_switcher.TRAIN_SEEDS:
        train_rows.extend(generalization.collect_rows_for_seed(seed, generalization.TRAIN_SCENARIOS, words, vocab_index))
    for seed in local_switcher.TEST_SEEDS:
        test_rows.extend(generalization.collect_rows_for_seed(seed, generalization.TEST_SCENARIOS, words, vocab_index))

    summary_rows: list[dict[str, float | str]] = []
    scenario_rows: list[dict[str, float | str]] = []
    for pack in PACKS:
        summary, scenarios = evaluate_pack(train_rows, test_rows, pack)
        summary_rows.append(summary)
        scenario_rows.extend(scenarios)

    summary_rows = sorted(summary_rows, key=lambda row: float(row["overall_accuracy"]), reverse=True)
    write_csv(summary_rows, OUT / "low_dimensional_summary.csv")
    write_csv(scenario_rows, OUT / "low_dimensional_scenarios.csv")

    best = summary_rows[0]
    lines = [
        "# Boundary Access Low-Dimensional Chooser",
        "",
        "- question: how small can the chooser get before it stops traveling across worlds?",
        f"- best pack: `{best['pack']}`",
        f"- dimensions: `{int(best['dimensions'])}`",
        f"- overall held-out accuracy: `{float(best['overall_accuracy']):.3f}`",
        "",
        "Ranking:",
    ]
    for row in summary_rows:
        lines.append(
            f"- {row['pack']} ({int(row['dimensions'])}D): `{float(row['overall_accuracy']):.3f}`"
        )
    lines.extend(["", "Best-pack scenario breakdown:"])
    for row in sorted(
        [item for item in scenario_rows if item["pack"] == best["pack"]],
        key=lambda item: str(item["scenario"]),
    ):
        lines.append(f"- {row['scenario']}: `{float(row['accuracy']):.3f}`")
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
