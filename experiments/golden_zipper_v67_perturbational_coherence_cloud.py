#!/usr/bin/env python3
"""v67 perturbational coherence cloud.

PCI-style toy:
poke a memory structure and score whether the echo is
spread, differentiated, integrated, and stable.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import golden_zipper_v41_prediction_band_binding as v41


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v67_outputs"
V41_SUMMARY = ROOT / "golden_zipper_v41_outputs" / "summary.csv"

SEED = 20260526
RNG = np.random.default_rng(SEED)
MODES = ("point_slot", "flat_local_cloud", "global_smooth_cloud", "coherence_weighted_cloud", "context_gated_cloud")
STEPS = 128
START = 16
DECAY = 0.72
COUPLING = 0.34
ACTIVITY_THRESHOLD = 0.04


@dataclass(frozen=True)
class BestCondition:
    flow: str
    family: str
    alpha: float
    slot_count: int
    delay: int
    window_width: float
    field_radius: int
    field_width: float
    admission_center: float
    admission_width: float


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


def load_best_conditions() -> list[BestCondition]:
    specs = {spec.flow: spec for spec in v41.v31b.find_best_specs()}
    rows = list(csv.DictReader(V41_SUMMARY.open()))
    selected: list[BestCondition] = []
    for row in rows:
        spec = specs[row["flow"]]
        selected.append(
            BestCondition(
                flow=spec.flow,
                family=spec.family,
                alpha=spec.alpha,
                slot_count=spec.condition.slot_count,
                delay=spec.condition.delay,
                window_width=spec.condition.window_width,
                field_radius=int(float(row["best_field_radius"])),
                field_width=float(row["best_field_width"]),
                admission_center=float(row["best_admission_center"]),
                admission_width=float(row["best_admission_width"]),
            )
        )
    return selected


def local_dist(a: int, b: int, slot_count: int) -> int:
    return min((a - b) % slot_count, (b - a) % slot_count)


def build_weights(center: int, slot_count: int, radius: int, width: float, mode: str) -> np.ndarray:
    if mode == "point_slot":
        weights = np.zeros(slot_count, dtype=float)
        weights[center] = 1.0
        return weights
    if mode == "global_smooth_cloud":
        return np.full(slot_count, 1.0 / slot_count, dtype=float)

    weights = np.zeros(slot_count, dtype=float)
    for idx in range(slot_count):
        d = local_dist(idx, center, slot_count)
        if mode == "flat_local_cloud":
            if d <= radius:
                weights[idx] = 1.0
        else:
            if d <= radius:
                weights[idx] = np.exp(-0.5 * (d / max(width, 1e-6)) ** 2)
    total = weights.sum()
    if total > 0:
        weights /= total
    return weights


def hidden_drive(condition: BestCondition) -> tuple[np.ndarray, np.ndarray]:
    hidden = v41.v31b.v31.hidden_trace(condition.alpha)
    slots = np.zeros(STEPS, dtype=int)
    contacts = np.zeros(STEPS, dtype=float)
    for step in range(STEPS):
        idx = START + step + condition.delay + 2
        delayed = hidden[idx - condition.delay]
        previous = hidden[idx - condition.delay - 1]
        contact = v41.v31b.v31.contact_likelihood(delayed, condition.window_width)
        slot, _phase = v41.v31b.v31.route_slot(
            delayed,
            previous,
            idx,
            condition.alpha,
            type("Tmp", (), {"slot_count": condition.slot_count, "delay": condition.delay, "window_width": condition.window_width})(),
        )
        slots[step] = slot
        contacts[step] = contact
    return slots, contacts


def simulate_echo(condition: BestCondition, mode: str) -> dict[str, float]:
    slots, contacts = hidden_drive(condition)
    state = np.zeros(condition.slot_count, dtype=float)
    response = []
    propagated = []
    pulse_energy = []
    prev_state = np.zeros(condition.slot_count, dtype=float)

    for step in range(STEPS):
        center = int(slots[step])
        pulse = max(float(contacts[step]), 0.04)
        weights = build_weights(center, condition.slot_count, condition.field_radius, condition.field_width, mode if mode != "context_gated_cloud" else "coherence_weighted_cloud")
        predicted = float(np.dot(prev_state, weights))
        gate = 1.0
        if mode == "context_gated_cloud":
            error = abs(pulse - predicted)
            gate = float(np.exp(-0.5 * ((error - condition.admission_center) / max(condition.admission_width, 1e-9)) ** 2))

        impulse = np.zeros(condition.slot_count, dtype=float)
        impulse[center] = pulse
        next_state = DECAY * state + impulse + gate * COUPLING * (weights * state.sum() + weights * pulse)
        next_state = np.clip(next_state, 0.0, 2.0)

        response.append(next_state.copy())
        propagated.append(float((gate * COUPLING * (weights * state.sum() + weights * pulse)).sum()))
        pulse_energy.append(pulse)
        prev_state = state.copy()
        state = next_state

    resp = np.array(response)
    total = resp.sum(axis=1)
    mean_slot = resp.mean(axis=1)
    std_slot = resp.std(axis=1)
    active_frac = (resp > ACTIVITY_THRESHOLD).mean(axis=1)

    spread = float(active_frac.mean())
    spread_score = float(np.exp(-0.5 * ((spread - 0.38) / 0.18) ** 2))
    differentiation = float(np.mean(std_slot / np.maximum(mean_slot, 1e-6)))
    differentiation_score = float(np.tanh(differentiation / 1.5))
    integration = float(np.mean(np.array(propagated) / np.maximum(np.array(pulse_energy), 1e-6)))
    integration_score = float(np.tanh(integration / 0.35))
    tail = total[-16:]
    recovery_score = float(np.exp(-tail.std() / 0.08) * np.exp(-abs(tail.mean() - 0.22) / 0.22))
    uniformity_penalty = float(np.clip(active_frac.mean() * max(0.0, 0.18 - differentiation_score) / 0.18, 0.0, 1.0))
    locality_penalty = float(np.clip((0.14 - spread) / 0.14, 0.0, 1.0))
    overload_penalty = float(np.clip((resp.max() - 1.1) / 0.9, 0.0, 1.0))

    score = float(
        0.28 * spread_score
        + 0.26 * differentiation_score
        + 0.24 * integration_score
        + 0.22 * recovery_score
        - 0.10 * uniformity_penalty
        - 0.10 * locality_penalty
        - 0.06 * overload_penalty
    )
    return {
        "spread_rate": spread,
        "differentiation_score": differentiation_score,
        "integration_score": integration_score,
        "recovery_score": recovery_score,
        "uniformity_penalty": uniformity_penalty,
        "locality_penalty": locality_penalty,
        "overload_penalty": overload_penalty,
        "score": score,
    }


def main() -> None:
    ensure_dir(OUT)
    conditions = load_best_conditions()
    rows: list[dict] = []
    for condition in conditions:
        for mode in MODES:
            metrics = simulate_echo(condition, mode)
            rows.append({"flow": condition.flow, "family": condition.family, "mode": mode, **metrics})

    write_csv(rows, OUT / "mode_metrics.csv")

    summary_rows: list[dict] = []
    for flow in sorted({row["flow"] for row in rows}):
        subset = [row for row in rows if row["flow"] == flow]
        real = next(row for row in subset if row["mode"] == "coherence_weighted_cloud")
        best = max(subset, key=lambda row: row["score"])
        summary_rows.append(
            {
                "flow": flow,
                "best_mode": best["mode"],
                "real_score": real["score"],
                "spread_rate": real["spread_rate"],
                "differentiation_score": real["differentiation_score"],
                "integration_score": real["integration_score"],
                "recovery_score": real["recovery_score"],
                "real_vs_point_gap": real["score"] - next(row for row in subset if row["mode"] == "point_slot")["score"],
                "real_vs_flat_gap": real["score"] - next(row for row in subset if row["mode"] == "flat_local_cloud")["score"],
                "real_vs_global_gap": real["score"] - next(row for row in subset if row["mode"] == "global_smooth_cloud")["score"],
                "real_vs_gated_gap": real["score"] - next(row for row in subset if row["mode"] == "context_gated_cloud")["score"],
            }
        )

    write_csv(summary_rows, OUT / "summary.csv")
    golden = next(row for row in summary_rows if row["flow"] == "golden")
    report = f"""# Golden Zipper v67 - Perturbational Coherence Cloud

Golden result:
- best mode: `{golden['best_mode']}`
- coherence-cloud score: `{golden['real_score']:.3f}`
- spread rate: `{golden['spread_rate']:.3f}`
- differentiation score: `{golden['differentiation_score']:.3f}`
- integration score: `{golden['integration_score']:.3f}`
- recovery score: `{golden['recovery_score']:.3f}`
- real vs point gap: `{golden['real_vs_point_gap']:.3f}`
- real vs flat gap: `{golden['real_vs_flat_gap']:.3f}`
- real vs global gap: `{golden['real_vs_global_gap']:.3f}`
- real vs gated gap: `{golden['real_vs_gated_gap']:.3f}`
"""
    write_text(OUT / "report.md", report)
    print(f"files created: {OUT}")
    print(f"golden best mode: {golden['best_mode']}")
    print(f"golden coherence-cloud score: {golden['real_score']:.3f}")
    print(f"golden real vs point gap: {golden['real_vs_point_gap']:.3f}")
    print(f"golden real vs flat gap: {golden['real_vs_flat_gap']:.3f}")
    print(f"golden real vs global gap: {golden['real_vs_global_gap']:.3f}")


if __name__ == "__main__":
    main()
