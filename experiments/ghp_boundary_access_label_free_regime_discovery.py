#!/usr/bin/env python3
"""Label-free regime discovery for Boundary Access selector features.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import ghp_boundary_access_belief_inertia_switcher as inertia_switcher
import ghp_boundary_access_local_switcher as local_switcher
import ghp_boundary_access_selector_generalization as generalization
import ghp_boundary_access_strange_familiar_switcher as belief_switcher


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_access_label_free_regime_discovery_outputs"

REPRESENTATIONS = [
    ("base_features", local_switcher.FEATURE_NAMES),
    ("strange_features", belief_switcher.AXIS_NAMES),
    ("groove_features", [inertia_switcher.AXIS_NAMES[i] for i in inertia_switcher.PACKS["groove_compass"]]),
    ("belief_features", inertia_switcher.AXIS_NAMES),
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


def matrix_from_rows(rows: list[dict[str, object]], key: str) -> np.ndarray:
    return np.vstack([np.asarray(row[key], dtype=float) for row in rows]).astype(float)


def zscore_fit(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = x.mean(axis=0)
    std = x.std(axis=0)
    std[std == 0.0] = 1.0
    return mean, std


def zscore_apply(x: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    norm = (x - mean) / std
    return np.nan_to_num(norm, nan=0.0, posinf=0.0, neginf=0.0)


def seeded_centroids(x: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    first = int(rng.integers(0, len(x)))
    distances = np.sum((x - x[first]) ** 2, axis=1)
    second = int(np.argmax(distances))
    return np.vstack([x[first], x[second]])


def kmeans_two(x: np.ndarray, seed: int, restarts: int = 12, iterations: int = 40) -> tuple[np.ndarray, np.ndarray, float]:
    best_assignments: np.ndarray | None = None
    best_centroids: np.ndarray | None = None
    best_loss = float("inf")
    for restart in range(restarts):
        rng = np.random.default_rng(seed + restart)
        centroids = seeded_centroids(x, rng)
        assignments = np.zeros(len(x), dtype=int)
        for _ in range(iterations):
            distances = np.stack([np.sum((x - center) ** 2, axis=1) for center in centroids], axis=1)
            new_assignments = np.argmin(distances, axis=1)
            if np.array_equal(new_assignments, assignments):
                break
            assignments = new_assignments
            for idx in range(2):
                members = x[assignments == idx]
                if len(members) == 0:
                    centroids[idx] = x[int(rng.integers(0, len(x)))]
                else:
                    centroids[idx] = members.mean(axis=0)
        loss = float(np.sum((x - centroids[assignments]) ** 2))
        if loss < best_loss:
            best_loss = loss
            best_assignments = assignments.copy()
            best_centroids = centroids.copy()
    assert best_assignments is not None and best_centroids is not None
    return best_assignments, best_centroids, best_loss


def nearest_centroid_assign(x: np.ndarray, centroids: np.ndarray) -> np.ndarray:
    distances = np.stack([np.sum((x - center) ** 2, axis=1) for center in centroids], axis=1)
    return np.argmin(distances, axis=1)


def target_codes(rows: list[dict[str, object]]) -> np.ndarray:
    return np.array([1 if row["target_family"] == "fibonacci" else 0 for row in rows], dtype=int)


def best_alignment_accuracy(assignments: np.ndarray, labels: np.ndarray) -> tuple[float, dict[int, int]]:
    mappings = [{0: 0, 1: 1}, {0: 1, 1: 0}]
    best_acc = -1.0
    best_mapping = mappings[0]
    for mapping in mappings:
        predicted = np.array([mapping[int(cluster)] for cluster in assignments], dtype=int)
        acc = float(np.mean(predicted == labels))
        if acc > best_acc:
            best_acc = acc
            best_mapping = mapping
    return best_acc, best_mapping


def scenario_accuracy(
    rows: list[dict[str, object]],
    assignments: np.ndarray,
    mapping: dict[int, int],
) -> list[dict[str, float | str]]:
    scenario_names = sorted({str(row["scenario"]) for row in rows})
    summary: list[dict[str, float | str]] = []
    labels = target_codes(rows)
    predicted = np.array([mapping[int(cluster)] for cluster in assignments], dtype=int)
    for scenario_name in scenario_names:
        indices = [idx for idx, row in enumerate(rows) if str(row["scenario"]) == scenario_name]
        acc = float(np.mean(predicted[indices] == labels[indices]))
        summary.append({"scenario": scenario_name, "transfer_accuracy": acc})
    return summary


def cluster_profile(
    centroids: np.ndarray,
    feature_names: list[str],
    mapping: dict[int, int],
) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for cluster_id, centroid in enumerate(centroids):
        semantic = "fibonacci_like" if mapping[cluster_id] == 1 else "generic_ternary_like"
        row: dict[str, float | str] = {"cluster": cluster_id, "semantic": semantic}
        for name, value in zip(feature_names, centroid.tolist()):
            row[name] = float(value)
        rows.append(row)
    return rows


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

    for rep_name, feature_names in REPRESENTATIONS:
        train_x = matrix_from_rows(train_rows, rep_name)
        test_x = matrix_from_rows(test_rows, rep_name)
        mean, std = zscore_fit(train_x)
        train_norm = zscore_apply(train_x, mean, std)
        test_norm = zscore_apply(test_x, mean, std)

        train_assign, centroids, loss = kmeans_two(train_norm, seed=20260528)
        test_assign = nearest_centroid_assign(test_norm, centroids)

        train_labels = target_codes(train_rows)
        test_labels = target_codes(test_rows)
        train_best_acc, train_mapping = best_alignment_accuracy(train_assign, train_labels)
        test_transfer_acc = float(
            np.mean(np.array([train_mapping[int(cluster)] for cluster in test_assign], dtype=int) == test_labels)
        )
        test_best_acc, _ = best_alignment_accuracy(test_assign, test_labels)

        summary_rows.append(
            {
                "representation": rep_name,
                "train_best_alignment": train_best_acc,
                "test_transfer_alignment": test_transfer_acc,
                "test_best_alignment": test_best_acc,
                "kmeans_loss": loss,
            }
        )

        for row in scenario_accuracy(test_rows, test_assign, train_mapping):
            row["representation"] = rep_name
            scenario_rows.append(row)

        write_csv(
            cluster_profile(centroids, feature_names, train_mapping),
            OUT / f"{rep_name}_cluster_profile.csv",
        )

    summary_rows = sorted(summary_rows, key=lambda row: float(row["test_transfer_alignment"]), reverse=True)
    write_csv(summary_rows, OUT / "label_free_summary.csv")
    write_csv(scenario_rows, OUT / "scenario_transfer_summary.csv")

    best = summary_rows[0]
    lines = [
        "# Boundary Access Label-Free Regime Discovery",
        "",
        f"- best representation: `{best['representation']}`",
        f"- held-out transfer alignment: `{float(best['test_transfer_alignment']):.3f}`",
        f"- held-out best alignment (oracle remap): `{float(best['test_best_alignment']):.3f}`",
        "",
        "Ranking:",
    ]
    for row in summary_rows:
        lines.append(
            "- "
            f"{row['representation']}: train-best `{float(row['train_best_alignment']):.3f}`, "
            f"test-transfer `{float(row['test_transfer_alignment']):.3f}`, "
            f"test-best `{float(row['test_best_alignment']):.3f}`"
        )
    lines.extend(["", "Held-out scenario transfer:"])
    for rep_name, _ in REPRESENTATIONS:
        lines.append(f"- `{rep_name}`")
        for row in sorted(
            [item for item in scenario_rows if item["representation"] == rep_name],
            key=lambda item: str(item["scenario"]),
        ):
            lines.append(f"  - {row['scenario']}: `{float(row['transfer_accuracy']):.3f}`")
    write_text(OUT / "report.md", "\n".join(lines) + "\n")
    print(f"files created: {OUT}")


if __name__ == "__main__":
    main()
