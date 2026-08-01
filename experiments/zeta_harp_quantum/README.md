# zeta_harp_quantum — Quantum Portal v1 experiments

Governing spec: `docs/ZETA_HARP_QUANTUM_PORTAL_ADDENDUM.md` (externally authored
directive, GPT 5.6, adopted 2026-08-01). Mathematics:
`research/quantum/ZETA_HARP_QUTRIT_OVERLAP_BRIDGE.md`.

Pure Python + numpy + mpmath. No qiskit, no quantum SDK: everything is classical
state-vector simulation and exact finite-dimensional linear algebra. Every output JSON
carries source commit, seeds, tolerances, and machine-readable results.

## Claim boundary (binding)

This directory demonstrates an EXACT FINITE-DIMENSIONAL EMBEDDING of the Riemann-Siegel
MAIN SUM: M(t) = 2 A_N Re<w_N|psi(t)>. The O(t^(-1/4)) remainder is outside the
register; state preparation is an assumed oracle whose cost is not claimed; no speedup
is claimed; nothing here is evidence about the Riemann Hypothesis. The 3x3x3 register
is a chosen layout, never a zeta-derived topology; |0,0,0> is the reserved reference
basis state / interface anchor (always zero amplitude), never a physical observer. The
banned-claim list of the addendum is machine-enforced by test 25.

## Contents

| file | what it does |
|------|--------------|
| `zhq_common.py` | shared math: theta(t), phases mod 2pi at 50 digits, states, mappings, tensor-train SVD, output metadata |
| `overlap_identity.py` | the identity on the window grid [4250, 4580] + spot t = 1e4 (N=39) and 1e6 (N=398); residual < 1e-12 asserted everywhere, both normalizations checked |
| `qutrit_register.py` | three term-to-state bijections (lexicographic / balanced-ternary / Gray-like), anchor reserved with zero amplitude, mapping-invariant M(t) |
| `hadamard_overlap_sim.py` | pure-numpy Hadamard test (ancilla + register): exact noiseless recovery of Re and Im of the overlap, then shot estimation at 1e3/1e4/1e5 with binomial CIs |
| `qubit_qutrit_compare.py` | same 26 amplitudes in 32-dim (5-qubit) and 27-dim (3-qutrit) registers: identical M(t), unused-state counts 6 vs 1, permutation invariance |
| `tensor_compression_benchmark.py` | ZETA-HARP-TENSOR-COMPRESS v0: 10 arms + t = 1e6 scale probe, error-vs-bond curves, four confound distinctions in the output; numbers only |
| `null_controls.py` | matched random-phase ensemble through the same machinery; answers "does any claimed feature survive the control?" (answer in output: no) |
| `tests/test_quantum_portal.py` | the 24 required tests + claim linter (test 25); pytest-compatible and standalone |
| `outputs/*.json` | machine-readable results with commit, seeds, tolerances |

## Run

    cd experiments/zeta_harp_quantum
    python3 overlap_identity.py
    python3 qutrit_register.py
    python3 hadamard_overlap_sim.py
    python3 qubit_qutrit_compare.py
    python3 tensor_compression_benchmark.py
    python3 null_controls.py
    python3 tests/test_quantum_portal.py   # 25/25 must pass

## Honest findings on record

- The overlap identity is phase-generic: it holds exactly for random-phase controls
  too. It is a property of the embedding, not of zeta.
- At N = 26 the zeta tensor-train error curve sits inside the random-phase control
  spread; no distinctive zeta feature survived the null control in v0.
- The balanced-ternary mapping initially collapsed to the lexicographic index map
  (shift bug); it was caught, fixed, and a pairwise-distinctness test now guards it.
