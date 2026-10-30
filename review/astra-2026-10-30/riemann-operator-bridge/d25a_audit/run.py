#!/usr/bin/env python3
"""Independent bounded reproduction of stated D25A equations."""
import hashlib,json,math
from functools import lru_cache
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import legval,leggauss
from scipy.linalg import eigh
from scipy.optimize import brentq

HERE=Path(__file__).resolve().parent

def mode(c,parity,N):
    X=np.zeros((N+1,N+1))
    for n in range(N):
        X[n,n+1]=X[n+1,n]=(n+1)/math.sqrt((2*n+1)*(2*n+3))
    H=np.diag(np.arange(N)*(np.arange(N)+1))+c*c*(X@X)[:N,:N]
    ix=np.arange(parity,N,2)
    eig,v=eigh(H[np.ix_(ix,ix)],subset_by_index=[0,0])
    out=np.zeros(N);out[ix]=v[:,0]
    if out[parity]<0:out=-out
    return float(eig[0]),out

@lru_cache(None)
def gauss(N):return leggauss(N+8)

def corr(v,L,a):
    a=abs(a)
    if a>=2*L:return 0.0
    y,w=gauss(len(v));h=L-a/2
    coeff=v*np.sqrt((2*np.arange(len(v))+1)/(2*L))
    left=legval((h*y-a/2)/L,coeff)
    right=legval((h*y+a/2)/L,coeff)
    return float(h*np.dot(w,left*right))

def root(v,L):
    points=np.linspace(0,1.8*L,181)
    previous=corr(v,L,0)
    for a,b in zip(points[:-1],points[1:]):
        value=corr(v,L,b)
        if previous>0 and value<0:return float(brentq(lambda x:corr(v,L,x),a,b,xtol=5e-15))
        previous=value
    raise ValueError('No positive-to-negative crossing in prescribed bracket')

def powers(limit):
    primes=[]
    for p in range(2,limit+1):
        if all(p%q for q in primes if q*q<=p):primes.append(p)
    out=[]
    for p in primes:
        n=p
        while n<=limit:out.append(n);n*=p
    return sorted(out)

def run_case(L,N,family='quadratic'):
    c=.5*L*(13.1+15.3*(L-.4)) if family=='quadratic' else (.5*.4*13.1)*L/.4
    e0,v0=mode(c,0,N);e1,v1=mode(c,1,N)
    cross=root(v1,L)
    eligible=[n for n in powers(int(math.exp(2*L))) if math.log(n)<2*L]
    rows=[{'n':n,'a':math.log(n),'even':corr(v0,L,math.log(n)),
           'odd':corr(v1,L,math.log(n))} for n in eligible]
    return {'L':float(L),'N':N,'family':family,'c':c,'eigen_even':e0,'eigen_odd':e1,
       'a_star':cross,'visible_prime_powers':rows,
       'even_unit_norm_error':corr(v0,L,0)-1,'odd_unit_norm_error':corr(v1,L,0)-1,
       'outside_support_check':corr(v1,L,2*L)},v0,v1

def main():
    targets=[.4,.7,1.,1.2,2.]
    reported=[.278059,.384966,.418034,.431191,.459784]
    detail=[]
    for L,target in zip(targets,reported):
        byN={};vec={}
        for N in [32,64,96]:
            byN[str(N)],v0,v1=run_case(L,N);vec[N]=(v0,v1)
        byN['reported_rounded_a_star']=target
        byN['delta_a_32_96']=byN['32']['a_star']-byN['96']['a_star']
        byN['delta_a_64_96']=byN['64']['a_star']-byN['96']['a_star']
        byN['coefficient_delta_32_96']=[float(np.linalg.norm(np.pad(vec[32][p],(0,64))-vec[96][p])) for p in [0,1]]
        detail.append(byN)
    sweep=[run_case(float(L),64)[0] for L in np.linspace(.4,2.,33)]
    control=[run_case(L,96,'linear')[0] for L in targets]
    ceiling=2/math.sqrt(15.3)
    out={'status':'RAN; numerical, not interval-certified',
      'plan_sha256':hashlib.sha256((HERE/'PLAN.md').read_bytes()).hexdigest(),
      'source_script_available':False,'definition':'c(L)=L*(13.1+15.3*(L-.4))/2',
      'hermite_asymptotic_crossover':ceiling,'log2':math.log(2),
      'reported_points':detail,'sweep':sweep,'linear_bandwidth_control':control,
      'sweep_max_crossover':max(r['a_star'] for r in sweep),
      'sweep_ceiling_holds':all(r['a_star']<ceiling for r in sweep),
      'visible_odd_signs_negative_in_sweep':all(x['odd']<0 for r in sweep for x in r['visible_prime_powers']),
      'claims_not_established':['uniform L ceiling','uniqueness of correlation crossing for exact PSWF',
        'exact infinite-dimensional PSWF error bound','full Weil excitation-cost inequality','RH']}
    (HERE/'results.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'ceiling':ceiling,'points':[(d['96']['L'],d['96']['a_star'],d['delta_a_32_96']) for d in detail],
       'L.7':detail[1]['96']['visible_prime_powers'],'sweep_max':out['sweep_max_crossover'],
       'negative_visible':out['visible_odd_signs_negative_in_sweep'],
       'linear_control':[(d['L'],d['a_star']) for d in control]},indent=2))

if __name__=='__main__':main()
