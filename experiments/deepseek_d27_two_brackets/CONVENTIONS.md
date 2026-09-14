# Court-script conventions (D27, 2026-09-14)

The cross-script parameter and convention table for the Weil court scripts.
Written after three D26/D27 implementation slips (wrong `L`, copied `HERE`
paths, a scale-invariance misconception) — all were value-level copies inside
otherwise-identical scripts, the class graphify's file-level graph does not
cover. This table plus the L-threading control are the instruments for that
class. One home per fact; scripts cite this file.

## Function and coefficient convention

- Stored minimizer list = `c`; the function is
  `f(x) = Σ c_n · sqrt((2n+1)/(2L)) · P_n(x/L)` — the court re-applies the
  sqrt factor; **store `c`, not `c·sqrt(...)`** (D26 slip #4).
- `||f||² = Σ 2L·c_n²/(2n+1)`. `c` frozen by `d22_candidates2.py` is unit
  Euclidean; W is homogeneous degree 0 after normalization, so any nonzero
  scaling of `c` scores identically (D26 C5 slip).
- Parity: odd = polar/`sinh`/negative pole (`−2S²`); even = `cosh`/positive
  pole (`+2C²`). `pole_term(b, PARITY, L)` takes the parity as its 2nd arg;
  `compact_integral(b, PARITY, T, L)` likewise. `derivative_evidence` is
  parity-free.

## Per-run parameters (must match the data being scored)

| parameter | meaning | D26/D27 values |
|---|---|---|
| `L` | room half-width; **must equal the candidate's L** (D26 slip #1) | 0.4 / 0.5 |
| `T_R` | selector cutoff (certificate build) | 160 |
| `T_score` | scoring cutoff (mass-conditioned tail) | 512, 1024 |
| `K` | Gauss nodes per unit panel | 64 |
| precision | Arb bits | 192 (cert), 256 (score) |
| `NE` | modes (odd: n = 1..2·NE−1) | 80 or 160 |

## Visible set and symbol

- Visible prime powers: `log n < 2L`. L=0.4 → {2}; **L=0.5 → {2}** (log 3 =
  1.0986 > 1.0); L=0.6 → {2,3}; L=0.7 → {2,3,4}.
- `B = Σ w_n` over visible; `w_p = 2 log p/√p`; prime powers use the prime's
  log (`w_4 = log 2`, not `2 log 4/2`).
- `β = a(T) − B` with `a(t) = Re ψ(1/4 + it/2) − log π`.

## Certification quantities

- Certified floor `ℓ` (all-function): finite eigenbound `λ0` (d5_certify,
  eigenbasis-Gershgorin) + the 2×2 Schur with `d = β − ε_D − 2ε_p²`,
  `coupling = ε_C + 2·norm_pN·ε_p`; `ℓ` = smaller root of
  `(λ0−μ)(d−μ) = coupling²`. ε values come from the cert JSON of the SAME L
  and parity.
- Wave enclosure `[W_lo, W_hi]` at a cutoff: compact archimedean integral
  (Arb) + tail (lower `a(T)·M_lo`; upper via the D24 §4.3 mass-conditioned
  bound) + pole − prime; divide once by `norm2`.
- **Infimum ratio** = `W_hi / ℓ`. **Energy gate** = `W_lo ≤ 1.1·ℓ`, using the
  TIGHTER (higher) lower endpoint when several cutoffs are computed (the even
  L=0.4 case: T=512 said pass, T=1024 said fail; the tighter one decides).

## Mandatory controls before any new-L score

1. **L-threading control**: reproduce one saved matrix entry at the new L,
   Step-0 style, ≥15-digit overlap (D27 control: 20+ digits).
2. **C2 layer-cake**: verified once for the court (D27, planted Gaussian);
   re-run if the scoring code changes.

## graphify (file-level GPS; complements, never replaces, the above)

- venv: `~/aukora-lab/graphify-venv` (pinned 0.9.61); index:
  `~/golden-horizon-principle/experiments/graphify-out/` (gitignored; 6,904
  nodes in ~5 s; rebuild: `graphify update <path>`).
- Query: `graphify explain "<file-or-symbol>"`, `graphify path "A" "B"`.
- Skill deployed to `~/.config/opencode/skills/graphify/`.
