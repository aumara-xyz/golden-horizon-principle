# D10 — what the identities do and do not prove

This round borrows the *methodological* lesson of Viviani's theorem: contributions that change together should be kept together. It does not identify the Weil form with triangle areas. The user reports a family connection to Vincenzo Viviani; that motivates the experiment, not its conclusions.

## Exact full-form statement

See [KERNEL-PROOF.md](KERNEL-PROOF.md) for definitions, complex conjugations, domains, and derivations. For a zero-extended test wave, with D_u=||f(.+u)-f||², the existing Weil form satisfies

    W(f) = (a0-B)||f||² + Pi(f)
           + (1/2) integral_0^infinity [exp(u/2)/sinh(u)] D_u du
           + (1/2) sum_n w_n D_log(n).

The sum is only over prime powers visible in the support. The squared differences are nonnegative, but a0-B<0, and the odd pole contribution is negative. This identity does not establish that their total is nonnegative. Separately bounding the pieces is precisely where cancellations can be lost.

The full off-diagonal continuous kernel, away from the negative prime atoms, is

    K(r) = 2cosh(r/2)-exp(r/2)/(2sinh(r))
         = (q³-q-1)/(sqrt(q)(q²-1)), q=exp(r)>1.

The exact triangle at centers -log(5/4),0,log(5/4), with radius-1/100 neighborhoods, excludes a local diagonal-gauge representation whose off-diagonal kernel is everywhere real nonpositive. It does NOT exclude a general positive representation. The explicit positive 3-variable toy in KERNEL-PROOF.md enforces that distinction.

## Unplanned analytic corollary: the precise sign-obstruction threshold

This was derived AFTER the preregistered triangle test, without selecting further numerical windows or fitting a constant. It is not counted as a successful blind prediction. Two analytical readers independently checked the argument.

Let rho>1 be the unique solution of rho³-rho-1=0 and r_star=log(rho). Since q³-q-1 increases for q>1, K(r)<0 for r<r_star and K(r)>0 for r>r_star. Also rho<sqrt(2), because the polynomial at sqrt(2) equals sqrt(2)-1>0.

For any L>r_star/2 choose d in (r_star/2,min(L,r_star)). The centers -d,0,d fit inside the window. Neighboring separations are below r_star, while the outer separation is above r_star and below 2r_star<log(2). Small neighborhoods retain these strict inequalities. No prime-shift cross term occurs. The signs are (-,-,+), whose product is invariant under diagonal phase changes and incompatible with three negative edges. The same argument applies to almost-everywhere measurable nonvanishing phase/positive gauges, by choosing almost every triple in these neighborhoods.

If L<=r_star/2, every allowed separation is <=r_star, so the continuous kernel is nonpositive and no prime atom occurs. At equality the zero kernel value is reached only at the two opposite endpoints, a null set. Thus r_star/2 is sharp for **this off-diagonal sign obstruction only**. It is not a threshold for Weil positivity, RH, physical confinement, or an observer. The cubic constant is fixed by this particular kernel's coefficients; it is not evidence for a preferred number in nature. No theorem-novelty claim is made.

## Finite joint completion around the known pole direction

See [SCHUR-PROOF.md](SCHUR-PROOF.md). For the D7 finite lower-envelope matrix R_120, keep H=A-prime together and write R_kappa=H+kappa pp^T. The vector p is the analytic cosh/sinh projection, not an optimized eigenvector. With u=p/||p||, write f=tu+g, g perpendicular to u. Set a=<u,Hu>, b=P_perp Hu, C=P_perp H P_perp. If C>0,

    R_kappa(f) = ||C^(1/2)(g+C^(-1)b t)||² + sigma |t|²,
    sigma = a+kappa||p||²-b^T C^(-1)b.

The identity preserves the arithmetic/background dependence. But it requires proving C>0 AND sigma>=0. Computing C^(1/2) only after positivity has been checked is not a new proof mechanism. The measured quantity called a 'gap' in code is the minimum eigenvalue above zero, NOT the spacing between the first two eigenvalues.

Principal finite blocks of a lower envelope are analyzed here, not exact full-W matrices and not newly certified all-function operators. The old D7 infinite-dimensional statement remains a separate input. No claim across all support widths follows.

## New control-matrix enclosure

build.py runs the unchanged Opus builder in this directory. If old and new weights differ by delta_w, changing the model changes H by

    2 integral_0^120 [sum delta_w cos(a t)] F_i(t) F_j(t) dt.

The existing unit-panel Fourier/ellipse bounds apply. The analytic multiplier is bounded by M_delta=sum |delta_w| cosh(a b_ellipse). Consequently the added entry error is bounded by

    2*Cq*120*M_delta*MF_i*MF_j.

All constants, nodes, products, matrices and errors are Arb balls. The factor 2 includes negative frequencies. Archimedean-only and reversed-positive-weight models have absolute-weight sum no larger than the authentic B, so the authentic beta=a(120)-B remains a valid fixed lower envelope for them. A negative control R_120 witness is still NOT a negative full-W witness.

## Full-W pole-strength witnesses, using D9 data

For each previously frozen D9 wave, p_overlap=Pi(f)/kappa_auth is nonnegative, with kappa_auth=+2 even or -2 odd. D9 already normalized all component scores by ||f||². Hence

    W_kappa(f)/||f||² = W_auth(f)/||f||²
                       +(kappa-kappa_auth)*p_overlap.

pole_witness.py propagates the D9 lower and upper endpoints, reverses endpoint ordering for division by -2, and rechecks each saved sign. Its negative upper bounds refer to the complete modified W, with D9's full infinite-frequency tail retained. These are artificial pole mutations, not other zeta functions; a positive score concerns only that frozen wave.

## Sources and priority boundaries

- Viviani invariant: [Abboud, On Viviani's Theorem and its Extensions (2009; published 2010)](https://arxiv.org/abs/0903.0753). Methodological inspiration only.
- Weil-form normalization and earlier operator positivity research: [Connes–Consani, Weil positivity and Trace formula: the archimedean place (2021), equations (1)–(3)](https://alainconnes.org/wp-content/uploads/Selecta.pdf).
- Established ground-state representation methods: [Frank–Seiringer (2008)](https://arxiv.org/abs/0803.0503). This paper is background, not a source asserting our particular zeta-kernel obstruction.
- Standard Schur complement/congruence/inertia identities: [Gowda–Sznajder (2010), introductory identities](https://userpages.umbc.edu/~gowda/papers/GOW10-01.pdf). The finite completion used here is ordinary linear algebra.

The explicit sign-cycle application was derived in this round. A limited source search is not a novelty audit. No claim that the kernel observation, toy, or Schur rewrite is new to the literature is justified here. Proofs are mathematical text and ball-arithmetic checks, not proof-assistant formalizations; reviewers share this machine and arithmetic library.
