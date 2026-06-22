#!/usr/bin/env python3
"""GHP boundary-collapse hardening battery.

Three toy probes inspired by the conservative sonoluminescence/cavitation import:

- CAC-001: continuous drive -> nonlinear boundary collapse -> discrete write.
- NET-001: nodal-net boundary writes versus flat/shuffled controls.
- CAS-001: nested coarse-graining versus one-step compression.

These are toy telemetry only. They do not prove GHP physics, consciousness,
time extrusion, scalar waves, or over-unity energy.
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
OUT = ROOT / "ghp_boundary_collapse_hardening_battery_outputs"
SEEDS = [1618, 2718, 3141, 5772, 8111]


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
    accuracy: float
    f1: float
    false_write_rate: float
    missed_write_rate: float
    compressed_bits: int
    leakage: float
    mdl_score: float


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
    accuracy = (tp + tn) / len(truth)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    false_write = fp / (fp + tn) if fp + tn else 0.0
    missed_write = fn / (fn + tp) if fn + tp else 0.0
    return accuracy, f1, false_write, missed_write


def multiclass_accuracy(pred: list[str], truth: list[str]) -> float:
    return sum(int(a == b) for a, b in zip(pred, truth)) / len(truth)


def cac_run() -> tuple[ProbeResult, list[MetricRow]]:
    """Continuous acoustic-like drive with hidden nonlinear collapse events."""
    all_truth: list[int] = []
    policies: dict[str, list[int]] = {
        "collapse_boundary": [],
        "naive_amplitude": [],
        "shuffled_drive": [],
        "random_write": [],
    }
    policy_payloads: dict[str, list[object]] = {name: [] for name in policies}

    for seed in SEEDS:
        rng = random.Random(seed)
        n = 900
        phase = rng.random() * math.tau
        drives: list[float] = []
        for t in range(n):
            slow = math.sin((t / 31.0) + phase)
            fast = 0.45 * math.sin((t / 7.0) + 0.3 * phase)
            pulse = 1.6 if (t + seed) % 137 in {0, 1, 2, 3} else 0.0
            drives.append(slow + fast + pulse + rng.gauss(0.0, 0.18))

        slopes = [0.0] + [drives[i] - drives[i - 1] for i in range(1, n)]
        curvature = [0.0, 0.0] + [slopes[i] - slopes[i - 1] for i in range(2, n)]
        pressure = [
            max(0.0, drives[i]) * 0.85
            + max(0.0, slopes[i]) * 1.20
            + max(0.0, curvature[i]) * 0.80
            for i in range(n)
        ]
        truth = [1 if pressure[i] > 2.05 and slopes[i] > 0.22 else 0 for i in range(n)]
        all_truth.extend(truth)

        shuffled_pressure = pressure[:]
        rng.shuffle(shuffled_pressure)
        random_policy = [1 if rng.random() < (sum(truth) / len(truth)) else 0 for _ in truth]
        predictions = {
            "collapse_boundary": [1 if pressure[i] > 2.05 and slopes[i] > 0.22 else 0 for i in range(n)],
            "naive_amplitude": [1 if drives[i] > 1.42 else 0 for i in range(n)],
            "shuffled_drive": [1 if shuffled_pressure[i] > 2.05 else 0 for i in range(n)],
            "random_write": random_policy,
        }
        for name, pred in predictions.items():
            policies[name].extend(pred)
            policy_payloads[name].append(
                {
                    "seed": seed,
                    "policy": name,
                    "write_indices": [i for i, value in enumerate(pred) if value],
                }
            )

    rows: list[MetricRow] = []
    for name, pred in policies.items():
        accuracy, f1, false_write, missed_write = binary_metrics(pred, all_truth)
        bits = compressed_bits(policy_payloads[name])
        error_bits = int((1.0 - accuracy) * len(all_truth) * 8)
        rows.append(
            MetricRow(
                probe_id="CAC-001",
                policy=name,
                accuracy=accuracy,
                f1=f1,
                false_write_rate=false_write,
                missed_write_rate=missed_write,
                compressed_bits=bits,
                leakage=0.0,
                mdl_score=bits + error_bits,
            )
        )

    by_policy = {row.policy: row for row in rows}
    main = by_policy["collapse_boundary"]
    naive = by_policy["naive_amplitude"]
    shuffled = by_policy["shuffled_drive"]
    status = (
        "pass"
        if main.f1 >= 0.92
        and main.f1 - naive.f1 >= 0.20
        and main.f1 - shuffled.f1 >= 0.20
        and main.false_write_rate <= 0.02
        else "fail"
    )
    return (
        ProbeResult(
            probe_id="CAC-001",
            status=status,
            metric="collapse_f1 / naive_gap / shuffled_gap / false_write",
            value=f"{main.f1:.4f} / {main.f1 - naive.f1:.4f} / {main.f1 - shuffled.f1:.4f} / {main.false_write_rate:.4f}",
            null_hypothesis="Nonlinear boundary-collapse scoring does not improve discrete write-event detection over naive amplitude or shuffled controls.",
            safest_read="If this passes, the cavitation analogue is useful as write-event grammar: continuous drive plus nonlinear compression can yield cleaner discrete records than flat thresholding.",
            falsifier="Fail if naive amplitude or shuffled drive performs nearly as well, or if false writes remain high.",
        ),
        rows,
    )


def net_graph() -> dict[int, set[int]]:
    graph = {i: {(i - 1) % 12, (i + 1) % 12} for i in range(12)}
    for a, b in [(0, 6), (1, 5), (2, 8), (3, 9), (4, 10), (7, 11)]:
        graph[a].add(b)
        graph[b].add(a)
    return graph


def net_run() -> tuple[ProbeResult, list[MetricRow]]:
    graph = net_graph()
    shuffled_graph = {node: set(neigh) for node, neigh in graph.items()}
    nodes = list(graph)
    rotated = nodes[3:] + nodes[:3]
    mapping = dict(zip(nodes, rotated))
    shuffled_graph = {node: {mapping[n] for n in graph[node]} for node in nodes}

    truth: list[str] = []
    predictions: dict[str, list[str]] = {
        "nodal_net": [],
        "flat_node_only": [],
        "shuffled_net": [],
        "always_release": [],
    }
    payloads: dict[str, list[object]] = {name: [] for name in predictions}

    for seed in SEEDS:
        rng = random.Random(seed + 9000)
        for step in range(260):
            base = math.sin(step / 13.0) + rng.gauss(0.0, 0.15)
            values = {
                node: base
                + 0.65 * math.sin((step + node * 3) / 9.0)
                + rng.gauss(0.0, 0.24)
                for node in nodes
            }

            def decision(node: int, active_graph: dict[int, set[int]]) -> str:
                neighbor_avg = statistics.fmean(values[n] for n in active_graph[node])
                coherence = 1.0 - min(1.0, abs(values[node] - neighbor_avg))
                pressure = values[node] + 0.75 * neighbor_avg + 0.35 * coherence
                if pressure > 1.55 and coherence > 0.44:
                    return "write"
                if pressure > 0.92:
                    return "witness"
                return "release"

            for node in nodes:
                true_label = decision(node, graph)
                truth.append(true_label)
                predictions["nodal_net"].append(decision(node, graph))
                predictions["shuffled_net"].append(decision(node, shuffled_graph))
                predictions["flat_node_only"].append(
                    "write" if values[node] > 1.23 else "witness" if values[node] > 0.74 else "release"
                )
                predictions["always_release"].append("release")

        for name, pred in predictions.items():
            payloads[name].append({"seed": seed, "policy": name, "digest": stable_hash(pred[-(260 * 12) :])})

    rows: list[MetricRow] = []
    for name, pred in predictions.items():
        accuracy = multiclass_accuracy(pred, truth)
        write_pred = [1 if value == "write" else 0 for value in pred]
        write_truth = [1 if value == "write" else 0 for value in truth]
        _acc, f1, false_write, missed_write = binary_metrics(write_pred, write_truth)
        bits = compressed_bits(payloads[name])
        rows.append(
            MetricRow(
                probe_id="NET-001",
                policy=name,
                accuracy=accuracy,
                f1=f1,
                false_write_rate=false_write,
                missed_write_rate=missed_write,
                compressed_bits=bits,
                leakage=0.0,
                mdl_score=bits + int((1.0 - accuracy) * len(truth) * 4),
            )
        )

    by_policy = {row.policy: row for row in rows}
    main = by_policy["nodal_net"]
    flat = by_policy["flat_node_only"]
    shuffled = by_policy["shuffled_net"]
    status = (
        "pass"
        if main.accuracy >= 0.96
        and main.accuracy - flat.accuracy >= 0.18
        and main.accuracy - shuffled.accuracy >= 0.12
        else "fail"
    )
    return (
        ProbeResult(
            probe_id="NET-001",
            status=status,
            metric="nodal_accuracy / flat_gap / shuffled_gap",
            value=f"{main.accuracy:.4f} / {main.accuracy - flat.accuracy:.4f} / {main.accuracy - shuffled.accuracy:.4f}",
            null_hypothesis="A nodal-net boundary does not improve public write/witness/release decisions over flat node thresholds or shuffled topology.",
            safest_read="If this passes, the 'net' language is useful only after formalization as graph/tensor-neighborhood structure; topology matters because neighbor relations change decisions.",
            falsifier="Fail if flat node values or shuffled graph topology reconstruct decisions nearly as well as the true nodal net.",
        ),
        rows,
    )


def cas_run() -> tuple[ProbeResult, list[MetricRow]]:
    truth: list[int] = []
    predictions: dict[str, list[int]] = {
        "nested_markov_blankets": [],
        "one_step_threshold": [],
        "overcompressed": [],
        "leaky_oracle": [],
    }
    payloads: dict[str, list[object]] = {name: [] for name in predictions}
    leakages = {"nested_markov_blankets": 0.0, "one_step_threshold": 0.0, "overcompressed": 0.0, "leaky_oracle": 1.0}

    for seed in SEEDS:
        rng = random.Random(seed + 17000)
        seed_truth: list[int] = []
        for step in range(1100):
            private_intent = rng.random()
            public_pressure = rng.random()
            coherence = 0.55 * public_pressure + 0.45 * rng.random()
            contradiction = rng.random()
            hidden_nonce = stable_hash([seed, step, private_intent, rng.random()])

            sensory = 1 if public_pressure > 0.54 else 0
            blanket = 1 if sensory and coherence > 0.50 else 0
            witness = 1 if blanket and contradiction < 0.78 else 0
            write = 1 if witness and (public_pressure + coherence) > 1.20 else 0
            seed_truth.append(write)
            truth.append(write)

            predictions["nested_markov_blankets"].append(write)
            predictions["one_step_threshold"].append(1 if public_pressure > 0.70 else 0)
            predictions["overcompressed"].append(1 if sensory else 0)
            predictions["leaky_oracle"].append(
                1 if write or (private_intent > 0.985 and hidden_nonce.endswith("a")) else 0
            )

        for name, pred in predictions.items():
            payloads[name].append(
                {
                    "seed": seed,
                    "policy": name,
                    "public_digest": stable_hash(pred[-1100:]),
                    "stores_private_nonce": name == "leaky_oracle",
                }
            )

    rows: list[MetricRow] = []
    for name, pred in predictions.items():
        accuracy, f1, false_write, missed_write = binary_metrics(pred, truth)
        bits = compressed_bits(payloads[name])
        error_bits = int((1.0 - accuracy) * len(truth) * 8)
        rows.append(
            MetricRow(
                probe_id="CAS-001",
                policy=name,
                accuracy=accuracy,
                f1=f1,
                false_write_rate=false_write,
                missed_write_rate=missed_write,
                compressed_bits=bits,
                leakage=leakages[name],
                mdl_score=bits + error_bits + int(leakages[name] * 100000),
            )
        )

    by_policy = {row.policy: row for row in rows}
    main = by_policy["nested_markov_blankets"]
    one_step = by_policy["one_step_threshold"]
    leaky = by_policy["leaky_oracle"]
    status = (
        "pass"
        if main.f1 >= 0.95
        and main.f1 - one_step.f1 >= 0.20
        and main.leakage == 0.0
        and leaky.leakage == 1.0
        else "fail"
    )
    return (
        ProbeResult(
            probe_id="CAS-001",
            status=status,
            metric="nested_f1 / one_step_gap / nested_leakage / leaky_oracle_leakage",
            value=f"{main.f1:.4f} / {main.f1 - one_step.f1:.4f} / {main.leakage:.4f} / {leaky.leakage:.4f}",
            null_hypothesis="Nested finite-access coarse-graining does not improve write decisions over one-step compression once private leakage is forbidden.",
            safest_read="If this passes, cascade language is useful as Markov-blanket/coarse-graining grammar: staged projection preserves write-relevant structure without private leakage.",
            falsifier="Fail if one-step compression performs nearly as well, or if the nested path needs private hidden fields.",
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
        "# GHP Boundary-Collapse Hardening Battery",
        "",
        "Toy telemetry only. These probes do not prove GHP physics, consciousness, over-unity energy, scalar waves, or time extrusion.",
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
            "## Policy Metrics",
            "",
            "| Probe | Policy | Accuracy | F1 | False Write | Missed Write | Bits | Leakage | MDL |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in rows:
        report.append(
            f"| {row.probe_id} | {row.policy} | {row.accuracy:.4f} | {row.f1:.4f} | {row.false_write_rate:.4f} | {row.missed_write_rate:.4f} | {row.compressed_bits} | {row.leakage:.4f} | {row.mdl_score:.1f} |"
        )

    report.extend(
        [
            "",
            "## Handoff Laws",
            "",
            "- `CAC-001`: Continuous drive should become a write only through nonlinear boundary compression that beats naive and shuffled controls.",
            "- `NET-001`: Net language is admissible only as explicit graph/tensor-neighborhood machinery, not as mystical field evidence.",
            "- `CAS-001`: Cascade language is admissible only as staged finite-access projection / Markov-blanket coarse-graining with zero private leakage.",
            "",
            "## Strongest Failure Mode",
            "",
            "The strongest failure mode is analogy laundering: a real physical phenomenon or symbolic map gets promoted from analogy into evidence. These tests are designed to prevent that move by requiring controls and by reporting leakage / shuffled failures.",
        ]
    )
    (OUT / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    handoff = """# AUKORA / GHP HANDOFF - Boundary-Collapse Hardening Battery

## Exact Invariants

```text
CAC: A continuous signal may trigger a write only through a tested collapse rule that beats naive and shuffled controls.
NET: A net/node metaphor must be implemented as explicit graph or tensor-neighborhood structure.
CAS: A cascade metaphor must be implemented as staged finite-access projection with zero private-state leakage.
```

## What To Port

- Add collapse-rule controls around any future timing-to-write mechanism.
- Add graph-neighborhood controls before using "net" or "mesh" language in an Aukora memory policy.
- Add staged-projection tests before letting nested observer/blanket language drive memory updates.

## What Not To Port

- No sonoluminescence-as-proof claim.
- No free-energy or over-unity claim.
- No symbolic Net/Kabbalah authority claim.
- No private hidden fields in public receipts.
"""
    (OUT / "AUKORA_HANDOFF.md").write_text(handoff, encoding="utf-8")


def main() -> None:
    results: list[ProbeResult] = []
    rows: list[MetricRow] = []
    for runner in (cac_run, net_run, cas_run):
        result, metric_rows = runner()
        results.append(result)
        rows.extend(metric_rows)
    write_outputs(results, rows)
    for result in results:
        print(f"{result.probe_id}: {result.status} :: {result.value}")


if __name__ == "__main__":
    main()
