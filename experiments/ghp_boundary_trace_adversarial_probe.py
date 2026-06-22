#!/usr/bin/env python3
"""BTA-001 - Boundary Trace Adversarial Probe.

Follow-up to BTR-001.

Question:
Does the public boundary trace still predict write/witness/release without
private leakage when obvious single-field action encodings are weakened and the
test holds out whole regimes?

Toy telemetry only. No physics, consciousness, EWCS, split-property, or true
Markov-blanket proof.
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
OUT = ROOT / "ghp_boundary_trace_adversarial_probe_outputs"
TRAIN_REGIMES = ["quiet", "normal", "jittery", "loaded"]
TEST_REGIMES = ["bursty", "scarce", "inverted"]
SEEDS = [1618, 2718, 3141, 4159, 5772, 8111, 10946]
ACTIONS = ["release", "witness", "write"]
ACTION_INDEX = {action: i for i, action in enumerate(ACTIONS)}
PUBLIC_FIELDS = [
    "latency_us",
    "retry_count",
    "refusal_cause",
    "confidence_delta",
    "entropy_delta",
    "stability_delta",
    "queue_pressure",
]


@dataclass(frozen=True)
class Event:
    regime: str
    action: str
    latency_us: float
    retry_count: float
    refusal_cause: float
    confidence_delta: float
    entropy_delta: float
    stability_delta: float
    queue_pressure: float
    private_bucket: int
    private_authority: int


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


def params(regime: str) -> dict[str, float]:
    return {
        "quiet": {"noise": 0.08, "load": 0.12, "invert": 0.00},
        "normal": {"noise": 0.12, "load": 0.24, "invert": 0.00},
        "jittery": {"noise": 0.19, "load": 0.30, "invert": 0.00},
        "loaded": {"noise": 0.16, "load": 0.50, "invert": 0.00},
        "bursty": {"noise": 0.20, "load": 0.38, "invert": 0.00},
        "scarce": {"noise": 0.15, "load": 0.20, "invert": 0.00},
        "inverted": {"noise": 0.18, "load": 0.32, "invert": 1.00},
    }[regime]


def choose_action(pressure: float, confidence: float, rng: random.Random) -> str:
    if pressure > 0.70 and confidence > 0.58:
        return "write"
    if pressure > 0.50 or confidence > 0.60:
        return "witness"
    if rng.random() < 0.10:
        return "witness"
    return "release"


def generate(seed: int, regime: str, n: int = 2400) -> list[Event]:
    p = params(regime)
    rng = random.Random(int(stable_hash(["bta001", seed, regime]), 16))
    private_bucket = rng.randrange(12)
    private_authority = rng.randrange(5)
    pressure = 0.42 + rng.random() * 0.18
    confidence = 0.48 + rng.random() * 0.14
    entropy = 0.62 + rng.random() * 0.16
    stability = 0.50 + rng.random() * 0.16
    events: list[Event] = []

    for step in range(n):
        burst = 0.28 if regime == "bursty" and step % 101 in range(0, 11) else 0.0
        pressure = 0.82 * pressure + 0.18 * rng.random() + burst + rng.gauss(0.0, p["noise"])
        confidence = min(0.98, max(0.02, 0.88 * confidence + 0.12 * (1.0 - entropy + 0.16 * pressure)))
        confidence += rng.gauss(0.0, p["noise"] * 0.10)
        action = choose_action(pressure, confidence, rng)

        shared_jitter = rng.gauss(0.0, 0.026 + p["noise"] * 0.05)
        if action == "write":
            base_latency = 900 + 245 * p["load"] + rng.gauss(0.0, 75)
            base_retry = 0.20 + rng.gauss(0.0, 0.24)
            refusal = 0.0
            conf_delta = 0.030 + shared_jitter
            ent_delta = -0.020 - 0.012 * (1.0 - p["invert"]) + shared_jitter
            stab_delta = 0.030 + rng.gauss(0.0, 0.018)
        elif action == "witness":
            base_latency = 820 + 210 * p["load"] + rng.gauss(0.0, 70)
            base_retry = 0.28 + rng.gauss(0.0, 0.25)
            refusal = 1.0 if pressure > 0.66 and confidence < 0.60 else 0.0
            conf_delta = 0.012 + shared_jitter
            ent_delta = -0.006 + shared_jitter
            stab_delta = 0.018 + rng.gauss(0.0, 0.018)
        else:
            base_latency = 1010 + 300 * p["load"] + rng.gauss(0.0, 85)
            base_retry = 0.48 + rng.gauss(0.0, 0.33)
            refusal = 2.0 if pressure > 0.60 else 3.0
            conf_delta = -0.020 + shared_jitter
            ent_delta = 0.018 + 0.010 * (1.0 - p["invert"]) + shared_jitter
            stab_delta = -0.018 + rng.gauss(0.0, 0.020)

        # Inverted regime deliberately breaks the obvious entropy/action map.
        if p["invert"] > 0.5:
            ent_delta *= -0.65
            conf_delta *= 0.50

        entropy = min(1.25, max(0.02, entropy + ent_delta))
        confidence = min(0.98, max(0.02, confidence + conf_delta))
        stability = min(1.10, max(0.0, stability + stab_delta))

        events.append(
            Event(
                regime=regime,
                action=action,
                latency_us=max(50.0, base_latency),
                retry_count=max(0.0, base_retry),
                refusal_cause=refusal,
                confidence_delta=conf_delta,
                entropy_delta=ent_delta,
                stability_delta=stab_delta,
                queue_pressure=pressure,
                private_bucket=private_bucket,
                private_authority=private_authority,
            )
        )
    return events


def collect(regimes: list[str]) -> list[Event]:
    out: list[Event] = []
    for seed in SEEDS:
        for regime in regimes:
            out.extend(generate(seed, regime))
    return out


def matrix(events: list[Event], fields: list[str]) -> np.ndarray:
    rows = []
    for event in events:
        row = [1.0]
        for field in fields:
            value = float(getattr(event, field))
            if field == "latency_us":
                value /= 1000.0
            row.append(value)
        rows.append(row)
    return np.asarray(rows, dtype=float)


def labels(events: list[Event], target: str) -> list[int]:
    if target == "action":
        return [ACTION_INDEX[event.action] for event in events]
    if target == "private_bucket":
        return [event.private_bucket for event in events]
    if target == "private_authority":
        return [event.private_authority for event in events]
    raise ValueError(target)


def fit(x: np.ndarray, y: list[int], lam: float = 0.05) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    means = x.mean(axis=0)
    stds = x.std(axis=0)
    means[0] = 0.0
    stds[0] = 1.0
    stds[stds < 1e-9] = 1.0
    z = (x - means) / stds
    penalty = np.eye(z.shape[1]) * lam
    penalty[0, 0] = 0.0
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        weights = np.linalg.solve(z.T @ z + penalty, z.T @ np.asarray(y, dtype=float))
    if not np.isfinite(weights).all():
        raise FloatingPointError("non-finite linear weights")
    return weights, means, stds


def predict(x: np.ndarray, model: tuple[np.ndarray, np.ndarray, np.ndarray]) -> np.ndarray:
    weights, means, stds = model
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        pred = ((x - means) / stds) @ weights
    if not np.isfinite(pred).all():
        raise FloatingPointError("non-finite linear prediction")
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


def score(train: list[Event], test: list[Event], fields: list[str], target: str, k: int) -> float:
    pred = nearest(predict(matrix(test, fields), fit(matrix(train, fields), labels(train, target))), k)
    return macro_f1(pred, labels(test, target), k)


def shuffled_score(train: list[Event], test: list[Event], fields: list[str]) -> float:
    pred = nearest(predict(matrix(test, fields), fit(matrix(train, fields), labels(train, "action"))), len(ACTIONS))
    truth = labels(test, "action")
    random.Random(424242).shuffle(truth)
    return macro_f1(pred, truth, len(ACTIONS))


def run(train: list[Event], test: list[Event]) -> tuple[list[Result], list[dict[str, object]]]:
    field_sets = {
        "full": PUBLIC_FIELDS,
        "minimal_noisy": ["entropy_delta"],
        "cross_section": ["refusal_cause", "confidence_delta", "entropy_delta", "stability_delta"],
        "no_entropy": ["latency_us", "retry_count", "refusal_cause", "confidence_delta", "stability_delta", "queue_pressure"],
        "latency_only": ["latency_us"],
    }
    rows = []
    for name, fields in field_sets.items():
        action_f1 = score(train, test, fields, "action", len(ACTIONS))
        private_f1 = score(train, test, fields, "private_bucket", 12)
        authority_f1 = score(train, test, fields, "private_authority", 5)
        shuffled = shuffled_score(train, test, fields)
        rows.append(
            {
                "field_set": name,
                "fields": "+".join(fields),
                "action_f1": action_f1,
                "shuffled_f1": shuffled,
                "private_f1": private_f1,
                "authority_f1": authority_f1,
                "bits": compressed_bits(fields),
            }
        )
    full = next(row for row in rows if row["field_set"] == "full")
    cross = next(row for row in rows if row["field_set"] == "cross_section")
    latency = next(row for row in rows if row["field_set"] == "latency_only")
    no_entropy = next(row for row in rows if row["field_set"] == "no_entropy")
    passed = (
        float(cross["action_f1"]) - float(cross["shuffled_f1"]) >= 0.18
        and float(cross["private_f1"]) <= 0.12
        and float(cross["authority_f1"]) <= 0.25
    )
    latency_passed = float(latency["action_f1"]) >= 0.42 and float(full["action_f1"]) - float(no_entropy["action_f1"]) >= 0.03
    results = [
        Result(
            "BTA-001",
            "PASS" if passed else "FAIL",
            "cross_action_f1 / shuffled_f1 / private_f1 / authority_f1",
            f"{float(cross['action_f1']):.4f} / {float(cross['shuffled_f1']):.4f} / {float(cross['private_f1']):.4f} / {float(cross['authority_f1']):.4f}",
            "The public trace survives harder regime holdout only if it beats shuffled controls while private state remains near chance.",
        ),
        Result(
            "LAT-001R",
            "PASS" if latency_passed else "FAIL",
            "latency_only_f1 / full_minus_no_entropy",
            f"{float(latency['action_f1']):.4f} / {float(full['action_f1']) - float(no_entropy['action_f1']):.4f}",
            "Latency is not primary unless it carries signal under regime holdout and materially improves the full model.",
        ),
    ]
    return results, rows


def write_outputs(results: list[Result], rows: list[dict[str, object]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["probe", "status", "metric", "value", "safe_read"])
        for result in results:
            writer.writerow([result.probe, result.status, result.metric, result.value, result.safe_read])
    with (OUT / "field_sets.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["field_set", "fields", "action_f1", "shuffled_f1", "private_f1", "authority_f1", "bits"])
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        "# BTA-001 Boundary Trace Adversarial Probe",
        "",
        "Toy telemetry only. This stress-tests the HRT/MCT/MBT trace under harder regime holdouts.",
        "",
        "| Probe | Status | Metric | Value | Safe Read |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in results:
        lines.append(f"| {result.probe} | {result.status} | {result.metric} | `{result.value}` | {result.safe_read} |")
    lines += ["", "## Field Sets", "", "| Set | Action F1 | Shuffled F1 | Private F1 | Authority F1 | Bits |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for row in rows:
        lines.append(
            f"| {row['field_set']} | {float(row['action_f1']):.4f} | {float(row['shuffled_f1']):.4f} | "
            f"{float(row['private_f1']):.4f} | {float(row['authority_f1']):.4f} | {int(row['bits'])} |"
        )
    lines += [
        "",
        "## Safe Read",
        "",
        "If this passes, the HRT handoff becomes stronger but remains an engineering analogue only.",
        "",
        "Do not claim this proves EWCS, Markov blankets, split property, Hawking radiation, consciousness, or GHP physics.",
    ]
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    results, rows = run(collect(TRAIN_REGIMES), collect(TEST_REGIMES))
    write_outputs(results, rows)
    print("BTA-001:", " / ".join(f"{result.probe}:{result.status}" for result in results))


if __name__ == "__main__":
    main()
