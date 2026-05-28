#!/usr/bin/env python3
"""v32d soft selective recall.

This calibrates between v32b and v32c:
- some context can recolor the groove
- unrelated context should mostly fail
- recall must still survive often enough to matter

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import golden_zipper_v23_boundary_pocket_attractor as v23
import golden_zipper_v31b_phase_null_repair as v31b


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v32d_outputs"

SEED = 20260523
RNG = np.random.default_rng(SEED)

CONTEXT_PRESSURES = [0.08, 0.16, 0.24]
SIMILARITY_THRESHOLDS = [0.58, 0.68, 0.78]
RECALL_WINDOWS = [13, 21]
RECALL_GAINS = [0.08, 0.14, 0.20]
PASS_THROUGHS = [0.18, 0.32, 0.46]
SPLIT_THRESHOLDS = [0.24, 0.36]
MAX_VARIANTS = 54


@dataclass(frozen=True)
class RecallCondition:
    context_pressure: float
    similarity_threshold: float
    recall_window: int
    recall_gain: float
    pass_through: float
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
            context_pressure=context_pressure,
            similarity_threshold=similarity_threshold,
            recall_window=recall_window,
            recall_gain=recall_gain,
            pass_through=pass_through,
            split_threshold=split_threshold,
        )
        for context_pressure in CONTEXT_PRESSURES
        for similarity_threshold in SIMILARITY_THRESHOLDS
        for recall_window in RECALL_WINDOWS
        for recall_gain in RECALL_GAINS
        for pass_through in PASS_THROUGHS
        for split_threshold in SPLIT_THRESHOLDS
    ]
    if len(full) <= MAX_VARIANTS:
        return full
    picks = np.sort(RNG.choice(len(full), size=MAX_VARIANTS, replace=False))
    return [full[idx] for idx in picks]


def neighbor_slot(slot: int, slot_count: int, direction: int) -> int:
    return (slot + direction) % slot_count


def score_recall(metrics: dict[str, float]) -> float:
    deepen = min(metrics["same_slot_recall_rate"] / 0.40, 1.0)
    survive = min(metrics["recall_survival_rate"] / 0.40, 1.0)
    stable = 1.0 - min(metrics["split_rate"] / 0.30, 1.0)
    distortion = 1.0 - min(metrics["context_distortion_rate"] / 0.40, 1.0)
    blocked = min(metrics["blocked_context_rate"] / 0.35, 1.0)
    return float(
        0.14 * metrics["phase_lock_resistance"]
        + 0.15 * metrics["witness_conversion"]
        + 0.11 * metrics["delayed_retention"]
        + 0.15 * survive
        + 0.13 * deepen
        + 0.10 * stable
        + 0.08 * distortion
        + 0.08 * blocked
        + 0.03 * (1.0 - metrics["rupture_rate"])
        + 0.03 * (1.0 - metrics["pollution"])
    )


def build_soft_selective_sequence(
    alpha: float,
    base_condition,
    recall_condition: RecallCondition,
) -> tuple[np.ndarray, dict[str, float]]:
    hidden = v31b.v31.hidden_trace(alpha)
    seq = np.full(v31b.v31.LENGTH, -2, dtype=np.int8)
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
    split_events = 0
    context_distortions = 0
    blocked_contexts = 0

    for idx in range(base_condition.delay + 2, v31b.v31.LENGTH):
        charges *= base_condition.stack_decay
        grooves *= base_condition.groove_decay
        delayed = hidden[idx - base_condition.delay]
        previous = hidden[idx - base_condition.delay - 1]
        contact = v31b.v31.contact_likelihood(delayed, base_condition.window_width)
        if contact < 0.12:
            if np.max(charges) < 0.05:
                seq[idx] = -1
                releases += 1
            continue

        slot, phase = v31b.v31.route_slot(delayed, previous, idx, alpha, base_condition)
        if last_slot >= 0:
            grooves[last_slot, slot] += base_condition.groove_gain * contact
        incoming_groove = float(np.max(grooves[:, slot])) if last_slot >= 0 else 0.0

        neighbor_support = 0.0
        for neighbor in range(base_condition.slot_count):
            distance = v31b.v31.slot_distance(slot, neighbor, base_condition.slot_count)
            if 0 < distance <= 2:
                neighbor_support += charges[neighbor] * (1.0 / (1.0 + distance))
        neighbor_support *= base_condition.relation_gain

        phase_alignment = 1.0 - abs(((phase + 0.5) % 1.0) - 0.5) * 2.0
        phase_support = base_condition.phase_gain * phase_alignment * (incoming_groove + contact)

        if idx - memory_age[slot] <= recall_condition.recall_window:
            recall_hits += 1
            context_similarity = 1.0 - abs(phase_alignment - contact)
            if context_similarity >= recall_condition.similarity_threshold:
                context_push = recall_condition.context_pressure * (0.5 - phase_alignment)
                if abs(context_push) > 0.03:
                    context_distortions += 1
                target_slot = slot
                if context_push > 0.0:
                    target_slot = neighbor_slot(slot, base_condition.slot_count, 1)
                elif context_push < 0.0:
                    target_slot = neighbor_slot(slot, base_condition.slot_count, -1)

                if target_slot == slot:
                    same_slot_recalls += 1
                    recall_survivals += 1
                    charges[slot] += recall_condition.recall_gain * charges[slot]
                else:
                    charges[target_slot] += recall_condition.recall_gain * (charges[slot] + incoming_groove)
                    charges[slot] += recall_condition.recall_gain * recall_condition.pass_through
                    recall_survivals += 1
                    if charges[target_slot] >= recall_condition.split_threshold:
                        split_events += 1
                        seq[idx] = 2
                        ruptures += 1
                        charges[target_slot] *= 0.30
                        last_slot = target_slot
                        continue
            else:
                blocked_contexts += 1
                charges[slot] += recall_condition.recall_gain * recall_condition.pass_through * 0.35

        charges[slot] += base_condition.stack_gain * contact + neighbor_support + phase_support
        effective_charge = charges[slot] + incoming_groove + neighbor_support + phase_support

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
        "split_events": float(split_events),
        "context_distortions": float(context_distortions),
        "blocked_contexts": float(blocked_contexts),
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
        "split_rate": diag["split_events"] / recall_hits,
        "context_distortion_rate": diag["context_distortions"] / recall_hits,
        "blocked_context_rate": diag["blocked_contexts"] / recall_hits,
        "pollution": pollution,
        "phase_lock_resistance": v23.phase_lock_resistance(seq),
    }


def density_surrogate(seq: np.ndarray) -> np.ndarray:
    values, counts = np.unique(seq, return_counts=True)
    probs = counts / counts.sum()
    return RNG.choice(values, size=len(seq), p=probs).astype(np.int8)


def plot_summary(rows: list[dict], path: Path) -> None:
    labels = [row["flow"] for row in rows]
    score = [row["mean_score"] for row in rows]
    survival = [row["mean_recall_survival_rate"] for row in rows]
    blocked = [row["mean_blocked_context_rate"] for row in rows]
    x = np.arange(len(labels))
    width = 0.25
    plt.figure(figsize=(11, 5))
    plt.bar(x - width, score, width=width, label="mean score")
    plt.bar(x, survival, width=width, label="recall survival")
    plt.bar(x + width, blocked, width=width, label="blocked context")
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
            seq, diag = build_soft_selective_sequence(spec.alpha, spec.condition, recall_condition)
            metrics = evaluate_recall(seq, diag)
            direct_rows.append(
                {
                    "flow": spec.flow,
                    "family": spec.family,
                    "alpha": spec.alpha,
                    "best_delay": spec.condition.delay,
                    "best_slot_count": spec.condition.slot_count,
                    "context_pressure": recall_condition.context_pressure,
                    "similarity_threshold": recall_condition.similarity_threshold,
                    "recall_window": recall_condition.recall_window,
                    "recall_gain": recall_condition.recall_gain,
                    "pass_through": recall_condition.pass_through,
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
            context_pressure=best["context_pressure"],
            similarity_threshold=best["similarity_threshold"],
            recall_window=int(best["recall_window"]),
            recall_gain=best["recall_gain"],
            pass_through=best["pass_through"],
            split_threshold=best["split_threshold"],
        )
        seq, diag = build_soft_selective_sequence(spec.alpha, spec.condition, recall_condition)
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
            "split_events": 0.0,
            "context_distortions": 0.0,
            "blocked_contexts": 0.0,
        }
        mean_score = float(np.mean([row["score"] for row in subset]))
        summary_rows.append(
            {
                "flow": spec.flow,
                "family": spec.family,
                "best_score": best["score"],
                "best_delay": spec.condition.delay,
                "best_slot_count": spec.condition.slot_count,
                "best_context_pressure": recall_condition.context_pressure,
                "best_similarity_threshold": recall_condition.similarity_threshold,
                "best_recall_window": recall_condition.recall_window,
                "best_recall_gain": recall_condition.recall_gain,
                "best_pass_through": recall_condition.pass_through,
                "best_split_threshold": recall_condition.split_threshold,
                "mean_score": mean_score,
                "mean_recall_survival_rate": float(np.mean([row["recall_survival_rate"] for row in subset])),
                "mean_same_slot_recall_rate": float(np.mean([row["same_slot_recall_rate"] for row in subset])),
                "mean_context_distortion_rate": float(np.mean([row["context_distortion_rate"] for row in subset])),
                "mean_blocked_context_rate": float(np.mean([row["blocked_context_rate"] for row in subset])),
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
    report = f"""# Golden Zipper v32d - Soft Selective Recall

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best flow by mean score: `{best['flow']}` with `{best['mean_score']:.3f}`

Golden result:
- mean score: `{golden['mean_score']:.3f}`
- best context pressure: `{golden['best_context_pressure']:.3f}`
- best similarity threshold: `{golden['best_similarity_threshold']:.3f}`
- best recall window: `{golden['best_recall_window']}`
- best pass-through: `{golden['best_pass_through']:.3f}`
- mean recall survival rate: `{golden['mean_recall_survival_rate']:.3f}`
- mean same-slot recall rate: `{golden['mean_same_slot_recall_rate']:.3f}`
- mean context distortion rate: `{golden['mean_context_distortion_rate']:.3f}`
- mean blocked context rate: `{golden['mean_blocked_context_rate']:.3f}`
- mean split rate: `{golden['mean_split_rate']:.3f}`
- density gap: `{golden['density_gap']:.3f}`

Interpretation:
- This panel calibrates selective recall so some context can recolor memory without collapsing survival.
- A useful result would sit between v32b and v32c: better survival than v32c, lower distortion than v32b, and a positive density gap.
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best flow by mean score: {best['flow']} {best['mean_score']:.3f}")
    print(f"golden mean score: {golden['mean_score']:.3f}")
    print(f"golden best context pressure: {golden['best_context_pressure']:.3f}")
    print(f"golden best similarity threshold: {golden['best_similarity_threshold']:.3f}")
    print(f"golden best pass_through: {golden['best_pass_through']:.3f}")
    print(f"golden recall survival rate: {golden['mean_recall_survival_rate']:.3f}")
    print(f"golden blocked context rate: {golden['mean_blocked_context_rate']:.3f}")
    print(f"golden split rate: {golden['mean_split_rate']:.3f}")
    print(f"golden density gap: {golden['density_gap']:.3f}")


if __name__ == "__main__":
    main()
