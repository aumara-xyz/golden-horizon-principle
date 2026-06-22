#!/usr/bin/env python3
"""CAS-004 - Finite Observer-Depth Replication Probe.

Paper-focused GHP toy probe.

Question:
Does staged finite-depth public projection repeatedly outperform both raw
access and over-filtered access when reconstructing hidden write-relevant state?

This is toy telemetry only. It does not prove GHP physics, consciousness, or
observer-boundary selection by nature.
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


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_cascade_depth_replication_probe_outputs"

TRAIN_SEEDS = [1618, 2718, 3141, 4159]
TEST_SEEDS = [5772, 8111, 10946, 14142]
REGIMES = ["stable", "noisy", "drifty", "bursty"]
DEPTHS = [1, 2, 3, 4, 5, 6]


@dataclass
class ProbeResult:
    probe_id: str
    status: str
    metric: str
    value: str
    null_hypothesis: str
    safest_read: str
    falsifier: str


@dataclass
class MetricRow:
    regime: str
    policy: str
    split: str
    accuracy: float
    f1: float
    false_write_rate: float
    missed_write_rate: float
    auc_like: float
    leakage: float
    threshold: float
    compressed_bits: int


def stable_hash(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def compressed_bits(payload: object) -> int:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return len(zlib.compress(raw, level=9)) * 8


def binary_metrics(pred: list[int], truth: list[int]) -> tuple[float, float, float, float]:
    tp = sum(1 for p, t in zip(pred, truth) if p == 1 and t == 1)
    tn = sum(1 for p, t in zip(pred, truth) if p == 0 and t == 0)
    fp = sum(1 for p, t in zip(pred, truth) if p == 1 and t == 0)
    fn = sum(1 for p, t in zip(pred, truth) if p == 0 and t == 1)
    accuracy = (tp + tn) / len(truth) if truth else 0.0
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    false_write = fp / (fp + tn) if fp + tn else 0.0
    missed_write = fn / (fn + tp) if fn + tp else 0.0
    return accuracy, f1, false_write, missed_write


def auc_like(scores: list[float], truth: list[int]) -> float:
    positives = [score for score, label in zip(scores, truth) if label == 1]
    negatives = [score for score, label in zip(scores, truth) if label == 0]
    if not positives or not negatives:
        return 0.5
    wins = 0.0
    count = 0
    for p in positives[:500]:
        for n in negatives[:500]:
            count += 1
            if p > n:
                wins += 1.0
            elif p == n:
                wins += 0.5
    return wins / count if count else 0.5


def best_threshold(scores: list[float], truth: list[int]) -> float:
    candidates = sorted(set(scores))
    if len(candidates) > 180:
        candidates = [statistics.quantiles(scores, n=180)[i] for i in range(179)]
    best_t = candidates[0] if candidates else 0.0
    best_f1 = -1.0
    for threshold in candidates:
        pred = [1 if score >= threshold else 0 for score in scores]
        _acc, f1, _fw, _mw = binary_metrics(pred, truth)
        if f1 > best_f1:
            best_f1 = f1
            best_t = threshold
    return best_t


def train_linear_discriminant(rows: list[dict[str, float]], truth: list[int], features: list[str]) -> dict[str, float]:
    pos = [row for row, label in zip(rows, truth) if label == 1]
    neg = [row for row, label in zip(rows, truth) if label == 0]
    weights: dict[str, float] = {}
    for feature in features:
        pos_mean = statistics.fmean(row[feature] for row in pos) if pos else 0.0
        neg_mean = statistics.fmean(row[feature] for row in neg) if neg else 0.0
        vals = [row[feature] for row in rows]
        variance = statistics.pvariance(vals) if len(vals) > 1 else 1.0
        weights[feature] = (pos_mean - neg_mean) / (variance + 1e-6)
    return weights


def score_linear(row: dict[str, float], weights: dict[str, float]) -> float:
    return sum(row[key] * weight for key, weight in weights.items())


def regime_params(regime: str) -> dict[str, float]:
    return {
        "stable": {"noise": 0.16, "drift": 0.02, "burst": 0.00, "latent": 0.08},
        "noisy": {"noise": 0.28, "drift": 0.02, "burst": 0.00, "latent": 0.08},
        "drifty": {"noise": 0.18, "drift": 0.13, "burst": 0.00, "latent": 0.12},
        "bursty": {"noise": 0.20, "drift": 0.04, "burst": 0.32, "latent": 0.10},
    }[regime]


def cascade_dataset(seed: int, regime: str, n: int = 1800) -> tuple[list[dict[str, float]], list[int]]:
    """Generate a hidden write process with public projections at depths 1..6."""
    params = regime_params(regime)
    rng = random.Random(int(stable_hash([seed, regime]), 16))
    latent = rng.random()
    drift_state = rng.random()
    rows: list[dict[str, float]] = []
    truth: list[int] = []

    for step in range(n):
        burst = params["burst"] if step % 97 in range(0, 9) else 0.0
        external = rng.random()
        drift_state = 0.98 * drift_state + 0.02 * rng.random()
        latent = 0.92 * latent + 0.08 * rng.random()
        source = 0.62 * external + params["drift"] * drift_state + burst + rng.gauss(0.0, params["noise"])

        depth_values: dict[str, float] = {}
        previous = source
        for depth in DEPTHS:
            # Each layer denoises some prior signal but injects its own distortion.
            smoothing = 0.72 - (0.025 * min(depth, 5))
            local_noise = rng.gauss(0.0, params["noise"] * (0.72 + depth * 0.08))
            previous = smoothing * previous + (1 - smoothing) * rng.random() + local_noise
            depth_values[f"depth_{depth}"] = previous

        # Hidden truth uses an intermediate projection plus latent perturbation.
        # Depth 3 is structurally favored, but the detector must rediscover this
        # from public train/test behavior rather than being told.
        hidden_score = (
            0.28 * depth_values["depth_2"]
            + 0.62 * depth_values["depth_3"]
            - 0.18 * abs(depth_values["depth_5"] - depth_values["depth_3"])
            + params["latent"] * latent
            + rng.gauss(0.0, params["noise"] * 0.35)
        )
        write = 1 if hidden_score > 0.64 else 0
        row = {"external": external, "hidden_latent": latent, "source": source}
        row.update(depth_values)
        rows.append(row)
        truth.append(write)
    return rows, truth


def collect(regime: str, seeds: list[int]) -> tuple[list[dict[str, float]], list[int]]:
    rows: list[dict[str, float]] = []
    truth: list[int] = []
    for seed in seeds:
        seed_rows, seed_truth = cascade_dataset(seed, regime)
        rows.extend(seed_rows)
        truth.extend(seed_truth)
    return rows, truth


def policy_features(policy: str) -> tuple[list[str], float]:
    if policy.startswith("depth_"):
        depth = int(policy.split("_")[1])
        return [f"depth_{i}" for i in range(1, depth + 1)], 0.0
    if policy == "raw_external":
        return ["external"], 0.0
    if policy == "overdeep_6":
        return [f"depth_{i}" for i in DEPTHS], 0.0
    if policy == "leaky_depth_3":
        return ["depth_1", "depth_2", "depth_3", "hidden_latent"], 1.0
    if policy == "source_oracle":
        return ["source"], 1.0
    raise ValueError(policy)


def run_regime(regime: str) -> list[MetricRow]:
    train_rows, train_truth = collect(regime, TRAIN_SEEDS)
    test_rows, test_truth = collect(regime, TEST_SEEDS)
    policies = ["raw_external"] + [f"depth_{depth}" for depth in DEPTHS] + ["overdeep_6", "leaky_depth_3", "source_oracle"]
    metrics: list[MetricRow] = []

    for policy in policies:
        features, leakage = policy_features(policy)
        weights = train_linear_discriminant(train_rows, train_truth, features)
        train_scores = [score_linear(row, weights) for row in train_rows]
        threshold = best_threshold(train_scores, train_truth)
        for split, rows, truth in [("train", train_rows, train_truth), ("test", test_rows, test_truth)]:
            scores = [score_linear(row, weights) for row in rows]
            pred = [1 if score >= threshold else 0 for score in scores]
            accuracy, f1, false_write, missed_write = binary_metrics(pred, truth)
            metrics.append(
                MetricRow(
                    regime=regime,
                    policy=policy,
                    split=split,
                    accuracy=accuracy,
                    f1=f1,
                    false_write_rate=false_write,
                    missed_write_rate=missed_write,
                    auc_like=auc_like(scores, truth),
                    leakage=leakage,
                    threshold=threshold,
                    compressed_bits=compressed_bits({"policy": policy, "features": features, "threshold": threshold}),
                )
            )

    # Shuffled-label control for anti-circularity.
    shuffled_truth = train_truth[:]
    random.Random(int(stable_hash([regime, "shuffle"]), 16)).shuffle(shuffled_truth)
    features = ["depth_1", "depth_2", "depth_3"]
    weights = train_linear_discriminant(train_rows, shuffled_truth, features)
    train_scores = [score_linear(row, weights) for row in train_rows]
    threshold = best_threshold(train_scores, shuffled_truth)
    for split, rows, truth in [("train", train_rows, train_truth), ("test", test_rows, test_truth)]:
        scores = [score_linear(row, weights) for row in rows]
        pred = [1 if score >= threshold else 0 for score in scores]
        accuracy, f1, false_write, missed_write = binary_metrics(pred, truth)
        metrics.append(
            MetricRow(
                regime=regime,
                policy="shuffled_label_control",
                split=split,
                accuracy=accuracy,
                f1=f1,
                false_write_rate=false_write,
                missed_write_rate=missed_write,
                auc_like=auc_like(scores, truth),
                leakage=0.0,
                threshold=threshold,
                compressed_bits=compressed_bits({"policy": "shuffled_label_control", "threshold": threshold}),
            )
        )
    return metrics


def summarize(metrics: list[MetricRow]) -> tuple[ProbeResult, list[dict[str, object]]]:
    test_rows = [row for row in metrics if row.split == "test"]
    regime_summaries: list[dict[str, object]] = []
    clean_depth_winners: list[str] = []

    for regime in REGIMES:
        rows = [row for row in test_rows if row.regime == regime]
        by_policy = {row.policy: row for row in rows}
        clean_depths = [by_policy[f"depth_{depth}"] for depth in DEPTHS]
        best_clean = max(clean_depths, key=lambda row: row.f1)
        clean_depth_winners.append(best_clean.policy)
        depth_1 = by_policy["depth_1"]
        overdeep = by_policy["overdeep_6"]
        leaky = by_policy["leaky_depth_3"]
        shuffled = by_policy["shuffled_label_control"]
        regime_summaries.append(
            {
                "regime": regime,
                "best_clean_policy": best_clean.policy,
                "best_clean_f1": best_clean.f1,
                "depth_1_gap": best_clean.f1 - depth_1.f1,
                "overdeep_gap": best_clean.f1 - overdeep.f1,
                "leaky_gap": leaky.f1 - best_clean.f1,
                "shuffled_gap": best_clean.f1 - shuffled.f1,
                "best_clean_auc": best_clean.auc_like,
            }
        )

    stable_depth_3_count = sum(1 for winner in clean_depth_winners if winner == "depth_3")
    avg_best_f1 = statistics.fmean(float(row["best_clean_f1"]) for row in regime_summaries)
    avg_depth1_gap = statistics.fmean(float(row["depth_1_gap"]) for row in regime_summaries)
    avg_overdeep_gap = statistics.fmean(float(row["overdeep_gap"]) for row in regime_summaries)
    avg_leaky_gap = statistics.fmean(float(row["leaky_gap"]) for row in regime_summaries)
    avg_shuffled_gap = statistics.fmean(float(row["shuffled_gap"]) for row in regime_summaries)
    status = (
        "pass"
        if stable_depth_3_count >= 3
        and avg_best_f1 >= 0.74
        and avg_depth1_gap >= 0.10
        and avg_overdeep_gap >= 0.02
        and avg_leaky_gap <= 0.025
        and avg_shuffled_gap >= 0.30
        else "fail"
    )
    result = ProbeResult(
        probe_id="CAS-004",
        status=status,
        metric="depth3_regimes / avg_best_f1 / depth1_gap / overdeep_gap / leaky_gap / shuffled_gap",
        value=(
            f"{stable_depth_3_count}/{len(REGIMES)} / "
            f"{avg_best_f1:.4f} / {avg_depth1_gap:.4f} / "
            f"{avg_overdeep_gap:.4f} / {avg_leaky_gap:.4f} / {avg_shuffled_gap:.4f}"
        ),
        null_hypothesis="Finite staged projection has no stable optimal depth across hidden regimes once controls and private-leak checks are applied.",
        safest_read="If this passes, staged finite-depth projection is a paper-relevant computational analogue for finite-access observer boundaries: neither raw access nor over-filtering is best.",
        falsifier="Fail if the best depth is unstable, raw/overdeep access performs similarly, shuffled controls survive, or hidden leakage materially improves the result.",
    )
    return result, regime_summaries


def write_outputs(result: ProbeResult, metrics: list[MetricRow], regime_summaries: list[dict[str, object]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(MetricRow.__annotations__.keys()))
        writer.writeheader()
        for row in metrics:
            writer.writerow(row.__dict__)

    with (OUT / "regime_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "regime",
                "best_clean_policy",
                "best_clean_f1",
                "depth_1_gap",
                "overdeep_gap",
                "leaky_gap",
                "shuffled_gap",
                "best_clean_auc",
            ],
        )
        writer.writeheader()
        for row in regime_summaries:
            writer.writerow(row)

    report = [
        "# CAS-004 Finite Observer-Depth Replication Probe",
        "",
        "Toy telemetry only. This is not physics evidence, consciousness evidence, or proof that nature selects any observer depth.",
        "",
        "## Probe Result",
        "",
        "| Probe | Status | Metric | Value | Safest Read |",
        "| --- | --- | --- | --- | --- |",
        f"| {result.probe_id} | {result.status.upper()} | {result.metric} | `{result.value}` | {result.safest_read} |",
        "",
        "## Regime Summary",
        "",
        "| Regime | Best Clean Policy | Best F1 | Gap vs Depth 1 | Gap vs Overdeep | Leaky Gain | Gap vs Shuffled | AUC-like |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in regime_summaries:
        report.append(
            "| {regime} | {best} | {f1:.4f} | {d1:.4f} | {od:.4f} | {leaky:.4f} | {shuf:.4f} | {auc:.4f} |".format(
                regime=row["regime"],
                best=row["best_clean_policy"],
                f1=float(row["best_clean_f1"]),
                d1=float(row["depth_1_gap"]),
                od=float(row["overdeep_gap"]),
                leaky=float(row["leaky_gap"]),
                shuf=float(row["shuffled_gap"]),
                auc=float(row["best_clean_auc"]),
            )
        )

    report.extend(
        [
            "",
            "## Paper-Safe Read",
            "",
            "If promoted, the safe paper language is only that finite-depth staged projection can outperform both raw access and over-filtered access in a toy observer-boundary setting.",
            "",
            "Do not claim GHP physics, consciousness, observer-created reality, or a universal depth of three.",
        ]
    )
    (OUT / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    handoff = """# AUKORA / GHP HANDOFF - CAS-004

## Exact Invariant If Promoted

```text
Memory/write policies should test finite-depth staged projections against raw, over-filtered, shuffled-label, and leaky-oracle controls before promotion.
```

## Aukora Timing

Do not port this into Aukora unless the paper-lane read is accepted first.
"""
    (OUT / "AUKORA_HANDOFF.md").write_text(handoff, encoding="utf-8")


def main() -> None:
    metrics: list[MetricRow] = []
    for regime in REGIMES:
        metrics.extend(run_regime(regime))
    result, regime_summaries = summarize(metrics)
    write_outputs(result, metrics, regime_summaries)
    print(f"{result.probe_id}: {result.status} :: {result.value}")


if __name__ == "__main__":
    main()
