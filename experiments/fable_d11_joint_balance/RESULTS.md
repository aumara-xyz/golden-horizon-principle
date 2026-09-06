# Fable D11 — independent audit of D10, and a Krylov test of the joint Schur balance (2026-09-06)
Base: research branch tip 5c22b35 (D10 fb55c90 an ancestor). Predictions committed before compute: 9369fd5 (PREDICTIONS.md). Machine: Mac, Darwin 25.1.0; /private/tmp/weil-arb-gTYWza/venv/bin/python; python-flint 0.6.0 (Arb), mpmath 1.4.1; ball precision 256 bits (512 for the doubled rerun), H built at 192 bits; mpmath 60 digits. Frozen: L = 7/10, T = 120, N = 80 per parity, m ∈ {2,4,8,16,32}, κ = +2 even / −2 odd. No zero ordinates, no φ, no new models, no enlarged L. Budget used: compute ≈ 5 min of 30 (builds 2×44 s, main runs 2×40 s, follow-ups 2×3 s, diagnostics); total ≈ 75 min of 90.

## 1. Dependency audit of D10 (D11.1)
| Dependency | How handled here | Status |
|---|---|---|
| Exact form W, position-space kernel K, ½ symmetrization, pole kernel 2cosh(r/2), prime atoms, a₀ − B | Re-derived before reading Codex's code (PROOF.md §1); K(a), K(2a) reproduced by hand | MEASURED, agrees |
| Sharp-threshold corollary ρ³ − ρ − 1 = 0, r*/2 | Re-derived; endpoint and no-atom conditions checked | correct |
| a.e. measurable-gauge extension (my preregistered "most fragile" item) | Asserted without argument in KERNEL-PROOF.md; supplied a two-line Fubini/cyclic-product proof (PROOF.md §1) | REPAIRED (not refuted) |
| Positive frustrated toy A = ½I + vvᵀ | Eigenvalues ½, ½, 7/2 by inspection (v ⟂ complement, ‖v‖² = 3); conclusion "sign pattern does not imply non-positivity" affirmed | correct |
| Householder axis, Schur identity, σ, κ_crit | Re-derived (PROOF.md §2); U orthogonality needs q₀ ≠ −1 (holds, q₀ > 0) | correct |
| Residual bracket | Re-derived and proved (PROOF.md §3) | correct |
| Finite H, p | Independently rebuilt with my own builder (d11_build.py), not D10's Opus-based build.py | see §2 |
| δ = lower bound on λmin(C) | Independently certified by my eigenbasis Gershgorin (PROOF.md §4) for every family; D10's saved values used only for comparison | see §2 |
| Quadrature-error theorem hypotheses | Checked for MY builder (PROOF.md §5); D10's H inherits Opus's derivation | analyticity and constants OK; Trefethen citation still UNVERIFIED, immaterial |
| Infinite tail/coupling bounds | Not needed for finite R_120; scoped (PROOF.md §6) | n/a |
| Control error bound in build.py (M_δ = Σ|δw| cosh(a b)) | Reviewed: valid analytic multiplier bound on the ellipse; controls used here only as INPUTS | reused, labeled |
| D10 negative finite witnesses / D9 full-W pole mutation | Rechecked in spirit by regenerating negative witnesses from my own H (§4); D9 numbers cited, not re-scored | consistent |
No substantive defect in D10 was found. One overprecise-looking display (κ_crit to 24 digits) is justified by the ~1e-40 bracket width in D10's data.

## 2. Reconstruction comparison (independent build vs D10 input)
| quantity | mine (192-bit build) | D10 (Opus builder, 256-bit) | comparison |
|---|---|---|---|
| H entries, even | radii ≤ 1.16e-22 | radii ≤ 1.38e-25 | 6400/6400 enclosures overlap; max centre difference 9.5e-22 |
| H entries, odd | radii ≤ 1.17e-22 | — | 6400/6400 overlap |
| p (80 entries), β | overlap all; β agrees to the printed digits | — | agree |
| δ even | 1.22600538345e-8 | min C 1.226005383456979e-8 | 12 digits |
| δ odd | 1.71888151806e-6 | 1.71888151805606654e-6 | 12 digits |
| σ even (m = 32 bracket) | [2.16778715e-13, 2.16778724e-13] | 2.167787235972e-13 | D10 inside my bracket |
| σ odd (m = 32 bracket) | [2.531978866614e-10, 2.531978866616e-10] | 2.531978866615e-10 | inside |
Input hashes are in d11_results_*.json (mine and D10's). My enclosures are ~1000× wider than Opus's; the entrywise agreement is to 21 digits.

## 3. The Krylov test (D11.2): can ≤ 8 steps certify σ > 0?
**Frozen discriminator: NO.** m = 8 leaves σ UNVERIFIED in both parities; the first frozen order that certifies is m = 32 in both. Label for what closed: **compressed response construction at m = 32** (32 of 79 complement dimensions), depending on a full-size δ verifier.
Even sector (‖b‖ = 0.2765, δ = 1.2260e-8, a + κ‖p‖² ≈ 0.056296):
| m | ‖r_m‖ (upper) | q-bracket width ‖r‖²/δ | σ lower | σ upper (= score of U(1, −x_m)) | verdict |
|---|---|---|---|---|---|
| 2 | 7.23e-2 | 4.26e5 | −4.26e5 | +7.03e-3 | UNVERIFIED |
| 4 | 2.43e-2 | 4.81e4 | −4.81e4 | +1.11e-3 | UNVERIFIED |
| 8 | 2.37e-3 | 4.60e2 | −4.60e2 | +1.34e-4 | UNVERIFIED |
| 16 | 1.06e-3 | 9.25e1 | −9.25e1 | +1.14e-4 | UNVERIFIED |
| 32 | 9.99e-15 | 8.14e-21 | +2.1677871544e-13 | +2.1677872363e-13 | CERTIFIED σ > 0 |
Odd sector (‖b‖ = 0.4269, δ = 1.7189e-6):
| m | ‖r_m‖ | width | σ lower | σ upper | verdict |
|---|---|---|---|---|---|
| 2 | 7.70e-2 | 3.45e3 | −3.45e3 | +1.32e-2 | UNVERIFIED |
| 4 | 3.03e-2 | 5.34e2 | −5.34e2 | +9.17e-3 | UNVERIFIED |
| 8 | 2.08e-2 | 2.51e2 | −2.51e2 | +4.54e-3 | UNVERIFIED |
| 16 | 1.15e-2 | 7.65e1 | −7.65e1 | +2.09e-4 | UNVERIFIED |
| 32 | 1.78e-21 | 1.85e-36 | +2.53197886661426e-10 | +2.53197886661611e-10 | CERTIFIED σ > 0 |
Exploratory, NOT frozen (labeled): m = 20, 24, 28 give even residuals 6.2e-4, 1.2e-4, 4.5e-5 and odd 1.6e-4, 5.6e-5, 1.4e-4, all UNVERIFIED (widths 31.6, 1.11, 0.163 even). The certification therefore happens between m = 28 and m = 32. Why (floating diagnostic, d11_spectral_diagnostic.log): in C's eigenbasis, b has 31 (even) / 32 (odd) components above 1e-6 of ‖b‖ and 36 above 1e-10; the smallest-eigenvalue direction carries a share 0.0000 of q (|b_i|/‖b‖ = 3.9e-8 even, 6.7e-6 odd); q ≈ 0.0563 (even) / 0.1495 (odd) is dominated by O(1) eigenvalues. So the tiny δ never contributes to q itself; it only enters through the crude bracket ‖r‖²/δ, which is why closure requires the residual to fall to ~1e-10·√δ and not before ~30 Krylov directions are exhausted. The near-null direction of C is essentially orthogonal to the pole coupling b.
Sensitive directions (D11.3): each σ upper endpoint IS the exact ball score of the explicit vector U(1, −x_m) (an upper bound on the minimum over the pole-mixed family); each certified lower endpoint is an operator bound (lower bound on the minimum). At m = 32 they sandwich σ to width 8e-21 (even) and 2e-27 (odd). Neither is used as the other.
Full-size reference (labeled FULL_SOLVE_DIAGNOSTIC, uses a full inverse, not part of the short certificate): σ ∈ [2.16778723582e-13, 2.16778723631e-13] even; [2.5319788666142611e-10, 2.5319788666161128e-10] odd.
Follow-ups on the two successes: (a) same frozen x_32, same δ recipe, 512-bit balls: identical verdicts and endpoints to the printed digits (d11_followup_*.json); (b) N = 40 replay, same recipe rebuilt from the 40×40 principal block of my H and p[:40]: m = 2…16 UNVERIFIED, m = 32 CERTIFIED with σ = 2.18498787e-13 (even) and 2.53219679e-10 (odd) — a different finite model, same L, same first order.
Costs: H build 44 s per parity (192-bit, my quadrature); δ certificate 4–8 s per family (full-size eigensolve + ball congruence); Krylov response < 1 s; bracket evaluation < 1 s. The speed-up over D10's full residual solve is in the response construction only; the verifier is not shortened.

## 4. Controls (D11.3), run before authentic acceptance
| control | outcome |
|---|---|
| Planted diagonal SPD (q exact = 2.2352564…) | bracket encloses q at m = 2, 4; at m = 6 (full dimension) width 1e-120 and F_6 = q. First run flagged m = 6 "False" because the harness compared overlapping balls; repaired to endpoint tests (repair kept; run-1 files retained as *_run1.*) |
| Same problem in non-orthogonal invertible coordinates | encloses the same q at every m (invariance holds for any invertible change of complement coordinates) |
| Indefinite diag(1, −1) / singular diag(1, 0) / ambiguous diag(1, 0 ± 1e-3) | all REFUSED by the δ certifier; bracket never divided |
| D10 arch-only, even (input reused) | C certified INDEFINITE (one negative direction) → SPD precondition fails, bracket refused; Krylov F_m still tabulated |
| D10 reversed-weight, even | same: C indefinite, refused |
| D10 arch-only, odd | C ⪰ 0.00764 I certified; σ upper < 0 at m = 2; direct witness score −1.0113 (negative, finite R_120 only) |
| D10 reversed-weight, odd | C certified; witness at m = 2, score −0.1042 |
| Pole sign flipped, even (my H) | C ⪰ δ; witness at m = 2, score −5.827 (D10 min R_120 ≈ −5.788) |
| Pole sign flipped, odd (my H) | stays positive: CERTIFIED at m = 32, σ = 0.234335 — the checker correctly does not reject it |
| κ − 1e-4, even | witness at m = 8, score −1.2119e-5 (finite R_120); D9's full-W witness on its own frozen wave is −6.937e-5 — different form, both negative, not conflated |
| κ − 1e-4, odd | witness at m = 32, score −5.8581e-6; D9 full-W: [−1.35e-6, −1.31e-6] |
Each control used its own certified δ or a refusal; the authentic δ was never reused for another matrix.

## 5. Prediction ledger
| prediction | outcome |
|---|---|
| P1 no numerical D10 step fails; fragile item = a.e.-gauge extension | HELD; extension repaired with a written argument |
| P1 numerics: my H overlaps D10's in every entry; δ agrees to 4 digits | HELD (6400/6400; 12 digits) |
| P2 m ≤ 8 does NOT certify in both parities | HELD |
| P3 failure through m = 32 in both parities | **FAILED**: m = 32 certifies in both. My reasoning (crude bracket pays λmax/δ on every unresolved component) was right about the mechanism but wrong about b: it has only ~31–36 significant eigencomponents, so 32 steps exhaust them |
| ‖r_8‖/‖b‖ > 1e-2 (even) | FAILED narrowly (8.6e-3); odd 4.9e-2 |
| ‖r_32‖/‖b‖ > 1e-4 (even); width > 1e-3 at every m ≤ 32 | FAILED (3.6e-14; width 8e-21 at m = 32) |
| F_m increases monotonically with m | HELD |
| P4 planted controls, refusals | HELD (after one harness repair, kept) |
| P4 even controls refused, odd controls C > 0 with witness ≤ 32 (reversed-weight uncertain) | HELD; both odd controls give witnesses at m = 2 |
| P4 even pole flip witness at m ≤ 4; odd pole flip positive | HELD (m = 2; certified positive at 32) |
| P4 κ − 1e-4 witness by m ≤ 16 (even), ≤ 32 (odd) | HELD (8; 32) |
| P5 no successes, so no reruns | FAILED (successes occurred); doubled precision and N = 40 replays done as required |

## 6. Comparison with D10
| quantity | D10 (full residual solve, 320 bits) | D11 (Krylov m = 32, 256 bits) |
|---|---|---|
| σ even | 2.167787235972e-13 ± 2.5e-26 | [2.1677871544e-13, 2.1677872363e-13] |
| σ odd | 2.531978866615e-10 ± 9e-26 | [2.531978866614e-10, 2.531978866616e-10] |
| min C even / odd | 1.226005383e-8 / 1.718881518e-6 | δ = 1.22600538345e-8 / 1.71888151806e-6 (independent) |
| response vector | x = C⁻¹b (79-dim solve) | x_32 ∈ K_32(C, b) |
| negative witnesses | 13 exact-decimal, finite R_120 | 7 generated from my own H/inputs, finite R_120 |

## 7. What is established, and what is not
1. Independent audit of D10: derivations re-done, H and p rebuilt independently, δ certified independently, controls regenerated; one textual gap repaired; nothing reused except D10's two control matrices as labeled inputs and its saved numbers for comparison.
2. Finite compression: the frozen "≤ 8 steps" target FAILS. A compressed response at m = 32 certifies σ > 0 in both parities (independent bracket, independent δ), reproduced at 512 bits and at N = 40. This is a finite numerical statement about R_120 at L = 0.7.
3. Still missing: a structurally proved lower bound on C and upper bound on bᵀC⁻¹b valid across all support widths. Nothing here bears on other L; nothing here is an RH mechanism; no novelty is claimed.

## 8. Plain language
We asked whether the balancing act at the heart of the certificate can be checked with a short recipe: eight rounds of a standard iteration instead of solving a whole 79-by-79 system. Eight rounds are not enough; thirty-two are, and only because the pole's coupling to the rest of the room lives in about thirty directions. Even then the recipe leans on a full-size check that the complement is safely positive. So we did not make the balancing rule shorter; we verified the same balance with a different computation, found one place where Codex's text needed a two-line argument, and confirmed every number they reported. The rule that would work in every room is still not in hand.
