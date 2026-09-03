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
Mutation (larger N and prolate degree): x=30 at N=240/deg 340 → 1.47e-5 (was 6.15e-6 at N=200/deg 300); x=36 at N=280/deg 380 → 7.69e-6 (was 1.00e-5 at N=240/deg 340).
MEASURED: at x ≥ 30 the angle moves by factors of 1.5–2.4 under truncation changes, so individual values there are resolved only to within a factor ~2, and the "bump at 36" is truncation noise, not structure. Honest statement of F2: the angle falls from 3e-5 (x=20) to about 1e-5 (x=30–36) with an exponent somewhere between −1 and −3 in x that this grid cannot pin down; my earlier −3.9 (from N=120 data) and −2.8 (20→30) are VOID as precise exponents. What survives, robustly: at λ=6 the required threshold λ^{−½}(ln λ)^{−½} ≈ 0.3, and the measured angle is ~1e-5, four orders below it. (★) holds numerically with a wide margin; its RATE is UNVERIFIED beyond "faster than needed". Resolving the rate needs N and degree pushed until the value stabilizes, which at 180 digits is hours per point.

## F3 — how much of the closeness is the prolate deformation? (undeformed Hermite h vs prolate h_λ, my projection; validated: prolate angle at x=9 reproduces Codex's 1.6442e-4 to 5 digits)
| x | sin θ prolate | sin θ Hermite | ratio |
|---|---|---|---|
| 9 | 1.64e-4 | 0.282 | 1.7e3 |
| 13 | 6.85e-5 | 0.345 | 5.0e3 |
| 14 | 6.21e-5 | 0.358 | 5.8e3 |
| 16 | 5.32e-5 | 0.382 | 7.2e3 |
MEASURED: the undeformed Gaussian guess is NOT close to the ground state (angle ≈ 0.3, and not improving with λ), while the prolate guess is within 1e-4 and improving. The λ^{−2} closeness of h_λ to h (their Lemma 7.2) is destroyed by the dilation map E, which sums over ~λ/u copies. Consequence for the inequality room: (★) cannot be proved through the Hermite limit; it must be proved in prolate terms, where the trace formula lives. This narrows where a proof can be, which is the point of a negative result.
