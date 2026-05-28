#!/usr/bin/env python3
"""v37b relational field nulls.

This attacks the v37 field-identity object:
- real relational field
- no field coupling
- flat field
- shuffled field footprint

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import golden_zipper_v37_relational_field_identity as v37


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v37b_outputs"
V37_SUMMARY = ROOT / "golden_zipper_v37_outputs" / "summary.csv"

SEED = 20260525
RNG = np.random.default_rng(SEED)
MODES = ["real", "no_field", "flat_field", "shuffled_field"]


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
    specs = {spec.flow: spec for spec in v37.v31b.find_best_specs()}
    rows = list(csv.DictReader(V37_SUMMARY.open()))
    selected = []
    for row in rows:
        spec = specs[row["flow"]]
        selected.append(
            (
                spec,
                v37.RecallCondition(
                    context_pressure=float(row["best_context_pressure"]),
                    similarity_threshold=float(row["best_similarity_threshold"]),
                    recall_window=int(float(row["best_recall_window"])),
                    recall_gain=0.14,
                    layer_window=13,
                    recency_decay=0.72,
                    resonance_gain=0.08,
                    field_radius=int(float(row["best_field_radius"])),
                    field_width=float(row["best_field_width"]),
                    field_support_gain=float(row["best_field_support_gain"]),
                    field_competition_gain=float(row["best_field_competition_gain"]),
                    split_threshold=0.24,
                ),
            )
        )
    return selected


def score_recall(metrics: dict[str, float]) -> float:
    return v37.score_recall(metrics)


def evaluate_recall(seq: np.ndarray, diag: dict[str, float]) -> dict[str, float]:
    return v37.evaluate_recall(seq, diag)


def field_mode(slot: int, slot_count: int, recall_condition, mode: str) -> np.ndarray:
    field = v37.field_weights(slot, slot_count, recall_condition.field_radius, recall_condition.field_width)
    if mode == "real":
        return field
    if mode == "no_field":
        out = np.zeros_like(field)
        out[slot] = 1.0
        return out
    if mode == "flat_field":
        mask = field > 0
        out = np.zeros_like(field)
        out[mask] = 1.0 / max(mask.sum(), 1)
        return out
    nonzero = field[field > 0]
    shuffled = nonzero.copy()
    RNG.shuffle(shuffled)
    out = np.zeros_like(field)
    out[field > 0] = shuffled
    total = out.sum()
    if total > 0:
        out /= total
    return out


def run_sequence(alpha: float, base_condition, recall_condition, mode: str):
    hidden = v37.v31b.v31.hidden_trace(alpha)
    seq = np.full(v37.v31b.v31.LENGTH, -2, dtype=np.int8)
    charges = np.zeros(base_condition.slot_count, dtype=float)
    grooves = np.zeros((base_condition.slot_count, base_condition.slot_count), dtype=float)
    memory_age = np.full(base_condition.slot_count, -9999, dtype=int)
    last_slot = -1
    last_witness_at = np.full(base_condition.slot_count, -9999, dtype=int)

    layer_trace = np.zeros((base_condition.slot_count, recall_condition.layer_window), dtype=float)
    kernel = v37.temporal_kernel(recall_condition.layer_window, recall_condition.recency_decay)

    witnesses = writes = releases = ruptures = witness_to_write = 0
    recall_hits = recall_survivals = same_core_recalls = same_field_recalls = 0
    split_events = context_distortions = blocked_contexts = overlap_events = 0

    perm = RNG.permutation(base_condition.slot_count)

    for idx in range(base_condition.delay + 2, v37.v31b.v31.LENGTH):
        charges *= base_condition.stack_decay
        grooves *= base_condition.groove_decay
        layer_trace[:, 1:] = layer_trace[:, :-1]
        layer_trace[:, 0] = 0.0

        delayed = hidden[idx - base_condition.delay]
        previous = hidden[idx - base_condition.delay - 1]
        contact = v37.v31b.v31.contact_likelihood(delayed, base_condition.window_width)
        if contact < 0.12:
            if np.max(charges) < 0.05:
                seq[idx] = -1
                releases += 1
            continue

        slot, phase = v37.v31b.v31.route_slot(delayed, previous, idx, alpha, base_condition)
        if last_slot >= 0:
            grooves[last_slot, slot] += base_condition.groove_gain * contact
        incoming_groove = float(np.max(grooves[:, slot])) if last_slot >= 0 else 0.0

        phase_alignment = 1.0 - abs(((phase + 0.5) % 1.0) - 0.5) * 2.0
        phase_support = base_condition.phase_gain * phase_alignment * (incoming_groove + contact)

        field = field_mode(slot, base_condition.slot_count, recall_condition, mode)
        field_charge = float(np.dot(charges, field))
        field_layer = float(np.dot(np.dot(layer_trace, kernel), field))
        core_recent = idx - memory_age[slot] <= recall_condition.recall_window
        field_recent = np.any(field * ((idx - memory_age) <= recall_condition.recall_window) > 0)

        support = 0.0
        competition = 0.0
        for neighbor in range(base_condition.slot_count):
            if neighbor == slot:
                continue
            probe = perm[neighbor] if mode == "shuffled_field" else neighbor
            weight = field[probe]
            if weight == 0.0:
                continue
            neighbor_layer = float(np.dot(layer_trace[probe], kernel))
            coherence = 1.0 - abs(neighbor_layer - field_layer)
            signed = (coherence - 0.5) * 2.0
            if signed >= 0:
                support += recall_condition.field_support_gain * signed * charges[probe] * weight
                if signed > 0.25:
                    overlap_events += 1
            else:
                competition += recall_condition.field_competition_gain * abs(signed) * charges[probe] * weight

        if field_recent:
            recall_hits += 1
            context_similarity = 1.0 - abs(phase_alignment - contact)
            echo_support = 0.35 * min(field_layer / max(recall_condition.resonance_gain, 1e-9), 1.5)
            soft_admit = context_similarity + echo_support
            soft_threshold = recall_condition.similarity_threshold + 0.10
            if soft_admit >= soft_threshold:
                tint = recall_condition.context_pressure * max(context_similarity - recall_condition.similarity_threshold, 0.0)
                if tint > 0.03:
                    context_distortions += 1
                recall_survivals += 1
                same_field_recalls += 1
                if core_recent:
                    same_core_recalls += 1

                charges += recall_condition.recall_gain * 0.25 * field * (field_charge + incoming_groove + support)
                charges[slot] += recall_condition.recall_gain * 0.55 * (
                    charges[slot] + incoming_groove + 0.40 * field_layer + support - competition
                )
                grooves[slot] += recall_condition.resonance_gain * field * (contact + phase_alignment)
                layer_trace[:, 0] += recall_condition.resonance_gain * field * (0.5 + contact + phase_alignment)

                spill = recall_condition.context_pressure * tint * max(charges[slot], 0.10) + competition * 0.5
                if spill > 0.0:
                    far_slot = (slot + recall_condition.field_radius + 2) % base_condition.slot_count
                    charges[far_slot] += spill
                    if charges[far_slot] >= recall_condition.split_threshold:
                        split_events += 1
                        seq[idx] = 2
                        ruptures += 1
                        charges[far_slot] *= 0.40
                        last_slot = slot
                        continue
            else:
                blocked_contexts += 1
                charges[slot] += recall_condition.recall_gain * (0.08 + 0.10 * min(field_layer, 1.0))

        total_support = 0.30 * field_layer + support - 0.5 * competition
        charges[slot] += base_condition.stack_gain * contact + phase_support + total_support
        effective_charge = charges[slot] + incoming_groove + phase_support + total_support

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
        "same_core_recalls": float(same_core_recalls),
        "same_field_recalls": float(same_field_recalls),
        "split_events": float(split_events),
        "context_distortions": float(context_distortions),
        "blocked_contexts": float(blocked_contexts),
        "overlap_events": float(overlap_events),
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
                "same_field_recall_rate": real["same_field_recall_rate"],
                "same_core_recall_rate": real["same_core_recall_rate"],
                "split_rate": real["split_rate"],
                "no_field_gap": real["score"] - next(row for row in subset if row["mode"] == "no_field")["score"],
                "flat_field_gap": real["score"] - next(row for row in subset if row["mode"] == "flat_field")["score"],
                "shuffled_field_gap": real["score"] - next(row for row in subset if row["mode"] == "shuffled_field")["score"],
            }
        )

    write_csv(summary_rows, OUT / "summary.csv")
    ranked = sorted(summary_rows, key=lambda row: row["real_score"], reverse=True)
    best = ranked[0]
    golden = next(row for row in summary_rows if row["flow"] == "golden")

    report = f"""# Golden Zipper v37b - Relational Field Nulls

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best flow by real score: `{best['flow']}` with `{best['real_score']:.3f}`

Golden result:
- real score: `{golden['real_score']:.3f}`
- same-field recall rate: `{golden['same_field_recall_rate']:.3f}`
- same-core recall rate: `{golden['same_core_recall_rate']:.3f}`
- split rate: `{golden['split_rate']:.3f}`
- no-field gap: `{golden['no_field_gap']:.3f}`
- flat-field gap: `{golden['flat_field_gap']:.3f}`
- shuffled-field gap: `{golden['shuffled_field_gap']:.3f}`

Interpretation:
- This panel attacks whether the relational field itself is doing work.
- A useful result keeps positive gaps when the field is removed, flattened, or scrambled.
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best flow by real score: {best['flow']} {best['real_score']:.3f}")
    print(f"golden real score: {golden['real_score']:.3f}")
    print(f"golden same-field recall rate: {golden['same_field_recall_rate']:.3f}")
    print(f"golden no-field gap: {golden['no_field_gap']:.3f}")
    print(f"golden flat-field gap: {golden['flat_field_gap']:.3f}")
    print(f"golden shuffled-field gap: {golden['shuffled_field_gap']:.3f}")


if __name__ == "__main__":
    main()
