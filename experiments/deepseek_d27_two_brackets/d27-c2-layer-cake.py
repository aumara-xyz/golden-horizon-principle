#!/usr/bin/env python3
"""D27 Task 1: numeric C2 layer-cake check, interval arithmetic.

Planted function: F(t) = e^{-t^2/4} (Gaussian in frequency; tail in closed form).
Identity: 2*int_T^inf log(t/2pi) F^2 dt  ==  log(T/2pi) M(T) + int_T^inf M(s)/s ds,
with M(s) = 2*int_s^inf F^2.
All inner integrals via acb.integral (rigorous); tails bounded by the standard
Gaussian tail bound:  int_x^inf e^{-2 a t^2} dt <= e^{-2 a x^2}/(4 a x).
Two cutoffs. Pass iff LHS and RHS intervals intersect.
"""
import sys, json, time, math
from pathlib import Path
from flint import acb, arb, ctx
ctx.prec = 256
HERE = Path('/Users/peterviviani/golden-horizon-principle/experiments/deepseek_d27_two_brackets')

ALPHA = arb(1) / 8           # F = exp(-ALPHA t^2 * 2)? use F^2 = e^{-t^2/2 * (1/2)}... keep explicit:
# Define F2(t) = e^{-t^2/4} = e^{-2*alpha*t^2} with alpha = 1/8 -> 2*alpha = 1/4. Consistent.
A2 = arb(1) / 4              # coefficient in exp(-A2 t^2)
T2 = arb(30)                 # truncation: tails ~ e^{-0.25*900} = e^{-225}, utterly below precision

def F2(t):
    return (-A2 * t * t).exp()

def g(t):
    return (t / (2 * arb.pi())).log() * F2(t)

def upper_int_F2(x):
    # int_x^inf F2 <= e^{-A2 x^2}/(2 A2 x)
    return ((-A2 * x * x).exp()) / (2 * A2 * x)

def upper_mass_tail_log(x_hi, x_lo):
    # int_{x_hi}^inf F2 * log(x_lo/T-style factors) handled by caller; here plain mass tail bound suffices
    return upper_int_F2(x_hi)

def check(T):
    T = arb(T)
    lhs_core = 2 * acb.integral(lambda t, analytic: acb(g(t)), acb(T), acb(T2), abs_tol=arb('1e-40'), rel_tol=arb('1e-40'), eval_limit=10**6, depth_limit=200)
    lhs_tail = 2 * ((T2 / (2 * arb.pi())).log() + 1) * upper_int_F2(T2)  # crude but e^{-225}-scaled
    LHS = lhs_core.real + lhs_tail

    # M(T) = 2*int_T^T2 F2 + 2*tail
    M_core = 2 * acb.integral(lambda t, analytic: acb(F2(t)), acb(T), acb(T2), abs_tol=arb('1e-40'), rel_tol=arb('1e-40'), eval_limit=10**6, depth_limit=200)
    M = M_core.real + 2 * upper_int_F2(T2)

    # int_T^T2 M(s)/s ds = 2*int_T^T2 F2(u) log(u/T) du + 2*log(T2/T)*int_T2^inf F2
    inner = 2 * acb.integral(lambda u, analytic: acb(F2(u) * (u / T).log()), acb(T), acb(T2), abs_tol=arb('1e-40'), rel_tol=arb('1e-40'), eval_limit=10**6, depth_limit=200)
    tail_int = ((T2 / T).log()) * 2 * upper_int_F2(T2)
    RHS = (T / (2 * arb.pi())).log() * M + inner.real + tail_int
    lo = min(LHS.lower(), RHS.lower()); hi = max(LHS.upper(), RHS.upper())
    overlap = LHS.intersection(RHS)
    return {'T': str(T), 'LHS': str(LHS), 'RHS': str(RHS),
            'LHS_width': str(LHS.rad() if hasattr(LHS,'rad') else LHS.upper()-LHS.lower()),
            'intersects': bool(overlap is not None and overlap != ()) if hasattr(LHS,'intersection') else None,
            'LHS_lower': str(LHS.lower()), 'RHS_upper': str(RHS.upper()),
            'RHS_lower': str(RHS.lower()), 'LHS_upper': str(LHS.upper())}

out = {}
t0 = time.time()
for T in (8, 12):
    r = check(T)
    l = arb(r['LHS']); rr = arb(r['RHS'])
    inter = l.intersection(rr)
    r['intervals_intersect'] = inter is not None
    out[f'T{T}'] = r
    print(f"T={T}: LHS={r['LHS'][:30]} RHS={r['RHS'][:30]} intersect={r['intervals_intersect']}", flush=True)
out['elapsed_s'] = round(time.time() - t0, 1)
out['verdict'] = 'IDENTITY HOLDS' if all(out[f'T{T}']['intervals_intersect'] for T in (8, 12)) else 'IDENTITY FAILS'
print(out['verdict'], f"({out['elapsed_s']}s)")
(HERE / 'd27-c2-result.json').write_text(json.dumps(out, indent=1) + '\n')
