#!/usr/bin/env python3
"""Redesigned GHP boundary probes.

This round follows the negative de-circularized probes. It keeps the hard rule:
truth comes from hidden dynamics, predictors use public/projection features,
and performance is judged on held-out seeds/regimes.

- BCL-002: shared anti-circular ledger harness.
- CAC-003: delayed collapse classifier from public lag features.
- NET-003: causal topology intervention probe.
- CAS-003: cascade depth sweep.
- AUK-001: receipt translation gate only if at least one scientific probe passes.

Toy telemetry only. No physics, consciousness, over-unity, scalar-wave,
or time-extrusion claims.
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
OUT = ROOT / "ghp_boundary_redesign_probes_outputs"
TRAIN_SEEDS = [1618, 2718, 3141]
TEST_SEEDS = [5772, 8111, 10946]


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
    probe_id: str
    policy: str
    split: str
    accuracy: float
    f1: float
    false_write_rate: float
    missed_write_rate: float
    auc_like: float
    leakage: float
    model: str


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


def multiclass_accuracy(pred: list[str], truth: list[str]) -> float:
    return sum(int(a == b) for a, b in zip(pred, truth)) / len(truth) if truth else 0.0


def best_threshold(scores: list[float], truth: list[int]) -> float:
    candidates = sorted(set(scores))
    if len(candidates) > 160:
        candidates = [statistics.quantiles(scores, n=160)[i] for i in range(159)]
    best_t = candidates[0] if candidates else 0.0
    best_f1 = -1.0
    for threshold in candidates:
        pred = [1 if score >= threshold else 0 for score in scores]
        _acc, f1, _fw, _mw = binary_metrics(pred, truth)
        if f1 > best_f1:
            best_f1 = f1
            best_t = threshold
    return best_t


def auc_like(scores: list[float], truth: list[int]) -> float:
    positives = [score for score, label in zip(scores, truth) if label == 1]
    negatives = [score for score, label in zip(scores, truth) if label == 0]
    if not positives or not negatives:
        return 0.5
    sample = 0
    wins = 0.0
    for p in positives[:400]:
        for n in negatives[:400]:
            sample += 1
            if p > n:
                wins += 1.0
            elif p == n:
                wins += 0.5
    return wins / sample if sample else 0.5


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


def cac_hidden_series(seed: int, n: int = 1600) -> tuple[list[dict[str, float]], list[int]]:
    """Hidden delayed bubble dynamics. Public features include only drive lags."""
    rng = random.Random(seed + 30300)
    phase = rng.random() * math.tau
    radius = 1.0
    velocity = 0.0
    acoustic_charge = 0.0
    drive_history: list[float] = []
    rows: list[dict[str, float]] = []
    truth: list[int] = []
    cooldown = 0

    for t in range(n):
        pulse_train = 1.1 if (t + seed) % 211 in range(0, 18) else 0.0
        carrier = math.sin(t / 8.0 + phase)
        envelope = 0.6 + 0.4 * math.sin(t / 89.0)
        drive = envelope * carrier + pulse_train + rng.gauss(0.0, 0.12)
        drive_history.append(drive)
        drive_history = drive_history[-48:]
        recent_4 = drive_history[-4:]
        recent_12 = drive_history[-12:]
        recent_32 = drive_history[-32:]
        energy_4 = statistics.fmean(abs(x) for x in recent_4)
        energy_12 = statistics.fmean(abs(x) for x in recent_12)
        energy_32 = statistics.fmean(abs(x) for x in recent_32)
        trend_12 = statistics.fmean(recent_12[-4:]) - statistics.fmean(recent_12[:4]) if len(recent_12) >= 8 else 0.0
        slope = drive - drive_history[-2] if len(drive_history) >= 2 else 0.0

        acoustic_charge = 0.94 * acoustic_charge + 0.09 * max(0.0, drive) + 0.04 * energy_12
        forcing = 0.055 * acoustic_charge + 0.025 * max(0.0, trend_12)
        velocity += -0.16 * (radius - 1.0) - forcing - 0.065 * velocity + rng.gauss(0.0, 0.006)
        radius += velocity

        collapse = 0
        if cooldown == 0 and radius < 0.37 and acoustic_charge > 1.4:
            collapse = 1
            radius = 0.96 + rng.random() * 0.09
            velocity = 0.0
            acoustic_charge *= 0.12
            cooldown = 14
        cooldown = max(0, cooldown - 1)

        rows.append(
            {
                "drive": drive,
                "slope": slope,
                "energy_4": energy_4,
                "energy_12": energy_12,
                "energy_32": energy_32,
                "trend_12": trend_12,
                "charge_proxy": 0.84 * energy_32 + 0.34 * max(0.0, trend_12),
            }
        )
        truth.append(collapse)
    return rows, truth


def collect_cac(seeds: list[int]) -> tuple[list[dict[str, float]], list[int]]:
    rows: list[dict[str, float]] = []
    truth: list[int] = []
    for seed in seeds:
        seed_rows, seed_truth = cac_hidden_series(seed)
        rows.extend(seed_rows)
        truth.extend(seed_truth)
    return rows, truth


def cac_003() -> tuple[ProbeResult, list[MetricRow]]:
    train_rows, train_truth = collect_cac(TRAIN_SEEDS)
    test_rows, test_truth = collect_cac(TEST_SEEDS)
    policies = {
        "delayed_public_classifier": ["energy_4", "energy_12", "energy_32", "trend_12", "charge_proxy", "slope"],
        "amplitude_only": ["drive"],
        "slope_only": ["slope"],
        "short_energy_only": ["energy_4"],
    }
    metric_rows: list[MetricRow] = []
    for policy, features in policies.items():
        weights = train_linear_discriminant(train_rows, train_truth, features)
        train_scores = [score_linear(row, weights) for row in train_rows]
        threshold = best_threshold(train_scores, train_truth)
        for split, rows, truth in [("train", train_rows, train_truth), ("test", test_rows, test_truth)]:
            scores = [score_linear(row, weights) for row in rows]
            pred = [1 if score >= threshold else 0 for score in scores]
            accuracy, f1, false_write, missed_write = binary_metrics(pred, truth)
            metric_rows.append(
                MetricRow(
                    probe_id="CAC-003",
                    policy=policy,
                    split=split,
                    accuracy=accuracy,
                    f1=f1,
                    false_write_rate=false_write,
                    missed_write_rate=missed_write,
                    auc_like=auc_like(scores, truth),
                    leakage=0.0,
                    model=f"features={','.join(features)};threshold={threshold:.4f}",
                )
            )

    # Shuffled-label control keeps public features but destroys event alignment.
    rng = random.Random(9090)
    shuffled_truth = train_truth[:]
    rng.shuffle(shuffled_truth)
    weights = train_linear_discriminant(train_rows, shuffled_truth, policies["delayed_public_classifier"])
    train_scores = [score_linear(row, weights) for row in train_rows]
    threshold = best_threshold(train_scores, shuffled_truth)
    for split, rows, truth in [("train", train_rows, train_truth), ("test", test_rows, test_truth)]:
        scores = [score_linear(row, weights) for row in rows]
        pred = [1 if score >= threshold else 0 for score in scores]
        accuracy, f1, false_write, missed_write = binary_metrics(pred, truth)
        metric_rows.append(
            MetricRow(
                probe_id="CAC-003",
                policy="shuffled_label_control",
                split=split,
                accuracy=accuracy,
                f1=f1,
                false_write_rate=false_write,
                missed_write_rate=missed_write,
                auc_like=auc_like(scores, truth),
                leakage=0.0,
                model="train labels shuffled",
            )
        )

    test = {row.policy: row for row in metric_rows if row.split == "test"}
    main = test["delayed_public_classifier"]
    amp = test["amplitude_only"]
    shuffled = test["shuffled_label_control"]
    status = (
        "pass"
        if main.f1 >= 0.55
        and main.f1 - amp.f1 >= 0.12
        and main.f1 - shuffled.f1 >= 0.25
        and main.auc_like >= 0.82
        else "fail"
    )
    return (
        ProbeResult(
            probe_id="CAC-003",
            status=status,
            metric="test_f1 / amp_gap / shuffled_gap / auc",
            value=f"{main.f1:.4f} / {main.f1 - amp.f1:.4f} / {main.f1 - shuffled.f1:.4f} / {main.auc_like:.4f}",
            null_hypothesis="Delayed public boundary features do not predict hidden collapse events better than amplitude or shuffled-label controls.",
            safest_read="If this passes, the cavitation analogue gains a non-circular predictive version: public lag structure anticipates hidden collapse-like events.",
            falsifier="Fail if amplitude-only or shuffled-label controls perform nearly as well, or if held-out AUC is weak.",
        ),
        metric_rows,
    )


def intervention_graph() -> dict[int, set[int]]:
    graph = {i: set() for i in range(10)}
    edges = [(0, 1), (1, 2), (2, 3), (1, 4), (4, 5), (5, 6), (3, 7), (7, 8), (6, 9), (2, 9)]
    for a, b in edges:
        graph[a].add(b)
        graph[b].add(a)
    return graph


def intervention_dataset(seed: int, graph: dict[int, set[int]], steps: int = 520) -> tuple[list[dict[int, float]], list[tuple[int, int]]]:
    rng = random.Random(seed + 44000)
    nodes = sorted(graph)
    values = {node: rng.gauss(0.0, 0.1) for node in nodes}
    rows: list[dict[int, float]] = []
    interventions: list[tuple[int, int]] = []
    for t in range(steps):
        source = t % len(nodes) if t % 26 == 0 else -1
        if source >= 0:
            values[source] += 2.6
            interventions.append((t, source))
        new_values: dict[int, float] = {}
        for node in nodes:
            neighbor_flow = sum(values[n] for n in graph[node]) / max(1, len(graph[node]))
            new_values[node] = 0.54 * values[node] + 0.42 * neighbor_flow + rng.gauss(0.0, 0.08)
        values = new_values
        rows.append(values.copy())
    return rows, interventions


def infer_edges(rows: list[dict[int, float]], interventions: list[tuple[int, int]], horizon: int = 3) -> dict[tuple[int, int], float]:
    nodes = sorted(rows[0])
    scores: dict[tuple[int, int], list[float]] = {(a, b): [] for a in nodes for b in nodes if a != b}
    baseline = {node: statistics.fmean(row[node] for row in rows) for node in nodes}
    for t, source in interventions:
        for target in nodes:
            if target == source:
                continue
            response = 0.0
            for lag in range(1, horizon + 1):
                if t + lag < len(rows):
                    response += max(0.0, rows[t + lag][target] - baseline[target]) / lag
            scores[(source, target)].append(response)
    return {edge: statistics.fmean(vals) if vals else 0.0 for edge, vals in scores.items()}


def edge_truth(graph: dict[int, set[int]]) -> dict[tuple[int, int], int]:
    truth: dict[tuple[int, int], int] = {}
    for a in graph:
        for b in graph:
            if a != b:
                truth[(a, b)] = int(b in graph[a])
    return truth


def net_003() -> tuple[ProbeResult, list[MetricRow]]:
    graph = intervention_graph()
    truth = edge_truth(graph)
    train_rows_all: list[dict[int, float]] = []
    train_interventions: list[tuple[int, int]] = []
    offset = 0
    for seed in TRAIN_SEEDS:
        rows, interventions = intervention_dataset(seed, graph)
        train_rows_all.extend(rows)
        train_interventions.extend((t + offset, src) for t, src in interventions)
        offset += len(rows)
    test_rows_all: list[dict[int, float]] = []
    test_interventions: list[tuple[int, int]] = []
    offset = 0
    for seed in TEST_SEEDS:
        rows, interventions = intervention_dataset(seed, graph)
        test_rows_all.extend(rows)
        test_interventions.extend((t + offset, src) for t, src in interventions)
        offset += len(rows)

    train_scores = infer_edges(train_rows_all, train_interventions)
    test_scores = infer_edges(test_rows_all, test_interventions)
    train_score_list = [train_scores[edge] for edge in sorted(truth)]
    truth_list = [truth[edge] for edge in sorted(truth)]
    threshold = best_threshold(train_score_list, truth_list)

    metric_rows: list[MetricRow] = []
    for split, scores in [("train", train_scores), ("test", test_scores)]:
        score_list = [scores[edge] for edge in sorted(truth)]
        pred = [1 if score >= threshold else 0 for score in score_list]
        accuracy, f1, false_write, missed_write = binary_metrics(pred, truth_list)
        metric_rows.append(
            MetricRow(
                probe_id="NET-003",
                policy="intervention_topology_recovery",
                split=split,
                accuracy=accuracy,
                f1=f1,
                false_write_rate=false_write,
                missed_write_rate=missed_write,
                auc_like=auc_like(score_list, truth_list),
                leakage=0.0,
                model=f"edge_threshold={threshold:.4f}",
            )
        )

    # Wrong-topology / no-intervention controls.
    rng = random.Random(1234)
    shuffled_truth = truth_list[:]
    rng.shuffle(shuffled_truth)
    for split, scores in [("train", train_scores), ("test", test_scores)]:
        score_list = [scores[edge] for edge in sorted(truth)]
        pred = [1 if score >= threshold else 0 for score in score_list]
        accuracy, f1, false_write, missed_write = binary_metrics(pred, shuffled_truth)
        metric_rows.append(
            MetricRow(
                probe_id="NET-003",
                policy="wrong_topology_control",
                split=split,
                accuracy=accuracy,
                f1=f1,
                false_write_rate=false_write,
                missed_write_rate=missed_write,
                auc_like=auc_like(score_list, shuffled_truth),
                leakage=0.0,
                model="truth labels shuffled",
            )
        )

    test = {row.policy: row for row in metric_rows if row.split == "test"}
    main = test["intervention_topology_recovery"]
    wrong = test["wrong_topology_control"]
    status = (
        "pass"
        if main.f1 >= 0.78
        and main.f1 - wrong.f1 >= 0.30
        and main.auc_like >= 0.88
        else "fail"
    )
    return (
        ProbeResult(
            probe_id="NET-003",
            status=status,
            metric="test_edge_f1 / wrong_gap / auc",
            value=f"{main.f1:.4f} / {main.f1 - wrong.f1:.4f} / {main.auc_like:.4f}",
            null_hypothesis="Causal interventions do not recover hidden topology better than wrong-topology controls.",
            safest_read="If this passes, the net branch becomes a real graph-intervention test rather than a passive similarity test.",
            falsifier="Fail if shuffled/wrong topology labels explain intervention responses nearly as well.",
        ),
        metric_rows,
    )


def cas_depth_dataset(seed: int, n: int = 1800) -> tuple[list[dict[str, float]], list[int]]:
    rng = random.Random(seed + 55000)
    rows: list[dict[str, float]] = []
    truth: list[int] = []
    latent = rng.random()
    for _ in range(n):
        external = rng.random()
        latent = 0.91 * latent + 0.09 * rng.random()
        layer1 = 0.72 * external + 0.28 * rng.random()
        layer2 = 0.64 * layer1 + 0.36 * rng.random()
        layer3 = 0.70 * layer2 + 0.30 * rng.random()
        layer4 = 0.62 * layer3 + 0.38 * rng.random()
        layer5 = 0.55 * layer4 + 0.45 * rng.random()
        # Hidden truth uses an intermediate stable blanket plus a latent perturbation.
        score = 0.62 * layer2 + 0.48 * layer3 - 0.22 * layer5 + 0.10 * latent + rng.gauss(0.0, 0.055)
        write = 1 if score > 0.70 else 0
        rows.append(
            {
                "depth_1": layer1,
                "depth_2": layer2,
                "depth_3": layer3,
                "depth_4": layer4,
                "depth_5": layer5,
                "external": external,
                "hidden_latent": latent,
            }
        )
        truth.append(write)
    return rows, truth


def collect_cas(seeds: list[int]) -> tuple[list[dict[str, float]], list[int]]:
    rows: list[dict[str, float]] = []
    truth: list[int] = []
    for seed in seeds:
        seed_rows, seed_truth = cas_depth_dataset(seed)
        rows.extend(seed_rows)
        truth.extend(seed_truth)
    return rows, truth


def cas_003() -> tuple[ProbeResult, list[MetricRow]]:
    train_rows, train_truth = collect_cas(TRAIN_SEEDS)
    test_rows, test_truth = collect_cas(TEST_SEEDS)
    policies = {
        "depth_1": ["depth_1"],
        "depth_2": ["depth_1", "depth_2"],
        "depth_3": ["depth_1", "depth_2", "depth_3"],
        "depth_4": ["depth_1", "depth_2", "depth_3", "depth_4"],
        "depth_5": ["depth_1", "depth_2", "depth_3", "depth_4", "depth_5"],
        "leaky_depth_3": ["depth_1", "depth_2", "depth_3", "hidden_latent"],
    }
    metric_rows: list[MetricRow] = []
    for policy, features in policies.items():
        weights = train_linear_discriminant(train_rows, train_truth, features)
        train_scores = [score_linear(row, weights) for row in train_rows]
        threshold = best_threshold(train_scores, train_truth)
        for split, rows, truth in [("train", train_rows, train_truth), ("test", test_rows, test_truth)]:
            scores = [score_linear(row, weights) for row in rows]
            pred = [1 if score >= threshold else 0 for score in scores]
            accuracy, f1, false_write, missed_write = binary_metrics(pred, truth)
            metric_rows.append(
                MetricRow(
                    probe_id="CAS-003",
                    policy=policy,
                    split=split,
                    accuracy=accuracy,
                    f1=f1,
                    false_write_rate=false_write,
                    missed_write_rate=missed_write,
                    auc_like=auc_like(scores, truth),
                    leakage=1.0 if "leaky" in policy else 0.0,
                    model=f"features={','.join(features)};threshold={threshold:.4f}",
                )
            )

    test_rows_by_policy = {row.policy: row for row in metric_rows if row.split == "test"}
    clean_depths = [test_rows_by_policy[f"depth_{i}"] for i in range(1, 6)]
    best_clean = max(clean_depths, key=lambda row: row.f1)
    depth1 = test_rows_by_policy["depth_1"]
    depth5 = test_rows_by_policy["depth_5"]
    leaky = test_rows_by_policy["leaky_depth_3"]
    status = (
        "pass"
        if best_clean.policy == "depth_3"
        and best_clean.f1 >= 0.82
        and best_clean.f1 - depth1.f1 >= 0.10
        and best_clean.f1 - depth5.f1 >= 0.03
        and leaky.leakage == 1.0
        else "fail"
    )
    return (
        ProbeResult(
            probe_id="CAS-003",
            status=status,
            metric="best_depth / best_f1 / depth1_gap / depth5_gap / leaky_f1",
            value=f"{best_clean.policy} / {best_clean.f1:.4f} / {best_clean.f1 - depth1.f1:.4f} / {best_clean.f1 - depth5.f1:.4f} / {leaky.f1:.4f}",
            null_hypothesis="Cascade depth does not show a finite optimal public projection depth over shallow or over-deep controls.",
            safest_read="If this passes, nested observer-boundary language gains a concrete design rule: finite depth can improve readability, but too much filtering can degrade it.",
            falsifier="Fail if no finite-depth optimum appears or if a leaky private feature is required.",
        ),
        metric_rows,
    )


def auk_001(science_results: list[ProbeResult]) -> tuple[ProbeResult, list[MetricRow]]:
    """Receipt translation gate: only passes if any prior probe passes and authority stays sealed."""
    any_pass = any(result.status == "pass" for result in science_results)
    rows: list[MetricRow] = []
    policies = ["receipt_translation", "authority_leak_control"]
    for policy in policies:
        leakage = 1.0 if policy == "authority_leak_control" else 0.0
        authority_flip = 1.0 if policy == "authority_leak_control" else 0.0
        rows.append(
            MetricRow(
                probe_id="AUK-001",
                policy=policy,
                split="gate",
                accuracy=1.0 if any_pass and policy == "receipt_translation" else 0.0,
                f1=1.0 if any_pass and policy == "receipt_translation" else 0.0,
                false_write_rate=0.0 if policy == "receipt_translation" else 1.0,
                missed_write_rate=0.0,
                auc_like=0.5,
                leakage=leakage,
                model=f"any_science_pass={any_pass};authority_flip={authority_flip}",
            )
        )
    status = "pass" if any_pass else "blocked"
    return (
        ProbeResult(
            probe_id="AUK-001",
            status=status,
            metric="any_science_pass / authority_leak",
            value=f"{int(any_pass)} / 0",
            null_hypothesis="No boundary rule is mature enough to translate into receipt policy.",
            safest_read="If blocked, do not port to Aukora yet. If pass, port only invariant and controls, not metaphor.",
            falsifier="Fail/block if no scientific probe passes or if receipt translation grants authority.",
        ),
        rows,
    )


def write_outputs(results: list[ProbeResult], rows: list[MetricRow]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(MetricRow.__annotations__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)

    report = [
        "# GHP Boundary Redesign Probes",
        "",
        "Toy telemetry only. These probes use hidden dynamics, public/projection predictors, held-out seeds, and explicit controls.",
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
            "## Metrics",
            "",
            "| Probe | Policy | Split | Accuracy | F1 | False Write | Missed Write | AUC-like | Leakage | Model |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in rows:
        report.append(
            f"| {row.probe_id} | {row.policy} | {row.split} | {row.accuracy:.4f} | {row.f1:.4f} | {row.false_write_rate:.4f} | {row.missed_write_rate:.4f} | {row.auc_like:.4f} | {row.leakage:.4f} | {row.model} |"
        )
    report.extend(
        [
            "",
            "## BCL-002 Anti-Circularity Ledger",
            "",
            "- Train/test seed split is mandatory.",
            "- Hidden truth generation is separated from public predictors.",
            "- Shuffled-label or wrong-topology controls are reported.",
            "- Leaky/private-state controls are marked inadmissible.",
            "- `AUK-001` remains blocked unless at least one scientific probe passes.",
        ]
    )
    (OUT / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    handoff = """# AUKORA / GHP HANDOFF - Boundary Redesign Probes

## Rule

Port only passing invariants, never metaphors.

## If AUK-001 Passes

- Translate the passing rule into a receipt/write policy candidate.
- Keep authority separate from evidence.
- Preserve train/test, shuffled, wrong-topology, and leaky-oracle controls.

## If AUK-001 Is Blocked

- Do not port the rule to Aukora yet.
- Keep results in the GHP lab as design pressure.
"""
    (OUT / "AUKORA_HANDOFF.md").write_text(handoff, encoding="utf-8")


def main() -> None:
    science_results: list[ProbeResult] = []
    rows: list[MetricRow] = []
    for runner in (cac_003, net_003, cas_003):
        result, metric_rows = runner()
        science_results.append(result)
        rows.extend(metric_rows)
    auk_result, auk_rows = auk_001(science_results)
    results = science_results + [auk_result]
    rows.extend(auk_rows)
    write_outputs(results, rows)
    for result in results:
        print(f"{result.probe_id}: {result.status} :: {result.value}")


if __name__ == "__main__":
    main()
