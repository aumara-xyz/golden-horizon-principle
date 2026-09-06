# D11b — the right-angle fact does NOT survive room enlargement (VOID as structure)
Floating double precision, d11b_orthogonality.log/json. Prediction (ORTHOGONALITY-PREDICTIONS.md): ρ_L = |b·v_min|/‖b‖ ≤ 1e-4 at every L. **FAILED.**
| L | even λmin(C) | even ρ | odd λmin(C) | odd ρ | random-p control ρ |
|---|---|---|---|---|---|
| 0.4 | 1.8e-1 | 0.96 | 7.1e-1 | 0.77 | 0.3–0.98 |
| 0.5 | 7.6e-3 | 2.3e-2 | 1.5e-1 | 0.58 | 0.1–0.6 |
| 0.6 | 3.4e-5 | 1.3e-4 | 2.0e-3 | 5.3e-3 | 0.03–0.6 |
| 0.7 | 3.4e-8 | 1.0e-7 | 4.2e-6 | 1.6e-5 | 0.006–0.7 |
| 0.8 | 1.8e-12 | 5.1e-12 | 6.6e-10 | 3.8e-9 | 1e-4–0.3 |
Reading: ρ is not a constant of the problem; it tracks λmin(C) (ρ ≈ 3·λmin(C) in both parities, N = 40 and 80 identical). In small rooms the pole coupling is fully aligned with C's softest direction. As the room grows and C's softest eigenvalue collapses, the coupling along it collapses with it. That is what positivity forces (q ≥ (b·v_min)²/λmin must stay below a + κ‖p‖²); it is a consequence of the balance, not an explanation of it. The structural reading is VOID. Arch-only controls have ρ ≈ 0.5–0.8 at every L and an indefinite C from L = 0.6 on. Nothing here bears on L beyond 0.8.
