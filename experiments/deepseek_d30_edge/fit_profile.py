#!/usr/bin/env python3
"""D30 Task 2: refit D23's profile on the certified visible-form floors.

Models on log(ell) over the four T=160 points per parity (L = 0.4, 0.5, 0.6, 0.7):
  M1: log ell = A - B*L          (linear in L)
  M2: log ell = A - C*exp(2L)    (linear in exp(2L))
Reports fitted parameters, measured per-step slopes (d log ell / dL), model slopes,
relative RMS slope error and max |log residual| -- the D23 format, so the comparison
is direct. Four points, two parameters: a model comparison, not an asymptotic law.
"""
import json, math
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent

def slopes(Ls, logells):
    return [ (logells[i] - logells[i-1]) / (Ls[i] - Ls[i-1]) for i in range(1, len(Ls)) ]

def fit(parity, rows):
    Ls = np.array([float(r['L']) for r in rows])
    y = np.array([math.log(r['ell_float']) for r in rows])
    out = {}
    # M1: y = A - B*L
    X1 = np.vstack([np.ones_like(Ls), -Ls]).T
    (A1, B1), *_ = np.linalg.lstsq(X1, y, rcond=None)
    res1 = y - X1 @ np.array([A1, B1])
    # M2: y = A - C*exp(2L)
    E = np.exp(2 * Ls)
    X2 = np.vstack([np.ones_like(E), -E]).T
    (A2, C2), *_ = np.linalg.lstsq(X2, y, rcond=None)
    res2 = y - X2 @ np.array([A2, C2])
    meas = slopes(Ls, list(y))
    mod1 = slopes(Ls, list(X1 @ np.array([A1, B1])))
    mod2 = slopes(Ls, list(X2 @ np.array([A2, C2])))
    rms1 = float(np.sqrt(np.mean(((np.array(mod1) - meas) / np.array(meas)) ** 2)))
    rms2 = float(np.sqrt(np.mean(((np.array(mod2) - meas) / np.array(meas)) ** 2)))
    return {'parity': parity, 'L': list(Ls), 'measured_slopes': [round(s, 3) for s in meas],
            'M1': {'A': A1, 'B': B1, 'model_slopes': [round(s, 3) for s in mod1],
                   'rel_rms_slope_err': rms1, 'max_abs_log_resid': float(np.max(np.abs(res1)))},
            'M2': {'A': A2, 'C': C2, 'model_slopes': [round(s, 3) for s in mod2],
                   'rel_rms_slope_err': rms2, 'max_abs_log_resid': float(np.max(np.abs(res2)))},
            'prediction_held': rms2 < 0.10}

def main():
    floors = json.loads((HERE / 'floors.json').read_text())
    t160 = [r for r in floors if r['kind'] == 'new' or r['kind'] == 'cited']
    res = []
    for par in ('even', 'odd'):
        rows = sorted([r for r in t160 if r['parity'] == par and r['T'] == 160], key=lambda r: float(r['L']))
        res.append(fit(par, rows))
    (HERE / 'profile_fits.json').write_text(json.dumps(res, indent=1) + '\n')
    for r in res:
        print(f"=== {r['parity']} (slopes measured {r['measured_slopes']}) ===")
        print(f"  M1 linear : A={r['M1']['A']:.3f} B={r['M1']['B']:.3f} slopes={r['M1']['model_slopes']} relRMS={r['M1']['rel_rms_slope_err']:.3f}")
        print(f"  M2 exp(2L): A={r['M2']['A']:.3f} C={r['M2']['C']:.3f} slopes={r['M2']['model_slopes']} relRMS={r['M2']['rel_rms_slope_err']:.3f}")
        print(f"  prediction (M2 < 10%): {'HELD' if r['prediction_held'] else 'FAILED -> D23 law dead'}")

if __name__ == '__main__':
    main()
