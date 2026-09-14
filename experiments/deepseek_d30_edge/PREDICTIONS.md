# D30 — Edge of the method: predictions (preregistered before any compute)

Base tip 6176889. Court frozen at its D28 hashes. No GPU. API cap $3 (expected spend: $0 — no
model calls are part of this round). Budget: 60 CPU-min, 90 wall, hard stop.

## Task 0 — correction (no compute)
Gate definition: the infimum bracket is [ell, W_hi], so the gate is **W_hi/ell < 1.10**; the D28
tables' W_lo/ell column is not a bound on the infimum and is not the gate. Restated closures on the
corrected criterion: L=0.4 odd 1.0884, L=0.5 odd 1.0882, L=0.4 even 1.0643 (D29).

## Task 1 — visible-form all-function floors (T=160, N=160, K=64; L=0.7 also T=240, N=192)
Existing (cite, do not recompute): L=0.4 odd 0.0141715765223 (D26); L=0.4 even 0.000172308870206 (D27);
L=0.5 odd 0.000180934196848 (D26).
New (this round): L=0.5 even; L=0.6 odd; L=0.6 even; L=0.7 odd; L=0.7 even (T=160); L=0.7 both parities
(T=240), each = finite eigenbound (certified lambda0) plus the three Schur tails (eps_D, eps_C,
eps_p/norm_pN), with the D24-repaired quadrature allowance.

Prediction (directive): every new floor lies above its D22 counterpart by 0 to 25 percent. The D22
counterparts (void endpoints, invisible shifts kept):
| L | odd lambda0 (D22) | even lambda0 (D22) |
|---|---|---|
| 0.4 | 0.0124019265771 | 0.000144919164005 |
| 0.5 | 0.000142134532495 | 7.14785349231e-7 |
| 0.6 | 4.12866743816e-7 | 1.10135673044e-9 |
| 0.7 | 1.58596369131e-10 | 2.67167228677e-13 |
| 0.7 T=240 | 2.03304233017e-10 | 3.37581912571e-13 |

Measured visible/void ratios at the three known points: 0.4 odd 1.143, 0.4 even 1.189, 0.5 odd 1.273.
My numerical sub-prediction: new floors near D22 x {1.15-1.30}: L=0.5 even 8.2-9.3e-7; L=0.6 odd
5.0-5.6e-7; L=0.6 even 1.3-1.5e-9; L=0.7 odd 2.0-2.2e-10; L=0.7 even 3.3-3.7e-13. Also: log-slopes
between rooms (per L step) increase with L in both parities.

## Task 2 — D23 profile on the certified table
Fit log ell vs M1: A - B*L and M2: A - C*exp(2L) on the four T=160 points per parity (0.4, 0.5, 0.6, 0.7).
Prediction (directive): M2 wins in both parities with relative RMS slope error under 10 percent; if not,
D23's law is dead. No asymptotic claim either way.

## Task 3 — brackets at the edge (T=1024, D28 winning rule frozen, no reselection)
Cases and preregistered outcomes:
| case | predicted ratio (W_hi/ell) | predicted verdict | deciding stage if open |
|---|---|---|---|
| L=0.5 even | 1.07 to 1.12 | closes, may miss the 1.10 gate narrowly | tail (A_up) if it misses |
| L=0.6 odd | 1.08 to 1.15 | closes or misses narrowly | tail / floor tightness |
| L=0.6 even | above 1.3 | stays open; floor ~1e-9, required absolute tail beyond the mass-conditioned bound's demonstrated reach | tail |

The valuable output is the first room where the method fails and why. No T escalation, no rule change,
no reselection.

## Task 4 — provenance
Reconstruct d23.py from d23_results.log's header and the D23 RESULTS description (fits on the eight
D22 certified lower bounds; prolate overlaps over Omega); label a provenance repair. Commit the Task 1
floor JSONs with sha256 hashes.

## Prediction ledger for this round (refined after compute, never edited)
- Task 1: new floors in the stated windows; D22-plus 15-30 percent.
- Task 2: M2 under 10 percent in both parities (D23 law survives) else dead.
- Task 3: 0.5 even closes (maybe narrowly), 0.6 odd close-to-narrow-miss, 0.6 even open >1.3.
