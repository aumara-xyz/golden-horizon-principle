#!/usr/bin/env python3
"""Focused receipt-boundary reconstruction probe for GHP/Aukora.

This tests a sharp engineering question:

- Can signed boundary receipts reconstruct the public system trajectory?
- Does the chain itself recover order even if transport order is scrambled?
- Do the reconstruction controls fail when effect tokens or chain links are broken?

It is toy telemetry only. It does not prove GHP physics, consciousness, or
that reality is literally holographic.
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
from dataclasses import asdict, dataclass, replace
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_receipt_boundary_reconstruction_probe_outputs"

OWNERS = ["alice", "bob", "cara"]
SLOTS = ["memory", "notes"]


@dataclass
class BoundaryReceipt:
    step: int
    timestamp_ms: int
    actor: str
    owner: str
    action: str
    slot: str
    effect_kind: str
    effect_token: str
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


def blank_public_state() -> dict[str, dict[str, object]]:
    return {
        owner: {"memory": "empty", "notes": "empty", "grant_active": True, "grant_version": 0}
        for owner in OWNERS
    }


def generate_receipts(seed: int = 1618, n: int = 240) -> tuple[list[BoundaryReceipt], list[str]]:
    rng = random.Random(seed)
    public_state = blank_public_state()
    private_payloads: list[str] = []
    receipts: list[BoundaryReceipt] = []
    prev_receipt_id = "GENESIS"
    timestamp_ms = 0

    for step in range(n):
        owner = rng.choices(OWNERS, weights=[0.5, 0.3, 0.2])[0]
        slot = rng.choice(SLOTS)
        action = rng.choices(
            ["write", "delete", "grant_issue", "grant_revoke", "read", "echo"],
            weights=[0.34, 0.10, 0.09, 0.07, 0.24, 0.16],
        )[0]
        timestamp_ms += int(max(9, rng.gauss(88, 13)))

        effect_kind = "none"
        effect_token = "-"
        if action == "write":
            nonce = stable_hash([owner, slot, step, rng.random()])
            private_plaintext = f"{owner}:{slot}:secret:{step}:{nonce}"
            private_payloads.append(private_plaintext)
            effect_token = stable_hash({"opaque": private_plaintext, "salt": stable_hash([step, owner])})
            public_state[owner][slot] = effect_token
            effect_kind = f"write:{slot}"
        elif action == "delete":
            public_state[owner][slot] = "tombstone"
            effect_kind = f"delete:{slot}"
        elif action == "grant_issue":
            public_state[owner]["grant_active"] = True
            public_state[owner]["grant_version"] = int(public_state[owner]["grant_version"]) + 1
            effect_token = stable_hash({"grant_version": public_state[owner]["grant_version"], "owner": owner})
            effect_kind = "grant_issue"
        elif action == "grant_revoke":
            public_state[owner]["grant_active"] = False
            public_state[owner]["grant_version"] = int(public_state[owner]["grant_version"]) + 1
            effect_token = stable_hash({"grant_version": public_state[owner]["grant_version"], "owner": owner, "revoked": True})
            effect_kind = "grant_revoke"
        elif action == "read":
            effect_kind = f"read:{slot}"
        else:
            effect_kind = "echo"

        state_digest = stable_hash(public_state)
        receipt_id = stable_hash(
            {
                "step": step,
                "prev": prev_receipt_id,
                "owner": owner,
                "action": action,
                "slot": slot,
                "effect_kind": effect_kind,
                "effect_token": effect_token,
                "digest": state_digest,
            }
        )
        receipts.append(
            BoundaryReceipt(
                step=step,
                timestamp_ms=timestamp_ms,
                actor=f"{owner}.agent",
                owner=owner,
                action=action,
                slot=slot,
                effect_kind=effect_kind,
                effect_token=effect_token,
                state_digest=state_digest,
                receipt_id=receipt_id,
                prev_receipt_id=prev_receipt_id,
                signed=True,
            )
        )
        prev_receipt_id = receipt_id

    return receipts, private_payloads


def apply_effect(state: dict[str, dict[str, object]], receipt: BoundaryReceipt) -> None:
    if receipt.effect_kind.startswith("write:"):
        state[receipt.owner][receipt.slot] = receipt.effect_token
    elif receipt.effect_kind.startswith("delete:"):
        state[receipt.owner][receipt.slot] = "tombstone"
    elif receipt.effect_kind == "grant_issue":
        state[receipt.owner]["grant_active"] = True
        state[receipt.owner]["grant_version"] = int(state[receipt.owner]["grant_version"]) + 1
    elif receipt.effect_kind == "grant_revoke":
        state[receipt.owner]["grant_active"] = False
        state[receipt.owner]["grant_version"] = int(state[receipt.owner]["grant_version"]) + 1


def reorder_by_chain(receipts: list[BoundaryReceipt]) -> list[BoundaryReceipt]:
    by_prev = {receipt.prev_receipt_id: receipt for receipt in receipts if receipt.signed}
    ordered: list[BoundaryReceipt] = []
    prev = "GENESIS"
    seen: set[str] = set()
    while prev in by_prev:
        receipt = by_prev[prev]
        if receipt.receipt_id in seen:
            break
        ordered.append(receipt)
        seen.add(receipt.receipt_id)
        prev = receipt.receipt_id
    return ordered


def replay(receipts: list[BoundaryReceipt], use_chain_order: bool) -> tuple[float, float]:
    total = len(receipts)
    if total == 0:
        return 0.0, 0.0

    state = blank_public_state()
    sequence = reorder_by_chain(receipts) if use_chain_order else [receipt for receipt in receipts if receipt.signed]
    matches = 0
    for receipt in sequence:
        apply_effect(state, receipt)
        if stable_hash(state) == receipt.state_digest:
            matches += 1
    digest_accuracy = matches / total
    completeness = len(sequence) / total
    return digest_accuracy, completeness


def ablate_effect_tokens(receipts: list[BoundaryReceipt]) -> list[BoundaryReceipt]:
    ablated: list[BoundaryReceipt] = []
    for receipt in receipts:
        if receipt.effect_kind in {"grant_issue", "grant_revoke"} or receipt.effect_kind.startswith("write:"):
            ablated.append(replace(receipt, effect_token="opaque_redacted"))
        else:
            ablated.append(receipt)
    return ablated


def tamper_chain(receipts: list[BoundaryReceipt], seed: int = 2718, rate: float = 0.12) -> list[BoundaryReceipt]:
    rng = random.Random(seed)
    tampered: list[BoundaryReceipt] = []
    for receipt in receipts:
        if rng.random() < rate:
            tampered.append(
                replace(
                    receipt,
                    effect_token=f"tampered-{receipt.effect_token[-4:]}",
                    prev_receipt_id=f"bad-{receipt.prev_receipt_id[-6:]}",
                )
            )
        else:
            tampered.append(receipt)
    return tampered


def drop_receipts(receipts: list[BoundaryReceipt], seed: int = 3141, rate: float = 0.10) -> list[BoundaryReceipt]:
    rng = random.Random(seed)
    return [receipt for receipt in receipts if rng.random() >= rate]


def schema_plaintext_leak_chars(receipts: list[BoundaryReceipt]) -> int:
    leak_chars = 0
    for receipt in receipts:
        if "secret" in receipt.effect_token or "secret" in receipt.effect_kind:
            leak_chars += len(receipt.effect_token)
    return leak_chars


def run_probe() -> list[ProbeResult]:
    canonical, private_payloads = generate_receipts()
    shuffled = canonical[:]
    random.Random(42).shuffle(shuffled)
    ablated = ablate_effect_tokens(canonical)
    tampered = tamper_chain(canonical)
    dropped = drop_receipts(canonical)

    ordered_acc, ordered_complete = replay(canonical, use_chain_order=True)
    chain_shuffled_acc, chain_shuffled_complete = replay(shuffled, use_chain_order=True)
    naive_shuffled_acc, naive_shuffled_complete = replay(shuffled, use_chain_order=False)
    ablated_acc, ablated_complete = replay(ablated, use_chain_order=True)
    tampered_acc, tampered_complete = replay(tampered, use_chain_order=True)
    dropped_acc, dropped_complete = replay(dropped, use_chain_order=True)
    leak_chars = schema_plaintext_leak_chars(canonical)

    order_status = (
        "pass / chain recovers order"
        if ordered_acc == 1.0 and chain_shuffled_acc == 1.0 and chain_shuffled_complete == 1.0 and naive_shuffled_acc < 0.25
        else "watch"
    )
    control_status = (
        "pass / controls break replay"
        if ablated_acc < 0.20 and tampered_complete < 0.95 and tampered_acc < 0.75 and dropped_complete < 0.95
        else "watch"
    )

    return [
        ProbeResult(
            probe_id="RBR-001",
            status=order_status,
            metric=(
                "ordered_digest_acc; chain_shuffled_digest_acc; naive_shuffled_digest_acc; "
                "ordered_completeness; chain_shuffled_completeness; naive_shuffled_completeness"
            ),
            value=(
                f"{ordered_acc:.4f}; {chain_shuffled_acc:.4f}; {naive_shuffled_acc:.4f}; "
                f"{ordered_complete:.4f}; {chain_shuffled_complete:.4f}; {naive_shuffled_complete:.4f}"
            ),
            null_hypothesis="Boundary receipts do not carry enough linked information to reconstruct public trajectory or recover order from the chain.",
            safest_read=(
                "The signed receipt chain is sufficient to replay the public trajectory and recover order even when transport order is scrambled. "
                "Presented order alone is not enough."
            ),
            falsifier="Chain-aware replay fails to recover exact public digests, or naive shuffled replay matches chain-aware replay.",
        ),
        ProbeResult(
            probe_id="RBR-002",
            status=control_status,
            metric="ablated_digest_acc; tampered_digest_acc; dropped_digest_acc; tampered_completeness; dropped_completeness",
            value=(
                f"{ablated_acc:.4f}; {tampered_acc:.4f}; {dropped_acc:.4f}; "
                f"{tampered_complete:.4f}; {dropped_complete:.4f}"
            ),
            null_hypothesis="Effect tokens and intact chain links are not needed; reconstruction survives just as well after ablation, tampering, or missing receipts.",
            safest_read=(
                "Replay depends on intact effect tokens and chain links. Once those are degraded, the public trajectory stops being reconstructible."
            ),
            falsifier="Ablated, tampered, or dropped controls reconstruct just as well as the intact chain.",
        ),
        ProbeResult(
            probe_id="RBR-003",
            status="pass / public-private split" if leak_chars == 0 else "watch",
            metric="plaintext_payload_count; plaintext_leak_chars",
            value=f"{len(private_payloads)}; {leak_chars}",
            null_hypothesis="Public boundary receipts must expose private payload content in order to reconstruct public state.",
            safest_read=(
                "Public replay can succeed with opaque effect tokens and state digests while raw private payload text stays outside the receipt schema."
            ),
            falsifier="Receipt fields expose plaintext payloads or reconstruction requires plaintext content rather than opaque public tokens.",
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
        "# GHP Receipt Boundary Reconstruction Probe",
        "",
        "Status: synthetic toy telemetry only.",
        "",
        "This isolates the receipt question: can a signed boundary record replay the public trajectory without exposing private payload text?",
        "",
        "It does not prove holography, consciousness, or GHP physics.",
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
            "receipt_id + prev_receipt_id + effect token + state digest",
            "  -> replayable public trajectory",
            "```",
            "",
            "Hard rule:",
            "",
            "```text",
            "Receipts may reconstruct the public trajectory.",
            "Receipts may not expose private payload text by default.",
            "Broken links, missing receipts, or ablated effect tokens should break replay.",
            "```",
            "",
            "## Suggested Live Port",
            "",
            "- Add a local receipt-replay test that recomputes a public trace digest from signed receipts only.",
            "- Verify replay still succeeds after transport reordering if chain links are intact.",
            "- Verify replay fails closed under missing links, tampered effect tokens, or dropped receipts.",
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
