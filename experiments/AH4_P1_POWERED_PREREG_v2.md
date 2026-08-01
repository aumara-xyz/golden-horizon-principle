# Preregistration — AH.4-P1-POWERED v2 (the powered structural sequel)

- test_id: AH4-P1-POWERED-v2
- date_locked: **PENDING OWNER SIGNATURE** (lock protocol as v1.1: signature line completed, sentinel dated, file hash to ledger, then and only then may the run execute).
- anchor: AH.4-P1 v1.1 verdict **INTERACTION/MIXED** (2026-08-01). The signed v1.1 outcome table says interaction "gets its own preregistration rather than a post-hoc story here." This is that preregistration.
- runtime: the EXISTING verifier-stamped pipeline (`experiments/ah4_p1_pipeline.py`), byte-identical — no physics code changes permitted. Same n = 12, same arms, same channel, same recovery, same scorer.

## 0. The declared hypothesis (new, stated before any v2 data)

v1.1 observed Δ(f) = fib − ising at uniform of +0.011 / +0.065 / +0.101 at f = 0.25/0.50/0.75, every CI including 0 at 20 seeds. The v2 hypothesis, motivated by that shape and committed before data: **structural advantage, if real, emerges under high damage.** v1's all-three-fractions rule is not re-used, and the reason is stated plainly: v1's own point estimate at f = 0.25 (+0.011) sits below the 0.02 margin, so a rule gating on f = 0.25 would fail regardless of seeds; carrying it forward would manufacture a predetermined kill, which is as dishonest as manufacturing a pass.

## 1. Design deltas from v1.1 (everything else inherited verbatim)

- Seeds: **3000–3399 (400 fresh seeds)**. The v1 seeds (1000–1019) are EXCLUDED from all v2 analysis — no double-dipping.
- Primary constant: uniform. Full 4 × 4 grid still run; other constants and modes are secondary.
- Expected CI half-width shrinks ~4.5× vs v1 (~±0.02 at f = 0.50), adequate to certify or dissolve the observed trend.

## 2. Rules (signed before data)

- **PASS (structural advantage at high damage):** Δ(0.50) > +0.02 AND Δ(0.75) > +0.02, each with 95% bootstrap CI (10,000 paired resamples) excluding 0. f = 0.25 is reported, not gating.
- **KILL:** either high-damage fraction fails its condition → the structural-advantage hypothesis at n = 12 under this channel is **dead**. No v3 with re-cut thresholds; reopening requires the four-part-bar idiom (new channel family or new n counts as a new experiment with its own prereg, not a reopen).
- **Secondary (preregistered, non-gating):** (a) trend slope of Δ vs f positive with CI excluding 0; (b) the v1 surprises — fib − z3 and fib − classical negative contrasts — re-measured at 400 seeds: certified or dissolved, reported either way.
- Burst mode: reported, no veto.

## 3. No-upgrade sentences (carried verbatim)

A pass is engineering evidence about an architecture in a simulated code; it is not evidence that nature selects φ. A kill closes this hypothesis, not GHP. Software echoes may inform the theory; they do not confirm the physics.

**Signed:** ______________________ (owner) **Date (UTC):** ____________

*Until signed: no run. The pipeline file's SHA-256 at signing is recorded alongside this contract's, so "byte-identical pipeline" is checkable.*
