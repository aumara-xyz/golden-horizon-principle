"""T4: same quadratic form W, Codex's sine basis f_j=sin(j pi (x+L)/(2L))/sqrt(L), evaluated in FREQUENCY space with mpmath
(closed-form transforms, mp.quad panels to T_b, analytic tail estimate) against Codex's position-space Arb entries."""
import json, mpmath as mp
mp.mp.dps=30
L=mp.mpf(7)/10; Tb=mp.mpf(20000)
def a_m(t): return mp.re(mp.digamma(mp.mpf(1)/4+1j*t/2))-mp.log(mp.pi)
def Psi(t): return a_m(t)-sum(2*mp.log(p)/mp.sqrt(p**k)*mp.cos(t*k*mp.log(p)) for p,k in ((2,1),(3,1),(2,2)))
def F(i,t):   # (2pi)^{-1/2} L^{-1/2} e^{iLt} int_0^{2L} sin(a u) e^{-iut} du
    a=i*mp.pi/(2*L)
    def E(w): return (mp.exp(1j*w*2*L)-1)/(1j*w) if abs(w)>mp.mpf('1e-20') else 2*L
    inner=(E(a-t)-E(-a-t))/(2j)
    return mp.exp(1j*L*t)*inner/mp.sqrt(2*mp.pi*L)
def fhat(i,c):  # int f_i e^{c x} dx
    a=i*mp.pi/(2*L); return mp.exp(-c*L)/mp.sqrt(L)*a*(1-(-1)**i*mp.exp(2*c*L))/(a*a+c*c)
codex=json.load(open('certified_results.json'))
ent=[r for r in codex['rows'] if r['model']=='authentic'][0]['entries']
res={}
for (i,j) in [(1,1),(1,3),(2,2),(3,3),(2,4),(4,4),(1,2)]:
    g=lambda t: Psi(t)*mp.re(F(i,t)*mp.conj(F(j,t)))
    main=2*mp.quad(g,mp.linspace(0,Tb,2501))
    pole=fhat(i,mp.mpf(1)/2)*fhat(j,-mp.mpf(1)/2)+fhat(j,mp.mpf(1)/2)*fhat(i,-mp.mpf(1)/2)
    ai,aj=i*mp.pi/(2*L),j*mp.pi/(2*L)
    tail=2*(mp.log(1+Tb)+6)*(2*ai)*(2*aj)/(2*mp.pi*L)/(3*Tb**3)   # |F_i|<=2a_i/(sqrt(2 pi L)(t^2-a_i^2)), |Psi|<=log(1+t)+6 (estimate)
    mine=main+pole; theirs=mp.mpf(ent[i-1][j-1].split(' +/-')[0].strip('[')) if ent[i-1][j-1]!='0' else mp.mpf(0)
    res[f"{i},{j}"]={"mine":mp.nstr(mine,20),"codex":mp.nstr(theirs,20),"diff":mp.nstr(mine-theirs,3),"tail_estimate":mp.nstr(tail,2)}
    print(i,j,res[f"{i},{j}"],flush=True)
json.dump(res,open('d6_sameform.json','w'),indent=1)
