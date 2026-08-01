# PRODUCT_SPEC.md — Zeta Harp v2

Standing label everywhere: KNOWN MATHEMATICS / INTERACTIVE SCIENTIFIC AND ARTISTIC
INSTRUMENT / NOT EVIDENCE FOR RH OR GHP.

## Dual identity

One artifact, two presentations of the SAME mathematics (MATH_SPEC.md is the single
source of truth for both):

- **"Riemann-Siegel Phase Observatory"** — scientific default. Sober labels, axes, units,
  the required caveats inline, validation status visible. This is the identity the build
  opens in.
- **"Zeta Harp // Resonance Temple"** — installation mode. Evocative copy and staging are
  allowed, but only over the identical Truth Mode computation; "string birth" may name the
  cutoff-entry event here and nowhere else. The claim boundary and standing label still
  apply verbatim in this mode.

Mode is a presentation toggle, never a computation toggle.

## Rooms in scope tonight

1. **Phase Cathedral** — the default Truth Mode geometry: 3D phase trajectories h_n(u)
   (MATH_SPEC section 8) for n = 1..N(t) over a height window; camera flight along the
   height axis. Auxiliary-coordinate caveat rendered in-room.
2. **Phasor Flower** — the 2D phasor sum at a chosen t: chained p_n vectors whose real
   axis resultant is M(t). The imaginary axis is labeled auxiliary; the resultant's length
   is never labeled |Z|.
3. **Zero-Crossing Microscope** — zoom on a sign change of M(t): the crossing location,
   the nearest table zero (windows below t ~ 75000 only), and the offset between them.
   Label: "computed reference crossing", never certified zero.
4. **Truth Audio** — the sonification of MATH_SPEC section 9: one disclosed v_t, one
   disclosed gain, per-string frequencies v_t * (theta' - ln n)/(2*pi). No tuning, no
   quantization in Truth Mode. The disclosed constants are displayed while sound plays.
5. **Opening sequence** — a short guided pass that states the standing label, shows the
   claim boundary, introduces theta, phi_n, M, and the cutoff-entry heights, then hands
   over control. The opening is documentation-first: it teaches what the instrument is NOT
   before it plays.

## Deferred to roadmap (explicitly NOT tonight)

- Term Influence Lab full ablations (per-term mute/solo studies with error accounting)
- Approximation Observatory slope study (R_ref behavior across windows)
- Turing Gate (crossing-count accounting room)
- Prime Mirror
- X-Ray room (in the sense of the Arias-de-Reyna style curves; see PRIOR_ART.md)
- GUE room (spacing statistics)
- MIDI / gamepad input
- WebGPU renderer (tonight's build targets WebGL2 / Canvas paths only)

Deferred means deferred: no stub UI for these rooms ships tonight.

## Build laws inherited from Gate 0

- Files live only under `instruments/zeta_harp_v2/`; `experiments/zeta_harp/` (v1) is
  frozen.
- Documentation first: MATH_SPEC.md is canonical before any visual exists; rooms implement
  the spec, the spec is never edited to match a room.
- Validation gates rendering (VALIDATION_PLAN.md gate rule).
- One commit per gate, no push from the build lane.
