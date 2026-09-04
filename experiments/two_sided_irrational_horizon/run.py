#!/usr/bin/env python3
"""Controls-first runner for TWO-SIDED-IRRATIONAL-HORIZON v0."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
PHI = (1.0 + math.sqrt(5.0)) / 2.0
SEED = 20260904


def seam(omega, kappa=1.0):
    q = math.exp(-2.0 * math.pi * omega / kappa)
    r, t = math.sqrt(1.0 - q), 1j * math.sqrt(q)
    return np.asarray([[r, t], [t, r]], dtype=complex), q


def matrix_checks():
    mirror = np.asarray([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
    eye = np.eye(2)
    unitary, commute = [], []
    for omega in np.linspace(0.01, 10.0, 1001):
        s, _ = seam(float(omega))
        unitary.append(np.linalg.norm(s.conj().T @ s - eye, ord=2))
        commute.append(np.linalg.norm(s @ mirror - mirror @ s, ord=2))
    return {"max_unitarity_residual": float(max(unitary)), "max_mirror_commutator": float(max(commute))}


def delayed_recurrence(alpha, q_min=100, q_max=10000):
    q = np.arange(q_min, q_max + 1, dtype=float)
    mismatch = np.abs(q * alpha - np.rint(q * alpha))
    weighted = q * mismatch
    i = int(np.argmin(weighted))
    return {
        "alpha": float(alpha), "C_tail": float(weighted[i]),
        "minimizing_q": int(q[i]), "phase_mismatch": float(mismatch[i]),
        "amplitude_return_error": float(abs(math.sin(math.pi * q[i] * alpha))),
    }


def fibonacci_returns():
    f = [1, 1]
    while f[-1] <= 10000:
        f.append(f[-1] + f[-2])
    rows = []
    for q in sorted(set(f)):
        if q > 10000:
            continue
        mismatch = abs(q * PHI - round(q * PHI))
        rows.append({
            "q": q, "time_2pi_q": float(2.0 * math.pi * q),
            "phase_mismatch": float(mismatch),
            "q_times_mismatch": float(q * mismatch),
            "amplitude_return_error": float(abs(math.sin(math.pi * q * PHI))),
        })
    return rows


def one_sided_poles():
    rows = []
    for omega in (0.05, 0.1, 0.25, 0.5, 1.0):
        _, leakage = seam(omega)
        reflection = math.sqrt(1.0 - leakage)
        rows.append({
            "carrier_omega": omega, "leakage_probability": leakage,
            "reflection_amplitude": reflection,
            "pole_real_n0": 0.0, "pole_imaginary": math.log(reflection),
        })
    return rows


def quartet_checks():
    beta, gamma = 0.7, PHI
    roots = np.asarray([
        beta + 1j * gamma, beta - 1j * gamma,
        1.0 - beta + 1j * gamma, 1.0 - beta - 1j * gamma,
    ])
    points = [complex(x, y) for x in np.linspace(-1, 2, 31) for y in np.linspace(-3, 3, 29)]
    mirror_resid, reality_resid = [], []
    for s in points:
        f = np.prod(s - roots)
        mirror_resid.append(abs(np.prod((1.0 - s) - roots) - f) / max(1.0, abs(f)))
        reality_resid.append(abs(np.prod(np.conjugate(s) - roots) - np.conjugate(f)) / max(1.0, abs(f)))
    return {
        "beta": beta, "gamma": gamma,
        "distance_from_symmetry_line": abs(beta - 0.5),
        "max_relative_F_1_minus_s_minus_F_s": float(max(mirror_resid)),
        "max_relative_F_conj_s_minus_conj_F_s": float(max(reality_resid)),
        "roots": [{"real": float(z.real), "imag": float(z.imag)} for z in roots],
    }


def main():
    OUT.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED)

    # Control order is frozen: named controls, random controls, then phi.
    named = {
        "rational_3_over_2": delayed_recurrence(1.5),
        "sqrt2": delayed_recurrence(math.sqrt(2.0)),
        "pi_minus_3": delayed_recurrence(math.pi - 3.0),
    }
    random_alpha = rng.uniform(0.1, 0.9, 500)
    random_scores = np.asarray([delayed_recurrence(float(a))["C_tail"] for a in random_alpha])
    golden = delayed_recurrence(PHI)
    percentile = float(np.mean(random_scores <= golden["C_tail"]))
    recurrence_survives = percentile >= 0.95

    checks = matrix_checks()
    poles = one_sided_poles()
    quartet = quartet_checks()
    all_poles_complex = all(row["pole_imaginary"] < 0 for row in poles)
    symmetries_hold = quartet["max_relative_F_1_minus_s_minus_F_s"] < 1e-12 and quartet["max_relative_F_conj_s_minus_conj_F_s"] < 1e-12

    result = {
        "test_id": "TWO-SIDED-IRRATIONAL-HORIZON-v0",
        "uses_primes": False, "uses_zeta_zeros": False,
        "execution_order": ["rational_3_over_2", "sqrt2", "pi_minus_3", "500_random", "phi"],
        "seam": {**checks, "kappa": 1.0, "profile": "q(omega)=exp(-2*pi*omega/kappa)", "physics_status": "Hawking-like toy, not Hawking radiation"},
        "recurrence": {
            "named_controls": named,
            "random_controls": {
                "count": len(random_scores), "median": float(np.median(random_scores)),
                "p05": float(np.quantile(random_scores, .05)), "p95": float(np.quantile(random_scores, .95)),
                "p99": float(np.quantile(random_scores, .99)),
            },
            "phi": golden, "phi_percentile": percentile,
            "survives_95_percent_rule": bool(recurrence_survives),
            "fibonacci_returns": fibonacci_returns(),
        },
        "one_sided_poles": poles,
        "off_line_mirror_quartet": quartet,
        "verdict": {
            "global_two_sided_unitarity": "MEASURED" if checks["max_unitarity_residual"] < 1e-12 else "UNVERIFIED",
            "phi_delayed_recurrence": "MEASURED" if recurrence_survives else "VOID",
            "radiation_forces_real_resonances": "VOID" if all_poles_complex else "UNVERIFIED",
            "mirror_symmetry_forces_critical_line": "VOID" if symmetries_hold else "UNVERIFIED",
            "RH_connection": "UNVERIFIED",
        },
    }
    (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n")

    report = [
        "# TWO-SIDED-IRRATIONAL-HORIZON v0 — results", "",
        "No primes or zeta zeros entered this toy. Named and random controls ran before the golden-ratio case.", "",
        "| Test | Result | Status |", "|---|---:|---|",
        f"| Full two-sided unitarity residual | {checks['max_unitarity_residual']:.3e} | {result['verdict']['global_two_sided_unitarity']} |",
        f"| Mirror commutator | {checks['max_mirror_commutator']:.3e} | MEASURED |",
        f"| `phi` delayed-recurrence statistic | {golden['C_tail']:.6f} | percentile {100*percentile:.1f}% |",
        f"| One-sided poles below real axis | {sum(x['pole_imaginary'] < 0 for x in poles)}/{len(poles)} | {'MEASURED' if all_poles_complex else 'UNVERIFIED'} |",
        f"| Off-line quartet mirror residual | {quartet['max_relative_F_1_minus_s_minus_F_s']:.3e} | MEASURED counterexample |", "",
        "## Recurrence controls", "",
        "| Phase ratio | C over q=100…10000 |", "|---|---:|",
        f"| rational 3/2 | {named['rational_3_over_2']['C_tail']:.6f} |",
        f"| sqrt(2) | {named['sqrt2']['C_tail']:.6f} |",
        f"| pi-3 | {named['pi_minus_3']['C_tail']:.6f} |",
        f"| random median | {np.median(random_scores):.6f} |",
        f"| random 95th percentile | {np.quantile(random_scores,.95):.6f} |",
        f"| phi | {golden['C_tail']:.6f} |", "",
        "## Prediction ledger", "",
        "| Prediction | Outcome |", "|---|---|",
        f"| Two-sided unitarity and mirror symmetry | {'MATCH' if checks['max_unitarity_residual'] < 1e-12 and checks['max_mirror_commutator'] < 1e-12 else 'FAILED'} |",
        f"| Radiation makes one-sided poles complex | {'MATCH' if all_poles_complex else 'FAILED'} |",
        f"| Mirror identities permit an off-line quartet | {'MATCH' if symmetries_hold else 'FAILED'} |",
        f"| phi exceeds 95% of recurrence controls | {'MATCH' if recurrence_survives else 'FAILED'} |",
        "| No prime trace or T log T law generated | MATCH |", "",
        "## Honest paragraph", "",
        "The two-sided correction is mathematically meaningful: the complete seam is unitary even though one side alone looks lossy, and the golden phase genuinely tests delayed recurrence. But global conservation does not force the observed one-sided resonances to be real, and mirror symmetry does not force zeros onto its fixed line; the explicit off-line quartet obeys both mirror identities. A successful RH route would still need a positivity or self-adjoint dilation theorem that identifies zeta's spectrum, plus the prime trace and T log T counting law. The Boltzmann leakage used here is an analogy only, not a model of gravitational Hawking radiation.", "",
        "Full machine-readable output: `outputs/results.json`.",
    ]
    (HERE / "RESULTS.md").write_text("\n".join(report) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    main()
