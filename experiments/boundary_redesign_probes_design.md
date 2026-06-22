# Boundary Redesign Probes

## Purpose

This battery follows the negative de-circularized probes.

The goal is to make the analogues harder to fool:

```text
hidden dynamics generate truth;
public/projection features predict;
held-out seeds test generalization;
controls catch leakage, shuffled labels, and wrong topology.
```

## BCL-002 - Anti-Circularity Ledger Harness

Shared rules:

- train/test seed split,
- hidden truth generation separated from public predictors,
- shuffled or wrong-topology controls,
- explicit leakage flags,
- no Aukora handoff unless at least one scientific probe passes.

## CAC-003 - Delayed Collapse Classifier

Question:

```text
Can public lag features predict hidden collapse-like events?
```

Result:

```text
FAIL
```

Interesting detail:

```text
AUC-like score is high, but F1 is poor because clean event writes are rare and thresholding misses too many events.
```

Read:

The public signal ranks collapse risk, but it is not yet a usable write rule.

## NET-003 - Causal Topology Intervention Probe

Question:

```text
If one node is poked, can intervention responses recover hidden graph edges?
```

Result:

```text
FAIL
```

Read:

Wrong-topology control is beaten, but edge recovery remains too weak. The mesh idea needs stronger intervention design or richer graph inference.

## CAS-003 - Cascade Depth Sweep

Question:

```text
Is there an optimal finite depth for public nested projections?
```

Result:

```text
FAIL by threshold, but directionally interesting.
```

Interesting detail:

```text
depth_3 was best;
depth_3 beat depth_1 and depth_5;
leaky_depth_3 barely improved, so private leakage did not meaningfully help.
```

Read:

This is the best signal in the round. It suggests finite-depth nested projection may be real as an engineering shape, but the result is not strong enough yet for promotion.

## AUK-001 - Receipt Translation Gate

Result:

```text
BLOCKED
```

Reason:

```text
No scientific probe passed the promotion threshold.
```

## Next Redesign

- `CAC-004`: risk-ranking / early-warning metric instead of hard write-event F1.
- `NET-004`: use longer interventions and precision/recall over directed paths, not just immediate edges.
- `CAS-004`: focus on the finite-depth optimum with larger data, calibration curves, and withheld regimes.
