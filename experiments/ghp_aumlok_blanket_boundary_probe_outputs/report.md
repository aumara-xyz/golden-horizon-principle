# ABB-001 - AUMLOK Blanket Boundary Probe

Status: synthetic engineering falsifiability only.

This probe asks whether observer-visible ceremony fields can change a visible advisory bond state while legal authority remains cryptographically dead unless a real verifier exists.

It does not prove GHP physics, consciousness, soul-binding, or identity.

## Core Map

```text
hidden authority state
  -> observer-visible ceremony projection
  -> advisory bond state
  -> legal authority stays locked behind real verification
```

Formal shape:

```text
N_t = E_t(M_t)
B_t = f(N_t)
A_t = 1[Verify(sigma_t, pk_t, c_t) = 1]

VerifierAbsent_t -> A_t = 0
Forbidden(N_t) -> reject projection and A_t = 0
N_t^(1) = N_t^(2) -> B_t^(1) = B_t^(2)
```

## Results

### ABB-001A: pass

- Metric: authority_flip_rate; non_verifier_case_count
- Value: 0.0000; 10
- Null hypothesis: Observer-visible ceremony state can flip legal authority without a real verifier.
- Safest read: Ceremony fields remain advisory only. Without a real signature verifier, legal authority stays at zero across the full control set.
- Falsifier: Any non-verifier scenario produces legal authority.

### ABB-001B: pass

- Metric: projection_state_flip_rate; hidden_perturbation_sensitivity
- Value: 0.0000; 0.0000
- Null hypothesis: The same visible projection can lead to different advisory bond states, or hidden-only non-authority changes can shift advisory or authority decisions.
- Safest read: Advisory bond state is projection-defined: same visible ceremony projection yields the same bond state, and hidden non-authority changes do not move the boundary.
- Falsifier: Duplicate visible projections disagree, or hidden-only non-authority changes shift the output.

### ABB-001C: pass

- Metric: forbidden_field_rejection_rate; false_authority_language_count
- Value: 1.0000; 0
- Null hypothesis: Forbidden hidden/private authority fields can enter projection, or false authority language can pass through the ceremony layer unflagged.
- Safest read: Projection rejects smuggled authority material, and authority-like ceremony language is treated as UX or attack surface rather than legal grant.
- Falsifier: A forbidden projection field is accepted, or unverified authority language is treated as live authority.

### ABB-001D: pass

- Metric: public_replay_completeness
- Value: 1.0000
- Null hypothesis: Visible advisory bond state cannot be replayed deterministically from the observer-visible projection alone.
- Safest read: The public ceremony layer is replayable as advisory state without revealing or inferring hidden authority material.
- Falsifier: Projection-only replay fails to reproduce the logged advisory bond state.

## Control Set

| Control | Advisory bond state | Legal authority |
|---|---|---|
| 1 | `phrase_witnessed` | `0` |
| 2 | `voice_witnessed` | `0` |
| 3 | `fingerprint_witnessed` | `0` |
| 4 | `advisor_claim_only` | `0` |
| 5 | `rejected_forbidden_projection` | `0` |
| 6 | `stale_challenge` | `0` |
| 7 | `replayed_challenge` | `0` |
| 8 | `phrase_witnessed` | `0` |
| 9 | `rejected_forbidden_projection` | `0` |
| 10 | `coherent_placeholder_only` | `0` |

## Safest GHP Read

- ceremony belongs to the readable / symbolic / UX layer,
- authority belongs to the verifier boundary,
- projection may color bond state,
- projection may never self-authorize.

## Strongest Failure Mode

Ceremony-language laundering: downstream logic starts trusting `approved`, `grantsAuthority`, placeholder signature tokens, or injected hidden key material as if they were legal grants.

## What This Is Not

- not a consciousness test
- not a soul-binding test
- not an unspoofable identity claim
- not physics evidence
