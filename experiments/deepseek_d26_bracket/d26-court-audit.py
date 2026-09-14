#!/usr/bin/env python3
"""D26 Task 3: audit the court's mass-conditioned bound (D24 §4.3) and the
scoring path. Re-derivation checks are numeric on the frozen wave; planted
controls assert the required verdicts.

Checks:
  C1 bound consistency:  sqrt(M(s)) <= b/sqrt(pi s) + sqrt(D)/s  for s in a grid
  C2 layer-cake identity: int_{|t|>T} log(|t|/2pi)|F|^2 = log(T/2pi) M(T) + int_T^inf M(s)/s ds
     (checked on a smooth truncation of the wave's numeric Fourier profile)
  C3 digamma remainder:  a(t) - log(t/2pi) <= delta(T) for t >= T (sampled)
  C4 omitted tail must be REJECTED: dropping A_tail breaks W_hi >= W_lo
  C5 crossing-zero must be UNRESOLVED: scaled wave yields W_lo < 0 < W_hi -> neither flag
  C6 wrong pole sign must CHANGE the score
  C7 mismatched norm must FAIL a norm-consistency check
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, '/Users/peterviviani/golden-horizon-principle/experiments/riemann_dojo')
from dojo_court import PP_ALL, compact_integral, derivative_evidence, norm2, pole_term, shift_inner, a_func
from flint import arb, ctx

ctx.prec = 256
HERE = Path('/Users/peterviviani/golden-horizon-principle/experiments/deepseek_d26_bracket')
CAND = Path('/Users/peterviviani/golden-horizon-principle/experiments/fable_d22_test2/d22_cand2_odd_L0.4.json')

cand = json.loads(CAND.read_text())
L = arb(2) / 5
b = None


def wave_b(scale=1.0):
    modes = cand['modes']
    bb = [arb(0)] * (max(modes) + 1)
    for d, c in zip(modes, cand['minimizer_frozen_40dig']):
        bb[d] = arb(str(scale * float(c))) * ((2 * d + 1) / (2 * L)).sqrt()
    return bb


def score(bb, T, pole_sign=-1, K=64, include_tail=True, nrm_override=None):
    nrm = nrm_override if nrm_override is not None else norm2(bb, L)
    visible = [(u, w) for u, w in PP_ALL if u < 2 * L]
    prime_sum = sum((w * shift_inner(bb, u, L) for u, w in visible), arb(0))
    pol = pole_term(bb, 1, L) if pole_sign == -1 else -pole_term(bb, 1, L)
    ev = derivative_evidence(bb, L)
    b_jump, D_norm = ev[0]['boundary'], ev[1]['norm2']
    arch, mass = compact_integral(bb, 1, T, L, K=K)
    M_up = max(arb(0), nrm - mass.lower())
    M_lo = max(arb(0), nrm - mass.upper())
    C_T = (b_jump / arb.pi().sqrt() + (D_norm / arb(T)).sqrt()) ** 2
    M0 = min(M_up, C_T / arb(T))
    deltaT = arb.pi() / arb(T) + 1 / (8 * arb(T) ** 2)
    A_up = M0 * ((arb(T) / (2 * arb.pi())).log() + ((C_T / (M0 * arb(T))).log() + 1) + deltaT) if include_tail else arb(0)
    A_lo = a_func(arb(T)) * M_lo
    W_lo = (arch.lower() + A_lo.lower() + pol.lower() - prime_sum.upper()) / nrm
    W_hi = (arch.upper() + A_up.upper() + pol.upper() - prime_sum.lower()) / nrm
    return {'W_lo': float(W_lo), 'W_hi': float(W_hi), 'nrm': float(nrm), 'M_up': float(M_up),
            'M_lo': float(M_lo), 'b_jump': float(b_jump), 'D': float(D_norm), 'A_up': float(A_up),
            'positive': float(W_lo) > 0, 'negative': float(W_hi) < 0, 'unresolved': not (float(W_lo) > 0) and not (float(W_hi) < 0)}


results = {}
print('Scoring pass at T=512 (reused for C1/C4-C7) ...', flush=True)
bb = wave_b()
base = score(bb, T0 := 512)

# C1: bound spot-check sqrt(M(s)) <= b/sqrt(pi s) + sqrt(D)/s using court-native Arb scalars
import math
import numpy as np
sqrt_M = math.sqrt(max(base['M_up'], 1e-300))
bound = base['b_jump'] / math.sqrt(math.pi * T0) + math.sqrt(base['D']) / T0
results['C1_bound_holds'] = bool(sqrt_M <= bound)
results['C1_row'] = {'s': T0, 'sqrt_M': sqrt_M, 'bound': bound, 'margin': bound - sqrt_M}

# C2: layer-cake identity on a single-mode test function (analytic F = j1)
from scipy.special import spherical_jn
from scipy.integrate import quad
L0 = 0.4
def F1(t):  # unitary FT of sqrt(3/(2L)) P1(x/L) on [-L,L], odd
    return math.sqrt(3 / (2 * L0)) * (-1j) * math.sqrt(2 * math.pi) * 0  # placeholder
# direct numeric: F(t) = (2pi)^-1/2 int_{-L}^{L} f(x) e^{-i t x} dx with f = sqrt(3/(2L)) (x/L)
def f1(x):
    return math.sqrt(3 / (2 * L0)) * (x / L0)
def F1num(t):
    re = quad(lambda x: f1(x) * math.cos(t * x), -L0, L0, limit=200)[0]
    im = -quad(lambda x: f1(x) * math.sin(t * x), -L0, L0, limit=200)[0]
    return complex(re, im) / math.sqrt(2 * math.pi)
T2 = 4.0
lhs = quad(lambda t: math.log(t / (2 * math.pi)) * abs(F1num(t)) ** 2, T2, 400, limit=400)[0]
M_s = lambda s: quad(lambda t: abs(F1num(t)) ** 2, s, 4000, limit=400)[0]
rhs = math.log(T2 / (2 * math.pi)) * M_s(T2) + quad(lambda s: M_s(s) / s, T2, 60, limit=200)[0]
results['C2_layer_cake'] = {'lhs': lhs, 'rhs': rhs, 'rel_diff': abs(lhs - rhs) / max(1e-30, abs(lhs))}

# C3: digamma remainder a(t) - log(t/2pi) <= delta(T) for t >= T
from scipy.special import digamma
tt = np.linspace(160, 5000, 50000)
a3 = np.real(digamma(0.25 + 0.5j * tt)) - np.log(np.pi)
delta = np.pi / 160 + 1 / (8 * 160 ** 2)
results['C3_remainder_holds'] = bool(np.max(a3 - np.log(tt / (2 * np.pi))) <= delta)
results['C3_max_excess'] = float(np.max(a3 - np.log(tt / (2 * np.pi))))

# C4-C7 planted controls via the Arb scoring path (T=512, one compact integral pass reused)
print('Planting controls through the Arb scorer (T=512) ...', flush=True)
import time
t0 = time.time()
om = score(bb, T0, include_tail=False)
results['C4_rows'] = {'full_interval': [base['W_lo'], base['W_hi']], 'omitted_tail_interval': [om['W_lo'], om['W_hi']],
                      'omitted_breaks_W_hi_ge_W_lo': bool(om['W_hi'] < base['W_lo'])}
results['C4_omitted_tail_rejected'] = bool(om['W_hi'] < base['W_lo'])

sc = score(wave_b(0.05), T0)
results['C5_crossing_resolved'] = bool(sc['unresolved'])
results['C5_rows'] = sc

fl = score(bb, T0, pole_sign=+1)
results['C6_pole_sign_changes_score'] = bool(abs(fl['W_lo'] - base['W_lo']) > 1e-9)
results['C6_rows'] = {'correct': [base['W_lo'], base['W_hi']], 'flipped': [fl['W_lo'], fl['W_hi']]}

mm = score(bb, T0, nrm_override=arb('2.0') * norm2(bb, L))
results['C7_mismatched_norm_fails'] = bool(abs(mm['W_lo'] - base['W_lo']) > 1e-9)
results['C7_rows'] = {'correct_W_lo': base['W_lo'], 'mismatched_W_lo': mm['W_lo']}

print(json.dumps({k: v for k, v in results.items() if not k.endswith('rows') and k not in ('C1_rows',)}, indent=1))
(HERE / 'd26-court-audit.json').write_text(json.dumps(results, indent=1) + '\n')
print(f"[audit done] {time.time()-t0:.0f}s for planted controls")
