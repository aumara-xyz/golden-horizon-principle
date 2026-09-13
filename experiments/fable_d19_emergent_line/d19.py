import sys, json, math
sys.path.insert(0,'../fable_d17_squares_exponent'); exec(open('../fable_d17_squares_exponent/d17.py').read().split("res={'A'")[0])
NF=3e-14
def edge(name,L,par,direction):
    # bisection for the boundary of {sigma: lam>NF} starting at 0.5 going in direction (+1/-1); assume positive at 0.5
    a,b=0.5,0.5+direction*0.2
    if lam2(name,L,par,sigma=b)>NF: return b  # boundary beyond search range
    for _ in range(22):
        m=(a+b)/2
        if lam2(name,L,par,sigma=m)>NF: a=m
        else: b=m
    return a
res={}
for name,Ls in (('zeta',(0.30,0.35,0.40,0.45,0.50,0.55,0.60)),('chi_-4',(0.5,0.7,0.9,1.0))):
    for L in Ls:
        row={}
        for par,pn in ((0,'even'),(1,'odd')):
            lo=edge(name,L,par,-1); hi=edge(name,L,par,+1); row[pn]=(lo,hi)
        jlo=max(row['even'][0],row['odd'][0]); jhi=min(row['even'][1],row['odd'][1]); w=jhi-jlo; mid=(jlo+jhi)/2
        row['joint']=(jlo,jhi); row['width']=w; row['midpoint']=mid
        print(f"{name} L={L:.2f}: even [{row['even'][0]:.6f},{row['even'][1]:.6f}] odd [{row['odd'][0]:.6f},{row['odd'][1]:.6f}] joint width {w:.2e} midpoint {mid:.6f} (offset {mid-0.5:+.2e})",flush=True)
        res[f"{name} L={L}"]=row
json.dump(res,open('d19_results.json','w'),indent=1)
