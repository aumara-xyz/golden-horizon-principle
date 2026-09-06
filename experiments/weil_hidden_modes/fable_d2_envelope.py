"""D2: Zhu-style frequency-envelope reduction at L=0.7, even functions, Legendre basis. Numerical (mpmath), not interval-certified."""
import sys, json, time, mpmath as mp
mp.mp.dps=40
L=mp.mpf('0.7'); Tsharp=mp.mpf(sys.argv[1]); NE=int(sys.argv[2])   # NE even Legendre modes: n=0,2,...,2NE-2
t0=time.time()
# arithmetic: prime powers with m log p < 2L
pp=[(mp.log(2),2*mp.log(2)/mp.sqrt(2)),(mp.log(3),2*mp.log(3)/mp.sqrt(3)),(2*mp.log(2),2*mp.log(2)/2)]
B=mp.fsum(wt for _,wt in pp)
a=lambda t: mp.re(mp.digamma(mp.mpf(1)/4+1j*t/2))-mp.log(mp.pi)
Psi=lambda t: a(t)-mp.fsum(wt*mp.cos(u*t) for u,wt in pp)
beta=a(Tsharp)-B
ns=[2*m for m in range(NE)]
# unitary Fourier transform of normalized Legendre q_n(x)=sqrt((2n+1)/(2L)) P_n(x/L) on [-L,L]: F_n(t)=(2pi)^{-1/2} sqrt((2n+1)/(2L)) * L * 2 (-i)^n j_n(tL); for even n, (-i)^n=(-1)^{n/2} real
def jn(n,x): return mp.sqrt(mp.pi/(2*x))*mp.besselj(n+mp.mpf(1)/2,x) if x!=0 else (mp.mpf(1) if n==0 else mp.mpf(0))
def F(n,t): return (-1)**(n//2)*mp.sqrt((2*n+1)/(2*L))*L*2*jn(n,t*L)/mp.sqrt(2*mp.pi)
# Gauss-Legendre panels on [0,T], width 5, 40 nodes; integrand even in t -> factor 2
nodes=[];weights=[]
gx,gw=zip(*[(x,w) for x,w in zip(*mp.gauss_legendre(40)) ]) if hasattr(mp,'gauss_legendre') else (None,None)
if gx is None:
    from mpmath.calculus.quadrature import GaussLegendre
    gl=GaussLegendre(mp.mp); pts=gl.calc_nodes(6,mp.mp.prec)  # degree 6 -> 3*2^5=96 nodes on [-1,1]
    gx=[p[0] for p in pts]; gw=[p[1] for p in pts]
npan=int(Tsharp/5)
for k in range(npan):
    lo,hi=5*k,5*(k+1); c,hw=(lo+hi)/2,(hi-lo)/2
    for x,wq in zip(gx,gw): nodes.append(c+hw*x); weights.append(hw*wq)
Ft=[[F(n,t) for t in nodes] for n in ns]                      # NE x K table
Pt=[Psi(t)-beta for t in nodes]
M=mp.matrix(NE,NE)
for i in range(NE):
    for j in range(i,NE):
        M[i,j]=M[j,i]=2*mp.fsum(weights[k]*Pt[k]*Ft[i][k]*Ft[j][k] for k in range(len(nodes)))
# pole term: p_n = <q_n, cosh(x/2)> on [-L,L], by quadrature in x
pxs=[]; 
for x,wq in zip(gx,gw): pxs.append((L*x,L*wq))
p=mp.matrix([mp.fsum(wq*mp.sqrt((2*n+1)/(2*L))*mp.legendre(n,x/L)*mp.cosh(x/2) for x,wq in pxs) for n in ns])
R=M+2*p*p.T+beta*mp.eye(NE)
ev,V=mp.eigsy(R); imin=min(range(NE),key=lambda k:ev[k]); vmin=V[:,imin]
tail=max(abs(vmin[i]) for i in range(NE-5,NE))
# also the true finite-basis form Q on the same span: Q = P + int_{all t} Psi |F|^2 ~ M_full via envelope? Not needed; report R only.
out={"L":"0.7","T_sharp":str(Tsharp),"NE_even_modes":NE,"max_n":ns[-1],"beta_star":mp.nstr(beta,10),"B":mp.nstr(B,10),"a(T)":mp.nstr(a(Tsharp),10),
     "lambda_min_R":mp.nstr(ev[imin],10),"lambda_2_R":mp.nstr(sorted(ev)[1],8),"minimizer_last5_coeff_max":mp.nstr(tail,4),"minimizer_first4_coeff":[mp.nstr(vmin[i],5) for i in range(4)],
     "nodes":len(nodes),"runtime_s":time.time()-t0}
print(json.dumps(out),flush=True); json.dump(out,open(f"d2_T{int(Tsharp)}_NE{NE}.json","w"),indent=1)
