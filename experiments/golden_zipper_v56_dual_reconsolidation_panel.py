#!/usr/bin/env python3
"""v56 dual reconsolidation panel.

This tests whether recall should have two modes:
- touch-up for mild mismatch
- melt-resettle for stronger mismatch

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import golden_zipper_v41_prediction_band_binding as v41


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v56_outputs"
V41_SUMMARY = ROOT / "golden_zipper_v41_outputs" / "summary.csv"

SEED = 20260526
RNG = np.random.default_rng(SEED)
MODES = {
    "rigid": {"binding_mode": "real", "mode_kind": "rigid", "random_plastic": False},
    "touch_up": {"binding_mode": "real", "mode_kind": "touch_up", "random_plastic": False},
    "dual_recon": {"binding_mode": "real", "mode_kind": "dual_recon", "random_plastic": False},
    "melt_heavy": {"binding_mode": "real", "mode_kind": "melt_heavy", "random_plastic": False},
}


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
    specs = {spec.flow: spec for spec in v41.v31b.find_best_specs()}
    rows = list(csv.DictReader(V41_SUMMARY.open()))
    selected = []
    for row in rows:
        spec = specs[row["flow"]]
        selected.append(
            (
                spec,
                v41.RecallCondition(
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
                    phase_bind_gain=float(row["best_phase_bind_gain"]),
                    phase_bind_threshold=float(row["best_phase_bind_threshold"]),
                    window_levels=int(float(row["best_window_levels"])),
                    window_blend_gain=float(row["best_window_blend_gain"]),
                    admission_center=float(row["best_admission_center"]),
                    admission_width=float(row["best_admission_width"]),
                    admission_gain=float(row["best_admission_gain"]),
                    split_threshold=0.24,
                ),
            )
        )
    return selected


def score_recall(metrics: dict[str, float]) -> float:
    return v41.score_recall(metrics)


def evaluate_recall(seq: np.ndarray, diag: dict[str, float]) -> dict[str, float]:
    metrics = v41.evaluate_recall(seq, diag)
    metrics["rewrite_drift_rate"] = diag["rewrite_drift_events"] / max(diag["recall_hits"], 1.0)
    return metrics


def run_sequence(
    alpha: float,
    base_condition,
    recall_condition,
    binding_mode: str,
    mode_kind: str,
    random_plastic: bool = False,
):
    hidden = v41.v31b.v31.hidden_trace(alpha)
    seq = np.full(v41.v31b.v31.LENGTH, -2, dtype=np.int8)
    charges = np.zeros(base_condition.slot_count, dtype=float)
    grooves = np.zeros((base_condition.slot_count, base_condition.slot_count), dtype=float)
    memory_age = np.full(base_condition.slot_count, -9999, dtype=int)
    last_slot = -1
    last_witness_at = np.full(base_condition.slot_count, -9999, dtype=int)

    layer_trace = np.zeros((base_condition.slot_count, recall_condition.layer_window), dtype=float)
    kernel = v41.temporal_kernel(recall_condition.layer_window, recall_condition.recency_decay)
    perm = RNG.permutation(base_condition.slot_count)
    window_levels = recall_condition.window_levels
    window_blend_gain = recall_condition.window_blend_gain
    admission_gain = recall_condition.admission_gain

    witnesses = writes = releases = ruptures = witness_to_write = 0
    recall_hits = recall_survivals = same_core_recalls = same_field_recalls = 0
    split_events = context_distortions = blocked_contexts = overlap_events = phase_bind_events = macro_window_events = admission_band_events = rewrite_drift_events = 0

    for idx in range(base_condition.delay + 2, v41.v31b.v31.LENGTH):
        charges *= base_condition.stack_decay
        grooves *= base_condition.groove_decay
        layer_trace[:, 1:] = layer_trace[:, :-1]
        layer_trace[:, 0] = 0.0

        delayed = hidden[idx - base_condition.delay]
        previous = hidden[idx - base_condition.delay - 1]
        contact = v41.v31b.v31.contact_likelihood(delayed, base_condition.window_width)
        if contact < 0.12:
            if np.max(charges) < 0.05:
                seq[idx] = -1
                releases += 1
            continue

        slot, phase = v41.v31b.v31.route_slot(delayed, previous, idx, alpha, base_condition)
        if last_slot >= 0:
            grooves[last_slot, slot] += base_condition.groove_gain * contact
        incoming_groove = float(np.max(grooves[:, slot])) if last_slot >= 0 else 0.0

        phase_alignment = 1.0 - abs(((phase + 0.5) % 1.0) - 0.5) * 2.0
        phase_support = base_condition.phase_gain * phase_alignment * (incoming_groove + contact)

        field = v41.field_weights(slot, base_condition.slot_count, recall_condition.field_radius, recall_condition.field_width)
        field_charge = float(np.dot(charges, field))
        base_layer = float(np.dot(np.dot(layer_trace, kernel), field))
        layer_strengths = [base_layer]
        for level in range(2, window_levels + 1):
            coarse_kernel = v41.temporal_kernel(
                recall_condition.layer_window,
                min(0.92, recall_condition.recency_decay ** (1 / level)),
            )
            layer_strengths.append(float(np.dot(np.dot(layer_trace, coarse_kernel), field)))
        field_layer = max(layer_strengths)
        if len(layer_strengths) > 1 and np.argmax(layer_strengths) > 0:
            macro_window_events += 1
        core_recent = idx - memory_age[slot] <= recall_condition.recall_window
        field_recent = np.any((idx - memory_age) <= recall_condition.recall_window) and np.any(
            field * ((idx - memory_age) <= recall_condition.recall_window) > 0
        )

        phase_field = np.zeros(base_condition.slot_count, dtype=float)
        for neighbor in range(base_condition.slot_count):
            if field[neighbor] == 0.0:
                continue
            probe = perm[neighbor] if binding_mode == "shuffled_phase" else neighbor
            neighbor_phase = ((probe * alpha) + idx / max(base_condition.delay, 1)) % 1.0
            bind = 1.0 - abs(neighbor_phase - phase_alignment)
            bind = max(0.0, 1.0 - 2.0 * abs(bind - 0.5))
            if binding_mode == "no_binding":
                bind = 0.0
            elif binding_mode == "flat_binding":
                bind = 1.0
            phase_field[neighbor] = bind * field[neighbor]
        phase_bind_strength = float(phase_field.sum())
        if phase_bind_strength > recall_condition.phase_bind_threshold:
            phase_bind_events += 1

        support = 0.0
        competition = 0.0
        band_support = 0.0
        for neighbor in range(base_condition.slot_count):
            if neighbor == slot:
                continue
            weight = field[neighbor]
            if weight == 0.0:
                continue
            neighbor_layer = float(np.dot(layer_trace[neighbor], kernel))
            coherence = 1.0 - abs(neighbor_layer - field_layer)
            signed = (coherence - 0.5) * 2.0
            if signed >= 0:
                support += recall_condition.field_support_gain * signed * charges[neighbor] * weight
                if signed > 0.25:
                    overlap_events += 1
            else:
                competition += recall_condition.field_competition_gain * abs(signed) * charges[neighbor] * weight

        if field_recent:
            recall_hits += 1
            context_similarity = 1.0 - abs(phase_alignment - contact)
            echo_support = 0.30 * min(field_layer / max(recall_condition.resonance_gain, 1e-9), 1.5)
            bind_support = 0.35 * min(phase_bind_strength / max(recall_condition.phase_bind_threshold, 1e-9), 1.5)
            prediction_center = 0.5 * (field_layer + phase_bind_strength)
            prediction_error = abs(contact - prediction_center)
            band_shape = np.exp(
                -0.5
                * ((prediction_error - recall_condition.admission_center) / max(recall_condition.admission_width, 1e-9)) ** 2
            )
            band_support = admission_gain * float(band_shape)
            if band_support >= 0.08:
                admission_band_events += 1
            soft_admit = context_similarity + echo_support + bind_support + band_support
            soft_threshold = recall_condition.similarity_threshold + 0.10
            if soft_admit >= soft_threshold:
                tint = recall_condition.context_pressure * max(context_similarity - recall_condition.similarity_threshold, 0.0)
                if tint > 0.03:
                    context_distortions += 1
                recall_survivals += 1
                same_field_recalls += 1
                if core_recent:
                    same_core_recalls += 1

                charges += recall_condition.recall_gain * 0.25 * field * (
                    field_charge
                    + incoming_groove
                    + support
                    + recall_condition.phase_bind_gain * phase_bind_strength
                    + window_blend_gain * field_layer
                    + band_support
                )
                charges[slot] += recall_condition.recall_gain * 0.55 * (
                    charges[slot]
                    + incoming_groove
                    + 0.40 * field_layer
                    + support
                    + recall_condition.phase_bind_gain * phase_bind_strength
                    + window_blend_gain * field_layer
                    + band_support
                    - competition
                )
                grooves[slot] += recall_condition.resonance_gain * phase_field * (contact + phase_alignment)
                layer_trace[:, 0] += recall_condition.resonance_gain * (
                    0.6 * field + 0.4 * phase_field
                ) * (0.5 + contact + phase_alignment)

                if mode_kind != "rigid":
                    if mode_kind == "rigid":
                        active_plasticity = 0.0
                        active_anchor = 0.18
                    elif mode_kind == "touch_up":
                        active_plasticity = 0.06
                        active_anchor = 0.18
                    elif mode_kind == "melt_heavy":
                        active_plasticity = 0.22 if prediction_error > 0.18 else 0.10
                        active_anchor = 0.06 if prediction_error > 0.18 else 0.14
                    else:
                        if prediction_error < 0.12:
                            active_plasticity = 0.04
                            active_anchor = 0.20
                        elif prediction_error < 0.26:
                            active_plasticity = 0.10
                            active_anchor = 0.15
                        else:
                            active_plasticity = 0.18
                            active_anchor = 0.08

                    if active_plasticity <= 0.0:
                        active_plasticity = 0.0
                        active_anchor = 0.18

                    rewrite_field = field.copy()
                    phase_total = phase_field.sum()
                    if phase_total > 0:
                        rewrite_field = 0.6 * field + 0.4 * (phase_field / phase_total)
                    rewrite_field_sum = rewrite_field.sum()
                    if rewrite_field_sum > 0:
                        rewrite_field = rewrite_field / rewrite_field_sum
                    if random_plastic:
                        rewrite_field = rewrite_field[perm]
                    rewrite_push = active_plasticity * (0.35 + field_layer + 0.5 * phase_bind_strength)
                    charges += 0.35 * rewrite_push * rewrite_field
                    charges[slot] += active_anchor * rewrite_push
                    drift_slot = (slot + recall_condition.field_radius + 1) % base_condition.slot_count
                    drift_push = max(active_plasticity - active_anchor, 0.0) * rewrite_push
                    if drift_push > 0.0:
                        charges[drift_slot] += 0.40 * drift_push
                        if drift_push >= 0.04:
                            rewrite_drift_events += 1

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
                charges[slot] += recall_condition.recall_gain * (
                    0.08
                    + 0.08 * min(field_layer, 1.0)
                    + 0.06 * min(phase_bind_strength, 1.0)
                    + 0.04 * band_support
                )

        total_support = 0.24 * field_layer + 0.20 * phase_bind_strength + 0.12 * band_support + support - 0.5 * competition
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
        "phase_bind_events": float(phase_bind_events),
        "macro_window_events": float(macro_window_events),
        "admission_band_events": float(admission_band_events),
        "rewrite_drift_events": float(rewrite_drift_events),
    }
    return seq, diag


def main() -> None:
    ensure_dir(OUT)
    specs = load_best_conditions()

    rows = []
    for spec, recall_condition in specs:
        real_score = None
        for mode, config in MODES.items():
            seq, diag = run_sequence(spec.alpha, spec.condition, recall_condition, **config)
            metrics = evaluate_recall(seq, diag)
            score = score_recall(metrics)
            row = {"flow": spec.flow, "family": spec.family, "mode": mode, "score": score, **metrics}
            rows.append(row)
            if mode == "dual_recon":
                real_score = score
        assert real_score is not None
        for row in rows[-len(MODES):]:
            row["gap_from_real"] = real_score - row["score"]

    write_csv(rows, OUT / "mode_metrics.csv")

    summary_rows = []
    for flow in sorted({row["flow"] for row in rows}):
        subset = [row for row in rows if row["flow"] == flow]
        real = next(row for row in subset if row["mode"] == "dual_recon")
        summary_rows.append(
            {
                "flow": flow,
                "best_mode": max(subset, key=lambda row: row["score"])["mode"],
                "dual_score": real["score"],
                "same_field_recall_rate": real["same_field_recall_rate"],
                "same_core_recall_rate": real["same_core_recall_rate"],
                "rewrite_drift_rate": real["rewrite_drift_rate"],
                "split_rate": real["split_rate"],
                "dual_vs_rigid_gap": real["score"] - next(row for row in subset if row["mode"] == "rigid")["score"],
                "dual_vs_touchup_gap": real["score"] - next(row for row in subset if row["mode"] == "touch_up")["score"],
                "dual_vs_meltheavy_gap": real["score"] - next(row for row in subset if row["mode"] == "melt_heavy")["score"],
            }
        )

    write_csv(summary_rows, OUT / "summary.csv")
    ranked = sorted(summary_rows, key=lambda row: row["dual_score"], reverse=True)
    best = ranked[0]
    golden = next(row for row in summary_rows if row["flow"] == "golden")

    report = f"""# Golden Zipper v56 - Dual Reconsolidation Panel

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best flow by dual-recon score: `{best['flow']}` with `{best['dual_score']:.3f}`

Golden result:
- best mode: `{golden['best_mode']}`
- dual score: `{golden['dual_score']:.3f}`
- same-field recall rate: `{golden['same_field_recall_rate']:.3f}`
- same-core recall rate: `{golden['same_core_recall_rate']:.3f}`
- rewrite drift rate: `{golden['rewrite_drift_rate']:.3f}`
- split rate: `{golden['split_rate']:.3f}`
- dual vs rigid gap: `{golden['dual_vs_rigid_gap']:.3f}`
- dual vs touch-up gap: `{golden['dual_vs_touchup_gap']:.3f}`
- dual vs melt-heavy gap: `{golden['dual_vs_meltheavy_gap']:.3f}`

Interpretation:
- This panel asks whether recall should switch between touch-up and melt-resettle modes.
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best flow by dual-recon score: {best['flow']} {best['dual_score']:.3f}")
    print(f"golden best mode: {golden['best_mode']}")
    print(f"golden dual score: {golden['dual_score']:.3f}")
    print(f"golden same-field recall rate: {golden['same_field_recall_rate']:.3f}")
    print(f"golden rewrite drift rate: {golden['rewrite_drift_rate']:.3f}")
    print(f"golden dual vs rigid gap: {golden['dual_vs_rigid_gap']:.3f}")
    print(f"golden dual vs touch-up gap: {golden['dual_vs_touchup_gap']:.3f}")
    print(f"golden dual vs melt-heavy gap: {golden['dual_vs_meltheavy_gap']:.3f}")


if __name__ == "__main__":
    main()
