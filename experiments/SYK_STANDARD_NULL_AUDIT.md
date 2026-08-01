# SYK Corridor Standard-Null Audit (Boundary §12.4 item 2 — mandatory pre-compute)

- artifact_id: SYK-STDNULL-AUDIT-2026-08-01
- lane: P-002a / OP 111 / OP 179 (SYK β corridor)
- status: **PRE-COMPUTE AUDIT — no run, no data, no verdict on physics.** This document only
  places the standard-physics answer relative to the pass band and the kill window, from the
  repo's own documents. Every load-bearing definition below is quoted verbatim with its source;
  nothing is reconstructed from memory. Where the sources cannot place the null, that is said
  explicitly and it gates spend.

---

## 1. The mandate this audit discharges

Verbatim, `GHP_BOUNDARY_PROGRAM_v2.md` §12.4 ("The concrete next experiments, in priority
order"), item 2:

> **The SYK Module C corridor kill window (P-002 sibling; OP 111).** This is the *only other*
> window whose result genuinely means something, because no pre-registered β has ever actually
> been computed for it. The pipeline was broken — twelve scripts pointed at a stale, unrelated
> directory (now fixed, 2026-07-03), the N=22 seed run died mid-seed, the ν-collapse bootstrap
> is degenerate (ν pegged at the grid ceiling), and no ν→β conversion script exists. First fix
> the pipeline; then compute a real β under the OP 111 decision branch, which was written
> precisely to handle a stable ν≈0.7 result without either silently losing it or lazily
> overclaiming it. The corridor's kill window is real *only* if the standard null can fall
> outside it — this must be checked against the same σ′/8-9 audit that retired the DMRG band
> before any compute is committed.

And the governing criterion itself, verbatim, `GHP_CORE_v3.md` §8:

> **The rule (the discriminator criterion):** *No new compute for any test whose pass-region
> contains the standard-physics answer.* A test that cannot fail cannot inform.

## 2. The precedent being imitated: the σ′/8-9 audit that retired the DMRG band

Verbatim, `GHP_BOUNDARY_PROGRAM_v2.md` §6.2:

> The decisive development is a **2026-07-03 theory audit** (recorded in ledger P-002). Reading
> Feiguin et al. 2007 carefully, the mass deformation used here couples to the tricritical-Ising
> **σ′ operator** (scaling dimension Δ = 7/8, ≈85% confidence), which predicts a standard-CFT
> null exponent **β_null = 8/9 ≈ 0.889** — and 8/9 sits *inside* the pre-registered band
> [1/φ, φ]. This is the crux: **the band as designed contains the standard-CFT null.** An
> in-band DMRG result would therefore confirm known 2007-era conformal field theory, not GHP.

That audit's structure: identify the standard-physics prediction for the *measured quantity
in the units the decision rule is written in*, then check whether it lands in the pass band
(band retired) or can fall outside the kill window (window loaded).

## 3. The bands and the window under audit

Verbatim, `GHP_v1_618_MASTER.md` §5.10A.2:

> **Primary band B1: β_crit ∈ [1/φ, φ] = [0.618034, 1.618034].**
>
> **Extended band B2: β_crit ∈ [1/φ², φ] = [0.381966, 1.618034].**
>
> **Kill window K: β_crit ∈ [1.95, 2.05].**
>
> B1's endpoints are |λ_±| = {1/φ, φ}, the magnitudes of the Fibonacci fusion matrix
> eigenvalues (§5.10B). K is the Dyson β_D = 2 generic-spectrum target preserved verbatim
> from v0.669.

## 4. Placement in β space: the standard null lands INSIDE the kill window, OUTSIDE the pass band

The master states the standard-physics answer for β_crit directly. Verbatim,
`GHP_v1_618_MASTER.md` §5.10A.1 glossary (the passage distinguishing β_crit from the Dyson
index):

> - **Dyson index β_D ∈ {1, 2, 4}.** Discrete class label for random-matrix ensembles
>   (orthogonal / unitary / symplectic). Not a continuous parameter.
> - **Why both hit "2" at the generic point.** If the observer's spectrum is genuinely
>   β_D = 2 (GUE), a Fermi-golden-rule calculation of revival-degradation scaling gives
>   β_crit = 2 to leading order in 1/d. The kill window β ≈ 2 below is the *critical
>   exponent* value 2, which is the *prediction* of the Dyson β_D = 2 class under a specific
>   spectral assumption — not the Dyson index itself.

Arithmetic on the quoted numbers (this audit's only original content in this section):

- Standard null in β space: **β_crit = 2** (Fermi-golden-rule under GUE, as quoted).
- 2 ∈ [1.95, 2.05] → the standard null sits **at the center of the kill window K**.
- 2 ∉ [0.618034, 1.618034] and 2 ∉ [0.381966, 1.618034] → the standard null is **outside
  both B1 and B2**, i.e. outside the entire pass side.

Read against the two tests:

- **Discriminator criterion (`GHP_CORE_v3.md` §8):** the pass-region (B1, and the strong-pass
  neighborhoods of §5.10A.6.3) does **not** contain the standard-physics answer. In β space
  this corridor passes the rule the DMRG band failed — the design contrast is explicit in the
  sources: for DMRG, β_null = 8/9 fell *inside* the pass band (retired); here the generic
  answer is the *kill target by construction* ("K is the Dyson β_D = 2 generic-spectrum
  target").
- **§12.4 item 2 wording ("the kill window is real only if the standard null can fall outside
  it"):** read literally against the β-space placement, the standard null falls exactly
  **inside** K, not outside it. The sources resolve the apparent tension themselves: K exists
  *because* the generic answer lands there — a generic result "falsifies cleanly" (ledger
  P-002a) and "hitting it fires Kill Condition 9" (`GHP_BOUNDARY_PROGRAM_v2.md` §6.1). The
  window is loaded in the sense that matters: the standard answer cannot masquerade as a pass,
  and the kill can actually fire. What the §12.4 sentence adds — and what Section 5 below
  shows is NOT yet satisfied — is that this placement must survive the corridor's *actual
  measurement route*, which runs through ν, not through a direct β extraction.

## 5. Placement via the measured quantity ν: **CANNOT BE ESTABLISHED FROM THE SOURCES — MISSING-INPUT**

The corridor does not measure β directly. Verbatim, `GHP_BOUNDARY_PROGRAM_v2.md` §6.3:

> The measured quantity is the transition exponent ν in mass-deformed SYK₄, even-parity
> sector, across N = 10, 14, 18, 22.

and, same section:

> **no script exists that converts a collapse-ν into the pre-registered β_crit or applies the
> decision buckets.**

and the ledger row, verbatim, `RESEARCH_LEDGER.md` P-002a:

> Repaired pipeline + completed N=22 + a written ν→β conversion protocol satisfying OP 179.
> Until then: **the kill window [1.95, 2.05] is the only live content** — a generic-random
> result there falsifies cleanly

Standard-physics values *in ν space* that the sources do contain:

1. Verbatim, `GHP_v1_618_MASTER.md` AE.8 §5.10A.2, item (iv):
   > The Louw et al. 2024 (arXiv:2312.14644) result ν = 1/2 for coupled-SYK mean-field
   > criticality is likewise about the standard correlation-length exponent of that
   > transition, not about β_fusion. Its presence below the band floor does not falsify GHP
   > because it is not measuring the band's predicted quantity.
2. Verbatim, `GHP_BOUNDARY_PROGRAM_v2.md` §6.3 (the corridor's own preliminary):
   > The master's preliminary framing — repeated in §5.7, §5.10, and §6.0 — was "**ν trending
   > above 0.618 toward 0.7**," with §6 adding that the four-size data favor ν closer to 0.7
   > than to 1/φ, which would *falsify the original ν = 1/φ prediction*.
3. Verbatim, `GHP_v1_618_MASTER.md` AE.8 §5.10A.2 (the CFT sister quantity):
   > The tricritical Ising correlation length ν_TCI = 5/9 is an independent quantity derived
   > from the M(4,5) minimal-model operator content, and it is NOT a GHP prediction.

**The audit finding:** to place any of these ν-space standard values relative to B1 and K —
which are defined **in β space** — requires the ν→β conversion. The sources state that no
such conversion exists (OP 179 OPEN; P-002a "a written ν→β conversion protocol satisfying
OP 179" is a *future* gate; OP 111 "specified but never coded"), and per AE.9 the
channel-exponent assignment that any conversion would rest on is **non-unique** (candidates
1.236 / 1.328 / 1.412 / 1.764 — see `experiments/op179_nu_to_beta.py`, where the assignment
is an injected port). Therefore:

> **The standard-physics null for the corridor's actual measurement route (ν) cannot be
> placed relative to the pass band or the kill window from the repo's documents. That
> placement is MISSING-INPUT.**

This is not a formality. The DMRG band was retired precisely because the σ′ audit *could*
place the standard null and found it in-band. Here the equivalent audit **cannot be completed
at all** until the ν→β port is filled — which means it is currently unknown whether, under
the eventually chosen assignment, the ν-route standard null (mean-field ν = 1/2, or a stable
tricritical/quotient ν ≈ 0.7) maps inside the pass band, inside K, or elsewhere. Any of those
outcomes is possible on paper until an assignment is pinned.

## 6. Consequence for spend (this finding gates Nebius)

Per the §12.4 item 2 mandate ("before any compute is committed") and the `GHP_CORE_v3.md` §8
discriminator criterion, the order of operations is forced:

1. **No Nebius (or any) compute for the SYK corridor may be committed now.** The β-space
   placement (Section 4) is favorable, but the corridor measures ν, and the ν-route
   standard-null placement is MISSING-INPUT (Section 5).
2. Before any spend: the owner must pin one channel-exponent assignment (the injected port of
   `experiments/op179_nu_to_beta.py`, candidates per AE.9) and a written ν→β conversion
   protocol satisfying OP 179, inside a signed preregistration
   (`experiments/SYK_CORRIDOR_PREREG_v1.md`).
3. **Then this audit must be re-run under that pinned conversion**: map ν = 1/2 (Louw
   mean-field), ν_TCI = 5/9, and the ν ≈ 0.7 tricritical/quotient lane through the pinned
   converter and record where each lands relative to B1, B2, K and the §5.10A.6.3 buckets.
   If the pinned conversion sends any standard ν-null into the pass band, the corridor fails
   the discriminator criterion exactly as the DMRG band did, and the spend is refused before
   it happens.
4. Only if the re-run audit shows the pass-region clean of standard nulls under the pinned
   conversion does the corridor qualify for compute under the house rule.

## 7. No-upgrade sentences

Nothing in this audit is evidence for GHP. The β-space placement in Section 4 is a statement
about the *design* of the kill window, quoted from the sources; it does not certify the
corridor, and per `GHP_BOUNDARY_PROGRAM_v2.md` §6.3, "no SYK number may be reported as GHP
support in either direction" until the pipeline, run, and conversion protocol all exist.
Software echoes may inform the theory; they do not confirm the physics.
