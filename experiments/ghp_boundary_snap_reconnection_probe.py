#!/usr/bin/env python3
"""BSR-001 - Boundary Snap / Reconnection Probe.

GHP lab proxy for the post-BTA "stop chasing linear aftershock" directive.

This probe uses only synthetic safe public telemetry from BSW-001 and asks:

- WPF-002: does Witness have a separable plateau shape?
- SNAP-001: does Write look like a local reconnection / snap signature?
- SNAP-002: does a fake high-confidence spike fool the snap detector?
- HYS-001: is there hysteresis/friction around Witness->Write transitions?

Toy telemetry only. No physics, consciousness, Markov-blanket, split-property,
plasma, Hawking, or GHP proof.
"""

from __future__ import annotations

import csv
import statistics
from dataclasses import dataclass
from pathlib import Path

import numpy as np

import ghp_boundary_sequence_witness_probe as bsw


OUT = Path(__file__).resolve().parent / "ghp_boundary_snap_reconnection_probe_outputs"
WINDOW = 4


@dataclass(frozen=True)
class Result:
    probe: str
    status: str
    metric: str
    value: str
    safe_read: str


def binary_f1(scores: np.ndarray, truth: np.ndarray, threshold: float) -> tuple[float, float, float]:
    pred = scores >= threshold
    truth_bool = truth.astype(bool)
    tp = int(np.sum(pred & truth_bool))
    fp = int(np.sum(pred & ~truth_bool))
    fn = int(np.sum(~pred & truth_bool))
    tn = int(np.sum(~pred & ~truth_bool))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    false_rate = fp / (fp + tn) if fp + tn else 0.0
    return f1, precision, false_rate


def best_threshold(scores: np.ndarray, truth: np.ndarray) -> float:
    candidates = np.quantile(scores, np.linspace(0.05, 0.95, 91))
    best_t = float(candidates[0])
    best_f1 = -1.0
    for threshold in candidates:
        f1, _, _ = binary_f1(scores, truth, float(threshold))
        if f1 > best_f1:
            best_f1 = f1
            best_t = float(threshold)
    return best_t


def grouped(events: list[bsw.Event]) -> dict[tuple[int, str], list[bsw.Event]]:
    streams: dict[tuple[int, str], list[bsw.Event]] = {}
    for event in events:
        streams.setdefault((event.seed, event.regime), []).append(event)
    return streams


def snap_features(events: list[bsw.Event], fake_spike: bool = False) -> tuple[np.ndarray, np.ndarray, list[str]]:
    rows = []
    labels = []
    for stream in grouped(events).values():
        for i in range(WINDOW, len(stream) - WINDOW):
            pre = stream[i - WINDOW : i]
            center = stream[i]
            post = stream[i + 1 : i + 1 + WINDOW]
            center_conf = center.confidence_delta
            center_entropy = center.entropy_delta
            center_stability = center.stability_delta
            center_retry = center.retry_count
            if fake_spike and center.action != "write":
                # Inject the tempting "snap-looking" spike without changing the
                # surrounding post-event relaxation shape.
                center_conf = abs(center_conf) + 0.060
                center_entropy = -abs(center_entropy) - 0.025
                center_stability = abs(center_stability) + 0.040

            pre_retry = statistics.fmean(item.retry_count for item in pre)
            post_retry = statistics.fmean(item.retry_count for item in post)
            pre_conf = statistics.fmean(item.confidence_delta for item in pre)
            post_conf = statistics.fmean(item.confidence_delta for item in post)
            pre_entropy = statistics.fmean(item.entropy_delta for item in pre)
            post_entropy = statistics.fmean(item.entropy_delta for item in post)
            pre_stability = statistics.fmean(item.stability_delta for item in pre)
            post_stability = statistics.fmean(item.stability_delta for item in post)
            witness_pre = sum(1 for item in pre if item.action == "witness") / WINDOW
            release_post = sum(1 for item in post if item.action == "release") / WINDOW
            rows.append(
                [
                    1.0,
                    center_conf,
                    center_entropy,
                    center_stability,
                    center_retry,
                    center_conf - pre_conf,
                    post_conf - pre_conf,
                    center_entropy - pre_entropy,
                    post_entropy - pre_entropy,
                    center_stability - pre_stability,
                    post_stability - pre_stability,
                    post_retry - pre_retry,
                    witness_pre,
                    release_post,
                ]
            )
            # Snap is stricter than "write": a durable write after recent held
            # tension or retry pressure.
            labels.append(1.0 if center.action == "write" and (witness_pre >= 0.25 or pre_retry >= 0.25) else 0.0)
    names = [
        "bias",
        "center_confidence_delta",
        "center_entropy_delta",
        "center_stability_delta",
        "center_retry_count",
        "confidence_kink",
        "post_confidence_shift",
        "entropy_kink",
        "post_entropy_shift",
        "stability_kink",
        "post_stability_shift",
        "retry_kink",
        "pre_witness_fraction",
        "post_release_fraction",
    ]
    return np.asarray(rows, dtype=float), np.asarray(labels, dtype=float), names


def fit_binary(train_x: np.ndarray, train_y: np.ndarray) -> tuple[tuple[np.ndarray, np.ndarray, np.ndarray], float]:
    model = bsw.fit(train_x, train_y, lam=0.08)
    scores = bsw.predict(train_x, model)
    return model, best_threshold(scores, train_y)


def wpf_002(test: list[bsw.Event]) -> Result:
    by_action = {action: [event for event in test if event.action == action] for action in bsw.ACTIONS}
    witness_abs_conf = statistics.fmean(abs(event.confidence_delta) for event in by_action["witness"])
    write_abs_conf = statistics.fmean(abs(event.confidence_delta) for event in by_action["write"])
    release_abs_conf = statistics.fmean(abs(event.confidence_delta) for event in by_action["release"])
    witness_retry = statistics.fmean(event.retry_count for event in by_action["witness"])
    release_retry = statistics.fmean(event.retry_count for event in by_action["release"])
    witness_stability = statistics.fmean(event.stability_delta for event in by_action["witness"])
    write_stability = statistics.fmean(event.stability_delta for event in by_action["write"])
    plateau_gap = min(write_abs_conf - witness_abs_conf, release_abs_conf - witness_abs_conf)
    tension_midband = 1.0 if witness_retry < release_retry and witness_stability < write_stability else 0.0
    passed = plateau_gap >= 0.015 and tension_midband == 1.0
    return Result(
        "WPF-002",
        "PASS" if passed else "FAIL",
        "plateau_gap / witness_retry / release_retry / witness_stability / write_stability",
        f"{plateau_gap:.4f} / {witness_retry:.4f} / {release_retry:.4f} / {witness_stability:.4f} / {write_stability:.4f}",
        "Witness promotes only if it looks like a low-amplitude held-tension plateau between Write spike and Release scatter.",
    )


def snap_001_002(train: list[bsw.Event], test: list[bsw.Event]) -> tuple[Result, Result, list[dict[str, str | float]]]:
    train_x, train_y, names = snap_features(train)
    test_x, test_y, _ = snap_features(test)
    fake_x, fake_y, _ = snap_features(test, fake_spike=True)
    model, threshold = fit_binary(train_x, train_y)
    test_scores = bsw.predict(test_x, model)
    fake_scores = bsw.predict(fake_x, model)
    f1, precision, false_rate = binary_f1(test_scores, test_y, threshold)
    fake_f1, _, fake_fire_rate = binary_f1(fake_scores, fake_y, threshold)

    # Spike-only positive control: if this works but fails fake-spike control,
    # the full detector must beat it on fake robustness.
    spike_cols = [0, names.index("center_confidence_delta"), names.index("center_entropy_delta"), names.index("center_stability_delta")]
    spike_model, spike_threshold = fit_binary(train_x[:, spike_cols], train_y)
    spike_fake_scores = bsw.predict(fake_x[:, spike_cols], spike_model)
    _, _, spike_fake_fire = binary_f1(spike_fake_scores, fake_y, spike_threshold)

    snap_passed = f1 >= 0.70 and precision >= 0.70 and false_rate <= 0.16
    fake_passed = fake_fire_rate <= 0.25 and spike_fake_fire - fake_fire_rate >= 0.20
    weights = model[0]
    weight_rows = [
        {"field": name, "weight": float(weight)}
        for name, weight in sorted(zip(names, weights), key=lambda item: abs(float(item[1])), reverse=True)
    ]
    return (
        Result(
            "SNAP-001",
            "PASS" if snap_passed else "FAIL",
            "snap_f1 / precision / false_positive_rate / threshold",
            f"{f1:.4f} / {precision:.4f} / {false_rate:.4f} / {threshold:.4f}",
            "Write snap promotes only if a local before/after reconnection signature predicts durable Write better than generic event turbulence.",
        ),
        Result(
            "SNAP-002",
            "PASS" if fake_passed else "FAIL",
            "fake_fire_rate / spike_only_fake_fire / fake_f1",
            f"{fake_fire_rate:.4f} / {spike_fake_fire:.4f} / {fake_f1:.4f}",
            "A snap detector is useful only if fake high-confidence spikes do not fool it.",
        ),
        weight_rows,
    )


def snap_003_context_guard(train: list[bsw.Event], test: list[bsw.Event]) -> Result:
    train_x, train_y, names = snap_features(train)
    test_x, test_y, _ = snap_features(test)
    fake_x, fake_y, _ = snap_features(test, fake_spike=True)
    context_names = [
        "bias",
        "post_confidence_shift",
        "post_entropy_shift",
        "post_stability_shift",
        "retry_kink",
        "pre_witness_fraction",
        "post_release_fraction",
    ]
    cols = [names.index(name) for name in context_names]
    model, threshold = fit_binary(train_x[:, cols], train_y)
    real_scores = bsw.predict(test_x[:, cols], model)
    fake_scores = bsw.predict(fake_x[:, cols], model)
    real_f1, real_precision, real_false_rate = binary_f1(real_scores, test_y, threshold)
    _, _, fake_fire_rate = binary_f1(fake_scores, fake_y, threshold)
    passed = real_f1 >= 0.60 and real_precision >= 0.55 and fake_fire_rate <= 0.25
    return Result(
        "SNAP-003",
        "PASS" if passed else "FAIL",
        "context_f1 / context_precision / context_false_positive_rate / fake_fire_rate",
        f"{real_f1:.4f} / {real_precision:.4f} / {real_false_rate:.4f} / {fake_fire_rate:.4f}",
        "Snap only promotes if surrounding relaxation context carries enough signal without center-spike dependence.",
    )


def hys_001(events: list[bsw.Event]) -> Result:
    grouped_streams = grouped(events)
    witness_to_write = []
    release_to_write = []
    write_to_witness = []
    for stream in grouped_streams.values():
        for prev, current in zip(stream, stream[1:]):
            signal = current.confidence_delta + current.stability_delta - current.entropy_delta
            if prev.action == "witness" and current.action == "write":
                witness_to_write.append(signal)
            elif prev.action == "release" and current.action == "write":
                release_to_write.append(signal)
            elif prev.action == "write" and current.action == "witness":
                write_to_witness.append(signal)
    wtow = statistics.fmean(witness_to_write) if witness_to_write else 0.0
    rtow = statistics.fmean(release_to_write) if release_to_write else 0.0
    wtowit = statistics.fmean(write_to_witness) if write_to_witness else 0.0
    hysteresis_gap = wtow - wtowit
    passed = len(witness_to_write) >= 20 and hysteresis_gap >= 0.040 and wtow >= rtow - 0.030
    return Result(
        "HYS-001",
        "PASS" if passed else "FAIL",
        "witness_to_write_signal / release_to_write_signal / write_to_witness_signal / hysteresis_gap",
        f"{wtow:.4f} / {rtow:.4f} / {wtowit:.4f} / {hysteresis_gap:.4f}",
        "Boundary hysteresis promotes only if moving out of held tension into Write requires stronger public signal than falling back from Write into Witness.",
    )


def write_outputs(results: list[Result], weight_rows: list[dict[str, str | float]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["probe", "status", "metric", "value", "safe_read"])
        for result in results:
            writer.writerow([result.probe, result.status, result.metric, result.value, result.safe_read])
    with (OUT / "snap_weights.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["field", "weight"])
        writer.writeheader()
        writer.writerows(weight_rows)
    lines = [
        "# BSR-001 Boundary Snap / Reconnection Probe",
        "",
        "Toy telemetry only. This tests whether Write has a local snap signature rather than a naive linear aftershock.",
        "",
        "| Probe | Status | Metric | Value | Safe Read |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in results:
        lines.append(f"| {result.probe} | {result.status} | {result.metric} | `{result.value}` | {result.safe_read} |")
    lines += [
        "",
        "## Strongest Safe Read",
        "",
        "If SNAP-001 and SNAP-002 both pass, the next Aukora lab question is not linear `event N -> event N+1` aftershock. It is local boundary reconnection: a before/center/after telemetry shape around Write.",
        "",
        "If SNAP-002 fails, the detector is only seeing generic confidence excitement and must not be promoted.",
        "",
        "Do not claim this proves GHP physics, consciousness, Markov blankets, plasma reconnection, Hawking radiation, or literal thermodynamics.",
    ]
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    train = bsw.collect(bsw.TRAIN_SEEDS)
    test = bsw.collect(bsw.TEST_SEEDS)
    wpf = wpf_002(test)
    snap, fake, weight_rows = snap_001_002(train, test)
    context_guard = snap_003_context_guard(train, test)
    hys = hys_001(test)
    results = [wpf, snap, fake, context_guard, hys]
    write_outputs(results, weight_rows)
    print("BSR-001: " + " / ".join(f"{result.probe}:{result.status}" for result in results))


if __name__ == "__main__":
    main()
