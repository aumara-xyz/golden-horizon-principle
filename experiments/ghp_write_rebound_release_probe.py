#!/usr/bin/env python3
"""WRR-001 - Write-Rebound-Release Probe.

Paper-lane toy probe for the GHP write-law candidate.

Question:
Do write / witness / release events leave distinct after-effects that make
future boundary state more predictable than memoryless, write-only, or shuffled
receipt controls?

This is inspired by the sonoluminescence "shockwave after flash" analogy, but
does not claim sonoluminescence proves GHP physics.

Toy telemetry only. No physics, consciousness, or observer-selection proof.
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
import statistics
import zlib
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_write_rebound_release_probe_outputs"
TRAIN_SEEDS = [1618, 2718, 3141, 4159, 5772]
TEST_SEEDS = [8111, 10946, 14142, 17320, 22360]
REGIMES = ["stable", "noisy", "drifty", "bursty", "sparse", "dense", "volatile", "smooth"]
DEPTHS = [1, 2, 3, 4, 5, 6, 7]
LABELS = ["release", "witness", "write"]


@dataclass
class Event:
    regime: str
    seed: int
    step: int
    pressure: float
    uncertainty: float
    surprise: float
    action: str
    next_pressure: float
    next_uncertainty: float
    next_surprise: float
    private_latent: float


@dataclass
class MetricRow:
    policy: str
    split: str
    surprise_mae: float
    pressure_mae: float
    action_accuracy: float
    action_macro_f1: float
    rebound_mi_like: float
    leakage: float
    harmful_action_error: float


@dataclass
class ProbeResult:
    probe_id: str
    status: str
    metric: str
    value: str
    safest_read: str


def stable_hash(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def compressed_bits(payload: object) -> int:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return len(zlib.compress(raw, level=9)) * 8


def regime_params(regime: str) -> dict[str, float]:
    return {
        "stable": {"noise": 0.14, "drift": 0.02, "burst": 0.00, "threshold": 0.66},
        "noisy": {"noise": 0.28, "drift": 0.02, "burst": 0.00, "threshold": 0.68},
        "drifty": {"noise": 0.18, "drift": 0.14, "burst": 0.00, "threshold": 0.67},
        "bursty": {"noise": 0.20, "drift": 0.04, "burst": 0.35, "threshold": 0.72},
        "sparse": {"noise": 0.16, "drift": 0.02, "burst": 0.00, "threshold": 0.76},
        "dense": {"noise": 0.16, "drift": 0.02, "burst": 0.00, "threshold": 0.58},
        "volatile": {"noise": 0.34, "drift": 0.10, "burst": 0.25, "threshold": 0.71},
        "smooth": {"noise": 0.10, "drift": 0.06, "burst": 0.00, "threshold": 0.64},
    }[regime]


def f1_for_label(pred: list[str], truth: list[str], label: str) -> float:
    tp = sum(1 for p, t in zip(pred, truth) if p == label and t == label)
    fp = sum(1 for p, t in zip(pred, truth) if p == label and t != label)
    fn = sum(1 for p, t in zip(pred, truth) if p != label and t == label)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return (2 * precision * recall / (precision + recall)) if precision + recall else 0.0


def macro_f1(pred: list[str], truth: list[str]) -> float:
    return statistics.fmean(f1_for_label(pred, truth, label) for label in LABELS)


def harmful_error(pred: list[str], truth: list[str]) -> float:
    return sum(
        1
        for p, t in zip(pred, truth)
        if (p == "write" and t == "release") or (p == "release" and t == "write")
    ) / len(truth)


def action_from_pressure(pressure: float, threshold: float, noise: float) -> str:
    witness_cut = threshold - (0.16 + noise * 0.08)
    if pressure > threshold:
        return "write"
    if pressure > witness_cut:
        return "witness"
    return "release"


def generate(seed: int, regime: str, n: int = 2600) -> list[Event]:
    p = regime_params(regime)
    rng = random.Random(int(stable_hash([seed, regime, "wrr001"]), 16))
    latent = rng.random()
    drift = rng.random()
    pressure_memory = 0.0
    uncertainty = 0.48 + rng.random() * 0.16
    events: list[Event] = []
    previous_action = "release"

    raw_rows: list[dict[str, float]] = []
    pressures: list[float] = []
    actions: list[str] = []
    surprises: list[float] = []
    uncertainties: list[float] = []
    latents: list[float] = []

    for step in range(n + 1):
        burst = p["burst"] if step % 113 in range(0, 11) else 0.0
        external = rng.random()
        drift = 0.985 * drift + 0.015 * rng.random()
        latent = 0.93 * latent + 0.07 * rng.random()
        current = 0.62 * external + p["drift"] * drift + burst + rng.gauss(0.0, p["noise"])
        row = {"external": external, "source": current}
        for depth in DEPTHS:
            preserve = 0.75 - 0.03 * min(depth, 6)
            current = preserve * current + (1 - preserve) * rng.random() + rng.gauss(0.0, p["noise"] * (0.60 + 0.07 * depth))
            row[f"depth_{depth}"] = current

        pressure = (
            0.18 * row["depth_2"]
            + 0.36 * row["depth_3"]
            + 0.32 * row["depth_4"]
            - 0.18 * abs(row["depth_7"] - row["depth_4"])
            + 0.08 * latent
        )
        pressure += 0.18 * pressure_memory
        pressure += rng.gauss(0.0, p["noise"] * 0.28)

        action = action_from_pressure(pressure, p["threshold"], p["noise"])

        # Distinct after-effects. These are the toy "shockwaves."
        if previous_action == "write":
            pressure_memory = 0.25 * pressure_memory - 0.22 + rng.gauss(0.0, 0.025)
            uncertainty = max(0.05, 0.58 * uncertainty + 0.08 + rng.gauss(0.0, 0.018))
        elif previous_action == "witness":
            pressure_memory = 0.62 * pressure_memory + 0.06 + rng.gauss(0.0, 0.018)
            uncertainty = max(0.05, 0.78 * uncertainty - 0.06 + rng.gauss(0.0, 0.014))
        else:
            pressure_memory = 0.72 * pressure_memory - 0.02 + rng.gauss(0.0, 0.020)
            uncertainty = min(1.2, 0.92 * uncertainty + 0.025 + rng.gauss(0.0, 0.016))

        surprise = abs(pressure - p["threshold"]) * uncertainty
        raw_rows.append(row)
        pressures.append(pressure)
        actions.append(action)
        surprises.append(surprise)
        uncertainties.append(uncertainty)
        latents.append(latent)
        previous_action = action

    for step in range(n):
        events.append(
            Event(
                regime=regime,
                seed=seed,
                step=step,
                pressure=pressures[step],
                uncertainty=uncertainties[step],
                surprise=surprises[step],
                action=actions[step],
                next_pressure=pressures[step + 1],
                next_uncertainty=uncertainties[step + 1],
                next_surprise=surprises[step + 1],
                private_latent=latents[step],
            )
        )
    return events


def collect(seeds: list[int]) -> list[Event]:
    events: list[Event] = []
    for regime in REGIMES:
        for seed in seeds:
            events.extend(generate(seed, regime))
    return events


def action_code(action: str) -> float:
    return {"release": -1.0, "witness": 0.25, "write": 1.0}[action]


def feature_row(event: Event, policy: str) -> dict[str, float]:
    row = {
        "bias": 1.0,
        "pressure": event.pressure,
        "uncertainty": event.uncertainty,
        "surprise": event.surprise,
    }
    if policy in {"write_only_rebound", "ternary_rebound", "leaky_rebound"}:
        row["is_write"] = 1.0 if event.action == "write" else 0.0
    if policy in {"ternary_rebound", "leaky_rebound"}:
        row["is_witness"] = 1.0 if event.action == "witness" else 0.0
        row["is_release"] = 1.0 if event.action == "release" else 0.0
        row["action_code"] = action_code(event.action)
    if policy == "leaky_rebound":
        row["private_latent"] = event.private_latent
    return row


def train_linear(rows: list[dict[str, float]], y: list[float]) -> dict[str, float]:
    keys = list(rows[0])
    weights: dict[str, float] = {}
    y_mean = statistics.fmean(y)
    y_var = statistics.pvariance(y) if len(y) > 1 else 1.0
    for key in keys:
        xs = [row[key] for row in rows]
        x_mean = statistics.fmean(xs)
        x_var = statistics.pvariance(xs) if len(xs) > 1 else 1.0
        cov = statistics.fmean((x - x_mean) * (yy - y_mean) for x, yy in zip(xs, y))
        weights[key] = cov / (x_var + 1e-6)
    weights["bias"] = y_mean - sum(weights[key] * statistics.fmean(row[key] for row in rows) for key in keys if key != "bias")
    return weights


def predict(row: dict[str, float], weights: dict[str, float]) -> float:
    return weights.get("bias", 0.0) + sum(value * weights.get(key, 0.0) for key, value in row.items() if key != "bias")


def threshold_actions(events: list[Event], policy: str) -> list[str]:
    if policy == "memoryless":
        return [action_from_pressure(event.pressure, regime_params(event.regime)["threshold"], regime_params(event.regime)["noise"]) for event in events]
    if policy == "write_only_rebound":
        labels = []
        for event in events:
            adjusted = event.pressure - (0.08 if event.action == "write" else 0.0)
            labels.append(action_from_pressure(adjusted, regime_params(event.regime)["threshold"], regime_params(event.regime)["noise"]))
        return labels
    if policy == "ternary_rebound":
        labels = []
        for event in events:
            adjusted = event.pressure
            if event.action == "write":
                adjusted -= 0.10
            elif event.action == "witness":
                adjusted += 0.025
            else:
                adjusted -= 0.015
            labels.append(action_from_pressure(adjusted, regime_params(event.regime)["threshold"], regime_params(event.regime)["noise"]))
        return labels
    if policy == "shuffled_receipt":
        shuffled = [event.action for event in events]
        random.Random(424242).shuffle(shuffled)
        labels = []
        for event, action in zip(events, shuffled):
            adjusted = event.pressure + (0.025 if action == "witness" else -0.05 if action == "write" else 0.0)
            labels.append(action_from_pressure(adjusted, regime_params(event.regime)["threshold"], regime_params(event.regime)["noise"]))
        return labels
    if policy == "leaky_rebound":
        labels = []
        for event in events:
            adjusted = event.pressure + 0.06 * event.private_latent
            labels.append(action_from_pressure(adjusted, regime_params(event.regime)["threshold"], regime_params(event.regime)["noise"]))
        return labels
    raise ValueError(policy)


def rebound_mi_like(events: list[Event]) -> float:
    means = {}
    counts = {}
    overall = statistics.fmean(event.next_surprise for event in events)
    total_var = statistics.pvariance([event.next_surprise for event in events])
    if total_var == 0:
        return 0.0
    for label in LABELS:
        vals = [event.next_surprise for event in events if event.action == label]
        means[label] = statistics.fmean(vals) if vals else overall
        counts[label] = len(vals)
    between = sum(counts[label] * (means[label] - overall) ** 2 for label in LABELS) / len(events)
    return between / total_var


def run_probe() -> tuple[ProbeResult, list[MetricRow]]:
    train_events = collect(TRAIN_SEEDS)
    test_events = collect(TEST_SEEDS)
    policies = ["memoryless", "write_only_rebound", "ternary_rebound", "shuffled_receipt", "leaky_rebound"]
    rows: list[MetricRow] = []
    for policy in policies:
        train_rows = [feature_row(event, policy) for event in train_events]
        train_surprise = [event.next_surprise for event in train_events]
        train_pressure = [event.next_pressure for event in train_events]
        surprise_weights = train_linear(train_rows, train_surprise)
        pressure_weights = train_linear(train_rows, train_pressure)
        for split, events in [("train", train_events), ("test", test_events)]:
            data_rows = [feature_row(event, policy) for event in events]
            surprise_pred = [predict(row, surprise_weights) for row in data_rows]
            pressure_pred = [predict(row, pressure_weights) for row in data_rows]
            surprise_truth = [event.next_surprise for event in events]
            pressure_truth = [event.next_pressure for event in events]
            surprise_mae = statistics.fmean(abs(a - b) for a, b in zip(surprise_pred, surprise_truth))
            pressure_mae = statistics.fmean(abs(a - b) for a, b in zip(pressure_pred, pressure_truth))
            action_truth = [event.action for event in events]
            action_pred = threshold_actions(events, policy)
            action_accuracy = sum(int(a == b) for a, b in zip(action_pred, action_truth)) / len(events)
            action_macro = macro_f1(action_pred, action_truth)
            rows.append(
                MetricRow(
                    policy=policy,
                    split=split,
                    surprise_mae=surprise_mae,
                    pressure_mae=pressure_mae,
                    action_accuracy=action_accuracy,
                    action_macro_f1=action_macro,
                    rebound_mi_like=rebound_mi_like(events),
                    leakage=1.0 if policy == "leaky_rebound" else 0.0,
                    harmful_action_error=harmful_error(action_pred, action_truth),
                )
            )
    test = {row.policy: row for row in rows if row.split == "test"}
    ternary = test["ternary_rebound"]
    memoryless = test["memoryless"]
    write_only = test["write_only_rebound"]
    shuffled = test["shuffled_receipt"]
    leaky = test["leaky_rebound"]
    surprise_gain = memoryless.surprise_mae - ternary.surprise_mae
    write_only_gain = write_only.surprise_mae - ternary.surprise_mae
    shuffled_gain = shuffled.surprise_mae - ternary.surprise_mae
    leaky_gain = ternary.surprise_mae - leaky.surprise_mae
    status = (
        "pass"
        if surprise_gain >= 0.004
        and write_only_gain >= 0.001
        and shuffled_gain >= 0.003
        and leaky_gain <= 0.0015
        and ternary.harmful_action_error <= 0.01
        and ternary.action_macro_f1 >= 0.72
        else "fail"
    )
    result = ProbeResult(
        probe_id="WRR-001",
        status=status,
        metric="surprise_gain_vs_memoryless / vs_write_only / vs_shuffled / leaky_gain / action_macro_f1 / harmful_error",
        value=(
            f"{surprise_gain:.4f} / {write_only_gain:.4f} / {shuffled_gain:.4f} / "
            f"{leaky_gain:.4f} / {ternary.action_macro_f1:.4f} / {ternary.harmful_action_error:.4f}"
        ),
        safest_read="If this passes, write/witness/release events are not isolated labels: their rebound effects help predict future boundary surprise better than memoryless or write-only controls.",
    )
    return result, rows


def write_outputs(result: ProbeResult, rows: list[MetricRow]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(MetricRow.__annotations__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)
    report = [
        "# WRR-001 Write-Rebound-Release Probe",
        "",
        "Toy telemetry only. This tests whether ternary boundary actions leave distinct after-effects that improve future-state prediction.",
        "",
        "| Probe | Status | Metric | Value | Safest Read |",
        "| --- | --- | --- | --- | --- |",
        f"| {result.probe_id} | {result.status.upper()} | {result.metric} | `{result.value}` | {result.safest_read} |",
        "",
        "## Metrics",
        "",
        "| Policy | Split | Surprise MAE | Pressure MAE | Action Accuracy | Action Macro F1 | Rebound MI-like | Leakage | Harmful Error |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        report.append(
            f"| {row.policy} | {row.split} | {row.surprise_mae:.4f} | {row.pressure_mae:.4f} | {row.action_accuracy:.4f} | {row.action_macro_f1:.4f} | {row.rebound_mi_like:.4f} | {row.leakage:.4f} | {row.harmful_action_error:.4f} |"
        )
    report.extend(
        [
            "",
            "## Paper-Safe Read",
            "",
            "If promoted, the safe claim is that toy receipt events have after-effects: ternary write/witness/release state can improve prediction of future boundary surprise compared with memoryless or write-only controls.",
            "",
            "Do not claim sonoluminescence proves GHP, AI experience, physical time, or consciousness.",
        ]
    )
    (OUT / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> None:
    result, rows = run_probe()
    write_outputs(result, rows)
    print(f"{result.probe_id}: {result.status} :: {result.value}")


if __name__ == "__main__":
    main()
