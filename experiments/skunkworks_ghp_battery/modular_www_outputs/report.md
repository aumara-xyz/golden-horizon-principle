# modular_www — Result Report (write/witness/release)

- **test_id:** modular_www
- **Lane:** engineering/verified-computation telemetry only
- **Primary operating point:** theta=0.1, w=4
- **System:** n=3 sites (dim 8), T=60 steps, register=6, 10 seeds.
- **Numerology guard:** phi=1.618034, violation=False (phi-FREE channel).
- **Leak-scan:** invalid=False.

## CLASSIFICATION: PASS-TERNARY

> Software/toy success is NEVER physics evidence (master hard rule 7): no outcome proves GHP, observer-boundary selection, phi selection, or a write-law; even a clean PASS is a single-toy engineering result and 'ternary witness is a universal memory law' is the forbidden upgrade that voids interpretation.

## Primary: designated metric per regime, ternary vs binary and degenerate controls (theta=0.10, w=4)

| regime | metric | vs | mean adv | k/10 | 95% CI | H1 pass |
|---|---|---|---|---|---|---|
| delayed-meaning | delayed_meaning_recovery | binary | +0.0000 | 0/10 | [+0.0000, +0.0000] | no |
| delayed-meaning | delayed_meaning_recovery | random-third | +0.0000 | 0/10 | [+0.0000, +0.0000] | no |
| delayed-meaning | delayed_meaning_recovery | rate-matched-binary | +0.0000 | 0/10 | [+0.0000, +0.0000] | no |
| contradiction | pollution | binary | +0.5000 | 10/10 | [+0.5000, +0.5000] | YES |
| contradiction | pollution | random-third | +0.4833 | 10/10 | [+0.3833, +0.5833] | YES |
| contradiction | pollution | rate-matched-binary | +0.5333 | 10/10 | [+0.4500, +0.6333] | YES |
| overload | overload_recovery | binary | +0.0000 | 0/10 | [+0.0000, +0.0000] | no |
| overload | overload_recovery | random-third | +0.0000 | 0/10 | [+0.0000, +0.0000] | no |
| overload | overload_recovery | rate-matched-binary | +0.0000 | 0/10 | [+0.0000, +0.0000] | no |
| concept-drift | retention | binary | -0.0500 | 1/10 | [-0.1500, +0.0000] | no |
| concept-drift | retention | random-third | -0.0500 | 1/10 | [-0.1500, +0.0000] | no |
| concept-drift | retention | rate-matched-binary | -0.0500 | 1/10 | [-0.1500, +0.0000] | no |

## Symmetric-loss guard (secondary retention & pollution vs binary)

| regime | secondary metric | mean adv (ternary better>0) | k/10 | ternary loses by H1 bar |
|---|---|---|---|---|
| delayed-meaning | retention | +0.0000 | 0/10 | no |
| delayed-meaning | pollution | +0.3833 | 9/10 | no |
| contradiction | retention | +0.0000 | 0/10 | no |
| contradiction | pollution | +0.5000 | 10/10 | no |
| overload | retention | +0.0000 | 0/10 | no |
| overload | pollution | +0.0000 | 0/10 | no |
| concept-drift | retention | -0.0500 | 1/10 | no |
| concept-drift | pollution | -0.0333 | 2/10 | no |

## Decision detail

- Winning metric x regime pairs (cleared H1 over binary AND both degenerate controls): [('contradiction', 'pollution')]
- Symmetric losses (ternary loses by H1 bar on retention/pollution): []

## Robustness sweep (theta x w) — CANNOT move the call

Designated-metric ternary-minus-binary mean advantage per regime:

| op point | delayed-meaning | contradiction | overload | concept-drift |
|---|---|---|---|---|
| theta=0.05,w=2 | -0.200 (k2) | +0.500 (k10) | +0.000 (k0) | -0.050 (k1) |
| theta=0.05,w=4 | +0.000 (k0) | +0.500 (k10) | +0.000 (k0) | -0.050 (k1) |
| theta=0.05,w=8 | +0.000 (k0) | +0.500 (k10) | +0.000 (k0) | -0.050 (k1) |
| theta=0.1,w=2 | -0.200 (k2) | +0.500 (k10) | +0.000 (k0) | -0.050 (k1) |
| theta=0.1,w=8 | +0.000 (k0) | +0.500 (k10) | +0.000 (k0) | -0.050 (k1) |
| theta=0.2,w=2 | -0.200 (k2) | +0.500 (k10) | +0.000 (k0) | -0.050 (k1) |
| theta=0.2,w=4 | +0.000 (k0) | +0.500 (k10) | +0.000 (k0) | -0.050 (k1) |
| theta=0.2,w=8 | +0.000 (k0) | +0.500 (k10) | +0.000 (k0) | -0.050 (k1) |
| theta=0.4,w=2 | -0.200 (k2) | +0.500 (k10) | +0.000 (k0) | -0.050 (k1) |
| theta=0.4,w=4 | +0.000 (k0) | +0.500 (k10) | +0.000 (k0) | -0.050 (k1) |
| theta=0.4,w=8 | +0.000 (k0) | +0.500 (k10) | +0.000 (k0) | -0.050 (k1) |

## Epsilon-sensitivity (brittleness flag, NOT optimized)

| regime | designated-metric adv spread across ±0.15 theta/cut |
|---|---|
| delayed-meaning | 0.0000 |
| contradiction | 0.0000 |
| overload | 0.0000 |
| concept-drift | 0.1000 |

## Size smoke check (n in {2,4}) — validity only, not the decision

| n | dim | binary commits | ternary commits | tr(rho_ref) | min eig |
|---|---|---|---|---|---|
| 2 | 4 | 60 | 31 | 1.0000 | 1.59e-02 |
| 4 | 16 | 60 | 31 | 1.0000 | 6.30e-05 |

---
Preregistration: experiments/MODULAR_WWW_PREREG_v1.md (LOCKED before run). Ledger slots T-004 / E-001 to be written AFTER the run, carrying this classification verbatim with the forbidden-upgrade sentence attached.