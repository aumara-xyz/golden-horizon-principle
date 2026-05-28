#!/usr/bin/env python3
"""v36c distance specificity nulls.

This asks whether cross-knot interference depends on locality:
- real distance-weighted interference
- flat-distance interference
- far-only interference
- near-only interference

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import golden_zipper_v36_cross_knot_interference as v36


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v36c_outputs"
V36_SUMMARY = ROOT / "golden_zipper_v36_outputs" / "summary.csv"

SEED = 20260524
RNG = np.random.default_rng(SEED)
MODES = ["real", "flat_distance", "far_only", "near_only"]


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


def load_best_conditions():
    specs = {spec.flow: spec for spec in v36.v31b.find_best_specs()}
    rows = list(csv.DictReader(V36_SUMMARY.open()))
    selected = []
    for row in rows:
        spec = specs[row["flow"]]
        selected.append(
            (
                spec,
                v36.RecallCondition(
                    context_pressure=float(row["best_context_pressure"]),
                    similarity_threshold=float(row["best_similarity_threshold"]),
                    recall_window=int(float(row["best_recall_window"])),
                    recall_gain=0.14,
                    layer_window=13,
                    recency_decay=0.72,
                    resonance_gain=0.08,
                    interference_radius=int(float(row["best_interference_radius"])),
                    interference_gain=float(row["best_interference_gain"]),
                    competition_gain=float(row["best_competition_gain"]),
                    basin_radius=2,
                    split_threshold=0.24,
                ),
            )
        )
    return selected


def score_recall(metrics: dict[str, float]) -> float:
    return v36.score_recall(metrics)


def evaluate_recall(seq: np.ndarray, diag: dict[str, float]) -> dict[str, float]:
    return v36.evaluate_recall(seq, diag)


def distance_weight(distance: int, basin_radius: int, interference_radius: int, mode: str) -> float:
    if mode == "flat_distance":
        return 1.0
    midpoint = (basin_radius + interference_radius) / 2.0
    if mode == "near_only":
        return 1.0 if distance <= midpoint else 0.0
    if mode == "far_only":
        return 1.0 if distance > midpoint else 0.0
    return 1.0 / (1.0 + distance)


def run_sequence(alpha: float, base_condition, recall_condition, mode: str):
    hidden = v36.v31b.v31.hidden_trace(alpha)
    seq = np.full(v36.v31b.v31.LENGTH, -2, dtype=np.int8)
    charges = np.zeros(base_condition.slot_count, dtype=float)
    grooves = np.zeros((base_condition.slot_count, base_condition.slot_count), dtype=float)
    memory_age = np.full(base_condition.slot_count, -9999, dtype=int)
    last_slot = -1
    last_witness_at = np.full(base_condition.slot_count, -9999, dtype=int)

    layer_trace = np.zeros((base_condition.slot_count, recall_condition.layer_window), dtype=float)
    kernel = v36.temporal_kernel(recall_condition.layer_window, recall_condition.recency_decay)

    witnesses = writes = releases = ruptures = witness_to_write = 0
    recall_hits = recall_survivals = same_slot_recalls = same_region_recalls = 0
    split_events = context_distortions = blocked_contexts = interference_coherences = 0
    interference_checks = 0

    for idx in range(base_condition.delay + 2, v36.v31b.v31.LENGTH):
        charges *= base_condition.stack_decay
        grooves *= base_condition.groove_decay
        layer_trace[:, 1:] = layer_trace[:, :-1]
        layer_trace[:, 0] = 0.0

        delayed = hidden[idx - base_condition.delay]
        previous = hidden[idx - base_condition.delay - 1]
        contact = v36.v31b.v31.contact_likelihood(delayed, base_condition.window_width)
        if contact < 0.12:
            if np.max(charges) < 0.05:
                seq[idx] = -1
                releases += 1
            continue

        slot, phase = v36.v31b.v31.route_slot(delayed, previous, idx, alpha, base_condition)
        if last_slot >= 0:
            grooves[last_slot, slot] += base_condition.groove_gain * contact
        incoming_groove = float(np.max(grooves[:, slot])) if last_slot >= 0 else 0.0

        phase_alignment = 1.0 - abs(((phase + 0.5) % 1.0) - 0.5) * 2.0
        phase_support = base_condition.phase_gain * phase_alignment * (incoming_groove + contact)

        region = v36.region_members(slot, base_condition.slot_count, recall_condition.basin_radius)
        recent_region = [member for member in region if idx - memory_age[member] <= recall_condition.recall_window]
        region_layer_strength = float(np.mean([np.dot(layer_trace[member], kernel) for member in region]))

        neighbor_support = 0.0
        for neighbor in region:
            if neighbor != slot:
                distance = v36.v31b.v31.slot_distance(slot, neighbor, base_condition.slot_count)
                neighbor_support += charges[neighbor] * (1.0 / (1.0 + distance))
        neighbor_support *= base_condition.relation_gain

        outer_support = 0.0
        outer_competition = 0.0
        for neighbor in range(base_condition.slot_count):
            distance = v36.v31b.v31.slot_distance(slot, neighbor, base_condition.slot_count)
            if recall_condition.basin_radius < distance <= recall_condition.interference_radius:
                weight = distance_weight(distance, recall_condition.basin_radius, recall_condition.interference_radius, mode)
                if weight == 0.0:
                    continue
                interference_checks += 1
                neighbor_layer = float(np.dot(layer_trace[neighbor], kernel))
                coherence = 1.0 - abs(neighbor_layer - region_layer_strength)
                signed = (coherence - 0.5) * 2.0
                if signed >= 0:
                    outer_support += recall_condition.interference_gain * signed * charges[neighbor] * weight
                    if signed > 0.25:
                        interference_coherences += 1
                else:
                    outer_competition += recall_condition.competition_gain * abs(signed) * charges[neighbor] * weight

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

    diag = {
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
    return seq, diag


def main() -> None:
    ensure_dir(OUT)
    specs = load_best_conditions()

    rows = []
    for spec, recall_condition in specs:
        real_score = None
        for mode in MODES:
            seq, diag = run_sequence(spec.alpha, spec.condition, recall_condition, mode)
            metrics = evaluate_recall(seq, diag)
            score = score_recall(metrics)
            row = {"flow": spec.flow, "family": spec.family, "mode": mode, "score": score, **metrics}
            rows.append(row)
            if mode == "real":
                real_score = score
        assert real_score is not None
        for row in rows[-len(MODES):]:
            row["gap_from_real"] = real_score - row["score"]

    write_csv(rows, OUT / "mode_metrics.csv")

    summary_rows = []
    for flow in sorted({row["flow"] for row in rows}):
        subset = [row for row in rows if row["flow"] == flow]
        real = next(row for row in subset if row["mode"] == "real")
        summary_rows.append(
            {
                "flow": flow,
                "real_score": real["score"],
                "same_region_recall_rate": real["same_region_recall_rate"],
                "split_rate": real["split_rate"],
                "flat_distance_gap": real["score"] - next(row for row in subset if row["mode"] == "flat_distance")["score"],
                "far_only_gap": real["score"] - next(row for row in subset if row["mode"] == "far_only")["score"],
                "near_only_gap": real["score"] - next(row for row in subset if row["mode"] == "near_only")["score"],
            }
        )

    write_csv(summary_rows, OUT / "summary.csv")
    ranked = sorted(summary_rows, key=lambda row: row["real_score"], reverse=True)
    best = ranked[0]
    golden = next(row for row in summary_rows if row["flow"] == "golden")

    report = f"""# Golden Zipper v36c - Distance Specificity Nulls

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best flow by real score: `{best['flow']}` with `{best['real_score']:.3f}`

Golden result:
- real score: `{golden['real_score']:.3f}`
- same-region recall rate: `{golden['same_region_recall_rate']:.3f}`
- split rate: `{golden['split_rate']:.3f}`
- flat-distance gap: `{golden['flat_distance_gap']:.3f}`
- far-only gap: `{golden['far_only_gap']:.3f}`
- near-only gap: `{golden['near_only_gap']:.3f}`

Interpretation:
- This panel asks whether cross-knot interference depends on locality.
- A useful result keeps positive gaps when distance structure is flattened or shifted.
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best flow by real score: {best['flow']} {best['real_score']:.3f}")
    print(f"golden real score: {golden['real_score']:.3f}")
    print(f"golden same-region recall rate: {golden['same_region_recall_rate']:.3f}")
    print(f"golden flat-distance gap: {golden['flat_distance_gap']:.3f}")
    print(f"golden far-only gap: {golden['far_only_gap']:.3f}")
    print(f"golden near-only gap: {golden['near_only_gap']:.3f}")


if __name__ == "__main__":
    main()
