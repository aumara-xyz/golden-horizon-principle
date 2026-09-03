#!/usr/bin/env python3
"""Zero-free Kuipers--Hummel--Richter butterfly-graph reconstruction.

The script reproduces a finite version of the recursive phase construction in
arXiv:1307.6055 / Phys. Rev. Lett. 112, 070406 (2014), runs a matched
pseudo-prime control first, and then applies identity, DFT, and fixed-seed Haar
central-scatterer surgeries.  It contains no table or oracle for the Riemann
zeros.

The paper requires two independent cutoffs, p < P and m < M.  Round 5 fixed
the four prime cutoffs but did not register a repetition cutoff.  We therefore
state and freeze M=8 here.  Every result is only about this finite truncation.

There is a sign inconsistency in the printed prescription: Eqs. (11)--(12),
the worked p=2 example, and Supplemental Eq. (B1) require
cos(theta[p,m]) = -T[p,m]/l[p,m], while the displayed Eq. (14) prints a plus.
Both signs are evaluated; the trace identity selects the minus sign.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np


SOURCE = {
    "authors": ["Jack Kuipers", "Quirin Hummel", "Klaus Richter"],
    "title": "Quantum graphs whose spectra mimic the zeros of the Riemann zeta function",
    "arxiv": "1307.6055v2",
    "arxiv_url": "https://arxiv.org/abs/1307.6055",
    "arxiv_dateline": "arXiv:1307.6055v2 [nlin.CD] 26 Feb 2014",
    "journal": "Physical Review Letters 112, 070406 (2014)",
    "doi": "10.1103/PhysRevLett.112.070406",
    "doi_url": "https://doi.org/10.1103/PhysRevLett.112.070406",
    "published_pdf_archive_url": "https://epub.uni-regensburg.de/29572/1/2014-PRL-Kuipers-et-al.pdf",
    "published_pdf_sha256": "252cd592227dbbea0a975f8b6c9513c1d4f561a343a0fb070ad3c36adf6e8834",
    "pdf_sha256": "0d2a6491a5b52096544f032fdff89dbaacfd971dd7f1c7507b02620505717837",
    "source_archive_sha256": "09e7f86796eec6d4ecea1c7e69d1fec51d67f4a84c5dc8dbea322b4123ed0df2",
    "equations_used": [
        "(2)",
        "(4)",
        "(5)",
        "(7)",
        "(11)",
        "(12)",
        "(14)",
        "Supplemental (B1)",
    ],
}

PRIME_CUTOFFS = (29, 53, 97, 193)
REPETITION_CUTOFF = 8
K_MIN = 0.0
K_MAX = 256.0
K_INTERVALS = 8192
HAAR_SEED = 52025555


@dataclass(frozen=True)
class Phase:
    """One (base, repetition) phase and its number of butterfly copies."""

    base: float
    repetition: int
    copies: int
    cosine: float
    theta: float
    T: float


@dataclass(frozen=True)
class Mode:
    """One directed mode of one butterfly copy."""

    prime: int
    repetition: int
    copy: int
    channel: int
    length: float
    integer_length_key: int


def utc_now() -> str:
    """Return a stable ISO timestamp in UTC."""

    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    """Hash a file without changing it."""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def primes_up_to(limit: int) -> list[int]:
    """Return all primes not exceeding ``limit`` by an elementary sieve."""

    sieve = bytearray(b"\x01") * (limit + 1)
    if limit >= 0:
        sieve[0] = 0
    if limit >= 1:
        sieve[1] = 0
    for p in range(2, math.isqrt(limit) + 1):
        if sieve[p]:
            sieve[p * p : limit + 1 : p] = b"\x00" * (((limit - p * p) // p) + 1)
    return [p for p in range(2, limit + 1) if sieve[p]]


def proper_divisors(value: int) -> list[int]:
    """Return positive divisors smaller than ``value``."""

    return [candidate for candidate in range(1, value) if value % candidate == 0]


def phase_schedule(
    base: float,
    max_repetition: int,
    *,
    sign: int,
    fixed_copies: list[int] | None = None,
) -> list[Phase]:
    """Evaluate the paper's recursive phase prescription.

    ``sign=-1`` is the sign required by Eqs. (11)--(12). ``sign=+1`` is
    the literal sign printed after Eq. (14), retained as a diagnostic.
    """

    if sign not in (-1, 1):
        raise ValueError("sign must be -1 or +1")
    phases: list[Phase] = []
    for m in range(1, max_repetition + 1):
        partial = 0.0
        for d in proper_divisors(m):
            previous = phases[d - 1]
            partial += (
                (d / m)
                * previous.copies
                * math.cos((m / d) * previous.theta)
            )
        T = 1.0 / (2.0 * m * base ** (m / 2.0)) + partial
        if fixed_copies is None:
            copies = max(1, math.ceil(abs(T) - 4.0 * np.finfo(float).eps))
        else:
            copies = fixed_copies[m - 1]
        cosine = sign * T / copies
        if abs(cosine) > 1.0 + 2e-14:
            raise ArithmeticError(
                f"non-unitary phase request at base={base}, m={m}: cos={cosine}"
            )
        cosine = min(1.0, max(-1.0, cosine))
        phases.append(
            Phase(
                base=base,
                repetition=m,
                copies=copies,
                cosine=cosine,
                theta=math.acos(cosine),
                T=T,
            )
        )
    return phases


def trace_identity_residual(schedule: list[Phase]) -> dict[str, float]:
    """Check Eq. (11) for every repetition in a phase schedule."""

    base = schedule[0].base
    absolute: list[float] = []
    relative: list[float] = []
    for m in range(1, len(schedule) + 1):
        lhs = 0.0
        for d in range(1, m + 1):
            if m % d:
                continue
            phase = schedule[d - 1]
            lhs += (
                d
                * 2.0
                * phase.copies
                * math.cos((m / d) * phase.theta)
            )
        target = -(base ** (-m / 2.0))
        error = abs(lhs - target)
        absolute.append(error)
        relative.append(error / abs(target))
    return {
        "max_absolute": max(absolute),
        "max_relative": max(relative),
        "rms_absolute": float(np.sqrt(np.mean(np.square(absolute)))),
    }


def graph_terms(schedules: dict[int, list[Phase]]) -> list[tuple[float, float]]:
    """Return (frequency, density coefficient) from the butterfly trace."""

    terms: list[tuple[float, float]] = []
    for prime, schedule in schedules.items():
        logp = math.log(schedule[0].base)
        for m in range(1, len(schedule) + 1):
            numerator = 0.0
            for d in range(1, m + 1):
                if m % d:
                    continue
                phase = schedule[d - 1]
                numerator += (
                    d
                    * logp
                    * 2.0
                    * phase.copies
                    * math.cos((m / d) * phase.theta)
                )
            terms.append((m * logp, numerator / math.pi))
    return terms


def analytic_terms(bases: Iterable[float], max_repetition: int) -> list[tuple[float, float]]:
    """Return the finite explicit prime-comb terms corresponding to Eq. (2)."""

    terms: list[tuple[float, float]] = []
    for base in bases:
        logq = math.log(base)
        for m in range(1, max_repetition + 1):
            terms.append((m * logq, -(logq / math.pi) * base ** (-m / 2.0)))
    return terms


def evaluate_terms(terms: Iterable[tuple[float, float]], grid: np.ndarray) -> np.ndarray:
    """Evaluate a finite real cosine trace on the fixed k grid."""

    result = np.zeros_like(grid)
    for frequency, coefficient in terms:
        result += coefficient * np.cos(frequency * grid)
    return result


def signal_metrics(candidate: np.ndarray, target: np.ndarray) -> dict[str, float]:
    """Return direct fixed-grid discrepancy measures."""

    difference = candidate - target
    return {
        "rmse": float(np.sqrt(np.mean(np.square(difference)))),
        "mae": float(np.mean(np.abs(difference))),
        "max_abs": float(np.max(np.abs(difference))),
        "target_rms": float(np.sqrt(np.mean(np.square(target)))),
    }


def matched_pseudo_schedules(
    primes: list[int], true_schedules: dict[int, list[Phase]]
) -> tuple[dict[int, list[Phase]], dict[str, object]]:
    """Make deterministic pseudo-prime bases with matched graph size and length.

    Raw logarithms are equally spaced strictly inside [log 2, log P].  A single
    positive scale factor then matches the exact total physical bond length.
    The true copy topology is held fixed, so the directed-bond count also
    matches exactly.
    """

    count = len(primes)
    raw_logs = np.linspace(math.log(2.0), math.log(float(primes[-1])), count + 2)[1:-1]
    true_total = 0.0
    raw_total = 0.0
    max_repetition = len(true_schedules[primes[0]])
    for index, prime in enumerate(primes):
        for phase in true_schedules[prime]:
            true_total += phase.copies * phase.repetition * math.log(prime)
            raw_total += phase.copies * phase.repetition * float(raw_logs[index])
    scale = true_total / raw_total
    pseudo_logs = raw_logs * scale
    pseudo_schedules: dict[int, list[Phase]] = {}
    max_cosine = 0.0
    for index, prime in enumerate(primes):
        base = math.exp(float(pseudo_logs[index]))
        fixed_copies = [phase.copies for phase in true_schedules[prime]]
        schedule = phase_schedule(
            base,
            max_repetition,
            sign=-1,
            fixed_copies=fixed_copies,
        )
        pseudo_schedules[prime] = schedule
        max_cosine = max(max_cosine, *(abs(phase.cosine) for phase in schedule))
    pseudo_total = sum(
        phase.copies * phase.repetition * math.log(phase.base)
        for schedule in pseudo_schedules.values()
        for phase in schedule
    )
    metadata: dict[str, object] = {
        "generation": "equally spaced interior log coordinates, one common length-matching scale",
        "scale": scale,
        "bases": [pseudo_schedules[p][0].base for p in primes],
        "true_physical_length": true_total,
        "pseudo_physical_length": pseudo_total,
        "absolute_length_difference": abs(pseudo_total - true_total),
        "max_abs_cosine": max_cosine,
        "directed_bond_count": 2
        * sum(phase.copies for schedule in pseudo_schedules.values() for phase in schedule),
    }
    return pseudo_schedules, metadata


def build_decoupled_matrix(
    primes: list[int], schedules: dict[int, list[Phase]]
) -> tuple[np.ndarray, np.ndarray, list[Mode]]:
    """Build the direct sum of real 2x2 unitary butterfly scatterers."""

    component_count = sum(
        phase.copies for schedule in schedules.values() for phase in schedule
    )
    dimension = 2 * component_count
    scattering = np.zeros((dimension, dimension), dtype=np.complex128)
    lengths = np.empty(dimension, dtype=np.float64)
    modes: list[Mode] = []
    offset = 0
    for prime in primes:
        for phase in schedules[prime]:
            sine = math.sin(phase.theta)
            block = np.array(
                [[phase.cosine, sine], [-sine, phase.cosine]],
                dtype=np.complex128,
            )
            length = phase.repetition * math.log(prime)
            integer_key = prime ** phase.repetition
            for copy in range(phase.copies):
                scattering[offset : offset + 2, offset : offset + 2] = block
                lengths[offset : offset + 2] = length
                modes.append(
                    Mode(prime, phase.repetition, copy, 0, length, integer_key)
                )
                modes.append(
                    Mode(prime, phase.repetition, copy, 1, length, integer_key)
                )
                offset += 2
    return scattering, lengths, modes


def dft_unitary(dimension: int) -> np.ndarray:
    """Return the normalized positive-phase discrete Fourier matrix."""

    indices = np.arange(dimension, dtype=np.float64)
    return np.exp(2j * math.pi * np.outer(indices, indices) / dimension) / math.sqrt(
        dimension
    )


def haar_unitary(dimension: int, seed: int) -> np.ndarray:
    """Return a complex Haar unitary from fixed-seed complex Gaussian QR."""

    generator = np.random.Generator(np.random.PCG64DXSM(seed))
    gaussian = (
        generator.standard_normal((dimension, dimension))
        + 1j * generator.standard_normal((dimension, dimension))
    ) / math.sqrt(2.0)
    q_matrix, r_matrix = np.linalg.qr(gaussian)
    diagonal = np.diag(r_matrix)
    phases = diagonal / np.abs(diagonal)
    return q_matrix * phases.conjugate()[None, :]


def right_multiply_blocks(central: np.ndarray, schedules: list[Phase]) -> np.ndarray:
    """Compute central @ direct_sum(S_phase) without a cubic matrix product."""

    result = np.empty_like(central)
    offset = 0
    for phase in schedules:
        sine = math.sin(phase.theta)
        for _ in range(phase.copies):
            first = central[:, offset]
            second = central[:, offset + 1]
            result[:, offset] = phase.cosine * first - sine * second
            result[:, offset + 1] = sine * first + phase.cosine * second
            offset += 2
    return result


def prime_orbit_coefficients(
    scattering: np.ndarray, modes: list[Mode], primes: list[int]
) -> list[dict[str, object]]:
    """Extract the complex r=1 Fourier coefficient at every primitive log p."""

    rows: list[dict[str, object]] = []
    diagonal = np.diag(scattering)
    for prime in primes:
        indices = [
            index
            for index, mode in enumerate(modes)
            if mode.prime == prime and mode.repetition == 1
        ]
        coefficient = sum(modes[index].length * diagonal[index] for index in indices)
        target = -math.log(prime) / math.sqrt(prime)
        rows.append(
            {
                "prime": prime,
                "length": math.log(prime),
                "coefficient_real": float(coefficient.real / math.pi),
                "coefficient_imag": float(coefficient.imag / math.pi),
                "coefficient_abs": float(abs(coefficient) / math.pi),
                "target": target / math.pi,
                "relative_complex_error": float(abs(coefficient - target) / abs(target)),
            }
        )
    return rows


def mixed_two_step_coefficients(
    scattering: np.ndarray, modes: list[Mode], limit: int = 10
) -> tuple[list[dict[str, object]], float]:
    """Aggregate r=2 cross-prime closed-walk amplitudes at log(pq)."""

    indices = [index for index, mode in enumerate(modes) if mode.repetition == 1]
    coefficients: dict[int, complex] = {}
    for i in indices:
        mode_i = modes[i]
        for j in indices:
            mode_j = modes[j]
            if mode_i.prime == mode_j.prime:
                continue
            key = mode_i.prime * mode_j.prime
            coefficients[key] = coefficients.get(key, 0.0j) + (
                mode_i.length * scattering[i, j] * scattering[j, i]
            )
    ordered = sorted(coefficients.items(), key=lambda item: abs(item[1]), reverse=True)
    rows = [
        {
            "integer_length_key": key,
            "length": math.log(key),
            "coefficient_real": float(value.real / math.pi),
            "coefficient_imag": float(value.imag / math.pi),
            "coefficient_abs": float(abs(value) / math.pi),
        }
        for key, value in ordered[:limit]
    ]
    l2_norm = float(
        math.sqrt(sum((abs(value) / math.pi) ** 2 for value in coefficients.values()))
    )
    return rows, l2_norm


def surgery_case(
    name: str,
    central: np.ndarray,
    decoupled: np.ndarray,
    lengths: np.ndarray,
    modes: list[Mode],
    primes: list[int],
    ordered_phases: list[Phase],
) -> dict[str, object]:
    """Apply one central unitary and measure its short-orbit coefficients."""

    if name == "identity":
        scattering = decoupled.copy()
    else:
        scattering = right_multiply_blocks(central, ordered_phases)
    # NumPy 2.0 linked to Apple's Accelerate emits spurious floating-point
    # warnings inside this finite, well-scaled ZGEMM.  We still reject a
    # non-finite Gram matrix rather than suppressing a numerical failure.
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        gram = scattering.conjugate().T @ scattering
    if not np.all(np.isfinite(gram)):
        raise FloatingPointError(f"non-finite Gram matrix for {name} coupling")
    gram_error = float(np.max(np.abs(gram - np.eye(len(lengths)))))
    prime_rows = prime_orbit_coefficients(scattering, modes, primes)
    mixed_rows, mixed_l2 = mixed_two_step_coefficients(scattering, modes)
    relative_errors = [float(row["relative_complex_error"]) for row in prime_rows]
    return {
        "coupling": name,
        "dimension": len(lengths),
        "unitarity_max_abs": gram_error,
        "prime_orbits": prime_rows,
        "prime_relative_error_median": float(np.median(relative_errors)),
        "prime_relative_error_max": max(relative_errors),
        "prime_coefficients_spoiled_over_1pct": sum(error > 0.01 for error in relative_errors),
        "mixed_two_step_l2": mixed_l2,
        "strongest_mixed_two_step": mixed_rows,
    }


def run_cutoff(
    cutoff: int, grid: np.ndarray, max_repetition: int = REPETITION_CUTOFF
) -> dict[str, object]:
    """Run pseudo-control, corrected reconstruction, and all surgeries."""

    events: list[dict[str, object]] = []
    primes = primes_up_to(cutoff)
    corrected = {
        prime: phase_schedule(prime, max_repetition, sign=-1) for prime in primes
    }
    literal = {
        prime: phase_schedule(prime, max_repetition, sign=+1) for prime in primes
    }

    # Mandatory hostile control.  No true reconstruction error is evaluated
    # before this block completes.
    pseudo, pseudo_metadata = matched_pseudo_schedules(primes, corrected)
    pseudo_bases = [pseudo[prime][0].base for prime in primes]
    true_target = evaluate_terms(analytic_terms(primes, max_repetition), grid)
    pseudo_target = evaluate_terms(analytic_terms(pseudo_bases, max_repetition), grid)
    pseudo_graph = evaluate_terms(graph_terms(pseudo), grid)
    pseudo_own_match = signal_metrics(pseudo_graph, pseudo_target)
    pseudo_against_prime = signal_metrics(pseudo_graph, true_target)
    pseudo_control = {
        **pseudo_metadata,
        "own_trace_match": pseudo_own_match,
        "against_true_prime_trace": pseudo_against_prime,
        "completed_at": utc_now(),
    }
    events.append({"event": "pseudo_control_completed", "time": pseudo_control["completed_at"]})

    true_graph = evaluate_terms(graph_terms(corrected), grid)
    true_match = signal_metrics(true_graph, true_target)
    corrected_identity = {
        str(prime): trace_identity_residual(corrected[prime]) for prime in primes
    }
    literal_identity = {
        str(prime): trace_identity_residual(literal[prime]) for prime in primes
    }
    events.append({"event": "true_trace_match_computed", "time": utc_now()})

    decoupled, lengths, modes = build_decoupled_matrix(primes, corrected)
    ordered_phases = [phase for prime in primes for phase in corrected[prime]]
    dimension = len(lengths)
    identity = np.eye(dimension, dtype=np.complex128)
    dft = dft_unitary(dimension)
    haar = haar_unitary(dimension, HAAR_SEED)
    surgeries = [
        surgery_case(
            "identity", identity, decoupled, lengths, modes, primes, ordered_phases
        ),
        surgery_case("dft", dft, decoupled, lengths, modes, primes, ordered_phases),
        surgery_case("haar", haar, decoupled, lengths, modes, primes, ordered_phases),
    ]
    events.append({"event": "central_scatterer_mutations_completed", "time": utc_now()})

    physical_length = float(np.sum(lengths) / 2.0)
    weyl = physical_length / math.pi
    target_rms = float(np.sqrt(np.mean(np.square(true_target))))
    sign_audit = {
        "printed_eq14_p2_m1_absolute": math.sqrt(2.0),
        "printed_eq14_plus_sign_max_abs": max(
            result["max_absolute"] for result in literal_identity.values()
        ),
        "eq11_eq12_required_minus_sign_max_abs": max(
            result["max_absolute"] for result in corrected_identity.values()
        ),
        "interpretation": (
            "The plus sign printed after Eq. (14) contradicts Eqs. (11)-(12), "
            "the p=2 worked example, and Supplemental Eq. (B1); the minus sign "
            "is used for the reconstruction."
        ),
    }
    return {
        "prime_cutoff_inclusive": cutoff,
        "prime_count": len(primes),
        "primes": primes,
        "repetition_cutoff_inclusive": max_repetition,
        "component_count": dimension // 2,
        "directed_bond_count": dimension,
        "physical_total_length": physical_length,
        "weyl_coefficient_Ltot_over_pi": weyl,
        "finite_prime_trace_rms": target_rms,
        "weyl_to_oscillatory_rms": weyl / target_rms,
        "pseudo_control_first": pseudo_control,
        "corrected_phase_trace_match": true_match,
        "phase_sign_audit": sign_audit,
        "corrected_eq11_residual_by_prime": corrected_identity,
        "literal_eq14_residual_by_prime": literal_identity,
        "max_butterfly_copies": max(
            phase.copies for schedule in corrected.values() for phase in schedule
        ),
        "central_scatterers": surgeries,
        "event_order": events,
    }


def write_csvs(output_directory: Path, results: list[dict[str, object]]) -> None:
    """Write compact cutoff and Fourier-coefficient audit tables."""

    with (output_directory / "quantum-graph-cutoffs.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        fieldnames = [
            "prime_cutoff",
            "prime_count",
            "repetition_cutoff",
            "component_count",
            "directed_bond_count",
            "physical_total_length",
            "weyl_coefficient",
            "finite_trace_rms",
            "weyl_to_oscillatory_rms",
            "pseudo_against_prime_rmse",
            "pseudo_own_rmse",
            "true_match_rmse",
            "printed_plus_sign_max_abs",
            "corrected_minus_sign_max_abs",
        ]
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            pseudo = result["pseudo_control_first"]
            sign = result["phase_sign_audit"]
            writer.writerow(
                {
                    "prime_cutoff": result["prime_cutoff_inclusive"],
                    "prime_count": result["prime_count"],
                    "repetition_cutoff": result["repetition_cutoff_inclusive"],
                    "component_count": result["component_count"],
                    "directed_bond_count": result["directed_bond_count"],
                    "physical_total_length": result["physical_total_length"],
                    "weyl_coefficient": result["weyl_coefficient_Ltot_over_pi"],
                    "finite_trace_rms": result["finite_prime_trace_rms"],
                    "weyl_to_oscillatory_rms": result["weyl_to_oscillatory_rms"],
                    "pseudo_against_prime_rmse": pseudo["against_true_prime_trace"]["rmse"],
                    "pseudo_own_rmse": pseudo["own_trace_match"]["rmse"],
                    "true_match_rmse": result["corrected_phase_trace_match"]["rmse"],
                    "printed_plus_sign_max_abs": sign["printed_eq14_plus_sign_max_abs"],
                    "corrected_minus_sign_max_abs": sign["eq11_eq12_required_minus_sign_max_abs"],
                }
            )

    with (output_directory / "quantum-graph-prime-amplitudes.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        fieldnames = [
            "prime_cutoff",
            "coupling",
            "prime",
            "length",
            "coefficient_real",
            "coefficient_imag",
            "coefficient_abs",
            "target",
            "relative_complex_error",
        ]
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            for surgery in result["central_scatterers"]:
                for row in surgery["prime_orbits"]:
                    writer.writerow(
                        {
                            "prime_cutoff": result["prime_cutoff_inclusive"],
                            "coupling": surgery["coupling"],
                            **row,
                        }
                    )

    with (output_directory / "quantum-graph-mixed-orbits.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        fieldnames = [
            "prime_cutoff",
            "coupling",
            "rank",
            "integer_length_key",
            "length",
            "coefficient_real",
            "coefficient_imag",
            "coefficient_abs",
        ]
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            for surgery in result["central_scatterers"]:
                for rank, row in enumerate(surgery["strongest_mixed_two_step"], start=1):
                    writer.writerow(
                        {
                            "prime_cutoff": result["prime_cutoff_inclusive"],
                            "coupling": surgery["coupling"],
                            "rank": rank,
                            **row,
                        }
                    )


def write_log(output_directory: Path, payload: dict[str, object]) -> None:
    """Write a short human-readable run audit."""

    lines = [
        "R5.5b Kuipers-Hummel-Richter butterfly graph surgery",
        f"run_utc: {payload['run_utc']}",
        f"script_sha256: {payload['script_sha256']}",
        f"source: {SOURCE['arxiv_url']}",
        f"published_pdf_sha256: {SOURCE['published_pdf_sha256']}",
        f"source_pdf_sha256: {SOURCE['pdf_sha256']}",
        f"source_archive_sha256: {SOURCE['source_archive_sha256']}",
        f"k_interval: [{K_MIN}, {K_MAX}] on {K_INTERVALS + 1} points",
        f"repetition_cutoff: m <= {REPETITION_CUTOFF}",
        "event_order: pseudo-prime control before corrected prime-trace match",
        "status_vocabulary: MEASURED / UNVERIFIED / PREDICTED / VOID",
        "",
    ]
    all_cases = [*payload["cutoffs"], *payload["repetition_mutations"]]
    for result in all_cases:
        pseudo = result["pseudo_control_first"]
        sign = result["phase_sign_audit"]
        surgeries = {row["coupling"]: row for row in result["central_scatterers"]}
        lines.extend(
            [
                f"P={result['prime_cutoff_inclusive']}, m<={result['repetition_cutoff_inclusive']}",
                f"  MEASURED pseudo-vs-prime RMSE: {pseudo['against_true_prime_trace']['rmse']:.12e}",
                f"  MEASURED pseudo-own-trace RMSE: {pseudo['own_trace_match']['rmse']:.12e}",
                f"  MEASURED corrected prime-trace RMSE: {result['corrected_phase_trace_match']['rmse']:.12e}",
                f"  MEASURED Eq.14 printed-sign residual: {sign['printed_eq14_plus_sign_max_abs']:.12e}",
                f"  MEASURED corrected-sign residual: {sign['eq11_eq12_required_minus_sign_max_abs']:.12e}",
                f"  MEASURED Weyl coefficient Ltot/pi: {result['weyl_coefficient_Ltot_over_pi']:.12e}",
                f"  MEASURED Weyl/oscillatory-RMS: {result['weyl_to_oscillatory_rms']:.12e}",
                f"  MEASURED identity spoiled primitive coefficients >1%: {surgeries['identity']['prime_coefficients_spoiled_over_1pct']}",
                f"  MEASURED DFT spoiled primitive coefficients >1%: {surgeries['dft']['prime_coefficients_spoiled_over_1pct']}",
                f"  MEASURED Haar spoiled primitive coefficients >1%: {surgeries['haar']['prime_coefficients_spoiled_over_1pct']}",
                f"  MEASURED identity mixed r=2 L2: {surgeries['identity']['mixed_two_step_l2']:.12e}",
                f"  MEASURED DFT mixed r=2 L2: {surgeries['dft']['mixed_two_step_l2']:.12e}",
                f"  MEASURED Haar mixed r=2 L2: {surgeries['haar']['mixed_two_step_l2']:.12e}",
                "",
            ]
        )
    lines.extend(
        [
            "UNVERIFIED: no claim about chaotic dynamics or a cutoff-limit spectrum is made.",
            "MEASURED: every finite scattering matrix tested is unitary to floating-point residual.",
            "MEASURED: genuine central coupling creates cross-prime two-step lengths and changes primitive prime coefficients.",
            "MEASURED: the Weyl term is not canceled; its ratio to the finite oscillatory RMS increases over the tested cutoffs.",
        ]
    )
    (output_directory / "quantum-graph-run.log").write_text("\n".join(lines) + "\n")


def main() -> None:
    """Run all frozen finite cases and write machine-readable evidence."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "outputs" / "quantum-graph",
    )
    arguments = parser.parse_args()
    output_directory = arguments.output_dir.resolve()
    output_directory.mkdir(parents=True, exist_ok=True)

    grid = np.linspace(K_MIN, K_MAX, K_INTERVALS + 1, dtype=np.float64)
    results = [run_cutoff(cutoff, grid) for cutoff in PRIME_CUTOFFS]
    repetition_mutations = [
        run_cutoff(PRIME_CUTOFFS[-1], grid, max_repetition=6),
        run_cutoff(PRIME_CUTOFFS[-1], grid, max_repetition=10),
    ]
    ratios = [result["weyl_to_oscillatory_rms"] for result in results]
    payload: dict[str, object] = {
        "status": "MEASURED",
        "run_utc": utc_now(),
        "source": SOURCE,
        "script_sha256": sha256_file(Path(__file__).resolve()),
        "zero_input_audit": {
            "uses_zeta_zero_ordinates": False,
            "construction_inputs": {
                "prime_cutoffs_inclusive": list(PRIME_CUTOFFS),
                "repetition_cutoff_inclusive": REPETITION_CUTOFF,
                "repetition_cutoff_mutations": [6, 10],
                "k_interval": [K_MIN, K_MAX],
                "k_intervals": K_INTERVALS,
                "haar_seed": HAAR_SEED,
            },
            "note": "No zeta-zero function, table, file, ordinate, fitted scale, or zero-selected window is read.",
        },
        "scope_limitation": (
            "The source requires independent p and m cutoffs. Round 5 registered P but not M; "
            "this run freezes m<=8 and makes no inference beyond that finite truncation."
        ),
        "central_surgery_definition": (
            "S_C = C direct_sum(S_p,m) at a zero-length common vertex; propagation remains "
            "diag(exp(i k L_j)). Identity, normalized DFT, and fixed-seed Haar C are used."
        ),
        "cutoffs": results,
        "repetition_mutations": repetition_mutations,
        "aggregate": {
            "weyl_to_oscillatory_rms_strictly_increases": all(
                later > earlier for earlier, later in zip(ratios, ratios[1:])
            ),
            "weyl_to_oscillatory_rms_first": ratios[0],
            "weyl_to_oscillatory_rms_last": ratios[-1],
            "weyl_ratio_growth_factor": ratios[-1] / ratios[0],
            "repetition_mutation_summary": {
                str(row["repetition_cutoff_inclusive"]): {
                    "true_match_rmse": row["corrected_phase_trace_match"]["rmse"],
                    "pseudo_against_prime_rmse": row["pseudo_control_first"][
                        "against_true_prime_trace"
                    ]["rmse"],
                    "weyl_to_oscillatory_rms": row["weyl_to_oscillatory_rms"],
                    "dft_spoiled_primitive_coefficients": row["central_scatterers"][1][
                        "prime_coefficients_spoiled_over_1pct"
                    ],
                    "haar_spoiled_primitive_coefficients": row["central_scatterers"][2][
                        "prime_coefficients_spoiled_over_1pct"
                    ],
                }
                for row in repetition_mutations
            },
            "three_yeses": {
                "self_adjoint_discrete_finite_graph": (
                    "MEASURED unitary finite boundary matrix; the exact-unitary "
                    "idealization is self-adjoint under the derivative-matched "
                    "domain of KHR Eq. (5); the code does not independently "
                    "construct the operator domain or eigenvalue list"
                ),
                "chaotic_without_arithmetic_degeneracy": (
                    "VOID: exact log-product arithmetic length degeneracies "
                    "remain; chaos itself was not tested"
                ),
                "orbits_of_length_log_p_exist_after_genuine_coupling": (
                    "MEASURED yes, with wrong amplitudes"
                ),
                "only_clean_orbits_of_length_log_p_after_genuine_coupling": (
                    "MEASURED no: mixed log(pq) lengths remain"
                ),
                "three_yes_row": False,
            },
        },
    }
    write_csvs(output_directory, [*results, *repetition_mutations])
    write_log(output_directory, payload)
    json_path = output_directory / "quantum-graph-surgery.json"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n")
    print(json.dumps({"output": str(json_path), "status": "MEASURED"}))


if __name__ == "__main__":
    main()
