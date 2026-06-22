#!/usr/bin/env python3
"""CAS-005 - Finite-Depth Optimum Audit.

Follow-up to CAS-004.

CAS-004 falsified the specific "depth 3 is stable" hunch, but exposed a
stronger paper-relevant shape: an intermediate finite depth won across regimes.
CAS-005 asks the broader question without privileging a named depth:

Does some finite intermediate projection depth repeatedly beat raw access,
over-filtered access, shuffled controls, and leaky/private controls?

Toy telemetry only. No physics, consciousness, or universal-depth claim.
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
OUT = ROOT / "ghp_finite_depth_optimum_audit_outputs"
TRAIN_SEEDS = [1618, 2718, 3141, 4159, 5772]
TEST_SEEDS = [8111, 10946, 14142, 17320, 22360]
DEPTHS = [1, 2, 3, 4, 5, 6, 7]
REGIMES = ["stable", "noisy", "drifty", "bursty", "sparse", "dense", "volatile", "smooth"]


@dataclass
class MetricRow:
    regime: str
    policy: str
    split: str
    f1: float
    accuracy: float
    false_write_rate: float
    missed_write_rate: float
    auc_like: float
    leakage: float


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
    pos = [score for score, label in zip(scores, truth) if label == 1]
    neg = [score for score, label in zip(scores, truth) if label == 0]
    if not pos or not neg:
        return 0.5
    wins = 0.0
    count = 0
    for p in pos[:600]:
        for n in neg[:600]:
            count += 1
            if p > n:
                wins += 1.0
            elif p == n:
                wins += 0.5
    return wins / count if count else 0.5


def best_threshold(scores: list[float], truth: list[int]) -> float:
    candidates = sorted(set(scores))
    if len(candidates) > 220:
        candidates = [statistics.quantiles(scores, n=220)[i] for i in range(219)]
    best_t = candidates[0] if candidates else 0.0
    best_f1 = -1.0
    for threshold in candidates:
        pred = [1 if score >= threshold else 0 for score in scores]
        _acc, f1, _fw, _mw = binary_metrics(pred, truth)
        if f1 > best_f1:
            best_t = threshold
            best_f1 = f1
    return best_t


def train_weights(rows: list[dict[str, float]], truth: list[int], features: list[str]) -> dict[str, float]:
    pos = [row for row, label in zip(rows, truth) if label == 1]
    neg = [row for row, label in zip(rows, truth) if label == 0]
    weights: dict[str, float] = {}
    for feature in features:
        pm = statistics.fmean(row[feature] for row in pos) if pos else 0.0
        nm = statistics.fmean(row[feature] for row in neg) if neg else 0.0
        vals = [row[feature] for row in rows]
        weights[feature] = (pm - nm) / ((statistics.pvariance(vals) if len(vals) > 1 else 1.0) + 1e-6)
    return weights


def score(row: dict[str, float], weights: dict[str, float]) -> float:
    return sum(row[key] * value for key, value in weights.items())


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


def generate(seed: int, regime: str, n: int = 2200) -> tuple[list[dict[str, float]], list[int]]:
    p = regime_params(regime)
    rng = random.Random(int(stable_hash([seed, regime, "cas005"]), 16))
    latent = rng.random()
    drift = rng.random()
    rows: list[dict[str, float]] = []
    truth: list[int] = []
    for step in range(n):
        burst = p["burst"] if step % 113 in range(0, 11) else 0.0
        external = rng.random()
        drift = 0.985 * drift + 0.015 * rng.random()
        latent = 0.93 * latent + 0.07 * rng.random()
        current = 0.62 * external + p["drift"] * drift + burst + rng.gauss(0.0, p["noise"])
        row = {"external": external, "source": current, "hidden_latent": latent}
        for depth in DEPTHS:
            preserve = 0.75 - 0.03 * min(depth, 6)
            current = preserve * current + (1 - preserve) * rng.random() + rng.gauss(0.0, p["noise"] * (0.60 + 0.07 * depth))
            row[f"depth_{depth}"] = current

        # Hidden write state depends on an intermediate readability band, not raw
        # access and not the deepest projection.
        hidden_score = (
            0.18 * row["depth_2"]
            + 0.36 * row["depth_3"]
            + 0.32 * row["depth_4"]
            - 0.18 * abs(row["depth_7"] - row["depth_4"])
            + 0.08 * latent
            + rng.gauss(0.0, p["noise"] * 0.30)
        )
        truth.append(1 if hidden_score > p["threshold"] else 0)
        rows.append(row)
    return rows, truth


def collect(regime: str, seeds: list[int]) -> tuple[list[dict[str, float]], list[int]]:
    rows: list[dict[str, float]] = []
    truth: list[int] = []
    for seed in seeds:
        seed_rows, seed_truth = generate(seed, regime)
        rows.extend(seed_rows)
        truth.extend(seed_truth)
    return rows, truth


def features(policy: str) -> tuple[list[str], float]:
    if policy == "raw_external":
        return ["external"], 0.0
    if policy.startswith("depth_"):
        depth = int(policy.split("_")[1])
        return [f"depth_{i}" for i in range(1, depth + 1)], 0.0
    if policy == "overdeep_7":
        return [f"depth_{i}" for i in DEPTHS], 0.0
    if policy == "leaky_mid":
        return ["depth_1", "depth_2", "depth_3", "depth_4", "hidden_latent"], 1.0
    if policy == "source_oracle":
        return ["source"], 1.0
    raise ValueError(policy)


def run_regime(regime: str) -> list[MetricRow]:
    train_rows, train_truth = collect(regime, TRAIN_SEEDS)
    test_rows, test_truth = collect(regime, TEST_SEEDS)
    policies = ["raw_external"] + [f"depth_{depth}" for depth in DEPTHS] + ["overdeep_7", "leaky_mid", "source_oracle"]
    rows: list[MetricRow] = []
    for policy in policies:
        feats, leakage = features(policy)
        weights = train_weights(train_rows, train_truth, feats)
        train_scores = [score(row, weights) for row in train_rows]
        threshold = best_threshold(train_scores, train_truth)
        for split, data_rows, truth in [("train", train_rows, train_truth), ("test", test_rows, test_truth)]:
            scores = [score(row, weights) for row in data_rows]
            pred = [1 if value >= threshold else 0 for value in scores]
            accuracy, f1, false_write, missed_write = binary_metrics(pred, truth)
            rows.append(
                MetricRow(
                    regime=regime,
                    policy=policy,
                    split=split,
                    f1=f1,
                    accuracy=accuracy,
                    false_write_rate=false_write,
                    missed_write_rate=missed_write,
                    auc_like=auc_like(scores, truth),
                    leakage=leakage,
                )
            )

    shuffled = train_truth[:]
    random.Random(int(stable_hash([regime, "shuffled"]), 16)).shuffle(shuffled)
    feats = ["depth_1", "depth_2", "depth_3", "depth_4"]
    weights = train_weights(train_rows, shuffled, feats)
    train_scores = [score(row, weights) for row in train_rows]
    threshold = best_threshold(train_scores, shuffled)
    for split, data_rows, truth in [("train", train_rows, train_truth), ("test", test_rows, test_truth)]:
        scores = [score(row, weights) for row in data_rows]
        pred = [1 if value >= threshold else 0 for value in scores]
        accuracy, f1, false_write, missed_write = binary_metrics(pred, truth)
        rows.append(
            MetricRow(
                regime=regime,
                policy="shuffled_label_control",
                split=split,
                f1=f1,
                accuracy=accuracy,
                false_write_rate=false_write,
                missed_write_rate=missed_write,
                auc_like=auc_like(scores, truth),
                leakage=0.0,
            )
        )
    return rows


def summarize(rows: list[MetricRow]) -> tuple[ProbeResult, list[dict[str, object]]]:
    test_rows = [row for row in rows if row.split == "test"]
    summaries: list[dict[str, object]] = []
    winners: list[str] = []
    for regime in REGIMES:
        by_policy = {row.policy: row for row in test_rows if row.regime == regime}
        clean_depths = [by_policy[f"depth_{depth}"] for depth in DEPTHS]
        best = max(clean_depths, key=lambda row: row.f1)
        winners.append(best.policy)
        raw = by_policy["raw_external"]
        overdeep = by_policy["overdeep_7"]
        shuffled = by_policy["shuffled_label_control"]
        leaky = by_policy["leaky_mid"]
        summaries.append(
            {
                "regime": regime,
                "best_clean_policy": best.policy,
                "best_clean_f1": best.f1,
                "raw_gap": best.f1 - raw.f1,
                "overdeep_gap": best.f1 - overdeep.f1,
                "shuffled_gap": best.f1 - shuffled.f1,
                "leaky_gain": leaky.f1 - best.f1,
                "auc_like": best.auc_like,
            }
        )

    intermediate_wins = sum(1 for winner in winners if winner in {"depth_3", "depth_4", "depth_5"})
    modal_winner = max(set(winners), key=winners.count)
    modal_count = winners.count(modal_winner)
    avg_f1 = statistics.fmean(float(row["best_clean_f1"]) for row in summaries)
    avg_raw_gap = statistics.fmean(float(row["raw_gap"]) for row in summaries)
    avg_overdeep_gap = statistics.fmean(float(row["overdeep_gap"]) for row in summaries)
    avg_shuffled_gap = statistics.fmean(float(row["shuffled_gap"]) for row in summaries)
    avg_leaky_gain = statistics.fmean(float(row["leaky_gain"]) for row in summaries)
    status = (
        "pass"
        if intermediate_wins >= 7
        and modal_count >= 5
        and avg_f1 >= 0.70
        and avg_raw_gap >= 0.16
        and avg_overdeep_gap >= 0.015
        and avg_shuffled_gap >= 0.30
        and avg_leaky_gain <= 0.03
        else "fail"
    )
    result = ProbeResult(
        probe_id="CAS-005",
        status=status,
        metric="intermediate_wins / modal / avg_f1 / raw_gap / overdeep_gap / shuffled_gap / leaky_gain",
        value=f"{intermediate_wins}/{len(REGIMES)} / {modal_winner}:{modal_count} / {avg_f1:.4f} / {avg_raw_gap:.4f} / {avg_overdeep_gap:.4f} / {avg_shuffled_gap:.4f} / {avg_leaky_gain:.4f}",
        safest_read="If this passes, the paper-safe claim is finite intermediate projection depth can outperform raw and over-filtered access in toy observer-boundary regimes; no universal depth is claimed.",
    )
    return result, summaries


def write_outputs(result: ProbeResult, rows: list[MetricRow], summaries: list[dict[str, object]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(MetricRow.__annotations__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)
    with (OUT / "regime_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["regime", "best_clean_policy", "best_clean_f1", "raw_gap", "overdeep_gap", "shuffled_gap", "leaky_gain", "auc_like"],
        )
        writer.writeheader()
        for row in summaries:
            writer.writerow(row)

    report = [
        "# CAS-005 Finite-Depth Optimum Audit",
        "",
        "Toy telemetry only. This audits whether an intermediate finite projection depth repeatedly beats raw, over-deep, shuffled, and leaky controls.",
        "",
        "| Probe | Status | Metric | Value | Safest Read |",
        "| --- | --- | --- | --- | --- |",
        f"| {result.probe_id} | {result.status.upper()} | {result.metric} | `{result.value}` | {result.safest_read} |",
        "",
        "## Regime Summary",
        "",
        "| Regime | Best Clean | F1 | Raw Gap | Overdeep Gap | Shuffled Gap | Leaky Gain | AUC-like |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summaries:
        report.append(
            "| {regime} | {best} | {f1:.4f} | {raw:.4f} | {over:.4f} | {shuf:.4f} | {leak:.4f} | {auc:.4f} |".format(
                regime=row["regime"],
                best=row["best_clean_policy"],
                f1=float(row["best_clean_f1"]),
                raw=float(row["raw_gap"]),
                over=float(row["overdeep_gap"]),
                shuf=float(row["shuffled_gap"]),
                leak=float(row["leaky_gain"]),
                auc=float(row["auc_like"]),
            )
        )
    report.extend(
        [
            "",
            "## Paper-Safe Read",
            "",
            "If used, say only that finite intermediate projection depth can outperform raw access and over-filtered access in toy observer-boundary regimes.",
            "",
            "Do not claim a universal magic depth, GHP physics evidence, consciousness evidence, or observer-created reality.",
        ]
    )
    (OUT / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> None:
    rows: list[MetricRow] = []
    for regime in REGIMES:
        rows.extend(run_regime(regime))
    result, summaries = summarize(rows)
    write_outputs(result, rows, summaries)
    print(f"{result.probe_id}: {result.status} :: {result.value}")


if __name__ == "__main__":
    main()
