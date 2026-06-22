# HRT-002 Boundary Trace Flow

Status: visual implementation guide / engineering handoff.

This graph summarizes the survived HRT invariant:

> Safe public telemetry may describe boundary mode, but it may not expose private state or influence authorization.

```mermaid
flowchart LR
  subgraph PrivateInterior["Private Interior"]
    P["proposal / hidden context"]
    K["keys, PoP, verifier internals"]
  end

  subgraph GateBoundary["Gate Boundary"]
    G["gate decision"]
    M["receipt mode: write / witness / release / unknown"]
  end

  subgraph Sanitizer["Telemetry Sanitizer"]
    A["positive allowlist"]
    S["recursive forbidden-field scanner"]
    F["fail closed on forbidden nested fields"]
  end

  subgraph PublicTrace["Public Boundary Trace"]
    T["event id, timestamp, mode, verdict, refusal cause"]
    W["safe confidence / stability / held-tension metadata"]
  end

  subgraph OfflineAudit["Offline Audit Only"]
    C["mode classifier vs shuffled control"]
    N["private and authority non-reconstruction tests"]
  end

  P --> G
  K --> G
  G --> M
  M --> A
  A --> S
  S --> F
  F --> T
  F --> W
  T --> C
  W --> C
  T --> N
  W --> N

  T -. forbidden .-> G
  W -. forbidden .-> G
  T -. forbidden .-> K
  W -. forbidden .-> K
```

## Current Lab Result

| Probe | Status | Metric |
|---|---|---|
| BTA-001 | pass | action macro-F1 `0.7624` vs shuffled `0.3333`; private `0.0230`; authority `0.0730` |
| WPF-001 | pass | witness action F1 `0.9983`; private `0.0272` |
| STP-001 | not promoted | sequence gain `0.00028` |
| SCM-001 / HCM-001 | not promoted | no public-policy gain over memoryless baseline |
| AIR-001 | green for HRT + witness only | build HRT-002 telemetry-only |

## Build Law

Build a boundary stethoscope, not a gate.

HRT-002 may help later analysis understand the boundary. It must never authorize, deny, retry, accelerate, or alter a gate decision.
