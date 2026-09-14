# D27 two-brackets pilot — prediction ledger (committed BEFORE any compute)

Base efc7a20. Executor DeepSeek 4.1 Flash. Caps: 60 CPU-min, 90 wall.

## Declared reading (discrepancy flagged)

Astra's D27 Task 3 says "2 and 3 are visible at L = 0.5". 2L = 1.0 and
log 3 = 1.0986 > 1.0, so at L = 0.5 only n = 2 is visible (log 2 = 0.6931);
that sentence matches L = 0.6 (2L = 1.2: log 2, log 3 visible; log 4 excluded).
This run uses the mathematically correct set {n=2} at L=0.5 — the same filter
the D22 candidate builder applies — and flags the discrepancy.

## Predictions (before compute)

1. **C2 layer-cake numeric check** (single Legendre mode, closed-form
   spherical-Bessel transform, Arb interval integrals at two cutoffs):
   identity holds to the enclosure width (relative overlap 1e-20 or better).
2. **L-threading control**: a saved D22 L=0.5 matrix entry reproduces via the
   clean-room quadrature with >= 15-digit overlap. If this fails, no L=0.5
   score is admissible.
3. **L=0.5 odd**: Stage A floor ell ≈ 0.0001809342 (D26 cert, visible {2});
   Stage B gate a/μ = 1.058 (recorded) → PASS. Stage C at T=1024: ratio
   1.06–1.10 → predicted CLOSE (a surprise only if the enclosure is wider than
   the gate margin).
4. **L=0.4 even**: Stage A floor per the even finite minimum; Stage C at
   T=1024: ratio > 1.5 → predicted OPEN (the tail is ~60x too loose for this
   sector); a closure would be the more important result. Either published.

## Labels

Stages A/B/C = certified floor / gate / fixed-wave interval score at a stated
cutoff. No RH claim. If C2 fails, the D26 closure is withdrawn and everything
downstream stops.
