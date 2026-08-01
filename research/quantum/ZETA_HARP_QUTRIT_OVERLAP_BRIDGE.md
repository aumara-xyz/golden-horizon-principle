# The Zeta Harp Qutrit Overlap Bridge — the exact mathematics

Layer: EXACT SCIENCE (with the register constructions of layer 2 clearly marked).
Adopted 2026-08-01 per `docs/ZETA_HARP_QUANTUM_PORTAL_ADDENDUM.md`. Everything numbered
here is machine-checked in `experiments/zeta_harp_quantum/`.

## 1. The single-qutrit space H3

H3 = C^3 with orthonormal basis {|0>, |1>, |2>} (equivalently labeled
{|-1>, |0>, |+1>}; the labels are a naming choice). A general qutrit state is

    |phi> = a|0> + b|1> + c|2>,   a, b, c in C,  |a|^2 + |b|^2 + |c|^2 = 1.

The genuine two-pole superposition of the pole labels is |B> = (|-1> + |+1>)/sqrt(2),
which is distinct from the basis state |0> (correction B of the addendum).

## 2. The three-qutrit register H27

    H27 = C^3 (x) C^3 (x) C^3  ≅  C^27,

with product basis |t2, t1, t0>, t_i in {0, 1, 2}, indexed by i = 9 t2 + 3 t1 + t0.
The state |0,0,0> (index 0) is the RESERVED REFERENCE BASIS STATE / INTERFACE ANCHOR:
by convention it carries zero amplitude in every embedding below. The 3x3x3 layout is a
chosen register, not a zeta-derived topology.

## 3. The 26-term window

The Riemann-Siegel main sum truncates at N(t) = floor(sqrt(t/2pi)). N(t) = 26 exactly on

    [2*pi*26^2, 2*pi*27^2) = [4247.4332676534..., 4580.4420889339...),

the 26-term window. Below it N = 25, at its right endpoint N becomes 27. (Boundary
behavior is tested to 1e-6 on either side; the printed decimals are tested to 1e-9.)

## 4. The states

Fix t with N = N(t). With theta(t) the Riemann-Siegel theta function and

    phi_n(t) = theta(t) - t ln n,        A_N = sum_{n=1}^{N} n^(-1/2),

define two normalized states over the term labels n = 1..N (embedded in H27 for N = 26
via any of the three register mappings; the identity below is representation-blind):

    |psi(t)> = (1/sqrt(A_N)) sum_{n=1}^{N} n^(-1/4) e^{i phi_n(t)} |n>,
    |w_N>    = (1/sqrt(A_N)) sum_{n=1}^{N} n^(-1/4) |n>.

Both carry the weights n^(-1/4)/sqrt(A_N), so

    <psi|psi> = (1/A_N) sum_n n^(-1/2) = 1 = <w_N|w_N>.

## 5. The overlap identity

With M(t) = 2 sum_{n=1}^{N} n^(-1/2) cos(phi_n(t)) the Riemann-Siegel MAIN SUM:

    M(t) = 2 A_N Re<w_N|psi(t)>.

**Two-line proof.**

    <w_N|psi(t)> = (1/A_N) sum_n n^(-1/4) · n^(-1/4) e^{i phi_n(t)}
                 = (1/A_N) sum_n n^(-1/2) e^{i phi_n(t)},
    so  2 A_N Re<w_N|psi(t)> = 2 sum_n n^(-1/2) cos(phi_n(t)) = M(t).   qed

Machine verification: residual < 1e-31 at t = 4300/4400/4500 at adoption (resident
lane, high precision); < 1e-37 at 40 digits in this build; < 3e-15 in the float64
pipeline across the grid t = 4250..4580 and at t = 1e4 (N = 39) and t = 1e6 (N = 398).
The identity is N-generic — and phase-generic: it holds for ANY phase assignment with
these weights (see the null controls), which is precisely why it is an embedding
statement and not a statement about zeta.

## 6. What this is, exactly

**This is an EXACT FINITE-DIMENSIONAL EMBEDDING OF THE RIEMANN-SIEGEL MAIN SUM.**
Nothing more:

- It represents the MAIN SUM M(t), not the Hardy function. The full relation is
  Z(t) = M(t) + R(t) with the remainder R(t) = O(t^(-1/4)) (leading Riemann-Siegel
  correction (-1)^(N-1) (t/2pi)^(-1/4) Psi(p) + ...), and R(t) lives OUTSIDE the
  register. A zero of M(t) is not a zero of Z(t); the reference instrument
  (`experiments/zeta_harp/`) discloses the same omission.
- Z_ref context: any comparison against reference values of Z(t) (mpmath's
  siegelz / Odlyzko tables) must carry the remainder term; this layer never conflates
  the two.
- No speedup claim: evaluating the overlap classically costs exactly the N terms the
  main sum costs; the Hadamard readout assumes a state-preparation oracle whose cost is
  not claimed.
- No RH claim: the identity holds identically in t on the critical line and says
  nothing about off-line zeros.

## 7. Register mappings (layer 2, for N = 26)

Three bijections of terms n = 1..26 onto the 26 noncentral basis states of H27, all
reported neutrally, |0,0,0> reserved with zero amplitude in each:

1. **lexicographic** — n -> base-3 digits of n.
2. **balanced ternary** — n -> balanced-ternary digits of v(n) (v = n-14 for n <= 13,
   v = n-13 for n >= 14; the zero value is excluded), digit d -> trit d mod 3.
3. **Gray-like ternary** — n -> reflected-ternary Gray code of n (consecutive codes
   differ in exactly one trit).

Reconstructed M(t) is identical under all three (inner products are basis-blind); the
mapping documents are printed in `outputs/qutrit_register.json`.
