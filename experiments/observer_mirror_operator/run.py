#!/usr/bin/env python3
"""OBSERVER-MIRROR-OPERATOR v0 controls-first runner."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.special import erf


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
PHI = (1.0 + math.sqrt(5.0)) / 2.0
N = 40
Q = math.exp(-2.0 * math.pi * 0.1)
SEED = 20260904


def matrices(alpha_right):
    modes = np.arange(-N, N + 1)
    pl = np.exp(2j * math.pi * modes / 3.0)
    pr = np.exp(2j * math.pi * modes * alpha_right)
    z = np.zeros((len(modes), len(modes)), dtype=complex)
    d = np.block([[np.diag(pl), z], [z, np.diag(pr)]])
    eye_mode = np.eye(len(modes), dtype=complex)
    r, t = math.sqrt(1.0 - Q), 1j * math.sqrt(Q)
    b = np.block([[r * eye_mode, t * eye_mode], [t * eye_mode, r * eye_mode]])
    return b @ d


def evolve(alpha_right, steps=2000):
    modes = np.arange(-N, N + 1)
    packet = np.exp(-0.5 * ((modes - 7.0) / 5.0) ** 2).astype(complex)
    packet /= np.linalg.norm(packet)
    left, right = packet.copy(), np.zeros_like(packet)
    pl = np.exp(2j * math.pi * modes / 3.0)
    pr = np.exp(2j * math.pi * modes * alpha_right)
    r, t = math.sqrt(1.0 - Q), 1j * math.sqrt(Q)
    fidelity, visible, norm = [], [], []
    for step in range(1, steps + 1):
        lp, rp = pl * left, pr * right
        left, right = r * lp + t * rp, t * lp + r * rp
        if step >= 100:
            fidelity.append(abs(np.vdot(packet, left)) ** 2)
        visible.append(float(np.vdot(left, left).real))
        norm.append(float(np.vdot(left, left).real + np.vdot(right, right).real))
    return {
        "alpha_right": float(alpha_right),
        "max_fidelity_steps_100_to_2000": float(max(fidelity)),
        "mean_visible_probability": float(np.mean(visible)),
        "min_visible_probability": float(np.min(visible)),
        "max_visible_probability": float(np.max(visible)),
        "max_total_norm_error": float(np.max(np.abs(np.asarray(norm) - 1.0))),
    }


def ks_distance(sample, cdf):
    x = np.sort(np.asarray(sample))
    n = len(x)
    f = cdf(x)
    return float(max(np.max(np.arange(1, n + 1) / n - f), np.max(f - np.arange(n) / n)))


def operator_checks(alpha_right):
    u = matrices(alpha_right)
    eye = np.eye(len(u), dtype=complex)
    unitary = np.linalg.norm(u.conj().T @ u - eye, ord=2)
    v = np.exp(1j * 0.137) * u
    h = 1j * (eye + v) @ np.linalg.inv(eye - v)
    self_adjoint = np.linalg.norm(h - h.conj().T, ord=2) / max(1.0, np.linalg.norm(h, ord=2))
    max_imag_eig = float(np.max(np.abs(np.linalg.eigvals(h).imag)))

    angles = np.mod(np.angle(np.linalg.eigvals(u)), 2.0 * math.pi)
    angles.sort()
    spacings = np.diff(np.r_[angles, angles[0] + 2.0 * math.pi])
    spacings /= spacings.mean()
    cdfs = {
        "poisson": lambda s: 1.0 - np.exp(-s),
        "goe": lambda s: 1.0 - np.exp(-math.pi * s * s / 4.0),
        "gue": lambda s: erf(2.0 * s / math.sqrt(math.pi)) - (4.0 * s / math.pi) * np.exp(-4.0 * s * s / math.pi),
    }
    ks = {name: ks_distance(spacings, fn) for name, fn in cdfs.items()}
    return {
        "unitarity_residual": float(unitary),
        "relative_self_adjoint_residual": float(self_adjoint),
        "max_eigenvalue_imaginary_part": max_imag_eig,
        "eigenphase_spacing_ks": ks,
        "eigenphase_spacing_closest": min(ks, key=ks.get),
    }


def main():
    OUT.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED)

    # Frozen control order before authentic 1/phi.
    named = {
        "rational_2_over_5": evolve(2.0 / 5.0),
        "sqrt2_minus_1": evolve(math.sqrt(2.0) - 1.0),
    }
    random_alphas = rng.uniform(0.0, 1.0, 200)
    random_scores = np.asarray([evolve(float(alpha))["max_fidelity_steps_100_to_2000"] for alpha in random_alphas])
    authentic = evolve(1.0 / PHI)
    authentic_percentile = float(np.mean(random_scores <= authentic["max_fidelity_steps_100_to_2000"]))
    operator = operator_checks(1.0 / PHI)

    unitary_ok = operator["unitarity_residual"] < 1e-11
    self_adjoint_ok = operator["relative_self_adjoint_residual"] < 1e-11
    norm_ok = authentic["max_total_norm_error"] < 1e-11
    phi_beats_random = authentic_percentile < 0.05
    gue_closest = operator["eigenphase_spacing_closest"] == "gue"

    result = {
        "test_id": "OBSERVER-MIRROR-OPERATOR-v0",
        "uses_primes": False, "uses_zeta_zeros": False,
        "dimensions": {"N": N, "modes_per_sector": 2 * N + 1, "full_dimension": 2 * (2 * N + 1)},
        "parameters": {"alpha_left": 1.0 / 3.0, "alpha_right_authentic": 1.0 / PHI, "q": Q, "cayley_phase_shift": 0.137},
        "execution_order": ["rational_2_over_5", "sqrt2_minus_1", "200_random", "one_over_phi"],
        "controls": {
            "named": named,
            "random": {"count": len(random_scores), "median": float(np.median(random_scores)), "p05": float(np.quantile(random_scores,.05)), "p95": float(np.quantile(random_scores,.95))},
        },
        "authentic": {**authentic, "random_control_percentile": authentic_percentile},
        "operator": operator,
        "measure_theoretic_boundary": "Q intersect [0,1] has Lebesgue measure zero, so its ordinary L2 support projection is zero; the two channels are modeled sectors, not a literal rational/irrational spatial cut.",
        "verdict": {
            "global_unitarity": "MEASURED" if unitary_ok else "UNVERIFIED",
            "cayley_self_adjointness": "MEASURED" if self_adjoint_ok else "UNVERIFIED",
            "observer_radiation_with_global_norm": "MEASURED" if norm_ok and authentic["min_visible_probability"] < .99 else "UNVERIFIED",
            "phi_whole_operator_recurrence": "MEASURED" if phi_beats_random else "VOID",
            "zeta_identification": "UNVERIFIED",
        },
    }
    (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n")

    report = [
        "# OBSERVER-MIRROR-OPERATOR v0 — results", "",
        "No primes or zeta zeros entered the operator. Controls ran before the `1/phi` sector.", "",
        "| Check | Result | Status |", "|---|---:|---|",
        f"| `U†U-I` operator norm | {operator['unitarity_residual']:.3e} | {'MEASURED' if unitary_ok else 'UNVERIFIED'} |",
        f"| Cayley `H-H†` relative norm | {operator['relative_self_adjoint_residual']:.3e} | {'MEASURED' if self_adjoint_ok else 'UNVERIFIED'} |",
        f"| Maximum imaginary part of `H` eigenvalues | {operator['max_eigenvalue_imaginary_part']:.3e} | MEASURED |",
        f"| Total-norm drift over 2,000 steps | {authentic['max_total_norm_error']:.3e} | {'MEASURED' if norm_ok else 'UNVERIFIED'} |",
        f"| Visible probability range | {authentic['min_visible_probability']:.4f}–{authentic['max_visible_probability']:.4f} | MEASURED exchange |",
        f"| `1/phi` recurrence score percentile | {100*authentic_percentile:.1f}% | {'MEASURED survivor' if phi_beats_random else 'VOID as distinctive mechanism'} |",
        f"| Eigenphase spacing closest to | {operator['eigenphase_spacing_closest'].upper()} | {'prediction failed' if gue_closest else 'prediction matched'} |", "",
        "## Recurrence controls", "",
        "| Right-sector phase | Maximum return fidelity, steps 100–2000 |", "|---|---:|",
        f"| rational 2/5 | {named['rational_2_over_5']['max_fidelity_steps_100_to_2000']:.6f} |",
        f"| sqrt(2)-1 | {named['sqrt2_minus_1']['max_fidelity_steps_100_to_2000']:.6f} |",
        f"| random median | {np.median(random_scores):.6f} |",
        f"| random 5th–95th percentile | {np.quantile(random_scores,.05):.6f}–{np.quantile(random_scores,.95):.6f} |",
        f"| 1/phi | {authentic['max_fidelity_steps_100_to_2000']:.6f} |", "",
        "## Prediction ledger", "",
        "| Prediction | Outcome |", "|---|---|",
        f"| Global unitary and Cayley self-adjoint | {'MATCH' if unitary_ok and self_adjoint_ok else 'FAILED'} |",
        f"| Observer sees exchange while total norm stays one | {'MATCH' if norm_ok and authentic['min_visible_probability'] < .99 else 'FAILED'} |",
        f"| `phi` does not beat 95% of random whole-operator controls | {'MATCH' if not phi_beats_random else 'FAILED'} |",
        f"| Eigenphases not closest to GUE | {'MATCH' if not gue_closest else 'FAILED'} |",
        "| No zeta trace or `T log T` law generated | MATCH |", "",
        "## Honest paragraph", "",
        "This is the requested wave operator plus observer in exact finite form. The full evolution is unitary, the observer's sector exchanges probability with the mirror sector, and the inverse Cayley transform is self-adjoint with real eigenvalues. That solves the abstract 'real-spectrum' box for this toy, but not the zeta-identification box: the spectrum is generated by chosen rotations and a beam-splitter seam, not by the zeta explicit formula. Also, rational and irrational numbers have no spatial border in the continuum; the two-sector split is a model choice. The next non-negotiable step would be to derive the seam from a zeta trace or Weil-positive form rather than choose it.", "",
        "Full machine-readable output: `outputs/results.json`.",
    ]
    (HERE / "RESULTS.md").write_text("\n".join(report) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    main()
