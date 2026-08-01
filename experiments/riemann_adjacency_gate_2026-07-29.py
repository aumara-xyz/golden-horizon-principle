#!/usr/bin/env python3
"""Receipt script for the Riemann adjacency map (Boundary Addendum B.4, LIT-RH001/003).

Verifies, dependency-free, the machine-checkable facts cited there.
EXTERNAL MATHEMATICS ONLY. Nothing here is evidence for GHP under any outcome.
"""
import itertools
import math

TOL = dict(cantor=1e-12, glaisher=1e-6)
failures = []

def check(name, ok, detail):
    print(f"  {name}: {'PASS' if ok else 'FAIL'}   {detail}")
    if not ok:
        failures.append(name)

print("GATE 1 — balanced ternary / 27 structure")
cells = list(itertools.product([-1, 0, 1], repeat=3))
vals = sorted(9 * a + 3 * b + c for a, b, c in cells)
check("bijection {-1,0,+1}^3 <-> -13..+13", vals == list(range(-13, 14)),
      "27 cells, center (0,0,0) -> 0")
check("torus carry-closure", (26 + 1) % 27 == 0, "index 26 + 1 -> index 0 (the loop)")

print("GATE 2 — Cantor string complex dimensions (LIT-RH001, Lapidus)")
D = math.log(2) / math.log(3)
period = 2 * math.pi / math.log(3)
worst = max(abs(1 - 2 * 3 ** (-complex(D, k * period))) for k in range(6))
check("poles of 3^-s/(1-2*3^-s) at D + 2*pi*i*k/log3", worst < TOL["cantor"],
      f"D={D:.6f}, period={period:.6f}, worst residual {worst:.2e} over k=0..5")

print("GATE 3 — hyperfactorial 1,4,27 -> 108 -> Glaisher -> zeta'(-1) (LIT-RH003)")
check("H(3) = 1^1 * 2^2 * 3^3 = 108", 1 * 4 * 27 == 108, "the 1-4-27 product")
n = 4000
ln_H = sum(k * math.log(k) for k in range(1, n + 1))
ln_A = ln_H - (n * n / 2 + n / 2 + 1.0 / 12) * math.log(n) + n * n / 4
zeta_prime_minus1 = 1.0 / 12 - ln_A
REF = -0.16542114370045092921  # published value of zeta'(-1)
err = abs(zeta_prime_minus1 - REF)
check("ln A = 1/12 - zeta'(-1)", err < TOL["glaisher"],
      f"asymptotic ln A={ln_A:.9f} at n={n} -> zeta'(-1)={zeta_prime_minus1:.9f} vs published {REF:.9f} (err {err:.1e})")
print("  note: the identity is a property of the hyperfactorial's asymptotics,")
print("  not of the number 108 itself.")

print()
if failures:
    print(f"GATE FAILED: {failures}")
    raise SystemExit(1)
print("ALL GATES PASSED — external mathematics verified; no GHP claim is supported by any of it.")
