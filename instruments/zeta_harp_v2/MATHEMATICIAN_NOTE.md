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

## 3. Representation (filled at Gates 3-6; artifact: public/observatory.html)

- 3D Truth geometry: h_n(u) = (a_n cos phi_n, a_n sin phi_n, scale_t (u - t0)) with
  radius scale 6.0 scene-units per unit amplitude and scale_t = 80 / half-window(t),
  half-window(t) = clamp(48 / ln N(t), 4, 30) height units; both constants live in the
  fence panel [i]. Phases along the window use the local expansion
  phi0 + omega u + (1/2)theta'' u^2 + (1/6)theta''' u^3 with phi0 computed in float64 at
  the window center (worst truncation ~3e-2 rad at t~100 where the exact evaluation path
  is used anyway; <1e-6 rad above 1e4).
- Color: signed real contribution — blue positive, purple negative; brightness maps
  a_n; gold = the resultant (its 2D magnitude is never labeled |Z|; the imaginary
  part is labeled AUXILIARY wherever it appears).
- The ribbon/flower/microscope M(t) uses exact per-sample evaluation when
  N(window end) <= 512, else the phase recurrence above (windows there never cross a
  cutoff since spacing 2pi(2N+1) >> window width).
- Fixture overlays (Z_ref, R_ref) are drawn as GRID DOTS with a faint connecting line:
  at W3/W4 heights the 0.5 grid step is comparable to the local zero spacing, so the
  connecting line is a visual aid only and never used to locate crossings. The opening
  sequence freezes at a fixture GRID POINT adjacent to a sign change of Z_ref
  (bracket certain from the high-precision endpoint values) — no interpolation.
- Truth Audio: f_audio_n = v_t (theta'(t) - ln n)/2pi with one global v_t
  (slider-disclosed, default ~36 height/s, range 1..1000) and one global linear gain
  (slider x 0.045). Direct render: min(N, 512) sample-exact complex-phasor voices in an
  AudioWorklet; for N > 512 the remainder terms are band-summed into 8 log bands
  (energy-preserving amplitude sqrt(sum a_n^2), amplitude-weighted mean rate), always
  disclosed by the honesty line "N terms in the sum · D rendered sample-exact ·
  V individually voiced · B band-summed". Reverb / scale-quantize controls exist but
  flip the badge to "ARTISTIC SONIFICATION — NOT A PRIVILEGED MATHEMATICAL MAPPING".
  The cutoff-entry chime is a UI event cue (clamped up to 55 Hz), disclosed in the
  fence as not part of the sonification law.
- Sign changes of the computed main sum are labeled "computed crossing (finite
  approximation)" everywhere, including the flight shockwave events; the Zero
  Microscope uses only the 40-entry refined reference list and displays the offset
  between our computed crossing and the reference ordinate.

## 4. Validation summary (recorded 2026-08-01, harness: reference/check_inline_math.mjs)

Inline float64 implementation (extracted verbatim from the shipped artifact) vs the
frozen 80-digit Gate-2 fixtures, max-abs over every grid point:

| window | pts | max err theta (rad) | max err theta' | max err M | fixture max abs R_ref | fixture RMS R_ref |
|---|---|---|---|---|---|---|
| W1 [100,160]   | 241 | 5.7e-14 | 2.2e-15 | 2.2e-13 | 0.4651  | 0.2802  |
| W2 ~1e4        | 141 | 1.1e-11 | 8.9e-16 | 5.6e-11 | 0.1461  | 0.127   |
| W3 ~1e6        | 141 | 9.3e-10 | 1.8e-15 | 9.5e-9  | 0.04102 | 0.04028 |
| W4 ~1e8        | 41  | 1.2e-7  | 1.8e-15 | 1.7e-6  | 0.006225| 0.006224|

- W1 theta beats the 1e-6 plan target by ~8 orders; W3/W4 errors are float64 rounding
  of theta itself (eps * theta(t)), the documented honest edge of the instrument.
- Embedded 13-digit fixture excerpts vs full fixtures: max dev < 5e-12 (all windows).
- Cutoff-entry consistency: N(t) increments by exactly 1 at t_n = 2 pi n^2 for the
  boundaries inside W1 (n = 4, 5), including the equality edge (PASS).
- Audio-law derivative check: max |central-diff phi_n - (theta' - ln n)| = 8.3e-10
  rad/unit-t over W1+W2 grids at n = 1, N/2, N (tolerance 1e-8; PASS).
- Crossing offsets vs refined reference zeros (finite-sum error, reported not gated):
  #1 gamma=14.13: +0.38; #2565 gamma=3097.3: -0.042; #25642 gamma=22436.6: -4.7e-3;
  #51283 gamma=41351.8: no main-sum sign change within +-1.5; #76923 gamma=59286.1:
  +5.1e-3; #100000 gamma=74920.8: +1.1. These offsets are displayed in the Zero
  Microscope as the disclosed finite-sum error; they shrink as R_ref shrinks with t
  but individual zeros can sit far from the nearest main-sum crossing.
- The artifact recomputes max |M_inline - M_fixture| per window at load and displays
  it in the fence panel's validation table.

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
