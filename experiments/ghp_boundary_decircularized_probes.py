#!/usr/bin/env python3
"""De-circularized GHP boundary probes.

Follow-up to the boundary-collapse hardening battery.

The first battery proved the scaffolds were internally coherent. These probes
separate truth generation from detector rules:

- CAC-002: hidden bubble-like collapse dynamics, public drive-only detector.
- NET-002: recover which topology predicts withheld write/witness/release labels.
- CAS-002: hidden multilayer cascade, public staged-projection detector.

Toy telemetry only. No physics, consciousness, over-unity, scalar-wave, or
time-extrusion claims.
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
OUT = ROOT / "ghp_boundary_decircularized_probes_outputs"
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
    compressed_bits: int
    leakage: float
    selected_model: str


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
    if not scores:
        return 0.0
    candidates = sorted(set(scores))
    if len(candidates) > 120:
        candidates = [statistics.quantiles(scores, n=120)[i] for i in range(119)]
    best_t = candidates[0]
    best_f1 = -1.0
    for threshold in candidates:
        pred = [1 if score >= threshold else 0 for score in scores]
        _acc, f1, _fw, _mw = binary_metrics(pred, truth)
        if f1 > best_f1:
            best_f1 = f1
            best_t = threshold
    return best_t


def cac_series(seed: int, n: int = 1200) -> tuple[list[dict[str, float]], list[int]]:
    """Generate hidden bubble-like state and public drive features."""
    rng = random.Random(seed)
    phase = rng.random() * math.tau
    radius = 1.0 + rng.random() * 0.08
    velocity = 0.0
    memory = 0.0
    rows: list[dict[str, float]] = []
    truth: list[int] = []
    recent_drive: list[float] = []

    for t in range(n):
        carrier = math.sin(t / 9.0 + phase)
        envelope = 0.5 + 0.5 * math.sin(t / 73.0 + 0.4 * phase)
        burst = 1.2 if (t + seed) % 173 in {0, 1, 2, 3, 4, 5, 6} else 0.0
        drive = envelope * carrier + burst + rng.gauss(0.0, 0.10)
        recent_drive.append(drive)
        recent_drive = recent_drive[-16:]
        energy = statistics.fmean(abs(x) for x in recent_drive)
        slope = drive - rows[-1]["drive"] if rows else 0.0
        memory = 0.88 * memory + max(0.0, drive) + 0.35 * max(0.0, slope)

        # Hidden dynamics: detectors do not see radius/velocity directly.
        forcing = 0.032 * memory + 0.018 * max(0.0, drive)
        spring = 0.18 * (radius - 1.0)
        damping = 0.072 * velocity
        velocity += -spring - forcing - damping + rng.gauss(0.0, 0.010)
        radius += velocity

        collapse = 1 if radius < 0.44 and velocity < -0.045 else 0
        if collapse:
            radius = 0.94 + rng.random() * 0.08
            velocity = 0.0
            memory *= 0.15

        rows.append(
            {
                "drive": drive,
                "slope": slope,
                "energy": energy,
                "memory": memory,
            }
        )
        truth.append(collapse)

    return rows, truth


def cac_scores(rows: list[dict[str, float]], policy: str, seed: int) -> list[float]:
    rng = random.Random(seed + 404)
    if policy == "public_collapse_detector":
        return [
            0.65 * row["memory"] + 1.25 * max(0.0, row["slope"]) + 0.75 * row["energy"]
            for row in rows
        ]
    if policy == "amplitude_only":
        return [row["drive"] for row in rows]
    if policy == "slope_only":
        return [row["slope"] for row in rows]
    if policy == "shuffled_phase_control":
        scores = [0.65 * row["memory"] + 1.25 * max(0.0, row["slope"]) for row in rows]
        rng.shuffle(scores)
        return scores
    if policy == "random_control":
        return [rng.random() for _ in rows]
    raise ValueError(policy)


def cac_002() -> tuple[ProbeResult, list[MetricRow]]:
    policies = [
        "public_collapse_detector",
        "amplitude_only",
        "slope_only",
        "shuffled_phase_control",
        "random_control",
    ]
    train: dict[str, tuple[list[float], list[int]]] = {}
    test: dict[str, tuple[list[float], list[int]]] = {}
    train_truth: list[int] = []
    test_truth: list[int] = []
    for seed in TRAIN_SEEDS:
        rows, truth = cac_series(seed)
        train_truth.extend(truth)
        for policy in policies:
            train.setdefault(policy, ([], []))[0].extend(cac_scores(rows, policy, seed))
            train[policy][1].extend(truth)
    for seed in TEST_SEEDS:
        rows, truth = cac_series(seed)
        test_truth.extend(truth)
        for policy in policies:
            test.setdefault(policy, ([], []))[0].extend(cac_scores(rows, policy, seed))
            test[policy][1].extend(truth)

    metric_rows: list[MetricRow] = []
    thresholds: dict[str, float] = {}
    for policy in policies:
        thresholds[policy] = best_threshold(train[policy][0], train[policy][1])
        for split, data in [("train", train[policy]), ("test", test[policy])]:
            scores, truth = data
            pred = [1 if score >= thresholds[policy] else 0 for score in scores]
            accuracy, f1, false_write, missed_write = binary_metrics(pred, truth)
            metric_rows.append(
                MetricRow(
                    probe_id="CAC-002",
                    policy=policy,
                    split=split,
                    accuracy=accuracy,
                    f1=f1,
                    false_write_rate=false_write,
                    missed_write_rate=missed_write,
                    compressed_bits=compressed_bits({"policy": policy, "threshold": thresholds[policy]}),
                    leakage=0.0,
                    selected_model=f"threshold={thresholds[policy]:.4f}",
                )
            )

    test_rows = {row.policy: row for row in metric_rows if row.split == "test"}
    main = test_rows["public_collapse_detector"]
    amp = test_rows["amplitude_only"]
    shuffled = test_rows["shuffled_phase_control"]
    status = (
        "pass"
        if main.f1 >= 0.62
        and main.f1 - amp.f1 >= 0.15
        and main.f1 - shuffled.f1 >= 0.18
        and main.false_write_rate <= 0.08
        else "fail"
    )
    return (
        ProbeResult(
            probe_id="CAC-002",
            status=status,
            metric="test_f1 / amp_gap / shuffled_gap / false_write",
            value=f"{main.f1:.4f} / {main.f1 - amp.f1:.4f} / {main.f1 - shuffled.f1:.4f} / {main.false_write_rate:.4f}",
            null_hypothesis="A public boundary-collapse detector cannot predict hidden collapse events better than amplitude-only or shuffled controls.",
            safest_read="If this passes, the cavitation analogue becomes less circular: public drive history predicts hidden collapse-like events on held-out seeds.",
            falsifier="Fail if amplitude-only or shuffled phase controls perform nearly as well, or if false writes are high.",
        ),
        metric_rows,
    )


def true_graph() -> dict[int, set[int]]:
    graph = {i: {(i - 1) % 12, (i + 1) % 12} for i in range(12)}
    for a, b in [(0, 6), (1, 5), (2, 8), (3, 9), (4, 10), (7, 11)]:
        graph[a].add(b)
        graph[b].add(a)
    return graph


def ring_graph() -> dict[int, set[int]]:
    return {i: {(i - 1) % 12, (i + 1) % 12} for i in range(12)}


def shuffled_graph(seed: int) -> dict[int, set[int]]:
    base = true_graph()
    nodes = list(base)
    rng = random.Random(seed)
    shuffled = nodes[:]
    rng.shuffle(shuffled)
    mapping = dict(zip(nodes, shuffled))
    return {node: {mapping[n] for n in base[node]} for node in nodes}


def net_dataset(seed: int, graph: dict[int, set[int]], steps: int = 360) -> tuple[list[dict[int, float]], list[dict[int, str]]]:
    rng = random.Random(seed + 5000)
    nodes = list(graph)
    values = {node: rng.gauss(0.0, 0.35) for node in nodes}
    signal_rows: list[dict[int, float]] = []
    label_rows: list[dict[int, str]] = []
    for step in range(steps):
        global_drive = 0.4 * math.sin(step / 19.0) + 0.3 * math.sin(step / 53.0)
        next_values: dict[int, float] = {}
        for node in nodes:
            neigh = statistics.fmean(values[n] for n in graph[node])
            local = 0.58 * values[node] + 0.34 * neigh + global_drive + rng.gauss(0.0, 0.22)
            next_values[node] = local
        values = next_values
        labels: dict[int, str] = {}
        for node in nodes:
            neigh = statistics.fmean(values[n] for n in graph[node])
            roughness = statistics.fmean(abs(values[node] - values[n]) for n in graph[node])
            pressure = 0.66 * values[node] + 0.82 * neigh - 0.28 * roughness
            if pressure > 1.15:
                labels[node] = "write"
            elif pressure > 0.58:
                labels[node] = "witness"
            else:
                labels[node] = "release"
        signal_rows.append(values.copy())
        label_rows.append(labels)
    return signal_rows, label_rows


def net_predict(signals: list[dict[int, float]], graph: dict[int, set[int]]) -> list[str]:
    pred: list[str] = []
    for values in signals:
        for node in sorted(values):
            neigh = statistics.fmean(values[n] for n in graph[node])
            roughness = statistics.fmean(abs(values[node] - values[n]) for n in graph[node])
            score = 0.62 * values[node] + 0.70 * neigh - 0.20 * roughness
            if score > 1.00:
                pred.append("write")
            elif score > 0.50:
                pred.append("witness")
            else:
                pred.append("release")
    return pred


def flat_predict(signals: list[dict[int, float]]) -> list[str]:
    pred: list[str] = []
    for values in signals:
        for node in sorted(values):
            value = values[node]
            if value > 1.08:
                pred.append("write")
            elif value > 0.56:
                pred.append("witness")
            else:
                pred.append("release")
    return pred


def flatten_labels(labels: list[dict[int, str]]) -> list[str]:
    return [row[node] for row in labels for node in sorted(row)]


def net_002() -> tuple[ProbeResult, list[MetricRow]]:
    candidates = {
        "true_topology": true_graph(),
        "ring_only": ring_graph(),
        "shuffled_a": shuffled_graph(42),
        "shuffled_b": shuffled_graph(73),
    }
    train_signals: list[dict[int, float]] = []
    train_labels: list[dict[int, str]] = []
    test_signals: list[dict[int, float]] = []
    test_labels: list[dict[int, str]] = []
    graph = true_graph()
    for seed in TRAIN_SEEDS:
        signals, labels = net_dataset(seed, graph)
        train_signals.extend(signals)
        train_labels.extend(labels)
    for seed in TEST_SEEDS:
        signals, labels = net_dataset(seed, graph)
        test_signals.extend(signals)
        test_labels.extend(labels)

    train_truth = flatten_labels(train_labels)
    test_truth = flatten_labels(test_labels)
    train_scores: dict[str, float] = {}
    for name, candidate in candidates.items():
        train_scores[name] = multiclass_accuracy(net_predict(train_signals, candidate), train_truth)
    selected = max(train_scores, key=train_scores.get)

    metric_rows: list[MetricRow] = []
    policies = dict(candidates)
    policies["selected_topology"] = candidates[selected]
    for split, signals, truth in [("train", train_signals, train_truth), ("test", test_signals, test_truth)]:
        for policy, candidate in policies.items():
            pred = net_predict(signals, candidate)
            accuracy = multiclass_accuracy(pred, truth)
            write_pred = [1 if value == "write" else 0 for value in pred]
            write_truth = [1 if value == "write" else 0 for value in truth]
            _acc, f1, false_write, missed_write = binary_metrics(write_pred, write_truth)
            metric_rows.append(
                MetricRow(
                    probe_id="NET-002",
                    policy=policy,
                    split=split,
                    accuracy=accuracy,
                    f1=f1,
                    false_write_rate=false_write,
                    missed_write_rate=missed_write,
                    compressed_bits=compressed_bits({"policy": policy, "selected": selected}),
                    leakage=0.0,
                    selected_model=selected if policy == "selected_topology" else policy,
                )
            )
        flat = flat_predict(signals)
        accuracy = multiclass_accuracy(flat, truth)
        write_pred = [1 if value == "write" else 0 for value in flat]
        write_truth = [1 if value == "write" else 0 for value in truth]
        _acc, f1, false_write, missed_write = binary_metrics(write_pred, write_truth)
        metric_rows.append(
            MetricRow(
                probe_id="NET-002",
                policy="flat_node_only",
                split=split,
                accuracy=accuracy,
                f1=f1,
                false_write_rate=false_write,
                missed_write_rate=missed_write,
                compressed_bits=compressed_bits({"policy": "flat_node_only"}),
                leakage=0.0,
                selected_model="none",
            )
        )

    test_rows = {row.policy: row for row in metric_rows if row.split == "test"}
    selected_row = test_rows["selected_topology"]
    flat = test_rows["flat_node_only"]
    best_bad = max(test_rows["ring_only"].accuracy, test_rows["shuffled_a"].accuracy, test_rows["shuffled_b"].accuracy)
    status = (
        "pass"
        if selected == "true_topology"
        and selected_row.accuracy >= 0.90
        and selected_row.accuracy - flat.accuracy >= 0.12
        and selected_row.accuracy - best_bad >= 0.06
        else "fail"
    )
    return (
        ProbeResult(
            probe_id="NET-002",
            status=status,
            metric="selected / test_accuracy / flat_gap / best_bad_gap",
            value=f"{selected} / {selected_row.accuracy:.4f} / {selected_row.accuracy - flat.accuracy:.4f} / {selected_row.accuracy - best_bad:.4f}",
            null_hypothesis="Observed node streams do not let a topology-sensitive boundary recover the correct graph better than flat or wrong-topology controls.",
            safest_read="If this passes, the 'net' branch becomes testable graph recovery rather than symbolic mesh language.",
            falsifier="Fail if a wrong graph or flat node-only policy predicts withheld labels nearly as well as the selected topology.",
        ),
        metric_rows,
    )


def cas_dataset(seed: int, n: int = 1400) -> tuple[list[dict[str, float]], list[int]]:
    rng = random.Random(seed + 22000)
    rows: list[dict[str, float]] = []
    truth: list[int] = []
    hidden_mood = rng.random()
    for _step in range(n):
        external = rng.random()
        sensory_noise = rng.random()
        contradiction = rng.random()
        hidden_mood = 0.94 * hidden_mood + 0.06 * rng.random()
        sensory = 0.72 * external + 0.28 * sensory_noise
        blanket = 0.63 * sensory + 0.37 * rng.random()
        witness = 0.68 * blanket + 0.32 * (1.0 - contradiction)
        private_bias = 0.18 * hidden_mood
        write_probability = 1 / (1 + math.exp(-7.0 * (witness + private_bias - 0.83)))
        write = 1 if rng.random() < write_probability else 0
        rows.append(
            {
                "external": external,
                "sensory": sensory,
                "blanket": blanket,
                "witness": witness,
                "public_contradiction": contradiction,
                "hidden_mood": hidden_mood,
            }
        )
        truth.append(write)
    return rows, truth


def cas_score(row: dict[str, float], policy: str) -> float:
    if policy == "nested_projection":
        return 0.25 * row["sensory"] + 0.35 * row["blanket"] + 0.40 * row["witness"]
    if policy == "one_step_external":
        return row["external"]
    if policy == "overcompressed_sensory":
        return row["sensory"]
    if policy == "flat_public_combo":
        return 0.55 * row["external"] + 0.45 * (1.0 - row["public_contradiction"])
    if policy == "leaky_hidden_oracle":
        return 0.25 * row["sensory"] + 0.35 * row["blanket"] + 0.40 * row["witness"] + 0.18 * row["hidden_mood"]
    raise ValueError(policy)


def cas_002() -> tuple[ProbeResult, list[MetricRow]]:
    policies = [
        "nested_projection",
        "one_step_external",
        "overcompressed_sensory",
        "flat_public_combo",
        "leaky_hidden_oracle",
    ]
    train_rows: list[dict[str, float]] = []
    train_truth: list[int] = []
    test_rows_data: list[dict[str, float]] = []
    test_truth: list[int] = []
    for seed in TRAIN_SEEDS:
        rows, truth = cas_dataset(seed)
        train_rows.extend(rows)
        train_truth.extend(truth)
    for seed in TEST_SEEDS:
        rows, truth = cas_dataset(seed)
        test_rows_data.extend(rows)
        test_truth.extend(truth)

    thresholds: dict[str, float] = {}
    metric_rows: list[MetricRow] = []
    for policy in policies:
        train_scores = [cas_score(row, policy) for row in train_rows]
        thresholds[policy] = best_threshold(train_scores, train_truth)
        for split, rows, truth in [("train", train_rows, train_truth), ("test", test_rows_data, test_truth)]:
            scores = [cas_score(row, policy) for row in rows]
            pred = [1 if score >= thresholds[policy] else 0 for score in scores]
            accuracy, f1, false_write, missed_write = binary_metrics(pred, truth)
            metric_rows.append(
                MetricRow(
                    probe_id="CAS-002",
                    policy=policy,
                    split=split,
                    accuracy=accuracy,
                    f1=f1,
                    false_write_rate=false_write,
                    missed_write_rate=missed_write,
                    compressed_bits=compressed_bits({"policy": policy, "threshold": thresholds[policy]}),
                    leakage=1.0 if policy == "leaky_hidden_oracle" else 0.0,
                    selected_model=f"threshold={thresholds[policy]:.4f}",
                )
            )

    test_rows = {row.policy: row for row in metric_rows if row.split == "test"}
    main = test_rows["nested_projection"]
    one_step = test_rows["one_step_external"]
    flat = test_rows["flat_public_combo"]
    leaky = test_rows["leaky_hidden_oracle"]
    status = (
        "pass"
        if main.f1 >= 0.72
        and main.f1 - one_step.f1 >= 0.10
        and main.f1 - flat.f1 >= 0.06
        and main.leakage == 0.0
        and leaky.leakage == 1.0
        else "fail"
    )
    return (
        ProbeResult(
            probe_id="CAS-002",
            status=status,
            metric="test_f1 / one_step_gap / flat_gap / nested_leakage / leaky_f1",
            value=f"{main.f1:.4f} / {main.f1 - one_step.f1:.4f} / {main.f1 - flat.f1:.4f} / {main.leakage:.4f} / {leaky.f1:.4f}",
            null_hypothesis="Staged finite-access projection does not improve hidden write prediction over one-step public compression once private leakage is forbidden.",
            safest_read="If this passes, cascade language is useful as a non-circular engineering pattern: staged public projections generalize better than flatter projections.",
            falsifier="Fail if one-step or flat public baselines perform nearly as well, or if the winning path needs hidden/private state.",
        ),
        metric_rows,
    )


def write_outputs(results: list[ProbeResult], rows: list[MetricRow]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(MetricRow.__annotations__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)

    report = [
        "# GHP De-Circularized Boundary Probes",
        "",
        "Toy telemetry only. Truth labels are generated by hidden dynamics, while detectors use public/projection features and held-out seeds.",
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
            "| Probe | Policy | Split | Accuracy | F1 | False Write | Missed Write | Leakage | Selected/Threshold |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in rows:
        report.append(
            f"| {row.probe_id} | {row.policy} | {row.split} | {row.accuracy:.4f} | {row.f1:.4f} | {row.false_write_rate:.4f} | {row.missed_write_rate:.4f} | {row.leakage:.4f} | {row.selected_model} |"
        )
    report.extend(
        [
            "",
            "## Read",
            "",
            "- `CAC-002` asks whether public drive history predicts hidden collapse-like events on held-out seeds.",
            "- `NET-002` asks whether the correct topology can be selected from candidates and still predict withheld labels.",
            "- `CAS-002` asks whether staged public projections beat flatter public compression without using private hidden state.",
            "",
            "## Promotion Rule",
            "",
            "Only passing probes should be considered for future paper hardening. Failed probes stay in the lab as demotion / redesign targets.",
        ]
    )
    (OUT / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    handoff = """# AUKORA / GHP HANDOFF - De-Circularized Boundary Probes

## Core Lesson

Do not port the analogy. Port the anti-circular test shape.

## Candidate Invariants

```text
CAC-002: hidden-event prediction must be trained on public boundary features and evaluated on held-out regimes.
NET-002: mesh/topology claims require topology recovery or wrong-topology controls.
CAS-002: nested observer/blanket claims require staged public projections that beat flat baselines without private leakage.
```

## Aukora Relevance

- Receipt/write policies should be evaluated against held-out regimes, not just self-generated labels.
- Mesh/swarm memory should include wrong-topology controls.
- Hypothesis memory should include leaky-oracle controls so private state cannot masquerade as intelligence.
"""
    (OUT / "AUKORA_HANDOFF.md").write_text(handoff, encoding="utf-8")


def main() -> None:
    results: list[ProbeResult] = []
    rows: list[MetricRow] = []
    for runner in (cac_002, net_002, cas_002):
        result, metric_rows = runner()
        results.append(result)
        rows.extend(metric_rows)
    write_outputs(results, rows)
    for result in results:
        print(f"{result.probe_id}: {result.status} :: {result.value}")


if __name__ == "__main__":
    main()
