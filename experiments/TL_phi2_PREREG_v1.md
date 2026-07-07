# Preregistration — TL_phi2 (Temperley–Lieb / Jones conditional-expectation numerics)

- test_id: TL_phi2
- ledger_anchor: P-005 (conditional expectation / Jones index phi^2)
- date_locked: 2026-07-03
- lane: engineering / verified-computation. NOT physics evidence. No result here proves GHP or observer-boundary selection (master hard rule 7).
- runtime: Python 3.9.6 + numpy 2.0.2 / scipy 1.13.1, deterministic, offline. No RNG needed (construction is exact); if any sampling is added it uses fixed seeds [1618, 2718, 3141].

## 0. Pinned constants (locked BEFORE any run; verified numerically)

- phi = (1+sqrt5)/2 = 1.6180339887498949
- delta_phi = phi. Jones index = delta^2 = phi^2 = 1+phi = **2.6180339887498949**.
  - 1/index = 2 - phi = **0.3819660112501051**.
  - phi closes as the A4 / Fibonacci fusion category: quantum integer [4]_delta = 0 at delta=phi (Jones–Wenzl p_4 vanishes).
- CONTROLS (must be run identically):
  - delta = sqrt2 (Ising / A3). Index = 2. 1/index = 0.5. Closes at [3]_delta = 0.
  - delta = 2cos(pi/7) = 1.8019377358048383 (A6). Index = 3.2469796037174670. 1/index = 0.3079785283699041. Closes at [7]_delta = 0.
  - delta = 2 (index 4, the boundary of the discrete Jones series; NOT a finite-depth category — [n]_delta = n+1, never returns to 0).
- ADVERSARIAL NOTE (index ordering, locked): index(Ising)=2 < index(phi)=2.618 < index(2cos pi/7)=3.247 < index(delta2)=4. **phi is NOT the minimal index.** Any phi-specific claim is therefore forbidden from resting on "phi^2 is small/special/recovered"; it must come from a control comparison on a closure-QUALITY metric, never from re-deriving phi^2 (which is definitional once delta=phi is chosen).

## 1. Construction (frozen)

For each delta in {phi, sqrt2, 2cos(pi/7), 2}:
1. Build TL_n(delta) for n = 2..N (N frozen at N=8; report per-n) via the **diagram basis** (planar non-crossing pairings of 2n points; dimension = Catalan(n)). Generators e_1..e_{n-1} with relations e_i^2 = delta e_i, e_i e_{i±1} e_i = e_i, e_i e_j = e_j e_i (|i-j|>=2).
2. Independently build the **Jones–Wenzl** projections p_k by the Wenzl recurrence p_{k+1} = p_k - ([k]/[k+1]) p_k e_k p_k, with [m] the delta-quantum integers. Cross-check: p_k e_{k-1} p_k = ([k-1]/[k]) p_k when [k] != 0 (used only at non-degenerate levels; for phi the recurrence is run only up to k=3 since [4]=0 — degeneracy is EXPECTED and logged, not an error).
3. Markov trace tr on TL_n: tr(1)=1, normalized so tr(e_i x) = delta^{-1} tr(x) for x in TL_{i}. Build the Gram matrix G of the diagram basis under tr; record det(G) and its rank/nullity (Wenzl: G is singular exactly at the non-generic delta = 2cos(pi/l), reflecting the negligible ideal).
4. Conditional expectation E_n: TL_n -> TL_{n-1} (the trace-preserving projection removing the last strand / the map with E(x e_{n-1} y) = delta^{-1} x y for x,y in TL_{n-1}). Realize E as the tr-orthogonal projection onto TL_{n-1} inside the GNS space of (TL_n, tr).

## 2. Quantities computed (identical across all four delta)

For each delta, each n:
- **PP** = Pimsner–Popa constant: the largest c such that E(x) >= c x for all x >= 0 in TL_n (equivalently the min over the GNS spectrum of the relevant operator). Theory: PP = 1/index = delta^{-2}.
  - metric PP_err(delta,n) = | PP_numeric - delta^{-2} |.
- **PP_pos** = min eigenvalue of (E(x) - delta^{-2} x) evaluated over a frozen probe set of positive x (JW projections and e_i's and their tr-normalized positive combinations). The bound holds iff PP_pos >= -tol.
- **MC** = Markov consistency residual: max over the frozen probe set of | tr(E(x)) - tr(x) | and | tr(e_{n-1} x) - delta^{-1} tr(x) | for x in TL_{n-1}.
- **IDEM** = idempotency/module residual: || E(E(x)) - E(x) || and || E(a x b) - a E(x) b || for a,b in TL_{n-1} (bimodule property), max over probe set, operator norm in GNS.
- **CQ** = closure quality: at the category-closing level (n crossing the vanishing quantum integer), the operator-norm gap between the numeric negligible ideal (nullspace of Gram) and the analytic Jones–Wenzl-predicted ideal. CQ measures whether the finite-access machinery *closes cleanly* (small, well-conditioned degeneracy) vs *raggedly* (ill-conditioned).

tol = 1e-9 (absolute, operator norm / eigenvalue scale). Condition-number guard: any Gram matrix with cond > 1e12 is flagged ILL and its PP_err at that n is excluded from pass/fail (reported separately), because floating error, not math, would dominate.

## 3. Hypothesis (H1) and null (H0)

- **H0 (primary, the one I expect to hold):** The finite-access TL/Jones machinery closes cleanly and satisfies Pimsner–Popa + Markov consistency **for ALL four admissible delta equally well**. phi's closure quality is statistically INDISTINGUISHABLE from the sqrt2, 2cos(pi/7), and delta=2 controls after conditioning on index magnitude and category depth. i.e. good behavior is GENERIC to admissible indices, not special to phi.
- **H1 (the interesting, harder claim):** phi is DISTINGUISHED — its closure-quality metric CQ (and/or PP_err, MC, IDEM) is better-conditioned than ALL non-golden controls by a margin exceeding the pinned threshold below, and this survives the index-magnitude and depth confounds.

This is deliberately a null-favoring prereg: TL closure works for every admissible delta by construction, so the DEFAULT scientific outcome is H0. H1 must clear a high bar.

## 4. Kill-or-pass rule (NUMERIC, locked)

Two separate verdicts are recorded.

### 4a. Machinery-validity gate (sanity; must pass or the whole test is INVALID, not informative)
For every delta and every non-ILL n:
- PP_err <= 1e-6, AND
- PP_pos >= -1e-9 (Pimsner–Popa bound holds), AND
- MC <= 1e-9, AND
- IDEM <= 1e-9.
If this gate fails for the golden case but passes for controls (or vice-versa) that is itself a reportable asymmetry; if it fails everywhere the implementation is broken -> INVALID, fix code, do not interpret.

### 4b. phi-distinctiveness verdict (the actual scientific question)
Define the closure-quality score per delta as
  CQ_score(delta) = median over closing levels of [ log10(cond(Gram at closing n)) ] ,
and PP tightness score
  PPQ(delta) = max over non-ILL n of PP_err(delta,n).

- **PASS-H1 (phi distinguished) — requires ALL of:**
  1. CQ_score(phi) < CQ_score(c) - 1.0 (i.e. phi's closing Gram is >=10x better conditioned) for EVERY control c in {sqrt2, 2cos pi/7, delta2}; AND
  2. the phi advantage is NOT explained by index magnitude: it must also beat the control whose index is *nearest* phi^2 (that is 2cos(pi/7), index 3.247) by the same >=1.0 log-margin; AND
  3. PPQ(phi) < min_c PPQ(c) by at least 1 order of magnitude.
- **KILL-H1 / CONFIRM-H0 (default, expected):** any of:
  - |CQ_score(phi) - CQ_score(c)| <= 1.0 for any control (phi within 10x of a control's conditioning), OR
  - a control ties or beats phi on CQ_score or PPQ, OR
  - the ordering of CQ_score across delta tracks index magnitude or category depth (Spearman |rho| >= 0.9 between CQ_score and index, computed over the 4 deltas) rather than singling out phi.
- **Decision when 4a passes and 4b is neither clean PASS nor clean KILL:** record as **WATCH / underpowered** (4 deltas is a small n); do NOT promote either way. No ledger status change beyond "machinery validated, phi-distinctiveness not established."

Thresholds (1.0 log-decade margin, Spearman 0.9, 1e-6/1e-9 tolerances) are locked now and MUST NOT be adjusted after seeing data.

## 5. Controls it MUST beat (to earn H1)

- delta = sqrt2 (Ising / A3, index 2) — smaller index than phi; the "phi is not minimal" control.
- delta = 2cos(pi/7) (A6, index 3.247) — index NEAREST above phi^2; the index-magnitude confound control. This is the decisive one.
- delta = 2 (index 4, series boundary, non-closing) — the "no finite category" control; expected to be worst-conditioned for structural reasons unrelated to phi.
- Additionally the SAME code path for all four (single parametrized builder) is itself a control against per-delta special-casing.

## 6. What result is CIRCULAR / NUMEROLOGY / INVALID (locked)

- **CIRCULAR:** Reporting that "the Jones index came out to phi^2 = 2.618" or "1/index = 2-phi" as evidence. These are DEFINITIONAL once delta=phi is chosen (index = delta^2). Recovering them proves only that arithmetic works. They may appear as sanity checks in 4a ONLY, never as H1 support.
- **NUMEROLOGY:** Any claim that surfaces phi, Fibonacci, [4]=0, or the A4 quantum dimensions as "special" without a matched control clearing the section-4b margins. The A4-closure of phi is a property of ALL 2cos(pi/l) deltas at their own l — sqrt2 closes at l=4, 2cos(pi/7) at l=7 — so "phi closes" alone is generic Jones-series structure, not phi content.
- **INVALID:** (a) tuning N, the probe set, tol, or the margin after inspecting results; (b) using different construction paths / conditioning for phi vs controls; (c) letting an ILL-flagged (cond>1e12) point drive the verdict; (d) interpreting a 4a failure-everywhere run as anything but a code bug; (e) presenting any 4b outcome as physical evidence for GHP.
- **Honest prior:** I expect H0. TL closure and Pimsner–Popa hold for every admissible delta by theorem; phi's index sits mid-series and is not minimal, so the most likely honest outcome is "machinery validated, phi indistinguishable — closure quality tracks index/depth, not the golden ratio." A KILL of H1 is the expected, valuable result.

## 7. Ledger link

Row P-005 in `GHP_RESEARCH_LEDGER.md`. Prereg artifact pinned at `experiments/TL_phi2_PREREG_v1.md` (this file). No ledger status may be upgraded before an audited run against this contract; per discipline, "pre-registered" may not be claimed without this pinned path+version.
