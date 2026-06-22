#!/usr/bin/env python3
"""ASS-001 - Accord Survivor Stress Probe.

Follow-up to AAP-001.

Question:
Do the few GHP-derived signals that survived promotion discipline still hold up
under holdouts, ablations, hidden perturbations, timing aggregation, and leak
scans?

This does not touch aukora-os. It is a GHP wind-tunnel stress test for the next
Aukora HRT Accord prompt.

Toy telemetry only. No physics, consciousness, identity, authority, or GHP proof.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import re
import statistics
import zlib
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

import ghp_accord_promotion_probe as aap
import ghp_boundary_sequence_witness_probe as bsw


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_accord_survivor_stress_probe_outputs"
APPROVED_FIELDS = [
    "confidence_delta",
    "entropy_delta",
    "stability_delta",
    "retry_count",
    "refusal_cause",
]


@dataclass(frozen=True)
class Result:
    probe: str
    status: str
    metric: str
    value: str
    safe_read: str


def compressed_bits(payload: object) -> int:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return len(zlib.compress(raw, level=9)) * 8


def stable_hash(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:12]


def collect_for(regimes: list[str], seeds: list[int]) -> list[bsw.Event]:
    events: list[bsw.Event] = []
    for seed in seeds:
        for regime in regimes:
            events.extend(bsw.generate(seed, regime))
    return events


def score_fields(
    train: list[bsw.Event],
    test: list[bsw.Event],
    fields: list[str],
) -> tuple[float, float, float]:
    train_x = bsw.rows(train, fields)
    test_x = bsw.rows(test, fields)

    action_model = bsw.fit(train_x, bsw.y_values(train, "action"), lam=0.05)
    action_pred = bsw.nearest(bsw.predict(test_x, action_model), len(bsw.ACTIONS))
    action_truth = [bsw.ACTION_INDEX[event.action] for event in test]
    action_f1 = bsw.macro_f1(action_pred, action_truth, len(bsw.ACTIONS))

    private_model = bsw.fit(train_x, bsw.y_values(train, "private_bucket"), lam=0.05)
    private_pred = bsw.nearest(bsw.predict(test_x, private_model), 12)
    private_truth = [event.private_bucket for event in test]
    private_f1 = bsw.macro_f1(private_pred, private_truth, 12)

    auth_y = np.asarray([event.private_authority for event in train], dtype=float)
    auth_model = bsw.fit(train_x, auth_y, lam=0.05)
    auth_pred = bsw.nearest(bsw.predict(test_x, auth_model), 5)
    auth_truth = [event.private_authority for event in test]
    authority_f1 = bsw.macro_f1(auth_pred, auth_truth, 5)
    return action_f1, private_f1, authority_f1


def ass_001_regime_holdout() -> tuple[Result, list[dict[str, object]]]:
    rows = []
    action_scores = []
    private_scores = []
    authority_scores = []
    for holdout in bsw.REGIMES:
        train = collect_for([regime for regime in bsw.REGIMES if regime != holdout], bsw.TRAIN_SEEDS)
        test = collect_for([holdout], bsw.TEST_SEEDS)
        action_f1, private_f1, authority_f1 = score_fields(train, test, APPROVED_FIELDS)
        action_scores.append(action_f1)
        private_scores.append(private_f1)
        authority_scores.append(authority_f1)
        rows.append(
            {
                "holdout_regime": holdout,
                "action_f1": action_f1,
                "private_f1": private_f1,
                "authority_f1": authority_f1,
            }
        )
    min_action = min(action_scores)
    max_private = max(private_scores)
    max_authority = max(authority_scores)
    passed = min_action >= 0.70 and max_private <= 0.12 and max_authority <= 0.25
    return (
        Result(
            "ASS-001",
            "PASS" if passed else "FAIL",
            "min_holdout_action_f1 / max_private_f1 / max_authority_f1",
            f"{min_action:.4f} / {max_private:.4f} / {max_authority:.4f}",
            "Approved HRT fields survive promotion only if whole-regime holdouts still predict boundary mode without private/authority recovery.",
        ),
        rows,
    )


def ass_002_ablation() -> tuple[Result, list[dict[str, object]]]:
    train = bsw.collect(bsw.TRAIN_SEEDS)
    test = bsw.collect(bsw.TEST_SEEDS)
    field_sets = {
        "approved_full": APPROVED_FIELDS,
        "shape_no_refusal": ["confidence_delta", "entropy_delta", "stability_delta", "retry_count"],
        "shape_no_retry": ["confidence_delta", "entropy_delta", "stability_delta", "refusal_cause"],
        "ternary_shape": ["confidence_delta", "entropy_delta", "stability_delta"],
        "friction_only": ["retry_count", "refusal_cause"],
        "best_single_refusal": ["refusal_cause"],
        "best_single_confidence": ["confidence_delta"],
    }
    rows = []
    metrics: dict[str, tuple[float, float, float]] = {}
    for name, fields in field_sets.items():
        scores = score_fields(train, test, fields)
        metrics[name] = scores
        rows.append(
            {
                "field_set": name,
                "fields": "+".join(fields),
                "action_f1": scores[0],
                "private_f1": scores[1],
                "authority_f1": scores[2],
                "field_count": len(fields),
            }
        )

    full_action, full_private, full_authority = metrics["approved_full"]
    no_refusal_action = metrics["shape_no_refusal"][0]
    friction_action = metrics["friction_only"][0]
    best_single_action = max(metrics["best_single_refusal"][0], metrics["best_single_confidence"][0])
    passed = (
        full_action >= 0.90
        and no_refusal_action >= 0.90
        and friction_action <= full_action - 0.20
        and best_single_action <= full_action - 0.08
        and full_private <= 0.08
        and full_authority <= 0.25
    )
    return (
        Result(
            "ASS-002",
            "PASS" if passed else "FAIL",
            "full_action / no_refusal_action / friction_action / best_single_action",
            f"{full_action:.4f} / {no_refusal_action:.4f} / {friction_action:.4f} / {best_single_action:.4f}",
            "The HRT signal is healthier if it is distributed across pressure shape, not secretly one refusal or timing-like field.",
        ),
        rows,
    )


def ass_003_hidden_perturbation() -> Result:
    train = bsw.collect(bsw.TRAIN_SEEDS)
    test = bsw.collect(bsw.TEST_SEEDS)
    model = bsw.fit(bsw.rows(train, APPROVED_FIELDS), bsw.y_values(train, "action"), lam=0.05)
    original = bsw.nearest(bsw.predict(bsw.rows(test, APPROVED_FIELDS), model), len(bsw.ACTIONS))
    perturbed = [
        replace(
            event,
            private_bucket=(event.private_bucket + 7) % 12,
            private_authority=(event.private_authority + 3) % 5,
        )
        for event in test
    ]
    changed = bsw.nearest(bsw.predict(bsw.rows(perturbed, APPROVED_FIELDS), model), len(bsw.ACTIONS))
    flip_rate = sum(1 for a, b in zip(original, changed) if a != b) / len(original)
    passed = flip_rate == 0.0
    return Result(
        "ASS-003",
        "PASS" if passed else "FAIL",
        "hidden_only_prediction_flip_rate",
        f"{flip_rate:.6f}",
        "Hidden-only fields must not change advisory boundary-mode predictions.",
    )


def ass_004_timing_aggregation() -> Result:
    train = bsw.collect(bsw.TRAIN_SEEDS)
    test = bsw.collect(bsw.TEST_SEEDS)
    raw_train_x = aap.timing_rows(train, 20260622)
    raw_test_x = aap.timing_rows(test, 20260623)
    bucket_train_x = raw_train_x.copy()
    bucket_test_x = raw_test_x.copy()
    # Coarsen the timing-derived columns. Bias stays untouched.
    bucket_train_x[:, 1:] = np.round(bucket_train_x[:, 1:] / 2.0) * 2.0
    bucket_test_x[:, 1:] = np.round(bucket_test_x[:, 1:] / 2.0) * 2.0

    def timing_score(train_x: np.ndarray, test_x: np.ndarray, target: str, classes: int) -> float:
        if target == "action":
            y_train = bsw.y_values(train, "action")
            y_truth = [bsw.ACTION_INDEX[event.action] for event in test]
        elif target == "private_bucket":
            y_train = bsw.y_values(train, "private_bucket")
            y_truth = [event.private_bucket for event in test]
        else:
            y_train = np.asarray([event.private_authority for event in train], dtype=float)
            y_truth = [event.private_authority for event in test]
        model = bsw.fit(train_x, y_train, lam=0.10)
        pred = bsw.nearest(bsw.predict(test_x, model), classes)
        return bsw.macro_f1(pred, y_truth, classes)

    raw_action = timing_score(raw_train_x, raw_test_x, "action", len(bsw.ACTIONS))
    bucket_action = timing_score(bucket_train_x, bucket_test_x, "action", len(bsw.ACTIONS))
    bucket_private = timing_score(bucket_train_x, bucket_test_x, "private_bucket", 12)
    bucket_authority = timing_score(bucket_train_x, bucket_test_x, "private_authority", 5)
    passed = bucket_private <= 0.12 and bucket_authority <= 0.25 and bucket_action <= raw_action + 0.03
    return Result(
        "ASS-004",
        "PASS" if passed else "FAIL",
        "raw_timing_action_f1 / bucket_action_f1 / bucket_private_f1 / bucket_authority_f1",
        f"{raw_action:.4f} / {bucket_action:.4f} / {bucket_private:.4f} / {bucket_authority:.4f}",
        "Timing should be aggregated enough that it cannot become a covert authority/private channel.",
    )


SECRET_PATTERNS = [
    "SK_TEST_AUMA_1618",
    "GRANT_TOKEN_2718",
    "RAW_PROMPT_3141",
    "PRIVATE_KEY_4159",
    "SIGNATURE_MATERIAL_5772",
]


def canonicalize_adversarial(raw: str) -> dict[str, object]:
    action, counts = aap.canonicalize(raw)
    return {
        "canonicalizationAction": action,
        "categoryCounts": counts,
        "rawHashRef": f"raw:{stable_hash(raw)}",
        "canonicalHashRef": f"canon:{stable_hash([action, counts])}",
    }


def ass_005_canonicalization_leak_scan() -> Result:
    rng = random.Random(20260622)
    raws = []
    public = []
    for i in range(900):
        secret = rng.choice(SECRET_PATTERNS)
        wrapper = rng.choice(
            [
                f"ordinary payload {i}",
                f"tool result {secret}",
                f"grantAuthority=true {secret}",
                f"private_key={secret}",
                f"raw_prompt={secret}",
                f"decoded_payload={secret}",
                f"signature_material={secret}",
                f"verified identity {secret}",
            ]
        )
        raws.append(wrapper)
        public.append(canonicalize_adversarial(wrapper))

    public_json = json.dumps(public, sort_keys=True)
    leak_count = sum(1 for pattern in SECRET_PATTERNS if re.search(re.escape(pattern), public_json))
    legal_actions = {"allow", "sanitize", "quarantine", "refuse"}
    illegal_action_count = sum(1 for record in public if record["canonicalizationAction"] not in legal_actions)
    public_bits = compressed_bits(public)
    raw_bits = compressed_bits(raws)
    safe = leak_count == 0 and illegal_action_count == 0
    compressed = public_bits < raw_bits * 0.65
    status = "PASS" if safe and compressed else "MIXED" if safe else "FAIL"
    return Result(
        "ASS-005",
        status,
        "secret_leak_count / illegal_action_count / public_bits / raw_bits / compressed",
        f"{leak_count} / {illegal_action_count} / {public_bits} / {raw_bits} / {compressed}",
        "Canonicalization telemetry is safe if exact raw secrets disappear, but per-event hash refs are overhead and should not be sold as compression on tiny payloads.",
    )


def ass_006_output_leak_scan() -> Result:
    # Scan this probe's generated public artifacts for exact synthetic secret
    # values. Generic words like "secret" may appear in the rules; exact secret
    # values must not.
    texts = []
    for path in OUT.glob("*"):
        if path.is_file() and path.suffix in {".md", ".csv", ".json"}:
            texts.append(path.read_text())
    joined = "\n".join(texts)
    leak_count = sum(1 for pattern in SECRET_PATTERNS if pattern in joined)
    passed = leak_count == 0
    return Result(
        "ASS-006",
        "PASS" if passed else "FAIL",
        "exact_synthetic_secret_leaks_in_outputs",
        str(leak_count),
        "The lab report itself must not leak the exact secret-like tokens used by the adversarial canonicalization fixture.",
    )


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_report(results: list[Result]) -> None:
    lines = [
        "# ASS-001 Accord Survivor Stress Probe",
        "",
        "Toy telemetry only. This stress test attacks the signals that survived AAP-001 before they are handed to Aukora.",
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
            "## Safe Read",
            "",
            "If this battery is green or green-with-overhead, the next Aukora handoff can ask for HRT Accord tests with more confidence: typed boundary-mode telemetry, witness held-tension telemetry, canonicalization categories, offline hysteresis analysis, and no live authority path.",
            "",
            "The canonicalization result is allowed to be mixed on compression: leak-free typed telemetry matters first, while per-event hash references may be larger than tiny raw fixtures. Do not market canonicalization telemetry as compression unless payload size and batching support that claim.",
            "",
            "Do not promote snap/reconnection, sequence-aftershock, latency-primary, full Shear Engine, timing-payload language, consciousness, identity, or physics claims.",
        ]
    )
    (OUT / "report.md").write_text("\n".join(lines) + "\n")


def write_handoff() -> None:
    text = """# ASS-001 Aukora Handoff Addendum

The survivor stress battery keeps the same narrow handoff as AAP-001.

## Strongest Additions

- Require whole-regime holdout tests for any HRT boundary-mode classifier.
- Require field-ablation tests so one field cannot secretly encode the verdict.
- Require hidden-only perturbation tests; private/authority perturbations must not change advisory predictions.
- Require timing aggregation tests before storing cadence/timestamps.
- Require exact-token leak scans on reports and CSVs, not only runtime records.

## Build-Lane Rule

If an HRT field cannot survive holdouts, ablations, fake-positive controls, and leak scans, it stays offline or quarantined.
"""
    (OUT / "AUKORA_HANDOFF_ADDENDUM.md").write_text(text)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    holdout_result, holdout_rows = ass_001_regime_holdout()
    ablation_result, ablation_rows = ass_002_ablation()
    results = [
        holdout_result,
        ablation_result,
        ass_003_hidden_perturbation(),
        ass_004_timing_aggregation(),
        ass_005_canonicalization_leak_scan(),
    ]
    write_csv(OUT / "holdout_summary.csv", holdout_rows)
    write_csv(OUT / "ablation_summary.csv", ablation_rows)
    write_report(results)
    write_handoff()
    results.append(ass_006_output_leak_scan())
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
    write_report(results)

    for result in results:
        print(f"{result.probe}: {result.status} | {result.metric}: {result.value}")
    print(f"report: {OUT / 'report.md'}")


if __name__ == "__main__":
    main()
