# Opus round D7 — independent audit of the L = 0.7 compact-window certificate (2026-09-06)

Auditor: Claude Opus 5, acting as an independent third party. Fable produced D4–D6; Codex produced the sine-basis certificates. Neither was trusted: every dependency below was re-derived, and every number was rebuilt from my own code.

Repository `/Users/peterviviani/golden-horizon-principle`, branch `codex/metatron-prime-return-v0`.
**HEAD when the audit opened: `b68b14c988c6a8e14ab565135fcea14c3700de55`.**
Between that snapshot and my first commit the branch advanced by one commit made by the repository owner, `18f0005` ("Add central Reimann Research hub and Opus audit handoff"), which added `Reimann Research/README.md`, `Reimann Research/NEXT-ROUND-D7.md` and tracked `experiments/prime_gears_codex/STATUS-AND-CONTRIBUTIONS.md`. `git diff b68b14c 18f0005 -- experiments/weil_hidden_modes` is **empty**: no file under audit changed, and `b68b14c` is an ancestor of my commits. Recording both hashes rather than the one I first wrote down.
Predictions committed BEFORE any computation at **`b372ccecda2410f029f9fd98e2069b175e204696`** (`OPUS-PREDICTIONS-D7.md`), parent `18f0005`. Audit results committed at **`e09a3d6a35aeaa6fcf0907a63cda193034e62fce`**. Committed locally; not pushed.
`NEXT-ROUND-D7.md` asks that this file be linked from the hub. I did not do that: my instructions forbid editing any pre-existing file, so the link must be added by the repository owner. No existing file was edited or deleted. No zeta zero ordinates were used. No novelty is claimed.

Compute budget set in advance: ≤ 90 min total, ≤ 20 min per run. **Actual: ~14 min** (four 27 s reconstructions, two 40 s replays, a 3 min normalization control, seconds for the checker controls).

The two 0.7s (GHP's central charge c = 7/10 and the support half-width L = 0.7) are **not** investigated here; per the directive they are different quantities with no established bridge.

---

## D7.1 Dependency audit — the mathematics, derived before replaying anything

I derived the objects from the Riemann–von Mangoldt / Weil explicit formula without reading Fable's derivation first, then compared.

### Conventions I fixed
`F(t) = (2π)^{-1/2} ∫ f(x) e^{-ixt} dx` (unitary), `f̂(ξ) = ∫ f e^{-iξx} dx = √(2π) F(ξ)`, `f̃(x) = conj(f(-x))`, `g = f ⋆ f̃`, `h(r) = ∫ g e^{irx} dx = ĝ(-r)`.

### (1) Fourier normalization and the prime powers — DERIVED, AGREES
Starting from the explicit formula in the form
`Σ_ρ h(γ_ρ) = h(i/2) + h(-i/2) - Σ_n (Λ(n)/√n)[g(log n)+g(-log n)] + (1/2π)∫ h(r)[Re ψ(¼+ir/2) - log π] dr`:
- archimedean: `(1/2π)∫ h(r) a(r) dr = (1/2π)∫ 2π|F(-r)|² a(r) dr = ∫ |F|² a` (a even). The 2π cancels **exactly once**; the factor is forced.
- prime: `g(log n)+g(-log n) = (1/2π)∫ h(r)·2cos(r log n) dr = ∫ |F|²·2cos(t log n) dt`, so the symbol is `P(t) = Σ (2Λ(n)/√n) cos(t log n)`. The factor 2 is not a convention; it is the two-sided pair `g(±log n)`.
- support: `supp g ⊂ [-2L, 2L] = [-1.4, 1.4]`; `log 4 = 1.3862… ≤ 1.4 < log 5 = 1.6094`. So exactly `n ∈ {2,3,4}` with weights `2log2/√2, 2log3/√3, log2`. **My independent enumeration is the same, and the code asserts `log 5 > 2L`.** `B = P(0) = 2.9419735252236204555…` (my Arb value, identical to Fable's).
**Verdict: MEASURED-consistent, derivation reproduced. Prime powers 2, 3, 4 correct; no term omitted, none spurious.**

### (2) The Hermitian pole term and its even/odd signs — DERIVED, AGREES
`ĝ(ξ) = f̂(ξ)·conj(f̂(ξ̄))`: substituting `u = y - x` gives `ĝ(ξ) = f̂(ξ)·∫ conj(f(u)) e^{iξu} du`, and `∫ conj(f) e^{iξu} du = conj(∫ f e^{-i ξ̄ u} du) = conj(f̂(ξ̄))` because `conj(e^{iξu}) = e^{-i ξ̄ u}` for real `u`. (I first mis-derived this as `conj(f̂(-ξ̄))`; the real-ξ sanity check `ĝ(ξ) = |f̂(ξ)|²` catches that instantly. Fable's version is the right one.)
Hence `Π(f) = ĝ(i/2)+ĝ(-i/2) = 2 Re[f̂(i/2) conj(f̂(-i/2))]`, and for real `f = f_e + f_o` with `C = ∫f_e cosh(x/2)`, `S = ∫f_o sinh(x/2)`:
`Π = 2(C+S)(C-S) = +2C² - 2S²`.
**So the even-sector pole enters with sign +1 and the odd-sector pole with sign -1.** The certificate JSONs used for the advertised constants are `pole+1` (even) and `pole-1` (odd) — i.e. `pole_sign_mutation = +1`, the *unmutated* runs in both sectors. I checked the filename convention against the code path (`POLE = (+1 even / -1 odd) × PSIGN`) so that a mutated run could not be passed off as the certificate. It was not.
**Verdict: correct, and the sign is load-bearing — see control C9 below.**

### (3) Complex-function decomposition and domains — DERIVED, AGREES
`|F₁+iF₂|² = |F₁|²+|F₂|² - 2 Im(conj(F₁)F₂)`. With `f₁,f₂` real, `F_j(-t) = conj(F_j(t))`, so `u(t) = conj(F₁)F₂` satisfies `u(-t) = conj(u(t))` and `Im u` is **odd**; `Ψ` is even, so the weighted cross term integrates to zero (absolutely convergent). The pointwise identity is false; the integrated one holds. Pole: `Π(f₁+if₂) = 2(a₁b₁+a₂b₂) = Π(f₁)+Π(f₂)`, whereas the non-Hermitian `2f̂(i/2)f̂(-i/2)` gives `2(a₁b₁-a₂b₂)+2i(…)` and is wrong. Therefore `W(f) = W(f₁)+W(f₂)` and, with the parity split, `W(f) ≥ min(λ_e, λ_o)‖f‖²` for all complex `f`.
Domain: `Ψ(t) ≥ a(t) - B` and `a(t) = log(|t|/2) - log π + O(t^{-2})`, so `Ψ` is bounded below and `W: L² → (-∞, +∞]` is well defined, finite exactly on `𝒟_W = {∫|F|² log(2+|t|) < ∞}`. `R_T` is bounded on all of `L²`. The zero-sum identity is used only on the explicit-formula class.
**Verdict: correct as stated in D6.** One overstatement flagged: D6 says the inequality "is implied by RH". RH gives `Σ_ρ h(γ_ρ) ≥ 0`; it does not give `≥ λ‖f‖²` with `λ > 0`. Cosmetic, not load-bearing.

### (4) `W ≥ R_T` and `β*` — DERIVED, AGREES
`R_T(f) := ∫_{|t|≤T}(Ψ-β*)|F|² + β*‖f‖² + Π(f)` with `β* = a(T) - B`. Then `W - R_T = ∫_{|t|>T}(Ψ-β*)|F|² ≥ 0` **provided** `Ψ ≥ β*` off `[-T,T]`, which needs (i) `|P| ≤ B` (immediate, positive weights, `|cos| ≤ 1`) and (ii) `a` increasing on `t > 0`.
Proof of (ii), re-derived: `d/dt Re ψ(¼+it/2) = -½ Im ψ'(¼+it/2)`, and `Im (A+it)^{-2} = -2At/|A+it|⁴ < 0` for `A, t > 0`, so `Im ψ' = Σ_{k≥0} Im(¼+k+it)^{-2} < 0` and `a' > 0`. **Proved, not spot-checked.**
Numerically `β*(120) = 0.0076382575953959615868…` — my Arb value is digit-identical to Fable's. Note the threshold: `β* > 0` requires `T > 2π e^B = 119.0866…`, so **T = 120 sits 0.8 % above the threshold**. This is why `β*` is small, and it is a real scope limitation, not a defect.

### (5) The quadrature-error theorem — HYPOTHESES CHECKED; **the cited constant could not be verified and is smaller than a correctly derived one**
`d5_certify.py` uses `Cq = (64/15)·h·ρ^{-2K}/(ρ²-1)`, attributed to Trefethen ATAP Thm 19.3. This was my **preregistered most-likely-to-fail step (P0)**.
- Hypotheses that DO check out: the integrand `(Ψ-β*)F_mF_n` is analytic in the Bernstein ellipse of each unit panel, because `F_n` is entire and the nearest singularity of `a` is at `|Im t| = ½` (from `¼ ± it/2 = 0`), while the ellipse semi-minor axis is `0.375 < 0.5`. The `M_ρ` bound is a valid product bound. The box cover of the bounding rectangle is contiguous and complete (I checked the centre/radius arithmetic).
- What I could NOT check: the exact constant in ATAP Thm 19.3. I do not have the book offline and a web search did not surface the statement. **I therefore refused to use any remembered constant** and derived my own from scratch:
  > Gauss–Legendre with `K` nodes is exact on degree `≤ 2K-1`; its weights are positive and sum to 2. For `f` analytic in `E_ρ` with `|f| ≤ M`, Bernstein's Chebyshev-coefficient bound `|a_k| ≤ 2Mρ^{-k}` gives `‖f - p_{2K-1}‖_∞ ≤ 2Mρ^{-(2K-1)}/(ρ-1)`. Hence `|I - I_K| = |(I-I_K)(f-p)| ≤ 4‖f-p‖_∞ ≤ 8Mρ/((ρ-1)ρ^{2K})`, times the panel half-width.
  At `ρ = 2` this constant is **11.25× larger** than the one d5_certify.py uses. So either the ATAP constant is sharper than the elementary bound (plausible — it comes from a contour argument) or it is misquoted. **I cannot settle it, and I do not need to:** my reconstruction uses the conservative derived constant and still lands at an entry error bound of `2.4e-26`, nine orders below the eigenvalue being certified.
**Verdict on P0: UNRESOLVED as a citation, IMMATERIAL as a defect.** My preregistered prediction that it was "misquoted, too small by 3–4×" is scored **FAILED (unresolved)** — I could neither confirm nor refute it. The certificate does not depend on the answer.

### (6) The infinite discarded-block and coupling bounds — DERIVED, AGREE (mine slightly tighter)
Write the infinite matrix of `R_T` in the orthonormal basis as `[[A, C],[Cᵀ, D]]`, `A` the retained `80×80` block (`n ≤ 158` even / `≤ 159` odd), `D` the infinite discarded block.
- `|j_n(y)| ≤ y^n/(2n+1)!!·e^{y²/(2(2n+3))}` for `y ≥ 0`: from the series, using `(2n+3)(2n+5)⋯(2n+2k+1) ≥ (2n+3)^k`. **Proved.** With `y = TL = 84` this gives `s_n ≥ sup_{[0,T]}|F_n|`.
- `‖M_DD‖ ≤ 2T·supΨ·Σ_{n≥ncut} s_n²` by Cauchy–Schwarz. (Fable uses `(Σ s_n)²`, which is also valid but looser; my `ε_D` is correspondingly smaller: `2.67e-38` vs `3.05e-38` even, `1.59e-39` vs `1.81e-39` odd.)
- `‖M_ND‖ ≤ ‖M_ND‖_F ≤ 2T·supΨ·(Σ_{m∈N}c_m²)^{1/2}(Σ_{n∈D}s_n²)^{1/2}` using `|j_m| ≤ 1` (itself from `|j_n(z)| ≤ ½∫|P_n| ≤ 1`). My `ε_C` is **identical** to Fable's (`3.88501e-16` even, `9.53491e-17` odd).
- geometric tail: `s_{n+2}/s_n ≤ r(ncut)` for all `n ≥ ncut` because `r(n) = √((2n+5)/(2n+1))·y²/((2n+3)(2n+5))` is decreasing and the dropped exponential ratio is `< 1`. `r(160) = 0.0676 < 1`. **Proved.**
- pole tail: `|p_n| ≤ √((2n+1)/(2L))·2L·(L/2)^n/(2n+1)!!·e^{(L/2)²/(2(2n+3))}`, `ε_p ≈ 2.4e-406`.
- Schur: for `‖u‖,‖v‖` and `A ≥ λ₀I`, `D ≥ d_low I`, `‖C‖ ≤ off`, the form is `≥ λ₀‖u‖² - 2·off·‖u‖‖v‖ + d_low‖v‖² ≥ μ‖(u,v)‖²` with `μ` the smaller eigenvalue of `[[λ₀,-off],[-off,d_low]]`. Valid on finitely supported vectors, extended to `ℓ²` by boundedness/continuity of `R_T`. **Proved.**
**Verdict: sound. `d_low = β* - ε_D - 2ε_p² > 0` with enormous room (`7.6e-3` vs `2.7e-38`).**

### (7) Basis invertibility and congruence → eigenvalue bound — DERIVED, AGREES
For invertible `V` and `x = Vy`: `xᵀAx ≥ λ_min(VᵀAV)‖y‖²` and `‖x‖² ≤ λ_max(VᵀV)‖y‖²`, so `λ_min(A) ≥ λ_min(VᵀAV)/λ_max(VᵀV)` **when the numerator is ≥ 0** (if negative one must divide by `λ_min(VᵀV)` instead — my implementation handles both branches; d5_certify.py only ever hits the positive branch). Gershgorin supplies `λ_min` from below and `λ_max` from above for symmetric matrices. `V` is certified invertible by `λ_min(VᵀV) > 0`; ball arithmetic over-encloses `VᵀAV` for the *fixed* `V` inside the ball, so the bound is valid for that `V`.
One point I checked and initially misread: the JSON's `λ₀ = [1.03101776024e-13 ± 9.33e-26]` looks too tight against entry radii of `1.16e-22`. It is not a propagated radius — `gersh` is built from `.lower()`/`.abs_upper()` endpoints, so the uncertainty is already absorbed, and the printed `±` is Arb's *display* inflation at 12 digits. `d6_checker.py` re-parses the printed string and takes `.lower()`, which is conservative. **Sound.**

---

## D7.2 Independent reconstruction (`opus_d7_rebuild.py`, `opus_d7_*_NE80_pole*.json`)

Same normalized Legendre basis `q_n(x) = √((2n+1)/(2L)) P_n(x/L)` (so entries are comparable), everything else independent:

| ingredient | d5_certify.py (Fable) | opus_d7_rebuild.py (mine) |
|---|---|---|
| precision | 192 bits | 256 bits |
| `j_n` | hand Taylor series + Rayleigh closed form | Arb `bessel_j(n+½)` (hypergeometric) via `j_n(z)=√(π/2z)J_{n+½}(z)` |
| quadrature | GL, ρ = 2, K = 48, ATAP constant | GL, ρ = 1.9, K = 56, constant **derived here** from Bernstein + positive weights (11.25× more conservative at ρ = 2) |
| ellipse cover | 6 × 4 boxes | 20 × 24 boxes, digamma recurrence shifted by 8 |
| pole vector | `acb.integral` of `q_n·cosh/sinh` | **closed form** `p_n = √((2n+1)/(2L))·2L·i_n(L/2)` via Arb `bessel_i`, from `∫_{-1}^1 e^{zs}P_n(s)ds = 2 i_n(z)` |
| discarded block | `(Σ s_n)²` | `Σ s_n²` (Cauchy–Schwarz) |

Derivation of `F_n`: `∫_{-1}^{1} e^{izs}P_n(s)ds = 2 i^n j_n(z)` ⇒ `F_n(t) = (2π)^{-1/2}√((2n+1)/(2L))·2L·(-i)^n j_n(Lt)`; the common phase `(-i)^{parity}` cancels in `|F|²`. Plancherel check: `∫_ℝ F_0² = (L/π)(π/L) = 1` exactly, which pins the `2π`.

### Entry enclosures (independent vs. certificate, same basis)

| entry | Fable (192-bit) | Opus (256-bit) | agree |
|---|---|---|---|
| even (0,0) | `-2.8719459474324615205` | `-2.871945947432461520544 ± 8.4e-24` | 20 digits |
| even (0,2) | `0.066388923568830598971` | `0.06638892356883059897076 ± 6.9e-25` | 21 digits |
| even (20,40) | `0.055741017294763338419` | `0.05574101729476333841925 ± 1.0e-25` | 21 digits |
| odd (1,1) | `0.25688409618514113521` | `0.2568840961851411352137 ± 1.0e-23` | 20 digits |
| odd (1,3) | `0.19804528851707719748` | `0.1980452885170771974817 ± 2.3e-23` | 20 digits |
| odd (21,41) | `-0.012031683660645433836` | `-0.01203168366064543383578 ± 3.9e-24` | 21 digits |

My max entry radius is `4.79e-26` (Fable's `1.16e-22`); max quadrature error bound `2.39e-26` under the conservative derived constant. `B`, `β*`, `a(0)`, `a(T)`, `sup|Ψ-β*|` are digit-identical to the certificate. `‖p_N‖` from the closed form: `1.20771838681024` (even) / `0.242040702857047` (odd) versus the certificate's `1.20771838681` / `0.242040702857` — **agreement of a closed-form Bessel evaluation with a numerical integration, to every printed digit.**

### Finite-block, tail, coupling and full-form bounds

| quantity | even | odd |
|---|---|---|
| finite-block `λ₀` (certified, mine) | `1.03101781648892e-13` | `5.85907085398903e-11` |
| finite-block `λ₀` (certified, Fable) | `1.03101776023907e-13` | `5.85907085320948e-11` |
| float smallest eigenvalue (both) | `1.0310178165129809e-13` | `5.859070853989362e-11` |
| `ε_D` | `2.66638e-38` | `1.58614e-39` |
| `ε_C` | `3.88501e-16` | `9.53491e-17` |
| `ε_p` | `2.41824e-406` | `2.62853e-409` |
| `off = ε_C + 2‖p_N‖ε_p` | `3.88501e-16` | `9.53491e-17` |
| `d_low = β* - ε_D - 2ε_p²` | `0.007638257595` | `0.007638257595` |
| Schur correction | `1.976e-29` | `1.190e-30` |
| **full-form lower bound (mine)** | **`1.03101781648892e-13`** | **`5.85907085398903e-11`** |

My certified bounds are **larger** than Fable's in both sectors (by `5.6e-21` and `7.8e-21`), because my entry radii are ~2400× smaller, so the Gershgorin off-diagonal subtraction eats less. The two float eigenvalues agree to all 17 printed digits, which is the real statement: **the matrices are the same; only the certified slack differs.**

**Both advertised constants survive my independent endpoint:** `1.031e-13 ≤ 1.0310178165e-13` and `5.859e-11 ≤ 5.8590708540e-11`. And Fable's D6 correction is confirmed: `5.86e-11` exceeds the endpoint and must be rejected.

---

## D7.3 Sensitive directions — score vs. certificate

The directive's point is exactly right: entrywise agreement at 1e-11 cannot resolve a 1e-13 margin, and a vector's score and an operator bound are different objects. So:

- I froze the approximate minimizing eigenvector as an **exact 80-component decimal vector** (40 digits each) and evaluated `R_T(c)/‖c‖² = (cᵀMc + β*‖c‖² + 2·POLE·(p·c)²)/‖c‖²` in ball arithmetic.
- even: score `= [1.0310178165130e-13 ± 4.0e-27]`, upper endpoint `1.03101781651300e-13`.
- odd: score `= [5.85907085398936e-11 ± 3.0e-26]`.
- Both balls are strictly positive; the sign is resolved with 13 orders of margin.

**Sandwich.** The score is an **upper** bound on the minimum of the finite block (and hence on the full-space minimum, since the block is a subspace of the full space); the Gershgorin/Schur bound is a **lower** bound:

| sector | certified lower bound | frozen-vector score (upper) | relative width |
|---|---|---|---|
| even | `1.03101781648892e-13` | `1.03101781651300e-13` | `2.3e-14` |
| odd | `5.85907085398903e-11` | `5.85907085398936e-11` | `5.6e-15` |

So the true minimum is pinned to 13–14 significant digits, and the two bounds are of opposite type — neither substitutes for the other, and here they meet.

---

## D7.4 Attack the checker first (`opus_d7_controls.py`, `opus_d7_controls.json`)

I wrote my own verdict function, my own congruence certifier and my own endpoint test rather than importing `d4_checker.py`/`d6_checker.py`, and ran the six required controls **before** accepting the authentic numbers. All results use MY reconstructed endpoints.

| # | required behaviour | result |
|---|---|---|
| C1 | missing tail evidence → no certificate | **NO_VERDICT** ("missing tail/coupling/pole/beta evidence") — PASS |
| C2 | excessive coupling → rejection when the certified inequality fails | `off = 1e-5`, `λ₀ = 1e-13` → **REJECT** (`μ = -2.0e-10`) — PASS |
| C2b | positive control, `off = 1e-9` | **ACCEPT** (`μ = 9.9998e-14`) — PASS |
| C3 | `λ₀` not interval-certified | **NO_VERDICT** — PASS |
| C4 | `ε_D` swamps `β*` | **REJECT** (discarded block not certified positive) — PASS |
| C5 | advertised constant above the rigorous endpoint → rejection | even: `1.03e-13` ACCEPT, `1.031e-13` ACCEPT, `1.0311e-13` REJECT, `1.032e-13` REJECT; odd: `5.85e-11` ACCEPT, `5.859e-11` ACCEPT, `5.8591e-11` REJECT, `5.86e-11` REJECT — 8/8 PASS |
| C6 | orthogonal `V` recovers the planted `1e-13` | `[1.0000000e-13 ± 3e-25]` — PASS |
| C7 | **singular basis transformation → rejection** | duplicated column ⇒ Gershgorin bound on `VᵀV` is `-1.35e-40`, certifier **REFUSES** — PASS |
| C8 | **nonorthogonal invertible basis → correct norm conversion** | `V = Q·diag(100,1,1,1,1,1)`: correct conversion returns `1.0000000e-13` (the true value); the naive `λ_min(VᵀAV)` without dividing by `λ_max(VᵀV)` would advertise `1.0e-9`, four orders **above** the truth — the naive conversion is demonstrably unsound, the implemented one is not — PASS |

*(C8 was strengthened mid-audit: my first version scaled a non-minimizing direction, and the naive bound came out right by luck. A control that does not bite is not a control; the weak version is recorded here rather than quietly dropped.)*

### C9 — wrong pole sign
Run with the pole sign flipped in each sector (`opus_d7_even_NE80_pole-1.json`, `opus_d7_odd_NE80_pole+1.json`):

| sector | correct sign | flipped sign |
|---|---|---|
| even | `+2ppᵀ` → `+1.031e-13` | `-2ppᵀ` → **`λ_min = -5.78819388152601`** (indefinite; any positivity checker rejects) |
| odd | `-2ssᵀ` → `+5.859e-11` | `+2ssᵀ` → **`λ_min = +1.71884712655414e-6`** (still positive definite) |

This reproduces Fable's mutation exactly (`1.71884712655e-6`) and makes the directive's point concrete: **in the odd sector a generic positivity checker accepts the wrong model.** The wrong sign is caught only by comparison with the independently derived form — which is what §D7.1(2) does. It is a model-validation obligation, not a checker bug. In the even sector the sign happens to be caught for free.

### C10 — normalization vs. a genuinely independent implementation (`opus_d7_sameform.py`)
Entrywise agreement with Fable proves only that we implement the same formula. To test the formula I compared my frequency-space `W` against **Codex's position-space certified matrix** (`certified_results.json`, 16 sine modes, 384-bit Arb, entry radii `< 1.75e-34`) on Codex's own basis, re-deriving `F_i`, `f̂_i(c)` and `Π_ij` myself, and truncating the frequency integral at three values of `T_b`. A wrong `2π`, a wrong factor 2 on the prime weights, or a wrong pole ordering would leave a `T_b`-independent residual `≥ 1e-3`.

| entry (sine basis) | Codex position-space, 384-bit | residual `mine - codex` at `T_b = 2e4` | `T_b = 6e4` | `T_b = 1.8e5` | shrink per 3x |
|---|---|---|---|---|---|
| (1,1) | `0.001417909623284128270657…` | `-1.603e-12` | `-6.740e-14` | `-3.059e-15` | 23.78, 22.04 |
| (2,2) | `0.003552080729165840895182…` | `-6.414e-12` | `-2.685e-13` | `-1.109e-14` | 23.89, 24.22 |
| (1,2) | `0` (parity-forbidden) | `[± 1.3e-46]` | `[± 1.3e-46]` | `[± 1.3e-46]` | exactly zero |

Predicted shrink per 3x in `T_b`: `3^3 · log(2e4)/log(6e4) = 24.3`. Measured: 22.0–24.2. Quadrature self-check (24 vs 36 Gauss nodes per half-period panel at `T_b = 2e4`): `-2.9e-16` and `8.7e-18`, i.e. far below the residuals being interpreted. My `T_b = 2e4` residual for (1,1), `-1.603e-12`, independently reproduces Fable's T4 figure of `-1.6e-12`.

The residual falls at the analytic tail rate (`|F_i| = O(t^{-2})`, `|Ψ| = O(log t)` ⇒ tail `= O(log T_b / T_b³)`, predicted shrink ≈ 24.3 per 3× in `T_b`). **This is truncation, not normalization.** Two independent implementations in two different representations, written from two independent derivations, agree on the same quadratic form.

### C11 — replay control
`d5_certify.py` was re-run unmodified from a scratch directory (so no repository file was touched) for both sectors. Output is **bitwise identical** to the committed JSONs on every certified key (`beta_star`, `lambda0_certified`, `eps_D`, `eps_C`, `eps_p`, `norm_pN`, radii, verdict). This establishes determinism and rules out fabricated JSONs; it is the *same machine* and therefore **not** independent validation. Obligation #1 of D6 is only half discharged by it — and fully discharged by D7.2, which is an independent implementation on the same machine. A second machine remains outstanding.

---

## D7.5 Prediction ledger

| # | preregistered prediction | outcome |
|---|---|---|
| P0 | the ATAP Thm 19.3 constant is misquoted (3–4× too small), but harmless | **FAILED (unresolved)** — I could not verify the source offline, so I neither confirmed nor refuted the misquotation. Sidestepped by deriving my own constant, 11.25× more conservative at ρ = 2; certificate unaffected. |
| P1–P4 | discarded/coupling bounds, congruence conversion, Hermitian pole, domain all survive | **HELD** (all four re-derived and correct) |
| N1 | my matrix reproduces the three even + three odd cross-check entries to 1e-18 | **HELD** (agreement to 20–21 printed digits) |
| N2 | even certified bound reproduces to ≥ 8 significant digits (`1.0310177602e-13`) | **FAILED as stated** — mine is `1.0310178165e-13`, agreeing only to 7 digits. Benign: the whole difference is Gershgorin slack (my entry radii are 2400× smaller), the *float* eigenvalues agree to 17 digits, and my bound is **larger**, so the advertised constant still stands. Recorded as a failure because the prediction was quantitative and wrong. |
| N3 | odd certified bound reproduces to ≥ 8 significant digits | **HELD** (10 digits: `5.859070853…`) |
| N4 | `ε_D < 1e-35`; `ε_C ∈ [1e-16,1e-15]` even, `[1e-17,1e-16]` odd; `ε_p < 1e-400` | **HELD** (`2.67e-38`, `3.885e-16`, `9.535e-17`, `2.4e-406`) |
| N5 | Schur correction `< 1e-28` (even) | **HELD** (`1.976e-29`) |
| N6 | frozen-vector score upper endpoint in `[1.0310177e-13, 1.0310179e-13]`, lower endpoint `> 0` | **HELD** (`1.03101781651300e-13`) |
| N7 | lower bound and score sandwich the minimum to relative width `< 1e-6` | **HELD** (`2.3e-14` even, `5.6e-15` odd) |
| N8 | endpoint checker: `1.031e-13`/`5.859e-11` ACCEPT, `1.032e-13`/`5.86e-11` REJECT | **HELD** (8/8 on my own checker with my own endpoints) |
| N9 | even sector with flipped pole sign has `λ_min < -0.5` | **HELD** (`-5.788`) |
| N10 | odd sector with flipped pole sign stays positive at ~`1.7e-6` | **HELD** (`1.71884712655414e-6`) |
| N11 | closed-form pole vector matches `‖p_N‖` to 1e-11 | **HELD** (every printed digit) |
| N12 | singular `V` refused | **HELD** |
| N13 | nonorthogonal invertible `V` handled with correct norm conversion | **HELD**, and strengthened so the naive alternative visibly fails |
| N14 | missing `ε_D` → NO_VERDICT | **HELD** |
| N15 | excessive coupling → REJECT | **HELD** |

No kill condition fired. Two predictions failed (P0 unresolved, N2 quantitatively wrong); both are preserved above.

---

## Verdict

**INDEPENDENTLY VERIFIED, with the following exact scope and constants.**

For `L = 7/10` and `T = 120`, with `W`, `R_T`, `Ψ`, `Π` as defined in §D7.1, I independently certify, from my own derivation and my own ball-arithmetic implementation:

1. `R_T(f) ≥ 1.031·10⁻¹³ ‖f‖²` for every real even `f ∈ L²([-L,L])` (my endpoint `1.03101781648892e-13`);
2. `R_T(f) ≥ 5.859·10⁻¹¹ ‖f‖²` for every real odd `f` (my endpoint `5.85907085398903e-11`);
3. hence `R_T(f) ≥ 1.031·10⁻¹³ ‖f‖²` and `W(f) ≥ 1.031·10⁻¹³ ‖f‖²` for every complex `f ∈ L²([-L,L])`, with `W` extended-real-valued and `+∞` off `𝒟_W`;
4. and, on the explicit-formula class, `Σ_ρ h(γ_ρ) ≥ 1.031·10⁻¹³ ‖f‖²` — this last step alone rests on the literature explicit formula, which I did not re-prove.

Both advertised constants are valid after downward rounding, and D6's withdrawal of `5.86e-11` in favour of `5.859e-11` is confirmed as necessary. My independently certified endpoints are slightly *larger* than Fable's, so nothing needs weakening.

**What is NOT established, and remains outstanding:**
- **Only this window.** `L = 0.7`, `T = 120`. Nothing here says anything about any other support half-width, and `T = 120` is only 0.8 % above the threshold `2π e^B = 119.087` at which `β*` turns positive.
- **Weil's criterion needs every admissible test function**, i.e. every window. A fixed-window certificate has no RH consequence, and the residual gap is a quantifier, not a constant. This audit supplies no mechanism for that quantifier.
- **A second machine / second arithmetic library.** Both my reconstruction and Fable's ran on this machine against the same Arb build. Correctness of python-flint/Arb is assumed by both.
- **Four analytic lemmas** (the `j_n`/`i_n` series bounds, the strip bound `|j_n(z)| ≤ e^{|Im z|}`, the Legendre/`i_n` coefficient identity, and `Ψ ≥ β*` off `[-T,T]`) now have text proofs from two independent authors, but no machine-checked or refereed proof.
- **The quadrature constant citation** (ATAP Thm 19.3) is unverified; my reconstruction avoids depending on it.
- **The claimed prior art** (Zhu, arXiv 2608.24827, `L = 0.8`) was not checked — it postdates my knowledge and I did not fetch it. Novelty is therefore UNVERIFIED, and no novelty is claimed either way.
- **No bridge to `c = 7/10`.** Out of scope by directive and unsupported by anything in this round.

---

## Reproducibility

```
repo   /Users/peterviviani/golden-horizon-principle   branch codex/metatron-prime-return-v0
HEAD at audit open  b68b14c988c6a8e14ab565135fcea14c3700de55
owner commit landed mid-audit  18f0005  (no audited file touched)
predictions commit  b372ccecda2410f029f9fd98e2069b175e204696   (before any compute)
results commit      e09a3d6a35aeaa6fcf0907a63cda193034e62fce
python  /private/tmp/weil-arb-gTYWza/venv/bin/python   python-flint 0.6.0 (Arb), mpmath 1.4.1
cd experiments/weil_hidden_modes
python opus_d7_rebuild.py even 80 1     # -> opus_d7_even_NE80_pole+1.json   (27 s)
python opus_d7_rebuild.py odd  80 1     # -> opus_d7_odd_NE80_pole-1.json    (27 s)
python opus_d7_rebuild.py even 80 -1    # pole-sign mutation control
python opus_d7_rebuild.py odd  80 -1    # pole-sign mutation control
python opus_d7_controls.py              # -> opus_d7_controls.json           (seconds)
python opus_d7_sameform.py              # -> opus_d7_sameform.json           (~3 min)
# replay control, run from a scratch directory so no repository file is written:
mkdir -p /tmp/replay && cd /tmp/replay && python <repo>/experiments/weil_hidden_modes/d5_certify.py 80 48 even 1
```
Files I created (all prefixed `OPUS-`/`opus_d7_`): `OPUS-PREDICTIONS-D7.md`, `OPUS-ROUND-D7-RESULTS.md`, `opus_d7_rebuild.py`, `opus_d7_controls.py`, `opus_d7_sameform.py`, `opus_d7_*.json`, `opus_d7_*.log`. No existing file was edited or deleted.

---

## For an eight-year-old

Someone built a fence around a small playground and said: **inside this playground, every possible wobble is a safe wobble — none of them can go below zero.** They wrote down exactly how safe: at least a tiny number, like 0.0000000000001.

My job was to not believe them. So I worked out the shape of the fence from scratch, on my own paper, and then measured the playground again with different rulers — a different way of computing the wiggly Bessel numbers, a different way of adding up the areas, and a safety margin I proved myself instead of copying from a book I couldn't open. I got the same answer, to twenty digits. I also checked the *infinitely many* wobbles that are too fast to fit in my list, and showed they can only change the answer by less than a millionth of a billionth of a billionth.

Then I tried to break the safety-checker before trusting it. I gave it missing evidence — it refused to answer. I gave it a broken ruler — it refused. I gave it a slightly-too-greedy claim (`5.86` instead of `5.859`) — it said no, and it was right to: the person who built the fence had rounded that number the wrong way and had already fixed it. I flipped one sign in the formula on purpose: in one half of the playground everything collapsed, which is good — but in the *other* half the wrong formula still looked perfectly safe. That's the scariest thing I found, and it isn't a bug in the checker: **a checker that only asks "is it positive?" cannot tell you that you asked about the right thing.** Only re-deriving the formula catches that, which is why I did.

So the fence is real. **But it is one small playground.** The big question — the Riemann Hypothesis — needs every playground of every size to be safe, and nobody here has shown that. Making this one playground a tiny bit bigger might break everything, and this work gives no way to know. What we have is a carefully checked answer to a small question, and an honest map of how far it doesn't reach.
