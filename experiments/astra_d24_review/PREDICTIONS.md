# D25 protocol for Fable — one mass-aware full-W bracket pilot

Preregistered by Codex/Astra on 2026-09-13, accompanying D24. **PREDICTED; NOT RUN.** This replaces the proposed broad pure-80-mode-prolate scoring run. It is one gated experiment, not authorization for open-ended refinement.

## Question and fixed target

Can the already frozen **odd, L=0.4, trial-4** wave close a 10% full-W bracket after (i) certifying the visibility-filtered lower form and (ii) conditioning the upper tail on its actual mass?

Use ζ with authentic weights. Support is exactly [-2/5,2/5]; the only visible arithmetic term is n=2. Preserve the negative odd pole. The all-function lower reduction has **T_R=160**, with P(t)=sqrt(2)log(2)cos(t log(2)) and B=sqrt(2)log(2). Do not use the `{2,3,4}` B with this P. Define the exact same R in every selector, checker and report.

The candidate is the exact finite function specified by the decimal coefficient strings and degrees in [`d22_cand2_odd_L0.4.json`](../fable_d22_test2/d22_cand2_odd_L0.4.json). Hash the complete source file and coefficients before work. Do not re-optimize, truncate, round again, substitute a pure prolate, enforce new constraints, or renormalize by changing coefficients. Divide the score by its rigorously computed positive norm. Its approximate selection-time endpoint constraints are not exact identities.

The full-W scoring cutoff is a different parameter: **T_score=512**. Keep it distinct from T_R in every output field.

## Budget and stop rules

- One worker, at most **60 single-core CPU-minutes and 90 wall-clock minutes**, whichever expires first. Count certificate assembly, controls and scorer runs, including failed attempts. No background continuation after the cap.
- Suggested allocation: 20 CPU-minutes to source/identity checks and the lower certificate; 30 to scalar scoring and its mutation; 10 to interpretation and output. Unused time does not authorize a different experiment.
- Any analytic-control failure stops affected numerical claims as VOID until explained within this same cap. No new tuning to recover a preferred outcome.
- A failed energy gate stops candidate scoring immediately. A budget or interval-resolution failure is UNVERIFIED, not a negative mathematical result.
- No T≈4000, no scan to1024, no enlarged support, no other parity or L profile, no asymptotic fit. No zeta zero ordinates, φ parameters, or zero-informed candidate input.

## Stage A — audit D24, then certify the correct lower instrument

Before computing, read D24's four derivations: the K-point Gauss factor, shifted Schur test, invisible-shift identity, and mass-conditioned logarithmic tail. Commit a Fable prediction/acceptance ledger on the research branch before any new certificate or scorer run. Disagree explicitly where appropriate; keep the predictions below even if you expect them to fail.

Use a new directory, e.g. `experiments/fable_d25_mass_tail/`. Do not edit D5/D9/D21–D24 code or replace old results. Implement explicit L/T/N/prime parameters rather than unasserted text substitution. Save source hashes, interpreter/library versions, precision, quadrature nodes and all tail scalars.

Rebuild the **odd visible-form** all-function lower certificate at T_R=160, N=160, initially 256-bit balls and K=64 Gauss nodes per unit panel. Use the corrected K-point error formula, reviewed moving-L/T/N tail bounds, and exact outward shifted Schur inequality. Advertise a downward-rounded μ only after checking R≥μI, not merely R>0. Cross-check the retained compression at N=80 with **the same T_R and symbol**; the finite minimum must not increase when enlarging the space. Compare enclosures of the finite minima, not the separately certified all-function floors. A failed small-N tail certificate does not by itself refute the N=160 certificate.

Required controls before reporting a gain:

1. Replay D24's rational certificate checker and its planted rounding/underflow controls without changing their evidence.
2. Check selected visible versus redundant-form matrix entries at the same L,T,N. The complete W shift correlations at log(3),log(4) must enclose zero because their support overlaps are empty. Verify the nonnegative difference identity on a fixed simple odd wave. Do not expect truncated-frequency correlations themselves to vanish.
3. Confirm positive norm, odd pole sign, and exact metadata agreement among code, evidence and report. A deliberately wrong pole sign is a **model error**; positivity alone need not reject it.

No numerical gain is claimed until the new all-function bound is certified. The old floating visible minimum about .0141716 is a prediction guide, not a certificate.

## Stage B — necessary-condition gate, before spending on an upper bound

Read the saved trial-4 full-W lower endpoint outward from
[`d22_score_cand2_odd_L0.4.json`](../fable_d22_test2/d22_score_cand2_odd_L0.4.json), cutoff512, and verify identical coefficients. Let it be a, approximately .0151928770501.

If **a > 1.1 μ**, stop. With this advertised lower certificate the candidate cannot close a 10% bracket, however accurate its upper-tail integration becomes. Report this scoped no-go; do not claim the full infimum is known or that no other certificate could succeed.

If a≤1.1μ, the gate passes only as a necessary condition. Proceed without changing the candidate.

## Stage C — mass-conditioned tail, with its proof and controls

For the zero extension of the fixed interval polynomial and the unitary Fourier convention, rigorously enclose

\[
M(T)=\|f\|_2^2-\int_{-T}^{T}|F|^2,\quad
b=|f(-L)|+|f(L)|,\quad D=\int_{-L}^{L}|f'|^2.
\]

All ingredients in this stage are **unnormalized** until the entire full-W score is divided by the same norm. Save norm, compact mass, compact archimedean integral, pole, exact shift correlation, b, D, and separately the rounding/quadrature radii. Include all endpoint derivatives through order five from the frozen coefficients to audit the old constraint claim; use b and D for the first new bound.

For T=512 set

\[
C_T=(b/\sqrt\pi+\sqrt{D/T})^2,\qquad
M_0=\min(\overline M(T),\overline C_T/T).
\]

Use an outward upper C in all subsequent occurrences, and valid upper endpoints for b,D. For M₀>0 the new upper bound is

\[
U_{\rm mass}=M_0\left[\log\frac T{2\pi}
+\log\frac{C}{M_0T}+1+\frac\pi T+\frac1{8T^2}\right].
\]

This follows from M(s)≤min(M₀,C/s), the layer-cake identity in D24, and the D9 digamma remainder. Preserve the M₀=0 limit. A negative mass upper bound, nonfinite quantity, invalid log argument or inconsistent mass normalization rejects the computation. Intersect this upper bound with all existing valid D9 upper bounds. Retain the original lower bound and enclose the complete W; never infer an exact tail merely from a smaller majorant.

Controls:

- Derive the IBP boundary term and mass/log identities explicitly for a constant and a linear polynomial. They have nonzero endpoint jumps and must not be treated as boundary-vanishing. Compare rigorous compact quadratures and enclosing tails on these controls before using the bound on the candidate.
- Evaluate at K=64/256 bits and, for any claimed surviving gain or bracket, K=80/400 bits. Both describe the exact same frozen wave. Check overlap of compact mass/archimedean intervals and final enclosures; export both evidence sets.
- Check the deliberately false assertion M=0 is rejected by a control with a strictly positive lower mass endpoint. Check factor-two/Fourier normalization by Plancherel on the simple controls.
- Replay one existing D9 fixed-wave score as a regression control. Every new calculation must have its complete analytic error allowance; agreement alone is not a certificate.

If an upper-tail improvement survives, but the 10% bracket does not, save the improvement and stop. Do not add coherent Bessel-tail expansion, new candidate selection or larger cutoffs to this round.

## Frozen prediction ledger

| ID | PREDICTED before this round | Pass/fail rule |
|---|---|---|
| P1 | The visible-form odd lower certificate closes with μ in [.0140,.0142]. | Must be an all-function certified bound in this interval, not a floating minimum. A completed attempt that does not close such a bound fails this prediction; an unfinished budget-limited calculation is UNVERIFIED. |
| P2 | The existing trial-4 wave passes the necessary gate against that new μ. | Exact outward comparison a≤1.1μ. If μ never certifies, UNVERIFIED. |
| P3 | Conditional on Stage C, the mass-conditioned archimedean tail upper bound is at least twice as small as the best old D9 tail upper bound at the identical T and normalization. | Compare **upper bounds**, not unknown true tails; both quadrature/precision runs must support the inequality. Otherwise failed or UNVERIFIED if unresolved. |
| P4 | The 10% full-W bracket will still be open after this one pilot. | A rigorous enclosure [μ,U] with U≤1.1μ falsifies this prediction. Failure to finish arithmetic is UNVERIFIED, not confirmation. |
| P5 | All stated mathematical controls hold; planted false claims are rejected. | List each result separately; no aggregate PASS covering unrun controls. |

P1–P3 are informed by the saved data, not novel numerical discoveries. P4 is deliberately conservative. Keep every failed prediction. Do not reinterpret a slightly different metric after the run.

## Deliverables and scope

Save source, frozen-input hashes, proof adaptation, exported interval endpoints, timing, a prediction ledger and `RESULTS.md`. Include one table with old redundant μ, new visible μ, fixed-wave scalar lower endpoint, old and new tail upper bounds, final W upper endpoint, and gap (U−μ)/μ. Label unresolved entries explicitly. A successful result would be one full-W bracket or a validated tail-bound improvement on one wave—not a new compact-window positivity theorem, a prolate identity, an asymptotic profile, or RH.

Commit and push only the new D25 files plus an additive hub row on `codex/metatron-prime-return-v0`. Hand the exact evidence back for audit. If D23's missing construction code becomes available, preserve it with provenance for a later review; do not turn this pilot into an additional prolate experiment.
