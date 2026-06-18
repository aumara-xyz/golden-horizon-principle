#!/usr/bin/env python3
"""Two-observer shared-reality probe for GHP/Aukora.

This is the Aukora-shaped version of the "two ears" idea:

- two bounded observer receipts each carry partial information about the same event;
- the fused estimate should reconstruct the hidden event state better than either
  observer alone;
- mismatched or unsigned pairings must not write a shared estimate.

It is toy telemetry only. It does not prove that reality is literally created by
observer interference.
"""

from __future__ import annotations

import csv
import math
import random
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_two_observer_shared_reality_probe_outputs"

LABELS = [
    "allow:read",
    "allow:write",
    "allow:delete",
    "allow:observe",
    "capability_refusal:none",
    "authorization_refusal:none",
    "malformed_refusal:none",
    "replay_refusal:none",
]

ACTION_SPECS = {
    "read_file": ("read", "local", 1, {"self", "peer"}),
    "list_dir": ("read", "local", 1, {"self"}),
    "fetch_url": ("external", "network", 2, {"self"}),
    "write_file": ("write", "local", 1, {"self"}),
    "delete_file": ("destructive", "local", 0, {"self"}),
    "read_secret": ("secret", "private", 0, set()),
    "export_memory": ("memory", "private", 2, {"self"}),
}

OWNER_RELATIONS = ["self", "peer", "system"]
POP_STATES = ["valid", "missing", "malformed", "replayed"]
ACTION_CHOICES = [
    "read_file",
    "list_dir",
    "fetch_url",
    "write_file",
    "export_memory",
    "delete_file",
    "read_secret",
]
ACTION_WEIGHTS = [0.20, 0.18, 0.16, 0.18, 0.12, 0.10, 0.06]


@dataclass
class HiddenEvent:
    event_id: int
    timestamp_ms: int
    action: str
    family: str
    resource_class: str
    owner_relation: str
    ring: int
    pop_state: str
    revoked: bool
    capability_allowed: bool
    verdict: str
    effect_class: str


@dataclass
class ObserverAReceipt:
    event_id: int
    timestamp_ms: int
    signed: bool
    action_family: str
    resource_hint: str
    pop_hint: str
    timing_bucket: str


@dataclass
class ObserverBReceipt:
    event_id: int
    timestamp_ms: int
    signed: bool
    owner_relation: str
    capability_hint: str
    integrity_hint: str
    scope_hint: str


@dataclass
class ProbeResult:
    probe_id: str
    status: str
    metric: str
    value: str
    null_hypothesis: str
    safest_read: str
    falsifier: str


def verdict_of(event: HiddenEvent) -> str:
    if not event.capability_allowed:
        return "capability_refusal"
    if event.pop_state == "missing" or event.revoked:
        return "authorization_refusal"
    if event.pop_state == "malformed":
        return "malformed_refusal"
    if event.pop_state == "replayed":
        return "replay_refusal"
    return "allow"


def effect_of(action: str, verdict: str) -> str:
    if verdict != "allow":
        return "none"
    if action == "write_file":
        return "write"
    if action == "delete_file":
        return "delete"
    if action in {"read_file", "list_dir", "read_secret"}:
        return "read"
    return "observe"


def state_label(event: HiddenEvent) -> str:
    return f"{event.verdict}:{event.effect_class}"


def jitter_bucket(timestamp_ms: int) -> str:
    mod = timestamp_ms % 120
    if mod < 40:
        return "early"
    if mod < 80:
        return "mid"
    return "late"


def noisy_choice(rng: random.Random, base: str, alternatives: list[str], error_rate: float) -> str:
    if rng.random() >= error_rate:
        return base
    options = [item for item in alternatives if item != base]
    return rng.choice(options)


def generate_events(seed: int, n: int) -> tuple[list[HiddenEvent], list[ObserverAReceipt], list[ObserverBReceipt]]:
    rng = random.Random(seed)
    events: list[HiddenEvent] = []
    obs_a: list[ObserverAReceipt] = []
    obs_b: list[ObserverBReceipt] = []
    timestamp_ms = 0

    for event_id in range(n):
        action = rng.choices(ACTION_CHOICES, weights=ACTION_WEIGHTS)[0]
        family, resource_class, ring_ceiling, allowed_relations = ACTION_SPECS[action]
        owner_relation = rng.choices(OWNER_RELATIONS, weights=[0.80, 0.15, 0.05])[0]
        ring = rng.choices([0, 1, 2, 3], weights=[0.36, 0.34, 0.20, 0.10])[0]
        pop_state = rng.choices(POP_STATES, weights=[0.60, 0.18, 0.12, 0.10])[0]
        revoked = rng.random() < 0.07
        capability_allowed = ring <= ring_ceiling and owner_relation in allowed_relations
        timestamp_ms += int(max(12, rng.gauss(95, 16)))
        hidden = HiddenEvent(
            event_id=event_id,
            timestamp_ms=timestamp_ms,
            action=action,
            family=family,
            resource_class=resource_class,
            owner_relation=owner_relation,
            ring=ring,
            pop_state=pop_state,
            revoked=revoked,
            capability_allowed=capability_allowed,
            verdict="pending",
            effect_class="pending",
        )
        hidden.verdict = verdict_of(hidden)
        hidden.effect_class = effect_of(action, hidden.verdict)
        events.append(hidden)

        pop_hint_base = "clean" if hidden.pop_state == "valid" and not hidden.revoked else (
            "auth_issue" if hidden.pop_state == "missing" or hidden.revoked else "integrity_issue"
        )
        capability_hint_base = "capable" if hidden.capability_allowed else "blocked"
        integrity_hint_base = "clean" if hidden.pop_state == "valid" and not hidden.revoked else (
            "auth_issue" if hidden.pop_state == "missing" or hidden.revoked else "integrity_issue"
        )

        obs_a.append(
            ObserverAReceipt(
                event_id=event_id,
                timestamp_ms=timestamp_ms + rng.randint(-3, 3),
                signed=rng.random() > 0.03,
                action_family=hidden.family,
                resource_hint=noisy_choice(rng, hidden.resource_class, ["local", "network", "private"], error_rate=0.08),
                pop_hint=noisy_choice(rng, pop_hint_base, ["clean", "auth_issue", "integrity_issue"], error_rate=0.14),
                timing_bucket=jitter_bucket(timestamp_ms),
            )
        )
        obs_b.append(
            ObserverBReceipt(
                event_id=event_id,
                timestamp_ms=timestamp_ms + rng.randint(-3, 3),
                signed=rng.random() > 0.03,
                owner_relation=hidden.owner_relation,
                capability_hint=noisy_choice(rng, capability_hint_base, ["capable", "blocked"], error_rate=0.18),
                integrity_hint=noisy_choice(rng, integrity_hint_base, ["clean", "auth_issue", "integrity_issue"], error_rate=0.18),
                scope_hint=noisy_choice(rng, f"ring<={ring_ceiling}", ["ring<=0", "ring<=1", "ring<=2"], error_rate=0.14),
            )
        )

    return events, obs_a, obs_b


class Predictor:
    def __init__(self, mode: str) -> None:
        self.mode = mode
        self.counts: dict[object, list[int]] = defaultdict(lambda: [1 for _ in LABELS])

    def key(self, obs_a: ObserverAReceipt, obs_b: ObserverBReceipt | None = None) -> object:
        if self.mode == "a_only":
            return (obs_a.action_family, obs_a.resource_hint, obs_a.pop_hint, obs_a.timing_bucket)
        if self.mode == "b_only":
            assert obs_b is not None
            return (obs_b.owner_relation, obs_b.capability_hint, obs_b.integrity_hint, obs_b.scope_hint)
        assert obs_b is not None
        return (
            obs_a.action_family,
            obs_a.resource_hint,
            obs_a.pop_hint,
            obs_b.owner_relation,
            obs_b.capability_hint,
            obs_b.integrity_hint,
            obs_b.scope_hint,
        )

    def update(self, obs_a: ObserverAReceipt, obs_b: ObserverBReceipt | None, label: str) -> None:
        self.counts[self.key(obs_a, obs_b)][LABELS.index(label)] += 1

    def predict(self, obs_a: ObserverAReceipt, obs_b: ObserverBReceipt | None) -> str:
        bucket = self.counts[self.key(obs_a, obs_b)]
        return LABELS[max(range(len(bucket)), key=lambda idx: bucket[idx])]

    def probability(self, obs_a: ObserverAReceipt, obs_b: ObserverBReceipt | None, label: str) -> float:
        bucket = self.counts[self.key(obs_a, obs_b)]
        return bucket[LABELS.index(label)] / sum(bucket)


def pair_valid(obs_a: ObserverAReceipt, obs_b: ObserverBReceipt, max_skew_ms: int = 6) -> bool:
    return obs_a.signed and obs_b.signed and obs_a.event_id == obs_b.event_id and abs(obs_a.timestamp_ms - obs_b.timestamp_ms) <= max_skew_ms


def train_predictors() -> tuple[Predictor, Predictor, Predictor]:
    events, obs_a, obs_b = generate_events(seed=1618, n=4200)
    model_a = Predictor("a_only")
    model_b = Predictor("b_only")
    model_pair = Predictor("paired")
    for event, left, right in zip(events, obs_a, obs_b):
        label = state_label(event)
        model_a.update(left, None, label)
        model_b.update(left, right, label)
        model_pair.update(left, right, label)
    return model_a, model_b, model_pair


def evaluate(
    model_a: Predictor,
    model_b: Predictor,
    model_pair: Predictor,
) -> tuple[float, float, float, float, float, float, float]:
    events, obs_a, obs_b = generate_events(seed=2718, n=2200)
    valid_rows = [
        (event, left, right)
        for event, left, right in zip(events, obs_a, obs_b)
        if pair_valid(left, right)
    ]

    correct_a = 0
    correct_b = 0
    correct_pair = 0
    surprise_a = 0.0
    surprise_b = 0.0
    surprise_pair = 0.0
    for event, left, right in valid_rows:
        pred_a = model_a.predict(left, None)
        pred_b = model_b.predict(left, right)
        pred_pair = model_pair.predict(left, right)
        label = state_label(event)
        if pred_a == label:
            correct_a += 1
        if pred_b == label:
            correct_b += 1
        if pred_pair == label:
            correct_pair += 1
        surprise_a += -math.log2(max(model_a.probability(left, None, label), 1e-12))
        surprise_b += -math.log2(max(model_b.probability(left, right, label), 1e-12))
        surprise_pair += -math.log2(max(model_pair.probability(left, right, label), 1e-12))

    shuffled_right = [right for _, _, right in valid_rows]
    shuffled_right = shuffled_right[1:] + shuffled_right[:1]
    shuffled_correct = 0
    shuffled_surprise = 0.0
    for (event, left, _), shuffled_right_obs in zip(valid_rows, shuffled_right):
        pred = model_pair.predict(left, shuffled_right_obs)
        label = state_label(event)
        if pred == label:
            shuffled_correct += 1
        shuffled_surprise += -math.log2(max(model_pair.probability(left, shuffled_right_obs, label), 1e-12))

    invalid_pairs = 0
    invalid_shared_writes = 0
    mismatched_right = shuffled_right
    for (_, left, _), right in zip(valid_rows, mismatched_right):
        invalid_pairs += 1
        if pair_valid(left, right):
            invalid_shared_writes += 1

    total = len(valid_rows)
    return (
        correct_a / total,
        correct_b / total,
        correct_pair / total,
        shuffled_correct / total,
        surprise_a / total,
        surprise_pair / total,
        invalid_shared_writes / invalid_pairs if invalid_pairs else 0.0,
    )


def run_probe() -> list[ProbeResult]:
    model_a, model_b, model_pair = train_predictors()
    acc_a, acc_b, acc_pair, acc_shuffled, surprise_a, surprise_pair, invalid_write_rate = evaluate(
        model_a, model_b, model_pair
    )

    status = (
        "pass / paired lift"
        if acc_pair > max(acc_a, acc_b) + 0.05 and acc_pair > acc_shuffled + 0.18 and surprise_pair < surprise_a
        else "watch"
    )
    safety = "pass / no invalid writes" if invalid_write_rate == 0.0 else "watch"

    return [
        ProbeResult(
            probe_id="TSR-001",
            status=status,
            metric="single_a_acc; single_b_acc; paired_acc; shuffled_pair_acc; single_a_surprise; paired_surprise",
            value=f"{acc_a:.4f}; {acc_b:.4f}; {acc_pair:.4f}; {acc_shuffled:.4f}; {surprise_a:.4f}; {surprise_pair:.4f}",
            null_hypothesis="Two bounded observers do not reconstruct hidden event state better than either single observer or a shuffled pair.",
            safest_read=(
                "Paired bounded observers reconstruct refusal cause and allow-state better than either observer alone, and the benefit collapses when one stream is mismatched."
            ),
            falsifier="Single-observer or shuffled-pair accuracy matches the paired estimate, or paired surprise does not improve.",
        ),
        ProbeResult(
            probe_id="TSR-002",
            status=safety,
            metric="invalid_pair_shared_write_rate",
            value=f"{invalid_write_rate:.4f}",
            null_hypothesis="Invalid or mismatched observer pairings still produce a shared estimate.",
            safest_read=(
                "Shared-reality estimates should only be written when both receipts verify and the pairing relation is valid."
            ),
            falsifier="Mismatched or unsigned pairings still count as valid shared estimates.",
        ),
        ProbeResult(
            probe_id="TSR-003",
            status="policy",
            metric="authority_status",
            value="shared_estimate_is_evidence_not_authority",
            null_hypothesis="n/a",
            safest_read=(
                "Even a high-confidence shared estimate is an evidential or mnemonic object. Authorization remains a separate gate decision."
            ),
            falsifier="Any implementation lets observer fusion bypass the gate.",
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
        "# GHP Two-Observer Shared-Reality Probe",
        "",
        "Status: synthetic toy telemetry only.",
        "",
        "This is the Aukora-shaped two-ear test: two signed observer streams each carry partial event information, and the paired estimate should beat either single stream while still failing closed on invalid pairings.",
        "",
        "It does not prove that reality is literally made of observer interference.",
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
            "node A signed receipt + node B signed receipt + valid pairing",
            "  -> sharedRealityEstimate",
            "  -> optional memory / confidence consequence",
            "```",
            "",
            "Hard rule:",
            "",
            "```text",
            "Observer fusion may be evidence.",
            "Observer fusion may be memory.",
            "Observer fusion may never be authority.",
            "Invalid or unsigned pairings should write nothing.",
            "```",
            "",
            "## Suggested Live Port",
            "",
            "- Add paired observer receipt fields: `sharedEventId`, `observerNodeId`, `pairingSkewMs`, `sharedRealityEstimate`.",
            "- Require both signed receipts plus event-id and skew validation before writing the shared estimate.",
            "- Compare paired estimate accuracy against node-A-only, node-B-only, and shuffled-pair controls.",
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
