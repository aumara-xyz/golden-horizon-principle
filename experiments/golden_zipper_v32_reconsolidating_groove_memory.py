#!/usr/bin/env python3
"""v32 reconsolidating groove memory.

This keeps the repaired v31b groove object and adds recall:
- recalls can deepen the same groove
- recalls can drift into a nearby groove
- recalls can split a knot-family when context pressure is high

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import golden_zipper_v23_boundary_pocket_attractor as v23
import golden_zipper_v31_path_phase_groove_memory as v31
import golden_zipper_v31b_phase_null_repair as v31b


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v32_outputs"

SEED = 20260523
RNG = np.random.default_rng(SEED)

RECALL_WINDOWS = [13, 21]
RECALL_GAINS = [0.06, 0.12, 0.20]
DRIFT_RATES = [0.00, 0.08, 0.16]
SPLIT_THRESHOLDS = [0.18, 0.30, 0.44]
MAX_VARIANTS = 54


@dataclass(frozen=True)
class RecallCondition:
    recall_window: int
    recall_gain: float
    drift_rate: float
    split_threshold: float


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


def build_recall_conditions() -> list[RecallCondition]:
    full = [
        RecallCondition(
            recall_window=recall_window,
            recall_gain=recall_gain,
            drift_rate=drift_rate,
            split_threshold=split_threshold,
        )
        for recall_window in RECALL_WINDOWS
        for recall_gain in RECALL_GAINS
        for drift_rate in DRIFT_RATES
        for split_threshold in SPLIT_THRESHOLDS
    ]
    if len(full) <= MAX_VARIANTS:
        return full
    picks = np.sort(RNG.choice(len(full), size=MAX_VARIANTS, replace=False))
    return [full[idx] for idx in picks]


def neighbor_slot(slot: int, slot_count: int, phase: float) -> int:
    direction = 1 if phase >= 0.5 else -1
    return (slot + direction) % slot_count


def score_recall(metrics: dict[str, float]) -> float:
    deepen = min(metrics["same_slot_recall_rate"] / 0.45, 1.0)
    survive = min(metrics["recall_survival_rate"] / 0.45, 1.0)
    stable = 1.0 - min(metrics["split_rate"] / 0.35, 1.0)
    drift = 1.0 - min(metrics["drift_rate"] / 0.35, 1.0)
    return float(
        0.16 * metrics["phase_lock_resistance"]
        + 0.16 * metrics["witness_conversion"]
        + 0.12 * metrics["delayed_retention"]
        + 0.15 * survive
        + 0.13 * deepen
        + 0.10 * stable
        + 0.08 * drift
        + 0.05 * (1.0 - metrics["rupture_rate"])
        + 0.05 * (1.0 - metrics["pollution"])
    )


def build_reconsolidating_sequence(
    alpha: float,
    base_condition: v31.Condition,
    recall_condition: RecallCondition,
) -> tuple[np.ndarray, dict[str, float]]:
    hidden = v31.hidden_trace(alpha)
    seq = np.full(v31.LENGTH, -2, dtype=np.int8)
    charges = np.zeros(base_condition.slot_count, dtype=float)
    grooves = np.zeros((base_condition.slot_count, base_condition.slot_count), dtype=float)
    memory_age = np.full(base_condition.slot_count, -9999, dtype=int)
    last_slot = -1
    last_witness_at = np.full(base_condition.slot_count, -9999, dtype=int)

    witnesses = 0
    writes = 0
    releases = 0
    ruptures = 0
    witness_to_write = 0
    recall_hits = 0
    recall_survivals = 0
    same_slot_recalls = 0
    drift_events = 0
    split_events = 0

    for idx in range(base_condition.delay + 2, v31.LENGTH):
        charges *= base_condition.stack_decay
        grooves *= base_condition.groove_decay
        delayed = hidden[idx - base_condition.delay]
        previous = hidden[idx - base_condition.delay - 1]
        contact = v31.contact_likelihood(delayed, base_condition.window_width)
        if contact < 0.12:
            if np.max(charges) < 0.05:
                seq[idx] = -1
                releases += 1
            continue

        slot, phase = v31.route_slot(delayed, previous, idx, alpha, base_condition)
        if last_slot >= 0:
            grooves[last_slot, slot] += base_condition.groove_gain * contact
        incoming_groove = float(np.max(grooves[:, slot])) if last_slot >= 0 else 0.0

        neighbor_support = 0.0
        for neighbor in range(base_condition.slot_count):
            distance = v31.slot_distance(slot, neighbor, base_condition.slot_count)
            if 0 < distance <= 2:
                neighbor_support += charges[neighbor] * (1.0 / (1.0 + distance))
        neighbor_support *= base_condition.relation_gain

        phase_alignment = 1.0 - abs(((phase + 0.5) % 1.0) - 0.5) * 2.0
        phase_support = base_condition.phase_gain * phase_alignment * (incoming_groove + contact)

        recall_pressure = 0.0
        if idx - memory_age[slot] <= recall_condition.recall_window:
            recall_hits += 1
            recall_pressure = recall_condition.recall_gain * charges[slot]
            charges[slot] += recall_pressure
            recall_survivals += 1
            same_slot_recalls += 1
        else:
            nearby = neighbor_slot(slot, base_condition.slot_count, phase)
            if idx - memory_age[nearby] <= recall_condition.recall_window and recall_condition.drift_rate > 0:
                recall_hits += 1
                drift_events += 1
                charges[nearby] += recall_condition.recall_gain * recall_condition.drift_rate
                charges[slot] += recall_condition.recall_gain * (1.0 - recall_condition.drift_rate) * 0.5
                if charges[nearby] >= recall_condition.split_threshold:
                    split_events += 1
                    seq[idx] = 2
                    ruptures += 1
                    charges[nearby] *= 0.30
                    last_slot = nearby
                    continue

        charges[slot] += base_condition.stack_gain * contact + neighbor_support + phase_support
        effective_charge = charges[slot] + incoming_groove + neighbor_support + phase_support + recall_pressure

        if effective_charge >= base_condition.rupture_threshold:
            seq[idx] = 2
            ruptures += 1
            charges[slot] *= 0.25
            last_witness_at[slot] = -9999
            last_slot = slot
            continue

        if effective_charge >= base_condition.write_threshold and last_witness_at[slot] > -9999:
            seq[idx] = 1
            writes += 1
            witness_to_write += 1
            charges[slot] *= 0.50
            last_witness_at[slot] = -9999
            memory_age[slot] = idx
            last_slot = slot
            continue

        if effective_charge >= 0.34:
            seq[idx] = 0
            witnesses += 1
            last_witness_at[slot] = idx
            last_slot = slot
            continue

        seq[idx] = -1
        releases += 1
        last_slot = slot

    return seq, {
        "witnesses": float(witnesses),
        "writes": float(writes),
        "releases": float(releases),
        "ruptures": float(ruptures),
        "witness_to_write": float(witness_to_write),
        "recall_hits": float(recall_hits),
        "recall_survivals": float(recall_survivals),
        "same_slot_recalls": float(same_slot_recalls),
        "drift_events": float(drift_events),
        "split_events": float(split_events),
    }


def evaluate_recall(seq: np.ndarray, diag: dict[str, float]) -> dict[str, float]:
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
    recall_hits = max(diag["recall_hits"], 1.0)
    return {
        "witness_conversion": witness_conversion,
        "delayed_retention": delayed_retention,
        "release_rate": release_rate,
        "rupture_rate": rupture_rate,
        "recall_survival_rate": diag["recall_survivals"] / recall_hits,
        "same_slot_recall_rate": diag["same_slot_recalls"] / recall_hits,
        "drift_rate": diag["drift_events"] / recall_hits,
        "split_rate": diag["split_events"] / recall_hits,
        "pollution": pollution,
        "phase_lock_resistance": v23.phase_lock_resistance(seq),
    }


def density_surrogate(seq: np.ndarray) -> np.ndarray:
    values, counts = np.unique(seq, return_counts=True)
    probs = counts / counts.sum()
    return RNG.choice(values, size=len(seq), p=probs).astype(np.int8)


def plot_summary(rows: list[dict], path: Path) -> None:
    labels = [row["flow"] for row in rows]
    real = [row["mean_score"] for row in rows]
    density = [row["density_gap"] for row in rows]
    split = [row["mean_split_rate"] for row in rows]
    x = np.arange(len(labels))
    width = 0.25
    plt.figure(figsize=(11, 5))
    plt.bar(x - width, real, width=width, label="mean score")
    plt.bar(x, density, width=width, label="density gap")
    plt.bar(x + width, split, width=width, label="split rate")
    plt.axhline(0.0, color="black", linewidth=1.0)
    plt.xticks(x, labels, rotation=20)
    plt.tight_layout()
    plt.legend()
    plt.savefig(path, dpi=180)
    plt.close()


def main() -> None:
    ensure_dir(OUT)
    specs = v31b.find_best_specs()
    recall_conditions = build_recall_conditions()

    direct_rows: list[dict] = []
    for spec in specs:
        for recall_condition in recall_conditions:
            seq, diag = build_reconsolidating_sequence(spec.alpha, spec.condition, recall_condition)
            metrics = evaluate_recall(seq, diag)
            direct_rows.append(
                {
                    "flow": spec.flow,
                    "family": spec.family,
                    "alpha": spec.alpha,
                    "best_delay": spec.condition.delay,
                    "best_slot_count": spec.condition.slot_count,
                    "recall_window": recall_condition.recall_window,
                    "recall_gain": recall_condition.recall_gain,
                    "drift_rate": recall_condition.drift_rate,
                    "split_threshold": recall_condition.split_threshold,
                    **metrics,
                    "score": score_recall(metrics),
                }
            )

    summary_rows: list[dict] = []
    for spec in specs:
        subset = [row for row in direct_rows if row["flow"] == spec.flow]
        best = max(subset, key=lambda row: row["score"])
        recall_condition = RecallCondition(
            recall_window=int(best["recall_window"]),
            recall_gain=best["recall_gain"],
            drift_rate=best["drift_rate"],
            split_threshold=best["split_threshold"],
        )
        seq, diag = build_reconsolidating_sequence(spec.alpha, spec.condition, recall_condition)
        density = density_surrogate(seq)
        density_diag = {
            "witnesses": float(np.sum(density == 0)),
            "writes": float(np.sum(density == 1)),
            "releases": float(np.sum(density == -1)),
            "ruptures": float(np.sum(density == 2)),
            "witness_to_write": 0.0,
            "recall_hits": 1.0,
            "recall_survivals": 0.0,
            "same_slot_recalls": 0.0,
            "drift_events": 0.0,
            "split_events": 0.0,
        }
        mean_score = float(np.mean([row["score"] for row in subset]))
        summary_rows.append(
            {
                "flow": spec.flow,
                "family": spec.family,
                "best_score": best["score"],
                "best_delay": spec.condition.delay,
                "best_slot_count": spec.condition.slot_count,
                "best_recall_window": recall_condition.recall_window,
                "best_recall_gain": recall_condition.recall_gain,
                "best_drift_rate": recall_condition.drift_rate,
                "best_split_threshold": recall_condition.split_threshold,
                "mean_score": mean_score,
                "mean_recall_survival_rate": float(np.mean([row["recall_survival_rate"] for row in subset])),
                "mean_same_slot_recall_rate": float(np.mean([row["same_slot_recall_rate"] for row in subset])),
                "mean_drift_rate": float(np.mean([row["drift_rate"] for row in subset])),
                "mean_split_rate": float(np.mean([row["split_rate"] for row in subset])),
                "density_gap": mean_score - score_recall(evaluate_recall(density, density_diag)),
            }
        )

    ranked = sorted(summary_rows, key=lambda row: row["mean_score"], reverse=True)
    write_csv(direct_rows, OUT / "direct_metrics.csv")
    write_csv(summary_rows, OUT / "summary.csv")
    plot_summary(summary_rows, OUT / "summary.png")

    best = ranked[0]
    golden = next(row for row in summary_rows if row["flow"] == "golden")
    report = f"""# Golden Zipper v32 - Reconsolidating Groove Memory

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best flow by mean score: `{best['flow']}` with `{best['mean_score']:.3f}`

Golden result:
- mean score: `{golden['mean_score']:.3f}`
- best delay: `{golden['best_delay']}`
- best slot count: `{golden['best_slot_count']}`
- best recall window: `{golden['best_recall_window']}`
- mean recall survival rate: `{golden['mean_recall_survival_rate']:.3f}`
- mean same-slot recall rate: `{golden['mean_same_slot_recall_rate']:.3f}`
- mean drift rate: `{golden['mean_drift_rate']:.3f}`
- mean split rate: `{golden['mean_split_rate']:.3f}`
- density gap: `{golden['density_gap']:.3f}`

Interpretation:
- This panel asks whether recalled memories deepen the same groove, drift into nearby grooves, or split.
- A useful result would show strong same-slot recall survival without runaway splitting.
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best flow by mean score: {best['flow']} {best['mean_score']:.3f}")
    print(f"golden mean score: {golden['mean_score']:.3f}")
    print(f"golden recall survival rate: {golden['mean_recall_survival_rate']:.3f}")
    print(f"golden same-slot recall rate: {golden['mean_same_slot_recall_rate']:.3f}")
    print(f"golden drift rate: {golden['mean_drift_rate']:.3f}")
    print(f"golden split rate: {golden['mean_split_rate']:.3f}")
    print(f"golden density gap: {golden['density_gap']:.3f}")


if __name__ == "__main__":
    main()
