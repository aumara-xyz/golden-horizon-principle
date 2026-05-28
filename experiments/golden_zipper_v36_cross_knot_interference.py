#!/usr/bin/env python3
"""v36 cross-knot interference.

This tests whether neighboring knot-families shape recall:
- nearby memories can reinforce the current knot-family
- or tug against it and increase drift / split pressure
- memory identity may depend on local interference, not just isolated storage

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
OUT = ROOT / "golden_zipper_v36_outputs"

SEED = 20260524
RNG = np.random.default_rng(SEED)

CONTEXT_PRESSURES = [0.04, 0.08]
SIMILARITY_THRESHOLDS = [0.58, 0.68, 0.78]
RECALL_WINDOWS = [13, 21]
RECALL_GAINS = [0.08, 0.14, 0.20]
LAYER_WINDOWS = [8, 13]
RECENCY_DECAYS = [0.55, 0.72]
RESONANCE_GAINS = [0.08, 0.14]
INTERFERENCE_RADII = [4, 6]
INTERFERENCE_GAINS = [0.04, 0.08, 0.12]
COMPETITION_GAINS = [0.04, 0.08]
BASIN_RADII = [2]
SPLIT_THRESHOLDS = [0.24, 0.36]
MAX_VARIANTS = 54


@dataclass(frozen=True)
class RecallCondition:
    context_pressure: float
    similarity_threshold: float
    recall_window: int
    recall_gain: float
    layer_window: int
    recency_decay: float
    resonance_gain: float
    interference_radius: int
    interference_gain: float
    competition_gain: float
    basin_radius: int
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
            layer_window=layer_window,
            recency_decay=recency_decay,
            resonance_gain=resonance_gain,
            interference_radius=interference_radius,
            interference_gain=interference_gain,
            competition_gain=competition_gain,
            basin_radius=basin_radius,
            split_threshold=split_threshold,
        )
        for context_pressure in CONTEXT_PRESSURES
        for similarity_threshold in SIMILARITY_THRESHOLDS
        for recall_window in RECALL_WINDOWS
        for recall_gain in RECALL_GAINS
        for layer_window in LAYER_WINDOWS
        for recency_decay in RECENCY_DECAYS
        for resonance_gain in RESONANCE_GAINS
        for interference_radius in INTERFERENCE_RADII
        for interference_gain in INTERFERENCE_GAINS
        for competition_gain in COMPETITION_GAINS
        for basin_radius in BASIN_RADII
        for split_threshold in SPLIT_THRESHOLDS
    ]
    if len(full) <= MAX_VARIANTS:
        return full
    picks = np.sort(RNG.choice(len(full), size=MAX_VARIANTS, replace=False))
    return [full[idx] for idx in picks]


def region_members(slot: int, slot_count: int, radius: int) -> list[int]:
    return sorted({(slot + offset) % slot_count for offset in range(-radius, radius + 1)})


def temporal_kernel(length: int, decay: float) -> np.ndarray:
    powers = np.arange(length, dtype=float)
    kernel = decay**powers
    return kernel / kernel.sum()


def score_recall(metrics: dict[str, float]) -> float:
    same_region = min(metrics["same_region_recall_rate"] / 0.50, 1.0)
    same_slot = min(metrics["same_slot_recall_rate"] / 0.35, 1.0)
    survive = min(metrics["recall_survival_rate"] / 0.42, 1.0)
    stable = 1.0 - min(metrics["split_rate"] / 0.30, 1.0)
    distortion = 1.0 - min(metrics["context_distortion_rate"] / 0.35, 1.0)
    blocked = min(metrics["blocked_context_rate"] / 0.35, 1.0)
    interference = min(metrics["interference_coherence_rate"] / 0.45, 1.0)
    return float(
        0.14 * metrics["phase_lock_resistance"]
        + 0.14 * metrics["witness_conversion"]
        + 0.10 * metrics["delayed_retention"]
        + 0.14 * survive
        + 0.10 * same_region
        + 0.04 * same_slot
        + 0.09 * interference
        + 0.10 * stable
        + 0.07 * distortion
        + 0.06 * blocked
        + 0.01 * (1.0 - metrics["rupture_rate"])
        + 0.01 * (1.0 - metrics["pollution"])
    )


def build_interference_sequence(
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

    layer_trace = np.zeros((base_condition.slot_count, recall_condition.layer_window), dtype=float)
    kernel = temporal_kernel(recall_condition.layer_window, recall_condition.recency_decay)

    witnesses = writes = releases = ruptures = witness_to_write = 0
    recall_hits = recall_survivals = same_slot_recalls = same_region_recalls = 0
    split_events = context_distortions = blocked_contexts = interference_coherences = 0
    interference_checks = 0

    for idx in range(base_condition.delay + 2, v31b.v31.LENGTH):
        charges *= base_condition.stack_decay
        grooves *= base_condition.groove_decay
        layer_trace[:, 1:] = layer_trace[:, :-1]
        layer_trace[:, 0] = 0.0

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

        phase_alignment = 1.0 - abs(((phase + 0.5) % 1.0) - 0.5) * 2.0
        phase_support = base_condition.phase_gain * phase_alignment * (incoming_groove + contact)

        region = region_members(slot, base_condition.slot_count, recall_condition.basin_radius)
        recent_region = [member for member in region if idx - memory_age[member] <= recall_condition.recall_window]
        region_layer_strength = float(np.mean([np.dot(layer_trace[member], kernel) for member in region]))

        neighbor_support = 0.0
        for neighbor in region:
            if neighbor != slot:
                distance = v31b.v31.slot_distance(slot, neighbor, base_condition.slot_count)
                neighbor_support += charges[neighbor] * (1.0 / (1.0 + distance))
        neighbor_support *= base_condition.relation_gain

        outer_support = 0.0
        outer_competition = 0.0
        for neighbor in range(base_condition.slot_count):
            distance = v31b.v31.slot_distance(slot, neighbor, base_condition.slot_count)
            if recall_condition.basin_radius < distance <= recall_condition.interference_radius:
                interference_checks += 1
                neighbor_layer = float(np.dot(layer_trace[neighbor], kernel))
                coherence = 1.0 - abs(neighbor_layer - region_layer_strength)
                signed = (coherence - 0.5) * 2.0
                if signed >= 0:
                    outer_support += recall_condition.interference_gain * signed * charges[neighbor] / (1.0 + distance)
                    if signed > 0.25:
                        interference_coherences += 1
                else:
                    outer_competition += recall_condition.competition_gain * abs(signed) * charges[neighbor] / (1.0 + distance)

        if recent_region:
            recall_hits += 1
            context_similarity = 1.0 - abs(phase_alignment - contact)
            soft_admit = context_similarity + 0.35 * min(region_layer_strength / max(recall_condition.resonance_gain, 1e-9), 1.5)
            soft_threshold = recall_condition.similarity_threshold + 0.10
            if soft_admit >= soft_threshold:
                tint = recall_condition.context_pressure * max(context_similarity - recall_condition.similarity_threshold, 0.0)
                if tint > 0.03:
                    context_distortions += 1
                recall_survivals += 1
                same_region_recalls += 1
                if slot in recent_region:
                    same_slot_recalls += 1

                region_charge = np.mean([charges[member] for member in recent_region])
                for member in recent_region:
                    charges[member] += recall_condition.recall_gain * 0.35 * (
                        region_charge + incoming_groove + 0.45 * region_layer_strength + outer_support
                    )
                    grooves[slot, member] += recall_condition.resonance_gain * (contact + phase_alignment)
                charges[slot] += recall_condition.recall_gain * 0.65 * (
                    charges[slot] + incoming_groove + 0.40 * region_layer_strength + outer_support - outer_competition
                )
                layer_trace[slot, 0] += recall_condition.resonance_gain * (0.5 + contact + phase_alignment)

                outer_left = (slot - recall_condition.basin_radius - 1) % base_condition.slot_count
                outer_right = (slot + recall_condition.basin_radius + 1) % base_condition.slot_count
                neighbor_bleed = recall_condition.context_pressure * tint * max(charges[slot], 0.10) + outer_competition * 0.5
                if neighbor_bleed > 0.0:
                    charges[outer_left] += neighbor_bleed * 0.5
                    charges[outer_right] += neighbor_bleed * 0.5
                    if max(charges[outer_left], charges[outer_right]) >= recall_condition.split_threshold:
                        split_events += 1
                        seq[idx] = 2
                        ruptures += 1
                        charges[outer_left] *= 0.40
                        charges[outer_right] *= 0.40
                        last_slot = slot
                        continue
            else:
                blocked_contexts += 1
                charges[slot] += recall_condition.recall_gain * (0.08 + 0.10 * min(region_layer_strength, 1.0))

        support = 0.30 * region_layer_strength + outer_support - 0.5 * outer_competition
        charges[slot] += base_condition.stack_gain * contact + neighbor_support + phase_support + support
        effective_charge = charges[slot] + incoming_groove + neighbor_support + phase_support + support

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
            layer_trace[slot, 0] += 1.0
            last_slot = slot
            continue

        if effective_charge >= 0.34:
            seq[idx] = 0
            witnesses += 1
            last_witness_at[slot] = idx
            layer_trace[slot, 0] += 0.45
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
        "same_region_recalls": float(same_region_recalls),
        "split_events": float(split_events),
        "context_distortions": float(context_distortions),
        "blocked_contexts": float(blocked_contexts),
        "interference_coherences": float(interference_coherences),
        "interference_checks": float(interference_checks),
    }


def evaluate_recall(seq: np.ndarray, diag: dict[str, float]) -> dict[str, float]:
    witnesses = diag["witnesses"]
    writes = diag["writes"]
    releases = diag["releases"]
    ruptures = diag["ruptures"]
    total_events = max(witnesses + writes + releases + ruptures, 1.0)
    recall_hits = max(diag["recall_hits"], 1.0)
    return {
        "witness_conversion": diag["witness_to_write"] / max(witnesses, 1.0),
        "delayed_retention": writes / max(writes + witnesses, 1.0),
        "release_rate": releases / total_events,
        "rupture_rate": ruptures / total_events,
        "recall_survival_rate": diag["recall_survivals"] / recall_hits,
        "same_slot_recall_rate": diag["same_slot_recalls"] / recall_hits,
        "same_region_recall_rate": diag["same_region_recalls"] / recall_hits,
        "split_rate": diag["split_events"] / recall_hits,
        "context_distortion_rate": diag["context_distortions"] / recall_hits,
        "blocked_context_rate": diag["blocked_contexts"] / recall_hits,
        "interference_coherence_rate": diag["interference_coherences"] / max(diag["interference_checks"], 1.0),
        "pollution": float(np.mean((seq[:-1] == 1) & (seq[1:] <= -1))) if len(seq) > 1 else 0.0,
        "phase_lock_resistance": v23.phase_lock_resistance(seq),
    }


def density_surrogate(seq: np.ndarray) -> np.ndarray:
    values, counts = np.unique(seq, return_counts=True)
    probs = counts / counts.sum()
    return RNG.choice(values, size=len(seq), p=probs).astype(np.int8)


def plot_summary(rows: list[dict], path: Path) -> None:
    labels = [row["flow"] for row in rows]
    score = [row["mean_score"] for row in rows]
    region = [row["mean_same_region_recall_rate"] for row in rows]
    interference = [row["mean_interference_coherence_rate"] for row in rows]
    x = np.arange(len(labels))
    width = 0.25
    plt.figure(figsize=(11, 5))
    plt.bar(x - width, score, width=width, label="mean score")
    plt.bar(x, region, width=width, label="same-region recall")
    plt.bar(x + width, interference, width=width, label="interference coherence")
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
            seq, diag = build_interference_sequence(spec.alpha, spec.condition, recall_condition)
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
                    "layer_window": recall_condition.layer_window,
                    "recency_decay": recall_condition.recency_decay,
                    "resonance_gain": recall_condition.resonance_gain,
                    "interference_radius": recall_condition.interference_radius,
                    "interference_gain": recall_condition.interference_gain,
                    "competition_gain": recall_condition.competition_gain,
                    "basin_radius": recall_condition.basin_radius,
                    "split_threshold": recall_condition.split_threshold,
                    **metrics,
                    "score": score_recall(metrics),
                }
            )

    summary_rows: list[dict] = []
    for spec in specs:
        subset = [row for row in direct_rows if row["flow"] == spec.flow]
        best = max(subset, key=lambda row: row["score"])
        mean_score = float(np.mean([row["score"] for row in subset]))
        seq, diag = build_interference_sequence(
            spec.alpha,
            spec.condition,
            RecallCondition(
                context_pressure=best["context_pressure"],
                similarity_threshold=best["similarity_threshold"],
                recall_window=int(best["recall_window"]),
                recall_gain=best["recall_gain"],
                layer_window=int(best["layer_window"]),
                recency_decay=best["recency_decay"],
                resonance_gain=best["resonance_gain"],
                interference_radius=int(best["interference_radius"]),
                interference_gain=best["interference_gain"],
                competition_gain=best["competition_gain"],
                basin_radius=int(best["basin_radius"]),
                split_threshold=best["split_threshold"],
            ),
        )
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
            "same_region_recalls": 0.0,
            "split_events": 0.0,
            "context_distortions": 0.0,
            "blocked_contexts": 0.0,
            "interference_coherences": 0.0,
            "interference_checks": 1.0,
        }
        summary_rows.append(
            {
                "flow": spec.flow,
                "family": spec.family,
                "best_score": best["score"],
                "best_delay": spec.condition.delay,
                "best_slot_count": spec.condition.slot_count,
                "best_context_pressure": best["context_pressure"],
                "best_similarity_threshold": best["similarity_threshold"],
                "best_recall_window": best["recall_window"],
                "best_interference_radius": best["interference_radius"],
                "best_interference_gain": best["interference_gain"],
                "best_competition_gain": best["competition_gain"],
                "mean_score": mean_score,
                "mean_recall_survival_rate": float(np.mean([row["recall_survival_rate"] for row in subset])),
                "mean_same_slot_recall_rate": float(np.mean([row["same_slot_recall_rate"] for row in subset])),
                "mean_same_region_recall_rate": float(np.mean([row["same_region_recall_rate"] for row in subset])),
                "mean_interference_coherence_rate": float(np.mean([row["interference_coherence_rate"] for row in subset])),
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
    report = f"""# Golden Zipper v36 - Cross-Knot Interference

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best flow by mean score: `{best['flow']}` with `{best['mean_score']:.3f}`

Golden result:
- mean score: `{golden['mean_score']:.3f}`
- best context pressure: `{golden['best_context_pressure']:.3f}`
- best similarity threshold: `{golden['best_similarity_threshold']:.3f}`
- best recall window: `{golden['best_recall_window']}`
- best interference radius: `{golden['best_interference_radius']}`
- best interference gain: `{golden['best_interference_gain']:.3f}`
- best competition gain: `{golden['best_competition_gain']:.3f}`
- mean recall survival rate: `{golden['mean_recall_survival_rate']:.3f}`
- mean same-slot recall rate: `{golden['mean_same_slot_recall_rate']:.3f}`
- mean same-region recall rate: `{golden['mean_same_region_recall_rate']:.3f}`
- mean interference coherence rate: `{golden['mean_interference_coherence_rate']:.3f}`
- mean context distortion rate: `{golden['mean_context_distortion_rate']:.3f}`
- mean blocked context rate: `{golden['mean_blocked_context_rate']:.3f}`
- mean split rate: `{golden['mean_split_rate']:.3f}`
- density gap: `{golden['density_gap']:.3f}`

Interpretation:
- This panel tests whether neighboring knot-families shape recall through reinforcement and competition.
- A useful result should improve same-region recall or stability without blowing up split pressure.
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best flow by mean score: {best['flow']} {best['mean_score']:.3f}")
    print(f"golden mean score: {golden['mean_score']:.3f}")
    print(f"golden best interference_radius: {golden['best_interference_radius']}")
    print(f"golden best interference_gain: {golden['best_interference_gain']:.3f}")
    print(f"golden best competition_gain: {golden['best_competition_gain']:.3f}")
    print(f"golden same-region recall rate: {golden['mean_same_region_recall_rate']:.3f}")
    print(f"golden interference coherence rate: {golden['mean_interference_coherence_rate']:.3f}")
    print(f"golden split rate: {golden['mean_split_rate']:.3f}")
    print(f"golden density gap: {golden['density_gap']:.3f}")


if __name__ == "__main__":
    main()
