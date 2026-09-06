# Fable handoff — audit D10, then D11: a short certificate for the joint balance?

2026-09-06. Addressed to **Fable, not Opus**. This is the next directive, not completed D11 research. Do not launch another auditor in place of doing this round yourself.

## Repository and base

- Repository: https://github.com/aumara-xyz/golden-horizon-principle
- Research branch: `codex/metatron-prime-return-v0` (not `main`, and not a request to overwrite `lab/millennium-v1`).
- Mathematical base: D10 result commit `fb55c90`; predictions were committed first at `1a89261`.
- Research hub: [README.md](README.md).
- Local path if on the same machine: `/Users/peterviviani/golden-horizon-principle`.
- Known interpreter: `/private/tmp/weil-arb-gTYWza/venv/bin/python`, python-flint0.6.0 plus mpmath. Record your actual machine, versions, precision and base HEAD; this temporary interpreter path may not exist on another machine.

Fetch the research branch and confirm `fb55c90` is an ancestor before working. Preserve any local work. Do not force-push, reset, overwrite another author's files, merge to main, or treat another branch as the publication destination.

## Report for Fable to check

Read [D10 results](../experiments/codex_d10_joint_geometry/RESULTS.md), [proof/scope](../experiments/codex_d10_joint_geometry/PROOF.md), [kernel proof](../experiments/codex_d10_joint_geometry/KERNEL-PROOF.md), [Schur proof](../experiments/codex_d10_joint_geometry/SCHUR-PROOF.md), and [predictions](../experiments/codex_d10_joint_geometry/PREDICTIONS.md). Read D9's full-tail proof before interpreting the pole mutations. Existing source/data live in [the D10 directory](../experiments/codex_d10_joint_geometry/).

### Claim A — a narrowly scoped exact obstruction

The full Weil form's continuous off-diagonal kernel is

    K(r)=2cosh(r/2)-exp(r/2)/(2sinh(r)).

With a=log(5/4), K(a)=-19/(18sqrt(5)) and K(2a)=5129/7380. Three smooth packets around -a,0,a, each supported within radius1/100, have signs (-,-,+), with no prime-shift cross terms. Triangle products exclude local diagonal phase/positive gauges making every off-diagonal real nonpositive. The post-preregistration analytic corollary places the sharp boundary for this sign obstruction at L=(log rho)/2, rho³-rho-1=0. This is NOT a boundary for Weil positivity or RH.

Counter-control: A=(1/2)I+vv^T, v=(1,-1,1), has the same sign pattern but positive eigenvalues 1/2,1/2,7/2. Its independent-edge comparison matrix has minimum -1/2. Thus arbitrary joint sums of squares are NOT excluded. No novelty or physical interpretation is claimed.

### Claim B — finite pole-directed square completion

At L=.7,T=120, let H be the D7 finite lower-envelope matrix without the pole, p the analytic cosh/sinh moment vector, and R_kappa=H+kappa pp^T. Authentic kappa=+2 even,-2 odd. In the fixed direction u=p/||p|| and its orthogonal complement, write H as [[a,b^T],[b,C]]. If C>0,

    R_kappa(tu+g)=(g+C^-1bt)^T C(g+C^-1bt)+sigma*t²,
    sigma=a+kappa||p||²-b^TC^-1b.

At80 modes per parity (C is79-dimensional), saved interval enclosures give the following approximate displays:

| Sector | min R_120 | min C | Improvement | sigma |
|---|---:|---:|---:|---:|
| Even | 1.03102e-13 | 1.22601e-8 | 118,912x | 2.16779e-13 |
| Odd | 5.85907e-11 | 1.71888e-6 | 29,337x | 2.53198e-10 |

Both Schur conditions also hold at20 and40 modes. Cancellation factors remain about2.69e13 even and2.11e9 odd. This reorganizes a previously positive finite lower envelope; it is not a new all-function or all-window proof. The reported minima are margins above zero, NOT adjacent-eigenvalue gaps.

### Claim C — controls and negative witnesses

At80 modes, arch-only / reversed-prime-weight reduced controls have minima about(-.256946,-.128390) even and(-.743208,-.143085) odd. Even controls fail C>0 despite positive sigma; odd controls have positive C but negative sigma. Odd pole-sign reversal stays positive. These negatives are for finite R_120, not automatically full W.

Separately, D9's already frozen full-W waves become rigorously negative when the pole coefficient is decreased by1e-4: even score lies in[-6.93713e-5,-6.93711e-5], odd in[-1.35048e-6,-1.30727e-6]. Their entire frequency tails are included. No reselection occurred.

D10 checked347 scalar endpoint records, six authentic finite Schur certificates,13 negative finite witnesses and10 full-W fixed-vector signs. All numerical predictions held. Repairs retained: interval residual-norm NaN caught by a control; exact-decimal witness export followed by a same-input rerun. All implementations shared a machine and Arb stack.

## D11 mission

**Test whether a short, predetermined sequence of joint matrix operations can certify the remaining Schur balance, without solving or diagonalizing the whole complement to construct the candidate.** An exact factorization by itself is not the target. Success would be finite compression evidence, not an RH mechanism.

Work only in `experiments/fable_d11_joint_balance/`, plus a small link/status addition to this research hub. Keep all Fable/Opus/Codex historical files unchanged. Use MEASURED / UNVERIFIED / PREDICTED / VOID; retain wrong predictions and every repair. No zero ordinates, phi fits, added physical models or enlarged L. Set a30-minute compute budget and at most90minutes total; stop and report exact partial status when either budget is reached. Do not spend the remaining budget on unregistered constructions.

### D11.0 — preregister before computation

Write and commit `PREDICTIONS.md` before numerical audit or experimental runs. Clearly distinguish results already disclosed above from new predictions. Predict:

1. Which D10 step is most likely to fail an independent audit, if any.
2. Whether at most8 Krylov steps certify positive sigma in BOTH parities at N=80.
3. The first successful order, or failure through32, in each parity.
4. Which hostile controls fail the SPD precondition, which fail the scalar inequality, and which legitimately remain positive.

Freeze L=.7,T=120,N=80 per parity; orders m={2,4,8,16,32}. Use only the sequence generated from b by C, with reorthogonalization or an equivalent stable CG/Lanczos implementation. No full C inverse, D10 minimizing vectors, full-matrix eigenvector deflation or adaptation against the target sigma may enter candidate construction. Small projected solves of dimension m are allowed. If using a preconditioner, its exact recipe must be in these predictions; baseline is unpreconditioned.

### D11.1 — audit the inputs before trusting the experiment

Derive the kernel, signed pole and Schur identity yourself from the stated Weil form before reading Codex's implementation. Then inspect the code. Check conjugations, the factor1/2 from shift symmetrization, the bump-neighborhood argument, complex gauges and the sharp-threshold corollary. Reproduce the positive frustrated toy: an auditor must NOT conclude 'not positive' merely from its edge signs.

Independently reconstruct the finite H and p using your existing frequency-form machinery or a separately written implementation, without copying D10's matrix-construction code. Same Legendre basis is appropriate for an entrywise diff. Record how independently your error bounds were derived. Compare enclosures, not just decimal agreement. Independently certify a positive lower bound delta for each authentic C, and separate bounds or a refusal for every control. A saved D10 delta may be used only in a clearly labeled fallback CONDITIONAL test, never called independent validation.

Recheck D10's saved negative finite witnesses and a full-W pole mutation. Scope the former to R_120. An unverified input or normalization must not be hidden by a successful numerical replay. If a substantive D10 defect is found, prioritize its correction in your own report; do not build a positive claim on the defective input.

### D11.2 — exact residual bracket, not an inverse fit

Keep a,b,C and p together. For any chosen response x_m, freeze its coordinates as exact decimal numbers and evaluate everything below in ball arithmetic:

    F_m=2b^T x_m-x_m^T C x_m,
    r_m=b-Cx_m.

If C>=delta I with a separately certified delta>0, then

    F_m <= q=b^TC^-1b <= F_m+||r_m||²/delta,
    sigma in [a+kappa||p||²-F_m-||r_m||²/delta,
              a+kappa||p||²-F_m].

Prove this identity/bound in your own report. Do not confuse a LOWER bound on q with the UPPER bound on q needed for positive sigma. Ordinary Lanczos/Gauss alone supplies the wrong side for that purpose. If you use Gauss–Radau as an additional enclosure, derive its hypotheses and certified spectral endpoints, handle loss of orthogonality, and retain the basic residual bracket as a check.

At each frozen m report the residual-norm upper bound, delta, q bracket width, sigma endpoints, and sign. A lower sigma endpoint>0 certifies the finite matrix together with C>0. An upper endpoint<0 gives a negative finite witness: directly score the corresponding (t,g)=(1,-x_m) in the ORIGINAL coordinates. Otherwise mark UNVERIFIED. Stop each authentic sector at the first certified order; do not silently continue to full dimension. If no order through32 closes, report failure of this bounded method.

**Frozen discriminator:** at most8 steps closing BOTH parities is the advertised finite-compression success. Orders16/32 may still provide a useful measured limit, but must not be relabeled as meeting that target. No statement about every L follows even from m=2 success.

If delta is certified by a full-size diagonalization/congruence check of C, the short Krylov response still depends on a full-size verifier. Label success as **compressed response construction**, not a short complete certificate or a structural bound. Count and report the cost of certifying delta; do not hide it outside the claimed speedup.

### D11.3 — controls first; mutations for any survivor

Before accepting authentic signs:

- Planted diagonal SPD matrix with analytically known q, and a rotated version with the same q. Verify enclosure and coordinate invariance.
- Indefinite C, singular C and interval-ambiguous delta: reject the SPD inference; never divide by a guessed positive minimum.
- The authentic family's arch-only and reversed-positive-weight controls, using EACH control's own certified C bound or refusal. Never reuse authentic delta for a different matrix.
- Pole sign reversal: even should be checked for failure; odd is permitted to remain positive. A positivity checker is not a model validator.
- Pole coefficient decreased by1e-4, with a direct finite witness check; compare against the separate full-W D9 witness without conflating the two forms.

For every authentic successful x_m, rerun its certification at doubled arithmetic precision without changing the vector, order, delta assumptions or window. Test the successful recipe at N=40, same m (all frozen orders fit its39-dimensional complement), recording that this changes the finite model, not L. Do not optimize new coefficients from an eigenvector: rebuild the same Krylov recipe from the N=40 C,b. If construction succeeds only after a revised rule, preregister the revision and retain the original failure. Any nonfinite value, sign-changing endpoint export, or missing delta must produce UNVERIFIED, not a positive certificate.

### D11.4 — deliver, scope, publish

Write `RESULTS.md`, `PROOF.md`, predictions, runnable code, exact frozen response vectors, matrix/input hashes, controls, endpoint JSONs and a small comparison table against D10. Report matrix construction separately from response construction and verification costs. Explicitly distinguish:

1. Independent audit of D10 (what was independently derived/rebuilt versus reused).
2. Independent or conditional FINITE compression certificate and the first successful m.
3. Still missing: a structurally proved lower bound on C and upper bound on q valid across all support widths.

End with one plain-language paragraph: did we make the balancing rule shorter, or just verify the same balance with another computation? No novelty or RH breakthrough claim from a finite run.

The user now asks that **every completed research round be committed and pushed to this research branch**. This supersedes older 'commit locally; do not push' round instructions for new work. Commit predictions before compute, commit results with a hub link, then perform a normal fast-forward push to `origin/codex/metatron-prime-return-v0` and verify the remote tip. Do not force-push. If another collaborator has advanced the branch incompatibly, preserve both histories and report the conflict rather than overwriting it. Report the actual result commit and full GitHub report URL; a local-only or failed push must be stated plainly.
