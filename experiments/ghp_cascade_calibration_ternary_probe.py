#!/usr/bin/env python3
"""CAS-006/009/010 - Cascade calibration and ternary action probe.

Follow-up to CAS-005.

CAS-005 suggested finite intermediate depth is informative, but binary F1 stayed
below promotion threshold. This battery tests whether the problem is bad signal
or bad action alphabet:

- CAS-006: calibration / early-warning audit for finite-depth scores.
- CAS-009: write / witness / release ternary action probe.
- CAS-010: paper-promotion gate for the finite-depth toy lane.

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
OUT = ROOT / "ghp_cascade_calibration_ternary_probe_outputs"
TRAIN_SEEDS = [1618, 2718, 3141, 4159, 5772]
TEST_SEEDS = [8111, 10946, 14142, 17320, 22360]
DEPTHS = [1, 2, 3, 4, 5, 6, 7]
REGIMES = ["stable", "noisy", "drifty", "bursty", "sparse", "dense", "volatile", "smooth"]


@dataclass
class ProbeResult:
    probe_id: str
    status: str
    metric: str
    value: str
    safest_read: str


@dataclass
class CalibrationRow:
    regime: str
    policy: str
    split: str
    auc_like: float
    top_decile_capture: float
    top_quintile_capture: float
    lift_top_decile: float
    leakage: float


@dataclass
class TernaryRow:
    regime: str
    policy: str
    split: str
    accuracy: float
    macro_f1: float
    write_f1: float
    witness_f1: float
    release_f1: float
    harmful_error_rate: float
    leakage: float


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
    for p in pos[:700]:
        for n in neg[:700]:
            count += 1
            if p > n:
                wins += 1.0
            elif p == n:
                wins += 0.5
    return wins / count if count else 0.5


def class_f1(pred: list[str], truth: list[str], label: str) -> float:
    tp = sum(1 for p, t in zip(pred, truth) if p == label and t == label)
    fp = sum(1 for p, t in zip(pred, truth) if p == label and t != label)
    fn = sum(1 for p, t in zip(pred, truth) if p != label and t == label)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return (2 * precision * recall / (precision + recall)) if precision + recall else 0.0


def ternary_metrics(pred: list[str], truth: list[str]) -> tuple[float, float, float, float, float, float]:
    accuracy = sum(int(p == t) for p, t in zip(pred, truth)) / len(truth)
    write_f1 = class_f1(pred, truth, "write")
    witness_f1 = class_f1(pred, truth, "witness")
    release_f1 = class_f1(pred, truth, "release")
    macro_f1 = statistics.fmean([write_f1, witness_f1, release_f1])
    harmful = sum(
        1
        for p, t in zip(pred, truth)
        if (p == "write" and t == "release") or (p == "release" and t == "write")
    ) / len(truth)
    return accuracy, macro_f1, write_f1, witness_f1, release_f1, harmful


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
            best_f1 = f1
            best_t = threshold
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


def generate(seed: int, regime: str, n: int = 2200) -> tuple[list[dict[str, float]], list[int], list[str]]:
    p = regime_params(regime)
    rng = random.Random(int(stable_hash([seed, regime, "cas006"]), 16))
    latent = rng.random()
    drift = rng.random()
    rows: list[dict[str, float]] = []
    write_truth: list[int] = []
    ternary_truth: list[str] = []
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

        hidden_score = (
            0.18 * row["depth_2"]
            + 0.36 * row["depth_3"]
            + 0.32 * row["depth_4"]
            - 0.18 * abs(row["depth_7"] - row["depth_4"])
            + 0.08 * latent
            + rng.gauss(0.0, p["noise"] * 0.30)
        )
        write_cut = p["threshold"]
        witness_cut = write_cut - (0.16 + p["noise"] * 0.08)
        if hidden_score > write_cut:
            label = "write"
        elif hidden_score > witness_cut:
            label = "witness"
        else:
            label = "release"
        write_truth.append(1 if label == "write" else 0)
        ternary_truth.append(label)
        rows.append(row)
    return rows, write_truth, ternary_truth


def collect(regime: str, seeds: list[int]) -> tuple[list[dict[str, float]], list[int], list[str]]:
    rows: list[dict[str, float]] = []
    write_truth: list[int] = []
    ternary_truth: list[str] = []
    for seed in seeds:
        seed_rows, seed_write, seed_ternary = generate(seed, regime)
        rows.extend(seed_rows)
        write_truth.extend(seed_write)
        ternary_truth.extend(seed_ternary)
    return rows, write_truth, ternary_truth


def policy_features(policy: str) -> tuple[list[str], float]:
    if policy == "raw_external":
        return ["external"], 0.0
    if policy == "finite_mid":
        return ["depth_1", "depth_2", "depth_3", "depth_4"], 0.0
    if policy == "overdeep":
        return [f"depth_{i}" for i in DEPTHS], 0.0
    if policy == "leaky_mid":
        return ["depth_1", "depth_2", "depth_3", "depth_4", "hidden_latent"], 1.0
    raise ValueError(policy)


def capture_metrics(scores: list[float], truth: list[int], fraction: float) -> tuple[float, float]:
    count = max(1, int(len(scores) * fraction))
    ranked = sorted(zip(scores, truth), key=lambda item: item[0], reverse=True)
    positives = sum(truth)
    captured = sum(label for _score, label in ranked[:count])
    base_rate = positives / len(truth) if truth else 0.0
    capture = captured / positives if positives else 0.0
    precision = captured / count
    lift = precision / base_rate if base_rate else 0.0
    return capture, lift


def train_ternary_thresholds(scores: list[float], labels: list[str]) -> tuple[float, float]:
    write_truth = [1 if label == "write" else 0 for label in labels]
    not_release_truth = [1 if label != "release" else 0 for label in labels]
    write_t = best_threshold(scores, write_truth)
    witness_t = best_threshold(scores, not_release_truth)
    if witness_t > write_t:
        witness_t, write_t = write_t, witness_t
    return witness_t, write_t


def apply_ternary(scores: list[float], witness_t: float, write_t: float) -> list[str]:
    labels: list[str] = []
    for value in scores:
        if value >= write_t:
            labels.append("write")
        elif value >= witness_t:
            labels.append("witness")
        else:
            labels.append("release")
    return labels


def run_regime(regime: str) -> tuple[list[CalibrationRow], list[TernaryRow]]:
    train_rows, train_write, train_ternary = collect(regime, TRAIN_SEEDS)
    test_rows, test_write, test_ternary = collect(regime, TEST_SEEDS)
    calibration_rows: list[CalibrationRow] = []
    ternary_rows: list[TernaryRow] = []
    for policy in ["raw_external", "finite_mid", "overdeep", "leaky_mid"]:
        features, leakage = policy_features(policy)
        weights = train_weights(train_rows, train_write, features)
        train_scores = [score(row, weights) for row in train_rows]
        witness_t, write_t = train_ternary_thresholds(train_scores, train_ternary)
        for split, rows, write_truth, ternary_truth in [
            ("train", train_rows, train_write, train_ternary),
            ("test", test_rows, test_write, test_ternary),
        ]:
            scores = [score(row, weights) for row in rows]
            top_decile_capture, lift_top_decile = capture_metrics(scores, write_truth, 0.10)
            top_quintile_capture, _lift_top_quintile = capture_metrics(scores, write_truth, 0.20)
            calibration_rows.append(
                CalibrationRow(
                    regime=regime,
                    policy=policy,
                    split=split,
                    auc_like=auc_like(scores, write_truth),
                    top_decile_capture=top_decile_capture,
                    top_quintile_capture=top_quintile_capture,
                    lift_top_decile=lift_top_decile,
                    leakage=leakage,
                )
            )
            pred = apply_ternary(scores, witness_t, write_t)
            accuracy, macro_f1, write_f1, witness_f1, release_f1, harmful = ternary_metrics(pred, ternary_truth)
            ternary_rows.append(
                TernaryRow(
                    regime=regime,
                    policy=policy,
                    split=split,
                    accuracy=accuracy,
                    macro_f1=macro_f1,
                    write_f1=write_f1,
                    witness_f1=witness_f1,
                    release_f1=release_f1,
                    harmful_error_rate=harmful,
                    leakage=leakage,
                )
            )

    # Shuffled-label control for finite_mid.
    shuffled_write = train_write[:]
    shuffled_ternary = train_ternary[:]
    rng = random.Random(int(stable_hash([regime, "shuffled"]), 16))
    rng.shuffle(shuffled_write)
    rng.shuffle(shuffled_ternary)
    features, leakage = policy_features("finite_mid")
    weights = train_weights(train_rows, shuffled_write, features)
    train_scores = [score(row, weights) for row in train_rows]
    witness_t, write_t = train_ternary_thresholds(train_scores, shuffled_ternary)
    for split, rows, write_truth, ternary_truth in [
        ("train", train_rows, train_write, train_ternary),
        ("test", test_rows, test_write, test_ternary),
    ]:
        scores = [score(row, weights) for row in rows]
        decile, lift = capture_metrics(scores, write_truth, 0.10)
        quintile, _ = capture_metrics(scores, write_truth, 0.20)
        calibration_rows.append(
            CalibrationRow(
                regime=regime,
                policy="shuffled_label_control",
                split=split,
                auc_like=auc_like(scores, write_truth),
                top_decile_capture=decile,
                top_quintile_capture=quintile,
                lift_top_decile=lift,
                leakage=0.0,
            )
        )
        pred = apply_ternary(scores, witness_t, write_t)
        accuracy, macro_f1, write_f1, witness_f1, release_f1, harmful = ternary_metrics(pred, ternary_truth)
        ternary_rows.append(
            TernaryRow(
                regime=regime,
                policy="shuffled_label_control",
                split=split,
                accuracy=accuracy,
                macro_f1=macro_f1,
                write_f1=write_f1,
                witness_f1=witness_f1,
                release_f1=release_f1,
                harmful_error_rate=harmful,
                leakage=0.0,
            )
        )
    return calibration_rows, ternary_rows


def summarize(calibration_rows: list[CalibrationRow], ternary_rows: list[TernaryRow]) -> tuple[list[ProbeResult], list[dict[str, object]]]:
    test_cal = [row for row in calibration_rows if row.split == "test"]
    test_ter = [row for row in ternary_rows if row.split == "test"]
    summary_rows: list[dict[str, object]] = []
    for regime in REGIMES:
        cal = {row.policy: row for row in test_cal if row.regime == regime}
        ter = {row.policy: row for row in test_ter if row.regime == regime}
        finite_cal = cal["finite_mid"]
        finite_ter = ter["finite_mid"]
        summary_rows.append(
            {
                "regime": regime,
                "finite_auc": finite_cal.auc_like,
                "raw_auc_gap": finite_cal.auc_like - cal["raw_external"].auc_like,
                "overdeep_auc_gap": finite_cal.auc_like - cal["overdeep"].auc_like,
                "shuffled_auc_gap": finite_cal.auc_like - cal["shuffled_label_control"].auc_like,
                "top_decile_capture": finite_cal.top_decile_capture,
                "lift_top_decile": finite_cal.lift_top_decile,
                "macro_f1": finite_ter.macro_f1,
                "write_f1": finite_ter.write_f1,
                "witness_f1": finite_ter.witness_f1,
                "release_f1": finite_ter.release_f1,
                "harmful_error_rate": finite_ter.harmful_error_rate,
                "leaky_macro_gain": ter["leaky_mid"].macro_f1 - finite_ter.macro_f1,
            }
        )

    avg_auc = statistics.fmean(float(row["finite_auc"]) for row in summary_rows)
    avg_raw_gap = statistics.fmean(float(row["raw_auc_gap"]) for row in summary_rows)
    avg_shuffled_gap = statistics.fmean(float(row["shuffled_auc_gap"]) for row in summary_rows)
    avg_decile_capture = statistics.fmean(float(row["top_decile_capture"]) for row in summary_rows)
    avg_macro_f1 = statistics.fmean(float(row["macro_f1"]) for row in summary_rows)
    avg_harmful = statistics.fmean(float(row["harmful_error_rate"]) for row in summary_rows)
    avg_leaky_gain = statistics.fmean(float(row["leaky_macro_gain"]) for row in summary_rows)

    cas006_status = (
        "pass"
        if avg_auc >= 0.90
        and avg_raw_gap >= 0.12
        and avg_shuffled_gap >= 0.25
        and avg_decile_capture >= 0.42
        and avg_leaky_gain <= 0.03
        else "fail"
    )
    cas009_status = (
        "pass"
        if avg_macro_f1 >= 0.62
        and avg_harmful <= 0.08
        and avg_leaky_gain <= 0.03
        else "fail"
    )
    cas010_status = "pass" if cas006_status == "pass" and cas009_status == "pass" else "blocked"
    results = [
        ProbeResult(
            probe_id="CAS-006",
            status=cas006_status,
            metric="avg_auc / raw_gap / shuffled_gap / top_decile_capture / leaky_gain",
            value=f"{avg_auc:.4f} / {avg_raw_gap:.4f} / {avg_shuffled_gap:.4f} / {avg_decile_capture:.4f} / {avg_leaky_gain:.4f}",
            safest_read="If this passes, finite-depth projection is a calibrated early-warning signal rather than just a weak binary classifier.",
        ),
        ProbeResult(
            probe_id="CAS-009",
            status=cas009_status,
            metric="avg_macro_f1 / harmful_error / leaky_gain",
            value=f"{avg_macro_f1:.4f} / {avg_harmful:.4f} / {avg_leaky_gain:.4f}",
            safest_read="If this passes, write/witness/release is a better action alphabet than binary write/no-write for finite-depth boundary output.",
        ),
        ProbeResult(
            probe_id="CAS-010",
            status=cas010_status,
            metric="calibration_pass / ternary_pass",
            value=f"{int(cas006_status == 'pass')} / {int(cas009_status == 'pass')}",
            safest_read="If this passes, the paper can receive one cautious toy-telemetry sentence about finite-depth projection and ternary boundary actions.",
        ),
    ]
    return results, summary_rows


def write_outputs(
    results: list[ProbeResult],
    summary_rows: list[dict[str, object]],
    calibration_rows: list[CalibrationRow],
    ternary_rows: list[TernaryRow],
) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "calibration_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(CalibrationRow.__annotations__.keys()))
        writer.writeheader()
        for row in calibration_rows:
            writer.writerow(row.__dict__)
    with (OUT / "ternary_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(TernaryRow.__annotations__.keys()))
        writer.writeheader()
        for row in ternary_rows:
            writer.writerow(row.__dict__)
    with (OUT / "regime_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        for row in summary_rows:
            writer.writerow(row)

    report = [
        "# CAS-006/009/010 Cascade Calibration And Ternary Probe",
        "",
        "Toy telemetry only. This tests whether finite-depth projection is better read as calibrated early-warning plus ternary write/witness/release rather than binary write/no-write.",
        "",
        "## Probe Results",
        "",
        "| Probe | Status | Metric | Value | Safest Read |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in results:
        report.append(
            f"| {result.probe_id} | {result.status.upper()} | {result.metric} | `{result.value}` | {result.safest_read} |"
        )
    report.extend(
        [
            "",
            "## Regime Summary",
            "",
            "| Regime | AUC | Raw Gap | Shuffled Gap | Top-Decile Capture | Decile Lift | Macro F1 | Write F1 | Witness F1 | Release F1 | Harmful Error | Leaky Gain |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in summary_rows:
        report.append(
            "| {regime} | {auc:.4f} | {raw:.4f} | {shuf:.4f} | {capture:.4f} | {lift:.4f} | {macro:.4f} | {write:.4f} | {witness:.4f} | {release:.4f} | {harm:.4f} | {leaky:.4f} |".format(
                regime=row["regime"],
                auc=float(row["finite_auc"]),
                raw=float(row["raw_auc_gap"]),
                shuf=float(row["shuffled_auc_gap"]),
                capture=float(row["top_decile_capture"]),
                lift=float(row["lift_top_decile"]),
                macro=float(row["macro_f1"]),
                write=float(row["write_f1"]),
                witness=float(row["witness_f1"]),
                release=float(row["release_f1"]),
                harm=float(row["harmful_error_rate"]),
                leaky=float(row["leaky_macro_gain"]),
            )
        )
    report.extend(
        [
            "",
            "## Paper-Safe Read",
            "",
            "If CAS-010 passes, the safe paper update is limited to a toy-telemetry note: finite-depth public projections may be better interpreted through calibrated early-warning and a write/witness/release alphabet than through binary write/no-write scoring.",
            "",
            "No physics proof, consciousness proof, universal depth, or observer-created-reality claim follows.",
        ]
    )
    (OUT / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> None:
    calibration_rows: list[CalibrationRow] = []
    ternary_rows: list[TernaryRow] = []
    for regime in REGIMES:
        cal, ter = run_regime(regime)
        calibration_rows.extend(cal)
        ternary_rows.extend(ter)
    results, summary_rows = summarize(calibration_rows, ternary_rows)
    write_outputs(results, summary_rows, calibration_rows, ternary_rows)
    for result in results:
        print(f"{result.probe_id}: {result.status} :: {result.value}")


if __name__ == "__main__":
    main()
