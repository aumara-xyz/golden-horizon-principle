import numpy as np, math, warnings, json
warnings.simplefilter('ignore')
from scipy.special import spherical_jn, digamma, eval_legendre
K=48; xg,wg=np.polynomial.legendre.leggauss(K)
def pps(L):
    out=[]
    for p in (2,3,5,7,11,13,17,19,23):
        k=1
        while k*math.log(p)<=2*L: out.append((p,k)); k+=1
    return out
CHARS={'chi_-4':dict(q=4,a=1,chi=lambda n: 0 if n%2==0 else (1 if n%4==1 else -1)),
       'chi_-3':dict(q=3,a=1,chi=lambda n: 0 if n%3==0 else (1 if n%3==1 else -1)),
       'chi_5':dict(q=5,a=0,chi=lambda n: 0 if n%5==0 else (1 if n%5 in (1,4) else -1))}
def a_chi(t,a): return np.real(digamma(0.25+a/2+0.5j*np.asarray(t,dtype=complex)))-math.log(math.pi)
def lam(name,L,parity,scale=None):
    c=CHARS[name]; terms=[(k*math.log(p), c['chi'](p**k)*2*math.log(p)/p**(k/2)) for p,k in pps(L)]
    terms=[(u,w*(scale.get(round(math.exp(u)),1.0) if scale else 1.0)) for u,w in terms if w!=0]
    B=sum(abs(w) for _,w in terms); shift=math.log(c['q']); T=60.0
    while a_chi(T,c['a'])+shift-B<0.01: T*=1.3
    T=max(1.3*T,60) if T>60 else 60.0
    NE=int(1.2*T*L)+40; ns=np.arange(parity,2*NE,2); npan=int(math.ceil(T)); ts=[];ws=[]
    for kp in range(npan):
        lo,hi=kp,min(kp+1,T); ts.append((hi-lo)/2*xg+(lo+hi)/2); ws.append((hi-lo)/2*wg)
    ts=np.concatenate(ts); ws=np.concatenate(ws); beta=a_chi(T,c['a'])+shift-B
    sym=a_chi(ts,c['a'])+shift-sum(w*np.cos(u*ts) for u,w in terms)-beta
    F=np.array([np.sqrt((2*n+1)/(2*L))*2*L*spherical_jn(n,ts*L)/math.sqrt(2*math.pi)*(-1)**(n//2) for n in ns]); F[~np.isfinite(F)]=0
    A=2*(F*(ws*sym))@F.T+beta*np.eye(len(ns))
    return float(np.linalg.eigvalsh(A)[0]),T
out={}
for name,L,pr in (('chi_-3',0.9,2),('chi_-4',1.0,3),('chi_5',1.0,2)):
    row={}
    for s in (1.0,0.999,0.0):
        e,T=lam(name,L,0,{pr:s}); o,_=lam(name,L,1,{pr:s}); row[str(s)]=(e,o); print(f"SLACK {name} L={L} prime {pr} x{s}: even {e:+.2e} odd {o:+.2e} (T={T:.0f})",flush=True)
    out[f"{name} L={L} prime{pr}"]=row
for name in ('chi_-3','chi_5'):
    e1,_=lam(name,0.5,0); e0,_=lam(name,0.5,0,{2:0.0}); o1,_=lam(name,0.5,1); o0,_=lam(name,0.5,1,{2:0.0})
    out[f"{name} L=0.5 remove2"]=(e1,e0,o1,o0); print(f"REMOVE2 {name} L=0.5: even {e1:+.2e}->{e0:+.2e} odd {o1:+.2e}->{o0:+.2e}",flush=True)
json.dump(out,open('d15_slack.json','w'),indent=1)
