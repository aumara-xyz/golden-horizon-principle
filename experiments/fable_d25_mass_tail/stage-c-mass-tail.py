#!/usr/bin/env python3
"""D25 Stage C — mass-conditioned tail bound (D24 §4.3) on the frozen trial-4 wave.

Implements: sqrt(M(s)) <= b/sqrt(pi s) + sqrt(D)/s  =>  M(s) <= C_T/s,
C_T = (b/sqrt(pi) + sqrt(D/T))^2;  M0 = min(Mbar(T), C_T/T);
A_tail <= M0 * [ log(T/2pi) + (log(C_T/(M0*T)) + 1)/p + delta(T) ],  p=1,
delta(T) = pi/T + 1/(8 T^2).

All ingredients unnormalized; the final W endpoints divide once by the norm.
Labels: this is an interval fixed-wave score for d22_cand2_odd_L0.4, cutoff
T=512, with the old lower endpoint retained (a = 0.0151928770501 from the
saved D22 score). No reselection; coefficients exactly as frozen.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, '/Users/peterviviani/golden-horizon-principle/experiments/riemann_dojo')
from dojo_court import (  # noqa: E402
    PP_ALL, compact_integral, derivative_evidence, norm2, pole_term, shift_inner,
)
from flint import arb, ctx  # noqa: E402

ctx.prec = 256
OUT = Path('/Users/peterviviani/golden-horizon-principle/experiments/fable_d25_mass_tail')
CAND = Path('/Users/peterviviani/golden-horizon-principle/experiments/fable_d22_test2/d22_cand2_odd_L0.4.json')

cand_text = CAND.read_text()
import hashlib  # noqa: E402
print(f"candidate sha256: {hashlib.sha256(cand_text.encode()).hexdigest()}", flush=True)
cand = json.loads(cand_text)
L = arb(2) / 5
T = 512
modes = cand['modes']
coeffs = [str(c) for c in cand['minimizer_frozen_40dig']]
b = [arb(0)] * (max(modes) + 1)
for d, c in zip(modes, coeffs):
    b[d] = arb(c) * ((2 * d + 1) / (2 * L)).sqrt()

t0 = time.time()
nrm = norm2(b, L)
print(f"norm2: {str(nrm)[:24]}  ({time.time()-t0:.0f}s)", flush=True)

# Visible arithmetic: only n=2 at L=0.4
visible = [(u, w) for u, w in PP_ALL if u < 2 * L]
shifts = [shift_inner(b, u, L) for u, w in visible]
prime_sum = sum((w * s for (u, w), s in zip(visible, shifts)), arb(0))
pol = pole_term(b, 1, L)
print(f"prime_sum: {str(prime_sum)[:24]}  pole: {str(pol)[:24]}  ({time.time()-t0:.0f}s)", flush=True)

# Compact archimedean integral and compact mass at T=512
arch_compact, mass = compact_integral(b, 1, T, L, K=64)
print(f"arch_compact: {str(arch_compact)[:30]}  mass: {str(mass)[:24]}  ({time.time()-t0:.0f}s)", flush=True)

# b and D: endpoint jump and derivative norm (upper bounds from derivative evidence)
ev = derivative_evidence(b, L)
b_jump = ev[0]['boundary']           # |f(-L)| + |f(L)|
D_norm = ev[1]['norm2']              # ||f'||^2
print(f"b_jump: {str(b_jump)[:24]}  D: {str(D_norm)[:24]}  ({time.time()-t0:.0f}s)", flush=True)

# Tail mass bounds: M(T) in [nrm - mass.upper(), nrm - mass.lower()]
M_upper = max(arb(0), nrm - mass.lower())
M_lower = max(arb(0), nrm - mass.upper())
C_T = (b_jump / arb.pi().sqrt() + (D_norm / arb(T)).sqrt()) ** 2
M0 = min(M_upper, C_T / arb(T))
delta_T = arb.pi() / arb(T) + 1 / (8 * arb(T) ** 2)
log_ratio = (C_T / (M0 * arb(T))).log()
A_tail_upper = M0 * ((arb(T) / (2 * arb.pi())).log() + (log_ratio + 1) + delta_T)
print(f"M_upper: {str(M_upper)[:24]}  M_lower: {str(M_lower)[:24]}  C_T: {str(C_T)[:24]}  M0: {str(M0)[:24]}", flush=True)
print(f"A_tail_upper: {str(A_tail_upper)[:30]}  ({time.time()-t0:.0f}s)", flush=True)

# Lower endpoint of the archimedean tail (retained old style): a(T) * mass_lower
a_T = arb(  # a(T) = Re psi(1/4 + iT/2) - log pi
    (arb(1) / 4 + arb(0, 1) * arb(T) / 2) )
from dojo_court import a_func  # noqa: E402
aT = a_func(arb(T))
A_tail_lower = aT * M_lower

# Unnormalized W endpoints, then divide once by the norm
W_lower = (arch_compact.lower() + A_tail_lower.lower() + pol.lower() - prime_sum.upper()) / nrm
W_upper = (arch_compact.upper() + A_tail_upper.upper() + pol.upper() - prime_sum.lower()) / nrm
a_saved = arb('0.0151928770501')

result = {
    'wave': 'd22_cand2_odd_L0.4',
    'candidate_sha256': hashlib.sha256(cand_text.encode()).hexdigest(),
    'L': '0.4', 'parity': 'odd', 'T_score': T, 'T_R_note': 'T_R=160 (Stage A instrument)',
    'norm2': str(nrm),
    'prime_visible_sum_unnorm': str(prime_sum),
    'pole_unnorm': str(pol),
    'arch_compact_unnorm': str(arch_compact),
    'compact_mass_unnorm': str(mass),
    'mass_tail_upper_unnorm': str(M_upper),
    'mass_tail_lower_unnorm': str(M_lower),
    'b_jump': str(b_jump),
    'D_norm': str(D_norm),
    'C_T': str(C_T),
    'M0': str(M0),
    'delta_T': str(delta_T),
    'A_tail_upper_unnorm': str(A_tail_upper),
    'A_tail_lower_unnorm': str(A_tail_lower),
    'W_lower_T512': str(W_lower),
    'W_upper_T512_massconditioned': str(W_upper),
    'ratio_upper_over_lower': str(W_upper / W_lower),
    'saved_lower_endpoint_a': str(a_saved),
    'ratio_upper_over_saved_lower': str(W_upper / a_saved),
    'labels': 'interval fixed-wave score, T=512, mass-conditioned upper; lower kept from the old route; court bounds unaudited (D24-style audit pending)',
    'elapsed_s': round(time.time() - t0, 1),
}
(OUT / 'stage-c-result.json').write_text(json.dumps(result, indent=1) + '\n')
print(json.dumps({k: result[k] for k in ('W_lower_T512', 'W_upper_T512_massconditioned',
                                         'ratio_upper_over_lower', 'ratio_upper_over_saved_lower')}, indent=1))
print(f"[done] {result['elapsed_s']}s")
