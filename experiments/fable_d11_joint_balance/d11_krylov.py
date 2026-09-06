"""D11.2-D11.3: Krylov (Lanczos/CG, full reorthogonalization) responses x_m for C x = b, frozen as exact decimals, evaluated in
ball arithmetic with the residual bracket q in [F_m, F_m + ||r_m||^2/delta]; delta certified independently (eigenbasis Gershgorin).
Controls first. Fable's own code; D10's schur.py was read for audit but not copied."""
import sys, json, time, hashlib
import mpmath as mp
from flint import arb, arb_mat, ctx
ctx.prec=256; mp.mp.dps=60
ORDERS=[2,4,8,16,32]
def A(s): return arb(s)
def mat(rows): return arb_mat([[A(v) if isinstance(v,str) else v for v in r] for r in rows])
def dot(x,y): return sum((u*v for u,v in zip(x,y)),arb(0))
def mv(M,x): 
    y=M*arb_mat([[v] for v in x]); return [y[i,0] for i in range(y.nrows())]
def absnorm_upper(x):  # sqrt(sum abs_upper^2) as an arb upper bound (abs first: r_i*r_i may straddle zero)
    return arb(sum((arb(z.abs_upper())**2 for z in x),arb(0)).sqrt().upper())
def midf(x): return mp.mpf(x.mid().str(70,radius=False))
def householder(H,p):
    n=len(p); np2=dot(p,p); q=[v/np2.sqrt() for v in p]; v=q[:]; v[0]+=1; den=dot(v,v)
    U=arb_mat([[2*v[i]*v[j]/den-(1 if i==j else 0) for j in range(n)] for i in range(n)])
    G=U.transpose()*U
    assert all((U[i,0]-q[i]).contains(0) for i in range(n)) and all((G[i,j]-(1 if i==j else 0)).contains(0) for i in range(n) for j in range(n))
    J=U.transpose()*H*U
    return U,J[0,0],[J[i,0] for i in range(1,n)],arb_mat([[J[i,j] for j in range(1,n)] for i in range(1,n)]),np2
def certify(Cm):
    """Fable's eigenbasis Gershgorin: returns dict with delta (arb lower bound on lambda_min, or None=refused), inertia info."""
    n=Cm.nrows(); E,Vm=mp.eigsy(mp.matrix([[midf(Cm[i,j]) for j in range(n)] for i in range(n)]))
    V=arb_mat([[arb(mp.nstr(Vm[i,j],60)) for j in range(n)] for i in range(n)])
    D=V.transpose()*Cm*V; G=V.transpose()*V
    gl=min((G[i,i]-sum((G[i,j].abs_upper() for j in range(n) if j!=i),arb(0))).lower() for i in range(n))
    gu=max((G[i,i]+sum((G[i,j].abs_upper() for j in range(n) if j!=i),arb(0))).upper() for i in range(n))
    if not arb(gl)>0: return dict(delta=None,status='REFUSED: basis not certified invertible')
    lo=[arb((D[i,i]-sum((D[i,j].abs_upper() for j in range(n) if j!=i),arb(0))).lower()) for i in range(n)]
    hi=[arb((D[i,i]+sum((D[i,j].abs_upper() for j in range(n) if j!=i),arb(0))).upper()) for i in range(n)]
    dmin=min(lo)
    if dmin>0: return dict(delta=arb((dmin/arb(gu)).lower()),status='CERTIFIED C >= delta I',float_eigs=[float(E[i]) for i in range(min(4,n))])
    neg=sum(1 for h in hi if h<0)
    return dict(delta=None,status=('INDEFINITE/NEGATIVE: %d certified negative directions'%neg if neg else 'REFUSED: sign of lambda_min unresolved'),float_eigs=[float(E[i]) for i in range(min(4,n))])
def lanczos_response(Cm,b,m):
    """Krylov subspace K_m(C_mid,b_mid) with full reorthogonalization; Galerkin solve T_m y = Q^T b; x_m = Q y. Frozen decimals."""
    n=len(b); Cf=mp.matrix([[midf(Cm[i,j]) for j in range(n)] for i in range(n)]); bf=mp.matrix([midf(v) for v in b])
    Q=[]; q=bf/mp.norm(bf); Q.append(q)
    for k in range(1,m):
        w=Cf*Q[-1]
        for _ in range(2):
            for qq in Q: w-= (qq.T*w)[0]*qq
        nw=mp.norm(w)
        if nw<mp.mpf(10)**(-50): break
        Q.append(w/nw)
    k=len(Q); Qm=mp.matrix(n,k)
    for j in range(k):
        for i in range(n): Qm[i,j]=Q[j][i]
    T=Qm.T*Cf*Qm; rhs=Qm.T*bf; y=mp.lu_solve(T,rhs); x=Qm*y
    return [mp.nstr(x[i],60) for i in range(n)],k
def bracket(a,b,Cm,kappa,np2,xs,delta):
    x=[arb(s) for s in xs]; Cx=mv(Cm,x); F=2*dot(b,x)-dot(x,Cx); r=[bi-ci for bi,ci in zip(b,Cx)]
    rn=absnorm_upper(r); corr=arb((rn*rn/delta).upper()) if delta is not None else None
    base=a+kappa*np2-F
    lo=arb((base-corr).lower()) if corr is not None else None; up=arb(base.upper())
    verdict='UNVERIFIED'
    if lo is not None and lo>0: verdict='CERTIFIED sigma>0'
    elif up<0: verdict='NEGATIVE WITNESS'
    return dict(F_m=F.str(30),residual_norm_upper=rn.str(12),q_bracket_width=(corr.str(8) if corr is not None else None),
                sigma_lower=(lo.str(20) if lo is not None else None),sigma_upper=up.str(20),verdict=verdict),x
def witness_score(U,H,p,kappa,x):
    n=H.nrows(); f=mv(U,[arb(1)]+[-v for v in x]); s=dot(f,mv(H,f))+kappa*dot(p,f)**2
    return s
def run_family(name,H,p,kappa,orders=ORDERS,stop_on_cert=True,delta_override=None,do_full=False):
    t0=time.time(); U,a,b,C,np2=householder(H,p); cert=certify(C) if delta_override is None else delta_override
    row=dict(label=name,kappa=str(kappa),a=a.str(25),pole_norm_sq=np2.str(25),b_norm=absnorm_upper(b).str(10),C_certificate=cert['status'],
             delta=(cert['delta'].str(12) if cert['delta'] is not None else None),orders={})
    if cert['delta'] is None:
        row['note']='SPD precondition not certified: bracket refused (no division by a guessed delta); Krylov lower bounds F_m still reported'
    for m in orders:
        xs,k=lanczos_response(C,b,m); br,x=bracket(a,b,C,kappa,np2,xs,cert['delta']); br['krylov_dim']=k
        if br['verdict']=='NEGATIVE WITNESS':
            sc=witness_score(U,H,p,kappa,x); br['direct_witness_score_(1,-x_m)']=sc.str(20); br['witness_score_upper_negative']=bool(arb(sc.upper())<0)
            br['frozen_x_m']=xs
        if br['verdict']=='CERTIFIED sigma>0': br['frozen_x_m']=xs
        row['orders'][str(m)]=br; print(name,'m=%d'%m,br['verdict'],'sigma in [',br['sigma_lower'],',',br['sigma_upper'],'] width',br['q_bracket_width'],'|r|',br['residual_norm_upper'],flush=True)
        if stop_on_cert and br['verdict']!='UNVERIFIED': break
    if do_full and cert['delta'] is not None:   # labeled fallback diagnostic: full-size solve (uses a full inverse; NOT candidate construction)
        n=len(b); Cf=mp.matrix([[midf(C[i,j]) for j in range(n)] for i in range(n)]); bf=mp.matrix([midf(v) for v in b]); xf=mp.lu_solve(Cf,bf)
        br,_=bracket(a,b,C,kappa,np2,[mp.nstr(xf[i],60) for i in range(n)],cert['delta']); row['FULL_SOLVE_DIAGNOSTIC']=br
        print(name,'full-solve diagnostic',br['verdict'],br['sigma_lower'],br['sigma_upper'],flush=True)
    row['seconds']=time.time()-t0; return row
def controls():
    out={}
    # planted diagonal SPD with analytic q, and an invertible (non-orthogonal) rotation with the same q
    d=[arb(k) for k in (1,2,3,5,8,13)]; n=len(d); C=arb_mat([[d[i] if i==j else arb(0) for j in range(n)] for i in range(n)]); b=[arb(1)]*n
    qexact=sum((1/v for v in d),arb(0)); a=arb(1); kappa=arb(1); np2=arb(1)
    cert=certify(C); res=[]
    for m in (2,4,6):
        xs,k=lanczos_response(C,b,m); br,_=bracket(a,b,C,kappa,np2,xs,cert['delta']); Fm=arb(br['F_m']); enc=bool(arb(Fm.lower())<=arb(qexact.upper()) and arb((Fm+arb(br['q_bracket_width'])).upper())>=arb(qexact.lower())); res.append((m,br['F_m'][:20],br['q_bracket_width'],bool(enc)))
    out['planted_diag']=dict(q_exact=qexact.str(20),delta=cert['delta'].str(10),per_m=res)
    mp.mp.dps=60; import random; random.seed(11); Rm=mp.matrix([[mp.mpf(random.uniform(-1,1)) for j in range(n)] for i in range(n)])
    Qa=arb_mat([[arb(mp.nstr(Rm[i,j],50)) for j in range(n)] for i in range(n)]); C2=Qa.transpose()*C*Qa; b2=mv(Qa.transpose(),b)
    cert2=certify(C2); res2=[]
    for m in (2,4,6):
        xs,k=lanczos_response(C2,b2,m); br,_=bracket(a,b2,C2,kappa,np2,xs,cert2['delta']); Fm=arb(br['F_m']); enc=bool(arb(Fm.lower())<=arb(qexact.upper()) and arb((Fm+arb(br['q_bracket_width'])).upper())>=arb(qexact.lower())); res2.append((m,br['F_m'][:20],br['q_bracket_width'],bool(enc)))
    out['planted_rotated_invertible']=dict(delta=cert2['delta'].str(10),per_m=res2,note='q invariant under any invertible change of coordinates of the complement')
    # indefinite, singular, ambiguous: must refuse
    for nm,M in (('indefinite',[[1,0],[0,-1]]),('singular',[[1,0],[0,0]]),('ambiguous',[[arb(1),arb(0)],[arb(0),arb('0 +/- 1e-3')]])):
        c=certify(mat(M) if nm!='ambiguous' else arb_mat(M)); out[nm]=c['status']; assert c['delta'] is None
    return out
if __name__=='__main__':
    parity=sys.argv[1]; t0=time.time()
    mine=json.load(open(f'd11_input_{parity}.json')); d10=json.load(open(f'../codex_d10_joint_geometry/input_{parity}.json'))
    kappa=arb(2 if parity=='even' else -2); N=80
    H=mat(mine['H']); p=[A(s) for s in mine['p']]
    report=dict(parity=parity,base_commit='5c22b35',prec_bits=ctx.prec,mp_dps=mp.mp.dps,
                input_sha256=dict(mine=hashlib.sha256(open(f'd11_input_{parity}.json','rb').read()).hexdigest(),d10=hashlib.sha256(open(f'../codex_d10_joint_geometry/input_{parity}.json','rb').read()).hexdigest()))
    report['controls_first']=controls(); print('controls',report['controls_first'],flush=True)
    # entrywise comparison with D10's authentic H (Opus-built) and p
    H10=mat(d10['models']['authentic']); p10=[A(s) for s in d10['p']]
    ov=sum(1 for i in range(N) for j in range(N) if H[i,j].overlaps(H10[i,j])); md=max(abs(H[i,j].mid()-H10[i,j].mid()) for i in range(N) for j in range(N))
    report['H_comparison']=dict(entries_overlapping=ov,of=N*N,max_mid_diff=str(md),my_max_rad=mine['max_entry_radius'],d10_max_rad=str(max(H10[i,j].rad() for i in range(N) for j in range(N))),
                                p_overlap_all=all(p[i].overlaps(p10[i]) for i in range(N)),beta_mine=mine['beta'][:30],beta_d10=d10['beta'][:30])
    print('H comparison',report['H_comparison'],flush=True)
    rows=[]
    # hostile controls BEFORE authentic: D10 control matrices as inputs (labeled), my certifier
    for model in ('arch_only','weight_reverse'):
        rows.append(run_family(f'D10-input {model}',mat(d10['models'][model]),p10,kappa))
    rows.append(run_family('pole sign flipped (my H)',H,p,-kappa))
    rows.append(run_family('pole coefficient kappa-1e-4 (my H)',H,p,kappa-arb('1e-4')))
    rows.append(run_family('AUTHENTIC (my H, my p)',H,p,kappa,do_full=True))
    rows.append(run_family('EXPLORATORY unfrozen orders (authentic)',H,p,kappa,orders=[20,24,28],stop_on_cert=False))
    report['rows']=rows; report['seconds']=time.time()-t0
    # D10 reference values
    try:
        s10=json.load(open(f'../codex_d10_joint_geometry/schur_{parity}.json'))
        for r in s10['rows']:
            if r['label']=='authentic' and r['N']==80: report['d10_reference']=dict(minC=r['complement']['lambda_min']['ball'][:40],sigma=r['sigma']['ball'][:40],response_norm=r['response_norm']['ball'][:30])
    except Exception as e: report['d10_reference']=str(e)
    json.dump(report,open(f'd11_results_{parity}.json','w'),indent=1); print('DONE',parity,report['seconds'],'s',flush=True)
