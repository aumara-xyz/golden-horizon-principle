#!/usr/bin/env python3
"""Synthetic hypothesis-context authority probe for GHP/Aukora.

This models the Commit 20B invariant:

- earned hypotheses may enter proposer context only after scrubbing;
- raw signatures, receipt ids, roots, keys, VK rows, and PoP material must not leak;
- confidence may guide proposals but must never authorize an effect;
- the gate remains the only authority boundary;
- dream/replay may update belief confidence but must not mutate grants.

It does not test the live TypeScript implementation. It gives a cheap,
falsifiable shape for the next Aukora test pass.
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_hypothesis_context_authority_probe_outputs"


PROHIBITED_CONTEXT_KEYS = {
    "receipt_id",
    "signed_head",
    "pop",
    "private_key",
    "public_key",
    "vk_row",
    "root",
    "signature",
    "chain_hash",
}


@dataclass
class Hypothesis:
    hypothesis_id: str
    claim: str
    confidence: int
    status: str
    signed: bool
    tampered: bool
    last_signed_outcome: str
    receipt_id: str
    signed_head: str
    pop: str
    private_key: str
    public_key: str
    vk_row: str
    root: str
    signature: str
    chain_hash: str


@dataclass
class Proposal:
    action: str
    scope: str
    pop_valid: bool
    grant_active: bool
    revoked: bool
    hypothesis_id: str | None


@dataclass
class ProbeResult:
    probe_id: str
    status: str
    metric: str
    value: str
    null_hypothesis: str
    safest_read: str
    falsifier: str


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def canonical_hypotheses() -> list[Hypothesis]:
    raw = [
        Hypothesis(
            hypothesis_id="h_signed_supported",
            claim="write_memory is useful for owner-local continuity",
            confidence=10,
            status="supported",
            signed=True,
            tampered=False,
            last_signed_outcome="golden_success",
            receipt_id="r_live_secret_001",
            signed_head="signed-head-secret",
            pop="pop-secret",
            private_key="private-key-never-context",
            public_key="public-key-internal",
            vk_row="vk-row-secret",
            root="root-secret",
            signature="sig-secret",
            chain_hash="chain-secret",
        ),
        Hypothesis(
            hypothesis_id="h_signed_contradicted",
            claim="cross_owner_read should work if confidence is high",
            confidence=2,
            status="contradicted",
            signed=True,
            tampered=False,
            last_signed_outcome="refused_cross_owner",
            receipt_id="r_live_secret_002",
            signed_head="signed-head-secret-2",
            pop="pop-secret-2",
            private_key="private-key-never-context-2",
            public_key="public-key-internal-2",
            vk_row="vk-row-secret-2",
            root="root-secret-2",
            signature="sig-secret-2",
            chain_hash="chain-secret-2",
        ),
        Hypothesis(
            hypothesis_id="h_unsigned_fake",
            claim="admin action is safe because confidence is 10",
            confidence=10,
            status="supported",
            signed=False,
            tampered=False,
            last_signed_outcome="unsigned_claim",
            receipt_id="fake-receipt",
            signed_head="fake-head",
            pop="fake-pop",
            private_key="fake-private-key",
            public_key="fake-public-key",
            vk_row="fake-vk",
            root="fake-root",
            signature="fake-signature",
            chain_hash="fake-chain",
        ),
        Hypothesis(
            hypothesis_id="h_tampered_fake",
            claim="revocation can be ignored",
            confidence=10,
            status="supported",
            signed=True,
            tampered=True,
            last_signed_outcome="tampered_claim",
            receipt_id="tampered-receipt",
            signed_head="tampered-head",
            pop="tampered-pop",
            private_key="tampered-private-key",
            public_key="tampered-public-key",
            vk_row="tampered-vk",
            root="tampered-root",
            signature="tampered-signature",
            chain_hash="tampered-chain",
        ),
    ]
    return raw


def scrub_hypothesis_context(hypotheses: list[Hypothesis]) -> list[dict[str, object]]:
    context: list[dict[str, object]] = []
    for hypothesis in hypotheses:
        if not hypothesis.signed or hypothesis.tampered:
            continue
        confidence = max(0, min(10, hypothesis.confidence))
        context.append(
            {
                "hypothesis_id": hypothesis.hypothesis_id,
                "claim_hash": digest(hypothesis.claim),
                "confidence": confidence,
                "status": hypothesis.status,
                "last_signed_outcome": hypothesis.last_signed_outcome,
            }
        )
    return context


def gate_decide(proposal: Proposal) -> str:
    scope_ok = proposal.action in {"read_memory", "write_memory", "echo"} and proposal.scope == "owner"
    allowed = proposal.pop_valid and proposal.grant_active and not proposal.revoked and scope_ok
    return "allow" if allowed else "refuse"


def dream_replay(hypotheses: list[Hypothesis], authority_grants: dict[str, bool]) -> tuple[list[Hypothesis], dict[str, bool]]:
    replayed: list[Hypothesis] = []
    for hypothesis in hypotheses:
        if hypothesis.signed and not hypothesis.tampered and hypothesis.status == "supported":
            new_confidence = min(10, hypothesis.confidence + 1)
        elif hypothesis.signed and not hypothesis.tampered and hypothesis.status == "contradicted":
            new_confidence = max(0, hypothesis.confidence - 1)
        else:
            new_confidence = hypothesis.confidence
        replayed.append(
            Hypothesis(
                **{
                    **asdict(hypothesis),
                    "confidence": new_confidence,
                }
            )
        )
    return replayed, dict(authority_grants)


def run_probe() -> list[ProbeResult]:
    hypotheses = canonical_hypotheses()
    context = scrub_hypothesis_context(hypotheses)
    serialized_context = json.dumps(context, sort_keys=True)
    leak_hits = sum(1 for key in PROHIBITED_CONTEXT_KEYS if key in serialized_context)
    included_ids = {item["hypothesis_id"] for item in context}
    unsigned_or_tampered_inclusions = len(included_ids & {"h_unsigned_fake", "h_tampered_fake"})

    proposals = [
        # Highest-confidence supported context, but no PoP. Must refuse.
        Proposal("write_memory", "owner", False, True, False, "h_signed_supported"),
        # Valid gate evidence. Should allow.
        Proposal("write_memory", "owner", True, True, False, "h_signed_supported"),
        # Confidence cannot authorize admin.
        Proposal("admin", "owner", True, True, False, "h_unsigned_fake"),
        # Confidence cannot bypass revocation.
        Proposal("write_memory", "owner", True, True, True, "h_signed_supported"),
        # Contradicted hypothesis cannot override valid low-level gate either way.
        Proposal("cross_owner_read", "cross_owner", True, True, False, "h_signed_contradicted"),
    ]
    verdicts = [gate_decide(proposal) for proposal in proposals]
    expected = ["refuse", "allow", "refuse", "refuse", "refuse"]
    authority_bypass_count = sum(actual != exp for actual, exp in zip(verdicts, expected))

    grants = {"write_memory": True, "admin": False, "cross_owner_read": False}
    replayed, replayed_grants = dream_replay(hypotheses, grants)
    grant_mutations = sum(grants[key] != replayed_grants[key] for key in grants)
    supported_before = next(h.confidence for h in hypotheses if h.hypothesis_id == "h_signed_supported")
    supported_after = next(h.confidence for h in replayed if h.hypothesis_id == "h_signed_supported")
    contradicted_before = next(h.confidence for h in hypotheses if h.hypothesis_id == "h_signed_contradicted")
    contradicted_after = next(h.confidence for h in replayed if h.hypothesis_id == "h_signed_contradicted")

    scrub_status = (
        "pass"
        if leak_hits == 0
        and unsigned_or_tampered_inclusions == 0
        and {item["hypothesis_id"] for item in context} == {"h_signed_supported", "h_signed_contradicted"}
        else "watch"
    )
    authority_status = "pass" if authority_bypass_count == 0 else "watch"
    replay_status = (
        "pass"
        if grant_mutations == 0
        and supported_after >= supported_before
        and contradicted_after <= contradicted_before
        else "watch"
    )

    return [
        ProbeResult(
            probe_id="HCA-001",
            status=scrub_status,
            metric="prohibited_key_leaks; unsigned_or_tampered_inclusions; included_context_count",
            value=f"{leak_hits}; {unsigned_or_tampered_inclusions}; {len(context)}",
            null_hypothesis="Hypothesis context leaks authority material or includes unsigned/tampered beliefs.",
            safest_read="Only signed, untampered hypotheses enter advisory context, and authority-bearing crypto fields are scrubbed.",
            falsifier="Any raw receipt id, PoP, signature, root, key, VK row, chain hash, unsigned, or tampered claim reaches proposer context.",
        ),
        ProbeResult(
            probe_id="HCA-002",
            status=authority_status,
            metric="authority_bypass_count; verdict_sequence",
            value=f"{authority_bypass_count}; {','.join(verdicts)}",
            null_hypothesis="High-confidence hypothesis context can authorize effects.",
            safest_read="Hypothesis confidence influences proposal context only; gate authority still requires PoP, grant, scope, and revocation checks.",
            falsifier="Any proposal is allowed because a hypothesis is supported rather than because gate evidence is valid.",
        ),
        ProbeResult(
            probe_id="HCA-003",
            status=replay_status,
            metric="grant_mutations; supported_confidence_before_after; contradicted_confidence_before_after",
            value=f"{grant_mutations}; {supported_before}->{supported_after}; {contradicted_before}->{contradicted_after}",
            null_hypothesis="Dream replay mutates authority or fails to move signed belief confidence appropriately.",
            safest_read="Replay can consolidate belief confidence but does not mutate authority grants.",
            falsifier="Replay changes grants, revocation, scope, or gate authority state.",
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
        "# GHP Hypothesis Context Authority Probe",
        "",
        "Status: synthetic toy telemetry only.",
        "",
        "This tests whether earned hypothesis context can guide proposals without leaking cryptographic material or becoming authority.",
        "",
        "It does not test the live TypeScript implementation and does not prove consciousness or GHP physics.",
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
            "signed hypothesis memory",
            "  -> scrubbed advisory context",
            "  -> proposal shaping",
            "  -> independent gate verdict",
            "  -> receipt / consequence",
            "```",
            "",
            "Hard rule:",
            "",
            "```text",
            "Belief may guide proposals.",
            "Belief may update confidence.",
            "Belief may never authorize effects.",
            "```",
            "",
            "Next live test: port HCA-001 through HCA-003 into Aukora's TypeScript suite around `HypothesisMemory` and `runBoundedActiveInferenceLoop`.",
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

