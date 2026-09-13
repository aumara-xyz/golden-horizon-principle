# D20 reading and source map

Reviewed base: `fd36b054211492dfc8872126280114aeca21f308`, 2026-09-13. [RESULTS.md](RESULTS.md) is the integrated review. [PREDICTIONS.md](PREDICTIONS.md) contains exactly three future tests, none executed in D20.

## Requested reading, completed in the handoff's order

The primary reviewer read the hub and each listed report in full, and inspected the D19 figure. Three parallel supporting reviews examined perturbation/parity algebra, decay/operator identification, and primary-source scope; their findings were checked and consolidated into RESULTS.md. This is not three independent numerical certificate replays.

| Item | Repository link |
|---|---|
| Hub | [Reimann Research/README.md](../../Reimann%20Research/README.md) |
| D20 instructions | [ASTRA-HANDOFF-D20.md](../../Reimann%20Research/ASTRA-HANDOFF-D20.md) |
| D6 corrections and form domain | [FABLE-ROUND-D6-RESULTS.md](../weil_hidden_modes/FABLE-ROUND-D6-RESULTS.md) |
| D7 independent certificate report | [OPUS-ROUND-D7-RESULTS.md](../weil_hidden_modes/OPUS-ROUND-D7-RESULTS.md) |
| D10 joint geometry/Schur completion | [RESULTS.md](../codex_d10_joint_geometry/RESULTS.md) |
| D11 Krylov/interval balance | [RESULTS.md](../fable_d11_joint_balance/RESULTS.md) |
| D8 confinement | [REPORT.md](../fable_d8_confinement/REPORT.md) |
| D12 prime necessity | [RESULTS.md](../fable_d12_prime_necessity/RESULTS.md) |
| D13 weights | [RESULTS.md](../fable_d13_prime_weights/RESULTS.md) |
| D14 interference | [RESULTS.md](../fable_d14_interference/RESULTS.md) |
| D15 Dirichlet forms | [RESULTS.md](../fable_d15_dirichlet/RESULTS.md) |
| D16 places | [RESULTS.md](../fable_d16_places/RESULTS.md) |
| D17 powers/exponent | [RESULTS.md](../fable_d17_squares_exponent/RESULTS.md) |
| D19 and D19b | [RESULTS.md](../fable_d19_emergent_line/RESULTS.md), [figure](../fable_d19_emergent_line/d19_emergent_line.png) |
| D18 separate tomography lane | [RESULTS.md](../fable_d18_observer_tomography/RESULTS.md) |

## Additional evidence used to test the reports

- [D9 complete fixed-wave scores](../codex_d9_exact_scores/RESULTS.md): the logical distinction between a negative lower form and a negative exact score was already repaired there.
- [D15 source](../fable_d15_dirichlet/d15_slack.py), [D16 source](../fable_d16_places/d16.py), [D17 source](../fable_d17_squares_exponent/d17.py), [D19 source](../fable_d19_emergent_line/d19.py): analytic identification of `sym - beta`, `beta*I`, and adaptive B/T/N. These files were inspected, not executed.
- D12 saved [coarse metadata](../fable_d12_prime_necessity/d12_results.json) and [fine metadata](../fable_d12_prime_necessity/d12_fine.json); D13/D16 saved removal results; D19 [predictions](../fable_d19_emergent_line/PREDICTIONS.md), [bisection data](../fable_d19_emergent_line/d19_results.json), and [secant data](../fable_d19_emergent_line/d19b_susceptibility.json).
- The D12 sweep assembly script, D15 original grid assembly script, and D19b secant-generation source were not found in their respective experiment directories. Later shared code and logs are not a substitute for those exact missing sources.
- No new numerical experiment, spectral solve, original certificate replay, or golden-ratio/zero-informed construction was run. Algebraic examples and differentiations in RESULTS.md are explicit proofs, not retrospective prediction outcomes.

## Primary references and access limitations

1. H. Yoshida (1992), *On Hermitian forms attached to zeta functions*, pp. 281–325. Its Theorem 1 was read as reproduced in Connes–Consani below; the original chapter was not obtained. Do not label that an audit of Yoshida's original proof.
2. A. Connes and C. Consani (2021), *Weil positivity and trace formula, the archimedean place*, Selecta Mathematica 27, article 77. [Author-hosted text](https://alainconnes.org/wp-content/uploads/Selecta.pdf), especially Theorem 1, p. 2. The author PDF's date is July 4, 2021.
3. E. Bombieri (2000), *Remarks on Weil's quadratic functional in the theory of prime numbers, I*, Rendiconti Lincei, Matematica e Applicazioni, series 9, vol. 11, pp. 183–233. [Original archive](https://www.bdim.eu/item?fmt=pdf&id=RLIN_2000_9_11_3_183_0). Relevant original text: Theorems 3, 5, 12; pp. 225–228. The archive HTTPS endpoint failed in this environment; a public HTTP download of the same archival PDF was read by the source reviewer and its extracted theorem text checked by the primary reviewer.
4. X. Zhu (2026), *Weil positivity in compact windows: a finite reduction, certified two-sided bounds, and a Landau–Widom decay law*. [Version-pinned record](https://arxiv.org/abs/2608.24827v2), [v2 text](https://arxiv.org/html/2608.24827v2). Submission August 25; v2 September 2; title page September 3. The v1/v2 author metadata change is disclosed by the record. This review verifies the statement's scope, not the preprint's entire proof or external software.
5. H. J. Landau and H. Widom (1980), *Eigenvalue distribution of time and frequency limiting*, Journal of Mathematical Analysis and Applications 77, pp. 469–481. [DOI](https://doi.org/10.1016/0022-247X(80)90241-3). The fixed-parameter transition was checked through Slepian's primary author exposition below; the original paper was not independently audited end to end.
6. D. Slepian (1983), *Some comments on Fourier analysis, uncertainty and modeling*, SIAM Review 25, pp. 379–393. [Primary text](https://www.math.ucdavis.edu/~saito/data/ONR15/slepian83.pdf), p. 387, equation (25).
7. S. Karnik, J. Romberg, and M. A. Davenport (2020 preprint), *Improved bounds for the eigenvalues of prolate spheroidal wave functions and discrete prolate spheroidal sequences*. [arXiv:2006.00427v2](https://arxiv.org/pdf/2006.00427v2), §2.2 and Theorem 3. Useful for distinguishing concentration-operator bounds from a Weil-operator comparison.
8. X.-J. Li (1997), *The positivity of a sequence of numbers and the Riemann hypothesis*, Journal of Number Theory 65, pp. 325–333. [Publisher record](https://www.sciencedirect.com/science/article/pii/S0022314X97921375). Criterion also recalled in [Li's 2004 primary paper](https://arxiv.org/pdf/math/0403148). Original 1997 full proof not retrieved.
9. B. Rodgers and T. Tao (2018 preprint; 2020 publication), *The de Bruijn–Newman constant is non-negative*. [arXiv:1801.05914](https://arxiv.org/abs/1801.05914), [Forum of Mathematics, Pi 8, e6](https://doi.org/10.1017/fmp.2020.6), Theorem 1.
10. T. Tao (2010), [*254A, Notes 3a: Eigenvalues and sums of Hermitian matrices*](https://terrytao.wordpress.com/2010/01/12/254a-notes-3a-eigenvalues-and-sums-of-hermitian-matrices/). Variational principle and Weyl bounds; the small matrix counterexamples and derivative deductions are displayed explicitly in the review.
11. NIST Digital Library of Mathematical Functions, [25.15.5](https://dlmf.nist.gov/25.15.E5), the Dirichlet-L functional equation. Cited to distinguish that identity from a prime-exponent-only mutation.

External mathematical statements are attributed, not silently promoted from preprint assertions to independently verified theorems. No novelty claim is based on failing to find a matching search result. No random physical analogy serves as prior art or evidence for RH.
