# Cascade Calibration And Ternary Notes

## CAS-006

Question:

```text
Is finite-depth projection a calibrated early-warning signal even when binary write/no-write F1 is weak?
```

Result:

```text
PASS
```

Key metrics:

```text
average AUC-like: 0.9711
raw-access AUC gap: +0.3004
shuffled-control AUC gap: +0.6940
top-decile capture: 0.8248
leaky/private gain: 0.0003
```

Read:

The finite-depth signal is strong. The earlier weakness was largely an action/scoring problem, not absence of signal.

## CAS-009

Question:

```text
Does write / witness / release outperform binary write/no-write as the boundary action alphabet?
```

Result:

```text
PASS
```

Key metrics:

```text
average macro F1: 0.7296
harmful write/release confusion: 0.0020
leaky/private gain: 0.0003
```

Read:

The ternary action alphabet is strongly supported in this toy setting. Many apparent binary failures were likely witness states.

## CAS-010

Question:

```text
Should this branch be eligible for cautious paper wording?
```

Result:

```text
PASS
```

Paper-safe wording:

```text
Toy observer-boundary probes suggest that finite-depth public projections may function better as calibrated early-warning signals feeding a write/witness/release action alphabet than as binary write/no-write classifiers.
```

Guardrail:

```text
No physics proof.
No consciousness proof.
No universal depth.
No observer-created-reality claim.
```
