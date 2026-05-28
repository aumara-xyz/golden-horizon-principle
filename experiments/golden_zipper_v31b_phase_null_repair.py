#!/usr/bin/env python3
"""v31b stricter phase-null repair for path-phase groove memory.

This keeps the v31 object but attacks the phase claim directly with:
- phase scramble
- constant phase shift
- local phase jitter
- preserved slot counts with broken path order

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


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v31b_outputs"

SEED = 20260523
RNG = np.random.default_rng(SEED)


@dataclass(frozen=True)
class BestSpec:
    flow: str
    family: str
    alpha: float
    condition: v31.Condition


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


def find_best_specs() -> list[BestSpec]:
    flows = v31.build_flows()
    conditions = v31.build_conditions()
    specs: list[BestSpec] = []
    for flow in flows:
        best_row: dict | None = None
        best_score = -1.0
        for condition in conditions:
            for offset in v31.OFFSET_GRID:
                alpha = flow.alpha + float(offset)
                if not (0.0 < alpha < 1.0):
                    continue
                seq, diag = v31.build_sequence("phase_groove", alpha, condition)
                metrics = v31.evaluate(seq, diag)
                current = v31.score(metrics)
                if current > best_score:
                    best_score = current
                    best_row = {"alpha": alpha, "condition": condition}
        assert best_row is not None
        specs.append(BestSpec(flow.name, flow.family, best_row["alpha"], best_row["condition"]))
    return specs


def density_surrogate(seq: np.ndarray) -> np.ndarray:
    values, counts = np.unique(seq, return_counts=True)
    probs = counts / counts.sum()
    return RNG.choice(values, size=len(seq), p=probs).astype(np.int8)


def block_surrogate(seq: np.ndarray, block: int = 13) -> np.ndarray:
    chunks = [seq[idx : idx + block].copy() for idx in range(0, len(seq), block)]
    RNG.shuffle(chunks)
    return np.concatenate(chunks).astype(np.int8)


def constant_phase_shift(values: np.ndarray, shift: float) -> np.ndarray:
    return np.roll(values, int(shift * len(values)) % len(values))


def local_phase_jitter(values: np.ndarray, max_jitter: int = 5) -> np.ndarray:
    out = values.copy()
    for idx in range(0, len(values), 17):
        stop = min(idx + 17, len(values))
        segment = out[idx:stop].copy()
        if len(segment) <= 1:
            continue
        jitter = int(RNG.integers(-max_jitter, max_jitter + 1))
        out[idx:stop] = np.roll(segment, jitter % len(segment))
    return out


def broken_path_order(values: np.ndarray, block: int = 21) -> np.ndarray:
    chunks = [values[idx : idx + block].copy() for idx in range(0, len(values), block)]
    RNG.shuffle(chunks)
    return np.concatenate(chunks)


def build_sequence_from_hidden(alpha: float, condition: v31.Condition, hidden: np.ndarray) -> tuple[np.ndarray, dict[str, float]]:
    seq = np.full(v31.LENGTH, -2, dtype=np.int8)
    charges = np.zeros(condition.slot_count, dtype=float)
    grooves = np.zeros((condition.slot_count, condition.slot_count), dtype=float)
    last_slot = -1
    last_witness_at = np.full(condition.slot_count, -9999, dtype=int)

    witnesses = 0
    writes = 0
    releases = 0
    ruptures = 0
    witness_to_write = 0
    groove_hits = 0
    relation_hits = 0
    phase_hits = 0

    for idx in range(condition.delay + 2, v31.LENGTH):
        charges *= condition.stack_decay
        grooves *= condition.groove_decay
        delayed = hidden[idx - condition.delay]
        previous = hidden[idx - condition.delay - 1]
        contact = v31.contact_likelihood(delayed, condition.window_width)
        if contact < 0.12:
            if np.max(charges) < 0.05:
                seq[idx] = -1
                releases += 1
            continue

        slot, phase = v31.route_slot(delayed, previous, idx, alpha, condition)
        if last_slot >= 0:
            grooves[last_slot, slot] += condition.groove_gain * contact
        incoming_groove = float(np.max(grooves[:, slot])) if last_slot >= 0 else 0.0
        if incoming_groove > 0.08:
            groove_hits += 1

        neighbor_support = 0.0
        for neighbor in range(condition.slot_count):
            distance = v31.slot_distance(slot, neighbor, condition.slot_count)
            if 0 < distance <= 2:
                neighbor_support += charges[neighbor] * (1.0 / (1.0 + distance))
        neighbor_support *= condition.relation_gain

        phase_alignment = 1.0 - abs(((phase + 0.5) % 1.0) - 0.5) * 2.0
        phase_support = condition.phase_gain * phase_alignment * (incoming_groove + contact)
        if phase_support > 0.05:
            phase_hits += 1

        charges[slot] += condition.stack_gain * contact + neighbor_support + phase_support
        effective_charge = charges[slot] + neighbor_support + phase_support + incoming_groove
        if neighbor_support > 0.05:
            relation_hits += 1

        if effective_charge >= condition.rupture_threshold:
            seq[idx] = 2
            ruptures += 1
            charges[slot] *= 0.25
            last_witness_at[slot] = -9999
            last_slot = slot
            continue

        if effective_charge >= condition.write_threshold and last_witness_at[slot] > -9999:
            seq[idx] = 1
            writes += 1
            witness_to_write += 1
            charges[slot] *= 0.50
            last_witness_at[slot] = -9999
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

    total_groove = float(np.sum(grooves))
    return seq, {
        "witnesses": float(witnesses),
        "writes": float(writes),
        "releases": float(releases),
        "ruptures": float(ruptures),
        "witness_to_write": float(witness_to_write),
        "groove_hits": float(groove_hits),
        "relation_hits": float(relation_hits),
        "phase_hits": float(phase_hits),
        "total_groove": total_groove,
        "max_groove": float(np.max(grooves)),
    }


def score_seq(seq: np.ndarray, diag: dict[str, float]) -> float:
    return v31.score(v31.evaluate(seq, diag))


def plot_summary(rows: list[dict], path: Path) -> None:
    labels = [row["flow"] for row in rows]
    real = [row["real_score"] for row in rows]
    phase_scramble = [row["phase_scramble_gap"] for row in rows]
    path_break = [row["path_break_gap"] for row in rows]
    x = np.arange(len(labels))
    width = 0.25
    plt.figure(figsize=(11, 5))
    plt.bar(x - width, real, width=width, label="real score")
    plt.bar(x, phase_scramble, width=width, label="phase scramble gap")
    plt.bar(x + width, path_break, width=width, label="path-break gap")
    plt.axhline(0.0, color="black", linewidth=1.0)
    plt.xticks(x, labels, rotation=20)
    plt.tight_layout()
    plt.legend()
    plt.savefig(path, dpi=180)
    plt.close()


def main() -> None:
    ensure_dir(OUT)
    specs = find_best_specs()
    rows: list[dict] = []

    for spec in specs:
        hidden = v31.hidden_trace(spec.alpha)
        seq, diag = build_sequence_from_hidden(spec.alpha, spec.condition, hidden)
        real_score = score_seq(seq, diag)

        density = density_surrogate(seq)
        block = block_surrogate(seq)
        density_diag = {
            "witnesses": float(np.sum(density == 0)),
            "writes": float(np.sum(density == 1)),
            "releases": float(np.sum(density == -1)),
            "ruptures": float(np.sum(density == 2)),
            "witness_to_write": 0.0,
            "groove_hits": 0.0,
            "relation_hits": 0.0,
            "phase_hits": 0.0,
            "total_groove": 0.0,
            "max_groove": 0.0,
        }
        block_diag = {
            **density_diag,
            "witnesses": float(np.sum(block == 0)),
            "writes": float(np.sum(block == 1)),
            "releases": float(np.sum(block == -1)),
            "ruptures": float(np.sum(block == 2)),
        }

        phase_hidden = v31.phase_scramble(hidden)
        phase_seq, phase_diag = build_sequence_from_hidden(spec.alpha, spec.condition, phase_hidden)
        shift_hidden = constant_phase_shift(hidden, 0.173)
        shift_seq, shift_diag = build_sequence_from_hidden(spec.alpha, spec.condition, shift_hidden)
        jitter_hidden = local_phase_jitter(hidden)
        jitter_seq, jitter_diag = build_sequence_from_hidden(spec.alpha, spec.condition, jitter_hidden)
        broken_hidden = broken_path_order(hidden)
        broken_seq, broken_diag = build_sequence_from_hidden(spec.alpha, spec.condition, broken_hidden)

        rows.append(
            {
                "flow": spec.flow,
                "family": spec.family,
                "alpha": spec.alpha,
                "best_delay": spec.condition.delay,
                "best_slot_count": spec.condition.slot_count,
                "real_score": real_score,
                "density_gap": real_score - score_seq(density, density_diag),
                "block_gap": real_score - score_seq(block, block_diag),
                "phase_scramble_gap": real_score - score_seq(phase_seq, phase_diag),
                "constant_shift_gap": real_score - score_seq(shift_seq, shift_diag),
                "local_jitter_gap": real_score - score_seq(jitter_seq, jitter_diag),
                "path_break_gap": real_score - score_seq(broken_seq, broken_diag),
            }
        )

    ranked = sorted(rows, key=lambda row: row["real_score"], reverse=True)
    write_csv(rows, OUT / "summary.csv")
    plot_summary(rows, OUT / "summary.png")

    best = ranked[0]
    golden = next(row for row in rows if row["flow"] == "golden")
    report = f"""# Golden Zipper v31b - Phase Null Repair

Toy telemetry only. Not physics evidence. Not proof of GHP.

Best flow by repaired real score: `{best['flow']}` with `{best['real_score']:.3f}`

Golden result:
- real score: `{golden['real_score']:.3f}`
- best delay: `{golden['best_delay']}`
- best slot count: `{golden['best_slot_count']}`
- density gap: `{golden['density_gap']:.3f}`
- block gap: `{golden['block_gap']:.3f}`
- phase scramble gap: `{golden['phase_scramble_gap']:.3f}`
- constant shift gap: `{golden['constant_shift_gap']:.3f}`
- local jitter gap: `{golden['local_jitter_gap']:.3f}`
- path break gap: `{golden['path_break_gap']:.3f}`

Interpretation:
- This panel keeps the v31 path-phase groove object fixed and attacks only the phase claim.
- A strong result would keep the phase scramble and path-break gaps positive while the constant-shift gap stays near zero.
"""
    write_text(OUT / "report.md", report)

    print(f"files created: {OUT}")
    print(f"best flow by repaired real score: {best['flow']} {best['real_score']:.3f}")
    print(f"golden real score: {golden['real_score']:.3f}")
    print(f"golden phase scramble gap: {golden['phase_scramble_gap']:.3f}")
    print(f"golden constant shift gap: {golden['constant_shift_gap']:.3f}")
    print(f"golden local jitter gap: {golden['local_jitter_gap']:.3f}")
    print(f"golden path break gap: {golden['path_break_gap']:.3f}")


if __name__ == "__main__":
    main()
