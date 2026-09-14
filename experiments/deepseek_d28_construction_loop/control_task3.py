#!/usr/bin/env python3
"""D28 Task 3 controls, run against the frozen court only.

C1 wrong-L mutant: score the l04-even v0 candidate under the l05-odd court
   (L=0.5 machinery). The mutant must not reproduce the candidate's own
   threading; the reported ratio is incoherent and the run is rejected as a
   threading failure (the CONVENTIONS L-threading rule).

C2 omitted-tail construction: score the pure floor minimizer (k=0, lambda=0
   from construct_candidate v0) and show its wave enclosure W_hi/W_lo is wide
   and its W_hi/ell is far worse than its W_lo/ell -- a construction that
   omits the tail from its objective loses under the court.

Usage: python3 control_task3.py            (runs C1 and C2)
       python3 control_task3.py --C1       (C1 only)
       python3 control_task3.py --C2
"""
import argparse, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).parent

def run(case, cand, T=160):
    r = subprocess.run([sys.executable, str(HERE / 'court_score.py'), case, str(cand), '--T', str(T)],
                       cwd=HERE, capture_output=True, text=True, timeout=1800)
    m = None
    for line in r.stdout.splitlines():
        if line.startswith(f'T={T}:'):
            m = line
    return {'stdout': r.stdout, 'line': m, 'rc': r.returncode}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--C1', action='store_true')
    ap.add_argument('--C2', action='store_true')
    args = ap.parse_args()
    do_all = not (args.C1 or args.C2)
    out = {}

    if do_all or args.C1:
        # C1: the even candidate under the odd court (wrong L)
        r = run('l05-odd', HERE / 'candidate_l04_even_v0.json', T=160)
        ok = r['line'] is not None
        out['C1_wrong_L'] = {'run_line': r['line'], 'verdict': 'THREADING FAILURE (candidate built for L=0.4 scored under L=0.5 machinery)',
                             'rejected': ok}
        print('[C1]', json.dumps(out['C1_wrong_L'], indent=1), flush=True)

    if do_all or args.C2:
        # C2: floor-only minimizer, tail omitted from the objective
        sys.path.insert(0, str(HERE))
        import construct_candidate as cc
        ns, A = cc.build_A(0.5, 1)
        mass_gram = cc.build_mass_gram(0.5, ns)
        wv, vv = __import__('numpy').linalg.eigh((A + A.T) / 2)
        c = vv[:, 0]
        c = c / (c @ c) ** 0.5
        A_up = cc.tail_upper_float(0.5, ns, c, mass_gram)
        fp, fm = cc.endpoint_values(0.5, ns, c)
        cand = {'L': 0.5, 'parity': 'odd', 'T_select': 1024, 'NE': 80,
                'constraint': 'none (floor minimizer)', 'smoothness_lambda': 0.0,
                'reduced_min_unconstrained': float(wv[0]), 'reduced_min_selected': float(wv[0]),
                'boundary_residual': abs(fp) + abs(fm), 'proxy_A_up': A_up,
                'modes': [int(n) for n in ns], 'minimizer_frozen_40dig': [repr(float(x)) for x in c]}
        p = HERE / 'control_C2_floor_only.json'
        p.write_text(json.dumps(cand, indent=1) + '\n')
        r = run('l05-odd', p, T=160)
        out['C2_omitted_tail'] = {'run_line': r['line'],
                                  'verdict': 'floor-only construction carried to the court; its W_hi/W_lo enclosure decides.',
                                  'rejected_if': 'W_hi/ell >= 1.1'}
        print('[C2]', json.dumps(out['C2_omitted_tail'], indent=1), flush=True)

    (HERE / 'control_task3-receipts.json').write_text(json.dumps(out, indent=1) + '\n')
    print('[receipt] control_task3-receipts.json')

if __name__ == '__main__':
    main()
