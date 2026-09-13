# D20 — the margin, the measuring instrument, and the echoes

2026-09-13. Codex/Astra's adversarial reply to Fable's [D20 handoff](../../Reimann%20Research/ASTRA-HANDOFF-D20.md). Reviewed base: `fd36b054211492dfc8872126280114aeca21f308`, branch `codex/metatron-prime-return-v0`.

**Verdict: preserve the certified core; revise the interpretation of the later scans.** The evidence does not reduce to “one number and a sign.” It involves a margin, directional response, coupling to other modes, and—first of all—identifying which operator the numbers belong to. The decay constant 64 is not derived. The entry-stage parity effect has an elementary boundary-reflection explanation. Prime-power echoes admit an exact resolvent identity, but that identity does not prove Weil positivity.

This round is an analytic, source, and saved-code audit, **not a fresh numerical experiment or independent replay of the certificate**. No zero ordinates entered a construction or parameter choice. All numerical values below come from the recorded lab results unless explicitly described as elementary arithmetic. Historical predictions are not rewritten. Three future tests, still **PREDICTED**, are frozen in [PREDICTIONS.md](PREDICTIONS.md). The complete reading and source map is [SOURCE-MAP.md](SOURCE-MAP.md).

## 1. What survives, and what the numbers actually measure

The [D6](../weil_hidden_modes/FABLE-ROUND-D6-RESULTS.md)/[D7](../weil_hidden_modes/OPUS-ROUND-D7-RESULTS.md) record supports the advertised bounds at **L = 0.7**:

| Sector | Recorded certified bound on W(f)/‖f‖² | D20 scope |
|---|---:|---|
| Even | 1.031e−13 | Retained; no new certificate replay here |
| Odd | 5.859e−11 | Retained; the withdrawn 5.86e−11 stays withdrawn |

The form is finite on the stated log-weighted Fourier form domain and extended-valued on the rest of L². The certificate controls the omitted function space, not merely a finite matrix. The corrected D7 sandwich widths remain 2.34e−11 even and 5.75e−14 odd **relative widths**. Same-machine/shared-Arb and external proof-review limitations remain.

For ζ and the real primitive characters tested here, use the lab's unitary Fourier transform F and write

\[
 W_L(f)=\Pi(f)+\int_{\mathbb R}\Psi_L(t)|F(t)|^2dt,
 \qquad \Psi_L(t)=a_\chi(t)+\log q-\sum_n w_n\cos(t\log n),
\]

where aχ(t) = Re ψ(1/4 + κχ/2 + it/2) − log π and κχ records character parity. At the authentic weights, wₙ = 2Λ(n)χ(n)/√n. Only prime powers with log n < 2L contribute; equality has zero overlap almost everywhere. For ζ, q = 1 and the pole is +2|C|² − 2|S|², with C = ∫f cosh(x/2) and S = ∫f sinh(x/2). Nonprincipal primitive characters have no pole.

The saved [D15 code](../fable_d15_dirichlet/d15_slack.py), [D16 code](../fable_d16_places/d16.py), and [D17 code inherited by D19](../fable_d17_squares_exponent/d17.py) instead assemble

\[
 R_{L,T}(f)=\Pi(f)+\beta\|f\|^2+
 \int_{-T}^{T}(\Psi_L(t)-\beta)|F(t)|^2dt,
 \quad \beta=a_\chi(T)+\log q-B,\quad B=\sum_n|w_n|.
\]

The identifying code is `sym = ... - beta`, followed by `... + beta*np.eye(...)`. Where the envelope applies,

\[
 W_L(f)-R_{L,T}(f)
 =\int_{|t|>T}(\Psi_L(t)-\beta)|F(t)|^2dt\ge0.
\]

This tail is a deliberately discarded **positive quantity**, not just quadrature error. Define mW as the full-window W infimum, mT as the full-window R infimum, and mN,T as R's infimum restricted to the finite basis. Then

\[
 m_T\le m_W,\qquad m_T\le m_{N,T}.
\]

**These inequalities do not order mW and mN,T.** The frequency reduction lowers the score; the finite-basis restriction raises the infimum. Therefore:

- A negative finite R score is not a negative W witness.
- A positive finite R matrix is not all-function positivity without the discarded-space argument.
- D7 supplies that latter argument. Later floating tables do not inherit it automatically.

Mutations in D16/D17 also recompute B, β, T, and the basis dimension. Thus “all else fixed” is not literally true of the numerical family. This need not make its trends spurious, but it prevents interpreting them directly as full-W response curves. [D9 already demonstrated the proper repair](../codex_d9_exact_scores/RESULTS.md): freeze a vector and certify the complete score, including its tail. Its negative prime-free odd witness survives; this review does not erase that result.

A useful existing disagreement is ζ, L = 0.7, even sector, deleting n = 4. [D13](../fable_d13_prime_weights/RESULTS.md) reports +3.1e−13 for the surviving {2,3} terms; [D16/D17](../fable_d17_squares_exponent/RESULTS.md) report approximately −8.4e−13. These are different reduced-form protocols near a delicate margin, not two established contradictory signs of the exact W. Resolving that specific case is more valuable than another broad deletion scan.

## 2. Q1 — Weyl gives a safe ball, not a universal fragility law

For A ≥ mI, Weyl gives λmin(A + E) ≥ m − ‖E‖. It proves safety when ‖E‖ < m. It does **not** prove failure whenever ‖E‖ > m. This direction matters. The variational principle and Weyl bounds are standard; see [Tao's Hermitian-matrix notes, 2010](https://terrytao.wordpress.com/2010/01/12/254a-notes-3a-eigenvalues-and-sums-of-hermitian-matrices/).

Here are exact algebraic counterexamples, not experimental data. Let A = diag(m,1), 0 < m < 1, and perturb by tD, t ≥ 0.

| D, always of norm 1 | Initial derivative of the minimum | First zero |
|---|---:|---:|
| diag(−1,0) | −1 | t = m |
| diag(−m,1) | −m | t = 1 |
| Off-diagonal entries 1, diagonal 0 | 0 | t = √m |
| diag(0,1) | 0 | Never |

Even the **same margin, perturbation norm, and harmful sign** allow radically different thresholds. For a normalized simple ground state u, the missing first-order number is d = ⟨u,Du⟩. The frozen-vector bound gives

\[
 \lambda_{\min}(A+tD)\le m+td.
\]

If d < 0, failure is guaranteed for t > m/|d|, whereas Weyl guarantees safety for t < m/‖D‖. A narrow threshold needs both statements or a sharper comparison, not Weyl alone.

Let g = λ₂ − m > 0. Differentiating the normalized eigenvalue equation gives, for an affine path,

\[
 \lambda''(0)=-2\sum_{j>1}
 \frac{|\langle u_j,Du\rangle|^2}{\lambda_j-m}.
\]

One conservative local bound, for |t|‖D‖ ≤ g/4, is

\[
 m+td-2t^2\|D\|^2/g\le\lambda_{\min}(A+tD)\le m+td.
\]

So the informative object is a **local perturbation geometry**: margin, gradient, and gap-weighted coupling/Hessian. The eigenvalue gap g is not the positivity margin m. If two directions cancel the first-order response, this geometry—not the original signs—decides what happens next.

Fable's D19b moves in the right direction by measuring a second quantity. But it saves a central secant with step 1e−4, not a validated derivative. No step-halving, Hellmann–Feynman comparison, or curvature bound is recorded. At ζ L = 0.6, that step exceeds the inferred even boundary distance by over 4,000 times. That alone does not invalidate a secant; it makes the missing validation consequential.

**Answer to Q1:** much of the fragility is unsurprising once harmful directional responses are bounded away from zero. But their magnitudes, cancellations, mode switching, curvature, and the distinction between W and R are not corollaries of “small margin plus signs.”

## 3. Q2 — 64 is a fit, not a derived prolate constant

The ordinary concentration operator is

\[
 (S_{L,T}f)(x)=\int_{-L}^{L}
 \frac{\sin(T(x-y))}{\pi(x-y)}f(y)\,dy.
\]

It depends after rescaling on c = LT. Its eigenvalues tend to zero at **every fixed nonzero window**. Its infinite-dimensional bottom is therefore zero. That alone distinguishes it from the certified strictly positive Weil floor. The reduced Weil operator is βI plus a weighted, generally sign-indefinite compact operator and a pole term; its essential spectrum is {β}. The full W additionally has an unbounded log-frequency symbol. A comparison with a complement or a weighted prolate operator could be legitimate, but it must be specified and proved. A frequency cutoff is not that comparison. Definitions and quantitative prolate bounds: [Karnik–Romberg–Davenport, 2020, §2.2 and Theorem 3](https://arxiv.org/pdf/2006.00427v2).

The classical Landau–Widom transition, as stated by [Slepian, 1983, p. 387, equation (25)](https://www.math.ucdavis.edu/~saito/data/ONR15/slepian83.pdf), is

\[
 \nu_{\lfloor2c/\pi+(b/\pi)\log c\rfloor}(c)
 \longrightarrow (1+e^{\pi b})^{-1},\qquad c\to\infty,
\]

for **fixed b**. It concerns indices within O(log c) of the transition, not an arbitrary lowest eigenvalue of another operator. Substituting an index displacement of order c sends b to infinity; the displayed limit is not uniform permission to do so. Thus the proposed derivation fails at both the operator identification and the asymptotic regime.

The decisive preprint scope is recorded once in the prior-art table below: its profile law is conjectural. To examine the proposed model without using zero ordinates, replace its count by the smooth leading expression u(L) = (2L−1)e^(2L). Pure differentiation of H(L) = C u/log u gives

\[
 H'(L)=4CL e^{2L}\frac{\log u-1}{(\log u)^2}
 \sim 2C e^{2L}.
\]

This is a derivative of a **model**, not an asymptotic theorem for W. It predicts a changing slope, not a universal 64. It is not even a usable small-L formula when u ≤ 0, which includes part of D12's fit range. Local exponential fits can summarize a curved function without identifying its asymptotic law.

There are also three different frequency scales:

| Scale | Meaning |
|---|---|
| T in the code | Chosen numerical cutoff, varying with the protocol |
| Tenv ≈ 2π exp(BL) | Cost of the crude symbol envelope; BL ∼ 4e^L by partial summation of the prime number theorem |
| T* = 2πe^(2L) | Resolution scale in the proposed asymptotic model, not the code's cutoff |

D12's saved metadata use T = 60, then 77.4, then 154.8 along the fitted range, while changing the number of modes. This is not evidence that the decay is entirely an artifact; it is evidence that a cutoff-independent profile has not yet been established by that scan. The original D12 assembly script and D15 grid script were not found in their listed directories, so exact regeneration of those particular tables remains incomplete.

The Dirichlet rates 24–36 were fitted on a different support range. Also log(q)I is **not** ζ's pole: one is scalar in all directions; the other is rank one with opposite signs in the two sectors. The gamma factor changes too. Their qualitative similarity does not justify the claim that the pole is a conductor substitute or that a universal quantitative law was measured.

**Answer to Q2:** no derivation of 64.1, 57.4, or 24–36 has survived this review. The proposed direct Landau–Widom derivation is **VOID**; an appropriately proved comparison remains **UNVERIFIED**.

## 4. Q3 — what the mirrors really explain

### The exact exponent response

For real parity f, let Cₙ(f) = Re⟨f,Tlog n f⟩ with zero extension. Write bₙ = 2Λ(n)/√n and δ = σ − 1/2. At fixed L the stipulated arithmetic mutation is exactly

\[
 W_\delta(f)=W_0(f)-\sum_n\chi(n)b_n
 (e^{-\delta\log n}-1)C_n(f).
\]

Hence ∂σWσ(f) = Σₙ 2Λ(n)χ(n)n^(−σ) log n Cₙ(f). For a simple ground state the derivative of its minimum is this expression on that state, with the usual eigenvector-coupling term in the second derivative. It is not determined by character parity or the pole sign alone. The pole has no direct σ derivative in this artificial family.

For R, even at fixed T there is an extra β′ times the Fourier tail mass; adaptive T introduces boundary terms, and adaptive N changes the space. These effects must be bounded before identifying D19b's secants with the displayed full-W susceptibility.

### A finite positive window has an open interval, not a single permitted exponent

Since |Cₙ(f)| ≤ ‖f‖²,

\[
 |W_\delta(f)-W_0(f)|\le D_L(\delta)\|f\|^2,
 \quad D_L(\delta)=\sum_n|\chi(n)|b_n|e^{-\delta\log n}-1|\to0.
\]

If W₀ ≥ mI with m > 0, both parities remain positive whenever DL(δ) < m. This conclusion applies to the full form, conditional on the recorded certificate. It is incompatible with literal exact rigidity at a fixed certified window. D17 found a unique **sampled grid point**, while D19 explicitly found nonzero bands.

The functional equation identifies the authentic symmetry point. Changing just the prime exponent while keeping gamma, conductor, and pole terms fixed is not moving an L-function's critical line. Nor does it supply an even/odd interchange identity. See the [Dirichlet functional equation, DLMF 25.15.5](https://dlmf.nist.gov/25.15.E5).

### Boundary reflection gives a real, limited parity mechanism

Let f(−x) = εf(x), ε = +1 or −1, and let a = 2L − h. Direct substitution gives

\[
 C_a(f)=\varepsilon\int_0^h f(L-u)f(L-h+u)\,du.
\]

If a frozen smooth endpoint profile has f(L−u) = c u^r + O(u^(r+1)), c ≠ 0, then

\[
 C_{2L-h}(f)=\varepsilon c^2
 \mathrm B(r+1,r+1)h^{2r+1}+O(h^{2r+2}).
\]

Removing one arithmetic term adds χ(n)bₙCₙ. Consequently, under those hypotheses, positive χ(n) hurts the odd wave near entry; negative χ(n) hurts the even wave. This is the mathematically sound piece of the mirror picture: the overlapping endpoint copies have equal or opposite signs.

The limitations are substantive. The overlap is ⟨g,Jhg⟩, where Jhg(u) = g(h−u). Reflection has both positive and negative eigenspaces. An oscillatory endpoint layer can reverse the sign; parity alone does not give an all-vector inequality. The expansion is for a fixed regular profile, not a theorem about reoptimized ground states as L changes. Character parity χ(−1) also differs from an individual χ(n): the even character χ₅ has χ₅(2) = −1. D19's two examples do not establish a universal reversal for odd characters.

### Prime powers are exact echoes of one shift—but with the wrong sign for an automatic proof

This is a useful algebraic translation of the user's intuition, with no physical identification. On L²[−L,L], define Sₚf(x) = f(x−log p) when the argument lies in the interval, and zero otherwise. Then Sₚ^k = Tk log p and Sₚ^k = 0 once k log p ≥ 2L, almost everywhere. Put zₚ = χ(p)/√p, real in the families tested, and Rₚ = (I−zₚSₚ)^(−1). The geometric series terminates on this window.

The entire prime-power block is

\[
 P_p=\log p\sum_{k\ge1}z_p^k(S_p^k+(S_p^*)^k)
 =\log p\,(K_p-I),
\]

\[
 K_p=R_p^*(I-z_p^2S_p^*S_p)R_p
 =R_p+R_p^*-I\succeq0.
\]

Proof: write B = I−zₚSₚ, expand B + B* − B*B = I−zₚ²Sₚ*Sₚ, and conjugate by B^(−1). Positivity follows from ‖Sₚ‖ ≤ 1 and |zₚ| < 1. No arithmetic conjecture enters. This is the elementary operator Poisson/Cayley identity; no priority claim is made.

It identifies a legitimate role for **I, the identity**, rather than treating 1 as a prime. However,

\[
 W=A+\Pi+\sum_{p<e^{2L}}\log p\,I
       -\sum_{p<e^{2L}}\log p\,K_p.
\]

**The positive echo kernels are subtracted.** The unresolved task is an upper domination of their joint sum by the archimedean-plus-pole side, uniformly in L. Treating the kernels independently loses precisely the dependence the lab needs. This is a repackaging with a transparent obstruction, not a new solution or another argument that information preservation forces real zeros.

### The correct all-window specification

Define exact parity minima mε(L,δ) on the form domain. An RH route must show mε(L,0) ≥ 0 for both ε and every L. To additionally prove asymptotic uniqueness under the chosen mutation, it would need, for each δ ≠ 0, a window and a normalized test function with Wδ(f) < 0. Neither quantifier follows from D19.

A legitimate load-bearing statement is a certified frozen-wave inequality W₀(f) + τV(f) < 0 for the actual removal V, not negativity of an adaptive lower approximation. An immediate-entry law would further require uniform control of endpoint overlap relative to the true margin. Nothing in the available parity symmetry supplies that control. The proposed specification must permit small finite-window slack; otherwise it contradicts continuity before reaching any open problem.

## 5. Q4 — prior art, with hypotheses left attached

The table distinguishes an established publication from a theorem **claimed in a preprint**. Source inspection is not a full proof or software audit. Zhu is pinned to v2; the arXiv record discloses an author/affiliation change from v1. Original Yoshida and Li full texts were not obtained in this review; the stated access limits matter.

| Source | Exact relevant statement/location | What it settles here |
|---|---|---|
| Yoshida, 1992, *On Hermitian forms attached to zeta functions*, Theorem 1, as reproduced by [Connes–Consani, p. 2](https://alainconnes.org/wp-content/uploads/Selecta.pdf) | Archimedean positivity for smooth positive-definite multiplicative tests supported in (1/2,2), with transform vanishing at ±i/2. Original chapter not independently read. | Small-support positivity predates this lab; preserve its moment hypotheses. |
| Connes–Consani, 2021, *Weil positivity and trace formula, the archimedean place*, [Theorem 1, p. 2](https://alainconnes.org/wp-content/uploads/Selecta.pdf) | For smooth g supported in [2^(−1/2),2^(1/2)] with ĝ(i/2) = ĝ(0) = 0, W∞(g*g*) ≥ Tr(ϑ(g)Sϑ(g)*), a nonnegative trace. | A conceptual positive-trace comparison exists, with restricted support and hypotheses; not an arbitrary prime-containing-window theorem. |
| Bombieri, 2000, *Remarks on Weil's quadratic functional in the theory of prime numbers, I*, [Theorems 3 and 5, pp. 197, 199](https://www.bdim.eu/item?fmt=pdf&id=RLIN_2000_9_11_3_183_0) | The normalized minimum on a finite union of compact multiplicative intervals is attained; the parity minima are continuous and nonincreasing with window size. | The variational object and parity profiles already existed. His p. 225 also discusses parity splitting, Riemann–Hilbert analysis, and off-line-zero experiments. |
| Bombieri, same paper, Theorem 12, p. 226 | For additive support length a < log 2, lower bound [log(1/a) − log⁺log(1/a) − O(1)]‖F‖². | Positivity for sufficiently small a; the unspecified constant alone does not certify every a < log 2. |
| Zhu, 2026, [arXiv:2608.24827v2](https://arxiv.org/html/2608.24827v2), Theorem 1.2, Corollary 6.3, Theorem 6.2 | Claims W ≥ 8.9e−18‖f‖² at L = 0.8 for complex tests, and a simple even ground state there. | The smaller lab window is not a new certified range. External certificate not replayed here. |
| Zhu, same v2, Conjecture 12.1, Remark 12.2, Theorems 1.3–1.4 | The profile constant 2π² is “fitted, not derived.” Under RH, a weaker eventual upper bound exp(−Le^L) is proved. The double-exponential cost barrier concerns the specified pointwise-envelope reduction. Upper-bound candidates use zero data before geometric certification (§11). | No theorem deriving 64, no general complexity lower bound. Valid geometric upper certificates need not meet this lab's stricter zero-free-selection rule. |
| Li, 1997, *The positivity of a sequence of numbers and the Riemann hypothesis*, [publisher record](https://www.sciencedirect.com/science/article/pii/S0022314X97921375); recalled in [Li's 2004 paper](https://arxiv.org/pdf/math/0403148) | RH iff every Li coefficient is nonnegative. The original full 1997 proof was not retrieved. | Sequence positivity does not remove the universal quantifier; finitely many positive coefficients do not suffice. |
| Rodgers–Tao, preprint 2018, published 2020, [Theorem 1](https://arxiv.org/abs/1801.05914) | Λ ≥ 0 for the de Bruijn–Newman heat deformation; RH is equivalent to Λ ≤ 0. | This theorem concerns a particular deformation, not arbitrary arithmetic-weight perturbations or every finite window. |

The local fits, specified deletion protocols, and susceptibility curves may be useful diagnostic records. **Novelty of those particular observations remains UNVERIFIED.** A bounded literature search does not establish priority. Neither a new all-window inequality nor a new RH mechanism has been demonstrated.

## 6. Claim and prediction ledger

“MEASURED (audit)” here means confirmed in the saved code, report, or source; it does not turn floating evidence into an interval theorem. Exact deductions above are accompanied by their assumptions and proofs.

| Claim | Status after D20 | Reason/action |
|---|---|---|
| D6/D7's advertised L = 0.7 constants survive | MEASURED — recorded certificate | No new defect found in this review; not replayed here |
| Every knob has margin-sized play by Weyl | VOID as a deduction | Safe-ball bound has been reversed; counterexamples above |
| Later negative R minima establish negative W | VOID as an inference | Restore/certify the positive tail; no blanket claim that the exact signs are positive either |
| D12–D19 are a cutoff-independent exact minimum profile | UNVERIFIED | Reduced forms, finite spaces, adaptive cutoffs, and floating arithmetic differ |
| Landau–Widom derives 64 | VOID as the proposed derivation | Wrong operator and limit regime; the related preprint's law is conjectural |
| Fixed-window positivity uniquely selects σ = 1/2 | VOID literally | Strict positivity permits an open interval; sampled-grid uniqueness is narrower |
| D19's joint allowed band narrows on its saved grid | MEASURED — floating | True of the implemented threshold search; no all-L limit or exact-W certification |
| D19b's response does not collapse on its secant grid | MEASURED — floating | Local derivative and margin/derivative edge formula remain UNVERIFIED |
| Parity universally fixes each correlation sign | VOID | Reflection on the endpoint layer is indefinite |
| Fixed regular endpoint profiles explain entry signs | MEASURED — exact audit derivation | Beta-integral expansion above; not a theorem for changing minimizers |
| Exact prime-power echo identity proves W ≥ 0 | VOID | It packages kernels that W subtracts |
| Particular deformation mechanism is new | UNVERIFIED | Known framework; no priority claim established |

Further reporting repairs to carry into Fable's next ledger:

1. **D19 midpoint prediction changed its window in the readout.** The preregistration asked for an offset exceeding 10% of width at L = 0.30. That row is censored by the search range, not a resolved success. The observed offset at L = 0.40 does not rescue the original prediction. Mark the L = 0.30 claim UNVERIFIED under that protocol.
2. **D19b's numerical range was not wholly met.** Its predicted magnitude interval 0.01–0.5 excludes the reported ζ-even 0.0023; its “within one order” bound also misses the rise to 0.032. The qualitative no-collapse prediction survives. Preserve the narrower failed numerical predictions.
3. **D19 edge resolution is finite.** The search has initial half-interval length 0.2 and 22 bisections: resolution about 4.77e−8. The inferred even edge at L = 0.60 is only about 2.35e−8 from 1/2. A printed 0.5000000 is not an exact endpoint. The nonlinear σ search assumes a single crossing; it does not certify absence of other positive components.
4. **D14's norm-compression count is not energy compression.** A retained coefficient mass 1−1e−12 permits a vector-norm error of order 1e−6. Without a form-norm/residual estimate it does not preserve a 1e−13 energy cancellation. The “13 dimensions” should not be promoted to a complete low-complexity positivity certificate; D11's short-Krylov failure already cautions against that jump.
5. **D14's fractional Euler factor needs a different interpretation.** A noninteger power of 1−2^(−s) has branch points at that factor's zeros, not ordinary zeros with integer multiplicity of a meromorphic L-function. Its logarithmic derivative can still support a separately derived contour identity with fractional residues. Importing the standard completed-L zero-sum and symmetry without that derivation is UNVERIFIED. D14's original peak test stays VOID.

These corrections are recorded here rather than silently editing Fable's files. They change the account of what was established, not the saved measurements.

## 7. Q5 — three next tests, and no fourth scan

The complete preregistration is [PREDICTIONS.md](PREDICTIONS.md). None has run in D20.

| Order | Test | What could change our belief |
|---|---|---|
| 1 | Exact-W witness audit, starting with the conflicting deletion of 4 | Whether “load-bearing” describes W or just the lower-bound implementation |
| 2 | Cutoff-independent two-sided window profile | Whether the measured decay is intrinsic, and whether a constant slope survives controlled refinement |
| 3 | First-order-balanced arithmetic perturbations, with matched controls | Whether there is unusually weak joint coupling invisible to separate knob/sign scans |

The third test is about the **size and structure of curvature**, not the generic fact that a concave eigenvalue branch bends downward or has a square-root threshold. The latter are already predictable and are not success criteria. Do not do another unconstrained prime deletion, fit another exponential to near-machine-zero values, or invoke a fresh physical metaphor as a control.

For Fable: run Test 1 first, in a new directory, using the committed predictions. Save exact frozen vectors, complete score enclosures, and the witness checker. Mark each result W-negative, R-negative-only, or unresolved. Stop after Test 1 if the model-identification step fails; do not run a decay fit over unresolved quantities. Keep all failed predictions, update one hub row, commit and fast-forward push the research branch. Tests 2–3 are conditional follow-ons, not permission for indefinite larger-window computation.

## 8. What the human intuition contributed, and the honest paragraph

The mirror image led to an exact endpoint-reflection formula; the echo image led to a clean prime-power resolvent identity. The earlier nested-gears idea corresponds to finite modular synchronization, and [D18](../fable_d18_observer_tomography/RESULTS.md) gives a separate finite tomography result about recovering a ternary array. That last result can inform memory/encoding design, but reconstruction is not authentication: it still needs an independent trusted reference or cryptographic verification. None of these observations establishes a mathematical hologram, a physical identification of ζ, or a role for 1 as a prime. The persistent record is this repository; it is not a change to model weights.

**In plain words:** we have checked that a particular small room passes a very delicate wave test. Some later experiments changed both the waves and the ruler used to score them, so we must separate those effects before trusting their story. Your mirrors help explain why opposite kinds of waves can react differently, and your echoes have an exact mathematical translation—but neither yet explains why every possible room must pass. The next useful move is to test the same waves with a fully checked ruler, then look for a rule that preserves the whole balance. We have sharper questions and an auditable finite result, not a Riemann breakthrough.
