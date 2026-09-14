# D27 two-brackets pilot — RESULTS (DeepSeek 4.1 Flash, 2026-09-14)

Base efc7a20. `experiments/deepseek_d27_two_brackets/`. Budget: ~25 single-core
CPU-minutes of the 60 cap; wall within 90.

## Task 0 — corrections (committed before compute)

Both appended to `../deepseek_d26_bracket/RESULTS.md` (nothing edited in place):
(a) the "impossible for a valid lower enclosure" logic slip corrected — two
valid lower bounds may differ freely; the D22 value is void for D24's reasons;
(b) the D26 closure carried "court audit incomplete (C2)" until this run.

## Task 1 — C2 layer-cake: PASSES

`d27-c2-layer-cake.py`: planted frequency-domain Gaussian F(t)=e^{-t²/4} (tails
in closed form), both sides computed with rigorous `acb.integral`, Gaussian
tail bounds explicit, at T=8 and T=12. LHS and RHS intervals intersect with
full agreement to every printed digit at both cutoffs. **Identity HOLDS**; the
D26 closure's label upgrades to **court audit complete (C2 verified)**.

## Task 2 — L-threading control: PASSES

`d27-lthread-control.py` (clean-room quadrature, Step-0 style) recomputed saved
D22 L=0.5 matrix entries (1,1), (1,3), (21,41): agreement to 20+ digits
(e.g. (21,41) = −0.067255662984916726916 both sides, radii ~1.6e-23), 7.3 s.
L=0.5 scores admissible from this run.

## Task 3 — L=0.5 odd: gate fails, bracket open

- Visible set at L=0.5: **{n=2} only** (log 3 = 1.0986 > 2L = 1.0; Astra's
  "2 and 3 visible" line matches L=0.6 and was not followed — flagged in the
  ledger).
- Stage A: certified visible floor **ℓ = 0.000180934196848** (D26 cert:
  λ0 matched the candidate's reduced minimum; Schur tails ~1e-298/−146/−957).
- Stage B: frozen D22 candidate (constrained boundary-vanishing minimizer).
  Its full-W lower endpoint (T=1024, fresh enclosure) = 0.00020911 >
  1.1ℓ = 0.00019903 → **energy gate FAILS** — the scoped no-go: no tail
  improvement can close a 10% bracket for this candidate.
- Stage C: W ∈ [0.00020911, 0.00021539] at T=1024 (wave enclosure 3.0%);
  **W_hi/ℓ = 1.1904 — open.** Published open; no T escalation, no reselection.

## Task 4 — L=0.4 even: gate fails, bracket open (the informative hard case)

- Stage A: certified visible floor **ℓ = 0.000172308870206** (λ0 matches the
  candidate's reduced minimum 0.000172308870199; tails negligible).
- Stage B: frozen D22 even candidate. Fresh full-W lower endpoint at T=1024 =
  0.000190480 > 1.1ℓ = 0.000189540 → **energy gate FAILS** (at T=512 the
  weaker endpoint 0.000189460 sat marginally under 1.1ℓ; the tighter T=1024
  endpoint decides). Scoped no-go.
- Stage C: W ∈ [0.000190480, 0.000194524] at T=1024 (wave enclosure 2.1%);
  **W_hi/ℓ = 1.1289 — open.** Astra's ">1.5" estimate was pessimistic: the
  mass-conditioned tail tightened further than expected, but the gate fails on
  the wave itself, not the tail.

## The three sectors, one table (all T=1024)

| sector | ℓ (certified) | W enclosure | W_lo/ℓ | W_hi/ℓ | verdict |
|---|---|---|---|---|---|
| L=0.4 odd | 0.0141715765223 | [0.0152552, 0.0154249] | 1.0764 | **1.0884** | **infimum bracket CLOSED** (gate pass) |
| L=0.5 odd | 0.000180934196848 | [0.00020911, 0.00021539] | 1.1557 | 1.1904 | open — gate fail (scoped no-go) |
| L=0.4 even | 0.000172308870206 | [0.000190480, 0.000194524] | 1.1055 | 1.1289 | open — gate fail (scoped no-go) |

## Prediction ledger outcome

| # | predicted | measured |
|---|---|---|
| 1 | C2 holds to enclosure width | ✓ exact agreement |
| 2 | threading control ≥15 digits | ✓ 20+ digits |
| 3 | L=0.5: gate pass (1.058), T=1024 ratio 1.06–1.10 closing | gate FAILS (wave endpoint 1.1557/ℓ) and ratio 1.1904 — **miss** (wrong: predicted on the reduced-form ratio, the full-W endpoint decides) |
| 4 | L=0.4 even: open, ratio >1.5 | open, but 1.1289 — direction ✓, magnitude miss (tail better than estimated; gate decides) |

Wall sentence (achieved, restated):

*odd L=0.4 closed at 8.8% with an audited court (C2 verified); L=0.5 odd and
L=0.4 even fail their energy gates — the frozen candidates cannot close —
open at 19.0% and 12.9% respectively.*

## Implementation slips recorded (mine, none affecting the numbers above)

- A sed copy kept the D26 `HERE` path: two output JSONs briefly landed in the
  D26 directory (moved back).
- A sed missed the ℓ literal in the even run: the first printed even ratio used
  the L=0.5 floor; corrected against ℓ_even in the saved JSON, and the gate
  sentence above uses the corrected numbers (the raw W enclosures were never
  affected).
- No stuck commands; no over-budget stages this run.

## One paragraph

With the court's C2 identity now numerically interval-verified and the L=0.5
data path controlled to 20 digits, the two-bracket question has a clean
answer: the L=0.4 odd sector's infimum bracket is closed at 8.8% with an
audited court, while the two harder sectors both stop at the *energy gate* —
their frozen candidates' full-W lower endpoints exceed 1.1ℓ, so no
tail-computation improvement can close them without a new candidate (which
this protocol does not authorize). The even L=0.4 sector tightened far better
than preregistered expectations (1.129 not >1.5), and the L=0.5 odd sector
sits at 1.190; both are recorded open with their exact limiting quantities.
No claim about the Riemann Hypothesis is made or implied.

## Files

`PREDICTIONS.md`; `d27-c2-layer-cake.py` / `d27-c2-result.json`;
`d27-lthread-control.py`; `d27-l05-clean.py` / `d27-l05-bracket.json`;
`d27-cert-visible-even-L04.py` / `d27_cert_visible_evenL04_*.json` /
`d27-l04-even-clean.py` / `d27-l04-even-bracket.json`.
