# Riemann research: correction-aware report for Qwen

Prepared for Peter Viviani, 13 September 2026. Scope: the available Aukora millennium-lab records through R15, the Golden Horizon Principle (GHP) experiments, and the D-series through **D24**. This is a synthesis of saved research, not a new execution or independent recertification of every experiment.

## 1. Executive verdict

**We have not proved the Riemann Hypothesis, established a new route that reaches it, or verified a novel RH theorem.** We have built a useful computational research and audit program. Its strongest outputs are finite-window positivity certificates, rigorously scored counterexamples to modified forms, corrections to misleading numerical conclusions, and concrete tests of proposed bridges to spectral geometry.

The most important advances *within this lab* are:

1. Independently implemented small-window certificates, with explicit treatment of the infinitely many directions outside the finite matrix.
2. Separation of the actual Weil form from the lower approximation used to certify it. This overturned several claims about indispensable prime powers.
3. Detection and conservative repair of a quadrature error allowance and a checker that did not prove the exact advertised bound.
4. Identification of why a very close-looking prolate wave can still have much too much energy.
5. Counterexamples showing that mirror symmetry, unitary completion, consistent observer loops, and golden-ratio geometry do not, by themselves, force RH.

These are valuable research outcomes, but “we found and repaired an error” is different from “we found a new theorem about zeta.” General prolate–Weil connections, compact-window positivity, and the relevant spectral methods have substantial prior art. The lab has no demonstrated priority claim for those ideas. See the [D20 audit][D20] and [D24 audit][D24].

The existing Fable `FULL-REPORT-2026-09-13.md` predates D24. Preserve it as history, **not as the final training truth**: its exact-prolate, decay-law, unique-exponent, and some certificate wording require the corrections below.

## 2. What problem are we actually studying?

For Re(s)>1,

\[
\zeta(s)=\sum_{n\ge1}n^{-s}=\prod_{p\text{ prime}}(1-p^{-s})^{-1}.
\]

The function extends beyond this region. RH says all its nontrivial zeros have real part 1/2. The completed function

\[
\xi(s)=\tfrac12s(s-1)\pi^{-s/2}\Gamma(s/2)\zeta(s)
\]

satisfies ξ(s)=ξ(1−s) and conjugation symmetry. A zero off the critical line can therefore belong to a symmetric quartet β±iγ, 1−β±iγ. **Symmetry permits this quartet; it does not exclude it.**

The spectral approach seeks a mathematically defined operator, built without importing the target zeros, whose spectrum is provably linked to zeta. Self-adjointness supplies real spectral values, but only after the exact spectral identification has been proved does that help RH. Designing an arbitrary self-adjoint model proves something about that model, not zeta.

The current GHP lane uses Weil positivity instead: a prime-built quadratic form must be nonnegative on the full admissible test-function class. Compactly supported tests of every support size provide a formulation of that obligation. A certificate at one support size is a genuine restricted statement, **not the missing universal quantifier**. RH does not demand a single strictly positive lower constant uniform over every size.

### Exact conventions for the D-series

Let f be supported in [−L,L], extended by zero, with unitary Fourier transform

\[
F(t)=(2\pi)^{-1/2}\int f(x)e^{-itx}\,dx.
\]

Set

\[
a(t)=\Re\psi(1/4+it/2)-\log\pi,\qquad
P_L(t)=\sum_{p^k\le e^{2L}}\frac{2\log p}{p^{k/2}}\cos(t\log p^k),
\]

and define H±=∫f(x)e^{±x/2}dx and Π(f)=2 Re(H+ conjugate(H−)). Then the convention used here is

\[
W_L(f)=\int_{\mathbb R}(a(t)-P_L(t))|F(t)|^2dt+\Pi(f).
\]

For real even f, Π=+2C² with C=∫f cosh(x/2); for real odd f, Π=−2S² with S=∫f sinh(x/2). **The odd pole is not zero.** Do not mix the unitary Fourier normalization with the unnormalized H±.

W is finite on the appropriate logarithmically weighted Fourier class; compact support and L² alone do not ensure finite W. The extended form can take +∞. The classical explicit formula is invoked on its admissible class, not by silently asserting convergence for every L² function.

The certificate uses B equal to the sum of the absolute arithmetic weights, β=a(T)−B, and

\[
R_T(f)=\int_{|t|\le T}(a-P_L-\beta)|F|^2dt+\beta\|f\|^2+\Pi(f),
\qquad W_L\ge R_T.
\]

Let mW and mR be the normalized all-function infima, and mR,N the minimum on a finite subspace. Then

\[
m_R\le m_W,\qquad m_R\le m_{R,N}.
\]

There is **no general ordering between mW and mR,N**. A negative lower approximation need not imply negative W; a positive finite matrix need not imply all-function positivity. This distinction is the central lesson of D20–D24.

## 3. Evidence labels and source precedence

| Label | Meaning in this pack |
|---|---|
| MEASURED — certified | Interval or exact-arithmetic evidence, with explicitly stated analytic dependencies and domain. Not necessarily peer-reviewed or machine-formalized. |
| MEASURED — numerical | An observed finite numerical result. Precision, controls, and reproducibility still matter. |
| UNVERIFIED | Missing proof, missing implementation, unresolved intervals, or an extrapolation not supported by the evidence. |
| PREDICTED | A preregistered statement not yet established by a completed test. |
| VOID | The stated interpretation/certificate is invalid as written. It does not mean every nearby weaker statement is false. |

Classical theorems are identified by source rather than relabeled as lab discoveries. A later audit overrides only the claims it actually checks. Unrun tests do not pass; inconclusive computations do not refute a theorem. Older precision claims in the Aukora history below are reported from its records, not newly interval-verified in this synthesis.

Two numbering systems exist: **Aukora R5 is not GHP D5**. Their spaces, normalizations, cutoffs, and matrices must not be conflated. The no-zero-input rule governed particular constructions and later protocols; it did not forbid all historical diagnostic studies of recorded zeros.

## 4. Earlier Aukora work: what each avenue taught us

Sources: [early lab summary][ASUM], [R5][AR5], [R5b][AR5b], and the individually linked later rounds. These are research records, not endorsements of every earlier sentence.

### R1–R4: baseline checks and named approaches

| Avenue | Recorded outcome | What follows |
|---|---|---|
| Zeta evaluation, Gram intervals, zero statistics | Reproduced familiar numerical features; Gram's law fails. | A critical-line zero search alone is not an exhaustive zero count or RH proof. |
| Explicit-formula prime peaks | Ratios about 1.294 and 0.707 were reproduced as prime-power weight effects. | Known arithmetic structure, not a new mechanism. |
| Li coefficients | The zero-free calculation corrected λ100 from 118.385 to approximately **118.603775376791**. | A useful numerical correction; one positive coefficient does not prove all Li inequalities. |
| Rogue-zero horizons | A β=.75, γ≈14.1347 Li toy first failed at n=7638. A targeted Weil witness looked much faster but used γ in its design. | No fair zero-blind superiority or universal γ² law was established. Arbitrarily injecting a quartet does not define modified divisor sums for Robin/Lagarias tests. |
| Maass forms and scattering | Arithmetic spectral statistics were Poisson-like in the tested sense; modular scattering had the expected unit-modulus property, also present in a Dirichlet control. | Generic scattering identities are not RH. |
| Berry–Keating / Sierra–Rodríguez-Laguna | Implementations reproduced mean-density ideas, not accurate individual zeta ordinates. A smooth-count control outperformed their fitted low spectra in the recorded comparison. | Mean count and exact arithmetic spectrum are different targets. |
| Bender–Brody–Müller | Formal spectral claims did not settle the operator-domain/self-adjointness problem. | No numerical shortcut around the published mathematical objection. |
| Backward de Bruijn–Newman toy flow | Finite-block collision times closely tracked the smallest-gap estimate; Poisson controls collided earlier. | Truncated-block times are **not measurements of Λ**. Rodgers–Tao and Polymath bounds are external theorems. |
| Finite-field model | Good-reduction primes below 200 for y²=x³−x gave Frobenius eigenvalues of modulus √p. | A replication illustrating established finite-field theory; the corresponding integer-side geometric mechanism remains missing. |

The older “three yeses” table asked for self-adjoint discrete spectrum, suitable chaotic behavior, and prime-length orbits. No candidate met all three in the intended way. **This is a checklist for one spectral program, not a theorem that every possible proof of RH must satisfy those three conditions.** The Erdős/AI survey and BSD side examples were orientation work, not advances on RH; no updated exhaustive 2026 AI-priority survey is asserted here.

### R5–R7: the Weil–prolate bridge and its controls

Independent finite Weil reconstructions reportedly agreed to high precision. However, the prolate-only control also approximately located zeros: the arithmetic dilation transform E can carry a zeta factor in its Mellin transform. A broad match was therefore **VOID as evidence that the finite arithmetic matrix caused the match**. This is an algebraic attribution problem, not necessarily a hidden software oracle.

R5b then asked a sharper question. Reported first-zero errors were:

| x | Weil ground-state error | Raw prolate-only error | Finite discriminator |
|---|---:|---:|---|
| 9 | 1.5823×10⁻³⁴ | 1.1480×10⁻¹⁹ | About 15 orders worse: UNVERIFIED under the frozen 10/20-order rule. |
| 13 | 2.4363×10⁻⁵⁵ | 2.9293×10⁻³⁰ | About 25 orders worse: additional finite arithmetic accuracy observed. |
| 14 | 1.0652×10⁻⁶⁰ | 4.0480×10⁻³³ | About 28 orders worse: additional finite arithmetic accuracy observed. |

The even-projected control led to the same classifications. Thus “the dilation identity explains all the extra accuracy” is too strong; “extra accuracy proves the missing theorem” is also too strong. The measured residual/gap ratios did not give a usable convergence bridge, and the tested commutators were far too large relative to the relevant ground-state gaps.

[R6][AR6] aligned the native spaces more carefully and found strong finite candidate/ground-state alignment absent from controls, but no successful near-commutation principle. [R7][AR7] restored the missing integral direction—the mathematical identity contribution, not a new prime—and found it did not mediate that alignment. Large archimedean, pole, and arithmetic contributions canceled in a manner related to the published radical/range-E mechanism. These statements concern particular spaces and finite approximations; they do not contradict a positive gap on a different fixed compact-support class.

### R8–R15: translating the human pictures into falsifiable models

| Round | Concrete translation | What landed |
|---|---|---|
| [R8][AR8] | Prime logarithms as frequencies on a finite torus; recover them from complex trace data. | Small reconstructions worked, controls worked too. Unique factorization explains rational independence of prime logs; no special physical hologram followed. |
| [R9][AR9] | Mirror exchange as theta/Poisson duality. | The lattice origin contributes the constant term needed for the homogeneous reciprocal law. This is a real role for **1 as identity**, not as prime. Symmetry still allows off-line quartets. |
| [R10][AR10] | Look for a robust positive native pullback. | Authentic finite positivity, but extremely small normalized floors; the preregistered robust-coercivity target failed. This is not a requirement that RH itself have a uniform positive margin. |
| [R11][AR11] | A two-sided return/monodromy operator. | The chosen unitary factor forced the line by construction for fake controls too. Adding gain moved it. No zeta identification. |
| [R12][AR12] | Observer-loop consistency and information-preserving geometry. | Loops closed even off the critical line; a parameter-dependent metric made transport isometric there too. Consistency plus a freely chosen ruler cannot select RH. |
| [R13][AR13] | Common wavelength / golden coherence across Odlyzko blocks. | Frozen golden-ratio superiority tests failed. A promising half-window feature did not survive its paired control. |
| [R14][AR14] | “Golden ocean” prime-signal scale. | A correlation peak drifted with scale and endpoint, rather than selecting φ. A scalar Fibonacci recurrence bounded in both time directions has only the zero solution; this is a scoped toy fact, not a ban on golden geometry. |
| [R15][AR15] | Fibonacci spring medium with prime-power excitation. | A concrete self-adjoint finite model, but spectral controls and localization failed the proposed discriminatory gates. Prime inputs did not automatically become the desired zeta spectrum. |

These tests preserved useful distinctions: medium versus source, topology versus metric, identity versus prime, and observable consistency versus genuine spectral constraints.

## 5. GHP geometry, mirrors, gears, and information

The sketches were productive when converted into equations and controls. They did not establish that reality is a hologram or that primes are physical vibrations.

- **Nested gears:** periods 2,3,5 repeat after 30; adding 7 gives 210. This is a finite sieve. Its survivors include composites: with 2,3,5 removed, 49 still survives. Composite coprime gears produce periodicity and Fourier peaks too. Adding more prime gears improves the sieve; it does not turn a finite repeating mask into all primes. [Prime gears][GEARS]
- **“Every prime is one dimension”:** prime-exponent vectors encode integers exactly by unique factorization. Replacing the vector with only its coordinate sum loses information. The integer 1 is the empty product, negative integers add a sign, and zero lies outside this multiplicative representation.
- **Balanced ternary:** three digits in {−1,0,+1} give 27 labels, −13 through 13. Cyclic addition modulo 27 and coordinatewise addition in (Z/3Z)³ are different structures. The number of labels does not select zeta.
- **Observer tomography:** axis line sums of a 3×3×3 cube have rank 19 and an eight-dimensional invisible space over GF(3). Adding six face-diagonal families gives rank 27. This is a concrete information-recovery result, known in substance as discrete tomography—not RH or authentication. An attacker who replaces both data and its consistent checks is a different problem. [D18][D18]
- **Mirrors and unitary completion:** a unitary whole can contain a compressed subsystem with nonreal resonances. The Halmos one-step completion is not automatically a power dilation. Mirror-pair exchange has positive and negative directions; checking only symmetric directions can hide the latter. [Mirror inertia][MIRROR], [D6][D6]
- **Golden billiards, Metatron graphs, and the prime horn:** geometric models or visualizations were constructed; the tested golden selections did not beat the required controls. A horn with prime radii does not therefore resonate at prime frequencies. Acoustic modes require an operator and boundary conditions. [Horn][HORN], [Graph][GRAPH]
- **Lee–Yang analogy:** positive coefficients and a palindromic polynomial alone do not force zeros onto a circle. The relevant extra hypotheses matter. No representation and convergence theorem connecting the tested toy to ξ was supplied. [Lee–Yang][LEE]

Negative primes ±p are associates in the integers, not two independent prime species. φ=(1+√5)/2 is important in many settings, but no privileged φ selection survived these lab controls. A shared visual appearance, a broken mirror, or “everything is connected” is not evidence for a mathematical implication.

## 6. The D-series: strongest surviving results and corrections

### D4–D7: the small-room certificate

The retained advertised L=.7, T=120 all-function bounds are **1.031×10⁻¹³ even** and **5.859×10⁻¹¹ odd**, under the reviewed analytic machinery. They cover complex functions by the correct integrated parity/real-imaginary decomposition. The old pointwise identity |F1+iF2|²=|F1|²+|F2|² was false; its cross term integrates away in the relevant setting. The old odd rounded value 5.86×10⁻¹¹ was too high and withdrawn.

Fable and Opus used independent implementations but shared a machine and Arb build. Opus's reported sandwich widths were corrected to **2.34×10⁻¹¹ even** and **5.75×10⁻¹⁴ odd**. These compare the reduced-form floor with matching trial information, not a solved all-window full-W profile. Text proofs and executable interval evidence are not the same as a fully formalized proof. [D7][D7], [D20][D20]

### D8–D11: useful structure, restricted scope

The sharp compact-support translation inequality reduces to finite path graphs:

\[
\Re\langle f,T_af\rangle\le\cos\!\left(\frac\pi{\lceil2L/a\rceil+1}\right)\|f\|^2.
\]

It is known in substance. Replacing prime correlations by this worst-case bound lost the cancellation needed by the chosen certificate. This does **not** prove that all attempts to bound primes are impossible. The stronger historical claim that every positive amount of this relaxation fails was corrected: a strictly positive margin allows a sufficiently small bounded perturbation. [D8][D8], [D9][D9]

D10 found a sign obstruction to one local positive-conductance/gauge representation, not to all positivity proofs. A positive toy matrix can have the same frustrated signs. Completion of squares isolated a Schur balance; D11 compressed part of its finite calculation to 32 Krylov steps, but still required a full-size verifier. [D10][D10], [D11][D11]

### D12–D20: sensitivities, parity, and the moving ruler

Parameter scans showed tiny margins and parity-dependent reactions to weights, shifts, and exponent changes. These are finite observations. They did not establish that every prime power is essential to full W, that σ=1/2 is the unique allowed exponent at fixed L, or that a universal margin law had been measured.

For a simple eigenvalue, the first directional effect is λ′(0)=⟨u,Du⟩. Weyl's bound says perturbations smaller than a positive margin cannot cross zero; it does not say larger perturbations must do so. Norm size alone cannot explain a sign-specific failure.

Some scans changed B, β, T, or the basis together with the proposed arithmetic mutation. D20 called this a moving ruler: a worse lower bound was being mistaken for a worse underlying form. Its audit also identified a local endpoint-parity correlation formula, but parity alone does not fix every global shift-correlation sign. No new global parity theorem was obtained. [D20][D20]

### D21: genuine negative witnesses, and claims that were withdrawn

| Mutation at L=.7 | Surviving conclusion after D21.1/D24 |
|---|---|
| Delete the n=2 contribution, keeping n=4 | Explicit negative witnesses for the modified **full W**, both parities. |
| Delete all arithmetic contributions | Explicit negative full-W witnesses, both parities. |
| Delete n=4 | The tested waves were positive, sometimes by a separate certified lower route; this neither proves all-wave positivity nor shows a negative witness. |

Eight exported negative witness cases passed the D24 saved-endpoint audit. One delete-4 direct interval was huge and crossed zero: that route was unresolved, despite a separate R128 lower bound proving positivity for that wave. One additional survivor lacked an exported endpoint for complete replay. Removing n=2 alone is not the same mutation as removing all powers of prime 2. [D21][D21], [D24][D24]

### D22/D24: certificate error found; positivity survived a conservative repair

D24 found a missing factor ρ²=4 in the K-node Gauss quadrature allowance used by the D22 matrix machinery. It also found that the old floating checker could underflow tails and checked positivity rather than the exact advertised shifted lower bound.

The repair enlarged the finite error allowance and checked the **shifted Schur condition using exact rational arithmetic**. The resulting conservative bounds below passed on the saved evidence. This was not a fresh matrix reconstruction. Analytic and source dependencies remain part of the statement.

| L | T | Repaired even lower bound | Repaired odd lower bound |
|---:|---:|---:|---:|
| .4 | 160 | 1.44919×10⁻⁴ | .0124019 |
| .5 | 160 | 7.14785×10⁻⁷ | 1.42134×10⁻⁴ |
| .6 | 160 | 1.10135×10⁻⁹ | 4.12866×10⁻⁷ |
| .7 | 160 | 2.67167×10⁻¹³ | 1.58596×10⁻¹⁰ |
| .7 | 240 | 3.37581×10⁻¹³ | 2.03304×10⁻¹⁰ |

The original high-precision D22 endpoints are **VOID as certified-as-written**; these conservative repairs retain positivity. D7's separate independent quadrature allowance is not invalidated by this finding. These are lower certificates, not exact values of mW(L). [D24][D24]

D24 also showed that all eight existing trial-4 waves already had rigorous scalar lower scores exceeding 1.1 times their original comparison floors. Better upper-tail integration alone cannot make those unchanged candidate/floor pairs close a 10% bracket.

Finally, at smaller L the certificate retained invisible shifts while the selector omitted them. Removing those redundant shifts strengthens the lower approximation without changing full W. This suggests an inexpensive, specific repair—not a new RH principle.

### D23/D24: prolate resemblance is not an energy theorem

D23 reported overlaps .997–.9999 with leading prolate functions. Its construction script was absent from the reviewed commit, so the implementation claim remains **UNVERIFIED**, though floating outputs are recorded.

Even a correct overlap is not enough. For normalized v and a true first eigenvector u1 of a Hermitian finite compression,

\[
R_N(v)\ge\lambda_1+(\lambda_2-\lambda_1)(1-|\langle u_1,v\rangle|^2).
\]

When λ1 is tiny compared with the gap, a tiny angle error can overwhelm it. The saved L=.7 numbers gave conditional excess-energy diagnostics about **33 times the minimum even and 104 times odd**. These were not new interval-certified exclusions, but they decisively explain why a pretty overlap is insufficient.

Likewise,

\[
m_W(L)\le\inf_\Omega W_L(\psi_\Omega)
\]

is a variational **upper bound**, not an equality. Equality requires a new argument, such as adequate ground-state approximation in the form norm. D23's raw prolate also differs from the transformed and constrained candidate used in CCM.

The fitted expression log λ≈A−C e^(2L), C≈10–11, described four lower-certificate values. Its quoted 2–7% fit metric concerned neighboring log-slopes, not relative errors in λ. It is not an established asymptotic law for the true full-W minimum. Neither “64” nor “10–11” has been derived for this lab object. [D24][D24]

## 7. Prior art and novelty boundary

| Source | What it supplies; what it does not |
|---|---|
| Slepian–Pollak, 1961, [Prolate Spheroidal Wave Functions, Fourier Analysis and Uncertainty—I](https://doi.org/10.1002/j.1538-7305.1961.tb03976.x) | Concentration eigenfunctions and commuting differential structure; not a theorem equating them to the Weil ground state. |
| Landau–Widom, 1980, [Eigenvalue distribution of time and frequency limiting](https://doi.org/10.1016/0022-247X(80)90241-3) | A concentration-spectrum transition law in its own asymptotic regime; not an automatic prediction of this lab's bottom eigenvalue. |
| Connes–Consani, 2021, [Weil positivity and Trace formula, the archimedean place](https://alainconnes.org/wp-content/uploads/Selecta.pdf) | Earlier prolate/positivity structure with specific spaces and constraints. Do not omit those constraints. |
| Connes–Consani, 2021, [Spectral Triples and Zeta-Cycles](https://arxiv.org/abs/2106.01715) | Earlier arithmetic transforms of prolates and small Weil eigenvectors. The general connection is not our invention. |
| Connes–Consani–Moscovici, 2025, [Zeta Spectral Triples, v1](https://arxiv.org/html/2511.22755v1) | A particular transformed candidate and convergence results; missing simple/even ground-state and sufficiently strong candidate/ground-state bridge conditions remain. |
| Zhu, 2026, [Weil positivity in compact windows…, v2](https://arxiv.org/html/2608.24827v2) | Prior compact-window work; the exact profile is conjectural and its constant fitted. An RH-conditional bound cannot be recycled as an unconditional RH proof. Version pinning matters. |
| Hale–Trefethen, 2008, [New quadrature formulas from conformal maps](https://appliedmaths.sun.ac.za/~nhale/publications/HaleTrefethen2008.pdf), Theorem 2.1 | The node-count/error convention relevant to the D24 factor-four repair. |

This table follows the scoped [D24 primary-source audit][D24], not an exhaustive novelty search or re-refereeing of each paper. Earlier finite-field, Li, quantum-chaos, and scattering experiments were replications of established programs. Even a fully sound independent certificate within an already treated window is not automatically a new theorem.

## 8. Human contributions and reusable Aukora technology

Peter's mirror, standing-wave, and observer descriptions helped isolate questions about symmetry, boundary conditions, compression, and hidden directions. Mika's nested gears supplied a particularly clear finite-sieve hypothesis. The “ocean versus pebble” correction separated a medium from its excitation, leading to an actual spring model. Requests for two-sided and ternary models encouraged tests of sign, information loss, and reconstruction.

Those are contributions to **hypothesis formation and experimental design**, not evidence that the metaphors describe physical reality or that known mathematics was newly invented here. Archimedes/Apollonius/Viviani-style geometric thinking can guide decompositions; a family connection or visual resemblance does not establish mathematical provenance.

The strongest reusable engineering lessons are:

1. **Versioned knowledge:** retain old claims, but retrieve their corrections with them. A memory system that remembers enthusiasm and forgets retractions becomes less reliable with more context.
2. **Source versus view:** full W is the source object; R and matrix compressions are derived views. Keep the transformation, normalization, and inequality direction in the metadata.
3. **Nullspace-aware observation:** multiple consistent summaries can leave invisible information. Rank and reconstruction tests are more informative than a visualization.
4. **Consistency is not authentication:** a coherently altered dataset can satisfy all its own checks. Anchor provenance outside the data being checked.
5. **Independent checkers:** cheap exact endpoint logic can catch rounding, underflow, and theorem/implementation mismatches. Agreement between two similar floating programs is weaker evidence.
6. **Task-relevant approximation:** preserving vector norm or visual shape need not preserve a tiny energy, stability margin, or downstream decision.
7. **Gated compute:** rule out an impossible target cheaply before spending on precision. Preserve failed runs and predictions.

These principles can inform KIRA/Aukora memory and evaluation systems. This report does not claim a production implementation or measured commercial benefit.

## 9. The actual blockers and next test

**Immediate blocker:** certify a sufficiently tight comparison between an all-function lower floor and the complete energy of an explicitly frozen wave. Current prolate resemblance and reduced-form scans do not do that.

**Structural blocker:** obtain a valid bridge from the tractable candidate/operator to the exact Weil form, in the right domain and norm, with errors small relative to the relevant scale. Known concentration formulas alone do not supply it.

**RH blocker:** prove the required nonnegativity for every admissible test function / every support size. More finite windows, or a fitted rate for a lower approximation, do not supply this universal argument.

The current [D25 protocol][D25] is **PREDICTED and unrun in this snapshot**. It replaces the broad new prolate scan with one pilot: odd L=.4; certify the visibility-filtered lower form at T_R=160; retain the existing frozen trial-4 wave; reject immediately if its known energy is already too high; otherwise score at T_score=512 using a mass-conditioned tail bound. Cap: 60 single-core CPU-minutes and 90 wall minutes. No new candidate, larger window, or zero-informed tuning.

The tail idea uses actual remaining Fourier mass rather than only a loose derivative majorant. It is a proposed improvement to an error bound, not a measured gain yet. A successful pilot would be a local bracket or validated tail improvement, not a prolate identity, an asymptotic law, or RH.

## 10. Giving this to Qwen without teaching it false confidence

Qwen's official repository lists **Qwen/Qwen3.8-27B**. Reading this report gives the model context; storing it in a retrieval system gives persistent external access. Neither changes model weights. [Official Qwen repository](https://github.com/QwenLM/Qwen3.8/blob/main/README.md).

Actual fine-tuning is a separate training job. Nebius documents supervised full-weight and LoRA post-training, but support for this exact Qwen variant was not confirmed in the managed training catalog checked for this report. Running an inference endpoint on Nebius does not itself establish that it can train that model. A self-hosted GPU deployment is a different setup from a managed inference API. [Nebius overview](https://docs.tokenfactory.nebius.com/post-training/overview), [training-model catalog](https://docs.tokenfactory.nebius.com/post-training/models).

Start with retrieval and tool-checked evaluation. Compare the untouched model against the same model with the corrected pack and, separately, with repository/checker access. Test whether it distinguishes W from R, notices a missing tail, and rejects a false symmetry argument. Do not grade it on agreement with our preferred story.

If training is later justified, curate reviewed examples with the problem, a concise verifiable derivation, answer, domain, and correction provenance. Do not bulk-train on raw optimistic chats or let the model certify its own generated claims. Split evaluation by mathematical problem family and use unseen variants; adjacent paraphrases of training examples are not a clean test. Record model revision, quantization, training configuration, and evaluation results. No such training job was started for this report.

### Plain-language ending

We have built a few small rooms and checked that every allowed wave in those rooms stays on the safe side of a mathematical balance. We also discovered that some of our rulers bent, and some waves that looked almost identical had very different balance scores. Fixing those mistakes is real progress in understanding the experiment. The unsolved part is a rule that works for every room, however large—not a prettier mirror or a more confident AI.

## Source snapshots

GHP records were read at `1849a0062a71c60d5b684ae652f7b049e080cbd1`. Aukora records were read without changing its checkout, principally from `633e91cbb24f8574a4bbbe55e1b3b8cc0ada4160` (`lab/millennium-v1-codex`), with the merged historical branch also inspected. Links below identify those snapshots; GitHub access to every older blob was not independently replayed this turn. If a model cannot fetch a link, supply the file contents; it must not pretend to have read them. This pack is a new local synthesis, not a replacement for authors' historical files.

[D20]: https://github.com/aumara-xyz/golden-horizon-principle/blob/1849a0062a71c60d5b684ae652f7b049e080cbd1/experiments/astra_d20_review/RESULTS.md
[D24]: https://github.com/aumara-xyz/golden-horizon-principle/blob/1849a0062a71c60d5b684ae652f7b049e080cbd1/experiments/astra_d24_review/RESULTS.md
[D25]: https://github.com/aumara-xyz/golden-horizon-principle/blob/1849a0062a71c60d5b684ae652f7b049e080cbd1/experiments/astra_d24_review/PREDICTIONS.md
[D21]: https://github.com/aumara-xyz/golden-horizon-principle/blob/1849a0062a71c60d5b684ae652f7b049e080cbd1/experiments/fable_d21_test1/RESULTS.md
[D6]: https://github.com/aumara-xyz/golden-horizon-principle/blob/1849a0062a71c60d5b684ae652f7b049e080cbd1/experiments/weil_hidden_modes/FABLE-ROUND-D6-RESULTS.md
[D7]: https://github.com/aumara-xyz/golden-horizon-principle/blob/1849a0062a71c60d5b684ae652f7b049e080cbd1/experiments/weil_hidden_modes/OPUS-ROUND-D7-RESULTS.md
[D8]: https://github.com/aumara-xyz/golden-horizon-principle/blob/1849a0062a71c60d5b684ae652f7b049e080cbd1/experiments/fable_d8_confinement/REPORT.md
[D9]: https://github.com/aumara-xyz/golden-horizon-principle/blob/1849a0062a71c60d5b684ae652f7b049e080cbd1/experiments/codex_d9_exact_scores/RESULTS.md
[D10]: https://github.com/aumara-xyz/golden-horizon-principle/blob/1849a0062a71c60d5b684ae652f7b049e080cbd1/experiments/codex_d10_joint_geometry/RESULTS.md
[D11]: https://github.com/aumara-xyz/golden-horizon-principle/blob/1849a0062a71c60d5b684ae652f7b049e080cbd1/experiments/fable_d11_joint_balance/RESULTS.md
[D18]: https://github.com/aumara-xyz/golden-horizon-principle/blob/1849a0062a71c60d5b684ae652f7b049e080cbd1/experiments/fable_d18_observer_tomography/RESULTS.md
[GEARS]: https://github.com/aumara-xyz/golden-horizon-principle/blob/1849a0062a71c60d5b684ae652f7b049e080cbd1/experiments/prime_gears_codex/RESULTS.md
[MIRROR]: https://github.com/aumara-xyz/golden-horizon-principle/blob/1849a0062a71c60d5b684ae652f7b049e080cbd1/experiments/mirror_inertia_lemma/RESULTS.md
[HORN]: https://github.com/aumara-xyz/golden-horizon-principle/blob/1849a0062a71c60d5b684ae652f7b049e080cbd1/experiments/prime_horn/README.md
[GRAPH]: https://github.com/aumara-xyz/golden-horizon-principle/blob/1849a0062a71c60d5b684ae652f7b049e080cbd1/experiments/metatron_prime_return/RESULTS.md
[LEE]: https://github.com/aumara-xyz/golden-horizon-principle/blob/1849a0062a71c60d5b684ae652f7b049e080cbd1/experiments/lee_yang_bridge/RESULTS.md
[ASUM]: https://github.com/aumara-xyz/aukora-deep/blob/633e91cbb24f8574a4bbbe55e1b3b8cc0ada4160/research/millennium-lab-v1/LAB-SUMMARY.md
[AR5]: https://github.com/aumara-xyz/aukora-deep/blob/633e91cbb24f8574a4bbbe55e1b3b8cc0ada4160/research/millennium-lab-v1/RESULTS-codex-r5.md
[AR5b]: https://github.com/aumara-xyz/aukora-deep/blob/633e91cbb24f8574a4bbbe55e1b3b8cc0ada4160/research/millennium-lab-v1/RESULTS-codex-r5b.md
[AR6]: https://github.com/aumara-xyz/aukora-deep/blob/633e91cbb24f8574a4bbbe55e1b3b8cc0ada4160/research/millennium-lab-v1/RESULTS-codex-r6.md
[AR7]: https://github.com/aumara-xyz/aukora-deep/blob/633e91cbb24f8574a4bbbe55e1b3b8cc0ada4160/research/millennium-lab-v1/RESULTS-codex-r7.md
[AR8]: https://github.com/aumara-xyz/aukora-deep/blob/633e91cbb24f8574a4bbbe55e1b3b8cc0ada4160/research/millennium-lab-v1/RESULTS-codex-r8.md
[AR9]: https://github.com/aumara-xyz/aukora-deep/blob/633e91cbb24f8574a4bbbe55e1b3b8cc0ada4160/research/millennium-lab-v1/RESULTS-codex-r9.md
[AR10]: https://github.com/aumara-xyz/aukora-deep/blob/633e91cbb24f8574a4bbbe55e1b3b8cc0ada4160/research/millennium-lab-v1/RESULTS-codex-r10.md
[AR11]: https://github.com/aumara-xyz/aukora-deep/blob/633e91cbb24f8574a4bbbe55e1b3b8cc0ada4160/research/millennium-lab-v1/RESULTS-codex-r11.md
[AR12]: https://github.com/aumara-xyz/aukora-deep/blob/633e91cbb24f8574a4bbbe55e1b3b8cc0ada4160/research/millennium-lab-v1/RESULTS-codex-r12.md
[AR13]: https://github.com/aumara-xyz/aukora-deep/blob/633e91cbb24f8574a4bbbe55e1b3b8cc0ada4160/research/millennium-lab-v1/RESULTS-codex-r13.md
[AR14]: https://github.com/aumara-xyz/aukora-deep/blob/633e91cbb24f8574a4bbbe55e1b3b8cc0ada4160/research/millennium-lab-v1/RESULTS-codex-r14.md
[AR15]: https://github.com/aumara-xyz/aukora-deep/blob/633e91cbb24f8574a4bbbe55e1b3b8cc0ada4160/research/millennium-lab-v1/RESULTS-codex-r15.md
