#!/usr/bin/env python3
"""BSW-001 - Boundary Sequence & Witness Footprint Probe.

GHP lab proxy for the post-BTA test round:

- WPF-001: Witness Pressure Footprint
- STP-001: Sequential Trace Prediction

This does not touch aukora-os. It uses synthetic safe public telemetry to shape
the next live handoff.

Toy telemetry only. No physics, consciousness, Markov-blanket, split-property,
or GHP proof.
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
OUT = ROOT / "ghp_boundary_sequence_witness_probe_outputs"
TRAIN_SEEDS = [1618, 2718, 3141, 4159, 5772]
TEST_SEEDS = [8111, 10946, 14142, 17320, 22360]
REGIMES = ["quiet", "normal", "jittery", "loaded", "bursty", "scarce", "inverted"]
ACTIONS = ["release", "witness", "write"]
ACTION_INDEX = {action: i for i, action in enumerate(ACTIONS)}
PUBLIC_FIELDS = ["confidence_delta", "entropy_delta", "stability_delta", "retry_count", "refusal_cause"]


@dataclass(frozen=True)
class Event:
    seed: int
    regime: str
    step: int
    action: str
    confidence_delta: float
    entropy_delta: float
    stability_delta: float
    retry_count: float
    refusal_cause: float
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
        "quiet": {"noise": 0.07, "load": 0.12, "invert": 0.0},
        "normal": {"noise": 0.11, "load": 0.24, "invert": 0.0},
        "jittery": {"noise": 0.18, "load": 0.30, "invert": 0.0},
        "loaded": {"noise": 0.15, "load": 0.50, "invert": 0.0},
        "bursty": {"noise": 0.19, "load": 0.38, "invert": 0.0},
        "scarce": {"noise": 0.14, "load": 0.20, "invert": 0.0},
        "inverted": {"noise": 0.18, "load": 0.32, "invert": 1.0},
    }[regime]


def choose_action(pressure: float, confidence: float, tension: float, rng: random.Random) -> str:
    if pressure > 0.72 and confidence > 0.58 and tension < 0.74:
        return "write"
    if pressure > 0.50 or tension > 0.56 or 0.54 <= confidence <= 0.72:
        return "witness"
    if rng.random() < 0.08:
        return "witness"
    return "release"


def generate(seed: int, regime: str, n: int = 3000) -> list[Event]:
    p = params(regime)
    rng = random.Random(int(stable_hash(["bsw001", seed, regime]), 16))
    private_bucket = rng.randrange(12)
    private_authority = rng.randrange(5)
    pressure = 0.40 + rng.random() * 0.20
    confidence = 0.48 + rng.random() * 0.15
    entropy = 0.62 + rng.random() * 0.14
    stability = 0.48 + rng.random() * 0.18
    tension = 0.30 + rng.random() * 0.20
    last_action = "release"
    events: list[Event] = []

    for step in range(n):
        burst = 0.30 if regime == "bursty" and step % 101 in range(0, 11) else 0.0
        pressure = 0.80 * pressure + 0.20 * rng.random() + burst + rng.gauss(0.0, p["noise"])
        confidence = min(0.98, max(0.02, 0.88 * confidence + 0.12 * (1.0 - entropy + 0.16 * pressure)))
        confidence += rng.gauss(0.0, p["noise"] * 0.10)

        # Temporal after-effect. This is what STP tries to recover from public traces.
        if last_action == "write":
            tension = 0.62 * tension - 0.040 + rng.gauss(0.0, 0.018)
        elif last_action == "witness":
            tension = 0.88 * tension + 0.032 + rng.gauss(0.0, 0.014)
        else:
            tension = 0.74 * tension + 0.055 + rng.gauss(0.0, 0.026)
        tension = min(1.0, max(0.0, tension))

        action = choose_action(pressure, confidence, tension, rng)
        shared = rng.gauss(0.0, 0.018 + p["noise"] * 0.05)

        if action == "write":
            conf_delta = 0.042 + 0.018 * confidence + shared
            ent_delta = -0.026 - 0.012 * confidence + shared
            stab_delta = 0.050 + 0.020 * (1.0 - tension) + rng.gauss(0.0, 0.014)
            retry = max(0.0, 0.16 + rng.gauss(0.0, 0.20))
            refusal = 0.0
            tension *= 0.70
        elif action == "witness":
            # Active quarantine: small movement, low resolution, sustained tension.
            conf_delta = 0.010 + rng.gauss(0.0, 0.010)
            ent_delta = -0.004 + shared * 0.55
            stab_delta = 0.014 + rng.gauss(0.0, 0.010)
            retry = max(0.0, 0.24 + 0.15 * tension + rng.gauss(0.0, 0.18))
            refusal = 1.0 if pressure > 0.66 and confidence < 0.60 else 0.0
            tension = min(1.0, tension + 0.050)
        else:
            conf_delta = -0.026 - 0.010 * p["load"] + shared
            ent_delta = 0.022 + 0.012 * p["load"] + shared
            stab_delta = -0.022 - 0.010 * tension + rng.gauss(0.0, 0.016)
            retry = max(0.0, 0.48 + 0.22 * p["load"] + 0.18 * tension + rng.gauss(0.0, 0.30))
            refusal = 2.0 if pressure > 0.62 else 3.0
            tension = min(1.0, tension + 0.080)

        if p["invert"] > 0.5:
            ent_delta *= -0.55
            conf_delta *= 0.60

        entropy = min(1.25, max(0.02, entropy + ent_delta))
        confidence = min(0.98, max(0.02, confidence + conf_delta))
        stability = min(1.10, max(0.0, stability + stab_delta))
        last_action = action

        events.append(
            Event(
                seed=seed,
                regime=regime,
                step=step,
                action=action,
                confidence_delta=conf_delta,
                entropy_delta=ent_delta,
                stability_delta=stab_delta,
                retry_count=retry,
                refusal_cause=refusal,
                private_bucket=private_bucket,
                private_authority=private_authority,
            )
        )
    return events


def collect(seeds: list[int]) -> list[Event]:
    events: list[Event] = []
    for seed in seeds:
        for regime in REGIMES:
            events.extend(generate(seed, regime))
    return events


def rows(events: list[Event], fields: list[str]) -> np.ndarray:
    data = []
    for event in events:
        data.append([1.0] + [float(getattr(event, field)) for field in fields])
    return np.asarray(data, dtype=float)


def y_values(events: list[Event], target: str) -> np.ndarray:
    if target == "action":
        return np.asarray([ACTION_INDEX[event.action] for event in events], dtype=float)
    if target == "next_stability":
        return np.asarray([events[i + 1].stability_delta for i in range(len(events) - 1)], dtype=float)
    if target == "private_bucket":
        return np.asarray([event.private_bucket for event in events], dtype=float)
    raise ValueError(target)


def fit(x: np.ndarray, y: np.ndarray, lam: float = 0.03) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
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


def mae(pred: np.ndarray, truth: np.ndarray) -> float:
    return float(np.mean(np.abs(pred - truth)))


def score_action(train: list[Event], test: list[Event], fields: list[str]) -> float:
    model = fit(rows(train, fields), y_values(train, "action"))
    pred = nearest(predict(rows(test, fields), model), len(ACTIONS))
    truth = [ACTION_INDEX[event.action] for event in test]
    return macro_f1(pred, truth, len(ACTIONS))


def wpf_probe(train: list[Event], test: list[Event]) -> tuple[Result, list[dict[str, float | str]]]:
    field_sets = {
        "pressure_shape": ["confidence_delta", "entropy_delta", "stability_delta", "retry_count"],
        "no_retry": ["confidence_delta", "entropy_delta", "stability_delta"],
        "friction_only": ["retry_count", "refusal_cause"],
        "full_public": PUBLIC_FIELDS,
    }
    rows_out = []
    for name, fields in field_sets.items():
        action_f1 = score_action(train, test, fields)
        private_pred = nearest(predict(rows(test, fields), fit(rows(train, fields), y_values(train, "private_bucket"))), 12)
        private_truth = [event.private_bucket for event in test]
        private_f1 = macro_f1(private_pred, private_truth, 12)
        rows_out.append({"field_set": name, "fields": "+".join(fields), "action_f1": action_f1, "private_f1": private_f1})

    best = max(rows_out, key=lambda item: float(item["action_f1"]))
    witness_events = [event for event in test if event.action == "witness"]
    write_events = [event for event in test if event.action == "write"]
    release_events = [event for event in test if event.action == "release"]
    witness_plateau = abs(statistics.fmean(event.confidence_delta for event in witness_events))
    write_resolution = statistics.fmean(event.stability_delta for event in write_events)
    release_friction = statistics.fmean(event.retry_count for event in release_events)
    witness_friction = statistics.fmean(event.retry_count for event in witness_events)
    plateau_ok = witness_plateau <= 0.020 and write_resolution >= 0.040 and release_friction - witness_friction >= 0.10
    passed = float(best["action_f1"]) >= 0.72 and float(best["private_f1"]) <= 0.12 and plateau_ok
    value = f"{best['field_set']} / {float(best['action_f1']):.4f} / {float(best['private_f1']):.4f} / {witness_plateau:.4f}"
    return (
        Result(
            "WPF-001",
            "PASS" if passed else "FAIL",
            "best_field_set / action_f1 / private_f1 / witness_confidence_plateau",
            value,
            "Witness is active quarantine if it has a stable pressure footprint, not a null trace.",
        ),
        rows_out,
    )


def sequence_rows(events: list[Event], fields: list[str], include_previous: bool) -> tuple[np.ndarray, np.ndarray]:
    x = []
    y = []
    for i in range(1, len(events) - 1):
        # Avoid stitching across generated streams.
        if events[i - 1].seed != events[i].seed or events[i].regime != events[i - 1].regime:
            continue
        if events[i + 1].seed != events[i].seed or events[i].regime != events[i + 1].regime:
            continue
        row = [1.0]
        if include_previous:
            row += [float(getattr(events[i - 1], field)) for field in fields]
            row += [float(ACTION_INDEX[events[i - 1].action])]
        row += [float(getattr(events[i], field)) for field in fields]
        x.append(row)
        y.append(float(events[i + 1].stability_delta))
    return np.asarray(x, dtype=float), np.asarray(y, dtype=float)


def stp_probe(train: list[Event], test: list[Event]) -> Result:
    current_train_x, current_train_y = sequence_rows(train, PUBLIC_FIELDS, include_previous=False)
    current_test_x, current_test_y = sequence_rows(test, PUBLIC_FIELDS, include_previous=False)
    seq_train_x, seq_train_y = sequence_rows(train, PUBLIC_FIELDS, include_previous=True)
    seq_test_x, seq_test_y = sequence_rows(test, PUBLIC_FIELDS, include_previous=True)
    memoryless_mae = mae(predict(current_test_x, fit(current_train_x, current_train_y)), current_test_y)
    sequence_mae = mae(predict(seq_test_x, fit(seq_train_x, seq_train_y)), seq_test_y)
    shuffled_seq = seq_train_x.copy()
    rng = np.random.default_rng(424242)
    rng.shuffle(shuffled_seq[:, 1 : 1 + len(PUBLIC_FIELDS) + 1])
    shuffled_mae = mae(predict(seq_test_x, fit(shuffled_seq, seq_train_y)), seq_test_y)
    gain_vs_memoryless = memoryless_mae - sequence_mae
    gain_vs_shuffled = shuffled_mae - sequence_mae
    passed = gain_vs_memoryless >= 0.0015 and gain_vs_shuffled >= 0.0015
    value = f"{sequence_mae:.5f} / {memoryless_mae:.5f} / {shuffled_mae:.5f} / {gain_vs_memoryless:.5f}"
    return Result(
        "STP-001",
        "PASS" if passed else "FAIL",
        "sequence_mae / memoryless_mae / shuffled_mae / gain_vs_memoryless",
        value,
        "Temporal boundary effects are useful only if prior public trace improves next-stability prediction over memoryless and shuffled controls.",
    )


def write_outputs(results: list[Result], wpf_rows: list[dict[str, float | str]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["probe", "status", "metric", "value", "safe_read"])
        for result in results:
            writer.writerow([result.probe, result.status, result.metric, result.value, result.safe_read])
    with (OUT / "wpf_field_sets.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["field_set", "fields", "action_f1", "private_f1"])
        writer.writeheader()
        writer.writerows(wpf_rows)
    lines = [
        "# BSW-001 Boundary Sequence & Witness Footprint Probe",
        "",
        "Toy telemetry only. This tests witness footprint and public-trace sequence effects.",
        "",
        "| Probe | Status | Metric | Value | Safe Read |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in results:
        lines.append(f"| {result.probe} | {result.status} | {result.metric} | `{result.value}` | {result.safe_read} |")
    lines += ["", "## Witness Field Sets", "", "| Set | Action F1 | Private F1 | Fields |", "| --- | ---: | ---: | --- |"]
    for row in wpf_rows:
        lines.append(f"| {row['field_set']} | {float(row['action_f1']):.4f} | {float(row['private_f1']):.4f} | {row['fields']} |")
    lines += [
        "",
        "## Safe Read",
        "",
        "If WPF passes, witness should be treated as active quarantine, not a null trace.",
        "If STP passes, the next live handoff should include sequence-level telemetry, not isolated events only.",
        "",
        "Do not claim this proves GHP physics, consciousness, Markov blankets, split property, or literal thermodynamics.",
    ]
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    train = collect(TRAIN_SEEDS)
    test = collect(TEST_SEEDS)
    wpf, wpf_rows = wpf_probe(train, test)
    stp = stp_probe(train, test)
    write_outputs([wpf, stp], wpf_rows)
    print(f"BSW-001: {wpf.probe}:{wpf.status} / {stp.probe}:{stp.status}")


if __name__ == "__main__":
    main()
