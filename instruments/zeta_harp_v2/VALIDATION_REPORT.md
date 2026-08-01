# VALIDATION_REPORT.md — Zeta Harp v2 / Riemann-Siegel Phase Observatory

Standing label: KNOWN MATHEMATICS / INTERACTIVE SCIENTIFIC AND ARTISTIC INSTRUMENT /
NOT EVIDENCE FOR RH OR GHP.

Independent adversarial verification run. Every number below was produced by the
verifier's own execution of the committed scripts on the committed artifact — not
copied from MATHEMATICIAN_NOTE.md. (The recorded summary there was then compared
against these runs and found to agree.)

## Environment

- Date: 2026-08-01
- Verified commit: d8d8642e4f8dde6c04bf9692be259df9201ad5f4 (branch
  instrument/zeta-harp-phase-observatory-v2, tip at time of verification; this
  report is committed on top)
- OS: macOS 26.1 (Darwin 25.1.0), arm64
- Python 3.9.6, mpmath 1.3.0 (mp.dps = 50 in validators; fixtures generated at dps = 80)
- Node.js v22.23.0

## Fixture integrity (SHA-256, recomputed and compared to reference/fixtures/MANIFEST.txt)

All five hashes match the committed manifest exactly:

```
216db9e0ca4b6093aace4cd400d8293f5a00f56343d2a773ace63567ac220dae  window_W1.json
fd71b9efebaafd61fa8d2311c2e41c75151274346dfff3c217e39b7a9a60d344  window_W2.json
0c24c6ad5fa0e058b87937f473c5c05f1093ce76bb4c8dd355a82a63f2ea8072  window_W3.json
63f5cd214df138e7fc9fa0030b5ea38115203157fac372903d2279dc3cfd2979  window_W4.json
15ec43ba036119004f87aefda90fe77ac4334eef7b25d279d28525e728eacfce  zeros_reference.json
```

Shipped artifact at verification: public/observatory.html
SHA-256 267a57b5d6fc3ed449e1e256c8007ca0701dabeb2b755bdfae87b81ca6b67910 (122.7 KiB).
Running `node src/build.mjs` regenerated it byte-identically (same hash; git tree
stayed clean), so the shipped page is exactly what the src/ parts produce.

## Gate 2 — validate_theta.py (exit 0, PASS)

Max / RMS error of the float64 working asymptotic against dps-80 exact theta
(VALIDATION_PLAN.md metric 3), per window:

| window | float64-total max (rad) | RMS (rad) | in ulp of theta | series-trunc max (rad) | theta' max (rad/unit-t) | target | verdict |
|---|---|---|---|---|---|---|---|
| W1 [100,160] | 6.184e-14 | 2.510e-14 | 3.81 | 3.845e-14 | 1.933e-15 | abs < 1e-6 | PASS |
| W2 ~1e4 | 7.124e-12 | 2.737e-12 | 1.96 | 3.864e-24 | 4.581e-16 | abs < 1e-9 | PASS |
| W3 ~1e6 | 1.252e-09 | 4.423e-10 | 1.34 | 8.763e-34 | 1.322e-15 | < 4 ulp | PASS |
| W4 ~1e8 | 1.432e-07 | 7.034e-08 | 1.20 | 4.899e-32 | 1.414e-15 | < 4 ulp | PASS |

W3/W4 errors are the float64 rounding of theta itself (theta ~ 8e8 rad at t = 1e8);
1.2 ulp at W4 documents the float64 phase-accuracy frontier where the instrument's
honest range ends.

## Gate 2 — validate_z.py (exit 0, PASS)

| window | recon max (M_hp+R_ref)-Z_ref | impl max M_f64-M_hp | max \|M_f64-Z_ref\| | max \|R_ref\| | RMS R_ref | N mismatches | verdict |
|---|---|---|---|---|---|---|---|
| W1 | 9.000e-40 | 2.004e-13 | 4.651e-01 | 4.651e-01 | 2.802e-01 | 0 | PASS |
| W2 | 8.300e-39 | 3.165e-11 | 1.461e-01 | 1.461e-01 | 1.270e-01 | 0 | PASS |
| W3 | 6.410e-39 | 6.089e-09 | 4.102e-02 | 4.102e-02 | 4.028e-02 | 0 | PASS |
| W4 | 5.583e-39 | 2.056e-06 | 6.225e-03 | 6.225e-03 | 6.224e-03 | 0 | PASS |

Reconstruction sits at fixture numerical noise (< 1e-30 gate). The main-sum-vs-Z
column equals |R_ref| by construction and is the disclosed un-drawn remainder: the
main sum alone is NOT Z, and its sign changes are computed crossings only.

## Gates 3-6 — check_inline_math.mjs against the shipped artifact (exit 0, ALL CHECKS PASS)

`node --check` on both inline script blocks extracted from public/observatory.html:
OK (zh-math 4212 bytes, zh-app 66763 bytes; also re-extracted and re-checked
independently of the harness with identical result).

Inline float64 core vs full-precision fixtures at every grid point:

| window | pts | max \|dTheta\| | max \|dTheta'\| | max \|dM\| | max \|embed-full\| | N mismatch | verdict |
|---|---|---|---|---|---|---|---|
| W1 | 241 | 5.684e-14 | 2.220e-15 | 2.203e-13 | 4.980e-13 | 0 | PASS |
| W2 | 141 | 1.091e-11 | 8.882e-16 | 5.569e-11 | 4.672e-12 | 0 | PASS |
| W3 | 141 | 9.313e-10 | 1.776e-15 | 9.502e-09 | 3.830e-12 | 0 | PASS |
| W4 | 41 | 1.192e-07 | 1.776e-15 | 1.697e-06 | 4.967e-12 | 0 | PASS |

- Cutoff-entry consistency: N(t) increments by exactly 1 at t_n = 2*pi*n^2 (a
  height, never a frequency) for n = 4 (t_4 = 100.530964915) and n = 5
  (t_5 = 157.079632679), including the equality edge. PASS.
- Audio-law derivative check (W1+W2 grids, n = 1, N/2, N): worst
  |central-diff phi_n - (theta' - ln n)| = 8.304e-10 rad/unit-t (tol 1e-8). PASS.
  This pins "what you hear is the derivative of the phase you see" to a test.
- Crossing offsets vs refined reference zeros (finite-sum error; REPORTED, NOT
  GATED, per VALIDATION_PLAN metric 4): #1 gamma=14.135: +3.83e-1; #2565
  gamma=3097.34: -4.19e-2; #25642 gamma=22436.6: -4.68e-3; #51283 gamma=41351.8:
  no main-sum sign change within +-1.5; #76923 gamma=59286.1: +5.09e-3; #100000
  gamma=74920.8: +1.11. These are the disclosed distance between a computed
  crossing of the finite main sum and a published-table ordinate; individual
  zeros can sit far from the nearest main-sum crossing (or lack one nearby).
  Nothing here certifies a zero.

## Zero-displacement spot checks (verifier's own mpmath runs, dps = 40)

For entries #1, #2565, #51283, #97436, #100000 of the embedded 40-entry refined
reference list, |Z(gamma_refined)| evaluated independently via mp.siegelz at the
18-digit truncation of the stored ordinate came out between 2.2e-34 and 8.3e-30 —
consistent with the stored higher-precision residuals (~1e-51..1e-57 at full stored
digits) and limited only by the truncation fed in. Stored refine offsets against the
Odlyzko-derived table are all ~1e-10 to 1e-12. All spot checks < 1e-8: PASS. These
ordinates remain "Odlyzko-derived, mpmath-refined, NOT certified", as labeled.

## Language and claim-boundary audit (grep over all v2 docs, HTML, JS, Python)

- "measured amplitude": ABSENT. Amplitudes are consistently "computed spectral".
- "certified zero": appears only inside negative statements ("never certified
  zeros", "not a certified zero", "NOT certified").
- "proves RH" / "supports RH": ABSENT outside CLAIM_BOUNDARY.md's not-list.
- "first ever" / "first in history" / "historic": ABSENT outside the not-list and
  PRIOR_ART.md's quotation of the directive.
- cube / Trinity / 54-observers / torus / holography / phi-as-claim / GHP: ABSENT
  as claims. "cube" occurs only in the file path experiments/zeta_cube_null/zeros1.txt
  (the zero table's location); every phi in the build is the phase variable
  phi_n(t) = theta(t) - t ln n; "GHP" occurs only inside the negative standing
  label; no golden-ratio or 1.618 content anywhere.
- 2*pi*n^2 called a frequency: NO occurrence. Every mention labels it the
  CUTOFF-ENTRY height, several explicitly "a height, never a frequency".

## Required artifact elements (confirmed present in public/observatory.html)

- Standing label (page top, opening sequence, fence panel, source comment):
  "KNOWN MATHEMATICS / INTERACTIVE SCIENTIFIC AND ARTISTIC INSTRUMENT / NOT
  EVIDENCE FOR RH OR GHP".
- Phasor caveat (flower panel + fence): imaginary part is an AUXILIARY
  visualization coordinate; only the real part equals M(t); the resultant's
  length "is not |Z| and is never labeled |Z|".
- Ordering caveat (flower panel): "Polygon chained in n-order: the partial-sum
  path depends on that ordering; only the endpoint (the resultant) is
  order-independent."
- Audio honesty: gesture-gated start ("off — audio starts only on your gesture");
  disclosed law f_audio_n = v_t (theta'(t) - ln n)/2pi with one global v_t and
  gain; live honesty line "N terms in the sum · D rendered sample-exact · V
  individually voiced · B band-summed" (setHonesty); reverb/quantize flip the
  badge to "ARTISTIC SONIFICATION — NOT A PRIVILEGED MATHEMATICAL MAPPING".
- Both badges: truthBadge ("TRUTH MODE — no per-string tuning, no remapping")
  and valBadge ("validated: W1-W4 fixtures embedded").
- Fence panel [i]: standing label, full formula set, labeling laws in force,
  remainder table per window, disclosed rendering/audio constants, load-time
  validation table (max |M_inline - M_fixture| per window), and the closing
  Riemann fence: "Nothing in this instrument is evidence for or against the
  Riemann Hypothesis."

## Scope check

`git diff origin/main --name-status` shows ADDITIONS ONLY, all 27 paths under
instruments/zeta_harp_v2/. The v1 artifact at experiments/zeta_harp/ (README.md,
zeta_harp.html) is untouched, per CLAIM_BOUNDARY.md's scope clause.

## Known limitations (restated from the verified evidence)

1. Float64 phase frontier: near t = 1e8 the absolute theta error is ~1.4e-7 rad
   (~1.2 ulp of theta); no float64 implementation can do better, and the build
   labels this as the end of its honest range.
2. The rendered/sonified object is the main sum M(t) only. The remainder R_ref
   (max ~0.465 in W1, shrinking to ~6.2e-3 in W4) is drawn only as reference
   overlays; sign changes of M(t) are computed crossings, not zeros — near
   gamma_1 the crossing sits 0.38 away, near #100000 1.1 away, and one sampled
   reference zero (#51283) has no main-sum sign change within +-1.5.
3. Zero comparisons exist only below t ~ 75000 (table range); W3/W4 zero
   locations are unchecked against any table and the UI says so.
4. The embedded fixture excerpts are 13-significant-digit compactions of the
   frozen fixtures (max deviation < 5e-12, verified above); full-precision
   originals live in reference/fixtures/ under the SHA-256 manifest.
5. For N > 512 audio strings, remainder terms are band-summed into 8 log bands
   (energy-preserving amplitude, amplitude-weighted mean rate) — disclosed live
   by the honesty line; the cutoff-entry chime is a UI cue, not part of the
   sonification law.

## Verdict

PASS. All committed validators pass under independent execution, the shipped
artifact is byte-reproducible from source and carries every required honesty
element, and no blocked claim language appears anywhere in the v2 tree.
