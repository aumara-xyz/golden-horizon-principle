# Codex D9 — exact fixed-wave scores, including the infinite frequency tail

2026-09-06. Predictions committed before computation at `402b199`. No zero ordinates, fitted constants, larger support windows, or edits to Fable/Opus code. All results below are fixed-vector tests unless expressly called a conditional operator statement. No RH breakthrough or theorem novelty claimed.

## Outcome

The two unmodified D7 R_120-minimizing vectors were frozen as exact40-digit decimal coefficients and then scored independently by scalar integrals. They are NOT claimed to minimize the full W. At the first preregistered cutoff T=128, bounds on the entire omitted tail were sufficient to resolve every requested score sign. Stopped there; T=256,512,1024 were not needed.

**Exact R_theta is negative at theta=0.1,0.25,1 in both tested parities**, with certified upper endpoints below zero. This supplies the negative witnesses missing from D8's lower-envelope calculation. **The original W scores are positive**, and tiny positive mixing is not universally fatal.

## Full score intervals (outwardly rounded here)

| Fixed candidate | W(f)/||f||² | R_0.1(f)/||f||² | W without the prime term |
|---|---|---|---|
| Even D7 candidate | [9.25e-12,8.753e-11] | [-0.164120,-0.164118] | [0.03281345483,0.03281345492] |
| Odd D7 candidate | [5.135e-9,4.834e-8] | [-0.192413,-0.192412] | [-0.250120024,-0.250119979] |

Higher precision endpoint enclosures are in scores_even.json and scores_odd.json, verified by verify.py after serialization. Compact Arb display strings can over-enclose enough to lose a sign; use the explicit endpoint fields, not a dropped +/- radius.

On these same vectors, theta=0,1e-15,1e-14,1e-13,1e-12 are all positive; theta=0.1,0.25,1 are all negative. This finite grid does not locate the exact transition and is not a statement about positivity on other vectors.

## The cancellation is three-way; primes matter

| Contribution to W (normalized) | Even | Odd |
|---|---:|---:|
| Full archimedean A (approximate display) | -1.3546116582 | -0.2230077 |
| Pole | +1.38742511309 | -0.0271122858814 |
| Prime functional P | +0.0328134548279 | -0.250120028334 |
| How it enters W | subtract P | subtract P |

Removing arithmetic makes the odd candidate's exact score negative. The prime term is small relative to a crude worst-case bound but enormous relative to the remaining positive score. For these frozen waves all three individual shift correlations have the same sign within each sector; here the small net prime sum is not cancellation among positive and negative prime terms. The contribution is dominated by the shift log2.

| Weighted prime contribution | Even | Odd |
|---|---:|---:|
| n=2 | +0.0327819182110 | -0.248598539354 |
| n=3 | +0.0000315366089359 | -0.00152148634232 |
| n=4 | +7.96180912358e-12 | -2.63792427591e-9 |

These are different fixed candidates from D8's T=160 sweep. Differences from D8's saturation numbers are not presented as implementation errors or exact minima comparisons.

Wrong-pole mutation: the even candidate becomes negative (about -2.775), while the odd candidate stays positive (about +0.05422). A positivity check alone cannot identify the correct model.

## Rigorous infinite-tail handling

Scalar compact quadrature at T=128 is enclosed using320-bit Arb,64-node Gauss panels and a proved ellipse remainder. The complete archimedean tail is bounded by repeated integration by parts, retaining every endpoint derivative, plus derivative L2 norms and a(t)<=log t on the tail. Details: PROOF.md.

| Candidate | Chosen derivative order | Tail lower bound (approximate) | Tail upper bound (rounded up) |
|---|---:|---:|---:|
| Even | 11 | 9.066e-12 | 8.734e-11 |
| Odd | 12 | 4.742e-9 | 4.795e-8 |

The lower bound uses monotonicity of a and Plancherel tail mass. Thus a positive W lower bound and a negative R_theta upper bound are separate valid conclusions. The complete tail is not assumed negligible and no negative lower approximation is promoted to a negative exact score.

Prime integrals are polynomial-exact Gauss quadrature with159/160 nodes (degrees158/159), enclosed in Arb and cross-checked with16 more nodes. Pole integrals use the closed-form modified spherical Bessel identity. The existing D7 builder was reused solely to choose frozen vectors and reproduce its original data in this directory: this is not an independent reconstruction of the D7 operator certificate.

## Tiny mixing survives for ALL waves, conditional on D7

The previously certified m=1.031e-13 gives R_theta>=[m-theta(c_L+B_L)]I. Arb evaluates the bracket at theta=1e-14 to more than5.69e-14. Thus every theta in [0,1e-14] preserves positivity at L=0.7, conditional on D7's operator certificate. Do not extrapolate our scalar positivity at theta=1e-12 to all functions.

This corrects D8's universal 'every positive theta fails' wording while confirming failure at the larger tested values by actual counterexamples to the modified form. Negativity of R_theta does NOT refute positivity of W, because R_theta is a different, smaller form.

## Controls, mutations and prediction ledger

12 control checks passed before authentic sign acceptance: constant/linear analytic overlaps, zero-overlap and touching-endpoint cases, Legendre derivative,64/80-node compact quadrature overlap, refusal of missing/negative/nonfinite tails and crossing-zero intervals, planted negative and positive intervals. A second verify.py pass checked compact quadrature on both actual candidates and reparsed every exported sign. Every original prime overlap also passed the higher-node mutation. Two additional Codex readers independently checked the scalar and tail formulas without editing the code; neither reran a full operator certificate or used another arithmetic library.

| Prediction | Outcome |
|---|---|
| P1 original fixed-vector W positive | HELD; direct scalar bounds resolve both signs |
| P2 exact R_0.1,R_0.25,R_1 negative | HELD in both sectors, entire tail included |
| P3 arithmetic not negligible relative to residual | HELD; removal changes odd score to negative |
| P4 tiny-theta all-wave margin conditional on D7 | HELD; explicit margin >5.69e-14 at1e-14 |
| P5 affine exact-score identity | HELD by construction from independently enclosed full W and exact prime functional |

All prediction outcomes retained. Two implementation/export repairs are preserved in REPAIRS.md: an interval-equality control at touching support endpoints, and serialization that obscured positive signs. Neither was a changed physical hypothesis or fitted parameter. No candidate reselection occurred.

## Reproduce

Interpreter used: /private/tmp/weil-arb-gTYWza/venv/bin/python (python-flint0.6.0; shared Arb infrastructure). From repository root:

```
python experiments/codex_d9_exact_scores/freeze.py even
python experiments/codex_d9_exact_scores/freeze.py odd
python experiments/codex_d9_exact_scores/score.py controls
python experiments/codex_d9_exact_scores/score.py even
python experiments/codex_d9_exact_scores/score.py odd
python experiments/codex_d9_exact_scores/verify.py
```

The first two commands regenerate the frozen candidates and should only be used to reproduce this selection recipe. Normal verification should use the committed frozen JSONs. Saved source hashes identify the D7 selector version. Outputs stay in this directory. All runs fit within the25-minute preregistered compute allowance; each candidate-selection replay took about34 seconds and score runs were short scalar calculations. Nothing pushed.

## Honest paragraph — where elegance would have to appear

The result is not an elegant solution to RH. It is a cleaner diagnosis: uniform worst-case substitution throws away the correlation among archimedean, pole and prime terms that protects these small positive scores. A promising structural target would preserve that dependence in a single inequality or explicit positive representation across every support window. Saying 'find a positive representation' is a goal, not a construction or a proof; no such all-window mechanism was found. These tests establish negative witnesses for this particular relaxation at specified mixing values and retain the original positive fixed-wave scores. They neither rule out other arithmetic approaches nor validate a physical chaos, hologram or phi model.
