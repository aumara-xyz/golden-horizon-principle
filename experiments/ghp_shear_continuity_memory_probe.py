#!/usr/bin/env python3
"""SCM-001 - Shear Continuity Memory Probe.

Tests whether an unresolved contradiction/shear memory improves boundary-mode
prediction compared with forced coherence or raw case memory.

This is inspired by:

- THE_SHEAR_ENGINE.md: hold productive incoherence instead of collapsing it.
- Auracle Continuity Layer: episodic memory, hybrid retrieval, consolidation.
- JEPA-style intuition: predict future latent state from compact internal state,
  not by reconstructing every raw detail.

Toy telemetry only. No proof of GHP, consciousness, JEPA, robotics, or physics.
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

import numpy as np


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_shear_continuity_memory_probe_outputs"
TRAIN_SEEDS = [1618, 2718, 3141, 4159, 5772]
TEST_SEEDS = [8111, 10946, 14142, 17320, 22360]
ACTIONS = ["release", "witness", "write"]
ACTION_INDEX = {action: i for i, action in enumerate(ACTIONS)}
PHI = (1 + 5 ** 0.5) / 2
SHEAR_FLOOR = 1 / PHI


@dataclass(frozen=True)
class Event:
    seed: int
    episode: int
    step: int
    action: str
    confidence_delta: float
    entropy_delta: float
    stability_delta: float
    refusal_cause: float
    lexical_tag: int
    semantic_coord: float
    framework_a: float
    framework_b: float
    shear: float
    next_action: str
    private_bucket: int


@dataclass(frozen=True)
class Result:
    probe: str
    status: str
    metric: str
    value: str
    safe_read: str


def stable_hash(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def compressed_bits(payload: object) -> int:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return len(zlib.compress(raw, level=9)) * 8


def action_from_state(pressure: float, confidence: float, shear: float) -> str:
    if pressure > 0.70 and confidence > 0.58 and shear < 0.78:
        return "write"
    if pressure > 0.50 or shear > 0.66 or 0.54 <= confidence <= 0.72:
        return "witness"
    return "release"


def generate(seed: int, episodes: int = 28, steps: int = 130) -> list[Event]:
    rng = random.Random(int(stable_hash(["scm001", seed]), 16))
    events: list[Event] = []
    for episode in range(episodes):
        private_bucket = rng.randrange(12)
        lexical_topic = rng.randrange(9)
        latent_task = rng.random()
        framework_a = rng.uniform(-1.0, 1.0)
        framework_b = rng.uniform(-1.0, 1.0)
        shear_memory = max(SHEAR_FLOOR, min(1.0, abs(framework_a - framework_b) / 2))
        pressure = 0.40 + rng.random() * 0.20
        confidence = 0.48 + rng.random() * 0.18
        entropy = 0.64 + rng.random() * 0.14
        stability = 0.50 + rng.random() * 0.14
        raw: list[dict[str, float | str | int]] = []

        for step in range(steps + 1):
            framework_a = 0.92 * framework_a + 0.08 * (latent_task * 2 - 1) + rng.gauss(0.0, 0.08)
            framework_b = 0.90 * framework_b + 0.10 * (rng.random() * 2 - 1) + rng.gauss(0.0, 0.08)
            current_shear = max(SHEAR_FLOOR, min(1.0, 0.72 * shear_memory + 0.28 * abs(framework_a - framework_b) / 2))

            pressure = 0.82 * pressure + 0.18 * rng.random() + 0.10 * (current_shear - SHEAR_FLOOR)
            confidence = min(0.98, max(0.02, 0.88 * confidence + 0.12 * (1 - entropy + 0.10 * pressure)))
            action = action_from_state(pressure, confidence, current_shear)

            if action == "write":
                confidence_delta = 0.045 + rng.gauss(0.0, 0.012)
                entropy_delta = -0.030 + rng.gauss(0.0, 0.014)
                stability_delta = 0.050 + rng.gauss(0.0, 0.014)
                refusal = 0
                shear_memory = SHEAR_FLOOR + (current_shear - SHEAR_FLOOR) * 0.62
            elif action == "witness":
                confidence_delta = 0.010 + rng.gauss(0.0, 0.011)
                entropy_delta = -0.004 + rng.gauss(0.0, 0.013)
                stability_delta = 0.018 + rng.gauss(0.0, 0.012)
                refusal = 1 if pressure > 0.66 and confidence < 0.60 else 0
                shear_memory = min(1.0, SHEAR_FLOOR + (current_shear - SHEAR_FLOOR) * 0.92 + 0.035)
            else:
                confidence_delta = -0.025 + rng.gauss(0.0, 0.014)
                entropy_delta = 0.026 + rng.gauss(0.0, 0.016)
                stability_delta = -0.022 + rng.gauss(0.0, 0.014)
                refusal = 2 if pressure > 0.60 else 3
                shear_memory = min(1.0, SHEAR_FLOOR + (current_shear - SHEAR_FLOOR) * 0.80 + 0.060)

            entropy = min(1.25, max(0.02, entropy + entropy_delta))
            confidence = min(0.98, max(0.02, confidence + confidence_delta))
            stability = min(1.10, max(0.0, stability + stability_delta))
            semantic_coord = 0.65 * latent_task + 0.20 * pressure + 0.15 * current_shear
            raw.append(
                {
                    "action": action,
                    "confidence_delta": confidence_delta,
                    "entropy_delta": entropy_delta,
                    "stability_delta": stability_delta,
                    "refusal_cause": refusal,
                    "lexical_tag": lexical_topic if rng.random() > 0.18 else rng.randrange(9),
                    "semantic_coord": semantic_coord,
                    "framework_a": framework_a,
                    "framework_b": framework_b,
                    "shear": current_shear,
                    "private_bucket": private_bucket,
                }
            )

        for step in range(steps):
            row = raw[step]
            nxt = raw[step + 1]
            events.append(
                Event(
                    seed=seed,
                    episode=episode,
                    step=step,
                    action=str(row["action"]),
                    confidence_delta=float(row["confidence_delta"]),
                    entropy_delta=float(row["entropy_delta"]),
                    stability_delta=float(row["stability_delta"]),
                    refusal_cause=float(row["refusal_cause"]),
                    lexical_tag=int(row["lexical_tag"]),
                    semantic_coord=float(row["semantic_coord"]),
                    framework_a=float(row["framework_a"]),
                    framework_b=float(row["framework_b"]),
                    shear=float(row["shear"]),
                    next_action=str(nxt["action"]),
                    private_bucket=int(row["private_bucket"]),
                )
            )
    return events


def collect(seeds: list[int]) -> list[Event]:
    events: list[Event] = []
    for seed in seeds:
        events.extend(generate(seed))
    return events


def matrix(events: list[Event], policy: str) -> tuple[np.ndarray, list[str]]:
    fields_by_policy = {
        "memoryless_public": ["confidence_delta", "entropy_delta", "stability_delta", "refusal_cause"],
        "forced_coherence": ["confidence_delta", "entropy_delta", "stability_delta", "refusal_cause", "coherence_mean"],
        "shear_memory": ["confidence_delta", "entropy_delta", "stability_delta", "refusal_cause", "coherence_mean", "shear"],
        "raw_frameworks": ["confidence_delta", "entropy_delta", "stability_delta", "refusal_cause", "framework_a", "framework_b"],
        "hybrid_continuity": ["confidence_delta", "entropy_delta", "stability_delta", "refusal_cause", "lexical_tag", "semantic_coord", "shear"],
        "leaky_private": ["confidence_delta", "entropy_delta", "stability_delta", "refusal_cause", "coherence_mean", "shear", "private_bucket"],
    }
    fields = fields_by_policy[policy]
    rows = []
    for event in events:
        row = [1.0]
        for field in fields:
            if field == "coherence_mean":
                value = (event.framework_a + event.framework_b) / 2
            else:
                value = float(getattr(event, field))
            row.append(value)
        rows.append(row)
    return np.asarray(rows, dtype=float), fields


def y(events: list[Event], target: str) -> list[int]:
    if target == "next_action":
        return [ACTION_INDEX[event.next_action] for event in events]
    if target == "private_bucket":
        return [event.private_bucket for event in events]
    raise ValueError(target)


def fit(x: np.ndarray, target: list[int], lam: float = 0.03) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    means = x.mean(axis=0)
    stds = x.std(axis=0)
    means[0] = 0.0
    stds[0] = 1.0
    stds[stds < 1e-9] = 1.0
    z = (x - means) / stds
    penalty = np.eye(z.shape[1]) * lam
    penalty[0, 0] = 0.0
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        weights = np.linalg.solve(z.T @ z + penalty, z.T @ np.asarray(target, dtype=float))
    if not np.isfinite(weights).all():
        raise FloatingPointError("non-finite weights")
    return weights, means, stds


def predict(x: np.ndarray, model: tuple[np.ndarray, np.ndarray, np.ndarray]) -> np.ndarray:
    weights, means, stds = model
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        pred = ((x - means) / stds) @ weights
    if not np.isfinite(pred).all():
        raise FloatingPointError("non-finite prediction")
    return pred


def nearest(values: np.ndarray, k: int) -> list[int]:
    return [min(range(k), key=lambda label: abs(float(value) - label)) for value in values]


def macro_f1(pred: list[int], truth: list[int], k: int) -> float:
    scores = []
    for label in range(k):
        tp = sum(1 for p, t in zip(pred, truth) if p == label and t == label)
        fp = sum(1 for p, t in zip(pred, truth) if p == label and t != label)
        fn = sum(1 for p, t in zip(pred, truth) if p != label and t == label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        scores.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return statistics.fmean(scores)


def score(train: list[Event], test: list[Event], policy: str, target: str, k: int) -> tuple[float, int]:
    x_train, fields = matrix(train, policy)
    x_test, _ = matrix(test, policy)
    pred = nearest(predict(x_test, fit(x_train, y(train, target))), k)
    return macro_f1(pred, y(test, target), k), compressed_bits(fields)


def run(train: list[Event], test: list[Event]) -> tuple[list[Result], list[dict[str, object]]]:
    policies = ["memoryless_public", "forced_coherence", "shear_memory", "raw_frameworks", "hybrid_continuity", "leaky_private"]
    rows = []
    for policy in policies:
        next_f1, bits = score(train, test, policy, "next_action", len(ACTIONS))
        private_f1, _ = score(train, test, policy, "private_bucket", 12)
        rows.append({"policy": policy, "next_action_f1": next_f1, "private_f1": private_f1, "bits": bits})

    base = next(float(row["next_action_f1"]) for row in rows if row["policy"] == "memoryless_public")
    forced = next(float(row["next_action_f1"]) for row in rows if row["policy"] == "forced_coherence")
    shear = next(float(row["next_action_f1"]) for row in rows if row["policy"] == "shear_memory")
    hybrid = next(float(row["next_action_f1"]) for row in rows if row["policy"] == "hybrid_continuity")
    leaky_private = next(float(row["private_f1"]) for row in rows if row["policy"] == "leaky_private")
    shear_private = next(float(row["private_f1"]) for row in rows if row["policy"] == "shear_memory")

    scm_pass = shear - forced >= 0.015 and shear - base >= 0.015 and shear_private <= 0.12
    hybrid_pass = hybrid - shear >= 0.005 and leaky_private >= 0.50
    return (
        [
            Result(
                "SCM-001",
                "PASS" if scm_pass else "FAIL",
                "shear_f1 / forced_f1 / memoryless_f1 / shear_private_f1",
                f"{shear:.4f} / {forced:.4f} / {base:.4f} / {shear_private:.4f}",
                "Shear memory is useful only if unresolved tension beats forced coherence without leaking private state.",
            ),
            Result(
                "HCM-001",
                "PASS" if hybrid_pass else "FAIL",
                "hybrid_f1 / shear_f1 / leaky_private_f1",
                f"{hybrid:.4f} / {shear:.4f} / {leaky_private:.4f}",
                "Hybrid continuity is useful only if lexical/semantic episode cues improve prediction beyond shear alone; private leakage remains a forbidden positive control.",
            ),
        ],
        rows,
    )


def write_outputs(results: list[Result], rows: list[dict[str, object]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["probe", "status", "metric", "value", "safe_read"])
        for result in results:
            writer.writerow([result.probe, result.status, result.metric, result.value, result.safe_read])
    with (OUT / "policy_scores.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["policy", "next_action_f1", "private_f1", "bits"])
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# SCM-001 Shear Continuity Memory Probe",
        "",
        "Toy telemetry only. This tests whether unresolved shear memory improves next boundary prediction.",
        "",
        "| Probe | Status | Metric | Value | Safe Read |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in results:
        lines.append(f"| {result.probe} | {result.status} | {result.metric} | `{result.value}` | {result.safe_read} |")
    lines += ["", "## Policy Scores", "", "| Policy | Next Action F1 | Private F1 | Bits |", "| --- | ---: | ---: | ---: |"]
    for row in rows:
        lines.append(f"| {row['policy']} | {float(row['next_action_f1']):.4f} | {float(row['private_f1']):.4f} | {int(row['bits'])} |")
    lines += [
        "",
        "## Safe Read",
        "",
        "If SCM passes, the next test should treat witness as retained shear / unresolved tension rather than a simple event label.",
        "",
        "Do not claim this proves JEPA, robotics memory, GHP physics, consciousness, or a live organism.",
    ]
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    results, rows = run(collect(TRAIN_SEEDS), collect(TEST_SEEDS))
    write_outputs(results, rows)
    print("SCM-001:", " / ".join(f"{result.probe}:{result.status}" for result in results))


if __name__ == "__main__":
    main()
