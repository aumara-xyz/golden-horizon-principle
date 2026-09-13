"""Trial-3 candidates: minimizer of the fixed-ruler reduced form (T=160, 160 modes, double precision, selection only) restricted to waves with
f and its first 4 derivatives vanishing at x=+-L. Writes d22_cand_{parity}_L{L}.json with frozen decimals (same schema as the cert JSONs)."""
import numpy as np, math, json, sys, warnings
warnings.simplefilter('ignore')
from scipy.special import spherical_jn, digamma, eval_legendre
from math import factorial
K48=48; xg,wg=np.polynomial.legendre.leggauss(K48)
PPf=[(math.log(2),2*math.log(2)/math.sqrt(2)),(math.log(3),2*math.log(3)/math.sqrt(3)),(2*math.log(2),math.log(2))]
def a_t(t): return np.real(digamma(0.25+0.5j*np.asarray(t,dtype=complex)))-math.log(math.pi)
def build(L,parity,T=160,NE=160):
    pp=[(u,w) for u,w in PPf if u<2*L]; B=sum(w for _,w in pp); ns=np.arange(parity,2*NE,2); ts=[];ws=[]
    for kp in range(T):
        ts.append(0.5*xg+kp+0.5); ws.append(0.5*wg)
    ts=np.concatenate(ts); ws=np.concatenate(ws); beta=a_t(T)-B; sym=a_t(ts)-sum(w*np.cos(u*ts) for u,w in pp)-beta
    F=np.array([np.sqrt((2*n+1)/(2*L))*2*L*spherical_jn(n,ts*L)/math.sqrt(2*math.pi)*(-1)**(n//2) for n in ns]); F[~np.isfinite(F)]=0
    A=2*(F*(ws*sym))@F.T+beta*np.eye(len(ns))
    xq,wq=np.polynomial.legendre.leggauss(200); x=L/2*xq+L/2; wx=L/2*wq; hyp=np.cosh(x/2) if parity==0 else np.sinh(x/2)
    p=np.array([2*np.sum(wx*np.sqrt((2*n+1)/(2*L))*eval_legendre(n,x/L)*hyp) for n in ns]); A+=(2 if parity==0 else -2)*np.outer(p,p)
    return ns,A
def endpoint_derivs(ns,L,kmax=4):
    # d^k/dx^k [sqrt((2n+1)/2L) P_n(x/L)] at x=L: sqrt(..) L^-k * P_n^(k)(1),  P_n^(k)(1)=(n+k)!/(2^k k! (n-k)!); at x=-L: times (-1)^(n-k). Parity makes +-L rows dependent; use x=+L only.
    rows=[]
    for k in range(kmax+1):
        rows.append([math.sqrt((2*n+1)/(2*L))*L**(-k)*(factorial(n+k)/(2**k*factorial(k)*factorial(n-k)) if n>=k else 0.0) for n in ns])
    return np.array(rows)
for L in (0.4,0.5,0.6,0.7):
    for parity,pn in ((0,'even'),(1,'odd')):
        ns,A=build(L,parity); Cm=endpoint_derivs(ns,L)
        # null space of constraints (scaled rows)
        Cm=Cm/np.linalg.norm(Cm,axis=1,keepdims=True); u,s,vt=np.linalg.svd(Cm); N=vt[len(s):].T
        Ar=N.T@A@N; ev,V=np.linalg.eigh(Ar); c=N@V[:,0]; c/=np.linalg.norm(c)
        unconstrained=float(np.linalg.eigvalsh(A)[0]); constrained=float(ev[0])
        out=dict(L=str(L),parity=pn,T_select=160,constraint='f, f\', f\'\', f\'\'\', f\'\'\'\' vanish at +-L',reduced_min_unconstrained=unconstrained,reduced_min_constrained=constrained,
                 ratio=constrained/unconstrained if unconstrained>0 else None,boundary_residual=float(np.max(np.abs(Cm@c))),modes=[int(n) for n in ns],minimizer_frozen_40dig=[repr(float(v)) for v in c],
                 lambda0_certified=json.load(open(f'd22_cert_{pn}_L{L}_T160_N160.json'))['lambda0_certified'],verdict='candidate for upper bound only')
        json.dump(out,open(f'd22_cand_{pn}_L{L}.json','w'),indent=1)
        print(f"{pn} L={L}: reduced min unconstrained {unconstrained:.3e}, boundary-vanishing constrained {constrained:.3e} (ratio {constrained/unconstrained:.3f}), boundary residual {np.max(np.abs(Cm@c)):.1e}",flush=True)
