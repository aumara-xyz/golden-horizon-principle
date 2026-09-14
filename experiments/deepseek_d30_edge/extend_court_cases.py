#!/usr/bin/env python3
"""D30 Task 3 support: add the three new cases to court_score.py's CASES table.

The frozen court files (court_frozen_dojo.py, court_frozen_score.py) are untouched.
Only the driver's case table grows: each new entry takes its Schur constants from the
Task 1 certified floor JSON (via floor_ell.py) and its default candidate from
construct_d30.py's output. Idempotent: refuses to run if the cases are already there.
"""
import json
from pathlib import Path
from floor_ell import floor_from_cert, interval

HERE = Path(__file__).parent
COURT = HERE.parent / 'deepseek_d28_construction_loop' / 'court_score.py'

CASES = [
    ('l05-even', '0.5', 'even', 'certs/d30_cert_visible_even_L0.5_T160_N160.json', 'candidate_l05_even_d30.json'),
    ('l06-odd',  '0.6', 'odd',  'certs/d30_cert_visible_odd_L0.6_T160_N160.json',  'candidate_l06_odd_d30.json'),
    ('l06-even', '0.6', 'even', 'certs/d30_cert_visible_even_L0.6_T160_N160.json', 'candidate_l06_even_d30.json'),
]

def main():
    s = COURT.read_text()
    for name, L, par, cert, cand in CASES:
        if f"'{name}':" in s:
            print(f"{name}: already present, skip")
            continue
        r = floor_from_cert(HERE / cert)
        d = json.loads((HERE / cert).read_text())
        eps_D = interval(d['eps_D'])[1]
        eps_C = interval(d['eps_C'])[1]
        eps_p = interval(d['eps_p'])[1]
        norm_pN = interval(d['norm_pN'])[1]
        beta = interval(d['beta_star'])[1]
        entry = (
            f"    '{name}': {{\n"
            f"        'L': arb({L}), 'parity': {1 if par == 'odd' else 0},\n"
            f"        'lam0': '{r['lam0_lower']}', 'eps_D': '{eps_D}', 'eps_C': '{eps_C}',\n"
            f"        'eps_p': '{eps_p}', 'norm_pN': '{norm_pN}', 'beta': '{beta}',\n"
            f"        'default_cand': '{HERE.parent / 'deepseek_d28_construction_loop' / cand}',\n"
            f"    }},\n"
        )
        s = s.replace("    'l04-even': {", entry + "    'l04-even': {", 1)
        print(f"{name}: added (lam0={r['lam0_lower'][:20]}, ell={r['ell'][:20]})")
    COURT.write_text(s)

if __name__ == '__main__':
    main()
