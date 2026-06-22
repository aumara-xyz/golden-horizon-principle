#!/usr/bin/env python3
"""BTR-001 - Boundary Trace Refinement Probe.

GHP lab proxy for the next post-HRT test round:

- MCT-001: Minimal Cross-Section Trace
- MBT-001: Markov Blanket Conditional Independence
- WNT-001: Witness Null Trace
- LAT-001: Latency Carrier Ablation

This does not touch aukora-os. It uses synthetic public/private telemetry to
design the live Aukora test shape.

Toy telemetry only. No physics, consciousness, split-property, Markov-blanket,
Hawking-radiation, or EWCS proof.
"""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import random
import statistics
import zlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_boundary_trace_refinement_probe_outputs"
TRAIN_SEEDS = [1618, 2718, 3141, 4159, 5772]
TEST_SEEDS = [8111, 10946, 14142, 17320, 22360]
REGIMES = ["quiet", "normal", "jittery", "loaded", "bursty", "scarce"]
ACTIONS = ["release", "witness", "write"]
ACTION_INDEX = {action: i for i, action in enumerate(ACTIONS)}


@dataclass(frozen=True)
class Event:
    seed: int
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
class ProbeResult:
    probe: str
    status: str
    metric: str
    value: str
    safe_read: str


PUBLIC_FIELDS = [
    "latency_us",
    "retry_count",
    "refusal_cause",
    "confidence_delta",
    "entropy_delta",
    "stability_delta",
    "queue_pressure",
]


def stable_hash(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def compressed_bits(payload: object) -> int:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return len(zlib.compress(raw, level=9)) * 8


def params(regime: str) -> dict[str, float]:
    return {
        "quiet": {"noise": 0.05, "load": 0.10, "write_bias": 0.04},
        "normal": {"noise": 0.09, "load": 0.22, "write_bias": 0.00},
        "jittery": {"noise": 0.16, "load": 0.28, "write_bias": -0.02},
        "loaded": {"noise": 0.13, "load": 0.48, "write_bias": -0.05},
        "bursty": {"noise": 0.15, "load": 0.34, "write_bias": -0.03},
        "scarce": {"noise": 0.11, "load": 0.18, "write_bias": -0.07},
    }[regime]


def choose_action(pressure: float, confidence: float, rng: random.Random) -> str:
    if pressure > 0.68 and confidence > 0.57:
        return "write"
    if pressure > 0.48 or 0.54 <= confidence <= 0.72:
        return "witness"
    if rng.random() < 0.06:
        return "witness"
    return "release"


def generate(seed: int, regime: str, n: int = 2600) -> list[Event]:
    p = params(regime)
    rng = random.Random(int(stable_hash(["btr001", seed, regime]), 16))
    private_bucket = rng.randrange(12)
    private_authority = rng.randrange(5)
    pressure = 0.38 + rng.random() * 0.20
    confidence = 0.46 + rng.random() * 0.16
    entropy = 0.62 + rng.random() * 0.14
    stability = 0.50 + rng.random() * 0.16
    drift = rng.random()
    events: list[Event] = []

    for step in range(n):
        burst = 0.35 if regime == "bursty" and step % 97 in range(0, 9) else 0.0
        drift = 0.990 * drift + 0.010 * rng.random()
        pressure = 0.80 * pressure + 0.20 * rng.random() + 0.07 * drift + burst + p["write_bias"]
        pressure += rng.gauss(0.0, p["noise"])
        confidence = min(0.98, max(0.02, 0.86 * confidence + 0.14 * (1.0 - entropy + pressure * 0.18)))
        confidence += rng.gauss(0.0, p["noise"] * 0.08)
        action = choose_action(pressure, confidence, rng)

        if action == "write":
            latency = 930 + 250 * p["load"] + 85 * pressure + rng.gauss(0.0, 30 + 120 * p["noise"])
            retry = max(0.0, 0.11 + rng.gauss(0.0, 0.17))
            refusal = 0.0
            confidence_delta = 0.055 + 0.025 * confidence + rng.gauss(0.0, 0.010)
            entropy_delta = -0.040 - 0.012 * confidence + rng.gauss(0.0, 0.012)
            stability_delta = 0.045 + rng.gauss(0.0, 0.012)
        elif action == "witness":
            latency = 720 + 120 * p["load"] + 25 * abs(pressure - 0.58) + rng.gauss(0.0, 20 + 70 * p["noise"])
            retry = max(0.0, 0.18 + rng.gauss(0.0, 0.16))
            refusal = 1.0 if pressure > 0.68 and confidence < 0.57 else 0.0
            confidence_delta = 0.010 + rng.gauss(0.0, 0.008)
            entropy_delta = -0.010 + rng.gauss(0.0, 0.009)
            stability_delta = 0.020 + rng.gauss(0.0, 0.010)
        else:
            latency = 1050 + 380 * p["load"] + 80 * max(0.0, 0.58 - confidence) + rng.gauss(0.0, 48 + 140 * p["noise"])
            retry = max(0.0, 0.55 + 0.20 * p["load"] + rng.gauss(0.0, 0.34))
            refusal = 2.0 if pressure > 0.62 else 3.0
            confidence_delta = -0.026 - 0.012 * p["load"] + rng.gauss(0.0, 0.012)
            entropy_delta = 0.030 + 0.016 * p["load"] + rng.gauss(0.0, 0.014)
            stability_delta = -0.026 + rng.gauss(0.0, 0.013)

        confidence = min(0.98, max(0.02, confidence + confidence_delta))
        entropy = min(1.25, max(0.02, entropy + entropy_delta))
        stability = min(1.10, max(0.0, stability + stability_delta))

        events.append(
            Event(
                seed=seed,
                regime=regime,
                action=action,
                latency_us=max(50.0, latency),
                retry_count=retry,
                refusal_cause=refusal,
                confidence_delta=confidence_delta,
                entropy_delta=entropy_delta,
                stability_delta=stability_delta,
                queue_pressure=pressure,
                private_bucket=private_bucket,
                private_authority=private_authority,
            )
        )
    return events


def collect(seeds: list[int]) -> list[Event]:
    out: list[Event] = []
    for seed in seeds:
        for regime in REGIMES:
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


def fit(x: np.ndarray, y: list[int], lam: float = 0.02) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    y_arr = np.asarray(y, dtype=float)
    means = x.mean(axis=0)
    stds = x.std(axis=0)
    means[0] = 0.0
    stds[0] = 1.0
    stds[stds < 1e-9] = 1.0
    z = (x - means) / stds
    penalty = np.eye(z.shape[1]) * lam
    penalty[0, 0] = 0.0
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        weights = np.linalg.solve(z.T @ z + penalty, z.T @ y_arr)
    if not np.isfinite(weights).all():
        raise FloatingPointError("non-finite linear weights")
    return weights, means, stds


def predict_raw(x: np.ndarray, model: tuple[np.ndarray, np.ndarray, np.ndarray]) -> np.ndarray:
    weights, means, stds = model
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        pred = ((x - means) / stds) @ weights
    if not np.isfinite(pred).all():
        raise FloatingPointError("non-finite linear prediction")
    return pred


def nearest(pred: np.ndarray, k: int) -> list[int]:
    return [min(range(k), key=lambda label: abs(float(value) - label)) for value in pred]


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


def score_target(train: list[Event], test: list[Event], fields: list[str], target: str, k: int) -> float:
    model = fit(matrix(train, fields), labels(train, target))
    pred = nearest(predict_raw(matrix(test, fields), model), k)
    return macro_f1(pred, labels(test, target), k)


def shuffled_action_f1(train: list[Event], test: list[Event], fields: list[str]) -> float:
    pred_model = fit(matrix(train, fields), labels(train, "action"))
    pred = nearest(predict_raw(matrix(test, fields), pred_model), len(ACTIONS))
    truth = labels(test, "action")
    random.Random(424242).shuffle(truth)
    return macro_f1(pred, truth, len(ACTIONS))


def mct_probe(train: list[Event], test: list[Event]) -> tuple[ProbeResult, list[dict[str, object]]]:
    candidates: list[dict[str, object]] = []
    for size in range(1, 5):
        for combo in itertools.combinations(PUBLIC_FIELDS, size):
            fields = list(combo)
            action_f1 = score_target(train, test, fields, "action", len(ACTIONS))
            private_f1 = score_target(train, test, fields, "private_bucket", 12)
            candidates.append(
                {
                    "fields": "+".join(fields),
                    "field_count": size,
                    "action_f1": action_f1,
                    "private_f1": private_f1,
                    "bits": compressed_bits(fields),
                }
            )
    valid = [row for row in candidates if float(row["action_f1"]) >= 0.70 and float(row["private_f1"]) <= 0.12]
    best = min(valid, key=lambda row: (int(row["field_count"]), int(row["bits"]), -float(row["action_f1"]))) if valid else None
    if best:
        status = "PASS"
        value = f"{best['fields']} / {float(best['action_f1']):.4f} / {float(best['private_f1']):.4f} / {best['bits']}"
    else:
        status = "FAIL"
        top = max(candidates, key=lambda row: float(row["action_f1"]))
        value = f"no_valid / top={top['fields']} / {float(top['action_f1']):.4f} / {float(top['private_f1']):.4f}"
    return (
        ProbeResult(
            "MCT-001",
            status,
            "minimal_fields / action_f1 / private_f1 / compressed_bits",
            value,
            "A narrow public telemetry cross-section is useful only if it predicts boundary mode while private state remains unrecoverable.",
        ),
        candidates,
    )


def mbt_probe(train: list[Event], test: list[Event]) -> ProbeResult:
    public_private = score_target(train, test, PUBLIC_FIELDS, "private_bucket", 12)
    public_authority = score_target(train, test, PUBLIC_FIELDS, "private_authority", 5)
    leak_fields = PUBLIC_FIELDS + ["private_bucket"]
    inadmissible = score_target(train, test, leak_fields, "private_bucket", 12)
    action_f1 = score_target(train, test, PUBLIC_FIELDS, "action", len(ACTIONS))
    shuffled = shuffled_action_f1(train, test, PUBLIC_FIELDS)
    passed = action_f1 - shuffled >= 0.25 and public_private <= 0.12 and public_authority <= 0.24 and inadmissible >= 0.80
    value = f"{action_f1:.4f} / {shuffled:.4f} / {public_private:.4f} / {public_authority:.4f} / {inadmissible:.4f}"
    return ProbeResult(
        "MBT-001",
        "PASS" if passed else "FAIL",
        "action_f1 / shuffled_f1 / private_bucket_f1 / private_authority_f1 / inadmissible_private_f1",
        value,
        "A Markov-blanket analogue requires public boundary signal plus conditional private-state non-recoverability.",
    )


def wnt_probe(test: list[Event]) -> ProbeResult:
    groups = {action: [event for event in test if event.action == action] for action in ACTIONS}
    def avg(action: str, field: str) -> float:
        return statistics.fmean(float(getattr(event, field)) for event in groups[action])

    witness_latency_gap = min(avg("write", "latency_us") - avg("witness", "latency_us"), avg("release", "latency_us") - avg("witness", "latency_us"))
    witness_retry_gap = min(avg("write", "retry_count") - avg("witness", "retry_count"), avg("release", "retry_count") - avg("witness", "retry_count"))
    witness_entropy_abs = abs(avg("witness", "entropy_delta"))
    release_entropy_abs = abs(avg("release", "entropy_delta"))
    write_entropy_abs = abs(avg("write", "entropy_delta"))
    trace_score = min(release_entropy_abs, write_entropy_abs) - witness_entropy_abs
    passed = witness_latency_gap >= 80.0 and witness_retry_gap >= -0.05 and trace_score >= 0.018
    value = f"{witness_latency_gap:.2f} / {witness_retry_gap:.4f} / {trace_score:.4f}"
    return ProbeResult(
        "WNT-001",
        "PASS" if passed else "FAIL",
        "witness_latency_gap_us / witness_retry_gap / trace_quietness_gap",
        value,
        "Witness is a useful low-friction state only if it is quieter than write/release while remaining distinguishable.",
    )


def lat_probe(train: list[Event], test: list[Event]) -> tuple[ProbeResult, list[dict[str, object]]]:
    field_sets = {
        "latency_only": ["latency_us"],
        "retry_only": ["retry_count"],
        "non_time": ["refusal_cause", "confidence_delta", "entropy_delta", "stability_delta", "queue_pressure"],
        "no_latency": ["retry_count", "refusal_cause", "confidence_delta", "entropy_delta", "stability_delta", "queue_pressure"],
        "full": PUBLIC_FIELDS,
    }
    rows = []
    for name, fields in field_sets.items():
        rows.append(
            {
                "field_set": name,
                "fields": "+".join(fields),
                "action_f1": score_target(train, test, fields, "action", len(ACTIONS)),
            }
        )
    full = next(float(row["action_f1"]) for row in rows if row["field_set"] == "full")
    no_latency = next(float(row["action_f1"]) for row in rows if row["field_set"] == "no_latency")
    latency_only = next(float(row["action_f1"]) for row in rows if row["field_set"] == "latency_only")
    non_time = next(float(row["action_f1"]) for row in rows if row["field_set"] == "non_time")
    passed = (full - no_latency >= 0.03) and (latency_only >= 0.42) and (full > non_time)
    value = f"{full:.4f} / {no_latency:.4f} / {latency_only:.4f} / {non_time:.4f}"
    return (
        ProbeResult(
            "LAT-001",
            "PASS" if passed else "FAIL",
            "full_f1 / no_latency_f1 / latency_only_f1 / non_time_f1",
            value,
            "Latency is a carrier only if removing or isolating it materially changes event prediction.",
        ),
        rows,
    )


def write_outputs(results: list[ProbeResult], mct_rows: list[dict[str, object]], lat_rows: list[dict[str, object]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["probe", "status", "metric", "value", "safe_read"])
        for result in results:
            writer.writerow([result.probe, result.status, result.metric, result.value, result.safe_read])
    with (OUT / "mct_candidates.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["fields", "field_count", "action_f1", "private_f1", "bits"])
        writer.writeheader()
        writer.writerows(mct_rows)
    with (OUT / "lat_ablation.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["field_set", "fields", "action_f1"])
        writer.writeheader()
        writer.writerows(lat_rows)

    lines = [
        "# BTR-001 Boundary Trace Refinement Probe",
        "",
        "Toy telemetry only. This battery sharpens HRT-style public trace tests before any Aukora handoff.",
        "",
        "## Results",
        "",
        "| Probe | Status | Metric | Value | Safe Read |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in results:
        lines.append(f"| {result.probe} | {result.status} | {result.metric} | `{result.value}` | {result.safe_read} |")
    best_mct = sorted(mct_rows, key=lambda row: (-float(row["action_f1"]), float(row["private_f1"]), int(row["bits"])))[:8]
    lines += ["", "## Top MCT Candidates", "", "| Fields | Action F1 | Private F1 | Bits |", "| --- | ---: | ---: | ---: |"]
    for row in best_mct:
        lines.append(f"| {row['fields']} | {float(row['action_f1']):.4f} | {float(row['private_f1']):.4f} | {int(row['bits'])} |")
    lines += ["", "## Latency Ablation", "", "| Field Set | Action F1 | Fields |", "| --- | ---: | --- |"]
    for row in lat_rows:
        lines.append(f"| {row['field_set']} | {float(row['action_f1']):.4f} | {row['fields']} |")
    lines += [
        "",
        "## Safe Handoff Read",
        "",
        "Only promote an Aukora test shape if public trace predicts boundary mode while private-state reconstruction remains near chance.",
        "",
        "Do not claim this proves EWCS, split property, a true Markov blanket, Hawking radiation, consciousness, or GHP physics.",
    ]
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    train = collect(TRAIN_SEEDS)
    test = collect(TEST_SEEDS)
    mct, mct_rows = mct_probe(train, test)
    mbt = mbt_probe(train, test)
    wnt = wnt_probe(test)
    lat, lat_rows = lat_probe(train, test)
    results = [mct, mbt, wnt, lat]
    write_outputs(results, mct_rows, lat_rows)
    print("BTR-001:", " / ".join(f"{result.probe}:{result.status}" for result in results))


if __name__ == "__main__":
    main()
