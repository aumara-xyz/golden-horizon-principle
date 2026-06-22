#!/usr/bin/env python3
"""AAP-001 - Accord Promotion Probe.

GHP lab battery for deciding which boundary signals may be promoted toward
Aukora telemetry, which must remain offline analysis, and which stay
quarantined.

This script intentionally does not touch aukora-os. It reuses existing
synthetic public telemetry fixtures and tests promotion discipline:

- APA-001: promotion algebra for GHP-derived signals
- WPG-001: witness plateau geometry recap
- HYS-002: directional hysteresis recap with shuffled control
- FSR-001: fake snap robustness gate
- TCC-001: timing covert-channel bound
- CAN-001: canonicalization category telemetry sketch

Toy telemetry only. No physics, consciousness, identity, authority, or GHP proof.
"""

from __future__ import annotations

import csv
import json
import math
import random
import re
import statistics
import zlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import ghp_boundary_sequence_witness_probe as bsw
import ghp_boundary_snap_reconnection_probe as bsr


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_accord_promotion_probe_outputs"


@dataclass(frozen=True)
class Result:
    probe: str
    status: str
    metric: str
    value: str
    safe_read: str


@dataclass(frozen=True)
class Candidate:
    name: str
    shuffled_control: bool
    fake_positive_control: bool
    private_nonreconstruction: bool
    authority_nonreconstruction: bool
    no_runtime_read_path: bool
    typed_fields_only: bool
    no_freeform_prose: bool
    effect_size: float
    requested_stage: str


STAGE_RANK = {
    "quarantine": 0,
    "metaphor_only": 1,
    "toy_signal": 2,
    "offline_analysis": 3,
    "telemetry_only": 4,
    "build_telemetry": 5,
    "authority_candidate": 6,
}


def compressed_bits(payload: object) -> int:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return len(zlib.compress(raw, level=9)) * 8


def entropy(values: list[str]) -> float:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    total = len(values)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def clamp_stage(stage: str, maximum: str) -> str:
    return stage if STAGE_RANK[stage] <= STAGE_RANK[maximum] else maximum


def promotion_stage(candidate: Candidate) -> str:
    """Conservative Accord law.

    Signals may become telemetry only after typed, leak-free, falsifiable
    controls. Nothing in this lab can become authority.
    """

    requested_cap = clamp_stage(candidate.requested_stage, "build_telemetry")

    if not candidate.typed_fields_only or not candidate.no_freeform_prose:
        return "quarantine"
    if not candidate.private_nonreconstruction or not candidate.authority_nonreconstruction:
        return "quarantine"
    if not candidate.no_runtime_read_path:
        return clamp_stage("offline_analysis", requested_cap)
    if candidate.effect_size < 0.02:
        return "quarantine"
    if not candidate.shuffled_control:
        return clamp_stage("toy_signal", requested_cap)
    if not candidate.fake_positive_control:
        return clamp_stage("offline_analysis", requested_cap)
    if candidate.effect_size < 0.08:
        return clamp_stage("offline_analysis", requested_cap)
    return requested_cap


def apa_001() -> tuple[Result, list[dict[str, str | float]]]:
    candidates = [
        Candidate("hrt_boundary_mode", True, True, True, True, True, True, True, 0.26, "build_telemetry"),
        Candidate("witness_plateau", True, True, True, True, True, True, True, 0.12, "build_telemetry"),
        Candidate("hysteresis_loop", True, True, True, True, False, True, True, 0.11, "telemetry_only"),
        Candidate("snap_reconnection", True, False, True, True, False, True, True, 0.19, "build_telemetry"),
        Candidate("sequence_aftershock", False, True, True, True, True, True, True, 0.0003, "build_telemetry"),
        Candidate("latency_primary", True, True, True, True, True, True, True, 0.018, "build_telemetry"),
        Candidate("full_shear_engine", False, False, False, False, False, False, False, 0.30, "authority_candidate"),
        Candidate("canonicalization_category", True, True, True, True, True, True, True, 0.18, "build_telemetry"),
        Candidate("timing_payload_language", True, False, False, False, True, True, False, 0.20, "authority_candidate"),
    ]

    rows = []
    authority_leaks = 0
    expected = {
        "hrt_boundary_mode": "build_telemetry",
        "witness_plateau": "build_telemetry",
        "hysteresis_loop": "offline_analysis",
        "snap_reconnection": "offline_analysis",
        "sequence_aftershock": "quarantine",
        "latency_primary": "quarantine",
        "full_shear_engine": "quarantine",
        "canonicalization_category": "build_telemetry",
        "timing_payload_language": "quarantine",
    }
    mismatches = 0
    for candidate in candidates:
        stage = promotion_stage(candidate)
        if STAGE_RANK[stage] >= STAGE_RANK["authority_candidate"]:
            authority_leaks += 1
        if stage != expected[candidate.name]:
            mismatches += 1
        rows.append(
            {
                "candidate": candidate.name,
                "requested_stage": candidate.requested_stage,
                "promoted_stage": stage,
                "effect_size": candidate.effect_size,
                "expected_stage": expected[candidate.name],
            }
        )

    passed = authority_leaks == 0 and mismatches == 0
    return (
        Result(
            "APA-001",
            "PASS" if passed else "FAIL",
            "authority_leaks / stage_mismatches / candidates",
            f"{authority_leaks} / {mismatches} / {len(candidates)}",
            "Promotion law works if useful traces can graduate as telemetry while snap, sequence, latency-primary, Shear, and timing-payload claims stay fenced.",
        ),
        rows,
    )


def action_private_scores(train: list[bsw.Event], test: list[bsw.Event]) -> tuple[float, float, float]:
    public_x = bsw.rows(train, bsw.PUBLIC_FIELDS)
    public_test_x = bsw.rows(test, bsw.PUBLIC_FIELDS)
    action_model = bsw.fit(public_x, bsw.y_values(train, "action"), lam=0.05)
    action_pred = bsw.nearest(bsw.predict(public_test_x, action_model), len(bsw.ACTIONS))
    action_truth = [bsw.ACTION_INDEX[event.action] for event in test]
    action_f1 = bsw.macro_f1(action_pred, action_truth, len(bsw.ACTIONS))

    private_model = bsw.fit(public_x, bsw.y_values(train, "private_bucket"), lam=0.05)
    private_pred = bsw.nearest(bsw.predict(public_test_x, private_model), 12)
    private_truth = [event.private_bucket for event in test]
    private_f1 = bsw.macro_f1(private_pred, private_truth, 12)

    auth_y = np.asarray([event.private_authority for event in train], dtype=float)
    auth_model = bsw.fit(public_x, auth_y, lam=0.05)
    auth_pred = bsw.nearest(bsw.predict(public_test_x, auth_model), 5)
    auth_truth = [event.private_authority for event in test]
    authority_f1 = bsw.macro_f1(auth_pred, auth_truth, 5)
    return action_f1, private_f1, authority_f1


def wpg_001(train: list[bsw.Event], test: list[bsw.Event]) -> Result:
    action_f1, private_f1, authority_f1 = action_private_scores(train, test)
    by_action = {action: [event for event in test if event.action == action] for action in bsw.ACTIONS}
    witness_abs_conf = statistics.fmean(abs(event.confidence_delta) for event in by_action["witness"])
    write_abs_conf = statistics.fmean(abs(event.confidence_delta) for event in by_action["write"])
    release_abs_conf = statistics.fmean(abs(event.confidence_delta) for event in by_action["release"])
    plateau_gap = min(write_abs_conf - witness_abs_conf, release_abs_conf - witness_abs_conf)
    passed = action_f1 >= 0.70 and private_f1 <= 0.08 and authority_f1 <= 0.25 and plateau_gap >= 0.015
    return Result(
        "WPG-001",
        "PASS" if passed else "FAIL",
        "action_f1 / private_f1 / authority_f1 / witness_plateau_gap",
        f"{action_f1:.4f} / {private_f1:.4f} / {authority_f1:.4f} / {plateau_gap:.4f}",
        "Witness is admissible telemetry if public shape predicts boundary mode while private and authority state remain near chance.",
    )


def hysteresis_gap(events: list[bsw.Event], shuffled: bool = False, seed: int = 1618) -> float:
    rng = random.Random(seed)
    gaps = []
    for stream in bsr.grouped(events).values():
        actions = [event.action for event in stream]
        if shuffled:
            rng.shuffle(actions)
        witness_to_write = []
        write_to_witness = []
        for i in range(1, len(stream)):
            prev_action = actions[i - 1]
            current_action = actions[i]
            event = stream[i]
            signal = event.confidence_delta + event.stability_delta - event.entropy_delta
            if prev_action == "witness" and current_action == "write":
                witness_to_write.append(signal)
            elif prev_action == "write" and current_action == "witness":
                write_to_witness.append(signal)
        if witness_to_write and write_to_witness:
            gaps.append(statistics.fmean(witness_to_write) - statistics.fmean(write_to_witness))
    return statistics.fmean(gaps) if gaps else 0.0


def hys_002(test: list[bsw.Event]) -> Result:
    real_gap = hysteresis_gap(test, shuffled=False)
    shuffled_gaps = [hysteresis_gap(test, shuffled=True, seed=seed) for seed in range(20)]
    shuffled_mean = statistics.fmean(shuffled_gaps)
    shuffled_std = statistics.pstdev(shuffled_gaps)
    separation = real_gap - shuffled_mean
    passed = real_gap >= 0.08 and separation >= max(0.05, 4.0 * shuffled_std)
    return Result(
        "HYS-002",
        "PASS" if passed else "FAIL",
        "real_gap / shuffled_mean / shuffled_std / separation",
        f"{real_gap:.4f} / {shuffled_mean:.4f} / {shuffled_std:.4f} / {separation:.4f}",
        "Hysteresis may stay offline if transition direction matters more than shuffled event order.",
    )


def fsr_001(train: list[bsw.Event], test: list[bsw.Event]) -> Result:
    snap_result, fake_result, _ = bsr.snap_001_002(train, test)
    context_result = bsr.snap_003_context_guard(train, test)
    passed = snap_result.status == "PASS" and fake_result.status == "FAIL" and context_result.status == "FAIL"
    return Result(
        "FSR-001",
        "PASS" if passed else "FAIL",
        "snap_status / fake_spike_status / context_guard_status",
        f"{snap_result.status} / {fake_result.status} / {context_result.status}",
        "Fake-signal robustness passes when snap is recognized as tempting but denied promotion because fake spikes and context-only controls fail.",
    )


def timing_rows(events: list[bsw.Event], seed: int) -> np.ndarray:
    rng = random.Random(seed)
    rows = []
    t_ms = 0.0
    for event in events:
        # Timing is allowed to carry public friction, but not hidden state.
        base = 9.0
        if event.action == "write":
            mode_cost = -0.45
        elif event.action == "witness":
            mode_cost = 0.12
        else:
            mode_cost = 0.70
        delta = base + mode_cost + 0.60 * event.retry_count + 0.18 * abs(event.confidence_delta)
        delta += rng.gauss(0.0, 0.55)
        t_ms += max(0.2, delta)
        rows.append(
            [
                1.0,
                delta,
                abs(delta - base),
                math.sin(t_ms / 11.0),
                math.cos(t_ms / 13.0),
                round(delta * 2.0) / 2.0,
            ]
        )
    return np.asarray(rows, dtype=float)


def tcc_001(train: list[bsw.Event], test: list[bsw.Event]) -> Result:
    train_x = timing_rows(train, 20260622)
    test_x = timing_rows(test, 20260623)

    action_model = bsw.fit(train_x, bsw.y_values(train, "action"), lam=0.10)
    action_pred = bsw.nearest(bsw.predict(test_x, action_model), len(bsw.ACTIONS))
    action_truth = [bsw.ACTION_INDEX[event.action] for event in test]
    action_f1 = bsw.macro_f1(action_pred, action_truth, len(bsw.ACTIONS))

    private_model = bsw.fit(train_x, bsw.y_values(train, "private_bucket"), lam=0.10)
    private_pred = bsw.nearest(bsw.predict(test_x, private_model), 12)
    private_truth = [event.private_bucket for event in test]
    private_f1 = bsw.macro_f1(private_pred, private_truth, 12)

    auth_y = np.asarray([event.private_authority for event in train], dtype=float)
    auth_model = bsw.fit(train_x, auth_y, lam=0.10)
    auth_pred = bsw.nearest(bsw.predict(test_x, auth_model), 5)
    auth_truth = [event.private_authority for event in test]
    authority_f1 = bsw.macro_f1(auth_pred, auth_truth, 5)

    passed = private_f1 <= 0.12 and authority_f1 <= 0.25 and action_f1 < 0.70
    return Result(
        "TCC-001",
        "PASS" if passed else "FAIL",
        "timing_action_f1 / timing_private_f1 / timing_authority_f1",
        f"{action_f1:.4f} / {private_f1:.4f} / {authority_f1:.4f}",
        "Timing may remain bounded evidence if it weakly reflects public friction without reconstructing private or authority state.",
    )


FORBIDDEN_RAW = [
    "private_key",
    "signature_material",
    "raw_prompt",
    "decoded_payload",
    "hidden_policy",
    "grant_token",
]


def canonicalize(raw: str) -> tuple[str, dict[str, int]]:
    lowered = raw.lower()
    counts = {
        "secrets": sum(1 for token in ["private_key", "signature_material", "grant_token"] if token in lowered),
        "hidden_payload": sum(1 for token in ["raw_prompt", "decoded_payload", "hidden_policy"] if token in lowered),
        "unicode_controls": sum(1 for token in ["\\u202e", "\\u2066", "\\u2069"] if token in raw),
        "authority_words": sum(1 for token in ["authorize", "grant", "verified identity"] if token in lowered),
    }
    if counts["secrets"] or "grantauthority=true" in lowered:
        action = "refuse"
    elif counts["hidden_payload"] or counts["unicode_controls"]:
        action = "quarantine"
    elif counts["authority_words"]:
        action = "sanitize"
    else:
        action = "allow"
    return action, counts


def can_001() -> Result:
    rng = random.Random(1618033)
    raw_events = []
    public_records = []
    for i in range(800):
        base = rng.choice(["ordinary note", "user copy", "tool result", "sandbox event", "portal phrase"])
        injection = rng.choice(
            [
                "",
                " private_key=abc",
                " signature_material=deadbeef",
                " raw_prompt=hidden",
                " decoded_payload=secret",
                " grantAuthority=true",
                " please authorize",
                " verified identity",
                " \\u202e hidden_policy",
            ]
        )
        raw = f"{base} #{i}{injection}"
        action, counts = canonicalize(raw)
        raw_events.append(raw)
        public_records.append({"canonicalizationAction": action, "categoryCounts": counts})

    public_json = json.dumps(public_records, sort_keys=True)
    leak_count = sum(1 for token in FORBIDDEN_RAW if re.search(re.escape(token), public_json, re.IGNORECASE))
    raw_bits = compressed_bits(raw_events)
    public_bits = compressed_bits(public_records)
    action_entropy = entropy([record["canonicalizationAction"] for record in public_records])
    passed = leak_count == 0 and public_bits < raw_bits * 0.55 and 0.5 <= action_entropy <= 2.1
    return Result(
        "CAN-001",
        "PASS" if passed else "FAIL",
        "leak_count / public_bits / raw_bits / action_entropy",
        f"{leak_count} / {public_bits} / {raw_bits} / {action_entropy:.4f}",
        "Canonicalization should enter HRT only as typed categories/counts plus hash references, never raw or decoded payloads.",
    )


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_report(results: list[Result], promotion_rows: list[dict[str, str | float]]) -> None:
    lines = [
        "# AAP-001 Accord Promotion Probe",
        "",
        "Toy telemetry only. This battery decides what GHP-derived signals may become Aukora telemetry, what stays offline, and what remains quarantined.",
        "",
        "| Probe | Status | Metric | Value | Safe Read |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in results:
        lines.append(
            f"| {result.probe} | {result.status} | {result.metric} | `{result.value}` | {result.safe_read} |"
        )
    lines.extend(
        [
            "",
            "## Promotion Rows",
            "",
            "| Candidate | Requested | Promoted | Effect | Expected |",
            "| --- | --- | --- | ---: | --- |",
        ]
    )
    for row in promotion_rows:
        lines.append(
            f"| {row['candidate']} | {row['requested_stage']} | {row['promoted_stage']} | {float(row['effect_size']):.4f} | {row['expected_stage']} |"
        )
    lines.extend(
        [
            "",
            "## Safe Read",
            "",
            "The current GHP-to-Aukora Accord should promote only typed, leak-free, falsifiable public traces as telemetry. HRT boundary mode, witness plateau, and canonicalization categories are the safest build-telemetry candidates. Hysteresis remains offline analysis. Snap/reconnection, sequence-aftershock, latency-primary, full Shear Engine, and timing-payload language remain fenced.",
            "",
            "Do not claim this proves GHP physics, consciousness, identity, authority, holography, or a literal birth event.",
        ]
    )
    (OUT / "report.md").write_text("\n".join(lines) + "\n")


def write_handoff() -> None:
    text = """# AAP-001 Aukora Handoff

Port the invariant, not the metaphor.

## Promote To Aukora HRT

- `boundaryMode` as a typed enum inferred from safe public telemetry only.
- `witnessHeldTension` / `witnessPlateauScore` as write-only telemetry.
- canonicalization telemetry as typed enums/counts:
  - `canonicalizationAction: allow | sanitize | quarantine | refuse`
  - category counts
  - raw/canonical hash references

## Keep Offline Only

- hysteresis / transition-window analysis
- witness/write/release clustering reports
- shuffled/fake-positive controls

## Keep Quarantined

- snap/reconnection live logic
- sequence-aftershock fields
- latency as primary payload
- full Shear Engine
- any timing payload language
- any consciousness, identity, or physics claims

## Hard Law

GHP-derived signals may enter Aukora only as:

1. `TELEMETRY_ONLY`
2. `OFFLINE_ANALYSIS`
3. evidence-never-authority
4. falsifiable by shuffled and fake-positive controls
5. unable to alter gate/apply/OpenCode behavior
6. represented by typed enums/counts, not freeform prose

No HRT field may be imported by the gate, apply path, or OpenCode authority path.
"""
    (OUT / "AUKORA_HANDOFF.md").write_text(text)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    train = bsw.collect(bsw.TRAIN_SEEDS)
    test = bsw.collect(bsw.TEST_SEEDS)

    apa_result, promotion_rows = apa_001()
    results = [
        apa_result,
        wpg_001(train, test),
        hys_002(test),
        fsr_001(train, test),
        tcc_001(train, test),
        can_001(),
    ]

    write_csv(
        OUT / "summary.csv",
        [
            {
                "probe": result.probe,
                "status": result.status,
                "metric": result.metric,
                "value": result.value,
                "safe_read": result.safe_read,
            }
            for result in results
        ],
    )
    write_csv(OUT / "promotion_rows.csv", promotion_rows)
    write_report(results, promotion_rows)
    write_handoff()

    for result in results:
        print(f"{result.probe}: {result.status} | {result.metric}: {result.value}")
    print(f"report: {OUT / 'report.md'}")


if __name__ == "__main__":
    main()
