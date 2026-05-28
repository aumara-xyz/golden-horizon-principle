#!/usr/bin/env python3
"""v27 shootout between the two strongest surviving toy families.

This panel does not add a new metaphor. It compares:
- v19b model_revision_witness
- v23 boundary_pocket

Both are graded with the same downstream score and the same null pressure.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import golden_zipper_v19b_model_revision_robustness as v19b
import golden_zipper_v23_boundary_pocket_attractor as v23


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v27_outputs"

SEED = 20260521
RNG = np.random.default_rng(SEED)

LOOKAHEAD = 6
STABILITY_HORIZON = 3


@dataclass(frozen=True)
class BranchSpec:
    name: str
    label: str


BRANCHES = [
    BranchSpec("model_revision_witness", "Model Revision + Witness"),
    BranchSpec("boundary_pocket", "Boundary Pocket"),
]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(rows: list[dict], path: Path) -> None:
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


def block_shuffle_surrogate(seq: np.ndarray, block: int = 8) -> np.ndarray:
    chunks = [seq[idx : idx + block].copy() for idx in range(0, len(seq), block)]
    RNG.shuffle(chunks)
    return np.concatenate(chunks).astype(np.int8)


def first_order_markov_surrogate(seq: np.ndarray) -> np.ndarray:
    values = np.unique(seq)
    index = {value: idx for idx, value in enumerate(values)}
    counts = np.zeros((len(values), len(values)), dtype=float)
    starts = np.zeros(len(values), dtype=float)
    starts[index[int(seq[0])]] += 1.0
    for left, right in zip(seq[:-1], seq[1:]):
        counts[index[int(left)], index[int(right)]] += 1.0
    row_sums = counts.sum(axis=1, keepdims=True)
    probs = np.divide(counts, row_sums, out=np.full_like(counts, 1.0 / len(values)), where=row_sums > 0)
    start_probs = starts / starts.sum()
    out = np.empty_like(seq)
    out[0] = RNG.choice(values, p=start_probs)
    for idx in range(1, len(seq)):
        out[idx] = RNG.choice(values, p=probs[index[int(out[idx - 1])]])
    return out.astype(np.int8)


def witness_conversion_proxy(seq: np.ndarray) -> float:
    witness_idx = np.flatnonzero(seq == 0)
    if len(witness_idx) == 0:
        return 0.0
    hits = 0
    for idx in witness_idx:
        tail = seq[idx + 1 : idx + 1 + LOOKAHEAD]
        if np.any(tail == 1):
            first_write = int(np.flatnonzero(tail == 1)[0])
            first_neg = np.flatnonzero(tail < 0)
            if len(first_neg) == 0 or first_write < int(first_neg[0]):
                hits += 1
    return hits / len(witness_idx)


def write_persistence(seq: np.ndarray) -> float:
    write_idx = np.flatnonzero(seq == 1)
    if len(write_idx) == 0:
        return 0.0
    stable = 0
    for idx in write_idx:
        tail = seq[idx : idx + STABILITY_HORIZON]
        if np.mean(tail >= 0) >= 2.0 / 3.0:
            stable += 1
    return stable / len(write_idx)


def generic_metrics(seq: np.ndarray) -> dict[str, float]:
    seq = seq.astype(np.int8)
    write_count = float(np.sum(seq == 1))
    witness_count = float(np.sum(seq == 0))
    admitted = write_count + witness_count
    activity_rate = admitted / max(len(seq), 1)
    delayed_retention = write_count / max(admitted, 1.0)
    pollution = float(np.mean((seq[:-1] == 1) & (seq[1:] < 0))) if len(seq) > 1 else 0.0
    overload_rate = float(np.mean(seq == 2))
    return {
        "write_count": write_count,
        "witness_count": witness_count,
        "activity_rate": activity_rate,
        "delayed_retention": delayed_retention,
        "witness_conversion_proxy": witness_conversion_proxy(seq),
        "write_persistence": write_persistence(seq),
        "pollution": pollution,
        "overload_rate": overload_rate,
        "phase_lock_resistance": v23.phase_lock_resistance(seq),
    }


def generic_score(metrics: dict[str, float]) -> float:
    balanced_activity = 1.0 - min(abs(metrics["activity_rate"] - 0.08) / 0.08, 1.0)
    return float(
        0.22 * metrics["phase_lock_resistance"]
        + 0.20 * metrics["witness_conversion_proxy"]
        + 0.18 * metrics["write_persistence"]
        + 0.16 * metrics["delayed_retention"]
        + 0.10 * balanced_activity
        + 0.08 * (1.0 - metrics["pollution"])
        + 0.06 * (1.0 - metrics["overload_rate"])
    )


def shared_anchors() -> dict[str, float]:
    anchors = {anchor.name: anchor.alpha for anchor in v19b.build_anchors()}
    flows = {flow.name: flow.alpha for flow in v23.build_flows()}
    names = sorted(set(anchors) & set(flows))
    return {name: anchors[name] for name in names}


def run_model_revision(anchor_name: str, alpha: float) -> list[dict]:
    rows: list[dict] = []
    for condition in v19b.build_conditions():
        for offset in v19b.OFFSET_GRID:
            shifted = alpha + float(offset)
            if not (0.0 < shifted < 1.0):
                continue
            seq, _ = v19b.build_sequence("model_revision_witness", shifted, condition)
            metrics = generic_metrics(seq)
            rows.append(
                {
                    "branch": "model_revision_witness",
                    "anchor": anchor_name,
                    "alpha": shifted,
                    "offset": float(offset),
                    "window_width": condition.window_width,
                    "beta": condition.beta,
                    "score_a": condition.learning_rate,
                    "score_b": condition.model_rate,
                    "score_c": condition.surprise_high,
                    "score_d": condition.revision_threshold,
                    "score_e": condition.coherence_limit,
                    "score_f": condition.write_threshold,
                    **metrics,
                    "generic_score": generic_score(metrics),
                }
            )
    return rows


def run_boundary_pocket(anchor_name: str, alpha: float) -> list[dict]:
    rows: list[dict] = []
    for condition in v23.build_conditions():
        for offset in v23.OFFSET_GRID:
            shifted = alpha + float(offset)
            if not (0.0 < shifted < 1.0):
                continue
            seq, _ = v23.build_sequence(shifted, condition)
            metrics = generic_metrics(seq)
            rows.append(
                {
                    "branch": "boundary_pocket",
                    "anchor": anchor_name,
                    "alpha": shifted,
                    "offset": float(offset),
                    "window_width": condition.window_width,
                    "beta": condition.beta,
                    "score_a": condition.pocket_gain,
                    "score_b": condition.pocket_decay,
                    "score_c": condition.write_threshold,
                    "score_d": condition.release_threshold,
                    "score_e": condition.overload_threshold,
                    **metrics,
                    "generic_score": generic_score(metrics),
                }
            )
    return rows


def rebuild_sequence(best_row: dict) -> np.ndarray:
    if best_row["branch"] == "model_revision_witness":
        condition = v19b.Condition(
            window_width=best_row["window_width"],
            beta=best_row["beta"],
            learning_rate=best_row["score_a"],
            model_rate=best_row["score_b"],
            surprise_high=best_row["score_c"],
            revision_threshold=best_row["score_d"],
            coherence_limit=best_row["score_e"],
            write_threshold=best_row["score_f"],
        )
        seq, _ = v19b.build_sequence("model_revision_witness", best_row["alpha"], condition)
        return seq
    condition = v23.Condition(
        window_width=best_row["window_width"],
        beta=best_row["beta"],
        pocket_gain=best_row["score_a"],
        pocket_decay=best_row["score_b"],
        write_threshold=best_row["score_c"],
        release_threshold=best_row["score_d"],
        overload_threshold=best_row["score_e"],
    )
    seq, _ = v23.build_sequence(best_row["alpha"], condition)
    return seq


def plot_branch_summary(rows: list[dict], path: Path) -> None:
    labels = [row["branch"] for row in rows]
    scores = [row["mean_generic_score"] for row in rows]
    density = [row["density_gap"] for row in rows]
    block = [row["block_gap"] for row in rows]
    markov = [row["markov_gap"] for row in rows]
    x = np.arange(len(labels))
    width = 0.2
    plt.figure(figsize=(10, 5))
    plt.bar(x - 1.5 * width, scores, width=width, label="mean score")
    plt.bar(x - 0.5 * width, density, width=width, label="density gap")
    plt.bar(x + 0.5 * width, block, width=width, label="block gap")
    plt.bar(x + 1.5 * width, markov, width=width, label="markov gap")
    plt.axhline(0.0, color="black", linewidth=1.0)
    plt.xticks(x, labels, rotation=15)
    plt.tight_layout()
    plt.legend()
    plt.savefig(path, dpi=180)
    plt.close()


def main() -> None:
    ensure_dir(OUT)
    anchors = shared_anchors()

    direct_rows: list[dict] = []
    for anchor_name, alpha in anchors.items():
        direct_rows.extend(run_model_revision(anchor_name, alpha))
        direct_rows.extend(run_boundary_pocket(anchor_name, alpha))

    branch_rows: list[dict] = []
    for branch in BRANCHES:
        subset = [row for row in direct_rows if row["branch"] == branch.name]
        best = max(subset, key=lambda row: row["generic_score"])
        seq = rebuild_sequence(best)
        density_metrics = generic_metrics(v23.density_random_surrogate(seq))
        block_metrics = generic_metrics(block_shuffle_surrogate(seq))
        markov_metrics = generic_metrics(first_order_markov_surrogate(seq))
        mean_score = float(np.mean([row["generic_score"] for row in subset]))
        branch_rows.append(
            {
                "branch": branch.name,
                "label": branch.label,
                "best_anchor": best["anchor"],
                "best_score": best["generic_score"],
                "mean_generic_score": mean_score,
                "mean_witness_conversion": float(np.mean([row["witness_conversion_proxy"] for row in subset])),
                "mean_write_persistence": float(np.mean([row["write_persistence"] for row in subset])),
                "mean_delayed_retention": float(np.mean([row["delayed_retention"] for row in subset])),
                "mean_overload_rate": float(np.mean([row["overload_rate"] for row in subset])),
                "density_gap": mean_score - generic_score(density_metrics),
                "block_gap": mean_score - generic_score(block_metrics),
                "markov_gap": mean_score - generic_score(markov_metrics),
            }
        )

    anchor_rows: list[dict] = []
    for branch in BRANCHES:
        for anchor_name in anchors:
            subset = [row for row in direct_rows if row["branch"] == branch.name and row["anchor"] == anchor_name]
            anchor_rows.append(
                {
                    "branch": branch.name,
                    "anchor": anchor_name,
                    "mean_generic_score": float(np.mean([row["generic_score"] for row in subset])),
                    "best_generic_score": float(np.max([row["generic_score"] for row in subset])),
                    "mean_witness_conversion": float(np.mean([row["witness_conversion_proxy"] for row in subset])),
                    "mean_write_persistence": float(np.mean([row["write_persistence"] for row in subset])),
                }
            )

    ranked = sorted(branch_rows, key=lambda row: row["mean_generic_score"], reverse=True)
    winner = ranked[0]
    runner_up = ranked[1]

    write_csv(direct_rows, OUT / "direct_metrics.csv")
    write_csv(branch_rows, OUT / "branch_summary.csv")
    write_csv(anchor_rows, OUT / "anchor_summary.csv")
    plot_branch_summary(branch_rows, OUT / "branch_summary.png")

    report = f"""# Golden Zipper v27 - Branch Shootout

Toy telemetry only. Not physics evidence. Not proof of GHP.

Shared anchors:
{", ".join(anchors.keys())}

Winner by mean generic score: `{winner['branch']}` with `{winner['mean_generic_score']:.3f}`

Runner-up:
- `{runner_up['branch']}` with `{runner_up['mean_generic_score']:.3f}`

Winner details:
- best anchor: `{winner['best_anchor']}`
- mean witness conversion: `{winner['mean_witness_conversion']:.3f}`
- mean write persistence: `{winner['mean_write_persistence']:.3f}`
- density gap: `{winner['density_gap']:.3f}`
- block gap: `{winner['block_gap']:.3f}`
- markov gap: `{winner['markov_gap']:.3f}`

Interpretation:
- This shootout removes family-specific scoring and asks which branch gives cleaner witness-to-write behavior under the same downstream score.
- A durable winner should keep positive null gaps while also preserving witness conversion and write persistence.
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"winner: {winner['branch']} {winner['mean_generic_score']:.3f}")
    print(f"runner_up: {runner_up['branch']} {runner_up['mean_generic_score']:.3f}")
    print(f"{winner['branch']} density gap: {winner['density_gap']:.3f}")
    print(f"{winner['branch']} block gap: {winner['block_gap']:.3f}")
    print(f"{winner['branch']} markov gap: {winner['markov_gap']:.3f}")


if __name__ == "__main__":
    main()
