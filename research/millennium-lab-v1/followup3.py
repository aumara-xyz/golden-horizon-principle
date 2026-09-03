"""Follow-up 3: angle between the true Weil ground state and (a) the prolate candidate k_lambda [Codex's exact projection], (b) the undeformed Hermite candidate E(h) [my quadrature projection]. Validation: (a) must reproduce Codex's actual_sin_angle."""
import sys, json, time, math
sys.path.insert(0,"codex-r5")
import mpmath as mp
from flint import arb_mat, arb, ctx
from run_prolate_only_control import high_precision_candidate
from run_prolate_exact_bridge import exact_e_projection
from weil_core import parity_blocks, prime_power_terms
X=[int(a) for a in sys.argv[1].split(",")]; N=120; DPS=100; out={}
for x in X:
    t0=time.time(); mp.mp.dps=DPS; ctx.dps=DPS; lam=mp.sqrt(x); L=mp.log(x)
    # ground state via Codex's parity blocks (even block) + flint inverse iteration
    even,odd,meta=parity_blocks(N,x,prime_power_terms(x),DPS); M=even.rows
    Em=arb_mat(M,M,[arb(mp.nstr(even[i,j],DPS+5)) for i in range(M) for j in range(M)])
    v=[arb(1)]*M
    for _ in range(5):
        y=Em.solve(arb_mat(M,1,v)); v=[y[i,0].mid() for i in range(M)]; s=sum(t*t for t in v).sqrt(); v=[t/s for t in v]
    xi_even=[mp.mpf(t.str(DPS,radius=False)) for t in v]          # orthonormal even basis: e_0=V_0, e_n=(V_-n+V_n)/sqrt2
    # (a) prolate candidate, Codex exact projection -> full (-N..N) coefficients
    cand=high_precision_candidate(x,200 if x<18 else 240); proj=exact_e_projection(cand,N); full=proj["full"]
    def to_even(full):
        e=[full[N]]+[(full[N-n]+full[N+n])/mp.sqrt(2) for n in range(1,N+1)]; return e
    def angle(c):
        c=[mp.mpc(t) for t in c]; nc=mp.sqrt(mp.fsum(abs(t)**2 for t in c)); ov=abs(mp.fsum(mp.conj(c[i])*xi_even[i] for i in range(M)))/nc
        return float(mp.sqrt(max(0,1-ov**2)))
    a_prolate=angle(to_even(full))
    # (b) undeformed Hermite candidate: h = (sqrt3/2^(11/4)) h4 - (3/2^(17/4)) h0, E(h)(u)=sqrt(u) sum_m h(m u); project on V_n over [1/lam, lam] with d*u
    mp.mp.dps=30
    h0=lambda y: mp.mpf(2)**mp.mpf(0.25)*mp.exp(-mp.pi*y*y)
    h4=lambda y: (16*mp.pi**2*y**4-24*mp.pi*y**2+3)*mp.exp(-mp.pi*y*y)/(2*mp.sqrt(2)*mp.sqrt(3))
    h=lambda y: mp.sqrt(3)/mp.mpf(2)**mp.mpf(11)/4*h4(y)-3/mp.mpf(2)**mp.mpf(17)/4*h0(y)
    def Eh(u):
        s=mp.mpf(0); m=1
        while True:
            t=h(m*u); s+=t
            if m*u>4 and abs(t)<mp.mpf(10)**-28: break
            m+=1
        return mp.sqrt(u)*s
    lamf=mp.sqrt(x); Lf=mp.log(x)
    def cn(n): return mp.quad(lambda u: Eh(u)*mp.exp(-2j*mp.pi*n*mp.log(lamf*u)/Lf)/mp.sqrt(Lf)/u,[1/lamf,1,lamf],maxdegree=8)
    herm=[cn(n) for n in range(-N,N+1)]
    mp.mp.dps=DPS; a_herm=angle(to_even(herm))
    out[x]={"sin_angle_prolate":a_prolate,"sin_angle_hermite":a_herm,"ratio_hermite_over_prolate":a_herm/a_prolate,"wall_s":time.time()-t0}
    print("RESULT",x,out[x],flush=True); json.dump(out,open("followup3-hermite-vs-prolate.json","w"),indent=1)
