#!/usr/bin/env python3
"""Cheap local falsifiability probes for the GHP/Aukora loop.

This synthetic harness tests whether a receipt-bound boundary loop has
measurable advantages over controls:

- boundary receipts reconstruct state better than ablated/shuffled records;
- receipt memory reduces verdict surprise over time;
- compact VK-like counts can improve MDL versus a tiny base-rate control;
- signed evidence upgrades true hypotheses and decays false hypotheses;
- Chronos-style timing carries bounded information until jitter collapses it.

It does not prove consciousness, physics, GHP, gravity, or holography.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import statistics
import zlib
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_aukora_loop_falsifiability_probe_outputs"


@dataclass
class Receipt:
    step: int
    timestamp_ms: int
    actor: str
    owner: str
    action: str
    resource: str
    grant_active: bool
    revoked: bool
    malformed: bool
    timing_gap_ms: int
    predicted_verdict_probability: float
    verdict: str
    effect_delta: str
    state_digest: str
    receipt_id: str
    prev_receipt_id: str
    signed: bool


@dataclass
class ProbeResult:
    probe_id: str
    status: str
    metric: str
    value: str
    null_hypothesis: str
    safest_read: str
    falsifier: str


def stable_hash(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def actor_owner(actor: str) -> str:
    return actor.split(".", 1)[0]


ALLOWED_ACTIONS = {"read", "write", "delete", "echo"}
ALL_ACTIONS = ["read", "write", "delete", "echo", "admin", "cross_read", "malformed"]


def policy_verdict(
    actor: str,
    owner: str,
    action: str,
    grant_active: bool,
    revoked: bool,
    malformed: bool,
) -> str:
    owned = actor_owner(actor) == owner
    scope_ok = action in ALLOWED_ACTIONS
    allowed = owned and grant_active and not revoked and not malformed and scope_ok
    return "allow" if allowed else "refuse"


def policy_features(receipt: Receipt) -> tuple[str, bool, bool, bool, str]:
    return (
        receipt.action,
        actor_owner(receipt.actor) == receipt.owner,
        receipt.grant_active,
        receipt.revoked,
        receipt.resource,
    )


class OnlineVerdictPredictor:
    def __init__(self, conditioned: bool) -> None:
        self.conditioned = conditioned
        self.counts: dict[object, list[int]] = defaultdict(lambda: [1, 1])

    def key(self, receipt: Receipt) -> object:
        return policy_features(receipt) if self.conditioned else "global"

    def probability(self, receipt: Receipt, verdict: str) -> float:
        allow_count, refuse_count = self.counts[self.key(receipt)]
        total = allow_count + refuse_count
        return (allow_count if verdict == "allow" else refuse_count) / total

    def update(self, receipt: Receipt) -> None:
        bucket = self.counts[self.key(receipt)]
        if receipt.verdict == "allow":
            bucket[0] += 1
        else:
            bucket[1] += 1

    def serializable_counts(self) -> dict[str, list[int]]:
        return {repr(key): value for key, value in sorted(self.counts.items(), key=lambda item: repr(item[0]))}


def generate_receipts(seed: int = 1618, n: int = 720) -> list[Receipt]:
    rng = random.Random(seed)
    memory: dict[str, str] = {"alice": "empty", "bob": "empty"}
    receipts: list[Receipt] = []
    prev_receipt_id = "GENESIS"
    timestamp_ms = 0
    predictor = OnlineVerdictPredictor(conditioned=True)

    for step in range(n):
        owner = "alice" if rng.random() < 0.68 else "bob"
        actor_pool = [f"{owner}.agent", f"{owner}.agent", f"{owner}.agent", "mallory.agent"]
        if owner == "alice":
            actor_pool.append("bob.agent")
        else:
            actor_pool.append("alice.agent")
        actor = rng.choice(actor_pool)

        action_weights = ["read", "write", "write", "echo", "delete", "admin", "cross_read", "malformed"]
        action = rng.choice(action_weights)
        malformed = action == "malformed" or rng.random() < 0.025
        if action == "malformed":
            action = rng.choice(ALL_ACTIONS[:-1])
        resource = "memory" if action in {"read", "write", "delete", "cross_read"} else "tool"
        grant_active = rng.random() > 0.18
        revoked = rng.random() < 0.08
        timing_gap_ms = int(max(10, rng.gauss(100 + (35 if action in {"admin", "cross_read"} else 0), 18)))
        timestamp_ms += timing_gap_ms

        shell = Receipt(
            step=step,
            timestamp_ms=timestamp_ms,
            actor=actor,
            owner=owner,
            action=action,
            resource=resource,
            grant_active=grant_active,
            revoked=revoked,
            malformed=malformed,
            timing_gap_ms=timing_gap_ms,
            predicted_verdict_probability=0.5,
            verdict="refuse",
            effect_delta="none",
            state_digest="pending",
            receipt_id="pending",
            prev_receipt_id=prev_receipt_id,
            signed=True,
        )

        verdict = policy_verdict(actor, owner, action, grant_active, revoked, malformed)
        predicted_prob = predictor.probability(shell, verdict)

        effect_delta = "none"
        if verdict == "allow":
            if action == "write":
                new_value = f"{owner}:{step}:{stable_hash([owner, step, actor])}"
                memory[owner] = new_value
                effect_delta = f"write:{owner}:{stable_hash(new_value)}"
            elif action == "delete":
                memory[owner] = "tombstone"
                effect_delta = f"delete:{owner}"
            elif action == "read":
                effect_delta = f"read:{owner}:{stable_hash(memory[owner])}"
            elif action == "echo":
                effect_delta = f"echo:{owner}:{step}"

        state_digest = stable_hash(memory)
        receipt_id = stable_hash(
            {
                "step": step,
                "prev": prev_receipt_id,
                "actor": actor,
                "owner": owner,
                "action": action,
                "verdict": verdict,
                "effect": effect_delta,
                "state": state_digest,
            }
        )

        # Small amount of unsigned noise to verify that hypothesis memory ignores it.
        signed = rng.random() > 0.06
        receipt = Receipt(
            step=step,
            timestamp_ms=timestamp_ms,
            actor=actor,
            owner=owner,
            action=action,
            resource=resource,
            grant_active=grant_active,
            revoked=revoked,
            malformed=malformed,
            timing_gap_ms=timing_gap_ms,
            predicted_verdict_probability=predicted_prob,
            verdict=verdict,
            effect_delta=effect_delta,
            state_digest=state_digest,
            receipt_id=receipt_id,
            prev_receipt_id=prev_receipt_id,
            signed=signed,
        )
        receipts.append(receipt)
        predictor.update(receipt)
        prev_receipt_id = receipt_id

    return receipts


def reconstruct_state_digests(receipts: list[Receipt], mode: str) -> list[str | None]:
    ordered = list(receipts)
    if mode == "shuffled":
        ordered = sorted(receipts, key=lambda r: stable_hash([r.receipt_id, "shuffle"]))

    memory: dict[str, str] = {"alice": "empty", "bob": "empty"}
    out: list[str | None] = []
    unresolved = False

    for receipt in ordered:
        if mode == "ablated":
            # Without effect deltas, a boundary observer cannot know memory writes.
            if receipt.verdict == "allow" and receipt.action in {"write", "delete"}:
                unresolved = True
            out.append(None if unresolved else stable_hash(memory))
            continue

        if receipt.verdict == "allow":
            parts = receipt.effect_delta.split(":")
            if parts[0] == "write" and len(parts) == 3:
                memory[parts[1]] = f"hash:{parts[2]}"
            elif parts[0] == "delete" and len(parts) == 2:
                memory[parts[1]] = "tombstone"
        out.append(stable_hash(memory))

    if mode == "shuffled":
        by_step = {receipt.step: digest for receipt, digest in zip(ordered, out)}
        return [by_step.get(receipt.step) for receipt in receipts]
    return out


def verify_receipt_chain(receipts: list[Receipt]) -> float:
    prev = "GENESIS"
    valid = 0
    for receipt in receipts:
        expected = stable_hash(
            {
                "step": receipt.step,
                "prev": receipt.prev_receipt_id,
                "actor": receipt.actor,
                "owner": receipt.owner,
                "action": receipt.action,
                "verdict": receipt.verdict,
                "effect": receipt.effect_delta,
                "state": receipt.state_digest,
            }
        )
        if receipt.prev_receipt_id == prev and receipt.receipt_id == expected:
            valid += 1
        prev = receipt.receipt_id
    return valid / len(receipts)


def h2(p: float) -> float:
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def boundary_sufficiency_probe(receipts: list[Receipt]) -> ProbeResult:
    actual = [receipt.state_digest for receipt in receipts]
    full = reconstruct_state_digests(receipts, "full")
    ablated = reconstruct_state_digests(receipts, "ablated")
    shuffled = reconstruct_state_digests(receipts, "shuffled")

    def accuracy(predicted: list[str | None]) -> float:
        return sum(a == p for a, p in zip(actual, predicted)) / len(actual)

    full_acc = accuracy(full)
    ablated_acc = accuracy(ablated)
    private_shuffled_acc = accuracy(shuffled)
    public_chain_acc = verify_receipt_chain(receipts)
    shuffled_chain_acc = verify_receipt_chain(sorted(receipts, key=lambda r: stable_hash([r.receipt_id, "shuffle"])))
    unresolved_rate = sum(item is None for item in ablated) / len(ablated)
    missing_entropy = h2(unresolved_rate)
    completeness = sum(bool(r.receipt_id and r.prev_receipt_id and r.effect_delta and r.state_digest) for r in receipts) / len(receipts)

    status = (
        "pass / privacy-bounded"
        if public_chain_acc > 0.99 and shuffled_chain_acc < 0.05 and full_acc < 0.50
        else "watch"
    )
    return ProbeResult(
        probe_id="AUK-F001",
        status=status,
        metric=(
            "public_chain_acc; shuffled_chain_acc; private_state_reconstruction_acc; "
            "ablated_private_acc; private_shuffled_acc; missing_entropy_bits; receipt_completeness"
        ),
        value=(
            f"{public_chain_acc:.4f}; {shuffled_chain_acc:.4f}; {full_acc:.4f}; "
            f"{ablated_acc:.4f}; {private_shuffled_acc:.4f}; {missing_entropy:.4f}; {completeness:.4f}"
        ),
        null_hypothesis="Boundary receipts do not verify public trajectory better than shuffled controls.",
        safest_read=(
            "Ordered receipts verify the public trajectory, while private memory content is not reconstructable "
            "from hashes alone. This is good custody, not a failure, if the design goal is public proof plus private memory."
        ),
        falsifier="Receipt chain verification fails or shuffled order verifies as well as the true order.",
    )


def surprise_proxy_probe(receipts: list[Receipt]) -> tuple[ProbeResult, OnlineVerdictPredictor, OnlineVerdictPredictor, float, float]:
    memory_model = OnlineVerdictPredictor(conditioned=True)
    base_model = OnlineVerdictPredictor(conditioned=False)
    memory_surprises: list[float] = []
    base_surprises: list[float] = []

    for receipt in receipts:
        p_mem = memory_model.probability(receipt, receipt.verdict)
        p_base = base_model.probability(receipt, receipt.verdict)
        memory_surprises.append(-math.log(max(p_mem, 1e-12)))
        base_surprises.append(-math.log(max(p_base, 1e-12)))
        memory_model.update(receipt)
        base_model.update(receipt)

    q = len(receipts) // 4
    mem_first = statistics.mean(memory_surprises[:q])
    mem_last = statistics.mean(memory_surprises[-q:])
    base_mean = statistics.mean(base_surprises)
    mem_mean = statistics.mean(memory_surprises)
    improvement = base_mean - mem_mean
    decrease = mem_first - mem_last
    status = "pass" if improvement > 0.08 and decrease > 0.08 else "watch"

    result = ProbeResult(
        probe_id="AUK-F002",
        status=status,
        metric="memory_mean_surprise; base_mean_surprise; improvement; memory_first_to_last_decrease",
        value=f"{mem_mean:.4f}; {base_mean:.4f}; {improvement:.4f}; {decrease:.4f}",
        null_hypothesis="Receipt memory does not reduce prediction surprise more than a base-rate control.",
        safest_read="Conditioned receipt memory reduces verdict surprise over the loop in this synthetic gate.",
        falsifier="Memory surprise stays flat, worsens, or matches the base-rate control.",
    )
    return result, memory_model, base_model, sum(memory_surprises) / math.log(2), sum(base_surprises) / math.log(2)


def compressed_size(obj: object) -> int:
    encoded = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return len(zlib.compress(encoded, level=9))


def compression_probe(
    receipts: list[Receipt],
    memory_model: OnlineVerdictPredictor,
    base_model: OnlineVerdictPredictor,
    memory_surprise_bits: float,
    base_surprise_bits: float,
) -> ProbeResult:
    raw = [asdict(receipt) for receipt in receipts]
    raw_bytes = compressed_size(raw)
    vk_payload = {
        "counts": memory_model.serializable_counts(),
        "final_receipt": receipts[-1].receipt_id,
        "final_state": receipts[-1].state_digest,
    }
    base_payload = {"counts": base_model.serializable_counts()}
    vk_bytes = compressed_size(vk_payload)
    base_bytes = compressed_size(base_payload)

    vk_mdl = (vk_bytes * 8) + memory_surprise_bits
    base_mdl = (base_bytes * 8) + base_surprise_bits
    structural_payload = {
        # In a live node this should be a signed Capability Sigil / policy version,
        # not repeated prose. The MDL question is whether verified experience can
        # compress into a small named rule plus residual errors.
        "rule_id": "aukora_scope_v1",
        "scope_hash": stable_hash(sorted(ALLOWED_ACTIONS)),
    }
    structural_errors = sum(
        policy_verdict(
            receipt.actor,
            receipt.owner,
            receipt.action,
            receipt.grant_active,
            receipt.revoked,
            receipt.malformed,
        )
        != receipt.verdict
        for receipt in receipts
    )
    structural_error_bits = structural_errors * math.log2(max(2, len(receipts)))
    structural_bytes = compressed_size(structural_payload)
    structural_mdl = (structural_bytes * 8) + structural_error_bits
    compression_ratio = vk_bytes / raw_bytes
    status = (
        "pass / structural-memory"
        if structural_mdl < base_mdl and compression_ratio < 0.50
        else "watch"
    )

    return ProbeResult(
        probe_id="AUK-F003",
        status=status,
        metric=(
            "raw_zlib_bytes; count_memory_bytes; base_bytes; structural_rule_bytes; "
            "count_memory_mdl_bits; base_mdl_bits; structural_mdl_bits; count_to_raw_ratio"
        ),
        value=(
            f"{raw_bytes}; {vk_bytes}; {base_bytes}; {structural_bytes}; "
            f"{vk_mdl:.2f}; {base_mdl:.2f}; {structural_mdl:.2f}; {compression_ratio:.4f}"
        ),
        null_hypothesis="VK-style compressed memory is smaller only because it loses predictive function.",
        safest_read=(
            "A count-table memory reduces surprise but is not MDL-efficient against a tiny base-rate model. "
            "A structural boundary rule is the better compression target in this synthetic gate."
        ),
        falsifier="No compact structural memory beats the base-rate control, or compression only works by losing prediction.",
    )


HypothesisFn = Callable[[Receipt], str]


def hypothesis_memory_probe(receipts: list[Receipt]) -> ProbeResult:
    hypotheses: dict[str, HypothesisFn] = {
        "true_scope_owner_grant": lambda r: policy_verdict(
            r.actor, r.owner, r.action, r.grant_active, r.revoked, r.malformed
        ),
        "false_grant_is_enough": lambda r: "allow" if r.grant_active and not r.revoked else "refuse",
        "false_owner_is_enough": lambda r: "allow" if actor_owner(r.actor) == r.owner else "refuse",
        "false_timing_is_authority": lambda r: "allow" if r.timing_gap_ms > 118 else "refuse",
        "false_cross_read_allowed": lambda r: "allow" if r.action in {"read", "cross_read"} and r.grant_active else "refuse",
    }
    scores = {name: [1, 1] for name in hypotheses}  # success, failure
    unsigned_events = 0

    for receipt in receipts:
        if not receipt.signed:
            unsigned_events += 1
            continue
        for name, hypothesis in hypotheses.items():
            if hypothesis(receipt) == receipt.verdict:
                scores[name][0] += 1
            else:
                scores[name][1] += 1

    confidence = {name: s / (s + f) for name, (s, f) in scores.items()}
    true_conf = confidence["true_scope_owner_grant"]
    max_false = max(value for name, value in confidence.items() if not name.startswith("true_"))
    gap = true_conf - max_false
    status = "pass" if true_conf > 0.98 and max_false < 0.80 and gap > 0.20 and unsigned_events > 0 else "watch"

    return ProbeResult(
        probe_id="AUK-F004",
        status=status,
        metric="true_confidence; max_false_confidence; confidence_gap; unsigned_ignored_events",
        value=f"{true_conf:.4f}; {max_false:.4f}; {gap:.4f}; {unsigned_events}",
        null_hypothesis="Hypothesis confidence is not meaningfully shaped by signed evidence.",
        safest_read="Signed receipts sharply separate the true boundary rule from false shortcut hypotheses.",
        falsifier="False hypotheses remain high after signed contradiction, or unsigned evidence moves confidence.",
    )


def chronos_timing_probe(seed: int = 2718, n_bits: int = 5000) -> ProbeResult:
    rng = random.Random(seed)
    bits = [rng.randrange(2) for _ in range(n_bits)]
    short_gap = 80.0
    long_gap = 140.0
    threshold = (short_gap + long_gap) / 2

    def ber_for(jitter: float, shuffled: bool = False) -> float:
        source = bits[:]
        if shuffled:
            rng.shuffle(source)
        errors = 0
        for bit, original_bit in zip(source, bits):
            gap = (long_gap if bit else short_gap) + rng.gauss(0.0, jitter)
            decoded = 1 if gap >= threshold else 0
            errors += decoded != original_bit
        return errors / n_bits

    low = ber_for(4.0)
    mid = ber_for(18.0)
    high = ber_for(40.0)
    shuffled = ber_for(4.0, shuffled=True)
    capacity_proxy = 1 - h2(low)
    collapse = next((j for j in range(2, 61, 2) if ber_for(float(j)) > 0.15), None)
    status = "pass" if low < 0.02 and high > 0.20 and shuffled > 0.45 else "watch"

    return ProbeResult(
        probe_id="AUK-F005",
        status=status,
        metric="BER_low; BER_mid; BER_high; shuffled_BER; capacity_proxy_low; collapse_jitter",
        value=f"{low:.4f}; {mid:.4f}; {high:.4f}; {shuffled:.4f}; {capacity_proxy:.4f}; {collapse}",
        null_hypothesis="Pulse gaps carry no recoverable signal beyond shuffled timing controls.",
        safest_read="Timing carries bounded local information under low jitter and collapses under high jitter; timing remains evidence, never authority.",
        falsifier="Low-jitter BER is near chance, or shuffled timing performs the same as ordered timing.",
    )


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
        "# GHP / Aukora Loop Falsifiability Probe",
        "",
        "Status: synthetic toy telemetry only.",
        "",
        "This harness tests whether a receipt-bound boundary loop can reconstruct state, reduce surprise, compress experience, separate true from false hypotheses, and carry bounded timing information better than controls.",
        "",
        "It does not prove consciousness, GHP physics, gravity, holography, or a literal birth event.",
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
            "## Engineering Interpretation",
            "",
            "The most important implementation rule is:",
            "",
            "```text",
            "proposal -> verdict -> consequence -> receipt -> memory consequence -> next proposal",
            "```",
            "",
            "The loop only becomes a useful GHP proving ground if every step is measured and controls are kept close.",
            "",
            "## Next Live Aukora Hooks",
            "",
            "1. Add predicted verdict probability to each gate receipt.",
            "2. Add receipt completeness and reconstruction health to the UI.",
            "3. Add hypothesis confidence updates that require signed receipts.",
            "4. Add MDL-style trace compression metrics to the harvester.",
            "5. Keep Chronos timing as side-lab telemetry only.",
            "",
        ]
    )
    (OUT / "report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    receipts = generate_receipts()
    boundary = boundary_sufficiency_probe(receipts)
    surprise, memory_model, base_model, memory_bits, base_bits = surprise_proxy_probe(receipts)
    compression = compression_probe(receipts, memory_model, base_model, memory_bits, base_bits)
    hypothesis = hypothesis_memory_probe(receipts)
    chronos = chronos_timing_probe()
    results = [boundary, surprise, compression, hypothesis, chronos]
    write_outputs(results)
    print(f"Wrote {OUT / 'report.md'}")
    for result in results:
        print(f"{result.probe_id}: {result.status} :: {result.value}")


if __name__ == "__main__":
    main()
