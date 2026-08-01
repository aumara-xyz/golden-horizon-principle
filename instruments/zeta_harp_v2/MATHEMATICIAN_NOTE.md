# MATHEMATICIAN_NOTE.md — note for a reviewing mathematician (skeleton)

Standing label: KNOWN MATHEMATICS / INTERACTIVE SCIENTIFIC AND ARTISTIC INSTRUMENT /
NOT EVIDENCE FOR RH OR GHP.

Status: SKELETON. Sections marked [TO FILL] are completed at later gates; the structure
and the review questions are fixed now (Gate 1).

## 1. What it is

An interactive rendering and sonification of the Riemann-Siegel main sum for Hardy's
Z-function on the critical line: the terms a_n cos(phi_n(t)) with a_n = 2/sqrt(n),
phi_n(t) = theta(t) - t ln n, summed to N(t) = floor(sqrt(t/2pi)), drawn as phase
trajectories and played as time-compressed frequencies v_t (theta'(t) - ln n)/(2pi).
Full function set: MATH_SPEC.md. All formulas are standard (DLMF 25.10).

## 2. What it is not

- Not new mathematics; not a computation of new zeros; not a certification of any zero
  (sign changes of the main sum are labeled "computed reference crossings").
- Not evidence for or against the Riemann Hypothesis, and not connected to any speculative
  program (the binding not-list is CLAIM_BOUNDARY.md).
- Not a measurement: every amplitude and frequency is computed from the formulas above
  ("computed spectral", never "measured").
- The 2D/3D phasor pictures use the imaginary part of the phasor sum as an auxiliary
  visualization coordinate; the magnitude of that sum is not |Z| and is never labeled so.

## 3. Representation

[TO FILL at render gates: exact mapping from MATH_SPEC quantities to screen coordinates,
color, and audio parameters, including the disclosed constants scale_t, v_t, and gain, and
where each required caveat appears in the UI.]

## 4. Validation summary

[TO FILL from VALIDATION_PLAN.md results: per-window (W1 [100,160], W2 ~1e4, W3 ~1e6,
W4 ~1e8) reconstruction error, R_ref size, theta asymptotic error, crossing offsets
against the in-repo Odlyzko table (t < ~75000 only), cutoff-entry consistency, and the
audio-frequency derivative check. Windows without recorded results are labeled
unvalidated.]

## 5. Review questions

We ask a reviewing mathematician specifically:

1. Is the working theta asymptotic (through the 7/(5760 t^3) term) and its derivative
   adequate at the displayed heights, and is our stated error target for it the right one?
2. Is the treatment of the remainder honest — R_ref defined by subtraction from
   high-precision Z rather than by the Riemann-Siegel correction series — and is its size
   adequately disclosed relative to what is drawn?
3. Is the "auxiliary coordinate" framing of the phasor sum's imaginary part (and the
   refusal to label its magnitude |Z|) sufficient to prevent misreading, or is a stronger
   caveat needed?
4. Is the labeling "computed reference crossings" (with offsets against a published zero
   table, in-range windows only) the correct level of claim, and is any wording here still
   too strong?
5. Does the Truth Audio law — a single disclosed time compression v_t applied to
   theta'(t) - ln n, with no per-string tuning — faithfully present the phase derivative,
   and are there artifacts of time compression we should disclose?

[TO FILL: reviewer responses and resulting changes.]
