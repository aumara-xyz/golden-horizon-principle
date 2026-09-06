"""Replay unchanged D7 as INPUT, adding fixed-beta arithmetic controls.

This does not independently certify the D7 all-function tail. New analysis lives
in schur.py. All generated files remain in the D10 directory.
"""
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys
import time
from flint import arb, arb_mat

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'weil_hidden_modes' / 'opus_d7_rebuild.py'


def main():
    parity = sys.argv[1]
    assert parity in ('even', 'odd')
    os.chdir(HERE)
    sys.argv = [str(SOURCE), parity, '80', '1']
    d = runpy.run_path(str(SOURCE), run_name='__main__')
    n = d['NE']
    ns, fv, wv, pp = d['ns'], d['Fv'], d['Wv'], d['PP']
    h = [[d['M'][i][j] + (d['beta'] if i == j else 0)
          for j in range(n)] for i in range(n)]
    # Controls are assembled and exported first. They keep exactly the same
    # beta so they are variations of the SAME finite lower-envelope functional.
    models = {}
    fmat = arb_mat([fv[q] for q in ns])
    oldweights = [w for _, w in pp]
    for name, weights in [('arch_only', [arb(0)] * 3),
                          ('weight_reverse', list(reversed(oldweights)))]:
        start = time.time()
        diffs = [oldweights[k] - weights[k] for k in range(3)]
        delta = []
        for panel in range(d['T']):
            for x, _ in d['nodes']:
                t = arb(panel) + d['h'] + d['h'] * x
                delta.append(sum((diffs[k] * (pp[k][0] * t).cos()
                                  for k in range(3)), arb(0)))
        assert len(delta) == len(wv)
        gmat = arb_mat([[fv[q][k] * wv[k] * delta[k]
                        for k in range(len(wv))] for q in ns])
        add = 2 * (gmat * fmat.transpose())
        # |sum delta_w cos(a z)| <= sum |delta_w| cosh(a Im z)
        # on every unit-panel ellipse. The inherited Fourier ellipse bounds
        # and Chebyshev/Gauss error are exactly those proved in D7.
        bound = sum((abs(diffs[k]) * (pp[k][0] * d['b_ax']).cosh()
                     for k in range(3)), arb(0))
        rows = []
        for i, m in enumerate(ns):
            row = []
            for j, q in enumerate(ns):
                err = 2 * d['Cq'] * d['T'] * bound * d['MFc'][m] * d['MFc'][q]
                row.append(h[i][j] + add[i, j] + arb(0, err.abs_upper()))
            rows.append(row)
        models[name] = rows
        print('control built', parity, name, time.time() - start, flush=True)
    models['authentic'] = h
    out = dict(parity=parity, N=n, beta=d['beta'].str(90),
               p=[v.str(90) for v in d['p']],
               models={name: [[v.str(90) for v in row] for row in rows]
                       for name, rows in models.items()},
               source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               scope='Principal finite blocks of R_120, NOT exact W matrices',
               control_error='2*Cq*T*M_delta*MFc[i]*MFc[j], all Arb',
               precision_bits=d['ctx'].prec)
    (HERE / ('input_' + parity + '.json')).write_text(json.dumps(out, indent=1) + '\n')
    print('INPUT READY', parity, flush=True)


if __name__ == '__main__':
    main()
