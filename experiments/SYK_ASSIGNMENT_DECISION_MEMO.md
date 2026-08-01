# SYK Assignment Decision Memo — the one physics choice blocking the Nebius run

- artifact_id: SYK-ASSIGNMENT-DECISION-MEMO-2026-08-01
- lane: P-002a / OP 111 / OP 179 (SYK beta corridor)
- audiences: the owner (the decision is his alone), Zeb's lane, and the phi/Opus lane
- status: **DECISION MEMO — no run, no data, no verdict.** This document changes nothing by
  itself. It lays out the single physics decision that every downstream gate
  (`experiments/SYK_CORRIDOR_PREREG_v1.md`, `experiments/SYK_STANDARD_NULL_AUDIT.md` section 6,
  `experiments/op179_nu_to_beta.py`) is waiting on, plus recommended values for the
  operational prereg fields. Every load-bearing definition is quoted verbatim with its source;
  nothing is reconstructed from memory.

---

## 1. The decision, in one sentence

Before any corridor data exists, the owner must pin exactly one of the four candidate
channel-exponent assignments into the injected port of `experiments/op179_nu_to_beta.py`
(`ChannelExponentAssignment`, which has **no default** and raises if unset), together with a
written nu-to-beta conversion protocol satisfying OP 179 — and must do so **by argument, not
by default**, because the four candidates are physically distinct and the sources supply no
first-principles reason to prefer one.

## 2. The four candidates, with verbatim AE.8/AE.9 provenance

All quotes in this section are verbatim from `GHP_v1_618_MASTER.md` (Addendum AE; AE.8 begins
at line 10952, AE.9 at line 10974 of the copy on this branch).

### 2.1 What the exponent even is (AE.8, section 5.10A.2)

> **Status:** CRITICAL CLARIFICATION. Addresses mutually inconsistent pair of claims flagged
> by Kimi 2026 hostile review: the Fibonacci band [1/φ, φ] ≈ [0.618, 1.618] and the
> tricritical-Ising boundary CFT (ν_TCI = 5/9 ≈ 0.556, below the band floor).
>
> **The critical exponent bounded by the Fibonacci band [1/φ, φ] is the fusion-channel
> renormalization exponent β_fusion, derived from the eigenvalue spectrum {φ, −1/φ} of the
> Fibonacci fusion matrix N_τ via the Verlinde formula (§5.10B). It is NOT the standard CFT
> correlation-length exponent ν of the boundary theory.**

and, on the corridors specifically (AE.8, consequence iii):

> (iii) The SYK N=22 β-extraction pre-registration (§5.10A.5) and the mass-deformed
> golden-chain pre-registration (§5.10A.6) both remain active, but their output must be
> related to β_fusion, not to the boundary CFT's ν. The kill-condition window [1.95, 2.05]
> remains the quantitative falsification target for β_fusion specifically.

### 2.2 Candidate A — magnitude-of-eigenvalue assignment, β_crit ≈ 1.236 (AE.9, section 5.10A.3)

> **Status:** SUGGESTIVE POST-DICTION. Not a band-to-point theorem. Not a derivation.
> Included for completeness because the calculation is clean and the numerical coincidence is
> worth logging.
>
> **Calculation.** Given Fibonacci fusion rule τ ⊗ τ = 1 ⊕ τ with fusion probabilities
> P(1) = 1/φ², P(τ) = 1/φ (Verlinde-derived), and under the specific channel-exponent
> assignment β(1) = 1/φ, β(τ) = φ (magnitudes of the eigenvalues of N_τ):
>
> $$\beta_{\text{crit}} = P(1)\,\beta(1) + P(\tau)\,\beta(\tau) = \frac{1}{\varphi^3} + 1 \approx 1.236$$
>
> **Numerical coincidence:** 1.236 is within 1.1% of ν_TCI = 5/4 = 1.25.

And its honest caveat (AE.9, why-not-a-derivation, item ii):

> (ii) ν_TCI = 5/4 is the M(4,5) order-parameter exponent, a quantity known before this
> calculation was performed. Hitting 1.236 is post-hoc agreement, not prediction.

### 2.3 Candidates B, C, D — RMS 1.328, CFT-weight-based 1.412, squared eigenvalues 1.764 (AE.9, item i)

The sources' complete statement of the three alternatives is a single sentence:

> (i) The channel-exponent assignment β(1) = 1/φ, β(τ) = φ is not unique. Alternative
> natural assignments give 1.412 (CFT-weight-based), 1.764 (squared eigenvalues), or 1.328
> (RMS form). No first-principles argument currently forces the magnitude-of-eigenvalue
> assignment over the alternatives.

**That sentence is the entire written provenance of candidates B, C, and D.** No derivation,
no per-channel exponent values, and no formula for these three numbers appears anywhere in
`GHP_v1_618_MASTER.md` or the boundary papers on this branch. Any elaboration of what "RMS
form," "CFT-weight-based," or "squared eigenvalues" concretely assign per channel would be
reconstruction, and is therefore **MISSING-INPUT** here. Whichever candidate is chosen, the
choice memo that pins it must supply and cite that derivation.

### 2.4 What the candidates buy and what they risk (AE.9, closing paragraph)

> **What this does provide:** motivation for OP 179 (operationalize β_fusion) and a candidate
> numerical target to check against SYK N=22 / golden-chain DMRG extractions. If the SYK
> extraction lands near 1.236, that is evidence for the magnitude-of-eigenvalue assignment.
> If it lands elsewhere in the band, that falsifies this specific channel-weighting choice
> while leaving the band itself unchanged.

Note that this paragraph's logic is only available if the assignment is chosen FIRST. Which
brings us to the law.

## 3. The window-closing law

**The assignment must be preregistered BEFORE any corridor data exists.** Otherwise the
corridor cannot falsify anything:

- The four candidate targets — 1.236, 1.328, 1.412, 1.764 — span most of the decision
  geography. The pass band is B1 = [0.618034, 1.618034] and the kill window is
  K = [1.95, 2.05] (master section 5.10A.2, quoted in full in
  `experiments/SYK_STANDARD_NULL_AUDIT.md` section 3 and in the converter docstring).
- The corridor measures ν, not β (verbatim, `GHP_BOUNDARY_PROGRAM_v2.md` section 6.3: "The
  measured quantity is the transition exponent ν in mass-deformed SYK₄, even-parity sector,
  across N = 10, 14, 18, 22"). The nu-to-beta conversion rests entirely on the assignment.
- Therefore, if the assignment may be chosen AFTER a ν is measured, **any measured ν can be
  rationalized into any β**: pick the weighting whose conversion lands the number where you
  want it — in-band for a "pass," or out of K to dodge a kill. Four candidates is enough
  freedom to steer almost any outcome. A window that can be moved after the shot is not a
  window.
- This is the same discipline the master already imposes on itself: section 5.10A.5 ("The
  band is the commitment," as carried into `experiments/SYK_CORRIDOR_PREREG_v1.md` section 0)
  and the forbid list carried in prereg section 4 (no retrospective narrowing, no
  retrospective widening, no kill-window reinterpretation, no silent supersession, no
  band-substitution escape). The assignment is exactly such a commitment, and it is the last
  one still unpinned.

The choice must also be made **by argument, not by default**: `op179_nu_to_beta.py` was
deliberately built with no default so that silence cannot choose. Candidate A is the only one
with a written calculation, but AE.9 itself says no first-principles argument forces it —
"has a calculation attached" is provenance, not an argument. The owner's signing memo must
state why the chosen weighting is the physically correct operationalization of β_fusion for
this observable.

## 4. Where the standard null lands, per candidate

Short answer: **for the corridor's actual measurement route (ν), this is not derivable from
the sources — for any of the four candidates.** Verbatim, the audit's finding
(`experiments/SYK_STANDARD_NULL_AUDIT.md` section 5):

> **The standard-physics null for the corridor's actual measurement route (ν) cannot be
> placed relative to the pass band or the kill window from the repo's documents. That
> placement is MISSING-INPUT.**

The reason is structural, not a gap in effort: the four candidate numbers are β_crit POINT
values under alternative channel weightings; the sources contain **no formula mapping a
measured collapse exponent ν to β_crit** under any of them (that formula IS the OP 179 gap).
Until an assignment plus conversion protocol is written down, mapping the standard ν-nulls —
mean-field ν = 1/2 (Louw et al. 2024, quoted in AE.8 item iv), ν_TCI = 5/9, and the stable
tricritical/quotient lane ν ≈ 0.7 — into β space is impossible on paper. Per prereg section 3
this mapping is a **HARD GATE**: after the port is pinned, the standard-null audit must be
re-run under the pinned conversion, and if any standard ν-null lands in the pass band B1, the
preregistration is VOID and no compute is committed (`GHP_CORE_v3.md` section 8: "No new
compute for any test whose pass-region contains the standard-physics answer").

What IS derivable from the quoted numbers alone (arithmetic only, no new physics):

| Candidate | β_crit target | vs pass band B1 [0.618034, 1.618034] | vs kill window K [1.95, 2.05] |
|---|---|---|---|
| A — magnitude-of-eigenvalue | 1.236 | inside | outside |
| B — RMS form | 1.328 | inside | outside |
| C — CFT-weight-based | 1.412 | inside | outside |
| D — squared eigenvalues | 1.764 | **outside** (above band ceiling) | outside (below kill floor) |

Two derivable observations, flagged as this memo's only original content in this section:

1. The **direct-β standard null is assignment-independent**: β_crit = 2 (Fermi golden rule
   under GUE, master section 5.10A.1 as quoted in the audit's section 4) sits at the center
   of K and outside both bands no matter which assignment is pinned. The kill window's
   loadedness in β space does not depend on this decision. What depends on it is whether the
   ν-route nulls stay out of the pass band — and that is exactly the un-derivable part.
2. Candidate D is self-undermining on the quoted numbers: its own predicted point (1.764)
   lies outside the pass band it would be defending, in the no-man's-land between the band
   ceiling (1.618034) and the kill floor (1.95). If the owner leans toward D, the signing
   memo must explain what a "pass" would even look like under it. This is arithmetic on
   quoted values, not a physics argument against D.

## 5. Recommended owner-fill values for the operational prereg fields

**STATUS: RECOMMENDATIONS ONLY — AWAITING OWNER RATIFICATION.** None of the following is
pinned by this memo. These are proposed fills for the [OWNER-FILL] fields of
`experiments/SYK_CORRIDOR_PREREG_v1.md`, offered so the owner ratifies or amends concrete
numbers rather than blanks. They become binding only when written into the prereg and signed.

- **κ grid (prereg section 1).** The master's prior grid is, verbatim
  (`GHP_v1_618_MASTER.md` line 8512, Addendum U item AI4): "**Mass-deformation κ grid:**
  [0, 16.6, 16.7, 16.8, 16.85, 16.9, 16.95, 17.0] — identical to current N=22 run. No grid
  modification post-seed." And the failure on record, verbatim (`GHP_BOUNDARY_PROGRAM_v2.md`
  section 6.3): "its κ grid no longer brackets the crossing." The sources do not record on
  which side the crossing escaped, so the recommendation extends the prior grid on **both**
  sides while keeping every prior point as a subset for comparability:

  RECOMMENDED κ grid: [0, 15.8, 16.2, 16.4, 16.6, 16.7, 16.8, 16.85, 16.9, 16.95, 17.0,
  17.1, 17.2, 17.5, 18.0]

  plus a mechanical bracketing rule fixed at signing: the fitted crossing must be strictly
  interior with at least two grid points on each side, else the run is void (no post-hoc
  grid extension; a widened grid is a new timestamped preregistration).

- **Seeds (prereg section 1).** RECOMMENDED: **40 disorder seeds per size, explicit range
  5000–5039 inclusive**, per (N, κ) point, N ∈ {14, 18, 22} for official fits (N = 10
  telemetry only, per the carried ban). 40 matches the master's own AI4 discipline ("40
  disorder seeds per (N, κ)") and the prior tight7×40 design. The range 5000–5039 is
  disjoint from the seed ranges already consumed on this branch (AH4-P1-POWERED v2 used
  3000–3399; SILVER-OPT-GEO v1 used 4000–4099) and — per prereg section 1 — any seeds from
  the dead tight7×40 partial run are EXCLUDED regardless (its exact range is not recorded in
  the sources; if the owner knows it overlaps 5000–5039, shift the recommended range, do not
  reuse).

- **Bootstrap non-degeneracy (prereg section 2).** RECOMMENDED: ν search interval
  [0.30, 1.50]; 2000 bootstrap resamples; the fitted ν must lie strictly in the interval's
  interior, and **no more than 5%** of the bootstrap mass may sit within the outermost grid
  cell at either edge of the search interval. A bootstrap violating either condition is
  DEGENERATE (the prior run's failure mode: "ν pegged at the grid ceiling") and the run is
  not certifiable; a rerun with a widened interval is a new timestamped preregistration.

- **Convergence / collapse-quality thresholds (prereg section 2).** RECOMMENDED: per-size
  scaling-collapse quality R² ≥ 0.98, and cross-size collapse correlation ≥ 0.99 (the
  sources record a preliminary "Pearson 0.999 cross-size correlation" as shape universality
  but define no acceptance threshold; 0.99 is deliberately below the preliminary so the
  criterion does not smuggle in the old data's performance as a requirement).

- **Budget cap (prereg section 5).** RECOMMENDED: **hard cap USD 400** for the entire
  corridor run — all sizes, all seeds, including reruns voided by degenerate bootstraps. The
  cap is a kill switch, not a target: hitting it with an incomplete grid voids the run and
  produces no verdict.

## 6. Closing statement — the law this memo serves

**The corridor may not run and no Nebius spend of any size may occur until:**

1. the channel-exponent assignment is chosen **by argument, not by default** — a signed
   choice memo stating which of the four candidates is pinned and why, with the conversion
   formula written out and its derivation cited (Candidates B/C/D additionally require the
   currently-MISSING derivations of their assignments);
2. the operational prereg fields (κ grid, seed count and range, bootstrap non-degeneracy
   thresholds, convergence thresholds, budget cap) are ratified by the owner — the section 5
   values above are recommendations, not decisions;
3. the standard-null audit (`experiments/SYK_STANDARD_NULL_AUDIT.md` section 6) is re-run
   under the pinned conversion and shows the pass region clean of every standard ν-null —
   if it is not clean, the corridor dies here, before spend, exactly as the DMRG band did;
4. `experiments/SYK_CORRIDOR_PREREG_v1.md` is signed, with the SHA-256 of the signed prereg
   and of `experiments/op179_nu_to_beta.py` recorded in the ledger row.

Until all four are discharged, the only live content of this corridor remains the unfired
kill window — and per the sources, no SYK number may be reported as GHP support in either
direction. Nothing in this memo is evidence for GHP. Software echoes may inform the theory;
they do not confirm the physics.
