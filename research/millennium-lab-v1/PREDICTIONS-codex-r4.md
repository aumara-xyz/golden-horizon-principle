# Codex Round 4 prediction ledger

Status words in this ledger and the resulting report are restricted to **MEASURED**, **UNVERIFIED**, **PREDICTED**, and **VOID**. Predictions are appended and committed before the corresponding part is computed. They are never rewritten after a run.

## R4.1 — truncated de Bruijn–Newman flow

**PREDICTED R4.1-A (identity and time).** In each of the four 10,000-zero Odlyzko blocks used by toy T3, the first pair to collide under the toy-T4 backward flow will be the consecutive pair attaining the initial minimum physical gap, $g_{\min}$. Its collision magnitude will be

\[
 |t_{\mathrm{collision}}|_{\mathrm{pred}}=g_{\min}^{2}/8.
\]

I predict $0.90\le |t_{\mathrm{actual}}|/(g_{\min}^{2}/8)\le1.15$ for all four blocks. The prediction is algorithmic rather than fitted: the numerical $g_{\min}^{2}/8$ values will first be emitted by the frozen runner alongside the as-loaded pair indices, then compared with event times from an independent integration path.

**PREDICTED R4.1-B (height scaling).** For $n=10^4$ fixed spacings, the GUE small-gap CDF is cubic, so the smallest unfolded gap is $O(n^{-1/3})$. With local density

\[
 d(T)=\frac{\log(T/2\pi)}{2\pi},
\]

the physical minimum gap is $O(n^{-1/3}d(T)^{-1})$, hence the collision time is $O(n^{-2/3}d(T)^{-2})$. Thus the predicted exponent in density, equivalently in $\log(T/2\pi)$, is $-2$. It is not a power of $T$: the literal $T$-power exponent is $0$ with a squared-log correction. Because finite-block extreme gaps fluctuate, I predict only that a log-log regression of the four observed times on density has negative slope; I do not predict monotone ordering of four individual minima.

**PREDICTED R4.1-C (Poisson control).** For each block, generate 10,000 exponential spacings with mean $1/d(T)$, using fixed seed `20260902 + block_index`. A Poisson small-gap CDF is linear, giving $g_{\min}=O(n^{-1}d^{-1})$ and $|t_c|=O(n^{-2}d^{-2})$. Relative to GUE, the scale ratio is therefore $n^{-4/3}\approx4.64\times10^{-6}$. I predict every Poisson control time is below $10^{-3}$ of its Odlyzko counterpart. The closest Poisson pair should again collide first and its two-body estimate should be within 20%.

**PREDICTED R4.1-D (registered mutation).** For every Odlyzko block satisfying R4.1-A, delete the two zeros in its first colliding pair, keep every surviving offset unchanged, and rerun. I predict the new initial closest consecutive pair collides first and $0.85\le |t_{\mathrm{actual}}|/(g_{\min}^{2}/8)\le1.20$. This mutation is performed only after the primary result is frozen, and a failure remains in the ledger.

**Interpretive boundary (PREDICTED wording).** These event times belong to finite, truncated blocks with omitted exterior zeros. They are not measurements, estimates, upper bounds, or lower bounds for the de Bruijn–Newman constant $\Lambda$. The report will keep separate the theorem $\Lambda\ge0$ (Rodgers–Tao, 2018) and the theorem $\Lambda\le0.22$ (D.H.J. Polymath/Polymath 15, 2019).

## R4.2 — Berry–Keating and Sierra–Rodríguez-Laguna (2011)

**Frozen models and normalization.** The Berry–Keating calculation will use their published half-line differential problem (Eqs. 2.7–2.9 and 2.22), with self-adjoint phase $\alpha=0$ and $\eta=1/(2\pi)$. The Sierra–Rodríguez-Laguna calculation will use their exact Bessel secular equation (Eq. 14), with $h=1$, $\hbar=1/(2\pi)$, and $\vartheta=\pi/4$. For both, the raw positive energy $E_n$ is reported first and the only scaled comparison is the published mean-density identification $t_n=2\pi E_n$. There will be no regression, offset, or fit to the first 20 zeta ordinates.

**PREDICTED R4.2-A (low spectra).** Both exact quantizations will return 20 real, ordered positive levels. Applying $2\pi$ will improve RMSE against the first 20 zeta ordinates by at least a factor of three relative to the raw energies, and the scaled sequences will have Pearson correlation above $0.99$ with the ordinates. Neither scaled spectrum will match the arithmetic fluctuations: I predict RMSE above $1$, maximum absolute residual above $2$, and no level equal to a zeta ordinate within $10^{-6}$. I predict Sierra–Rodríguez-Laguna has the lower scaled RMSE of the two.

**PREDICTED R4.2-B (numerical convergence).** Berry–Keating shooting at $x_{\max}=30$ with relative/absolute tolerance $10^{-11}$ will agree with $x_{\max}=40$, tolerance $10^{-12}$ to below $10^{-6}$ in every scaled level; a separate collocation or reverse-shooting residual will confirm the same roots. Sierra–Rodríguez-Laguna roots bracketed on an energy mesh of width $0.002$ and refined at 60 decimal digits will be unchanged to $10^{-10}$ in scaled units when the mesh is halved and precision raised to 80 digits. A direct quadrature of its nonlocal boundary condition is the independent residual control.

**PREDICTED R4.2-C (smooth-density control).** In each model, the candidate-to-zeta residuals will be no smaller in RMSE than a parameter-free smooth Riemann–von Mangoldt quantile control by more than 20%. In other words, any visible match will be attributable to the shared mean counting law, not prime fluctuations. If either exact candidate beats that control by more than 20%, that is a surviving claim and must also survive the phase mutation below.

**PREDICTED R4.2-D (registered mutation).** Change only the self-adjoint extension phase, to $\alpha=\pi/2$ for Berry–Keating and $\vartheta=3\pi/4$ for Sierra–Rodríguez-Laguna. I predict the spectra remain real and discrete and retain the same leading mean density, while at least one of the first 20 scaled levels moves by more than $0.1$. Thus a low-level agreement that disappears under phase mutation is not arithmetic evidence.

**PREDICTED R4.2-E (three-yeses rows).** Each fixed phase supplies a self-adjoint operator with discrete real spectrum: yes. Both classical systems have one degree of freedom and are integrable, so “chaotic without arithmetic degeneracy” is no. Berry–Keating explicitly has one primitive orbit per energy, and Sierra–Rodríguez-Laguna has $T_E\sim\log(E/h)$ rather than a prime-indexed family; “orbits of length $\log p$” is no for both. I predict neither row has three yeses.

## R4.3 — Polymath 15 in miniature

**Frozen normalization and window.** Use the final Polymath paper’s normalization

\[
 H_0(z)=\frac18\,\xi\left(\frac12+\frac{iz}{2}\right),\qquad
 H_t(z)=\int_0^\infty e^{tu^2}\Phi(u)\cos(zu)\,du,
\]

not the inconsistent shorthand on older wiki pages. At $t=0.2$, use the paper’s effective Riemann–Siegel approximation (Theorem 1.3, with the sharper $A+B-C$ correction where implemented) on the fixed rectangle $210\le\Re z\le300$, $|\Im z|\le1$. Its truncation index is constantly $N=4$ there. The defining integral is an independent evaluator, not the source of the primary brackets.

**PREDICTED R4.3-A (count, reality, simplicity).** I predict 22 zeros in the rectangle, all on the real segment $(210,300)$ and all simple. The numerical criterion is: the full boundary winding equals the number of real brackets; a small conjugation-symmetric contour around each bracket has winding one; the local counts sum to the full count; and the analytic derivative is nonzero at each root. I also predict the minimum real-root separation exceeds $0.25$.

**PREDICTED R4.3-B (approximation and integral control).** The effective Riemann–Siegel evaluator and the independent defining-integral evaluator will give the same rectangle count and pair roots in order with maximum displacement below $0.2$. Repeating the winding and roots at 30 additional decimal digits and twice the boundary mesh will leave the count unchanged and move each root by less than $10^{-8}$. If the explicit remainder is not used with interval/Rouché bounds, the outcome will be labelled MEASURED rather than proved.

**PREDICTED R4.3-C (normalization control).** At $t=0$, direct evaluation in the same window will reproduce every applicable control root $z=2\gamma_n$ to $10^{-8}$ and the argument-principle count will agree with the tabulated zeta-zero count. This control is required because comparing $z$ directly with $\gamma_n$ would introduce a factor-of-two error.

**PREDICTED R4.3-D (registered mutation).** Repeat the complete count at $t=0.19$ on the same rectangle. I predict the count remains 22, all counted zeros remain real and simple, every $t=0.2$ root continues uniquely, and at least one root shifts by more than $10^{-4}$. A primary reality/simplicity claim that fails this mutation is not reported as robust.

**PREDICTED R4.3-E (scope of Polymath 15).** The report will distinguish this finite-window measurement from the theorem. Polymath 15 used $t_0=y_0=0.2$ and a barrier near $X=6\times10^{10}+83952-1/2$ to obtain $\Lambda\le t_0+y_0^2/2=0.22$; it did not prove that all zeros of $H_{0.2}$ are real. I predict the miniature illustrates the evaluator but adds no bound on $\Lambda$. The method as implemented cannot attain $0$: its criterion keeps $t_0,y_0>0$, its asymptotic threshold grows like $\exp(C/t_0)$, and finite RH verification yields only a positive $O(1/\log T)$ bound.

## R4.4 — wrap

**PREDICTED R4.4-A (no three-yeses row).** The cumulative table will contain at least the five explicitly tested rows: Berry–Keating cutoff $xp$, Bender–Brody–Müller, Weil/Connes–Consani positivity, Berry–Keating compact 2011, and Sierra–Rodríguez-Laguna 2011. I predict none has all three demonstrated properties: a self-adjoint discrete zero spectrum, chaos without arithmetic degeneracy, and prime-labelled orbit lengths $\log p$.

**PREDICTED R4.4-B (failure audit).** The one-page summary will retain every located failed prediction from both Fable and Codex, including near-threshold misses and category errors, and append every Round 4 miss without rewriting the original ledger. Apparent successes will be stated only at their measured finite scope and paired with their registered control and mutation outcome.

**PREDICTED R4.4-C (historical boundary).** The wrap will attribute results to the earliest source that established the actual statement being summarized, with year and a primary citation where available. If priority cannot be supported, it will say UNVERIFIED rather than guess. Results over finite fields, finite zero windows, truncated heat flow, smooth spectral counts, and positivity on finite test families will not be promoted to RH over the integers.

**PREDICTED R4.4-D (open problem).** Unless a registered Round 4 control overturns the premise, the final sentence will be: “Construct a demonstrated self-adjoint operator whose discrete spectrum is the Riemann ordinates, whose dynamics is chaotic without arithmetic degeneracy, and whose periodic orbits have lengths $\log p$ with the required repetitions and trace-formula signs.”
