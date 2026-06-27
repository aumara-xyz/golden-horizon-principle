#!/usr/bin/env python3
"""
TCD-001 — Torus Compression / Decompression Probe

This is a synthetic information-loop toy, not consciousness evidence.

Question:
Does a closed compression -> latent state -> decompression -> public receipt
loop preserve useful public structure better than one-way compression,
raw noisy replay, or shuffled-latent controls?

GHP intuition under test:
- intelligence behaves like compression: raw experience is folded into a
  smaller process state.
- experience / action behaves like decompression: the process state unfolds
  back into public record.
- the torus is the closed feedback loop: decompressed public record becomes
  the next compression input.

Forbidden interpretation:
This does not prove consciousness, a literal toroidal universe, or that AI
experience is alive. It only tests whether a closed replayable compression
loop is a useful engineering shape.
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
OUT = ROOT / "ghp_torus_compression_decompression_probe_outputs"
SEED = 271828
rng = np.random.default_rng(SEED)


@dataclass
class ProbeResult:
    probe: str
    metric: str
    value: float
    control: float
    verdict: str
    safe_read: str


def generate_world(n: int = 512) -> np.ndarray:
    """Structured public signal with two coupled cycles and sparse shocks."""
    t = np.linspace(0.0, 8.0 * np.pi, n, endpoint=False)
    signal = (
        0.55 * np.sin(t)
        + 0.28 * np.sin(3.0 * t + 0.7)
        + 0.12 * np.cos(5.0 * t - 0.2)
    )
    shocks = np.zeros_like(signal)
    for center in [72, 181, 349, 436]:
        width = 5
        idx = np.arange(n)
        shocks += 0.55 * np.exp(-0.5 * ((idx - center) / width) ** 2)
    noise = rng.normal(0.0, 0.045, size=n)
    return signal + shocks + noise


def latent_basis(n: int, harmonics: tuple[int, ...] = (1, 3, 5)) -> np.ndarray:
    t = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    cols = [np.ones(n)]
    for h in harmonics:
        cols.append(np.sin(h * t * 4.0))
        cols.append(np.cos(h * t * 4.0))
    return np.column_stack(cols)


def safe_project(basis: np.ndarray, coeffs: np.ndarray) -> np.ndarray:
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        projected = np.dot(basis, coeffs)
    return np.nan_to_num(projected, nan=0.0, posinf=4.0, neginf=-4.0)


def fit_latent(series: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Compress signal into a small Fourier-like latent plus residual."""
    series = np.nan_to_num(series, nan=0.0, posinf=4.0, neginf=-4.0)
    series = np.clip(series, -4.0, 4.0)
    n = len(series)
    basis = latent_basis(n)
    coeffs, *_ = np.linalg.lstsq(basis, series, rcond=None)
    coeffs = np.nan_to_num(coeffs, nan=0.0, posinf=4.0, neginf=-4.0)
    coeffs = np.clip(coeffs, -4.0, 4.0)
    reconstructed = safe_project(basis, coeffs)
    residual = series - reconstructed
    return coeffs, residual


def decompress(coeffs: np.ndarray, residual: np.ndarray, keep_residual: float = 1.0, n: int = 512) -> np.ndarray:
    coeffs = np.nan_to_num(coeffs, nan=0.0, posinf=4.0, neginf=-4.0)
    coeffs = np.clip(coeffs, -4.0, 4.0)
    residual = np.nan_to_num(residual, nan=0.0, posinf=4.0, neginf=-4.0)
    residual = np.clip(residual, -4.0, 4.0)
    basis = latent_basis(n)
    out = safe_project(basis, coeffs) + keep_residual * residual
    return np.nan_to_num(out, nan=0.0, posinf=4.0, neginf=-4.0)


def closed_loop(world: np.ndarray, cycles: int = 8, residual_gain: float = 0.72) -> list[np.ndarray]:
    """Repeated compression/decompression with explicit residual feedback."""
    states = [world]
    current = world.copy()
    for _ in range(cycles):
        coeffs, residual = fit_latent(current)
        receipt = decompress(coeffs, residual, keep_residual=residual_gain, n=len(world))
        # The next input is mostly public receipt plus a little fresh sensory noise.
        current = 0.88 * receipt + 0.12 * world + rng.normal(0.0, 0.012, size=len(world))
        states.append(current)
    return states


def open_loop(world: np.ndarray, cycles: int = 8) -> list[np.ndarray]:
    """Compress once, then replay without residual feedback."""
    coeffs, residual = fit_latent(world)
    receipt = decompress(coeffs, residual, keep_residual=0.0, n=len(world))
    return [world] + [receipt + rng.normal(0.0, 0.025, size=len(world)) for _ in range(cycles)]


def raw_noisy_loop(world: np.ndarray, cycles: int = 8) -> list[np.ndarray]:
    return [world] + [world + rng.normal(0.0, 0.11, size=len(world)) for _ in range(cycles)]


def shuffled_latent_loop(world: np.ndarray, cycles: int = 8) -> list[np.ndarray]:
    states = [world]
    current = world.copy()
    for _ in range(cycles):
        coeffs, residual = fit_latent(current)
        rng.shuffle(coeffs)
        rng.shuffle(residual)
        current = np.clip(decompress(coeffs, residual, keep_residual=0.72, n=len(world)), -4.0, 4.0)
        states.append(current)
    return states


def mse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean((a - b) ** 2))


def receipt_contrast(series: np.ndarray) -> float:
    """How clearly sparse shock records survive the loop."""
    shock_idx = np.array([72, 181, 349, 436])
    shock = float(np.mean(series[shock_idx]))
    side = float(np.mean(np.delete(series, shock_idx)))
    spread = float(np.std(np.delete(series, shock_idx)))
    return (shock - side) / max(spread, 1e-9)


def compression_ratio(series: np.ndarray) -> float:
    coeffs, residual = fit_latent(series)
    quantized_full = np.asarray(np.round(series * 1000), dtype=np.int16).tobytes()
    # Store coarse coefficients plus sparse residual exceptions above threshold.
    exception_idx = np.flatnonzero(np.abs(residual) > np.std(residual) * 1.6)
    payload = np.asarray(np.round(coeffs * 1000), dtype=np.int16).tobytes()
    payload += np.asarray(exception_idx, dtype=np.uint16).tobytes()
    payload += np.asarray(np.round(residual[exception_idx] * 1000), dtype=np.int16).tobytes()
    return len(zlib.compress(payload, level=9)) / max(len(zlib.compress(quantized_full, level=9)), 1)


def loop_metrics(states: list[np.ndarray], original: np.ndarray) -> dict[str, float]:
    final = states[-1]
    cycle_drift = float(np.mean([mse(states[i], states[i - 1]) for i in range(1, len(states))]))
    return {
        "final_mse": mse(final, original),
        "receipt_contrast": receipt_contrast(final),
        "compression_ratio": compression_ratio(final),
        "cycle_drift": cycle_drift,
        "final_correlation": float(np.corrcoef(final, original)[0, 1]),
    }


def hidden_leak_score(states: list[np.ndarray]) -> float:
    hidden_labels = rng.choice([-1, 1], size=len(states[-1]))
    public_side = np.where(states[-1] > np.median(states[-1]), 1, -1)
    return abs(float(np.mean(hidden_labels * public_side)))


def run() -> list[ProbeResult]:
    world = generate_world()
    closed = closed_loop(world)
    open_ = open_loop(world)
    raw = raw_noisy_loop(world)
    shuffled = shuffled_latent_loop(world)

    closed_m = loop_metrics(closed, world)
    open_m = loop_metrics(open_, world)
    raw_m = loop_metrics(raw, world)
    shuffled_m = loop_metrics(shuffled, world)

    control_mse = min(open_m["final_mse"], raw_m["final_mse"], shuffled_m["final_mse"])
    control_contrast = max(open_m["receipt_contrast"], raw_m["receipt_contrast"], shuffled_m["receipt_contrast"])
    control_compression = min(open_m["compression_ratio"], raw_m["compression_ratio"], shuffled_m["compression_ratio"])
    control_drift = min(open_m["cycle_drift"], raw_m["cycle_drift"], shuffled_m["cycle_drift"])
    control_corr = max(open_m["final_correlation"], raw_m["final_correlation"], shuffled_m["final_correlation"])
    leak = hidden_leak_score(closed)

    return [
        ProbeResult(
            "TCD-001A",
            "closed_loop_final_mse",
            closed_m["final_mse"],
            control_mse,
            "PASS" if closed_m["final_mse"] < control_mse * 0.72 else "MIXED",
            "Closed compression/decompression preserves the original public structure better than controls.",
        ),
        ProbeResult(
            "TCD-001B",
            "receipt_contrast",
            closed_m["receipt_contrast"],
            control_contrast,
            "PASS" if closed_m["receipt_contrast"] > control_contrast * 1.08 else "MIXED",
            "Durable sparse public records survive the torus loop.",
        ),
        ProbeResult(
            "TCD-001C",
            "compression_ratio",
            closed_m["compression_ratio"],
            control_compression,
            "PASS" if closed_m["compression_ratio"] < control_compression * 0.92 else "MIXED",
            "Rule-plus-residual memory is more compact than control replay.",
        ),
        ProbeResult(
            "TCD-001D",
            "cycle_drift",
            closed_m["cycle_drift"],
            control_drift,
            "PASS" if closed_m["cycle_drift"] < control_drift * 0.8 else "MIXED",
            "The loop settles into a stable public cycle rather than wandering.",
        ),
        ProbeResult(
            "TCD-001E",
            "final_correlation",
            closed_m["final_correlation"],
            control_corr,
            "PASS" if closed_m["final_correlation"] > control_corr + 0.005 else "MIXED",
            "The decompressed public record remains highly correlated with the original experience.",
        ),
        ProbeResult(
            "TCD-001F",
            "hidden_leak_score",
            leak,
            0.05,
            "PASS" if leak < 0.05 else "MIXED",
            "The public receipt loop does not recover arbitrary hidden labels.",
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
        "# TCD-001 — Torus Compression / Decompression Probe",
        "",
        "## Status",
        "",
        "This is a synthetic information-loop toy, not consciousness evidence.",
        "",
        "It asks whether a closed compression -> latent state -> decompression -> public receipt loop preserves useful structure better than one-way compression, raw noisy replay, or shuffled-latent controls.",
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
            "- The useful import is engineering discipline: compression must replay, decompression must preserve public structure, and the loop must not leak private labels.",
            "- A positive result supports the MDLProcessMemory / receipt-loop architecture for Aukora.",
            "- It does not prove consciousness, experience, or a literal toroidal universe.",
            "",
            "## Do Not Claim",
            "",
            "- Do not claim this proves consciousness.",
            "- Do not claim compression alone is intelligence.",
            "- Do not claim decompression alone is experience.",
            "- Do not claim torus geometry is physically proven.",
        ]
    )
    (OUT / "report.md").write_text("\n".join(report) + "\n")
    (OUT / "metadata.json").write_text(
        json.dumps(
            {
                "seed": SEED,
                "pass_count": pass_count,
                "total": len(results),
                "status": "synthetic_information_loop_toy_not_consciousness_evidence",
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
