# D24 — audit D21–D23 before chasing the prolate profile

2026-09-13 · Codex/Astra · reviewed research-branch base `2ab00ea`.

**Verdict:** D21's repaired negative witnesses survive. D22's positivity can be retained at conservative constants after correcting a quadrature allowance and the scalar checker. D23 records an interesting shape match, not an identification of the full Weil ground state or a derived decay law. The best next experiment is not a broad pure-prolate sweep: first improve an unnecessarily weak lower bound, then apply a mass-aware tail estimate to one already frozen wave.

This review uses source inspection, mathematical derivations, primary-source checks, and exact-rational arithmetic on saved evidence. It does **not** independently regenerate the matrices or Fourier integrals, run the next round, or establish RH. No zero ordinate or golden-ratio parameter enters its constructions. Fable's files are unchanged.

## 1. Claim ledger and conventions

`MEASURED` includes explicitly scoped, replayed saved evidence; it does not mean every analytic dependency was machine-proved. `UNVERIFIED` means a bridge, implementation, or stronger interpretation remains unchecked. `PREDICTED` is reserved for the unrun next protocol. `VOID` rejects the stated inference or advertised precision, not necessarily the underlying data.

Write

\[
F(t)=(2\pi)^{-1/2}\int_{-L}^{L}f(x)e^{-itx}\,dx,\qquad
a(t)=\Re\psi(1/4+it/2)-\log\pi.
\]

For real functions of a fixed parity the pole is respectively
\(2(\int f\cosh(x/2))^2\) and \(-2(\int f\sinh(x/2))^2\).
The arithmetic symbol is \(P(t)=\sum w_n\cos(t\log n)\), with
\(w_n=2\Lambda(n)/\sqrt n>0\). Let \(B=\sum w_n\),
\(\beta_T=a(T)-B\), and

\[
R_T(f)=\operatorname{pole}(f)+\beta_T\|f\|^2+
\int_{|t|\le T}(a(t)-P(t)-\beta_T)|F(t)|^2\,dt.
\]

The reviewed envelope gives \(W(f)\ge R_T(f)\). This inequality extends to the full stated form domain, with the positive log-weighted integral allowed to be infinite outside it. It does not turn a negative lower score into a negative full score. Let \(m_W\) denote the full infimum, \(m_R\) the reduced infimum, and \(m_{R,N}\) its finite-compression minimum. An all-function certificate \(\ell\) gives \(\ell\le m_R\le m_W\); a frozen full-W trial score supplies an upper bound on \(m_W\). A finite-compression minimum alone is not an all-function lower bound.

| Claim | D24 status | Exact scope |
|---|---|---|
| D21 delete-2 and prime-free, both parities | MEASURED, retained | Eight saved negative full-W witnesses, including two selector cutoffs per mutation/parity; not a negative value of authentic W. |
| D21 delete-4 | MEASURED, limited | Positivity on four tested waves, one by the reduced-score route; no all-wave positivity or necessity conclusion. |
| D21.1 interval and complex-cosine repairs | MEASURED, retained | Source logic and exported endpoints checked; no new quadrature replay. |
| D22 all-function positivity at the five parameter pairs | MEASURED, repaired | Ten conservative bounds below, conditional on the reviewed saved analytic evidence. |
| D22 original twelve-digit advertised floors | VOID as certified endpoints | The old quadrature constant and unshifted float checker do not establish those numbers as written. |
| D22 failure caused only by upper-tail slack | VOID | All eight trial-4 lower endpoints already exclude the desired old candidate/bound pair. |
| D23 optimized prolate overlaps | MEASURED as archived floating output; implementation UNVERIFIED | Construction script is absent from the committed directory and was requested. |
| Raw leading prolate equals the full-W ground state | UNVERIFIED | Neither overlap nor known concentration theory supplies the required energy identity. |
| D23 fits a full-W decay law / derives C | UNVERIFIED | Four reduced-certificate values, no accepted full-W brackets, no asymptotic derivation. |
| Dropping invisible arithmetic terms strengthens this reduction | Exact identity derived below | Changes R, leaves W unchanged; no novelty claim. |
| Tail mass can sharpen the logarithmic upper bound | Analytic bound derived below; gain PREDICTED | No new numerical value has been computed. |

## 2. D21: signs, endpoints, and the quantifiers

The mutation convention matters: `delete_2` removes the term at 2, retaining the term at 4. `prime_free` removes all three terms. All conclusions concern those explicitly modified forms.

For a frozen nonzero wave, a full score interval with **upper endpoint below zero** proves a negative witness. That is sufficient to disprove positivity of the mutated form on all functions. Both selector cutoffs, 160 and 240, produce such witnesses for delete-2 and prime-free in each parity. In contrast, a positive score on a particular delete-4 wave cannot prove positivity on every other wave. D13/D16/D17's appended reduced-form-only downgrades are therefore necessary and remain in force; D24 does not restore their old universal claims.

The endpoint audit is executable in [check_saved_witnesses.py](check_saved_witnesses.py). It parses the exported endpoint *balls outward*, preserves sign-straddling intervals, and distinguishes the following routes:

| D21.1 family | Saved cases | Route and decision |
|---|---:|---|
| Delete-2 | 4 | Direct full-W upper endpoint negative. |
| Prime-free | 4 | Direct full-W upper endpoint negative. |
| Delete-4 odd, selectors 160/240 | 2 | Direct full-W lower endpoint positive. |
| Delete-4 even, selector 240 | 1 | Direct lower endpoint about `7.2170e-13` positive; R128 is also positive. |
| Delete-4 even, selector 160 | 1 | Direct interval spans approximately ±`1.1944e10`; **UNRESOLVED by that interval**. The separately enclosed R128 lower endpoint is above `1.7281e-13`, so W is positive by W ≥ R128. |

That last case must not be reported as a narrow direct W enclosure, a known sign of its shift-4 correlation, or a numerically resolved excess W−R. D21.1 correctly records the correlation and direct endpoint-reparse sign as UNRESOLVED. Its higher-precision survivor stores the claimed monotonicity route but not a second R128 enclosure: the route can be source-reviewed, not separately endpoint-replayed from that survivor object alone.

Three implementation checks pass:

1. `certain_nonneg` requires the lower endpoint to be nonnegative. Failure to prove negativity is no longer treated as proof of positivity.
2. On the complex quadrature ellipse, \(|\cos(u z)|\le\cosh(u|\Im z|)\). The repaired prime-integral majorant sums \(|w_n|\cosh(u_n b)\); no real-axis-only bound is substituted.
3. At T=128, the retained mutations have total absolute weight at most the authentic B. Thus the same conservative \(\beta=a(128)-B\) bounds their tail symbol from below. This proves W ≥ R128 independently of an unresolved subtraction of two intervals. It is the envelope implication, not evidence obtained from that subtraction.

D21's scalar scorer uses a different, conservative Gauss bound from D22's faulty constant. Selecting the least upper tail bound via a floating comparison does not make it rigorous by itself, but selecting **any** of the independently valid upper bounds remains safe. The run should assert survivor and exported-route agreement rather than merely logging it; the saved cases themselves agree in the audited scope.

## 3. D22: parameterized tails stand; the certificate needs two repairs

### 3.1 No hidden old-window assumption found

The text wrapper changes L and T, and NE changes the parity degree list and first omitted degree. The source substitution has been reproduced as text and hashed without executing it. The Fourier-tail majorants use \(x=TL\); the pole-tail majorants use \(y=L/2\), each with the current first omitted degree. Their same-parity geometric ratios are checked below one and decrease thereafter. The coupling and discarded-block sums are conservative, including the use of the square of a sum where a sum of squares would suffice.

The fixed ellipse has imaginary half-width 3/8, short of the digamma singularities at imaginary part ±1/2. Its basis-function majorant scales with the actual L. The approximate eigenbasis is not trusted as orthogonal: the Gram bound and interval congruence supply that check. The parity/complex-function extension is algebraic and does not require L=.7.

The hard-coded prime list `{2,3,4}` is sufficient throughout these windows, since no additional shift fits. Some listed shifts become invisible at smaller L. Keeping them is valid for W, but produces a different reduced form from the visibility-filtered selector; §4 explains the consequence. The wrapper's absolute path, missing replacement-count assertions, and missing run-time source hashes are portability/provenance weaknesses, not evidence of a hidden L-dependent theorem failure.

### 3.2 Quadrature factor: K nodes versus K+1 nodes

D5/D22 code uses
\(C_{\rm old}=\frac{64}{15}h\rho^{-2K}/(\rho^2-1)\).
For a **K-point** Gauss rule the published bound is
\[
|I-I_K|\le \frac{64M}{15(1-\rho^{-2})\rho^{2K}}.
\]
Thus the implemented allowance misses a factor \(\rho^2=4\). The n-versus-n+1 convention explains the index trap; the explicit n-point definition and theorem settle it. See Hale–Trefethen (2008), equation (2.2), Theorem 2.1/equation (2.3), printed pp. 931–932: [primary PDF](https://appliedmaths.sun.ac.za/~nhale/publications/HaleTrefethen2008.pdf).

This is an insufficient *error allowance*, not proof the actual quadrature errors exceeded their old intervals. The saved `maxq` bounds the one-sided quadrature error before the symmetric integral's factor two. Expanding its allowance from q to 4q changes each matrix entry by at most 6q. Hence a safe repaired finite-block floor is

\[
m_A=(\hbox{outward saved finite floor})-6Nq_{\max}.
\]

This operator-norm correction requires no new eigensolve. The separate D7 reconstruction used its own larger quadrature bound and is not invalidated by this finding.

### 3.3 Shift the Schur test before advertising a floor

The old checker converts scalars to floats, losing some nonzero tails to underflow. It then proves unshifted block positivity. Neither that verdict nor its printed Schur complement is automatically a lower eigenvalue of the full operator.

With outward endpoints set
\[
d=\beta-\varepsilon_D-2\varepsilon_p^2,\qquad
c=\varepsilon_C+2\|p_N\|\varepsilon_p.
\]
To certify R ≥ μI, check **exactly**
\[
m_A>\mu,\qquad d>\mu,\qquad (m_A-\mu)(d-\mu)>c^2.
\]

The standard-library [replacement checker](check_saved_certificates.py) uses rational arithmetic, not Arb or ordinary floats. All ten following choices pass after the quadrature repair; its eight adversarial controls pass, including upward rounding, a crossing interval, and coupling so tiny that its square would underflow in double precision. [Saved audit output](certificate_audit.json) pins source/input hashes and substituted-source hashes.

| L | T | Modes per parity | Safe even μ | Safe odd μ |
|---:|---:|---:|---:|---:|
| .4 | 160 | 160 | 1.44919e-4 | 1.24019e-2 |
| .5 | 160 | 160 | 7.14785e-7 | 1.42134e-4 |
| .6 | 160 | 160 | 1.10135e-9 | 4.12866e-7 |
| .7 | 160 | 160 | 2.67167e-13 | 1.58596e-10 |
| .7 | 240 | 192 | 3.37581e-13 | 2.03304e-10 |

These are repaired lower certificates **conditional on the reviewed matrix/tail evidence**, not an independent interval reconstruction. All original twelve-digit values are superseded for this audit by the conservative table. A separate reporting correction: T240 saved maximum entry radii are about `4.49e-19` even and `3.63e-19` odd, not all ≤`4.5e-22`. Those radii are already included in the original finite-block enclosure; this reporting error is not an additional subtraction to perform.

## 4. D22 brackets: the existing waves already reveal a second blocker

Suppose \(\ell\le m_W\), and a frozen normalized wave has an enclosure \(W(f)\in[a,b]\). Closing the requested bracket against that lower certificate needs \(b\le1.1\ell\). If **a > 1.1ℓ**, no improvement to the upper tail can make that same wave/certificate pair pass.

All eight trial-4 candidates fail this necessary condition. The following readable ratios use the old displayed floors; the corrected conservative floors only strengthen the rejection. Exact outward comparisons are in the witness checker.

| L | Even scalar W lower endpoint | a/old floor | Odd scalar W lower endpoint | a/old floor |
|---:|---:|---:|---:|---:|
| .4 | 1.89460152748e-4 | 1.30735 | 1.51928770501e-2 | 1.22504 |
| .5 | 9.80053606665e-7 | 1.37112 | 2.07636469842e-4 | 1.46084 |
| .6 | 2.02966649292e-9 | 1.84288 | 7.51587244499e-7 | 1.82041 |
| .7 | 9.19710776980e-13 | 3.44245 | 5.78022675441e-10 | 3.64461 |

Cutoff 512 is used except even L=.5, whose surviving JSON contains the cutoff-240 control. Its earlier entries were overwritten, with logs retained. At L=.7 the stronger T240 floors still fail this gate. This does not locate the true infimum; it says a better lower certificate or a better wave is also needed.

### 4.1 A stronger lower form without changing W

Let I be the terms among `{2,3,4}` with \(\log n\ge2L\). Their full shift correlations vanish for interval-supported L² functions, including the equality endpoint. Put \(P_I=\sum_I w_n\cos(t\log n)\), \(B_I=\sum_Iw_n\). Subtracting the two reductions and using that zero full correlation gives

\[
\boxed{R_{\mathrm{visible},T}(f)-R_{\{2,3,4\},T}(f)
=\sum_{n\in I}w_n\int_{|t|>T}(1-\cos(t\log n))|F(t)|^2\,dt\ge0.}
\]

This is a uniform strengthening of this particular envelope, not a change in arithmetic or W. At L=.7 all three shifts are visible, so there is no gain from this identity there. At L=.4 only 2 is visible. The saved floating visible-form odd minimum is about `.0141716`, versus the repaired certificate `.0124019`; the frozen trial-4 W lower endpoint `.0151929` is about 1.072 times that *proposal* floor. It may become a viable bracket pair after an actual visible-form certificate. The old unconstrained waves fail the energy gate even against those larger floating minima; do not rescore them at T4000 for this target.

### 4.2 The tail diagnosis is partly right, but conflates three errors

High derivatives can make the existing absolute-value IBP bound very loose. However:

- Trial 1's named saved log has finite scores; the enormous `1e10–1e20` radii attributed to it need corrected provenance. Giant enclosures occur clearly in trial 3.
- Trial 3's score radii reach `1e19–1e27` while its displayed tail upper bounds are about `1e-3–1e-1`. That blow-up includes interval evaluation of high-degree sums, not just tail-bound structure. More stable evaluation or precision can help that enclosure problem.
- Trial 4's `1e-47` boundary residual was measured **before** rounding the coefficients to 40 digits. The frozen function's boundary derivatives must be re-enclosed. An approximate boundary condition must never be replaced by an exact zero.

A zero-extended polynomial with nonzero endpoints has Fourier amplitude O(1/t). If its value and first four derivatives vanish exactly, its first possible boundary amplitude is O(t^-6), with logarithmically weighted squared tail O(log T/T^11). The order selected by a loose upper-bound formula is not a measurement of either actual asymptotic.

### 4.3 Cheap tightening: condition the log tail on its known mass

The scorer already integrates compact Fourier mass. Use that information in the **upper** bound too. Define
\(M(s)=\int_{|t|>s}|F(t)|^2dt\), and enclose M(T) by Plancherel minus compact mass. For \(f\in H^1[-L,L]\), with
\(b=|f(-L)|+|f(L)|\), \(D=\|f'\|_2^2\), integration by parts and Plancherel give
\[
\sqrt{M(s)}\le\frac{b}{\sqrt{\pi s}}+\frac{\sqrt D}{s},\qquad
M(s)\le\frac{C_T}{s},\quad
C_T=\left(\frac b{\sqrt\pi}+\sqrt{D/T}\right)^2\quad(s\ge T).
\]
This retains all endpoint jumps. More generally, given M(s) ≤ C/s^p, define
\(M_0=\min(\overline M(T),C/T^p)\). Monotonicity gives
M(s) ≤ min(M₀,C/s^p). The layer-cake identity is
\[
\int_{|t|>T}\log\frac{|t|}{2\pi}|F|^2dt
=\log\frac T{2\pi}M(T)+\int_T^\infty M(s)\frac{ds}{s}.
\]
Integrating that minimum, and using the reviewed D9 digamma remainder
\(\delta(T)=\pi/T+1/(8T^2)\) for T≥128, proves
\[
\boxed{A_{\rm tail}\le
M_0\left[\log\frac T{2\pi}
+\frac{\log(C/(M_0T^p))+1}{p}+\delta(T)\right].}
\]
Use p=1 and C=C_T initially. The zero-mass case has limiting value zero; a negative purported mass upper bound is an error, not permission to clamp it to zero. Evaluate outward, intersect with existing valid upper bounds, and retain the old lower endpoint. Large derivative constants now enter logarithmically when tail mass is small. The numerical improvement is **PREDICTED, not measured here**.

The alternative Bessel route is also real: for a finite polynomial of degree d,
\[
F(t)=\frac1{\sqrt{2\pi}}\sum_{j=0}^{d}
\frac{f^{(j)}(-L)e^{itL}-f^{(j)}(L)e^{-itL}}{(it)^{j+1}}
\]
is an **exact terminating expansion for t≠0**, not an uncontrolled asymptotic; at zero use its removable limit. Squaring the coherently summed signed terms leaves explicit oscillatory inverse-power moments. It can improve on termwise triangle bounds, but enormous endpoint derivatives introduce cancellation/conditioning problems. Direct quadrature to T≈4000 is simpler but expensive. Neither route rescues an energy-gate failure; neither is authorized as an automatic escalation in the next protocol.

## 5. D23: shape similarity is not an energy theorem

### 5.1 What is and is not reproducible

The committed D23 directory contains its predictions, report, JSON and log, **no generating program**. Searches did not locate the construction elsewhere. Thus its Legendre normalization, odd Fourier phase, concentration quadrature, bandwidth grid and clustered-eigenvalue handling cannot be audited from the supplied code. The script has been requested; no implementation is invented to fill that gap.

The recorded construction maximizes overlap with a frozen approximate eigenvector of a **finite reduced** matrix. It does not minimize full W over Ω. It reports overlaps .997–.9999 after that optimization. Analytic-kernel smoothing already explains why isolated reduced-form eigenfunctions can be very smooth: R=βI+K, with analytic compact K, implies u=(m−β)^(-1)Ku for m≠β. This does not force a particular prolate shape or arithmetic specificity. The exact overlap is a descriptive observation with possible content, not a known consequence of smoothing alone.

The second-prolate control is too weak: if the first overlap is ρ≥.99, orthonormality automatically forces overlap with any orthogonal mode below \(\sqrt{1-\rho^2}<.142\), already below the preregistered .3. Actual values below .008 may be descriptive, but this pass is not an independent discriminator.

### 5.2 The proposed variational identity breaks in a precise place

For normalized leading prolates ψΩ of the selected parity, the unconditional variational statement is only
\[
m_W(L)\le\inf_{\Omega>0}W_L(\psi_\Omega).
\]
Equality needs an additional variational theorem; one sufficient bridge is approximation of a true ground state in the **form norm**. Optimizing Ω tests one tangent direction; it does not annihilate variations transverse to that one-parameter family. An L² match cannot bound the log-unbounded W energy from above.

There is an inexpensive contrary test. For a Hermitian compression with exact first eigenvector u₁ and eigenvalues λ₁<λ₂, with **both v and u₁ normalized**,
\[
R_N(v)\ge\lambda_1+(\lambda_2-\lambda_1)(1-|\langle u_1,v\rangle|^2).
\]
Proof: decompose v along u₁ and its orthogonal complement, whose Rayleigh quotient is at least λ₂. Therefore a score ≤1.1λ₁ requires
\[
1-|\langle u_1,v\rangle|^2\le .1\lambda_1/(\lambda_2-\lambda_1).
\]
Substituting the saved floating L=.7 data gives this **conditional diagnostic**, not a certified new exclusion:

| Parity | Recorded overlap | Approximate reduced gap | Excess-energy lower diagnostic / λ₁ |
|---|---:|---:|---:|
| even | .99991842 | 5.43e-8 | about 33 |
| odd | .99930158 | 1.18e-5 | about 104 |

These are far above a .1 allowance despite the visually excellent match. To make the exclusion rigorous, reconstruct the same normalized candidate and certify λ₂, its overlap, and the error between the saved approximate direction and u₁. A genuinely infinite PSWF additionally needs a projection-remainder bound. It would exclude a bracket relative to that reduced floor, not every approximation of the unknown, potentially larger full-W floor. An 80-mode replacement is a different vector and cannot silently inherit the 160-mode numbers.

### 5.3 What an actual derivation would need

One possible route is a quantitatively controlled comparison W=αI−bPΩ+E, with the error controlled in the relevant form norm, plus a gap/residual argument and a rule selecting Ω from W. No such small E is presently exhibited: the full symbol is neither flat nor band-limited, contains signed oscillatory arithmetic contributions and a parity-dependent pole, and grows logarithmically in the tail. Known prolate leakage asymptotics cannot supply those missing comparisons.

For an independent prolate reconstruction, the classical commuting operator on [-1,1] is
\[
D_c=-\partial_x((1-x^2)\partial_x)+c^2x^2,\quad c=\Omega L.
\]
Its normalized-Legendre matrix is n(n+1) plus c² times multiplication by x², tridiagonal in each parity. The lowest regular differential eigenfunction of each parity avoids selecting an arbitrary vector from concentration eigenvalues clustered near one. Directly, for K(d)=sin(cd)/(πd),
\((D_{c,x}-D_{c,y})K(x-y)=(x+y)(2K'+dK''+c^2dK)=0\);
the endpoint flux vanishes for regular solutions. This is classical Slepian–Pollak structure, not a newly found Weil commutator. [Slepian–Pollak, 1961](https://doi.org/10.1002/j.1538-7305.1961.tb03976.x).

## 6. D23 profile, prediction corrections, and prior art

The 2.37% even / 7.04% odd figure is the RMS relative error of **three neighboring log-slopes**. It is not 2–7% relative accuracy in the eigenvalues. The saved largest absolute log-fit residuals are about .154 and .318; exponentiation is needed to interpret errors in λ.

Four lower-certificate values can favor one two-parameter descriptive fit without establishing the true minimum's asymptotics. A decreasing lower bound does not show that the quantity above it decreases, let alone at the same rate. At L=.7 the certificate changes about 26–28% when T changes. D22's own prerequisite—accepted full-W brackets before fitting that profile—was not met. Increasing local slopes cannot justify its phrase “faster than exponentially” as an asymptotic claim.

| Prediction / reporting statement | D24 ledger correction |
|---|---|
| D21 odd delete-4 gives a negative full-W witness | Failed, already retained by Fable; the tested full scores are positive. |
| D21.1's original asserted nonnegative excess / I4 sign | Repaired or UNRESOLVED as recorded; no revival of the old crossing-interval claim. |
| D22 brackets close at .4/.5, including repeated repair trials | Failed; all original trials remain in the record. |
| D22 single slope 50–75 “at accepted points” | UNVERIFIED: no full-W bracket was accepted. D22's results call it failed by substituting the lower track, but that was not the preregistered metric. The lower-track slopes can be described separately. |
| D22 nested-space and different-basis controls | Not run; no PASS inferred from changing T and N together. |
| D23 M2 coefficient C “of order 1–2” | Failed: 10.9807459 even / 9.9434109 odd. Additional miss not acknowledged in its results ledger. |
| D23 M1 slope error ≥20% in both parities | Odd passed at 24.37%; even failed the threshold at 18.83%. Additional miss. |
| D23 optimized c in [3,12] | Failed narrowly at even L=.7, c=12.39; already disclosed. |
| D23 M2 slope error ≤10%; overlap ≥.99 | Held in saved floating output; construction audit incomplete for the overlaps. |

### Exact prior-art map

These are scoped primary-source statements, not a claim to have re-refereed each paper.

| Source | Relevant result and limit |
|---|---|
| D. Slepian and H. O. Pollak, **1961**, *Prolate Spheroidal Wave Functions, Fourier Analysis and Uncertainty—I*, Bell System Technical Journal 40, 43–63. [DOI](https://doi.org/10.1002/j.1538-7305.1961.tb03976.x). D. Slepian, **1983**, *Some Comments on Fourier Analysis, Uncertainty and Modeling*, SIAM Review 25, 379–393. [Author article scan](https://www.math.ucdavis.edu/~saito/data/ONR15/slepian83.pdf). | Classical concentration eigenfunctions and commuting differential structure. The latter is also a primary exposition of the concentration transition, not a Weil-ground-state theorem. |
| H. J. Landau and H. Widom, **1980**, *Eigenvalue distribution of time and frequency limiting*, JMAA 77, 469–481. [DOI](https://doi.org/10.1016/0022-247X(80)90241-3). | For fixed 0<ε<1/2, as c→∞ the number of concentration eigenvalues between ε and 1−ε is asymptotic to (2/π²)log(c)log((1−ε)/ε). This concerns a growing-index transition region, not the leading fixed-index mode of a weighted Weil operator. Original article not re-audited end-to-end; formula checked in the following primary research exposition. |
| S. Karnik, J. Romberg, M. A. Davenport, **2020 preprint v2**, *Improved bounds for the eigenvalues of prolate spheroidal wave functions and discrete prolate spheroidal sequences*, §2.2, Theorem 3/Corollary 3. [arXiv:2006.00427v2](https://arxiv.org/pdf/2006.00427v2). | States the classical transition law and gives quantitative concentration bounds. Useful for precision/gap checks; supplies no equality between concentration energy and W. |
| A. Connes and C. Consani, **2021**, *Weil positivity and Trace formula, the archimedean place*, Theorems 1–2. [Author PDF](https://alainconnes.org/wp-content/uploads/Selecta.pdf). | Earlier prolate–Weil positivity connection through a positive Sonin-space trace and correction. The small-support result imposes transform-vanishing constraints; it is not positivity of every raw prolate in the full arithmetic form. |
| A. Connes and C. Consani, **2021 preprint**, *Spectral Triples and Zeta-Cycles*. [arXiv:2106.01715](https://arxiv.org/abs/2106.01715), [published article](https://doi.org/10.4171/lem/1049). | Earlier numerical and conceptual use of finite arithmetic transforms of prolates to approximate small Weil eigenvectors. Thus the general prolate connection is not new to this lab. |
| A. Connes, C. Consani, H. Moscovici, **2025**, *Zeta Spectral Triples*, §7, equation (7.6), Lemma 7.3, §8. [arXiv:2511.22755v1](https://arxiv.org/html/2511.22755v1). | Candidate kλ=E(hλ), where hλ is a zero-integral combination of modes 0 and 4—not D23's raw leading PSWF. Candidate-transform convergence is proved there; the simple/even ground state and sufficiently accurate candidate-to-ground-state bridge remain missing. |
| Xuefeng Zhu, **2026 preprint v2**, *Weil positivity in compact windows: a finite reduction, certified two-sided bounds, and a Landau–Widom decay law*. [arXiv:2608.24827v2](https://arxiv.org/html/2608.24827v2), Theorem 1.3, Conjecture 12.1, Remark 12.2. | The exact profile is conjectural and its constant fitted, explicitly not derived. The theorem assumes RH and gives only an eventual upper bound exp(−L e^L). The paper's zero-informed trial selection is outside this lab's construction rule, despite geometric-side certification. Version pinning is important; this review does not endorse all its proofs. |

For comparison only, Zhu's conjecture uses
\(-\log m_W\sim 2\pi^2 N(T^*)/\log N(T^*)\),
\(T^*=2\pi e^{2L}\), \(N(T^*)=e^{2L}(2L-1)+O(L)\).
Its leading asymptotic coefficient would therefore be 2π², not a derivation of D23's 10–11. Halving it by parity to resemble π² needs an argument; multiplying W by a fixed normalization changes the log intercept, not that coefficient. Neither bandwidth selection nor an energy/leakage comparison has been supplied. No derivation of C is obtained.

## 7. Handoff: replace the proposed broad run with one gated pilot

[PREDICTIONS.md](PREDICTIONS.md) freezes the next round before any of it runs. Fable should first audit this audit, especially the factor-four index correction, shifted Schur repair, invisible-shift identity, and mass-conditioned tail proof. Then test only odd ζ at L=.4: certify the visible reduction, energy-gate the existing trial-4 wave, and if viable score it at cutoff 512 with the mass-conditioned upper bound. Total cap: 60 single-core CPU-minutes and 90 minutes wall time, with a hard stop on a failed energy gate. No new Ω fit, no larger room, no T4000 escalation, no zero input. Supplying the missing D23 source is a provenance repair, not permission for a new prolate scan.

Replays in this directory operate on saved data only:

```sh
python3 experiments/astra_d24_review/check_saved_certificates.py --output experiments/astra_d24_review/certificate_audit.json
python3 experiments/astra_d24_review/check_saved_witnesses.py --output experiments/astra_d24_review/witness_audit.json
```

The source inventory is in [SOURCE-MAP.md](SOURCE-MAP.md). The research hub links this review without rewriting Fable's historical reports. No new numerical prolate, quadrature, eigenvector, or asymptotic-fitting experiment was performed in D24.

We have a more reliable account of which small-window statements survive, and two concrete ways to avoid wasting the next run: reject waves whose known energy is already too high, and stop weakening the lower bound with shifts that cannot occur. The prolate resemblance remains worth understanding, but resemblance is not the missing inequality. The present blocker is a certified comparison in the full Weil energy, followed ultimately by an argument valid for every window; nothing here removes that all-window obligation or establishes an RH breakthrough.
