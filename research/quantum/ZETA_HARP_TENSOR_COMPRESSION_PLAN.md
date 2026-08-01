# ZETA-HARP-TENSOR-COMPRESS-v1 — plan

Adopted 2026-08-01 per `docs/ZETA_HARP_QUANTUM_PORTAL_ADDENDUM.md` (RQ5). The v0
implementation is `experiments/zeta_harp_quantum/tensor_compression_benchmark.py`;
its outputs are numbers only, with no advantage language anywhere in the lane.

## The research question

**ZETA-HARP-TENSOR-COMPRESS-v1.** Does the Harp amplitude vector at fixed t — the 26
complex amplitudes n^(-1/4) e^{i(theta(t) - t ln n)}/sqrt(A_26), padded into a chosen
qudit register — compress under tensor-train (sequential-SVD) decomposition differently
from matched control ensembles, at a stated term ordering and a stated tolerance, and
how does any difference scale with N as t grows?

## The 10 comparison arms

| # | arm | layout | content |
|---|-----|--------|---------|
| 1 | zeta_qutrit_lex | 3x3x3 (27, anchor reserved) | zeta phases, lexicographic order |
| 2 | zeta_qubit | 2x2x2x2x2 (32, padded) | zeta phases, same order |
| 3 | random_phase_qutrit | 3x3x3 | same magnitudes, iid uniform phases (seeded) |
| 4 | permuted_phase_qutrit | 3x3x3 | zeta phases randomly permuted across terms |
| 5 | amplitude_sorted_qutrit | 3x3x3 | terms reordered by descending magnitude (identity here, since n^(-1/4) is already descending; retained as the null it is) |
| 6 | phase_sorted_qutrit | 3x3x3 | terms reordered by increasing phase |
| 7 | mismatched_reshape_qutrit | 3x3x3 | zeta amplitudes scattered by a fixed seeded wrong assignment before reshape |
| 8 | random_phase_qubit | 2^5 | arm 3 in the qubit layout |
| 9 | permuted_phase_qubit | 2^5 | arm 4 in the qubit layout |
| 10 | zeta_qutrit_balanced | 3x3x3 | zeta phases, balanced-ternary term-to-state order |

Plus one scale probe (not an arm): t near 1e6, N = 398, padded into 3^6 = 729 and
reshaped as a six-qutrit train, so the N-scaling axis exists.

## Metrics

- relative L2 reconstruction error vs bond-dimension cap (full curve, every arm);
- |Delta M(t)| of the reconstructed sum vs bond-dimension cap (each arm scored against
  its own matched reference sum);
- parameter count of the tensor-train cores vs bond-dimension cap;
- position of the zeta arm within the control ensemble spread (percentile, in the null
  controls experiment);
- singular-value structure implicit in the error curves (no thresholded verdicts).

## The four confound distinctions (binding, stated with every result)

Any apparent zeta-vs-control difference must be decomposed against all four before it
may even be described as a candidate feature:

1. **Arithmetic structure vs ordering.** The phases theta(t) - t ln n carry arithmetic
   structure, but the register also imposes an ORDER on terms. Arms 4, 5, 6, and 10
   hold the amplitude multiset fixed while changing only order; whatever they reproduce
   is ordering, not arithmetic.
2. **Ordering vs layout.** The term-to-state assignment and the reshape are chosen.
   Arms 7 and 10 move the layout with the phase content untouched; whatever moves with
   them is layout, not content.
3. **Low-N smallness.** At N = 26 the register is 3x3x3 with maximal bond dimension 3;
   every curve is dominated by dimension counting, and nothing at N = 26 generalizes.
   The t = 1e6 (N = 398) probe exists to give the scaling axis — and is itself a single
   point on it.
4. **Loose tolerance.** "Compresses well" is meaningless without a stated tolerance.
   Full error-vs-bond curves are reported instead of thresholded verdicts, and every
   tolerance used is recorded in the output metadata.

## v0 status

v0 ran 2026-08-01: all 10 arms plus the scale probe, seeds and tolerances in
`outputs/tensor_compression_benchmark.json`, confound distinctions restated in the
output itself. Headline numbers (neutral): at N = 26 every qutrit arm reaches exact
reconstruction at bond cap 3 and every qubit arm at cap 4, as dimension counting
requires; at the scale probe (N = 398, 3^6) the zeta vector's relative L2 error is
0.95 / 0.89 / 0.78 / 0.56 / 0.32 / 0.07 at bond caps 1 / 2 / 3 / 6 / 9 / 14 and is
exact by cap 20. Interpretation is deferred to a preregistered v1 with control
ensembles at scale.
