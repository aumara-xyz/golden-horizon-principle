#!/usr/bin/env python3
"""Same-dimension Suzuki mesh comparison; float64 diagnostics only."""
import hashlib,json,math,time
from fractions import Fraction
from pathlib import Path
import numpy as np
from scipy.linalg import ldl
from scipy.special import digamma,polygamma

HERE=Path(__file__).resolve().parent

def prime_powers(limit):
    sieve=bytearray(b'\x01')*(limit+1);sieve[:2]=b'\x00\x00'
    for p in range(2,math.isqrt(limit)+1):
        if sieve[p]:sieve[p*p::p]=b'\x00'*(((limit-p*p)//p)+1)
    out=[]
    for p in range(2,limit+1):
        if sieve[p]:
            n=p
            while n<=limit:out.append((n,p));n*=p
    return sorted(out)

class Psi:
    def __init__(self,horizon=5.5):
        self.horizon=horizon
        pp=prime_powers(math.floor(math.exp(horizon)))
        self.n=np.array([n for n,p in pp],float)
        self.ln=np.log(self.n);self.lp=np.log([p for n,p in pp])
        self.C=float(polygamma(1,.25))
        self.linear=.5*(float(digamma(.25))-math.log(math.pi))
        self.cache={0.:0.};self.max_series_tail=0.
    def arch(self,t):
        t=abs(float(t))
        if t>self.horizon+1e-12:raise ValueError('time outside constructed arithmetic horizon')
        if t in self.cache:return self.cache[t]
        K=max(8,math.ceil(47/(2*t)))
        k=np.arange(K,dtype=float)
        lerch=math.fsum((np.exp(-2*t*k)/(k+.25)**2).tolist())
        tail=math.exp(-2*t*K)/((K+.25)**2*(-math.expm1(-2*t)))
        self.max_series_tail=max(self.max_series_tail,.25*math.exp(-t/2)*tail)
        v=4*(math.expm1(t/2)+math.expm1(-t/2))+self.linear*t+.25*(self.C-math.exp(-t/2)*lerch)
        self.cache[t]=v;return v
    def evaluate(self,times,sigma):
        a=np.asarray(times,dtype=float);flat=np.abs(a).ravel()
        unique,inv=np.unique(flat,return_inverse=True)
        base=np.array([self.arch(t) for t in unique])
        arithmetic=np.maximum(unique[:,None]-self.ln[None,:],0)@(self.lp/self.n**sigma)
        return (base-arithmetic)[inv].reshape(a.shape)

def stats(A):
    A=(A+A.T)/2;ev=np.linalg.eigvalsh(A)
    lu,D,perm=ldl(A,lower=True,hermitian=True)
    piv=np.linalg.eigvalsh(D)
    abs_ev=np.abs(ev)
    return {'lambda_min':float(ev[0]),'lambda_max':float(ev[-1]),
      'negative_eigenvalues_tol1e-10':int(np.sum(ev < -1e-10)),
      'near_zero_eigenvalues_tol1e-10':int(np.sum(abs_ev<=1e-10)),
      'condition2':float(abs_ev.max()/abs_ev.min()),
      'LDLT_min_block_eigenvalue':float(piv.min()),
      'LDLT_negative_pivot_eigenvalues':int(np.sum(piv < -1e-10)),
      'LDLT_reconstruction_max_abs':float(np.max(np.abs(lu@D@lu.T-A))),
      'entrywise_spectral_perturbation_budget':float(max(0,ev[0])/len(A)),
      'budget_status':'lambda_min/N numerical target only; no outward entry enclosures',
    }

def main():
    arithmetic={n for n,p in prime_powers(244)}|{244}
    while len(arithmetic)<110:
        best=max((n for n in range(2,245) if n not in arithmetic),
          key=lambda n:(min(abs(math.log(n)-math.log(m)) for m in arithmetic),-n))
        arithmetic.add(best)
    ns=sorted(arithmetic)
    meshes={'original_uniform_t':np.arange(1,111)/20,
      'arithmetic_reciprocals':np.log(ns),
      'matched_uniform_t':np.linspace(math.log(2),math.log(244),110)}
    calc=Psi();rows=[]
    for name,t in meshes.items():
        u=np.exp(-t);d=np.sqrt(u)
        for sigma in [.45,.5,.55]:
            before=time.perf_counter()
            v=calc.evaluate(t,sigma)
            K=v[:,None]+v[None,:]-calc.evaluate(t[:,None]-t[None,:],sigma)
            Kc=d[:,None]*K*d[None,:]
            row={'mesh':name,'sigma':sigma,'n':len(t),'t_min':float(t.min()),'t_max':float(t.max()),
                'min_t_spacing':float(np.diff(t).min()),'K':stats(K),'Kc':stats(Kc),
                'construction_and_diagnostics_seconds':time.perf_counter()-before,
                'inverse_congruence_max_abs':float(np.max(np.abs(Kc/d[:,None]/d[None,:]-K)))}
            if np.all(np.diag(K)>0):
                z=np.sqrt(np.diag(K));zc=np.sqrt(np.diag(Kc))
                C=K/z[:,None]/z[None,:];Cc=Kc/zc[:,None]/zc[None,:]
                row['correlation_normalized']=stats(C)
                row['correlation_matrix_invariance_error']=float(np.max(np.abs(C-Cc)))
            rows.append(row)
    control=np.full((4,4),-.4);np.fill_diagonal(control,1.)
    d=np.array([1.,.5,.25,.125])
    triples=[float(np.linalg.eigvalsh(np.delete(np.delete(control,j,axis=0),j,axis=1))[0]) for j in range(4)]
    out={'status':'RAN float64; no interval certificate',
      'plan_sha256':hashlib.sha256((HERE/'PLAN.md').read_bytes()).hexdigest(),
      'arithmetic_n':ns,'arithmetic_u_exact':[str(Fraction(1,n)) for n in ns],
      'arithmetic_prime_power_count':len(prime_powers(244)),
      'arithmetic_mixed_ray_relations':sum(1 for n in ns for m in ns if m>n and m%n==0),
      'rows':rows,'max_analytic_lerch_truncation_bound_evaluated':calc.max_series_tail,
      'floating_roundoff_certified':False,
      'local_global_control':{'triple_minima':triples,'original':stats(control),'compact':stats(d[:,None]*control*d[None,:])},
      'interpretation':'Same finite samples preserve inertia by congruence; different meshes need not preserve the count of negative eigenvalues.'}
    (HERE/'results.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'rows':[{'mesh':r['mesh'],'sigma':r['sigma'],'K_min':r['K']['lambda_min'],
      'K_cond':r['K']['condition2'],'Kc_cond':r['Kc']['condition2'],
      'negK':r['K']['negative_eigenvalues_tol1e-10'],'negKc':r['Kc']['negative_eigenvalues_tol1e-10'],
      'budgetK':r['K']['entrywise_spectral_perturbation_budget']} for r in rows]},indent=2))

if __name__=='__main__':main()
