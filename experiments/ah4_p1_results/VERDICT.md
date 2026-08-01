# AH.4-P1 — VERDICT (mechanical application of prereg §2.2)

- test_id: AH4-P1-ANYON-RECOV-v1
- prereg: `experiments/AH4_P1_ANYON_RECOVERABILITY_PREREG_v1.md` (v1.1, SIGNED 2026-08-01)
- run date: 2026-08-01
- data: `experiments/ah4_p1_results/results.json` (96 cells x 20 seeds, seeds 1000-1019)
- analysis: `experiments/ah4_p1_results/analyze.py` -> `analysis.json` (bootstrap: 10,000 paired resamples over seed indices, RNG seed 20260801, percentile 95% CI)
- budget honesty: per-cell 120 s abort guard armed; **0 cells aborted** (slowest cell 0.9 s; full sweep well under budget). No value faked or extrapolated.

## Mechanical verdict

**INTERACTION/MIXED**

Rule applied exactly as written: STRUCTURAL ADVANTAGE requires Delta(f) > +0.02 with the 95% CI excluding 0 at all three fractions — fails (CI includes 0 at every fraction). PRIMARY KILL (flat) requires |Delta(f)| <= 0.02 at all three — fails (|Delta| > 0.02 at f = 0.50 and f = 0.75). Therefore the exhaustive rule's remaining branch fires.

## Primary Delta table (fib − ising, constant = uniform, scattered mode)

| f | median fib | median ising | Delta(f) | 95% CI | CI excludes 0 | Delta > +0.02 | \|Delta\| <= 0.02 |
|---|---|---|---|---|---|---|---|
| 0.25 | 0.880887 | 0.870059 | +0.010827 | [-0.062703, +0.058776] | no | no | yes |
| 0.50 | 0.752182 | 0.687500 | +0.064682 | [-0.031258, +0.137557] | no | yes | no |
| 0.75 | 0.601130 | 0.500000 | +0.101130 | [-0.097607, +0.123603] | no | yes | no |

## Outcome-table row that fired (prereg §2.1, verbatim)

> | **Interaction only** | Neither axis alone; the effect requires a specific pairing. Genuinely interesting, and it gets its own preregistration rather than a post-hoc story here. |

Mechanical note on the row assignment: the §2.2 rule's own third branch is the classifier — "anything else is **INTERACTION/MIXED**, reported under that name with no upgrade" — and that is the branch that fired. Axis-B is additionally NOT flat (below), so neither "flat in Axis B" row applies.

## Axis-B flatness check (max pairwise |Delta| of medians across constants within an arm, scattered; flat iff <= 0.02)

| arm | f=0.25 | f=0.50 | f=0.75 |
|---|---|---|---|
| fib | 0.169318 (not flat) | 0.136891 (not flat) | 0.089893 (not flat) |
| ising | 0.370059 (not flat) | 0.187500 (not flat) | 0.000000 (flat) |
| z3 | 0.022926 (not flat) | 0.136733 (not flat) | 0.080922 (not flat) |
| classical | 0.038832 (not flat) | 0.214953 (not flat) | 0.162552 (not flat) |

Axis-B flat everywhere: **NO**. Note: in every arm at every fraction, `uniform` or `golden` has the highest median and `bronze`/`silver` the lowest — the heavy-tail-beats-uniform direction of K-RECOV does not reproduce under this channel; recorded, not interpreted.

## Secondary contrasts (constant = uniform, scattered; fib minus other)

| contrast | f=0.25 | f=0.50 | f=0.75 |
|---|---|---|---|
| fib − z3 | −0.081341 [−0.168420, −0.008122] | −0.073801 [−0.151045, +0.027236] | −0.128277 [−0.229441, −0.051556] |
| fib − classical | −0.084884 [−0.161167, −0.012543] | −0.097120 [−0.172972, −0.017996] | −0.134848 [−0.235978, −0.095520] |

Fib does not beat z3 or classical at any fraction (all point estimates negative). Prereg §2.2(2) confound rule is therefore not triggered in its stated direction (it conditions on "Fibonacci beats classical and abelian", which did not occur).

## Burst stressor (fib − ising, uniform; reported separately, no veto power)

| f | Delta | 95% CI |
|---|---|---|
| 0.25 | +0.030505 | [−0.052757, +0.038298] |
| 0.50 | −0.046752 | [−0.113191, +0.056238] |
| 0.75 | +0.000000 | [−0.037567, +0.000000] |

## Prereg no-upgrade sentences (verbatim)

> anything else is **INTERACTION/MIXED**, reported under that name with no upgrade. The burst tear is reported separately as a stressor and cannot rescue or veto the primary rule.

> **Interaction only** — Neither axis alone; the effect requires a specific pairing. Genuinely interesting, and it gets its own preregistration rather than a post-hoc story here.

> - That a positive result proves the physical selection of φ. It would show a recoverability advantage for one fusion category in a simulated code, which is **engineering evidence about an architecture**, not evidence that nature selects it.
> - That any result here bears on the SYK corridor, the DMRG band, or the dynamical-selection lane, all of which are separately governed.
> - That software success constitutes physics evidence. The standing rule holds: *software echoes may inform the theory; they do not confirm the physics.*

No interpretation beyond the mechanical rule is offered in this document.
