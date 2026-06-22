# Write-Rebound-Release Notes

Status: toy telemetry only.

These probes test the sonoluminescence-inspired analogy carefully: a boundary event may have an after-effect or wake, but the analogy does not prove GHP physics.

## WRR-001

File: `ghp_write_rebound_release_probe.py`

Question: do write / witness / release labels improve prediction of the next full surprise state?

Result: fail.

Safest read: the first whole-state rebound framing is too broad. Current visible state already carries most of the next-surprise signal, and the ternary receipt labels do not improve it.

## WRR-002

File: `ghp_write_rebound_residual_probe.py`

Question: after current visible state is known, do actual receipt actions explain the next residual wake?

Result: fail overall, but with a useful sub-signal.

The receipt action improves `delta_uncertainty` prediction over projection-only and shuffled controls by about `0.0060` MAE, with no meaningful private-leakage gain. It does not meaningfully improve `delta_pressure`, and the full pass gate fails because the rebound is not broad enough across targets.

## Current Interpretation

The live candidate is not:

> a write immediately moves the whole state.

The better candidate is:

> a legal write first changes public uncertainty / readability, then later dynamics may relax around that updated boundary record.

For paper use, this is not ready for promotion. For the next lab step, test a narrower `readability-relaxation` law:

- target public confidence / uncertainty residuals directly,
- require shuffled-receipt controls,
- require hidden-leak controls,
- require lagged downstream effects before claiming rebound,
- keep Chronos and metaphysical claims out of the result.

Do not claim sonoluminescence proves GHP, consciousness, time extrusion, identity, or physical observer selection.

## RRL-001

File: `ghp_readability_relaxation_probe.py`

Question: does a receipt first change public readability / uncertainty, and does that later reduce surprise?

Result: fail, but directionally informative.

The receipt model improves immediate and lagged uncertainty residuals over projection-only and shuffled controls, but the gains are below promotion threshold. The lagged surprise gain is small, and the leaky/private-friction control remains too helpful on uncertainty. This means the current toy does not justify a paper claim.

Best next step: either find a public, legal proxy for friction/readability that removes the leaky advantage, or move the test into Aukora where actual receipts, gate refusals, retries, and memory updates create a real after-effect trace.
