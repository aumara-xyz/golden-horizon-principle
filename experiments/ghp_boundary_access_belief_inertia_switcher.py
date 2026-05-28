#!/usr/bin/env python3
"""Compact switcher using familiarity, surprise, and current-state inertia.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import ghp_boundary_access_local_switcher as local_switcher


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_belief_inertia_switcher_outputs"

AXIS_NAMES = [
    "familiarity",
    "surprise",
    "inertia",
    "openness",
    "deep_pull",
    "wake_pull",
    "novel_but_fits",
    "foreign_pressure",
    "novel_fit_raw",
    "foreign_pressure_raw",
    "belief_tension",
]

PACKS = {
    "feelings_only": [0, 1],
    "inertia_only": [2],
    "feelings_plus_inertia": [0, 1, 2],
    "compass_only": [6, 7],
    "raw_compass_only": [8, 9],
    "groove_compass": [0, 1, 2, 6, 7],
    "raw_groove_compass": [0, 1, 8, 9],
    "all_axes": list(range(len(AXIS_NAMES))),
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


def derive_axes(
    damaged: np.ndarray,
    helper: np.ndarray,
    wake: np.ndarray,
    deep_trace: np.ndarray,
) -> np.ndarray:
    base = local_switcher.base
    helper_wake_cos = float(base.cosine(helper, wake))
    helper_deep_cos = float(base.cosine(helper, deep_trace))
    damage_wake_cos = float(base.cosine(damaged, wake))
    wake_deep_cos = float(base.cosine(wake, deep_trace))
    entropy_gap = abs(float(base.entropy_score(damaged)) - float(base.entropy_score(helper)))

    familiarity = 0.5 * (helper_wake_cos + helper_deep_cos)
    surprise = 0.5 * ((1.0 - damage_wake_cos) + entropy_gap)
    inertia = wake_deep_cos
    openness = 1.0 - inertia
    deep_pull = helper_deep_cos * inertia
    wake_pull = helper_wake_cos * inertia
    novel_but_fits = surprise * familiarity * inertia
    foreign_pressure = surprise * (1.0 - familiarity) * inertia
    novel_fit_raw = surprise * familiarity
    foreign_pressure_raw = surprise * (1.0 - familiarity)
    belief_tension = abs(helper_wake_cos - helper_deep_cos)
    return np.array(
        [
            familiarity,
            surprise,
            inertia,
            openness,
            deep_pull,
            wake_pull,
            novel_but_fits,
            foreign_pressure,
            novel_fit_raw,
            foreign_pressure_raw,
            belief_tension,
        ],
        dtype=float,
    )


def collect_rows(seed: int, words: dict[str, str], vocab_index: dict[str, int]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    base = local_switcher.base
    event = local_switcher.event
    groove = local_switcher.groove
    hardening = local_switcher.hardening
    wrong_variants = local_switcher.wrong_variants

    old_rng = event.loop.RNG
    event.loop.RNG = np.random.default_rng(seed)
    try:
        for family_name in local_switcher.FAMILY_NAMES:
            word = words[family_name]
            cross_family_name = "generic_ternary" if family_name != "generic_ternary" else "fibonacci"
            cross_truth = base.full_histogram(words[cross_family_name], base.KMER, vocab_index)
            limit = len(word) - base.KMER + 1

            for noise_level in local_switcher.NOISE_LEVELS:
                scenario = {
                    "name": f"uniform_{noise_level:.2f}",
                    "helper_kind": "uniform_mix",
                    "noise_level": noise_level,
                }
                for variant in local_switcher.INTERNAL_VARIANTS + local_switcher.COHERENT_VARIANTS:
                    for _ in range(event.loop.TRIALS):
                        start_a = int(event.loop.RNG.integers(0, limit))
                        start_b = int(event.loop.RNG.integers(0, limit))
                        wake = np.zeros(len(vocab_index), dtype=float)
                        deep_trace = np.zeros(len(vocab_index), dtype=float)
                        prev_b = np.zeros(len(vocab_index), dtype=float)

                        for step in range(event.loop.TIMESTEPS - 1):
                            current_a = event.loop.base.histogram_from_positions(
                                word,
                                event.loop.chunk_positions(len(word), event.loop.CHUNK, start_a + step),
                                event.loop.base.KMER,
                                vocab_index,
                            )
                            current_b = event.loop.base.histogram_from_positions(
                                word,
                                event.loop.chunk_positions(len(word), event.loop.SECOND_CHUNK, start_b + 2 * step),
                                event.loop.base.KMER,
                                vocab_index,
                            )

                            readable_a = event.loop.normalize(current_a)
                            readable_b = event.loop.normalize(current_b)
                            helper = hardening.helper_view(scenario, readable_b, prev_b, readable_b)

                            wake = event.loop.normalize(event.WAKE_DECAY * wake + 0.5 * readable_a + 0.5 * helper)
                            deep_trace = event.loop.normalize(groove.DEEP_DECAY * deep_trace + (1.0 - groove.DEEP_DECAY) * wake)

                            if float(event.loop.RNG.random()) >= event.DAMAGE_PROB:
                                prev_b = readable_b
                                continue

                            damaged = event.loop.normalize(wrong_variants.wrong_signal(variant, readable_a, cross_truth))
                            rows.append(
                                {
                                    "seed": seed,
                                    "variant": variant,
                                    "noise_level": noise_level,
                                    "label": 1 if variant in local_switcher.COHERENT_VARIANTS else 0,
                                    "target_family": "fibonacci"
                                    if variant in local_switcher.COHERENT_VARIANTS
                                    else "generic_ternary",
                                    "features": derive_axes(damaged, helper, wake, deep_trace),
                                }
                            )
                            prev_b = readable_b
    finally:
        event.loop.RNG = old_rng
    return rows


def select_axes(rows: list[dict[str, object]], indices: list[int]) -> list[dict[str, object]]:
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
        familiarity, surprise, inertia, _, _, _, novel_but_fits, foreign_pressure, _, _, _ = np.asarray(
            row["features"], dtype=float
        )
        if novel_but_fits >= foreign_pressure and familiarity >= 0.78 and inertia >= 0.78 and surprise >= 0.45:
            chosen.append("fibonacci")
        else:
            chosen.append("generic_ternary")
    accuracy = np.mean([choice == row["target_family"] for choice, row in zip(chosen, test_rows)])
    return {
        "pack": "simple_inertia_heuristic",
        "target_family_accuracy": float(accuracy),
    }


def summarize_axes(rows: list[dict[str, object]]) -> list[dict[str, float | str]]:
    summary: list[dict[str, float | str]] = []
    groups = [
        ("fibonacci_target", [row for row in rows if row["target_family"] == "fibonacci"]),
        ("generic_ternary_target", [row for row in rows if row["target_family"] == "generic_ternary"]),
        ("coherent_variant", [row for row in rows if row["variant"] == "cross_family"]),
        ("internal_scramble", [row for row in rows if row["variant"] != "cross_family"]),
    ]
    for key, subset in groups:
        axes = np.vstack([np.asarray(row["features"], dtype=float) for row in subset])
        mean_axes = axes.mean(axis=0)
        row: dict[str, float | str] = {"group": key}
        for name, value in zip(AXIS_NAMES, mean_axes.tolist()):
            row[name] = float(value)
        summary.append(row)
    return summary


def main() -> None:
    ensure_dir(OUT)
    words = local_switcher.build_words()
    vocab = local_switcher.base.collect_vocabulary(words, local_switcher.base.KMER)
    vocab_index = {token: idx for idx, token in enumerate(vocab)}

    train_rows: list[dict[str, object]] = []
    test_rows: list[dict[str, object]] = []
    for seed in local_switcher.TRAIN_SEEDS:
        train_rows.extend(collect_rows(seed, words, vocab_index))
    for seed in local_switcher.TEST_SEEDS:
        test_rows.extend(collect_rows(seed, words, vocab_index))

    rows = [evaluate_pack(name, indices, train_rows, test_rows) for name, indices in PACKS.items()]
    rows.append(evaluate_heuristic(test_rows))
    rows = sorted(rows, key=lambda row: float(row["target_family_accuracy"]), reverse=True)
    write_csv(rows, OUT / "belief_inertia_summary.csv")

    axis_rows = summarize_axes(test_rows)
    write_csv(axis_rows, OUT / "axis_summary.csv")

    best = rows[0]
    lines = [
        "# Boundary Access Belief-Inertia Switcher",
        "",
        f"- best compact pack: `{best['pack']}` `{float(best['target_family_accuracy']):.3f}`",
        "- compare to full local switcher: about `0.890`",
        "- compare to strange-familiar compact pack: about `0.837`",
        "",
        "Ranking:",
    ]
    for row in rows:
        lines.append(f"- {row['pack']}: `{float(row['target_family_accuracy']):.3f}`")
    lines.extend(["", "Held-out axis means:"])
    for row in axis_rows:
        axis_bits = ", ".join(f"{name} `{float(row[name]):.3f}`" for name in AXIS_NAMES)
        lines.append(f"- {row['group']}: {axis_bits}")
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
