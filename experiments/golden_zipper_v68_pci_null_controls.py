#!/usr/bin/env python3
"""v68 PCI-style null controls."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

import golden_zipper_v67_perturbational_coherence_cloud as v67


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "golden_zipper_v68_outputs"
SEED = 20260526
RNG = np.random.default_rng(SEED)
MODES = ("real", "shuffled_connections", "random_weights", "local_only", "uniform_global", "overconnected")


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


def simulate_null(condition: v67.BestCondition, mode: str) -> dict[str, float]:
    slots, contacts = v67.hidden_drive(condition)
    state = np.zeros(condition.slot_count, dtype=float)
    response = []
    propagated = []
    pulse_energy = []
    perm = RNG.permutation(condition.slot_count)

    for step in range(v67.STEPS):
        center = int(slots[step])
        pulse = max(float(contacts[step]), 0.04)
        weights = v67.build_weights(center, condition.slot_count, condition.field_radius, condition.field_width, "coherence_weighted_cloud")
        if mode == "shuffled_connections":
            weights = weights[perm]
        elif mode == "random_weights":
            weights = RNG.random(condition.slot_count)
            weights /= weights.sum()
        elif mode == "local_only":
            weights = v67.build_weights(center, condition.slot_count, condition.field_radius, condition.field_width, "point_slot")
        elif mode == "uniform_global":
            weights = v67.build_weights(center, condition.slot_count, condition.field_radius, condition.field_width, "global_smooth_cloud")
        elif mode == "overconnected":
            weights = v67.build_weights(center, condition.slot_count, condition.field_radius + 2, condition.field_width * 2.0, "flat_local_cloud")

        impulse = np.zeros(condition.slot_count, dtype=float)
        impulse[center] = pulse
        next_state = v67.DECAY * state + impulse + v67.COUPLING * (weights * state.sum() + weights * pulse)
        next_state = np.clip(next_state, 0.0, 2.0)
        response.append(next_state.copy())
        propagated.append(float((v67.COUPLING * (weights * state.sum() + weights * pulse)).sum()))
        pulse_energy.append(pulse)
        state = next_state

    resp = np.array(response)
    total = resp.sum(axis=1)
    mean_slot = resp.mean(axis=1)
    std_slot = resp.std(axis=1)
    active_frac = (resp > v67.ACTIVITY_THRESHOLD).mean(axis=1)
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
    return {"score": score, "spread_rate": spread, "differentiation_score": differentiation_score, "integration_score": integration_score, "recovery_score": recovery_score}


def main() -> None:
    ensure_dir(OUT)
    rows: list[dict] = []
    for condition in v67.load_best_conditions():
        for mode in MODES:
            metrics = v67.simulate_echo(condition, "coherence_weighted_cloud") if mode == "real" else simulate_null(condition, mode)
            rows.append({"flow": condition.flow, "family": condition.family, "mode": mode, **metrics})

    write_csv(rows, OUT / "mode_metrics.csv")
    summary_rows: list[dict] = []
    for flow in sorted({row["flow"] for row in rows}):
        subset = [row for row in rows if row["flow"] == flow]
        real = next(row for row in subset if row["mode"] == "real")
        summary_rows.append(
            {
                "flow": flow,
                "real_score": real["score"],
                "real_vs_shuffled_gap": real["score"] - next(row for row in subset if row["mode"] == "shuffled_connections")["score"],
                "real_vs_random_gap": real["score"] - next(row for row in subset if row["mode"] == "random_weights")["score"],
                "real_vs_local_gap": real["score"] - next(row for row in subset if row["mode"] == "local_only")["score"],
                "real_vs_uniform_gap": real["score"] - next(row for row in subset if row["mode"] == "uniform_global")["score"],
                "real_vs_overconnected_gap": real["score"] - next(row for row in subset if row["mode"] == "overconnected")["score"],
            }
        )
    write_csv(summary_rows, OUT / "summary.csv")
    golden = next(row for row in summary_rows if row["flow"] == "golden")
    report = f"""# Golden Zipper v68 - PCI Null Controls

Golden result:
- real score: `{golden['real_score']:.3f}`
- real vs shuffled gap: `{golden['real_vs_shuffled_gap']:.3f}`
- real vs random gap: `{golden['real_vs_random_gap']:.3f}`
- real vs local gap: `{golden['real_vs_local_gap']:.3f}`
- real vs uniform gap: `{golden['real_vs_uniform_gap']:.3f}`
- real vs overconnected gap: `{golden['real_vs_overconnected_gap']:.3f}`
"""
    write_text(OUT / "report.md", report)
    print(f"files created: {OUT}")
    print(f"golden real score: {golden['real_score']:.3f}")
    print(f"golden real vs shuffled gap: {golden['real_vs_shuffled_gap']:.3f}")
    print(f"golden real vs uniform gap: {golden['real_vs_uniform_gap']:.3f}")


if __name__ == "__main__":
    main()
