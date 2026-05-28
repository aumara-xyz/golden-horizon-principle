#!/usr/bin/env python3
"""v28 hybrid: pocket witness plus model revision write law.

The goal is to keep the best part of v23 (real middle state)
while borrowing the strongest part of v19b (write when the observer's
model genuinely has to update).

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import golden_zipper_v23_boundary_pocket_attractor as v23


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v28_outputs"

SEED = 20260521
RNG = np.random.default_rng(SEED)

LENGTH = 3072
OFFSET_GRID = np.arange(-0.036, 0.0361, 0.012)
WINDOW_WIDTHS = [0.16, 0.24]
BETAS = [0.0, 0.011]
POCKET_GAINS = [0.14, 0.24, 0.36]
POCKET_DECAYS = [0.88, 0.94, 0.98]
WRITE_THRESHOLDS = [0.50, 0.68]
REVISION_THRESHOLDS = [0.05, 0.10, 0.16]
LEARNING_RATES = [0.03, 0.07, 0.13]
COHERENCE_LIMITS = [0.22, 0.38, 0.56]
RELEASE_THRESHOLDS = [0.08, 0.14]
OVERLOAD_THRESHOLDS = [1.10, 1.45]
MAX_CONDITIONS = 84


@dataclass(frozen=True)
class FlowSpec:
    name: str
    alpha: float
    family: str


@dataclass(frozen=True)
class Condition:
    window_width: float
    beta: float
    pocket_gain: float
    pocket_decay: float
    write_threshold: float
    revision_threshold: float
    learning_rate: float
    coherence_limit: float
    release_threshold: float
    overload_threshold: float


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


def build_flows() -> list[FlowSpec]:
    return [FlowSpec(flow.name, flow.alpha, flow.family) for flow in v23.build_flows()]


def build_conditions() -> list[Condition]:
    full = [
        Condition(
            window_width=window_width,
            beta=beta,
            pocket_gain=pocket_gain,
            pocket_decay=pocket_decay,
            write_threshold=write_threshold,
            revision_threshold=revision_threshold,
            learning_rate=learning_rate,
            coherence_limit=coherence_limit,
            release_threshold=release_threshold,
            overload_threshold=overload_threshold,
        )
        for window_width in WINDOW_WIDTHS
        for beta in BETAS
        for pocket_gain in POCKET_GAINS
        for pocket_decay in POCKET_DECAYS
        for write_threshold in WRITE_THRESHOLDS
        for revision_threshold in REVISION_THRESHOLDS
        for learning_rate in LEARNING_RATES
        for coherence_limit in COHERENCE_LIMITS
        for release_threshold in RELEASE_THRESHOLDS
        for overload_threshold in OVERLOAD_THRESHOLDS
    ]
    if len(full) <= MAX_CONDITIONS:
        return full
    picks = np.sort(RNG.choice(len(full), size=MAX_CONDITIONS, replace=False))
    return [full[idx] for idx in picks]


def build_sequence(alpha: float, condition: Condition) -> tuple[np.ndarray, dict[str, float]]:
    hidden = v23.build_hidden_trace(alpha, condition)
    seq = np.full(LENGTH, -2, dtype=np.int8)

    pocket = 0.0
    pocket_open = False
    pocket_age = 0
    prediction = 0.25

    writes = 0
    witnesses = 0
    releases = 0
    overloads = 0
    witness_to_write = 0
    revision_writes = 0
    pocket_lifetimes: list[int] = []
    revision_sizes: list[float] = []

    for idx in range(1, LENGTH):
        prev = hidden[idx - 1]
        cur = hidden[idx]
        distance_to_zero = abs(cur)
        near_boundary = distance_to_zero <= condition.window_width
        approach = max(0.0, condition.window_width - distance_to_zero) / max(condition.window_width, 1e-9)
        slope = abs(cur - prev)
        coherence = 1.0 - min(abs(cur - prev) / 1.4, 1.0)
        contact_quality = 0.6 * approach + 0.25 * slope + 0.15 * coherence

        surprise = abs(contact_quality - prediction)
        proposed_prediction = (1.0 - condition.learning_rate) * prediction + condition.learning_rate * contact_quality
        revision_size = abs(proposed_prediction - prediction)
        revision_sizes.append(revision_size)

        pocket *= condition.pocket_decay
        if pocket_open:
            pocket_age += 1

        if near_boundary:
            pocket += condition.pocket_gain * contact_quality
            if not pocket_open:
                seq[idx] = 0
                witnesses += 1
                pocket_open = True
                pocket_age = 0

        if pocket >= condition.overload_threshold:
            seq[idx] = 2
            overloads += 1
            if pocket_open:
                pocket_lifetimes.append(pocket_age)
            pocket = 0.0
            pocket_open = False
            pocket_age = 0
            prediction = 0.9 * prediction + 0.1 * proposed_prediction
            continue

        revision_ok = revision_size >= condition.revision_threshold and abs(proposed_prediction - 0.5) <= condition.coherence_limit
        intense_ok = surprise >= 0.24 and abs(proposed_prediction - 0.5) <= condition.coherence_limit
        if pocket_open and near_boundary and pocket >= condition.write_threshold and (revision_ok or intense_ok):
            seq[idx] = 1
            writes += 1
            witness_to_write += 1
            revision_writes += 1 if revision_ok or intense_ok else 0
            pocket_lifetimes.append(pocket_age)
            pocket *= 0.35
            pocket_open = False
            pocket_age = 0
            prediction = proposed_prediction
            continue

        if pocket_open and pocket <= condition.release_threshold and not near_boundary:
            seq[idx] = -1
            releases += 1
            pocket_lifetimes.append(pocket_age)
            pocket = 0.0
            pocket_open = False
            pocket_age = 0

        if seq[idx] >= 0:
            prediction = proposed_prediction
        else:
            prediction = 0.995 * prediction + 0.005 * proposed_prediction

    return seq, {
        "writes": float(writes),
        "witnesses": float(witnesses),
        "releases": float(releases),
        "overloads": float(overloads),
        "witness_to_write": float(witness_to_write),
        "revision_writes": float(revision_writes),
        "mean_pocket_lifetime": float(np.mean(pocket_lifetimes)) if pocket_lifetimes else 0.0,
        "mean_revision_size": float(np.mean(revision_sizes)) if revision_sizes else 0.0,
    }


def evaluate_model(seq: np.ndarray, diag: dict[str, float]) -> dict[str, float]:
    writes = diag["writes"]
    witnesses = diag["witnesses"]
    releases = diag["releases"]
    overloads = diag["overloads"]
    total_events = writes + witnesses + releases + overloads
    witness_conversion = diag["witness_to_write"] / max(witnesses, 1.0)
    delayed_retention = writes / max(writes + witnesses, 1.0)
    release_rate = releases / max(total_events, 1.0)
    overload_rate = overloads / max(total_events, 1.0)
    pollution = float(np.mean((seq[:-1] == 1) & (seq[1:] <= -1))) if len(seq) > 1 else 0.0
    revision_write_rate = diag["revision_writes"] / max(writes, 1.0)
    return {
        "write_count": writes,
        "witness_count": witnesses,
        "witness_conversion": witness_conversion,
        "delayed_retention": delayed_retention,
        "release_rate": release_rate,
        "overload_rate": overload_rate,
        "mean_pocket_lifetime": diag["mean_pocket_lifetime"],
        "mean_revision_size": diag["mean_revision_size"],
        "revision_write_rate": revision_write_rate,
        "pollution": pollution,
        "phase_lock_resistance": v23.phase_lock_resistance(seq),
    }


def composite_score(metrics: dict[str, float]) -> float:
    pocket_lifetime = min(metrics["mean_pocket_lifetime"] / 8.0, 1.0)
    revision_signal = min(metrics["mean_revision_size"] / 0.08, 1.0)
    return float(
        0.18 * metrics["phase_lock_resistance"]
        + 0.18 * metrics["witness_conversion"]
        + 0.16 * metrics["delayed_retention"]
        + 0.12 * pocket_lifetime
        + 0.12 * metrics["revision_write_rate"]
        + 0.10 * revision_signal
        + 0.08 * (1.0 - metrics["pollution"])
        + 0.06 * (1.0 - metrics["overload_rate"])
    )


def plot_flow_summary(rows: list[dict], path: Path) -> None:
    labels = [row["flow"] for row in rows]
    scores = [row["mean_composite"] for row in rows]
    witness = [row["mean_witness_conversion"] for row in rows]
    x = np.arange(len(labels))
    width = 0.35
    plt.figure(figsize=(10, 5))
    plt.bar(x - width / 2, scores, width=width, label="mean composite")
    plt.bar(x + width / 2, witness, width=width, label="witness conversion")
    plt.xticks(x, labels, rotation=20)
    plt.tight_layout()
    plt.legend()
    plt.savefig(path, dpi=180)
    plt.close()


def main() -> None:
    ensure_dir(OUT)
    flows = build_flows()
    conditions = build_conditions()

    direct_rows: list[dict] = []
    for flow in flows:
        print(f"flow: {flow.name}")
        for condition in conditions:
            for offset in OFFSET_GRID:
                alpha = flow.alpha + float(offset)
                if not (0.0 < alpha < 1.0):
                    continue
                seq, diag = build_sequence(alpha, condition)
                metrics = evaluate_model(seq, diag)
                direct_rows.append(
                    {
                        "flow": flow.name,
                        "family": flow.family,
                        "alpha": alpha,
                        "offset": float(offset),
                        "window_width": condition.window_width,
                        "beta": condition.beta,
                        "pocket_gain": condition.pocket_gain,
                        "pocket_decay": condition.pocket_decay,
                        "write_threshold": condition.write_threshold,
                        "revision_threshold": condition.revision_threshold,
                        "learning_rate": condition.learning_rate,
                        "coherence_limit": condition.coherence_limit,
                        "release_threshold": condition.release_threshold,
                        "overload_threshold": condition.overload_threshold,
                        **metrics,
                        "composite_score": composite_score(metrics),
                    }
                )

    flow_rows: list[dict] = []
    for flow in flows:
        subset = [row for row in direct_rows if row["flow"] == flow.name]
        best = max(subset, key=lambda row: row["composite_score"])
        cond = Condition(
            window_width=best["window_width"],
            beta=best["beta"],
            pocket_gain=best["pocket_gain"],
            pocket_decay=best["pocket_decay"],
            write_threshold=best["write_threshold"],
            revision_threshold=best["revision_threshold"],
            learning_rate=best["learning_rate"],
            coherence_limit=best["coherence_limit"],
            release_threshold=best["release_threshold"],
            overload_threshold=best["overload_threshold"],
        )
        seq, _ = build_sequence(best["alpha"], cond)
        density = v23.density_random_surrogate(seq)
        density_metrics = evaluate_model(
            density,
            {
                "writes": float(np.sum(density == 1)),
                "witnesses": float(np.sum(density == 0)),
                "releases": float(np.sum(density == -1)),
                "overloads": float(np.sum(density == 2)),
                "witness_to_write": 0.0,
                "revision_writes": 0.0,
                "mean_pocket_lifetime": 0.0,
                "mean_revision_size": 0.0,
            },
        )
        mean_composite = float(np.mean([row["composite_score"] for row in subset]))
        flow_rows.append(
            {
                "flow": flow.name,
                "family": flow.family,
                "best_composite": best["composite_score"],
                "mean_composite": mean_composite,
                "mean_witness_conversion": float(np.mean([row["witness_conversion"] for row in subset])),
                "mean_revision_write_rate": float(np.mean([row["revision_write_rate"] for row in subset])),
                "mean_delayed_retention": float(np.mean([row["delayed_retention"] for row in subset])),
                "mean_overload_rate": float(np.mean([row["overload_rate"] for row in subset])),
                "mean_density_gap": mean_composite - composite_score(density_metrics),
            }
        )

    ranked = sorted(flow_rows, key=lambda row: row["mean_composite"], reverse=True)
    write_csv(direct_rows, OUT / "direct_metrics.csv")
    write_csv(flow_rows, OUT / "flow_summary.csv")
    plot_flow_summary(flow_rows, OUT / "flow_summary.png")

    best = ranked[0]
    golden = next(row for row in flow_rows if row["flow"] == "golden")
    report = f"""# Golden Zipper v28 - Revision Pocket Hybrid

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best flow by mean composite: `{best['flow']}` with `{best['mean_composite']:.3f}`

Golden result:
- mean composite: `{golden['mean_composite']:.3f}`
- witness conversion: `{golden['mean_witness_conversion']:.3f}`
- revision-write rate: `{golden['mean_revision_write_rate']:.3f}`
- delayed retention: `{golden['mean_delayed_retention']:.3f}`
- density gap: `{golden['mean_density_gap']:.3f}`

Interpretation:
- This hybrid asks whether a pocket should only become a memory write when it also forces a model update.
- A durable positive would improve witness conversion without giving up the positive gap.
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best flow by mean composite: {best['flow']}")
    print(f"golden mean composite: {golden['mean_composite']:.3f}")
    print(f"golden witness conversion: {golden['mean_witness_conversion']:.3f}")
    print(f"golden revision-write rate: {golden['mean_revision_write_rate']:.3f}")
    print(f"golden delayed retention: {golden['mean_delayed_retention']:.3f}")
    print(f"golden density gap: {golden['mean_density_gap']:.3f}")


if __name__ == "__main__":
    main()
