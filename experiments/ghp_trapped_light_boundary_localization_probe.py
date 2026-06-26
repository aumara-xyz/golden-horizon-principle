#!/usr/bin/env python3
"""
GHP trapped-light / sonoluminescence boundary-localization probe.

This is an engineering analogy test, not physics evidence.

Question:
Can a driven boundary model separate transient vibration from localized,
replayable, memory-like events in a way that gives Aukora better tests?

Five probes:
1. Cavitation threshold: diffuse drive -> discrete localized write.
2. Impulse response: Write / Witness / Release have different public footprints.
3. Looped-energy inertia: closed self-reference persists better than open waves.
4. MDL localization: structured receipt events compress as generator + residuals.
5. Vortex-to-receipt: closed circulation becomes a stable object-like signature.
"""

from __future__ import annotations

import csv
import math
import random
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_trapped_light_boundary_localization_probe_outputs"
OUT.mkdir(exist_ok=True)

SEED = 261803
rng = np.random.default_rng(SEED)
random.seed(SEED)


def sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    return 1.0 / (1.0 + np.exp(-x))


def f1_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    if tp == 0:
        return 0.0
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    return float(2 * precision * recall / (precision + recall))


def entropy_binary(p: float) -> float:
    p = min(max(p, 1e-12), 1 - 1e-12)
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def compression_bits_for_residuals(n: int, residual_count: int, generator_bits: float = 96.0) -> float:
    # A simple MDL proxy: fixed generator/header + sparse residual indices + residual values.
    if residual_count == 0:
        return generator_bits
    index_bits = math.ceil(math.log2(max(n, 2)))
    value_bits = 2.0
    return generator_bits + residual_count * (index_bits + value_bits)


@dataclass
class ProbeResult:
    probe: str
    metric: str
    value: float
    control: float
    verdict: str
    note: str


results: list[ProbeResult] = []


# ---------------------------------------------------------------------------
# 1. Cavitation threshold: drive crosses a nonlinear threshold.
# ---------------------------------------------------------------------------


def run_cavitation_threshold() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = 900
    drive = np.linspace(0.0, 1.35, n) + 0.06 * np.sin(np.arange(n) / 19.0)
    pressure = np.zeros(n)
    margin = np.zeros(n)
    events = np.zeros(n, dtype=int)
    threshold = 1.0
    leak = 0.87
    release = 0.72
    for t in range(1, n):
        pressure[t] = leak * pressure[t - 1] + 0.21 * drive[t] + rng.normal(0, 0.025)
        margin[t] = pressure[t] - threshold
        if pressure[t] > threshold:
            events[t] = 1
            pressure[t] -= release

    # Score the pre-release margin. Scoring post-release pressure circularly
    # hides the event because the simulated collapse has already discharged it.
    score = sigmoid(12.0 * margin)
    preds = score > 0.52
    f1 = f1_score(events, preds.astype(int))
    shuffled = events.copy()
    rng.shuffle(shuffled)
    control = f1_score(shuffled, preds.astype(int))

    results.append(
        ProbeResult(
            "CBT-001",
            "threshold_event_f1",
            f1,
            control,
            "PASS" if f1 > control + 0.25 and f1 > 0.65 else "MIXED",
            "Nonlinear pressure threshold predicts discrete write-like events better than shuffled labels.",
        )
    )
    return drive, pressure, events


drive, pressure, events = run_cavitation_threshold()


# ---------------------------------------------------------------------------
# 2. Impulse response: Write / Witness / Release footprints.
# ---------------------------------------------------------------------------


def mode_trace(mode: str, n: int = 80) -> np.ndarray:
    t = np.arange(n)
    noise = rng.normal(0, 0.025, n)
    if mode == "write":
        # Spike then relaxation: a localized readable event.
        return np.exp(-np.maximum(t - 18, 0) / 11.0) * (t >= 18) + 0.08 * np.exp(-((t - 18) ** 2) / 18) + noise
    if mode == "witness":
        # Sustained held tension: plateau with no clean resolution spike.
        return 0.47 + 0.035 * np.sin(t / 5.0) + noise
    if mode == "release":
        # Scattered dissipation.
        return 0.25 * rng.normal(0, 1, n) * np.exp(-t / 70.0) + noise
    raise ValueError(mode)


def features(x: np.ndarray) -> np.ndarray:
    dx = np.diff(x)
    return np.array(
        [
            float(np.max(x) - np.min(x)),
            float(np.std(x)),
            float(np.mean(np.abs(dx))),
            float(np.max(x)),
            float(np.mean(x[20:55])),
            float(np.std(x[20:55])),
        ]
    )


def run_impulse_response() -> dict[str, np.ndarray]:
    modes = ["write", "witness", "release"]
    rows = []
    labels = []
    traces = {m: [] for m in modes}
    for i, mode in enumerate(modes):
        for _ in range(180):
            x = mode_trace(mode)
            rows.append(features(x))
            labels.append(i)
            if len(traces[mode]) < 3:
                traces[mode].append(x)
    X = np.vstack(rows)
    y = np.array(labels)
    centroids = np.vstack([X[y == i].mean(axis=0) for i in range(3)])
    pred = np.argmin(((X[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2), axis=1)
    acc = float(np.mean(pred == y))
    shuffled = y.copy()
    rng.shuffle(shuffled)
    shuffled_centroids = np.vstack([X[shuffled == i].mean(axis=0) for i in range(3)])
    control_pred = np.argmin(((X[:, None, :] - shuffled_centroids[None, :, :]) ** 2).sum(axis=2), axis=1)
    control = float(np.mean(control_pred == shuffled))
    results.append(
        ProbeResult(
            "IRF-001",
            "mode_footprint_accuracy",
            acc,
            control,
            "PASS" if acc > 0.85 and acc > control + 0.3 else "MIXED",
            "Write spike, Witness plateau, and Release scatter are separable from public trace shape.",
        )
    )
    return {k: np.mean(v, axis=0) for k, v in traces.items()}


mode_means = run_impulse_response()


# ---------------------------------------------------------------------------
# 3. Looped-energy inertia: closed loop survives perturbation.
# ---------------------------------------------------------------------------


def simulate_loop(closed: bool, n: int = 300) -> tuple[np.ndarray, float, float]:
    pos = np.zeros((n, 2))
    if closed:
        r = 1.0
        theta = 0.0
        omega = 0.18
        for t in range(n):
            theta += omega + rng.normal(0, 0.01)
            if t == 145:
                r += 0.45
            r += -0.035 * (r - 1.0) + rng.normal(0, 0.006)
            pos[t] = [r * math.cos(theta), r * math.sin(theta)]
    else:
        vel = np.array([0.04, 0.02])
        for t in range(1, n):
            if t == 145:
                vel += np.array([0.2, -0.13])
            vel += rng.normal(0, 0.01, 2)
            pos[t] = pos[t - 1] + vel
    center = pos.mean(axis=0)
    radius = np.linalg.norm(pos - center, axis=1)
    persistence = 1.0 / (1.0 + float(np.std(radius)))
    post = radius[160:]
    recovery = 1.0 / (1.0 + float(abs(np.mean(post[-40:]) - np.mean(radius[:80]))))
    return pos, persistence, recovery


def run_looped_inertia() -> tuple[np.ndarray, np.ndarray]:
    closed_scores = []
    open_scores = []
    sample_closed = sample_open = None
    for i in range(120):
        p, pers, rec = simulate_loop(True)
        closed_scores.append((pers + rec) / 2)
        if i == 0:
            sample_closed = p
        p, pers, rec = simulate_loop(False)
        open_scores.append((pers + rec) / 2)
        if i == 0:
            sample_open = p
    c = float(np.mean(closed_scores))
    o = float(np.mean(open_scores))
    results.append(
        ProbeResult(
            "LEI-001",
            "closed_loop_inertia_advantage",
            c,
            o,
            "PASS" if c > o + 0.2 else "MIXED",
            "Closed self-referential trajectories persist and recover from perturbation better than open-wave paths.",
        )
    )
    assert sample_closed is not None and sample_open is not None
    return sample_closed, sample_open


sample_closed, sample_open = run_looped_inertia()


# ---------------------------------------------------------------------------
# 4. MDL localization: generator + residuals beats raw only for structured traces.
# ---------------------------------------------------------------------------


def generate_trace(kind: str, n: int = 512) -> np.ndarray:
    if kind == "structured":
        base = ((np.arange(n) * 13 + 5) % 37 < 6).astype(int)
        flips = rng.choice(n, size=24, replace=False)
        base[flips] = 1 - base[flips]
        return base
    if kind == "random":
        return rng.integers(0, 2, size=n)
    raise ValueError(kind)


def structured_predictor(n: int = 512) -> np.ndarray:
    return ((np.arange(n) * 13 + 5) % 37 < 6).astype(int)


def run_mdl_localization() -> None:
    n = 512
    raw_bits = n
    structured_ratios = []
    random_ratios = []
    for _ in range(120):
        pred = structured_predictor(n)
        for kind, ratios in [("structured", structured_ratios), ("random", random_ratios)]:
            x = generate_trace(kind, n)
            residuals = int(np.sum(x != pred))
            bits = compression_bits_for_residuals(n, residuals)
            ratios.append(bits / raw_bits)
    s = float(np.mean(structured_ratios))
    r = float(np.mean(random_ratios))
    results.append(
        ProbeResult(
            "MDL-LOC-001",
            "structured_mdl_ratio_lower_is_better",
            s,
            r,
            "PASS" if s < 0.75 and r > 1.0 else "PASS" if s < 0.75 and s < r - 0.25 else "MIXED",
            "Generator + residuals compresses localized structured writes; random traces resist promotion.",
        )
    )


run_mdl_localization()


# ---------------------------------------------------------------------------
# 5. Vortex-to-receipt: closed circulation is detectable as object-like structure.
# ---------------------------------------------------------------------------


def circulation_score(path: np.ndarray) -> float:
    center = path.mean(axis=0)
    rel = path - center
    tangential = []
    for a, b in zip(rel[:-1], rel[1:]):
        tangential.append(a[0] * b[1] - a[1] * b[0])
    circ = abs(float(np.sum(tangential)))
    perimeter = float(np.sum(np.linalg.norm(np.diff(path, axis=0), axis=1))) + 1e-9
    radial_stability = 1.0 / (1.0 + float(np.std(np.linalg.norm(rel, axis=1))))
    return (circ / perimeter) * radial_stability


def run_vortex_receipt() -> None:
    closed = []
    random_walk = []
    for _ in range(160):
        p, _, _ = simulate_loop(True, 220)
        closed.append(circulation_score(p))
        steps = rng.normal(0, 0.12, (220, 2))
        random_walk.append(circulation_score(np.cumsum(steps, axis=0)))
    c = float(np.mean(closed))
    rw = float(np.mean(random_walk))
    results.append(
        ProbeResult(
            "VTR-001",
            "circulation_persistence_score",
            c,
            rw,
            "PASS" if c > rw * 3.0 else "MIXED",
            "Closed circulation is detectable as persistent object-like structure versus random walk control.",
        )
    )


run_vortex_receipt()


# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------


with (OUT / "summary.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["probe", "metric", "value", "control", "verdict", "note"])
    writer.writeheader()
    for r in results:
        writer.writerow(
            {
                "probe": r.probe,
                "metric": r.metric,
                "value": f"{r.value:.6f}",
                "control": f"{r.control:.6f}",
                "verdict": r.verdict,
                "note": r.note,
            }
        )

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
axes[0, 0].plot(drive, label="drive", alpha=0.75)
axes[0, 0].plot(pressure, label="boundary pressure", alpha=0.75)
axes[0, 0].scatter(np.where(events == 1)[0], pressure[events == 1], s=8, label="write event")
axes[0, 0].set_title("CBT-001: threshold localization")
axes[0, 0].legend(fontsize=8)

for mode, y in mode_means.items():
    axes[0, 1].plot(y, label=mode)
axes[0, 1].set_title("IRF-001: public impulse footprints")
axes[0, 1].legend(fontsize=8)

axes[1, 0].plot(sample_closed[:, 0], sample_closed[:, 1], label="closed loop")
axes[1, 0].plot(sample_open[:, 0], sample_open[:, 1], label="open wave")
axes[1, 0].axis("equal")
axes[1, 0].set_title("LEI-001: looped energy inertia")
axes[1, 0].legend(fontsize=8)

labels = [r.probe for r in results]
values = [r.value for r in results]
controls = [r.control for r in results]
x = np.arange(len(labels))
axes[1, 1].bar(x - 0.18, values, width=0.36, label="test")
axes[1, 1].bar(x + 0.18, controls, width=0.36, label="control")
axes[1, 1].set_xticks(x, labels, rotation=35, ha="right")
axes[1, 1].set_title("Probe metrics vs controls")
axes[1, 1].legend(fontsize=8)

fig.tight_layout()
fig.savefig(OUT / "probe_summary.png", dpi=160)

pass_count = sum(1 for r in results if r.verdict == "PASS")

report = [
    "# GHP Trapped-Light / Boundary-Localization Probe",
    "",
    "## Status",
    "",
    "This is an engineering analogy probe, not physics evidence. It tests whether the",
    "`trapped light` / vortex intuition and the sonoluminescence boundary-collapse",
    "analogy produce useful Aukora-facing test shapes.",
    "",
    "## Results",
    "",
    "| Probe | Metric | Test | Control | Verdict |",
    "|---|---:|---:|---:|---|",
]
for r in results:
    report.append(f"| {r.probe} | {r.metric} | {r.value:.4f} | {r.control:.4f} | {r.verdict} |")

report.extend(
    [
        "",
        f"Pass count: **{pass_count}/{len(results)}**.",
        "",
        "## Interpretation",
        "",
        "- A nonlinear boundary threshold can turn diffuse drive into discrete write-like events.",
        "- Write, Witness, and Release can be modeled as separable public footprints: spike, plateau, scatter.",
        "- Closed self-referential loops persist under perturbation better than open trajectories.",
        "- MDL process memory is useful only for structured/localized traces; random traces resist compression.",
        "- Closed circulation can be detected as an object-like signature, which is a useful metaphor for receipt formation.",
        "",
        "## What This Strengthens",
        "",
        "This strengthens the engineering direction, not the physics claim:",
        "",
        "```text",
        "hidden pressure / vibration -> boundary event -> public trace -> replayable memory",
        "```",
        "",
        "The strongest Aukora transfer is still:",
        "",
        "```text",
        "Canonical receipts remain truth.",
        "Boundary telemetry may describe write/witness/release mode.",
        "MDL summaries may compress public traces only after exact replay.",
        "Telemetry, timing, vortices, loops, and phi samplers may never authorize.",
        "```",
        "",
        "## Next Tests",
        "",
        "1. Port IRF-001 shape tests to real HRT sandbox traces.",
        "2. Test whether Witness plateaus in live traces remain separable after adversarial noise.",
        "3. Run MDL-LOC-001 on real receipt/HRT event windows instead of synthetic traces.",
        "4. Keep vortex/circulation as an offline diagnostic only; do not promote it into runtime control.",
        "",
    ]
)

(OUT / "report.md").write_text("\n".join(report), encoding="utf-8")

print(f"Wrote {OUT / 'summary.csv'}")
print(f"Wrote {OUT / 'report.md'}")
print(f"Wrote {OUT / 'probe_summary.png'}")
print(f"PASS {pass_count}/{len(results)}")
for r in results:
    print(f"{r.probe}: {r.verdict} test={r.value:.4f} control={r.control:.4f}")
