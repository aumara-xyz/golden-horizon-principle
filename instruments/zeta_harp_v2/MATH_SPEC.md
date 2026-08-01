# MATH_SPEC.md — Canonical function set (Zeta Harp v2)

Status: CANONICAL. Documentation precedes implementation (Gate 1 law). Every renderer,
sonifier, and validation script in this build implements exactly the functions below, with
exactly these names. Any deviation is a bug against this spec, not a reinterpretation of it.

All mathematics here is standard and known. Formula source: DLMF chapter 25.10
(Riemann-Siegel formula and Z-function). See PRIOR_ART.md. Nothing in this file is claimed
as new mathematics.

Notation: t is the real height on the critical line s = 1/2 + it. All logs are natural.

---

## 1. Hardy Z-function

    Z(t) = exp(i * theta(t)) * zeta(1/2 + i t)

Z(t) is real for real t. Its sign changes locate the zeros of zeta on the critical line.
Reference values Z_ref(t) are computed with high-precision zeta (mpmath), not with the
main sum.

## 2. Riemann-Siegel theta

Exact definition:

    theta(t) = Im log Gamma(1/4 + i t / 2) - (t/2) * ln(pi)

Working asymptotic (the implementation form for this build):

    theta(t) ~ (t/2) * ln(t / (2*pi)) - t/2 - pi/8 + 1/(48*t) + 7/(5760 * t^3)

Derivative (differentiate the working asymptotic term by term):

    theta'(t) ~ (1/2) * ln(t / (2*pi)) - 1/(48 * t^2) - 7/(1920 * t^4)

The asymptotic is the working form; its accuracy against the exact Gamma definition is a
required validation item (VALIDATION_PLAN.md), with the fixture windows chosen so the
asymptotic error is negligible at all displayed heights.

## 3. Main-sum term count (cutoff)

    N(t) = floor( sqrt( t / (2*pi) ) )

## 4. Term amplitude, phase, and contribution

For n = 1 .. N(t):

    a_n      = 2 / sqrt(n)                (computed spectral amplitude — never "measured")
    phi_n(t) = theta(t) - t * ln(n)
    c_n(t)   = a_n * cos( phi_n(t) )

## 5. Main sum and reference remainder

    M(t)     = sum_{n=1}^{N(t)} c_n(t)
    R_ref(t) = Z_ref(t) - M(t)

R_ref is defined by subtraction from the high-precision reference, not by evaluating the
Riemann-Siegel correction series. It is the honest residual of the main sum. Sign changes
of M(t) are "computed reference crossings", never certified zeros (CLAIM_BOUNDARY.md).

## 6. Instantaneous term frequency

    omega_n(t) = theta'(t) - ln(n)        (angular, radians per unit t)
    f_n(t)     = omega_n(t) / (2*pi)      (cycles per unit t)

f_n is the local rotation rate of phi_n in t. It is a rate with respect to the height
parameter t, not an audio frequency; audio frequencies exist only through the Truth Audio
law in section 9.

## 7. Cutoff entry height

    t_n = 2 * pi * n^2

t_n is the height at which N(t) first reaches n, i.e. the CUTOFF-ENTRY height of term n.
It is never a frequency. ("String birth" is permitted as a name for this entry event in
installation-mode copy only.)

## 8. Phasor and 3D phase trajectory

Per-term phasor:

    p_n(t) = a_n * exp( i * phi_n(t) )

REQUIRED CAVEAT (binding, appears wherever the phasor sum is drawn or described):
the real part of the phasor sum equals the main sum,

    Re( sum_{n=1}^{N(t)} p_n(t) ) = M(t),

while the imaginary part is an AUXILIARY coordinate introduced for visualization. The
magnitude of the phasor sum is NOT |Z(t)| and is never labeled |Z|.

Default Truth Mode geometry — the 3D phase trajectory of term n over a height window
centered at t0, parameterized by u:

    h_n(u) = ( a_n * cos(phi_n(u)),  a_n * sin(phi_n(u)),  scale_t * (u - t0) )

scale_t is a disclosed rendering constant (units: scene length per unit t). The first two
coordinates are the phasor p_n; the second coordinate inherits the auxiliary status of the
imaginary part.

## 9. Truth Audio law

Playback maps audio time tau (seconds) to height linearly:

    t(tau) = t0 + v_t * tau

with ONE global, disclosed time-compression rate v_t (units: height per second). The audio
frequency of string n at playback time tau is the chain-rule image of phi_n:

    f_audio_n(tau) = v_t * ( theta'( t(tau) ) - ln(n) ) / (2*pi)      [Hz]

with ONE disclosed global gain. In Truth Mode there is no per-string tuning, no scale
quantization, no detuning, and no frequency remapping of any kind: what is heard is the
phase law of section 4 compressed in time by the single disclosed constant v_t. Any
departure from this law belongs to a non-Truth mode and must be labeled as such.

---

## Implementation notes (binding on Gate 2+)

- Z_ref via mpmath `zeta` at sufficient precision for the fixture window; theta exact via
  mpmath `loggamma` where the validation compares asymptotic vs exact.
- All quantities above are pure functions of t (and n); no hidden state, no fitted
  parameters anywhere in Truth Mode.
- Displayed numeric labels use the vocabulary of CLAIM_BOUNDARY.md: "computed spectral"
  amplitudes, "computed reference crossings", "cutoff-entry height".
