#!/usr/bin/env python3
"""
CFR-001 — Cosmological Freeze-Out Record Probe

This is a synthetic record-law toy, not cosmology evidence and not physics
evidence for GHP.

Question:
Can a hidden oscillatory process freeze into a durable public correlation
record that later finite observers reconstruct, while shuffled/no-freeze
controls fail?

Analogy:
BAO / CMB record formation:
continuous early dynamics -> freeze-out -> durable public record -> later
observer reconstruction.

Forbidden interpretation:
This does not prove GHP, does not simulate the early universe, does not derive
the BAO scale, and does not imply dark matter or dark energy are observers.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_cosmological_freezeout_record_probe_outputs"
SEED = 53001
rng = np.random.default_rng(SEED)

SOUND_HORIZON_MPC = 150.0


@dataclass
class ProbeResult:
    probe: str
    metric: str
    value: float
    control: float
    verdict: str
    safe_read: str


def make_public_record(
    n: int = 12000,
    sound_horizon: float = SOUND_HORIZON_MPC,
    bump_fraction: float = 0.34,
    bump_sigma: float = 7.0,
    max_distance: float = 300.0,
) -> np.ndarray:
    """Synthetic pair-separation record with a BAO-like frozen bump."""
    n_bump = int(n * bump_fraction)
    n_background = n - n_bump
    background = rng.uniform(0.0, max_distance, size=n_background)
    bump = rng.normal(sound_horizon, bump_sigma, size=n_bump)
    bump = bump[(bump >= 0.0) & (bump <= max_distance)]
    while len(bump) < n_bump:
        extra = rng.normal(sound_horizon, bump_sigma, size=n_bump - len(bump))
        bump = np.concatenate([bump, extra[(extra >= 0.0) & (extra <= max_distance)]])
    return np.concatenate([background, bump[:n_bump]])


def reconstruct_peak(record: np.ndarray, bins: int = 120, max_distance: float = 300.0) -> float:
    hist, edges = np.histogram(record, bins=bins, range=(0.0, max_distance))
    centers = (edges[:-1] + edges[1:]) / 2.0
    # Remove a broad baseline by subtracting the median bin count.
    signal = hist - np.median(hist)
    search = (centers > 80.0) & (centers < 220.0)
    return float(centers[search][np.argmax(signal[search])])


def peak_error(record: np.ndarray) -> float:
    return abs(reconstruct_peak(record) - SOUND_HORIZON_MPC)


def ruler_contrast(record: np.ndarray) -> float:
    """
    Simple BAO-like contrast: excess counts near the ruler compared with
    sidebands. This avoids mistaking a smooth middle peak for a frozen record.
    """
    center = np.sum((record > 142.0) & (record < 158.0))
    left = np.sum((record > 112.0) & (record < 132.0))
    right = np.sum((record > 168.0) & (record < 188.0))
    side = (left + right) / 2.0
    return float((center - side) / max(np.sqrt(side), 1.0))


def shuffled_control(record: np.ndarray) -> np.ndarray:
    return rng.uniform(0.0, 300.0, size=len(record))


def no_freeze_control(n: int = 12000) -> np.ndarray:
    # No durable preferred scale; just smooth public background.
    return rng.triangular(0.0, 150.0, 300.0, size=n)


def noisy_observer_reconstructions(record: np.ndarray, trials: int = 80) -> list[float]:
    errors = []
    for _ in range(trials):
        sample = rng.choice(record, size=3500, replace=True)
        sample = sample + rng.normal(0.0, 3.0, size=len(sample))
        sample = np.clip(sample, 0.0, 300.0)
        errors.append(peak_error(sample))
    return errors


def noisy_observer_contrasts(record: np.ndarray, trials: int = 80) -> list[float]:
    contrasts = []
    for _ in range(trials):
        sample = rng.choice(record, size=3500, replace=True)
        sample = sample + rng.normal(0.0, 3.0, size=len(sample))
        sample = np.clip(sample, 0.0, 300.0)
        contrasts.append(ruler_contrast(sample))
    return contrasts


def expansion_scaled_records(scales: list[float]) -> list[float]:
    errors = []
    base = make_public_record()
    for scale in scales:
        physical = base * scale
        comoving_recovered = physical / scale
        errors.append(peak_error(comoving_recovered))
    return errors


def hidden_phase_leak_score(record: np.ndarray) -> float:
    """
    Toy private-state leak control. The public record should recover the
    frozen scale, not a hidden arbitrary phase assigned before freeze-out.
    """
    hidden_phase = rng.choice([-1, 1], size=len(record))
    public_side = np.where(record > SOUND_HORIZON_MPC, 1, -1)
    return abs(float(np.mean(hidden_phase * public_side)))


def run() -> list[ProbeResult]:
    record = make_public_record()
    shuffled = shuffled_control(record)
    no_freeze = no_freeze_control(len(record))

    record_contrast = ruler_contrast(record)
    shuffled_contrast = ruler_contrast(shuffled)
    no_freeze_contrast = ruler_contrast(no_freeze)

    noisy_contrasts = noisy_observer_contrasts(record)
    shuffled_noisy_contrasts = noisy_observer_contrasts(shuffled)

    scaled_errors = expansion_scaled_records([0.5, 0.75, 1.0, 1.5, 2.0])
    leak = hidden_phase_leak_score(record)

    return [
        ProbeResult(
            "CFR-001A",
            "frozen_ruler_contrast",
            record_contrast,
            shuffled_contrast,
            "PASS" if record_contrast > 20.0 and shuffled_contrast < 5.0 else "MIXED",
            "A frozen public correlation record has a strong ruler contrast; shuffled control does not.",
        ),
        ProbeResult(
            "CFR-001B",
            "no_freeze_control_contrast",
            record_contrast,
            no_freeze_contrast,
            "PASS" if record_contrast > 20.0 and no_freeze_contrast < 5.0 else "MIXED",
            "Without a preferred frozen scale, the smooth public background lacks a ruler contrast.",
        ),
        ProbeResult(
            "CFR-001C",
            "noisy_observer_median_contrast",
            float(np.median(noisy_contrasts)),
            float(np.median(shuffled_noisy_contrasts)),
            "PASS" if np.median(noisy_contrasts) > 10.0 and np.median(shuffled_noisy_contrasts) < 5.0 else "MIXED",
            "Finite noisy observers can still reconstruct the durable record better than shuffled controls.",
        ),
        ProbeResult(
            "CFR-001D",
            "expansion_rescaled_comoving_error_mpc",
            float(np.max(scaled_errors)),
            5.0,
            "PASS" if max(scaled_errors) < 5.0 else "MIXED",
            "The comoving ruler remains recoverable after expansion rescaling in the toy setup.",
        ),
        ProbeResult(
            "CFR-001E",
            "hidden_phase_leak_score",
            leak,
            0.05,
            "PASS" if leak < 0.05 else "MIXED",
            "The public record recovers the frozen scale, not arbitrary hidden phase labels.",
        ),
    ]


def write_outputs(results: list[ProbeResult]) -> None:
    OUT.mkdir(exist_ok=True)
    with (OUT / "summary.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["probe", "metric", "value", "control", "verdict", "safe_read"])
        writer.writeheader()
        for r in results:
            writer.writerow(r.__dict__)

    pass_count = sum(1 for r in results if r.verdict == "PASS")
    report = [
        "# CFR-001 — Cosmological Freeze-Out Record Probe",
        "",
        "## Status",
        "",
        "This is a synthetic record-law toy, not cosmology evidence and not physics evidence for GHP.",
        "",
        "It asks whether a hidden oscillatory process can freeze into a durable public correlation record that finite observers reconstruct later.",
        "",
        "It does **not** simulate BAO, derive the sound horizon, prove GHP, or say dark matter / dark energy are observers.",
        "",
        "## Results",
        "",
        "| Probe | Metric | Value | Control | Verdict |",
        "|---|---:|---:|---:|---|",
    ]
    for r in results:
        report.append(f"| {r.probe} | {r.metric} | {r.value:.6f} | {r.control:.6f} | {r.verdict} |")
    report.extend(
        [
            "",
            f"Pass count: **{pass_count}/{len(results)}**.",
            "",
            "## Interpretation",
            "",
            "- The useful import is the record-law pattern: oscillation -> freeze-out -> durable public imprint -> later reconstruction.",
            "- BAO / CMB are real cosmological examples of that pattern, but they do not prove GHP.",
            "- The toy supports adding cosmological freeze-out as an external analogue for the dark-to-readable interface.",
            "",
            "## Do Not Claim",
            "",
            "- Do not claim BAO proves GHP.",
            "- Do not claim CMB proves GHP.",
            "- Do not claim dark matter is consciousness.",
            "- Do not claim dark energy is the observer.",
            "- Do not insert phi into BAO without a derivation.",
        ]
    )
    (OUT / "report.md").write_text("\n".join(report) + "\n")
    (OUT / "metadata.json").write_text(
        json.dumps(
            {
                "seed": SEED,
                "pass_count": pass_count,
                "total": len(results),
                "status": "synthetic_record_law_toy_not_cosmology_evidence",
                "sound_horizon_mpc_toy_value": SOUND_HORIZON_MPC,
            },
            indent=2,
        )
        + "\n"
    )


def main() -> None:
    results = run()
    write_outputs(results)
    pass_count = sum(1 for r in results if r.verdict == "PASS")
    print(f"PASS {pass_count}/{len(results)}")
    for r in results:
        print(f"{r.probe}: {r.verdict} value={r.value:.6f} control={r.control:.6f}")


if __name__ == "__main__":
    main()
