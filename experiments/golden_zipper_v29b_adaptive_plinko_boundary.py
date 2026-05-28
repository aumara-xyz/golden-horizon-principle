#!/usr/bin/env python3
"""v29b adaptive Plinko boundary.

v29 ruptured almost everything because it asked the observer to predict
raw hidden value. This version asks the observer to predict contact
likelihood at the zero-boundary instead.

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import golden_zipper_v23_boundary_pocket_attractor as v23


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v29b_outputs"

SEED = 20260522
RNG = np.random.default_rng(SEED)

LENGTH = 4096
OFFSET_GRID = np.arange(-0.036, 0.0361, 0.012)
WINDOW_WIDTHS = [0.14, 0.22, 0.30]
DELAYS = [2, 5, 8, 13, 21]
PREDICTION_GAINS = [0.04, 0.08, 0.14]
POCKET_GAINS = [0.12, 0.22, 0.34]
POCKET_DECAYS = [0.90, 0.95, 0.985]
FIT_LIMITS = [0.18, 0.30, 0.46]
REVISION_THRESHOLDS = [0.015, 0.035, 0.070]
WRITE_THRESHOLDS = [0.36, 0.52, 0.68]
RUPTURE_LIMITS = [0.58, 0.74, 0.90]
MAX_CONDITIONS = 144


@dataclass(frozen=True)
class FlowSpec:
    name: str
    alpha: float
    family: str


@dataclass(frozen=True)
class Condition:
    window_width: float
    delay: int
    prediction_gain: float
    pocket_gain: float
    pocket_decay: float
    fit_limit: float
    revision_threshold: float
    write_threshold: float
    rupture_limit: float


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
            delay=delay,
            prediction_gain=prediction_gain,
            pocket_gain=pocket_gain,
            pocket_decay=pocket_decay,
            fit_limit=fit_limit,
            revision_threshold=revision_threshold,
            write_threshold=write_threshold,
            rupture_limit=rupture_limit,
        )
        for window_width in WINDOW_WIDTHS
        for delay in DELAYS
        for prediction_gain in PREDICTION_GAINS
        for pocket_gain in POCKET_GAINS
        for pocket_decay in POCKET_DECAYS
        for fit_limit in FIT_LIMITS
        for revision_threshold in REVISION_THRESHOLDS
        for write_threshold in WRITE_THRESHOLDS
        for rupture_limit in RUPTURE_LIMITS
    ]
    if len(full) <= MAX_CONDITIONS:
        return full
    picks = np.sort(RNG.choice(len(full), size=MAX_CONDITIONS, replace=False))
    return [full[idx] for idx in picks]


def hidden_trace(alpha: float) -> np.ndarray:
    n = np.arange(LENGTH, dtype=float)
    core = np.sin(2.0 * np.pi * alpha * n)
    reverse = 0.30 * np.sin(2.0 * np.pi * (1.0 - alpha) * n + 0.21)
    slow = 0.18 * np.sin(2.0 * np.pi * (alpha / v23.PHI) * n + 0.37)
    return (core + reverse + slow).astype(float)


def contact_likelihood(value: float, window_width: float) -> float:
    return float(np.exp(-((abs(value) / max(window_width, 1e-9)) ** 2)))


def density_surrogate(seq: np.ndarray) -> np.ndarray:
    values, counts = np.unique(seq, return_counts=True)
    probs = counts / counts.sum()
    return RNG.choice(values, size=len(seq), p=probs).astype(np.int8)


def block_surrogate(seq: np.ndarray, block: int = 13) -> np.ndarray:
    chunks = [seq[idx : idx + block].copy() for idx in range(0, len(seq), block)]
    RNG.shuffle(chunks)
    return np.concatenate(chunks).astype(np.int8)


def build_sequence(alpha: float, condition: Condition) -> tuple[np.ndarray, dict[str, float]]:
    hidden = hidden_trace(alpha)
    seq = np.full(LENGTH, -2, dtype=np.int8)

    predicted_contact = 0.08
    contact_trend = 0.0
    pocket = 0.0
    pocket_open = False
    pocket_age = 0

    witnesses = 0
    writes = 0
    releases = 0
    ruptures = 0
    witness_to_write = 0
    prediction_updates = 0
    fit_errors: list[float] = []
    revision_sizes: list[float] = []
    pocket_ages: list[int] = []

    for idx in range(condition.delay + 2, LENGTH):
        delayed = hidden[idx - condition.delay]
        previous_delayed = hidden[idx - condition.delay - 1]
        contact = contact_likelihood(delayed, condition.window_width)
        prev_contact = contact_likelihood(previous_delayed, condition.window_width)
        predicted_now = float(np.clip(predicted_contact + condition.delay * contact_trend, 0.0, 1.0))

        fit_error = abs(contact - predicted_now)
        revision = condition.prediction_gain * (contact - predicted_now)
        revision_size = abs(revision)
        fit_errors.append(fit_error)
        revision_sizes.append(revision_size)

        near_boundary = contact >= 0.18
        fits_map = fit_error <= condition.fit_limit
        can_revise = revision_size >= condition.revision_threshold
        rupture = near_boundary and fit_error >= condition.rupture_limit and contact >= 0.55

        pocket *= condition.pocket_decay
        if pocket_open:
            pocket_age += 1

        if near_boundary and fits_map:
            quality = contact * (1.0 - fit_error / max(condition.fit_limit, 1e-9))
            pocket += condition.pocket_gain * max(quality, 0.0)
            if not pocket_open:
                seq[idx] = 0
                witnesses += 1
                pocket_open = True
                pocket_age = 0

        if rupture:
            seq[idx] = 2
            ruptures += 1
            if pocket_open:
                pocket_ages.append(pocket_age)
            pocket = 0.0
            pocket_open = False
            pocket_age = 0
            predicted_contact = 0.98 * predicted_contact + 0.02 * contact
            contact_trend = 0.98 * contact_trend + 0.02 * (contact - prev_contact)
            continue

        if pocket_open and pocket >= condition.write_threshold and can_revise and fits_map:
            seq[idx] = 1
            writes += 1
            witness_to_write += 1
            prediction_updates += 1
            pocket_ages.append(pocket_age)
            pocket *= 0.4
            pocket_open = False
            pocket_age = 0
            predicted_contact = float(np.clip(predicted_now + revision, 0.0, 1.0))
            contact_trend = (1.0 - condition.prediction_gain) * contact_trend + condition.prediction_gain * (contact - prev_contact)
            continue

        if pocket_open and pocket < 0.045 and not near_boundary:
            seq[idx] = -1
            releases += 1
            pocket_ages.append(pocket_age)
            pocket = 0.0
            pocket_open = False
            pocket_age = 0

        if fits_map:
            predicted_contact = float(np.clip(predicted_now + 0.35 * revision, 0.0, 1.0))
            contact_trend = (1.0 - 0.35 * condition.prediction_gain) * contact_trend + 0.35 * condition.prediction_gain * (contact - prev_contact)
        else:
            predicted_contact = 0.998 * predicted_contact + 0.002 * contact
            contact_trend = 0.998 * contact_trend + 0.002 * (contact - prev_contact)

    return seq, {
        "witnesses": float(witnesses),
        "writes": float(writes),
        "releases": float(releases),
        "ruptures": float(ruptures),
        "witness_to_write": float(witness_to_write),
        "prediction_updates": float(prediction_updates),
        "mean_fit_error": float(np.mean(fit_errors)) if fit_errors else 0.0,
        "mean_revision_size": float(np.mean(revision_sizes)) if revision_sizes else 0.0,
        "mean_pocket_age": float(np.mean(pocket_ages)) if pocket_ages else 0.0,
    }


def evaluate(seq: np.ndarray, diag: dict[str, float]) -> dict[str, float]:
    witnesses = diag["witnesses"]
    writes = diag["writes"]
    releases = diag["releases"]
    ruptures = diag["ruptures"]
    total_events = max(witnesses + writes + releases + ruptures, 1.0)
    witness_conversion = diag["witness_to_write"] / max(witnesses, 1.0)
    delayed_retention = writes / max(writes + witnesses, 1.0)
    release_rate = releases / total_events
    rupture_rate = ruptures / total_events
    pollution = float(np.mean((seq[:-1] == 1) & (seq[1:] <= -1))) if len(seq) > 1 else 0.0
    return {
        "write_count": writes,
        "witness_count": witnesses,
        "witness_conversion": witness_conversion,
        "delayed_retention": delayed_retention,
        "release_rate": release_rate,
        "rupture_rate": rupture_rate,
        "prediction_update_rate": diag["prediction_updates"] / max(writes, 1.0),
        "mean_fit_error": diag["mean_fit_error"],
        "mean_revision_size": diag["mean_revision_size"],
        "mean_pocket_age": diag["mean_pocket_age"],
        "pollution": pollution,
        "phase_lock_resistance": v23.phase_lock_resistance(seq),
    }


def score(metrics: dict[str, float]) -> float:
    fit_term = 1.0 - min(metrics["mean_fit_error"] / 0.45, 1.0)
    revision_term = min(metrics["mean_revision_size"] / 0.05, 1.0)
    pocket_term = min(metrics["mean_pocket_age"] / 9.0, 1.0)
    return float(
        0.18 * metrics["phase_lock_resistance"]
        + 0.18 * metrics["witness_conversion"]
        + 0.15 * metrics["delayed_retention"]
        + 0.13 * metrics["prediction_update_rate"]
        + 0.10 * fit_term
        + 0.10 * revision_term
        + 0.08 * pocket_term
        + 0.04 * (1.0 - metrics["pollution"])
        + 0.04 * (1.0 - metrics["rupture_rate"])
    )


def plot_flow_summary(rows: list[dict], path: Path) -> None:
    labels = [row["flow"] for row in rows]
    scores = [row["mean_score"] for row in rows]
    witness = [row["mean_witness_conversion"] for row in rows]
    density = [row["density_gap"] for row in rows]
    x = np.arange(len(labels))
    width = 0.25
    plt.figure(figsize=(11, 5))
    plt.bar(x - width, scores, width=width, label="mean score")
    plt.bar(x, witness, width=width, label="witness conversion")
    plt.bar(x + width, density, width=width, label="density gap")
    plt.axhline(0.0, color="black", linewidth=1.0)
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
                metrics = evaluate(seq, diag)
                direct_rows.append(
                    {
                        "flow": flow.name,
                        "family": flow.family,
                        "alpha": alpha,
                        "offset": float(offset),
                        "window_width": condition.window_width,
                        "delay": condition.delay,
                        "prediction_gain": condition.prediction_gain,
                        "pocket_gain": condition.pocket_gain,
                        "pocket_decay": condition.pocket_decay,
                        "fit_limit": condition.fit_limit,
                        "revision_threshold": condition.revision_threshold,
                        "write_threshold": condition.write_threshold,
                        "rupture_limit": condition.rupture_limit,
                        **metrics,
                        "score": score(metrics),
                    }
                )

    flow_rows: list[dict] = []
    for flow in flows:
        subset = [row for row in direct_rows if row["flow"] == flow.name]
        best = max(subset, key=lambda row: row["score"])
        condition = Condition(
            window_width=best["window_width"],
            delay=int(best["delay"]),
            prediction_gain=best["prediction_gain"],
            pocket_gain=best["pocket_gain"],
            pocket_decay=best["pocket_decay"],
            fit_limit=best["fit_limit"],
            revision_threshold=best["revision_threshold"],
            write_threshold=best["write_threshold"],
            rupture_limit=best["rupture_limit"],
        )
        seq, _ = build_sequence(best["alpha"], condition)
        density = density_surrogate(seq)
        block = block_surrogate(seq)
        zero_diag = {
            "witnesses": float(np.sum(density == 0)),
            "writes": float(np.sum(density == 1)),
            "releases": float(np.sum(density == -1)),
            "ruptures": float(np.sum(density == 2)),
            "witness_to_write": 0.0,
            "prediction_updates": 0.0,
            "mean_fit_error": 0.45,
            "mean_revision_size": 0.0,
            "mean_pocket_age": 0.0,
        }
        density_score = score(evaluate(density, zero_diag))
        block_diag = {
            **zero_diag,
            "witnesses": float(np.sum(block == 0)),
            "writes": float(np.sum(block == 1)),
            "releases": float(np.sum(block == -1)),
            "ruptures": float(np.sum(block == 2)),
        }
        block_score = score(evaluate(block, block_diag))
        mean_score = float(np.mean([row["score"] for row in subset]))
        flow_rows.append(
            {
                "flow": flow.name,
                "family": flow.family,
                "best_score": best["score"],
                "best_delay": int(best["delay"]),
                "mean_score": mean_score,
                "mean_witness_conversion": float(np.mean([row["witness_conversion"] for row in subset])),
                "mean_delayed_retention": float(np.mean([row["delayed_retention"] for row in subset])),
                "mean_prediction_update_rate": float(np.mean([row["prediction_update_rate"] for row in subset])),
                "mean_rupture_rate": float(np.mean([row["rupture_rate"] for row in subset])),
                "mean_fit_error": float(np.mean([row["mean_fit_error"] for row in subset])),
                "density_gap": mean_score - density_score,
                "block_gap": mean_score - block_score,
            }
        )

    ranked = sorted(flow_rows, key=lambda row: row["mean_score"], reverse=True)
    write_csv(direct_rows, OUT / "direct_metrics.csv")
    write_csv(flow_rows, OUT / "flow_summary.csv")
    plot_flow_summary(flow_rows, OUT / "flow_summary.png")

    best = ranked[0]
    golden = next(row for row in flow_rows if row["flow"] == "golden")
    report = f"""# Golden Zipper v29b - Adaptive Plinko Boundary

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best flow by mean score: `{best['flow']}` with `{best['mean_score']:.3f}`

Golden result:
- mean score: `{golden['mean_score']:.3f}`
- best delay: `{golden['best_delay']}`
- witness conversion: `{golden['mean_witness_conversion']:.3f}`
- delayed retention: `{golden['mean_delayed_retention']:.3f}`
- prediction update rate: `{golden['mean_prediction_update_rate']:.3f}`
- rupture rate: `{golden['mean_rupture_rate']:.3f}`
- density gap: `{golden['density_gap']:.3f}`
- block gap: `{golden['block_gap']:.3f}`

Interpretation:
- This version predicts boundary-contact likelihood instead of raw hidden value.
- A useful result would reduce rupture while preserving witness conversion and positive null gaps.
- Phi/golden remains an anchor candidate, not the write point.
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best flow by mean score: {best['flow']} {best['mean_score']:.3f}")
    print(f"golden mean score: {golden['mean_score']:.3f}")
    print(f"golden best delay: {golden['best_delay']}")
    print(f"golden witness conversion: {golden['mean_witness_conversion']:.3f}")
    print(f"golden prediction update rate: {golden['mean_prediction_update_rate']:.3f}")
    print(f"golden rupture rate: {golden['mean_rupture_rate']:.3f}")
    print(f"golden density gap: {golden['density_gap']:.3f}")
    print(f"golden block gap: {golden['block_gap']:.3f}")


if __name__ == "__main__":
    main()
