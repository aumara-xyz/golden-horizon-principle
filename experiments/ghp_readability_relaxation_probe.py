#!/usr/bin/env python3
"""RRL-001 - Readability Relaxation Law Probe.

Paper-lane toy probe for the narrowed write-law candidate.

Question:
Does a receipt action first change public readability / uncertainty, and does
that change predict later surprise relaxation?

This is the follow-up to WRR-001/002. The tested law is narrower:

    legal receipt -> public readability shift -> lagged surprise relaxation

Toy telemetry only. No physics, consciousness, time, identity, or observer-
selection proof.
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
OUT = ROOT / "ghp_readability_relaxation_probe_outputs"
TRAIN_SEEDS = [1618, 2718, 3141, 4159, 5772, 8111]
TEST_SEEDS = [10946, 14142, 17320, 22360, 27182]
REGIMES = ["stable", "noisy", "drifty", "bursty", "sparse", "dense", "volatile", "smooth"]
ACTIONS = ["release", "witness", "write"]


@dataclass(frozen=True)
class Event:
    regime: str
    pressure: float
    uncertainty: float
    surprise: float
    distance: float
    action: str
    next_uncertainty: float
    lag2_surprise: float
    lag2_uncertainty: float
    private_friction: float


@dataclass(frozen=True)
class Metric:
    policy: str
    target: str
    mae: float
    gain_vs_projection: float
    gain_vs_shuffled: float
    leaky_gain: float
    feature_bits: int
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


def generate(seed: int, regime: str, n: int = 3600) -> list[Event]:
    p = params(regime)
    rng = random.Random(int(stable_hash(["rrl001", seed, regime]), 16))
    latent = rng.random()
    drift = rng.random()
    uncertainty = 0.50 + rng.random() * 0.16
    readability_momentum = 0.0
    last_action = "release"
    raw: list[dict[str, float | str]] = []

    for step in range(n + 2):
        burst = p["burst"] if step % 127 in range(0, 9) else 0.0
        drift = 0.985 * drift + 0.015 * rng.random()
        latent = 0.91 * latent + 0.09 * rng.random()
        carrier = 0.52 * rng.random() + p["drift"] * drift + burst
        depth2 = 0.74 * carrier + 0.26 * rng.random() + rng.gauss(0.0, p["noise"] * 0.55)
        depth3 = 0.70 * depth2 + 0.30 * rng.random() + rng.gauss(0.0, p["noise"] * 0.62)
        depth4 = 0.67 * depth3 + 0.33 * rng.random() + rng.gauss(0.0, p["noise"] * 0.70)
        pressure = 0.20 * depth2 + 0.38 * depth3 + 0.34 * depth4 + 0.07 * latent
        pressure += rng.gauss(0.0, p["noise"] * 0.18)
        distance = pressure - p["threshold"]

        deterministic = base_action(pressure, p["threshold"], p["noise"])
        near_boundary = abs(distance) < (0.10 + p["noise"] * 0.08)
        if near_boundary and rng.random() < 0.30:
            action = rng.choice(ACTIONS)
        else:
            action = deterministic

        # Readability, not raw pressure, is the first affected public state.
        if last_action == "write":
            readability_momentum = 0.52 * readability_momentum - 0.13 + rng.gauss(0.0, 0.010)
            private_friction = 0.42 + 0.18 * rng.random()
        elif last_action == "witness":
            readability_momentum = 0.68 * readability_momentum - 0.07 + rng.gauss(0.0, 0.008)
            private_friction = 0.24 + 0.12 * rng.random()
        else:
            readability_momentum = 0.78 * readability_momentum + 0.035 + rng.gauss(0.0, 0.010)
            private_friction = 0.10 + 0.08 * rng.random()

        uncertainty = min(1.2, max(0.04, 0.84 * uncertainty + 0.16 * (0.55 + readability_momentum)))
        surprise = abs(distance) * uncertainty
        raw.append(
            {
                "pressure": pressure,
                "uncertainty": uncertainty,
                "surprise": surprise,
                "distance": distance,
                "action": action,
                "private_friction": private_friction,
            }
        )
        last_action = action

    events: list[Event] = []
    for index in range(n):
        row = raw[index]
        nxt = raw[index + 1]
        lag2 = raw[index + 2]
        events.append(
            Event(
                regime=regime,
                pressure=float(row["pressure"]),
                uncertainty=float(row["uncertainty"]),
                surprise=float(row["surprise"]),
                distance=float(row["distance"]),
                action=str(row["action"]),
                next_uncertainty=float(nxt["uncertainty"]),
                lag2_surprise=float(lag2["surprise"]),
                lag2_uncertainty=float(lag2["uncertainty"]),
                private_friction=float(row["private_friction"]),
            )
        )
    return events


def collect(seeds: list[int]) -> list[Event]:
    events: list[Event] = []
    for regime in REGIMES:
        for seed in seeds:
            events.extend(generate(seed, regime))
    return events


def features(events: list[Event], policy: str, shuffled: list[str] | None = None) -> tuple[np.ndarray, list[str]]:
    names = ["bias", "pressure", "uncertainty", "surprise", "abs_distance"]
    if policy in {"receipt", "shuffled", "leaky"}:
        names += ["is_release", "is_witness", "is_write"]
    if policy == "leaky":
        names += ["private_friction"]
    rows: list[list[float]] = []
    for index, event in enumerate(events):
        row = [1.0, event.pressure, event.uncertainty, event.surprise, abs(event.distance)]
        if policy in {"receipt", "shuffled", "leaky"}:
            action = shuffled[index] if policy == "shuffled" and shuffled else event.action
            row += [1.0 if action == label else 0.0 for label in ACTIONS]
        if policy == "leaky":
            row += [event.private_friction]
        rows.append(row)
    return np.asarray(rows, dtype=float), names


def targets(events: list[Event], name: str) -> np.ndarray:
    if name == "delta_uncertainty_1":
        return np.asarray([event.next_uncertainty - event.uncertainty for event in events], dtype=float)
    if name == "delta_uncertainty_2":
        return np.asarray([event.lag2_uncertainty - event.uncertainty for event in events], dtype=float)
    if name == "delta_surprise_2":
        return np.asarray([event.lag2_surprise - event.surprise for event in events], dtype=float)
    raise ValueError(name)


def fit(x: np.ndarray, y: np.ndarray, lam: float = 0.002) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
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
        raise FloatingPointError("non-finite weights")
    return weights, means, stds


def predict(x: np.ndarray, model: tuple[np.ndarray, np.ndarray, np.ndarray]) -> np.ndarray:
    weights, means, stds = model
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        pred = ((x - means) / stds) @ weights
    if not np.isfinite(pred).all():
        raise FloatingPointError("non-finite predictions")
    return pred


def mae(pred: np.ndarray, y: np.ndarray) -> float:
    return float(np.mean(np.abs(pred - y)))


def evaluate(train: list[Event], test: list[Event]) -> list[Metric]:
    rng = random.Random(424242)
    shuffled_train = [event.action for event in train]
    shuffled_test = [event.action for event in test]
    rng.shuffle(shuffled_train)
    rng.shuffle(shuffled_test)
    rows: list[Metric] = []

    for target_name in ["delta_uncertainty_1", "delta_uncertainty_2", "delta_surprise_2"]:
        y_train = targets(train, target_name)
        y_test = targets(test, target_name)
        scores: dict[str, tuple[float, int, float]] = {}
        for policy in ["projection", "receipt", "shuffled", "leaky"]:
            x_train, names = features(train, policy, shuffled_train)
            x_test, _ = features(test, policy, shuffled_test)
            score = mae(predict(x_test, fit(x_train, y_train)), y_test)
            scores[policy] = (score, compressed_bits(names), 1.0 if policy == "leaky" else 0.0)

        projection = scores["projection"][0]
        shuffled = scores["shuffled"][0]
        leaky = scores["leaky"][0]
        receipt = scores["receipt"][0]
        for policy, (score, bits, leakage) in scores.items():
            rows.append(
                Metric(
                    policy=policy,
                    target=target_name,
                    mae=score,
                    gain_vs_projection=projection - score,
                    gain_vs_shuffled=shuffled - score,
                    leaky_gain=receipt - leaky,
                    feature_bits=bits,
                    leakage=leakage,
                )
            )
    return rows


def classify(rows: list[Metric]) -> tuple[str, str]:
    receipt = {row.target: row for row in rows if row.policy == "receipt"}
    min_uncertainty_gain = min(
        receipt["delta_uncertainty_1"].gain_vs_projection,
        receipt["delta_uncertainty_2"].gain_vs_projection,
        receipt["delta_uncertainty_1"].gain_vs_shuffled,
        receipt["delta_uncertainty_2"].gain_vs_shuffled,
    )
    surprise_gain = min(
        receipt["delta_surprise_2"].gain_vs_projection,
        receipt["delta_surprise_2"].gain_vs_shuffled,
    )
    max_leaky_gain = max(abs(row.leaky_gain) for row in receipt.values())
    passed = min_uncertainty_gain >= 0.004 and surprise_gain >= 0.0007 and max_leaky_gain <= 0.0015
    value = f"{min_uncertainty_gain:.4f} / {surprise_gain:.4f} / {max_leaky_gain:.4f}"
    return ("PASS" if passed else "FAIL", value)


def write_outputs(rows: list[Metric], status: str, value: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "policy",
                "target",
                "mae",
                "gain_vs_projection",
                "gain_vs_shuffled",
                "leaky_gain",
                "feature_bits",
                "leakage",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.policy,
                    row.target,
                    row.mae,
                    row.gain_vs_projection,
                    row.gain_vs_shuffled,
                    row.leaky_gain,
                    row.feature_bits,
                    row.leakage,
                ]
            )

    report = [
        "# RRL-001 Readability Relaxation Law Probe",
        "",
        "Toy telemetry only. This tests the narrowed law: receipt -> public readability shift -> lagged surprise relaxation.",
        "",
        f"Status: **{status}**",
        "",
        "Primary metric: `min_uncertainty_gain / lagged_surprise_gain / max_leaky_gain`",
        "",
        f"Value: `{value}`",
        "",
        "## Metrics",
        "",
        "| Policy | Target | MAE | Gain vs Projection | Gain vs Shuffled | Leaky Gain | Feature Bits | Leakage |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        report.append(
            f"| {row.policy} | {row.target} | {row.mae:.4f} | {row.gain_vs_projection:.4f} | "
            f"{row.gain_vs_shuffled:.4f} | {row.leaky_gain:.4f} | {row.feature_bits} | {row.leakage:.1f} |"
        )
    report += [
        "",
        "## Safe Read",
        "",
        "If this passes, the paper-safe result is that actual receipt actions can improve prediction of public readability relaxation and later surprise relaxation in a controlled toy boundary.",
        "",
        "Do not claim this proves GHP physics, sonoluminescence, time extrusion, consciousness, identity, or observer selection.",
    ]
    (OUT / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> None:
    rows = evaluate(collect(TRAIN_SEEDS), collect(TEST_SEEDS))
    status, value = classify(rows)
    write_outputs(rows, status, value)
    print(f"RRL-001: {status.lower()} :: {value}")


if __name__ == "__main__":
    main()
