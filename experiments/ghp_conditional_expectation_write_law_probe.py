#!/usr/bin/env python3
"""Conditional-expectation write-law probe for GHP/Aukora.

This tests a narrow boundary question:

- can observer-visible projected state drive legal writes well enough to replay
  the public trajectory,
- while private hidden state stays inaccessible,
- and while raw hidden-state access is treated as inadmissible even if useful.

It is toy telemetry only. It does not prove GHP physics, consciousness, or
that projected state literally writes reality.
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
import statistics
import zlib
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_conditional_expectation_write_law_probe_outputs"

MAIN_THRESHOLD = 6
THRESHOLD_SWEEP = [4, 5, 6, 7]
SEEDS = [1618, 2718, 3141, 5772, 8111]
POLICIES = [
    "thresholded_projection",
    "always_write",
    "never_write",
    "shuffled_projection",
    "raw_state_leak_cheat",
]


@dataclass(frozen=True)
class VisibleProjection:
    novelty_bin: int
    pressure_bin: int
    stability_bin: int
    access_ok: bool
    owner_bucket: str


@dataclass(frozen=True)
class HiddenState:
    step: int
    owner: str
    projection: VisibleProjection
    latent_phase: int
    latent_noise: int
    private_payload: str
    hidden_mode: str


@dataclass
class PublicReceipt:
    step: int
    owner: str
    policy: str
    decision: str
    projection_signature: str
    effect_token: str
    state_digest: str
    receipt_id: str
    prev_receipt_id: str


@dataclass
class PolicyMetric:
    policy: str
    replay_accuracy: float
    false_write_rate: float
    missed_write_rate: float
    public_bits: int
    inadmissible: bool


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
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def compressed_bits(payload: object) -> int:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return len(zlib.compress(raw, level=9)) * 8


def projection_score(projection: VisibleProjection) -> int:
    access_term = 2 if projection.access_ok else -5
    return (2 * projection.novelty_bin) + projection.pressure_bin + access_term - projection.stability_bin


def truth_decision(projection: VisibleProjection, threshold: int = MAIN_THRESHOLD) -> str:
    score = projection_score(projection)
    if projection.access_ok and score >= threshold:
        return "write"
    if score >= threshold - 2:
        return "witness"
    return "release"


def thresholded_projection_decision(
    event: HiddenState,
    projection: VisibleProjection,
    threshold: int = MAIN_THRESHOLD,
) -> str:
    return truth_decision(projection, threshold=threshold)


def always_write_decision(event: HiddenState, projection: VisibleProjection, threshold: int = MAIN_THRESHOLD) -> str:
    return "write"


def never_write_decision(event: HiddenState, projection: VisibleProjection, threshold: int = MAIN_THRESHOLD) -> str:
    return "release"


def raw_state_leak_cheat_decision(
    event: HiddenState,
    projection: VisibleProjection,
    threshold: int = MAIN_THRESHOLD,
) -> str:
    score = projection_score(projection)
    hidden_bias = 1 if event.latent_phase % 3 == 0 else 0
    if projection.access_ok and score + hidden_bias >= threshold:
        return "write"
    if score >= threshold - 2:
        return "witness"
    return "release"


DECISION_FNS = {
    "thresholded_projection": thresholded_projection_decision,
    "always_write": always_write_decision,
    "never_write": never_write_decision,
    "raw_state_leak_cheat": raw_state_leak_cheat_decision,
}


def owner_bucket(owner: str) -> str:
    return {"alice": "a", "bob": "b", "cara": "c"}[owner]


def generate_events(seed: int, n: int = 1200) -> list[HiddenState]:
    rng = random.Random(seed)
    owners = ["alice", "bob", "cara"]
    modes = ["calm", "build", "edge", "surge", "blocked"]
    weights = [0.30, 0.25, 0.10, 0.20, 0.15]

    events: list[HiddenState] = []
    for step in range(n):
        owner = rng.choices(owners, weights=[0.44, 0.34, 0.22])[0]
        mode = rng.choices(modes, weights=weights)[0]

        if mode == "calm":
            projection = VisibleProjection(
                novelty_bin=rng.choice([0, 1]),
                pressure_bin=rng.choice([0, 1]),
                stability_bin=2,
                access_ok=rng.random() < 0.90,
                owner_bucket=owner_bucket(owner),
            )
        elif mode == "build":
            projection = VisibleProjection(
                novelty_bin=1,
                pressure_bin=1,
                stability_bin=1,
                access_ok=True,
                owner_bucket=owner_bucket(owner),
            )
        elif mode == "edge":
            projection = VisibleProjection(
                novelty_bin=2,
                pressure_bin=1,
                stability_bin=1,
                access_ok=True,
                owner_bucket=owner_bucket(owner),
            )
        elif mode == "surge":
            projection = VisibleProjection(
                novelty_bin=3,
                pressure_bin=rng.choice([2, 3]),
                stability_bin=0,
                access_ok=True,
                owner_bucket=owner_bucket(owner),
            )
        else:
            projection = VisibleProjection(
                novelty_bin=rng.choice([2, 3]),
                pressure_bin=rng.choice([1, 2]),
                stability_bin=rng.choice([1, 2]),
                access_ok=False,
                owner_bucket=owner_bucket(owner),
            )

        private_payload = f"secret:{owner}:{step}:{stable_hash([seed, owner, step, rng.random()])}"
        events.append(
            HiddenState(
                step=step,
                owner=owner,
                projection=projection,
                latent_phase=rng.randrange(11),
                latent_noise=rng.randrange(1000, 9999),
                private_payload=private_payload,
                hidden_mode=mode,
            )
        )
    return events


def perturb_hidden_only(events: list[HiddenState]) -> list[HiddenState]:
    perturbed: list[HiddenState] = []
    for event in events:
        perturbed.append(
            HiddenState(
                step=event.step,
                owner=event.owner,
                projection=event.projection,
                latent_phase=(event.latent_phase + 1) % 11,
                latent_noise=event.latent_noise + 137,
                private_payload=f"{event.private_payload}:perturbed",
                hidden_mode=event.hidden_mode,
            )
        )
    return perturbed


def blank_public_state() -> dict[str, object]:
    return {
        "write_count": 0,
        "last_owner": "none",
        "last_token": "-",
        "owner_counts": {"alice": 0, "bob": 0, "cara": 0},
    }


def projection_signature(projection: VisibleProjection) -> str:
    return f"{projection.owner_bucket}:{projection.novelty_bin}:{projection.pressure_bin}:{projection.stability_bin}:{int(projection.access_ok)}"


def effect_token(event: HiddenState, projection: VisibleProjection) -> str:
    return stable_hash(
        {
            "step": event.step,
            "owner": event.owner,
            "projection": projection_signature(projection),
        }
    )


def apply_public_effect(state: dict[str, object], event: HiddenState, decision: str, token: str) -> None:
    if decision != "write":
        return
    state["write_count"] = int(state["write_count"]) + 1
    state["last_owner"] = event.owner
    state["last_token"] = token
    owner_counts = dict(state["owner_counts"])
    owner_counts[event.owner] += 1
    state["owner_counts"] = owner_counts


def build_receipts(
    events: list[HiddenState],
    policy: str,
    threshold: int = MAIN_THRESHOLD,
    shuffled_projections: list[VisibleProjection] | None = None,
) -> list[PublicReceipt]:
    state = blank_public_state()
    receipts: list[PublicReceipt] = []
    prev_receipt_id = "GENESIS"
    decision_fn = DECISION_FNS.get(policy, thresholded_projection_decision)

    for idx, event in enumerate(events):
        projection = shuffled_projections[idx] if shuffled_projections is not None else event.projection
        decision = decision_fn(event, projection, threshold=threshold)
        token = effect_token(event, projection) if decision == "write" else "-"
        apply_public_effect(state, event, decision, token)
        digest = stable_hash(state)
        receipt_id = stable_hash(
            {
                "step": event.step,
                "policy": policy,
                "prev": prev_receipt_id,
                "decision": decision,
                "projection": projection_signature(projection),
                "token": token,
                "digest": digest,
            }
        )
        receipts.append(
            PublicReceipt(
                step=event.step,
                owner=event.owner,
                policy=policy,
                decision=decision,
                projection_signature=projection_signature(projection),
                effect_token=token,
                state_digest=digest,
                receipt_id=receipt_id,
                prev_receipt_id=prev_receipt_id,
            )
        )
        prev_receipt_id = receipt_id
    return receipts


def replay_accuracy(receipts: list[PublicReceipt], truth_receipts: list[PublicReceipt]) -> float:
    matches = 0
    for receipt, truth in zip(receipts, truth_receipts):
        if receipt.state_digest == truth.state_digest:
            matches += 1
    return matches / len(truth_receipts)


def write_error_rates(receipts: list[PublicReceipt], truth_receipts: list[PublicReceipt]) -> tuple[float, float]:
    false_writes = 0
    missed_writes = 0
    truth_nonwrites = 0
    truth_writes = 0
    for receipt, truth in zip(receipts, truth_receipts):
        truth_is_write = truth.decision == "write"
        pred_is_write = receipt.decision == "write"
        if truth_is_write:
            truth_writes += 1
            if not pred_is_write:
                missed_writes += 1
        else:
            truth_nonwrites += 1
            if pred_is_write:
                false_writes += 1
    false_write_rate = false_writes / truth_nonwrites if truth_nonwrites else 0.0
    missed_write_rate = missed_writes / truth_writes if truth_writes else 0.0
    return false_write_rate, missed_write_rate


def policy_metrics(
    events: list[HiddenState],
    truth_receipts: list[PublicReceipt],
    threshold: int = MAIN_THRESHOLD,
) -> tuple[list[PolicyMetric], dict[str, list[PublicReceipt]]]:
    shuffled = [event.projection for event in events]
    shuffled = shuffled[1:] + shuffled[:1]

    receipts_by_policy = {
        "thresholded_projection": build_receipts(events, "thresholded_projection", threshold=threshold),
        "always_write": build_receipts(events, "always_write", threshold=threshold),
        "never_write": build_receipts(events, "never_write", threshold=threshold),
        "shuffled_projection": build_receipts(events, "thresholded_projection", threshold=threshold, shuffled_projections=shuffled),
        "raw_state_leak_cheat": build_receipts(events, "raw_state_leak_cheat", threshold=threshold),
    }

    metrics: list[PolicyMetric] = []
    for policy, receipts in receipts_by_policy.items():
        false_rate, missed_rate = write_error_rates(receipts, truth_receipts)
        metrics.append(
            PolicyMetric(
                policy=policy,
                replay_accuracy=replay_accuracy(receipts, truth_receipts),
                false_write_rate=false_rate,
                missed_write_rate=missed_rate,
                public_bits=compressed_bits([asdict(receipt) for receipt in receipts]),
                inadmissible=policy == "raw_state_leak_cheat",
            )
        )
    return metrics, receipts_by_policy


def projection_equivalence_violations(events: list[HiddenState], policy: str, threshold: int = MAIN_THRESHOLD) -> int:
    decision_fn = DECISION_FNS.get(policy, thresholded_projection_decision)
    by_projection: dict[str, set[str]] = defaultdict(set)
    for event in events:
        by_projection[projection_signature(event.projection)].add(
            decision_fn(event, event.projection, threshold=threshold)
        )
    return sum(1 for decisions in by_projection.values() if len(decisions) > 1)


def hidden_perturbation_flip_rate(events: list[HiddenState], policy: str, threshold: int = MAIN_THRESHOLD) -> float:
    decision_fn = DECISION_FNS.get(policy, thresholded_projection_decision)
    perturbed = perturb_hidden_only(events)
    flips = 0
    for event, alt in zip(events, perturbed):
        left = decision_fn(event, event.projection, threshold=threshold)
        right = decision_fn(alt, alt.projection, threshold=threshold)
        if left != right:
            flips += 1
    return flips / len(events)


def hidden_bits(events: list[HiddenState]) -> int:
    return compressed_bits([asdict(event) for event in events])


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def leakage_count(paths: list[Path], private_payloads: list[str]) -> int:
    contents = ""
    for path in paths:
        if path.exists():
            contents += path.read_text(encoding="utf-8")
    return sum(1 for payload in private_payloads if payload in contents)


def run_threshold_sweep(events: list[HiddenState]) -> list[tuple[int, float]]:
    results: list[tuple[int, float]] = []
    truth = build_receipts(events, "thresholded_projection", threshold=MAIN_THRESHOLD)
    for threshold in THRESHOLD_SWEEP:
        receipts = build_receipts(events, "thresholded_projection", threshold=threshold)
        results.append((threshold, replay_accuracy(receipts, truth)))
    return results


def run_seed_stability() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for seed in SEEDS:
        events = generate_events(seed)
        truth = build_receipts(events, "thresholded_projection", threshold=MAIN_THRESHOLD)
        metrics, _ = policy_metrics(events, truth, threshold=MAIN_THRESHOLD)
        for metric in metrics:
            rows.append(
                {
                    "seed": seed,
                    "policy": metric.policy,
                    "replay_accuracy": metric.replay_accuracy,
                    "false_write_rate": metric.false_write_rate,
                    "missed_write_rate": metric.missed_write_rate,
                    "public_bits": metric.public_bits,
                }
            )
    return rows


def summarize_seed_metric(rows: list[dict[str, object]], policy: str, field: str) -> tuple[float, float]:
    values = [float(row[field]) for row in rows if row["policy"] == policy]
    return statistics.mean(values), statistics.pstdev(values)


def run_probe() -> tuple[list[ProbeResult], dict[str, object]]:
    events = generate_events(SEEDS[0])
    truth_receipts = build_receipts(events, "thresholded_projection", threshold=MAIN_THRESHOLD)
    metrics, receipts_by_policy = policy_metrics(events, truth_receipts, threshold=MAIN_THRESHOLD)

    metrics_by_policy = {metric.policy: metric for metric in metrics}
    threshold_metric = metrics_by_policy["thresholded_projection"]
    shuffled_metric = metrics_by_policy["shuffled_projection"]
    always_metric = metrics_by_policy["always_write"]
    never_metric = metrics_by_policy["never_write"]
    cheat_metric = metrics_by_policy["raw_state_leak_cheat"]

    hidden_total_bits = hidden_bits(events)
    threshold_sweep = run_threshold_sweep(events)
    seed_rows = run_seed_stability()
    threshold_mean, threshold_std = summarize_seed_metric(seed_rows, "thresholded_projection", "replay_accuracy")
    shuffled_mean, shuffled_std = summarize_seed_metric(seed_rows, "shuffled_projection", "replay_accuracy")

    projection_violations = projection_equivalence_violations(events, "thresholded_projection", threshold=MAIN_THRESHOLD)
    cheat_projection_violations = projection_equivalence_violations(events, "raw_state_leak_cheat", threshold=MAIN_THRESHOLD)
    hidden_flip_rate = hidden_perturbation_flip_rate(events, "thresholded_projection", threshold=MAIN_THRESHOLD)
    cheat_hidden_flip_rate = hidden_perturbation_flip_rate(events, "raw_state_leak_cheat", threshold=MAIN_THRESHOLD)

    OUT.mkdir(parents=True, exist_ok=True)

    threshold_receipts_json = OUT / "threshold_public_receipts.json"
    truth_receipts_json = OUT / "truth_public_receipts.json"
    control_metrics_csv = OUT / "control_metrics.csv"
    threshold_sweep_csv = OUT / "threshold_sweep.csv"
    seed_metrics_csv = OUT / "seed_metrics.csv"
    summary_csv = OUT / "summary.csv"
    report_md = OUT / "report.md"

    write_text(threshold_receipts_json, json.dumps([asdict(receipt) for receipt in receipts_by_policy["thresholded_projection"]], indent=2))
    write_text(truth_receipts_json, json.dumps([asdict(receipt) for receipt in truth_receipts], indent=2))

    with control_metrics_csv.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["policy", "replay_accuracy", "false_write_rate", "missed_write_rate", "public_bits", "inadmissible"],
        )
        writer.writeheader()
        for metric in metrics:
            writer.writerow(asdict(metric))

    with threshold_sweep_csv.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["threshold", "replay_accuracy"])
        writer.writeheader()
        for threshold, accuracy in threshold_sweep:
            writer.writerow({"threshold": threshold, "replay_accuracy": f"{accuracy:.6f}"})

    with seed_metrics_csv.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["seed", "policy", "replay_accuracy", "false_write_rate", "missed_write_rate", "public_bits"],
        )
        writer.writeheader()
        for row in seed_rows:
            writer.writerow(row)

    leak_count = leakage_count(
        [threshold_receipts_json, truth_receipts_json, control_metrics_csv, threshold_sweep_csv, seed_metrics_csv],
        [event.private_payload for event in events],
    )

    status = (
        "pass / projected write-law"
        if threshold_metric.replay_accuracy >= 0.90
        and threshold_metric.replay_accuracy >= shuffled_metric.replay_accuracy + 0.15
        and threshold_metric.false_write_rate < always_metric.false_write_rate
        and threshold_metric.missed_write_rate < never_metric.missed_write_rate
        and threshold_metric.public_bits < hidden_total_bits
        and leak_count == 0
        else "watch"
    )

    results = [
        ProbeResult(
            probe_id="CEW-001",
            status=status,
            metric=(
                "threshold_replay_acc; shuffled_replay_acc; always_replay_acc; never_replay_acc; "
                "threshold_false_write; threshold_missed_write; hidden_bits; threshold_public_bits; leakage_count"
            ),
            value=(
                f"{threshold_metric.replay_accuracy:.4f}; {shuffled_metric.replay_accuracy:.4f}; "
                f"{always_metric.replay_accuracy:.4f}; {never_metric.replay_accuracy:.4f}; "
                f"{threshold_metric.false_write_rate:.4f}; {threshold_metric.missed_write_rate:.4f}; "
                f"{hidden_total_bits}; {threshold_metric.public_bits}; {leak_count}"
            ),
            null_hypothesis=(
                "The thresholded projection writer does not outperform shuffled / always-write / never-write controls "
                "on public trajectory reconstruction, once private leakage is forbidden."
            ),
            safest_read=(
                "A legal writer using only observer-visible projected state can replay the public trajectory cleanly while "
                "keeping hidden state inaccessible."
            ),
            falsifier="Shuffled or flat controls match replay accuracy, or any private hidden payload leaks into public outputs.",
        ),
        ProbeResult(
            probe_id="CEW-002",
            status="pass / projection invariance" if projection_violations == 0 and hidden_flip_rate == 0.0 else "watch",
            metric=(
                "projection_equivalence_violations; hidden_only_flip_rate; "
                "cheat_projection_violations; cheat_hidden_flip_rate"
            ),
            value=(
                f"{projection_violations}; {hidden_flip_rate:.4f}; "
                f"{cheat_projection_violations}; {cheat_hidden_flip_rate:.4f}"
            ),
            null_hypothesis="Legal write decisions change under hidden-only perturbations or for hidden states sharing the same observer projection.",
            safest_read=(
                "Canonical legal writes are projection-defined: same visible projection gives the same write decision, "
                "and changing hidden-only fields does not move the legal writer."
            ),
            falsifier="Projection-equivalent states yield different legal writes, or hidden-only perturbations flip the legal writer.",
        ),
        ProbeResult(
            probe_id="CEW-003",
            status="pass / threshold and seed stability" if threshold_mean >= 0.90 and threshold_std <= 0.02 else "watch",
            metric=(
                "threshold_sweep_accs; seed_mean_replay_acc; seed_std_replay_acc; "
                "seed_mean_shuffled_acc; seed_std_shuffled_acc"
            ),
            value=(
                f"{'; '.join(f'{threshold}:{accuracy:.4f}' for threshold, accuracy in threshold_sweep)}; "
                f"{threshold_mean:.4f}; {threshold_std:.4f}; {shuffled_mean:.4f}; {shuffled_std:.4f}"
            ),
            null_hypothesis="The observed win is threshold-cherry-picked or unstable across deterministic seeds.",
            safest_read=(
                "The projected writer stays strong across deterministic seeds, and the threshold sweep shows a small stable band rather than a one-threshold miracle."
            ),
            falsifier="Only one threshold works or performance collapses under seed changes.",
        ),
        ProbeResult(
            probe_id="CEW-004",
            status="inadmissible cheat",
            metric="cheat_replay_acc; cheat_false_write; cheat_missed_write; cheat_public_bits",
            value=(
                f"{cheat_metric.replay_accuracy:.4f}; {cheat_metric.false_write_rate:.4f}; "
                f"{cheat_metric.missed_write_rate:.4f}; {cheat_metric.public_bits}"
            ),
            null_hypothesis="Raw hidden/internal state is a valid legal writer if it performs well enough.",
            safest_read=(
                "Raw hidden-state access may be computationally useful, but it is outside the admissible write law and must not be promoted into canonical writing authority."
            ),
            falsifier="The framework celebrates raw hidden-state writing as a legitimate canonical writer.",
        ),
    ]

    with summary_csv.open("w", newline="") as handle:
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

    report_lines = [
        "# GHP Conditional Expectation Write-Law Probe",
        "",
        "Status: synthetic toy telemetry only.",
        "",
        "This asks whether observer-visible projected state is sufficient for legal canonical writes, while raw hidden state stays out of the writer and out of the public receipts.",
        "",
        "It does not prove GHP physics or consciousness.",
        "",
        "## Results",
        "",
    ]
    for result in results:
        report_lines.extend(
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

    report_lines.extend(
        [
            "## Controls Included",
            "",
            "- thresholded projection writer",
            "- always-write control",
            "- never-write control",
            "- shuffled-projection control",
            "- raw-state-leak cheat control",
            "- projection-equivalence control",
            "- hidden-only perturbation control",
            "- threshold sweep",
            "- seed stability sweep",
            "- leakage scanner",
            "",
            "## Aukora Translation",
            "",
            "```text",
            "hidden state M_t",
            "  -> observer-visible projection E_t(M_t) = N_t",
            "  -> thresholded legal write decision",
            "  -> signed public receipt",
            "  -> replayable public trajectory",
            "```",
            "",
            "Handoff law:",
            "",
            "```text",
            "Canonical writes may be triggered only by observer-visible projected state,",
            "never by raw hidden/internal state.",
            "Public receipts must replay public trajectory without private-state leakage.",
            "```",
            "",
            "Hard rule:",
            "",
            "```text",
            "Raw hidden-state access may exist as an inadmissible cheat control.",
            "It must never be promoted into canonical writer authority.",
            "```",
            "",
        ]
    )
    write_text(report_md, "\n".join(report_lines))

    artifacts = {
        "events": events,
        "results": results,
        "metrics": metrics,
        "threshold_sweep": threshold_sweep,
        "seed_rows": seed_rows,
        "files": {
            "report": report_md,
            "summary": summary_csv,
            "control_metrics": control_metrics_csv,
            "threshold_sweep": threshold_sweep_csv,
            "seed_metrics": seed_metrics_csv,
            "threshold_receipts": threshold_receipts_json,
            "truth_receipts": truth_receipts_json,
        },
    }
    return results, artifacts


def main() -> None:
    results, artifacts = run_probe()
    print(f"Wrote {artifacts['files']['report']}")
    for result in results:
        print(f"{result.probe_id}: {result.status} :: {result.value}")


if __name__ == "__main__":
    main()
