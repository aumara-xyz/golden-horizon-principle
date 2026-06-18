#!/usr/bin/env python3
"""Claim audit for the GHP music/surprise/horizon synthesis.

This script checks only narrow, testable pieces:

- timing modulation can carry information when jitter is bounded;
- rational frequency ratios phase-lock while phi avoids exact finite-window locking;
- relativistic proper-time factor decreases toward zero as v approaches c.

It does not prove GHP, does not solve gravity, does not prove consciousness,
and does not turn entropic-gravity / FEP analogy into established physics.
"""

from __future__ import annotations

import csv
import math
import random
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "ghp_music_surprise_claim_audit_outputs"


@dataclass
class AuditResult:
    check_id: str
    claim: str
    status: str
    metric: str
    value: str
    safest_read: str
    limit: str


def phi() -> float:
    return (1.0 + math.sqrt(5.0)) / 2.0


def nearest_symbol(value: float, symbols: list[float]) -> int:
    return min(range(len(symbols)), key=lambda idx: abs(value - symbols[idx]))


def timing_modulation_check(seed: int = 1618, trials: int = 8000) -> AuditResult:
    """Check whether timing intervals can carry symbols under bounded jitter."""

    rng = random.Random(seed)
    ph = phi()
    symbols = [
        1.0,
        1.0 + ph ** -3,
        1.0 + ph ** -2,
        1.0 + ph ** -1,
    ]

    def accuracy(jitter_sigma: float, modulated: bool) -> float:
        correct = 0
        for _ in range(trials):
            label = rng.randrange(len(symbols))
            base = symbols[label] if modulated else 1.0
            observed = base + rng.gauss(0.0, jitter_sigma)
            decoded = nearest_symbol(observed, symbols)
            correct += decoded == label
        return correct / trials

    low_jitter = accuracy(jitter_sigma=0.015, modulated=True)
    high_jitter = accuracy(jitter_sigma=0.220, modulated=True)
    static = accuracy(jitter_sigma=0.015, modulated=False)

    if not (low_jitter > 0.90 and high_jitter < low_jitter and static < 0.35):
        raise AssertionError(
            "Timing modulation sanity check failed: expected low-jitter modulation "
            "to carry more information than static timing and noisy timing."
        )

    return AuditResult(
        check_id="MS-001",
        claim="Timing modulation can carry information beyond static on/off pulses.",
        status="pass / toy telemetry",
        metric="decoder_accuracy_low_jitter; decoder_accuracy_high_jitter; static_accuracy",
        value=f"{low_jitter:.4f}; {high_jitter:.4f}; {static:.4f}",
        safest_read=(
            "A time-domain pulse channel can encode recoverable symbols when interval "
            "variation is preserved and jitter is bounded."
        ),
        limit=(
            "This supports Chronos-style timing-channel intuition only. It does not "
            "prove semantic understanding, consciousness, physics, or GHP."
        ),
    )


def phase_lock_check(max_q: int = 250) -> AuditResult:
    """Compare exact rational locking with bounded non-locking for phi rotation."""

    alpha_rational = 1.0 / 2.0
    alpha_phi = 1.0 / phi()
    alpha_sqrt2 = math.sqrt(2.0) - 1.0

    def min_return(alpha: float) -> tuple[int, float]:
        best_q = 0
        best_err = float("inf")
        for q in range(1, max_q + 1):
            err = abs(q * alpha - round(q * alpha))
            if err < best_err:
                best_q = q
                best_err = err
        return best_q, best_err

    q_rat, err_rat = min_return(alpha_rational)
    q_phi, err_phi = min_return(alpha_phi)
    q_sqrt2, err_sqrt2 = min_return(alpha_sqrt2)

    if not (err_rat == 0.0 and err_phi > 0.0):
        raise AssertionError("Phase-lock sanity check failed.")

    return AuditResult(
        check_id="MS-002",
        claim="Phi-like irrational offset resists exact phase-locking in a finite rational grid.",
        status="pass / bounded sanity check",
        metric="min_return_error_rational; min_return_error_phi; min_return_error_sqrt2",
        value=(
            f"q={q_rat}, err={err_rat:.6g}; "
            f"q={q_phi}, err={err_phi:.6g}; "
            f"q={q_sqrt2}, err={err_sqrt2:.6g}"
        ),
        safest_read=(
            "A rational ratio locks exactly; phi does not lock exactly in the checked "
            "finite window. This is compatible with anti-locking channel language."
        ),
        limit=(
            "This does not prove phi is always optimal, does not prove a physical "
            "communication law, and does not prove a permanent open channel."
        ),
    )


def relativity_time_dilation_check() -> AuditResult:
    """Check the narrow SR statement that proper-time factor falls as beta approaches 1."""

    betas = [0.0, 0.5, 0.9, 0.99, 0.999, 0.999999]
    factors = [math.sqrt(1.0 - beta * beta) for beta in betas]

    monotone = all(factors[idx] > factors[idx + 1] for idx in range(len(factors) - 1))
    if not monotone or not factors[-1] < 0.002:
        raise AssertionError("Relativistic proper-time factor sanity check failed.")

    return AuditResult(
        check_id="MS-003",
        claim="As speed approaches c, timelike proper-time factor approaches zero.",
        status="pass / established SR formula",
        metric="sqrt(1-beta^2) at beta=0,0.5,0.9,0.99,0.999,0.999999",
        value=", ".join(f"{factor:.8f}" for factor in factors),
        safest_read=(
            "The time-dilation limit is real for timelike observers approaching c."
        ),
        limit=(
            "A photon has no valid rest frame in special relativity. The formula does "
            "not imply zero entropy, infinite compression, or an instantaneous quantum realm."
        ),
    )


def quarantined_claims() -> list[AuditResult]:
    """Claims that should stay as synthesis candidates, not tests passed."""

    return [
        AuditResult(
            check_id="MS-Q001",
            claim="A flashing 2D boundary creates time.",
            status="quarantine / formal model needed",
            metric="not numerically tested",
            value="n/a",
            safest_read=(
                "Holographic and boundary-record language is relevant to GHP, but this "
                "claim needs a precise boundary dynamics model before it can be tested."
            ),
            limit=(
                "Do not state this as established physics. Use 'candidate boundary-time "
                "analogy' until a formal map is built."
            ),
        ),
        AuditResult(
            check_id="MS-Q002",
            claim="Gravity is the universe performing active inference.",
            status="quarantine / analogy only",
            metric="not numerically tested",
            value="n/a",
            safest_read=(
                "Entropic gravity and FEP share variational / entropy-flavored language, "
                "so this is a useful bridge metaphor."
            ),
            limit=(
                "Verlinde-style gravity is not settled physics, and FEP is not currently "
                "identical to gravitational dynamics."
            ),
        ),
        AuditResult(
            check_id="MS-Q003",
            claim="Quantum reality is instantaneous on the other side of light.",
            status="quarantine / correction required",
            metric="not numerically tested",
            value="n/a",
            safest_read=(
                "Quantum correlations are nonclassical, but usable information still obeys "
                "no-signalling constraints."
            ),
            limit=(
                "Do not use 'other side of c' as a literal physics claim without a defined "
                "model and no-signalling discipline."
            ),
        ),
        AuditResult(
            check_id="MS-Q004",
            claim="Aukora completes GHP because it resembles a physics engine.",
            status="quarantine / bridge-lab status",
            metric="not numerically tested",
            value="n/a",
            safest_read=(
                "Aukora can become a major engineering proving ground for bounded observer "
                "loops, receipt formation, memory custody, and active-inference-like behavior."
            ),
            limit=(
                "Software success remains engineering evidence, not physical proof of GHP."
            ),
        ),
    ]


def write_csv(results: list[AuditResult]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "claim_audit_summary.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "check_id",
                "claim",
                "status",
                "metric",
                "value",
                "safest_read",
                "limit",
            ],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(result.__dict__)


def write_report(results: list[AuditResult]) -> None:
    lines = [
        "# GHP Music / Surprise / Horizon Claim Audit",
        "",
        "Status: toy telemetry and claim hygiene only.",
        "",
        "This audit tests narrow pieces of the music/surprise synthesis. It does not complete GHP, solve gravity, prove consciousness, or turn software architecture into physics evidence.",
        "",
        "## Bottom Line",
        "",
        "- Timing modulation can carry information under bounded jitter.",
        "- Phi-style irrational offsets support anti-locking language against exact rational lock-in, but do not prove universal optimality.",
        "- Relativistic time dilation toward `c` is real, but the entropy / infinite-compression interpretation is not derived by this toy.",
        "- Holographic-boundary time, entropic-gravity-as-active-inference, and quantum-instantaneous language remain synthesis candidates, not proven claims.",
        "",
        "## Results",
        "",
    ]
    for result in results:
        lines.extend(
            [
                f"### {result.check_id}: {result.status}",
                "",
                f"- Claim: {result.claim}",
                f"- Metric: {result.metric}",
                f"- Value: {result.value}",
                f"- Safest read: {result.safest_read}",
                f"- Limit: {result.limit}",
                "",
            ]
        )

    lines.extend(
        [
            "## GHP Integration Guidance",
            "",
            "Use the synthesis as a research map like this:",
            "",
            "```text",
            "music / cymatics -> timing-channel and resonance analogy",
            "holography -> boundary-record vocabulary",
            "relativity -> finite signal-speed and time-dilation constraint",
            "entropic gravity -> variational / entropy analogy",
            "FEP -> active-inference architecture for agents",
            "Aukora -> engineering proving ground for bounded observer loops",
            "```",
            "",
            "Do not collapse these into one proven identity yet.",
            "",
            "## Best Current Sentence",
            "",
            "```text",
            "GHP is testing whether finite boundaries turn hidden state into trustworthy record, action, memory, and learning through timing, compression, and governed access.",
            "```",
            "",
        ]
    )
    (OUT / "report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    results = [
        timing_modulation_check(),
        phase_lock_check(),
        relativity_time_dilation_check(),
        *quarantined_claims(),
    ]
    write_csv(results)
    write_report(results)
    print(f"Wrote {OUT / 'report.md'}")
    for result in results:
        print(f"{result.check_id}: {result.status} :: {result.value}")


if __name__ == "__main__":
    main()
