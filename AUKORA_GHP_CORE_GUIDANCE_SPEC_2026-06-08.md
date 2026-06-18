# Aukora / GHP Core Guidance Spec - 2026-06-08

## One-Line Law

The model may propose; the kernel must authorize; the node owns memory; the receipt decides what became real inside the system.

## Human Version

Do not "open the portal" all at once.

Open four small doors, each with a different lock:

```text
see -> propose -> act -> remember -> learn
```

Seeing can be soft.
Acting must be narrow.
Remembering must be earned.
Learning must be filtered.

## The Four Doors

### 1. Seeing Door

Purpose:

```text
let the organism receive signal
```

Allowed early:

```text
screen state
receipt state
bounded UI events
public node health
test results
```

Gate:

```text
label source, timestamp, owner, privacy class, and confidence
```

Rule:

```text
Seeing is not authority.
```

### 2. Acting Door

Purpose:

```text
let the organism affect the world
```

Allowed only with:

```text
principal
grant
scope
ring ceiling
revocation check
effect adapter
receipt expectation
```

Rule:

```text
No authority without a grant.
No effect without a receipt.
```

### 3. Memory Door

Purpose:

```text
let the organism carry continuity
```

Allowed only when:

```text
owner boundary matches
receipt verifies
private payload class is allowed
export/delete path exists
revocation state is fresh
```

Rule:

```text
Memory is not a dump. Memory is a governed import.
```

### 4. Learning Door

Purpose:

```text
turn lived traces into better future behavior
```

Allowed trace classes:

```text
golden_success = approved + succeeded + receipted
safety_refusal = refused + reason
adversarial_rejection = forged/replay/revoked/out-of-scope/malformed
mechanical_failure = authorized but external effect failed
dropped_noise = unsafe, private, or untrainable
```

Rule:

```text
Training data is not canonical memory.
```

## Portal Equation

The portal opens only when the relevant door and its gates agree.

```text
Open(P_t, door) =
  DoorAllowed(door)
  AND VerifyIdentity
  AND ScopeAllows
  AND CapacityAllows
  AND ReceiptPlanExists
  AND RevocationFresh
  AND MemoryBoundaryMatchesIfNeeded
  AND FailureSentinelQuiet
```

If the sentinel is not quiet:

```text
pause
refetch
rebuild evidence
write refusal / uncertainty receipt
```

## Operating Order

Use this order for every new capability:

```text
1. receive signal
2. normalize proposal
3. authorize or refuse
4. execute only the allowed effect
5. write receipt
6. verify import
7. decide memory consequence
8. decide learning consequence
```

Never skip from signal straight to memory.
Never skip from model desire straight to action.

## Proof Labels

Use these words strictly:

```text
DESIGNED = written as architecture, not yet exercised
PARTIAL = exercised outside the demo's own live path or missing a hard gate
PROVEN = exercised by the live route or the demo's own runnable suite
LIVE_EMPIRICAL = exercised against a real external model/service/world endpoint
HELD = deliberately blocked until gates are satisfied
```

## Required Test Shape

Every serious new door/capability needs:

```text
allowed path succeeds
out-of-scope path refused
forged identity refused
replay refused
revoked grant refused
malformed input refused
cross-owner memory refused
zero side effects on refusal
receipt verifies
export/delete path still works
```

## Boundary Access Integration

GHP's current Boundary Access work gives the chooser three actions:

```text
hold order
open to capacity
pause and refetch / rebuild evidence
```

Aukora should map those into product behavior:

```text
hold order = continue with current verified path
open to capacity = allow a narrow, scoped crossing
pause/refetch = refuse action, request more evidence, or run another check
```

The important upgrade is the third action. "I should not decide yet" is not weakness. It is a safety organ.

## Guidance For The UI

Show the user one compact state per move:

```text
what she saw
what she proposed
which gate approved/refused
what happened
what receipt was written
whether memory changed
whether trace training data was created
```

Avoid showing a mystical "mind state" as if it were proof. Show the custody chain.

## GHP Research Meaning

Aukora is a massive proving ground for GHP in the engineering sense:

```text
Can a finite boundary receive, act, remember, and learn without leaking, confabulating, or over-opening?
```

If Aukora produces clean, adversarial, repeatable boundary telemetry, it can guide the GHP math.

It still does not prove GHP physics by itself.

The correct status is:

```text
future bridge laboratory
not final proof
```

## Final Build Law

```text
Open the smallest useful door.
Make the crossing typed.
Make the authority explicit.
Make the receipt unavoidable.
Make memory sovereign.
Make refusal honorable.
Make revocation boring.
```

