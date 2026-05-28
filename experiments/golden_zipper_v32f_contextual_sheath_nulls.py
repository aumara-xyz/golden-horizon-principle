#!/usr/bin/env python3
"""v32f contextual sheath nulls.

This attacks the best v32e recall object directly:
- real same-groove contextual sheath
- shuffled similarity null
- random tint null
- slot-break null

Toy telemetry only. Not physics evidence. Not proof of GHP.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import golden_zipper_v23_boundary_pocket_attractor as v23
import golden_zipper_v31b_phase_null_repair as v31b


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v32f_outputs"
V32E_SUMMARY = ROOT / "golden_zipper_v32e_outputs" / "summary.csv"

SEED = 20260523
RNG = np.random.default_rng(SEED)
MODES = ["real", "shuffled_similarity", "random_tint", "slot_break"]


@dataclass(frozen=True)
class RecallCondition:
    context_pressure: float
    similarity_threshold: float
    recall_window: int
    recall_gain: float
    sheath_gain: float
    bleed_rate: float
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


def load_best_conditions() -> list[tuple[object, RecallCondition]]:
    specs = {spec.flow: spec for spec in v31b.find_best_specs()}
    rows = list(csv.DictReader(V32E_SUMMARY.open()))
    selected: list[tuple[object, RecallCondition]] = []
    for row in rows:
        spec = specs[row["flow"]]
        selected.append(
            (
                spec,
                RecallCondition(
                    context_pressure=float(row["best_context_pressure"]),
                    similarity_threshold=float(row["best_similarity_threshold"]),
                    recall_window=int(float(row["best_recall_window"])),
                    recall_gain=float(row["best_recall_gain"]),
                    sheath_gain=float(row["best_sheath_gain"]),
                    bleed_rate=float(row["best_bleed_rate"]),
                    split_threshold=float(row["best_split_threshold"]),
                ),
            )
        )
    return selected


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
        "split_rate": diag["split_events"] / recall_hits,
        "context_distortion_rate": diag["context_distortions"] / recall_hits,
        "blocked_context_rate": diag["blocked_contexts"] / recall_hits,
        "pollution": float(np.mean((seq[:-1] == 1) & (seq[1:] <= -1))) if len(seq) > 1 else 0.0,
        "phase_lock_resistance": v23.phase_lock_resistance(seq),
    }


def run_sequence(alpha: float, base_condition, recall_condition: RecallCondition, mode: str) -> tuple[np.ndarray, dict[str, float]]:
    hidden = v31b.v31.hidden_trace(alpha)
    seq = np.full(v31b.v31.LENGTH, -2, dtype=np.int8)
    charges = np.zeros(base_condition.slot_count, dtype=float)
    grooves = np.zeros((base_condition.slot_count, base_condition.slot_count), dtype=float)
    memory_age = np.full(base_condition.slot_count, -9999, dtype=int)
    last_slot = -1
    last_witness_at = np.full(base_condition.slot_count, -9999, dtype=int)

    witnesses = writes = releases = ruptures = witness_to_write = 0
    recall_hits = recall_survivals = same_slot_recalls = split_events = 0
    context_distortions = blocked_contexts = 0

    similarity_bank = RNG.random(v31b.v31.LENGTH)
    tint_bank = RNG.random(v31b.v31.LENGTH)

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
            if mode == "shuffled_similarity":
                context_similarity = float(similarity_bank[idx])
            if context_similarity >= recall_condition.similarity_threshold:
                if mode == "random_tint":
                    tint = recall_condition.context_pressure * float(tint_bank[idx])
                else:
                    tint = recall_condition.context_pressure * max(context_similarity - recall_condition.similarity_threshold, 0.0)
                if tint > 0.03:
                    context_distortions += 1

                same_slot_recalls += 1
                recall_survivals += 1
                charges[slot] += recall_condition.recall_gain * (charges[slot] + incoming_groove)
                grooves[slot, slot] += recall_condition.sheath_gain * (contact + phase_alignment)

                neighbor_bleed = recall_condition.bleed_rate * tint * max(charges[slot], 0.10)
                if neighbor_bleed > 0.0:
                    left = (slot - 1) % base_condition.slot_count
                    right = (slot + 1) % base_condition.slot_count
                    if mode == "slot_break":
                        left = int(RNG.integers(0, base_condition.slot_count))
                        right = int(RNG.integers(0, base_condition.slot_count))
                    charges[left] += neighbor_bleed * 0.5
                    charges[right] += neighbor_bleed * 0.5
                    if max(charges[left], charges[right]) >= recall_condition.split_threshold:
                        split_events += 1
                        seq[idx] = 2
                        ruptures += 1
                        charges[left] *= 0.40
                        charges[right] *= 0.40
                        last_slot = slot
                        continue
            else:
                blocked_contexts += 1
                charges[slot] += recall_condition.recall_gain * recall_condition.bleed_rate * 0.20

        sheath_support = grooves[slot, slot] * 0.5
        charges[slot] += base_condition.stack_gain * contact + neighbor_support + phase_support + sheath_support
        effective_charge = charges[slot] + incoming_groove + neighbor_support + phase_support + sheath_support

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

    diag = {
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
    return seq, diag


def main() -> None:
    ensure_dir(OUT)
    specs = load_best_conditions()

    rows: list[dict] = []
    for spec, recall_condition in specs:
        real_score = None
        mode_scores: dict[str, float] = {}
        for mode in MODES:
            seq, diag = run_sequence(spec.alpha, spec.condition, recall_condition, mode)
            metrics = evaluate_recall(seq, diag)
            score = score_recall(metrics)
            mode_scores[mode] = score
            row = {
                "flow": spec.flow,
                "family": spec.family,
                "mode": mode,
                "score": score,
                **metrics,
            }
            rows.append(row)
            if mode == "real":
                real_score = score
        assert real_score is not None
        for row in rows[-len(MODES):]:
            row["gap_from_real"] = real_score - row["score"]

    write_csv(rows, OUT / "mode_metrics.csv")

    summary_rows: list[dict] = []
    flow_names = sorted({row["flow"] for row in rows})
    for flow in flow_names:
        subset = [row for row in rows if row["flow"] == flow]
        real = next(row for row in subset if row["mode"] == "real")
        summary_rows.append(
            {
                "flow": flow,
                "real_score": real["score"],
                "same_slot_recall_rate": real["same_slot_recall_rate"],
                "context_distortion_rate": real["context_distortion_rate"],
                "split_rate": real["split_rate"],
                "shuffled_similarity_gap": real["score"] - next(row for row in subset if row["mode"] == "shuffled_similarity")["score"],
                "random_tint_gap": real["score"] - next(row for row in subset if row["mode"] == "random_tint")["score"],
                "slot_break_gap": real["score"] - next(row for row in subset if row["mode"] == "slot_break")["score"],
            }
        )

    write_csv(summary_rows, OUT / "summary.csv")
    ranked = sorted(summary_rows, key=lambda row: row["real_score"], reverse=True)
    golden = next(row for row in summary_rows if row["flow"] == "golden")
    best = ranked[0]

    report = f"""# Golden Zipper v32f - Contextual Sheath Nulls

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best flow by real score: `{best['flow']}` with `{best['real_score']:.3f}`

Golden result:
- real score: `{golden['real_score']:.3f}`
- same-slot recall rate: `{golden['same_slot_recall_rate']:.3f}`
- context distortion rate: `{golden['context_distortion_rate']:.3f}`
- split rate: `{golden['split_rate']:.3f}`
- shuffled similarity gap: `{golden['shuffled_similarity_gap']:.3f}`
- random tint gap: `{golden['random_tint_gap']:.3f}`
- slot-break gap: `{golden['slot_break_gap']:.3f}`

Interpretation:
- This panel attacks the best v32e object with context-coupling nulls.
- A useful result keeps positive gaps against shuffled similarity, random tint, and slot-break nulls.
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best flow by real score: {best['flow']} {best['real_score']:.3f}")
    print(f"golden real score: {golden['real_score']:.3f}")
    print(f"golden same-slot recall rate: {golden['same_slot_recall_rate']:.3f}")
    print(f"golden shuffled similarity gap: {golden['shuffled_similarity_gap']:.3f}")
    print(f"golden random tint gap: {golden['random_tint_gap']:.3f}")
    print(f"golden slot-break gap: {golden['slot_break_gap']:.3f}")


if __name__ == "__main__":
    main()
