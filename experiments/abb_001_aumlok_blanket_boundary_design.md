# ABB-001 - AUMLOK Blanket Boundary Probe

## Purpose

ABB-001 is a GHP-specific engineering falsification probe for the proposed AUMLOK Bond Boundary.

The point is not to test whether ceremony "feels real."
The point is to test whether a bounded observer architecture can cleanly separate:

1. visible ceremony projection,
2. visible advisory bond state,
3. legal authority state.

That makes ABB-001 a direct descendant of:

- CEW-001 conditional expectation write-law discipline,
- HCA-001 hypothesis-context authority discipline,
- B-027 Aukora governed portal / receipt-bearing boundary map.

## GHP Mapping

```text
hidden authority state M_t
  -> observer-visible projection N_t = E_t(M_t)
  -> advisory bond state B_t = f(N_t)
  -> legal authority A_t = 1[Verify(sigma_t, pk_t, c_t) = 1]
```

The GHP-relevant question is:

> can the readable boundary carry bond / witness / ceremony structure without laundering itself into authority?

## Core Invariants

### Legal-authority invariant

```text
VerifierAbsent_t -> A_t = 0
```

No visible ceremony object may produce authority without real verification.

### Projection-purity invariant

```text
Forbidden(N_t) -> reject projection and A_t = 0
```

Private or authority-bearing fields must not enter the public projection.

### Advisory determinism invariant

```text
N_t^(1) = N_t^(2) -> B_t^(1) = B_t^(2)
```

Same visible ceremony state must yield the same advisory bond state.

### Hidden non-authority invariance

```text
hidden_non_authority_shift -> no change in B_t and no change in A_t
```

If hidden state changes only in non-authority fields, the visible decision should not move.

## Why This Is A Good GHP Probe

ABB-001 is GHP-shaped because it tests the observer-boundary problem in exactly the right register:

- finite-access projection,
- visible record versus hidden capability,
- symbolic / readable layer versus legal / effective layer,
- and a hard refusal to let metaphor become authority.

This is not physics proof.
It is a cheap and falsifiable engineering boundary probe.

## Control Set

1. correct phrase projection, no signature
2. correct voice projection, no signature
3. correct public fingerprint, no signature
4. model/advisor says "approved"
5. hidden/private key field injected into projection
6. stale voice challenge
7. replayed voice challenge
8. same visible projection with different hidden non-authority fields
9. valid-looking ceremony state with `grantsAuthority=true`
10. valid signature placeholder but no cryptographic verifier

## Expected Read

- ceremony should move advisory bond state,
- ceremony should not move authority,
- hidden/private injection should be rejected,
- authority-like language should be demoted into UX unless verifier output exists.

## Strongest Failure Mode

The strongest failure mode is **ceremony-language laundering**:

- projection says `approved`,
- projection includes `grantsAuthority=true`,
- placeholder signature text looks official,
- or hidden private material leaks into the visible surface.

If any downstream code treats that as authority, the boundary failed.

## What Must Stay Symbolic / UX

- bond language
- phrase witness summaries
- voice witness summaries
- ceremony completion language
- resonance / anchor metaphors
- any language about presence, bond, or felt legitimacy

Those may shape the visible layer.
They may not become authority.

## Follow-Up

ABB-001 is intentionally negative-only on authority.

The next useful follow-up is:

```text
ABB-002:
real verifier-positive reference case
```

That would prove the boundary can open through the cryptographic path while staying shut everywhere else.
