# Status, the two 0.7s, and the human contribution

2026-09-06. Scope: evidence-backed synthesis, not a new computation, certificate replay, or novelty assessment by exhaustive literature search.

## D7 update (same date, supersedes the pending-reconstruction status below)

Opus now reports an independent derivation and implementation in OPUS-ROUND-D7-RESULTS.md (commit e09a3d6), supporting the same advertised even/odd constants. This is implementation independence on the same machine and Arb build, not independent arithmetic infrastructure. Its alternative quadrature bound removes dependence on the unresolved Trefethen constant citation for this reconstruction. Codex has inspected the report and selected outputs, not replayed the complete implementation. The central research blocker remains all-window positivity.

Codex identified overstated minimum-sandwich precision in D7: displayed endpoint centres give relative widths about 2.34e-11 even and 5.63e-14 odd, not 2.3e-14 and 5.6e-15. Rigorous summaries must also use outward endpoints of the serialized balls, not just printed centres. This readout discrepancy does not threaten the advertised rounded lower constants. See the hub's D7-READOUT.md. The remaining sections preserve the pre-D7 assessment and contribution history.

## The two 0.7s

The user correctly remembered GHP's c=7/10. GHP_CORE_v3.md section 3 records the central charge of the antiferromagnetic Fibonacci golden chain's continuum theory, tricritical Ising. This is established prior mathematics/physics: [Feiguin et al., PRL 98,160409 (2007)](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.98.160409), [preprint](https://arxiv.org/abs/cond-mat/0612341). The repository reports reproducing aspects of it; that computation was not re-audited for this note.

The Weil experiment's L=7/10 is instead the half-width of allowed test-function support in a fixed logarithmic-coordinate convention. Its original PREDICTIONS.md selected L=0.4,0.7,1.0 before compute. No equation derives L from a central charge. Numerical equality between an adjustable cutoff and a theoretical invariant is not evidence of a common mechanism. A proposed bridge would need defined objects, a map, and normalization-independent predictions, not matching decimals.

The more defensible connection is methodological: architecture does not by itself determine dynamics. Fibonacci structure does not force every dynamical quantity to equal phi; prime-coordinate labels and 27 states likewise do not force a particular transition rule or spectrum.

## Current RH-related status

Fable D6 reports interval-certified positivity of the bounded lower-envelope form R_T at L=0.7, T=120, all parity sectors. Advertised lower bounds: even 1.031e-13, odd 5.859e-11, times squared norm. Extension to the exact Weil form uses W>=R_T, with the specified form domain and extended-value convention. Complex-function decomposition, pole signs, and downward rounding were corrected during audit.

Codex has inspected the reports and selected supporting files, but has NOT independently reconstructed or replayed the complete D5/D6 certificate. Treat the result as reported certification with outstanding independent validation, not an independently endorsed theorem. D6's sampled same-form agreement (max difference 2.6e-11) is a consistency check, not an independent verification of a 1.031e-13 lower bound. Tail-error control and analytic lemmas matter.

No novelty is claimed by Fable. Its report identifies the compact-window route as a reproduction at a smaller window than prior work. No RH proof, new all-window inequality, or newly identified zeta operator has been obtained.

## How the friend's input helped

| Human input | Mathematical translation | What the toy established | Limit |
|---|---|---|---|
| Nested gears and conjunctions | Periodic divisibility masks; Chinese remaindering | Exact periods 6,30,210,2310; next-prime-square obstructions | Known sieve mathematics, not new prime counting |
| Primes as separate foundational layers | Prime-exponent coordinates | Exact reconstruction of 1000 integers; collapsing axes leaves 10 labels | Abstract coordinates, not physical dimensions |
| Observer sees a repeating pattern | Coarse-grained mask of clock states | Adding period4 doubles the configuration period but not the observed mask period | Not a quantum or consciousness mechanism |
| -13..13 and wrapping | Balanced ternary labels with alternative group laws | 27-cycle versus three ternary coordinates have different additive orders | Labels alone choose neither dynamics nor geometry |
| Wave-field visualization | Fourier spectrum of a periodic mask | Composite-period controls also have spikes | Not replication of the video's particular code or prime-gap spectrum |

These contributions generated understandable hypotheses and discriminating controls. Credit belongs to the friend for the intuitive framing in this collaboration, not for inventing established sieve theory. The observations that survived and the hypotheses that failed are both useful. Ideas involving consciousness dimensions, string theory, or a physical prime field were not established or implemented.

## Blockers and next steps

1. Verification: independent implementation/replay of the same R_T; inspect analytic bounds and certify low-score directions to sufficient precision. A same-machine replay is not an independent implementation. Another machine alone does not eliminate shared derivation errors.
2. Scope: fixed-window positivity does not cover arbitrary compact supports. No common positive gap across all support sizes is required by RH, but positivity must hold for every admissible test function. No mechanism extending this certificate to that quantifier has been supplied.
3. Proposed physical/spectral bridges: symmetry, ambient unitarity, phi, or topology alone do not identify the zeta spectrum. The dilation counterexample and gear controls demonstrate specific failures of such shortcuts.
4. Novelty: establish something not already provided by the existing criterion or compact-window method before calling this a new result. A more reliable reproduction can still be valuable computational work.

Priority: one bounded independent audit, followed—if successful—by a preregistered investigation of the joint restriction on prime-phase alignment and Fourier concentration for compactly supported test functions. Controls must test the full quadratic form; improved plots or separate phase estimates do not suffice. This is a proposed research question, not a discovered route around the all-window obstacle.

For engineering, a reasonable offline follow-up is testing whether a proposed compressed observer state merges histories that have different futures. The gear example motivates such a benchmark; no Aukora improvement has yet been measured or implemented.

## Plain-language conclusion

We have a reported safety certificate for every allowed ripple in one small room, and useful demonstrations of why some appealing shortcuts fail. We have not found the rule that makes every possible room safe. The shared number 0.7 does not supply that rule. This is exploratory computational mathematics worth assessing on its reproducibility and results, not a demonstrated Riemann breakthrough or a basis for claiming one in funding materials.
