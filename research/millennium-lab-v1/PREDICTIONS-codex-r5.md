# Codex Round 5 prediction ledger

Computational base: `aukora-deep` commit `19cd2cb`. Status words in this ledger and the resulting report are restricted to **MEASURED**, **UNVERIFIED**, **PREDICTED**, and **VOID**. Each numbered part is appended and committed before its computation. Entries are never rewritten after a run. No zeta-zero ordinate may enter a construction, parameter choice, or window choice. Accuracy is the ordinal comparison on the already-frozen indices 20--50, with no fit, shift, rescaling, or reordered matching.

## R5.0 — sources first

### Source record

**MEASURED:** [`arXiv:2511.22755`](https://arxiv.org/abs/2511.22755) exists. The fetched v1 PDF has SHA-256 `c98d89f7fc999d038e15e80a9aaaee2af797c17711c4329ca7ce48ad49cb336b`, 34 pages, and the exact title `Zeta Spectral Triples`. Its arXiv dateline is `arXiv:2511.22755v1 [math.NT] 27 Nov 2025`; the title page supplies no separate manuscript date.

The full abstract was read from the PDF. A complete verbatim reproduction is not placed in this deliverable because it exceeds the allowed quotation length. A 13-word opening excerpt present in the preregistration commit was removed after computation solely to keep the aggregate quotation from this source within the per-source limit; no prediction or source interpretation changed. Faithful synopsis: Connes, Consani, and Moscovici propose self-adjoint rank-one perturbations of the periodic scaling operator on $[\lambda^{-1},\lambda]$, built from Euler factors with $p\le\lambda^2$; they report striking finite numerical agreement, conjectural convergence as $N,\lambda\to\infty$, and regularized determinants expected after normalization to converge to Riemann's $\Xi$ function.

The reported numerical claim is, in the paper's words, “errors ranging from $2.5\times10^{-55}$ ... to approximately $10^{-3}$ for the fiftieth”. Section 6 gives the detailed $N=120$ tables: $\lambda=3$ for 20 levels, then $\lambda^2=12,13,14$ for 50 levels. These are source claims, not Round-5 accuracy measurements.

The paper says there are “two essential steps still missing”. In full faithful paraphrase, they are:

1. prove that the bottom eigenvalue of the continuous compact-window Weil operator is simple and its eigenfunction is even;
2. prove that the prolate candidate $k_\lambda$ approximates a scalar multiple of that true ground state strongly enough to force convergence of the Fourier-transform zeros to the nontrivial zeta zeros.

Both remain **UNVERIFIED** as global/asymptotic statements in that paper.

**MEASURED:** [`arXiv:2608.24827`](https://arxiv.org/abs/2608.24827) exists. The fetched v1 PDF has SHA-256 `d6eed87e8362379281eb0e3ad23e187103c65750da33db79563380aa084318d9`, 9 pages, and the exact title `Weil positivity in compact windows: certified two-sided bounds and a Landau–Widom decay law`. Its arXiv dateline is `arXiv:2608.24827v1 [math.NT] 25 Aug 2026`; its title-page date is exactly `August 26, 2026`.

The full abstract was read from the PDF. A complete verbatim reproduction is not placed here because it exceeds the allowed quotation length. Faithful synopsis: Chuk studies the compact-window infimum $\lambda^*(L)$, claims a one-stroke finite-matrix lower-bound certificate at $L=0.8$, gives interval-arithmetic variational upper bounds through $L=2$, fits a Landau--Widom decay law, and proves a conditional qualitative upper bound under RH. The reported fixed-window enclosure is $8.9\times10^{-18}\le\lambda^*(0.8)\le2.27\times10^{-17}$; the $L=2$ upper bound is $3.2\times10^{-283}$.

### Source correction before computation

**MEASURED:** an earlier metadata rendering gave August 27 for the second preprint. The current PDF instead says August 26, while arXiv records submission on August 25. More substantively, the second preprint claims that the simple/even condition is certified only at the fixed scale $L=0.8$ and explicitly says the convergence condition is untouched. It does not complete the 2025 program. This correction was disclosed before any Round-5 computation.

**MEASURED source-archive audit:** the v1 archive for `2608.24827` contains its TeX source and two figures, but no executable code, coefficient vector, interval matrix, Cholesky residual, quadrature specification, or machine-readable certificate. Its finite numerical certificates therefore cannot be replayed from the submission and remain **UNVERIFIED** here unless reconstructed independently. Equation (4)'s fitted equality is explicitly restated as Conjecture 10; the uniform-comb lemma does not prove the abstract's broader barrier for every possible pointwise envelope; and the decisive potential-theoretic estimate invoked for conditional Theorem 2 is not supplied. These are source-scope findings, not refutations of statements for which a complete proof or certificate may exist elsewhere.

## R5.1 — independent finite Weil reconstruction

### Frozen construction

Let $x=\lambda^2$ and $L=2\log\lambda=\log x$. In the orthonormal Fourier basis $V_n$, $|n|\le N$, the builder will assemble the real symmetric matrix exactly from Eqs. (2.9), (3.13)--(3.16), and (4.1)--(4.14) of `2511.22755`:

\[
 QW_\lambda(V_n,V_m)=W_{0,2}(V_n,V_m)-W_{\mathbb R}(V_n,V_m)
 -\sum_{1<q\le x}\Lambda(q)q^{-1/2}q(V_n,V_m)(\log q).
\]

The sum is generated from prime powers $q=p^a\le x$ and contains no zeta data. The archimedean entries use the paper's hypergeometric/digamma formulas; selected entries and an $N=12$ replay use independent tanh--sinh integration of the defining distributions. The full and parity-reduced matrices are separate algebraic paths. The lowest even vector $\xi$ is normalized only by $\langle\delta_N,\xi\rangle=1$. Its transform is evaluated from Eq. (5.25), and positive roots are enumerated in order from zero using the unperturbed lattice poles; neither a root bracket nor a stopping rule may consult a zeta ordinate.

The fixed cases are $(x,N)=(9,120),(12,120),(13,120),(14,120)$. Each matrix and its low perturbed spectrum will be rebuilt at 100, 200, and 400 decimal digits. Files produced by this builder are forbidden from importing `mpmath.zetazero`, reading `zeros.txt`, or containing a stored zeta ordinate. A static audit will enforce that condition.

The independent Fable implementation remains embargoed: Codex will not read it until Codex's construction and output are committed and Fable's implementation is also committed. The report will display Codex's low spectrum before any implementation diff. If a committed Fable reconstruction is unavailable, the requested diff is **UNVERIFIED**, not silently replaced by a comparison with the published accuracy table.

### Registered predictions

**PREDICTED R5.1-A (matrix identities).** At every fixed case and precision, the assembled matrix will be real symmetric, commute with inversion parity, and agree with the direct-integral control on all sampled entries to at least 80, 175, and 350 decimal digits at 100, 200, and 400 dps. The smallest full eigenvalue will be simple and lie in the even sector; the lowest odd value and second even value will both be strictly larger.

**PREDICTED R5.1-B (precision and roots).** The first 50 positive transform roots will be real, simple, and ordered. Between the 100- and 200-digit builds their maximum displacement will be below $10^{-75}$; between 200 and 400 digits it will be below $10^{-160}$. The $x=9$ first-20 and $x=12,13,14$ first-50 source tables will be numerically reproducible once scoring is legally unblinded.

**PREDICTED R5.1-C (independent-implementation diff).** After resolving only documented convention changes (basis order, global vector sign, and $\delta_N$ normalization), independently committed Codex and Fable matrices will differ entrywise by less than $10^{-70}$ at their common precision and their first 50 positive spectral values by less than $10^{-60}$. Any undocumented fitted parameter or zeta-dependent bracket makes the comparison **VOID**.

**PREDICTED R5.1-D (registered mutations).** The $x=12,13,14$ support changes and the three precision replays are the primary construction mutations. A surviving low-spectrum claim must also survive $N=112$ and $N=128$ without reindexing: roots 20--50 may improve or worsen, but must remain real/simple and move continuously by ordinal index. Accuracy is not evaluated until the R5.2 pseudo-prime gate has completed.

**MEASURED source-archive addendum:** the `2511.22755` source likewise supplies no code, raw matrix, eigenvector, root brackets, interval certificate, or precision replay. Its stated chance probability $10^{-1235}$ has no null model or derivation and is **VOID** as evidence. Its detailed tables are targets for reconstruction, not certificates. “Primes $\le13$” means the six base primes $2,3,5,7,11,13$, while the matrix sum itself includes every prime power below the cutoff. The theorem's self-adjoint metric is the quotient metric induced by $QW_\lambda^N-\epsilon_N I$, not the original $L^2$ metric.

## R5.2 — hostile controls and the oracle gate

### Frozen gate and scoring rule

The baseline control case is $(x,N)=(13,120)$ at 100 dps. Before any computed accuracy, error, or zeta ordinate is emitted, a construction-only process will finish all ten pseudo-prime spectra and write `pseudo-gate.json` containing their seeds, parameters, output hashes, completion times, and an audit that no zero source was imported. That process may output spectral values but no accuracy. Only a separate scorer that verifies this gate may read the frozen ordinates 20--50. The scorer reports, in this order, pseudo-primes, the other controls, and only then the true-prime candidates.

For candidate roots $t_{20},\ldots,t_{50}$ and frozen ordinal targets $\gamma_{20},\ldots,\gamma_{50}$, the score is the unscaled ordinal error $e_j=t_j-\gamma_j$. Report RMSE, MAE, median $|e_j|$, maximum $|e_j|$, and every $|e_j|$ individually. A spectrum “lands” only if RMSE $\le0.01$ and maximum absolute error $\le0.05$. This threshold was fixed without running any candidate or control. Any hostile control that lands makes all zeta-accuracy conclusions **VOID** until an oracle leak or mathematical degeneracy is explained.

### Frozen controls

1. **Archimedean-only:** assemble $W_{0,2}-W_{\mathbb R}$ with the arithmetic comb exactly zero.
2. **Prolate-only:** use the paper's $k_\lambda=\mathcal E(h_\lambda)$, projected into the same $|n|\le120$ Fourier basis, and enumerate transform zeros without consulting $QW_\lambda$ or primes.
3. **Delete-prime:** starting from the true $x=13$ comb, delete in turn all powers of each base prime in $\{2,3,5,7,11,13\}$.
4. **Pseudo-primes:** use NumPy `PCG64DXSM` seeds `52025001` through `52025010`. For each seed, draw six continuous pseudo-primes on $[2,13]$ with intensity proportional to $1/\log u$, sort them, and deterministically reject the draw unless their powers $q^a\le13$ number nine, matching the true base-prime and prime-power counts. Give a pseudo-power $q^a$ weight $(\log q)q^{-a/2}$.
5. **Weight permutation:** preserve the nine true prime-power support locations and the Euclidean norm and multiset of their nine weights, but permute the weights with seed `52025999`.
6. **Three paths:** sample $x\in\{8,10,12,14,16\}$ along $N=\lceil8x\rceil$, $N=\lceil10x\rceil$, and $N=\lceil12x\rceil$. These are finite initial segments of three zero-free parameter paths, not evidence of a limit by themselves.

Each control uses the identical parity reduction, eigenvector normalization, and root enumerator as the true-prime case. An independent smooth Riemann--von Mangoldt quantile is reported only after the pseudo gate and is a scoring baseline, never a construction input.

### Registered predictions

**PREDICTED R5.2-A (pseudo-prime gate).** None of the ten density- and count-matched pseudo-prime spectra will land. I predict their RMSEs on indices 20--50 all exceed $0.5$, with seed-to-seed dispersion larger than the full true-prime $x=12,13,14$ spread.

**PREDICTED R5.2-B (ablation specificity).** Archimedean-only, prolate-only, and weight-permuted controls will not land. Every single-prime deletion will worsen the true $x=13$ RMSE; deleting 2 will be most destructive, while deleting 13 will cause the second-largest degradation. A deletion that still lands survives only provisionally and must also pass an added deletion-plus-5% weight mutation before any specificity claim is retained.

**PREDICTED R5.2-C (paths).** The three sampled $N(x)$ paths will agree on reality, simplicity, and ordinal continuity but not exhibit a clean uniform accuracy law on the short range. At common $x$, doubling-like changes in $N$ will affect indices 20--50 less than changing $x$ by two. I predict no hostile path artifact lands without the authentic arithmetic weights.

**PREDICTED R5.2-D (survivor mutations).** Any true-prime case that lands must survive the registered 100/200/400-dps replay and both $N=112,128$ mutations from R5.1. Any hostile control within a factor two of the landing RMSE threshold is rerun with ten additional preregistered seeds derived by adding `1000` to its original seed; a conclusion based on a lone favorable seed is **VOID**.

## R5.3 — measuring the prolate-to-Weil bridge

### Frozen candidate and norms

For $x=\lambda^2\in\{5,6,7,8,9,10,11,12,13,14,16,18,20\}$, use the regular even eigenfunctions $h_{0,\lambda}$ and $h_{4,\lambda}$ of

\[
 PW_\lambda=-\partial_y[(\lambda^2-y^2)\partial_y]+(2\pi\lambda y)^2
\]

on $[-\lambda,\lambda]$, with spheroidal parameter $2\pi\lambda^2$. Normalize them in $L^2$, fix positive value at zero, form the unique linear combination $h_\lambda$ with zero integral, extend it by zero, and set $k_\lambda(u)=u^{1/2}\sum_{m\ge1}h_\lambda(mu)$ on $[\lambda^{-1},\lambda]$. Project $k_\lambda$ into $E_{120}$ by quadrature fixed independently of any zero and normalize the coefficient vector to Euclidean norm one.

For the true-prime Weil matrix $M_\lambda$, define

\[
 \mu_\lambda=\langle k_\lambda,M_\lambda k_\lambda\rangle,\quad
 r_\lambda=\|(M_\lambda-\mu_\lambda I)k_\lambda\|_2,
\]

and $\Delta_\lambda=\min(\epsilon_{2,\mathrm{even}},\epsilon_{1,\mathrm{odd}})-\epsilon_{1,\mathrm{even}}$. Report $r_\lambda$, $\Delta_\lambda$, and $r_\lambda/\Delta_\lambda$. Also report the actual spectral separation $s_\lambda=\min_{j\ne1}|\epsilon_j-\mu_\lambda|$; only when $s_\lambda>0$ is the residual angle bound $\sin\angle(k_\lambda,\xi_\lambda)\le r_\lambda/s_\lambda$ asserted.

After optimally aligning the sign and scalar normalization of $k_\lambda$ and the ground vector, convert the angle bound by Cauchy--Schwarz into a uniform transform bound on the preselected rectangles $|\Re z|\le32,64,128$ and $|\Im z|\le1/4$. No rectangle is moved after seeing a spectrum or zero.

### Registered predictions

**PREDICTED R5.3-A (decay law).** The ratio will decay as a power rather than stall: a robust log--log fit on the last five $\lambda$ values will give $r_\lambda/\Delta_\lambda=C\lambda^{-p}$ with $1.25\le p\le2.75$, and the power model will beat a constant-plus-noise model by AIC. The central prediction is $p\approx2$, motivated by the paper's proved $O(\lambda^{-2})$ prolate-to-Hermite approximation; that theorem does not itself imply this bridge prediction.

**PREDICTED R5.3-B (usable angle bound).** For $x\ge12$, $\mu_\lambda$ will lie closer to the even ground value than to every competing eigenvalue, $r_\lambda/s_\lambda<1$, and the resulting transform bound will decrease on all three fixed rectangles. I do not predict that the finite bound alone is strong enough to transfer or isolate a zeta zero.

**PREDICTED R5.3-C (controls and mutations).** The undeformed Hermite combination $h$ substituted for $h_\lambda$ and pseudo-prime seed `52025001` substituted for the arithmetic comb will each have a larger final-five median $r/\Delta$ than the true prolate/prime pair. Every surviving trend is repeated at $N=96$ and $N=144$; it must retain the sign of its fitted slope. Failure of the trend or a pseudo-prime ratio as small as the true one makes the bridge interpretation **VOID**.

## R5.4 — one finite simple/even lemma attempt

### Frozen structural tests

On the same zero-free $x$ grid, split the Weil matrix into its orthonormal even and odd parity blocks. Test four possible finite mechanisms without tuning signs to an eigenvector:

1. whether a diagonal sign conjugation makes a scalar shift of the even block entrywise positive and irreducible, allowing Perron--Frobenius simplicity;
2. whether a diagonal sign conjugation makes the shifted block a nonsingular irreducible M-matrix;
3. whether minors through order four obey a consistent strict sign-regular pattern;
4. whether independently enclosed even/odd Ritz pairs and residuals give a strict min--max separation between the first even value, second even value, and first odd value.

The diagonal signs, if they exist, must solve all off-diagonal sign constraints and are found by graph propagation; choosing them from a computed ground vector is forbidden. A frustrated signed triangle is an explicit obstruction. Any surviving entry sign, minor sign, or eigenvalue ordering at $x\in\{5,9,12,13,14,20\}$ must be re-evaluated with outward-rounded Arb balls. A finite-$N$ interval statement is not promoted to the continuous operator or to all $\lambda$.

### Registered predictions

**PREDICTED R5.4-A (finite ordering).** At all sampled $x$ and $N=120$, the first even value will be simple and strictly below both the second even and first odd values. Verified residual enclosures will certify this finite ordering at the six interval-audit points.

**PREDICTED R5.4-B (structural obstruction).** No single diagonal sign conjugation will make the relevant shifted even block positivity-improving or an M-matrix throughout the grid; a three-index frustrated cycle will already obstruct it for at least one $x\ge9$. The minors will not retain one strict sign-regular pattern. Thus the finite ordering will survive numerically but the hoped-for uniform lemma will remain **UNVERIFIED**.

**PREDICTED R5.4-C (mutations).** Delete the base prime 13 at $x=13$ and separately move the continuous cutoff to $x=13.25$ without changing the prime set. I predict the finite simple/even ordering survives both, while the first frustrated sign cycle need not keep the same indices. A structural pattern reported as surviving only if both mutations preserve it is then interval-checked again.

## R5.5 — side bets

### R5.5a — rogue Jensen horizon

Use $F(z)=8\xi(1/2+z)=\sum_{n\ge0}\gamma(n)z^{2n}/n!$, with coefficients computed from the standard theta-kernel integral and no zero list. Insert, by multiplication rather than replacement, the functional-equation-symmetric rogue quartet with $\delta=\beta-1/2=1/4$ and $\Gamma\in\{14.13,100,1000\}$:

\[
 R_{\delta,\Gamma}(z)=
 \frac{((z-\delta)^2+\Gamma^2)((z+\delta)^2+\Gamma^2)}{(\delta^2+\Gamma^2)^2},
 \qquad F_\Gamma=F R_{\delta,\Gamma}.
\]

The primary horizon is the least shift $n\ge0$ for which the standard cubic Jensen polynomial

\[
 J_{\Gamma}^{3,n}(X)=\sum_{j=0}^{3}{3\choose j}\gamma_\Gamma(n+j)X^j
\]

is not hyperbolic. Degree two and four are registered mutations and are reported separately; “first” is never claimed without its degree. The search brackets by zero-free coefficient inequalities and doubling, then isolates the first transition. At the predecessor and horizon, certify independently by Arb root balls, a Sturm count using rational outward enclosures, and the inertia of the Hermite matrix. If the three certificates disagree, the horizon is **UNVERIFIED**.

**PREDICTED R5.5-A (Jensen scaling).** The cubic horizons will be finite and scale primarily as $\Gamma^2$: the regression slope of $\log n_J$ on $\log\Gamma$ will lie in $[1.7,2.3]$. The ratios $n_J/\Gamma^2$ may drift logarithmically, so a constant ratio is not predicted. Degree two and four will change constants but not the fitted exponent. A failure to bracket the $\Gamma=1000$ transition below $256\Gamma^2$ remains **UNVERIFIED**, not extrapolated.

### R5.5b — butterfly quantum-graph surgery

Reproduce Kuipers--Hummel--Richter's prime-orbit trace on a finite collection of butterfly graphs with primitive lengths $\log p$, repetitions $m\log p$, and unitary $2\times2$ scatterers chosen from their published phase prescription. Use prime cutoffs $P\in\{29,53,97,193\}$ and a fixed Fourier-test interval $0\le k\le256$; neither uses a zeta ordinate. The analytic explicit-formula prime sum is the match target. A graph with the same number and total length of pseudo-prime bonds is the control.

Then couple all butterflies through a unitary central scatterer, first the normalized discrete Fourier matrix, with the identity and a Haar unitary of fixed seed `52025555` as mutations. Report the smooth Weyl coefficient, the original prime-orbit Fourier amplitudes, and amplitudes of new mixed-length orbits before and after coupling.

**PREDICTED R5.5-B (trace and surgery).** The decoupled construction will reproduce its finite analytic prime trace to numerical quadrature error. Nontrivial central coupling will retain a self-adjoint finite graph but introduce mixed primitive lengths and spoil at least one prime coefficient by more than 1%; the Weyl term $L_{\rm tot}/\pi$ will persist and grow with cutoff, dominating rather than algebraically canceling the oscillatory prime trace. The identity mutation will recover the decoupled coefficients; the Haar mutation will not restore them.

**PREDICTED R5.5-C (three-yeses row).** A finite coupled graph has a self-adjoint discrete Laplacian, but no demonstrated zero spectrum in the cutoff limit. Chaos without arithmetic degeneracy remains **UNVERIFIED**, and clean prime lengths fail after genuine coupling. The row will therefore not have three yeses.

## R5.6 — stretch: band-limited SDP/SOS positivity

This part runs only after R5.0--R5.5 if time permits. Because `2608.24827` supplies no replayable certificate, an extension is not measured relative to an assumed-valid binary artifact. The mandatory control is an independent outward-rounded reconstruction at $L=0.8$. Only if that control produces a complete machine-checkable positive lower bound will the same frozen method be tried at $L\in\{0.805,0.81,0.82\}$.

The attempted method uses piecewise degree-16 Chebyshev majorants for the prime comb and archimedean symbol on a fixed rational subdivision, an SDP/SOS Gram representation rationalized after solving, and interval remainder bounds. A surviving bound is replayed at degree 24 and with every interval bisected. The deliverable must state the exact support, rational/interval certificate, and positive constant; a floating eigenvalue is not a theorem.

**PREDICTED R5.6-A.** No valid extension beyond $L=0.8$ will be certified in the available run. The likely blocker is reconstructing a complete $L=0.8$ tail certificate from the incomplete source description, not a measured loss of positivity. If no complete certificate is produced, the outcome is **UNVERIFIED** and no negative conclusion about compact-window positivity is drawn.
