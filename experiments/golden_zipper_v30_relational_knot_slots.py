#!/usr/bin/env python3
"""v30 relational knot-slot panel.

This tests the next Plinko correction:
- the pegs do not move
- delayed beads fall into nearby fixed probability slots
- memory is a knot-like stack in a slot
- nearby slots can support the same memory family

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
OUT = ROOT / "golden_zipper_v30_outputs"

SEED = 20260522
RNG = np.random.default_rng(SEED)

LENGTH = 4096
OFFSET_GRID = np.arange(-0.036, 0.0361, 0.012)
DELAYS = [5, 8, 13, 21]
SLOT_COUNTS = [8, 13, 21]
WINDOW_WIDTHS = [0.14, 0.22, 0.30]
STACK_GAINS = [0.10, 0.18, 0.30]
STACK_DECAYS = [0.94, 0.975, 0.992]
RELATION_GAINS = [0.00, 0.18, 0.36]
WITNESS_THRESHOLDS = [0.24, 0.36]
WRITE_THRESHOLDS = [0.54, 0.72]
RUPTURE_THRESHOLDS = [1.15, 1.55]
MAX_CONDITIONS = 150


@dataclass(frozen=True)
class FlowSpec:
    name: str
    alpha: float
    family: str


@dataclass(frozen=True)
class Condition:
    delay: int
    slot_count: int
    window_width: float
    stack_gain: float
    stack_decay: float
    relation_gain: float
    witness_threshold: float
    write_threshold: float
    rupture_threshold: float


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
            delay=delay,
            slot_count=slot_count,
            window_width=window_width,
            stack_gain=stack_gain,
            stack_decay=stack_decay,
            relation_gain=relation_gain,
            witness_threshold=witness_threshold,
            write_threshold=write_threshold,
            rupture_threshold=rupture_threshold,
        )
        for delay in DELAYS
        for slot_count in SLOT_COUNTS
        for window_width in WINDOW_WIDTHS
        for stack_gain in STACK_GAINS
        for stack_decay in STACK_DECAYS
        for relation_gain in RELATION_GAINS
        for witness_threshold in WITNESS_THRESHOLDS
        for write_threshold in WRITE_THRESHOLDS
        for rupture_threshold in RUPTURE_THRESHOLDS
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


def slot_distance(left: int, right: int, slot_count: int) -> int:
    raw = abs(left - right)
    return min(raw, slot_count - raw)


def route_slot(delayed: float, previous: float, idx: int, alpha: float, condition: Condition) -> int:
    contact = contact_likelihood(delayed, condition.window_width)
    slope = np.tanh(abs(delayed - previous))
    phase = (alpha * idx) % 1.0
    # Fixed board: the centers do not move; each bead is routed by its current feature vector.
    coordinate = (0.50 * contact + 0.30 * slope + 0.20 * phase) % 1.0
    return int(np.floor(coordinate * condition.slot_count)) % condition.slot_count


def build_sequence(mode: str, alpha: float, condition: Condition) -> tuple[np.ndarray, dict[str, float]]:
    hidden = hidden_trace(alpha)
    seq = np.full(LENGTH, -2, dtype=np.int8)
    charges = np.zeros(condition.slot_count, dtype=float)
    last_witness_at = np.full(condition.slot_count, -9999, dtype=int)
    last_write_slot = -1

    witnesses = 0
    writes = 0
    releases = 0
    ruptures = 0
    witness_to_write = 0
    relation_hits = 0
    slot_revisits = 0
    written_slots: list[int] = []

    for idx in range(condition.delay + 2, LENGTH):
        charges *= condition.stack_decay
        delayed = hidden[idx - condition.delay]
        previous = hidden[idx - condition.delay - 1]
        contact = contact_likelihood(delayed, condition.window_width)
        if contact < 0.12:
            if np.max(charges) < 0.05:
                seq[idx] = -1
                releases += 1
            continue

        slot = route_slot(delayed, previous, idx, alpha, condition)
        neighbor_support = 0.0
        if mode == "relational":
            for neighbor in range(condition.slot_count):
                distance = slot_distance(slot, neighbor, condition.slot_count)
                if 0 < distance <= 2:
                    neighbor_support += charges[neighbor] * (1.0 / (1.0 + distance))
            neighbor_support *= condition.relation_gain

        charges[slot] += condition.stack_gain * contact + neighbor_support
        effective_charge = charges[slot] + neighbor_support

        if last_write_slot >= 0 and slot_distance(slot, last_write_slot, condition.slot_count) <= 2:
            relation_hits += 1
        if last_witness_at[slot] > -9999:
            slot_revisits += 1

        if effective_charge >= condition.rupture_threshold:
            seq[idx] = 2
            ruptures += 1
            charges[slot] *= 0.20
            last_witness_at[slot] = -9999
            continue

        if effective_charge >= condition.write_threshold and last_witness_at[slot] > -9999:
            seq[idx] = 1
            writes += 1
            witness_to_write += 1
            written_slots.append(slot)
            last_write_slot = slot
            charges[slot] *= 0.45
            last_witness_at[slot] = -9999
            continue

        if effective_charge >= condition.witness_threshold:
            seq[idx] = 0
            witnesses += 1
            last_witness_at[slot] = idx
            continue

        seq[idx] = -1
        releases += 1

    occupied_slots = len(set(written_slots))
    return seq, {
        "witnesses": float(witnesses),
        "writes": float(writes),
        "releases": float(releases),
        "ruptures": float(ruptures),
        "witness_to_write": float(witness_to_write),
        "relation_hits": float(relation_hits),
        "slot_revisits": float(slot_revisits),
        "occupied_slots": float(occupied_slots),
        "mean_charge": float(np.mean(charges)),
        "max_charge": float(np.max(charges)),
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
        "relation_rate": diag["relation_hits"] / total_events,
        "slot_revisit_rate": diag["slot_revisits"] / total_events,
        "occupied_slots": diag["occupied_slots"],
        "mean_charge": diag["mean_charge"],
        "max_charge": diag["max_charge"],
        "pollution": pollution,
        "phase_lock_resistance": v23.phase_lock_resistance(seq),
    }


def score(metrics: dict[str, float]) -> float:
    occupancy = min(metrics["occupied_slots"] / 8.0, 1.0)
    relation = min(metrics["relation_rate"] / 0.35, 1.0)
    revisit = min(metrics["slot_revisit_rate"] / 0.35, 1.0)
    return float(
        0.16 * metrics["phase_lock_resistance"]
        + 0.18 * metrics["witness_conversion"]
        + 0.14 * metrics["delayed_retention"]
        + 0.12 * relation
        + 0.10 * revisit
        + 0.09 * occupancy
        + 0.08 * (1.0 - metrics["rupture_rate"])
        + 0.07 * (1.0 - metrics["pollution"])
        + 0.06 * (1.0 - metrics["release_rate"])
    )


def plot_summary(rows: list[dict], path: Path) -> None:
    labels = [f"{row['mode']}:{row['flow']}" for row in rows]
    scores = [row["mean_score"] for row in rows]
    density = [row["density_gap"] for row in rows]
    x = np.arange(len(labels))
    width = 0.35
    plt.figure(figsize=(13, 5))
    plt.bar(x - width / 2, scores, width=width, label="mean score")
    plt.bar(x + width / 2, density, width=width, label="density gap")
    plt.axhline(0.0, color="black", linewidth=1.0)
    plt.xticks(x, labels, rotation=35, ha="right")
    plt.tight_layout()
    plt.legend()
    plt.savefig(path, dpi=180)
    plt.close()


def main() -> None:
    ensure_dir(OUT)
    flows = build_flows()
    conditions = build_conditions()
    modes = ["independent", "relational"]

    direct_rows: list[dict] = []
    for mode in modes:
        print(f"mode: {mode}")
        for flow in flows:
            for condition in conditions:
                for offset in OFFSET_GRID:
                    alpha = flow.alpha + float(offset)
                    if not (0.0 < alpha < 1.0):
                        continue
                    seq, diag = build_sequence(mode, alpha, condition)
                    metrics = evaluate(seq, diag)
                    direct_rows.append(
                        {
                            "mode": mode,
                            "flow": flow.name,
                            "family": flow.family,
                            "alpha": alpha,
                            "offset": float(offset),
                            "delay": condition.delay,
                            "slot_count": condition.slot_count,
                            "window_width": condition.window_width,
                            "stack_gain": condition.stack_gain,
                            "stack_decay": condition.stack_decay,
                            "relation_gain": condition.relation_gain,
                            "witness_threshold": condition.witness_threshold,
                            "write_threshold": condition.write_threshold,
                            "rupture_threshold": condition.rupture_threshold,
                            **metrics,
                            "score": score(metrics),
                        }
                    )

    summary_rows: list[dict] = []
    for mode in modes:
        for flow in flows:
            subset = [row for row in direct_rows if row["mode"] == mode and row["flow"] == flow.name]
            best = max(subset, key=lambda row: row["score"])
            condition = Condition(
                delay=int(best["delay"]),
                slot_count=int(best["slot_count"]),
                window_width=best["window_width"],
                stack_gain=best["stack_gain"],
                stack_decay=best["stack_decay"],
                relation_gain=best["relation_gain"],
                witness_threshold=best["witness_threshold"],
                write_threshold=best["write_threshold"],
                rupture_threshold=best["rupture_threshold"],
            )
            seq, _ = build_sequence(mode, best["alpha"], condition)
            density = density_surrogate(seq)
            block = block_surrogate(seq)
            zero_diag = {
                "witnesses": float(np.sum(density == 0)),
                "writes": float(np.sum(density == 1)),
                "releases": float(np.sum(density == -1)),
                "ruptures": float(np.sum(density == 2)),
                "witness_to_write": 0.0,
                "relation_hits": 0.0,
                "slot_revisits": 0.0,
                "occupied_slots": 0.0,
                "mean_charge": 0.0,
                "max_charge": 0.0,
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
            summary_rows.append(
                {
                    "mode": mode,
                    "flow": flow.name,
                    "family": flow.family,
                    "best_score": best["score"],
                    "best_delay": int(best["delay"]),
                    "best_slot_count": int(best["slot_count"]),
                    "mean_score": mean_score,
                    "mean_witness_conversion": float(np.mean([row["witness_conversion"] for row in subset])),
                    "mean_delayed_retention": float(np.mean([row["delayed_retention"] for row in subset])),
                    "mean_relation_rate": float(np.mean([row["relation_rate"] for row in subset])),
                    "mean_slot_revisit_rate": float(np.mean([row["slot_revisit_rate"] for row in subset])),
                    "mean_rupture_rate": float(np.mean([row["rupture_rate"] for row in subset])),
                    "density_gap": mean_score - density_score,
                    "block_gap": mean_score - block_score,
                }
            )

    ranked = sorted(summary_rows, key=lambda row: row["mean_score"], reverse=True)
    write_csv(direct_rows, OUT / "direct_metrics.csv")
    write_csv(summary_rows, OUT / "summary.csv")
    plot_summary(summary_rows, OUT / "summary.png")

    best = ranked[0]
    golden_rel = next(row for row in summary_rows if row["mode"] == "relational" and row["flow"] == "golden")
    independent_mean = float(np.mean([row["mean_score"] for row in summary_rows if row["mode"] == "independent"]))
    relational_mean = float(np.mean([row["mean_score"] for row in summary_rows if row["mode"] == "relational"]))

    report = f"""# Golden Zipper v30 - Relational Knot Slots

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best branch by mean score: `{best['mode']}:{best['flow']}` with `{best['mean_score']:.3f}`

Mode comparison:
- independent mean score: `{independent_mean:.3f}`
- relational mean score: `{relational_mean:.3f}`

Golden relational result:
- mean score: `{golden_rel['mean_score']:.3f}`
- best delay: `{golden_rel['best_delay']}`
- best slot count: `{golden_rel['best_slot_count']}`
- witness conversion: `{golden_rel['mean_witness_conversion']:.3f}`
- delayed retention: `{golden_rel['mean_delayed_retention']:.3f}`
- relation rate: `{golden_rel['mean_relation_rate']:.3f}`
- slot revisit rate: `{golden_rel['mean_slot_revisit_rate']:.3f}`
- rupture rate: `{golden_rel['mean_rupture_rate']:.3f}`
- density gap: `{golden_rel['density_gap']:.3f}`
- block gap: `{golden_rel['block_gap']:.3f}`

Interpretation:
- This panel treats memory as repeated beads stacking in fixed probability slots.
- The relational mode lets nearby slots support the same knot-family.
- A useful result would show relational mode beating independent slots while keeping positive null gaps.
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best: {best['mode']}:{best['flow']} {best['mean_score']:.3f}")
    print(f"independent mean: {independent_mean:.3f}")
    print(f"relational mean: {relational_mean:.3f}")
    print(f"golden relational mean: {golden_rel['mean_score']:.3f}")
    print(f"golden relational density gap: {golden_rel['density_gap']:.3f}")
    print(f"golden relational block gap: {golden_rel['block_gap']:.3f}")


if __name__ == "__main__":
    main()
