#!/usr/bin/env python3
"""Step 0 Clean-Room Matrix Rebuild for D24/D25 Foundation Validation.
Recomputes entries (1,1), (1,3), and (21,41) directly from the raw quadrature definition
for L=0.4, T=160, odd parity, and verifies agreement with saved JSON evidence.
"""
import sys, json, time
sys.path.insert(0, "/Users/peterviviani/golden-horizon-principle/experiments/weil_hidden_modes")
from flint import arb, acb, ctx

ctx.prec = 192
t0 = time.time()

L = arb('4/10')
T = 160
NE = 160
PAR = 'odd'
PSIGN = 1

ns = [2*m + 1 for m in range(NE)]
pi = arb.pi()
rho = arb(2)
h = arb(1)/2
a_ax = h*(rho + 1/rho)/2
b_ax = h*(rho - 1/rho)/2

pp = [
    (arb(2).log(), 2*arb(2).log()/arb(2).sqrt()),
    (arb(3).log(), 2*arb(3).log()/arb(3).sqrt()),
    (2*arb(2).log(), 2*arb(2).log()/2)
]
B = sum((w for _, w in pp), arb(0))

def _psi(sv):
    return (sv + 1).digamma() - 1/sv

def a_c(t):
    s1 = acb(arb(1)/4) + acb(0, 1)*t/2
    s2 = acb(arb(1)/4) - acb(0, 1)*t/2
    return (_psi(s1) + _psi(s2))/2 - acb(pi.log())

def Psi_c(t):
    return a_c(t) - sum((acb(w)*(acb(u)*t).cos() for u, w in pp), acb(0))

a0 = arb(0) - arb.const_euler() - pi/2 - 3*arb(2).log() - pi.log()
aT = a_c(acb(T)).real
beta = aT - B
assert beta > 0

cn_pref = {n: ((2*n + 1)/(2*L)).sqrt() * L * 2 / (2*pi).sqrt() * (-1)**((n - 1)//2) for n in ns}

def F_old(n, t, analytic=False):
    z = t * acb(L)
    if analytic and not (z.real > 0):
        return acb('nan')
    return acb(cn_pref[n]) * (acb(pi)/(2*z)).sqrt() * z.bessel_j(acb(n + arb(1)/2))

saved_path = "/Users/peterviviani/golden-horizon-principle/experiments/fable_d22_test2/d22_cert_odd_L0.4_T160_N160.json"
saved = json.load(open(saved_path))
saved_checks = saved.get("cross_check_vs_acb_integral", {})

print("=" * 70)
print(f"STEP 0 CLEAN-ROOM MATRIX VALIDATION (L={L}, T={T}, parity={PAR})")
print("=" * 70)

sup_psi = abs(aT + B - beta).abs_upper()

targets = [(0, 0), (0, 1), (10, 20)]
results = {}
all_passed = True

for (i, j) in targets:
    m, n = ns[i], ns[j]
    key = f"{m},{n}"
    print(f"Computing matrix entry ({m}, {n})...", flush=True)
    
    def integrand(t, analytic):
        return (Psi_c(t) - acb(beta)) * F_old(m, t, analytic) * F_old(n, t, analytic)
    
    I = acb.integral(integrand, acb(arb('1e-30')), acb(T), abs_tol=arb('1e-25'), rel_tol=arb('1e-25'), eval_limit=2000000, depth_limit=600)
    head = arb('1e-30') * sup_psi * abs(cn_pref[m]) * abs(cn_pref[n])
    entry = 2 * (I.real + arb(0, head.abs_upper()))
    
    saved_val_str = saved_checks.get(key, {}).get("new", None)
    saved_val = arb(saved_val_str) if saved_val_str else None
    
    overlaps = entry.overlaps(saved_val) if saved_val else False
    if not overlaps:
        all_passed = False
        
    results[key] = {
        "modes": (m, n),
        "recomputed": entry.str(20),
        "saved": saved_val_str,
        "overlaps": overlaps
    }
    print(f"  Entry ({m},{n}):")
    print(f"    Recomputed: {entry.str(20)}")
    print(f"    Saved JSON: {saved_val_str}")
    print(f"    OVERLAPS:   {overlaps}", flush=True)

print("-" * 70)
print(f"ALL TARGET ENTRIES VALIDATED: {all_passed}")
print(f"ELAPSED TIME: {time.time() - t0:.2f} s")
print("=" * 70)

if not all_passed:
    sys.exit(1)
