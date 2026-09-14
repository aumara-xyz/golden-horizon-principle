#!/usr/bin/env python3
"""D30 Task 3: construct candidates for the three new cases with the D28 winning
rule FROZEN (construct_candidate.winner-iter08.py, sha 989be135...).

No rule change, no reselection: this driver imports the winner module and calls its
construct()/save_candidate() with the new case parameters only. The ell values come
from the Task 1 certified floors (floors.json). No T escalation: candidates are
built at the module's T_BUILD=1024 grid, exactly as in D28.
"""
import importlib.util, json
from pathlib import Path

HERE = Path(__file__).parent
WINNER = HERE.parent / 'deepseek_d28_construction_loop' / 'construct_candidate.winner-iter08.py'

CASES = {
    'l05-even': {'L': 0.5, 'parity': 0},
    'l06-odd':  {'L': 0.6, 'parity': 1},
    'l06-even': {'L': 0.6, 'parity': 0},
}

def main():
    spec = importlib.util.spec_from_file_location('winner_rule', WINNER)
    rule = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rule)
    floors = json.loads((HERE / 'floors.json').read_text())
    ell_for = {}
    for r in floors:
        if r['T'] == 160:
            ell_for[(float(r['L']), r['parity'])] = r['ell_float']
    for name, c in CASES.items():
        ell = ell_for[(c['L'], 'odd' if c['parity'] == 1 else 'even')]
        print(f"=== {name}: L={c['L']} parity={'odd' if c['parity']==1 else 'even'} ell={ell:.15g} ===", flush=True)
        ns, A, results = rule.construct(name, c['L'], c['parity'], ell)
        best = results[0]
        p = rule.save_candidate(HERE, name, c['L'], c['parity'], ns, A, best, ell,
                                f'candidate_{name.replace("-", "_")}_d30.json')
        print(f"[saved] {p.name}  proxy_ratio={best['proxy_ratio']:.6f}  "
              f"(k_max={best['k_max']}, lam={best['lam']:.0e}, mu_D={best['mu_D']:.0e}, "
              f"mu_e={best['mu_e']:.0e}, mu_m={best['mu_m']:.0e})", flush=True)

if __name__ == '__main__':
    main()
