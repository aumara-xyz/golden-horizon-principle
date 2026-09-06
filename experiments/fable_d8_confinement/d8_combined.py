"""D8 step 4: theta-family R_theta = int (a - (1-theta)P - theta c_L)|F|^2 + Pi, Legendre basis, per sector, per L. Floating (numpy/scipy)."""
import numpy as np, json, math, sys
from scipy.special import spherical_jn, digamma, eval_legendre
from scipy.linalg import eigh
from scipy.optimize import brentq
def primes_powers(L):
    out=[]
    for p in (2,3,5,7,11,13):
        k=1
        while k*math.log(p)<=2*L: out.append((k*math.log(p),2*math.log(p)/p**(k/2))); k+=1
    return out
def lemma(a,L): N=math.ceil(2*L/a-1e-15) if a<2*L else 1; return math.cos(math.pi/(N+1))
def a_t(t): return np.real(digamma(0.25+0.5j*np.asarray(t,dtype=complex)))-math.log(math.pi)
K=48; xg,wg=np.polynomial.legendre.leggauss(K)
def build(L,parity,theta,thetas=None,NE=None):
    pp=primes_powers(L); B=sum(w for _,w in pp); c=sum(w*lemma(a,L) for a,w in pp)
    if thetas is None: thetas=[theta]*len(pp)
    const=sum(w*((1-th)+th*lemma(a,L)) for (a,w),th in zip(pp,thetas))   # envelope constant: sup of (1-th)P_n + th c_n
    Troot=brentq(lambda T:a_t(T)-const,1.0,1e5); T=1.01*Troot
    ns=np.arange(parity,2*(NE if NE else int(1.2*T*L)+40),2)
    # nodes on [0,T]
    npan=int(math.ceil(T)); ts=[];ws=[]
    for kp in range(npan):
        lo,hi=kp,min(kp+1,T); ts.append((hi-lo)/2*xg+(lo+hi)/2); ws.append((hi-lo)/2*wg)
    ts=np.concatenate(ts); ws=np.concatenate(ws)
    beta=a_t(T)-const
    sym=a_t(ts)-sum(w*((1-th)*np.cos(a*ts)+th*lemma(a,L)) for (a,w),th in zip(pp,thetas))-beta
    F=np.array([np.sqrt((2*n+1)/(2*L))*2*L*spherical_jn(n,ts*L)/math.sqrt(2*math.pi)*(-1)**(n//2) for n in ns])
    M=2*(F*(ws*sym))@F.T
    # pole vector
    xq,wq=np.polynomial.legendre.leggauss(200); x=L/2*xq+L/2; wx=L/2*wq
    hyp=np.cosh(x/2) if parity==0 else np.sinh(x/2)
    p=np.array([2*np.sum(wx*np.sqrt((2*n+1)/(2*L))*eval_legendre(n,x/L)*hyp) for n in ns])
    A=M+beta*np.eye(len(ns))+(2 if parity==0 else -2)*np.outer(p,p)
    # prime matrix G (exact, position space) for saturation diagnostics
    G=np.zeros((len(ns),len(ns)))
    for a,w in pp:
        if a>=2*L: continue
        lo,hi=-L+a,L; xx=(hi-lo)/2*xq+(lo+hi)/2; wxx=(hi-lo)/2*wq
        Q1=np.array([np.sqrt((2*n+1)/(2*L))*eval_legendre(n,xx/L) for n in ns]); Q2=np.array([np.sqrt((2*n+1)/(2*L))*eval_legendre(n,(xx-a)/L) for n in ns])
        Gs=(Q1*wxx)@Q2.T; G+=w*(Gs+Gs.T)/2
    return dict(A=A,G=G,T=T,beta=beta,B=B,c=c,const=const,ns=ns,pp=pp)
out={}
for L in (0.4,0.7,0.8,1.0):
    for parity,name in ((0,'even'),(1,'odd')):
        row={}
        for theta in (0.0,0.25,0.5,0.75,1.0):
            if L==1.0 and theta<1.0: continue   # T>144 too large for the floating budget; recorded as not computed
            b=build(L,parity,theta); ev,V=eigh(b['A']); lam=ev[0]; v=V[:,0]
            sat=float(v@b['G']@v); persh=[float(v@(b['G']*0+1)@v)]
            row[f"theta={theta}"]=dict(T=round(b['T'],3),beta=b['beta'],const=b['const'],c=b['c'],B=b['B'],modes=len(b['ns']),lambda_min=float(lam),lambda_2=float(ev[1]),
                                       minimizer_prime_saturation=sat,G_top_eig=float(eigh(b['G'],eigvals_only=True)[-1]))
            print(L,name,theta,{k:(round(v,6) if isinstance(v,float) and abs(v)>1e-4 else v) for k,v in row[f"theta={theta}"].items()},flush=True)
        out[f"L={L} {name}"]=row
# per-shift theta_n in {0,1}^3 at L=0.7 even
combos={}
for bits in range(8):
    th=[(bits>>i)&1 for i in range(3)]
    b=build(0.7,0,None,thetas=th); ev=eigh(b['A'],eigvals_only=True)
    combos[str(th)]=dict(T=round(b['T'],2),lambda_min=float(ev[0]),const=b['const']); print('combo',th,combos[str(th)],flush=True)
out['L=0.7 even per-shift theta combos (order 2,3,4)']=combos
json.dump(out,open('d8_combined_results.json','w'),indent=1)
