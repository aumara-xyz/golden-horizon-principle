# Codex D10 — joint geometry: an obstruction and a completion of squares

2026-09-06. Preregistered at `1a89261`. L=7/10 throughout; no zeta zero input, fitted constants, new support windows, or edits to Fable/Opus files. Sources, mathematical scope and proof details: [PROOF.md](PROOF.md). Local results, not pushed.

## Outcome in plain language

The Viviani-inspired question was useful: can changing pieces be kept in one exact relationship instead of bounded independently?

**MEASURED:** a local 'all positive springs' picture fails for the actual Weil kernel. **MEASURED:** a joint completion of squares works for the tested finite lower-envelope matrices and isolates a substantial part of their small-eigenvalue behavior. **UNVERIFIED:** a structural reason for the remaining inequalities that works for every support width. No RH solution or theorem novelty is claimed.

The distinction matters: a positive expression need not consist of independently positive pairwise interactions. It can depend on a square involving several variables together. This is an algebraic fact, not evidence of physical chaos, a hologram, or an observer. Unlike the distance sum in Viviani's theorem, W(f) is not constant as f changes.

## 1. The exact joint rewrite, and where the difficulty remains

With D_u(f)=||f(.+u)-f||² and the conventions in KERNEL-PROOF.md,

    W(f) = (a0-B)||f||² + Pi(f)
           + 1/2 integral_0^infinity [exp(u/2)/sinh(u)] D_u(f) du
           + 1/2 sum_n w_n D_log(n)(f).

Every displayed difference square is nonnegative. However, a0-B is negative and the odd pole is negative. The identity preserves the needed compensation; it does not prove it. The complete prime/pole/background relationship must still be controlled.

## 2. A precise obstruction to local pairwise positive conductances

The continuous off-diagonal kernel is K(r)=2cosh(r/2)-exp(r/2)/(2sinh(r)). Put a=log(5/4). Direct transcendental and algebraic interval evaluations agree:

    K(a)=-19/(18sqrt(5))<0,
    K(2a)=5129/7380>0.

Three nonnegative smooth packets near -a,0,a therefore have edge signs (-,-,+). Their radius-1/100 neighborhoods fit inside the window, have no prime-shift cross interaction, and have strictly certified signs throughout. No real sign gauge (0 of 8) or complex pointwise phase gauge can make all three nonzero edges negative: the product around a triangle is unchanged. Positive pointwise scaling cannot change these signs either.

This excludes a **local diagonal-gauge, nonnegative-conductance pairwise-square representation of the full form**. It does not exclude nonlocal changes of basis, additional compensating remainders, general sums of squares, or positivity.

The decisive counter-control is elementary. For v=(1,-1,1),

    A=(1/2)I+vv^T,
    x*Ax=(1/2)(|x1|²+|x2|²+|x3|²)+|x1-x2+x3|².

A has the SAME conflicting edge signs, yet eigenvalues 1/2,1/2,7/2. Replacing each off-diagonal by minus its absolute value creates eigenvalue -1/2. Thus independent edge replacement destroys positivity in this toy; the joint square retains it. This toy is not a discretization of W.

Fourteen kernel controls and ten endpoint-sign reparses passed. Pole deletion and long-edge sign reversal each permit 2/8 gauges, as expected. Proof: [KERNEL-PROOF.md](KERNEL-PROOF.md); data: [kernel_results.json](kernel_results.json).

**Unplanned analytic corollary, not a blind prediction:** the above sign obstruction exists for every L>(log rho)/2, where rho³-rho-1=0, and is absent for smaller L. PROOF.md gives the strict-inequality and endpoint argument. This is only a boundary for that particular sign obstruction, NOT a positivity threshold. The cubic constant follows from the fixed kernel; no significance in nature or relation to phi is asserted.

## 3. Isolating the known pole direction without separating the primes

Replayed unchanged D7 data provide H=R_120 minus its pole. R_120 is a LOWER ENVELOPE, not the full W matrix. Its pole vector p is fixed analytically by cosh(x/2) or sinh(x/2), not chosen from the minimizing eigenvector. Principal blocks have 20,40,80 Legendre modes per parity.

Writing f=tu+g with u=p/||p|| and g perpendicular to u gives, if C>0,

    R_kappa(f)=||C^(1/2)(g+C^(-1)b t)||²+sigma |t|²,
    sigma=a+kappa||p||²-b^T C^(-1)b.

Here H, hence C and b, keeps arithmetic and background contributions together. Authentic kappa is +2 even, -2 odd. Both C and sigma are interval-certified positive in all six authentic finite blocks. Numerical values below are approximate displays of the saved enclosures, not newly rounded certificate endpoints.

| Parity | Modes | min R_120 | min C | Improvement min C / min R | sigma |
|---|---:|---:|---:|---:|---:|
| Even | 20 | 1.16275e-13 | 1.52349e-8 | 131,024 | 2.44570e-13 |
| Even | 40 | 1.03917e-13 | 1.23642e-8 | 118,982 | 2.18499e-13 |
| Even | 80 | 1.03102e-13 | 1.22601e-8 | 118,912 | 2.16779e-13 |
| Odd | 20 | 6.64035e-11 | 2.01325e-6 | 30,318 | 2.87139e-10 |
| Odd | 40 | 5.85956e-11 | 1.72531e-6 | 29,444 | 2.53220e-10 |
| Odd | 80 | 5.85907e-11 | 1.71888e-6 | 29,337 | 2.53198e-10 |

These 'gaps' are minimum eigenvalues above zero, NOT consecutive-eigenvalue spacings. Removing one direction improves the scale but does not leave an order-one robust background. At 80 modes, the next complement eigenvalues are approximately 4.73545e-4 even and 7.61595e-3 odd; two even and one odd complement eigenvalues fall below 1e-3 by the explicitly midpoint-only count.

The remaining subtraction is severe. The cancellation factor (|a|+|kappa|||p||²+|b^TC^-1b|)/|sigma| is about 2.69e13 even and 2.11e9 odd. The response norms ||C^-1b|| are about 1.05003 and 1.82246. Computing square roots after checking positivity is an equivalent reformulation, not a discovered explanation of it.

For positive C, the finite critical pole strength is kappa_crit=(b^TC^-1b-a)/||p||², and positivity requires kappa>kappa_crit. At 80 modes:

- Even kappa_crit ≈ 1.999999999999851377248132; authentic +2.
- Odd kappa_crit ≈ -2.000000004321985103554; authentic -2.

These are thresholds for the finite lower-envelope family only. Their closeness to the authentic coefficients describes the existing near-null balance; it is not a new invariant or physical fine-tuning claim.

## 4. Hostile controls and full-form mutations

Controls ran before authentic result acceptance, with identical support, basis, pole vector, beta and cutoff. At 80 modes:

| Finite reduced model | Parity | min R (approx.) | What fails |
|---|---|---:|---|
| Archimedean-only | Even | -0.256946 | C is indefinite, although sigma is positive |
| Reversed prime weights | Even | -0.128390 | C is indefinite, although sigma is positive |
| Archimedean-only | Odd | -0.743208 | C positive, sigma negative |
| Reversed prime weights | Odd | -0.143085 | C positive, sigma negative |
| Pole sign reversed | Even | -5.78819 | C positive, sigma negative |
| Pole sign reversed | Odd | +1.71885e-6 | Stays positive; positivity alone cannot validate the model |

Deletion/permutation controls have one certified negative eigenvalue at all three mode counts. These are negative witnesses for finite R_120, NOT automatically for full W. Thirteen exact-decimal finite witnesses were exported and directly rescored twice, preserving their signs.

Separately, the already frozen D9 waves provide genuine **full-W** pole-mutation witnesses, retaining the complete certified frequency tail. Lowering kappa by 1e-4 gives outward display intervals:

- Even: W_modified/||f||² in [-6.93713e-5,-6.93711e-5].
- Odd: W_modified/||f||² in [-1.35048e-6,-1.30727e-6].

Lowering by 1e-2 also makes both negative. Raising by 1e-4 or 1e-2 keeps both fixed-vector scores positive. These artificial coefficient mutations are not alternate zeta functions, and positive scores do not establish all-vector positivity. Data: [pole_witness_results.json](pole_witness_results.json).

## 5. Prediction ledger, repairs and reproducibility

| Prediction | Outcome |
|---|---|
| P1 exact kernel signs, neighborhood/gauge controls | HELD; analytic identities were known during design and are not blind discoveries |
| P2 authentic C and sigma positive in all frozen finite blocks | HELD, interval-certified; consistent with already known D7 positivity |
| P3 at 80 modes, improvement >=1000x in both sectors but a small complement mode remains | HELD; ratios ≈118912 and29337 |
| P4 arithmetic controls fail at least one Schur condition | HELD; both deletion and reversal fail in each parity |
| P5 full-W pole perturbation signs on frozen D9 waves | HELD; all10 endpoint verdicts reparsed |

No failed numerical prediction was hidden. One planted Schur control caught NaN from interval squaring across zero before taking a norm. The repair uses absolute-value endpoint bounds and rejects nonfinite exports. A second export-only repair stored the negative-witness coefficients as the actual frozen decimal strings, followed by a complete same-input rerun. Neither changed a construction, prediction or selected wave. Both are disclosed in SCHUR-PROOF.md and source.

Seven planted Schur controls ran in each parity, including positive/negative/indefinite inertia and singular/ambiguous refusal. Root verification reparsed 347 scalar endpoint records, confirmed six authentic Schur certificates, independently rescored 13 negative finite witnesses, and checked ten full-W fixed-vector signs. Kernel and Schur derivations and control construction were reviewed by additional readers. All use the same machine and Arb infrastructure, not an independent arithmetic stack. No proof-assistant or external referee validation is claimed.

Reproduce with python-flint0.6.0 and mpmath (interpreter used: /private/tmp/weil-arb-gTYWza/venv/bin/python):

```
python experiments/codex_d10_joint_geometry/kernel_test.py
python experiments/codex_d10_joint_geometry/build.py even
python experiments/codex_d10_joint_geometry/build.py odd
python experiments/codex_d10_joint_geometry/schur.py even
python experiments/codex_d10_joint_geometry/schur.py odd
python experiments/codex_d10_joint_geometry/schur.py verify
python experiments/codex_d10_joint_geometry/pole_witness.py
python experiments/codex_d10_joint_geometry/verify.py
```

The saved inputs suffice to replay Schur analysis without rebuilding. Builder source and input hashes are retained. Builders took about45 seconds per parity; each Schur pass about90 seconds per parity, repeated once for witness export. Parities ran concurrently and the computation remained inside the25-minute allowance. Original author files were untouched.

## Honest paragraph and next useful test

We have a more precise question, not an elegant solution to RH. The local positive-spring representation is obstructed, but a positive expression can contain conflicting pair interactions. The finite joint completion retains cancellations and separates a known pole direction; nevertheless it moves the unresolved work into positivity of C and a tiny sigma, rather than making that work disappear. The next worthwhile target is an analytic bound on b^TC^-1b that preserves the actual prime/background dependence, together with control of C, under a rule valid for arbitrary support. Another finite factorization is not enough. No all-window argument, new positivity theorem, proof of physical chaos/holography, or verified novelty has emerged from this round. Viviani's contribution here is the methodological inspiration to account for the whole relationship, with every part and limitation visible.
