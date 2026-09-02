"""Fable's implementation of Connes-Consani-Moscovici 'Zeta Spectral Triples' (arXiv:2511.22755), from the published formulas.
Usage: python3 ccm_triples.py --lam2 9 --N 120 --dps 220 [--drop-prime 2] [--pseudo SEED] [--no-primes] [--permute SEED] --out file.json
No zeta zero enters the construction; zeros are loaded only for scoring at the end."""
import argparse, json, time, math, random
import mpmath as mp
from flint import arb_mat, arb, ctx
ap=argparse.ArgumentParser(); ap.add_argument("--lam2",type=float,required=True); ap.add_argument("--N",type=int,default=120); ap.add_argument("--dps",type=int,default=220)
ap.add_argument("--drop-prime",type=int,default=0); ap.add_argument("--pseudo",type=int,default=-1); ap.add_argument("--no-primes",action="store_true"); ap.add_argument("--permute",type=int,default=-1)
ap.add_argument("--nzeros",type=int,default=50); ap.add_argument("--out",required=True); a=ap.parse_args()
mp.mp.dps=a.dps; ctx.dps=a.dps; t0=time.time()
lam=mp.sqrt(mp.mpf(a.lam2)); L=2*mp.log(lam); N=a.N; idx=list(range(-N,N+1)); pi=mp.pi
# ---- prime powers k <= lam^2 with von Mangoldt weights ----
def primes_upto(x):
    s=[True]*(x+1); s[0]=s[1]=False
    for i in range(2,int(x**.5)+1):
        if s[i]:
            for j in range(i*i,x+1,i): s[j]=False
    return [i for i in range(2,x+1) if s[i]]
pts=[]  # (y=log k, weight Lambda(k) k^{-1/2})
for p in primes_upto(int(math.floor(a.lam2))):
    if p==a.drop_prime: continue
    q=p
    while q<=a.lam2+1e-12: pts.append((mp.log(q),mp.log(p)/mp.sqrt(q))); q*=p
if a.no_primes: pts=[]
if a.pseudo>=0:
    rng=random.Random(a.pseudo); pts=[(L*mp.mpf(rng.random()),w) for (_,w) in pts]
if a.permute>=0:
    rng=random.Random(a.permute); ws=[w for _,w in pts]; rng.shuffle(ws); pts=[(y,w) for (y,_),w in zip(pts,ws)]
# ---- q(U_n,U_m)(y) for y in [0,L] (Lemma 2.3) ----
def q(n,m,y):
    if n==m: return 2*(1-y/L)*mp.cos(2*pi*n*y/L)
    return (mp.sin(2*pi*m*y/L)-mp.sin(2*pi*n*y/L))/(pi*(n-m))
# ---- archimedean: A_n = int_0^L sin(w x) rho(x) dx, G_n = int_0^L [2(1-x/L)cos(w x)e^{x/2} - 2]/(e^x-e^{-x}) dx ----
K=int(a.dps/(2*float(L)*0.4343))+8   # geometric tail terms: e^{-2kL} < 10^{-dps}
def A_of(n):
    w=2*pi*n/L; s=mp.im(mp.digamma(mp.mpf(1)/4+1j*pi*n/L))/2
    tail=mp.mpc(0)
    for k in range(K):
        c=2*k+mp.mpf(1)/2; sc=c-1j*w; tail+=mp.exp(-sc*L)/sc
    return s-mp.im(tail)
def G_of(n):
    w=2*pi*n/L; z=mp.mpf(1)/4+1j*pi*n/L
    main=mp.digamma(mp.mpf(1)/2)-mp.re(mp.digamma(z))-mp.re(mp.polygamma(1,z))/(2*L)
    tail=mp.mpf(0)
    for k in range(K):
        c=2*k+mp.mpf(1)/2; sc=c-1j*w; e=mp.exp(-sc*L)
        tail+=2*mp.re(e/sc)-(2/L)*mp.re(e*(L/sc+1/sc**2))-2*mp.exp(-(2*k+1)*L)/(2*k+1)
    return main-tail
A={n:A_of(n) for n in range(0,N+1)}; A.update({-n:-A[n] for n in range(1,N+1)})
G={n:G_of(n) for n in range(0,N+1)}; G.update({-n:G[n] for n in range(1,N+1)})
const=mp.euler+mp.log(4*pi*(mp.exp(L)-1)/(mp.exp(L)+1))
def WR(n,m): return const+G[n] if n==m else (A[m]-A[n])/(pi*(n-m))
def W02(n,m): return 32*L*mp.sinh(L/4)**2*(L**2-16*pi**2*m*n)/((L**2+16*pi**2*m**2)*(L**2+16*pi**2*n**2))
def WP(n,m): return mp.fsum(w*q(n,m,y) for (y,w) in pts) if pts else mp.mpf(0)
M=len(idx); T=[[None]*M for _ in range(M)]
for i,n in enumerate(idx):
    for j,m in enumerate(idx):
        if j<i: T[i][j]=T[j][i]; continue
        T[i][j]=W02(n,m)-WR(n,m)-WP(n,m)
tb=time.time()-t0
# ---- inverse iteration (flint) for the smallest eigenpair, then deflated for the second ----
Tm=arb_mat(M,M,[arb(mp.nstr(T[i][j],a.dps+5)) for i in range(M) for j in range(M)])
def solve(v):
    return Tm.solve(arb_mat(M,1,v))
def normalize(v):
    s=sum(x*x for x in v); s=s.sqrt(); return [x/s for x in v]
v=[arb(1)]*M
for it in range(4):
    x=solve(v); v=normalize([x[i,0].mid() for i in range(M)])
xi=v
ray=lambda v:(sum(v[i]*sum(Tm[i,j]*v[j] for j in range(M)) for i in range(M)))
eps1=ray(xi)
# even check and sign: xi_j vs xi_{-j}
even_err=max(abs(float((xi[i]-xi[M-1-i]).mid())) for i in range(M)); norm0=max(abs(float(x.mid())) for x in xi)
# second eigenvalue via deflated inverse iteration
u=[arb((-1)**k)*arb(1+k%3) for k in range(M)]
for it in range(5):
    d=sum(u[i]*xi[i] for i in range(M)); u=[u[i]-d*xi[i] for i in range(M)]; x=solve(u); x=[x[i,0].mid() for i in range(M)]; d=sum(x[i]*xi[i] for i in range(M)); u=normalize([x[i]-d*xi[i] for i in range(M)])
eps2=ray(u)
# ---- spectrum: roots of f(z) = sum_j xi_j/(z - 2 pi j/L) ----
xim=[mp.mpf(x.mid().str(a.dps,radius=False)) for x in xi]
def f(z): return mp.fsum(xim[i]/(z-2*pi*idx[i]/L) for i in range(M))
# scan for sign changes on (0, zmax) avoiding poles at 2 pi j / L
zmax=mp.mpf(150); step=mp.mpf("0.02"); roots=[]; z=step; fz=f(z)
while z<zmax and len(roots)<a.nzeros:
    z2=z+step; f2=f(z2)
    # skip intervals containing a pole
    pole=any(abs(2*pi*j/L-z)<step for j in range(1,N+1) if z<=2*pi*j/L<=z2)
    if not pole and fz*f2<0:
        lo,hi,flo=z,z2,fz
        for _ in range(int(a.dps*3.4)+10):
            mid=(lo+hi)/2; fm=f(mid)
            if flo*fm<0: hi=mid
            else: lo,flo=mid,fm
        roots.append((lo+hi)/2)
    z,fz=z2,f2
# ---- scoring only now ----
zeros=[mp.im(mp.zetazero(k)) for k in range(1,len(roots)+1)]
err=[abs(r-g) for r,g in zip(roots,zeros)]
out={"lam2":a.lam2,"lam":mp.nstr(lam,20),"L":mp.nstr(L,20),"N":N,"dps":a.dps,"n_prime_points":len(pts),"controls":{"drop_prime":a.drop_prime,"pseudo":a.pseudo,"no_primes":a.no_primes,"permute":a.permute},
     "eps1":eps1.mid().str(15,radius=False),"eps2":eps2.mid().str(15,radius=False),"even_err_rel":even_err/norm0,
     "n_roots":len(roots),"roots_first5":[mp.nstr(r,30) for r in roots[:5]],"abs_err":[mp.nstr(e,3) for e in err],"build_s":tb,"total_s":time.time()-t0}
json.dump(out,open(a.out,"w"),indent=1); print(json.dumps({k:v for k,v in out.items() if k!="abs_err"},indent=1)); print("errors:",out["abs_err"])
