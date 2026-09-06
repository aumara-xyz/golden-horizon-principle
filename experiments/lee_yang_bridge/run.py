"""Exact finite partition polynomials, numerical roots only where indicated."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json
import numpy as np


def polynomial(n,q):
    edges=[(0,1)] if n==2 else [(j,(j+1)%n) for j in range(n)]
    c=[F(0) for _ in range(n+1)]
    for spins in product((0,1),repeat=n):
        disagreements=sum(spins[a]!=spins[b] for a,b in edges)
        c[sum(spins)]+=q**disagreements
    return c


def report(c):
    roots=np.roots([float(x) for x in c[::-1]])
    residual=max(abs(sum(float(a)*z**j for j,a in enumerate(c))) for z in roots)
    return dict(coefficients=[str(x) for x in c],palindromic=c==c[::-1],
                positive_coefficients=all(x>0 for x in c),
                roots=[[float(z.real),float(z.imag)] for z in roots],
                max_radial_deviation=float(max(abs(abs(z)-1) for z in roots)),
                max_polynomial_residual=float(residual))


def run():
    rows=[]
    for q in (F(2),F(1,2)):
        for n in (2,4):
            c=polynomial(n,q)
            row=dict(model='ising',n=n,q=str(q),**report(c))
            if n==2:
                assert c==[F(1),2*q,F(1)]
            else:
                assert c==[F(1),4*q*q,4*q*q+2*q**4,4*q*q,F(1)]
            rows.append(row)
    for n in (2,4):
        c=polynomial(n,F(1))
        from math import comb
        assert c==[F(comb(n,j)) for j in range(n+1)]
        rows.append(dict(model='independent',n=n,coefficients=[str(x) for x in c],
                         exact_roots='-1 with multiplicity '+str(n)))
    for a in (3,1,2):
        rows.append(dict(model='ternary',a=a,discriminant=a*a-4,
                         exact_classification='off circle' if a>2 else 'on circle',
                         **(report([F(1),F(a),F(1)]) if a!=2 else
                            dict(coefficients=['1','2','1'],exact_roots='-1 twice'))))
    Path(__file__).with_name('results.json').write_text(json.dumps(rows,indent=2)+'\n')
    for row in rows:
        print(json.dumps(row))


if __name__=='__main__':
    run()
