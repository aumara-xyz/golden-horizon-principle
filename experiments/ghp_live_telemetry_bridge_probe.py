#!/usr/bin/env python3
"""LTB-001 - Live Telemetry Bridge Proxy.

GHP lab proxy for the next Aukora-facing test suite:

- AET-001: Epistemic Shockwave Telemetry
- HRT-001: Horizon Radiation Trace
- FBC-001: Fibonacci Cadence Window

This does not touch aukora-os. It generates live-like boundary telemetry with
public fields only, then checks whether write/witness/release after-effects can
be detected without private-state leakage.

Toy telemetry only. No physics, consciousness, Hawking-radiation, time, or
observer-selection proof.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import statistics
import zlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_live_telemetry_bridge_probe_outputs"
TRAIN_SEEDS = [1618, 2718, 3141, 4159, 5772]
TEST_SEEDS = [8111, 10946, 14142, 17320, 22360]
REGIMES = ["quiet", "normal", "jittery", "loaded", "bursty"]
ACTIONS = ["release", "witness", "write"]
ACTION_CODE = {"release": -1.0, "witness": 0.0, "write": 1.0}


@dataclass(frozen=True)
class Event:
    seed: int
    regime: str
    step: int
    action: str
    entropy: float
    confidence: float
    latency_us: float
    retry_count: float
    refusal_cause: float
    next_entropy: float
    next_confidence: float
    future_entropy_13: float
    private_bucket: int
    private_key_fragment: str


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
        "quiet": {"noise": 0.06, "load": 0.12, "burst": 0.00},
        "normal": {"noise": 0.10, "load": 0.22, "burst": 0.00},
        "jittery": {"noise": 0.17, "load": 0.26, "burst": 0.00},
        "loaded": {"noise": 0.13, "load": 0.46, "burst": 0.00},
        "bursty": {"noise": 0.16, "load": 0.32, "burst": 0.38},
    }[regime]


def choose_action(pressure: float, confidence: float, rng: random.Random) -> str:
    if pressure > 0.72 and confidence > 0.58:
        return "write"
    if pressure > 0.50 or confidence > 0.64:
        return "witness"
    if rng.random() < 0.08:
        return "witness"
    return "release"


def generate(seed: int, regime: str, n: int = 3200) -> list[Event]:
    p = params(regime)
    rng = random.Random(int(stable_hash(["ltb001", seed, regime]), 16))
    private_bucket = rng.randrange(16)
    private_key_fragment = stable_hash(["private", seed, regime, private_bucket])
    entropy = 0.62 + rng.random() * 0.15
    confidence = 0.42 + rng.random() * 0.18
    pressure = 0.45 + rng.random() * 0.20
    drift = rng.random()
    action_history: list[str] = ["release"] * 20
    raw: list[dict[str, float | str | int]] = []

    for step in range(n + 14):
        burst = p["burst"] if step % 89 in range(0, 8) else 0.0
        drift = 0.992 * drift + 0.008 * rng.random()

        # Fibonacci-lag public after-effects. This is an operator sanity test,
        # not evidence that real telemetry has Fibonacci cadence.
        fib_lag_effect = 0.0
        for lag, weight in [(1, 0.090), (2, 0.060), (3, 0.040), (5, 0.026), (8, 0.017), (13, 0.011)]:
            fib_lag_effect += weight * ACTION_CODE[action_history[-lag]]

        pressure = 0.78 * pressure + 0.22 * rng.random() + 0.08 * drift + burst
        pressure += rng.gauss(0.0, p["noise"])
        confidence = min(0.98, max(0.02, 0.84 * confidence + 0.16 * (1.0 - entropy + 0.18 * pressure)))
        confidence += rng.gauss(0.0, p["noise"] * 0.10)
        action = choose_action(pressure, confidence, rng)

        if action == "write":
            entropy_delta = -0.070 - 0.035 * confidence - 0.030 * fib_lag_effect
            confidence_delta = 0.070 + 0.025 * pressure
            latency = 900 + 240 * p["load"] + rng.gauss(0.0, 35 + 130 * p["noise"])
            retries = 0.10 + max(0.0, rng.gauss(0.0, 0.18))
            refusal = 0.0
        elif action == "witness":
            entropy_delta = -0.026 - 0.020 * abs(fib_lag_effect)
            confidence_delta = 0.026 + rng.gauss(0.0, 0.008)
            latency = 780 + 210 * p["load"] + rng.gauss(0.0, 30 + 100 * p["noise"])
            retries = 0.18 + max(0.0, rng.gauss(0.0, 0.20))
            refusal = 1.0 if pressure > 0.70 and confidence < 0.58 else 0.0
        else:
            entropy_delta = 0.044 + 0.018 * p["load"] - 0.018 * fib_lag_effect
            confidence_delta = -0.035 - 0.012 * p["load"]
            latency = 1040 + 360 * p["load"] + rng.gauss(0.0, 55 + 170 * p["noise"])
            retries = 0.60 + max(0.0, rng.gauss(0.0, 0.42))
            refusal = 2.0 if pressure > 0.68 else 3.0

        entropy = min(1.25, max(0.02, 0.88 * entropy + 0.12 * (entropy + entropy_delta)))
        confidence = min(0.98, max(0.02, confidence + confidence_delta))
        action_history.append(action)

        raw.append(
            {
                "action": action,
                "entropy": entropy + rng.gauss(0.0, p["noise"] * 0.030),
                "confidence": confidence + rng.gauss(0.0, p["noise"] * 0.025),
                "latency_us": max(100.0, latency),
                "retry_count": retries,
                "refusal_cause": refusal,
                "private_bucket": private_bucket,
                "private_key_fragment": private_key_fragment,
            }
        )

    events: list[Event] = []
    for step in range(n):
        row = raw[step]
        nxt = raw[step + 1]
        fut = raw[step + 13]
        events.append(
            Event(
                seed=seed,
                regime=regime,
                step=step,
                action=str(row["action"]),
                entropy=float(row["entropy"]),
                confidence=float(row["confidence"]),
                latency_us=float(row["latency_us"]),
                retry_count=float(row["retry_count"]),
                refusal_cause=float(row["refusal_cause"]),
                next_entropy=float(nxt["entropy"]),
                next_confidence=float(nxt["confidence"]),
                future_entropy_13=float(fut["entropy"]),
                private_bucket=int(row["private_bucket"]),
                private_key_fragment=str(row["private_key_fragment"]),
            )
        )
    return events


def collect(seeds: list[int]) -> list[Event]:
    events: list[Event] = []
    for seed in seeds:
        for regime in REGIMES:
            events.extend(generate(seed, regime))
    return events


def mean(values: list[float]) -> float:
    return statistics.fmean(values) if values else 0.0


def aet_probe(test: list[Event]) -> Result:
    by_action = {action: [event for event in test if event.action == action] for action in ACTIONS}
    write_drop = mean([event.entropy - event.next_entropy for event in by_action["write"]])
    witness_abs_delta = mean([abs(event.next_confidence - event.confidence) for event in by_action["witness"]])
    release_retry_cost = mean([event.retry_count for event in by_action["release"]]) - mean(
        [event.retry_count for event in by_action["write"] + by_action["witness"]]
    )
    release_entropy_cost = mean([event.next_entropy - event.entropy for event in by_action["release"]])
    passed = write_drop >= 0.006 and witness_abs_delta <= 0.018 and release_retry_cost >= 0.25 and release_entropy_cost >= 0.000
    value = f"{write_drop:.4f} / {witness_abs_delta:.4f} / {release_retry_cost:.4f} / {release_entropy_cost:.4f}"
    return Result(
        "AET-001",
        "PASS" if passed else "FAIL",
        "write_entropy_drop / witness_confidence_delta / release_retry_cost / release_entropy_cost",
        value,
        "Write lowers public entropy, witness is comparatively stabilizing, and release carries a short-term retry/entropy cost.",
    )


def feature_matrix(events: list[Event], include_private: bool = False) -> tuple[np.ndarray, list[str]]:
    names = ["bias", "entropy", "confidence", "latency_us", "retry_count", "refusal_cause"]
    if include_private:
        names.append("private_bucket")
    rows = []
    for event in events:
        row = [1.0, event.entropy, event.confidence, event.latency_us / 1000.0, event.retry_count, event.refusal_cause]
        if include_private:
            row.append(float(event.private_bucket))
        rows.append(row)
    return np.asarray(rows, dtype=float), names


def standard_fit(x: np.ndarray, y: np.ndarray, lam: float = 0.01) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    means = x.mean(axis=0)
    stds = x.std(axis=0)
    means[0] = 0.0
    stds[0] = 1.0
    stds[stds < 1e-9] = 1.0
    z = (x - means) / stds
    penalty = np.eye(z.shape[1]) * lam
    penalty[0, 0] = 0.0
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        weights = np.linalg.solve(z.T @ z + penalty, z.T @ y)
    if not np.isfinite(weights).all():
        raise FloatingPointError("non-finite linear weights")
    return weights, means, stds


def standard_predict(x: np.ndarray, model: tuple[np.ndarray, np.ndarray, np.ndarray]) -> np.ndarray:
    weights, means, stds = model
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        pred = ((x - means) / stds) @ weights
    if not np.isfinite(pred).all():
        raise FloatingPointError("non-finite linear prediction")
    return pred


def nearest_class(values: np.ndarray, classes: list[float]) -> list[int]:
    out = []
    for value in values:
        out.append(min(range(len(classes)), key=lambda index: abs(value - classes[index])))
    return out


def macro_f1(pred: list[int], truth: list[int], k: int) -> float:
    scores = []
    for label in range(k):
        tp = sum(1 for p, t in zip(pred, truth) if p == label and t == label)
        fp = sum(1 for p, t in zip(pred, truth) if p == label and t != label)
        fn = sum(1 for p, t in zip(pred, truth) if p != label and t == label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        scores.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return mean(scores)


def hrt_probe(train: list[Event], test: list[Event]) -> tuple[Result, dict[str, float]]:
    action_to_label = {action: index for index, action in enumerate(ACTIONS)}
    y_train = np.asarray([action_to_label[event.action] for event in train], dtype=float)
    y_test_int = [action_to_label[event.action] for event in test]
    x_train, names = feature_matrix(train)
    x_test, _ = feature_matrix(test)
    pred = nearest_class(standard_predict(x_test, standard_fit(x_train, y_train)), [0.0, 1.0, 2.0])
    action_f1 = macro_f1(pred, y_test_int, 3)

    shuffled_truth = y_test_int[:]
    random.Random(424242).shuffle(shuffled_truth)
    shuffled_f1 = macro_f1(pred, shuffled_truth, 3)

    y_private_train = np.asarray([event.private_bucket for event in train], dtype=float)
    y_private_test = [event.private_bucket for event in test]
    private_pred = nearest_class(standard_predict(x_test, standard_fit(x_train, y_private_train)), [float(i) for i in range(16)])
    private_f1 = macro_f1(private_pred, y_private_test, 16)

    x_train_leak, _ = feature_matrix(train, include_private=True)
    x_test_leak, _ = feature_matrix(test, include_private=True)
    private_leak_pred = nearest_class(
        standard_predict(x_test_leak, standard_fit(x_train_leak, y_private_train)), [float(i) for i in range(16)]
    )
    private_leak_f1 = macro_f1(private_leak_pred, y_private_test, 16)
    forbidden_leak_count = sum(1 for name in names if "private" in name.lower() or "key" in name.lower())
    public_trace_bits = compressed_bits(names)
    private_payload_bits = compressed_bits([event.private_key_fragment for event in test[:200]])

    passed = action_f1 - shuffled_f1 >= 0.25 and private_f1 <= 0.11 and private_leak_f1 >= 0.80 and forbidden_leak_count == 0
    value = f"{action_f1:.4f} / {shuffled_f1:.4f} / {private_f1:.4f} / {private_leak_f1:.4f} / {forbidden_leak_count}"
    metrics = {
        "action_f1": action_f1,
        "shuffled_f1": shuffled_f1,
        "private_f1": private_f1,
        "private_leak_f1": private_leak_f1,
        "public_trace_bits": float(public_trace_bits),
        "private_payload_bits": float(private_payload_bits),
    }
    return (
        Result(
            "HRT-001",
            "PASS" if passed else "FAIL",
            "action_f1 / shuffled_f1 / private_f1 / inadmissible_private_f1 / forbidden_leak_count",
            value,
            "Public telemetry can carry an exterior event trace while private state remains unrecoverable unless an inadmissible private field is supplied.",
        ),
        metrics,
    )


def cadence_features(events: list[Event], windows: list[int]) -> tuple[np.ndarray, list[str]]:
    names = ["bias", "entropy", "confidence"]
    names += [f"mean_action_{window}" for window in windows]
    rows = []
    codes = [ACTION_CODE[event.action] for event in events]
    for index, event in enumerate(events):
        row = [1.0, event.entropy, event.confidence]
        for window in windows:
            start = max(0, index - window + 1)
            row.append(mean(codes[start : index + 1]))
        rows.append(row)
    return np.asarray(rows, dtype=float), names


def mae(pred: np.ndarray, y: np.ndarray) -> float:
    return float(np.mean(np.abs(pred - y)))


def fbc_probe(train: list[Event], test: list[Event]) -> tuple[Result, list[dict[str, float | str]]]:
    window_sets = {
        "fibonacci": [1, 2, 3, 5, 8, 13],
        "powers2": [1, 2, 4, 8, 16],
        "linear": [1, 2, 3, 4, 5, 6],
        "wide": [2, 4, 6, 10, 14],
        "random_fixed": [1, 4, 7, 11, 15],
    }
    y_train = np.asarray([event.future_entropy_13 - event.entropy for event in train], dtype=float)
    y_test = np.asarray([event.future_entropy_13 - event.entropy for event in test], dtype=float)
    rows = []
    for name, windows in window_sets.items():
        x_train, feature_names = cadence_features(train, windows)
        x_test, _ = cadence_features(test, windows)
        score = mae(standard_predict(x_test, standard_fit(x_train, y_train)), y_test)
        rows.append({"window_set": name, "mae": score, "feature_bits": float(compressed_bits(feature_names))})
    ordered = sorted(rows, key=lambda row: float(row["mae"]))
    fib = next(row for row in rows if row["window_set"] == "fibonacci")
    second = ordered[1] if ordered[0]["window_set"] == "fibonacci" else ordered[0]
    gain = float(second["mae"]) - float(fib["mae"])
    passed = ordered[0]["window_set"] == "fibonacci" and gain >= 0.0002
    return (
        Result(
            "FBC-001",
            "PASS" if passed else "FAIL",
            "best_window_set / fib_gain_vs_next_best",
            f"{ordered[0]['window_set']} / {gain:.4f}",
            "Fibonacci cadence windows are a useful operator shape only if they beat nearby cadence controls; this toy is not live evidence.",
        ),
        rows,
    )


def write_outputs(results: list[Result], hrt_metrics: dict[str, float], fbc_rows: list[dict[str, float | str]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["probe", "status", "metric", "value", "safe_read"])
        for result in results:
            writer.writerow([result.probe, result.status, result.metric, result.value, result.safe_read])

    with (OUT / "fbc_windows.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["window_set", "mae", "feature_bits"])
        writer.writeheader()
        writer.writerows(fbc_rows)

    lines = [
        "# LTB-001 Live Telemetry Bridge Proxy",
        "",
        "Toy telemetry only. This is a handoff-shaping battery for Aukora live telemetry, not evidence for GHP physics.",
        "",
        "## Probe Results",
        "",
        "| Probe | Status | Metric | Value | Safe Read |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in results:
        lines.append(f"| {result.probe} | {result.status} | {result.metric} | `{result.value}` | {result.safe_read} |")
    lines += [
        "",
        "## HRT Split-Trace Metrics",
        "",
        f"- public action F1: `{hrt_metrics['action_f1']:.4f}`",
        f"- shuffled action F1: `{hrt_metrics['shuffled_f1']:.4f}`",
        f"- private reconstruction F1 from public trace: `{hrt_metrics['private_f1']:.4f}`",
        f"- inadmissible private-field reconstruction F1: `{hrt_metrics['private_leak_f1']:.4f}`",
        f"- public trace bits: `{hrt_metrics['public_trace_bits']:.0f}`",
        f"- sampled private payload bits: `{hrt_metrics['private_payload_bits']:.0f}`",
        "",
        "## FBC Window Scores",
        "",
        "| Window Set | MAE | Feature Bits |",
        "| --- | ---: | ---: |",
    ]
    for row in sorted(fbc_rows, key=lambda item: float(item["mae"])):
        lines.append(f"| {row['window_set']} | {float(row['mae']):.5f} | {float(row['feature_bits']):.0f} |")
    lines += [
        "",
        "## Aukora Handoff",
        "",
        "Port the telemetry shape, not the synthetic result:",
        "",
        "- log safe entropy proxies, confidence deltas, retry counts, refusal causes, latency, and receipt mode;",
        "- never log chain-of-thought, private keys, raw hidden state, or authority material;",
        "- test write/witness/release after-effects against shuffled receipts and memoryless controls;",
        "- test public horizon traces for event signal and private-state non-recoverability;",
        "- compare Fibonacci windows against powers-of-two, linear, and random windows on real telemetry.",
        "",
        "Do not claim Hawking radiation, split property, Trace Logic, or Fibonacci cadence is proven by this toy battery.",
    ]
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    train = collect(TRAIN_SEEDS)
    test = collect(TEST_SEEDS)
    aet = aet_probe(test)
    hrt, hrt_metrics = hrt_probe(train, test)
    fbc, fbc_rows = fbc_probe(train, test)
    results = [aet, hrt, fbc]
    write_outputs(results, hrt_metrics, fbc_rows)
    print("LTB-001:", " / ".join(f"{result.probe}:{result.status}" for result in results))


if __name__ == "__main__":
    main()
