#!/usr/bin/env python3
"""D30 floor extraction: cert JSON -> (lam0 lower endpoint, Schur ell, constants).

Per D29's note the certified floor's LOWER endpoint is used (X - R), not the printed
center; the Schur tail constants are rounded UP (upper endpoints), matching the
D26/D27 convention. Nothing here is the court: this only reads cert JSONs and applies
the published 2x2 Schur formula ell = smaller root of (lam0 - mu)(d - mu) = c^2.
"""
import json, re
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 80

def interval(s):
    """'[X +/- R]' -> (lower, upper) Decimals; a plain number -> (v, v)."""
    s = str(s).strip().strip('[]')
    if '+/-' in s:
        x, r = [t.strip() for t in s.split('+/-')]
        return Decimal(x) - Decimal(r), Decimal(x) + Decimal(r)
    v = Decimal(s)
    return v, v

def schur(lam0, eps_D, eps_C, eps_p, norm_pN, beta):
    d = beta - eps_D - 2 * eps_p * eps_p
    coupling = eps_C + 2 * norm_pN * eps_p
    c2 = coupling * coupling
    s = lam0 + d
    disc = (s * s - 4 * (lam0 * d - c2)).sqrt()
    return (s - disc) / 2

def floor_from_cert(path):
    d = json.loads(Path(path).read_text())
    lam0_lo, lam0_hi = interval(d['lambda0_certified'])
    eps_D = interval(d['eps_D'])[1]
    eps_C = interval(d['eps_C'])[1]
    eps_p = interval(d['eps_p'])[1]
    norm_pN = interval(d['norm_pN'])[1]
    beta = interval(d['beta_star'])[1]
    ell = schur(lam0_lo, eps_D, eps_C, eps_p, norm_pN, beta)
    return {
        'cert': str(path), 'L': d.get('L'), 'T': d.get('T'), 'parity': d.get('parity'),
        'lam0_lower': str(lam0_lo), 'lam0_upper': str(lam0_hi), 'radius': str(lam0_hi - lam0_lo),
        'eps_D': str(eps_D), 'eps_C': str(eps_C), 'eps_p': str(eps_p),
        'norm_pN': str(norm_pN), 'beta': str(beta),
        'ell': str(ell), 'ell_float': float(ell),
        'lam0_lower_float': float(lam0_lo),
        'schur_shift': str(lam0_lo - ell),
    }

if __name__ == '__main__':
    import sys
    for p in sys.argv[1:]:
        r = floor_from_cert(p)
        print(json.dumps({k: r[k] for k in ('cert', 'L', 'T', 'parity', 'lam0_lower', 'ell', 'ell_float', 'schur_shift')}, indent=1))
