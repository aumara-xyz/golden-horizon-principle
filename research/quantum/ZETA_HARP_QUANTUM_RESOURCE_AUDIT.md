# Zeta Harp Quantum Resource Audit — qubits vs qutrits at N = 26

Adopted 2026-08-01 per `docs/ZETA_HARP_QUANTUM_PORTAL_ADDENDUM.md` (RQ4). Machine
verification: `experiments/zeta_harp_quantum/qubit_qutrit_compare.py` (both registers
reconstruct M(t) identically to < 1e-12; basis permutations leave it unchanged).

## The table

| register | units | basis states | states used (terms 1..26) | unused states |
|----------|-------|--------------|---------------------------|---------------|
| qubit    | 5     | 2^5 = 32     | 26                        | 6             |
| qutrit   | 3     | 3^3 = 27     | 26                        | 1 (the reserved anchor |0,0,0>) |

Smallest register sizes: 5 is the least number of qubits with 2^k >= 26; 3 is the least
number of qutrits with 3^k >= 26.

## The warning (directive's, binding)

The closeness of 27 to 26 proves nothing about hardware superiority. One unused state
versus six is a bookkeeping fact about integer powers, not a physics result: it says
nothing about gate fidelities, coherence times, control complexity, error correction,
or any other cost that determines what hardware is actually better at holding these
amplitudes. Both embeddings reconstruct the same M(t) exactly; the reconstructed
mathematics is register-blind (machine-tested under basis permutations). Any future
hardware statement requires hardware evidence, which this layer does not have and does
not claim.

## Notes

- The single unused qutrit state is assigned the INTERFACE ANCHOR role |0,0,0> by
  convention (zero amplitude, machine-tested). That role is symbolic-installation
  bookkeeping, not a resource saving.
- No preparation costs are audited here: state preparation is an assumed oracle
  throughout the layer, and its cost is not claimed in either register.
