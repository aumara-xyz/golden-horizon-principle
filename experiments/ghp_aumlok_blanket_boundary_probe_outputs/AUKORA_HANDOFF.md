# ABB-001 Aukora Handoff

Status: local lab design plus synthetic simulation complete.

This is engineering falsifiability only.

## Bottom Line

ABB-001 is a good GHP probe because it isolates three layers that are easy to confuse:

1. observer-visible ceremony projection
2. advisory bond / UX state
3. legal authority state

The probe says:

```text
ceremony may move advisory bond state
ceremony may not move legal authority
authority moves only when a real verifier says so
```

## Exact Invariant To Port

```text
Let N_t be the scrubbed observer-visible ceremony projection.
Let B_t = f(N_t) be the advisory bond state.
Let A_t = 1[Verify(sigma_t, pk_t, c_t) = 1] be legal authority.

Then:

VerifierAbsent_t -> A_t = 0
Forbidden(N_t) -> reject projection and A_t = 0
N_t^(1) = N_t^(2) -> B_t^(1) = B_t^(2)
hidden_non_authority_shift -> no change in B_t and no change in A_t
```

## Recommended Aukora Implementation

Add a projection-only shadow boundary around the ceremony flow:

1. derive a scrubbed ceremony projection from visible fields only
2. compute advisory bond state from that projection
3. independently compute legal authority only from the cryptographic verifier path
4. reject any projection containing private or authority-bearing fields
5. flag authority-like language such as `approved` or `grantsAuthority` as ceremony-only unless verifier output exists
6. assert duplicate visible projections yield identical advisory bond state
7. assert hidden non-authority changes do not move either advisory or authority output

## Strongest Failure Mode

Ceremony-language laundering:

- advisor says `approved`
- projection includes `grantsAuthority=true`
- placeholder signature string looks official
- injected hidden key material slips into projection

Any of those becoming authority is a boundary failure.

## What Must Remain Symbolic / UX Only

- phrase witness summaries
- voice witness summaries
- bond language
- ceremony completion language
- resonance / familiarity presentation
- any metaphoric language about bond, anchor, or presence

None of that is legal authority.

## What Needs a Follow-Up Probe

ABB-001 is negative-only on authority by design.

Next follow-up:

```text
ABB-002:
add a real verifier-positive reference case
to show that authority can flip only through actual verification
```
