# Codex D9 — fixed-wave exact-score tests

2026-09-06. Commit before computation. Budget: approximately 25 minutes of bounded computation, at most two frozen 80-mode candidates, no zero ordinates, no larger L, no edits to Fable/Opus files, no pushing.

## Candidate selection, frozen before scoring

L=7/10. Obtain one real vector per parity from the existing Opus D7 unmutated 80-mode R_T (T=120) eigensolver, using its existing recipe and exact 40-digit decimal coefficients. Run the unchanged builder in this round's output directory, not its original directory. Save those coefficients before any new full-form scoring. This reuses D7 to select vectors; it is NOT a new independent operator certificate. Do not optimize candidates against D9 outcomes.

## New scalar checks

Re-evaluate each fixed wave's pole, individual prime-shift correlations (n=2,3,4), and archimedean integral separately in Arb. Prime integrals use polynomial-exact Gauss-Legendre with enough nodes for degree 318; pole uses closed-form Bessel i_n. Frequency integrals use scalar Gauss-Legendre on unit panels, 64 nodes, rho=1.9, independently bounded errors. Bound all omitted frequency mass and log-weighted mass by repeated integration by parts using endpoint derivatives and derivative L2 norms. Preregister cutoffs T=128,256,512,1024; derivative orders 1..12. Stop as soon as the requested signs are certified, retaining all attempted bounds. Combining proved bounds by intersection/minimum is allowed and not a fit.

Compute W=A+pole-prime and exact R_theta=W-theta(c_L-prime), normalized by ||f||². Frozen theta grid: 0,1e-15,1e-14,1e-13,1e-12,0.1,0.25,1. A negative reduced lower approximation is NOT a negative exact score; require an upper bound below zero. Report unresolved signs as UNVERIFIED.

## Predictions

P1: D7 even/odd candidates have full W positive. Direct scalar bounds may not resolve the tiny positive margin; distinguish that from the pre-existing D7 operator guarantee.
P2: theta=0.1,0.25,1 exact R_theta scores are negative in both sectors, with rigorous tail included. Predicted failure mode: polynomial derivative tail bounds too loose within T<=1024.
P3: the sum of prime contributions is much smaller than c_L, but is NOT negligible relative to W; removing that sum changes the score by orders of magnitude. Report each shift to test whether small net saturation hides cancellations.
P4: tiny theta<=1e-14 remains positive as an OPERATOR statement conditional on D7 m=1.031e-13, using R_theta >= [m-theta(c_L+B_L)]I. Certify this scalar inequality independently. Do not confuse this with candidate-only signs.
P5: exact scores obey the affine identity R_theta=W-theta(c_L-prime). They need not equal the floating D8 frequency-reduced scores.

Controls BEFORE accepting authentic signs: exact constant and linear test waves; exact zero overlap for shifts >=2L; interval checker rejects missing/negative/nonfinite tail evidence and refuses sign classification for intervals crossing zero; wrong pole sign separately labeled model mutation (not expected to fail positivity in both sectors). Validate prime integrals with higher node count, compact frequency integrals at 64/80 nodes on a small interval, and derivative endpoint identities on low Legendre polynomials. Keep failures and repairs. Use MEASURED/UNVERIFIED/PREDICTED/VOID. No new theorem novelty claim.
