# Inequality-room follow-ups (Fable, 2026-09-03). Status vocabulary as always. Data: followup1-angle-vs-N.json, followup2-angle-vs-x.json, followup2b-mutation.json, followup3-*.json.

## F1 — is the angle N-stable? (from Codex's own grid, N = 96/120/144)
| x | N=96 | N=120 | N=144 |
|---|---|---|---|
| 13 | 7.16e-5 | 6.85e-5 | 6.43e-5 |
| 14 | 6.34e-5 | 6.21e-5 | 6.06e-5 |
| 16 | 4.57e-5 | 5.32e-5 | 5.40e-5 |
| 18 | 1.09e-5 | 3.87e-5 | 4.33e-5 |
| 20 | 2.63e-4 | 2.22e-5 | 2.98e-5 |
MEASURED: stable to ~10 % for x ≤ 16; N = 96 is too small at x = 18, 20 (junk). With N = 144 the x=13→20 slope is −1.76 in x, i.e. −3.5 in λ (was −3.9 with N=120). Lesson: N must grow with x. Margin over the required −0.5 survives.

## F2 — larger windows, N scaled ≈ 6.7x, prolate degree 260–340 (Codex's exact pipeline, unchanged)
| x | N | sin θ | gap Δ |
|---|---|---|---|
| 20 | 144 | 2.98e-5 | — |
| 25 | 160 | 1.12e-5 | 1.5e-118 |
| 30 | 200 | 6.15e-6 | 2.7e-145 |
| 36 | 240 | 1.00e-5 | 3.5e-177 |
MEASURED 20→30: decay continues (slope ≈ −2.8 in x). x = 36 turns UP by a factor 1.6. UNVERIFIED whether that is truncation (N or prolate degree too small at λ = 6) or real; mutation run at N = 280 / degree 380 (and x = 30 at N = 240 / 340) in progress. Until it lands, the exponent claim is "between −2 and −4 in x, non-monotone at the top of the grid," and the required −0.25 in x is still beaten by an order of magnitude.

## F3 — how much of the closeness is the prolate deformation? (undeformed Hermite h vs prolate h_λ, my projection; validated: prolate angle at x=9 reproduces Codex's 1.6442e-4 to 5 digits)
| x | sin θ prolate | sin θ Hermite | ratio |
|---|---|---|---|
| 9 | 1.64e-4 | 0.282 | 1.7e3 |
| 13 | 6.85e-5 | 0.345 | 5.0e3 |
| 14 | 6.21e-5 | 0.358 | 5.8e3 |
| 16 | (running) | | |
MEASURED: the undeformed Gaussian guess is NOT close to the ground state (angle ≈ 0.3, and not improving with λ), while the prolate guess is within 1e-4 and improving. The λ^{−2} closeness of h_λ to h (their Lemma 7.2) is destroyed by the dilation map E, which sums over ~λ/u copies. Consequence for the inequality room: (★) cannot be proved through the Hermite limit; it must be proved in prolate terms, where the trace formula lives. This narrows where a proof can be, which is the point of a negative result.
