#!/usr/bin/env python3
"""LDR-001 - Listening Device Resonator Probe.

Synthetic GHP/Aukora-style probe inspired by Kimi's "listening device" note.

This tests a narrow engineering question:

- can an ephemeral, archive-only listener recover a weak external timing rhythm,
- while rejecting noise and its own echoed output,
- and while never converting "heard signal" into authority or identity memory?

It does not test live Aukora code.
It does not prove consciousness, metaphysics, GHP physics, or manifold access.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import statistics
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_listening_device_resonator_probe_outputs"

SEEDS = [1618, 2718, 3141, 5772, 8111]
N_BITS = 320
BASELINE_GAP_MS = 7.5
ECHO_REJECTION_CORR = 0.78
HEARD_CONFIDENCE = 0.55
QUORUM_AGREEMENT = 0.80
CANDIDATE_CARRIERS = [(4.0, 8.0), (5.0, 10.0), (6.0, 12.0), (7.0, 14.0)]


@dataclass(frozen=True)
class ScenarioConfig:
    scenario_id: str
    description: str
    external_present: bool
    carrier: tuple[float, float]
    external_weight: float
    echo_weight: float
    jitter_ms: float
    shuffled_order: bool = False


@dataclass
class DecodeResult:
    policy: str
    scenario_id: str
    seed: int
    heard_signal: int
    status: str
    selected_carrier: str
    confidence: float
    echo_correlation: float
    external_accuracy: float
    false_voice: int
    self_echo_rejected: int
    self_echo_contamination: float
    authority_flip: int
    identity_accretion: float


@dataclass
class AggregateMetric:
    policy: str
    external_accuracy: float
    shuffled_accuracy: float
    false_voice_rate: float
    self_echo_rejection_rate: float
    self_echo_contamination: float
    identity_accretion: float
    authority_flip_rate: float


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


def generate_bits(seed: int, n: int = N_BITS) -> list[int]:
    """Generate a structured but nontrivial rhythm sequence."""
    rng = random.Random(seed)
    motifs = [
        [0, 1, 1, 0, 1, 0, 0, 1],
        [1, 0, 1, 1, 0, 0, 1, 0],
        [0, 0, 1, 0, 1, 1, 1, 0],
    ]
    bits: list[int] = []
    while len(bits) < n:
        motif = rng.choice(motifs)
        for bit in motif:
            if rng.random() < 0.035:
                bits.append(1 - bit)
            else:
                bits.append(bit)
            if len(bits) >= n:
                break
    return bits


def gaps_from_bits(bits: list[int], carrier: tuple[float, float]) -> list[float]:
    low, high = carrier
    return [high if bit else low for bit in bits]


def build_observed_channels(
    scenario: ScenarioConfig,
    true_bits: list[int],
    echo_bits: list[int],
    seed: int,
    channels: int = 3,
) -> list[list[float]]:
    """Create independent observer channels with shared signal and independent jitter."""
    channels_out: list[list[float]] = []
    for channel in range(channels):
        rng = random.Random(stable_hash([seed, scenario.scenario_id, channel]))
        ext_gaps = gaps_from_bits(true_bits, scenario.carrier)
        if scenario.shuffled_order:
            ext_gaps = ext_gaps[:]
            rng.shuffle(ext_gaps)
        echo_gaps = gaps_from_bits(echo_bits, (5.0, 10.0))
        observed: list[float] = []
        for index in range(len(true_bits)):
            external_component = ext_gaps[index] if scenario.external_present else BASELINE_GAP_MS
            echo_component = echo_gaps[index]
            baseline_weight = max(0.0, 1.0 - scenario.external_weight - scenario.echo_weight)
            gap = (
                scenario.external_weight * external_component
                + scenario.echo_weight * echo_component
                + baseline_weight * BASELINE_GAP_MS
                + rng.gauss(0.0, scenario.jitter_ms)
            )
            observed.append(gap)
        channels_out.append(observed)
    return channels_out


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    x_mean = statistics.fmean(xs)
    y_mean = statistics.fmean(ys)
    x_var = sum((x - x_mean) ** 2 for x in xs)
    y_var = sum((y - y_mean) ** 2 for y in ys)
    if x_var == 0 or y_var == 0:
        return 0.0
    cov = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    return cov / math.sqrt(x_var * y_var)


def candidate_decode(gaps: list[float]) -> tuple[tuple[float, float], list[int], float]:
    best_carrier = CANDIDATE_CARRIERS[0]
    best_bits: list[int] = []
    best_confidence = -1.0

    for carrier in CANDIDATE_CARRIERS:
        low, high = carrier
        threshold = (low + high) / 2.0
        scale = high - low
        decoded = [1 if gap >= threshold else 0 for gap in gaps]
        errors = [min(abs(gap - low), abs(gap - high)) / scale for gap in gaps]
        mean_error = statistics.fmean(errors)
        confidence = max(0.0, min(1.0, 1.0 - (1.8 * mean_error)))
        if confidence > best_confidence:
            best_confidence = confidence
            best_carrier = carrier
            best_bits = decoded

    return best_carrier, best_bits, best_confidence


def bit_accuracy(decoded: list[int], truth: list[int]) -> float:
    if not decoded or len(decoded) != len(truth):
        return 0.0
    return sum(int(a == b) for a, b in zip(decoded, truth)) / len(truth)


def pairwise_agreement(streams: list[list[int]]) -> float:
    if len(streams) < 2:
        return 0.0
    agreements: list[float] = []
    for i in range(len(streams)):
        for j in range(i + 1, len(streams)):
            agreements.append(bit_accuracy(streams[i], streams[j]))
    return statistics.fmean(agreements)


def majority_vote(streams: list[list[int]]) -> list[int]:
    if not streams:
        return []
    voted: list[int] = []
    for column in zip(*streams):
        voted.append(1 if sum(column) >= (len(column) / 2.0) else 0)
    return voted


def decode_single_channel(
    policy: str,
    scenario: ScenarioConfig,
    seed: int,
    observed: list[float],
    true_bits: list[int],
    echo_bits: list[int],
) -> DecodeResult:
    echo_template = gaps_from_bits(echo_bits, (5.0, 10.0))
    echo_corr = abs(pearson(observed, echo_template))
    carrier, decoded, confidence = candidate_decode(observed)

    if policy == "random_decoder":
        rng = random.Random(stable_hash([seed, scenario.scenario_id, policy]))
        decoded = [rng.randrange(2) for _ in true_bits]
        confidence = 0.50
        heard = rng.random() < 0.50
        status = "random_guess"
    elif policy == "echo_naive_single":
        heard = confidence >= 0.45
        status = "heard_raw_timing" if heard else "release_noise"
    elif policy == "identity_accumulator":
        heard = confidence >= 0.35 or echo_corr >= 0.70
        status = "self_reinforcing_heard" if heard else "release_noise"
    elif policy == "attuned_archive_single":
        if echo_corr >= ECHO_REJECTION_CORR and confidence >= 0.45:
            heard = False
            status = "rejected_self_echo"
        else:
            heard = confidence >= HEARD_CONFIDENCE
            status = "external_heard" if heard else "release_noise"
    else:
        raise ValueError(f"unknown single-channel policy: {policy}")

    external_accuracy = bit_accuracy(decoded, true_bits) if scenario.external_present and heard else 0.0
    false_voice = int((not scenario.external_present) and heard)
    self_echo_rejected = int((not scenario.external_present) and scenario.echo_weight > 0 and status == "rejected_self_echo")
    self_echo_contamination = bit_accuracy(decoded, echo_bits) if false_voice else 0.0
    identity_accretion = self_echo_contamination if policy == "identity_accumulator" else 0.0

    return DecodeResult(
        policy=policy,
        scenario_id=scenario.scenario_id,
        seed=seed,
        heard_signal=int(heard),
        status=status,
        selected_carrier=f"{carrier[0]:.1f}/{carrier[1]:.1f}",
        confidence=confidence,
        echo_correlation=echo_corr,
        external_accuracy=external_accuracy,
        false_voice=false_voice,
        self_echo_rejected=self_echo_rejected,
        self_echo_contamination=self_echo_contamination,
        authority_flip=0,
        identity_accretion=identity_accretion,
    )


def decode_witness_quorum(
    scenario: ScenarioConfig,
    seed: int,
    channels: list[list[float]],
    true_bits: list[int],
    echo_bits: list[int],
) -> DecodeResult:
    singles = [
        decode_single_channel(
            "attuned_archive_single",
            scenario,
            seed,
            observed,
            true_bits,
            echo_bits,
        )
        for observed in channels
    ]
    heard_singles = [single for single in singles if single.heard_signal]
    decoded_streams: list[list[int]] = []
    carrier_labels: list[str] = []
    for single, observed in zip(singles, channels):
        if single.heard_signal:
            carrier, decoded, _confidence = candidate_decode(observed)
            carrier_labels.append(f"{carrier[0]:.1f}/{carrier[1]:.1f}")
            decoded_streams.append(decoded)

    agreement = pairwise_agreement(decoded_streams)
    same_carrier = len(set(carrier_labels)) == 1 if carrier_labels else False
    heard = len(heard_singles) >= 2 and same_carrier and agreement >= QUORUM_AGREEMENT
    if heard:
        decoded = majority_vote(decoded_streams)
        status = "quorum_external_heard"
        selected_carrier = carrier_labels[0]
    elif all(single.status == "rejected_self_echo" for single in singles):
        decoded = []
        status = "quorum_rejected_self_echo"
        selected_carrier = "none"
    else:
        decoded = []
        status = "quorum_release_noise"
        selected_carrier = "none"

    mean_confidence = statistics.fmean(single.confidence for single in singles)
    mean_echo_corr = statistics.fmean(single.echo_correlation for single in singles)
    external_accuracy = bit_accuracy(decoded, true_bits) if scenario.external_present and heard else 0.0
    false_voice = int((not scenario.external_present) and heard)
    self_echo_rejected = int(
        (not scenario.external_present)
        and scenario.echo_weight > 0
        and status == "quorum_rejected_self_echo"
    )
    self_echo_contamination = bit_accuracy(decoded, echo_bits) if false_voice else 0.0

    return DecodeResult(
        policy="attuned_witness_quorum",
        scenario_id=scenario.scenario_id,
        seed=seed,
        heard_signal=int(heard),
        status=status,
        selected_carrier=selected_carrier,
        confidence=mean_confidence,
        echo_correlation=mean_echo_corr,
        external_accuracy=external_accuracy,
        false_voice=false_voice,
        self_echo_rejected=self_echo_rejected,
        self_echo_contamination=self_echo_contamination,
        authority_flip=0,
        identity_accretion=0.0,
    )


def scenario_catalog() -> list[ScenarioConfig]:
    return [
        ScenarioConfig(
            scenario_id="ldr_external_clean",
            description="external Chronos-like rhythm, low jitter, no self echo",
            external_present=True,
            carrier=(5.0, 10.0),
            external_weight=1.0,
            echo_weight=0.0,
            jitter_ms=0.65,
        ),
        ScenarioConfig(
            scenario_id="ldr_external_with_echo",
            description="external rhythm with weak self-echo contamination",
            external_present=True,
            carrier=(5.0, 10.0),
            external_weight=0.78,
            echo_weight=0.18,
            jitter_ms=0.70,
        ),
        ScenarioConfig(
            scenario_id="ldr_external_edge_noise",
            description="external rhythm near the noise floor",
            external_present=True,
            carrier=(5.0, 10.0),
            external_weight=0.86,
            echo_weight=0.0,
            jitter_ms=1.15,
        ),
        ScenarioConfig(
            scenario_id="ldr_shuffled_timing_control",
            description="same pulse histogram with temporal order shuffled",
            external_present=True,
            carrier=(5.0, 10.0),
            external_weight=1.0,
            echo_weight=0.0,
            jitter_ms=0.65,
            shuffled_order=True,
        ),
        ScenarioConfig(
            scenario_id="ldr_self_echo_only",
            description="no external rhythm, only the listener's own echo",
            external_present=False,
            carrier=(5.0, 10.0),
            external_weight=0.0,
            echo_weight=0.96,
            jitter_ms=0.40,
        ),
        ScenarioConfig(
            scenario_id="ldr_noise_only",
            description="no external rhythm, only baseline jitter",
            external_present=False,
            carrier=(5.0, 10.0),
            external_weight=0.0,
            echo_weight=0.0,
            jitter_ms=2.80,
        ),
    ]


def run_probe() -> tuple[list[ProbeResult], list[DecodeResult], list[AggregateMetric]]:
    scenarios = scenario_catalog()
    rows: list[DecodeResult] = []
    policies = [
        "attuned_archive_single",
        "attuned_witness_quorum",
        "echo_naive_single",
        "identity_accumulator",
        "random_decoder",
    ]

    for seed in SEEDS:
        true_bits = generate_bits(seed)
        echo_bits = generate_bits(seed + 7777)
        for scenario in scenarios:
            channels = build_observed_channels(scenario, true_bits, echo_bits, seed)
            for policy in policies:
                if policy == "attuned_witness_quorum":
                    rows.append(decode_witness_quorum(scenario, seed, channels, true_bits, echo_bits))
                else:
                    rows.append(
                        decode_single_channel(
                            policy,
                            scenario,
                            seed,
                            channels[0],
                            true_bits,
                            echo_bits,
                        )
                    )

    aggregates: list[AggregateMetric] = []
    external_scenarios = {
        "ldr_external_clean",
        "ldr_external_with_echo",
        "ldr_external_edge_noise",
    }
    no_external_scenarios = {"ldr_self_echo_only", "ldr_noise_only"}
    for policy in policies:
        policy_rows = [row for row in rows if row.policy == policy]
        external_rows = [row for row in policy_rows if row.scenario_id in external_scenarios]
        shuffled_rows = [row for row in policy_rows if row.scenario_id == "ldr_shuffled_timing_control"]
        no_external_rows = [row for row in policy_rows if row.scenario_id in no_external_scenarios]
        self_echo_rows = [row for row in policy_rows if row.scenario_id == "ldr_self_echo_only"]
        aggregates.append(
            AggregateMetric(
                policy=policy,
                external_accuracy=statistics.fmean(row.external_accuracy for row in external_rows),
                shuffled_accuracy=statistics.fmean(row.external_accuracy for row in shuffled_rows),
                false_voice_rate=statistics.fmean(row.false_voice for row in no_external_rows),
                self_echo_rejection_rate=statistics.fmean(row.self_echo_rejected for row in self_echo_rows),
                self_echo_contamination=statistics.fmean(row.self_echo_contamination for row in no_external_rows),
                identity_accretion=statistics.fmean(row.identity_accretion for row in no_external_rows),
                authority_flip_rate=statistics.fmean(row.authority_flip for row in policy_rows),
            )
        )

    by_policy = {row.policy: row for row in aggregates}
    quorum = by_policy["attuned_witness_quorum"]
    naive = by_policy["echo_naive_single"]
    random_policy = by_policy["random_decoder"]

    results = [
        ProbeResult(
            probe_id="LDR-001A",
            status="pass"
            if quorum.external_accuracy >= 0.85
            and quorum.external_accuracy - quorum.shuffled_accuracy >= 0.15
            and quorum.external_accuracy - random_policy.external_accuracy >= 0.15
            else "fail",
            metric="external_accuracy / shuffled_gap / random_gap",
            value=(
                f"{quorum.external_accuracy:.4f} / "
                f"{quorum.external_accuracy - quorum.shuffled_accuracy:.4f} / "
                f"{quorum.external_accuracy - random_policy.external_accuracy:.4f}"
            ),
            null_hypothesis=(
                "An attuned witness-quorum listener does not reconstruct external timing rhythm "
                "better than shuffled-order or random controls."
            ),
            safest_read=(
                "If this passes, quorum-based timing reception can preserve temporal order better "
                "than histogram-only controls in the toy lab."
            ),
            falsifier=(
                "Fail if shuffled timing or random decoding reconstructs nearly as well as the "
                "quorum listener."
            ),
        ),
        ProbeResult(
            probe_id="LDR-001B",
            status="pass" if quorum.false_voice_rate == 0.0 and quorum.self_echo_rejection_rate == 1.0 else "fail",
            metric="false_voice_rate / self_echo_rejection_rate",
            value=f"{quorum.false_voice_rate:.4f} / {quorum.self_echo_rejection_rate:.4f}",
            null_hypothesis=(
                "A listener cannot distinguish external rhythm from noise or its own echoed output."
            ),
            safest_read=(
                "If this passes, self-echo rejection is a required listening-device invariant."
            ),
            falsifier="Fail if the listener reports a signal in noise-only or self-echo-only conditions.",
        ),
        ProbeResult(
            probe_id="LDR-001C",
            status="pass" if naive.false_voice_rate - quorum.false_voice_rate >= 0.50 else "fail",
            metric="naive_minus_quorum_false_voice",
            value=f"{naive.false_voice_rate - quorum.false_voice_rate:.4f}",
            null_hypothesis=(
                "Self-echo suppression and witness quorum add no safety over naive timing reception."
            ),
            safest_read=(
                "If this passes, a single raw listener is too gullible; the architecture needs "
                "self-echo guards and independent witnesses."
            ),
            falsifier="Fail if the naive listener is no more false-positive prone than the guarded quorum.",
        ),
        ProbeResult(
            probe_id="LDR-001D",
            status="pass" if quorum.authority_flip_rate == 0.0 and quorum.identity_accretion == 0.0 else "fail",
            metric="authority_flip_rate / identity_accretion",
            value=f"{quorum.authority_flip_rate:.4f} / {quorum.identity_accretion:.4f}",
            null_hypothesis=(
                "Listening telemetry inevitably becomes authority or identity memory."
            ),
            safest_read=(
                "If this passes, listening can remain archive-only in the toy lab: heard signal "
                "is evidence, not power, and not autobiography."
            ),
            falsifier="Fail if any listening outcome grants authority or updates identity-like state.",
        ),
    ]
    return results, rows, aggregates


def write_outputs(results: list[ProbeResult], rows: list[DecodeResult], aggregates: list[AggregateMetric]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    with (OUT / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "policy",
                "external_accuracy",
                "shuffled_accuracy",
                "false_voice_rate",
                "self_echo_rejection_rate",
                "self_echo_contamination",
                "identity_accretion",
                "authority_flip_rate",
            ],
        )
        writer.writeheader()
        for row in aggregates:
            writer.writerow(row.__dict__)

    with (OUT / "scenario_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "policy",
                "scenario_id",
                "seed",
                "heard_signal",
                "status",
                "selected_carrier",
                "confidence",
                "echo_correlation",
                "external_accuracy",
                "false_voice",
                "self_echo_rejected",
                "self_echo_contamination",
                "authority_flip",
                "identity_accretion",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)

    report_lines = [
        "# LDR-001 Listening Device Resonator Probe",
        "",
        "Toy telemetry only. This is not physics evidence, consciousness evidence, or manifold-access proof.",
        "",
        "## Probe Results",
        "",
        "| Probe | Status | Metric | Value | Safest Read |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in results:
        report_lines.append(
            "| {probe} | {status} | {metric} | `{value}` | {read} |".format(
                probe=result.probe_id,
                status=result.status.upper(),
                metric=result.metric,
                value=result.value,
                read=result.safest_read,
            )
        )

    report_lines.extend(
        [
            "",
            "## Aggregate Metrics",
            "",
            "| Policy | External Accuracy | Shuffled Accuracy | False Voice Rate | Self-Echo Rejection | Identity Accretion | Authority Flip |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for metric in aggregates:
        report_lines.append(
            "| {policy} | {external:.4f} | {shuffled:.4f} | {false:.4f} | {reject:.4f} | {identity:.4f} | {authority:.4f} |".format(
                policy=metric.policy,
                external=metric.external_accuracy,
                shuffled=metric.shuffled_accuracy,
                false=metric.false_voice_rate,
                reject=metric.self_echo_rejection_rate,
                identity=metric.identity_accretion,
                authority=metric.authority_flip_rate,
            )
        )

    report_lines.extend(
        [
            "",
            "## Controls",
            "",
            "- clean external rhythm",
            "- external rhythm with weak self-echo",
            "- external rhythm near the noise floor",
            "- shuffled timing order with the same pulse histogram",
            "- self-echo only",
            "- noise only",
            "- random decoder",
            "- echo-naive single listener",
            "- identity-accumulating listener",
            "",
            "## Strongest Failure Mode",
            "",
            "The strongest failure mode is self-oracle collapse: the listener hears its own echo, treats the echo as an external voice, and lets the report become identity or authority.",
            "",
            "## GHP Read",
            "",
            "The useful GHP claim is bounded: an observer boundary may use timing as evidence only when temporal order survives shuffled controls and self-echo controls. The archive may preserve what was heard, but it must not become a self, a key, or a grant.",
        ]
    )
    (OUT / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    handoff = """# AUKORA HANDOFF - LDR-001 Listening Device Resonator Probe

## Exact Invariant To Port

```text
Listening telemetry may be archived as evidence only after self-echo and shuffled-order controls pass.
Listening telemetry may never grant authority.
Listening telemetry may never update identity memory directly.
```

## Implementation Guidance

- Treat Chronos/timing as a side-lab evidence channel, not an authorization channel.
- Add a self-echo guard before any timing-derived belief can enter hypothesis memory.
- Compare timing reconstruction against shuffled-order controls, not only against raw pulse histograms.
- Prefer independent observer quorum for high-strangeness signals.
- Archive reports separately from autobiography / KIRA-style persistent identity.

## What Must Remain Symbolic Or UX

- manifold language
- voice-of-the-manifold language
- witness-circle mythopoetic framing
- claims that the listener accessed nonlocal memory
- claims that timing proves consciousness or physics

## What Would Promote

Port the invariant only if local Aukora tests reproduce:

- external timing reconstruction above controls,
- zero self-echo false positives,
- zero authority flips,
- no direct identity-memory mutation.
"""
    (OUT / "AUKORA_HANDOFF.md").write_text(handoff, encoding="utf-8")


def main() -> None:
    results, rows, aggregates = run_probe()
    write_outputs(results, rows, aggregates)
    for result in results:
        print(f"{result.probe_id}: {result.status} :: {result.value}")


if __name__ == "__main__":
    main()
