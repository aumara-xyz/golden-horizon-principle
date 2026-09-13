import numpy as np, math, json, warnings, mpmath as mp
warnings.simplefilter('ignore'); mp.mp.dps=60
from scipy.special import spherical_jn, digamma, eval_legendre
K48=48; xg,wg=np.polynomial.legendre.leggauss(K48)
PPf=[(math.log(2),2*math.log(2)/math.sqrt(2)),(math.log(3),2*math.log(3)/math.sqrt(3)),(2*math.log(2),math.log(2))]
def a_t(t): return np.real(digamma(0.25+0.5j*np.asarray(t,dtype=complex)))-math.log(math.pi)
def build(L,parity,T=160,NE=80):
    pp=[(u,w) for u,w in PPf if u<2*L]; B=sum(w for _,w in pp); ns=np.arange(parity,2*NE,2); ts=[];ws=[]
    for kp in range(T): ts.append(0.5*xg+kp+0.5); ws.append(0.5*wg)
    ts=np.concatenate(ts); ws=np.concatenate(ws); beta=a_t(T)-B; sym=a_t(ts)-sum(w*np.cos(u*ts) for u,w in pp)-beta
    F=np.array([np.sqrt((2*n+1)/(2*L))*2*L*spherical_jn(n,ts*L)/math.sqrt(2*math.pi)*(-1)**(n//2) for n in ns]); F[~np.isfinite(F)]=0
    A=2*(F*(ws*sym))@F.T+beta*np.eye(len(ns))
    xq,wq=np.polynomial.legendre.leggauss(200); x=L/2*xq+L/2; wx=L/2*wq; hyp=np.cosh(x/2) if parity==0 else np.sinh(x/2)
    p=np.array([2*np.sum(wx*np.sqrt((2*n+1)/(2*L))*eval_legendre(n,x/L)*hyp) for n in ns]); A+=(2 if parity==0 else -2)*np.outer(p,p)
    return ns,A
def constraints_mp(ns,L,kmax=4):
    Lm=mp.mpf(L); rows=[]
    for k in range(kmax+1):
        rows.append([mp.sqrt(mp.mpf(2*n+1)/(2*Lm))*Lm**(-k)*(mp.factorial(n+k)/(2**k*mp.factorial(k)*mp.factorial(n-k)) if n>=k else mp.mpf(0)) for n in [int(v) for v in ns]])
    return mp.matrix(rows)
for L in (0.4,0.5,0.6,0.7):
    for parity,pn in ((0,'even'),(1,'odd')):
        ns,A=build(L,parity); C=constraints_mp(ns,L); m,n=C.rows,C.cols
        # orthonormal basis N of the null space of C in 60 digits: N = columns of Q from QR of C^T beyond rank
        Q,R=mp.qr(C.T)   # C.T is n x m -> Q n x n
        N=mp.matrix(n,n-m)
        for i in range(n):
            for j in range(n-m): N[i,j]=Q[i,m+j]
        Nf=np.array([[float(N[i,j]) for j in range(n-m)] for i in range(n)])
        Ar=Nf.T@A@Nf; ev,V=np.linalg.eigh(Ar); y=V[:,0]
        c=N*mp.matrix([mp.mpf(float(v)) for v in y]); nrm=mp.sqrt(sum(c[i]**2 for i in range(n))); c=c/nrm
        resid=max(abs((C*c)[k]) for k in range(m)); unconstrained=float(np.linalg.eigvalsh(A)[0]); constrained=float(ev[0])
        out=dict(L=str(L),parity=pn,T_select=160,NE=80,constraint='value and first 4 derivatives vanish at +-L, enforced at 60 digits',reduced_min_unconstrained=unconstrained,reduced_min_constrained=constrained,ratio=constrained/unconstrained,
                 boundary_residual=mp.nstr(resid,5),modes=[int(v) for v in ns],minimizer_frozen_40dig=[mp.nstr(c[i],40) for i in range(n)],
                 lambda0_certified=json.load(open(f'd22_cert_{pn}_L{L}_T160_N160.json'))['lambda0_certified'],verdict='candidate for upper bound only')
        json.dump(out,open(f'd22_cand2_{pn}_L{L}.json','w'),indent=1)
        print(f"{pn} L={L}: unconstrained {unconstrained:.3e} constrained {constrained:.3e} ratio {constrained/unconstrained:.3f} boundary residual {mp.nstr(resid,3)}",flush=True)
