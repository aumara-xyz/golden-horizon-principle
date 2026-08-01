# AH4-P1-POWERED v2 — VERDICT

- test_id: AH4-P1-POWERED-v2
- contract: `experiments/AH4_P1_POWERED_PREREG_v2.md` (SIGNED 2026-08-01)
- pipeline: `experiments/ah4_p1_pipeline.py`, byte-identical, SHA-256
  `59fc150a67971c1a2af65915e2233b681c88f8e3ba4b9fb0147a40da17e2cbc2`
  (verified by the wrapper before import)
- runner/analyzer: `experiments/ah4_powered_results/run_v2.py` (ADD-only
  wrapper; seed injection via module attribute, disclosed in its docstring)
- seeds: 3000-3399 (400 fresh; v1 seeds 1000-1019 excluded)
- raw run: `experiments/ah4_powered_results/raw_run_v2.json` (96 cells x 400 seeds)
- analysis: `experiments/ah4_powered_results/results.json`
  (10,000 paired bootstrap resamples, percentile 95% CIs)
- date run (UTC): 2026-08-01

## VERDICT: KILL

The structural-advantage hypothesis at n = 12 under this channel is dead.
Per the signed contract: no v3 with re-cut thresholds; reopening requires
the four-part-bar idiom (new channel family or new n = a new experiment
with its own prereg, not a reopen).

## Primary gate (fib − ising medians, uniform, scattered)

| f | Delta | 95% CI | rule | result |
|---|---|---|---|---|
| 0.25 | +0.00426 | [−0.00242, +0.01457] | reported, not gating | — |
| 0.50 | +0.00051 | [−0.01019, +0.03165] | > +0.02 AND CI excludes 0 | FAIL |
| 0.75 | 0.00000 | [0.00000, 0.00000] | > +0.02 AND CI excludes 0 | FAIL |

Both high-damage gates fail: the v1 point estimates (+0.065 at f = 0.50,
+0.101 at f = 0.75 on 20 seeds) do not replicate at 400 seeds. At f = 0.75
the fib and ising medians are both exactly 0.5 and the bootstrap
distribution of the median difference is degenerate at 0.

## Secondaries (preregistered, non-gating)

- **Trend slope of Delta vs f:** −0.00853, 95% CI [−0.02914, +0.00483] —
  CI includes 0. The v1 rising trend is DISSOLVED (point estimate is now
  negative).
- **fib − z3 (uniform, scattered):** CERTIFIED negative at all fractions:
  −0.05508 [−0.06176, −0.04490] at f = 0.25; −0.23723 [−0.24846, −0.12326]
  at f = 0.50; −0.18087 [−0.18137, −0.18069] at f = 0.75.
- **fib − classical (uniform, scattered):** CERTIFIED negative at all
  fractions: −0.04615 [−0.05283, −0.03584] at f = 0.25; −0.23380
  [−0.24315, −0.13773] at f = 0.50; −0.23598 [−0.23598, −0.23598] at
  f = 0.75.

The v1 surprises are certified at 400 seeds: the abelian and classical
arms are MORE recoverable than the Fibonacci arm under this channel, with
large margins at high damage.

## Burst mode (reported, no veto)

fib − ising at uniform: +0.03050 [+0.03050, +0.03830] at f = 0.25;
−0.01239 [−0.08111, −0.01239] at f = 0.50; 0.00000 [−0.07513, 0.00000]
at f = 0.75. Sign-mixed; no coherent structural advantage under burst
either.

## No-upgrade sentences (carried verbatim from the contract)

A pass is engineering evidence about an architecture in a simulated code; it is not evidence that nature selects φ. A kill closes this hypothesis, not GHP. Software echoes may inform the theory; they do not confirm the physics.
