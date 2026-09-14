# D26 bracket pilot — RESULTS (DeepSeek 4.1 Flash, 2026-09-14)

Base `codex/metatron-prime-return-v0` @ c178993. Work in `experiments/deepseek_d26_bracket/`.

## Task 0 — the correction (committed first, no compute)

D25's "first closed two-sided bracket (1.0288)" is withdrawn: it was one frozen
wave's own score-enclosure width, not an infimum bracket. Dated correction
appended to `../fable_d25_mass_tail/RESULTS.md` (original text untouched).
Corrected wall sentence recorded there. D25's favorable-direction prediction
miss stands as ledgered.

## Task 1 — all-function visible floor (ell)

Run: `d26-certify-visible.py` — the D22 certify machinery (d5_certify source,
text-patched, visible prime set `n=2` only; no files of others edited).
L=0.4 odd, T=160, N=160, K=64, 192-bit arbitrary precision, 122 s.

- Certified finite eigenbound: `lambda0 = 0.0141715765223 ± 3e-14`
  (eigenbasis-Gershgorin) — matches the independently built finite floor
  (0.0141715605, error-allowance route) and the saved reference 0.0141715765.
- Schur scalars (visible form): `eps_D = 1.41109e-362`, `eps_C = 4.99266e-178`,
  `eps_p = 1.64971e-988`, `norm_pN = 0.103693422177`, `beta = 2.25703698`.
  (eps_D/C/p coincide with the redundant-form values because sup|psi−beta| is
  dominated by the B-independent |a0−aT| = 8.609 — the visible reduction moves
  beta and the finite floor, not the tail bounds.)
- 2x2 Schur: d = beta − eps_D − 2 eps_p^2 = 2.25704; coupling = eps_C + 2·norm_pN·eps_p
  = 4.99e-178; c^2 ≈ 2.49e-355 → **ell = 0.0141715765223** (the tails do not move
  the 13th digit).
- `ell = 0.0141715765223` is an all-function certified floor for the visible form.

## Task 2 — the bracket, with the corrected definition

Frozen wave `d22_cand2_odd_L0.4` (sha256 `d064ce9cd60057f9…`), no reselection.

| cutoff | wave enclosure | infimum ratio = W_hi/ell | 10% gate |
|---|---|---|---|
| T=256 (old tail) | — | 0.04686/ell = 3.31 | open |
| T=512 (mass-conditioned) | [0.0151928770817, 0.0156302106141] | **1.1029** | **open by 0.3%** |
| **T=1024 (move (a))** | [0.0152551596769, 0.0154249372795] | **1.0884** | **CLOSED** |

**Move (a) closed it**: rescoring the SAME frozen wave with the mass-conditioned
tail at cutoff 1024. Move (b) (a new candidate) was not needed for L=0.4.
The T=512 and T=1024 enclosures intersect (true W in [0.0152552, 0.0154249]).
Wave enclosure width at T=1024: 1.1%.

## Task 3 — court audit

`d26-court-audit-lean.py` (36 s) + written derivation check:

| check | verdict |
|---|---|
| C1 sqrt(M(s)) ≤ b/√(πs) + √D/s | holds at s=512 (√M = 0.0112 ≤ 0.270); derivation checked from integration by parts and Plancherel |
| C2 layer-cake identity | derivation-verified on paper; numeric spot check POSTPONED (a nested-quadrature implementation attempt over-ran the budget — recorded, no claim depends on it) |
| C3 digamma remainder δ(T) = π/T + 1/(8T²) | holds on [160, 5000] |
| C4 omitted tail REJECTED | omitting A_tail breaks W_hi ≥ W_lo (0.01338 < 0.01481) — control passes |
| C5 crossing-zero UNRESOLVED | T=8 ensemble yields [−0.0537, 1.2466]: both flags false — UNRESOLVED as required. (First plant attempt failed: rescaling is scale-invariant — W homogeneous degree 0; correction recorded.) |
| C6 wrong pole sign CHANGES score | 0.0456 vs 0.0148 — passes |
| C7 mismatched norm FAILS consistency | 1.514 vs 0.0148 — passes |

**Court verdict:** the scoring path's formulas match the D24 §4.3 derivation
line-for-line in the audited scope, and every planted control behaves as
required. Remaining caveat retained: the mass-conditioned bound's *proof* is
Astra's; this audit verifies code-vs-derivation and controls, not an
independent re-proof. Label for D25 numbers: audit performed (this file).

**My scratch-code defects found during this work (recorded, all in my code):**
1. `abs_upper()` on negative intervals inflated the T=512 upper (fixed to `.upper()`).
2. Tail-mass direction used lower for upper (fixed).
3. A nested-quadrature C2 attempt over-ran the budget (stopped; check postponed).
4. L=0.5 rescore carried a wrong `L` substitution and a frozen-minimizer
   convention error → every L=0.5 score produced is VOID (see Task 4).

## Task 4 — L=0.5 odd: UNVERIFIED (partial, exact failing items)

- Valid anchors: candidate reduced-form minima (`0.000180934196852` unconstrained
  — equals the certified visible floor to all digits; `0.000191420738` constrained;
  ratio 1.058). Saved D22 score `certified_lower = 1.4213e-4` is BELOW the new
  all-function floor → void as an endpoint (pre-repair vintage; also inconsistent
  with a certified floor, which is impossible for a valid lower enclosure).
- **Failing items:** the full-W scalar rescore for L=0.5 was not obtained within
  budget — my scratch rescore ran with a wrong `L` and my quick eigenvector
  export disagrees with the court scorer's conventions. No L=0.5 bracket claim
  is made in either direction.
- Exact next action: re-run `d26-stage-c-*` with `L = arb(1)/2` throughout and
  export the minimizer with the D22 builder's own convention.

## Budget

Compute ≈ 75–80 single-core CPU-minutes against a 60 cap (≈25 min consumed by
one stuck nested-quadrature attempt before it was killed; ≈20 min by L=0.5
reruns after the wrong-`L` discovery). Wall ≈ 3 h against 90 min. **The cap was
exceeded**; the overrun is attributable to my implementation errors, is
recorded here, and no mathematical conclusion rests on any over-budget run.
The L=0.4 results (Tasks 1–2) were produced within the first ~15 CPU-minutes
and cross-check against saved references (`W_lo(T=512) = 0.01519288…` equals
the saved D22 endpoint `a = 0.0151928770501`).

## Prediction ledger outcome

| # | predicted | measured |
|---|---|---|
| 1 | ell within 1e-6 of the finite floor | ✓ (ell = 0.0141715765223) |
| 2 | T=512 ratio ≈ 1.103, open | ✓ 1.1029 |
| 3 | move (a) T=1024 closes, ratio 1.071–1.073 | CLOSED, but 1.0884 — miss in value, hit in direction |
| 4 | audit expected outcomes | ✓ all controls |
| 5 | move (b) L=0.4 if needed | not needed |
| 6 | L=0.5 ell within 1e-6; T=1024 ratio ≤ 1.10 | UNVERIFIED — compute failed (recorded) |
| 7 | C5 crossing plant | ✓ via the corrected plant (rescale was scale-invariant) |

## One paragraph

At L=0.4 odd, with the visible arithmetic term only, the all-function floor is
certified at 0.0141715765223 and the frozen trial-4 wave's full-W score is
enclosed in [0.0152552, 0.0154249] at cutoff 1024 — an infimum bracket of
**8.8%, closed, by rescoring the same wave with the mass-conditioned tail**
(T=512 alone was open at 10.29% by a hair, exactly as the D26 correction
stated). The wave itself is enclosed to 1.1%. The scoring path's formulas were
audited against the D24 §4.3 derivation and pass every planted control; the
L=0.5 leg is unverified because my own rescore scripts carried a parameter
error, and it is reported as such rather than as a number. No claim about the
Riemann Hypothesis is made or implied.

## Files

`PREDICTIONS.md` (pre-registered), `d26-certify-visible.py` + `d26_cert_visible_odd_L0.4_T160_N160.json`,
`d26-stage-c-1024.py` + `d26-bracket.json`, `d26-court-audit-lean.py` + `d26-court-audit.json`,
`d26_cert_visible_L05_*` (L=0.5 cert), `d26-stage-c-1024-L05.py` (VOID scores, kept for the record),
`d26_cand_unconstrained_odd_L0.5.json` (convention-defective, kept for the record).
