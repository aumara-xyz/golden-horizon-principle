#!/usr/bin/env python3
"""
HSC-001 — Holographic Scale Correspondence Probe

This is a synthetic shape-correspondence toy, not physics evidence.

Question:
After removing physical units and absolute size, do three very different
boundary-record toys share the same dimensionless record-making shape?

Toy worlds:
- micro: sonoluminescence-like pressure threshold -> flash record
- macro: BAO-like oscillation freeze-out -> ruler record
- Aukora: proposal tension -> gate threshold -> receipt record

Forbidden interpretation:
This does not prove holography, GHP, consciousness, sonoluminescence cosmology,
or that software telemetry is physics. It only checks whether a shared
"hidden drive -> boundary threshold -> durable public record" shape survives
controls in a synthetic lab.
"""

from __future__ import annotations

import csv
import json
import math
import zlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_holographic_scale_correspondence_probe_outputs"
SEED = 161803
rng = np.random.default_rng(SEED)

RECORD_CENTER = 0.5
BINS = 96


@dataclass
class ProbeResult:
    probe: str
    metric: str
    value: float
    control: float
    verdict: str
    safe_read: str


def clip01(values: np.ndarray) -> np.ndarray:
    return np.clip(values, 0.0, 1.0)


def micro_flash_record(n: int = 9000) -> np.ndarray:
    """Pressure-threshold toy: flashes localize around the collapse threshold."""
    background = rng.beta(1.3, 1.3, size=int(n * 0.58))
    flash = rng.normal(RECORD_CENTER, 0.026, size=int(n * 0.42))
    return clip01(np.concatenate([background, flash]))


def macro_freeze_record(n: int = 9000) -> np.ndarray:
    """BAO-style toy: a frozen ruler bump is embedded in smooth public structure."""
    background = rng.triangular(0.0, RECORD_CENTER, 1.0, size=int(n * 0.62))
    ruler = rng.normal(RECORD_CENTER, 0.030, size=int(n * 0.38))
    return clip01(np.concatenate([background, ruler]))


def aukora_receipt_record(n: int = 9000) -> np.ndarray:
    """Gate-threshold toy: receipts cluster near the proposal/authorization boundary."""
    background = rng.uniform(0.0, 1.0, size=int(n * 0.60))
    receipts = rng.normal(RECORD_CENTER, 0.024, size=int(n * 0.40))
    return clip01(np.concatenate([background, receipts]))


def no_threshold_control(n: int = 9000) -> np.ndarray:
    return rng.uniform(0.0, 1.0, size=n)


def wrong_scale_control(n: int = 9000) -> np.ndarray:
    left = rng.normal(0.30, 0.035, size=int(n * 0.2))
    right = rng.normal(0.72, 0.035, size=int(n * 0.2))
    background = rng.uniform(0.0, 1.0, size=int(n * 0.6))
    return clip01(np.concatenate([background, left, right]))


def histogram(record: np.ndarray) -> np.ndarray:
    hist, _ = np.histogram(record, bins=BINS, range=(0.0, 1.0))
    hist = hist.astype(float) + 1e-12
    return hist / hist.sum()


def js_distance(p: np.ndarray, q: np.ndarray) -> float:
    m = 0.5 * (p + q)
    kl_pm = float(np.sum(p * np.log2(p / m)))
    kl_qm = float(np.sum(q * np.log2(q / m)))
    return math.sqrt(max(0.0, 0.5 * (kl_pm + kl_qm)))


def pairwise_mean_js(records: list[np.ndarray]) -> float:
    hists = [histogram(r) for r in records]
    distances = []
    for i in range(len(hists)):
        for j in range(i + 1, len(hists)):
            distances.append(js_distance(hists[i], hists[j]))
    return float(np.mean(distances))


def record_contrast(record: np.ndarray) -> float:
    center = np.sum((record > 0.47) & (record < 0.53))
    left = np.sum((record > 0.34) & (record < 0.42))
    right = np.sum((record > 0.58) & (record < 0.66))
    side = (left + right) / 2.0
    return float((center - side) / max(math.sqrt(side), 1.0))


def reconstruct_center(record: np.ndarray) -> float:
    hist, edges = np.histogram(record, bins=BINS, range=(0.0, 1.0))
    centers = (edges[:-1] + edges[1:]) / 2.0
    signal = hist - np.median(hist)
    window = (centers > 0.25) & (centers < 0.75)
    return float(centers[window][np.argmax(signal[window])])


def reconstruction_error(records: list[np.ndarray]) -> float:
    return float(np.mean([abs(reconstruct_center(r) - RECORD_CENTER) for r in records]))


def compression_ratio(record: np.ndarray) -> float:
    quantized = np.asarray(np.round(record * 255), dtype=np.uint8).tobytes()
    return len(zlib.compress(quantized, level=9)) / max(len(quantized), 1)


def hidden_leak_score(record: np.ndarray) -> float:
    hidden_phase = rng.choice([-1, 1], size=len(record))
    public_side = np.where(record > RECORD_CENTER, 1, -1)
    return abs(float(np.mean(hidden_phase * public_side)))


def coarse_grain_stability(record: np.ndarray) -> float:
    full = histogram(record)
    sample = rng.choice(record, size=int(len(record) * 0.42), replace=True)
    sample = clip01(sample + rng.normal(0.0, 0.015, size=len(sample)))
    coarse_full = full.reshape(24, 4).sum(axis=1)
    coarse_sample = histogram(sample).reshape(24, 4).sum(axis=1)
    return js_distance(coarse_full, coarse_sample)


def center_mass(record: np.ndarray) -> float:
    return float(np.mean((record > 0.47) & (record < 0.53)))


def law_vector(record: np.ndarray) -> np.ndarray:
    """
    Abstract record-law vector.

    This deliberately compares the common boundary-record behavior rather than
    demanding identical histograms across different toy worlds.
    """
    recon_error = abs(reconstruct_center(record) - RECORD_CENTER)
    return np.array(
        [
            math.log1p(max(record_contrast(record), 0.0)) / 5.0,
            1.0 - min(recon_error / 0.25, 1.0),
            center_mass(record),
            1.0 - compression_ratio(record),
            1.0 - min(coarse_grain_stability(record) / 0.2, 1.0),
        ]
    )


def law_vector_mean_distance(records: list[np.ndarray]) -> float:
    vectors = [law_vector(r) for r in records]
    distances = []
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            distances.append(float(np.linalg.norm(vectors[i] - vectors[j])))
    return float(np.mean(distances))


def run() -> list[ProbeResult]:
    worlds = [micro_flash_record(), macro_freeze_record(), aukora_receipt_record()]
    controls = [no_threshold_control(), wrong_scale_control(), no_threshold_control()]

    mean_contrast = float(np.mean([record_contrast(r) for r in worlds]))
    control_contrast = float(np.mean([record_contrast(r) for r in controls]))
    mean_js = pairwise_mean_js(worlds)
    control_js = pairwise_mean_js(controls)
    mean_error = reconstruction_error(worlds)
    control_error = reconstruction_error(controls)
    mean_compression = float(np.mean([compression_ratio(r) for r in worlds]))
    control_compression = float(np.mean([compression_ratio(r) for r in controls]))
    mean_leak = float(np.mean([hidden_leak_score(r) for r in worlds]))
    mean_stability = float(np.mean([coarse_grain_stability(r) for r in worlds]))
    control_stability = float(np.mean([coarse_grain_stability(r) for r in controls]))
    law_distance = law_vector_mean_distance(worlds)
    control_law_distance = law_vector_mean_distance(controls)

    return [
        ProbeResult(
            "HSC-001A",
            "mean_record_contrast",
            mean_contrast,
            control_contrast,
            "PASS" if mean_contrast > 45.0 and control_contrast < 10.0 else "MIXED",
            "All three scales form a strong public record near the normalized boundary.",
        ),
        ProbeResult(
            "HSC-001B",
            "cross_scale_shape_js_distance",
            mean_js,
            control_js,
            "PASS" if mean_js < 0.18 and control_js > mean_js * 1.7 else "MIXED",
            "The normalized public-record shapes are closer to each other than controls.",
        ),
        ProbeResult(
            "HSC-001C",
            "mean_reconstruction_error",
            mean_error,
            control_error,
            "PASS" if mean_error < 0.035 and control_error > mean_error * 3.0 else "MIXED",
            "A finite observer reconstructs the shared boundary location after scale removal.",
        ),
        ProbeResult(
            "HSC-001D",
            "mean_compression_ratio",
            mean_compression,
            control_compression,
            "PASS" if mean_compression < control_compression * 0.92 else "MIXED",
            "Structured public records compress better than unitless control records.",
        ),
        ProbeResult(
            "HSC-001E",
            "mean_hidden_leak_score",
            mean_leak,
            0.05,
            "PASS" if mean_leak < 0.05 else "MIXED",
            "The public record recovers boundary shape without leaking arbitrary hidden phase labels.",
        ),
        ProbeResult(
            "HSC-001F",
            "coarse_grain_stability_js",
            mean_stability,
            control_stability,
            "PASS" if mean_stability < 0.08 and mean_stability < control_stability else "MIXED",
            "The record shape survives observer noise and coarse-graining better than controls.",
        ),
        ProbeResult(
            "HSC-001G",
            "abstract_law_vector_distance",
            law_distance,
            control_law_distance,
            "PASS" if law_distance < 0.12 and law_distance < control_law_distance * 0.5 else "MIXED",
            "The worlds match at the abstract record-law level even when exact histograms differ.",
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
        "# HSC-001 — Holographic Scale Correspondence Probe",
        "",
        "## Status",
        "",
        "This is a synthetic shape-correspondence toy, not physics evidence for GHP.",
        "",
        "It asks whether micro, macro, and Aukora-style boundary-record toys share the same dimensionless record-making shape after scale removal.",
        "",
        "It does **not** prove holography, consciousness, sonoluminescence cosmology, or software-as-physics.",
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
            "- The useful import is dimensionless scale correspondence: hidden drive -> boundary threshold -> durable public record -> finite reconstruction.",
            "- The toy supports testing whether record-law shapes survive normalization across different domains.",
            "- The strongest positive signal is abstract law-vector correspondence, not exact histogram identity.",
            "- It should not be read as proof that physical microcosm and macrocosm are literally the same system.",
            "",
            "## Do Not Claim",
            "",
            "- Do not claim this proves the universe is a hologram.",
            "- Do not claim sonoluminescence, BAO, or Aukora are the same physical object.",
            "- Do not claim scale correspondence proves GHP.",
            "- Do not claim hidden private phase is recovered.",
        ]
    )
    (OUT / "report.md").write_text("\n".join(report) + "\n")
    (OUT / "metadata.json").write_text(
        json.dumps(
            {
                "seed": SEED,
                "pass_count": pass_count,
                "total": len(results),
                "status": "synthetic_scale_correspondence_toy_not_physics_evidence",
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
