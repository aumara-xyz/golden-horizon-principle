#!/usr/bin/env python3
"""
op179_nu_to_beta.py — SYK corridor (P-002a / OP 111 / OP 179) nu -> beta verdict bookkeeping.

STATUS: pre-compute artifact. Deterministic bucket bookkeeping ONLY. This module
contains NO physics choice: the nu -> beta channel-exponent conversion is an
INJECTED PORT (see `ChannelExponentAssignment`) that the caller must supply
explicitly and that a preregistration must pin BEFORE any run. There is no
default, and any attempt to run without an explicit assignment raises.

Why the port exists (verbatim from the repo's own documents; nothing below is
reconstructed from memory):

  RESEARCH_LEDGER.md, row P-002a (Part I, section 2):
    "| P-002a | SYK β corridor | **NEVER RUN** (no preregistered β ever
    computed) | Repaired pipeline + completed N=22 + a written ν→β conversion
    protocol satisfying OP 179. Until then: **the kill window [1.95, 2.05] is
    the only live content** — a generic-random result there falsifies cleanly |"

  RESEARCH_LEDGER.md, row OP 111 (Part I, section 2):
    "| OP 111 | SYK decision branch | **OPEN** | The converter + bucket logic
    (incl. quotient-confirmation branch), specified but never coded |"

  GHP_BOUNDARY_PROGRAM_v2.md section 6.3:
    "no script exists that converts a collapse-ν into the pre-registered
    β_crit or applies the decision buckets."

  GHP_v1_618_MASTER.md, AE.10 (OP 179):
    "**OP 179 — Operational definition of β_fusion.** Per AE.8, the band
    [1/φ, φ] bounds a fusion-channel exponent β_fusion that is distinct from
    any CFT correlation-length exponent. Derive the operational procedure by
    which β_fusion is extracted from a finite physical system (SYK at N=22,
    mass-deformed golden chain DMRG, or Rydberg-ladder critical experiment).
    Specify the observable, the data pipeline, and the fit protocol before any
    experimental data is allowed to inform the definition (per §5.10A.5
    anti-p-hacking discipline). **Status:** OPEN. Required for the band to
    have experimental contact."

NON-UNIQUENESS of the channel-exponent assignment (verbatim,
GHP_v1_618_MASTER.md AE.9 §5.10A.3):

    "(i) The channel-exponent assignment β(1) = 1/φ, β(τ) = φ is not unique.
    Alternative natural assignments give 1.412 (CFT-weight-based), 1.764
    (squared eigenvalues), or 1.328 (RMS form). No first-principles argument
    currently forces the magnitude-of-eigenvalue assignment over the
    alternatives."

and the magnitude-of-eigenvalue candidate itself (verbatim, same section):

    "Given Fibonacci fusion rule τ ⊗ τ = 1 ⊕ τ with fusion probabilities
    P(1) = 1/φ², P(τ) = 1/φ (Verlinde-derived), and under the specific
    channel-exponent assignment β(1) = 1/φ, β(τ) = φ (magnitudes of the
    eigenvalues of N_τ):
        β_crit = P(1) β(1) + P(τ) β(τ) = 1/φ³ + 1 ≈ 1.236"

NOTE these four numbers (1.236 / 1.328 / 1.412 / 1.764) are candidate
β_crit POINT VALUES under alternative channel weightings. The sources contain
NO formula mapping a measured collapse exponent ν to β_crit — that is exactly
the OP 179 gap. Therefore the conversion FUNCTION is MISSING-INPUT here and
must be injected; the table below documents the candidate landscape so the
physics choice is visible and pre-committable, never silently defaulted.

--------------------------------------------------------------------------
THE DECISION BUCKETS, AS WRITTEN
--------------------------------------------------------------------------

Point rule (verbatim, GHP_v1_618_MASTER.md §5.10A.6.3 "Decision rule
(four-bucket, fixed in advance)"):

    "The decision buckets are frozen before any DMRG output is generated:
     - **Strong pass.** β_crit ∈ [0.95·φ^-1, 1.05·φ^-1] ∪ [0.95·φ, 1.05·φ].
     - **In-band.** β_crit ∈ [1/φ, φ] outside the strong-pass neighborhoods.
     - **Boundary.** β_crit ∈ [0.95·φ^-2, 1.05·φ^-2] ∪ [0.95·φ^2, 1.05·φ^2].
     - **Kill.** β_crit ∈ [1.95, 2.05].
     Outside-band / outside-boundary results are reported as such. They do
     not get silently reclassified into in-band by widening the intervals
     after inspection."

CI rule (verbatim, GHP_v1_618_MASTER.md §5.10A.3 "Three-bucket decision
rule" — "the four-bucket explicit-CI version (Option B in `D2_BAND_v2.md`
§7)"):

    "- β_crit 95% CI entirely inside B1 → **strong pass.** Consistent with
       Postulate P in its narrowest form.
     - β_crit 95% CI overlaps B1 but is not contained within it → **boundary
       region.** Inconclusive. Requires more data or tighter error bars. Does
       NOT count as pass or kill.
     - β_crit 95% CI outside B1 and outside K → **outside band.** Non-kill,
       non-pass. Framework must investigate a specific alternative; does not
       get to widen B1 retrospectively.
     - β_crit 95% CI entirely inside K → **kill.** Module C demoted per the
       v0.669 rule preserved verbatim in §5.10A.4 below."

Band definitions (verbatim, GHP_v1_618_MASTER.md §5.10A.2 "The
pre-registered band"):

    "**Primary band B1: β_crit ∈ [1/φ, φ] = [0.618034, 1.618034].**
     **Extended band B2: β_crit ∈ [1/φ², φ] = [0.381966, 1.618034].**
     **Kill window K: β_crit ∈ [1.95, 2.05].**
     B1's endpoints are |λ_±| = {1/φ, φ}, the magnitudes of the Fibonacci
     fusion matrix eigenvalues (§5.10B). K is the Dyson β_D = 2
     generic-spectrum target preserved verbatim from v0.669."

--------------------------------------------------------------------------
KILL WINDOW FLIP LOGIC (Gate 5 / Kill Condition 9), AS SOURCED
--------------------------------------------------------------------------

Alias unification (verbatim, GHP_BOUNDARY_PROGRAM_v2.md §0.2 errata E-1):

    "**E-1 · Numbering aliases unified (no content change).** ... Canonical
    mapping, binding from v2 forward: **\"Gate 5\" (short paper) ≡ \"Kill
    Condition 9\" (this paper)** — the SYK generic-window kill."

What firing means (verbatim, GHP_BOUNDARY_PROGRAM_v2.md §6.1):

    "the pre-registered kill window K = [1.95, 2.05] (§5.10A.2) is the
    generic-observer target, and hitting it fires **Kill Condition 9**
    (§5.10, §6.2 kill list) — Module C loses its physics spine and the
    framework retains only its architectural (Module R) and engineering
    (Module A) content."

Demotion consequence (verbatim, GHP_v1_618_MASTER.md §5.10A.4
"Kill-condition demotion — preserved verbatim from v0.669"):

    "- If **β ≈ 2** within stable error bars across the finite-N sequence,
       then the **critical φ-dynamics claim is false**.
     ...
     This does **not** kill the Fibonacci minimum. It kills the stronger
     claim that the observer itself sits at a φ-critical dynamical point."

Short-paper statement (verbatim, GHP_CORE_v3.md §10):

    "- The SYK β corridor's exponent lands cleanly in the kill window
       [1.95, 2.05] (generic-random behavior)."

--------------------------------------------------------------------------
QUOTIENT-CONFIRMATION BRANCH (the "third bucket"), AS SOURCED
--------------------------------------------------------------------------

Alias (verbatim, GHP_CORE_v3.md Appendix B):

    "- Cross-document numbering reconciled: the quotient-confirmation branch
       is the **third bucket** uniformly (was \"third bucket\" vs \"fourth
       branch\")"

Branch definition (verbatim, GHP_v1_618_MASTER.md Addendum M.1):

    "> **ν ≈ 0.7 may count as quotient-confirmation rather than failure.**
     This does not mean \"promote every 0.7-looking number to victory.\"
     It means the decision logic should preserve a fourth branch:
     - if the exponent lands stably near the tricritical / quotient lane
       rather than the φ lane or generic GUE lane,
     - then Module C may be weakened, not killed, and the quotient principle
       may be what survived.
     This branch should be treated as a named possibility, not as
     after-the-fact excuse-making."

M.1 is stated in ν space and gives NO numeric tolerance for "stably near";
the tolerance is therefore MISSING-INPUT and must be supplied explicitly by
a preregistration (see `m1_quotient_confirmation_flag`). No default is
provided.

--------------------------------------------------------------------------
Implementation notes (bookkeeping decisions, disclosed):
- FLIP PRECEDENCE (added after adversarial review, 2026-08-01): when a CI is
  supplied, the CI rule governs Kill Condition 9 (master 5.10A.3: boundary-
  region CI "Does NOT count as pass or kill"; 5.10A.4: demotion requires
  "within stable error bars"). Point-rule-only flips occur only when no CI
  exists. The original draft fired on point-OR-CI; the verifier's probe
  (beta=2.0, CI=(1.5,2.5)) exposed that as a spurious-falsification path.
- The point-rule buckets are checked in the order written in §5.10A.6.3
  (strong pass, in-band, boundary, kill, else outside). Numerically the only
  interval contact is between the strong-pass neighborhoods and B1 (resolved
  by the source's own words "outside the strong-pass neighborhoods"); the
  strong-pass lower neighborhood [0.95/φ, 1.05/φ] ≈ [0.5871, 0.6489] extends
  slightly below the B1 floor 0.618034, and per the rule AS WRITTEN such a
  value is still Strong pass. This is applied as written, not reinterpreted.
- φ is computed as (1+sqrt(5))/2; the sources' six-decimal band endpoints
  [0.618034, 1.618034] agree with 1/φ and φ at that precision.

Self-test: `python3 op179_nu_to_beta.py` runs synthetic values covering
every bucket in both rules and asserts the injected-port refusal.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Optional, Tuple

PHI: float = (1.0 + math.sqrt(5.0)) / 2.0

# Band constants exactly as defined in GHP_v1_618_MASTER.md §5.10A.2 (quoted
# in the module docstring). B1/B2 endpoints are the exact algebraic values;
# the kill window is the literal pre-registered decimal pair.
B1: Tuple[float, float] = (1.0 / PHI, PHI)                # [0.618034, 1.618034]
B2: Tuple[float, float] = (1.0 / PHI ** 2, PHI)           # [0.381966, 1.618034]
KILL_WINDOW: Tuple[float, float] = (1.95, 2.05)           # K, verbatim

# §5.10A.6.3 neighborhoods, exactly as written.
STRONG_PASS_LOW: Tuple[float, float] = (0.95 / PHI, 1.05 / PHI)
STRONG_PASS_HIGH: Tuple[float, float] = (0.95 * PHI, 1.05 * PHI)
BOUNDARY_LOW: Tuple[float, float] = (0.95 / PHI ** 2, 1.05 / PHI ** 2)
BOUNDARY_HIGH: Tuple[float, float] = (0.95 * PHI ** 2, 1.05 * PHI ** 2)

# ---------------------------------------------------------------------------
# The INJECTED PORT: nu -> beta channel-exponent assignment.
# ---------------------------------------------------------------------------

#: Candidate β_crit point values under the non-unique channel-exponent
#: assignments, VERBATIM from GHP_v1_618_MASTER.md AE.9 §5.10A.3. These are
#: documentation of the candidate landscape, NOT conversion functions: the
#: sources contain no ν→β formula (that gap is OP 179). Keys are the
#: assignment names as the source names them.
AE9_CANDIDATE_BETA_TABLE = {
    "magnitude-of-eigenvalue": 1.236,   # "β_crit = P(1)β(1) + P(τ)β(τ) = 1/φ³ + 1 ≈ 1.236"
    "RMS form": 1.328,                  # "1.328 (RMS form)"
    "CFT-weight-based": 1.412,          # "1.412 (CFT-weight-based)"
    "squared eigenvalues": 1.764,       # "1.764 (squared eigenvalues)"
}


@dataclass(frozen=True)
class ChannelExponentAssignment:
    """The injected physics choice converting a measured collapse exponent ν
    into the pre-registered β_crit.

    MUST be constructed explicitly by the caller and pinned by a signed
    preregistration before any run (per §5.10A.5 anti-p-hacking discipline
    and the OP 179 operational-definition demand). There is no default.

    Fields:
      name        — assignment label; if it corresponds to one of the AE.9
                    candidates, use the source's own name (see
                    AE9_CANDIDATE_BETA_TABLE keys).
      convert     — the ν→β map. The sources do not define this function
                    (MISSING-INPUT / OP 179); supplying it is a physics
                    decision that must be preregistered, not defaulted.
      provenance  — where this choice was committed (prereg file + section +
                    signature state). Refuse to run against "MISSING".
    """
    name: str
    convert: Callable[[float], float]
    provenance: str

    def __post_init__(self) -> None:
        if not callable(self.convert):
            raise TypeError("ChannelExponentAssignment.convert must be callable")
        if not self.name or not self.provenance:
            raise ValueError(
                "ChannelExponentAssignment requires an explicit name and "
                "provenance; the nu->beta choice may never be silent."
            )


class MissingAssignmentError(RuntimeError):
    """Raised when a conversion is attempted without an injected assignment."""


# ---------------------------------------------------------------------------
# Bucket logic, as written.
# ---------------------------------------------------------------------------

def _in(x: float, iv: Tuple[float, float]) -> bool:
    return iv[0] <= x <= iv[1]


def beta_bucket_point(beta: float) -> str:
    """Apply the §5.10A.6.3 four-bucket point rule exactly as written.

    Returns one of: 'STRONG_PASS', 'IN_BAND', 'BOUNDARY', 'KILL', 'OUTSIDE'.
    'OUTSIDE' is the source's "Outside-band / outside-boundary results are
    reported as such" clause.
    """
    if not isinstance(beta, (int, float)) or isinstance(beta, bool) or math.isnan(beta):
        raise ValueError("beta must be a real number")
    if _in(beta, STRONG_PASS_LOW) or _in(beta, STRONG_PASS_HIGH):
        return "STRONG_PASS"
    if _in(beta, B1):
        return "IN_BAND"
    if _in(beta, BOUNDARY_LOW) or _in(beta, BOUNDARY_HIGH):
        return "BOUNDARY"
    if _in(beta, KILL_WINDOW):
        return "KILL"
    return "OUTSIDE"


def beta_bucket_ci(ci_low: float, ci_high: float) -> str:
    """Apply the §5.10A.3 four-bucket explicit-CI rule (Option B) as written.

    Returns one of: 'STRONG_PASS', 'BOUNDARY_REGION', 'OUTSIDE_BAND', 'KILL',
    'UNCLASSIFIED_BY_RULE'.

    The four written branches are checked literally. A CI that matches none
    of them (e.g. one straddling K without touching B1) is reported as
    'UNCLASSIFIED_BY_RULE' rather than silently forced into a bucket —
    consistent with §5.10A.6.3's no-silent-reclassification clause.
    """
    if math.isnan(ci_low) or math.isnan(ci_high) or ci_low > ci_high:
        raise ValueError("CI must be a well-ordered pair of real numbers")
    inside_b1 = B1[0] <= ci_low and ci_high <= B1[1]
    overlaps_b1 = ci_high >= B1[0] and ci_low <= B1[1]
    inside_k = KILL_WINDOW[0] <= ci_low and ci_high <= KILL_WINDOW[1]
    overlaps_k = ci_high >= KILL_WINDOW[0] and ci_low <= KILL_WINDOW[1]
    if inside_b1:
        return "STRONG_PASS"
    if overlaps_b1:
        return "BOUNDARY_REGION"
    if inside_k:
        return "KILL"
    if not overlaps_k:
        return "OUTSIDE_BAND"
    return "UNCLASSIFIED_BY_RULE"


def kill_condition_9_fires(bucket: str) -> bool:
    """Gate 5 / Kill Condition 9 flip: fires iff the bucket is KILL.

    Consequence, as sourced (GHP_BOUNDARY_PROGRAM_v2.md §6.1): "hitting it
    fires Kill Condition 9 ... Module C loses its physics spine and the
    framework retains only its architectural (Module R) and engineering
    (Module A) content." The demotion text lives in master §5.10A.4 and is
    quoted in the module docstring; this function only reports the flip.
    """
    return bucket == "KILL"


def m1_quotient_confirmation_flag(nu: float, tolerance: float) -> bool:
    """Advisory ν-space flag for the Addendum M.1 quotient-confirmation
    branch ("third bucket" per GHP_CORE_v3.md Appendix B).

    M.1 is written in ν space ("ν ≈ 0.7 may count as quotient-confirmation
    rather than failure") and supplies NO numeric tolerance for "lands
    stably near". The tolerance is MISSING-INPUT and must be given
    explicitly — there is no default. The flag is advisory bookkeeping only:
    per M.1, it means "Module C may be weakened, not killed", and per
    boundary v2 §6.3 it "must be honestly labeled as a demotion of the
    strong φ-critical claim". It never upgrades any β bucket.
    """
    if tolerance is None or not tolerance > 0:
        raise ValueError(
            "M.1 gives no numeric tolerance for 'stably near 0.7' "
            "(MISSING-INPUT); an explicit positive tolerance must be "
            "preregistered and passed in."
        )
    return abs(nu - 0.7) <= tolerance


@dataclass(frozen=True)
class Verdict:
    nu: float
    beta: float
    assignment_name: str
    assignment_provenance: str
    point_bucket: str
    ci_bucket: Optional[str]
    kill_condition_9: bool

    def __str__(self) -> str:
        ci_txt = self.ci_bucket if self.ci_bucket is not None else "(no CI supplied)"
        return (
            f"nu={self.nu:.6g} -> beta={self.beta:.6g} "
            f"[assignment: {self.assignment_name}; {self.assignment_provenance}] "
            f"point-rule={self.point_bucket} CI-rule={ci_txt} "
            f"KillCondition9={'FIRES' if self.kill_condition_9 else 'does not fire'}"
        )


def nu_to_beta_verdict(
    nu: float,
    assignment: ChannelExponentAssignment,
    ci: Optional[Tuple[float, float]] = None,
) -> Verdict:
    """Convert a measured collapse exponent ν into a β verdict.

    `assignment` is the injected port and is REQUIRED. Passing None (or
    anything that is not a ChannelExponentAssignment) raises
    MissingAssignmentError: the physics choice may never be silent.

    If `ci` is given it must already be the 95% CI of β under the SAME
    assignment (this module does not propagate ν-space error bars — doing so
    would itself be a physics choice belonging to the OP 179 protocol).
    """
    if not isinstance(assignment, ChannelExponentAssignment):
        raise MissingAssignmentError(
            "nu->beta channel-exponent assignment not injected. Per AE.8/AE.9 "
            "the assignment is NON-UNIQUE (candidates near 1.236 / 1.328 / "
            "1.412 / 1.764) and per OP 179 no operational definition exists "
            "in the sources; it must be preregistered and passed explicitly. "
            "No default will ever be applied."
        )
    beta = float(assignment.convert(nu))
    point_bucket = beta_bucket_point(beta)
    ci_bucket = beta_bucket_ci(ci[0], ci[1]) if ci is not None else None
    # Precedence (disclosed bookkeeping decision, verifier-mandated 2026-08-01):
    # when a CI is supplied, the CI rule GOVERNS the flip. Basis: master
    # 5.10A.3 (a boundary-region CI "Does NOT count as pass or kill") and
    # 5.10A.4 (demotion requires beta ~ 2 "within stable error bars" — a CI
    # spanning the window without sitting inside it is precisely not stable
    # error bars). Without a CI, the point rule is the only pinned rule and
    # governs alone. This precedence is surfaced for owner sign-off in
    # SYK_CORRIDOR_PREREG_v1.md section 4.
    if ci_bucket is not None:
        fires = ci_bucket == "KILL"
    else:
        fires = kill_condition_9_fires(point_bucket)
    return Verdict(
        nu=nu,
        beta=beta,
        assignment_name=assignment.name,
        assignment_provenance=assignment.provenance,
        point_bucket=point_bucket,
        ci_bucket=ci_bucket,
        kill_condition_9=fires,
    )


# ---------------------------------------------------------------------------
# Self-test: synthetic values covering every bucket in both rules.
# ---------------------------------------------------------------------------

def _selftest() -> None:
    # A TEST-ONLY identity assignment, injected explicitly so the port
    # machinery itself is exercised. This is NOT a physics choice and is not
    # eligible for any real run: its provenance says so.
    ident = ChannelExponentAssignment(
        name="TEST-ONLY-identity",
        convert=lambda nu: nu,
        provenance="self-test only; forbidden for real runs (OP 179 unresolved)",
    )

    # Port refusal: conversion without an injected assignment must raise.
    try:
        nu_to_beta_verdict(1.0, None)  # type: ignore[arg-type]
        raise AssertionError("port refusal failed: None accepted")
    except MissingAssignmentError:
        print("PORT REFUSAL           : OK (no assignment -> MissingAssignmentError, no default)")

    # Point-rule coverage: every §5.10A.6.3 bucket, including the written-
    # as-is strong-pass lower tail below the B1 floor, and both boundary
    # neighborhoods.
    point_cases = [
        (0.618034, "STRONG_PASS"),   # 1/φ, inside [0.95/φ, 1.05/φ]
        (0.60,     "STRONG_PASS"),   # in strong-pass lower neighborhood (as written)
        (1.618034, "STRONG_PASS"),   # φ, inside [0.95φ, 1.05φ]
        (1.00,     "IN_BAND"),       # in B1, outside strong-pass neighborhoods
        (0.70,     "IN_BAND"),       # the M.1 tricritical/quotient lane value
        (0.39,     "BOUNDARY"),      # in [0.95/φ², 1.05/φ²] ≈ [0.3629, 0.4011]
        (2.60,     "BOUNDARY"),      # in [0.95φ², 1.05φ²] ≈ [2.4870, 2.7490]
        (1.95,     "KILL"),          # kill window floor
        (2.00,     "KILL"),          # Dyson β_D = 2 generic-spectrum target
        (2.05,     "KILL"),          # kill window ceiling
        (1.80,     "OUTSIDE"),       # between strong-pass ceiling and K
        (0.20,     "OUTSIDE"),       # below every interval
        (3.50,     "OUTSIDE"),       # above every interval
    ]
    for nu, expected in point_cases:
        v = nu_to_beta_verdict(nu, ident)
        assert v.point_bucket == expected, (nu, v.point_bucket, expected)
        expected_fire = expected == "KILL"
        assert v.kill_condition_9 == expected_fire, (nu, v.kill_condition_9)
        print(f"POINT {nu:7.4f} -> {v.point_bucket:12s} "
              f"KC9 {'FIRES' if v.kill_condition_9 else 'no   '}  : OK")

    # CI-rule coverage: every §5.10A.3 Option-B branch, plus the literal
    # unclassified case.
    ci_cases = [
        ((0.80, 1.20), "STRONG_PASS"),          # entirely inside B1
        ((1.50, 1.70), "BOUNDARY_REGION"),      # overlaps B1, not contained
        ((1.96, 2.04), "KILL"),                 # entirely inside K
        ((2.50, 2.60), "OUTSIDE_BAND"),         # outside B1 and outside K
        ((1.90, 2.10), "UNCLASSIFIED_BY_RULE"), # straddles K, matches no written branch
    ]
    for (lo, hi), expected in ci_cases:
        got = beta_bucket_ci(lo, hi)
        assert got == expected, ((lo, hi), got, expected)
        print(f"CI    [{lo:.2f}, {hi:.2f}] -> {got:20s}: OK")

    # M.1 flag: tolerance is MISSING-INPUT; must refuse without it, and work
    # with an explicit one.
    try:
        m1_quotient_confirmation_flag(0.70, None)  # type: ignore[arg-type]
        raise AssertionError("M.1 tolerance refusal failed")
    except ValueError:
        print("M.1 TOLERANCE REFUSAL  : OK (no tolerance -> ValueError, no default)")
    assert m1_quotient_confirmation_flag(0.70, 0.02) is True
    assert m1_quotient_confirmation_flag(0.618, 0.02) is False
    print("M.1 FLAG (explicit tol): OK (0.70 in, 0.618 out at tol=0.02)")

    # Candidate table sanity: the four AE.9 candidate values are present and
    # the magnitude-of-eigenvalue value equals 1/φ³ + 1 to the source's
    # quoted precision.
    assert set(AE9_CANDIDATE_BETA_TABLE.values()) == {1.236, 1.328, 1.412, 1.764}
    assert abs((1.0 / PHI ** 3 + 1.0) - AE9_CANDIDATE_BETA_TABLE["magnitude-of-eigenvalue"]) < 5e-4
    print("AE.9 CANDIDATE TABLE   : OK (1.236 = 1/φ³ + 1 to quoted precision; "
          "1.328 / 1.412 / 1.764 present)")

    print("\nSELF-TEST: ALL CHECKS PASSED "
          "(bookkeeping only; no physics choice was made — the nu->beta "
          "assignment used above is TEST-ONLY identity and is forbidden for "
          "real runs until OP 179 is resolved and an assignment is "
          "preregistered).")


if __name__ == "__main__":
    _selftest()
