#!/usr/bin/env python3
"""D30 Task 1 assembly: the certified floor table (visible-form, D24-repaired).

Existing floors are CITED (not recomputed): their cert JSONs live in the D26/D27
directories. New floors come from certs/ (this round). Every row records the cert
file, its sha256, the lambda0 lower endpoint, the Schur ell and the shift.

Output: floors.json (+ printed table).
"""
import hashlib, json
from pathlib import Path
from floor_ell import floor_from_cert

HERE = Path(__file__).parent
GHP = HERE.parent.parent

ROWS = [
    # (L, parity, T, N, kind, cert path)
    ('0.4', 'odd',  160, 160, 'cited', GHP / 'experiments/deepseek_d26_bracket/d26_cert_visible_odd_L0.4_T160_N160.json'),
    ('0.4', 'even', 160, 160, 'cited', GHP / 'experiments/deepseek_d27_two_brackets/d27_cert_visible_evenL04_even_L0.4_T160_N160.json'),
    ('0.5', 'odd',  160, 160, 'cited', GHP / 'experiments/deepseek_d26_bracket/d26_cert_visible_L05_odd_L0.5_T160_N160.json'),
    ('0.5', 'even', 160, 160, 'new', HERE / 'certs/d30_cert_visible_even_L0.5_T160_N160.json'),
    ('0.6', 'odd',  160, 160, 'new', HERE / 'certs/d30_cert_visible_odd_L0.6_T160_N160.json'),
    ('0.6', 'even', 160, 160, 'new', HERE / 'certs/d30_cert_visible_even_L0.6_T160_N160.json'),
    ('0.7', 'odd',  160, 160, 'new', HERE / 'certs/d30_cert_visible_odd_L0.7_T160_N160.json'),
    ('0.7', 'even', 160, 160, 'new', HERE / 'certs/d30_cert_visible_even_L0.7_T160_N160.json'),
    ('0.7', 'odd',  240, 192, 'new', HERE / 'certs/d30_cert_visible_odd_L0.7_T240_N192.json'),
    ('0.7', 'even', 240, 192, 'new', HERE / 'certs/d30_cert_visible_even_L0.7_T240_N192.json'),
]

# D22 void counterparts (invisible shifts kept), for the 0-25% prediction check
D22 = {
    ('0.4', 'odd'): 0.0124019265771, ('0.4', 'even'): 0.000144919164005,
    ('0.5', 'odd'): 0.000142134532495, ('0.5', 'even'): 7.14785349231e-7,
    ('0.6', 'odd'): 4.12866743816e-7, ('0.6', 'even'): 1.10135673044e-9,
    ('0.7', 'odd'): 1.58596369131e-10, ('0.7', 'even'): 2.67167228677e-13,
    ('0.7T240', 'odd'): 2.03304233017e-10, ('0.7T240', 'even'): 3.37581912571e-13,
}

def main():
    out = []
    for L, par, T, N, kind, cert in ROWS:
        r = floor_from_cert(cert)
        if T == 240:
            key = ('0.7T240', par)
        else:
            key = (L, par)
        d22 = D22.get(key)
        r.update({'kind': kind, 'L': L, 'parity': par, 'T': T, 'N': N,
                  'cert_sha256': hashlib.sha256(Path(cert).read_bytes()).hexdigest(),
                  'd22_counterpart': d22,
                  'ratio_vs_d22': (r['lam0_lower_float'] / d22) if d22 else None})
        out.append(r)
    (HERE / 'floors.json').write_text(json.dumps(out, indent=1) + '\n')
    for r in out:
        print(f"L={r['L']} {r['parity']:>4} T={r['T']} {r['kind']:>5} lam0_lo={r['lam0_lower'][:22]:>22} "
              f"ell={r['ell'][:24]:>24} vs D22 x{r['ratio_vs_d22']:.3f}" if r['ratio_vs_d22'] else r)

if __name__ == '__main__':
    main()
