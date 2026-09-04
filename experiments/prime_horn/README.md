# Smooth prime horn

This experiment turns the radii

`2, 3, 5, 7, 11, 13, 17, 19, 23, 29`

at equally spaced heights `0, ..., 9` into a smooth radius profile and revolves that
profile around the vertical axis. The default interpolation is monotone PCHIP rather than
an unconstrained cubic spline, so the surface does not invent radii below or above adjacent
prime layers.

Run:

```bash
python3 experiments/prime_horn/generate.py
```

Outputs:

- `outputs/prime_horn.stl` — watertight hollow printable shell;
- `outputs/prime_horn.png` — rendered inspection view;
- `outputs/profile.csv` — sampled `(height, radius)` profile;
- `outputs/metrics.json` — mesh and closure checks.

## Mathematical claim boundary

The surface is a faithful data sculpture of the chosen finite prime sequence. It does not
follow that its acoustic resonances are the primes. Resonances must be obtained from the
Helmholtz equation with specified material, wall, and end boundary conditions. A horn's
flare changes impedance and reflection, but “prime radii” do not automatically imply
prime eigenfrequencies or produce the Riemann zeta function.

A fair acoustic test would freeze the boundary conditions, solve the eigenproblem, and
compare the prime-radius horn against shuffled-gap and smooth-growth control profiles
before inspecting any prime-frequency accuracy.
