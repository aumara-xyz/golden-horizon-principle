# D20 → Fable: three preregistered follow-on tests

2026-09-13. **PREDICTED; not run.** This file is committed with D20 before any of these experiments. It is not a retrospective preregistration of the existing D12–D19 data. D20 itself reviewed algebra, saved code/results, and literature only.

Read [RESULTS.md](RESULTS.md) first. Fable owns the next execution and should record the exact commit of this file, the interpreter/library versions, all inputs, and the final source hashes in a new `experiments/fable_d21_*/` directory. Do not edit earlier experiment files. Reuse validated routines by a provenance-recorded copy or a side-effect-free import, rather than silently modifying the old builders. Several old scripts execute scans at top level: do not import them in a way that starts an unplanned run before controls.

## Global rules and acceptance language

- No zero ordinates, zero-informed trial vectors, φ, or physical identifications. Selecting a wave from a matrix built entirely on the geometric side is allowed.
- ζ L ≤ 0.8 and Dirichlet L ≤ 1.2. The narrower lists below are frozen; no support enlargement.
- Every accepted match needs its control first; every substantive survivor needs the listed mutation. Keep failed predictions. Use MEASURED / UNVERIFIED / PREDICTED / VOID.
- Distinguish W, R, their finite compressions, and floating estimates in every output column. A negative lower estimate is not an upper certificate of a negative W score.
- Save coefficient vectors as exact decimal/rational inputs before certification. Freeze each proposal vector; do not reselect it after seeing a certification outcome without a separately recorded new trial.
- Numerical agreement alone is not interval certification. Missing norm, quadrature, infinite-tail, or discarded-space bounds mean UNVERIFIED, not an inferred sign.
- Do Test 1 first. Tests 2–3 are conditional and stop at their compute caps. No background continuation beyond those caps is authorized by this document.

## Test 1 — is the deletion failure in W or in its lower approximation?

**Question.** Resolve the conflicting saved signs for ζ, L = 0.7, even sector, removing n = 4. Then validate a very small preselected set of stronger deletion claims. Do not extrapolate their outcomes to every tested place.

**Frozen cases.** Authentic ζ at L = 0.7; deletion of n = 4, deletion of n = 2, and removal of all visible arithmetic terms. Both parities. Here n = 4 means only that power's coefficient, not the whole Euler block for prime 2. Every modified object is explicitly a mutation.

**Prediction.** The exact-W inference will fail to close for at least the marginal even deletion-of-4 claim: negative reduced-matrix output alone will not produce a certified negative W witness within this protocol. The strong prime-free odd negative witness will survive, as already established for a frozen vector in D9. This is a prediction about witness certification, not a prediction that the modified full operator must be positive.

**Protocol.** First validate the scalar scorer using analytic constant/linear shift overlaps, a shift outside the support, correct and incorrect pole conventions, and the original saved D9 fixed-wave intervals. These are controls, not new discoveries. Reproduce the competing adaptive-R conventions as proposals only, recording T, β, and N for each; if the missing D13 selector cannot be recovered, state that exact reproduction is unavailable and do not substitute an invented convention.

Select at most two arithmetic-side proposal waves per parity/case, one from a common reduced form with T = 160 and one from T = 240, each with 160 Legendre modes per parity. Save those waves. Independently enclose each wave's full W score by the geometric-side formula or the D9 complete-tail method. Also evaluate both reduced scores on each **same** wave. Freeze T and the vector during each comparison. The exact identity W − R = positive excess tail must hold within the enclosures. All displayed scores are divided by a rigorously enclosed positive norm.

**Survivor mutation.** Recompute each sign accepted as full-W negative with independent compact quadrature choices and increased working precision, without changing the vector. A second scorer should use a genuinely different representation where feasible; a shared special-function library is disclosed, not described as independent hardware verification. An intentionally omitted tail must be rejected by the checker.

**Report classes.** (a) Certified W-negative witness; (b) R-negative but W sign unresolved/positive on that wave; (c) neither sign resolved. Class (b) never proves positivity of the modified W on all waves. If the deletion-of-4 negative W witness closes, record the prediction above as failed.

**Kill conditions.** A normalization/prime-shift/pole control fails; exact fixed-wave enclosures from the two complete methods do not overlap; a required tail is missing; or the data cannot identify which operator was assembled. Then the affected result is VOID until repaired. An interval crossing zero is merely UNVERIFIED, not evidence of a contradiction.

**Compute cap.** 90 single-core CPU minutes, 160 modes per parity maximum, ordinary multiprecision proposal at 100 digits, certification at 100 then 200 digits maximum. If the allotted cases do not close, publish the unresolved cases and stop. Do not let eigensolver time displace the first independent scalar controls.

**Why this is not another small-margin/sign test.** It checks whether the quantity being interpreted was measured at all. Its result can change the truth status of “load-bearing” even if the saved R signs are unchanged.

## Test 2 — a profile independent of the cutoff and basis

**Prerequisite.** Test 1 establishes a correct full-W scorer and its norm/tail conventions. A new replay of a reduced certificate alone is insufficient.

**Frozen supports.** ζ L ∈ {0.40, 0.50, 0.60, 0.70}, both parities. No Dirichlet sweep in this test.

**Prediction.** The original dramatic decrease will survive qualitatively, but at least one existing reduced minimum will differ from a sufficiently resolved full-W bracket by more than 10% relatively. The old fixed exponential slope will remain a local fit, not a derived universal constant. If the profile cannot be enclosed tightly enough to test the 10% prediction within the cap, label that prediction UNVERIFIED.

**Protocol.** Compare T ∈ {160,240} and nested bases of 160 then 192 modes per parity. Use no zero-informed candidates. For each L, report separately: certified R lower bounds including the discarded basis space, and full-W upper bounds on frozen candidates. Do not report a candidate's scalar lower bound as an operator lower bound. Only where these sandwich the full infimum with positive lower endpoint and relative width ≤ 10% may that point enter the profile fit. A bracket that cannot close is an honest result. In particular, the positive tail discarded at T = 240 may itself prevent a 10% bracket; more arithmetic precision alone cannot recover it.

**Controls before fitting.** On one fixed wave, certify R160 ≤ R240 ≤ W, using the stated monotone envelopes; on nested finite spaces, verify the minimum of the same form cannot increase beyond its numerical enclosure. A deliberately mismatched norm or sign must fail the scorer. Record what changes when T changes rather than treating T as a physical parameter.

**Predetermined model comparison.** At accepted points, report the three neighboring log-slopes with propagated interval errors. Ask whether a single slope is compatible with all three intervals. Compare 64.1 and 57.4 only as the previous numerical summaries, not as fitted targets. No extrapolation outside the frozen range and no zero-count model evaluated at small invalid arguments. If four accepted points are unavailable, do not substitute precision-floor points or claim an asymptotic law.

**Survivor mutation.** Independently evaluate at least one accepted minimizing candidate in a sine-based/geometric representation, with its actual reconstruction error bounded in the form norm. A high L² overlap between two bases is not sufficient at a tiny energy scale.

**Kill conditions.** A violated same-form monotonicity or disjoint complete-score enclosures voids the comparison until repaired. Failure to obtain two-sided brackets kills the proposed attribution of a decay law, not positivity or RH.

**Compute cap.** Two single-core CPU hours; 192 modes per parity and 200 digits maximum. Reuse interval matrix entries where valid. Stop and publish partial brackets rather than automatically increasing a window, dimension, or precision.

**Why it can change belief.** The ordering W ≥ R and finite-dimensional variational ordering pull in opposite directions. Their quantitative difference is not fixed by the current margins and signs.

## Test 3 — cancel the known response, then measure the unresolved coupling

**Prerequisite.** A certified full-W finite compression and score convention at ζ L = 0.7 from Tests 1–2. If its two lowest eigenpairs/gaps cannot be enclosed adequately, skip this test as UNVERIFIED. This is a finite-projection diagnostic, not an all-function or Euler-product theorem.

**Frozen perturbations.** Independently vary the three visible coefficients n ∈ {2,3,4} along an affine path. These independently reweighted powers are artificial mutations, not L-functions. Work in at most 160 modes per parity, held fixed throughout. Form the two ground-state gradient rows and choose their common null direction v. A nullspace always exists with three columns, but this protocol requires certified rank two: use the oriented cross product, normalize by the norm of the direct sum Dv,even ⊕ Dv,odd (the maximum of the two sector norms), and fix its sign by the first nonzero coefficient. Interval rank ambiguity is a stop condition, not a basis-selection opportunity.

Let Dv be this direction. Enclose the first-order cancellation, the ground-state gaps gε, and

\[
 J_\varepsilon(v)=
 \sum_{j>1}\frac{|\langle u_j,D_vu_\varepsilon\rangle|^2}
 {\lambda_j-\lambda_\varepsilon}.
\]

This is minus half the affine eigenvalue curvature. Also report its dimensionless gap-normalized version hε = gεJε/‖Dv,ε‖², using the norm of that sector's restriction, and the orthogonal coupling norm ‖(I−uεuε*)Dvuε‖. Do not confuse that gap with λmin. If either restriction is identically zero, report that algebraic decoupling separately; do not divide by zero or apply the statistic below.

**Prediction.** There is no common annihilator: the tangent direction has nonzero coupling to other modes in at least one parity. For each parity define Eε = hε,auth / median(hε,control,k), k = 0,…,9; for ten values the median is the average of the fifth and sixth ordered values. Predict max(Eeven,Eodd) > 0.01. If both ratios are certified ≤ 0.01, the two-parity suppression falsifies this prediction and motivates a structural explanation. A zero or unresolved denominator stops this comparison. The generic negative curvature sign or a √margin threshold is not an informative success.

**Matched controls before authentic interpretation.** First use an exact 2×2 diagonal example with a known off-diagonal second-order response and a commuting example with zero coupling. Then express Dv,ε in each parity's eigenbasis, with eigenvalues ordered increasingly. Keep the base diagonal matrix fixed. Use ten permutation conjugates Qk*Dv,εQk, with Qk fixing the ground-state coordinate and permuting only the excited coordinates. Generate the permutation with `numpy.random.Generator(numpy.random.PCG64(seed)).permutation(M-1)`, seed = k + 1000ε, where ε = 0 for even and 1 for odd; record the NumPy version and save the ten actual integer permutations as exact inputs. Apply each permutation to the same certified matrix enclosures, without refitting or renormalizing it. This preserves the perturbation's spectrum, sector norm, ground derivative, and total ground-to-excited coupling norm, while changing how that coupling aligns with the base gaps. If excited eigenvalues cannot be ordered because enclosures overlap, stop rather than choosing a favorable ordering. Report all ten control values. These controls do not preserve the three-prime perturbation subspace; suppression would reveal spectral alignment, not by itself arithmetic specificity or novelty.

**Survivor mutation.** If exceptional suppression survives, perturb the relative coefficients of v by a fixed 1% in each coordinate in turn, reporting the newly nonzero first derivatives separately. Cross-check the authentic curvature via the projected resolvent and the spectral sum. Do not call a curvature effect if residual first-order leakage can explain it.

**Kill conditions.** Gradient cancellation, eigenpair/gap error, scorer error, or incomplete mode sums can exceed the proposed effect; then the curvature claim is UNVERIFIED. Disagreement of two exact finite-matrix evaluations beyond enclosures is VOID until fixed. No all-window conclusion is licensed by either outcome.

**Compute cap.** 45 single-core CPU minutes; fixed L = 0.7, 160 modes per parity, 100 then 200 digits maximum. Stop without a new inverse/projection ansatz if this does not close.

**Why this goes beyond the old account.** It removes both measured first-order responses and tests their common second-order geometry against controls with the same margin, gap, and zero first derivative. Only quantitative exceptional structure, not generic concavity, can change the current explanation.

## Handoff output

One results file, one machine-readable table of exact inputs/enclosures, the scorer/checker source, and the complete prediction ledger. Preserve W-negative versus R-negative-only labels. Link the result from the research hub and fast-forward push `codex/metatron-prime-return-v0`. Do not edit earlier reports to make their predictions look correct. If Test 1 is all the budget permits, a careful Test 1 is the completed next round.
