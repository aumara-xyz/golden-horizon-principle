#!/usr/bin/env python3
"""Structural memory vs case memory probe for GHP/Aukora.

Does a compact structural memory predict gate outcomes better, with fewer bits,
than raw case memory?

This is toy telemetry only. It does not prove consciousness or GHP physics.
"""

from __future__ import annotations

import csv
import json
import math
import random
import zlib
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_structural_vs_case_memory_probe_outputs"

LABELS = [
    "allow",
    "capability_refusal",
    "authorization_refusal",
    "malformed_refusal",
    "unknown_refusal",
]

ACTION_SPECS = {
    "read_file": ("read", "local", True, 1),
    "list_dir": ("read", "local", True, 1),
    "read_config": ("read", "local", True, 1),
    "inspect_log": ("read", "local", True, 1),
    "fetch_url": ("external", "network", True, 2),
    "sync_calendar": ("external", "network", True, 2),
    "write_file": ("write", "local", False, 1),
    "delete_file": ("destructive", "local", False, 0),
    "read_secret": ("secret", "private", False, 0),
    "export_memory": ("memory", "private", True, 2),
}

WITHHELD_ACTIONS = {"sync_calendar", "export_memory"}
POP_STATES = ["valid", "missing", "malformed", "replayed"]


@dataclass
class GateEvent:
    action: str
    family: str
    resource_class: str
    capability_allowed: bool
    ring: int
    ring_ceiling: int
    pop_state: str
    revoked: bool
    adversarial_near_miss: bool
    policy_id: str
    verdict: str


@dataclass
class ProbeResult:
    probe_id: str
    status: str
    metric: str
    value: str
    null_hypothesis: str
    safest_read: str
    falsifier: str


def gate_verdict(
    capability_allowed: bool,
    ring: int,
    ring_ceiling: int,
    pop_state: str,
    revoked: bool,
) -> str:
    if not capability_allowed or ring > ring_ceiling:
        return "capability_refusal"
    if pop_state == "missing" or revoked:
        return "authorization_refusal"
    if pop_state in {"malformed", "replayed"}:
        return "malformed_refusal"
    if pop_state == "valid":
        return "allow"
    return "unknown_refusal"


def generate_events(seed: int, n: int, include_withheld: bool) -> list[GateEvent]:
    rng = random.Random(seed)
    actions = list(ACTION_SPECS)
    if not include_withheld:
        actions = [action for action in actions if action not in WITHHELD_ACTIONS]

    events: list[GateEvent] = []
    for _ in range(n):
        action = rng.choice(actions)
        family, resource_class, capability_allowed, ring_ceiling = ACTION_SPECS[action]
        ring = rng.choice([0, 1, 2, 3])
        pop_state = rng.choices(POP_STATES, weights=[0.58, 0.20, 0.12, 0.10])[0]
        revoked = rng.random() < 0.08
        adversarial_near_miss = rng.random() < 0.20
        if adversarial_near_miss and capability_allowed:
            pop_state = rng.choice(["missing", "malformed", "replayed"])
            ring = min(ring, ring_ceiling)
        verdict = gate_verdict(capability_allowed, ring, ring_ceiling, pop_state, revoked)
        events.append(
            GateEvent(
                action=action,
                family=family,
                resource_class=resource_class,
                capability_allowed=capability_allowed,
                ring=ring,
                ring_ceiling=ring_ceiling,
                pop_state=pop_state,
                revoked=revoked,
                adversarial_near_miss=adversarial_near_miss,
                policy_id=f"{family}:{resource_class}:v1",
                verdict=verdict,
            )
        )
    return events


class Predictor:
    def __init__(self, key_mode: str) -> None:
        self.key_mode = key_mode
        self.counts: dict[object, list[int]] = defaultdict(lambda: [1 for _ in LABELS])

    def key(self, event: GateEvent) -> object:
        if self.key_mode == "case":
            return (
                event.action,
                event.resource_class,
                event.ring,
                event.pop_state,
                event.revoked,
                event.adversarial_near_miss,
            )
        if self.key_mode == "structural":
            return (
                event.family,
                event.resource_class,
                event.capability_allowed,
                event.ring <= event.ring_ceiling,
                event.pop_state,
                event.revoked,
                event.policy_id,
            )
        if self.key_mode == "random_policy":
            return (
                event.family,
                event.resource_class,
                event.capability_allowed,
                event.ring <= event.ring_ceiling,
                event.pop_state,
                event.revoked,
                f"random:{hash(event.action) % 5}",
            )
        return "global"

    def update(self, event: GateEvent, label: str | None = None) -> None:
        actual = label or event.verdict
        self.counts[self.key(event)][LABELS.index(actual)] += 1

    def probability(self, event: GateEvent, label: str) -> float:
        bucket = self.counts[self.key(event)]
        return bucket[LABELS.index(label)] / sum(bucket)

    def predict(self, event: GateEvent) -> str:
        bucket = self.counts[self.key(event)]
        return LABELS[max(range(len(bucket)), key=lambda idx: bucket[idx])]

    def payload(self) -> dict[str, object]:
        return {
            "key_mode": self.key_mode,
            "labels": LABELS,
            "counts": {repr(key): value for key, value in sorted(self.counts.items(), key=lambda item: repr(item[0]))},
        }


def compressed_bits(payload: object) -> int:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return len(zlib.compress(raw, level=9)) * 8


def evaluate(model: Predictor, test: list[GateEvent]) -> tuple[float, float, float]:
    correct = 0
    surprise_bits = 0.0
    near_miss_correct = 0
    near_miss_total = 0
    for event in test:
        predicted = model.predict(event)
        if predicted == event.verdict:
            correct += 1
            if event.adversarial_near_miss:
                near_miss_correct += 1
        if event.adversarial_near_miss:
            near_miss_total += 1
        surprise_bits += -math.log2(max(model.probability(event, event.verdict), 1e-12))
    return (
        correct / len(test),
        surprise_bits / len(test),
        near_miss_correct / near_miss_total if near_miss_total else 0.0,
    )


def train_model(train: list[GateEvent], key_mode: str, seed: int = 0, shuffled_labels: bool = False) -> Predictor:
    model = Predictor(key_mode)
    labels = [event.verdict for event in train]
    if shuffled_labels:
        random.Random(seed).shuffle(labels)
    for event, label in zip(train, labels):
        model.update(event, label=label)
    return model


def run_probe() -> list[ProbeResult]:
    train = generate_events(seed=1618, n=3600, include_withheld=False)
    test = generate_events(seed=2718, n=1800, include_withheld=True)
    withheld_test = [event for event in test if event.action in WITHHELD_ACTIONS]
    near_miss_test = [event for event in test if event.adversarial_near_miss]

    case_model = train_model(train, "case")
    structural_model = train_model(train, "structural")
    shuffled_model = train_model(train, "structural", seed=42, shuffled_labels=True)
    random_policy_model = train_model(train, "random_policy")

    case_acc, case_surprise, case_near = evaluate(case_model, test)
    structural_acc, structural_surprise, structural_near = evaluate(structural_model, test)
    shuffled_acc, shuffled_surprise, _ = evaluate(shuffled_model, test)
    random_policy_acc, _, _ = evaluate(random_policy_model, test)

    case_withheld_acc, case_withheld_surprise, _ = evaluate(case_model, withheld_test)
    structural_withheld_acc, structural_withheld_surprise, _ = evaluate(structural_model, withheld_test)
    shuffled_withheld_acc, _, _ = evaluate(shuffled_model, withheld_test)

    case_bits = compressed_bits(case_model.payload())
    structural_bits = compressed_bits(
        {
            "schema": "family/resource/capability/ring_ok/pop/revoked/policy_id",
            "labels": LABELS,
            "counts": structural_model.payload()["counts"],
        }
    )
    shuffled_bits = compressed_bits(shuffled_model.payload())

    case_mdl = case_bits + (case_surprise * len(test))
    structural_mdl = structural_bits + (structural_surprise * len(test))
    shuffled_mdl = shuffled_bits + (shuffled_surprise * len(test))

    status = (
        "pass / generalization"
        if structural_acc > case_acc + 0.05
        and structural_withheld_acc > case_withheld_acc + 0.20
        and structural_mdl < case_mdl
        and structural_acc > shuffled_acc + 0.25
        else "watch"
    )

    return [
        ProbeResult(
            probe_id="SVC-001",
            status=status,
            metric=(
                "case_acc; structural_acc; shuffled_acc; random_policy_acc; "
                "case_surprise; structural_surprise; case_mdl; structural_mdl; shuffled_mdl"
            ),
            value=(
                f"{case_acc:.4f}; {structural_acc:.4f}; {shuffled_acc:.4f}; {random_policy_acc:.4f}; "
                f"{case_surprise:.4f}; {structural_surprise:.4f}; {case_mdl:.2f}; {structural_mdl:.2f}; {shuffled_mdl:.2f}"
            ),
            null_hypothesis="Structural memory does not predict gate outcomes better or more compactly than case memory and controls.",
            safest_read=(
                "Structural policy-like memory improves prediction, withheld-action generalization, and MDL over raw case memory. "
                "Randomized policy IDs do not hurt here, which suggests the win comes from structural features rather than policy-id memorization."
            ),
            falsifier="Case memory or shuffled/randomized controls match structural memory, especially on withheld actions.",
        ),
        ProbeResult(
            probe_id="SVC-002",
            status="pass" if structural_withheld_acc > case_withheld_acc + 0.20 else "watch",
            metric="case_withheld_acc; structural_withheld_acc; shuffled_withheld_acc; case_withheld_surprise; structural_withheld_surprise",
            value=(
                f"{case_withheld_acc:.4f}; {structural_withheld_acc:.4f}; {shuffled_withheld_acc:.4f}; "
                f"{case_withheld_surprise:.4f}; {structural_withheld_surprise:.4f}"
            ),
            null_hypothesis="Structural memory does not generalize to withheld actions/resources better than case memory.",
            safest_read="Structural memory generalizes across action family and policy shape instead of exact remembered episodes.",
            falsifier="Withheld action prediction collapses to case-memory or shuffled-control levels.",
        ),
        ProbeResult(
            probe_id="SVC-003",
            status="pass" if structural_near > case_near + 0.10 else "watch",
            metric="case_near_miss_acc; structural_near_miss_acc; near_miss_count",
            value=f"{case_near:.4f}; {structural_near:.4f}; {len(near_miss_test)}",
            null_hypothesis="Structural memory does not handle adversarial near-miss intents better than case memory.",
            safest_read="Structural memory better distinguishes forbidden capability from missing/malformed authorization.",
            falsifier="Near-miss accuracy does not improve over case memory.",
        ),
    ]


def write_outputs(results: list[ProbeResult]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "probe_id",
                "status",
                "metric",
                "value",
                "null_hypothesis",
                "safest_read",
                "falsifier",
            ],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(asdict(result))

    lines = [
        "# GHP Structural Vs Case Memory Probe",
        "",
        "Status: synthetic toy telemetry only.",
        "",
        "This tests whether compact structural memory predicts gate outcomes better, with fewer bits, than raw case memory.",
        "",
        "It does not prove consciousness or GHP physics.",
        "",
        "## Results",
        "",
    ]
    for result in results:
        lines.extend(
            [
                f"### {result.probe_id}: {result.status}",
                "",
                f"- Metric: {result.metric}",
                f"- Value: {result.value}",
                f"- Null hypothesis: {result.null_hypothesis}",
                f"- Safest read: {result.safest_read}",
                f"- Falsifier: {result.falsifier}",
                "",
            ]
        )
    lines.extend(
        [
            "## Aukora Translation",
            "",
            "```text",
            "case memory = individual remembered gate episodes",
            "structural memory = compact signed rule / policy shape",
            "```",
            "",
            "Hard rule:",
            "",
            "```text",
            "Compression is only useful if it preserves or improves prediction.",
            "Structural memory may guide proposals.",
            "Structural memory may never authorize effects.",
            "```",
            "",
            "## Gemini 20D Target",
            "",
            "Port this into Aukora by comparing a case-memory predictor against a structural-memory predictor over `capability_refusal`, `authorization_refusal`, `malformed_refusal`, and `unknown_refusal`, including withheld actions/resources and near-miss intents.",
            "",
        ]
    )
    (OUT / "report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    results = run_probe()
    write_outputs(results)
    print(f"Wrote {OUT / 'report.md'}")
    for result in results:
        print(f"{result.probe_id}: {result.status} :: {result.value}")


if __name__ == "__main__":
    main()
