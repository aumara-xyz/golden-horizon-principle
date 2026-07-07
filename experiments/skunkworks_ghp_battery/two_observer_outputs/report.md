# Two-Observer Consensus Probe — Report
**Lane:** engineering / verified-computation. **Not physics evidence. Not GHP evidence.**
**Classification:** `KILL`

## No-upgrade
A PASS_SIGNATURE is only a request for a harder larger-L error-controlled follow-up; it is NOT evidence for GHP, NOT evidence for observer-boundary selection, and must never be upgraded to a physical claim.

## Setup
- Exact diagonalization, open chains, L_primary = 12, finite-size check L = 10.
- GOLDEN = XXZ at Delta = 1/phi = 0.618034 (golden-ratio-anisotropy critical chain, c=1). phi enters ONLY as a coupling, never in the observable.
- Controls: ISING (c=1/2), XX (c=1), HEIS (c=1), SILVER = XXZ Delta = sqrt2-1 = 0.414214 (c=1).
- Two overlapping intervals A,B; interface = overlap size [1, 2, 3, 4]. Metric: slope of I(A:B)/c vs log(geometric overlap factor). Reflected-entropy proxy tracked too.

## Primary result (L=12)
- GOLDEN slope (I/c): -0.14721 (L=10: 0.01643, stable=False, rel change=1.112).
- Control slopes (I/c): ISING=-0.05295, XX=-0.09913, HEIS=-0.15438, SILVER=-0.13681
- Control slope spread (RMS): 0.03892
- Separation of GOLDEN from CFT controls (spread units): ISING=2.42, XX=1.24, HEIS=0.18
- Separation from SILVER (non-golden metallic): 0.27
- Separation from same-c controls: XX=1.24, HEIS=0.18, SILVER=0.27
- Min same-c separation: 0.18

## Verdict logic
- PASS gate (>3 units vs every CFT control): False
- PASS gate (>3 units vs SILVER): False
- KILL if min same-c separation < 1.5: min = 0.18

**=> KILL**

GOLDEN's c-normalized consensus scaling is indistinguishable from generic c=1 critical-chain behavior. No architecture-linked golden signature; the golden-vs-control claim dies for this probe.
