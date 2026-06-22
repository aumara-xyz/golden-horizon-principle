#!/usr/bin/env python3
"""WRR-002 - Write-Rebound Residual Probe.

Paper-lane toy probe for the GHP write-law candidate.

Question:
After the observer-visible boundary state is already known, does the actual
receipt action (write / witness / release) explain the next-step residual wake?

This is the de-circularized follow-up to WRR-001. It avoids asking whether the
receipt can predict the whole next state when current pressure already dominates
the answer. Instead it asks whether receipts add predictive value for the
change left behind by the boundary event.

Toy telemetry only. No physics, consciousness, time, or identity proof.
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
import zlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_write_rebound_residual_probe_outputs"
TRAIN_SEEDS = [1618, 2718, 3141, 4159, 5772, 8111]
TEST_SEEDS = [10946, 14142, 17320, 22360, 27182]
REGIMES = ["stable", "noisy", "drifty", "bursty", "sparse", "dense", "volatile", "smooth"]
ACTIONS = ["release", "witness", "write"]


@dataclass(frozen=True)
class Event:
    regime: str
    seed: int
    step: int
    pressure: float
    uncertainty: float
    surprise: float
    distance: float
    action: str
    next_pressure: float
    next_uncertainty: float
    next_surprise: float
    hidden_friction: float


@dataclass(frozen=True)
class Row:
    policy: str
    split: str
    target: str
    mae: float
    gain_vs_projection: float
    gain_vs_shuffled: float
    leaky_gain: float
    compressed_feature_bits: int
    leakage: float


def stable_hash(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def compressed_bits(payload: object) -> int:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return len(zlib.compress(raw, level=9)) * 8


def params(regime: str) -> dict[str, float]:
    return {
        "stable": {"noise": 0.10, "drift": 0.02, "burst": 0.00, "threshold": 0.66},
        "noisy": {"noise": 0.22, "drift": 0.03, "burst": 0.00, "threshold": 0.68},
        "drifty": {"noise": 0.13, "drift": 0.12, "burst": 0.00, "threshold": 0.67},
        "bursty": {"noise": 0.15, "drift": 0.04, "burst": 0.32, "threshold": 0.72},
        "sparse": {"noise": 0.12, "drift": 0.02, "burst": 0.00, "threshold": 0.76},
        "dense": {"noise": 0.12, "drift": 0.02, "burst": 0.00, "threshold": 0.58},
        "volatile": {"noise": 0.25, "drift": 0.10, "burst": 0.28, "threshold": 0.71},
        "smooth": {"noise": 0.07, "drift": 0.06, "burst": 0.00, "threshold": 0.64},
    }[regime]


def base_action(pressure: float, threshold: float, noise: float) -> str:
    witness_cut = threshold - (0.16 + noise * 0.08)
    if pressure >= threshold:
        return "write"
    if pressure >= witness_cut:
        return "witness"
    return "release"


def generate(seed: int, regime: str, n: int = 3200) -> list[Event]:
    p = params(regime)
    rng = random.Random(int(stable_hash(["wrr002", seed, regime]), 16))
    latent = rng.random()
    drift = rng.random()
    uncertainty = 0.46 + rng.random() * 0.18
    pressure_memory = 0.0
    last_action = "release"
    events: list[Event] = []

    pressure = 0.0
    action = "release"
    surprise = 0.0
    distance = 0.0
    friction = 0.0

    for step in range(n + 1):
        old_pressure = pressure
        old_uncertainty = uncertainty
        old_surprise = surprise
        old_action = action
        old_distance = distance
        old_friction = friction

        burst = p["burst"] if step % 127 in range(0, 9) else 0.0
        drift = 0.985 * drift + 0.015 * rng.random()
        latent = 0.90 * latent + 0.10 * rng.random()

        signal = 0.48 * rng.random() + p["drift"] * drift + burst
        depth2 = 0.72 * signal + 0.28 * rng.random() + rng.gauss(0.0, p["noise"] * 0.55)
        depth3 = 0.70 * depth2 + 0.30 * rng.random() + rng.gauss(0.0, p["noise"] * 0.62)
        depth4 = 0.68 * depth3 + 0.32 * rng.random() + rng.gauss(0.0, p["noise"] * 0.70)
        depth6 = 0.64 * depth4 + 0.36 * rng.random() + rng.gauss(0.0, p["noise"] * 0.86)

        pressure = 0.20 * depth2 + 0.38 * depth3 + 0.34 * depth4 - 0.12 * abs(depth6 - depth4)
        pressure += 0.18 * pressure_memory + rng.gauss(0.0, p["noise"] * 0.18)
        distance = pressure - p["threshold"]

        deterministic = base_action(pressure, p["threshold"], p["noise"])
        near_boundary = abs(distance) < (0.09 + p["noise"] * 0.08)
        if near_boundary and rng.random() < 0.28:
            # The actual receipt is not fully recoverable from instantaneous
            # projection alone. This mimics a legal boundary event whose effect
            # is visible only after the receipt exists.
            action = rng.choice(ACTIONS)
        else:
            action = deterministic

        if last_action == "write":
            pressure_memory = 0.34 * pressure_memory - 0.18 + rng.gauss(0.0, 0.020)
            uncertainty = max(0.04, 0.62 * uncertainty + 0.075 + rng.gauss(0.0, 0.014))
            friction = 0.42 + 0.25 * rng.random()
        elif last_action == "witness":
            pressure_memory = 0.68 * pressure_memory + 0.04 + rng.gauss(0.0, 0.014)
            uncertainty = max(0.04, 0.80 * uncertainty - 0.045 + rng.gauss(0.0, 0.011))
            friction = 0.20 + 0.16 * rng.random()
        else:
            pressure_memory = 0.76 * pressure_memory - 0.015 + rng.gauss(0.0, 0.016)
            uncertainty = min(1.1, 0.93 * uncertainty + 0.018 + rng.gauss(0.0, 0.012))
            friction = 0.10 + 0.12 * rng.random()

        surprise = abs(distance) * uncertainty
        last_action = action

        if step > 0:
            events.append(
                Event(
                    regime=regime,
                    seed=seed,
                    step=step - 1,
                    pressure=old_pressure,
                    uncertainty=old_uncertainty,
                    surprise=old_surprise,
                    distance=old_distance,
                    action=old_action,
                    next_pressure=pressure,
                    next_uncertainty=uncertainty,
                    next_surprise=surprise,
                    hidden_friction=old_friction,
                )
            )
    return events


def collect(seeds: list[int]) -> list[Event]:
    events: list[Event] = []
    for regime in REGIMES:
        for seed in seeds:
            events.extend(generate(seed, regime))
    return events


def feature_matrix(events: list[Event], policy: str, shuffled_actions: list[str] | None = None) -> tuple[np.ndarray, list[str]]:
    rows: list[list[float]] = []
    names = ["bias", "pressure", "uncertainty", "surprise", "distance_abs"]
    if policy in {"receipt", "shuffled", "leaky"}:
        names += ["is_release", "is_witness", "is_write"]
    if policy == "leaky":
        names += ["hidden_friction"]

    for index, event in enumerate(events):
        row = [1.0, event.pressure, event.uncertainty, event.surprise, abs(event.distance)]
        if policy in {"receipt", "shuffled", "leaky"}:
            action = shuffled_actions[index] if policy == "shuffled" and shuffled_actions else event.action
            row += [1.0 if action == label else 0.0 for label in ACTIONS]
        if policy == "leaky":
            row += [event.hidden_friction]
        rows.append(row)
    return np.asarray(rows, dtype=float), names


def target(events: list[Event], name: str) -> np.ndarray:
    if name == "delta_surprise":
        return np.asarray([event.next_surprise - event.surprise for event in events], dtype=float)
    if name == "delta_pressure":
        return np.asarray([event.next_pressure - event.pressure for event in events], dtype=float)
    if name == "delta_uncertainty":
        return np.asarray([event.next_uncertainty - event.uncertainty for event in events], dtype=float)
    raise ValueError(name)


def ridge_fit(x: np.ndarray, y: np.ndarray, lam: float = 0.002) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    means = x.mean(axis=0)
    stds = x.std(axis=0)
    means[0] = 0.0
    stds[0] = 1.0
    stds[stds < 1e-9] = 1.0
    scaled = (x - means) / stds
    penalty = np.eye(scaled.shape[1]) * lam
    penalty[0, 0] = 0.0
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        weights = np.linalg.solve(scaled.T @ scaled + penalty, scaled.T @ y)
    if not np.isfinite(weights).all():
        raise FloatingPointError("non-finite ridge weights")
    return weights, means, stds


def ridge_predict(x: np.ndarray, model: tuple[np.ndarray, np.ndarray, np.ndarray]) -> np.ndarray:
    weights, means, stds = model
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        pred = ((x - means) / stds) @ weights
    if not np.isfinite(pred).all():
        raise FloatingPointError("non-finite ridge prediction")
    return pred


def mae(pred: np.ndarray, y: np.ndarray) -> float:
    return float(np.mean(np.abs(pred - y)))


def evaluate(train: list[Event], test: list[Event]) -> list[Row]:
    rng = random.Random(424242)
    shuffled_train = [event.action for event in train]
    shuffled_test = [event.action for event in test]
    rng.shuffle(shuffled_train)
    rng.shuffle(shuffled_test)
    rows: list[Row] = []

    for target_name in ["delta_surprise", "delta_pressure", "delta_uncertainty"]:
        y_train = target(train, target_name)
        y_test = target(test, target_name)
        projection_mae = 0.0
        shuffled_mae = 0.0
        leaky_mae = 0.0

        policy_outputs: dict[str, tuple[float, int, float]] = {}
        for policy in ["projection", "receipt", "shuffled", "leaky"]:
            x_train, names = feature_matrix(train, policy, shuffled_train)
            x_test, _ = feature_matrix(test, policy, shuffled_test)
            model = ridge_fit(x_train, y_train)
            score = mae(ridge_predict(x_test, model), y_test)
            leakage = 1.0 if policy == "leaky" else 0.0
            feature_bits = compressed_bits(names)
            policy_outputs[policy] = (score, feature_bits, leakage)
            if policy == "projection":
                projection_mae = score
            elif policy == "shuffled":
                shuffled_mae = score
            elif policy == "leaky":
                leaky_mae = score

        for policy, (score, feature_bits, leakage) in policy_outputs.items():
            rows.append(
                Row(
                    policy=policy,
                    split="test",
                    target=target_name,
                    mae=score,
                    gain_vs_projection=projection_mae - score,
                    gain_vs_shuffled=shuffled_mae - score,
                    leaky_gain=policy_outputs["receipt"][0] - leaky_mae,
                    compressed_feature_bits=feature_bits,
                    leakage=leakage,
                )
            )
    return rows


def status(rows: list[Row]) -> tuple[str, str]:
    receipt = [row for row in rows if row.policy == "receipt"]
    min_projection_gain = min(row.gain_vs_projection for row in receipt)
    min_shuffled_gain = min(row.gain_vs_shuffled for row in receipt)
    max_leaky_gain = max(abs(row.leaky_gain) for row in receipt)
    passed = (
        min_projection_gain >= 0.002
        and min_shuffled_gain >= 0.002
        and max_leaky_gain <= 0.0015
        and all(row.leakage == 0.0 for row in receipt)
    )
    metric = "min_gain_vs_projection / min_gain_vs_shuffled / max_leaky_gain"
    value = f"{min_projection_gain:.4f} / {min_shuffled_gain:.4f} / {max_leaky_gain:.4f}"
    return ("PASS" if passed else "FAIL", f"{metric} = {value}")


def write_outputs(rows: list[Row], probe_status: str, metric_value: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "policy",
                "split",
                "target",
                "mae",
                "gain_vs_projection",
                "gain_vs_shuffled",
                "leaky_gain",
                "compressed_feature_bits",
                "leakage",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.policy,
                    row.split,
                    row.target,
                    row.mae,
                    row.gain_vs_projection,
                    row.gain_vs_shuffled,
                    row.leaky_gain,
                    row.compressed_feature_bits,
                    row.leakage,
                ]
            )

    report = [
        "# WRR-002 Write-Rebound Residual Probe",
        "",
        "Toy telemetry only. This asks whether actual receipt actions explain next-step residual wake after current visible state is already known.",
        "",
        f"Status: **{probe_status}**",
        "",
        f"Primary metric: `{metric_value}`",
        "",
        "## Metrics",
        "",
        "| Policy | Target | MAE | Gain vs Projection | Gain vs Shuffled | Leaky Gain | Feature Bits | Leakage |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        report.append(
            f"| {row.policy} | {row.target} | {row.mae:.4f} | {row.gain_vs_projection:.4f} | "
            f"{row.gain_vs_shuffled:.4f} | {row.leaky_gain:.4f} | {row.compressed_feature_bits} | {row.leakage:.1f} |"
        )
    report += [
        "",
        "## Safe Read",
        "",
        "If this passes, the boundary receipt is not just a label. It carries post-event information about how the public state will relax, rebound, or release.",
        "",
        "Do not claim this proves sonoluminescence, GHP physics, time extrusion, consciousness, or identity.",
    ]
    (OUT / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> None:
    train = collect(TRAIN_SEEDS)
    test = collect(TEST_SEEDS)
    rows = evaluate(train, test)
    probe_status, metric_value = status(rows)
    write_outputs(rows, probe_status, metric_value)
    print(f"WRR-002: {probe_status.lower()} :: {metric_value}")


if __name__ == "__main__":
    main()
